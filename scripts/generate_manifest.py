#!/usr/bin/env python3
import os, glob, json
from pdf2image import convert_from_path

# ─── ROOT & PATHS ─────────────────────────────────────────────
ROOT        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR     = os.path.join(ROOT, "pdfs")
THUMB_DIR   = os.path.join(ROOT, "public", "thumbnails")
MANIFEST_FP = os.path.join(ROOT, "public", "books.json")
os.makedirs(THUMB_DIR, exist_ok=True)

# ─── SCAN FOR PDFS ────────────────────────────────────────────
all_pdfs = sorted(glob.glob(os.path.join(PDF_DIR, "**", "*.pdf"), recursive=True))
print(f"📁 Found {len(all_pdfs)} PDFs")

# ─── BUILD MANIFEST ──────────────────────────────────────────
manifest = []
for pdf_path in all_pdfs:
    name       = os.path.splitext(os.path.basename(pdf_path))[0]
    rel_pdf    = os.path.relpath(pdf_path, ROOT).replace("\\", "/")
    size_mb    = os.path.getsize(pdf_path) / (1024 * 1024)
    size_str   = f"{size_mb:.2f} MB"
    thumb_fp   = os.path.join(THUMB_DIR, f"{name}.webp")
    thumb_rel  = os.path.relpath(thumb_fp, ROOT).replace("\\", "/")

    if not os.path.exists(thumb_fp):
        try:
            img = convert_from_path(pdf_path, dpi=100, first_page=1, last_page=1)[0]
            img.save(thumb_fp, format="WEBP", quality=80)
            print(f"🖼️ Created thumbnail for {name}")
        except Exception as e:
            print(f"⚠️ Thumbnail failed for {name}: {e}")

    manifest.append({
        "thumb": thumb_rel,
        "name":  name,
        "file":  rel_pdf,
        "size":  size_str
    })

# ─── WRITE JSON ──────────────────────────────────────────────
with open(MANIFEST_FP, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(f"\n✅ Manifest saved with {len(manifest)} entries → {MANIFEST_FP}")