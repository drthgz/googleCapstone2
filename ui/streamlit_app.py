"""Streamlit UI for the Enterprise IT Operations supervisor."""
from __future__ import annotations

import asyncio
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google.adk.models.google_llm import _ResourceExhaustedError
from google.adk.runners import InMemoryRunner

from it_ops_observability import AgentSettings, create_supervisor_agent
from it_ops_observability.tools import (
    fetch_incident_digest,
    fetch_server_logs,
    summarize_utilization,
)

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DEFAULT_SCENARIO: List[str] = [
    "Give me an ops briefing: what happened overnight, what are the top risks, and what should leadership do next?",
    "Investigate prod-app-01 with the default window and summarize key log anomalies.",
    "Provide the utilization stats and risks.",
    "Draft the leadership summary and actions.",
]

FRIENDLY_SENDER_NAMES = {
    "user": "Operations Leader",
    "it_ops_supervisor": "Supervisor Agent",
    "log_analyst": "Log Analyst Agent",
    "metric_analyst": "Metric Analyst Agent",
    "operations_planner": "Operations Planner Agent",
}

SEVERITY_ORDER = ["CRITICAL", "ERROR", "WARN", "INFO"]
SEVERITY_EMOJI = {
    "CRITICAL": "🚨",
    "ERROR": "❗",
    "WARN": "⚠️",
    "INFO": "ℹ️",
}


@dataclass
class TranscriptTurn:
    speaker: str
    text: str


def _merge_text(parts: Iterable[object]) -> str:
    chunks: List[str] = []
    for part in parts:
        text = getattr(part, "text", None)
        if text:
            chunks.append(text)
    return "\n\n".join(chunks)


def _extract_turns(events: Iterable[object]) -> List[TranscriptTurn]:
    turns: List[TranscriptTurn] = []
    for event in events:
        content = getattr(event, "content", None)
        if not content:
            continue
        parts = getattr(content, "parts", None)
        if not parts:
            continue
        text = _merge_text(parts)
        if not text.strip():
            continue
        sender = _resolve_sender(event)
        turns.append(TranscriptTurn(speaker=sender, text=text))
    return turns


def _resolve_sender(event: object) -> str:
    raw = getattr(event, "author", None)
    if raw is None:
        raw = getattr(event, "sender", None)
    agent_obj = getattr(event, "agent", None)
    if agent_obj is not None:
        raw = getattr(agent_obj, "name", raw) or getattr(agent_obj, "id", raw)
    if raw is None:
        raw = "agent"
    raw_str = str(raw)
    if raw_str in FRIENDLY_SENDER_NAMES:
        return FRIENDLY_SENDER_NAMES[raw_str]
    return raw_str.replace("_", " ").title()


def _parse_logs(raw: str) -> List[dict]:
    entries: List[dict] = []
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


@st.cache_data(show_spinner=False)
def _load_dashboard_snapshot(server_id: str, window_minutes: int) -> dict:
    summary = summarize_utilization(hours=24)
    logs_text = fetch_server_logs(server_id=server_id, window_minutes=window_minutes)
    digest = fetch_incident_digest()
    parsed_logs = _parse_logs(logs_text)
    severity_counts = Counter(entry["level"] for entry in parsed_logs)
    return {
        "summary": summary,
        "logs": parsed_logs,
        "digest": digest,
        "severity_counts": dict(severity_counts),
    }


def _run_supervisor(prompts: List[str], verbose: bool) -> List[TranscriptTurn]:
    async def _inner() -> List[TranscriptTurn]:
        runner = InMemoryRunner(agent=create_supervisor_agent(AgentSettings()))
        try:
            events = await runner.run_debug(prompts, verbose=verbose, quiet=True)
        finally:
            await runner.close()
        return _extract_turns(events)

    return asyncio.run(_inner())


st.set_page_config(
    page_title="Enterprise IT Ops Supervisor",
    page_icon="🛠️",
    layout="wide",
)

st.title("Enterprise IT Operations Supervisor")
st.markdown(
    """
This streamlined interface routes your prompts through the Gemini-backed supervisor.
Provide one prompt per line (defaults shown below), then launch the run to capture a
leadership-ready briefing along with specialist responses.
"""
)

if "prompt_block" not in st.session_state:
    st.session_state.prompt_block = "\n".join(DEFAULT_SCENARIO)

with st.sidebar:
    st.header("Run Settings")
    use_defaults = st.button("Reset to default prompts")
    verbose = st.checkbox("Verbose tool tracing", value=True)
    st.caption(
        "Set GOOGLE_API_KEY in your environment before running. Each run spins up\n"
        "a fresh InMemoryRunner so you get isolated transcripts."
    )
    raw_server_id = st.text_input(
        "Server ID",
        value=st.session_state.get("dashboard_server", "prod-app-01"),
        help="Choose which service to analyze in the dashboard and default prompts.",
    )
    server_id = raw_server_id or "prod-app-01"
    window_minutes = st.slider(
        "Log lookback (minutes)",
        min_value=60,
        max_value=720,
        step=60,
        value=st.session_state.get("dashboard_window", 240),
    )
    refresh_dashboard = st.button("Refresh telemetry", key="refresh_telemetry")

if use_defaults:
    st.session_state.prompt_block = "\n".join(DEFAULT_SCENARIO)

st.session_state["dashboard_server"] = server_id
st.session_state["dashboard_window"] = window_minutes

if refresh_dashboard:
    _load_dashboard_snapshot.clear()
    st.rerun()

prompt_block = st.text_area(
    "Prompts (one per line)",
    value=st.session_state.prompt_block,
    height=180,
)
run_clicked = st.button("Run supervisor", type="primary")

if run_clicked:
    prompts = [line.strip() for line in prompt_block.splitlines() if line.strip()]
    st.session_state.prompt_block = prompt_block
    if not prompts:
        st.warning("Please provide at least one prompt before running the supervisor.")
    elif not os.environ.get("GOOGLE_API_KEY"):
        st.error(
            "GOOGLE_API_KEY is not set. Update your .env file or export the variable before running."
        )
    else:
        with st.spinner("Contacting supervisor and agents..."):
            try:
                turns = _run_supervisor(prompts, verbose=verbose)
            except _ResourceExhaustedError as exc:  # pragma: no cover - quota guard
                st.error(
                    "Gemini quota exhausted. Please retry later or switch to a different "
                    "model tier."
                )
                st.session_state.latest_transcript = None
            except ValueError as exc:  # pragma: no cover - missing credentials
                st.error(
                    f"Supervisor run failed: {exc}. Ensure GOOGLE_API_KEY is set and valid."
                )
                st.session_state.latest_transcript = None
            except Exception as exc:  # pragma: no cover - unexpected errors
                st.error(f"Unexpected error while running supervisor: {exc}")
                st.session_state.latest_transcript = None
            else:
                st.session_state.latest_transcript = turns
                st.session_state.last_prompts = prompts
                st.session_state.last_verbose = verbose
                st.success("Run complete. Transcript captured below.")

turns: List[TranscriptTurn] | None = st.session_state.get("latest_transcript")

dashboard_error: Exception | None = None
snapshot: dict | None = None
try:
    snapshot = _load_dashboard_snapshot(server_id, window_minutes)
except Exception as exc:  # pragma: no cover - defensive catch
    dashboard_error = exc

overview_tab, transcript_tab = st.tabs(["Ops Dashboard", "Supervisor Transcript"])

with overview_tab:
    if dashboard_error:
        st.error(f"Unable to load dashboard data: {dashboard_error}")
    elif not snapshot:
        st.info("Dashboard data unavailable for the selected parameters.")
    else:
        summary = snapshot["summary"]
        hours_window = summary.get("hours_evaluated", 24)
        st.subheader(f"Resource Utilization · last {hours_window}h")
        metric_cols = st.columns(2)
        metric_cols[0].metric(
            "Average CPU",
            f"{summary.get('average_cpu_pct', 0)}%",
            delta=f"Peak {summary.get('peak_cpu_pct', 0)}%",
        )
        metric_cols[1].metric(
            "Average Memory",
            f"{summary.get('average_memory_pct', 0)}%",
            delta=f"Peak {summary.get('peak_memory_pct', 0)}%",
        )
        progress_cols = st.columns(2)
        cpu_progress = max(0, min(int(round(summary.get("average_cpu_pct", 0))), 100))
        mem_progress = max(0, min(int(round(summary.get("average_memory_pct", 0))), 100))
        progress_cols[0].progress(cpu_progress, text="Avg CPU (%)")
        progress_cols[1].progress(mem_progress, text="Avg Memory (%)")

        samples_df = pd.DataFrame(summary.get("recent_samples", []))
        if not samples_df.empty:
            samples_df["timestamp"] = pd.to_datetime(
                samples_df["timestamp"], errors="coerce"
            )
            samples_df = samples_df.dropna(subset=["timestamp"]).set_index("timestamp")
            st.line_chart(
                samples_df[["cpu_pct", "memory_pct"]],
                height=260,
            )
        else:
            st.info("No recent utilization samples available for charting.")

        st.subheader(f"Log Signals · {server_id} (last {window_minutes} min)")
        severity_counts = snapshot["severity_counts"]
        severity_cols = st.columns(len(SEVERITY_ORDER))
        for col, level in zip(severity_cols, SEVERITY_ORDER):
            emoji = SEVERITY_EMOJI.get(level, "")
            col.metric(f"{emoji} {level.title()}", severity_counts.get(level, 0))

        logs_df = pd.DataFrame(snapshot["logs"])
        if not logs_df.empty:
            logs_df["timestamp"] = pd.to_datetime(
                logs_df["timestamp"], errors="coerce"
            )
            display_df = logs_df.sort_values("timestamp", ascending=False).copy()
            display_df["level"] = (
                display_df["level"].fillna("INFO").astype(str).str.upper()
            )
            display_df["message"] = display_df["message"].fillna("").astype(str)
            display_df["display_ts"] = display_df["timestamp"].dt.strftime("%H:%M:%S")
            highlights = display_df.head(3)
            for _, row in highlights.iterrows():
                emoji = SEVERITY_EMOJI.get(row["level"], "•")
                st.markdown(
                    f"{emoji} **{row['level'].title()}** · "
                    f"{row['display_ts']} — {row['message']}"
                )
            st.dataframe(
                display_df[["display_ts", "level", "message"]]
                .head(12)
                .rename(columns={"display_ts": "timestamp"}),
                use_container_width=True,
                height=240,
            )
        else:
            st.success("No anomalies detected in the selected window.")

        st.subheader("Incident Communications")
        digest_text = snapshot.get("digest") or "No incident digest available."
        st.code(digest_text, language="text")

with transcript_tab:
    if turns:
        for idx, turn in enumerate(turns, start=1):
            st.markdown(f"### {idx}. {turn.speaker}")
            st.write(turn.text)
    elif turns is not None:
        st.info("No transcript text returned. Check verbose logs for tool output.")

    with st.expander("Execution details"):
        st.write(
            {
                "default_prompts": DEFAULT_SCENARIO,
                "last_prompts": st.session_state.get("last_prompts"),
                "verbose": st.session_state.get("last_verbose"),
            }
        )