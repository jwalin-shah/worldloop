import marimo

__generated_with = "0.24.2"
app = marimo.App(width="full")


@app.cell
def _():
    import os
    from pathlib import Path

    import marimo as mo

    from worldloop.engine import WorldLoop
    from worldloop.lab import (
        heldout_comparison_rows,
        lab_summary,
        live_program_view,
        load_gate3_report,
        program_comparison_rows,
    )
    from worldloop.runtime import FIXTURES

    root = Path(__file__).resolve().parents[1]
    loop = WorldLoop(FIXTURES)
    gate3_report = load_gate3_report(root)
    scorecard = lab_summary(gate3_report)
    weave_project = os.getenv("WORLDLOOP_WEAVE_PROJECT", "jwalinshah13-personal/worldloop")
    weave_run_url = os.getenv("WORLDLOOP_WEAVE_RUN_URL", "")
    return (
        gate3_report,
        heldout_comparison_rows,
        live_program_view,
        loop,
        mo,
        program_comparison_rows,
        scorecard,
        weave_project,
        weave_run_url,
    )


@app.cell
def _(mo, scorecard, weave_project, weave_run_url):
    weave_status_text = weave_run_url or f"pending live canary in {weave_project}"
    mo.vstack(
        [
            mo.md(
                "# WorldLoop Lab\n"
                "**Learn from a verified failure, compile a smaller explicit program, "
                "and prove the change on frozen held-out tasks.**"
            ),
            mo.ui.table(
                [
                    {"metric": "Dataset snapshot", "value": scorecard["dataset_snapshot"]},
                    {"metric": "Frozen held-out cases", "value": scorecard["heldout_cases"]},
                    {"metric": "v0 first-pass verified", "value": scorecard["v0_first_pass"]},
                    {"metric": "v1 first-pass verified", "value": scorecard["v1_first_pass"]},
                    {"metric": "Final verified", "value": scorecard["final_verified"]},
                    {"metric": "Promotion", "value": scorecard["promotion_decision"]},
                    {"metric": "Weave", "value": weave_status_text},
                ],
                selection=None,
            ),
        ]
    )


@app.cell
def _(loop, mo):
    case_selector = mo.ui.dropdown(
        options=sorted(loop.cases),
        value="case-cross-entity",
        label="Inspect a sanitized execution",
    )
    mo.vstack([mo.md("## 1. Live Program"), case_selector])
    return (case_selector,)


@app.cell
def _(case_selector, live_program_view, loop):
    live_view = live_program_view(loop, case_selector.value)
    return (live_view,)


@app.cell
def _(live_view, mo):
    before = " -> ".join(live_view["program_before"])
    after = " -> ".join(live_view["program_after"])
    delta = ", ".join(live_view["program_delta"]) or "none"
    mo.vstack(
        [
            mo.md(
                f"### {live_view['case_id']}\n\n"
                f"**Question:** {live_view['question']}\n\n"
                f"**Required evidence:** `{', '.join(live_view['required_evidence'])}`"
            ),
            mo.md("#### Pass-by-pass execution"),
            mo.ui.table(live_view["pass_rows"], selection=None),
            mo.md("#### Transition checks"),
            mo.ui.table(live_view["transition_rows"], selection=None),
            mo.callout(
                mo.md(
                    f"**Localized failure:** `{live_view['failure_class']}`  \n"
                    f"**Program v0:** `{before}`  \n"
                    f"**Learned local delta:** `{delta}`  \n"
                    f"**Repaired program:** `{after}`  \n"
                    f"**Final verified:** `{live_view['final_sufficient']}`"
                ),
                kind="success" if live_view["final_sufficient"] else "warn",
            ),
        ]
    )


@app.cell
def _(gate3_report, heldout_comparison_rows):
    heldout_rows = heldout_comparison_rows(gate3_report)
    return (heldout_rows,)


@app.cell
def _(gate3_report, heldout_rows, mo):
    decision = gate3_report["promotion_decision"]
    mo.vstack(
        [
            mo.md("## 2. Held-out Comparison"),
            mo.md(
                "The rule policy was derived from **development trajectories only**. "
                "These metrics are computed on 21 frozen held-out cases with disjoint "
                "entity names and a later time cluster."
            ),
            mo.ui.table(heldout_rows, selection=None),
            mo.callout(
                mo.md(
                    f"**Decision: `{decision}`** — first-pass verified success improved from "
                    f"`{gate3_report['v0']['first_pass_verified_success']:.3f}` to "
                    f"`{gate3_report['v1']['first_pass_verified_success']:.3f}` while final "
                    f"verified success remained "
                    f"`{gate3_report['v1']['final_verified_success']:.3f}`."
                ),
                kind="success" if decision == "PROMOTED" else "warn",
            ),
        ]
    )


@app.cell
def _(gate3_report, program_comparison_rows):
    program_rows = program_comparison_rows(gate3_report)
    return (program_rows,)


@app.cell
def _(mo, program_rows):
    mo.vstack(
        [
            mo.md("## 3. Before / After Program"),
            mo.md(
                "WorldLoop does not ask a model to own global control flow. The derived v1 "
                "turns repeated failure structure into explicit retrieval operations."
            ),
            mo.ui.table(program_rows, selection=None),
            mo.md(
                "**What changed:** freshness-sensitive tasks compile `temporal`; "
                "cross-entity tasks compile `graph`; exact-control tasks stay `exact`. "
                "The held-out evaluator, not this notebook, decides whether v1 is promoted."
            ),
        ]
    )


@app.cell
def _(mo):
    mo.callout(
        mo.md(
            "**Reproducibility / privacy:** this lab reads only source-controlled sanitized "
            "WorldLoop fixtures and the committed Gate 3 report. W&B credentials are optional "
            "and injected at runtime; private LifeOps data is never loaded automatically."
        ),
        kind="info",
    )


if __name__ == "__main__":
    app.run()
