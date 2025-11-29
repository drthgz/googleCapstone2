# Evaluation Plan

This plan defines how we will measure the Enterprise IT Operations Agent against the success metrics and Kaggle rubric requirements.

## Objectives
- Validate that the multi-agent system reduces MTTR, detects SLA breaches, and produces executive-ready briefings within defined thresholds.
- Provide reproducible evidence (notebooks/tests) for the Kaggle submission, blog post, and video demo.

## Datasets & Fixtures
- **Real-world datasets:** CloudFront logs, NAB metrics, support ticket text (see `docs/data_sources.md`).
- **Synthetic augmentations:** Stress scenarios for rare outages, vendor incidents, and capacity bursts stored in `data/synthetic/`.
- **Evaluation splits:** Maintain train/test partitions or time windows for unbiased metrics, recorded in `data/processed/<modality>/meta.yaml` (to be generated).

## Test Scenarios
1. **Incident Triage Replay**
   - Inputs: Sampled log windows + aligned tickets from real datasets.
   - Expected outputs: Root cause summary, anomaly references, remediation steps.
   - Metrics: Response latency, coverage of key log lines, stakeholder summary length.
2. **Capacity Forecast Validation**
   - Inputs: NAB metric series and synthetic spikes.
   - Expected outputs: Forecasted CPU/memory usage with risk classification.
   - Metrics: MAPE ≤ 15%, timely flagging of predicted breaches.
3. **SLA Compliance Audit**
   - Inputs: Aggregated telemetry & policy definitions.
   - Expected outputs: Pass/fail per SLA with rationale paragraphs.
   - Metrics: Recall ≥ 90%, false positives ≤ 10%.
4. **Executive Briefing Quality**
   - Inputs: Combined incident context.
   - Expected outputs: ≤3 paragraph summary + actionable bullet list.
   - Metrics: Manual checklist (clarity, actionability), optional LLM evaluation rubric.

## Tooling & Automation
- **Notebook:** `notebooks/evaluation/run_evaluation.ipynb` shells out to the production runner, ensuring the supervised prompts and transcript can be regenerated after sourcing `.env`. Execute the notebook after activating the virtualenv; the single code cell will load env vars, set `PYTHONPATH=src`, and call `python scripts/run_adk_supervisor.py --verbose` with the standard prompt sequence. Archive the STDOUT in `reports/evaluation/examples/` for traceability.
- **CLI Tests:** Future pytest suite under `tests/evaluation/` for automated regression.
- **ADK Evaluation Hooks:** Leverage `runner.run_debug` traces and artifacts for auditable logs.
- **Reporting:** Export JSON/Markdown summaries to `reports/evaluation/` for inclusion in README/blog.
- **Example Transcript:** `scripts/quick_supervisor_demo.py` prints the agent hierarchy alongside sample outputs from each data tool. A recent run produced:

   ```text
   Agent hierarchy:

   - it_ops_supervisor [LlmAgent]
      - log_analyst [LlmAgent]
         tools: fetch_server_logs
      - metric_analyst [LlmAgent]
         tools: summarize_utilization
      - operations_planner [LlmAgent]
         tools: summarize_utilization, fetch_incident_digest

   Tool samples:

   fetch_server_logs →
   2025-11-29T02:57:59.870599Z [INFO] prod-app-01: Health check passed | 2025-11-29T03:02:59.870599Z [WARN] prod-app-01: CPU utilization approaching threshold |…

   summarize_utilization →
   {'hours_evaluated': 12, 'average_cpu_pct': 55.01, 'peak_cpu_pct': 75.94, 'average_memory_pct': 62.76, 'peak_memory_pct': 78.73, 'recent_samples': [{'timestamp': '2025-11-29T01:52:59.870673', 'cpu_pct': 57.09, 'memory_pct': 45.56}, {'timestamp': '2025-11-29T02:52:59.870673', 'cpu_pct': 59.18, 'memory_pct': 59.25}, {'timestamp': '2025-11-29T03:52:59.870673', 'cpu_pct': 75.94, 'memory_pct': 68.88}]}

   fetch_incident_digest →
   Subject: SEV2 Network Incident Update
   From: it-operations@company.com
   Body: Network team reports anomalies impacting customer latency. Suggested remediation window: 00:00-02:00 UTC.
   ```

   This lightweight smoke check demonstrates the supervisor wiring, tool descriptions, and synthetic fallbacks without needing live Gemini calls.
- **Gemini Backed Run:** `scripts/run_adk_supervisor.py --verbose` executes the full ADK runner with Gemini credentials. Example sequence (after loading `.env`):

   ```text
   User > Give me an ops briefing: what happened overnight, what are the top risks, and what should leadership do next?
   log_analyst > [Calling tool: fetch_server_logs(...)]
   log_analyst > Here's a summary of the key log anomalies for prod-app-01 overnight:
         • Disk saturation beyond 95% at 01:36Z, 02:21Z, 02:41Z
         • Database connection timeouts at 02:01Z and 03:31Z/03:41Z
         • Service mesh circuit breaker open events at 02:26Z and 02:46Z
         • Repeated WARN entries for CPU thresholds, replica lag, and latency spikes
      Top risks: service outage, performance degradation, data integrity issues
      Leadership actions: investigate disk/database health, scale resources, review mesh config

   User > Provide the utilization stats and risks.
   metric_analyst > [Calling tool: summarize_utilization(...)]
   metric_analyst > Over the last 24 hours CPU averaged 54.83% (peak 78.6%) and memory averaged 62.34% (peak 73.51%). Recent samples show CPU 63.83% / memory 68.74%.
      Top risks: outage from saturation + DB instability, performance drag, integrity concerns
      Leadership actions: allocate resources, stabilize DB, continue observability sweeps
   ```

   The transcript will be archived under `reports/evaluation/examples/` for the final submission package.

## Execution Schedule
- Complete data preprocessing scripts before running evaluations.
- Run full evaluation prior to code freeze; re-run after major agent/tool changes.
- Archive results with timestamped filenames and note them in `history.d`.

## Evidence Collection
- Capture screenshots or screen recordings of Try ADK web/Streamlit interactions during evaluation runs.
- Store representative responses (with prompt/context) in `reports/evaluation/examples/`.
- Record evaluation metrics in a summary table for the Kaggle write-up and LinkedIn blog.
- Current assets: [../assets/screenshots/evaluation_notebook_run.png](../assets/screenshots/evaluation_notebook_run.png) (notebook run), [../assets/screenshots/pytest_pass.png](../assets/screenshots/pytest_pass.png) (pytest summary), [../assets/enterprise_it_ops_architecture.png](../assets/enterprise_it_ops_architecture.png) (architecture diagram).

By following this plan, we ensure the project demonstrates measurable improvements and aligns tightly with the competition rubric.
