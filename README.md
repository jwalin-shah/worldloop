# WorldLoop

WorldLoop is a **self-improving context and epistemic/resource compiler** built for **CoreWeave Hacks: Agent Loops (September 12-13, 2026)**. It asks a practical question: when an agent fails because it chose the wrong context, retrieval path, model, tool, or verification strategy, can a cooperating loop diagnose why, change the decision policy, and measurably improve?

The public demo is fully reproducible on sanitized fixtures. Private LifeOps/LiveLM data is not required. The stronger research target is to turn prior failure trajectories into a policy that improves first-pass behavior or reduces routing/context regret on held-out tasks at equal verified correctness.

## Design

- [`docs/DESIGN.md`](docs/DESIGN.md) — canonical design specification: axioms, invariants, agent roles, data contracts, evaluation metrics, training targets, failure modes, MVP and extensions.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — end-to-end, inner-loop, outer-learning-loop, W/C/M, and prior-work architecture diagrams.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — hackathon proof -> real external knowledge -> continuous policy improvement -> production runtime.
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — OCI/marimo/W&B runtime, Infisical secret injection, external-memory adapters, and production promotion path.
- [`docs/SPONSOR_STACK.md`](docs/SPONSOR_STACK.md) — exact responsibility of Weave, marimo/molab, W&B MCP, ARIA, Models/Artifacts, Inference, TypeSafe, Sandboxes, SkyPilot, and prior-work adapters.
- [`experiments/registry.json`](experiments/registry.json) — executable experiment questions, hypotheses, metrics, stop rules, and artifact targets.
- [`PRIOR_WORK.md`](PRIOR_WORK.md) — explicit hackathon/prior-work boundary.

## Plug-and-play on the OCI VM

For an existing checkout:

```bash
cd ~/projects/worldloop
git fetch origin main && git merge --ff-only origin/main
./scripts/ready.sh
```

For a fresh checkout:

```bash
git clone https://github.com/jwalin-shah/worldloop.git ~/projects/worldloop
cd ~/projects/worldloop
./scripts/ready.sh
```

A successful run ends with `READY_FOR_HACKATHON`. Start the localhost demo server with `./scripts/start.sh`, verify the configured `/health` endpoint, then stop it with `./scripts/stop.sh`.

Or use `make ready`, `make demo`, and `make benchmark`. See `docs/OCI_RUNBOOK.md` for the host runbook.

## What the loop does

WorldLoop exposes three distinct roles:

1. **Context Compiler / Epistemic Router** chooses a bounded context/resource plan.
2. **Critic / Verifier** independently scores evidence sufficiency, grounding, freshness, contradictions, and failure class.
3. **Loop Doctor / Policy Researcher** changes the relevant retrieval/context/model/tool/verification decision and reruns.

The current deterministic engine gathers exact, lexical, vector, temporal, and graph evidence with provenance and fails closed when required support is absent. The benchmark contains 12 sanitized cases spanning temporal state, contradictory/stale claims, cross-entity joins, semantic misses, straightforward retrieval, and insufficient evidence.

The **inner loop** proves self-correction on a task. The **outer loop** is designed to use many traced failures/counterfactuals to produce a candidate policy and compare it with the incumbent on frozen held-out tasks before promotion.

## W&B Weave

`./scripts/bootstrap_oci.sh` installs the sponsor stack by default. Remote tracing activates only when `WANDB_API_KEY` is present. `WORLDLOOP_WEAVE_PROJECT` defaults to `worldloop-coreweave-2026`. Preflight reports only whether keys are present; it never prints values.

```bash
export WANDB_API_KEY='...'
export WORLDLOOP_WEAVE_PROJECT='worldloop-coreweave-2026'
uv run worldloop demo --case case-cross-entity --json
```

Weave is the experiment proof plane: Compiler decisions, retrieval/tool spans, Critic scores, Loop Doctor policy deltas, and policy-version evaluations should be inspectable there.

## marimo / molab

`notebooks/worldloop_lab.py` is the seed of the live WorldLoop Lab. The target surface is not a decorative dashboard: it is the interactive research workstation for inspecting trajectories, comparing policy versions, exploring failure classes, running W/C/M knowledge-location experiments, and—if justified—launching bounded training/fine-tuning work.

## Hackathon sponsor stack

The OCI bootstrap installs **W&B Weave**, **CoreWeave Sandboxes (`cwsandbox`)**, and **marimo**. ARIA uses the W&B/CoreWeave experiment state rather than becoming a second orchestration layer. TypeSafe is evaluated as a worker/router/verifier candidate if onsite access supports it. SkyPilot is optional and only belongs as a compute/job execution adapter when parallel experiment/training jobs justify it. See `docs/SPONSOR_STACK.md`.

## Prior-work and safety boundary

Pre-existing **LifeOps / Universal Knowledge Fabric**, **LiveLM/BTW**, **HomeBase/Bridge**, and related historical work are clearly prior infrastructure. WorldLoop may connect to them through optional read-only adapters, but the public benchmark and core judging demo do not depend on private prior systems.

WorldLoop does not mutate external systems in its public demo. Retrieval scores or model confidence do not confer authority. Fixture results prove only deterministic fixture behavior; stronger claims require the corresponding held-out/model experiments and recorded evidence.
