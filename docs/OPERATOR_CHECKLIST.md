# WorldLoop Operator Checklist

This is the shortest path from setup to a strong judged WorldLoop result. Do not work top-to-bottom mechanically if an item is blocked; preserve the offline baseline and continue with the next non-dependent item.

## A. User/account actions — do these first

### W&B

- [ ] Confirm the hackathon project is under a **W&B team entity**, not a personal entity, if ARIA is desired.
- [ ] Ask a W&B admin/onsite engineer to confirm **Smart features are enabled** for that organization.
- [ ] Create or identify the project `worldloop-coreweave-2026` under that team.
- [ ] Obtain a W&B API key and put it in Infisical `worldloop/hackathon` as `WANDB_API_KEY`.
- [ ] Confirm Inference credits are active if using W&B Inference.
- [ ] Connect W&B MCP to at least one coding agent (Gemini/Cursor/Claude) only after the runtime traces exist.

### Infisical

- [ ] Create/link project `worldloop`.
- [ ] Create environments `dev`, `hackathon`, `prod`.
- [ ] Put only required hackathon secrets in `hackathon`.
- [ ] Create a narrow OCI machine identity with read access to the `hackathon` secret path/environment.
- [ ] Prefer short-lived tokens; do not put broad provider keys into Git, notebook cells, prompts, LifeOps observations, or issues.

### marimo / molab

- [ ] Sign in to molab.
- [ ] Open/mirror the WorldLoop notebook from GitHub.
- [ ] Confirm GPU availability only if/when EXP-009 or training requires it.
- [ ] Treat downloaded models/datasets as scratch unless explicitly persisted/exported.
- [ ] Install/configure marimo pair if a coding/research agent will operate inside the live notebook.

### CoreWeave Sandboxes

Only if we decide a stateful/code-execution episode is useful:

- [ ] Ask onsite CoreWeave engineer whether the event account includes CKS Sandbox access.
- [ ] Confirm a CKS cluster exists.
- [ ] Confirm a Sandbox profile + runner exists and is `Ready`.
- [ ] Confirm your identity has `SANDBOX_USER`.
- [ ] Put the CoreWeave access token in Infisical as `CWSANDBOX_API_KEY`.

If any of these are unavailable, Sandboxes remain out of the critical path.

### TypeSafe

Ask onsite before coding against it:

- [ ] Exact API endpoint/protocol?
- [ ] Model IDs/capabilities?
- [ ] Structured output / tool calling?
- [ ] Context limits?
- [ ] Usage/rate limits?
- [ ] Request-level latency/token/cost telemetry?
- [ ] Intended hacker use cases?

Do not assume undocumented features.

### ARIA / W&B Launch

For analysis-only ARIA:

- [ ] Team project + Smart features is enough to begin asking questions.

For ARIA to launch experiments:

- [ ] Configure W&B Launch queue.
- [ ] Choose Docker or Kubernetes compute backend.
- [ ] Start a persistent Launch agent.
- [ ] Use a W&B service-account API key for the Launch agent when possible.
- [ ] Verify ARIA can see the queue and submit a tiny canary job.

If Launch setup becomes expensive, keep ARIA as the experiment analyst and continue.

## B. OCI bootstrap

From the authoritative WorldLoop source revision:

```bash
cd ~/projects/worldloop
git fetch origin main
git merge --ff-only origin/main
./scripts/bootstrap_oci.sh
```

Link/authenticate Infisical, then run:

```bash
export INFISICAL_TOKEN=$(infisical login \
  --method=universal-auth \
  --client-id="$INFISICAL_UNIVERSAL_AUTH_CLIENT_ID" \
  --client-secret="$INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET" \
  --silent --plain)

infisical run --projectId="$INFISICAL_PROJECT_ID" --env=hackathon -- \
  ./scripts/preflight.sh
```

Expected:

- git/python/uv available;
- weave/marimo/cwsandbox packages import;
- `WANDB_API_KEY=PRESENT`;
- fixture count valid;
- configured localhost port free.

Use the known-free WorldLoop port rather than colliding with existing LiveLM services.

## C. Judging-critical implementation order

### Gate 1 — Weave trajectory

Exit condition:

- one real WorldLoop episode appears in Weave;
- Compiler, retrieval/tool, worker, Critic, Loop Doctor and retry are inspectable;
- run/code/data/policy/model/scorer identity is attached before spans start;
- failure class and policy delta are explicit;
- score delta is real.

Use the native agent conversation/span model where practical. Avoid duplicate traces from implicit provider autopatching when hand-instrumenting.

### Gate 2 — marimo Live Loop

Exit condition:

- choose a case in the notebook/app;
- see Context Manifest;
- see pass-by-pass evidence;
- see Critic failure class;
- see Loop Doctor policy delta;
- see final verification;
- link/run ID into Weave.

### Gate 3 — EXP-008 held-out improvement

Exit condition:

- frozen train/development and held-out task groups;
- policy v0 fixed;
- derive/train policy v1 only from allowed development trajectories;
- compare first-pass success, verified final success, recovery, routing/context regret, latency/cost;
- no oracle/counterfactual leakage into online decision inputs.

A simple table/tree/classifier is acceptable if it produces the measured improvement. Do not force neural fine-tuning.

### Gate 4 — real model fleet

Only after evaluation is trustworthy:

- W&B Inference control models;
- TypeSafe if interface/access is known;
- identical evidence snapshot and evaluation contract;
- token/cost/latency captured where available.

### Gate 5 — W/C/M causal study

Only after core judging proof works:

- synthetic fictional world;
- W/C/M 2^3 cells;
- conflict/staleness cases;
- open-model LoRA on/off only if causal parameter intervention is feasible;
- publish durable dataset/adapter artifacts to W&B/Git, not molab scratch storage.

### Gate 6 — ARIA / BTW / SkyPilot / Sandboxes

Add only when each solves a measured residual:

- ARIA: identify real failure cluster and recommend/run one bounded experiment;
- BTW/LiveLM: real external-memory backend behind the same EvidenceItem contract;
- SkyPilot: parallel jobs or training that are painful without managed execution;
- Sandboxes: persistent isolated tool/code episodes.

## D. What the system must log

Every comparable run should expose:

- experiment_id
- run_id
- code_revision
- dataset/evidence snapshot
- context hash / selected refs
- policy_version
- provider/model
- scorer_version
- pass number
- action/resource recipe
- evidence refs
- final output / abstention
- failure_class
- policy_delta
- correctness/support scores
- retrieval/tool calls
- latency
- token/cost where available

## E. What not to spend time on during the hackathon

- rebuilding LifeOps;
- full Bridge/HomeBase integration;
- production auth perfection;
- multi-cloud portability;
- large-scale RL before eval works;
- deep frontend work beyond the marimo demo surface;
- turning every sponsor into a dependency;
- claiming closed-model weight access;
- making BTW/private data required for the demo.

## F. Three-minute demo readiness test

You are ready when a person who has never heard of LifeOps or BTW can understand this in one screen:

1. Compiler chooses the wrong cognitive resource/context.
2. Independent Critic proves why it is wrong.
3. Loop Doctor changes a real decision variable.
4. Retry becomes verified.
5. Weave shows the evidence/trajectory.
6. marimo shows policy v1 doing better than v0 on unseen tasks.
7. Optional: W/C/M or real BTW evidence shows the architecture generalizes.

## G. After the hackathon

The exact same contracts continue:

fixture backend -> BTW/LiveLM/source APIs

manual/simple policy -> trained Context Materializer + Epistemic Router

hackathon traces -> production monitors/feedback datasets

marimo demo -> research/operator console

OCI process -> container/service runtime

candidate policy -> frozen eval -> canary -> promote/reject/rollback

The project is successful if the hackathon implementation becomes the first measurable version of this long-lived loop rather than a separate throwaway demo.
