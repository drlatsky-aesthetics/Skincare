import io
import os
import re
from flask import Flask, render_template, request, jsonify, send_file, abort, Response
from dotenv import load_dotenv
from agent import SkincareAgent
from export_docx import generate_plan_docx
import patient_plans

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

# Persistent patient-page storage. Backed by a Railway Volume mounted at
# RAILWAY_VOLUME_MOUNT_PATH (falls back to a local ./data dir outside Railway,
# e.g. for local dev) so published pages survive redeploys.
PAGES_DIR = os.path.join(os.environ.get("RAILWAY_VOLUME_MOUNT_PATH", "./data"), "pages")
os.makedirs(PAGES_DIR, exist_ok=True)

# Slugs become filenames on disk and segments of a public URL — restrict to a
# safe charset so a crafted slug can't escape PAGES_DIR (e.g. "../../etc").
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")

try:
    agent = SkincareAgent()
except Exception as e:
    print(f"[startup] Agent init failed: {e}")
    agent = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    # Return an empty 204 so the browser stops logging a 404
    return "", 204


@app.route("/chat", methods=["POST"])
def chat():
    if agent is None:
        return jsonify({"error": "Agent failed to initialise — check server logs."}), 503

    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    clean_history = [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if isinstance(m, dict) and m.get("role") in ("user", "assistant") and m.get("content")
    ]

    try:
        reply = agent.chat(user_message, clean_history)
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"[chat] error: {e}")
        return jsonify({"error": f"Something went wrong: {e}"}), 500


@app.route("/api/process-consult", methods=["POST"])
def process_consult():
    if agent is None:
        return jsonify({"error": "Agent failed to initialise — check server logs."}), 503

    data = request.get_json(silent=True) or {}
    transcript = (data.get("transcript") or "").strip()
    if not transcript:
        return jsonify({"error": "No transcript provided"}), 400
    if len(transcript) < 20:
        return jsonify({"error": "Transcript too short to process — keep listening a bit longer."}), 400

    try:
        reply = agent.process_consult(transcript)
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"[process_consult] error: {e}")
        return jsonify({"error": f"Something went wrong: {e}"}), 500


@app.route("/export", methods=["POST"])
def export():
    data = request.get_json(silent=True) or {}
    plan = data.get("plan")
    if not plan or not isinstance(plan, dict):
        return jsonify({"error": "No plan provided"}), 400
    try:
        docx_bytes = generate_plan_docx(plan)
        title = plan.get("title", "Treatment Plan").replace(" ", "_")[:60]
        return send_file(
            io.BytesIO(docx_bytes),
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name=f"Treasury_Aesthetics_{title}.docx",
        )
    except Exception as e:
        print(f"[export] error: {e}")
        return jsonify({"error": f"Export failed: {e}"}), 500


@app.route("/api/publish-page", methods=["POST"])
def publish_page():
    auth = request.headers.get("Authorization", "")
    expected = os.environ.get("PUBLISH_TOKEN", "")
    if not expected or auth != f"Bearer {expected}":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    slug = (data.get("slug") or "").strip().lower()
    html = data.get("html")

    if not SLUG_RE.match(slug):
        return jsonify({"error": "Invalid slug — use lowercase letters, numbers, and hyphens only."}), 400
    if not html or not isinstance(html, str):
        return jsonify({"error": "No html provided"}), 400

    path = os.path.join(PAGES_DIR, f"{slug}.html")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
    except OSError as e:
        return jsonify({"error": f"Could not write page: {e}"}), 500

    domain = os.environ.get("APP_DOMAIN", request.host)
    return jsonify({"ok": True, "url": f"https://{domain}/{slug}.html"})


# ── Patient plans (structured, editable, DOB-protected) ──────────────────────

def _staff_authorized() -> bool:
    expected = os.environ.get("PUBLISH_TOKEN", "")
    auth = request.headers.get("Authorization", "")
    return bool(expected) and auth == f"Bearer {expected}"


@app.route("/staff")
def staff_dashboard():
    return render_template("staff.html")


@app.route("/p/<slug>")
def patient_plan_page(slug):
    slug = slug.lower()
    if not patient_plans.SLUG_RE.match(slug) or not patient_plans.load_plan(slug):
        abort(404)
    return render_template("plan_view.html", slug=slug)


@app.route("/api/staff/plans", methods=["GET"])
def staff_list_plans():
    if not _staff_authorized():
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"plans": patient_plans.list_plans()})


@app.route("/api/staff/plans/<slug>", methods=["GET", "PUT", "DELETE"])
def staff_plan(slug):
    if not _staff_authorized():
        return jsonify({"error": "Unauthorized"}), 401
    slug = slug.lower()

    if request.method == "GET":
        plan = patient_plans.load_plan(slug)
        if not plan:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"plan": plan})

    if request.method == "DELETE":
        if not patient_plans.delete_plan(slug):
            return jsonify({"error": "Not found"}), 404
        return jsonify({"ok": True})

    data = request.get_json(silent=True) or {}
    data["slug"] = slug
    plan, err = patient_plans.normalize_plan(data)
    if err:
        return jsonify({"error": err}), 400
    saved = patient_plans.save_plan(plan)
    domain = os.environ.get("APP_DOMAIN", request.host)
    return jsonify({"ok": True, "plan": saved, "url": f"https://{domain}/p/{slug}"})


@app.route("/api/staff/plans/publish", methods=["POST"])
def staff_publish_plan():
    """Publish a chat-built plan as a patient page: Claude restructures it
    into the patient-facing format (technologies/timelines, pre/post care,
    products with generic descriptors); a deterministic fallback mapping is
    used if that call fails, so publishing always succeeds."""
    if not _staff_authorized():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    chat_plan = data.get("plan")
    patient = data.get("patient") or {}
    name = (patient.get("name") or "").strip()
    dob = (patient.get("dob") or "").strip()
    concern = (data.get("concern") or "").strip()
    slug = (data.get("slug") or "").strip().lower() or patient_plans.slugify(name)

    if not chat_plan or not isinstance(chat_plan, dict):
        return jsonify({"error": "No plan provided"}), 400

    structured = None
    structure_error = None
    if agent is not None:
        try:
            structured = agent.structure_patient_plan(chat_plan, name, concern)
        except Exception as e:
            structure_error = str(e)
            print(f"[publish-plan] structuring failed, using fallback: {e}")

    if structured is None:
        structured = _fallback_patient_structure(chat_plan)

    payload = {
        "slug": slug,
        "patient": {"name": name, "dob": dob},
        "concern": concern,
        "title": structured.get("title") or chat_plan.get("title"),
        "overview": structured.get("overview", ""),
        "technologies": structured.get("technologies", []),
        "pre_care": structured.get("pre_care", []),
        "post_care": structured.get("post_care", []),
        "products": structured.get("products", []),
    }
    plan, err = patient_plans.normalize_plan(payload)
    if err:
        return jsonify({"error": err}), 400
    saved = patient_plans.save_plan(plan)
    domain = os.environ.get("APP_DOMAIN", request.host)
    return jsonify({
        "ok": True,
        "slug": saved["slug"],
        "url": f"https://{domain}/p/{saved['slug']}",
        "edit_url": f"https://{domain}/staff#edit={saved['slug']}",
        "used_fallback": structure_error is not None or agent is None,
    })


_PRODUCT_SECTIONS = ("morning routine", "evening routine", "post-procedure recovery")


def _fallback_patient_structure(chat_plan: dict) -> dict:
    """Deterministic mapping of a chat plan into the patient page shape,
    used when the Claude structuring call is unavailable."""
    technologies, products = [], []
    for section in chat_plan.get("sections") or []:
        sec_name = (section.get("name") or "").strip()
        is_product_section = sec_name.lower() in _PRODUCT_SECTIONS
        for item in section.get("items") or []:
            name = (item.get("name") or "").strip()
            if not name:
                continue
            entry_optional = item.get("checked") is False
            if is_product_section:
                products.append({
                    "brand_name": name,
                    "generic_name": "Equivalent product of your choice",
                    "detail": f"{sec_name}: {item.get('detail', '')}".strip(": "),
                    "optional": entry_optional,
                })
            elif sec_name.lower() != "membership":
                technologies.append({
                    "name": name,
                    "why": "",
                    "timeline": item.get("detail", ""),
                    "optional": entry_optional,
                })
    return {
        "title": chat_plan.get("title", "Treatment Plan"),
        "overview": "",
        "technologies": technologies,
        "pre_care": [],
        "post_care": [],
        "products": products,
    }


@app.route("/api/plans/<slug>/unlock", methods=["POST"])
def unlock_plan(slug):
    slug = slug.lower()
    plan = patient_plans.load_plan(slug)
    if not plan:
        return jsonify({"error": "Not found"}), 404
    if patient_plans.is_throttled(slug):
        return jsonify({"error": "Too many attempts — please try again later or contact the clinic."}), 429

    data = request.get_json(silent=True) or {}
    if not patient_plans.verify_dob(plan, data.get("dob", "")):
        return jsonify({"error": "That date of birth doesn't match our records."}), 403

    return jsonify({
        "token": patient_plans.issue_unlock_token(slug),
        "plan": patient_plans.public_plan(plan),
    })


@app.route("/api/plans/<slug>/preferences", methods=["POST"])
def plan_preferences(slug):
    """Persist the patient's per-product 'use my own instead' choices.
    Requires the signed token issued by a successful DOB unlock."""
    slug = slug.lower()
    plan = patient_plans.load_plan(slug)
    if not plan:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json(silent=True) or {}
    if not patient_plans.verify_unlock_token(slug, data.get("token", "")):
        return jsonify({"error": "Unauthorized"}), 401

    choices = data.get("use_generic")
    if not isinstance(choices, dict):
        return jsonify({"error": "No preferences provided"}), 400

    products = plan.get("products", [])
    for key, value in choices.items():
        try:
            idx = int(key)
        except (TypeError, ValueError):
            continue
        if 0 <= idx < len(products):
            products[idx]["use_generic"] = bool(value)

    patient_plans.save_plan(plan)
    return jsonify({"ok": True, "plan": patient_plans.public_plan(plan)})


@app.route("/<slug>.html")
def serve_page(slug):
    slug = slug.lower()
    if not SLUG_RE.match(slug):
        abort(404)
    path = os.path.join(PAGES_DIR, f"{slug}.html")
    if not os.path.isfile(path):
        abort(404)
    with open(path, "r", encoding="utf-8") as f:
        return Response(f.read(), mimetype="text/html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
