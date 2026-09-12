# WorldLoop Platform Deep Dive

Last audited: 2026-09-12 during CoreWeave Hacks.

This document records platform behavior that materially changes WorldLoop design or setup. It is intentionally focused on non-obvious constraints and high-leverage capabilities rather than marketing summaries.

## 1. W&B Weave — use the native agent/evaluation model

WorldLoop should treat Weave as the empirical proof plane, not generic logging.

### Native agent tracing

Weave's agent evaluation workflow can represent conversations with turns, LLM calls, tool calls, and sub-agents. When hand-instrumenting provider SDKs, disable implicit integration patching or the same model activity can be traced twice.

Recommended WorldLoop mapping:

- Context Compiler -> SubAgent/Turn span
- retrieval/tool choice -> Tool span
- worker model call -> LLM span
- Critic -> SubAgent/Turn span + scores
- Loop Doctor -> SubAgent/Turn span with policy delta

Do not create an unrelated parallel trace ontology if Weave can represent the event natively.

### Attributes and run identity

Weave attributes should carry WorldLoop comparison identity such as:

- experiment_id
- run_id
- code_revision
- dataset_snapshot
- evidence_snapshot
- policy_version
- provider/model
- scorer_version
- environment

Important: call attributes cannot be mutated after a Call begins. Attach version/run metadata before invoking each traced operation.

### Evaluation vs EvaluationLogger

Use `weave.Evaluation` for frozen, repeatable benchmark comparisons with predefined datasets/scorers.

Use `EvaluationLogger` for live/streaming WorldLoop episodes where predictions and scores arrive incrementally. Initialize it before LLM invocations when token/cost capture matters, and finish each prediction after its scores are logged.

### Debug determinism

Weave evaluation parallelism defaults to 20. During deterministic debugging and when order-sensitive fixtures are being validated, set `WEAVE_PARALLELISM=1`. Increase only after the evaluation itself is proven stable.

### Scorers

Prefer deterministic/source-aware scorers for core correctness, evidence coverage, provenance, staleness and abstention. Weave supports function/class scorers, applying scorers directly to Calls, built-in scorers, local SLM scorers, monitors, and real-time guardrails.

Production mapping:

- frozen eval -> `Evaluation`
- live episode -> `EvaluationLogger`
- passive production quality -> Monitor
- control-flow blocking -> Guardrail
- human labeling/corrections -> Feedback / annotations

### W&B Models + Weave

Training runs and application evals can be linked both directions. A candidate policy/model artifact should retain its training run ID; Weave eval traces should retain the artifact/model reference; the W&B run can retain the Weave evaluation trace URL/ID. This gives WorldLoop lineage from trajectory -> dataset -> training -> candidate -> held-out eval.

## 2. W&B Serverless Inference / LoRA

W&B Inference is OpenAI-compatible and uses the same W&B API key. It is useful for provider/model comparisons because WorldLoop can keep one request/evaluation contract.

Serverless LoRA inference accepts trained LoRA artifacts directly. Current documented supported base models/rank limits should be checked before committing the W/C/M LoRA intervention to a particular base model.

Do not hard-code a model family before confirming it is currently supported by the event account.

## 3. W&B ARIA — important setup constraints

ARIA is only available in W&B Multi-tenant Cloud team projects, not a personal entity. The organization admin must enable W&B Smart features.

ARIA can analyze runs, identify patterns, recommend experiments, create reports/visualizations, and run experiments. ARIA stores project-scoped memories, but those are ARIA convenience memory, not WorldLoop canonical state.

### To let ARIA actually run experiments

ARIA uses W&B Launch. Required infrastructure is not automatically provisioned by ARIA.

Need:

1. W&B team project with Smart features enabled.
2. W&B Launch queue.
3. Compute backend: Kubernetes or Docker/etc.
4. Running Launch agent polling that queue.
5. W&B service-account API key for durable/team infrastructure; avoid a personal key for the Launch agent.

After the queue + active agent exist, ARIA can submit jobs, relaunch with config overrides, monitor/debug results, and compare metrics.

Hackathon rule: if this setup consumes too much time, use ARIA for analysis/recommendations only. It should not block EXP-005/008.

## 4. W&B MCP

The hackathon-hosted W&B MCP should be treated as an experiment-access interface for coding/research agents. Gemini/Claude/Cursor can inspect runs, traces, evals and reports without manual screenshot copying.

Separate two ideas:

- WorldLoop runtime -> Weave SDK emits evidence.
- Coding/research agents -> W&B MCP inspect that evidence and propose work.

W&B MCP is not WorldLoop canonical project memory.

Weave also has a distinct MCP tracing integration that instruments MCP client/server Tools, Resources and Prompts. Current docs note client-side and server-side operations are traced separately rather than as a guaranteed unified end-to-end trace, so do not assume cross-MCP trace correlation magically exists.

## 5. marimo / molab — scientific workstation, not just UI

marimo notebooks are pure Python, reactive, Git-friendly, executable as scripts, testable, and deployable as apps. This makes the same WorldLoop Lab useful during research and later as an operator/research UI.

### marimo pair

marimo pair puts coding agents inside the live notebook kernel. Agents can inspect intermediate variables, run scratch code over live state, and commit useful work as notebook cells. This is unusually valuable for WorldLoop because agents can inspect ContextManifest objects, counterfactual matrices and failure clusters without the human serializing them into chat.

### molab compute

molab runs on CoreWeave and currently offers 12-hour sessions with optional GPU. Use it for interactive W/C/M inference, analysis and bounded fine-tuning.

### molab persistence constraint

For notebooks created after 2026-08-26, molab persists source files and files under 1GB uploaded/created through the file browser, plus the exact `.env` file and persistent cache subject to limits. Other downloaded artifacts/caches are scratch and are cleared on shutdown.

Therefore:

- source -> GitHub
- eval/model/dataset artifacts -> W&B or owned remote storage
- notebook local caches -> disposable
- do not depend on a downloaded Hugging Face model remaining next session

molab notebooks are public-but-undiscoverable by default; do not put private WorldLoop/LifeOps data or broad credentials into a public notebook.

## 6. Infisical — runtime secret plane

Infisical should inject credentials into WorldLoop processes; it does not own state, experiments, or notebook source.

### Developer path

Use user login + `infisical init` for manual development. `.infisical.json` stores project linkage rather than secret values.

### OCI/automation path

Prefer a narrow machine identity. Universal Auth exchanges client ID + client secret for a short-lived access token. `infisical run` can use `INFISICAL_TOKEN` + project ID and inject secrets into the child process.

Useful production behavior:

- `--watch` restarts the child process when secrets change; do not enable this blindly for active experiments because it can interrupt a run.
- `INFISICAL_DISABLE_UPDATE_CHECK=true` reduces startup overhead in production.
- If a target platform later supports native/OIDC/cloud identity, prefer that over a long-lived Universal Auth bootstrap secret.

WorldLoop environments:

- dev
- hackathon
- prod

Keep provider/API keys isolated by environment and least privilege.

## 7. CoreWeave Sandboxes — prerequisites and true role

CoreWeave Sandboxes are isolated execution environments on CKS for untrusted model-generated actions, RL rollouts, agent harnesses and evaluation episodes.

They are currently public preview and require actual CoreWeave/CKS setup, not only the Python package.

### Required before `cwsandbox` works

Admin side:

- running CKS cluster
- `SANDBOX_ADMIN`
- CoreWeave Intelligent CLI
- create profile
- enable runner

Researcher side:

- `SANDBOX_USER` (or admin)
- CoreWeave API token exposed as `CWSANDBOX_API_KEY`
- Python 3.11+
- runner in Ready state

The sandbox itself can have independent container image, resources, network egress, mounted files, exposed ports, secrets and max lifetime.

### Secret injection

The SDK supports named secrets from configured secret stores. Prefer that mechanism over embedding sensitive values in commands/mounted files if the event environment exposes the required secret store.

### Agent/RL episodes

A single sandbox can persist across multiple tool calls in one rollout, so files/packages/state survive within the episode. That makes it useful for code/SWE/browser-style agent tasks and RL trajectories. It is unnecessary for static WorldLoop retrieval QA.

## 8. SkyPilot — optional compute job plane

SkyPilot can run marimo directly and can submit workloads to existing Kubernetes clusters. It does not provision a Kubernetes cluster for us.

For CoreWeave CKS, `infra: k8s/...` plus `network_tier: best` can automatically request/configure InfiniBand for supported multi-GPU workloads. This becomes valuable only for real distributed training; it is excessive for the first WorldLoop router experiment.

SkyPilot should enter after we have access to an existing CoreWeave Kubernetes cluster and an experiment whose parallelism/training complexity makes managed jobs worthwhile.

## 9. TypeSafe AI — treat unknowns as unknowns

Public material currently describes TypeSafe as a stealth lab focused on machine-native intelligence and 'intelligence per dollar.' The public site does not expose enough stable API/interface documentation to design a hard dependency around it.

Therefore the correct onsite questions are:

- What exact API/protocol is available to hackers?
- What models and context/tool interfaces exist?
- Are structured outputs/tool calling supported?
- What usage limits/latency/cost telemetry are exposed?
- Can we obtain per-request usage/cost?
- Are model internals or only hosted inference exposed?
- Is there an intended router/verifier use case?

Until answered, keep TypeSafe behind the WorldLoop provider adapter and measure it rather than assume capabilities.

## 10. Immediate implications for WorldLoop

1. Use a W&B TEAM project now if ARIA is desired; a personal project will block it.
2. Attach immutable comparison metadata before traced Weave operations begin.
3. Initialize EvaluationLogger before LLM calls for live token/cost capture.
4. Use native Weave Turn/LLM/Tool/SubAgent semantics where possible.
5. Keep frozen `weave.Evaluation` separate from streaming episode logging.
6. Keep molab scratch artifacts disposable; publish durable experiment artifacts elsewhere.
7. Use Infisical machine identity for OCI once the project is linked.
8. Do not make Sandboxes critical-path until we confirm a CKS runner/profile is actually available.
9. Do not make ARIA job execution critical-path until Launch queue/agent is active.
10. Do not make SkyPilot critical-path until an existing CoreWeave K8s context is available.
11. Do not design around undocumented TypeSafe behavior; ask onsite and measure.
12. The first strong judged proof remains Weave trajectory + marimo Live Loop + EXP-008 held-out policy improvement.

## Official references audited

- https://docs.wandb.ai/weave/agent-evals
- https://docs.wandb.ai/weave/guides/tools/attributes
- https://docs.wandb.ai/weave/guides/evaluation/evaluation_logger
- https://docs.wandb.ai/weave/guides/evaluation/scorers
- https://docs.wandb.ai/weave/guides/evaluation/monitors
- https://docs.wandb.ai/weave/guides/evaluation/guardrails
- https://docs.wandb.ai/weave/guides/tracking/feedback
- https://docs.wandb.ai/weave/guides/integrations/mcp
- https://docs.wandb.ai/weave/cookbooks/Models_and_Weave_Integration_Demo
- https://docs.wandb.ai/inference
- https://docs.wandb.ai/inference/lora
- https://docs.wandb.ai/aria/overview
- https://docs.wandb.ai/aria/autoresearch
- https://marimo.io/pages/molab/storage
- https://molab.marimo.io/blog/marimo-pair
- https://docs.marimo.io/
- https://infisical.com/docs/cli/commands/login
- https://infisical.com/docs/cli/commands/run
- https://docs.coreweave.com/products/sandboxes
- https://docs.coreweave.com/products/sandboxes/get-started
- https://docs.coreweave.com/products/sandboxes/client/guides/sandbox-configuration
- https://docs.coreweave.com/products/sandboxes/client/guides/rl-training
- https://docs.skypilot.co/en/latest/examples/performance/coreweave_infiniband.html
- https://docs.skypilot.co/en/latest/examples/frameworks/marimo.html
- https://typesafe.ai/
