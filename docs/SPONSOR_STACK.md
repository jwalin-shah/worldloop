# Hackathon sponsor stack

WorldLoop keeps the public demo deterministic and usable without cloud credentials, while preinstalling the sponsor-facing SDKs we can use onsite.

| Capability | VM preparation | Credential / access boundary |
|---|---|---|
| W&B Weave | `weave` Python SDK installed by `bootstrap_oci.sh`; tracing hooks and `weave.Evaluation` adapter included | `WANDB_API_KEY`; project defaults to `worldloop-coreweave-2026` |
| CoreWeave Sandboxes | `cwsandbox` Python SDK installed | `CWSANDBOX_API_KEY`; no sandbox is created automatically |
| CoreWeave ARIA | No separate local package is assumed; WorldLoop's W&B project/traces are prepared for ARIA analysis | Access through the W&B/CoreWeave account/event environment |
| marimo | `marimo` installed locally for an optional benchmark notebook/dashboard | Local usage needs no cloud key; molab access is external |
| TypeSafe AI | Adapter slot only; not a hard dependency because the event provides model access/details onsite | Add the event-issued endpoint/key without committing it |

`./scripts/preflight.sh` prints **presence only**, never credential values. Missing sponsor credentials do not block the sanitized fixture demo.

CoreWeave Sandboxes are deliberately optional: WorldLoop itself does not execute untrusted generated code, so the demo has no reason to create cloud sandboxes until we add an agent/tool episode that benefits from isolated execution.
