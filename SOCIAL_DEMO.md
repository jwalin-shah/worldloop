# WorldLoop — 60–90 Second Demo Recording

## Goal

Record one continuous screen capture that makes the self-improving loop obvious without setup explanation. Use this as the AGI House demo-link fallback and, if desired, the Best Social Media Demo entry.

## Shot list

### 0:00–0:12 — Thesis

Say: “Agents can recover from mistakes, but recovery is expensive and transcript-based self-grading is easy to fool. WorldLoop turns verified failures into a better typed execution program.”

Show the WorldLoop README / architecture headline.

### 0:12–0:32 — Failure → diagnosis

Show `reports/weave/run-89b898a4fed9.json` or the corresponding Weave trace.

Point to:
- Program v0 selecting `vector`;
- the failed evidence obligation `evidence:E04 = false`;
- failure class `cross_entity_join`;
- Critic diagnosis: missing required evidence E04.

### 0:32–0:48 — Repair

Show the `program_delta_proposed` event:

`vector` → `vector + graph`

Then show pass 2 finding E04 and the verifier returning score `1.0`.

Say: “The improvement becomes an explicit program delta, not another vague prompt.”

### 0:48–1:05 — Held-out promotion

Show `reports/EXP-008-gate3.json`.

Highlight:
- v0 first-pass verified success: 7/21 = 33.33%;
- v1 first-pass verified success: 21/21 = 100%;
- `promotion_decision: PROMOTED`.

Say: “Both can eventually recover, but the learned program removes the avoidable recovery loop on frozen held-out tasks.”

### 1:05–1:20 — Self-healing infrastructure

Run or show:

`uv run python scripts/provider_readiness.py typesafe`

If blocked, show the typed first blocking hop. If ready, show `READY` with `external_provider_calls: 0`.

Say: “WorldLoop now treats provider capability as changing world state too, so it can diagnose a broken execution path before wasting paid calls.”

### 1:20–1:30 — Close

Say: “Models explore. WorldLoop learns what can become software—and promotes it only when independent evidence says it should.”

## Post caption

WorldLoop turns agent failures into better typed execution programs. It observes a trajectory, independently verifies the failure, compiles a candidate policy, and promotes it only on frozen held-out worlds. At CoreWeave Hacks we also used the same loop on its own provider/runtime failures: capability readiness becomes world state instead of another silent agent assumption.
