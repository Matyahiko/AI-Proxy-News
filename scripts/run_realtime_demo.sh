#!/usr/bin/env bash
set -euo pipefail

DOCS_PORT="${1:-8000}"
ASR_PORT="${2:-8765}"
export ASR_PORT

python3 scripts/realtime_server.py &
ASR_PID=$!

trap 'kill $ASR_PID' EXIT

bash scripts/serve_docs.sh "$DOCS_PORT"
