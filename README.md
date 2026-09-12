# WorldLoop

WorldLoop is a **self-improving context compiler** built for **CoreWeave Hacks: Agent Loops (September 12-13, 2026)**. It asks a practical question: when an agent fails because it built the wrong context, can it diagnose the retrieval failure, change how it retrieves evidence, rerun, and measurably improve?

The public demo is fully reproducible on sanitized fixtures. Private LifeOps data is not required.

## Plug-and-play on the OCI VM

```bash
git clone https://github.com/jwalin-shah/worldloop.git ~/projects/worldloop
cd ~/projects/worldloop
./scripts/bootstrap_oci.sh
./scripts/preflight.sh
./scripts/smoke.sh
```

Start the localhost demo server:

```bash
./scripts/start.sh
curl http://127.0.0.1:8787/health
./scripts/stop.sh
```

Or use `make bootstrap`, `make preflight`, `make smoke`, `make demo`, and `make benchmark`.

## What the loop does

1. **Context Compiler** chooses a bounded retrieval recipe.
2. **Evidence Retriever** gathers exact, lexical, vector, temporal, and graph evidence with provenance.
3. **Critic / Evaluator** scores whether required evidence is present and classifies the failure.
4. **Loop Doctor** changes the retrieval recipe.
5. WorldLoop reruns and compares pass-to-pass scores; if evidence remains insufficient, it fails closed.

The benchmark contains 12 sanitized cases spanning temporal state, contradictory/stale claims, cross-entity joins, semantic misses, straightforward retrieval, and insufficient evidence.

## W&B Weave

`./scripts/bootstrap_oci.sh` installs the optional `weave` extra by default. Remote tracing activates only when `WANDB_API_KEY` is present. `WORLDLOOP_WEAVE_PROJECT` defaults to `worldloop-coreweave-2026`. Preflight reports only whether keys are present; it never prints values.

```bash
export WANDB_API_KEY='...'
export WORLDLOOP_WEAVE_PROJECT='worldloop-coreweave-2026'
uv run worldloop demo --case case-cross-entity --json
```

See `docs/DEMO.md` for the three-minute story, `docs/ARCHITECTURE.md` for the system map, and `PRIOR_WORK.md` for the explicit hackathon/prior-work boundary.

## Safety boundary

WorldLoop does not mutate external systems. Retrieval scores do not confer authority. Fixture results prove only the deterministic fixture behavior in this repository.
