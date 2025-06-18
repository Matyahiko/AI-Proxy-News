#!/usr/bin/env bash
set -euo pipefail

# Signal handler for graceful shutdown
cleanup() {
    echo "Shutting down HTTP server..."
    if [ -n "${SERVER_PID:-}" ]; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM EXIT

PORT="${1:-12000}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="${SCRIPT_DIR}/.."
DOCS_DIR="${ROOT_DIR}/docs/site"
DATA_DIR="${ROOT_DIR}/data"

# Expose data directory inside docs for the HTTP server
if [ ! -e "${DOCS_DIR}/data" ]; then
  ln -s ../../data "${DOCS_DIR}/data"
fi

# Generate a simple JSON listing of available video files
python3 scripts/utils.py generate_videos "$DATA_DIR" "${DOCS_DIR}/assets/data/video_list.json"

cd "$DOCS_DIR"
echo "Serving demo site on http://localhost:${PORT}/demo.html"
echo "Press Ctrl+C to stop the server"

# Start HTTP server in background
python3 -m http.server "$PORT" &
SERVER_PID=$!

# Wait a moment for server to start
sleep 1

# Open browser (only if not in CI environment)
if [ -z "${CI:-}" ]; then
    python3 - <<EOF
import webbrowser
webbrowser.open(f"http://localhost:${PORT}/demo.html")
EOF
fi

# Wait for server process
wait $SERVER_PID
