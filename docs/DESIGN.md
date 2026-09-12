# WorldLoop Design Specification

WorldLoop is the hackathon-new project for CoreWeave Hacks: Agent Loops. It is a **self-improving context and epistemic/resource compiler**: a control system that decides what an agent should know, where that knowledge should come from, what resource should handle the task, whether the result is sufficiently supported, and what policy should change after failure.

This file is the canonical design. `ARCHITECTURE.md` is the visual map; `EXPERIMENTS` in `experiments/registry.json` is the executable research plan; `PRIOR_WORK.md` defines the eligibility boundary.

## 1. Problem

Agents have several possible sources of cognition:

- knowledge behaviorally accessible from model parameters;
- information already present in active context;
- external memory / retrieval systems;
- alternate models with different capability/cost profiles;
- tools and executable environments;
- independent verification;
- human escalation.

Most systems choose among these with fixed heuristics: always retrieve, always stuff a large context, always call a frontier model, or ask another LLM to choose without a reproducible objective. This creates both **under-allocation** (hallucination, stale knowledge, missing evidence) and **over-allocation** (unnecessary retrieval, context, latency, tool calls, and model spend).

WorldLoop learns or derives the **cheapest sufficient path to verified task completion**.

## 2. Hackathon claim

The minimum valid claim is:

> When an agent fails because it used the wrong context/retrieval strategy, WorldLoop can diagnose the failure, change the context-building behavior, rerun, and measurably improve.

The stronger self-improvement claim requires held-out evidence:

> A policy produced from previous trajectories improves first-pass behavior or reduces routing/context regret on unseen tasks at equal or better verified correctness.

Same-task retry demonstrates self-correction. Cross-task held-out improvement demonstrates learning.

## 3. Project boundary

### Hackathon-new

- WorldLoop context compiler / router;
- evidence packet and context-manifest contracts;
- Critic / Verifier role;
- Loop Doctor / Policy Researcher role;
- deterministic public fixture benchmark;
- Weave instrumentation and evaluation schema;
- marimo WorldLoop Lab;
- provider/model adapters added during the event;
- training/counterfactual data pipeline added during the event;
- optional read-only adapters to prior systems;
- policy comparison, promotion, rejection, and rollback logic.

### Prior work / external infrastructure

- LifeOps / Universal Knowledge Fabric;
- LiveLM / BTW index and historical corpus;
- HomeBase / Bridge authority system;
- Orca development governance;
- historical LiveLM benchmarks and prior observations.

Prior work may be connected through clearly labeled adapters. The public judging baseline must remain reproducible without private prior systems.

## 4. Axioms

1. **The world is not the model.** Mutable truth belongs in source-backed, versioned state, not implicitly in model weights.
2. **Context is working memory, not durable memory.** Preserve all relevant durable state; materialize only the working set needed now.
3. **Knowledge location is empirical.** Do not infer "the model knows" from self-reported confidence alone.
4. **Evidence and inference are distinct.** A generated claim never silently becomes authoritative evidence.
5. **Reasoning is not authority.** Retrieval, planning, and confidence do not confer permission to mutate external systems.
6. **Improvement must be measured.** Candidate policies are promoted only after frozen held-out evaluation.
7. **Compute is a resource.** Model size, retrieval depth, verification, tool use, and compute placement all have cost/capability tradeoffs.
8. **Failure should be classified before repair.** "Try harder" is not a learning algorithm.
9. **Source identity is part of state.** Every experiment binds exact code, data, evidence, model, and policy versions.
10. **No hidden dependency.** The core demo must work without LifeOps, BTW, TypeSafe, SkyPilot, or any single remote credential.

## 5. Invariants

- No silent context loss: the Context Manifest records what was selected, omitted, superseded, truncated, and versioned.
- Fail closed on missing or irreconcilably conflicting required evidence.
- Every substantive run has `experiment_id`, `run_id`, code revision, dataset/evidence snapshot, provider/model, policy version, and scorer version.
- Counterfactual oracle results used as training labels are never available to the online router before it acts.
- Train/test leakage is prohibited across held-out task/entity/time clusters.
- A proposal is not authorization; authorization is not execution; execution is not verification.
- A candidate policy cannot replace the incumbent without evaluation and rollback information.
- Mutable source truth outranks stale parametric memory when the task depends on current state.
- Prior-work adapters are read-only by default in the hackathon project.

## 6. Agent roles

WorldLoop should be visibly multi-agent rather than one monolithic chat loop.

### A. Context Compiler / Epistemic Router

Input: task, Context Manifest, budget, available resources, policy version.

Responsibilities:

- identify evidence obligations;
- decide initial retrieval/context recipe;
- optionally choose model/provider/tool/verification depth;
- respect token, latency, tool-call, and cost budgets;
- emit a typed plan before execution.

It does **not** judge its own success.

### B. Critic / Verifier

Input: task, obligations, evidence packet, candidate output, deterministic/source-aware scorer state.

Responsibilities:

- check required evidence coverage;
- detect stale/contradictory support;
- detect unsupported claims;
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
- `tool_execution_failure`;
- `verification_failure`;
- `true_insufficient_evidence`;
- `unnecessary_retrieval`.

### C. Loop Doctor / Policy Researcher

Input: failure classification plus prior trajectory.

Responsibilities:

- change the relevant decision variable instead of merely rewriting prose;
- add/remove retrieval operators;
- alter context schema or evidence obligations;
- escalate/de-escalate model/tool/verification resource usage;
- emit the reason for the policy change;
- aggregate repeated failures into candidate cross-task policy changes.

For the hackathon, the inner Loop Doctor may be deterministic/rule-based while the outer Policy Researcher may use ARIA or another model to propose experiments.

## 7. Core execution loop

```text
Task
  -> resolve Context Manifest
  -> Context Compiler chooses action/resource plan
  -> retrieve/materialize evidence
  -> worker/model produces candidate result
  -> Critic independently verifies
      -> sufficient: emit result + receipt
      -> insufficient: classify failure
          -> Loop Doctor modifies policy/context/resource choice
          -> rerun within budget
  -> trace every transition in Weave
```

A pass is only considered an improvement when the relevant measured score changes. A second answer with unchanged evidence/context behavior is not a WorldLoop repair.

## 8. Outer learning loop

```text
many trajectories
  -> Weave dataset / evaluation table
  -> failure clustering + counterfactual comparisons
  -> candidate policy/config/model
  -> frozen held-out evaluation
  -> guardrail comparison
  -> promote | reject | rollback
```

Policy improvement may initially be a learned lookup/table/decision tree or prompt policy. Fine-tuning is an extension, not a prerequisite.

## 9. Core data contracts

### Context Manifest

Required eventual fields:

```json
{
  "run_id": "run-uuid",
  "experiment_id": "EXP-...",
  "code_revision": "git-sha",
  "dataset_snapshot": "snapshot-id",
  "evidence_snapshot": "snapshot-id",
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

### Pass Record

```json
{
  "pass": 1,
  "recipe": ["vector"],
  "evidence_refs": ["E03"],
  "failure_class": "cross_entity_join",
  "policy_change": null,
  "score": 0.5,
  "latency_ms": 0,
  "cost": null,
  "sufficient": false
}
```

### Policy Version

A comparable policy version binds:

- routing/context algorithm/config;
- prompt/schema version;
- available action space;
- model/provider selection logic;
- budget rules;
- training-data artifact if learned;
- exact scorer/eval version used for promotion.

## 10. Action/resource space

The architecture should support this superset even if the MVP uses only a subset:

- model-only;
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
- tool/code execution;
- independent verifier;
- abstention / request more evidence.

The router should not invoke a resource merely because it exists.

## 11. Evaluation ontology

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
- cross-session continuity where applicable.

Derived metrics:

### Retrieval/context regret

Penalty for using more context/retrieval than the cheapest successful counterfactual route.

### Under-allocation regret

Penalty for choosing a cheap route that fails when an available escalation would have succeeded.

### Routing regret

Conceptually:

`U(best observed route) - U(chosen route)`

where utility rewards verified correctness/support and penalizes cost, latency, unnecessary context/tool use, and unsupported claims.

### Recovery rate

Among first-pass failures, fraction repaired within the allowed pass budget.

## 12. W / C / M knowledge-location experiment

Define:

- **W**: parameterized knowledge, causally manipulated on an open model using LoRA on/off;
- **C**: explicitly supplied active context;
- **M**: externally retrievable memory.

Use a synthetic fictional world so the target facts cannot plausibly be inherited from pretraining. Run the 2^3 W/C/M matrix plus conflict/staleness cases.

The controlled benchmark should answer:

- when is a fact behaviorally accessible from parameters alone?;
- when does supplied context override or conflict with parameterized memory?;
- when does the system correctly retrieve external memory?;
- does it retrieve unnecessarily when W or C already suffices?;
- how does it react when W is stale but M is current?;
- which models/policies best allocate cognitive resources per dollar/token/latency?

For closed hosted models, call this **behavioral parametric attribution**, not direct proof of what is physically stored in weights.

## 13. What gets trained

Do not train mutable user/project facts into weights as the primary architecture.

Train or optimize:

### Context Materializer

`task + durable candidates + budget -> minimum sufficient working set`

Objective penalizes missed relevant state, stale state, irrelevant context, and token cost.

### Epistemic / Resource Router

`task features + pre-action signals + Context Manifest + budget -> resource/action choice`

Offline counterfactual runs can execute many candidate actions and label the best observed action. The online policy may use only pre-action features.

Potential implementations by increasing ambition:

1. deterministic policy table / classifier;
2. logistic/tree/small supervised model;
3. small language-model router;
4. LoRA-tuned router;
5. reward-optimized / RL policy only after the eval contract is stable.

## 14. Tool/system boundaries

### W&B Weave — proof plane (CORE)

Use for trajectory spans, agent/sub-agent/tool events, context/policy attributes, custom scores, latency/cost, evaluation datasets, and v0-v1 comparisons. Weave is where the self-improvement claim becomes inspectable.

### marimo / molab — scientific workstation + demo (CORE)

Use one reactive notebook/app as the live experimental control surface:

- benchmark/case selector;
- current Context Manifest;
- pass-by-pass evidence and policy changes;
- failure-class explorer;
- policy v0 vs v1 scorecard;
- W/C/M cube;
- counterfactual action matrix;
- experiment registry;
- optional training controls/results;
- links/IDs to Weave runs;
- provider/model switcher when available.

molab GPU is for interactive counterfactual inference, embedding/representation analysis, and bounded fine-tuning. Do not rely on molab as a persistent artifact store; publish durable artifacts to Git/W&B/approved storage.

marimo pair is useful because a coding/research agent and human can operate over the same live reactive computational state. It must not become canonical project memory.

### W&B Models / Artifacts — training lineage (STRONG EXTENSION)

Version datasets, candidate policy/model artifacts, training configs, checkpoints, and lineage from trajectory data to promoted policy.

### W&B Inference — model fleet (STRONG EXTENSION)

Use the same request/eval contract across multiple hosted models. It may also serve a LoRA variant if the training extension lands.

### ARIA — outer scientific loop (STRONG EXTENSION)

ARIA should inspect real WorldLoop/Weave failure data, form one concrete hypothesis, propose or launch a bounded experiment, and compare against the incumbent. Do not use it merely to summarize charts.

### TypeSafe AI — experimental model candidate (CONDITIONAL)

Measure it in worker, router, or verifier roles. Compare verified task reward, resource decisions, latency, cost, recovery, abstention, and unnecessary tool/retrieval calls. Do not make undocumented TypeSafe capabilities a critical dependency.

### CoreWeave Sandboxes — isolated stateful episodes (CONDITIONAL)

Use only when a task executes generated/untrusted code or mutates state across steps. Static retrieval experiments do not require sandbox theater.

### SkyPilot — compute/job execution plane (OPTIONAL)

WorldLoop defines the experiment; SkyPilot may launch many reproducible jobs on CoreWeave Kubernetes or other approved resources. It never owns agent reasoning, project state, or execution authority. Add it only if it makes W/C/M sweeps or training materially easier.

### LifeOps / BTW — optional prior-work adapters

LifeOps supplies provider-neutral durable continuity; BTW/LiveLM may serve as a real changing-world external-memory backend. Both are clearly prior work. The public core benchmark cannot depend on them.

### HomeBase / Bridge — authority layer outside core demo

Consequential side effects would be proposed, authorized, executed, and independently verified through separate authority machinery. Retrieval or model confidence never grants action authority.

## 15. marimo product surface

The intended WorldLoop Lab should have five views.

### A. Live Loop

Show one selected task with:

- task/evidence obligations;
- initial resource/context plan;
- evidence selected;
- critic score/failure class;
- Loop Doctor policy delta;
- next pass;
- final supported answer/abstention;
- Weave trace link/ID.

### B. Policy Comparison

Compare v0 vs v1 on held-out tasks:

- first-pass success;
- final success;
- recovery rate;
- routing regret;
- retrieval/context use;
- latency and cost.

### C. Knowledge Location

Interactive W/C/M cube with toggles for parameterized adapter, active context, and external memory, including conflict cases.

### D. Failure Explorer

Aggregate failure classes and allow drill-down into exact trajectories and counterfactual successful routes.

### E. Experiment Registry

Show experiment status, hypothesis, independent variable, metrics, artifact refs, and stop rule. The notebook is an experiment client, not the canonical registry itself.

## 16. Realistic three-minute demo

1. **Problem (15s):** Agents waste money/context or hallucinate because they use the wrong cognitive resources.
2. **Failure (30s):** Pick `case-cross-entity`. Show Compiler chooses an insufficient recipe and pass 1 fails.
3. **Independent diagnosis (30s):** Critic classifies `cross_entity_join`, with missing support visible.
4. **Behavioral repair (30s):** Loop Doctor adds graph retrieval; pass 2 obtains the missing chain and verifies.
5. **Weave proof (30s):** Show the actual traced Compiler -> retrieval -> Critic -> Loop Doctor -> rerun trajectory and score delta.
6. **Learning (45s):** In marimo switch policy v0 to v1 and show held-out first-pass/retrieval-regret comparison. Use only measured values.
7. **Research extension (20s):** Show W/C/M cube or TypeSafe/model comparison if real results exist.
8. **Close (10s):** "WorldLoop is learning how to allocate cognition, not just retrying answers."

## 17. Judging alignment

- **Best Loop:** visible self-correction plus held-out policy improvement.
- **Creativity:** three distinct cooperating agent roles with typed handoffs and independent verification.
- **Utility:** reduces hallucination/under-contexting and excessive retrieval/model/tool spend.
- **Technical execution:** deterministic baseline, provenance, failure taxonomy, versioned policies, held-out eval, fail-closed behavior.
- **Sponsor usage:** Weave is structural; marimo is the live research surface; ARIA/TypeSafe/Models/Inference are used only when they add measured value.

Primary sponsor track recommendation: **Best Use of Weave**. All projects remain eligible for Best Loop.

## 18. Failure modes and mitigations

### Demo looks like ordinary RAG

Mitigation: make the decision/policy delta explicit; show resource choice, failure classification, and held-out v0-v1 behavior rather than only improved retrieval.

### Same-task retry is mistaken for learning

Mitigation: separate inner self-correction from outer held-out policy evaluation.

### LLM judge circularity

Mitigation: use deterministic/source-aware checks first; if an LLM judge is needed, use a distinct stronger/different judge and keep judge version visible.

### Router leaks counterfactual answers

Mitigation: offline oracle can see all arms; online policy can use only pre-action features.

### Training set too small

Mitigation: do not force neural fine-tuning. Use a simple policy first; add synthetic variations/counterfactuals only while preserving held-out entity/time/task clusters.

### Retrieval is rewarded just because it produces citations

Mitigation: explicitly penalize unnecessary retrieval/context/tool calls and measure retrieval harm.

### Sponsor integration becomes decoration

Mitigation: every sponsor tool must answer a real architectural need or remain optional.

### Live BTW/private data creates eligibility or privacy ambiguity

Mitigation: sanitized fixtures are core; BTW is read-only optional validation and is labeled prior work.

### molab storage/session loss

Mitigation: commit source to GitHub and publish durable datasets/models/results through W&B or another approved persistent store; never trust notebook filesystem as canonical state.

### Self-improvement changes production behavior unsafely

Mitigation: candidate -> held-out eval -> guardrails -> canary -> promote/reject; preserve rollback.

## 19. MVP / extensions / non-goals

### Must ship

- deterministic public benchmark still reproducible;
- three visible loop roles;
- one complete Weave trajectory;
- one marimo live-loop view;
- failure -> policy change -> verified repair;
- policy/version schema;
- held-out comparison or at minimum a clearly separated held-out scaffold if time blocks training;
- README/demo instructions and transparent prior-work boundary.

### Strong extensions

- provider/model abstraction and W&B Inference matrix;
- ARIA-generated experiment actually executed;
- Context Manifest continuity demo;
- W/C/M causal benchmark;
- simple trained router / LoRA;
- read-only BTW adapter.

### Optional

- SkyPilot parallel experiment jobs;
- CoreWeave Sandbox executable-agent episode;
- mechanistic probes on open-model hidden states.

### Non-goals for the weekend

- rebuild LifeOps;
- rebuild BTW;
- full HomeBase/Bridge deployment;
- universal personal agent OS;
- large-scale RL;
- multi-cloud scheduler product;
- exhaustive mechanistic interpretability;
- production mutation of external systems.

## 20. Decision rule for every new feature

Before adding anything, ask:

1. Does it make the self-improving loop more real or more measurable?
2. Does it improve one of the published judging dimensions?
3. Can it produce a real result before submission without destabilizing the core demo?
4. Does it have a clear source/version/eval boundary?
5. Is it doing work no existing component already owns?

If the answer is not clearly yes, do not add it during the hackathon.
