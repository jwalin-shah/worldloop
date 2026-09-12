#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
PORT="${WORLDLOOP_PORT:-8787}"
mkdir -p .run
if [[ -f .run/worldloop.pid ]] && kill -0 "$(cat .run/worldloop.pid)" 2>/dev/null; then
  echo "WorldLoop already running pid=$(cat .run/worldloop.pid) port=$PORT"
  exit 0
fi
nohup uv run uvicorn worldloop.server:app --host 127.0.0.1 --port "$PORT" > .run/worldloop.log 2>&1 &
echo $! > .run/worldloop.pid
for _ in $(seq 1 40); do
  if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    echo "START_OK pid=$(cat .run/worldloop.pid) port=$PORT"
    exit 0
  fi
  sleep 0.25
done
echo "BLOCKED: server failed health check"
tail -n 40 .run/worldloop.log || true
exit 1
