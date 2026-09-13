# WorldLoop — 90–110 Second Demo Recording

## Goal

Record one continuous screen capture that makes the self-improving loop obvious without setup explanation. Use this as the AGI House demo-link fallback and, if desired, the Best Social Media Demo entry.

Do not introduce LifeOps first. WorldLoop is the hackathon project; LifeOps is only one future production environment where learned programs could eventually be deployed.

## Shot list

### 0:00–0:12 — Thesis

Say: “A normal agent fails and thinks harder. WorldLoop watches the failure, independently diagnoses the wrong cognitive path, changes the execution program, and keeps the change only if it generalizes.”

Show the WorldLoop README / architecture headline.

### 0:12–0:35 — Failure → diagnosis → repair

Show `reports/weave/run-89b898a4fed9.json` or the corresponding Weave trace.

Point to:
- Program v0 selecting `vector`;
- failed evidence obligation `evidence:E04 = false`;
- failure class `cross_entity_join`;
- Critic diagnosis: missing required evidence E04;
- `program_delta_proposed`: `vector` → `vector + graph`;
- pass 2 finds E04 and the verifier returns score `1.0`.

Say: “The improvement becomes an explicit program delta, not another vague prompt.”

### 0:35–0:58 — Held-out promotion

Show `reports/EXP-008-gate3.json`.

Highlight:
- v0 first-pass verified success: 7/21 = 33.33%;
- v1 first-pass verified success: 21/21 = 100%;
- `promotion_decision: PROMOTED`.

Say: “Both eventually recover, but the learned program removes the avoidable recovery loop on frozen held-out tasks.”

### 0:58–1:18 — Falsification / where compilation stops

Show `reports/three-arm-eval-adversarial.json`.

Highlight:
- deterministic: 7/21 = 33.33%;
- TypeSafe: 14/21 = 66.67%;
- W&B Inference: 21/21 = 100%.

Say: “When we adversarially remove the easy cues, compiled deterministic routing breaks first. That is the point: WorldLoop should compile only what has actually become safe, and keep semantic intelligence where structure is still unresolved.”

### 1:18–1:35 — Self-healing infrastructure

Run or show:

`uv run python scripts/provider_readiness.py typesafe`

If blocked, show the typed first blocking hop. If ready, show `READY` with `external_provider_calls: 0`.

Say: “We also turned provider capability into changing world state, so the loop diagnoses a broken execution path before wasting live calls.”

### 1:35–1:45 — Close

Say: “The best agent loop is one that learns how to need less agent loop next time.”

## Post caption

WorldLoop uses agent loops to learn how to need less open-ended agent reasoning next time. It observes a trajectory, independently verifies the failure, compiles a candidate execution policy, and promotes it only on frozen held-out worlds. At CoreWeave Hacks we also used the same loop on its own provider/runtime failures, turning capability readiness into explicit world state rather than another silent agent assumption.
