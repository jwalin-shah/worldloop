# OCI one-command runbook

The intended host checkout is `/home/ubuntu/projects/worldloop`.

## Bring an existing clean checkout to hackathon-ready

```bash
cd /home/ubuntu/projects/worldloop
git fetch origin main
git merge --ff-only origin/main
./scripts/ready.sh
```

Equivalent shortcut after sync: `make ready`.

`ready.sh` runs the bootstrap twice (idempotence), sponsor/tool preflight, unit tests, Ruff, and the localhost end-to-end smoke. A successful run ends with `READY_FOR_HACKATHON`.

## Credentials

Do not put credentials in the repository or `.env.example`. Export event/account credentials only in the host session or an existing approved secret mechanism:

- `WANDB_API_KEY` enables remote Weave tracing/evaluation.
- `CWSANDBOX_API_KEY` enables CoreWeave Sandboxes.
- `WORLDLOOP_WEAVE_PROJECT` optionally changes the W&B project name.

Missing cloud credentials do **not** block the sanitized local demo; preflight reports presence only.

## Demo

```bash
make demo
make benchmark
./scripts/start.sh
curl http://127.0.0.1:8787/health
./scripts/stop.sh
```

The default service binds only to `127.0.0.1`; this runbook never changes OCI firewall, IAM, SSH, or cloud networking.
