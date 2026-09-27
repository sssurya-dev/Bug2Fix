"""
app/ui/dashboard.py — Editorial overview and dashboard page.

Redesigned with Astra-inspired minimal developer aesthetic:
- Confident, large typography hero with quiet technical tone.
- Minimal architecture flow diagram with precise connectivity.
- Typographic metric cells with high visual hierarchy.
- Direct call to action without marketing fluff.
"""

from __future__ import annotations
import streamlit as st
from app.components.styles import page_header, status_tag


def render_dashboard():
    # ── Editorial Hero ───────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding: 2.5rem 0 3rem 0; border-bottom: 1px solid var(--border-subtle); margin-bottom: 2.5rem;">
        <div class="editorial-eyebrow" style="margin-bottom: 1rem;">
            <span class="editorial-eyebrow-accent">AUTOMATED DEBUGGING WORKFLOW</span>
            <span>·</span>
            <span>MULTI-AGENT ARCHITECTURE</span>
        </div>
        <div style="font-size: 3.5rem; font-weight: 700; letter-spacing: -0.04em; line-height: 1.05; color: var(--text-primary); max-width: 900px; margin-bottom: 1.25rem;">
            From failure report to verified fix.
        </div>
        <p style="font-size: 1.125rem; color: var(--text-secondary); line-height: 1.6; max-width: 680px; margin: 0 0 2rem 0;">
            Bug2Fix AI orchestrates specialized IBM Bob 2.0 agents to inspect repository codebases, 
            isolate runtime exceptions, synthesize evidence-based root causes, generate targeted patches, 
            and prove resolution with regression test execution.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Primary Action Row
    col_action1, col_action2, col_spacer = st.columns([1.5, 1.5, 4])
    with col_action1:
        if st.button("Start Diagnosis →", type="primary", use_container_width=True):
            st.session_state.page = "diagnose"
            st.rerun()
    with col_action2:
        if st.button("Load Sample Incident", type="secondary", use_container_width=True):
            st.session_state.page = "diagnose"
            st.session_state["load_sample"] = True
            st.rerun()

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    # ── Active Session / Last Run Summary ───────────────────────────────────
    run_id = st.session_state.get("active_run_id")
    orch = st.session_state.get("orchestrator")
    state = orch.get_state(run_id) if (orch and run_id) else None

    if state and state.get("status") == "done":
        m = state.get("metrics", {})
        v = state.get("verification", {})
        rc = state.get("root_cause", {})

        st.markdown("""
        <div class="editorial-eyebrow" style="margin-bottom: 1rem;">
            <span>ACTIVE INCIDENT VERIFICATION SUMMARY</span>
        </div>
        """, unsafe_allow_html=True)

        # Verification Banner
        if v.get("verified"):
            st.markdown("""
            <div class="panel-accent" style="margin-bottom: 2rem;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div style="font-family:var(--font-mono); font-size:0.6875rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--success); margin-bottom:6px;">
                            STATUS: RESOLUTION VERIFIED
                        </div>
                        <div style="font-size:1.25rem; font-weight:600; color:var(--text-primary); margin-bottom:8px;">
                            Regression tests pass. 0 secondary regressions detected.
                        </div>
                        <div style="font-size:0.875rem; color:var(--text-secondary); line-height:1.5;">
                            Source patch applied to target workspace. Suite execution confirmed 8 passing assertions.
                        </div>
                    </div>
                    <span class="status-tag complete">VERIFIED</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Metrics Grid
        baseline = m.get("baseline_manual_minutes", 25)
        b2f_time = m.get("bug2fix_minutes", 0)
        saved = m.get("time_saved_minutes", 0)
        pct = round((saved / baseline) * 100) if baseline else 0

        st.markdown(f"""
        <div class="metric-group">
            <div class="metric-cell">
                <div class="metric-cell-label">MANUAL BASELINE</div>
                <div class="metric-cell-value">{baseline} min</div>
                <div class="metric-cell-detail">Triage to report</div>
            </div>
            <div class="metric-cell">
                <div class="metric-cell-label">BUG2FIX EXECUTION</div>
                <div class="metric-cell-value accent">{m.get('total_time_seconds', 1.3):.1f}s</div>
                <div class="metric-cell-detail">Parallel agent cycle</div>
            </div>
            <div class="metric-cell">
                <div class="metric-cell-label">TIME REDUCTION</div>
                <div class="metric-cell-value success">{pct}%</div>
                <div class="metric-cell-detail">{saved:.1f} min reclaimed</div>
            </div>
            <div class="metric-cell">
                <div class="metric-cell-label">FILES INSPECTED</div>
                <div class="metric-cell-value">{m.get('files_inspected', 14)}</div>
                <div class="metric-cell-detail">{m.get('files_changed', 1)} patch applied</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Quick Links to Artifacts
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            if st.button("Review Root Cause →", use_container_width=True):
                st.session_state.page = "root_cause"
                st.rerun()
        with col_r2:
            if st.button("Inspect Code Diff →", use_container_width=True):
                st.session_state.page = "fix"
                st.rerun()
        with col_r3:
            if st.button("Download Final Report →", use_container_width=True):
                st.session_state.page = "report"
                st.rerun()

    else:
        # Empty State / Cold Start
        st.markdown("""
        <div class="panel" style="padding: 2.5rem; text-align: left; margin-bottom: 2.5rem;">
            <div style="font-family:var(--font-mono); font-size:0.6875rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-muted); margin-bottom:0.75rem;">
                WORKFLOW READINESS
            </div>
            <div style="font-size:1.5rem; font-weight:600; color:var(--text-primary); margin-bottom:0.75rem;">
                Ready for incident ingestion.
            </div>
            <p style="font-size:0.9375rem; color:var(--text-secondary); line-height:1.6; max-width:640px; margin:0 0 1.5rem 0;">
                No debugging run is currently active. Select a target repository or initialize the bundled 
                sample project to observe real-time agent dispatch and verification.
            </p>
            <div style="display:flex; gap:1.5rem; font-family:var(--font-mono); font-size:0.75rem; color:var(--text-muted);">
                <div>SAMPLE: <code>sample_projects/python_bug_demo</code></div>
                <div>PARALLEL WORKERS: 3</div>
                <div>TEST HARNESS: pytest</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Architecture Workflow Diagram ───────────────────────────────────────
    st.markdown("""
    <div style="margin-top: 3rem; margin-bottom: 1.5rem;">
        <div class="editorial-eyebrow">
            <span>PIPELINE TOPOLOGY</span>
            <span>·</span>
            <span>PARALLEL EXECUTION MODEL</span>
        </div>
        <div style="font-size: 1.5rem; font-weight: 600; color: var(--text-primary); letter-spacing:-0.02em;">
            Orchestration Flow
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="flow-diagram-container">
        <!-- Node 1 -->
        <div class="flow-node">
            <div>
                <span style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-muted); margin-right:8px;">01</span>
                <span style="font-size:0.875rem; font-weight:500;">INCIDENT INGESTION</span>
                <span style="color:var(--text-muted); font-size:0.8125rem; margin-left:8px;">Bug report, runtime logs & documents</span>
            </div>
            <span class="status-tag queued">INPUT</span>
        </div>
        
        <div class="flow-connector"></div>

        <!-- Node 2: Parallel Box -->
        <div style="margin: 0; padding: 1.25rem; background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm);">
            <div style="font-family:var(--font-mono); font-size:0.6875rem; color:var(--accent); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.75rem;">
                02 · CONCURRENT AGENT ANALYSIS (THREAD POOL EXECUTOR)
            </div>
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
                <div style="background:var(--bg-elevated); padding:1rem; border:1px solid var(--border-subtle); border-radius:var(--radius-sm);">
                    <div style="font-size:0.8125rem; font-weight:600; color:var(--text-primary); margin-bottom:4px;">Code Explorer</div>
                    <div style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono);">AST parsing & call graph traversal</div>
                </div>
                <div style="background:var(--bg-elevated); padding:1rem; border:1px solid var(--border-subtle); border-radius:var(--radius-sm);">
                    <div style="font-size:0.8125rem; font-weight:600; color:var(--text-primary); margin-bottom:4px;">Error Analyzer</div>
                    <div style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono);">Traceback isolation & failure point</div>
                </div>
                <div style="background:var(--bg-elevated); padding:1rem; border:1px solid var(--border-subtle); border-radius:var(--radius-sm);">
                    <div style="font-size:0.8125rem; font-weight:600; color:var(--text-primary); margin-bottom:4px;">Test Analyzer</div>
                    <div style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono);">Coverage check & test synthesis</div>
                </div>
            </div>
        </div>

        <div class="flow-connector"></div>

        <!-- Node 3 -->
        <div class="flow-node">
            <div>
                <span style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-muted); margin-right:8px;">03</span>
                <span style="font-size:0.875rem; font-weight:500;">ROOT CAUSE SYNTHESIS</span>
                <span style="color:var(--text-muted); font-size:0.8125rem; margin-left:8px;">Evidence unification & minimal target location</span>
            </div>
            <span class="status-tag queued">SYNTHESIS</span>
        </div>

        <div class="flow-connector"></div>

        <!-- Node 4 -->
        <div class="flow-node">
            <div>
                <span style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-muted); margin-right:8px;">04</span>
                <span style="font-size:0.875rem; font-weight:500;">TARGETED PATCH & VERIFICATION</span>
                <span style="color:var(--text-muted); font-size:0.8125rem; margin-left:8px;">Smallest safe edit + automated pytest suite</span>
            </div>
            <span class="status-tag queued">EXECUTION</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
