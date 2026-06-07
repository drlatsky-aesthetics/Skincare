"""
Loads knowledge files at startup from one of three sources (in priority order):

  1. Google Drive folder  — set GOOGLE_DRIVE_FOLDER_ID + GOOGLE_API_KEY
  2. GitHub repo folder   — set GITHUB_KNOWLEDGE_REPO (+ optional GITHUB_KNOWLEDGE_PATH, GITHUB_TOKEN)
  3. Local knowledge/     — always available as fallback

Google Drive setup (one-time, ~2 min):
  a. Go to https://console.cloud.google.com/ → New project
  b. Enable "Google Drive API"
  c. Create an API key (Credentials → Create Credentials → API key)
  d. Add to .env:
       GOOGLE_DRIVE_FOLDER_ID=1MmTsBm_Y9AgIbfr1u6ds7KayUo7Vf44k
       GOOGLE_API_KEY=your_key_here
  e. Make sure the Drive folder sharing is set to "Anyone with the link"

Supported file types in Drive: .pdf, .md, .txt
PDFs are extracted with pypdf. Text/Markdown are read directly.
"""

import io
import os
import requests
from pathlib import Path

GITHUB_API  = "https://api.github.com"
GDRIVE_API  = "https://www.googleapis.com/drive/v3"
LOCAL_DIR   = Path(__file__).parent / "knowledge"


# ── Google Drive ──────────────────────────────────────────────────────────────

def _gdrive_list_files(folder_id: str, api_key: str) -> list[dict]:
    """Return metadata for all supported files in the Drive folder."""
    params = {
        "q": f"'{folder_id}' in parents and trashed = false",
        "fields": "files(id,name,mimeType)",
        "key": api_key,
        "pageSize": 100,
    }
    resp = requests.get(f"{GDRIVE_API}/files", params=params, timeout=15)
    resp.raise_for_status()
    return resp.json().get("files", [])


def _gdrive_download(file_id: str, api_key: str) -> bytes:
    """Download a file's raw bytes from Drive."""
    params = {"alt": "media", "key": api_key}
    resp = requests.get(f"{GDRIVE_API}/files/{file_id}", params=params, timeout=30)
    resp.raise_for_status()
    return resp.content


def _extract_pdf_bytes(data: bytes) -> str:
    """Extract text from PDF bytes using pypdf."""
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(p.strip() for p in pages if p.strip())


def _fetch_gdrive_knowledge(folder_id: str, api_key: str) -> str:
    files = _gdrive_list_files(folder_id, api_key)
    supported = [
        f for f in files
        if any(f["name"].lower().endswith(ext) for ext in (".pdf", ".md", ".txt"))
    ]
    if not supported:
        print("  [knowledge] Google Drive folder is empty or has no supported files (.pdf/.md/.txt).")
        return ""

    chunks = []
    for f in sorted(supported, key=lambda x: x["name"]):
        name  = f["name"]
        stem  = Path(name).stem.replace("_", " ").title()
        try:
            data = _gdrive_download(f["id"], api_key)
            if name.lower().endswith(".pdf"):
                text = _extract_pdf_bytes(data)
            else:
                text = data.decode("utf-8", errors="replace")
            text = text.strip()
            if text:
                chunks.append(f"=== {stem} ===\n{text}")
                print(f"  [knowledge] loaded from Google Drive: {name}")
            else:
                print(f"  [knowledge] skipped (no text extracted): {name}")
        except Exception as exc:
            print(f"  [knowledge] failed to load {name}: {exc}")

    return "\n\n".join(chunks)


# ── GitHub ────────────────────────────────────────────────────────────────────

def _github_headers() -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    h = {"Accept": "application/vnd.github+json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _fetch_github_knowledge(repo: str, path: str) -> str:
    url  = f"{GITHUB_API}/repos/{repo}/contents/{path}"
    resp = requests.get(url, headers=_github_headers(), timeout=10)
    resp.raise_for_status()

    chunks = []
    for item in sorted(resp.json(), key=lambda x: x["name"]):
        name: str = item["name"]
        if item["type"] != "file" or not (name.endswith(".md") or name.endswith(".txt")):
            continue
        fr = requests.get(item["download_url"], headers=_github_headers(), timeout=10)
        fr.raise_for_status()
        text = fr.text.strip()
        if text:
            stem = Path(name).stem.replace("_", " ").title()
            chunks.append(f"=== {stem} ===\n{text}")
            print(f"  [knowledge] loaded from GitHub: {name}")

    return "\n\n".join(chunks)


# ── Local fallback ────────────────────────────────────────────────────────────

def _fetch_local_knowledge() -> str:
    if not LOCAL_DIR.exists():
        return ""
    chunks = []
    # Recursively find all .md and .txt files so subdirectories work too
    for f in sorted(LOCAL_DIR.rglob("*.md")) + sorted(LOCAL_DIR.rglob("*.txt")):
        if f.name.startswith('.'):
            continue
        text = f.read_text(encoding="utf-8").strip()
        if text:
            stem = f.stem.replace("_", " ").title()
            chunks.append(f"=== {stem} ===\n{text}")
            print(f"  [knowledge] loaded locally: {f.relative_to(LOCAL_DIR)}")
    return "\n\n".join(chunks)


# ── Public entry point ────────────────────────────────────────────────────────

def load_knowledge() -> str:
    """
    Load all knowledge at startup.
    Priority: Google Drive → GitHub → local knowledge/ directory.
    """
    # 1. Google Drive
    folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "").strip()
    api_key   = os.environ.get("GOOGLE_API_KEY", "").strip()
    if folder_id and api_key:
        print(f"[knowledge] fetching from Google Drive folder: {folder_id}")
        try:
            result = _fetch_gdrive_knowledge(folder_id, api_key)
            if result:
                return result
            print("[knowledge] Drive folder empty — trying next source.")
        except Exception as exc:
            print(f"[knowledge] Google Drive fetch failed ({exc}) — trying next source.")

    # 2. GitHub
    repo = os.environ.get("GITHUB_KNOWLEDGE_REPO", "").strip()
    path = os.environ.get("GITHUB_KNOWLEDGE_PATH", "knowledge").strip()
    if repo:
        print(f"[knowledge] fetching from GitHub: {repo}/{path}")
        try:
            result = _fetch_github_knowledge(repo, path)
            if result:
                return result
            print("[knowledge] GitHub folder empty — falling back to local files.")
        except Exception as exc:
            print(f"[knowledge] GitHub fetch failed ({exc}) — falling back to local files.")

    # 3. Local
    print("[knowledge] loading from local knowledge/ directory.")
    return _fetch_local_knowledge()
