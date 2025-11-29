"""Tool wrappers that make data access functions available to ADK agents."""
from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from google.adk.tools.function_tool import FunctionTool

from .data_sources import DataConfig
from .data_sources import DEFAULT_CONFIG
from .data_sources import fetch_logs
from .data_sources import fetch_recent_ticket
from .data_sources import summarize_metrics


_ACTIVE_CONFIG: DataConfig = DEFAULT_CONFIG


def set_data_config(config: Optional[DataConfig]) -> None:
    """Override the data configuration used by the tool wrappers."""
    global _ACTIVE_CONFIG
    _ACTIVE_CONFIG = config or DEFAULT_CONFIG


def fetch_server_logs(server_id: str = "prod-app-01", window_minutes: int = 240) -> str:
    """Retrieve recent log entries for `server_id` as newline-delimited text.

    Use this when you need raw operational telemetry, including timestamps and
    severity levels, to explain an outage or anomaly. Provide the server ID (for
    example `prod-app-01`) and optionally adjust the lookback window in minutes.
    The tool loads curated CloudFront-style logs when present and otherwise
    falls back to synthetic events so the agent always receives context.
    """

    return fetch_logs(server_id, window_minutes=window_minutes, config=_ACTIVE_CONFIG)


def summarize_utilization(hours: int = 24, include_recent: int = 6) -> Dict[str, Any]:
    """Compute CPU and memory utilization statistics over the last `hours`.

    Use this when you need quantitative evidence for capacity planning or SLA
    reviews. The tool responds with averages, peaks, and a small sample of the
    most recent observations (ISO-8601 timestamps plus percentage values).
    Data come from prepared NAB metrics tables when available, otherwise from
    deterministic synthetic metrics, keeping outputs consistent across runs.
    """

    df = summarize_metrics(hours=hours, config=_ACTIVE_CONFIG)
    window = df.tail(include_recent)
    return {
        "hours_evaluated": hours,
        "average_cpu_pct": round(float(df["cpu_pct"].mean()), 2),
        "peak_cpu_pct": round(float(df["cpu_pct"].max()), 2),
        "average_memory_pct": round(float(df["memory_pct"].mean()), 2),
        "peak_memory_pct": round(float(df["memory_pct"].max()), 2),
        "recent_samples": [
            {
                "timestamp": sample["timestamp"].isoformat() if hasattr(sample["timestamp"], "isoformat") else str(sample["timestamp"]),
                "cpu_pct": round(float(sample["cpu_pct"]), 2),
                "memory_pct": round(float(sample["memory_pct"]), 2),
            }
            for sample in window.to_dict(orient="records")
        ],
    }


def fetch_incident_digest() -> str:
    """Return the latest support ticket or incident email for escalation context.

    Use this when stakeholder messaging or customer-facing summaries are
    required. The tool surfaces a subject line and body sourced from processed
    tickets when available and otherwise synthesizes a realistic SEV2 update so
    remediation planning can continue without production data.
    """

    return fetch_recent_ticket(config=_ACTIVE_CONFIG)


def build_data_tools() -> List[FunctionTool]:
    """Create `FunctionTool` instances for the observability data utilities."""

    return [
        FunctionTool(fetch_server_logs),
        FunctionTool(summarize_utilization),
        FunctionTool(fetch_incident_digest),
    ]
