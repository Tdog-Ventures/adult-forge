#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
set -a
# shellcheck disable=SC1091
source .env
set +a
npx tsx src/server.ts &
PID=$!
trap 'kill $PID 2>/dev/null || true' EXIT
sleep 3
curl -sS -X POST "http://127.0.0.1:4000/api/external/render-video-status" \
  -H "Authorization: Bearer af_live_replace_me" \
  -H "Content-Type: application/json" \
  -d '{"job_ids": ["test1","test2"]}'
echo
