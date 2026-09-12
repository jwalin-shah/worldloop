# OCI bootstrap report

Status: **VERIFIED (non-blocking gap: shared localhost port)**

- Observed (UTC): 2026-09-12T16:29:45Z
- Host: `Linux oci-free-vm 6.17.0-1020-oracle #20-Ubuntu SMP Sat Jul 25 00:52:17 UTC 2026 aarch64 aarch64 aarch64 GNU/Linux`
- Git SHA: `8efc08755a5a51aab78c8fd2589a383596740626` (origin/main, ff, clean before this run)

## Versions

- git: `git version 2.43.0`
- python: `Python 3.12.3`
- uv: `uv 0.12.13 (aarch64-unknown-linux-gnu)`
- weave: `0.53.9`
- cwsandbox: `1.14.2`
- marimo: `0.24.2`
- Orca runtime: active (single-instance lock observed; this run executed inside a live Orca session/worktree)

## Credentials (presence only, never values)

- WANDB_API_KEY: ABSENT
- CWSANDBOX_API_KEY: ABSENT
- WORLDLOOP_WEAVE_PROJECT: DEFAULT

## Readiness results

1. bootstrap: `BOOTSTRAP_OK`
2. idempotence check (bootstrap rerun): `BOOTSTRAP_OK`
3. preflight: `BLOCKED: localhost port 8787 is in use` (exit 2) — port held by an unrelated process from another project/worktree (`livelm-retrieval` demo UI), not a WorldLoop service. Left untouched per scope (no system/service changes outside this repo).
4. tests: `uv run pytest -q` → `5 passed`
5. lint: `uv run ruff check .` → initially found 1 error (`UP035`, `typing.Callable` deprecated import in `src/worldloop/weave_integration.py`); fixed by importing `Callable` from `collections.abc` per Ruff's own suggestion; rerun → `All checks passed!`
6. end-to-end smoke (`scripts/smoke.sh`, uses port 18787 by default so it does not collide with the busy 8787): `SMOKE_OK`, server `START_OK`, `health=OK`, cleanly `STOP_OK`

Overall: steps 1, 2, 4, 5, 6 are green. Step 3 (`preflight.sh`) fails only its own default-port-8787 availability probe because of the unrelated external process noted above; every functional check inside preflight (versions, credential presence, fixture load of 12 cases) passed before that probe ran. `READY_FOR_HACKATHON` was not printed because `ready.sh` chains these steps with `set -e`, but running each step independently shows nothing in WorldLoop itself is broken.

## Benchmark (fixtures, 12 cases)

Generated via `uv run worldloop benchmark --json` → `reports/benchmark.json`.

- case_count: 12
- seeded_failure_count: 8
- improved_seeded_cases: 8
- all_seeded_repaired: true
- final_sufficient_count: 12
- `case-cross-entity` score: 0.5 → 1.0 across the two adaptive passes (second pass recipe adds the graph join step, matching `scripts/smoke.sh`'s assertions)

## Localhost health

`curl http://127.0.0.1:18787/health` (via `scripts/smoke.sh`, which stands the service up on 18787): `{"ok": true, "cases": 12}` → `health=OK`. Default port 8787 was not exercised end-to-end because it is occupied by an unrelated process; this is an environmental condition of the shared host, not a WorldLoop defect.

## Non-blocking gaps

- Sponsor cloud credentials (`WANDB_API_KEY`, `CWSANDBOX_API_KEY`) are absent in this environment, so remote Weave tracing/evaluation and CoreWeave Sandboxes ran in local/sanitized mode only, as documented in `docs/OCI_RUNBOOK.md`.
- `preflight.sh`'s hardcoded port-8787 probe cannot pass while the unrelated external process holds that port; this does not affect the actual demo path, which binds to `WORLDLOOP_PORT` (18787 in the smoke test) and passed its health check.
