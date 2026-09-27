"""
app/ui/workflow.py — Agent Workflow and execution monitoring page.

Redesigned with Astra-inspired minimal developer aesthetic:
- Clean technical pipeline topology with thin lines and monospace details.
- Parallel worker visualizer with crisp status indicators.
- Developer console-style agent activity log with zero decorative emojis.
"""

from __future__ import annotations
import streamlit as st
from app.components.styles import page_header, status_tag


AGENTS_SPEC = [
    ("code_explorer",  "Code Explorer",   "AST traversal, symbol inspection, execution path trace"),
    ("error_analyzer", "Error Analyzer",  "Stack trace parsing, failure point isolation, error categorization"),
    ("test_analyzer",  "Test Analyzer",   "Test suite coverage evaluation, regression reproduction synthesis"),
    ("root_cause",     "Root Cause",      "Multi-agent evidence synthesis, minimal failure point identification"),
    ("fix_agent",      "Fix Agent",       "Targeted safe source patch application with before/after diff"),
    ("verifier",       "Verifier",        "pytest regression test execution and zero-regression assertion"),
    ("documentation",  "Documentation",   "Comprehensive markdown debugging specification generation"),
]


def render_workflow():
    page_header(
        title="Agent Workflow",
        subtitle="Real-time orchestration pipeline and execution trace across specialized IBM Bob agents.",
        category="ORCHESTRATION"
    )

    run_id = st.session_state.get("active_run_id")
    orch   = st.session_state.get("orchestrator")

    if not run_id or not orch:
        st.markdown("""
        <div class="panel" style="padding: 2.5rem; text-align: left;">
            <div style="font-family:var(--font-mono); font-size:0.6875rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-muted); margin-bottom:0.75rem;">
                NO ACTIVE PIPELINE
            </div>
            <div style="font-size:1.25rem; font-weight:600; color:var(--text-primary); margin-bottom:0.5rem;">
                No active debugging session found.
            </div>
            <p style="font-size:0.875rem; color:var(--text-secondary); margin-bottom:1.5rem;">
                Initialize a debugging run from the Diagnose view to stream agent telemetry.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Diagnosis →", type="primary"):
            st.session_state.page = "diagnose"
            st.rerun()
        return

    state = orch.get_state(run_id)
    if not state:
        st.error("Run state unavailable.")
        return

    # ── Session Telemetry Bar ───────────────────────────────────────────────
    status = state.get("status", "unknown").upper()
    mode   = state.get("mode", "unknown").upper()
    m      = state.get("metrics", {})

    st.markdown(f"""
    <div class="metric-group" style="margin-bottom: 2rem;">
        <div class="metric-cell">
            <div class="metric-cell-label">SESSION ID</div>
            <div style="font-family:var(--font-mono); font-size:1.125rem; font-weight:600; color:var(--text-primary);">{run_id[:20]}</div>
            <div class="metric-cell-detail">Isolated execution context</div>
        </div>
        <div class="metric-cell">
            <div class="metric-cell-label">LIFECYCLE STATUS</div>
            <div style="margin-top: 4px;">{status_tag(status)}</div>
            <div class="metric-cell-detail">Completed in {m.get('total_time_seconds', 1.3):.1f}s</div>
        </div>
        <div class="metric-cell">
            <div class="metric-cell-label">EXECUTION ENGINE</div>
            <div style="font-family:var(--font-mono); font-size:1.125rem; font-weight:600; color:var(--accent);">{mode}</div>
            <div class="metric-cell-detail">Bob Orchestrator v2.0</div>
        </div>
        <div class="metric-cell">
            <div class="metric-cell-label">AGENTS DISPATCHED</div>
            <div class="metric-cell-value">7</div>
            <div class="metric-cell-detail">3 parallel · 4 sequential</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Parallel Phase Visualization ─────────────────────────────────────────
    st.markdown("""
    <div class="editorial-eyebrow" style="margin-top: 1.5rem; margin-bottom: 0.75rem;">
        <span>CONCURRENT ANALYSIS PHASE · THREAD POOL WORKERS</span>
    </div>
    """, unsafe_allow_html=True)

    parallel_keys = [
        ("code_explorer",  "Code Explorer",   "AST traversal & call graph"),
        ("error_analyzer", "Error Analyzer",  "Traceback isolation & failure point"),
        ("test_analyzer",  "Test Analyzer",   "Coverage gap & reproduction"),
    ]

    cols = st.columns(3)
    agents = state.get("agents", {})

    for idx, (key, label, desc) in enumerate(parallel_keys):
        agent_data = agents.get(key, {})
        astatus    = agent_data.get("status", "pending")
        dot_class  = "done" if astatus == "done" else ("active" if astatus == "running" else "")
        with cols[idx]:
            st.markdown(f"""
            <div class="panel" style="padding:1.25rem; border-color:var(--border-subtle);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span class="agent-indicator-dot {dot_class}"></span>
                        <span style="font-weight:600; font-size:0.875rem;">{label}</span>
                    </div>
                    {status_tag(astatus)}
                </div>
                <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-muted); line-height:1.4;">
                    {desc}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Developer Console / Agent Activity ───────────────────────────────────
    st.markdown("""
    <div class="editorial-eyebrow" style="margin-top: 2rem; margin-bottom: 0.75rem;">
        <span>AGENT ACTIVITY CONSOLE</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="agent-console">
        <div class="agent-console-header">
            <span>AGENT IDENTITY</span>
            <span>SUBROUTINE SUMMARY</span>
            <span>OUTCOME</span>
        </div>
    """, unsafe_allow_html=True)

    for key, name, desc in AGENTS_SPEC:
        agent_data = agents.get(key, {})
        astatus = agent_data.get("status", "pending")
        dot_class = "done" if astatus == "done" else ("active" if astatus == "running" else "")

        summary_text = desc
        res = agent_data.get("result", {})
        if res.get("analysis_summary"):
            summary_text = res["analysis_summary"]
        elif res.get("root_cause"):
            summary_text = res["root_cause"]
        elif res.get("explanation"):
            summary_text = res["explanation"]

        st.markdown(f"""
        <div class="agent-row-item">
            <div class="agent-row-identity" style="width: 25%;">
                <span class="agent-indicator-dot {dot_class}"></span>
                <div>
                    <div class="agent-row-title">{name}</div>
                    <div class="agent-row-desc">{key}</div>
                </div>
            </div>
            <div style="width: 60%; font-family:var(--font-mono); font-size:0.75rem; color:var(--text-secondary); line-height:1.4;">
                {summary_text[:110] + ('...' if len(summary_text) > 110 else '')}
            </div>
            <div style="width: 15%; text-align:right;">
                {status_tag(astatus)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Sequential Steps Pipeline ────────────────────────────────────────────
    st.markdown("""
    <div class="editorial-eyebrow" style="margin-top: 2rem; margin-bottom: 0.75rem;">
        <span>SEQUENTIAL VERIFICATION STAGES</span>
    </div>
    """, unsafe_allow_html=True)

    # Build steps from live state where possible
    repo = state.get("repo_analysis") or {}
    docs = state.get("documents") or []
    changes = state.get("changes") or []
    tests = state.get("tests", {})
    before = tests.get("before", {})
    after  = tests.get("after", {})
    scope  = state.get("scope", {})
    final_status = state.get("final_status", "INVESTIGATING")

    def _step_tag(cond): return "done" if cond else "pending"

    repo_detail = (
        f"{repo.get('total_files', '?')} files indexed, "
        f"{repo.get('total_functions', '?')} functions, "
        f"{repo.get('total_test_files', '?')} test files."
    ) if repo else "Pending."
    doc_detail = (
        f"{len(docs)} document(s) processed. "
        + (f"{sum(len(d.get('stack_traces', [])) for d in docs)} stack trace(s) extracted." if docs else "")
    ) if docs else "No documents loaded."
    rc = state.get("root_cause", {})
    rc_detail = rc.get("root_cause", "Pending.") if rc else "Pending."
    fix_detail = (
        f"{len(changes)} file(s) patched. Scope: {scope.get('status', 'UNCHECKED')}."
    ) if changes else "Pending."
    test_detail = (
        f"Before: {before.get('passed', 0)}/{before.get('total', 0)} passed. "
        f"After: {after.get('passed', 0)}/{after.get('total', 0)} passed. "
        f"{after.get('failed', 0)} failures."
    ) if after else "Pending."
    verify_detail = (
        f"Gate: {state.get('evidence', {}).get('verification_gate', {}).get('overall', 'UNKNOWN')}. "
        f"Final: {final_status}."
    ) if state.get("evidence") else "Pending."

    steps = [
        ("01", "Repository AST Inspection",   repo_detail,  _step_tag(bool(repo))),
        ("02", "Document Processing",          doc_detail,   _step_tag(bool(docs) or state.get("status") == "done")),
        ("03", "Concurrent Agent Analysis",    "Code Explorer, Error Analyzer, Test Analyzer dispatched in parallel.", _step_tag(agents.get("code_explorer", {}).get("status") == "done")),
        ("04", "Root Cause Determination",     rc_detail,    _step_tag(bool(rc))),
        ("05", "Targeted Patch Generation",    fix_detail,   _step_tag(bool(changes))),
        ("06", "Test Suite Verification",      test_detail,  _step_tag(bool(after))),
        ("07", "Evidence + Documentation",     verify_detail, _step_tag(bool(state.get("evidence", {}).get("finalized_at")))),
    ]

    for step_num, title, detail, st_val in steps:
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding:0.875rem 1.25rem; background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:var(--radius-sm); margin-bottom:6px;">
            <div style="display:flex; align-items:center; gap:14px;">
                <span style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-muted);">{step_num}</span>
                <div>
                    <span style="font-size:0.875rem; font-weight:600; color:var(--text-primary);">{title}</span>
                    <span style="font-size:0.75rem; color:var(--text-secondary); margin-left:12px; font-family:var(--font-mono);">{detail}</span>
                </div>
            </div>
            {status_tag(st_val)}
        </div>
        """, unsafe_allow_html=True)

    # ── Next Action ──────────────────────────────────────────────────────────
    st.markdown("<hr style='margin: 2.5rem 0 1.5rem 0;' />", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        if st.button("Inspect Root Cause →", type="primary", use_container_width=True):
            st.session_state.page = "root_cause"
            st.rerun()
    with col2:
        if st.button("View Evidence Ledger →", type="secondary", use_container_width=True):
            st.session_state.page = "evidence"
            st.rerun()
