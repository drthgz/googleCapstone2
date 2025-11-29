# Rubric Coverage Plan

This document maps the Enterprise Agents rubric and bonus criteria to concrete deliverables in the project. It serves as a tracking sheet for implementation and the final submission write-up.

## Summary Table
| Rubric Area | Requirement | Planned Implementation | Status |
| --- | --- | --- | --- |
| **Core Concept & Value** | Clear problem and value proposition | Documented in README problem statement, mission background, and success metrics. | ✅ Complete |
| **Technical Implementation** | Multi-agent system demonstrating ≥3 key concepts | Supervisor + specialists (logs, metrics, operations) with tool ecosystem; see architecture doc. | ✅ Designed |
|  | Tools (custom/built-in) | `fetch_server_logs`, `get_cpu_utilization`, `read_incident_emails`, upcoming SLA & historical lookup tools. | 🔄 In progress |
|  | Sessions & Memory | ADK session usage with plan to add memory service for historical comparisons. | 🔄 In progress |
|  | Observability (logging/tracing/metrics) | Structured logging, ADK tracing, run metrics; integration into evaluation scripts. | 🔄 In progress |
|  | Evaluation | Scenario replay notebook plus ADK eval harness measuring MTTR, SLO recall, forecast accuracy (see `docs/evaluation_plan.md`). | 🔄 In progress |
|  | Deployment | Try ADK web + Streamlit dashboard + Cloud Run containerization plan. | 🔄 In progress |
| **Documentation** | README + diagrams + setup instructions | README sections, `docs/architecture_overview.md`, `docs/data_sources.md`, future setup guide. | 🔄 In progress |
| **Bonus** | Gemini usage | Gemini 2.5 Flash Lite powering all agents. | ✅ Complete |
|  | Deployment evidence | Targeting Cloud Run / Streamlit walkthrough. | 🔄 Planned |
|  | Video submission | Script/storyboard to be produced after feature implementation. | 🔄 Planned |

## Action Checklist
- [ ] Build tool wrappers for SLA policy checks and historical memory retrieval.
- [ ] Implement ADK memory service integration (Firestore/AlloyDB) and update architecture doc once selected.
- [ ] Instrument runners with consistent logging/tracing output and capture screenshots for write-up.
- [ ] Create evaluation notebook / tests covering incidents, capacity forecasts, and SLA detection.
	- Incident replay suite (logs + tickets)
	- Capacity forecasting accuracy harness
	- SLA compliance verification scenarios
- [ ] Draft deployment guide (Streamlit + Cloud Run) with reproducible steps.
- [ ] Prepare documentation bundle: setup guide, architecture diagrams, evaluation summary.
- [ ] Outline LinkedIn blog (problem → architecture → results → lessons) and video script.

This mapping should be consulted before each implementation sprint to ensure work items align directly to rubric scoring. Update statuses and checklist items as features land.
