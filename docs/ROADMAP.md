# WorldLoop Roadmap

WorldLoop starts as a hackathon proof of a self-improving context and epistemic/resource compiler, but the architecture is intentionally shaped so the same system can become useful against real, changing external knowledge rather than ending as a fixture-only demo.

`DESIGN.md` defines the system contract. `ARCHITECTURE.md` defines the component map. This file defines the order in which capabilities should become real.

## North star

Given a task and a budget, WorldLoop should select the cheapest sufficient combination of model capability, active context, external knowledge, tools, and verification needed for a supported result. When that selection fails, the failure should become evidence for a better future policy.

The product is therefore not "RAG with retries" and not "put everything into model weights." It is a learned control plane for allocating cognition over a changing world.

## Phase 0 — Hackathon proof

Goal: prove the loop and make every claim inspectable.

Required:

- deterministic/synthetic public benchmark;
- visible Context Compiler, independent Critic/Verifier, and Loop Doctor roles;
- real Weave trajectory with context/resource plan, evidence refs, scores, failure class, and policy delta;
- marimo WorldLoop Lab with Live Loop and Policy Comparison views;
- EXP-008 held-out policy-v0 versus policy-v1 result using first-pass success and/or routing/context regret;
- exact code, data/evidence, policy, provider/model, and scorer identity on every comparable run;
- fail-closed behavior on insufficient/conflicting evidence.

Strong extensions, only after the core proof is working:

- W/C/M controlled knowledge-location experiment;
- small learned router or LoRA intervention on molab;
- ARIA-generated bounded experiment;
- TypeSafe / W&B Inference model comparison;
- read-only BTW/LiveLM external-memory adapter;
- SkyPilot parallel experiment execution when it removes operational friction;
- CoreWeave Sandbox episodes for genuinely stateful/code-execution tasks.

Exit condition: a judge can see one task fail, understand why, see the actual decision variable change, see the repair succeed, and then see a later policy perform better on unseen tasks.

## Phase 1 — Real external knowledge

Goal: keep the same evaluation contract while replacing toy memory with source-backed changing-world evidence.

Add a normalized external-memory interface that can read from:

- BTW/LiveLM as a clearly labeled prior-work backend;
- source-native APIs/files/databases;
- web/freshness-aware evidence collectors where permitted;
- LifeOps durable objects for provider-neutral continuity when appropriate.

Every returned evidence item should preserve source identity, observation time, event/validity time, entity/object refs, provenance, and supersession/freshness state.

The Context Materializer should learn what subset of durable state must enter the active working context. The Epistemic Router should learn when model-only reasoning is sufficient, when memory is necessary, when a deeper source is required, when a stronger model/tool/verifier is worth the cost, and when to abstain.

Exit condition: the same WorldLoop policy/eval machinery works against real changing evidence without making the private index a hidden dependency or treating model output as world truth.

## Phase 2 — Continuous policy improvement

Goal: convert trajectories into safe cross-task learning.

Build a counterfactual dataset where selected tasks are run through multiple allowed routes. Record verified success, support, latency, tokens, cost, tool/retrieval usage, and failures. Use these outcomes to train or derive candidate context/resource policies.

Promote only through:

```text
incumbent policy
  -> candidate
  -> frozen held-out evaluation
  -> guardrail comparison
  -> canary
  -> promote | reject
```

Preserve rollback and full lineage from trajectory/evidence snapshot to training dataset to candidate policy to evaluation result.

Exit condition: policy changes improve unseen-task first-pass success or reduce routing/context regret at equal or better verified correctness.

## Phase 3 — Production runtime

Goal: deploy WorldLoop as a reliable service rather than a notebook-only experiment.

Runtime surfaces:

- `/answer` or task endpoint for bounded execution;
- `/health` / readiness;
- optional `/feedback` and evaluation ingestion;
- provider/model adapters;
- external-memory adapters;
- verifier/scorer service;
- policy registry and rollback;
- Weave telemetry/evaluations;
- budgets, timeouts, circuit breakers, cache, retries, abstention, and rate limits;
- explicit request/run IDs and receipts.

The marimo app remains the human research/operations surface, not the serving dependency. The same notebook code may be run as a read-only app for analysis because marimo notebooks are normal Python and can be deployed as apps.

For consequential external actions, WorldLoop proposes a plan/result but does not self-authorize. A separate authority/execution boundary such as HomeBase/Bridge can admit, execute, independently verify, and receipt the side effect.

Exit condition: policy/version rollback, source/version identity, observability, security boundaries, and failure behavior are all testable independently of the interactive research UI.

## Deployment and secret-management principle

GitHub owns source and reviewable configuration. W&B owns experiment/evaluation/model lineage. marimo/molab owns live scientific interaction. Infisical injects runtime secrets. Source-backed systems own mutable truth. No one of these systems becomes a substitute for the others.

The secret path should be:

```text
Infisical project/environment
  -> machine/user identity
  -> `infisical run -- <worldloop command>`
  -> process environment
  -> W&B / TypeSafe / CoreWeave / provider / LifeOps adapters
```

Do not commit `.env` files or copy long-lived keys into notebooks, prompts, LifeOps observations, or GitHub issues.

See `DEPLOYMENT.md` for the concrete setup.

## Decision rule for adding features

A new tool, sponsor integration, or architecture layer is accepted only if it materially improves one of four things:

1. verified correctness/recovery;
2. lower routing/context/cost/latency regret;
3. stronger causal/evaluation evidence;
4. safer, more reproducible production operation.

If it does not improve one of those, it is outside the critical path.
