#!/usr/bin/env python3
import os
import glob
import json
import subprocess
from pdf2image import convert_from_path

# ─── CONFIG ─────────────────────────────────────────────────────────
LLAMA_CLI   = r".\llama.exe"                         # your local llama.cpp binary
LLAMA_MODEL = "models/llama-2-7b-chat.gguf"
PDF_DIR     = "pdfs"
THUMB_DIR   = "public/thumbnails"
MANIFEST_FP = "public/books.json"
CHUNK_SIZE  = 25

# ─── ENSURE OUTPUT FOLDERS EXIST ───────────────────────────────────
os.makedirs(THUMB_DIR, exist_ok=True)

# ─── COLLECT & BATCH PDF FILES ──────────────────────────────────────
all_pdfs = sorted(glob.glob(f"{PDF_DIR}/**/*.pdf", recursive=True))
batches  = [all_pdfs[i : i + CHUNK_SIZE] for i in range(0, len(all_pdfs), CHUNK_SIZE)]
manifest = []

print(f"🔍 Found {len(all_pdfs)} PDFs → {len(batches)} batches of up to {CHUNK_SIZE}")

# ─── PROCESS EACH BATCH ─────────────────────────────────────────────
for idx, batch in enumerate(batches, start=1):
    print(f"\n📦 Batch {idx}/{len(batches)}")

    # Build minimal JSON list for the prompt
    book_list = []
    for pdf_path in batch:
        name = os.path.splitext(os.path.basename(pdf_path))[0]
        book_list.append({
            "name": name,
            "file": pdf_path.replace("\\", "/")
        })

    prompt = f"""
You are a formatting assistant. Given this JSON array:
{json.dumps(book_list, indent=2)}

Return ONLY a valid JSON array of objects with keys in this order:
1. thumb ("thumbnails/<name>.webp")
2. name
3. file
4. size ("X.XX MB")

No extra text or explanation.
""".strip()

    # Write prompt to temporary file
    with open("prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    # Invoke llama.exe with supported flags
    proc = subprocess.run([
        LLAMA_CLI,
        "-m",    LLAMA_MODEL,
        "-f",    "prompt.txt",
        "-n",    "512",
        "-t",    str(max(1, os.cpu_count() // 2)),
        "--temp","0.0",
        "--no-display-prompt",
        "--simple-io"
    ], capture_output=True, text=True)

    # Clean up prompt file
    os.remove("prompt.txt")

    if proc.returncode != 0:
        print(f"🔴 LLaMA failed (exit {proc.returncode}):\n{proc.stderr}")
        continue

    raw = proc.stdout.strip().replace("\\\\", "/").replace("\\", "/")
    print(f"📤 Raw stdout snippet: {raw[:200]!r}")

    # Parse JSON
    try:
        entries = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"🔴 JSON parse error: {e}")
        continue

    # Generate thumbnails and append manifest entries
    for entry in entries:
        name, size = entry["name"], entry["size"]
        pdf_path = next(
            p for p in batch
            if os.path.splitext(os.path.basename(p))[0] == name
        )
        pdf_url   = pdf_path.replace("\\", "/")
        thumb_rel = f"thumbnails/{name}.webp"
        thumb_fp  = os.path.join(THUMB_DIR, f"{name}.webp")

        if not os.path.exists(thumb_fp):
            try:
                img = convert_from_path(pdf_path, dpi=150, first_page=1, last_page=1)[0]
                img.save(thumb_fp, format="WEBP", quality=80)
                print(f"🖼️ Created thumbnail for {name}")
            except Exception as e:
                print(f"⚠️ Thumbnail failed for {name}: {e}")

        manifest.append({
            "thumb": thumb_rel,
            "name":  name,
            "file":  pdf_url,
            "size":  size
        })

# ─── WRITE FINAL MANIFEST ────────────────────────────────────────────
print(f"\n📘 Total entries: {len(manifest)}")
with open(MANIFEST_FP, "w", encoding="utf-8") as out_f:
    json.dump(manifest, out_f, indent=2)

print(f"✅ Indexed {len(manifest)} PDFs → {MANIFEST_FP}")