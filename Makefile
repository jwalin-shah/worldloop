.PHONY: ready bootstrap preflight test lint smoke start stop demo benchmark
ready:
	./scripts/ready.sh
bootstrap:
	./scripts/bootstrap_oci.sh
preflight:
	./scripts/preflight.sh
test:
	uv run pytest -q
lint:
	uv run ruff check .
smoke:
	./scripts/smoke.sh
start:
	./scripts/start.sh
stop:
	./scripts/stop.sh
demo:
	uv run worldloop demo --case case-cross-entity --json
benchmark:
	uv run worldloop benchmark --json
