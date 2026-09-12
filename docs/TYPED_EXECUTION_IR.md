# WorldLoop Typed Execution IR

WorldLoop should not treat an open-ended agent loop as the final production architecture. The loop is a **learning, debugging, and compilation mechanism**. The runtime destination is a typed workflow/state machine in which deterministic behavior is explicit, external evidence is source-backed, semantic intelligence is isolated to bounded nodes, consequential effects cross a separate authority boundary, and the actual world change is independently verified.

The design objective is:

> **Minimize the semantic surface area while preserving verified task success.**

The best WorldLoop policy is therefore not merely the one that retries successfully. It is the one that can progressively convert repeated successful behavior into a smaller, more explicit, more testable execution graph while retaining only the irreducible semantic judgments.

## 1. Two loops, two jobs

### Development / learning loop

```text
execute candidate graph
  -> observe in Weave
  -> Critic classifies failures
  -> Loop Doctor / ARIA proposes graph, node, context, or model change
  -> evaluate candidate on frozen tasks
  -> promote | reject | rollback
```

This loop may be exploratory and agentic.

### Production execution path

```text
typed input
  -> typed workflow IR
  -> explicit state transition
  -> bounded deterministic / retrieval / semantic / tool nodes
  -> proposed effect
  -> authority boundary if consequential
  -> bounded actuator
  -> independent verification
  -> typed output / durable receipt
```

The model does **not** own global control flow.

## 2. Workflow IR

A compiled WorldLoop program should eventually bind at least:

```json
{
  "workflow_id": "workflow-...",
  "workflow_version": "v1",
  "compiler_version": "...",
  "policy_version": "...",
  "input_schema": "...",
  "output_schema": "...",
  "initial_state": "S0",
  "states": [],
  "transitions": [],
  "budgets": {},
  "risk_policy": "...",
  "evidence_policy": "...",
  "rollback_ref": "..."
}
```

Every state/node has a typed input and typed output. Every transition has an explicit predicate. A free-form language-model response is never itself an implicit transition.

## 3. Node classes

### Deterministic node

Pure code, validation, formatting, arithmetic, schema conversion, policy checks, static routing, or any behavior that does not require semantic judgment.

### Retrieval node

Reads source-backed evidence through a typed adapter and returns provenance-bearing `EvidenceItem[]`. Retrieval does not decide truth or authorization.

### Semantic node

Performs one bounded intelligence primitive over typed inputs. It should have no broader authority than the primitive requires.

### Tool node

Invokes a bounded external tool or computation with typed arguments and captures typed output/errors.

### Authorization node

Asks a separate authority system whether a proposed consequential effect is permitted. Model confidence never bypasses this node.

### Actuation node

Executes only an admitted, bounded action.

### Verification node

Checks whether the intended real-world postcondition actually holds and emits evidence/receipt.

### Terminal node

Returns a typed result, abstention, escalation, or verified receipt.

## 4. Intelligence primitives

Provider neutrality should exist at the infrastructure layer, but WorldLoop should not erase semantically different model capabilities into one lowest-common-denominator `messages -> text` interface.

The semantic layer should expose primitives such as:

```text
GENERATE
  context -> artifact

CLASSIFY
  evidence -> enum + confidence

DECIDE
  evidence + alternatives + stakes
  -> alternative | abstain + confidence

EXTRACT
  evidence -> typed facts + provenance

PLAN
  goal + world state -> typed proposed graph

CRITIQUE
  artifact + invariant set -> violations[]

PREDICT
  state + intervention -> distribution(outcomes)

VERIFY
  claim + evidence -> supported | contradicted | unknown
```

A provider implements only the primitives it actually supports well. Claude/Gemini/OpenAI-style models may be strongest for generation/planning/code; a TypeSafe-like model may be especially interesting for bounded decision/classification/prediction if the onsite interface supports those capabilities; deterministic code should implement everything that does not need semantic intelligence.

Do not claim a TypeSafe API that has not been publicly or onsite documented. WorldLoop owns the primitive contract; adapters map real provider interfaces into it.

## 5. Semantic result contract

A semantic node should return something closer to:

```json
{
  "primitive": "DECIDE",
  "value": "PARTIAL_REFUND",
  "confidence": 0.982,
  "abstained": false,
  "evidence_refs": ["E12", "E19"],
  "provider": "...",
  "model": "...",
  "node_version": "..."
}
```

Confidence is useful only if it is empirically calibrated for the node/task distribution. Self-reported prose confidence is not calibration.

## 6. Confidence, stakes, and authority are different

WorldLoop should separate three questions:

```text
SEMANTIC NODE
What does the system believe should happen, and with what calibrated uncertainty?

RISK / STAKES POLICY
Is the uncertainty acceptable for this class of decision?

AUTHORITY LAYER
Is this actor permitted to perform the consequential effect?

VERIFIER
Did reality actually change as intended?
```

Example:

```text
semantic decision = MOVE_EVENT
calibrated confidence = 0.88
stakes = MEDIUM
autonomy threshold = 0.97

=> ESCALATE / PROPOSE, not execute
```

Even a confidence of `0.999` does not mint authority.

## 7. Explicit transition rule

A semantic node cannot emit arbitrary next-state instructions. The workflow engine evaluates typed output against explicit transition rules.

Example:

```text
S_CHECK
  -> DECIDE[Acceptability]

if decision=ACCEPT and confidence>=threshold:
  -> S_PROPOSE

if abstain or confidence<threshold:
  -> S_ESCALATE
```

This keeps nondeterministic intelligence local while control flow remains inspectable and testable.

## 8. Compilation

WorldLoop should learn not only **which resource to call**, but **which portions of a repeated workflow no longer require open-ended reasoning**.

A candidate compilation may:

- replace an LLM-generated transformation with deterministic code;
- replace free-form planning with a typed graph template;
- replace an open-ended tool-selection loop with an explicit branch;
- replace broad reasoning with a narrow `CLASSIFY` or `DECIDE` semantic node;
- add evidence obligations before a semantic node;
- add confidence/stakes thresholds and an abstention path;
- move execution behind an authorization node;
- add an independent postcondition verifier.

Compilation must be evaluated against the same frozen tasks/guardrails before promotion.

## 9. New metrics

In addition to verified correctness, routing regret, latency, cost, recovery, and evidence quality, measure:

### Semantic node count

Number of nondeterministic semantic decisions executed on a successful path.

### Semantic surface ratio

Fraction of executed workflow nodes that require nondeterministic semantic intelligence.

### Open-loop branching

Number of transitions whose next state is not statically represented in the IR. Production target is zero unless explicitly admitted as a bounded subgraph.

### Compilation ratio

Fraction of previously semantic/open-loop operations replaced by deterministic or typed bounded transitions without degrading held-out verified success.

### Calibration error

For semantic nodes that emit probabilistic confidence, compare predicted confidence with empirical correctness over the relevant node distribution.

### Authority violations

Count of execution attempts that bypass the explicit authorization boundary. Target: zero.

## 10. WorldLoop compilation lifecycle

```text
open exploratory behavior
  -> traced trajectories
  -> repeated successful pattern
  -> candidate typed graph
  -> node-level semantic obligations
  -> frozen held-out evaluation
  -> compare success + regret + semantic surface
  -> canary
  -> promote | reject
```

A lower semantic surface is desirable only if verified correctness, evidence obligations, safety boundaries, and failure behavior remain acceptable.

## 11. Relationship to the hackathon loop

For the hackathon, the visible Compiler / Critic / Loop Doctor loop remains useful because it makes learning legible. The stronger interpretation is now:

- **Compiler** chooses or compiles a typed execution graph/resource plan.
- **Critic** identifies which node/transition/evidence obligation failed.
- **Loop Doctor** edits the graph, node, primitive, threshold, evidence policy, or model choice.
- **Weave** records exact graph/node versions and outcomes.
- **marimo** visualizes the graph and compares candidate programs.
- **ARIA** may propose an outer-loop experiment over graph/node/policy changes.

The production destination is not an infinitely wandering agent. It is a progressively compiled intelligent program.

## 12. Relationship to external knowledge and authority

External knowledge remains separate from intelligence:

```text
LiveLM / BTW / source-native API
  -> EvidenceItem[]
  -> Context Materializer
  -> typed semantic/deterministic node
```

Consequential effects remain separate from epistemics:

```text
semantic result
  -> proposed effect
  -> HomeBase / Bridge authority
  -> actuator
  -> independent verifier
  -> durable world-state update
```

This preserves the existing WorldLoop/LifeOps principle that world truth, reasoning, authority, execution, and verification are distinct layers.

## 13. North-star statement

> **WorldLoop learns to turn open-ended agent behavior into the smallest verified typed program that can reliably accomplish the task over a changing world.**

The outer loop remains self-improving. The runtime path becomes progressively less agentic, more explicit, and easier to verify.
