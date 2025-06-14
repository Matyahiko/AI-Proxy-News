#!/usr/bin/env bash
set -euo pipefail

# Start the realtime ASR server and documentation demo using a Python virtual environment.

VENV_DIR=".venv"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Install required packages
pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

# Start realtime ASR server in the background
python scripts/realtime_server.py &
ASR_PID=$!

# Start the documentation demo (serves on http://localhost:8000 by default)
# When serve_docs.sh exits, stop the ASR server as well.
trap 'kill $ASR_PID' EXIT

scripts/serve_docs.sh
