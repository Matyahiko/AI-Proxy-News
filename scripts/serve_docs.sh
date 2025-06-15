#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-7000}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="${SCRIPT_DIR}/.."
DOCS_DIR="${ROOT_DIR}/docs/site"
DATA_DIR="${ROOT_DIR}/data"

# Expose data directory inside docs for the HTTP server
if [ ! -e "${DOCS_DIR}/data" ]; then
  ln -s ../../data "${DOCS_DIR}/data"
fi

# Generate a simple JSON listing of available video files
python3 - "$DATA_DIR" "${DOCS_DIR}/assets/data/video_list.json" <<'EOF'
import json, os, sys
data_dir = sys.argv[1]
out_path = sys.argv[2]
videos = [f for f in os.listdir(data_dir)
          if f.lower().endswith(('.mp4', '.mov', '.webm'))]
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(videos, f)
EOF

cd "$DOCS_DIR"
echo "Serving demo site on http://localhost:${PORT}/demo.html"
python3 -m http.server "$PORT" &
SERVER_PID=$!
sleep 1
python3 - <<EOF
import webbrowser
webbrowser.open(f"http://localhost:${PORT}/demo.html")
EOF
wait $SERVER_PID
