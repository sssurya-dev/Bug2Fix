# Bug2Fix AI — Presentation Content

> IBM Bob 2.0 Hackathon — 7 Slides

---

## Slide 1: Title

**BUG2FIX AI**

Evidence-first AI debugging, powered by IBM Bob 2.0.

*From bug report to verified fix — with proof.*

IBM Bob 2.0 Hackathon 2026 · Surya S S, Nithin Pranav K, Sharan Pranav K, Hari Kishor G

---

## Slide 2: The Developer Debugging Problem

**Every bug costs 25–45 minutes of manual, repetitive work**

| Stage | Manual Time |
|-------|-------------|
| Read bug report + error log | ~5 min |
| Search codebase for root cause | ~10 min |
| Write regression test | ~5 min |
| Implement the fix | ~5 min |
| Run tests manually | ~2 min |
| Write debugging report | ~5 min |
| **Total** | **~32 min** |

**The real problem isn't speed — it's reliability.**

- Fixes merged without regression tests
- Root causes guessed, not proven
- "Fix" applied, tests not rerun
- No evidence trail for what was actually verified

---

## Slide 3: Our Solution — Evidence-First Debugging

**Bug2Fix AI is not a code suggestion tool.**

It is a structured debugging workflow that **proves** the fix works.

```
Bug Report + Error Log
        ↓
IBM Bob 2.0 Orchestrator
        ↓
REPRODUCE → ANALYZE → FIX → VERIFY → PROVE
        ↓
✓ VERIFIED WITH EVIDENCE
```

**The difference:** Every claim is backed by a real artifact.

- Root cause? Backed by a file path + line number.
- Fix works? Backed by pytest output, not AI confidence.
- No regressions? Backed by full suite execution.
- Scope clean? Backed by expected vs. actual file comparison.

---

## Slide 4: IBM Bob 2.0 Architecture

**7 Specialized Agents. 3 Running in Parallel.**

```
                    IBM Bob Orchestrator
                           │
              ┌────────────┼────────────┐
              │            │            │
        Code Explorer  Error Analyzer  Test Analyzer
        (Parallel)     (Parallel)      (Parallel)
              │            │            │
              └────────────┼────────────┘
                           │
                    Root Cause Agent
                           │
                      Fix Agent
                           │
                  ┌────────┴────────┐
              Scope Guard    Verification Agent
                           │
                  Documentation Agent
                           │
                 VERIFIED WITH EVIDENCE
```

**IBM Bob capabilities demonstrated:**

| Capability | Implementation |
|-----------|---------------|
| Agent mode | 7 specialized agents |
| Parallel tasks | 3 agents concurrent (ThreadPoolExecutor) |
| Repository understanding | AST-based code inspection |
| Document understanding | Bug reports, error logs, API docs |
| Code editing | Minimal safe patch application |
| Test execution | pytest before + after |
| Custom workflow | `/bug2fix` reusable command |

---

## Slide 5: Live Workflow — Python Crash Demo

**The Bug:**
```
TypeError: 'NoneType' object is not subscriptable
```

**Step-by-step:**

1. Submit bug report + error log → Document processor extracts stack trace
2. AST inspection → Code Explorer identifies `users.py:get_user_profile()`
3. Error analysis → Error Analyzer confirms `user["id"]` subscripts `None`
4. Test analysis → Test Analyzer finds 3 failing tests, no existing None-check test
5. Root cause: Missing guard after `database.get_user()` returns `None`
6. Baseline tests: 5 passed / **3 failed** — bug confirmed
7. Fix applied: `if user is None: raise UserNotFoundError(...)`
8. Post-fix tests: **8 passed / 0 failed** — regression test now passes
9. Scope: Only `app/users.py` changed — CLEAN
10. Evidence Ledger: All 5 gate checks PASS

**Final verdict: ✓ VERIFIED WITH EVIDENCE**

---

## Slide 6: Evidence + Measured Impact

**The Evidence Ledger — 5 independent checks:**

| Check | Result |
|-------|--------|
| Regression test passes after fix | ✓ PASS |
| All relevant tests pass | ✓ PASS |
| Full test suite passes | ✓ PASS |
| No unexpected files changed | ✓ PASS |
| Diff consistent with root cause | ✓ PASS |
| **Overall verdict** | **✓ VERIFIED WITH EVIDENCE** |

**Measured results (this run):**

| Metric | Value |
|--------|-------|
| Before fix | 5 passed / 3 failed |
| After fix | 8 passed / 0 failed |
| Regressions | 0 |
| Files changed | 1 |
| Automated execution time | < 10 seconds |
| Manual baseline (estimated) | ~25 minutes |

*Manual baseline is labeled as an estimate. Automated time is measured.*

**42/42 tests passing in the Bug2Fix AI codebase itself.**

---

## Slide 7: Future Scope

**What's Next**

**Language expansion:**
- JavaScript / TypeScript (Node.js + Jest)
- Java (Maven + JUnit)
- C / C++ (CMake + CTest)

**Workflow expansion:**
- Pull-request auto-debugging
- GitHub Actions / CI pipeline integration
- IDE plugin (VS Code, JetBrains)
- Slack / Teams incident integration

**Intelligence expansion:**
- Team debugging pattern library
- Historical bug database
- Production incident correlation
- Multi-file refactoring with scope validation

**The IBM Bob agent framework makes all of this extensible without rewriting the core architecture.**

---

*Bug2Fix AI — IBM Bob 2.0 Hackathon 2026*
