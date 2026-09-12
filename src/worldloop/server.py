from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .engine import WorldLoop
from .runtime import FIXTURES
from .weave_integration import weave_status

app = FastAPI(title="WorldLoop", version="0.1.0")


@app.get("/health")
def health() -> dict:
    loop = WorldLoop(FIXTURES)
    return {"ok": True, "service": "worldloop", "cases": len(loop.cases), "weave": weave_status()}


@app.get("/demo/{case_id}")
def demo(case_id: str) -> dict:
    loop = WorldLoop(FIXTURES)
    if case_id not in loop.cases:
        raise HTTPException(status_code=404, detail="unknown case")
    return loop.run_case(case_id).to_dict()
