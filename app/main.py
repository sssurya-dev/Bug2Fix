"""
app/main.py — Bug2Fix AI application entry point.

Clean top bar with wordmark, target project, run status, and mode badge.
Editorial top navigation bar with clean typographic tabs.
Full state management and robust page routing.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Bug2Fix AI — Evidence-First Debugging",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from app.ui.dashboard    import render_dashboard
from app.ui.diagnose     import render_diagnose
from app.ui.workflow     import render_workflow
from app.ui.root_cause   import render_root_cause
from app.ui.fix          import render_fix
from app.ui.tests_view   import render_tests
from app.ui.evidence     import render_evidence
from app.ui.report       import render_report
from app.components.styles import inject_styles, status_tag

# Inject global design system
inject_styles()


# ── Top Bar & Navigation Component ─────────────────────────────────────────
def render_top_bar():
    """Render the persistent technical top bar and clean navigation tabs."""
    from core.bob_execution_adapter import BOB_AVAILABLE

    run_id = st.session_state.get("active_run_id")
    orch = st.session_state.get("orchestrator")
    state = orch.get_state(run_id) if (orch and run_id) else None

    # Project name
    project_label = "python_bug_demo"
    if state and state.get("project"):
        p = state.get("project")
        project_label = Path(p).name or p

    # Run status
    run_status = state.get("status", "IDLE").upper() if state else "READY"
    status_class = "complete" if run_status == "DONE" else ("running" if run_status == "RUNNING" else "queued")

    # Final status (the authoritative signal)
    final_status = state.get("final_status", "") if state else ""
    if final_status == "VERIFIED_WITH_EVIDENCE":
        status_class = "complete"
        run_status   = "VERIFIED"

    # Mode label
    mode_tag = '<span class="status-tag pass">BOB LIVE</span>' if BOB_AVAILABLE else '<span class="status-tag demo">DEMO MODE</span>'

    run_id_display = f"#{run_id[-8:]}" if run_id else "NO ACTIVE RUN"

    st.markdown(f"""
    <div class="top-bar-container">
        <div class="brand-mark">
            <span class="dot"></span>
            <span>BUG2FIX</span>
            <span style="color:var(--text-muted);font-weight:400;margin-left:8px;">/</span>
            <span style="color:var(--text-secondary);font-size:0.8125rem;font-weight:400;">{project_label}</span>
        </div>
        <div class="top-bar-meta">
            <div>RUN: <span style="color:var(--text-primary);">{run_id_display}</span></div>
            <div>STATUS: <span class="status-tag {status_class}">{run_status}</span></div>
            <div>{mode_tag}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Top Navigation Tabs ──
    nav_items = [
        ("Overview",   "dashboard"),
        ("Diagnose",   "diagnose"),
        ("Workflow",   "workflow"),
        ("Root Cause", "root_cause"),
        ("Fix",        "fix"),
        ("Tests",      "tests"),
        ("Evidence",   "evidence"),
        ("Report",     "report"),
    ]

    current_page = st.session_state.get("page", "dashboard")

    cols = st.columns(len(nav_items))
    for idx, (label, key) in enumerate(nav_items):
        with cols[idx]:
            is_active = (current_page == key)
            btn_kind = "primary" if is_active else "secondary"
            if st.button(label, key=f"topnav_{key}", type=btn_kind, use_container_width=True):
                st.session_state.page = key
                st.rerun()

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)


# ── Minimal Sidebar ────────────────────────────────────────────────────────
def render_sidebar():
    """Minimal sidebar for secondary navigation and environment metadata."""
    from core.bob_execution_adapter import BOB_AVAILABLE, BOB_EXECUTABLE

    with st.sidebar:
        st.markdown("""
        <div style="padding: 1.5rem 0.5rem 1rem 0.5rem;">
            <div style="font-family:var(--font-mono);font-size:0.875rem;font-weight:700;letter-spacing:0.08em;color:var(--text-primary);">
                BUG2FIX AI
            </div>
            <div style="font-size:0.75rem;color:var(--text-muted);margin-top:4px;">
                IBM Bob 2.0 Agent Laboratory
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='margin: 0.5rem 0 1.25rem 0;' />", unsafe_allow_html=True)

        pages = {
            "Overview":   "dashboard",
            "Diagnose":   "diagnose",
            "Workflow":   "workflow",
            "Root Cause": "root_cause",
            "Fix":        "fix",
            "Tests":      "tests",
            "Evidence":   "evidence",
            "Report":     "report",
        }

        if "page" not in st.session_state:
            st.session_state.page = "dashboard"

        for label, key in pages.items():
            is_active = st.session_state.page == key
            prefix = "› " if is_active else "  "
            if st.button(f"{prefix}{label}", key=f"side_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

        st.markdown("<hr style='margin: 1.5rem 0 1rem 0;' />", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="padding: 0.5rem; font-family:var(--font-mono); font-size:0.6875rem; color:var(--text-muted); line-height: 1.7;">
            <div>RUNTIME: Python 3.13</div>
            <div>ORCHESTRATOR: Bob v2.0</div>
            <div>ADAPTER: {'Live CLI' if BOB_AVAILABLE else 'Pre-computed Sample'}</div>
            <div style="margin-top:0.75rem;color:var(--text-secondary);">
                Press [R] to reload UI
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Main Application Router ────────────────────────────────────────────────
def main():
    render_sidebar()
    render_top_bar()

    page = st.session_state.get("page", "dashboard")

    if page == "dashboard":
        render_dashboard()
    elif page == "diagnose":
        render_diagnose()
    elif page == "workflow":
        render_workflow()
    elif page == "root_cause":
        render_root_cause()
    elif page == "fix":
        render_fix()
    elif page == "tests":
        render_tests()
    elif page == "evidence":
        render_evidence()
    elif page == "report":
        render_report()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
