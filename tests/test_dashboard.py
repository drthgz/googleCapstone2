"""Tests for dashboard utilities."""
from __future__ import annotations

from typing import Any, Dict, cast

import pytest

from it_ops_observability.dashboard import build_dashboard_snapshot, parse_logs


def test_parse_logs_extracts_fields() -> None:
    raw = "\n".join(
        [
            "2025-11-29T16:30:00Z [warn] prod-app-01: Replica lag increasing",
            "2025-11-29T16:35:00Z [info] prod-app-01: Health check passed",
            "",
            "malformed line without delimiters",
        ]
    )
    entries = parse_logs(raw)

    assert len(entries) == 3
    first, second, third = entries
    assert first["timestamp"] == "2025-11-29T16:30:00Z"
    assert first["level"] == "WARN"
    assert first["component"] == "prod-app-01"
    assert first["message"].startswith("Replica")
    assert second["level"] == "INFO"
    assert third["component"] == ""
    assert third["level"] == "LINE"


def test_build_dashboard_snapshot_aggregates_sources(monkeypatch: pytest.MonkeyPatch) -> None:
    summary: Dict[str, Any] = {
        "hours_evaluated": 24,
        "average_cpu_pct": 50.0,
        "peak_cpu_pct": 80.0,
        "average_memory_pct": 60.0,
        "peak_memory_pct": 90.0,
        "recent_samples": [
            {"timestamp": "2025-11-29T16:00:00Z", "cpu_pct": 50.0, "memory_pct": 60.0}
        ],
    }

    def fake_summarize_utilization(*, hours: int = 24, include_recent: int = 6) -> Dict[str, Any]:
        assert hours == 24
        assert include_recent == 6
        return summary

    def fake_fetch_server_logs(*, server_id: str, window_minutes: int) -> str:
        assert server_id == "prod-app-01"
        assert window_minutes == 120
        return "2025-11-29T16:30:00Z [error] prod-app-01: Database connection lost"

    def fake_fetch_incident_digest() -> str:
        return "Subject: Synthetic Incident\n\nAuto-mitigated in 5 minutes"

    monkeypatch.setattr(
        "it_ops_observability.dashboard.summarize_utilization",
        fake_summarize_utilization,
    )
    monkeypatch.setattr(
        "it_ops_observability.dashboard.fetch_server_logs",
        fake_fetch_server_logs,
    )
    monkeypatch.setattr(
        "it_ops_observability.dashboard.fetch_incident_digest",
        fake_fetch_incident_digest,
    )

    snapshot = cast(Dict[str, Any], build_dashboard_snapshot("prod-app-01", 120))

    assert snapshot["summary"] is summary
    assert snapshot["digest"].startswith("Subject: Synthetic Incident")
    assert snapshot["severity_counts"] == {"ERROR": 1}
    assert snapshot["logs"][0]["level"] == "ERROR"
