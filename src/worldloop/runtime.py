from __future__ import annotations

from pathlib import Path

from .engine import WorldLoop
from .weave_integration import traced

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "fixtures"


@traced
def run_traced_case(case_id: str) -> dict:
    return WorldLoop(FIXTURES).run_case(case_id).to_dict()
