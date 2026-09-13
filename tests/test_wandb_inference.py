from __future__ import annotations

import json
import httpx
import pytest

from worldloop.benchmark import generate_benchmark
from worldloop.wandb_inference import (
    _extract_json_block,
    build_routing_prompt,
    wandb_inference_route,
)


def test_extract_json_block():
    plain = '{"route": "GRAPH", "confidence": 0.95}'
    assert _extract_json_block(plain) == {"route": "GRAPH", "confidence": 0.95}

    markdown = '```json\n{"route": "TEMPORAL", "confidence": 0.88}\n```'
    assert _extract_json_block(markdown) == {"route": "TEMPORAL", "confidence": 0.88}

    with_surrounding = 'Here is the result:\n```\n{"route": "EXACT"}\n```\nThank you.'
    assert _extract_json_block(with_surrounding) == {"route": "EXACT"}


def test_build_routing_prompt():
    dataset = generate_benchmark()
    case = dataset.heldout[0]
    prompt = build_routing_prompt({"question": case.question, "risk_band": case.risk_band})
    assert "WorldLoop Semantic Router" in prompt
    assert case.question in prompt
    assert "Route Criteria:" in prompt


def test_wandb_inference_missing_key(monkeypatch):
    monkeypatch.delenv("WANDB_API_KEY", raising=False)
    dataset = generate_benchmark()
    case = dataset.heldout[0]
    with pytest.raises(RuntimeError, match="WANDB_API_KEY is not set"):
        wandb_inference_route(case)


def test_wandb_inference_with_mock_client():
    dataset = generate_benchmark()
    case = dataset.heldout[0]

    mock_resp_payload = {
        "id": "chatcmpl-test",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"route": "GRAPH", "confidence": 0.92, "reasoning": "Dependency on Lyra-001"}',
                },
            }
        ],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer test-key"
        assert "worldloop-eval" in request.headers["User-Agent"]
        return httpx.Response(200, json=mock_resp_payload)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)

    result = wandb_inference_route(case, api_key="test-key", client=client)
    assert result.route == "GRAPH"
    assert result.confidence == 0.92
    assert result.provider == "wandb_inference"
    assert result.model == "meta-llama/Llama-3.3-70B-Instruct"
    assert result.recipe == ("vector", "graph")
