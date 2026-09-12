# Three-minute demo

The demo should make one idea impossible to miss:

> **WorldLoop does not simply answer twice. Three cooperating roles identify that the agent used the wrong cognitive resources, change the policy, verify the repair, and use those trajectories to improve future routing/context decisions.**

Use only measured values. Never present fixture performance as production accuracy.

## Primary 3-minute narrative

### 0:00-0:15 — Problem

Show the marimo WorldLoop Lab.

Say approximately:

> "Agents often fail because they use the wrong knowledge at the wrong time: too little context and they hallucinate; too much retrieval/model/tool use and they waste time and money. WorldLoop learns how to allocate cognition."

### 0:15-0:45 — First-pass failure

Select `case-cross-entity`.

Show:

- task/evidence obligations;
- Context Compiler / Router initial recipe;
- retrieved evidence IDs;
- pass-1 score;
- missing evidence.

The known baseline is that vector retrieval only captures part of the required support chain.

### 0:45-1:15 — Independent critique

Show the **Critic / Verifier** as a distinct role.

It should classify the failure as `cross_entity_join`, not simply return "wrong".

Point out that the verifier evaluates evidence sufficiency/provenance rather than trusting the Compiler's confidence.

### 1:15-1:45 — Behavioral repair

Show the **Loop Doctor / Policy Researcher** receiving the typed failure and changing the actual retrieval policy:

```text
vector
  -> vector + graph
```

Rerun.

Show new evidence refs and the measured pass-to-pass score improvement. The critical proof is that context/retrieval behavior changed; the answer was not merely rewritten.

### 1:45-2:15 — Weave proof

Open the W&B Weave trajectory/evaluation view if available.

Show the sequence:

```text
Compiler plan
 -> retrieval spans
 -> worker/model
 -> Critic score/failure class
 -> Loop Doctor policy delta
 -> rerun
 -> verified score
```

Point to exact `run_id`, policy version, failure class, policy change, latency/cost if available, and pass score.

If remote W&B is unavailable, show the same typed local run record and say the public/offline baseline does not depend on credentials.

### 2:15-2:45 — Learning across tasks

This is the preferred strong ending if held-out results are ready.

In marimo switch between **Policy v0** and **Policy v1** on a frozen held-out set.

Show real measured differences in some subset of:

- first-pass success;
- final verified success / correct abstention;
- recovery rate;
- routing/context regret;
- unnecessary retrieval/tool use;
- latency;
- cost.

Say:

> "The first loop repairs one task. These trajectories then change the next policy, and we only promote it if it performs better on tasks it did not train on."

If held-out v1 results are not ready, do **not** pretend the same-task retry proves cross-task learning. Instead show the frozen outer-loop experiment and call it the next measured gate.

### 2:45-3:00 — Research extension / close

If real results exist, show one of:

- W/C/M knowledge-location cube;
- TypeSafe vs comparison model under the same budget;
- ARIA-generated experiment and result;
- read-only BTW/LiveLM external-memory adapter.

Close with:

> **"WorldLoop is a learned scheduler for intelligence: it learns what an agent already knows, what must be paged into context or retrieved from the world, and how much model/tool compute the task deserves."**

## marimo screen layout

The primary demo screen should fit the critical loop without navigation:

```text
+--------------------------------------------------------------+
| WORLDLOOP LAB                                                 |
| Case [cross-entity v]   Policy [v0/v1 v]   Provider [ ... ]  |
+-----------------------------+--------------------------------+
| Context / evidence plan     | Critic                         |
| vector                      | score: 0.5                     |
| E03                         | cross_entity_join              |
|                             | missing: E04,E05               |
+-----------------------------+--------------------------------+
| Loop Doctor: ADD graph                                       |
+--------------------------------------------------------------+
| Pass | Recipe          | Evidence     | Score | Sufficient   |
| 1    | vector          | E03          | 0.5   | no           |
| 2    | vector -> graph | E03,E04,E05  | 1.0   | yes          |
+--------------------------------------------------------------+
| Held-out policy comparison / failure distribution / regret   |
+--------------------------------------------------------------+
```

A Weave trace link/run ID should be visible from the selected trajectory.

## Fallback hierarchy

If an extension is unstable, fall back in this order without losing the core demo:

1. deterministic fixture inner loop;
2. local typed trace/score record;
3. remote Weave trajectory;
4. marimo held-out policy comparison;
5. ARIA / TypeSafe / W&C&M / training extensions.

Do not let sponsor credentials, model access, GPU access, LifeOps, BTW, SkyPilot, or Sandboxes become required to show a working WorldLoop.

## Optional BTW/LiveLM validation

BTW is **not** the project and is not needed for the public benchmark.

If the adapter is ready, show the same WorldLoop context/resource interface switching from `fixture-memory` to `btw-readonly` and demonstrate one public-safe changing-world query. Label LiveLM/BTW clearly as pre-existing infrastructure; the hackathon-new artifact is the adapter plus WorldLoop's decision/evaluation behavior.

## Demo truth rules

- Never claim a policy "learned" unless an unseen/held-out evaluation supports it.
- Never claim a hosted model fact is physically "in the weights"; call it closed-book or behaviorally accessible parametric knowledge.
- Never present fixture scores as production accuracy.
- Never hide prior-work dependencies.
- Never use an LLM's confidence as the sole verifier.
- If a candidate policy regresses, showing **REJECTED** is a valid and potentially stronger production-readiness demonstration than silently promoting it.
