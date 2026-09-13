# WorldLoop — 90–110 Second Demo Recording

## Goal

Record one continuous screen capture that proves the two things WorldLoop actually demonstrated: an inner failure→program-repair loop and an outer held-out policy-promotion loop.

Do not introduce LifeOps first. WorldLoop is the hackathon project; LifeOps is only one future production environment where learned programs could eventually be deployed.

## Shot list

### 0:00–0:12 — Thesis

Say:

“A normal agent fails and retries. WorldLoop independently diagnoses why the cognitive program failed, changes that program, and keeps the change only if it generalizes to unseen tasks.”

Open **WorldLoop Lab** immediately.

### 0:12–0:42 — Inner loop

Select the known cross-entity case.

Show:
- Program v0: `vector`;
- incomplete evidence / failed evidence obligation;
- Critic classification: `cross_entity_join`;
- Loop Doctor delta: `vector -> vector + graph`;
- rerun finds the missing evidence;
- verification passes;
- Critic score moves from `0.5` to `1.0`.

Say:

“This is not asking the model again. The execution program itself changed.”

### 0:42–1:05 — Outer loop

Switch to the held-out comparison.

Highlight:
- v0 first-pass verified success: `7/21 = 33.33%`;
- v1 first-pass verified success: `21/21 = 100%`;
- `promotion_decision: PROMOTED`.

Say:

“Both eventually recover to 100%. What improved is that the learned policy chooses the right cognitive path before failing, on frozen unseen cases.”

### 1:05–1:25 — Where compilation stops

Show `reports/three-arm-eval-adversarial.json` or the matching WorldLoop Lab table.

Highlight:
- deterministic: `7/21 = 33.33%`;
- TypeSafe: `14/21 = 66.67%`;
- W&B Inference: `21/21 = 100%`.

Say:

“When the easy cues disappear, compiled heuristics break first. WorldLoop should compile away semantic intelligence only where the structure is actually known, and keep semantic models where they are still necessary.”

### 1:25–1:38 — Weave

Flash the retained Weave trajectory or live trace: execution path, failure class, program delta, retry, verification.

Say:

“Weave is the evidence plane that lets us inspect exactly what changed and why it was promoted.”

### 1:38–1:48 — Close

Say:

“The loop doesn’t just fix one answer. It changes the program used for future tasks, and we only promote that change if it wins on unseen cases.”

Optional final card:

**The best agent loop is one that learns how to need less agent loop next time.**

## What not to put in the core video

Do not spend core demo time on LifeOps, Bridge, provider-readiness debugging, OCI internals, or current TypeSafe connectivity. Those are supporting context / Q&A. Current live TypeSafe connectivity is not proven and must not be implied.

## Post caption

WorldLoop turns verified agent failures into better typed execution policies. In the inner loop, it diagnoses a failed cognitive path and changes the program. In the outer loop, it promotes that change only if it improves first-pass verified behavior on frozen held-out tasks. At CoreWeave Hacks, v0 improved from 7/21 to 21/21 first-pass held-out success after policy derivation, while adversarial routing experiments showed where deterministic compilation stops and semantic models are still necessary.
