"""Streamlit UI for the Enterprise IT Operations supervisor."""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import streamlit as st
from dotenv import load_dotenv
from google.adk.models.google_llm import _ResourceExhaustedError
from google.adk.runners import InMemoryRunner

from it_ops_observability import AgentSettings, create_supervisor_agent

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

if use_defaults:
    st.session_state.prompt_block = "\n".join(DEFAULT_SCENARIO)

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