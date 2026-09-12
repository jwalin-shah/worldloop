# Hackathon sponsor and infrastructure stack

WorldLoop uses sponsor tools only where they own a real architectural responsibility. The project must remain reproducible on sanitized fixtures without remote credentials; sponsor services make the loop more observable, researchable, trainable, or executable rather than becoming hidden dependencies.

## Priority map

| Component | Priority | WorldLoop responsibility | Concrete hackathon proof |
|---|---|---|---|
| **W&B Weave** | CORE | trajectory/evaluation proof plane | Compiler -> retrieval -> Critic -> Loop Doctor -> rerun spans, scores, attributes, v0/v1 comparison |
| **marimo / molab** | CORE | live scientific workstation + demo + interactive GPU workbench | WorldLoop Lab with loop inspector, policy comparison, W/C/M cube, failure explorer, experiment registry |
| **W&B MCP** | HIGH | lets coding/research agents inspect W&B runs/traces/evals and participate in the improvement loop | Gemini/Cursor/Claude can query experiment evidence rather than relying on chat recollection |
| **ARIA** | STRONG EXTENSION | outer hypothesis/experiment agent | identifies a real failure cluster, proposes one bounded experiment, compares candidate with baseline |
| **W&B Models / Artifacts** | STRONG EXTENSION | dataset/training/model/policy lineage | counterfactual dataset -> training run -> candidate router -> held-out eval lineage |
| **W&B Inference** | STRONG EXTENSION | comparable hosted model fleet / optional LoRA serving | same WorldLoop task/evidence contract across several models |
| **TypeSafe AI** | CONDITIONAL | experimental worker, router, or verifier candidate | measured behavior per cost/latency/tool/retrieval decision, not a hard-coded sponsor path |
| **CoreWeave Sandboxes** | CONDITIONAL | isolated stateful or generated-code episodes | only use if an experiment needs clean executable per-trajectory state |
| **SkyPilot** | OPTIONAL | compute/job execution plane under WorldLoop | parallel W/C/M/counterfactual/training jobs on CoreWeave Kubernetes if it materially simplifies execution |
| **LifeOps / BTW** | OPTIONAL PRIOR WORK | durable continuity / real external-memory adapter | read-only generalization demo; never required for public benchmark |

## W&B Weave — measurement backbone

Weave should make the loop inspectable, not merely satisfy the W&B requirement.

Every pass should record attributes such as:

```text
run_id
experiment_id
case_id
code_revision
dataset_snapshot
evidence_snapshot
context_hash
provider
model
policy_version
pass_number
retrieval_recipe
evidence_refs
failure_class
policy_change
score
sufficient
latency_ms
cost
```

Target Weave story:

```text
pass 1
  -> Compiler chose vector
  -> retrieved incomplete chain
  -> Critic score 0.5 / cross_entity_join
  -> Loop Doctor added graph
pass 2
  -> retrieved complete evidence chain
  -> Critic score 1.0 / sufficient
```

The stronger outer-loop story compares policy versions on held-out tasks rather than only comparing pass 1 and pass 2 of the same task.

Environment:

```text
WANDB_API_KEY
WORLDLOOP_WEAVE_PROJECT=worldloop-coreweave-2026
```

Credentials are never printed or committed.

## marimo / molab — live WorldLoop Lab

marimo is a **first-class part of the project**, not a prettier Jupyter notebook.

The notebook/app should be both the research environment and the demo control surface.

### View 1 — Live Loop

- select task/case;
- show task obligations;
- show exact Context Manifest;
- show initial resource/retrieval plan;
- show evidence selected;
- show pass score/failure class;
- show Loop Doctor change;
- show next pass and final verified result;
- show Weave trace/run reference.

### View 2 — Policy Comparison

Toggle `policy-v0` / `policy-v1` and display held-out:

- first-pass success;
- final success/correct abstention;
- recovery rate;
- routing/context regret;
- retrieval/tool calls;
- latency;
- cost where available.

### View 3 — W/C/M Knowledge Location

Interactive toggles:

```text
W = parameterized adapter/base model state
C = active context supplied
M = external memory available
```

Display outcome, provenance, whether retrieval occurred, and conflict behavior across the 2^3 matrix.

### View 4 — Failure Explorer

Aggregate failures by class and drill down into exact trajectories / counterfactual routes.

### View 5 — Experiment Registry

Render hypothesis, independent variable, baseline/treatment, metrics, stop rule, status, and artifact references from the checked-in registry.

### molab GPU use

Use the CoreWeave-backed 96 GB VRAM GPU for interactive work that actually benefits from it:

- batched counterfactual inference;
- open-model W/C/M experiments;
- embeddings/representation analysis;
- small router/classifier training;
- bounded LoRA fine-tuning if the eval pipeline justifies it.

Do **not** use GPU size as the project story and do not make a large training job the critical path.

### marimo pair

Use marimo pair if useful so a coding/research agent and the human can inspect and change the same reactive experiment runtime. The notebook remains a computational working environment; canonical source is GitHub and durable experimental lineage belongs in W&B/artifacts.

### persistence rule

Do not rely on the molab notebook filesystem as the only copy of source/data/results. Mirror/commit source and persist important datasets/models/results through approved durable storage.

## W&B MCP — agent access to experiment truth

The onsite W&B MCP server is unusually aligned with WorldLoop: coding/research agents can inspect runs, traces, evaluations, and reports directly.

Desired use:

```text
Gemini / Cursor / Claude
        |
        +--> LifeOps MCP: durable project/world state (optional prior infrastructure)
        |
        +--> W&B MCP: empirical experiment state
```

This keeps provider agents from learning about experiment outcomes only through copied chat text.

W&B MCP must not become a second source of mutable world truth; it owns experiment evidence/observability.

## ARIA — outer scientific agent

Use ARIA only if it can contribute a real experimental step.

Good use:

```text
Weave results
  -> ARIA finds temporal failures cluster around a policy feature
  -> proposes a specific experiment
  -> candidate config/policy is run
  -> held-out comparison is recorded
  -> promote/reject
```

Weak use: asking ARIA to summarize charts already visible in marimo.

The system does not allow ARIA to silently mutate the production incumbent. ARIA proposes/designs candidates; evaluation gates promotion.

## W&B Models / Artifacts — training and provenance

If training lands, use Models/Artifacts to version:

- counterfactual trajectory dataset;
- train/validation/held-out splits;
- router features/labels;
- training configuration;
- candidate adapter/model/policy;
- evaluation report;
- promotion decision.

Desired lineage:

```text
Weave trajectories
 -> dataset artifact D3
 -> training run T2
 -> candidate P1
 -> held-out evaluation E4
 -> promote/reject receipt
```

## W&B Inference — model matrix

Use W&B Inference to compare models behind a common WorldLoop interface.

Control the experiment by keeping task, evidence snapshot, context schema, budget, and scorer constant while changing the model/provider.

Questions to measure:

- does model choice matter less or more than context quality?;
- which model best recognizes when retrieval/tool use is necessary?;
- which model wastes retrieval?;
- verified task reward per dollar/latency;
- abstention and recovery behavior.

## TypeSafe AI — machine-native intelligence experiment

Do not assume undocumented internals or make TypeSafe a dependency.

Evaluate whichever roles the onsite API/model actually supports:

1. **Worker:** verified task completion per cost/latency.
2. **Router:** selection of model-only/context/memory/tool/abstain.
3. **Verifier:** detection of unsupported or insufficient machine actions.

The useful question is not "is TypeSafe better at trivia?" but "does it allocate machine actions/intelligence differently and more reliably under a budget?"

## CoreWeave Sandboxes — clean executable episodes

The static fixture retrieval loop does not require sandboxes.

Add Sandboxes when an experiment genuinely needs:

- generated code execution;
- mutable filesystem state;
- dynamically created tools;
- package/environment changes;
- browser/computer-use episodes;
- clean sandbox-per-trajectory reward verification.

Then reset episode state while keeping learned policy/experiment state outside the sandbox.

## SkyPilot — optional compute/job execution plane

SkyPilot is not an agent and is not an authority system.

If used:

```text
WorldLoop experiment spec
  -> authorized/selected compute job
  -> SkyPilot
  -> CoreWeave Kubernetes
  -> result/artifacts
  -> Weave + WorldLoop evaluator
```

Good uses:

- many counterfactual arms;
- W/C/M matrix across model/policy variants;
- LoRA/router training jobs;
- parallel isolated evals.

For hackathon sponsor alignment, primary demonstrated compute should remain CoreWeave. Portability is architectural context, not the headline demo.

## Prior-work adapters: LifeOps and BTW/LiveLM

### LifeOps

Optional development/continuity substrate so Gemini, ChatGPT, Claude, or OCI workers can resolve the same durable project/checkpoint state. This is prior work, not a hackathon-new claim.

### BTW / LiveLM

Optional real-world external-memory backend `M`.

Correct use:

1. learn/evaluate WorldLoop on synthetic/sanitized memory where ground truth is controlled;
2. plug the same new WorldLoop adapter into pre-existing BTW;
3. demonstrate transfer/generalization to changing-world source-backed evidence;
4. label the index and corpus as prior work.

The public benchmark must never depend on private BTW data.

## Go / no-go rule

Add a sponsor/tool integration only when all of the following are true:

1. it owns a distinct architectural responsibility;
2. it produces evidence visible in the demo/evaluation;
3. it can be integrated without destabilizing the core loop;
4. its failure does not destroy the reproducible offline baseline;
5. we can explain its role in one sentence to a judge.
