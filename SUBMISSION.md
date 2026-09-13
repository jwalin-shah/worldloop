# CoreWeave Hacks — WorldLoop Submission

## Project name

WorldLoop

## 2–3 sentence description

WorldLoop turns verified agent failures into better typed execution policies. Instead of simply retrying when a task fails, WorldLoop independently diagnoses why the chosen evidence or control flow was insufficient, changes the execution program, and promotes that change only if it improves first-pass behavior on frozen held-out tasks. The longer-term goal is to progressively compile repeated successful agent behavior into explicit retrieval, reasoning, fallback, and abstention paths so semantic models are used only where they are still genuinely necessary.

## Repository

https://github.com/jwalin-shah/worldloop

## Primary track

Best Use of Weave

All projects are also eligible for Best Loop Design.

## What we actually proved

WorldLoop is **not** claiming to be a general self-improving AI. The hackathon proof is narrower and stronger: we proved an inner loop and an outer loop.

### Inner loop — repair one failed execution program

On the concrete cross-entity demo case:

1. Program v0 chooses `vector` retrieval.
2. Execution cannot satisfy the required cross-entity evidence obligation.
3. The independent Critic identifies `cross_entity_join` and the missing evidence.
4. The Loop Doctor changes the program from `vector` to `vector + graph`.
5. The rerun finds the missing evidence and independently verifies successfully.
6. Critic score improves from `0.5` to `1.0`.

This is a real program change, not “ask the same model again.” The retained trajectory is in `reports/weave/run-89b898a4fed9.json`.

### Outer loop — generalize the repair policy

A v1 routing policy was derived from 45 development cases and evaluated on 21 frozen held-out cases.

- v0: `7/21 = 33.33%` first-pass verified success.
- v1: `21/21 = 100%` first-pass verified success.
- both eventually reached `21/21`, so the measured gain is specifically choosing the right cognitive route before needing repair.
- promotion decision: `PROMOTED`.

The public artifact is `reports/EXP-008-gate3.json`.

## Actual use case

The use case is not “answer questions better.” It is:

> Given a task over a changing world, decide what kind of cognition and evidence is required before acting.

A repeated operational task such as “Should Project Aurora be approved for rollout right now?” may require an exact record, a current temporal fact, a dependency relationship, a semantic judgment, or an explicit abstention/escalation path. WorldLoop learns when a task needs exact lookup, vector search, temporal reasoning, graph traversal, a semantic model call, or abstention, and then progressively turns repeated successful behavior into a smaller explicit program.

This applies to deployment gates, support operations, compliance checks, research workflows, personal agents, and other long-lived agent systems.

## Semantic frontier experiment

The TypeSafe / W&B Inference experiment tests where deterministic structure stops being sufficient.

On the clean 21-case routing benchmark, deterministic routing, TypeSafe, and W&B Inference all reached 100%. On the adversarial version, where obvious keyword cues were removed:

- deterministic: `7/21 = 33.33%`;
- TypeSafe: `14/21 = 66.67%`;
- W&B Inference: `21/21 = 100%`.

The public artifact is `reports/three-arm-eval-adversarial.json`.

The takeaway is not “bigger models always win.” It is:

> Compile away semantic intelligence where the structure is known; keep semantic models only at nodes that still genuinely need them.

Current live TypeSafe connectivity is **not** part of the submission claim. Provider-specific claims should use retained artifacts only; offline fallback results must never be presented as live TypeSafe performance.

## Relationship to prior systems

- **WorldLoop:** learns better cognitive / execution programs.
- **LifeOps:** one future real environment that could run those learned programs.
- **Bridge / HomeBase:** governs whether real effects are authorized.
- **Verifier:** proves the intended real-world postcondition happened.

Do not present the hackathon as “we built a self-improving LifeOps.” LifeOps and LiveLM/BTW are prior infrastructure; the public WorldLoop proof is sanitized and independent of them.

## 3-minute judging script

### 0:00–0:25 — The problem

“Agents can often recover from mistakes, but they repeatedly rediscover the same mistakes. WorldLoop asks a narrower question: can verified failures change the execution program used on future tasks, and can we prove that change generalizes?”

### 0:25–1:15 — Inner loop

Open **WorldLoop Lab** on the known cross-entity case.

Show:

`Program v0 = vector`

Run it. Point to incomplete evidence and the failed obligation. Show the Critic classifying `cross_entity_join`. Then show the Loop Doctor changing:

`vector -> vector + graph`

Rerun and show the missing evidence being retrieved, verification passing, and the score moving from `0.5` to `1.0`.

Say: “This is not another retry prompt. The execution program itself changed.”

### 1:15–2:00 — Outer loop

Switch to the held-out comparison.

Show:

`v0: 7/21 = 33.3% first-pass verified`

`v1: 21/21 = 100% first-pass verified`

Explain that both eventually recover to 100%, so the measured improvement is that v1 chooses the correct cognitive route before failing. The policy was derived from development trajectories; the 21 evaluation cases were frozen and unseen during derivation.

### 2:00–2:30 — Where compilation stops

Optionally show the adversarial three-arm result:

`deterministic 33.3% | TypeSafe 66.7% | W&B Inference 100%`

Say: “This is the boundary: compile what has become reliable, but keep semantic intelligence where the structure is not yet safely captured.”

### 2:30–2:55 — Weave

Show the actual trajectory / program and policy versions in Weave or the retained Weave report. Emphasize that Weave is the evidence plane: execution path, failure class, program delta, retry, and verification are inspectable.

### 2:55–3:00 — Close

“The loop doesn’t just fix one answer. It changes the program used for future tasks, and we only promote that change if it wins on unseen cases.”

## One-diagram explanation

```text
TASK
  ↓
Program v0 chooses a route
  ↓
execute
  ↓
VERIFY explicit evidence obligations
  ↓
wrong?
  ↓
classify WHY
  ↓
change the program
  ↓
test candidate on unseen tasks
  ↓
better?
  ├─ no  → reject
  └─ yes → promote to v1
```

## Demo fallback

The core proof is fully reproducible from sanitized source-controlled fixtures. If Weave, OCI, or a sponsor API is unavailable during judging, use WorldLoop Lab plus the committed trajectory and held-out reports. Do not make a live external service a dependency of the proof.

## Submission checklist

- [ ] Every teammate signed into the AGI House platform.
- [ ] Every teammate completed the participant survey.
- [ ] One teammate creates/submits the project and lists every team member.
- [ ] Project name: WorldLoop.
- [ ] Paste the 2–3 sentence description above.
- [ ] GitHub: https://github.com/jwalin-shah/worldloop
- [ ] Select Best Use of Weave.
- [ ] Add the <2-minute demo recording.
- [ ] Verify WorldLoop Lab runs locally.
- [ ] Keep the team onsite for final presentations and the awards ceremony.
