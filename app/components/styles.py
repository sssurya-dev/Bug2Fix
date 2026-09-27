"""
app/components/styles.py — Design System and CSS for Bug2Fix AI.

Astra-inspired AI developer tool aesthetic:
- Restrained color palette: #0A0A0B (bg), #111113 (surface), #18181B (surface-elevated),
  #242427 (border), #5B8CFF (electric blue accent), #F5F5F2 (off-white), #929296 (muted text).
- Premium typography: Inter / Geist, tight tracking on headings, generous line-height.
- Subtle technical grid background.
- Zero emojis in production UI chrome; precise typographic cues and minimal SVG/line indicators.
- Complete override of Streamlit default styling.
"""

from __future__ import annotations
import streamlit as st


def inject_styles():
    st.markdown("""
    <style>
    /* ── Import Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Design System Variables ── */
    :root {
        --bg-base:          #0A0A0B;
        --bg-surface:       #111113;
        --bg-elevated:      #18181B;
        --bg-subtle:        #1F1F23;
        --border-subtle:    #242427;
        --border-hover:     #36363B;
        --border-focus:     #5B8CFF;
        
        --text-primary:     #F5F5F2;
        --text-secondary:   #929296;
        --text-muted:       #5E5E63;
        
        --accent:           #5B8CFF;
        --accent-hover:     #7AA2FF;
        --accent-glow:      rgba(91, 140, 255, 0.12);
        
        --success:          #34D399;
        --success-bg:       rgba(52, 211, 153, 0.08);
        --success-border:   rgba(52, 211, 153, 0.25);
        
        --error:            #F87171;
        --error-bg:         rgba(248, 113, 113, 0.08);
        --error-border:     rgba(248, 113, 113, 0.25);
        
        --warning:          #FBBF24;
        --warning-bg:       rgba(251, 191, 36, 0.08);
        --warning-border:   rgba(251, 191, 36, 0.25);

        --radius-sm:        4px;
        --radius-md:        6px;
        --radius-lg:        8px;

        --font-sans:        'Geist', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        --font-mono:        'Geist Mono', 'JetBrains Mono', "SF Mono", Consolas, monospace;
    }

    /* ── Hide Streamlit Chrome ── */
    #MainMenu { visibility: hidden !important; }
    header { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }

    /* ── Base App & Canvas with Technical Grid ── */
    .stApp {
        background-color: var(--bg-base) !important;
        font-family: var(--font-sans) !important;
        color: var(--text-primary) !important;
        background-image: 
            linear-gradient(to right, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.02) 1px, transparent 1px) !important;
        background-size: 32px 32px !important;
        background-position: top left !important;
    }

    /* ── Main Container Spacing ── */
    .main .block-container {
        padding: 2.5rem 3rem 5rem 3rem !important;
        max-width: 1280px !important;
        margin: 0 auto !important;
    }

    /* ── Typography Scale ── */
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-sans) !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.025em !important;
        font-weight: 600 !important;
        line-height: 1.2 !important;
    }

    p, span, label, div {
        font-family: var(--font-sans);
        color: var(--text-primary);
    }

    /* ── Editorial Header ── */
    .editorial-header {
        margin-bottom: 2.5rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid var(--border-subtle);
    }

    .editorial-eyebrow {
        font-family: var(--font-mono);
        font-size: 0.6875rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--text-muted);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .editorial-eyebrow-accent {
        color: var(--accent);
    }

    .editorial-title {
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.035em;
        color: var(--text-primary);
        line-height: 1.1;
        margin: 0 0 0.5rem 0;
    }

    .editorial-subtitle {
        font-size: 1rem;
        color: var(--text-secondary);
        max-width: 720px;
        line-height: 1.6;
        margin: 0;
        font-weight: 400;
    }

    /* ── Top Bar Brand & Navigation ── */
    .top-bar-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.875rem 1.5rem;
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        margin-bottom: 2.5rem;
    }

    .brand-mark {
        font-family: var(--font-mono);
        font-weight: 700;
        font-size: 0.9375rem;
        letter-spacing: 0.08em;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .brand-mark .dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: var(--accent);
    }

    .top-bar-meta {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        font-family: var(--font-mono);
        font-size: 0.75rem;
        color: var(--text-secondary);
    }

    /* ── Minimal Top Navigation Tabs ── */
    .nav-bar-wrapper {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 4px;
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        margin-bottom: 2rem;
        overflow-x: auto;
    }

    /* ── Subtle Flat Cards / Panels ── */
    .panel {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: border-color 0.15s ease;
    }

    .panel:hover {
        border-color: var(--border-hover);
    }

    .panel-header {
        font-family: var(--font-mono);
        font-size: 0.6875rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-muted);
        margin-bottom: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .panel-accent {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-left: 2px solid var(--accent);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }

    /* ── Technical Metrics ── */
    .metric-group {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }

    .metric-cell {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 1.25rem 1.5rem;
    }

    .metric-cell-label {
        font-family: var(--font-mono);
        font-size: 0.6875rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        margin-bottom: 0.5rem;
    }

    .metric-cell-value {
        font-size: 2.25rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--text-primary);
        line-height: 1;
    }

    .metric-cell-value.accent {
        color: var(--accent);
    }

    .metric-cell-value.success {
        color: var(--success);
    }

    .metric-cell-detail {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-top: 0.375rem;
        font-family: var(--font-mono);
    }

    /* ── Status Indicators & Tags ── */
    .status-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 2px 8px;
        border-radius: var(--radius-sm);
        font-family: var(--font-mono);
        font-size: 0.6875rem;
        font-weight: 500;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        border: 1px solid transparent;
    }

    .status-tag.complete, .status-tag.done, .status-tag.pass {
        background: var(--success-bg);
        color: var(--success);
        border-color: var(--success-border);
    }

    .status-tag.running, .status-tag.active {
        background: var(--accent-glow);
        color: var(--accent);
        border-color: rgba(91, 140, 255, 0.3);
    }

    .status-tag.queued, .status-tag.pending {
        background: var(--bg-elevated);
        color: var(--text-muted);
        border-color: var(--border-subtle);
    }

    .status-tag.failed, .status-tag.error {
        background: var(--error-bg);
        color: var(--error);
        border-color: var(--error-border);
    }

    .status-tag.demo {
        background: rgba(146, 146, 150, 0.08);
        color: var(--text-secondary);
        border-color: var(--border-subtle);
    }

    /* ── Console / Agent Activity Row ── */
    .agent-console {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        overflow: hidden;
        margin-bottom: 2rem;
    }

    .agent-console-header {
        padding: 0.75rem 1.25rem;
        background: var(--bg-elevated);
        border-bottom: 1px solid var(--border-subtle);
        font-family: var(--font-mono);
        font-size: 0.6875rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        display: flex;
        justify-content: space-between;
    }

    .agent-row-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.875rem 1.25rem;
        border-bottom: 1px solid var(--border-subtle);
        transition: background 0.15s ease;
    }

    .agent-row-item:last-child {
        border-bottom: none;
    }

    .agent-row-item:hover {
        background: rgba(255, 255, 255, 0.015);
    }

    .agent-row-identity {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .agent-indicator-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: var(--text-muted);
    }

    .agent-indicator-dot.active {
        background-color: var(--accent);
        box-shadow: 0 0 8px var(--accent);
    }

    .agent-indicator-dot.done {
        background-color: var(--success);
    }

    .agent-indicator-dot.error {
        background-color: var(--error);
    }

    .agent-row-title {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--text-primary);
    }

    .agent-row-desc {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 2px;
        font-family: var(--font-mono);
    }

    /* ── Technical Flow Diagram (Architecture / Workflow) ── */
    .flow-diagram-container {
        display: flex;
        flex-direction: column;
        gap: 0;
        margin: 2rem 0;
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 1.5rem;
    }

    .flow-node {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.875rem 1rem;
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        position: relative;
    }

    .flow-connector {
        width: 1px;
        height: 20px;
        background: var(--border-subtle);
        margin: 0 auto;
    }

    .flow-parallel-box {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        padding: 1rem;
        background: rgba(24, 24, 27, 0.4);
        border: 1px dashed var(--border-subtle);
        border-radius: var(--radius-sm);
    }

    /* ── Code Diff Styling ── */
    .diff-container {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        overflow: hidden;
        margin-bottom: 1.5rem;
    }

    .diff-header {
        padding: 0.625rem 1rem;
        background: var(--bg-elevated);
        border-bottom: 1px solid var(--border-subtle);
        font-family: var(--font-mono);
        font-size: 0.75rem;
        color: var(--text-secondary);
        display: flex;
        justify-content: space-between;
    }

    .diff-content {
        font-family: var(--font-mono);
        font-size: 0.8125rem;
        line-height: 1.6;
        padding: 1rem;
        overflow-x: auto;
    }

    .diff-line {
        display: flex;
        gap: 12px;
        padding: 2px 4px;
        border-radius: 2px;
    }

    .diff-line.addition {
        background: rgba(52, 211, 153, 0.08);
        color: #A7F3D0;
    }

    .diff-line.deletion {
        background: rgba(248, 113, 113, 0.08);
        color: #FECACA;
    }

    .diff-line.context {
        color: var(--text-secondary);
    }

    /* ── Streamlit Element Overrides ── */
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--bg-surface) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: 1px solid transparent !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        text-align: left !important;
        padding: 0.5rem 0.875rem !important;
        border-radius: var(--radius-sm) !important;
        font-size: 0.8125rem !important;
        font-family: var(--font-mono) !important;
        letter-spacing: 0.02em !important;
        transition: all 0.15s ease !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        border-color: var(--border-subtle) !important;
    }

    /* Buttons */
    .stButton > button[data-testid="baseButton-primary"],
    .stButton > button[kind="primary"] {
        background: var(--accent) !important;
        color: #0A0A0B !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        font-family: var(--font-sans) !important;
        letter-spacing: -0.01em !important;
        padding: 0.55rem 1.25rem !important;
        transition: all 0.15s ease !important;
        box-shadow: none !important;
    }

    .stButton > button[data-testid="baseButton-primary"]:hover,
    .stButton > button[kind="primary"]:hover {
        background: var(--accent-hover) !important;
        box-shadow: 0 0 16px var(--accent-glow) !important;
    }

    .stButton > button[data-testid="baseButton-secondary"],
    .stButton > button:not([data-testid="baseButton-primary"]):not([kind="primary"]) {
        background: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        padding: 0.55rem 1.25rem !important;
        transition: all 0.15s ease !important;
    }

    .stButton > button[data-testid="baseButton-secondary"]:hover,
    .stButton > button:not([data-testid="baseButton-primary"]):not([kind="primary"]):hover {
        background: var(--bg-elevated) !important;
        border-color: var(--border-hover) !important;
        color: var(--text-primary) !important;
    }

    /* Form Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-sans) !important;
        font-size: 0.875rem !important;
        padding: 0.625rem 0.875rem !important;
        transition: border-color 0.15s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
        outline: none !important;
    }

    /* Labels */
    .stTextInput label, .stTextArea label, .stSelectbox label, .stRadio label {
        font-family: var(--font-mono) !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        color: var(--text-secondary) !important;
        margin-bottom: 0.375rem !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        padding: 3px !important;
        gap: 2px !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: 3px !important;
        padding: 6px 14px !important;
        font-size: 0.8125rem !important;
        font-family: var(--font-mono) !important;
        font-weight: 500 !important;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        background: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-subtle) !important;
    }

    /* Radio buttons */
    .stRadio [role="radiogroup"] {
        gap: 1rem !important;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.8125rem !important;
        color: var(--text-secondary) !important;
    }

    .streamlit-expanderHeader:hover {
        color: var(--text-primary) !important;
        border-color: var(--border-hover) !important;
    }

    [data-testid="stExpanderDetails"] {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border-subtle) !important;
        border-top: none !important;
        border-bottom-left-radius: var(--radius-sm) !important;
        border-bottom-right-radius: var(--radius-sm) !important;
        padding: 1.25rem !important;
    }

    /* Code & Pre */
    code {
        font-family: var(--font-mono) !important;
        font-size: 0.8125rem !important;
        background: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        padding: 2px 6px !important;
        border-radius: 3px !important;
        border: 1px solid var(--border-subtle) !important;
    }

    .stCode {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
    }

    /* Streamlit Alert boxes (info, success, warning, error) */
    .stAlert {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        padding: 0.875rem 1.25rem !important;
    }

    [data-testid="stNotification"] {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border-subtle) !important;
    }

    /* Dividers */
    hr {
        border-color: var(--border-subtle) !important;
        margin: 2rem 0 !important;
    }

    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-base);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--border-subtle);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--border-hover);
    }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str, category: str = "LABORATORY"):
    """Render a unified, editorial page header without emojis."""
    st.markdown(f"""
    <div class="editorial-header">
        <div class="editorial-eyebrow">
            <span class="editorial-eyebrow-accent">BUG2FIX</span>
            <span>/</span>
            <span>{category}</span>
        </div>
        <h1 class="editorial-title">{title}</h1>
        <p class="editorial-subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def status_tag(status: str) -> str:
    """Render a minimal status tag with technical styling."""
    status_lower = status.lower()
    label = status.upper()
    return f'<span class="status-tag {status_lower}">{label}</span>'
