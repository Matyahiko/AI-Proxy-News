#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: run_demo.sh <audio_file>"
  exit 1
fi

AUDIO="$1"
TRANSCRIPT="data/transcript.txt"
OUTDIR="output"

echo "Step 1/3: Running speech-to-text"
python3 scripts/asr.py "$AUDIO" "$TRANSCRIPT"

echo "Step 2/3: Generating summary and questions"
python3 scripts/gpt_chain.py "$TRANSCRIPT" "$OUTDIR"

echo "Step 3/3: Signing article"
python3 scripts/sign_article.py "$OUTDIR/article.md" "$OUTDIR/article_signed.md"

cp "$OUTDIR/article_signed.md" docs/

echo "Demo complete. Signed article copied to docs/."
