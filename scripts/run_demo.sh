#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: run_demo.sh <wav_file>"
  exit 1
fi

WAV="$1"
TRANSCRIPT="data/transcript.txt"
OUTDIR="output"

python3 scripts/asr.py "$WAV" "$TRANSCRIPT"
python3 scripts/gpt_chain.py "$TRANSCRIPT" "$OUTDIR"
python3 scripts/sign_article.py "$OUTDIR/article.md" "$OUTDIR/article_signed.md"

cp "$OUTDIR/article_signed.md" docs/

echo "Demo complete. Signed article copied to docs/."
