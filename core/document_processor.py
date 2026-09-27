"""
core/document_processor.py — Extract useful context from supporting documents.

Supports: .md, .txt, .log, .rst, plain text.

Strategy:
- Parse the document.
- Extract relevant sections (headings, error blocks, stack traces, key terms).
- Avoid dumping the entire document into every agent context.
- Return a structured excerpt with source attribution.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from core.security import safe_read_file, sanitize_text


MAX_EXCERPT_LENGTH = 3_000


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_code_blocks(text: str) -> list[str]:
    """Extract fenced code blocks (``` ... ```)."""
    pattern = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
    return [m.group(1).strip() for m in pattern.finditer(text)]


def _extract_stack_traces(text: str) -> list[str]:
    """Extract Python stack traces (Traceback ... Error: ...)."""
    pattern = re.compile(
        r"(Traceback \(most recent call last\):.*?(?:Error|Exception)[^\n]*)",
        re.DOTALL,
    )
    return [m.group(0).strip() for m in pattern.finditer(text)]


def _extract_error_lines(text: str) -> list[str]:
    """Extract lines containing ERROR, CRITICAL, WARNING, Exception, Error."""
    pattern = re.compile(
        r"^.*(ERROR|CRITICAL|WARNING|Exception|Error|Traceback).*$",
        re.IGNORECASE | re.MULTILINE,
    )
    return [m.group(0).strip() for m in pattern.finditer(text)]


def _extract_headings(text: str) -> list[str]:
    """Extract markdown headings."""
    pattern = re.compile(r"^#{1,4}\s+(.+)$", re.MULTILINE)
    return [m.group(0).strip() for m in pattern.finditer(text)]


# ---------------------------------------------------------------------------
# Main processor
# ---------------------------------------------------------------------------

def process_document(
    content: str,
    filename: str,
    max_excerpt: int = MAX_EXCERPT_LENGTH,
) -> dict:
    """
    Process a document and return a structured excerpt.

    Returns:
        {
          "filename": str,
          "doc_type": str,
          "headings": [...],
          "stack_traces": [...],
          "error_lines": [...],
          "code_blocks": [...],
          "raw_excerpt": str,
          "summary": str,
        }
    """
    content  = sanitize_text(content)
    filename = filename or "unknown"
    ext      = Path(filename).suffix.lower()

    doc_type = _detect_type(filename, content)
    headings      = _extract_headings(content)
    stack_traces  = _extract_stack_traces(content)
    error_lines   = _extract_error_lines(content)
    code_blocks   = _extract_code_blocks(content)

    # Build a focused excerpt for the agents
    parts = []

    if headings:
        parts.append("## Document Structure\n" + "\n".join(headings[:10]))

    if stack_traces:
        parts.append("## Stack Traces Found\n" + "\n\n".join(stack_traces[:3]))

    if error_lines and not stack_traces:
        parts.append(
            "## Error Lines\n" + "\n".join(error_lines[:20])
        )

    if code_blocks and doc_type in ("bug_report", "readme", "api_doc"):
        parts.append("## Code Blocks\n" + "\n\n".join(code_blocks[:3]))

    # Fallback: first N characters of raw content
    raw_excerpt = content[:max_excerpt]

    combined = "\n\n".join(parts)
    if len(combined) < 200:
        # Not enough structure — use raw excerpt
        combined = raw_excerpt

    summary = _build_summary(filename, doc_type, headings, stack_traces, error_lines)

    return {
        "filename":     filename,
        "doc_type":     doc_type,
        "headings":     headings,
        "stack_traces": stack_traces,
        "error_lines":  error_lines,
        "code_blocks":  code_blocks,
        "raw_excerpt":  raw_excerpt,
        "excerpt":      combined[:max_excerpt],
        "summary":      summary,
    }


def process_uploaded_file(file_path: str) -> dict:
    """Read a file from disk and process it."""
    fpath   = Path(file_path)
    content = safe_read_file(fpath)
    return process_document(content, fpath.name)


def process_uploaded_content(content: str, filename: str) -> dict:
    """Process an already-loaded string."""
    return process_document(content, filename)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_type(filename: str, content: str) -> str:
    name = filename.lower()
    if "bug_report" in name or "issue" in name:
        return "bug_report"
    if "error" in name or name.endswith(".log"):
        return "error_log"
    if "readme" in name:
        return "readme"
    if "test" in name:
        return "test_report"
    if "api" in name or "spec" in name:
        return "api_doc"
    # Content heuristics
    if "Traceback" in content or "ERROR" in content:
        return "error_log"
    if "## Steps to Reproduce" in content or "## Bug" in content:
        return "bug_report"
    return "document"


def _build_summary(
    filename: str,
    doc_type: str,
    headings: list,
    stack_traces: list,
    error_lines: list,
) -> str:
    parts = [f"Document: {filename} (type: {doc_type})"]
    if headings:
        parts.append(f"{len(headings)} section(s) found.")
    if stack_traces:
        parts.append(f"{len(stack_traces)} stack trace(s) extracted.")
    if error_lines:
        parts.append(f"{len(error_lines)} error line(s) detected.")
    return " ".join(parts)
