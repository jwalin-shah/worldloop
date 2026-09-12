#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

echo "[1/6] bootstrap"
./scripts/bootstrap_oci.sh
echo "[2/6] idempotence check"
./scripts/bootstrap_oci.sh
echo "[3/6] preflight"
./scripts/preflight.sh
echo "[4/6] tests"
uv run pytest -q
echo "[5/6] lint"
uv run ruff check .
echo "[6/6] end-to-end smoke"
./scripts/smoke.sh

echo "READY_FOR_HACKATHON"
