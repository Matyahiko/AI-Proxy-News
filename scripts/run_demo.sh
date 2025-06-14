#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: run_demo.sh <audio_file>"
  exit 1
fi

AUDIO="$1"
TRANSCRIPT="data/transcript.txt"
OUTDIR="output"

echo "Step 1/2: Running speech-to-text"
python3 scripts/asr.py "$AUDIO" "$TRANSCRIPT"

echo "Step 2/2: Generating summary and questions"
python3 scripts/gpt_chain.py "$TRANSCRIPT" "$OUTDIR"

cp "$OUTDIR/article.md" docs/site/

echo "Demo complete. Article copied to docs/site/."
