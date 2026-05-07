"""
Loads knowledge files from a GitHub repository folder at startup.

Required env vars:
  GITHUB_KNOWLEDGE_REPO   — e.g. "drlatsky-aesthetics/Skincare"
  GITHUB_KNOWLEDGE_PATH   — folder within the repo, e.g. "knowledge"
  GITHUB_TOKEN            — personal access token (needed for private repos;
                             optional for public repos but avoids rate limits)

Falls back to local knowledge/ directory if GitHub vars are not set.
"""

import os
import requests
from pathlib import Path

GITHUB_API = "https://api.github.com"
LOCAL_KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


def _github_headers() -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _fetch_github_knowledge(repo: str, path: str) -> str:
    """Fetch all .md and .txt files from a GitHub repo folder via the API."""
    url = f"{GITHUB_API}/repos/{repo}/contents/{path}"
    resp = requests.get(url, headers=_github_headers(), timeout=10)
    resp.raise_for_status()

    chunks = []
    for item in sorted(resp.json(), key=lambda x: x["name"]):
        name: str = item["name"]
        if item["type"] != "file" or not (name.endswith(".md") or name.endswith(".txt")):
            continue

        file_resp = requests.get(item["download_url"], headers=_github_headers(), timeout=10)
        file_resp.raise_for_status()
        content = file_resp.text.strip()
        if content:
            stem = Path(name).stem.replace("_", " ").title()
            chunks.append(f"=== {stem} ===\n{content}")
            print(f"  [knowledge] loaded from GitHub: {name}")

    return "\n\n".join(chunks)


def _fetch_local_knowledge() -> str:
    """Read all .md and .txt files from the local knowledge/ directory."""
    if not LOCAL_KNOWLEDGE_DIR.exists():
        return ""
    chunks = []
    for ext in ("*.md", "*.txt"):
        for f in sorted(LOCAL_KNOWLEDGE_DIR.glob(ext)):
            content = f.read_text(encoding="utf-8").strip()
            if content:
                stem = f.stem.replace("_", " ").title()
                chunks.append(f"=== {stem} ===\n{content}")
                print(f"  [knowledge] loaded locally: {f.name}")
    return "\n\n".join(chunks)


def load_knowledge() -> str:
    """
    Load knowledge at startup.
    Prefers GitHub if GITHUB_KNOWLEDGE_REPO + GITHUB_KNOWLEDGE_PATH are set,
    otherwise falls back to local knowledge/ directory.
    """
    repo = os.environ.get("GITHUB_KNOWLEDGE_REPO", "").strip()
    path = os.environ.get("GITHUB_KNOWLEDGE_PATH", "knowledge").strip()

    if repo:
        print(f"[knowledge] fetching from GitHub: {repo}/{path}")
        try:
            result = _fetch_github_knowledge(repo, path)
            if result:
                return result
            print("[knowledge] GitHub folder was empty — falling back to local files.")
        except Exception as exc:
            print(f"[knowledge] GitHub fetch failed ({exc}) — falling back to local files.")

    print("[knowledge] loading from local knowledge/ directory.")
    return _fetch_local_knowledge()
