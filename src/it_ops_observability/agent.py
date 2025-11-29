"""Production agent factory for the IT observability workflow."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from google.adk.agents import Agent

from .tools import build_data_tools
from .tools import set_data_config
from .data_sources import DataConfig


DEFAULT_MODEL = "gemini-2.5-flash-lite"


@dataclass
class AgentSettings:
    """Runtime settings for constructing the observability agents."""

    model_name: str = DEFAULT_MODEL
    data_config: Optional[DataConfig] = None


def create_supervisor_agent(settings: AgentSettings | None = None) -> Agent:
    """Create the top-level supervisor agent with all specialist sub-agents.

    The returned agent orchestrates three specialists:
      * A log analyst that inspects infrastructure logs.
      * A metric analyst that quantifies utilization trends.
      * An operations planner that synthesizes remediation guidance.

    Each specialist receives the FunctionTool wrappers defined in
    `build_data_tools`, giving the workflow resilient access to real or
    synthetic datasets depending on the environment.
    """

    settings = settings or AgentSettings()
    set_data_config(settings.data_config)
    log_tool, metric_tool, ticket_tool = build_data_tools()

    log_agent = Agent(
        name="log_analyst",
        model=settings.model_name,
        instruction=(
            "You triage infrastructure logs to spot correlated errors,"
            " summarize bursts, and highlight root-cause clues with citations."
        ),
        tools=[log_tool],
    )

    metric_agent = Agent(
        name="metric_analyst",
        model=settings.model_name,
        instruction=(
            "You analyze CPU and memory time series to explain utilization,"
            " capacity risks, and SLA/SLO drift with quantitative evidence."
        ),
        tools=[metric_tool],
    )

    operations_agent = Agent(
        name="operations_planner",
        model=settings.model_name,
        instruction=(
            "You design mitigation and communication plans by combining log"
            " anomalies, utilization trends, and stakeholder tickets."
            " Recommend windows, owners, and customer messaging."
        ),
        tools=[metric_tool, ticket_tool],
    )

    supervisor_agent = Agent(
        name="it_ops_supervisor",
        model=settings.model_name,
        instruction=(
            "You coordinate observability specialists to answer leadership"
            " questions about reliability and customer impact. Trigger"
            " the right tools, request details from sub-agents, and deliver"
            " an actionable summary with next steps."
        ),
        sub_agents=[log_agent, metric_agent, operations_agent],
    )

    return supervisor_agent
