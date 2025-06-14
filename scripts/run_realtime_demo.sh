#!/usr/bin/env bash
set -euo pipefail

DOCS_PORT="${1:-8000}"
ASR_PORT="${2:-8765}"
export ASR_PORT

check_port() {
  python3 - "$1" <<'EOF'
import socket, sys
port = int(sys.argv[1])
s = socket.socket()
try:
    s.bind(("0.0.0.0", port))
except OSError:
    sys.exit(1)
s.close()
EOF
}

if ! check_port "$DOCS_PORT"; then
  echo "Port $DOCS_PORT is already in use; specify another." >&2
  exit 1
fi

if ! check_port "$ASR_PORT"; then
  echo "Port $ASR_PORT is already in use; specify another." >&2
  exit 1
fi

python3 scripts/realtime_server.py &
ASR_PID=$!

trap 'kill $ASR_PID' EXIT

bash scripts/serve_docs.sh "$DOCS_PORT"
