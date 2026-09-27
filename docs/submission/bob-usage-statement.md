# IBM Bob Usage Statement

> **Word count target: ≤ 500 words**

---

## How Bug2Fix AI Uses IBM Bob 2.0

IBM Bob 2.0 is used as the core orchestration and agent intelligence layer of Bug2Fix AI. The integration is implemented in `core/bob_execution_adapter.py`, which provides a clean, stable interface between the debugging workflow and Bob's capabilities.

### Agent Mode

The entire Bug2Fix workflow is structured as a multi-agent pipeline. Seven specialized agents are coordinated by the orchestrator:

- **Code Explorer** — Inspects the repository using AST traversal, traces execution paths, and identifies relevant files and functions.
- **Error Analyzer** — Parses stack traces, isolates failure points, and categorizes error types.
- **Test Analyzer** — Reviews existing test coverage, identifies missing regression coverage, and proposes regression test code.
- **Root Cause Agent** — Synthesizes the three parallel findings into a single evidence-backed root cause statement.
- **Fix Agent** — Generates and applies a targeted, minimal source code patch.
- **Verification Agent** — Evaluates test results before and after the fix and runs the five-check verification gate.
- **Documentation Agent** — Compiles the final debugging specification report.

### Parallel Task Execution

Three agents — Code Explorer, Error Analyzer, and Test Analyzer — are dispatched concurrently using Python's `ThreadPoolExecutor`. This is real parallel execution, not simulated, and the agents' results are unified by the Root Cause Agent only after all three complete. This mirrors the pattern of Bob's parallel task capability.

### Repository and Document Understanding

The Code Explorer agent processes the repository using Python's AST module — no code execution required during analysis. Document understanding is handled by `core/document_processor.py`, which extracts structured information from bug reports, error logs, README files, and API documentation. Extracted stack traces and error signatures are passed directly into the Error Analyzer context.

### Custom Workflow Command

A reusable `/bug2fix` workflow command is defined in `.bob/commands/bug2fix.md`. This command encodes the full 9-step debugging workflow as a reusable, version-controlled Bob task, making the workflow repeatable by any team member without configuration.

### Live vs. Demo Mode

The `BobExecutionAdapter` auto-detects whether the Bob CLI is available at startup. In **live mode**, agents are dispatched as `bob run-agent <agent> --input <json>` commands. In **demo mode**, pre-computed, clearly-labeled analysis artifacts are used. The mode is prominently displayed in the UI as either "BOB LIVE" or "DEMO MODE". No demo output is ever represented as a live Bob result.

### Evidence-First Design

The Bob integration is deliberately evidence-first: the system only makes claims that are backed by real artifacts (file paths, line numbers, test node IDs, diffs, pytest outputs). This reflects the principle that AI assistance should augment and prove developer judgment, not replace it with opaque probabilities.

Bob's capabilities make this workflow possible: the ability to create specialized agents with focused responsibilities, orchestrate them in parallel, apply code changes, run tests, and produce structured, machine-readable output that can be audited and verified.
