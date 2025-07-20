#!/usr/bin/env python3
import os, glob, json
from pdf2image import convert_from_path

# ─── ROOT PATH SETUP ───────────────────────────────────────────────
ROOT         = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR      = os.path.join(ROOT, "pdfs")
THUMB_DIR    = os.path.join(ROOT, "public", "thumbnails")
MANIFEST_FP  = os.path.join(ROOT, "public", "books.json")
os.makedirs(THUMB_DIR, exist_ok=True)

# ─── SCAN FOR PDF FILES ────────────────────────────────────────────
all_pdfs = sorted(glob.glob(f"{PDF_DIR}/**/*.pdf", recursive=True))
print(f"📁 Found {len(all_pdfs)} PDFs")

# ─── BUILD MANIFEST ENTRIES ────────────────────────────────────────
manifest = []
for pdf_path in all_pdfs:
    name       = os.path.splitext(os.path.basename(pdf_path))[0]
    rel_pdf    = pdf_path.replace("\\", "/").split("public/")[-1]
    size_mb    = os.path.getsize(pdf_path) / (1024 * 1024)
    size_str   = f"{size_mb:.2f} MB"
    thumb_fp   = os.path.join(THUMB_DIR, f"{name}.webp")
    thumb_rel  = thumb_fp.replace("\\", "/").split("public/")[-1]

    # Create thumbnail if it doesn't exist
    if not os.path.exists(thumb_fp):
        try:
            page = convert_from_path(pdf_path, dpi=100, first_page=1, last_page=1)[0]
            page.save(thumb_fp, format="WEBP", quality=80)
            print(f"🖼️ Created thumbnail for: {name}")
        except Exception as e:
            print(f"⚠️ Failed to generate thumbnail for {name}: {e}")

    manifest.append({
        "thumb": thumb_rel,
        "name":  name,
        "file":  rel_pdf,
        "size":  size_str
    })

# ─── WRITE TO JSON FILE ────────────────────────────────────────────
with open(MANIFEST_FP, "w", encoding="utf-8") as out:
    json.dump(manifest, out, indent=2)

print(f"\n✅ Manifest saved with {len(manifest)} entries → {MANIFEST_FP}")