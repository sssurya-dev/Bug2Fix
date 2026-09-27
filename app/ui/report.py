"""
app/ui/report.py — Final debugging report and artifact export view.

Redesigned with Astra-inspired minimal developer aesthetic:
- Formatted as an editorial technical specification document.
- Minimal, large typography impact metrics.
- Clean technical comparison table and one-click Markdown/JSON exports.
"""

from __future__ import annotations
import json
import streamlit as st
from app.components.styles import page_header, status_tag


def render_report():
    page_header(
        title="Final Debugging Report",
        subtitle="Formal remediation record, evidence synthesis, and verification telemetry.",
        category="SPECIFICATION"
    )

    run_id = st.session_state.get("active_run_id")
    orch   = st.session_state.get("orchestrator")

    if not run_id or not orch:
        st.markdown("""
        <div class="panel" style="padding: 2.5rem; text-align: left;">
            <div style="font-family:var(--font-mono); font-size:0.6875rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-muted); margin-bottom:0.75rem;">
                NO REPORT GENERATED
            </div>
            <div style="font-size:1.25rem; font-weight:600; color:var(--text-primary); margin-bottom:0.5rem;">
                No report available.
            </div>
            <p style="font-size:0.875rem; color:var(--text-secondary); margin-bottom:1.5rem;">
                Complete an automated diagnosis to compile a full engineering specification.
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

    report_text = state.get("report", "")
    metrics     = state.get("metrics", {})
    verify      = state.get("verification", {})

    # ── Executive Impact Telemetry ───────────────────────────────────────────
    baseline = metrics.get("baseline_manual_minutes", 25)
    b2f_time = metrics.get("bug2fix_minutes", 0.02)
    saved    = metrics.get("time_saved_minutes", 25.0)
    pct      = round((saved / baseline) * 100) if baseline else 95

    st.markdown(f"""
    <div class="panel" style="padding: 2rem; margin-bottom: 2.5rem;">
        <div class="editorial-eyebrow" style="margin-bottom: 1.25rem;">
            <span>ENGINEERING TIME IMPACT ANALYSIS</span>
        </div>
        <div style="display: flex; gap: 3rem; flex-wrap: wrap; align-items: baseline;">
            <div>
                <div style="font-family:var(--font-mono); font-size:0.6875rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;">
                    MANUAL TRIAGE BASELINE
                </div>
                <div style="font-size: 2.5rem; font-weight: 700; color: var(--text-muted); line-height: 1;">
                    {baseline} <span style="font-size:1rem; font-weight:400;">min</span>
                </div>
            </div>
            <div style="font-size: 1.5rem; color: var(--border-subtle); align-self: center;">→</div>
            <div>
                <div style="font-family:var(--font-mono); font-size:0.6875rem; color:var(--accent); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;">
                    BUG2FIX AUTOMATION
                </div>
                <div style="font-size: 2.5rem; font-weight: 700; color: var(--accent); line-height: 1;">
                    {metrics.get('total_time_seconds', 1.3):.1f} <span style="font-size:1rem; font-weight:400;">sec</span>
                </div>
            </div>
            <div style="font-size: 1.5rem; color: var(--border-subtle); align-self: center;">→</div>
            <div>
                <div style="font-family:var(--font-mono); font-size:0.6875rem; color:var(--success); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;">
                    NET EFFORT RECLAIMED
                </div>
                <div style="font-size: 2.5rem; font-weight: 700; color: var(--success); line-height: 1;">
                    {pct}% <span style="font-size:1rem; font-weight:400; color:var(--text-secondary);">({saved:.1f} min saved)</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Export Controls ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="editorial-eyebrow" style="margin-bottom: 0.75rem;">
        <span>EXPORTABLE ARTIFACTS</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download Markdown Specification (.md)",
            data=report_text,
            file_name=f"bug2fix_report_{run_id}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col2:
        export_state = {k: v for k, v in state.items() if k != "report"}
        try:
            state_json = json.dumps(export_state, indent=2, default=str)
        except Exception:
            state_json = "{}"
        st.download_button(
            label="Download Session JSON State (.json)",
            data=state_json,
            file_name=f"bug2fix_state_{run_id}.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("<hr style='margin: 2rem 0;' />", unsafe_allow_html=True)

    # ── Full Specification Document ──────────────────────────────────────────
    st.markdown("""
    <div class="editorial-eyebrow" style="margin-bottom: 1rem;">
        <span>DOCUMENTATION AGENT SPECIFICATION EXCERPT</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:var(--radius-md); padding:2rem; line-height:1.7;">
    """, unsafe_allow_html=True)

    st.markdown(report_text)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Comparison Matrix ────────────────────────────────────────────────────
    st.markdown("""
    <div class="editorial-eyebrow" style="margin-top: 2.5rem; margin-bottom: 1rem;">
        <span>DEVELOPER WORKFLOW EFFICIENCY MATRIX</span>
    </div>
    """, unsafe_allow_html=True)

    # Use actual measured time from the run
    actual_seconds = metrics.get("total_time_seconds", 0)
    actual_str = f"{actual_seconds:.1f}s" if actual_seconds < 60 else f"{actual_seconds/60:.1f} min"
    baseline_min = metrics.get("baseline_manual_minutes", 25)

    st.markdown(f"""
    | Operational Stage | Manual Process | Bug2Fix AI Orchestration |
    | :--- | :--- | :--- |
    | Incident comprehension | ~5 min reading | Document processor — instant |
    | Call graph / codebase search | ~10 min search | AST Code Explorer |
    | Stack trace isolation | ~3 min inspection | Error Analyzer |
    | Test gap identification | ~3 min review | Test Analyzer |
    | Root cause determination | ~5 min hypotheses | Evidence synthesis |
    | Source fix application | ~5 min editing | Targeted safe patch |
    | Verification test run | ~2 min CLI | Automated pytest suite |
    | Specification documentation | ~5 min writeup | Automated report |
    | **Cumulative Duration** | **~{baseline_min} min (MANUAL BASELINE)** | **{actual_str} (MEASURED)** |
    """)
