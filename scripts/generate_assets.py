#!/usr/bin/env python3
import os, glob, json, subprocess
from pdf2image import convert_from_path

# ─── PATH SETUP ────────────────────────────────────────────────
THIS_SCRIPT  = os.path.abspath(__file__)
PROJECT_ROOT = os.path.dirname(os.path.dirname(THIS_SCRIPT))

LLAMA_CLI    = os.path.join(PROJECT_ROOT, "llama.exe")
LLAMA_MODEL  = os.path.join(PROJECT_ROOT, "models", "llama-2-7b-chat.gguf")
PDF_DIR      = os.path.join(PROJECT_ROOT, "pdfs")
THUMB_DIR    = os.path.join(PROJECT_ROOT, "public", "thumbnails")
MANIFEST_FP  = os.path.join(PROJECT_ROOT, "public", "books.json")
CHUNK_SIZE   = 25
os.makedirs(THUMB_DIR, exist_ok=True)

# ─── BATCH & PROCESS ───────────────────────────────────────────
all_pdfs = sorted(glob.glob(os.path.join(PDF_DIR, "**", "*.pdf"), recursive=True))
batches  = [all_pdfs[i:i+CHUNK_SIZE] for i in range(0, len(all_pdfs), CHUNK_SIZE)]
manifest = []

for idx, batch in enumerate(batches, start=1):
    print(f"📦 Batch {idx}/{len(batches)}")
    book_list = [{
        "name": os.path.splitext(os.path.basename(p))[0],
        "file": os.path.relpath(p, PROJECT_ROOT).replace("\\", "/")
    } for p in batch]

    prompt = f"""
You are a formatting assistant. Given this JSON array:
{json.dumps(book_list, indent=2)}

Return ONLY a valid JSON array of objects with keys in this exact order:
1. thumb ("thumbnails/<name>.webp")
2. name
3. file
4. size ("X.XX MB")

No extra text or explanation.
""".strip()

    with open("prompt.txt", "w", encoding="utf-8") as pf:
        pf.write(prompt)

    proc = subprocess.run([
        LLAMA_CLI, "-m", LLAMA_MODEL,
        "-f", "prompt.txt", "-n", "512",
        "-t", str(max(1, os.cpu_count() // 2)),
        "--temp", "0.0", "--no-display-prompt", "--simple-io"
    ], capture_output=True, text=True)

    os.remove("prompt.txt")
    if proc.returncode != 0 or not proc.stdout.strip():
        print(f"🔴 LLaMA error:\n{proc.stderr}")
        continue

    raw = proc.stdout.strip().replace("\\\\", "/").replace("\\", "/")
    try:
        entries = json.loads(raw)
    except Exception as e:
        print(f"🔴 JSON parse error: {e}")
        continue

    for entry in entries:
        name      = entry["name"]
        size      = entry["size"]
        pdf_path  = next(p for p in batch if os.path.splitext(os.path.basename(p))[0] == name)
        pdf_url   = os.path.relpath(pdf_path, PROJECT_ROOT).replace("\\", "/")
        thumb_fp  = os.path.join(THUMB_DIR, f"{name}.webp")
        thumb_rel = os.path.relpath(thumb_fp, PROJECT_ROOT).replace("\\", "/")

        if not os.path.exists(thumb_fp):
            try:
                img = convert_from_path(pdf_path, dpi=150, first_page=1, last_page=1)[0]
                img.save(thumb_fp, format="WEBP", quality=80)
                print(f"🖼️ Created thumbnail: {thumb_rel}")
            except Exception as ex:
                print(f"⚠️ Thumb error for {name}: {ex}")

        manifest.append({
            "thumb": thumb_rel,
            "name":  name,
            "file":  pdf_url,
            "size":  size
        })

# ─── WRITE FINAL MANIFEST ─────────────────────────────────────
with open(MANIFEST_FP, "w", encoding="utf-8") as out:
    json.dump(manifest, out, indent=2)

print(f"\n✅ Indexed {len(manifest)} PDFs → {MANIFEST_FP}")