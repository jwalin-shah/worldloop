from __future__ import annotations

import json
import os
import re
import time
from typing import Any

import httpx

from .benchmark import GeneratedCase
from .typesafe_router import ROUTE_CRITERIA, Route, SemanticRouteResult, _coerce_route, routing_state

DEFAULT_WANDB_INFERENCE_MODEL = "meta-llama/Llama-3.3-70B-Instruct"
WANDB_INFERENCE_URL = "https://api.inference.wandb.ai/v1/chat/completions"


def _extract_json_block(text: str) -> dict[str, Any]:
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # Fallback to direct json parse
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        return json.loads(text[brace_start : brace_end + 1])
    return json.loads(text)


def build_routing_prompt(state: dict[str, Any]) -> str:
    return (
        "You are WorldLoop Semantic Router.\n"
        "Your task is to select the smallest, most bounded retrieval route needed before deciding "
        "the rollout question.\n"
        "Do NOT decide APPROVE/BLOCK/ESCALATE and do NOT invent facts that are absent from the state.\n\n"
        f"Route Criteria:\n{json.dumps(ROUTE_CRITERIA, indent=2)}\n\n"
        f"State:\n{json.dumps(state, indent=2)}\n\n"
        "Respond with ONLY a valid JSON object matching this exact schema:\n"
        "{\n"
        '  "route": "EXACT" | "TEMPORAL" | "GRAPH" | "DEEP_RETRIEVAL" | "MODEL_ONLY" | "LEXICAL" | "VECTOR" | "ABSTAIN",\n'
        '  "confidence": <float between 0.0 and 1.0>,\n'
        '  "reasoning": "<concise 1 sentence explanation>"\n'
        "}"
    )


def wandb_inference_route(
    case: GeneratedCase,
    model: str = DEFAULT_WANDB_INFERENCE_MODEL,
    mode: str = "latent",
    api_key: str | None = None,
    client: httpx.Client | None = None,
) -> SemanticRouteResult:
    """Run route prediction using W&B Hosted Inference (general LLM control arm)."""
    token = api_key or os.getenv("WANDB_API_KEY")
    if not token and client is None:
        raise RuntimeError(
            "WANDB_API_KEY is not set. Run with Infisical or provide api_key."
        )

    state = routing_state(case, mode=mode)
    prompt = build_routing_prompt(state)

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "worldloop-eval/1.0",
    }

    start_time = time.perf_counter()
    if client is not None:
        resp = client.post(WANDB_INFERENCE_URL, headers=headers, json=payload)
    else:
        with httpx.Client(timeout=30.0) as default_client:
            resp = default_client.post(WANDB_INFERENCE_URL, headers=headers, json=payload)
    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    if resp.status_code != 200:
        raise RuntimeError(
            f"W&B Inference API error (status {resp.status_code}): {resp.text}"
        )

    data = resp.json()
    choice_msg = data["choices"][0]["message"]["content"]
    parsed = _extract_json_block(choice_msg)

    route_raw = str(parsed.get("route", "EXACT")).strip().upper()
    route = _coerce_route(route_raw)
    confidence = float(parsed.get("confidence", 0.8))

    # Pseudo-distribution for parity with SemanticRouteResult
    probabilities = {route: round(confidence, 4)}

    return SemanticRouteResult(
        route=route,
        confidence=confidence,
        probabilities=probabilities,
        provider="wandb_inference",
        model=model,
    )
