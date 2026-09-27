"""
app/ui/diagnose.py — Incident submission and diagnosis launch page.

Redesigned with Astra-inspired minimal developer aesthetic:
- Clean technical form with restrained input surfaces and sharp hierarchy.
- Zero decorative emojis; clear section numbering and technical labels.
- Contextual step-by-step progress indicator during agent execution.
"""

from __future__ import annotations
import os
import sys
from pathlib import Path
import streamlit as st
from app.components.styles import page_header, status_tag


SAMPLE_PROJECT_PATH = str(
    Path(__file__).resolve().parent.parent.parent
    / "sample_projects" / "python_bug_demo"
)

SAMPLE_BUG = {
    "title": "Application crashes when requesting a missing user",
    "description": (
        "When a client requests a user ID that does not exist in the database, "
        "the application crashes with an unhandled TypeError instead of returning "
        "a meaningful error response. This affects all callers of get_user_profile()."
    ),
    "error_message": "TypeError: 'NoneType' object is not subscriptable",
    "stack_trace": (
        "Traceback (most recent call last):\n"
        '  File "app/main.py", line 22, in run_demo\n'
        "    profile = get_user_profile(999)\n"
        '  File "app/users.py", line 24, in get_user_profile\n'
        '    "id":    user["id"],\n'
        "             ~~~~^^^^^\n"
        "TypeError: 'NoneType' object is not subscriptable"
    ),
}

SAMPLE_ERROR_LOG = (
    Path(SAMPLE_PROJECT_PATH) / "error.log"
).read_text(encoding="utf-8") if Path(SAMPLE_PROJECT_PATH, "error.log").exists() else ""

SAMPLE_BUG_REPORT = (
    Path(SAMPLE_PROJECT_PATH) / "bug_report.md"
).read_text(encoding="utf-8") if Path(SAMPLE_PROJECT_PATH, "bug_report.md").exists() else ""


def render_diagnose():
    page_header(
        title="Diagnose Incident",
        subtitle="Ingest failure reports, stack traces, and diagnostics into the multi-agent debugging pipeline.",
        category="INVESTIGATION"
    )

    # Check if load_sample was triggered
    load_sample = st.session_state.pop("load_sample", False)
    if load_sample:
        st.session_state["bug_title"] = SAMPLE_BUG["title"]
        st.session_state["bug_desc"] = SAMPLE_BUG["description"]
        st.session_state["error_msg"] = SAMPLE_BUG["error_message"]
        st.session_state["stack_trace"] = SAMPLE_BUG["stack_trace"]
        st.session_state["project_source"] = "Sample Project (python_bug_demo)"

    # ── Section 1: Target Workspace ──────────────────────────────────────────
    st.markdown("""
    <div class="editorial-eyebrow" style="margin-top: 1.5rem; margin-bottom: 0.75rem;">
        <span>01 · TARGET REPOSITORY WORKSPACE</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        project_source = st.radio(
            "Project Source",
            ["Sample Project (python_bug_demo)", "Custom Local Path"],
            horizontal=True,
            label_visibility="collapsed",
            key="project_source_radio",
        )

    if "Sample Project" in project_source:
        project_path = SAMPLE_PROJECT_PATH
        st.markdown(f"""
        <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); padding:0.75rem 1rem; border-radius:var(--radius-sm); margin-bottom:1.5rem; font-family:var(--font-mono); font-size:0.8125rem; color:var(--text-secondary);">
            <span style="color:var(--accent); margin-right:8px;">WORKSPACE:</span>{project_path}
        </div>
        """, unsafe_allow_html=True)
    else:
        project_path = st.text_input(
            "Workspace Absolute Path",
            placeholder="C:/path/to/target/repository",
            key="custom_project_path",
        )

    # ── Section 2: Incident Specification ────────────────────────────────────
    st.markdown("""
    <div class="editorial-eyebrow" style="margin-top: 2rem; margin-bottom: 0.75rem;">
        <span>02 · INCIDENT SPECIFICATION</span>
    </div>
    """, unsafe_allow_html=True)

    bug_title = st.text_input(
        "Incident Title",
        value=st.session_state.get("bug_title", ""),
        placeholder="e.g., Application crashes when requesting a missing user ID",
        key="bug_title",
    )
    bug_desc = st.text_area(
        "Incident Description & Reproduction Steps",
        value=st.session_state.get("bug_desc", ""),
        height=110,
        placeholder="Describe observed behavior, expected contract, and trigger sequence.",
        key="bug_desc",
    )

    # ── Section 3: Runtime Trace & Diagnostics ───────────────────────────────
    st.markdown("""
    <div class="editorial-eyebrow" style="margin-top: 2rem; margin-bottom: 0.75rem;">
        <span>03 · RUNTIME TRACE & DIAGNOSTICS</span>
    </div>
    """, unsafe_allow_html=True)

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        error_msg = st.text_area(
            "Exception Signature",
            value=st.session_state.get("error_msg", ""),
            height=100,
            placeholder="e.g., TypeError: 'NoneType' object is not subscriptable",
            key="error_msg",
        )
    with col_e2:
        stack_trace = st.text_area(
            "Stack Trace / Failure Log",
            value=st.session_state.get("stack_trace", ""),
            height=100,
            placeholder="Paste raw stack trace or log excerpt...",
            key="stack_trace",
        )

    # ── Section 4: Supporting Artifacts ──────────────────────────────────────
    st.markdown("""
    <div class="editorial-eyebrow" style="margin-top: 2rem; margin-bottom: 0.75rem;">
        <span>04 · SUPPORTING ARTIFACTS</span>
    </div>
    """, unsafe_allow_html=True)

    tab_upload, tab_sample = st.tabs(["Upload Files", "Bundled Sample Documents"])

    uploaded_docs = []

    with tab_upload:
        uploaded_files = st.file_uploader(
            "Upload documentation, error dumps, or specifications",
            accept_multiple_files=True,
            type=["md", "txt", "log", "rst", "json"],
            label_visibility="collapsed",
        )
        if uploaded_files:
            for f in uploaded_files:
                content = f.read().decode("utf-8", errors="replace")
                uploaded_docs.append({"filename": f.name, "content": content})

    with tab_sample:
        st.markdown("""
        <div style="font-size:0.8125rem; color:var(--text-secondary); margin-bottom:0.75rem;">
            Load pre-configured incident documents from the sample project for immediate diagnosis.
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ingest Sample Documents", type="secondary"):
            if SAMPLE_ERROR_LOG:
                uploaded_docs.append({"filename": "error.log", "content": SAMPLE_ERROR_LOG})
            if SAMPLE_BUG_REPORT:
                uploaded_docs.append({"filename": "bug_report.md", "content": SAMPLE_BUG_REPORT})
            st.session_state["sample_docs_loaded"] = True
            st.success("Sample documents loaded (error.log, bug_report.md)")

    if st.session_state.get("sample_docs_loaded") and not uploaded_docs:
        if SAMPLE_ERROR_LOG:
            uploaded_docs.append({"filename": "error.log", "content": SAMPLE_ERROR_LOG})
        if SAMPLE_BUG_REPORT:
            uploaded_docs.append({"filename": "bug_report.md", "content": SAMPLE_BUG_REPORT})

    # ── Action Controls ──────────────────────────────────────────────────────
    st.markdown("<hr style='margin: 2.5rem 0 1.5rem 0;' />", unsafe_allow_html=True)

    col_btn, col_fill, col_clear = st.columns([2, 1.5, 1])

    with col_btn:
        start_clicked = st.button("Diagnose Bug →", type="primary", use_container_width=True)

    with col_fill:
        if st.button("Populate Sample Data", type="secondary", use_container_width=True):
            st.session_state["bug_title"] = SAMPLE_BUG["title"]
            st.session_state["bug_desc"] = SAMPLE_BUG["description"]
            st.session_state["error_msg"] = SAMPLE_BUG["error_message"]
            st.session_state["stack_trace"] = SAMPLE_BUG["stack_trace"]
            st.rerun()

    with col_clear:
        if st.button("Reset Form", use_container_width=True):
            for k in ("bug_title", "bug_desc", "error_msg", "stack_trace", "sample_docs_loaded"):
                st.session_state.pop(k, None)
            st.rerun()

    # ── Execution Trigger ────────────────────────────────────────────────────
    if start_clicked:
        if not bug_title.strip():
            st.error("Validation error: Incident title is required.")
            return

        if not project_path or not Path(project_path).exists():
            st.error(f"Validation error: Project path does not exist: {project_path}")
            return

        from core.orchestrator import Orchestrator

        orch = Orchestrator()
        st.session_state["orchestrator"] = orch

        bug_report = {
            "title":         bug_title,
            "description":   bug_desc,
            "error_message": error_msg,
            "stack_trace":   stack_trace,
        }

        # Progress feedback during execution
        with st.status("Executing Multi-Agent Workflow...", expanded=True) as status_box:
            st.write("Initializing repository inspection and security checkpoint...")
            st.write("Dispatching parallel agents: Code Explorer, Error Analyzer, Test Analyzer...")
            st.write("Synthesizing evidence-based root cause...")
            st.write("Generating and applying targeted source patch...")
            st.write("Executing verification test suite...")

            try:
                run_id = orch.start(
                    project_path=project_path,
                    bug_report=bug_report,
                    documents=uploaded_docs,
                )
                st.session_state["active_run_id"] = run_id
                status_box.update(label="Debugging Workflow Complete", state="complete")
            except Exception as exc:
                status_box.update(label=f"Workflow Error: {exc}", state="error")
                st.error(f"Execution failed: {exc}")
                return

        st.session_state.page = "workflow"
        st.rerun()
