"""
Extract text from a PDF and save it into the knowledge directory,
then optionally commit + push it to GitHub so the agent picks it up on next startup.

Usage:
    python load_pdf.py path/to/your_file.pdf [--no-push]

The extracted text is saved to knowledge/<filename>.txt.
If GITHUB_KNOWLEDGE_REPO is set in .env (and git is available), it will
also commit and push the new file to the repo automatically.
"""

import os
import sys
import subprocess
from pathlib import Path
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


def extract_pdf(pdf_path: str) -> tuple[str, str]:
    """Return (text, stem) from the PDF."""
    src = Path(pdf_path)
    if not src.exists():
        print(f"File not found: {pdf_path}")
        sys.exit(1)

    reader = PdfReader(str(src))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n\n".join(p.strip() for p in pages if p.strip())

    if not text:
        print("No text extracted. The PDF may be scanned (image-only).")
        print("Run it through an OCR tool first (e.g. Adobe Acrobat online → export as Word/text),")
        print("then save as .txt and drop into knowledge/ manually.")
        sys.exit(1)

    print(f"Extracted {len(reader.pages)} pages from {src.name}")
    return text, src.stem


def save_to_knowledge(text: str, stem: str) -> Path:
    KNOWLEDGE_DIR.mkdir(exist_ok=True)
    out = KNOWLEDGE_DIR / f"{stem}.txt"
    out.write_text(text, encoding="utf-8")
    print(f"Saved → {out}")
    return out


def git_push(out_file: Path) -> None:
    repo = os.environ.get("GITHUB_KNOWLEDGE_REPO", "").strip()
    if not repo:
        print("GITHUB_KNOWLEDGE_REPO not set — skipping git push.")
        print("Restart the app to load the new knowledge from the local file.")
        return

    rel = out_file.relative_to(Path(__file__).parent)
    try:
        subprocess.run(["git", "add", str(rel)], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Add knowledge: {out_file.name}"],
            check=True,
        )
        subprocess.run(["git", "push"], check=True)
        print(f"Pushed {out_file.name} to GitHub ({repo}).")
        print("The agent will load it automatically on next startup.")
    except subprocess.CalledProcessError as e:
        print(f"Git step failed: {e}")
        print("The file was saved locally. Push it manually with: git add . && git commit -m 'Add knowledge' && git push")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]

    if not args:
        print("Usage: python load_pdf.py path/to/file.pdf [--no-push]")
        sys.exit(1)

    text, stem = extract_pdf(args[0])
    out_file = save_to_knowledge(text, stem)

    if "--no-push" not in flags:
        git_push(out_file)
    else:
        print("Skipped git push (--no-push). Restart the app to load the new knowledge.")
