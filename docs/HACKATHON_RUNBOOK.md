# CoreWeave Hacks operating runbook

Event: CoreWeave Hacks: Agent Loops, September 12-13, 2026 (America/Los_Angeles).

The operating principle is **prove the self-improving loop first; add models, training, prior-work adapters, or infrastructure only when they strengthen that proof**. WorldLoop already has a functioning deterministic baseline. Do not reset into general infrastructure work.

The canonical project design is `docs/DESIGN.md`; the visual system map is `docs/ARCHITECTURE.md`.

## The judging-critical proof

By submission, a judge should be able to see this without explanation-heavy slides:

```text
Context Compiler chooses a bounded plan
  -> Worker executes over selected evidence/resources
  -> independent Critic classifies a concrete failure
  -> Loop Doctor changes an actual context/resource decision
  -> rerun measurably improves
  -> Weave contains the trajectory and scores
  -> marimo shows aggregate behavior
  -> candidate policy v1 is compared with v0 on frozen held-out tasks
```

If v1 does not improve held-out behavior, show the candidate being rejected rather than pretending same-task retry is cross-task learning.

## Saturday, Sep 12

| Phase | Goal | Exit condition |
|---|---|---|
| Kickoff / sponsor intelligence | Resolve actual event-issued W&B/ARIA/TypeSafe/marimo capabilities and get sponsor feedback on the architecture | No speculative sponsor dependency; concrete questions/credentials/access captured securely |
| Core instrumentation | Make the three-role inner loop visible in Weave | One complete Compiler -> retrieval/worker -> Critic -> Loop Doctor -> rerun trajectory with typed attributes and scores |
| marimo WorldLoop Lab | Turn the existing notebook into the primary research/demo surface | Live Loop view shows case, context/evidence plan, failure, policy delta, pass comparison, Weave run ID |
| Held-out policy experiment | Establish outer-loop learning contract and policy v0/v1 | Frozen train/held-out split; candidate derived only from training trajectories; first-pass/regret comparison reproducible |
| Model/provider experiment | Add real reasoning provider(s) only behind the common contract | At least one real model/provider can execute over frozen evidence without changing evaluation semantics |
| Sponsor feedback | Show working loop to Weave/marimo/ARIA/TypeSafe teams | Only adopt extensions that materially improve the proof or sponsor-track fit |
| Research extension | W/C/M, ARIA, TypeSafe, BTW, training as time allows | Extension produces a real measured result or stays out of the demo |
| Saturday freeze | Stabilize | Tests/lint/demo green; README and demo truth claims current; explicit Sunday blockers |

## Sunday, Sep 13

| Time (PT) | Goal | Exit condition |
|---|---|---|
| 09:00-10:15 | Regression + held-out rerun | Clean environment; exact benchmark/eval artifacts reproduced |
| 10:15-11:15 | Reliability + sponsor evidence | Fail-closed path, budgets, provenance/version identity, offline fallback, sponsor evidence visible |
| 11:15-12:00 | Final demo + README | Three-minute narrative rehearsed twice; screenshot/video capture ready |
| 12:00-12:30 | Submission package | Project summary, repo, sponsor/tool list, track selection, demo assets finalized |
| 12:30-13:00 | Freeze/buffer | **No new features.** Only submission-blocking fixes |
| 13:00 | Submission deadline | Submitted |
| 13:30 | Judging begins | Stable demo only |
| 15:30 | Presentations | Failure -> diagnosis -> behavioral change -> measured gain -> future-policy improvement |
| 16:30 | Awards | Done |

## Experiment priority

1. **EXP-005 Weave three-role trajectory — REQUIRED.** Makes the self-correcting agent team observable and is the strongest sponsor-track fit.
2. **marimo Live Loop / Policy Comparison — REQUIRED.** Not a separate registry experiment; it is the surface that makes EXP-005/008 understandable in seconds.
3. **EXP-008 held-out policy improvement — HIGHEST RESEARCH PRIORITY.** Separates actual cross-task improvement from a retry loop.
4. **EXP-003 same-evidence reader ablation — HIGH.** Prevents us from incorrectly treating reasoning/schema failures as retrieval failures.
5. **EXP-002 provider/model sensitivity — HIGH IF ACCESS IS EASY.** Gives TypeSafe/W&B Inference a meaningful controlled role.
6. **EXP-009 W/C/M causal knowledge-location study — HERO EXTENSION.** Do it if the core eval loop is stable and GPU/model access is ready.
7. **EXP-010 ARIA hypothesis loop — STRONG SPONSOR EXTENSION.** One real hypothesis-to-experiment cycle is enough.
8. **EXP-007 BTW/LiveLM read-only validation — OPTIONAL REAL-WORLD GENERALIZATION.** Prior work must be labeled; never a hidden core dependency.
9. **EXP-006 Gemini/LifeOps continuity — INTERNAL/OPTIONAL.** Valuable architecture proof for the broader system but lower judging leverage than the experiments above.
10. **EXP-004 retrieval operator ablation — AS NEEDED.** Run enough to explain which operators repair which failure classes; do not exhaustively sweep for its own sake.

## Go / no-go gates

- **W&B Weave: GO / CORE.** Must expose agent-role handoffs, policy deltas, scores, and version comparison.
- **marimo / molab: GO / CORE.** Live research workstation and primary demo surface; GPU only for experiments that need it.
- **W&B MCP: GO if credentialed quickly.** Useful so coding/research agents can inspect experiment evidence directly.
- **W&B Models / Artifacts: GO if training begins.** Use for lineage, not checkbox integration.
- **W&B Inference: GO if access is trivial.** Common provider/model matrix.
- **ARIA: CONDITIONAL.** Include only if it contributes one concrete measured hypothesis/experiment.
- **TypeSafe AI: CONDITIONAL.** Include when onsite capabilities support a controlled worker/router/verifier comparison.
- **CoreWeave Sandboxes: CONDITIONAL.** Only for genuinely stateful/generated-code episodes.
- **SkyPilot: OPTIONAL.** Add only if parallel W/C/M/counterfactual/training jobs become easier than direct execution.
- **LifeOps/BTW: OPTIONAL PRIOR WORK.** Read-only adapter/generalization; never required for judges to reproduce the core demo.
- **Training scaffold: GO.** Define dataset/policy/artifact/eval contracts.
- **Actual LoRA/fine-tuning: CONDITIONAL.** Start only after EXP-005/008 evaluation contracts are working and there is enough clean supervision.
- **RL: NO by default.** Only if everything above is stable and there is a measured reason to use it.
- **New retrieval/index infrastructure: NO.** Use current WorldLoop operators or optional adapters.
- **New features after Sunday 11:15: NO.** Reliability and submission win.

## Sponsor questions that change implementation

### Weave

- What is the cleanest object/span model for Compiler, Critic, Loop Doctor, and counterfactual routes?
- What would make this a non-obvious Best Use of Weave rather than basic tracing?
- How should we represent policy-version evaluation and custom routing-regret scores?

### marimo

- What would make WorldLoop Lab demonstrate marimo as an agent computational environment, not merely a dashboard?
- Best pattern for human + agent collaboration through marimo pair over live intermediate state?
- Best durable-artifact workflow from molab for model/data outputs?

### ARIA

- Can ARIA operate over custom Weave trajectory metrics and propose experiments over context/retrieval/model policy?
- Can we get one hypothesis -> launched/bounded experiment -> baseline comparison into the demo?

### TypeSafe

- What behavior is the model specifically optimized to change around tool/retrieval/abstention decisions?
- Which role (worker/router/verifier) most directly demonstrates machine-native intelligence per dollar?

## Questions to keep asking ourselves

- Did the failure come from missing evidence, stale evidence, contradiction, context structure, reasoning, model capability, tool execution, or verification?
- Did the next pass change **behavior/resources**, or only rewrite text?
- Did a candidate policy improve on data it did not train on?
- Are we measuring unnecessary retrieval/context/model/tool spend as well as correctness?
- Is each sponsor integration central to the proof or decoration?
- Can a judge understand the full loop in under 30 seconds of looking at the marimo screen?
- If a remote service fails, does the public fixture demo still work?
