"""Smoke tests for observability data tools."""
from __future__ import annotations

from it_ops_observability.tools import fetch_incident_digest
from it_ops_observability.tools import fetch_server_logs
from it_ops_observability.tools import summarize_utilization


def test_fetch_server_logs_returns_text() -> None:
    result = fetch_server_logs(server_id="test-123", window_minutes=60)
    assert isinstance(result, str)
    assert "test-123" in result


def test_summarize_utilization_shape() -> None:
    result = summarize_utilization(hours=12, include_recent=3)
    expected_keys = {
        "hours_evaluated",
        "average_cpu_pct",
        "peak_cpu_pct",
        "average_memory_pct",
        "peak_memory_pct",
        "recent_samples",
    }
    assert expected_keys == set(result)
    assert len(result["recent_samples"]) == 3


def test_fetch_incident_digest_returns_text() -> None:
    result = fetch_incident_digest()
    assert isinstance(result, str)
    assert "Subject:" in result
