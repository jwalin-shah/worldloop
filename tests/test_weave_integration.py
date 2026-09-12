import importlib

from worldloop import weave_integration


def test_weave_status_defaults_to_real_worldloop_project(monkeypatch):
    monkeypatch.delenv("WANDB_API_KEY", raising=False)
    monkeypatch.delenv("WORLDLOOP_WEAVE_PROJECT", raising=False)
    module = importlib.reload(weave_integration)
    status = module.weave_status()
    assert status["project"] == "jwalinshah13-personal/worldloop"
    assert status["api_key_present"] is False
    assert status["remote_tracing_ready"] is False
