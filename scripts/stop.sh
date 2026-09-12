#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if [[ ! -f .run/worldloop.pid ]]; then
  echo "STOP_OK not-running"
  exit 0
fi
PID="$(cat .run/worldloop.pid)"
if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  for _ in $(seq 1 20); do
    kill -0 "$PID" 2>/dev/null || break
    sleep 0.1
  done
fi
rm -f .run/worldloop.pid
echo "STOP_OK"
