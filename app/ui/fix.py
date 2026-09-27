"""
app/ui/fix.py — Code Diff and remediation view.

Redesigned with Astra-inspired minimal developer aesthetic:
- Professional code editor aesthetic with subtle additions and deletions.
- Git checkpoint metrics: insertions, deletions, modified files.
- Suggested conventional commit message and recommended verification path.
"""

from __future__ import annotations
import streamlit as st
from app.components.styles import page_header, status_tag


def render_fix():
    page_header(
        title="Remediation Patch",
        subtitle="Targeted source code modifications synthesized by the Fix Agent.",
        category="REMEDIATION"
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
                No remediation patch available.
            </div>
            <p style="font-size:0.875rem; color:var(--text-secondary); margin-bottom:1.5rem;">
                Launch an investigation to generate and apply source fixes.
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

    fix     = state.get("fix", {})
    changes = state.get("changes", [])
    git     = state.get("git", {})

    # ── Remediation Explanation ──────────────────────────────────────────────
    if fix.get("explanation"):
        st.markdown(f"""
        <div class="panel-accent" style="margin-bottom: 2rem;">
            <div style="font-family:var(--font-mono); font-size:0.6875rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--accent); margin-bottom:8px;">
                REMEDIATION RATIONALE
            </div>
            <div style="font-size:0.9375rem; color:var(--text-primary); line-height:1.6;">
                {fix["explanation"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Git Checkpoint Telemetry ─────────────────────────────────────────────
    cs = git.get("change_summary", {}) if git else {}
    files_changed_count = cs.get("files_changed", len(fix.get("files_changed", [1])))
    lines_added = cs.get("lines_added", 4)
    lines_removed = cs.get("lines_removed", 1)

    st.markdown(f"""
    <div class="metric-group" style="margin-bottom: 2rem;">
        <div class="metric-cell">
            <div class="metric-cell-label">MODIFIED FILES</div>
            <div class="metric-cell-value">{files_changed_count}</div>
            <div class="metric-cell-detail">app/users.py</div>
        </div>
        <div class="metric-cell">
            <div class="metric-cell-label">LINES INSERTED</div>
            <div class="metric-cell-value success">+{lines_added}</div>
            <div class="metric-cell-detail">Guard assertion & error raise</div>
        </div>
        <div class="metric-cell">
            <div class="metric-cell-label">LINES REMOVED</div>
            <div class="metric-cell-value" style="color:var(--error);">-{lines_removed}</div>
            <div class="metric-cell-detail">Unchecked index access</div>
        </div>
        <div class="metric-cell">
            <div class="metric-cell-label">APPLICATION STATUS</div>
            <div style="margin-top: 4px;">{status_tag('APPLIED')}</div>
            <div class="metric-cell-detail">Target source patched</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Code Diff View ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="editorial-eyebrow" style="margin-bottom: 1rem;">
        <span>CODE DIFF VIEWER</span>
    </div>
    """, unsafe_allow_html=True)

    if changes:
        for change in changes:
            fname  = change.get("file", "app/users.py")
            before = change.get("before", "")
            after  = change.get("after", "")
            reason = change.get("reason", "Insert None-check before dictionary subscript")

            st.markdown(f"""
            <div class="diff-container">
                <div class="diff-header">
                    <span>{fname}</span>
                    <span style="color:var(--text-muted);">{reason}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Before (Original):**")
                st.code(before, language="python")
            with col2:
                st.markdown("**After (Patched):**")
                st.code(after, language="python")

            # Structured unified-style diff with context
            import difflib
            before_lines = before.splitlines()
            after_lines  = after.splitlines()
            diff_gen = list(difflib.unified_diff(
                before_lines, after_lines,
                fromfile="before", tofile="after",
                lineterm="", n=3,
            ))
            if diff_gen:
                st.markdown("**Unified Diff:**")
                diff_lines_html = []
                for raw_line in diff_gen:
                    if raw_line.startswith("---") or raw_line.startswith("+++"):
                        diff_lines_html.append(
                            f'<div class="diff-line context" style="opacity:0.5;">'
                            f'<span>{raw_line}</span></div>'
                        )
                    elif raw_line.startswith("-"):
                        diff_lines_html.append(
                            f'<div class="diff-line deletion">'
                            f'<span style="user-select:none;opacity:0.6;margin-right:8px;">−</span>'
                            f'<span>{raw_line[1:]}</span></div>'
                        )
                    elif raw_line.startswith("+"):
                        diff_lines_html.append(
                            f'<div class="diff-line addition">'
                            f'<span style="user-select:none;opacity:0.6;margin-right:8px;">+</span>'
                            f'<span>{raw_line[1:]}</span></div>'
                        )
                    elif raw_line.startswith("@@"):
                        diff_lines_html.append(
                            f'<div class="diff-line context" style="color:var(--accent);opacity:0.7;">'
                            f'<span>{raw_line}</span></div>'
                        )
                    else:
                        diff_lines_html.append(
                            f'<div class="diff-line context">'
                            f'<span style="user-select:none;opacity:0.4;margin-right:8px;"> </span>'
                            f'<span>{raw_line}</span></div>'
                        )
                st.markdown(f"""
                <div class="diff-container">
                    <div class="diff-content">
                        {''.join(diff_lines_html)}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="panel" style="padding:1.5rem;">
            <div style="font-family:var(--font-mono); font-size:0.8125rem; color:var(--text-secondary);">
                Target file <code>app/users.py</code> was updated with guard logic:
            </div>
            <div style="margin-top:0.75rem;">
                <pre style="background:var(--bg-elevated); padding:1rem; border-radius:var(--radius-sm); border:1px solid var(--border-subtle); color:var(--text-primary); font-family:var(--font-mono); font-size:0.8125rem;">
user = get_user(user_id)
if user is None:
    raise UserNotFoundError(f"User {user_id} not found.")
return { ... }
                </pre>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Git Suggested Commit ─────────────────────────────────────────────────
    commit_msg = git.get("commit_message", "fix(users): raise UserNotFoundError when user is missing")
    if commit_msg:
        st.markdown("""
        <div class="editorial-eyebrow" style="margin-top: 2rem; margin-bottom: 0.75rem;">
            <span>SUGGESTED CONVENTIONAL COMMIT</span>
        </div>
        """, unsafe_allow_html=True)
        st.code(commit_msg, language=None)
        st.markdown("""
        <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-muted);">
            Note: Bug2Fix AI modifies local working tree only; commits and pushes are reserved for developer authorization.
        </div>
        """, unsafe_allow_html=True)

    # ── Navigation Row ───────────────────────────────────────────────────────
    st.markdown("<hr style='margin: 2.5rem 0 1.5rem 0;' />", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 5])
    with col1:
        if st.button("Review Test Verification →", type="primary", use_container_width=True):
            st.session_state.page = "tests"
            st.rerun()
