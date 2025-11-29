"""Generate an architecture diagram for the Enterprise IT Operations agent.

The diagram is rendered with Graphviz so we can regenerate it without using
GUI tools such as draw.io. Install dependencies and run:

    pip install graphviz
    sudo apt-get install graphviz  # or brew install graphviz on macOS
    PYTHONPATH=src python scripts/generate_architecture_diagram.py

The script emits both PNG and SVG versions under assets/ so they can be
embedded in documentation and slide decks.
"""
from __future__ import annotations

from pathlib import Path

from graphviz import Digraph


REPO_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = REPO_ROOT / "assets"
OUTPUT_BASENAME = "enterprise_it_ops_architecture"


def build_diagram() -> Digraph:
    """Create the agent + tool architecture diagram."""

    graph = Digraph("enterprise_it_ops", format="png")
    graph.attr(rankdir="TB", fontname="Helvetica", fontsize="12")

    # Entry points
    graph.node(
        "stakeholders",
        label="Enterprise Stakeholders\n(Execs, SRE leads, Incident Managers)",
        shape="box",
        style="rounded,filled",
        fillcolor="#EBF5FB",
    )

    graph.node(
        "interfaces",
        label="Interfaces\n- Gradio / Try ADK UI\n- Streamlit dashboard (planned)",
        shape="box",
        style="rounded",
    )

    graph.edge("stakeholders", "interfaces")

    # Supervisor cluster
    supervisor_cluster = Digraph(name="cluster_supervisor")
    supervisor_cluster.attr(label="Supervisor Layer", style="rounded")
    supervisor_cluster.node(
        "supervisor",
        label="it_ops_supervisor\nGemini 2.5 Flash Lite",
        shape="box",
        style="filled",
        fillcolor="#D6EAF8",
    )
    graph.subgraph(supervisor_cluster)

    # Specialist agents
    specialists_cluster = Digraph(name="cluster_specialists")
    specialists_cluster.attr(label="Specialist Agents", style="rounded")
    specialists_cluster.node(
        "log_analyst",
        label="log_analyst\n- fetch_server_logs",
        shape="box",
    )
    specialists_cluster.node(
        "metric_analyst",
        label="metric_analyst\n- summarize_utilization",
        shape="box",
    )
    specialists_cluster.node(
        "operations_planner",
        label="operations_planner\n- fetch_incident_digest",
        shape="box",
    )
    graph.subgraph(specialists_cluster)

    graph.edge("interfaces", "supervisor", label="prompts + follow-ups")
    graph.edge("supervisor", "log_analyst", label="delegate")
    graph.edge("supervisor", "metric_analyst", label="delegate")
    graph.edge("supervisor", "operations_planner", label="delegate")

    # Data/tool layer
    tools_cluster = Digraph(name="cluster_tools")
    tools_cluster.attr(label="Observability Tooling", style="rounded")
    tools_cluster.node(
        "logs",
        label="fetch_server_logs\nCloudFront + synthetic logs",
        shape="box",
    )
    tools_cluster.node(
        "metrics",
        label="summarize_utilization\nNAB metrics + synthetic",
        shape="box",
    )
    tools_cluster.node(
        "tickets",
        label="fetch_incident_digest\nSupport tickets + synthetic",
        shape="box",
    )
    graph.subgraph(tools_cluster)

    graph.edge("log_analyst", "logs", label="FunctionTool")
    graph.edge("metric_analyst", "metrics", label="FunctionTool")
    graph.edge("operations_planner", "tickets", label="FunctionTool")

    # Outputs
    graph.node(
        "outputs",
        label="Outputs\n- Leadership summaries\n- Risk assessments\n- Action plans",
        shape="box",
        style="rounded,filled",
        fillcolor="#E8F8F5",
    )
    graph.edge("supervisor", "outputs", label="synthesize")

    return graph


def main() -> None:
    ASSETS_DIR.mkdir(exist_ok=True)
    graph = build_diagram()

    png_path = ASSETS_DIR / f"{OUTPUT_BASENAME}.png"
    svg_path = ASSETS_DIR / f"{OUTPUT_BASENAME}.svg"

    graph.render(filename=OUTPUT_BASENAME, directory=str(ASSETS_DIR), cleanup=True)

    print(f"Generated diagram: {png_path}")
    if svg_path.exists():
        print(f"Generated diagram: {svg_path}")


if __name__ == "__main__":
    main()
