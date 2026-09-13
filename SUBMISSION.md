# CoreWeave Hacks — WorldLoop Submission

## Project name

WorldLoop

## 2–3 sentence description

WorldLoop is a self-improving execution compiler for agents: it observes a run, independently verifies what failed, proposes a smaller typed context/resource/workflow policy, and promotes that policy only if it wins on frozen held-out worlds. Instead of letting an agent endlessly reason about its own transcript, WorldLoop separates exploration from verification and progressively compiles successful behavior into deterministic transitions, retrieval steps, and bounded semantic decisions. During the hackathon we also used the loop on its own infrastructure failures, turning ambiguous provider/worker failures into explicit readiness states rather than silently treating missing evidence as success.

## Repository

https://github.com/jwalin-shah/worldloop

## Primary track

Best Use of Weave

All projects are also eligible for Best Loop Design.

## What to show judges first

1. **The problem:** agents repeatedly choose the wrong context/tool/model path and can mistake apparent progress for verified progress.
2. **Program v0:** a deliberately weaker execution/retrieval policy fails on a generated hidden-world case.
3. **Independent Critic:** classifies the concrete missing obligation/failure without reading the hidden answer during execution.
4. **Loop Doctor / compiler:** derives a candidate typed policy/program from development failures.
5. **Frozen held-out gate:** compares the candidate against the incumbent before promotion.
6. **Weave:** shows the trajectory and evaluation evidence for the loop.
7. **Provider readiness:** a zero-provider-call check reports the first broken runtime hop before paid/live experiments, so unavailable providers are routed around instead of producing false green results.

## Verified benchmark result to cite

The public `reports/EXP-008-gate3.json` artifact records a frozen 21-case held-out promotion gate: Program/policy v0 achieved 33.33% first-pass verified success, while the automatically derived v1 policy achieved 100% first-pass verified success and was marked `PROMOTED`. Both reached 100% eventual verified success, so the improvement is specifically that WorldLoop learned to choose the right execution/retrieval program on the first pass rather than relying on recovery.

A larger V2 generated-world sweep was also run during development, but do not use its metrics in the submission unless its exact artifact is published and linked.

## TypeSafe experiment story

TypeSafe is used as a bounded semantic routing primitive rather than as the global controller. Live experiments during the hackathon exposed an important composition result: broader multi-primitive routing could over-route, while a narrower Choice-style decision primitive was substantially more stable on the tested routing cases. Provider-specific claims should be shown only with retained request/usage evidence; offline fallback results must not be presented as live TypeSafe performance.

## 3-minute judging script

### 0:00–0:25 — Problem

“Agents are getting smarter, but they still repeatedly choose the wrong cognitive path: too much context, the wrong retriever, an expensive model when a deterministic branch would work, or a confident answer when evidence is insufficient. Observability tells you what happened after the run; WorldLoop asks whether verified failures can change the next execution program.”

### 0:25–1:05 — Show one failure

Open one generated hidden-world case. Show Program v0 choosing the weaker route, then the independent Critic identifying the missing evidence/failure class. Emphasize that the hidden oracle is not exposed to the runtime policy.

### 1:05–1:40 — Show the repair

Show the candidate graph/policy delta: change the retrieval/resource branch and/or add an explicit fallback/abstention transition. Explain: “The model can explore, but the improvement is compiled into a smaller typed program rather than becoming another prompt.”

### 1:40–2:10 — Show held-out proof

Open `reports/EXP-008-gate3.json`: v0 gets 7/21 (33.33%) first-pass verified success; v1 gets 21/21 (100%) and is marked `PROMOTED`. Both eventually recover to 21/21, which makes the result easy to explain: the learned program removes avoidable recovery loops instead of merely making the final answer look better.

### 2:10–2:35 — Show Weave

Open `reports/weave/run-89b898a4fed9.json` or the corresponding live Weave trace. Point to Program v0 selecting vector retrieval, the Critic classifying `cross_entity_join`, the Loop Doctor adding graph retrieval, and the independent verifier passing the repaired run. This is the evidence plane, not the authority plane.

### 2:35–2:55 — Show self-healing/readiness

Show the provider-readiness output or incident: WorldLoop found that the TypeSafe SDK/runtime existed but the isolated execution's Infisical secret context was unavailable, so it classified the first blocking hop before spending a provider call. Explain that runtime/provider capability is itself changing world state and should affect program selection.

### 2:55–3:00 — Close

“Models explore. WorldLoop learns what can become software—and only promotes it when independent evidence says it should.”

## Demo fallback if remote services fail

The public demo must remain reproducible from sanitized fixtures. If a sponsor API, Weave, or OCI path is unavailable during judging, run the generated-world benchmark and held-out promotion path locally, then show retained sponsor traces/artifacts separately. Do not block the core proof on a live external service.

## Submission checklist

- [ ] Every teammate signed into the AGI House platform.
- [ ] Every teammate completed the participant survey.
- [ ] One teammate creates/submits the project and lists every team member.
- [ ] Project name: WorldLoop.
- [ ] Paste the 2–3 sentence description above.
- [ ] GitHub: https://github.com/jwalin-shah/worldloop
- [ ] Select Best Use of Weave.
- [ ] Add a demo link / short video if setup is not instantly obvious.
- [ ] Verify the repo quick-start works from a clean checkout.
- [ ] Keep the team onsite for final presentations and the awards ceremony.
