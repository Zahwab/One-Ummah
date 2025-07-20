#!/usr/bin/env python3
import os
import glob
import json
import sys
from pdf2image import convert_from_path

# ─── 1) Compute paths ───────────────────────────────────────────────
script_dir   = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, ".."))

PDF_DIR      = os.path.join(project_root, "pdfs")
THUMB_DIR    = os.path.join(project_root, "public", "thumbnails")
MANIFEST_FP  = os.path.join(project_root, "public", "books.json")

print(f"DEBUG: cwd.............. {os.getcwd()}")
print(f"DEBUG: script_dir....... {script_dir}")
print(f"DEBUG: project_root..... {project_root}")
print(f"DEBUG: PDF_DIR.......... {PDF_DIR}")
print(f"DEBUG: PDF_DIR exists?.. {os.path.exists(PDF_DIR)}")
if not os.path.exists(PDF_DIR):
    print("ERROR: PDF_DIR doesn’t exist. Check your folder name or location.")
    sys.exit(1)

# ─── 2) Find PDFs ───────────────────────────────────────────────────
pattern  = os.path.join(PDF_DIR, "**", "*.pdf")
all_pdfs = sorted(glob.glob(pattern, recursive=True))
print(f"DEBUG: Glob pattern..... {pattern}")
print(f"DEBUG: Found {len(all_pdfs)} PDF(s)")

for p in all_pdfs[:5]:
    print("  →", p)

if not all_pdfs:
    print("ERROR: No PDFs were found. Exiting without writing JSON.")
    sys.exit(1)

# ─── 3) Ensure thumbnail folder ─────────────────────────────────────
os.makedirs(THUMB_DIR, exist_ok=True)
print(f"DEBUG: THUMB_DIR created {THUMB_DIR}")

# ─── 4) Build manifest ─────────────────────────────────────────────
manifest = []
for pdf_path in all_pdfs:
    name      = os.path.splitext(os.path.basename(pdf_path))[0]
    rel_pdf   = pdf_path.replace("\\", "/")
    size_str  = f"{os.path.getsize(pdf_path)/(1024*1024):.2f} MB"
    thumb_fp  = os.path.join(THUMB_DIR, f"{name}.webp")
    thumb_rel = thumb_fp.replace("\\", "/").split("public/")[-1]

    if not os.path.exists(thumb_fp):
        try:
            page = convert_from_path(pdf_path, dpi=80, first_page=1, last_page=1)[0]
            page.save(thumb_fp, "WEBP", quality=80)
            print(f"🖼️ Thumb created: {thumb_rel}")
        except Exception as e:
            print(f"⚠️ Thumb fail for {name}: {e}")

    manifest.append({
        "thumb": thumb_rel,
        "name":  name,
        "file":  rel_pdf,
        "size":  size_str
    })

# ─── 5) Write JSON ─────────────────────────────────────────────────
with open(MANIFEST_FP, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)
print(f"\n✅ Wrote manifest with {len(manifest)} entries → {MANIFEST_FP}")