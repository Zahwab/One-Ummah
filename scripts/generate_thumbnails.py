#!/usr/bin/env python3
import os, glob
import fitz            # PyMuPDF
from PIL import Image  # pip install Pillow

# ─── ROOT PATHS ──────────────────────────────────────────────
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT       = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

PDF_DIR    = os.path.join(ROOT, "pdfs")
THUMB_DIR  = os.path.join(ROOT, "public", "thumbnails")
os.makedirs(THUMB_DIR, exist_ok=True)

# ─── SCAN PDF FILES ──────────────────────────────────────────
pdfs = sorted(glob.glob(os.path.join(PDF_DIR, "**", "*.pdf"), recursive=True))
print(f"🔍 Found {len(pdfs)} PDFs\n")

# ─── THUMBNAIL CREATION ─────────────────────────────────────
created = 0
for pdf_path in pdfs:
    name      = os.path.splitext(os.path.basename(pdf_path))[0]
    thumb_fp  = os.path.join(THUMB_DIR, f"{name}.webp")

    if os.path.exists(thumb_fp):
        continue

    try:
        doc  = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix  = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        img  = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.save(thumb_fp, "WEBP", quality=80)
        thumb_rel = os.path.relpath(thumb_fp, ROOT).replace("\\", "/")
        print(f"🖼️ Created: {thumb_rel}")
        created += 1
    except Exception as e:
        print(f"⚠️ Failed for {name}: {e}")

# ─── DONE ───────────────────────────────────────────────────
print(f"\n✅ Saved {created} thumbnails to public/thumbnails/")