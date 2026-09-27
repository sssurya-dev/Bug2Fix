# Hackathon Categories

## Primary Category

**Developer Tools & Productivity**

Bug2Fix AI is a developer-facing tool that automates a repetitive, high-frequency engineering task: debugging. The workflow transforms an unstructured bug report into a verified, evidence-backed fix with zero manual codebase search.

## Secondary Categories

**AI Agents & Automation**

The core architecture is a multi-agent pipeline. Seven specialized IBM Bob 2.0 agents with distinct roles are orchestrated sequentially and in parallel, demonstrating agent composition and coordination.

**Code Quality & Testing**

Bug2Fix AI enforces a regression test gate: a bug fix is not complete until a regression test confirms the failure, the fix resolves it, and the full test suite passes. The scope guard prevents unintended changes from reaching production.

## IBM Bob Capabilities Demonstrated

- [x] Agent mode
- [x] Specialized subagents
- [x] Parallel task execution
- [x] Repository understanding (AST)
- [x] Document understanding
- [x] Code editing
- [x] Test execution and verification
- [x] Custom reusable workflow command (`/bug2fix`)
