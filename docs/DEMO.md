# Three-minute demo

The demo should make one idea impossible to miss:

> **WorldLoop uses an agent loop to learn how to build a better typed program. The loop diagnoses bad context/resource/node choices, repairs them, and then tries to compile repeated successful behavior into more explicit transitions and fewer broad semantic decisions.**

Use only measured values. Never present fixture performance as production accuracy.

## Primary 3-minute narrative

### 0:00-0:15 — Problem

Show the marimo WorldLoop Lab.

Say approximately:

> "Agents fail for two reasons at once: they often use the wrong knowledge or compute, and their control flow is too open-ended to reason about. WorldLoop learns what cognition a task needs and progressively compiles successful behavior into a typed workflow."

### 0:15-0:45 — First-pass failure

Select `case-cross-entity`.

Show:

- task/evidence obligations;
- current workflow/resource plan;
- retrieved evidence IDs;
- pass-1 score;
- missing evidence.

The known baseline is that vector retrieval only captures part of the required support chain.

### 0:45-1:15 — Independent critique

Show the **Critic / Verifier** as a distinct role.

It should classify the failure as `cross_entity_join`, not simply return "wrong".

Point out that the verifier evaluates evidence sufficiency/provenance rather than trusting the Compiler's confidence.

### 1:15-1:45 — Behavioral / graph repair

Show the **Loop Doctor / Policy Researcher** receiving the typed failure and changing an actual decision variable:

```text
retrieval node:
  vector
    -> vector + graph
```

Rerun.

Show new evidence refs and the measured pass-to-pass score improvement. The critical proof is that workflow/context behavior changed; the answer was not merely rewritten.

If a typed graph view is ready, show the failing node and the revised node/transition directly.

### 1:45-2:15 — Weave proof

Open the W&B Weave trajectory/evaluation view if available.

Show:

```text
workflow/program version
 -> Compiler / graph plan
 -> retrieval/tool/semantic nodes
 -> Critic score + failure class
 -> Loop Doctor graph/policy delta
 -> rerun
 -> verified score
```

Point to exact `run_id`, graph/program version, policy version, failure class, node/policy change, latency/cost if available, and pass score.

If remote W&B is unavailable, show the same typed local run record and say the public/offline baseline does not depend on credentials.

### 2:15-2:45 — Learning across tasks

Preferred strong ending if held-out results are ready.

In marimo switch between **Program/Policy v0** and **v1** on a frozen held-out set.

Show real measured differences in some subset of:

- first-pass verified success;
- final verified success / correct abstention;
- recovery rate;
- routing/context regret;
- unnecessary retrieval/tool use;
- semantic-node count;
- semantic-surface ratio;
- latency;
- cost.

Say:

> "The first loop repairs one task. Those trajectories then produce a candidate program. We only promote it if it works better on tasks it did not train on—and ideally needs less open-ended intelligence to do so."

If EXP-011 is ready, show one before/after graph where a broad semantic/open-loop operation has become deterministic or a narrow typed primitive.

If held-out results are not ready, do **not** claim the same-task retry proves cross-task learning.

### 2:45-3:00 — Close

If real results exist, flash one extension:

- EXP-011 progressive compilation;
- W/C/M knowledge-location cube;
- TypeSafe semantic-node comparison under the same typed primitive;
- ARIA-generated graph/node experiment;
- read-only BTW/LiveLM external-memory adapter.

Close with:

> **"WorldLoop is not trying to make an agent loop wander forever. It uses the loop to learn the smallest verified typed program that can do the work over a changing world."**

A shorter alternate close:

> **"The best agent loop is one that learns how to need less agent loop next time."**

## marimo screen layout

The primary demo screen should fit the critical loop without navigation:

```text
+------------------------------------------------------------------+
| WORLDLOOP LAB                                                     |
| Case [cross-entity v] Program [v0/v1] Provider [ ... ]           |
+------------------------------+-----------------------------------+
| Typed graph / current node   | Critic                            |
| retrieval.vector             | score: 0.5                        |
| evidence: E03                | cross_entity_join                 |
| next transition: blocked     | missing: E04,E05                  |
+------------------------------+-----------------------------------+
| Loop Doctor: retrieval.vector -> retrieval.vector+graph          |
+------------------------------------------------------------------+
| Pass | Program | Evidence      | Score | Semantic nodes | Pass?   |
| 1    | v0      | E03           | 0.5   | ...            | no      |
| 2    | v1      | E03,E04,E05   | 1.0   | ...            | yes     |
+------------------------------------------------------------------+
| Held-out comparison: success / regret / semantic-surface delta   |
+------------------------------------------------------------------+
```

A Weave trace/run ID and exact program/policy version should be visible from the selected trajectory.

## Why TypeSafe is interesting without making it a dependency

Do not pitch TypeSafe as “another chat model.” If onsite access supports typed/calibrated machine decisions, evaluate it inside a narrow semantic primitive such as `CLASSIFY` or `DECIDE` under the same input/output/eval contract.

The interesting comparison is:

```text
broad text-generation node
vs
bounded typed semantic node
```

Measure correctness, abstention, calibration if exposed, latency/cost, and downstream control-flow stability. Do not invent an API or calibration guarantee that TypeSafe has not actually exposed.

## Fallback hierarchy

If an extension is unstable, fall back without losing the core demo:

1. deterministic fixture inner repair loop;
2. local typed trace/score record;
3. remote Weave trajectory;
4. marimo held-out policy/program comparison;
5. EXP-011 typed-graph compilation result;
6. ARIA / TypeSafe / W/C/M / training extensions.

Do not let sponsor credentials, model access, GPU access, LifeOps, BTW, SkyPilot, or Sandboxes become required to show a working WorldLoop.

## Optional BTW/LiveLM validation

BTW is **not** the project and is not needed for the public benchmark.

If the adapter is ready, show the same retrieval/evidence node switching from `fixture-memory` to `btw-readonly` and demonstrate one public-safe changing-world query. Label LiveLM/BTW clearly as pre-existing infrastructure; the hackathon-new artifact is the adapter plus WorldLoop's typed compilation/decision/evaluation behavior.

## Demo truth rules

- Never claim a policy/program "learned" unless an unseen/held-out evaluation supports it.
- Never claim semantic-surface improvement unless a real before/after graph and metrics support it.
- Never claim a hosted model fact is physically "in the weights"; call it closed-book or behaviorally accessible parametric knowledge.
- Never present fixture scores as production accuracy.
- Never hide prior-work dependencies.
- Never use an LLM's confidence as the sole verifier or as execution authority.
- If a candidate graph/policy regresses, showing **REJECTED** is a valid and potentially stronger production-readiness demonstration than silently promoting it.
