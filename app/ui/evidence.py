"""
app/ui/evidence.py — Evidence Ledger view.

Shows the complete objective evidence record for the current run:
- Input artifacts
- Reproduction gate result
- Root cause evidence chain
- Scope validation
- Verification gate (all 5 checks)
- Timeline
- Final status
"""

from __future__ import annotations
import json
import streamlit as st
from app.components.styles import page_header, status_tag


def _gate_tag(value: str) -> str:
    """Render a verification gate entry as a status tag."""
    v = value.upper()
    if v == "PASS":
        return '<span class="status-tag complete">PASS</span>'
    elif v == "FAIL":
        return '<span class="status-tag failed">FAIL</span>'
    elif v == "BLOCKED":
        return '<span class="status-tag failed">BLOCKED</span>'
    else:
        return '<span class="status-tag queued">UNKNOWN</span>'


def _final_status_banner(final_status: str) -> str:
    label_map = {
        "VERIFIED_WITH_EVIDENCE": ("VERIFIED WITH EVIDENCE", "complete"),
        "VERIFICATION_FAILED":    ("VERIFICATION FAILED",    "failed"),
        "INVESTIGATING":          ("INVESTIGATING",           "running"),
        "FIX_GENERATED":          ("FIX GENERATED",          "active"),
        "VERIFICATION_RUNNING":   ("VERIFICATION RUNNING",   "running"),
        "BLOCKED":                ("BLOCKED",                 "failed"),
    }
    label, css = label_map.get(final_status, (final_status, "queued"))

    # Special treatment for the crown jewel
    if final_status == "VERIFIED_WITH_EVIDENCE":
        return f"""
        <div style="background:var(--success-bg); border:1px solid var(--success-border);
                    border-radius:var(--radius-md); padding:1.75rem 2rem; margin-bottom:2rem;
                    display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-family:var(--font-mono); font-size:0.75rem;
                            text-transform:uppercase; letter-spacing:0.1em;
                            color:var(--success); margin-bottom:6px;">
                    EVIDENCE LEDGER · FINAL VERDICT
                </div>
                <div style="font-size:1.875rem; font-weight:700; color:var(--success);
                            letter-spacing:-0.02em; line-height:1.1;">
                    ✓ VERIFIED WITH EVIDENCE
                </div>
                <div style="font-size:0.875rem; color:var(--text-secondary); margin-top:6px;">
                    All 5 verification gate checks passed. Fix is proven correct.
                </div>
            </div>
        </div>
        """
    else:
        return f"""
        <div class="panel" style="margin-bottom:2rem;">
            <div class="panel-header">EVIDENCE LEDGER · FINAL VERDICT</div>
            <span class="status-tag {css}" style="font-size:0.875rem; padding:6px 12px;">{label}</span>
        </div>
        """


def render_evidence():
    page_header(
        title="Evidence Ledger",
        subtitle="Objective, tamper-evident record of every artifact produced during this debugging run.",
        category="EVIDENCE"
    )

    run_id = st.session_state.get("active_run_id")
    orch   = st.session_state.get("orchestrator")

    if not run_id or not orch:
        st.markdown("""
        <div class="panel" style="padding: 2.5rem;">
            <div class="panel-header">NO EVIDENCE RECORD</div>
            <div style="font-size:1.25rem; font-weight:600; color:var(--text-primary); margin-bottom:0.5rem;">
                No active debugging run.
            </div>
            <p style="font-size:0.875rem; color:var(--text-secondary);">
                Complete a diagnosis to generate an objective evidence ledger.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Diagnose →", type="primary"):
            st.session_state.page = "diagnose"
            st.rerun()
        return

    state = orch.get_state(run_id)
    if not state or state.get("status") != "done":
        st.warning("Analysis in progress or incomplete.")
        return

    evidence = state.get("evidence", {})
    if not evidence:
        st.info("Evidence ledger not available for this run.")
        return

    final_status = evidence.get("final_status", "INVESTIGATING")

    # ── Final Status Banner ──────────────────────────────────────────────────
    st.markdown(_final_status_banner(final_status), unsafe_allow_html=True)

    # ── Verification Gate ────────────────────────────────────────────────────
    gate = evidence.get("verification_gate", {})
    st.markdown("""
    <div class="editorial-eyebrow" style="margin-bottom:1rem;">
        <span>VERIFICATION GATE — ALL 5 CHECKS REQUIRED FOR PASS</span>
    </div>
    """, unsafe_allow_html=True)

    gate_items = [
        ("regression_test_passes",  "Regression test passes after fix"),
        ("relevant_tests_pass",     "All relevant tests pass"),
        ("full_suite_passes",       "Full test suite passes (no new failures)"),
        ("no_unexpected_files",     "No unexpected files changed (scope clean)"),
        ("diff_consistent",         "Diff is consistent with requested fix"),
    ]

    gate_rows = ""
    for key, label in gate_items:
        val = gate.get(key, "UNKNOWN")
        gate_rows += f"""
        <div class="agent-row-item">
            <div style="font-family:var(--font-mono); font-size:0.8125rem; color:var(--text-primary);">
                {label}
            </div>
            {_gate_tag(val)}
        </div>
        """

    overall_tag = _gate_tag(gate.get("overall", "UNKNOWN"))
    st.markdown(f"""
    <div class="agent-console">
        <div class="agent-console-header">
            <span>CHECK</span>
            <span>RESULT</span>
        </div>
        {gate_rows}
        <div class="agent-row-item" style="background:var(--bg-elevated);">
            <div style="font-family:var(--font-mono); font-size:0.8125rem; font-weight:600;
                        color:var(--text-primary);">OVERALL GATE</div>
            {overall_tag}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Three-column evidence cards ──────────────────────────────────────────
    st.markdown("""
    <div class="editorial-eyebrow" style="margin-top:2rem; margin-bottom:1rem;">
        <span>EVIDENCE ARTIFACTS</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # Reproduction gate card
    with col1:
        repro_status = evidence.get("reproduction_result", "UNKNOWN")
        baseline     = evidence.get("baseline_test_status", "UNKNOWN")
        tests_before = evidence.get("tests_before", {})
        repro_color  = "var(--success)" if repro_status == "CONFIRMED_FAILING" else "var(--error)"
        st.markdown(f"""
        <div class="panel">
            <div class="panel-header">REPRODUCTION GATE</div>
            <div style="font-size:1.5rem; font-weight:700; color:{repro_color};
                        letter-spacing:-0.02em; margin-bottom:8px;">
                {'❌ BUG CONFIRMED' if repro_status == 'CONFIRMED_FAILING' else repro_status}
            </div>
            <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-muted);">
                Baseline: {tests_before.get('passed', 0)} passed /
                {tests_before.get('failed', 0)} failed
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Scope guard card
    with col2:
        scope_status = evidence.get("scope_status", "UNCHECKED")
        expected     = evidence.get("expected_files_to_change", [])
        actual       = evidence.get("actual_files_changed", [])
        unexpected   = evidence.get("unexpected_files", [])
        scope_color  = "var(--success)" if scope_status == "CLEAN" else "var(--warning)"
        scope_icon   = "✓ CLEAN" if scope_status == "CLEAN" else "⚠ SCOPE CHANGE"
        st.markdown(f"""
        <div class="panel">
            <div class="panel-header">SCOPE VALIDATION</div>
            <div style="font-size:1.125rem; font-weight:700; color:{scope_color};
                        letter-spacing:-0.02em; margin-bottom:8px;">
                {scope_icon}
            </div>
            <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-muted);">
                Expected: {len(expected)} file(s)<br>
                Actual: {len(actual)} file(s)<br>
                {'Unexpected: ' + str(unexpected) if unexpected else 'No unexpected changes'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Fix outcome card
    with col3:
        tests_after    = evidence.get("tests_after", {})
        regressions    = evidence.get("regressions_detected", [])
        tests_fixed    = evidence.get("tests_fixed", [])
        outcome_color  = "var(--success)" if not regressions and tests_after.get("failed", 1) == 0 else "var(--error)"
        st.markdown(f"""
        <div class="panel">
            <div class="panel-header">FIX OUTCOME</div>
            <div style="font-size:1.5rem; font-weight:700; color:{outcome_color};
                        letter-spacing:-0.02em; margin-bottom:8px;">
                {'✓ ALL PASS' if tests_after.get('failed', 1) == 0 else '✗ FAILURES'}
            </div>
            <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-muted);">
                After: {tests_after.get('passed', 0)} passed /
                {tests_after.get('failed', 0)} failed<br>
                Fixed: {len(tests_fixed)} test(s)<br>
                Regressions: {len(regressions)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Root Cause Evidence Chain ────────────────────────────────────────────
    rc_evidence = evidence.get("root_cause_evidence", [])
    if rc_evidence:
        st.markdown("""
        <div class="editorial-eyebrow" style="margin-top:2rem; margin-bottom:1rem;">
            <span>ROOT CAUSE EVIDENCE CHAIN</span>
        </div>
        """, unsafe_allow_html=True)
        for i, ev in enumerate(rc_evidence, 1):
            st.markdown(f"""
            <div style="display:flex; gap:12px; padding:0.75rem 1rem; background:var(--bg-surface);
                        border:1px solid var(--border-subtle); border-radius:var(--radius-sm);
                        margin-bottom:6px; font-family:var(--font-mono); font-size:0.8125rem;
                        color:var(--text-secondary);">
                <span style="color:var(--accent); min-width:20px;">{i:02d}</span>
                <span>{ev}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Timeline ─────────────────────────────────────────────────────────────
    timeline = evidence.get("timeline", [])
    if timeline:
        st.markdown("""
        <div class="editorial-eyebrow" style="margin-top:2rem; margin-bottom:1rem;">
            <span>RUN TIMELINE</span>
        </div>
        """, unsafe_allow_html=True)

        timeline_rows = ""
        for entry in timeline:
            ts = entry.get("timestamp", "")[:19].replace("T", " ")
            ev = entry.get("event", "")
            de = entry.get("detail", "")
            timeline_rows += f"""
            <div class="agent-row-item">
                <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-muted); min-width:160px;">
                    {ts}
                </div>
                <div style="font-family:var(--font-mono); font-size:0.8125rem; font-weight:600;
                            color:var(--accent); min-width:200px;">
                    {ev}
                </div>
                <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-secondary);">
                    {de}
                </div>
            </div>
            """

        st.markdown(f"""
        <div class="agent-console">
            <div class="agent-console-header">
                <span>TIMESTAMP</span>
                <span>EVENT</span>
                <span>DETAIL</span>
            </div>
            {timeline_rows}
        </div>
        """, unsafe_allow_html=True)

    # ── Diff Summary ─────────────────────────────────────────────────────────
    diff_text    = evidence.get("diff_text", "")
    diff_summary = evidence.get("diff_summary", "")
    if diff_text or diff_summary:
        st.markdown("""
        <div class="editorial-eyebrow" style="margin-top:2rem; margin-bottom:1rem;">
            <span>PATCH SUMMARY</span>
        </div>
        """, unsafe_allow_html=True)
        if diff_summary:
            st.markdown(f"""
            <div class="panel" style="margin-bottom:1rem;">
                <div class="panel-header">CHANGE SCOPE</div>
                <div style="font-family:var(--font-mono); font-size:0.875rem; color:var(--text-primary);">
                    {diff_summary}
                </div>
            </div>
            """, unsafe_allow_html=True)
        if diff_text:
            with st.expander("View raw git diff"):
                st.code(diff_text, language="diff")

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("<hr style='margin:2rem 0;' />", unsafe_allow_html=True)
    try:
        evidence_json = json.dumps(evidence, indent=2, default=str)
    except Exception:
        evidence_json = "{}"

    col1, col2 = st.columns([2, 5])
    with col1:
        st.download_button(
            label="Download Evidence Ledger (.json)",
            data=evidence_json,
            file_name=f"evidence_{run_id}.json",
            mime="application/json",
            use_container_width=True,
        )
    with col2:
        if st.button("View Final Report →", type="primary", use_container_width=True):
            st.session_state.page = "report"
            st.rerun()
