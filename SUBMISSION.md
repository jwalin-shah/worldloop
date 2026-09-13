# CoreWeave Hacks — WorldLoop Submission

## Project name

WorldLoop

## 2–3 sentence description

WorldLoop turns verified agent failures into better typed execution policies. Instead of simply retrying when a task fails, WorldLoop independently diagnoses why the chosen evidence or control flow was insufficient, changes the execution program, and promotes that change only if it improves first-pass behavior on frozen held-out tasks. We prove the mechanism on a controlled benchmark, then apply the same route → verify → diagnose → policy-change abstraction to a real changing execution fabric where the correct decision can be to abstain rather than call another agent.

## Repository

https://github.com/jwalin-shah/worldloop

## Primary track

Best Use of Weave

All projects are also eligible for Best Loop Design. marimo is used as the thin human-readable experiment/demo surface, not as runtime authority or state storage.

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

This is a real program change, not “ask the same model again.” The retained trajectory is in `reports/weave/run-89b898a4fed9.json` and a fresh live remote Weave run was also published as `run-110ce97451cc`.

### Outer loop — generalize the repair policy

A v1 routing policy was derived from 45 development cases and evaluated on 21 frozen held-out cases.

- v0: `7/21 = 33.33%` first-pass verified success.
- v1: `21/21 = 100%` first-pass verified success.
- both eventually reached `21/21`, so the measured gain is specifically choosing the right cognitive route before needing repair.
- promotion decision: `PROMOTED`.

The public artifact is `reports/EXP-008-gate3.json`.

## Real-world validation — LifeOps engineering routing

The synthetic benchmark proves the learning mechanism. We also captured one public-safe real-world routing snapshot from the LifeOps execution fabric.

In the live snapshot, the read boundary reported the governed runtime unavailable, worker control not exposed, and no usable current worker/runtime. Historical execution evidence was also internally conflicted: an earlier Cursor receipt was green at the verification layer but contained an Orca worker-invocation failure warning, while fresh provider/demo canaries had failed without successful execution receipts.

A naive baseline policy — “use the last green worker” — would route to `cursor-agent`. The proof-aware candidate policy instead chooses `ABSTAIN_REPAIR_CONTROL_PLANE`: do not spend another worker/provider call until current runtime exposure and worker-completion proof are trustworthy.

The committed pilot is `reports/lifeops-worker-routing-pilot.json`. This is explicitly **one real-world snapshot, not a generalization benchmark**. Its purpose is to show the same WorldLoop abstraction operating on actual changing infrastructure rather than only synthetic retrieval cases.

## Weave — fresh remote proof

The W&B integration is now proven end-to-end with a fresh Mac run using runtime-injected credentials.

- Weave project: `jwalinshah13-personal/worldloop`
- run id: `run-110ce97451cc`
- remote trace call: `01a09c24-3399-7189-a90b-d641fab6a9f9`
- evaluation summary call: `01a09c24-33af-76ac-a755-0082716056b3`
- publish receipt: `remote_logged=True`, `evaluation_logged=True`
- traced flow: `vector` → `cross_entity_join` / score `0.5` → Loop Doctor adds `graph` → `vector + graph` → `VERIFIED_SUCCESS` / score `1.0`

This makes Best Use of Weave a real submission claim rather than a code-only integration claim.

## Semantic frontier experiment

The TypeSafe / W&B Inference experiment tests where deterministic structure stops being sufficient.

On the clean 21-case routing benchmark, deterministic routing, TypeSafe, and W&B Inference all reached 100%. On the adversarial version, where obvious keyword cues were removed:

- deterministic: `7/21 = 33.33%`;
- TypeSafe: `14/21 = 66.67%`;
- W&B Inference: `21/21 = 100%`.

The public artifact is `reports/three-arm-eval-adversarial.json`.

Fresh live TypeSafe execution is also now proven. A Mac canary returned a verified `GRAPH` route with high confidence, and a larger OCI experiment issued 240 live HTTP-200 provider requests with unique request IDs. Importantly, that larger candidate scored only `36.67%` and the promotion gate correctly returned `REJECT` because the proposed retrieval recipe caused excessive false abstention. We treat that rejection as evidence that provider availability and model confidence do not override independent outcome verification.

The takeaway is:

> Compile away semantic intelligence where the structure is known; keep semantic models only at nodes that still genuinely need them — and reject semantic candidates when held-out verification says they are worse.

## Relationship to prior systems

- **WorldLoop:** learns better cognitive / execution programs.
- **LifeOps:** one real environment where those routing ideas can be validated and eventually deployed.
- **Bridge / HomeBase:** governs whether real effects are authorized.
- **Verifier:** proves the intended real-world postcondition happened.

Do not present the hackathon as “we built a self-improving LifeOps.” LifeOps and LiveLM/BTW are prior infrastructure; the public WorldLoop benchmark and learning loop are the hackathon project.

## 3-minute judging script

### 0:00–1:30 — Clean scientific proof

Open **WorldLoop Lab** on the known cross-entity case.

Show `Program v0 = vector`, incomplete evidence, Critic classification `cross_entity_join`, then the Loop Doctor change `vector -> vector + graph`. Rerun and show the missing evidence, verification passing, and score `0.5 -> 1.0`.

Then switch to the held-out comparison:

`v0: 7/21 = 33.3% first-pass verified`

`v1: 21/21 = 100% first-pass verified`

Say: “The loop doesn’t just repair this example. The candidate policy was derived from development failures and only promoted after it improved first-pass behavior on frozen unseen cases.”

### 1:30–2:25 — This is not just a toy

Open **WorldLoop Lab → Real-World Pilot**.

Say: “Here the world is not a fixture. It is my actual execution fabric: multiple workers, changing runtime health, repositories, and verification contracts.”

Show that the naive `last-green-worker` policy chooses Cursor, while the proof-aware candidate chooses `ABSTAIN_REPAIR_CONTROL_PLANE` because current worker/runtime proof is unavailable or contradictory.

Say: “Sometimes the better cognitive program is not a smarter model call. It is recognizing that the execution path itself is not trustworthy yet.”

### 2:25–2:50 — Weave + marimo

Open the fresh remote Weave trace for `run-110ce97451cc`. Point to the pass-1 failure, Critic diagnosis, program delta, retry, and verified result.

Say: “Weave is the evidence plane. marimo is the thin experiment surface. Neither gets to decide promotion — the verifier and frozen evaluation do.”

### 2:50–3:00 — Close

“WorldLoop learns the smallest verified program that can do the work, and keeps semantic intelligence only where it earns its cost.”

## One-diagram explanation

```text
TASK
  ↓
choose cognition / evidence / execution route
  ↓
execute
  ↓
VERIFY explicit obligations
  ↓
wrong or unproven?
  ↓
classify WHY
  ↓
change the program
  ↓
test candidate on unseen tasks / objective receipts
  ↓
better?
  ├─ no  → reject / abstain
  └─ yes → promote
```

## Demo fallback

The core proof is fully reproducible from sanitized source-controlled fixtures. If a live sponsor API or OCI path is unavailable during judging, use WorldLoop Lab plus the committed trajectory and held-out reports. The fresh remote Weave run is additive evidence, not a dependency of the core proof.

## Submission checklist

- [ ] Every teammate signed into the AGI House platform.
- [ ] Every teammate completed the participant survey.
- [ ] One teammate creates/submits the project and lists every team member.
- [ ] Project name: WorldLoop.
- [ ] Paste the 2–3 sentence description above.
- [ ] GitHub: https://github.com/jwalin-shah/worldloop
- [ ] Select Best Use of Weave.
- [ ] Add the <2-minute demo recording.
- [ ] Include / keep handy the fresh Weave run `run-110ce97451cc`.
- [ ] Verify WorldLoop Lab runs locally.
- [ ] Keep the team onsite for final presentations and the awards ceremony.
