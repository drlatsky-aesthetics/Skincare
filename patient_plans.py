"""
Patient treatment-plan storage + access control.

Plans are stored as structured JSON (one file per patient slug) on the same
persistent volume that hosts published pages, so they stay editable after
publishing — unlike the legacy /api/publish-page flow which stores opaque
HTML blobs.

Access model:
  - Staff endpoints authenticate with the existing PUBLISH_TOKEN bearer token.
  - Patients unlock a plan by entering the date of birth on file. A correct
    DOB returns a signed, time-limited token that authorizes reading the plan
    and persisting product preferences (the "use my own product" toggle).
"""

import hmac
import json
import os
import re
import time
from datetime import datetime, timezone

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
DOB_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

UNLOCK_MAX_AGE_SECONDS = 12 * 60 * 60  # 12h — long enough for a patient session

# DOB brute-force throttle: per-slug sliding window of failed attempts.
_FAILED_ATTEMPTS: dict[str, list[float]] = {}
_MAX_FAILURES = 15
_FAILURE_WINDOW_SECONDS = 60 * 60


def plans_dir() -> str:
    base = os.environ.get("RAILWAY_VOLUME_MOUNT_PATH", "./data")
    path = os.path.join(base, "plans")
    os.makedirs(path, exist_ok=True)
    return path


def _signing_key() -> str:
    # Reuse existing secrets so production works without new env vars.
    return (
        os.environ.get("SECRET_KEY")
        or os.environ.get("PUBLISH_TOKEN")
        or "dev-secret-change-in-production"
    )


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(_signing_key(), salt="plan-unlock")


def _plan_path(slug: str) -> str:
    return os.path.join(plans_dir(), f"{slug}.json")


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:80]
    return slug or "patient"


def normalize_plan(data: dict) -> tuple[dict | None, str | None]:
    """Validate + normalize an incoming plan payload. Returns (plan, error)."""
    slug = (data.get("slug") or "").strip().lower()
    if not SLUG_RE.match(slug):
        return None, "Invalid slug — use lowercase letters, numbers, and hyphens only."

    patient = data.get("patient") or {}
    name = (patient.get("name") or "").strip()
    dob = (patient.get("dob") or "").strip()
    if not name:
        return None, "Patient name is required."
    if not DOB_RE.match(dob):
        return None, "Patient date of birth must be in YYYY-MM-DD format."

    def _str(v):
        return v.strip() if isinstance(v, str) else ""

    def _str_list(v):
        if not isinstance(v, list):
            return []
        return [s.strip() for s in v if isinstance(s, str) and s.strip()]

    technologies = []
    for t in data.get("technologies") or []:
        if not isinstance(t, dict) or not _str(t.get("name")):
            continue
        technologies.append({
            "name": _str(t.get("name")),
            "why": _str(t.get("why")),
            "timeline": _str(t.get("timeline")),
            "optional": bool(t.get("optional")),
        })

    products = []
    for p in data.get("products") or []:
        if not isinstance(p, dict) or not _str(p.get("brand_name")):
            continue
        products.append({
            "brand_name": _str(p.get("brand_name")),
            "generic_name": _str(p.get("generic_name")) or "Equivalent product of your choice",
            "detail": _str(p.get("detail")),
            "use_generic": bool(p.get("use_generic")),
            "optional": bool(p.get("optional")),
        })

    plan = {
        "slug": slug,
        "patient": {"name": name, "dob": dob},
        "concern": _str(data.get("concern")),
        "title": _str(data.get("title")) or f"Treatment Plan for {name}",
        "overview": _str(data.get("overview")),
        "technologies": technologies,
        "pre_care": _str_list(data.get("pre_care")),
        "post_care": _str_list(data.get("post_care")),
        "products": products,
        "notes": _str(data.get("notes")),
    }
    return plan, None


def save_plan(plan: dict) -> dict:
    """Persist a normalized plan, preserving created timestamp on update."""
    path = _plan_path(plan["slug"])
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    existing = load_plan(plan["slug"])
    plan["created"] = existing.get("created", now) if existing else now
    plan["updated"] = now
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
    return plan


def load_plan(slug: str) -> dict | None:
    if not SLUG_RE.match(slug):
        return None
    path = _plan_path(slug)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def delete_plan(slug: str) -> bool:
    if not SLUG_RE.match(slug):
        return False
    path = _plan_path(slug)
    if not os.path.isfile(path):
        return False
    os.remove(path)
    return True


def list_plans() -> list[dict]:
    out = []
    for fname in sorted(os.listdir(plans_dir())):
        if not fname.endswith(".json"):
            continue
        plan = load_plan(fname[:-5])
        if plan:
            out.append({
                "slug": plan["slug"],
                "patient_name": plan.get("patient", {}).get("name", ""),
                "title": plan.get("title", ""),
                "concern": plan.get("concern", ""),
                "updated": plan.get("updated", ""),
            })
    return out


def public_plan(plan: dict) -> dict:
    """Plan as exposed to an unlocked patient — no DOB echo-back."""
    out = dict(plan)
    out["patient"] = {"name": plan.get("patient", {}).get("name", "")}
    return out


# ── DOB gate ──────────────────────────────────────────────────────────────────

def _prune_failures(slug: str) -> list[float]:
    cutoff = time.time() - _FAILURE_WINDOW_SECONDS
    attempts = [t for t in _FAILED_ATTEMPTS.get(slug, []) if t > cutoff]
    _FAILED_ATTEMPTS[slug] = attempts
    return attempts


def is_throttled(slug: str) -> bool:
    return len(_prune_failures(slug)) >= _MAX_FAILURES


def verify_dob(plan: dict, dob_attempt: str) -> bool:
    slug = plan["slug"]
    expected = plan.get("patient", {}).get("dob", "")
    attempt = (dob_attempt or "").strip()
    ok = bool(expected) and hmac.compare_digest(expected, attempt)
    if not ok:
        _prune_failures(slug)
        _FAILED_ATTEMPTS.setdefault(slug, []).append(time.time())
    return ok


def issue_unlock_token(slug: str) -> str:
    return _serializer().dumps(slug)


def verify_unlock_token(slug: str, token: str) -> bool:
    try:
        value = _serializer().loads(token, max_age=UNLOCK_MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return False
    return value == slug
