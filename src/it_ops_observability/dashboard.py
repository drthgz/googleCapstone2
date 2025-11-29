"""Utilities for assembling observability dashboards."""
from __future__ import annotations

from collections import Counter
from typing import Dict, List

from .tools import fetch_incident_digest, fetch_server_logs, summarize_utilization


def parse_logs(raw: str) -> List[Dict[str, str]]:
    """Convert newline-delimited log text into structured entries."""
    entries: List[Dict[str, str]] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split(" ", 2)
        if len(parts) < 3:
            continue
        timestamp, level_part, remainder = parts
        level = level_part.strip("[]").upper()
        message = remainder.strip()
        component = ""
        if ": " in message:
            component, message = message.split(": ", 1)
        entries.append(
            {
                "timestamp": timestamp,
                "level": level,
                "component": component.strip(),
                "message": message.strip(),
            }
        )
    return entries


def build_dashboard_snapshot(server_id: str, window_minutes: int) -> Dict[str, object]:
    """Fetch utilization, logs, and digest data for the dashboard."""
    summary = summarize_utilization(hours=24)
    logs_text = fetch_server_logs(server_id=server_id, window_minutes=window_minutes)
    digest = fetch_incident_digest()
    parsed_logs = parse_logs(logs_text)
    severity_counts = Counter(entry["level"] for entry in parsed_logs)
    return {
        "summary": summary,
        "logs": parsed_logs,
        "digest": digest,
        "severity_counts": dict(severity_counts),
    }
