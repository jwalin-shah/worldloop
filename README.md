# WorldLoop

WorldLoop is a **self-improving context, resource, and execution compiler** built for **CoreWeave Hacks: Agent Loops (September 12-13, 2026)**. It learns what an intelligent workflow should know, which resources it should use, and—crucially—how to turn successful open-ended agent behavior into a smaller typed program with explicit transitions and bounded semantic decisions.

The hackathon loop diagnoses failures and proposes better context/resource/workflow policies. The production destination is not an infinitely wandering agent: it is a progressively compiled state machine that is deterministic where possible, uses source-backed external knowledge when needed, isolates irreducible semantic judgment to typed nodes, and keeps authority plus real-world verification separate.

The public demo remains fully reproducible on sanitized fixtures. Private LifeOps/LiveLM data is not required.

## Design

- [`docs/DESIGN.md`](docs/DESIGN.md) — broader system specification: axioms, invariants, data contracts, evaluation metrics, training targets, failure modes, MVP and extensions.
- [`docs/TYPED_EXECUTION_IR.md`](docs/TYPED_EXECUTION_IR.md) — runtime centerpiece: typed workflow/state-machine IR, semantic primitives, explicit transitions, confidence/stakes/authority separation, and progressive compilation metrics.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — typed runtime graph, learning loop, W/C/M, compilation, source boundaries, and tool responsibilities.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — hackathon proof -> typed execution core -> real external knowledge -> progressive compilation -> production runtime.
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — OCI/marimo/W&B runtime, Infisical secret injection, external-memory adapters, and production promotion path.
- [`docs/PLATFORM_DEEP_DIVE.md`](docs/PLATFORM_DEEP_DIVE.md) — non-obvious platform constraints/capabilities from the current W&B, marimo, Infisical, CoreWeave, SkyPilot, and TypeSafe docs.
- [`docs/OPERATOR_CHECKLIST.md`](docs/OPERATOR_CHECKLIST.md) — exact account/setup actions, critical-path gates, and demo-readiness checklist.
- [`docs/SPONSOR_STACK.md`](docs/SPONSOR_STACK.md) — responsibility of Weave, marimo/molab, W&B MCP, ARIA, Models/Artifacts, Inference, TypeSafe, Sandboxes, SkyPilot, and prior-work adapters.
- [`experiments/registry.json`](experiments/registry.json) — executable experiment questions, hypotheses, metrics, stop rules, and artifact targets, including EXP-011 progressive compilation.
- [`PRIOR_WORK.md`](PRIOR_WORK.md) — explicit hackathon/prior-work boundary.

## Core thesis

The development loop is:

```text
execute
  -> observe in Weave
  -> classify failure
  -> change graph / node / context / model policy
  -> evaluate candidate
  -> promote | reject
```

The runtime destination is:

```text
typed input
  -> compiled workflow IR
  -> deterministic / retrieval / bounded semantic / tool nodes
  -> explicit transitions
  -> proposed effect if any
  -> separate authority boundary
  -> bounded actuation
  -> independent verification
```

The model does **not** own global control flow.

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

## What the loop does today

WorldLoop currently exposes three visible learning/debugging roles:

1. **Compiler / Epistemic Router** chooses a bounded context/resource plan and increasingly a typed execution graph.
2. **Critic / Verifier** independently scores evidence sufficiency, grounding, freshness, contradictions, and failure class.
3. **Loop Doctor / Policy Researcher** changes the relevant graph, retrieval, context, model, tool, verifier, or transition policy and reruns.

The deterministic engine already gathers exact, lexical, vector, temporal, and graph evidence with provenance and fails closed when required support is absent. The benchmark contains 12 sanitized cases spanning temporal state, contradictory/stale claims, cross-entity joins, semantic misses, straightforward retrieval, and insufficient evidence.

The **inner loop** proves self-correction on a task. The **outer loop** turns traced failures/counterfactuals into candidate programs/policies and compares them with the incumbent on frozen held-out tasks before promotion. EXP-011 adds the stronger question: can successful open-ended behavior be compiled into fewer semantic nodes and more explicit transitions without losing verified correctness?

## Intelligence primitives

WorldLoop should not normalize every provider into only `messages -> text`. The semantic layer targets typed primitives such as:

```text
GENERATE
CLASSIFY
DECIDE
EXTRACT
PLAN
CRITIQUE
PREDICT
VERIFY
```

Different providers may implement different subsets. TypeSafe is especially interesting as a candidate for bounded machine-native semantic decisions if the actual onsite API supports them; no undocumented TypeSafe interface is assumed.

## W&B Weave

`./scripts/bootstrap_oci.sh` installs the sponsor stack by default. Remote tracing activates only when `WANDB_API_KEY` is present. `WORLDLOOP_WEAVE_PROJECT` defaults to `worldloop-coreweave-2026`. Preflight reports only whether keys are present; it never prints values.

```bash
export WANDB_API_KEY='...'
export WORLDLOOP_WEAVE_PROJECT='worldloop-coreweave-2026'
uv run worldloop demo --case case-cross-entity --json
```

Weave is the experiment proof plane: workflow/node versions, Compiler decisions, retrieval/tool spans, semantic-node outputs, Critic scores, Loop Doctor deltas, verification results, and program-version evaluations should be inspectable there.

## marimo / molab

`notebooks/worldloop_lab.py` is the seed of the live WorldLoop Lab. The target surface is the interactive research workstation for inspecting execution graphs, comparing candidate programs/policies, exploring failure classes, running W/C/M knowledge-location experiments, visualizing progressive compilation, and—if justified—launching bounded training/fine-tuning work.

## External knowledge

Pre-existing **LiveLM/BTW** may be connected through a hackathon-built read-only evidence adapter. The index itself is prior work; WorldLoop's contribution is deciding when/how to materialize external evidence into a typed workflow and verifying whether that evidence is sufficient/current/non-contradictory.

## Prior-work and safety boundary

Pre-existing **LifeOps / Universal Knowledge Fabric**, **LiveLM/BTW**, **HomeBase/Bridge**, and related historical work are clearly prior infrastructure. WorldLoop may connect to them through optional adapters, but the public benchmark and core judging demo do not depend on private prior systems.

WorldLoop does not mutate external systems in its public demo. Model confidence is epistemic information, not authority. Consequential execution belongs behind a separate admission/authorization boundary and an independent postcondition verifier. Fixture results prove only deterministic fixture behavior; stronger claims require the corresponding held-out/model/compilation experiments and recorded evidence.
