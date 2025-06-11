#!/usr/bin/env python3
import json
import hashlib
import os
import subprocess
import sys

if len(sys.argv) != 3:
    print("Usage: sign_article.py <article_md> <signed_md>")
    sys.exit(1)

article = sys.argv[1]
signed = sys.argv[2]
os.makedirs(os.path.dirname(signed), exist_ok=True)
print(f"[SIGN] Signing article '{article}'...")

with open("credo.json", "rb") as f:
    credo_bytes = f.read()
credo_hash = hashlib.sha256(credo_bytes).hexdigest()

with open(article, "rb") as f:
    article_bytes = f.read()
article_hash = hashlib.sha256(article_bytes).hexdigest()

manifest = {
    "credentials": {
        "credo_url": "https://github.com/<user>/ai-proxy-news/blob/main/credo.json",
        "transcript_sha256": article_hash,
        "llm_model": "gemini-2.5-pro-preview-06-05",
        "asr_model": "google-speech-to-text",
    },
    "cred_hash": credo_hash,
}

manifest_path = os.path.join(os.path.dirname(signed), "manifest.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

cmd = ["c2patool", article, signed, "--manifest", manifest_path]
subprocess.run(cmd, check=False)
print(f"[SIGN] Signed article written to '{signed}'")
