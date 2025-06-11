#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${1:-ai-proxy-news}"

PROXY=""
if [ -f secrets/.env ]; then
  PROXY=$(grep -E '^PROXY=' secrets/.env | cut -d '=' -f2- || true)
fi

if [ -n "$PROXY" ]; then
  docker build --build-arg PROXY="$PROXY" -t "$IMAGE_NAME" .
else
  docker build -t "$IMAGE_NAME" .
fi
