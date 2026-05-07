"""
Usage:
    python load_pdf.py path/to/your_file.pdf

Extracts text from a PDF and saves it to knowledge/<filename>.txt
so the agent loads it automatically on next startup.
"""

import sys
from pathlib import Path
from pypdf import PdfReader

def extract(pdf_path: str) -> None:
    src = Path(pdf_path)
    if not src.exists():
        print(f"File not found: {pdf_path}")
        sys.exit(1)

    reader = PdfReader(str(src))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n\n".join(p.strip() for p in pages if p.strip())

    if not text:
        print("No text could be extracted. The PDF may be image-based (scanned).")
        print("If so, run it through an OCR tool first, then save as .txt and drop into knowledge/")
        sys.exit(1)

    out_dir = Path(__file__).parent / "knowledge"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / (src.stem + ".txt")
    out_file.write_text(text, encoding="utf-8")

    print(f"Saved {len(reader.pages)} pages → {out_file}")
    print("Restart the app (python app.py) to load the new knowledge.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python load_pdf.py path/to/file.pdf")
        sys.exit(1)
    extract(sys.argv[1])
