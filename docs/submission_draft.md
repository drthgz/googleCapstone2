# Enterprise IT Operations Supervisor Agent

**Subtitle:** Multi-agent Gemini workflow for proactive incident command

**Track:** Enterprise Agents  
**Word count (approx.):** 1010

---

## Problem, Opportunity, and Value
Enterprise IT operations leaders still begin every major incident with a scavenger hunt. Logs, metrics, and stakeholder emails live in separate silos, so responders burn thirty minutes stitching together context before leadership even hears what went wrong. During that delay, SLA breaches accumulate, customers escalate, and planned capacity work falls off the radar. The human cost is equally high: on-call engineers juggle multiple dashboards while executives wait for answers that read more like raw telemetry than actionable guidance.

Our goal is to shrink that insight window to under five minutes while generating an executive-ready briefing automatically. If the agent can deliver a clear root-cause narrative, quantify the top risks, and recommend next steps in conversational language, leadership teams can redirect their focus from hunting for data to coordinating mitigation. Faster, more coherent briefings also reduce the likelihood of unforced SLA violations, improve stakeholder communication, and calm stressed on-call rotations.

Primary stakeholders include operations directors, service owners, SRE leads, and incident managers who need to translate observability signals into business-ready language on demand.

---

## Solution Overview
We built a Gemini-powered supervisor that behaves like an incident command lead. Executives ask high-level questions (“What happened overnight?” “What should leadership do next?”) and the supervisor delegates to three specialists focused on logs, metrics, and stakeholder communications. Each specialist reasons over structured FunctionTool outputs but responds with concise English summaries so non-ML audiences can follow along without deciphering prompts or JSON blobs.

All data access routes through tool adapters that prioritize live datasets when available and fall back to deterministic synthetic bursts otherwise. That design keeps demos reliable while still surfacing meaningful anomalies when real data is present. Every run emits a transcript to disk and passes automated tests, supplying auditable evidence that the workflow is repeatable. The same agent stack powers the CLI, pytest suite, and reproduction notebook, ensuring what judges read is the same flow we run locally.

Key source files:
- `src/it_ops_observability/agent.py` – supervisor and specialist definitions.
- `src/it_ops_observability/tools.py` – FunctionTool wrappers for logs, utilization, and incident digests.
- `scripts/run_adk_supervisor.py` – production runner used by the notebook, CLI, and transcript capture.

---

## Architecture & Key Concepts
The architecture mirrors an operations command center (diagram: `assets/enterprise_it_ops_architecture.png`). The supervisor owns the conversation with stakeholders while routing investigative steps to subordinate agents that invoke tools. This separation lets leadership stay in plain English while the system quietly scrapes logs, summarizes utilization data, or pulls stakeholder digests.

The project demonstrates four rubric pillars simultaneously:
1. **Multi-agent orchestration:** Sequential delegation from supervisor → specialists, with loopback for follow-up questions.
2. **Tool integration:** Custom FunctionTool wrappers for observability data ensure the LLM interacts with structured telemetry instead of hallucinating details.
3. **Context engineering & reliability:** Deterministic synthetic fallbacks guarantee consistent anomalies when real datasets are unavailable, keeping transcripts meaningful.
4. **Observability & evaluation:** Automated transcripts, regression tests, timing metrics, and archived artifacts show the system behaves consistently across runs.

Future-facing hooks (documented in `docs/architecture_overview.md`) outline how memory services, Streamlit dashboards, and Cloud Run deployment will extend the architecture without rewriting the agent hierarchy.

---

## Data Sources & Synthetic Augmentation
Evidence comes from a blend of public datasets and deterministic scenarios:
- **CloudFront logs** (`paultimothymooney/amazon-cloudfront-logs`) expose HTTP anomalies for log analysis.
- **Numenta Anomaly Benchmark (NAB)** metrics provide seasonality and spikes for capacity planning.
- **Tech support ticket corpora** (`aslanahmedov/tech-support-ticket-classification`) capture stakeholder language for the communications agent.

When a machine lacks the raw datasets, synthetic bursts keep the briefing vivid so the demo never falls flat. The synthetic helpers power the unit tests, CLI runner, and evaluation notebook, guaranteeing that judges review the same narratives we produce locally. Implementation details live in `docs/data_sources.md` and `src/it_ops_observability/synthetic.py`.

---

## Implementation Highlights
- **Supervisor CLI and Notebook:** `scripts/run_adk_supervisor.py --verbose` drives the full ADK InMemoryRunner with Gemini. The evaluation notebook (`notebooks/evaluation/run_evaluation.ipynb`) shells out to this script, captures stdout/stderr, and stores transcripts under `reports/evaluation/examples/`.
- **Lightweight Demo Script:** `scripts/quick_supervisor_demo.py` prints the agent tree plus sample tool outputs without making live API calls—ideal for smoke tests.
- **Reproducible Artifacts:** Architecture diagram and screenshots are generated programmatically (`scripts/generate_architecture_diagram.py` and `assets/screenshots/`). Every substantive run and measurement is logged in `history.d` or `reports/evaluation/examples/` for auditability.
- **Streamlined UI:** `ui/streamlit_app.py` provides a browser-based command center so stakeholders can run the supervisor, view transcripts, and capture screenshots without touching the CLI.

---

## Evaluation & Metrics
Evaluation focuses on whether the system actually accelerates incident response and produces leadership-ready language.

**Automated Tests & Timings (captured 2025-11-29):**
- `tests/test_runner.py::test_supervisor_runner_outputs_summary` confirms the end-to-end supervisor flow with Gemini; pytest completes in **10.68 s** wall time (`PYTHONPATH=src pytest tests/test_runner.py -q --durations=5`).
- CLI supervisor run measured via `/usr/bin/time` completes in **10.01 s** real time (3.49 s user / 0.09 s sys) while generating a full transcript (`reports/evaluation/examples/2025-11-28_adk_supervisor_verbose_run_v2.txt`).
- Tool smoke tests live in `tests/test_tools.py` and confirm deterministic outputs for each FunctionTool wrapper.

**Utilization Snapshot:** `summarize_utilization(hours=24)` reports **avg CPU 54.83% / peak 78.60%** and **avg memory 62.34% / peak 73.51%** across the last 24 synthetic hours (artifact: `reports/evaluation/examples/metrics_2025-11-29.json`). These numbers feed the README evidence table and provide quantitative context for the leadership briefings.

**Artifacts & Screenshots:**
- Notebook run capture: `assets/screenshots/evaluation_notebook_run.png`.
- Pytest summary capture: `assets/screenshots/pytest_pass.png`.
- Metrics JSON: `reports/evaluation/examples/metrics_2025-11-29.json`.

Together, these assets demonstrate that the agent reliably produces value, and they give reviewers a clear trail to reproduce the results.

---

## Deployment & Cost Considerations
The deployment roadmap (see `docs/deployment_strategy.md`) targets three surfaces:
1. **Try ADK Web / Gradio Prototype:** Already functional for supervised demos.
2. **Streamlit Dashboard (planned):** Provides an authenticated executive view that reuses the existing Python code path without front-end engineering overhead.
3. **Cloud Run (future):** Containerized Streamlit or ADK service with secure secret management and Cloud Monitoring hooks.

Cost assumptions (documented in `docs/cost_estimate.md`) rely on free-tier GPU/CPU usage for development plus measured Gemini API consumption for the supervisor calls. We track these assumptions to set expectations for enterprise adoption.

---

## Lessons Learned & Future Work
- **Deterministic fallbacks matter:** Synthetic bursts ensured that every demo run surfaced meaningful incidents without chasing dataset permissions.
- **Transcript automation builds trust:** Capturing stdout/stderr alongside runtime metrics provided immediate evidence for the Kaggle rubric and internal stakeholders.
- **Tool-first design scales:** By isolating data access in FunctionTool wrappers, we can add new modalities (e.g., SLA policy checks, vector memory lookups) without refactoring prompts.

Planned next steps include: implementing the Streamlit dashboard, wiring ADK memory services for historical incident comparisons, and recording the short video demo that walks through the architecture and live agent run.

---

## Submission Checklist
- [x] Narrative drafted within the 1,500-word limit.
- [x] Architecture diagram embedded (`assets/enterprise_it_ops_architecture.png`).
- [x] Evidence linked (screenshots, transcript, metrics JSON, pytest timings).
- [ ] Record <3 minute demo video (scheduled for next working session).
- [ ] Final proofreading and word-count verification before Kaggle submission.
