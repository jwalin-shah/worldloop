# WorldLoop One-Day Hackathon MVP

This is the build target for the remaining hackathon window. It deliberately ignores the full long-term architecture unless a capability directly helps the proof.

## The problem we solve tomorrow

Agents often choose the wrong cognitive path before they fail:

- model-only when current external evidence is required;
- broad retrieval when one exact source would suffice;
- vector search when the task actually needs temporal or graph structure;
- an expensive model when a cheaper path would work;
- open-ended semantic routing where a typed deterministic branch is already known;
- confident generation when the evidence is insufficient and the right action is abstention/escalation.

Most observability systems tell you what happened after the run. Most routers choose only which model to call. Most workflow frameworks require the developer to design the graph manually.

WorldLoop's hackathon question is narrower:

> Can verified failures change the next execution policy/program so future tasks start with a better, smaller cognitive plan?

## The one-day product

Build **WorldLoop Lab** around one synthetic task family with exact ground truth and hidden held-out variants.

The product has four visible objects:

1. **Program v0** — the initial typed graph/resource policy.
2. **Trajectory** — what actually executed, including evidence/resources and the failure.
3. **Repair** — a typed graph/policy delta generated from the failure.
4. **Program v1** — the candidate derived from development trajectories and tested on frozen held-out tasks.

## Recommended task family: change-aware decision support

Use a synthetic but realistic "current-world decision" family rather than generic fact lookup.

Example shape:

> "Should Project Aurora be approved for rollout now?"

The answer depends on a small changing world:

- current owner/team relationships;
- current incident or blocker status;
- a policy/runbook rule;
- an entity dependency that may require graph traversal;
- a time-sensitive fact that can supersede an older claim;
- optional cost/risk/stakes metadata.

Why this family:

- it naturally requires external evidence/freshness rather than trivia;
- it can be evaluated deterministically from synthetic state;
- graph, temporal, exact, lexical/vector retrieval each have plausible roles;
- the final decision can be typed (`APPROVE | BLOCK | ESCALATE`) rather than free text;
- the same contract later maps to deployment gates, support operations, travel decisions, compliance checks, or personal-agent actions;
- it demonstrates why authority/verification must remain separate from semantic judgment.

Do **not** execute a consequential real action during the public demo. The output is a decision/proposal plus evidence and verification state.

## Demo scenario

### v0 failure

Program v0:

```text
S0 task
 -> vector retrieval
 -> DECIDE[RolloutReadiness]
 -> VERIFY[evidence sufficiency]
```

For one development case, vector retrieval returns an older owner/status fact but misses the current dependency/blocker relationship.

Critic result:

```text
failure_class = cross_entity_join | temporal_staleness
missing_obligation = current blocker/dependency evidence
```

### repair

Loop Doctor emits a typed delta:

```text
replace retrieval node:
  vector
with:
  temporal + graph

add explicit transition:
  if required current blocker evidence missing -> ESCALATE
```

### v1

Program v1 begins relevant task classes with the new branch.

Held-out variants contain different entity names/timestamps/relationships. v1 must not have seen them.

## What must be measured

Primary metric: choose exactly one before implementation:

- **first-pass verified success**, or
- **routing regret** at non-inferior correctness.

Secondary:

- final verified success / correct abstention;
- recovery rate;
- retrieved item count;
- context tokens if meaningful;
- latency/cost if available;
- semantic node count;
- semantic surface ratio;
- open-loop branch count.

Do not optimize all metrics at once.

## Minimum dataset

Current 12 fixtures remain regression tests.

Add one generated task family with approximately:

- 30-60 development variants;
- 15-30 frozen held-out variants;
- grouped failure classes;
- deterministic answer/evidence obligations;
- entity/time values separated across development vs held-out when possible.

The generator should produce the world state and expected required evidence, not ask an LLM to create labels on the fly.

## Candidate v1 — simplest acceptable implementation

Do not build a neural router unless it is clearly faster.

Preferred order:

1. train a tiny decision tree/logistic classifier from development trajectory features to retrieval/program action;
2. if data are too small, derive a data-driven lookup/rule table automatically from failure/action statistics;
3. only then consider a small LM/LoRA router.

Input features must be pre-action features or legitimate task metadata. Counterfactual oracle results and held-out labels cannot leak into v1 inputs.

## Weave implementation

One selected episode should be visible as a native agent/evaluation trajectory:

```text
Compiler / program selection
 -> retrieval/tool span(s)
 -> bounded worker/semantic node
 -> Critic score + failure class
 -> Loop Doctor graph/policy delta
 -> rerun
 -> verified result
```

Bind before execution:

- experiment_id;
- run_id;
- code_revision;
- dataset snapshot;
- evidence snapshot;
- workflow/policy version;
- node version;
- provider/model;
- scorer version.

Use `EvaluationLogger` for live episodes and `Evaluation` for frozen v0/v1 benchmark comparison where practical.

## marimo implementation

Only three views are required tomorrow:

### 1. Live Program

- selected case;
- graph/program v0 or v1;
- Context Manifest/evidence obligations;
- current/failing node highlighted;
- pass/score/failure class;
- graph/policy delta;
- Weave run link/ID.

### 2. Held-out Comparison

- v0 vs v1 primary metric;
- verified correctness;
- retrieval/semantic resource use;
- failure-class breakdown.

### 3. Before/After Program

- graph diff;
- semantic node count/surface ratio;
- explicit new deterministic/retrieval transition.

W/C/M cube and full failure explorer are stretch features after this.

## Optional real-world proof

If time and permissions are clean, switch the evidence backend for one public-safe case:

```text
fixture-memory -> btw-readonly
```

or another source-native public/current backend.

The same `EvidenceItem` contract and Critic must work unchanged. This demonstrates generalization; it is not required for the core benchmark.

## Tool usage that actually matters

### Core

- **Weave**: trajectory/evaluation proof and v0/v1 comparison.
- **marimo**: live program/trajectory/held-out experiment surface.

### Conditional

- **TypeSafe**: one bounded `DECIDE`/`CLASSIFY`/`VERIFY` node if the onsite API really exposes a useful machine-native interface.
- **W&B Inference**: provider/model comparison under the same node contract.
- **ARIA**: inspect actual failure data and propose one graph/node experiment after core results exist.
- **BTW/LiveLM**: one external current-memory backend after public benchmark works.

### Not critical

- Sandboxes unless generated/stateful code is part of the chosen task;
- SkyPilot unless parallel sweeps are actually bottlenecked;
- large fine-tuning/RL;
- full LifeOps/Bridge deployment.

## Hard parts and how to de-risk them

### Hardest: benchmark validity

Build the generator and held-out split before polishing UI. If there is no trustworthy held-out set, there is no strong self-improvement claim.

### Hard: automatic policy derivation

Use a tiny supervised classifier/table first. A simple model with a real held-out win is stronger than a sophisticated self-improvement story with no evidence.

### Hard: graph compilation claim

Compile exactly one kind of improvement: retrieval/resource branch + explicit fallback. Do not attempt a universal agent-to-program compiler in one day.

### Hard: real W&B trace

Prove one complete trajectory before instrumenting every benchmark case.

### Hard: sponsor account/setup

Remote failures must not block the deterministic local benchmark or marimo app.

## User bottleneck removal

After credentials/account gates are satisfied, no implementation task should require Jwalin to relay context manually.

Source of truth:

- GitHub docs/issues = plan and implementation requirements;
- experiment registry = hypotheses/metrics/stop rules;
- Weave = run/eval evidence;
- marimo = live scientific state;
- Infisical = secrets;
- LifeOps = optional durable cross-provider project continuity.

Builder agents should read GitHub + Weave directly and work against acceptance criteria. Jwalin's role becomes product choice/sponsor access/demo judgment, not copying logs or remembering next steps.

## Submission sell

Short version:

> Agents waste capability because they choose the wrong knowledge and control flow. WorldLoop turns verified failures into a better typed execution program: it learns which evidence/model/tool path is necessary and which open-ended reasoning can be compiled away. We prove the change on held-out tasks, trace it in Weave, and make the before/after program inspectable in marimo.

## Final go/no-go

By tonight, prioritize in this order:

1. valid generated train/held-out task family;
2. real Weave failure -> repair trajectory;
3. automatic candidate v1;
4. held-out v0/v1 result;
5. marimo visualization;
6. only then TypeSafe/ARIA/BTW/W&C&M extras.

If items 1-4 work, the project has a defensible result. If they do not, stop adding architecture and finish a truthful smaller demo.