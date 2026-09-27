"""
tests/test_document_processor.py — Tests for document processing.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest
from core.document_processor import process_document


def test_process_empty_document():
    result = process_document("", "empty.txt")
    assert result["filename"] == "empty.txt"
    assert isinstance(result["headings"], list)
    assert isinstance(result["stack_traces"], list)


def test_detect_bug_report_type():
    content = "# Bug Report\n## Steps to Reproduce\n1. Do X"
    result  = process_document(content, "bug_report.md")
    assert result["doc_type"] == "bug_report"


def test_detect_error_log_type():
    content = "2026-01-01 ERROR Something went wrong\nTraceback..."
    result  = process_document(content, "error.log")
    assert result["doc_type"] == "error_log"


def test_extract_stack_trace():
    content = (
        "Some text\n"
        "Traceback (most recent call last):\n"
        "  File app.py, line 10, in main\n"
        "    result = do_thing()\n"
        "TypeError: 'NoneType' object is not subscriptable"
    )
    result = process_document(content, "error.log")
    assert len(result["stack_traces"]) > 0
    assert "TypeError" in result["stack_traces"][0]


def test_extract_headings():
    content = "# Title\n## Section 1\n### Subsection\nBody text"
    result  = process_document(content, "readme.md")
    assert len(result["headings"]) >= 2


def test_extract_error_lines():
    content = "INFO ok\nERROR something failed\nWARNING possible issue"
    result  = process_document(content, "app.log")
    assert any("ERROR" in line for line in result["error_lines"])


def test_excerpt_length_limit():
    content = "x" * 100_000
    result  = process_document(content, "huge.txt")
    assert len(result["excerpt"]) <= 3_500  # allow small buffer


def test_code_block_extraction():
    content = "Some text\n```python\ndef foo():\n    pass\n```\nMore text"
    result  = process_document(content, "api_doc.md")
    assert len(result["code_blocks"]) > 0
    assert "def foo" in result["code_blocks"][0]


def test_summary_is_non_empty():
    content = "# Bug\n## Description\nCrash on line 5"
    result  = process_document(content, "issue.md")
    assert result["summary"]
