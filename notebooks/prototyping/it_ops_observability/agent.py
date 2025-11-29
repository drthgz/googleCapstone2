
    Multi-agent IT observability system for ADK Web.

    from __future__ import annotations

    import random
    from datetime import datetime, timedelta
    from typing import Literal

    import pandas as pd

    from google.adk.agents import Agent
    from google.adk.tools import FunctionTool

    MODEL_NAME = "gemini-2.5-flash-lite"

    SEVERITIES = ["CRITICAL", "ERROR", "WARN", "INFO"]
    INCIDENT_TYPES = ["Network", "Database", "Application", "Infrastructure"]


    def generate_mock_logs(server_id: str, window_minutes: int = 240) -> str:
        """Create timestamped log entries with realistic error bursts."""
        now = datetime.utcnow()
        entries: list[str] = []
        for minute in range(window_minutes // 5):
            timestamp = now - timedelta(minutes=minute * 5)
            level = random.choices(SEVERITIES, weights=[0.05, 0.15, 0.3, 0.5])[0]
            if level in {"CRITICAL", "ERROR"}:
                message = random.choice(
                    [
                        "Latency spike detected on API Gateway",
                        "Database connection timeout",
                        "Disk saturation beyond 95%",
                        "Service mesh circuit breaker open",
                    ]
                )
            elif level == "WARN":
                message = random.choice(
                    [
                        "Retrying connection to cache cluster",
                        "CPU utilization approaching threshold",
                        "Replica lag increasing",
                    ]
                )
            else:
                message = random.choice(
                    [
                        "Health check passed",
                        "Autoscaler polling",
                        "Background job completed",
                    ]
                )
            entries.append(f"{timestamp.isoformat()}Z [{level}] {server_id}: {message}")
        return "
".join(reversed(entries))


    def generate_mock_metrics(hours: int = 24) -> pd.DataFrame:
        """Return hourly CPU/memory stats with spikes to trigger SLA alerts."""
        now = datetime.utcnow()
        cpu = [max(10, min(99, random.gauss(55, 18))) for _ in range(hours)]
        memory = [max(20, min(95, random.gauss(63, 12))) for _ in range(hours)]
        return pd.DataFrame(
            {
                "timestamp": [now - timedelta(hours=h) for h in range(hours)][::-1],
                "cpu_pct": cpu,
                "memory_pct": memory,
            }
        )


    def generate_incident_email(severity: Literal["SEV1", "SEV2", "SEV3"]) -> str:
        incident = random.choice(INCIDENT_TYPES)
        window = random.choice(["00:00-02:00 UTC", "02:00-04:00 UTC", "Maintenance window TBD"])
        return (
            f"Subject: {severity} {incident} Incident Update
"
            f"From: it-operations@company.com
"
            f"Body: {incident} team reports anomalies impacting customer latency."
            f" Suggested remediation window: {window}."
        )


    def fetch_logs_tool(server_id: str = "prod-app-01") -> str:
        """Return recent log entries for a server."""
        return generate_mock_logs(server_id)


    def summarize_utilization(time_range: str = "last_24h") -> dict:
        """Provide aggregate CPU/Memory stats for the requested window."""
        df = generate_mock_metrics()
        return {
            "time_range": time_range,
            "average_cpu_pct": round(df["cpu_pct"].mean(), 2),
            "peak_cpu_pct": round(df["cpu_pct"].max(), 2),
            "average_memory_pct": round(df["memory_pct"].mean(), 2),
        }


    def fetch_latest_incident() -> str:
        """Return the latest synthetic incident email for context."""
        return generate_incident_email("SEV2")


    def create_agent() -> Agent:
        """Expose the supervisor agent for ADK web."""
        fetch_server_logs = FunctionTool(fetch_logs_tool)
        get_cpu_utilization = FunctionTool(summarize_utilization)
        read_incident_emails = FunctionTool(fetch_latest_incident)

        log_agent = Agent(
            name="log_analyst",
            model=MODEL_NAME,
            instruction=(
                "You inspect raw infrastructure logs to detect anomalies, downtime, and root causes."
                " Summarize key findings and cite log fragments."
            ),
            tools=[fetch_server_logs],
        )

        metric_agent = Agent(
            name="metric_analyst",
            model=MODEL_NAME,
            instruction=(
                "You analyze time-series metrics to explain utilization trends, SLA breaches, and capacity risks."
                " Produce concise stats and recommendations."
            ),
            tools=[get_cpu_utilization],
        )

        operations_agent = Agent(
            name="operations_planner",
            model=MODEL_NAME,
            instruction=(
                "You coordinate remediation windows, patching schedules, and scaling plans using inputs from peers."
                " Recommend low-impact execution windows and stakeholder messaging."
            ),
            tools=[get_cpu_utilization, read_incident_emails],
        )

        supervisor_agent = Agent(
            name="it_ops_supervisor",
            model=MODEL_NAME,
            instruction=(
                "You orchestrate specialists to answer executive questions about reliability and performance."
                " Decide when to call sub-agents and synthesize a single actionable response."
            ),
            sub_agents=[log_agent, metric_agent, operations_agent],
        )

        return supervisor_agent
