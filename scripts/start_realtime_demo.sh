#!/usr/bin/env bash
set -euo pipefail

# Start the realtime ASR server and documentation demo.

IN_DOCKER=0
if [ -f /.dockerenv ]; then
  IN_DOCKER=1
fi

VENV_DIR=".venv"

if [ "$IN_DOCKER" -eq 0 ]; then
  # Create virtual environment if it doesn't exist
  if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
  fi

  # Activate the virtual environment and install dependencies
  source "$VENV_DIR/bin/activate"
  pip install --upgrade pip >/dev/null
  pip install -r requirements.txt >/dev/null
fi

# Start realtime ASR server in the background
python scripts/realtime_server.py &
ASR_PID=$!

# Start the documentation demo (serves on http://localhost:8000 by default)
# When serve_docs.sh exits, stop the ASR server as well.
trap 'kill $ASR_PID' EXIT

if [ "$IN_DOCKER" -eq 1 ]; then
  HEADLESS=1 scripts/serve_docs.sh
else
  scripts/serve_docs.sh
fi
