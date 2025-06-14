#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8000}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCS_DIR="${SCRIPT_DIR}/../docs"

cd "$DOCS_DIR"
echo "Serving demo site on http://localhost:${PORT}"
python3 -m http.server "$PORT"
