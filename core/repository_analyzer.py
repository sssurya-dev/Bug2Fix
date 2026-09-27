"""
core/repository_analyzer.py — Static analysis of a Python project.

Responsibilities:
- Walk the file tree and collect Python source files.
- Extract module-level functions and classes (AST-based, no execution).
- Detect test files.
- Detect requirements files.
- Detect README and documentation files.
- Produce a structured project map for use by the agents.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Optional

from core.security import validate_project_path, safe_read_file, SecurityError


SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "env", ".env",
             "node_modules", ".tox", "dist", "build", ".mypy_cache"}
MAX_FILES = 500


# ---------------------------------------------------------------------------
# Data classes (plain dicts for JSON-serializability)
# ---------------------------------------------------------------------------

def _make_file_record(path: Path, workspace: Path) -> dict:
    rel = path.relative_to(workspace).as_posix()
    return {
        "path":     str(path),
        "rel_path": rel,
        "size":     path.stat().st_size,
        "is_test":  _is_test_file(rel),
    }


def _is_test_file(rel_path: str) -> bool:
    parts = rel_path.lower().replace("\\", "/").split("/")
    return any(
        p.startswith("test_") or p.endswith("_test.py") or p in ("tests", "test")
        for p in parts
    )


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def _extract_symbols(source: str) -> dict:
    """Return {functions: [...], classes: [...]} from source code."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {"functions": [], "classes": []}

    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append({
                "name":    node.name,
                "line":    node.lineno,
                "is_async": isinstance(node, ast.AsyncFunctionDef),
                "args":    [a.arg for a in node.args.args],
            })
        elif isinstance(node, ast.ClassDef):
            methods = [
                n.name for n in ast.walk(node)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and n is not node
            ]
            classes.append({
                "name":    node.name,
                "line":    node.lineno,
                "methods": methods,
            })

    return {"functions": functions, "classes": classes}


def _extract_imports(source: str) -> list[str]:
    """Return a list of top-level imported module names."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split(".")[0])
    return list(dict.fromkeys(imports))  # deduplicate, preserve order


# ---------------------------------------------------------------------------
# Main analyser
# ---------------------------------------------------------------------------

def analyze_repository(project_path: str) -> dict:
    """
    Walk *project_path* and produce a full project map.

    Returns a dict with:
      python_files, test_files, docs, requirements, structure_summary,
      total_files, language
    """
    workspace = validate_project_path(project_path)

    python_files = []
    test_files   = []
    docs         = []
    requirements = []
    all_files    = []
    file_count   = 0

    for root, dirs, files in os.walk(workspace):
        # Prune unwanted dirs in-place
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for fname in files:
            if file_count >= MAX_FILES:
                break
            fpath = Path(root) / fname
            try:
                rec = _make_file_record(fpath, workspace)
            except (PermissionError, OSError):
                continue

            all_files.append(rec)
            file_count += 1

            lname = fname.lower()

            if lname.endswith(".py"):
                try:
                    source = safe_read_file(fpath)
                    symbols = _extract_symbols(source)
                    imports = _extract_imports(source)
                    rec["symbols"]  = symbols
                    rec["imports"]  = imports
                    rec["source"]   = source
                except Exception:
                    rec["symbols"]  = {"functions": [], "classes": []}
                    rec["imports"]  = []
                    rec["source"]   = ""

                if rec["is_test"]:
                    test_files.append(rec)
                else:
                    python_files.append(rec)

            elif lname in ("readme.md", "readme.rst", "readme.txt",
                           "readme", "contributing.md"):
                try:
                    rec["content"] = safe_read_file(fpath)
                except Exception:
                    rec["content"] = ""
                docs.append(rec)

            elif lname in ("requirements.txt", "requirements-dev.txt",
                           "pyproject.toml", "setup.py", "setup.cfg",
                           "pipfile"):
                try:
                    rec["content"] = safe_read_file(fpath)
                except Exception:
                    rec["content"] = ""
                requirements.append(rec)

    total_functions = sum(
        len(f.get("symbols", {}).get("functions", []))
        for f in python_files
    )
    total_classes = sum(
        len(f.get("symbols", {}).get("classes", []))
        for f in python_files
    )

    return {
        "workspace":        str(workspace),
        "python_files":     python_files,
        "test_files":       test_files,
        "docs":             docs,
        "requirements":     requirements,
        "all_files":        all_files,
        "total_files":      file_count,
        "total_py_files":   len(python_files),
        "total_test_files": len(test_files),
        "total_functions":  total_functions,
        "total_classes":    total_classes,
        "language":         "Python",
        "structure_summary": (
            f"{len(python_files)} source files, {len(test_files)} test files, "
            f"{total_functions} functions, {total_classes} classes"
        ),
    }


def get_file_content(file_path: str, workspace_path: str) -> str:
    """Read a single file safely within the workspace."""
    workspace = validate_project_path(workspace_path)
    fpath = Path(file_path)
    if not fpath.is_absolute():
        fpath = workspace / fpath
    fpath = fpath.resolve()
    # Security: must be within workspace
    try:
        fpath.relative_to(workspace)
    except ValueError:
        raise SecurityError(f"File '{fpath}' is outside workspace.")
    return safe_read_file(fpath)
