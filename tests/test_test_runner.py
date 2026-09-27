"""
tests/test_test_runner.py — Tests for the test runner module.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest
from core.test_runner import run_tests, compare_results

SAMPLE_PROJECT = str(ROOT / "sample_projects" / "python_bug_demo")


def test_run_tests_on_sample_project():
    """Running pytest on the sample project should return structured results."""
    result = run_tests(SAMPLE_PROJECT)
    assert isinstance(result, dict)
    assert "passed" in result
    assert "failed" in result
    assert "total" in result
    assert result["total"] > 0


def test_run_tests_returns_duration():
    result = run_tests(SAMPLE_PROJECT)
    assert result["duration"] >= 0


def test_compare_results_detects_improvement():
    before = {"passed": 3, "failed": 1, "total": 4, "tests": [
        {"node_id": "test_a", "outcome": "failed"},
        {"node_id": "test_b", "outcome": "passed"},
    ]}
    after = {"passed": 4, "failed": 0, "total": 4, "tests": [
        {"node_id": "test_a", "outcome": "passed"},
        {"node_id": "test_b", "outcome": "passed"},
    ]}
    comp = compare_results(before, after)
    assert "test_a" in comp["fixed"]
    assert len(comp["regressions"]) == 0
    assert comp["verified"] is True


def test_compare_results_detects_regression():
    before = {"passed": 4, "failed": 0, "total": 4, "tests": [
        {"node_id": "test_a", "outcome": "passed"},
    ]}
    after = {"passed": 3, "failed": 1, "total": 4, "tests": [
        {"node_id": "test_a", "outcome": "failed"},
    ]}
    comp = compare_results(before, after)
    assert "test_a" in comp["regressions"]
    assert comp["verified"] is False


def test_compare_results_no_change():
    before = {"passed": 3, "failed": 1, "total": 4, "tests": [
        {"node_id": "test_a", "outcome": "failed"},
    ]}
    after = {"passed": 3, "failed": 1, "total": 4, "tests": [
        {"node_id": "test_a", "outcome": "failed"},
    ]}
    comp = compare_results(before, after)
    assert comp["verified"] is False
    assert len(comp["regressions"]) == 0  # same tests, not NEW regressions


def test_run_tests_invalid_path():
    """run_tests on a non-existent path should raise ValueError (security guard)."""
    with pytest.raises(ValueError):
        run_tests("/nonexistent/path/that/does/not/exist")
