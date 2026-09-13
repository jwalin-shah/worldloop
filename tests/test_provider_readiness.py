from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace


SCRIPT = Path(__file__).parents[1] / "scripts" / "provider_readiness.py"
SPEC = importlib.util.spec_from_file_location("provider_readiness", SCRIPT)
assert SPEC and SPEC.loader
provider_readiness = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = provider_readiness
SPEC.loader.exec_module(provider_readiness)


def test_typesafe_blocks_when_runtime_missing(monkeypatch, capsys):
    monkeypatch.setattr(provider_readiness.shutil, "which", lambda name: None if name == "infisical" else f"/bin/{name}")

    code = provider_readiness.typesafe_readiness()

    assert code == 11
    out = capsys.readouterr().out
    assert '"blocking_stage": "RUNTIME_EXECUTABLE"' in out
    assert '"reason": "INFISICAL_MISSING"' in out
    assert '"external_provider_calls": 0' in out


def test_typesafe_blocks_on_secret_context(monkeypatch, capsys):
    monkeypatch.setattr(provider_readiness.shutil, "which", lambda name: f"/bin/{name}")
    calls = []

    def fake_run(argv):
        calls.append(tuple(argv))
        if tuple(argv[:4]) == ("uv", "run", "python", "-c"):
            return SimpleNamespace(returncode=0)
        if tuple(argv[:2]) == ("infisical", "run"):
            return SimpleNamespace(returncode=1)
        raise AssertionError(f"unexpected command: {argv}")

    monkeypatch.setattr(provider_readiness, "run_quiet", fake_run)

    code = provider_readiness.typesafe_readiness()

    assert code == 13
    out = capsys.readouterr().out
    assert '"blocking_stage": "SECRET_CONTEXT"' in out
    assert '"reason": "INFISICAL_CONTEXT_UNAVAILABLE"' in out
    assert '"external_provider_calls": 0' in out
    assert len(calls) == 2


def test_typesafe_ready_without_provider_call(monkeypatch, capsys):
    monkeypatch.setattr(provider_readiness.shutil, "which", lambda name: f"/bin/{name}")
    calls = []

    def fake_run(argv):
        calls.append(tuple(argv))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(provider_readiness, "run_quiet", fake_run)

    code = provider_readiness.typesafe_readiness()

    assert code == 0
    out = capsys.readouterr().out
    assert '"status": "READY"' in out
    assert '"external_provider_calls": 0' in out
    # SDK import + secret-context probe + credential-presence probe. None invoke TypeSafe.
    assert len(calls) == 3
    assert all("api.typesafe.ai" not in " ".join(call) for call in calls)
