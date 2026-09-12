#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
TMP="$(mktemp)"
trap 'rm -f "$TMP"; WORLDLOOP_PORT=${WORLDLOOP_SMOKE_PORT:-18787} scripts/stop.sh >/dev/null 2>&1 || true' EXIT
uv run worldloop benchmark --json > "$TMP"
uv run python - "$TMP" <<'PY'
import json, sys
report = json.load(open(sys.argv[1]))
assert report["case_count"] >= 10
assert report["seeded_failure_count"] >= 3
assert report["improved_seeded_cases"] >= 3
case = next(r for r in report["results"] if r["case_id"] == "case-cross-entity")
assert len(case["passes"]) == 2
assert case["passes"][0]["score"] < case["passes"][1]["score"]
assert "graph" not in case["passes"][0]["recipe"]
assert "graph" in case["passes"][1]["recipe"]
print(f"benchmark_cases={report['case_count']}")
print(f"seeded_failures={report['seeded_failure_count']}")
print(f"improved_seeded_cases={report['improved_seeded_cases']}")
print(f"adaptive_case_score={case['passes'][0]['score']}->{case['passes'][1]['score']}")
PY
export WORLDLOOP_PORT="${WORLDLOOP_SMOKE_PORT:-18787}"
scripts/start.sh
curl -fsS "http://127.0.0.1:${WORLDLOOP_PORT}/health" | uv run python -c 'import json,sys; p=json.load(sys.stdin); assert p["ok"] and p["cases"] >= 10; print("health=OK")'
scripts/stop.sh
echo "SMOKE_OK"
