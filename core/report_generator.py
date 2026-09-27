"""
core/report_generator.py — Final debugging report generation.

Generates a structured, human-readable Markdown report for each Bug2Fix run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------

def generate_report(run_state: dict) -> str:
    """
    Generate a Markdown debugging report from *run_state*.

    Returns the report as a string.
    """
    run_id   = run_state.get("run_id", "unknown")
    project  = run_state.get("project", "unknown")
    status   = run_state.get("status", "unknown")
    bug      = run_state.get("bug_report", {})
    metrics  = run_state.get("metrics", {})
    agents   = run_state.get("agents", {})
    changes  = run_state.get("changes", [])
    tests    = run_state.get("tests", {})
    root_cause_data = run_state.get("root_cause", {})
    fix_data = run_state.get("fix", {})
    verify   = run_state.get("verification", {})

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        f"# Bug2Fix AI — Debugging Report",
        f"",
        f"> **Run ID:** `{run_id}`  |  **Generated:** {now}  |  **Status:** {status.upper()}",
        f"",
        "---",
        "",
        "## 1. Bug Summary",
        "",
        f"**Title:** {bug.get('title', 'N/A')}",
        "",
        f"**Description:**",
        f"> {bug.get('description', 'N/A')}",
        "",
        f"**Error Message:**",
        "```",
        bug.get("error_message", "N/A"),
        "```",
        "",
        "---",
        "",
        "## 2. Root Cause",
        "",
    ]

    rc = root_cause_data
    if rc:
        lines += [
            f"**Root Cause:** {rc.get('root_cause', 'N/A')}",
            "",
            f"**Explanation:** {rc.get('explanation', 'N/A')}",
            "",
            "**Evidence:**",
        ]
        for ev in rc.get("evidence", []):
            lines.append(f"- {ev}")
        lines.append("")
        lines += [
            f"**Failure Location:** `{rc.get('failure_location', 'N/A')}`",
            "",
            "**Affected Files:**",
        ]
        for af in rc.get("affected_files", []):
            lines.append(f"- `{af}`")
    else:
        lines.append("_Root cause analysis not yet completed._")

    lines += [
        "",
        "---",
        "",
        "## 3. Agent Analysis",
        "",
    ]

    # Code Explorer
    ce = agents.get("code_explorer", {})
    if ce.get("status") == "done":
        lines += [
            "### Code Explorer Agent",
            f"- **Files inspected:** {len(ce.get('result', {}).get('relevant_files', []))}",
            f"- **Relevant functions:** {', '.join(ce.get('result', {}).get('relevant_functions', [])[:5]) or 'N/A'}",
            f"- **Summary:** {ce.get('result', {}).get('analysis_summary', 'N/A')}",
            "",
        ]

    # Error Analyzer
    ea = agents.get("error_analyzer", {})
    if ea.get("status") == "done":
        lines += [
            "### Error Analysis Agent",
            f"- **Error type:** `{ea.get('result', {}).get('error_type', 'N/A')}`",
            f"- **Failure location:** `{ea.get('result', {}).get('failure_location', 'N/A')}`",
            f"- **Summary:** {ea.get('result', {}).get('analysis_summary', 'N/A')}",
            "",
        ]

    # Test Analyzer
    ta = agents.get("test_analyzer", {})
    if ta.get("status") == "done":
        lines += [
            "### Test Analysis Agent",
            f"- **Existing coverage:** {ta.get('result', {}).get('existing_coverage', 'N/A')}",
            f"- **Missing coverage:** {ta.get('result', {}).get('missing_coverage', 'N/A')}",
            f"- **Proposed test:** `{ta.get('result', {}).get('test_file', 'N/A')}`",
            "",
        ]

    lines += [
        "---",
        "",
        "## 4. Changes Made",
        "",
    ]

    if changes:
        for ch in changes:
            lines += [
                f"### `{ch.get('file', 'unknown')}`",
                "",
                "**Before:**",
                "```python",
                ch.get("before", ""),
                "```",
                "",
                "**After:**",
                "```python",
                ch.get("after", ""),
                "```",
                "",
                f"*Reason: {ch.get('reason', 'Bug fix')}*",
                "",
            ]
    else:
        lines.append("_No file changes recorded._")
        lines.append("")

    lines += [
        "---",
        "",
        "## 5. Tests",
        "",
    ]

    before_tests = tests.get("before", {})
    after_tests  = tests.get("after", {})
    comparison   = tests.get("comparison", {})

    if before_tests or after_tests:
        lines += [
            "| Metric | Before Fix | After Fix |",
            "|--------|-----------|-----------|",
            f"| Passed | {before_tests.get('passed', '?')} | {after_tests.get('passed', '?')} |",
            f"| Failed | {before_tests.get('failed', '?')} | {after_tests.get('failed', '?')} |",
            f"| Total  | {before_tests.get('total', '?')} | {after_tests.get('total', '?')} |",
            f"| Duration | {before_tests.get('duration', '?')}s | {after_tests.get('duration', '?')}s |",
            "",
        ]

        if comparison.get("fixed"):
            lines.append("**Tests Fixed (now passing):**")
            for t in comparison["fixed"]:
                lines.append(f"- ✅ `{t}`")
            lines.append("")

        if comparison.get("regressions"):
            lines.append("**⚠️ Regressions Detected:**")
            for t in comparison["regressions"]:
                lines.append(f"- ❌ `{t}`")
            lines.append("")
    else:
        lines.append("_Test data not available._")
        lines.append("")

    # Regression test
    proposed = ta.get("result", {}).get("proposed_test", "") if ta else ""
    if proposed:
        lines += [
            "**Regression Test Added:**",
            "```python",
            proposed,
            "```",
            "",
        ]

    lines += [
        "---",
        "",
        "## 6. Verification",
        "",
    ]

    if verify:
        verdict = "✅ **VERIFIED**" if verify.get("verified") else "❌ **NOT VERIFIED**"
        lines += [
            f"**Result:** {verdict}",
            "",
            f"**Summary:** {verify.get('summary', 'N/A')}",
            "",
        ]
        if verify.get("regressions"):
            lines.append("**Regressions:**")
            for r in verify["regressions"]:
                lines.append(f"- {r}")
        if verify.get("risks"):
            lines.append("")
            lines.append("**Remaining Risks:**")
            for r in verify["risks"]:
                lines.append(f"- {r}")
    else:
        lines.append("_Verification not yet completed._")

    lines += [
        "",
        "---",
        "",
        "## 7. Metrics",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Files Inspected | {metrics.get('files_inspected', 'N/A')} |",
        f"| Files Changed | {metrics.get('files_changed', 'N/A')} |",
        f"| Agents Used | {metrics.get('agents_used', 'N/A')} |",
        f"| Tests Executed | {metrics.get('tests_executed', 'N/A')} |",
        f"| Processing Time | {metrics.get('total_time_seconds', 'N/A')}s |",
        f"| Baseline Manual Time | {metrics.get('baseline_manual_minutes', 'N/A')} min |",
        f"| Bug2Fix Time | {metrics.get('bug2fix_minutes', 'N/A')} min |",
        f"| Time Saved | {metrics.get('time_saved_minutes', 'N/A')} min |",
        "",
        "---",
        "",
        "## 8. Recommended Next Steps",
        "",
    ]

    next_steps = fix_data.get("recommended_next_steps", []) if fix_data else []
    if not next_steps:
        next_steps = [
            "Review the proposed fix carefully before merging.",
            "Run the full test suite in CI/CD.",
            "Add edge-case tests for similar inputs.",
            "Update API documentation if public behaviour changed.",
        ]

    for step in next_steps:
        lines.append(f"- {step}")

    lines += [
        "",
        "---",
        "",
        "*Report generated by **Bug2Fix AI** — IBM Bob 2.0 Hackathon Project*",
        "",
    ]

    return "\n".join(lines)


def save_report(report_text: str, run_id: str, output_dir: str = "reports") -> str:
    """Save the report to a file and return the file path."""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    filename = path / f"bug2fix_report_{run_id}.md"
    filename.write_text(report_text, encoding="utf-8")
    return str(filename)
