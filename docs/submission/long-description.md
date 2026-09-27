# Long Description

> **Word count target: ≤ 500 words**

---

## Bug2Fix AI — From Bug Report to Verified Fix, With Evidence

Every developer knows the cycle: a bug arrives, you spend 25 to 45 minutes reading error logs, searching the codebase, writing a regression test, implementing the fix, running tests, and writing a report. Multiply that by every bug in a sprint and you've consumed a significant fraction of an engineer's week on work that is fundamentally repetitive and analyzable.

**Bug2Fix AI** is a structured, evidence-first debugging workflow that automates this entire cycle using IBM Bob 2.0 agents. It does not generate speculative fixes. It does not output confidence scores. It produces verifiable, objective evidence for every claim it makes — and it only marks a fix as complete when that evidence passes five independent checks.

### How It Works

A developer submits a bug report, an error log, and a repository path. The orchestrator immediately:

1. **Runs baseline tests** — confirming the bug is reproducible before any fix is attempted.
2. **Dispatches three parallel agents** — Code Explorer (AST traversal), Error Analyzer (stack trace parsing), and Test Analyzer (coverage gap identification) — all running concurrently via Python's ThreadPoolExecutor.
3. **Synthesizes root cause** — the Root Cause Agent unifies the three parallel findings into a single, evidence-backed diagnosis with source code references.
4. **Applies a minimal fix** — the Fix Agent makes the smallest safe change required. No unrelated refactoring. The actual file is patched on disk.
5. **Runs tests after the fix** — real pytest execution, not simulation.
6. **Validates scope** — a Scope Guard compares expected vs actual changed files. If anything unexpected changed, the fix is flagged for review rather than silently accepted.
7. **Runs the verification gate** — five independent checks must all pass: regression test passes, all relevant tests pass, full suite passes, scope is clean, diff is consistent.
8. **Generates an Evidence Ledger** — a tamper-evident JSON record of every artifact, decision, and measurement from the run.
9. **Produces a final report** — a structured Markdown debugging specification exportable by the team.

Only when all five verification gate checks pass does the system emit the verdict: **VERIFIED WITH EVIDENCE**.

### What Makes It Different

Most AI debugging tools generate suggestions. Bug2Fix AI generates proof. The Evidence Ledger ties every conclusion to a concrete artifact: a file path, a line number, a test ID, a diff, a pytest output. If a check fails, the system reports VERIFICATION FAILED or BLOCKED — it never inflates the result.

### IBM Bob 2.0 Integration

IBM Bob 2.0 serves as the orchestration and agent intelligence layer. The `BobExecutionAdapter` auto-detects whether the Bob CLI is available. In live mode, agents are dispatched as structured Bob shell commands. In demo mode, pre-computed artifacts labeled `mode: demo` are used, with the distinction clearly visible in the UI. No demo output is ever misrepresented as live.

### Results

On the included Python demo project:
- Before: 5 tests passing, 3 failing
- After: 8 tests passing, 0 failing, 0 regressions
- Total automated time: under 2 seconds
- Manual equivalent: ~25 minutes

Bug2Fix AI — structured debugging, powered by IBM Bob 2.0.
