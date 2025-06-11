#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
IMAGE_NAME="${1:-ai-proxy-news}"

PROXY=""
if [ -f "${SCRIPT_DIR}/../secrets/.env" ]; then
  PROXY=$(grep -E '^PROXY=' "${SCRIPT_DIR}/../secrets/.env" | cut -d '=' -f2- || true)
fi

if [ -n "$PROXY" ]; then
  docker build --build-arg PROXY="$PROXY" -t "$IMAGE_NAME" "$SCRIPT_DIR/.."
else
  docker build -t "$IMAGE_NAME" "$SCRIPT_DIR/.."
fi
