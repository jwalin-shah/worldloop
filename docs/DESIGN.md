# WorldLoop Design Specification

WorldLoop is the hackathon-new project for CoreWeave Hacks: Agent Loops. It is a **self-improving context, resource, and execution compiler**: a control system that learns what a task should know, which cognitive resources it should use, and how successful open-ended behavior can be compiled into a smaller typed workflow with explicit transitions and bounded semantic decisions.

The hackathon loop remains visible because it is the learning/debugging mechanism. The long-term runtime destination is **not** a model-owned open-ended loop; it is a typed state machine that is deterministic where possible, source-backed where facts are mutable, semantically intelligent only where judgment is irreducible, and separately governed for consequential effects.

This file is the canonical broad design. `TYPED_EXECUTION_IR.md` defines the runtime IR contract. `ARCHITECTURE.md` is the visual map. `experiments/registry.json` is the executable research plan. `PRIOR_WORK.md` defines the eligibility boundary.

## 1. Problem

Intelligent systems have several possible sources of capability:

- knowledge behaviorally accessible from model parameters;
- information already present in active context;
- external memory / retrieval systems;
- alternate models with different capability/cost profiles;
- deterministic code;
- tools and executable environments;
- independent verification;
- human escalation.

Most agent systems choose among these with fixed heuristics or an unconstrained LLM loop: always retrieve, always stuff a large context, always call a frontier model, or repeatedly ask a model what to do next. This creates both **under-allocation** (hallucination, stale knowledge, missing evidence) and **over-allocation** (unnecessary retrieval, context, semantic reasoning, latency, tools, and model spend).

It also creates a software-architecture problem: when the model owns global control flow, state transitions become difficult to reason about, test, replay, constrain, and verify.

WorldLoop therefore optimizes two coupled objectives:

1. **choose the cheapest sufficient cognitive resources for verified task completion**;
2. **minimize the semantic surface area by compiling repeated successful behavior into explicit typed programs**.

## 2. Project claim

### Minimum hackathon claim

> When a task fails because WorldLoop chose the wrong context/retrieval/resource strategy, it can diagnose the failure, change the actual decision policy, rerun, and measurably improve.

This demonstrates self-correction.

### Stronger learning claim

> A candidate policy/program derived from previous trajectories improves first-pass behavior or reduces routing/context regret on unseen tasks at equal or better verified correctness.

This requires frozen held-out evaluation.

### Stronger compilation claim

> WorldLoop can replace some broad/open-ended reasoning with deterministic transitions or narrower typed semantic primitives, reducing semantic-surface ratio without degrading held-out verified success or guardrails.

Same-task retry is self-correction. Cross-task held-out improvement is learning. Held-out reduction in semantic surface is progressive compilation.

## 3. Project boundary

### Hackathon-new

- WorldLoop context/resource/compiler logic;
- typed workflow/state-machine IR added during the event;
- evidence packet and Context Manifest contracts;
- Compiler / Critic / Loop Doctor learning roles;
- deterministic public fixture benchmark;
- Weave instrumentation and evaluation schema;
- marimo WorldLoop Lab;
- provider/model adapters added during the event;
- training/counterfactual data pipeline added during the event;
- optional read-only adapters to prior systems;
- policy/program comparison, promotion, rejection, and rollback logic.

### Prior work / external infrastructure

- LifeOps / Universal Knowledge Fabric;
- LiveLM / BTW index and historical corpus;
- HomeBase / Bridge authority system;
- Orca development governance;
- historical LiveLM benchmarks and prior observations.

Prior work may be connected through clearly labeled adapters. The public judging baseline must remain reproducible without private prior systems.

## 4. Axioms

1. **The world is not the model.** Mutable truth belongs in source-backed, versioned state, not implicitly in model weights.
2. **Context is working memory, not durable memory.** Preserve durable state; materialize only the working set needed now.
3. **Knowledge location is empirical.** Do not infer “the model knows” from self-reported confidence alone.
4. **Evidence and inference are distinct.** A generated claim never silently becomes authoritative evidence.
5. **Reasoning is not authority.** Retrieval, planning, confidence, or semantic output do not confer permission to mutate external systems.
6. **Execution is not verification.** An actuator reporting success is not evidence that the intended postcondition holds.
7. **Improvement must be measured.** Candidate policies/programs are promoted only after frozen held-out evaluation.
8. **Compute is a resource.** Model size, retrieval depth, verification, tool use, and compute placement all have cost/capability tradeoffs.
9. **Failure should be classified before repair.** “Try harder” is not a learning algorithm.
10. **The model does not own global control flow.** Semantic intelligence is local to typed nodes; explicit transition logic owns the workflow.
11. **Minimize semantic surface area.** Use nondeterministic intelligence only where deterministic or narrower typed logic cannot preserve verified utility.
12. **Source identity is part of state.** Every experiment binds exact code, data, evidence, workflow, model, policy, and scorer versions.
13. **No hidden dependency.** The core demo must work without LifeOps, BTW, TypeSafe, SkyPilot, or any single remote credential.

## 5. Invariants

- No silent context loss: the Context Manifest records what was selected, omitted, superseded, truncated, and versioned.
- Every workflow node has typed inputs/outputs and explicit transition semantics.
- No free-form model response implicitly chooses the next workflow state.
- Fail closed on missing or irreconcilably conflicting required evidence.
- Every substantive run has `experiment_id`, `run_id`, code revision, dataset/evidence snapshot, workflow/program version, provider/model, policy version, and scorer version.
- Counterfactual oracle results used as training labels are never available to the online router before it acts.
- Train/test leakage is prohibited across held-out task/entity/time clusters.
- A proposal is not authorization; authorization is not execution; execution is not verification.
- Model confidence never mints authority.
- A candidate policy/program cannot replace the incumbent without evaluation and rollback information.
- Mutable source truth outranks stale parametric memory when the task depends on current state.
- Prior-work adapters are read-only by default in the hackathon project.

## 6. Two loops, two responsibilities

### A. Runtime execution path

The production destination is:

```text
typed input
  -> Context Manifest + evidence obligations
  -> typed workflow IR
  -> deterministic / retrieval / semantic / tool nodes
  -> explicit transition predicates
  -> typed result or proposed effect
  -> separate authorization if consequential
  -> bounded actuation
  -> independent verification
  -> typed result / receipt
```

The runtime may contain semantic intelligence, but semantic nodes are bounded primitives inside a program rather than the owner of the whole program.

### B. Learning/debugging loop

The hackathon-visible loop is:

```text
execute candidate graph
  -> observe in Weave
  -> Critic classifies node / evidence / resource / transition failure
  -> Loop Doctor / ARIA proposes graph, node, context, threshold, or model change
  -> frozen held-out evaluation
  -> promote | reject | rollback
```

This loop may be exploratory and multi-agent because its job is to improve the program.

## 7. Learning roles

WorldLoop should visibly expose cooperating roles for the hackathon, but they are **development/learning roles**, not the long-term production-control abstraction.

### A. Compiler / Epistemic Router

Input: task/objective, Context Manifest, budget, available resources, incumbent workflow/policy version.

Responsibilities:

- identify evidence obligations;
- choose initial retrieval/context/resource recipe;
- increasingly compile or select a typed workflow graph;
- choose model/provider/tool/verification depth per bounded node;
- respect token, latency, tool-call, and cost budgets;
- emit a typed program/plan before execution.

It does not judge its own success.

### B. Critic / Verifier

Input: task, workflow/node identity, obligations, evidence packet, candidate outputs, deterministic/source-aware scorer state.

Responsibilities:

- check required evidence coverage;
- detect stale/contradictory support;
- detect unsupported claims;
- detect invalid transitions/schema violations;
- classify failure cause;
- determine whether the task is sufficiently solved or should fail closed.

Preferred failure classes include:

- `missing_evidence`;
- `semantic_retrieval_miss`;
- `cross_entity_join`;
- `temporal_staleness`;
- `contradictory_sources`;
- `reader_interpretation_failure`;
- `model_capability_failure`;
- `semantic_node_failure`;
- `transition_failure`;
- `tool_execution_failure`;
- `verification_failure`;
- `true_insufficient_evidence`;
- `unnecessary_retrieval`;
- `unnecessary_semantic_reasoning`.

### C. Loop Doctor / Policy Researcher

Input: failure classification plus prior trajectory/program.

Responsibilities:

- change the relevant decision variable instead of merely rewriting prose;
- add/remove retrieval operators;
- alter context schema or evidence obligations;
- replace broad reasoning with a deterministic or narrower semantic node;
- change explicit branches/transitions/thresholds;
- escalate/de-escalate model/tool/verification resource usage;
- emit the reason for the graph/policy change;
- aggregate repeated failures into candidate cross-task program changes.

For the hackathon, the inner Loop Doctor may be deterministic/rule-based while the outer Policy Researcher may use ARIA or another model to propose experiments.

## 8. Typed workflow IR

The runtime centerpiece is specified in `TYPED_EXECUTION_IR.md`.

A workflow version eventually binds:

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

Node classes:

- deterministic;
- retrieval;
- semantic;
- tool;
- authorization;
- actuation;
- verification;
- terminal.

A semantic result may influence a transition, but the workflow engine evaluates typed output against explicit predicates.

## 9. Intelligence primitives

Provider neutrality should exist at the infrastructure layer without collapsing every capability into `messages -> text`.

Semantic primitives:

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

Different providers can implement different subsets. TypeSafe is interesting as a candidate bounded semantic-node provider if its actual onsite interface supports machine-native decision/classification/prediction. Do not invent an API or calibration guarantee that has not been exposed.

## 10. Confidence, stakes, authority, verification

These are distinct objects.

```text
semantic node:
  what do I believe / decide, with what empirically calibrated uncertainty?

risk/stakes policy:
  is that uncertainty acceptable for this class of decision?

authority layer:
  is this actor permitted to cause the proposed effect?

verifier:
  did reality actually change as intended?
```

Self-reported prose confidence is not calibration. Even well-calibrated high confidence is not authority.

## 11. Core data contracts

### Context Manifest

Required eventual fields:

```json
{
  "run_id": "run-uuid",
  "experiment_id": "EXP-...",
  "code_revision": "git-sha",
  "dataset_snapshot": "snapshot-id",
  "evidence_snapshot": "snapshot-id",
  "workflow_version": "workflow-v0",
  "selected_object_refs": [],
  "omitted_candidate_refs": [],
  "superseded_refs": [],
  "truncated": false,
  "context_hash": "sha256",
  "context_tokens": 0,
  "policy_version": "policy-v0",
  "provider": "...",
  "model": "..."
}
```

### Evidence Item

Must preserve at minimum:

- stable evidence ID;
- source identity;
- content or normalized claim;
- observation time;
- event/validity time when applicable;
- entity/object refs;
- provenance chain;
- freshness / supersession status.

### Node Result

```json
{
  "node_id": "decision-3",
  "node_type": "semantic",
  "primitive": "DECIDE",
  "value": "OPTION_A",
  "confidence": 0.91,
  "abstained": false,
  "evidence_refs": ["E03"],
  "provider": "...",
  "model": "...",
  "node_version": "..."
}
```

Confidence is optional unless the provider supplies a meaningful calibrated quantity; a prose confidence estimate must not be mislabeled as calibration.

### Pass / trajectory record

```json
{
  "pass": 1,
  "workflow_version": "workflow-v0",
  "recipe": ["vector"],
  "evidence_refs": ["E03"],
  "failure_class": "cross_entity_join",
  "policy_change": null,
  "score": 0.5,
  "semantic_node_count": 1,
  "latency_ms": 0,
  "cost": null,
  "sufficient": false
}
```

### Policy/program version

A comparable candidate binds:

- workflow graph and transition logic;
- routing/context algorithm/config;
- prompt/schema/node versions;
- available action/resource space;
- model/provider selection logic;
- evidence and risk policies;
- budget rules;
- training-data artifact if learned;
- exact scorer/eval version used for promotion;
- rollback reference.

## 12. Action/resource space

The architecture should support this superset even if the MVP uses only a subset:

- deterministic code;
- model-only reasoning;
- active context only;
- exact lookup;
- lexical retrieval;
- vector retrieval;
- temporal retrieval/filtering;
- graph traversal;
- typed Facts;
- Stories / richer memory;
- deeper source retrieval;
- alternate model/provider;
- bounded semantic primitive;
- tool/code execution;
- independent verifier;
- abstention / request more evidence;
- human escalation.

The compiler should not invoke a resource merely because it exists.

## 13. Evaluation ontology

Per task / trajectory:

- final verified correctness or correct abstention;
- evidence coverage/recall;
- citation/provenance validity;
- unsupported-claim count;
- stale-evidence usage;
- contradiction handling;
- passes/recovery rate;
- retrieval/tool calls;
- unnecessary resource use;
- latency;
- token usage;
- cost where available;
- trace completeness;
- first-pass success;
- cross-session continuity where applicable;
- semantic-node count;
- semantic-surface ratio;
- open-loop branch count;
- compilation ratio;
- calibration error where a calibrated probability exists;
- authority violations.

### Retrieval/context regret

Penalty for using more context/retrieval than the cheapest successful counterfactual route.

### Under-allocation regret

Penalty for choosing a cheap route that fails when an available escalation would have succeeded.

### Routing regret

Conceptually:

`U(best observed route) - U(chosen route)`

where utility rewards verified correctness/support and penalizes cost, latency, unnecessary context/tool/semantic use, and unsupported claims.

### Recovery rate

Among first-pass failures, fraction repaired within the allowed pass budget.

### Semantic-surface ratio

Fraction of executed workflow nodes requiring nondeterministic semantic intelligence.

### Compilation ratio

Fraction of previously open-ended/semantic operations replaced by deterministic or narrower typed transitions without degrading held-out verified success.

## 14. W / C / M knowledge-location experiment

Define:

- **W**: parameterized knowledge, causally manipulated on an open model using LoRA on/off;
- **C**: explicitly supplied active context;
- **M**: externally retrievable memory.

Use a synthetic fictional world so target facts cannot plausibly be inherited from pretraining. Run the 2^3 W/C/M matrix plus conflict/staleness cases.

The controlled benchmark should answer:

- when is a fact behaviorally accessible from parameters alone?;
- when does supplied context override or conflict with parameterized memory?;
- when does the system correctly retrieve external memory?;
- does it retrieve unnecessarily when W or C already suffices?;
- how does it react when W is stale but M is current?;
- how much semantic reasoning remains necessary once the correct evidence is available?;
- which models/programs best allocate cognitive resources per dollar/token/latency?

For closed hosted models, call this **behavioral parametric attribution**, not direct proof of what is physically stored in weights.

## 15. What gets trained or optimized

Do not train mutable user/project facts into weights as the primary architecture.

### Context Materializer

`task + durable candidates + budget -> minimum sufficient working set`

Objective penalizes missed relevant state, stale state, irrelevant context, and token cost.

### Epistemic / Resource Router

`task features + pre-action signals + Context Manifest + budget -> resource/action choice`

Offline counterfactual runs can execute many candidate actions and label the best observed action. The online policy may use only pre-action features.

### Workflow compiler / graph policy

`task family + successful/failing trajectories -> candidate typed workflow / transition/node changes`

The candidate may reduce semantic surface by replacing broad reasoning with deterministic code or narrower primitives.

### Semantic nodes

Only when there is evidence that a bounded learned primitive materially outperforms simpler rules/models. Fine-tune the narrow semantic capability rather than mutable world facts.

Potential implementations by increasing ambition:

1. deterministic policy table / graph template;
2. logistic/tree/small supervised router;
3. small semantic model;
4. LoRA-tuned router/node;
5. reward-optimized / RL policy only after the eval contract is stable.

## 16. Progressive compilation lifecycle

```text
open exploratory behavior
  -> traced trajectories
  -> repeated successful pattern
  -> candidate typed graph
  -> replace broad reasoning with deterministic/narrow nodes
  -> frozen held-out evaluation
  -> compare correctness + regret + semantic surface + safety
  -> canary
  -> promote | reject
```

Lower semantic surface is desirable only when correctness, evidence obligations, safety boundaries, and failure behavior remain acceptable.

## 17. Tool/system boundaries

### W&B Weave — proof plane (CORE)

Use for trajectory spans, graph/node versions, context/policy attributes, custom scores, latency/cost, evaluation datasets, and v0-v1 comparisons. Weave is where self-correction, learning, and compilation claims become inspectable.

### marimo / molab — scientific workstation + demo (CORE)

Use one reactive notebook/app as the live experimental control surface for:

- benchmark/case selector;
- current Context Manifest;
- typed workflow graph/current node;
- pass-by-pass evidence and program changes;
- failure-class explorer;
- policy/program v0 vs v1 scorecard;
- semantic-surface/compilation view;
- W/C/M cube;
- counterfactual action matrix;
- experiment registry;
- optional training controls/results;
- links/IDs to Weave runs;
- provider/model switcher when available.

molab GPU is for interactive counterfactual inference, embedding/representation analysis, and bounded fine-tuning. Do not rely on molab as a persistent artifact store; publish durable artifacts to Git/W&B/approved storage.

marimo pair is useful because a coding/research agent and human can operate over the same live reactive computational state. It must not become canonical project memory.

### W&B Models / Artifacts — training lineage (STRONG EXTENSION)

Version datasets, candidate policy/program/model artifacts, training configs, checkpoints, and lineage from trajectory data to promoted version.

### W&B Inference — model fleet (STRONG EXTENSION)

Use one request/eval contract across comparable hosted models. It may also serve a LoRA variant if training lands.

### ARIA — outer scientific loop (STRONG EXTENSION)

ARIA should inspect real WorldLoop/Weave failure data, form one concrete hypothesis, propose or launch a bounded graph/node/context/model experiment, and compare against the incumbent. Do not use it merely to summarize charts.

### TypeSafe AI — semantic-node candidate (CONDITIONAL)

Evaluate TypeSafe inside bounded primitives such as `CLASSIFY`, `DECIDE`, or `PREDICT` if the onsite interface actually exposes suitable structured/calibrated behavior. Compare verified reward, calibration if available, latency, cost, abstention, and downstream transition stability. Do not make undocumented capabilities a hard dependency.

### CoreWeave Sandboxes — isolated stateful nodes (CONDITIONAL)

Use only when a workflow node executes generated/untrusted code or mutates state across steps. Static retrieval experiments do not require sandbox theater.

### SkyPilot — compute/job plane (OPTIONAL)

WorldLoop defines the experiment; SkyPilot may launch reproducible parallel jobs on CoreWeave Kubernetes or other approved resources. It never owns workflow semantics, durable state, or authority.

### LifeOps / BTW — optional prior-work adapters

LifeOps supplies provider-neutral durable continuity; BTW/LiveLM may serve as a real changing-world evidence backend. Both are clearly prior work. The public core benchmark cannot depend on them.

### HomeBase / Bridge — authority layer outside core demo

Consequential side effects are proposed, authorized, executed, and independently verified through separate authority machinery. Semantic confidence never grants action authority.

## 18. marimo product surface

The intended WorldLoop Lab should have six views.

### A. Live Execution

Show one selected task with:

- task/evidence obligations;
- Context Manifest;
- compiled workflow graph and current node;
- evidence selected;
- typed node outputs;
- Critic score/failure class;
- Loop Doctor graph/policy delta;
- next transition/pass;
- final supported result/abstention;
- Weave trace ID.

### B. Policy / Program Comparison

Compare v0 vs v1 on held-out tasks:

- first-pass success;
- final success;
- recovery rate;
- routing regret;
- retrieval/context use;
- semantic-node count / semantic-surface ratio;
- latency and cost.

### C. Knowledge Location

Interactive W/C/M cube with toggles for parameterized adapter, active context, and external memory, including conflict cases.

### D. Failure Explorer

Aggregate failure classes and drill into exact node/transition/evidence failures and counterfactual successful routes.

### E. Compilation View

Show before/after graph and identify which open-ended operations became deterministic or narrower semantic primitives.

### F. Experiment Registry

Show experiment status, hypothesis, independent variable, metrics, artifact refs, and stop rule. The notebook is an experiment client, not the canonical registry itself.

## 19. Realistic three-minute demo

1. **Problem:** agents use the wrong knowledge/resources and often let the model own too much control flow.
2. **Failure:** `case-cross-entity` starts with an insufficient retrieval node and fails.
3. **Diagnosis:** Critic identifies `cross_entity_join` and missing support.
4. **Repair:** Loop Doctor changes an actual node/resource decision, e.g. vector -> vector+graph.
5. **Weave proof:** show exact program/policy version, failure, node/policy delta, rerun, and score.
6. **Learning:** compare v0 vs v1 on frozen held-out tasks.
7. **Stronger result if ready:** show EXP-011 reducing semantic surface/open-loop branching without correctness loss.
8. **Close:** “WorldLoop uses the loop to learn the smallest verified typed program that can do the work over a changing world.”

## 20. Judging alignment

- **Best Loop:** visible self-correction plus held-out program/policy improvement.
- **Creativity:** cooperating learning roles improve a typed program instead of merely running personas in a chat loop.
- **Utility:** reduces hallucination/under-contexting, excessive model/tool spend, and unbounded runtime behavior.
- **Technical execution:** typed IR, deterministic baseline, provenance, failure taxonomy, versioned programs, held-out eval, fail-closed behavior, authority separation.
- **Sponsor usage:** Weave is structural; marimo is the live research surface; ARIA/TypeSafe/Models/Inference are used only when they add measured value.

Primary sponsor track recommendation remains **Best Use of Weave**. All projects remain eligible for Best Loop.

## 21. Failure modes and mitigations

### Demo looks like ordinary RAG

Mitigation: show the actual program/resource/node delta, independent verification, held-out comparison, and—if ready—semantic-surface reduction.

### Same-task retry is mistaken for learning

Mitigation: separate inner self-correction from outer held-out program evaluation.

### “Compiled” means hard-coded to one fixture

Mitigation: EXP-011 uses held-out variants/task families; accept only if the typed candidate generalizes.

### Typed output is confused with true calibration

Mitigation: distinguish schema-constrained output from empirically calibrated confidence. Measure calibration only when the provider exposes a meaningful probability/score and enough evaluation data exist.

### Model confidence becomes authority

Mitigation: semantic output -> risk/stakes policy -> separate authorization -> actuation -> independent verification.

### LLM judge circularity

Mitigation: use deterministic/source-aware checks first; if an LLM judge is needed, use a distinct stronger/different judge and keep judge version visible.

### Router leaks counterfactual answers

Mitigation: offline oracle can see all arms; online policy can use only pre-action features.

### Training set too small

Mitigation: do not force neural fine-tuning. Use rules/graph templates/simple policies first; preserve held-out entity/time/task clusters.

### Retrieval is rewarded just because it produces citations

Mitigation: explicitly penalize unnecessary retrieval/context/tool calls and measure retrieval harm.

### Semantic intelligence is rewarded just because it is sophisticated

Mitigation: explicitly measure semantic-node count/surface and prefer simpler deterministic behavior when correctness holds.

### Sponsor integration becomes decoration

Mitigation: every sponsor tool must answer a real architectural need or remain optional.

### Live BTW/private data creates eligibility or privacy ambiguity

Mitigation: sanitized fixtures are core; BTW is read-only optional validation and labeled prior work.

### molab storage/session loss

Mitigation: commit source to GitHub and publish durable datasets/models/results through W&B or another approved persistent store; never trust notebook filesystem as canonical state.

### Self-improvement changes production behavior unsafely

Mitigation: candidate -> held-out eval -> guardrails -> canary -> promote/reject; preserve rollback.

## 22. MVP / extensions / non-goals

### Must ship

- deterministic public benchmark still reproducible;
- three visible learning/debugging roles;
- one complete Weave trajectory;
- one marimo live execution view;
- failure -> actual graph/resource/policy change -> verified repair;
- workflow/policy version schema;
- held-out comparison or a clearly separated held-out scaffold if time blocks training;
- transparent prior-work boundary.

### Strong extensions

- first typed workflow/state-machine representation;
- EXP-011 before/after progressive compilation result;
- provider/model abstraction and W&B Inference matrix;
- ARIA-generated graph/node experiment actually executed;
- W/C/M causal benchmark;
- simple trained router / LoRA;
- read-only BTW adapter.

### Optional

- SkyPilot parallel experiment jobs;
- CoreWeave Sandbox executable workflow node;
- mechanistic probes on open-model hidden states.

### Non-goals for the weekend

- rebuild LifeOps;
- rebuild BTW;
- full HomeBase/Bridge deployment;
- universal personal Agent OS;
- large-scale RL;
- multi-cloud scheduler product;
- exhaustive mechanistic interpretability;
- production mutation of external systems;
- fully general compiler for arbitrary human workflows.

## 23. Decision rule for every new feature

Before adding anything, ask:

1. Does it make the self-improving loop or typed runtime more real/measurable?
2. Does it improve verified correctness, resource regret, semantic surface, causal evidence, or production safety?
3. Does it improve a published judging dimension?
4. Can it produce a real result before submission without destabilizing the core demo?
5. Does it have a clear source/version/eval/authority boundary?
6. Is it doing work no existing component already owns?

If the answer is not clearly yes, do not add it during the hackathon.
