# WorldLoop Roadmap

WorldLoop starts as a hackathon proof of self-correcting context/resource allocation, but the long-term architecture is now more precise: **the outer loop learns how to compile open-ended agent behavior into a smaller typed program over a changing world**.

`DESIGN.md` defines the broader system contract. `TYPED_EXECUTION_IR.md` defines the production execution target. `ARCHITECTURE.md` defines how the runtime and learning loops fit together.

## North star

Given an objective and a budget, WorldLoop should construct the smallest verified typed program that can reliably accomplish the task using the cheapest sufficient combination of deterministic code, active context, external knowledge, bounded semantic intelligence, tools, authorization, and verification.

When the program fails, the failure becomes evidence for improving the graph, node, context, model, threshold, or evidence policy.

The product is therefore not “RAG with retries,” not “a giant autonomous agent,” and not “put everything into model weights.” It is a **learning compiler for intelligent workflows**.

## Phase 0 — Hackathon proof

Goal: prove that the loop can diagnose a bad cognition/resource decision, repair it, and use prior trajectories to improve future execution.

Required:

- deterministic/synthetic public benchmark;
- visible Compiler, Critic/Verifier, and Loop Doctor roles;
- one real Weave trajectory with graph/resource plan, evidence refs, scores, failure class, and policy delta;
- marimo WorldLoop Lab with Live Execution and Policy/Program Comparison views;
- EXP-008 held-out policy-v0 versus policy-v1 result using first-pass success and/or routing/context regret;
- exact code, data/evidence, workflow/policy, provider/model, and scorer identity on comparable runs;
- fail-closed behavior on insufficient/conflicting evidence.

Stronger hackathon proof:

- represent the task as a small typed graph rather than only an open loop;
- show one broad/open-ended decision compiled into an explicit transition or narrow semantic primitive;
- report semantic-node count or semantic-surface ratio alongside success/regret;
- add EXP-011 progressive-compilation comparison.

Strong extensions only after the core proof works:

- W/C/M controlled knowledge-location experiment;
- small learned router or LoRA intervention on molab;
- ARIA-generated graph/node experiment;
- TypeSafe as a measured semantic-node provider if the onsite interface supports it;
- read-only BTW/LiveLM external-memory adapter;
- SkyPilot parallel experiment execution when it removes operational friction;
- CoreWeave Sandbox episodes for genuinely stateful/code-execution nodes.

Exit condition: a judge can see one task fail, see exactly which node/resource decision failed, see the graph/policy change, see the repaired execution, and see a candidate program/policy perform better on unseen tasks.

## Phase 1 — Typed execution core

Goal: stop treating the open-ended agent loop as the runtime architecture.

Build the first reusable workflow IR with:

- typed workflow/version identity;
- typed node inputs/outputs;
- explicit transitions;
- deterministic nodes;
- retrieval nodes;
- semantic primitives such as `CLASSIFY`, `DECIDE`, `EXTRACT`, `CRITIQUE`, and `VERIFY`;
- tool nodes;
- abstention/escalation paths;
- risk/stakes thresholds;
- separate authorization and verification nodes for consequential actions.

The model must not own global control flow. A semantic node can return a typed decision/uncertainty value; the workflow engine evaluates that output against explicit transition rules.

Exit condition: representative WorldLoop tasks execute as versioned typed graphs and can be replayed/tested without reconstructing control flow from model prose.

## Phase 2 — Real external knowledge

Goal: keep the same typed graph/evaluation contract while replacing toy memory with source-backed changing-world evidence.

Add normalized evidence adapters for:

- BTW/LiveLM as a clearly labeled prior-work backend;
- source-native APIs/files/databases;
- freshness-aware web evidence where permitted;
- LifeOps durable objects for provider-neutral continuity when appropriate.

Every evidence item preserves source identity, observation time, event/validity time, entity/object refs, provenance, and supersession/freshness state.

The Context Materializer learns which durable objects enter active working context. Semantic/retrieval nodes receive evidence through typed obligations instead of unbounded prompt stuffing.

Exit condition: the same compiled workflow can execute against real changing evidence while preserving source authority and fail-closed behavior.

## Phase 3 — Progressive compilation and continuous improvement

Goal: use trajectories to reduce unnecessary open-ended intelligence, not merely improve retry prompts.

Build counterfactual datasets where tasks are run through multiple allowed graphs/routes. Record:

- verified success;
- evidence quality;
- latency/tokens/cost;
- tool/retrieval usage;
- semantic-node count;
- semantic-surface ratio;
- calibration error where applicable;
- authority/verification guardrails.

Candidate improvements may:

- replace a model transformation with deterministic code;
- turn free-form planning into a typed graph template;
- replace broad reasoning with a narrow semantic node;
- introduce explicit branches/thresholds/abstention;
- change context/evidence obligations;
- change provider/model for one primitive;
- add a verifier or authorization boundary.

Promotion path:

```text
incumbent graph/policy
  -> candidate
  -> frozen held-out evaluation
  -> correctness + regret + semantic-surface + calibration + safety comparison
  -> canary
  -> promote | reject
```

Exit condition: candidate programs improve unseen-task behavior and/or reduce semantic surface/resource regret without verified-correctness or safety regression.

## Phase 4 — Production runtime

Goal: deploy WorldLoop as a reliable typed-workflow service rather than a notebook or wandering agent.

Runtime surfaces:

- `/execute` or task endpoint for bounded workflow execution;
- `/health` / readiness;
- optional `/feedback` and evaluation ingestion;
- workflow/policy registry + rollback;
- provider/model adapters by semantic primitive;
- external-memory adapters;
- verifier/scorer service;
- budgets, timeouts, circuit breakers, cache, retries, abstention, and rate limits;
- explicit request/run/workflow/node IDs and receipts;
- Weave telemetry/evaluations.

The marimo app remains the human research/operations surface, not a serving dependency.

For consequential external actions:

```text
semantic/deterministic result
  -> proposed effect
  -> HomeBase / Bridge authorization
  -> bounded actuator
  -> independent verification
  -> durable receipt/world-state update
```

Exit condition: graph/policy rollback, source/version identity, observability, security boundaries, authority separation, and failure behavior are independently testable.

## Deployment and secret-management principle

GitHub owns source, typed schemas, workflows, and reviewable configuration. W&B owns experiment/evaluation/model lineage. marimo/molab owns live scientific interaction. Infisical injects runtime secrets. Source-backed systems own mutable truth. Authority systems own permission to mutate consequential external state.

Secret path:

```text
Infisical project/environment
  -> machine/user identity
  -> `infisical run -- <worldloop command>`
  -> process environment
  -> W&B / TypeSafe / CoreWeave / provider / LifeOps adapters
```

Do not commit `.env` files or copy long-lived keys into notebooks, prompts, LifeOps observations, or GitHub issues.

See `DEPLOYMENT.md` for concrete setup.

## Decision rule for adding features

A new tool, sponsor integration, or architecture layer is accepted only if it materially improves one of five things:

1. verified correctness/recovery;
2. lower routing/context/cost/latency regret;
3. smaller semantic surface without correctness regression;
4. stronger causal/evaluation evidence;
5. safer, more reproducible production operation.

If it does not improve one of those, it is outside the critical path.
