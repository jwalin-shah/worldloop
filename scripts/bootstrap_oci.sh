#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

python3 - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit("BLOCKED: Python >=3.11 is required")
print(f"python={sys.version.split()[0]}")
PY

if ! command -v uv >/dev/null 2>&1; then
  echo "uv=missing; installing user-scoped uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi

if [[ "${WORLDLOOP_INSTALL_WEAVE:-1}" == "1" ]]; then
  uv sync --extra dev --extra weave
else
  uv sync --extra dev
fi

echo "uv=$(uv --version)"
echo "BOOTSTRAP_OK"
