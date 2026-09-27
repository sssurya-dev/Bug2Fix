# Bug2Fix AI — Demo Script

> **Target Duration:** ≤ 3 minutes  
> **Goal:** Show a bug going from report → root cause → verified fix, driven by IBM Bob 2.0 agents.

---

## PRE-DEMO CHECKLIST

- [ ] Run `reset_demo.bat` (restores sample project to buggy state)
- [ ] Verify: `python -m pytest sample_projects/python_bug_demo/tests/ -q` shows **3 failed**
- [ ] App running: `streamlit run app/main.py`
- [ ] Browser at `http://localhost:8501`
- [ ] Screen sharing ready, browser fullscreen
- [ ] No sensitive files or terminals visible

---

## TIMING BREAKDOWN

| Segment | Time | Content |
|---------|------|---------|
| Problem statement | 0:00–0:20 | The debugging pain |
| Bug2Fix concept | 0:20–0:40 | What it does and how |
| LIVE DEMO | 0:40–2:20 | Full workflow execution |
| Evidence + verification | 2:20–2:45 | Proof, not promises |
| Impact + close | 2:45–3:00 | Numbers + future |

---

## SCRIPT

### 0:00–0:20 — Problem

> "Every bug costs a developer 25 to 45 minutes. Reading the report. Searching the code. Writing a regression test. Implementing the fix. Running tests. Writing a report. Every single bug, every single time."

**Show:** Overview dashboard

---

### 0:20–0:40 — Bug2Fix Concept

> "Bug2Fix AI is a structured, evidence-first debugging workflow. You give it a bug report, an error log, and a repository. IBM Bob 2.0 agents take over. They prove the fix — they don't just generate it."

**Show:** Architecture pipeline diagram on Overview page

---

### 0:40–2:20 — LIVE DEMO

**Step 1:** Navigate to **Diagnose** page.

> "Here's our sample project — a Python user service that crashes with a TypeError when you request a missing user ID."

**Step 2:** Click **"Populate Sample Data"** button.

> "Bug title, error message, stack trace — all loaded."

**Step 3:** Click **"Ingest Sample Documents"** tab, then **"Ingest Sample Documents"** button.

> "We're feeding it the actual error log and bug report."

**Step 4:** Click **"Diagnose Bug →"** (primary CTA).

> "Watch the 7-agent pipeline execute."

*[Wait for completion — approximately 5–8 seconds]*

**Step 5:** Navigate to **Workflow** page.

> "All 7 agents completed. Three ran in parallel — Code Explorer, Error Analyzer, Test Analyzer. Then root cause synthesis, fix, verification, documentation."

**Step 6:** Navigate to **Root Cause** page.

> "The root cause: missing None-check in users.py, line 24. Direct evidence — from the stack trace and AST inspection of the source code."

**Step 7:** Navigate to **Fix** page.

> "One file changed. Three lines added. Here's the diff — before, no None check; after, a clean UserNotFoundError with a clear message. That's it."

**Step 8:** Navigate to **Tests** page.

> "Before: 5 passing, 3 failing. After: 8 passing, zero failing. The regression test now passes. No regressions detected. Real pytest execution."

---

### 2:20–2:45 — Evidence + Verification

**Step 9:** Navigate to **Evidence** page.

> "This is our signature feature — the Evidence Ledger. Not a probability score. Not a confidence percentage. Five objective checks."

*Point to the verification gate:*

> "Regression test passes — PASS. Relevant tests pass — PASS. Full suite passes — PASS. Scope clean — PASS. Diff consistent — PASS. Overall verdict: VERIFIED WITH EVIDENCE."

---

### 2:45–3:00 — Impact + Close

**Step 10:** Navigate to **Report** page briefly.

> "25 minutes of manual work. Under 2 seconds automated. Full debugging report generated automatically."

> "Bug2Fix AI — from bug report to verified fix, with evidence. Thank you."

---

## FALLBACK PLAN

If the live workflow fails mid-run:

1. Say: *"Let me show you the results from a previous run."*
2. If state is already loaded, navigate directly to Workflow → Root Cause → Fix → Tests → Evidence.
3. All pages show meaningful data from the completed state.

---

## THINGS TO NEVER DO

- Do not show the terminal or raw code files during demo
- Do not claim demo-mode outputs are live Bob results (UI shows "DEMO MODE" badge)
- Do not show the `.env` file
- Do not resize the browser window mid-recording
- Do not scroll to show sensitive content in the reports/ directory
