# WorldLoop Transition Contracts

WorldLoop's hackathon runtime now has one deliberately small executable formalism: `NodeSpec` plus `TransitionCheck`.

The goal is not to claim that a language model has been formally proved correct. The goal is to make each important transition carry inspectable evidence about **why the runtime admitted or rejected that transition**.

## MVP contract

`NodeSpec` binds the minimum information required to reason about a node:

```text
identity
  node_id
  version
  kind

interface
  input_schema
  output_schema

epistemics
  evidence_obligations

logic
  preconditions
  postconditions

world interaction
  effects

control flow
  success_transition
  failure_transition
```

The current fixture engine instantiates this contract for its retrieval/verification step rather than pretending the entire future workflow IR already exists.

`TransitionCheck` records what happened at runtime:

```text
node_id / node_version
pass_number
evidence_used
obligation_results
preconditions_checked
preconditions_passed
effects
result
postconditions_checked
postcondition_passed
next_state
failure_class
```

For the cross-entity case, for example, pass 1 can explicitly record that the `retrieval_method:graph` obligation failed and route to `REPAIR`; pass 2 records that the obligation passed and routes to `DONE`.

## Why this is stronger than typed JSON

Input/output validation answers only whether values have the expected shape.

A transition contract also asks:

- what evidence was required;
- what had to be true before the operation;
- what effect class the operation belongs to;
- what must be true afterward;
- what exact transition follows success or failure.

This is closer to a runtime contract over state evolution than to an LLM returning JSON that happens to parse.

## Proof-carrying transition, not proof-carrying model

The long-term abstraction is a transition certificate over `S0 -> S1`.

A semantic node may still depend on uncertain inference. WorldLoop should not claim a theorem proving the semantic judgment itself. Instead, the surrounding transition can preserve explicit assumptions, evidence obligations, authority constraints, and independently checkable postconditions.

Future certificates may bind:

```text
from_state / to_state
workflow/node/policy versions
input hash
evidence refs
preconditions checked
assumptions
reads / writes / effects
required capability witness
semantic result + uncertainty
postconditions checked
invariants preserved
authorization receipt
external verification refs
timestamp / validity window
```

The runtime question becomes:

> Do we have sufficient evidence and authority to admit this exact state transition?

not:

> Did the agent sound reasonable?

## Safety is not enough: liveness

A fail-closed system can game safety by refusing or escalating everything.

WorldLoop therefore needs both:

```text
Safety:
never commit an unsupported or unauthorized consequential transition.

Liveness:
when sufficient evidence and authority exist, a supported task should eventually reach an accepted terminal state.
```

Hackathon/empirical metrics should eventually include:

- safe completion rate;
- correct abstention rate;
- unnecessary escalation rate;
- time-to-terminal;
- retry count / loop budget exhaustion.

A candidate policy that reduces errors by escalating every case should be rejected.

## Specification provenance and the formalization gap

Formal verification can prove `implementation satisfies specification` while the specification itself is wrong.

WorldLoop must therefore retain provenance for obligations/specifications themselves:

```text
user intent
  -> source evidence
  -> derived obligation
  -> formal/typed contract
  -> runtime/proof check
```

Each transformation should eventually state whether it was:

- directly supplied;
- deterministically derived;
- semantically inferred;
- human approved;
- empirically learned.

This is why observations, evidence, claims, hypotheses, decisions, proposals, authorizations, executions, and verifications should remain distinct durable object types rather than collapsing into generic text.

## Security-context continuity

Separating reasoning from authority is necessary but insufficient. Across every component boundary, WorldLoop eventually needs to preserve the bounded context that justifies an effect:

```text
principal / who requested it
intent / why
source provenance
derivation / transformations
delegated authority and scope
policy version
exact admitted effect
freshness / validity
verification/finality
```

No adapter should silently widen, drop, or reinterpret this context as work moves through model, retrieval, WorldLoop, LifeOps, Bridge, and provider/API boundaries.

This is a post-hackathon production requirement, not a reason to expand the one-day MVP.

## Future NodeSpec expansion

After the hackathon proof works, a richer node contract can add:

```text
reads
writes
required_capabilities
assumptions
uncertainty_contract
budget
timeout
retry_policy
idempotency semantics
verifier
rollback / compensation semantics
```

These matter especially for consequential or partially effectful workflows, but they are intentionally outside the current fixture MVP.

## Relationship to current build

Tonight's target remains narrow:

1. emit real `TransitionCheck` records from the existing fixture engine;
2. trace those records in Weave;
3. visualize the failing obligation and transition delta in marimo;
4. use the generated held-out task family to decide whether program/policy v1 genuinely improves;
5. reject candidates that gain safety only by harming liveness.

No Lean/Dafny theorem-prover integration is required for the hackathon claim.
