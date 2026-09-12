# TypeSafe Experiment — Bounded Semantic Routing Node

This is an optional hackathon extension. Do not block MVP Gates 1–4 on TypeSafe access or integration.

## Question

Can a specialized typed semantic model make a better bounded routing decision than a GPT-style router or deterministic heuristic under the same WorldLoop evidence contract?

WorldLoop remains responsible for global control flow, evidence obligations, transition checks, and promotion. TypeSafe—if the onsite interface supports it—is only one candidate implementation of a semantic opcode.

## Semantic contract

Input:

```text
question/task features
available evidence summary
freshness / staleness signals
retrieval results already available
budget / latency constraints
previous failure class if any
```

Allowed output:

```text
MODEL_ONLY
EXACT
LEXICAL
VECTOR
TEMPORAL
GRAPH
DEEP_RETRIEVAL
ABSTAIN
```

Optional additional field:

```text
confidence / probability
```

Do not assume that a returned confidence is calibrated unless TypeSafe documents or explains what it means empirically.

## Baselines

Compare the exact same frozen task/evidence inputs across:

1. deterministic WorldLoop heuristic;
2. GPT-style general-purpose router with structured output;
3. TypeSafe semantic router, if actual onsite access exposes a compatible contract.

Prompts/contracts should be frozen before the comparison. Do not hand-tune each provider against held-out outcomes.

## Metrics

Primary:

- verified task success;
- routing regret.

Secondary:

- under-allocation rate;
- unnecessary retrieval rate;
- invalid-output rate;
- abstention correctness;
- recovery rate;
- latency;
- cost if exposed;
- semantic-surface contribution.

If meaningful probabilities are returned:

- Brier score;
- expected calibration error / reliability buckets.

Do not publish calibration claims from arbitrary self-reported LLM confidence.

## Transition boundary

The semantic model does not select the next state directly.

Example:

```text
semantic node returns:
  route = GRAPH
  probability = 0.94

WorldLoop TransitionCheck verifies:
  route in RouteEnum
  required evidence refs present
  freshness obligations satisfied
  risk/budget policy satisfied

then explicit workflow transition is admitted.
```

Model belief remains distinct from evidence, authority, and verification.

## Onsite questions for TypeSafe

Ask these before writing an adapter:

1. What is the actual invocation protocol / endpoint?
2. What model IDs or product surfaces are available to hackathon teams?
3. Is the decision schema supplied dynamically per request, trained into a model/task, or both?
4. What structured output types are natively supported: enums, bools, numbers, distributions, classifications?
5. What exactly does a returned probability/confidence mean?
6. Is calibration measured, and against what task distribution / metric?
7. Can the system explicitly abstain?
8. Can shared context be encoded once and reused across multiple decisions?
9. Which failure classes are structurally impossible versus merely statistically reduced?
10. What request-level latency, token/compute, and cost telemetry is exposed?
11. Are tool calling or external evidence interfaces supported, or should WorldLoop provide all evidence?
12. What context limits, rate limits, concurrency limits, and event quotas apply?

## Acceptance criteria

Run only after the core held-out benchmark exists.

A valid experiment requires:

- frozen held-out task set;
- identical legitimate pre-action inputs across baselines;
- one adapter per router under the same Route enum;
- no held-out outcome leakage;
- real measured results in Weave;
- a report that can conclude `TypeSafe wins`, `baseline wins`, or `inconclusive` without changing the benchmark after seeing results.

## Why this experiment matters

The experiment tests a narrow WorldLoop thesis:

> Use deterministic code where semantics are unnecessary, use source-backed evidence where truth changes, and invoke specialized semantic intelligence only for irreducible judgment.

A positive TypeSafe result would show that the bounded semantic-node layer benefits from a model trained/interface-designed for calibrated typed decisions. A negative result would still be useful: it would tell us that the general router or deterministic policy is sufficient for this task distribution and that adding a specialized semantic node is unnecessary.
