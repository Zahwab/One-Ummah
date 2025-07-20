#!/usr/bin/env python3
import os, glob
import fitz   # PyMuPDF

# 👇 This always sets ROOT to repo root no matter where script lives
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT       = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PDF_DIR    = os.path.join(ROOT, "pdfs")
THUMB_DIR  = os.path.join(ROOT, "public", "thumbnails")

os.makedirs(THUMB_DIR, exist_ok=True)

pdfs = sorted(glob.glob(os.path.join(PDF_DIR, "**", "*.pdf"), recursive=True))
print(f"🔍 Found {len(pdfs)} PDFs")

for pdf_path in pdfs:
    name     = os.path.splitext(os.path.basename(pdf_path))[0]
    thumb_fp = os.path.join(THUMB_DIR, f"{name}.webp")
    if os.path.exists(thumb_fp):
        continue

    try:
        doc  = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix  = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        pix.save(thumb_fp, output="webp", quality=80)
        print(f"🖼️ Created thumbnail for {name}")
    except Exception as e:
        print(f"⚠️ Failed for {name}: {e}")

print("✅ All thumbnails generated.")