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
- **Notebook:** `notebooks/evaluation/run_evaluation.ipynb` (to be created) orchestrates the three scenarios and logs metrics.
- **CLI Tests:** Future pytest suite under `tests/evaluation/` for automated regression.
- **ADK Evaluation Hooks:** Leverage `runner.run_debug` traces and artifacts for auditable logs.
- **Reporting:** Export JSON/Markdown summaries to `reports/evaluation/` for inclusion in README/blog.

## Execution Schedule
- Complete data preprocessing scripts before running evaluations.
- Run full evaluation prior to code freeze; re-run after major agent/tool changes.
- Archive results with timestamped filenames and note them in `history.d`.

## Evidence Collection
- Capture screenshots or screen recordings of Try ADK web/Streamlit interactions during evaluation runs.
- Store representative responses (with prompt/context) in `reports/evaluation/examples/`.
- Record evaluation metrics in a summary table for the Kaggle write-up and LinkedIn blog.

By following this plan, we ensure the project demonstrates measurable improvements and aligns tightly with the competition rubric.
