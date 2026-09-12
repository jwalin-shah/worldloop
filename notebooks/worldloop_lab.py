import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import json
    from pathlib import Path

    import marimo as mo

    from worldloop.engine import WorldLoop
    from worldloop.runtime import FIXTURES

    root = Path(__file__).resolve().parents[1]
    loop = WorldLoop(FIXTURES)
    registry = json.loads((root / "experiments" / "registry.json").read_text())
    return loop, mo, registry


@app.cell
def _(loop, mo):
    case_selector = mo.ui.dropdown(
        options=sorted(loop.cases),
        value="case-cross-entity",
        label="Benchmark case",
    )
    mo.vstack(
        [
            mo.md("# WorldLoop Lab\nInspect retrieval failures, policy changes, and experiment state."),
            case_selector,
        ]
    )
    return (case_selector,)


@app.cell
def _(case_selector, loop):
    result = loop.run_case(case_selector.value)
    pass_rows = [
        {
            "pass": item.pass_number,
            "recipe": " -> ".join(item.recipe),
            "score": item.score,
            "sufficient": item.sufficient,
            "failure_class": item.failure_class or "",
            "diagnosis": item.diagnosis or "",
            "evidence": ", ".join(item.evidence_ids),
        }
        for item in result.passes
    ]
    return pass_rows, result


@app.cell
def _(mo, pass_rows, result):
    mo.vstack(
        [
            mo.md(f"## {result.case_id}\n\n**Question:** {result.question}"),
            mo.ui.table(pass_rows),
            mo.md(
                f"**Improved:** `{result.improved}`  |  "
                f"**Final sufficient:** `{result.final_sufficient}`"
            ),
        ]
    )
    return


@app.cell
def _(loop):
    benchmark = loop.benchmark()
    summary = [
        {"metric": "case_count", "value": benchmark["case_count"]},
        {"metric": "seeded_failure_count", "value": benchmark["seeded_failure_count"]},
        {"metric": "improved_seeded_cases", "value": benchmark["improved_seeded_cases"]},
        {"metric": "final_sufficient_count", "value": benchmark["final_sufficient_count"]},
    ]
    return benchmark, summary


@app.cell
def _(mo, summary):
    mo.vstack([mo.md("## Benchmark scorecard"), mo.ui.table(summary)])
    return


@app.cell
def _(mo, registry):
    experiment_rows = [
        {
            "id": item["id"],
            "status": item["status"],
            "question": item["question"],
            "artifact": item["artifact"],
        }
        for item in registry["experiments"]
    ]
    mo.vstack([mo.md("## Experiment registry"), mo.ui.table(experiment_rows)])
    return


@app.cell
def _(mo):
    mo.callout(
        mo.md(
            "This notebook uses only the public sanitized WorldLoop fixtures. "
            "LifeOps/BTW access is intentionally not automatic: private/source-backed adapters "
            "must preserve their own authority and permissions."
        ),
        kind="info",
    )
    return


if __name__ == "__main__":
    app.run()
