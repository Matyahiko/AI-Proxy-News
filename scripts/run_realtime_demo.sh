#!/usr/bin/env bash
set -euo pipefail

# Set ports via environment variables if provided as arguments
if [ $# -ge 1 ]; then
  export DOCS_PORT="$1"
fi
if [ $# -ge 2 ]; then
  export ASR_PORT="$2"
fi

# Validate port availability using centralized config
python3 -c "
import sys
sys.path.append('scripts')
from config import validate_port_usage
validate_port_usage()
"

python3 scripts/realtime_server.py &
ASR_PID=$!

trap 'kill $ASR_PID' EXIT

# Get DOCS_PORT from config if not set
DOCS_PORT=$(python3 -c "
import sys
sys.path.append('scripts')
from config import get_docs_port
print(get_docs_port())
")

bash scripts/serve_docs.sh "$DOCS_PORT"
