"""Synthetic data generators for IT observability scenarios."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import random
from typing import Iterable, Literal

import pandas as pd


@dataclass(frozen=True)
class SyntheticConfig:
    """Configuration for synthetic signal generation."""

    seed: int = 42
    log_window_minutes: int = 240
    metrics_hours: int = 24


_SEVERITIES: tuple[str, ...] = ("CRITICAL", "ERROR", "WARN", "INFO")
_INCIDENT_TYPES: tuple[str, ...] = (
    "Network",
    "Database",
    "Application",
    "Infrastructure",
)


def _seed_if_needed(seed: int | None) -> None:
    if seed is not None:
        random.seed(seed)


def generate_mock_logs(
    server_id: str,
    *,
    window_minutes: int = 240,
    seed: int | None = SyntheticConfig.seed,
) -> str:
    """Create timestamped log entries with realistic error bursts."""
    _seed_if_needed(seed)
    now = datetime.utcnow()
    entries: list[str] = []
    for minute in range(window_minutes // 5):
        timestamp = now - timedelta(minutes=minute * 5)
        severity = random.choices(_SEVERITIES, weights=[0.05, 0.15, 0.3, 0.5])[0]
        message = _log_message(severity)
        entries.append(f"{timestamp.isoformat()}Z [{severity}] {server_id}: {message}")
    entries.reverse()
    return "\n".join(entries)


def _log_message(severity: str) -> str:
    critical_pool: tuple[str, ...] = (
        "Latency spike detected on API Gateway",
        "Database connection timeout",
        "Disk saturation beyond 95%",
        "Service mesh circuit breaker open",
    )
    warn_pool: tuple[str, ...] = (
        "Retrying connection to cache cluster",
        "CPU utilization approaching threshold",
        "Replica lag increasing",
    )
    info_pool: tuple[str, ...] = (
        "Health check passed",
        "Autoscaler polling",
        "Background job completed",
    )
    if severity in {"CRITICAL", "ERROR"}:
        return random.choice(critical_pool)
    if severity == "WARN":
        return random.choice(warn_pool)
    return random.choice(info_pool)


def generate_mock_metrics(
    *,
    hours: int = 24,
    seed: int | None = SyntheticConfig.seed,
) -> pd.DataFrame:
    """Return hourly CPU/memory stats with spikes to trigger SLA alerts."""
    _seed_if_needed(seed)
    now = datetime.utcnow()
    timestamps: Iterable[datetime] = (now - timedelta(hours=h) for h in range(hours))
    cpu_values = [max(10, min(99, random.gauss(55, 18))) for _ in range(hours)]
    memory_values = [max(20, min(95, random.gauss(63, 12))) for _ in range(hours)]
    df = pd.DataFrame(
        {
            "timestamp": list(reversed(list(timestamps))),
            "cpu_pct": cpu_values,
            "memory_pct": memory_values,
        }
    )
    return df


def generate_incident_email(
    severity: Literal["SEV1", "SEV2", "SEV3"],
    *,
    seed: int | None = SyntheticConfig.seed,
) -> str:
    """Return a synthetic incident email for context."""
    _seed_if_needed(seed)
    incident = random.choice(_INCIDENT_TYPES)
    window = random.choice(("00:00-02:00 UTC", "02:00-04:00 UTC", "Maintenance window TBD"))
    return (
        f"Subject: {severity} {incident} Incident Update\n"
        f"From: it-operations@company.com\n"
        f"Body: {incident} team reports anomalies impacting customer latency."
        f" Suggested remediation window: {window}."
    )
