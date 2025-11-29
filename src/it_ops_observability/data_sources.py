"""Data access helpers for the IT observability agents."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd

from . import synthetic


@dataclass
class DataConfig:
    """Configuration for locating processed datasets.

    All paths are optional; when a dataset is unavailable, the agents fall back to
    synthetic data so the system remains runnable in constrained environments
    (e.g., Kaggle notebooks without the large Kaggle datasets preloaded).
    """

    logs_path: Optional[Path] = None
    metrics_path: Optional[Path] = None
    tickets_path: Optional[Path] = None


DEFAULT_DATA_ROOT = Path(__file__).resolve().parents[2] / "data"
DEFAULT_CONFIG = DataConfig(
    logs_path=DEFAULT_DATA_ROOT / "processed" / "logs" / "cloudfront_sample.parquet",
    metrics_path=DEFAULT_DATA_ROOT / "processed" / "metrics" / "nab_sample.parquet",
    tickets_path=DEFAULT_DATA_ROOT / "processed" / "communications" / "tickets_sample.parquet",
)


def _resolve_path(path: Optional[Path]) -> Optional[Path]:
    if path is None:
        return None
    if path.exists():
        return path
    return None


def fetch_logs(server_id: str, *, window_minutes: int = 240, config: DataConfig = DEFAULT_CONFIG) -> str:
    """Return log events for the requested server, falling back to synthetic data."""
    logs_path = _resolve_path(config.logs_path)
    if logs_path is not None:
        try:
            df = pd.read_parquet(logs_path)
            df = df[df["server_id"].eq(server_id)].tail(window_minutes // 5)
            if not df.empty:
                return "\n".join(df["message"].tolist())
        except Exception:
            # Continue to synthetic fallback
            pass
    return synthetic.generate_mock_logs(server_id, window_minutes=window_minutes)


def summarize_metrics(*, hours: int = 24, config: DataConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    """Return metric data frame, either from disk or synthetic generation."""
    metrics_path = _resolve_path(config.metrics_path)
    if metrics_path is not None:
        try:
            df = pd.read_parquet(metrics_path)
            latest = df.tail(hours)
            if not latest.empty:
                return latest
        except Exception:
            pass
    return synthetic.generate_mock_metrics(hours=hours)


def fetch_recent_ticket(*, config: DataConfig = DEFAULT_CONFIG) -> str:
    """Return the latest support ticket/incident email."""
    tickets_path = _resolve_path(config.tickets_path)
    if tickets_path is not None:
        try:
            df = pd.read_parquet(tickets_path)
            if not df.empty:
                row = df.sample(1).iloc[0]
                subject = row.get("subject", "Support Ticket")
                body = row.get("body", row.get("message", ""))
                return f"Subject: {subject}\n{body}"
        except Exception:
            pass
    return synthetic.generate_incident_email("SEV2")
