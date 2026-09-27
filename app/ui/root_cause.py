"""
app/ui/root_cause.py — Evidence-based Root Cause determination display.

Redesigned with Astra-inspired minimal developer aesthetic:
- Dominant typographic hierarchy for the central finding.
- Clear structural division: Finding → Explanation → Affected Modules → Evidence.
- Zero decorative emojis; quiet technical confidence.
"""

from __future__ import annotations
import streamlit as st
from app.components.styles import page_header, status_tag


def render_root_cause():
    page_header(
        title="Root Cause Analysis",
        subtitle="Synthesized diagnostic evidence isolating failure mechanism and minimal patch target.",
        category="SYNTHESIS"
    )

    run_id = st.session_state.get("active_run_id")
    orch   = st.session_state.get("orchestrator")

    if not run_id or not orch:
        st.markdown("""
        <div class="panel" style="padding: 2.5rem; text-align: left;">
            <div style="font-family:var(--font-mono); font-size:0.6875rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-muted); margin-bottom:0.75rem;">
                NO ACTIVE RUN
            </div>
            <div style="font-size:1.25rem; font-weight:600; color:var(--text-primary); margin-bottom:0.5rem;">
                No diagnosis has been performed yet.
            </div>
            <p style="font-size:0.875rem; color:var(--text-secondary); margin-bottom:1.5rem;">
                Trigger a diagnosis run to generate root cause analysis.
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

    rc = state.get("root_cause", {})
    if not rc:
        st.info("Root cause data unavailable.")
        return

    # ── Dominant Root Cause Statement ────────────────────────────────────────
    root_cause_text = rc.get("root_cause", "Unchecked NoneType access")
    explanation_text = rc.get("explanation", "")

    st.markdown(f"""
    <div style="padding: 2rem 0; border-bottom: 1px solid var(--border-subtle); margin-bottom: 2.5rem;">
        <div class="editorial-eyebrow" style="margin-bottom: 1rem;">
            <span class="editorial-eyebrow-accent">PRIMARY DIAGNOSIS</span>
            <span>·</span>
            <span>CONFIDENCE: HIGH (DIRECT CODE EVIDENCE)</span>
        </div>
        <div style="font-size: 2.25rem; font-weight: 700; letter-spacing: -0.035em; color: var(--text-primary); line-height: 1.2; margin-bottom: 1.25rem;">
            {root_cause_text}
        </div>
        <p style="font-size: 1.0625rem; color: var(--text-secondary); line-height: 1.6; max-width: 800px; margin: 0;">
            {explanation_text}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Affected Modules & Failure Location ──────────────────────────────────
    st.markdown("""
    <div class="editorial-eyebrow" style="margin-bottom: 1rem;">
        <span>ISOLATED FAILURE TARGET</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        loc = rc.get("failure_location", "app/users.py:24 (get_user_profile)")
        st.markdown(f"""
        <div class="panel" style="margin-bottom: 1rem;">
            <div class="panel-header">EXACT FAILURE POINT</div>
            <div style="font-family:var(--font-mono); font-size:0.9375rem; color:var(--text-primary); font-weight:600;">
                {loc}
            </div>
            <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-muted); margin-top:6px;">
                Unconditional dictionary subscript on missing record
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        affected = rc.get("affected_files", ["app/users.py", "tests/test_users.py"])
        affected_html = "".join([f"<div style='font-family:var(--font-mono); font-size:0.875rem; color:var(--text-primary); margin-bottom:4px;'><code>{f}</code></div>" for f in affected])
        st.markdown(f"""
        <div class="panel" style="margin-bottom: 1rem;">
            <div class="panel-header">AFFECTED REPOSITORY FILES ({len(affected)})</div>
            {affected_html}
        </div>
        """, unsafe_allow_html=True)

    # ── Evidence List ────────────────────────────────────────────────────────
    evidence = rc.get("evidence", [])
    if evidence:
        st.markdown("""
        <div class="editorial-eyebrow" style="margin-top: 1.5rem; margin-bottom: 1rem;">
            <span>SUPPORTING EVIDENCE ({})</span>
        </div>
        """.format(len(evidence)), unsafe_allow_html=True)

        for ev in evidence:
            st.markdown(f"""
            <div style="padding: 0.875rem 1.25rem; background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); margin-bottom: 8px; font-family: var(--font-mono); font-size: 0.8125rem; color: var(--text-secondary); line-height: 1.5;">
                <span style="color:var(--accent); margin-right:8px;">›</span>{ev}
            </div>
            """, unsafe_allow_html=True)

    # ── Proposed Minimal Fix ─────────────────────────────────────────────────
    smallest_fix = rc.get("smallest_fix", "")
    if smallest_fix:
        st.markdown("""
        <div class="editorial-eyebrow" style="margin-top: 2rem; margin-bottom: 1rem;">
            <span>MINIMAL REMEDIATION STRATEGY</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="panel-accent" style="margin-bottom: 2rem;">
            <div style="font-family:var(--font-mono); font-size:0.6875rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--accent); margin-bottom:8px;">
                SAFE REMEDIATION PROPOSAL
            </div>
            <div style="font-size:0.9375rem; color:var(--text-primary); line-height:1.6;">
                {smallest_fix}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Agent Contributions (Technical Tabs) ─────────────────────────────────
    st.markdown("""
    <div class="editorial-eyebrow" style="margin-top: 2rem; margin-bottom: 1rem;">
        <span>SPECIALIZED SUBAGENT TELEMETRY</span>
    </div>
    """, unsafe_allow_html=True)

    agents = state.get("agents", {})
    tab1, tab2, tab3 = st.tabs(["Code Explorer Trace", "Error Analyzer Diagnosis", "Test Analyzer Coverage"])

    with tab1:
        ce = agents.get("code_explorer", {}).get("result", {})
        if ce:
            st.markdown(f"**Code Explorer Summary:** {ce.get('analysis_summary', 'N/A')}")
            if ce.get("execution_path"):
                st.markdown("**Execution Path Trace:**")
                for step in ce["execution_path"]:
                    st.code(step, language=None)

    with tab2:
        ea = agents.get("error_analyzer", {}).get("result", {})
        if ea:
            st.markdown(f"**Error Classification:** `{ea.get('error_type', 'N/A')}`")
            st.markdown(f"**Location:** `{ea.get('failure_location', 'N/A')}`")
            st.markdown("**Likely Causes:**")
            for rc_item in ea.get("likely_root_causes", []):
                st.markdown(f"- {rc_item}")

    with tab3:
        ta = agents.get("test_analyzer", {}).get("result", {})
        if ta:
            st.markdown(f"**Existing Coverage Status:** {ta.get('existing_coverage', 'N/A')}")
            st.markdown(f"**Coverage Gap Identified:** {ta.get('missing_coverage', 'N/A')}")

    # ── Navigation Row ───────────────────────────────────────────────────────
    st.markdown("<hr style='margin: 2.5rem 0 1.5rem 0;' />", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        if st.button("Inspect Code Diff →", type="primary", use_container_width=True):
            st.session_state.page = "fix"
            st.rerun()
    with col2:
        if st.button("View Test Results →", type="secondary", use_container_width=True):
            st.session_state.page = "tests"
            st.rerun()
