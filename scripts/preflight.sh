#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
PORT="${WORLDLOOP_PORT:-8787}"

command -v git >/dev/null || { echo "BLOCKED: git missing"; exit 2; }
command -v python3 >/dev/null || { echo "BLOCKED: python3 missing"; exit 2; }
command -v uv >/dev/null || { echo "BLOCKED: uv missing; run scripts/bootstrap_oci.sh"; exit 2; }

echo "git=$(git --version)"
echo "python=$(python3 --version)"
echo "uv=$(uv --version)"
echo "WANDB_API_KEY=$([[ -n "${WANDB_API_KEY:-}" ]] && echo PRESENT || echo ABSENT)"
echo "CWSANDBOX_API_KEY=$([[ -n "${CWSANDBOX_API_KEY:-}" ]] && echo PRESENT || echo ABSENT)"
echo "WORLDLOOP_WEAVE_PROJECT=$([[ -n "${WORLDLOOP_WEAVE_PROJECT:-}" ]] && echo PRESENT || echo DEFAULT)"
uv run python - <<'PY'
for name in ("weave", "cwsandbox", "marimo"):
    try:
        module = __import__(name)
        version = getattr(module, "__version__", "installed")
        print(f"{name}={version}")
    except Exception as exc:
        print(f"{name}=UNAVAILABLE:{type(exc).__name__}")
PY
uv run python - <<'PY'
from worldloop.engine import WorldLoop
from worldloop.runtime import FIXTURES
loop = WorldLoop(FIXTURES)
assert len(loop.cases) >= 10
print(f"fixture_cases={len(loop.cases)}")
PY
python3 - "$PORT" <<'PY'
import socket, sys
port = int(sys.argv[1])
s = socket.socket()
try:
    s.bind(("127.0.0.1", port))
except OSError:
    print(f"BLOCKED: localhost port {port} is in use")
    raise SystemExit(2)
finally:
    s.close()
print(f"port={port}:AVAILABLE")
PY
echo "READY"
