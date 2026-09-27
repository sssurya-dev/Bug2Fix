# Technology Stack

## Runtime

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| UI Framework | Streamlit 1.56+ |
| AI Orchestration | IBM Bob 2.0 |
| Concurrency | Python ThreadPoolExecutor |
| Static Analysis | Python AST module (stdlib) |
| Test Execution | pytest 9.0 |
| Test Reporting | pytest-json-report 1.5 |
| Git Operations | subprocess + git CLI |
| Configuration | python-dotenv |
| Containerization | Docker |

## IBM Bob Capabilities Used

| Bob Feature | Usage |
|-------------|-------|
| Agent mode | 7 specialized agents |
| Parallel tasks | 3 agents concurrent (ThreadPoolExecutor) |
| Repository understanding | AST-based code inspection |
| Document understanding | Bug reports, error logs, API docs |
| Code editing | Fix Agent applies minimal patches |
| Test execution | pytest before + after verification |
| Custom workflow command | `/bug2fix` reusable workflow |

## Architecture Components

| Module | Purpose |
|--------|---------|
| `core/orchestrator.py` | Central workflow engine |
| `core/bob_execution_adapter.py` | IBM Bob integration layer |
| `core/evidence_ledger.py` | Objective evidence capture |
| `core/scope_guard.py` | Fix scope validation |
| `core/repository_analyzer.py` | AST-based code analysis |
| `core/document_processor.py` | Document extraction |
| `core/test_runner.py` | pytest execution |
| `core/git_manager.py` | Git operations |
| `core/report_generator.py` | Markdown report generation |
| `core/security.py` | Path/command validation |
| `app/main.py` | Streamlit application entry |
| `app/ui/` | Page components (8 pages) |
| `app/components/styles.py` | Design system CSS |

## Infrastructure

- Streamlit single-page application
- In-memory run state (dict-based, no external DB required)
- Markdown + JSON report output to `reports/` directory
- Docker container with `EXPOSE 8501`
- Health check via `GET /health` (FastAPI companion route)
