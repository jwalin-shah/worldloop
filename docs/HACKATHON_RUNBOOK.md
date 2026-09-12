# CoreWeave Hacks operating runbook

Event: CoreWeave Hacks: Agent Loops, September 12-13, 2026 (America/Los_Angeles).

The operating principle is **prove the loop first, add sponsors/features only when they improve the proof**. WorldLoop is already a functioning deterministic baseline; do not reset into infrastructure work.

## Saturday, Sep 12

| Time (PT) | Goal | Exit condition |
|---|---|---|
| 09:45-10:30 | Pre-kickoff: account/API readiness + provider-neutral canary | W&B/CoreWeave/Gemini accounts reachable; LifeOps MCP path known; no secrets in repo |
| 10:30-11:15 | Kickoff + sponsor intelligence | Update only assumptions that sponsors explicitly clarify; choose questions for office hours |
| 11:15-12:15 | Freeze baseline + Weave trajectory schema | EXP-001 preserved; one pass record schema; pass-1 -> diagnosis -> policy change -> pass-2 is traceable |
| 12:15-13:15 | Gemini-on-Mac -> LifeOps canary | Gemini resolves WorldLoop + latest checkpoint from shared LifeOps and emits compatible run envelope |
| 13:15-14:15 | marimo WorldLoop Lab | Case selector, pass table, benchmark scorecard, experiment registry visible |
| 14:15-16:00 | EXP-002 + EXP-003 | Provider-sensitivity and same-evidence reader comparisons each have at least a minimal reproducible result |
| 16:00-17:00 | Sponsor/mentor feedback | Ask W&B/ARIA/TypeSafe/marimo teams what would make the core loop technically convincing; change plan only on concrete value |
| 17:00-19:00 | Held-out eval + repair | At least one held-out/fresh failure class; no overclaiming same-task retries as learning |
| 19:00-20:15 | Demo surface + reliability | One command runs demo; one screen shows failure -> repair -> measured delta; fallback path works offline |
| 20:15-21:00 | Saturday freeze/checkpoint | Tests green, README/demo steps current, durable checkpoint, explicit Sunday blockers |

## Sunday, Sep 13

| Time (PT) | Goal | Exit condition |
|---|---|---|
| 09:00-10:15 | Regression + held-out rerun | Clean environment; exact benchmark/eval artifacts reproduced |
| 10:15-11:15 | Production-readiness + failure modes | Timeouts/budgets/abstention/auth boundaries visible; no hidden private dependency |
| 11:15-12:00 | Final demo + README | Three-minute narrative rehearsed twice; screenshots/links ready |
| 12:00-12:30 | Submission package | Submission text, repo, demo instructions, sponsor evidence finalized |
| 12:30-13:00 | Freeze/buffer | **No new features.** Only submission-blocking fixes |
| 13:00 | Submission deadline | Submitted |
| 13:30 | Judging begins | Stable demo only |
| 15:30 | Presentations | Use concise failure -> diagnosis -> behavioral change -> measured gain story |
| 16:30 | Awards | Done |

## Experiment priority

1. **EXP-005 Weave trajectory** — required for Best Use of Weave and makes the loop legible.
2. **EXP-006 provider continuity** — differentiates WorldLoop/LifeOps from a one-provider agent demo.
3. **EXP-003 same-evidence reader ablation** — protects us from misdiagnosing interpretation failures as retrieval failures.
4. **EXP-002 provider sensitivity** — useful if model access is trivial; otherwise do not block core loop.
5. **EXP-004 retrieval ablation** — add only enough to explain which repair operators matter.
6. **EXP-007 real evidence adapter** — optional; skip if permissions/provenance are not clean.

## Go / no-go gates

- **Weave: GO.** It directly exposes the trajectory and comparison that the project claims.
- **marimo: GO.** Use it as the live experiment control/scorecard surface, not as another state store.
- **Gemini/LifeOps: GO.** One cross-provider continuity canary is strategically important.
- **ARIA: CONDITIONAL.** Add only if it can inspect traces and recommend the next experiment/failure cluster without becoming a second orchestration layer.
- **TypeSafe AI: CONDITIONAL.** Add if the onsite model interface makes provider/tool selection or structured semantics materially better; otherwise preserve an adapter slot.
- **CoreWeave Sandboxes: CONDITIONAL.** Use only if an experiment actually executes generated/untrusted tool code. Do not create sandbox theater.
- **New retrieval/index infrastructure: NO.** Use existing operators/adapters.
- **Training/RL: NO** unless the eval loop is already complete and a measured residual justifies it.
- **New features after Sunday 11:15: NO.** Reliability and submission win.

## Questions to keep asking

- Did the model fail because evidence was missing, stale, contradictory, badly structured, or badly reasoned over?
- Did the second pass change **retrieval/context behavior**, or just rewrite the answer?
- Does an experiment change a measured metric on held-out data?
- Is this sponsor integration central to the loop or just decoration?
- Could Gemini/ChatGPT/Claude continue this work from LifeOps without needing this chat transcript?
