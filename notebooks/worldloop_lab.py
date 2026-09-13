import marimo

__generated_with = "0.24.2"
app = marimo.App(width="full")


@app.cell
def _():
    import io
    import os
    import subprocess
    import sys
    import tarfile
    import urllib.request
    from pathlib import Path

    import marimo as mo

    root = Path(__file__).resolve().parents[1]
    if not (root / "fixtures").exists() or not (root / "src").exists():
        repo_dir = Path("/tmp/worldloop_repo")
        if not (repo_dir / "fixtures").exists():
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", "https://github.com/jwalin-shah/worldloop.git", str(repo_dir)],
                    check=True,
                    capture_output=True,
                )
            except (OSError, subprocess.SubprocessError):
                try:
                    url = "https://github.com/jwalin-shah/worldloop/archive/refs/heads/main.tar.gz"
                    with (
                        urllib.request.urlopen(url, timeout=15) as resp,
                        tarfile.open(fileobj=io.BytesIO(resp.read()), mode="r:gz") as tar,
                    ):
                        tar.extractall(path=Path("/tmp/worldloop_extract"))
                    repo_dir = next(Path("/tmp/worldloop_extract").glob("worldloop-*"), repo_dir)
                except (OSError, tarfile.TarError):
                    repo_dir = root
        if (repo_dir / "fixtures").exists():
            root = repo_dir

    if (root / "src").exists() and str(root / "src") not in sys.path:
        sys.path.insert(0, str(root / "src"))

    from worldloop.engine import WorldLoop
    from worldloop.lab import (
        heldout_comparison_rows,
        lab_summary,
        lifeops_pilot_rows,
        live_program_view,
        load_adversarial_report,
        load_gate3_report,
        load_lifeops_pilot,
        load_three_arm_report,
        program_comparison_rows,
        three_arm_case_rows,
        three_arm_summary_rows,
    )

    loop = WorldLoop(root / "fixtures")
    gate3_report = load_gate3_report(root)
    three_arm_report = load_three_arm_report(root)
    adversarial_report = load_adversarial_report(root)
    lifeops_pilot_report = load_lifeops_pilot(root)
    scorecard = lab_summary(gate3_report)
    weave_project = os.getenv("WORLDLOOP_WEAVE_PROJECT", "jwalinshah13-personal/worldloop")
    weave_run_url = os.getenv("WORLDLOOP_WEAVE_RUN_URL", "")
    return (
        adversarial_report,
        gate3_report,
        heldout_comparison_rows,
        lifeops_pilot_report,
        lifeops_pilot_rows,
        live_program_view,
        loop,
        mo,
        program_comparison_rows,
        scorecard,
        three_arm_case_rows,
        three_arm_report,
        three_arm_summary_rows,
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
def _(
    adversarial_report,
    mo,
    three_arm_case_rows,
    three_arm_report,
    three_arm_summary_rows,
):
    frontier_elements = [
        mo.md(
            "## 4. Three-Arm Cognitive Frontier\n"
            "Evaluating where deterministic structure stops being sufficient and where semantic "
            "judgment is strictly necessary.\n\n"
            "Three execution arms evaluated on unstructured operational prose:\n"
            "1. **Deterministic Heuristic** (compiler / pattern matching baseline)\n"
            "2. **TypeSafe Multi-Primitive Jev** (parallel Nouls & Choices + WorldLoop receipt policy matrix)\n"
            "3. **W&B Hosted Inference** (Meta Llama 3.3 70B Instruct general LLM)\n"
        )
    ]
    if three_arm_report is not None:
        summary_rows = three_arm_summary_rows(three_arm_report)
        case_rows = three_arm_case_rows(three_arm_report)
        frontier_elements.extend(
            [
                mo.md("### Frozen Held-Out Benchmark (Receipt-Obligated)"),
                mo.ui.table(summary_rows, selection=None),
                mo.ui.table(case_rows, selection=None),
                mo.callout(
                    mo.md(
                        "**Receipt-Aware Certification:** Routine cases requiring registry verification "
                        "are legally bounded to `EXACT` rather than unverified `MODEL_ONLY`, achieving 100% "
                        "verified receipt allocation across the frozen held-out tasks at ~200ms latency."
                    ),
                    kind="success",
                ),
            ]
        )
    if adversarial_report is not None:
        adv_summary = three_arm_summary_rows(adversarial_report)
        adv_cases = three_arm_case_rows(adversarial_report)
        frontier_elements.extend(
            [
                mo.md("### Adversarial / Naturalistic Frontier (No Keyword Giveaways)"),
                mo.ui.table(adv_summary, selection=None),
                mo.ui.table(adv_cases, selection=None),
                mo.callout(
                    mo.md(
                        "**Adversarial Frontier Takeaway:** When keyword giveaways (`'dependency'`, `'superseding'`) "
                        "are removed from operational prose, the deterministic heuristic collapses to **33.3%** "
                        "(under-allocating on every graph and temporal case). TypeSafe Jev and W&B Llama 3.3 70B "
                        "maintain semantic comprehension, proving where learned semantic primitives become strictly necessary."
                    ),
                    kind="warn",
                ),
            ]
        )
    if three_arm_report is None and adversarial_report is None:
        frontier_elements.append(
            mo.callout(
                mo.md("Run `python scripts/run_three_arm_eval.py` to populate live evaluations."),
                kind="info",
            )
        )
    frontier_view = mo.vstack(frontier_elements)
    frontier_view


@app.cell
def _(lifeops_pilot_report, lifeops_pilot_rows, mo):
    pilot_elements = [
        mo.md(
            "## 5. Real-World Pilot — Engineering Runtime Routing\n"
            "A public-safe snapshot from the real LifeOps execution fabric. This is a **single "
            "live snapshot**, not a held-out real-world benchmark."
        )
    ]
    if lifeops_pilot_report is not None:
        rows = lifeops_pilot_rows(lifeops_pilot_report)
        route = lifeops_pilot_report["candidate_policy_v1"]["selected_route"]
        pilot_elements.extend(
            [
                mo.ui.table(rows, selection=None),
                mo.callout(
                    mo.md(
                        f"**Proof-aware route:** `{route}`  \n"
                        "When current runtime proof is unavailable or internally conflicted, "
                        "the correct policy is to abstain and repair the evidence path before "
                        "spending another worker/model call."
                    ),
                    kind="warn",
                ),
            ]
        )
    else:
        pilot_elements.append(
            mo.callout(
                mo.md("Real-world pilot report is not present in this checkout."),
                kind="info",
            )
        )
    mo.vstack(pilot_elements)


@app.cell
def _(mo):
    mo.callout(
        mo.md(
            "**Reproducibility / privacy:** this lab reads only source-controlled sanitized "
            "WorldLoop fixtures, committed experiment reports, and a public-safe LifeOps routing "
            "snapshot. W&B credentials are optional and private LifeOps data is never loaded "
            "automatically."
        ),
        kind="info",
    )


if __name__ == "__main__":
    app.run()