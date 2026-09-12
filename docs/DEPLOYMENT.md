# WorldLoop Deployment and Secrets

WorldLoop should use one codebase across local development, OCI, marimo/molab experiments, and later production serving. Secrets are injected at runtime; code and non-secret configuration remain in GitHub.

## Principle

Infisical is the secret-distribution layer, not the project state store and not the notebook host.

GitHub stores source, schemas, experiment definitions, and deployment scripts. Infisical stores credentials. W&B stores traces/evaluations and model/data lineage. marimo/molab stores live computational state only for the duration of the experiment session. External source systems remain authoritative for mutable truth.

## Secret inventory

Expected secret families may include:

```text
WANDB_API_KEY
CWSANDBOX_API_KEY
TYPESAFE_API_KEY / endpoint credentials
OPENAI_API_KEY / other provider credentials
LIFEOPS_MCP_* credentials if a private adapter is enabled
SKYPILOT / cloud credentials only if the optional job plane is used
```

Non-secret configuration may remain in Git/source-controlled config where safe:

```text
WORLDLOOP_WEAVE_PROJECT
WORLDLOOP_PORT
experiment IDs
policy names
model aliases
adapter enable/disable flags
```

## Infisical project layout

Recommended environments:

```text
worldloop
  /dev
  /hackathon
  /prod
```

Use least-privilege machine identities for OCI/CI/production instead of sharing a broad personal token. The hackathon environment should receive only the credentials required for the experiments being run.

`infisical init` may create a repository-local pointer/config file; it contains project linkage rather than the secrets themselves and can be committed if reviewed. Never commit exported secret values.

## Local / OCI development

After installing the Infisical CLI and authenticating/linking the repo, launch WorldLoop by wrapping the existing command:

```bash
infisical run --env=hackathon -- ./scripts/preflight.sh

infisical run --env=hackathon -- \
  uv run worldloop demo --case case-cross-entity --json
```

For the marimo app on OCI:

```bash
infisical run --env=hackathon -- \
  uv run marimo edit notebooks/worldloop_lab.py
```

For read-only/app mode:

```bash
infisical run --env=hackathon -- \
  uv run marimo run notebooks/worldloop_lab.py --host 127.0.0.1 --port 18788
```

The application continues to read normal environment variables; the secrets never need to be written into `.env` or notebook source.

## W&B / Weave on OCI

The existing bootstrap installs the sponsor dependencies. With Infisical injecting `WANDB_API_KEY`, WorldLoop's Weave integration can initialize the configured `WORLDLOOP_WEAVE_PROJECT` without code changes.

Recommended flow:

```text
Git SHA
  -> Infisical injects WANDB_API_KEY + optional provider keys
  -> WorldLoop run
  -> Weave trajectory/evaluation
  -> marimo analysis
  -> candidate change
  -> held-out evaluation
```

Preflight should continue reporting secret presence only, never values.

## marimo / molab

marimo notebooks are source-controlled Python and should be treated as experiment applications, not secret stores.

On OCI/local, use Infisical runtime injection around `marimo edit` or `marimo run`.

On molab, use the platform's supported secret mechanism for the small number of credentials required by that session, or run experiments that do not require private credentials. Do not paste broad production keys into notebook cells. Durable source, experiment manifests, and results should be pushed to GitHub/W&B rather than depending on notebook-session storage.

The target WorldLoop Lab exposes Live Loop, Policy Comparison, Knowledge Location, Failure Explorer, and Experiment Registry views while linking each result to its Weave run/evaluation identity.

## Real-world external knowledge

The production memory/evidence interface should allow multiple backends under one typed contract:

```text
ExternalMemory.query(task, obligations, as_of)
  -> EvidenceItem[]
```

An `EvidenceItem` retains stable source ID, provenance, event/validity time, observation time, entity/object refs, freshness/supersession state, and content/normalized claims.

Backends can include the public/synthetic fixture store, a read-only BTW/LiveLM adapter, LifeOps durable objects where appropriate, and source-native APIs/databases/files.

The core rule is that a backend supplies evidence; it does not automatically become trusted context. WorldLoop still decides what to materialize and the Critic still verifies whether the evidence is sufficient/current/non-contradictory.

## Production serving path

The research notebook should not be the production serving dependency. A practical deployment is:

```text
client/task
  -> WorldLoop API/runtime
  -> Context Compiler / router
  -> model + external evidence/tool adapters
  -> independent verifier
  -> result/abstention + trace

              -> Weave
              -> W&B model/data lineage
              -> marimo operations/research app
```

Container/process secrets are injected by Infisical or a platform-native Infisical integration. Prefer short-lived/machine-identity authentication over static personal tokens as the system matures.

## Promotion path

Do not let the live service train and overwrite its own incumbent policy directly.

```text
production trajectories
  -> candidate dataset
  -> offline training/derivation
  -> frozen evaluation
  -> canary
  -> explicit promote/reject
  -> rollbackable version
```

This preserves the same scientific contract from hackathon demo through deployment.

## Immediate hackathon setup checklist

1. Create/link an Infisical `worldloop` project with a `hackathon` environment.
2. Put W&B and any event-issued provider/CoreWeave/TypeSafe credentials there.
3. Authenticate the OCI machine with the narrowest practical identity.
4. Verify `infisical run --env=hackathon -- ./scripts/preflight.sh` shows required keys as present without printing values.
5. Launch the traced WorldLoop run and marimo Lab under the same injected environment.
6. Keep fixture-only/offline fallback working when remote credentials are unavailable.
