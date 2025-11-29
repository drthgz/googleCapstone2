# Architecture Overview

This document summarizes how the Enterprise IT Operations Agent is structured, including agent hierarchy, tool interfaces, state management, observability, and deployment touchpoints.

## High-Level Diagram
```
┌──────────────────────────────────────────────────────────────────────┐
│                          Enterprise Stakeholders                     │
│                 (Execs, SRE leads, Incident Managers)                │
└───────────────┬──────────────────────────────┬───────────────────────┘
                │                              │
        Gradio / Try ADK UI            Session API / Streamlit (future)
                │                              │
┌───────────────▼──────────────────────────────▼──────────────────────┐
│                     Supervisor Agent: it_ops_supervisor             │
│  - Model: gemini-2.5-flash-lite                                     │
│  - Responsibilities: interpret intent, delegate to specialists,     │
│    synthesize executive summaries, orchestrate remediation plans.   │
└───────────────┬──────────────────────────────┬──────────────────────┘
                │                              │
     ┌──────────▼────────┐            ┌────────▼─────────┐            ┌────────▼─────────┐
     │ Log Analyst Agent │            │ Metric Analyst   │            │ Operations Planner│
     │ - fetch_server_   │            │ - get_cpu_       │            │ - get_cpu_       │
     │   logs tool       │            │   utilization tool│           │   utilization tool│
     │ - Email parsers   │            │ - Forecast helper│            │ - read_incident_  │
     │ - Trend scoring   │            │ - Anomaly labels │            │   emails tool     │
     └──────────┬────────┘            └────────┬─────────┘            └────────┬─────────┘
                │                              │                              │
       ┌────────▼────────┐            ┌────────▼─────────┐            ┌────────▼─────────┐
       │ Data Access &   │            │ Metrics Store &  │            │ Ticket DB &      │
       │ Preprocessing   │            │ Synthetic Spikes │            │ Synthetic emails │
       │ - Cloudfront    │            │ - NAB datasets   │            │ - Support tickets│
       │   logs          │            │ - Rolling stats  │            │ - Vendor alerts  │
       └─────────────────┘            └──────────────────┘            └──────────────────┘
```

## Agent Hierarchy
- **Supervisor (`it_ops_supervisor`)**
  - Handles user intent classification (incident triage, capacity review, SLA audit).
  - Delegates to specialists based on task requirements.
  - Consolidates tool outputs into a single narrative with recommendations.
- **Log Analyst (`log_analyst`)**
  - Consumes normalized log text, detects anomalies, highlights root causes.
  - Uses `fetch_server_logs` tool plus planned email parsing tool.
- **Metric Analyst (`metric_analyst`)**
  - Computes rolling statistics, forecasts resource usage, flags SLO breaches.
  - Uses `get_cpu_utilization` tool with future forecasting extension.
- **Operations Planner (`operations_planner`)**
  - Reads incident emails/tickets, coordinates remediation windows, crafts stakeholder messaging.
  - Uses both metric stats and incident communications to recommend actions.

## Tooling Layer
| Tool | Purpose | Inputs | Outputs | Notes |
| --- | --- | --- | --- | --- |
| `fetch_server_logs` | Retrieve latest log window for a given server or service. | `server_id`, `window_minutes` | Raw log text | Will expand to support filters (severity, component) and S3-based retrieval. |
| `get_cpu_utilization` | Summarize CPU/memory peaks, averages, and anomalies. | `time_range` | Stats dict + trend commentary | Future: integrate Prophet/ARIMA forecast tool. |
| `read_incident_emails` | Provide latest customer/vendor communications. | Optional filters (severity, source) | Email body text | To be extended with semantic search across ticket archive. |
| *Planned:* `assess_sla_policy` | Compare metric/log findings against SLA/OLAs. | Incident context | Pass/fail with rationale | Will use policy templates stored in config. |
| *Planned:* `historical_lookup` | Retrieve similar incidents from memory store. | Feature vector / incident metadata | Summaries of prior mitigations | Requires vector database or ADK memory service. |

## Session & Memory Strategy
- **Short-term state:** Managed via ADK sessions so that follow-up questions reuse context.
- **Long-term memory (planned):**
  - Utilize ADK memory service (Firestore/AlloyDB) to store incident summaries and remediation outcomes.
  - Expose retrieval tool (`historical_lookup`) allowing agents to compare current incidents with prior cases.
- **Context compaction:** Supervisor will employ context compaction for long conversations, storing transcripts in artifacts for post-mortem analysis.

## Observability
- **Logging:** Instrument agents and tools with structured logging via Python `logging` module.
- **Tracing:** Use ADK’s built-in tracing hooks to record agent call chains, accessible via Try ADK UI.
- **Metrics:** Publish run-level metrics (latency, tool error rate, SLA detection accuracy) to console/logs; roadmap includes exporting to Cloud Monitoring when deployed.

## Evaluation Plan (Preview)
- `tests/evaluation/` will contain:
  - Scenario scripts that replay historical incidents using the Kaggle datasets.
  - Assertions on success metrics (MTTR, recall, forecast accuracy).
  - Benchmarks comparing synthetic vs real data runs.

## Deployment Targets
- **Prototype:** Jupyter notebook + Gradio chat + Try ADK web (already scaffolded).
- **Next stage:** Package as Python module for `adk web` and containerize for Cloud Run.
- **Streamlit rationale:** Streamlit offers a Python-native path to a polished dashboard—ideal for rapidly exposing the multi-agent workflow to stakeholders without front-end engineering. It reuses our existing analytics code, supports charts and controls out of the box, and can be deployed to Streamlit Cloud or Cloud Run for rubric-ready demonstrations.
- **Future:** Streamlit UI with authenticated access and scheduled batch runs for capacity reports.

## Open Questions
- Which memory backend (Firestore vs AlloyDB vs local vector store) offers best balance for the capstone timeline?
- Are additional agents (e.g., cost optimization, compliance auditor) necessary for rubric bonus points or better avoided to maintain focus?
- How deeply should the forecasting tool integrate (basic stats vs ML model) given time constraints?

This overview will evolve as implementation proceeds; major updates will be reflected both here and in the planning checklist.
