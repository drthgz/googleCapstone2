# Data Sources & Ingestion Plan

This document captures the finalized datasets that power the Enterprise IT Operations Agent and the operational steps required to keep them reproducible.

## Overview
- **Primary modes:** Web access logs, infrastructure metrics, support communications, and synthetic augmentation.
- **Storage convention:** Raw downloads live under `data/raw/<modality>/`, processed artifacts under `data/processed/<modality>/`, and synthetic material under `data/synthetic/`.
- **Governance:** Each dataset includes license notes, update cadence, and preprocessing scripts referenced from the `scripts/` directory.

## Selected Datasets

| Modality | Kaggle Slug | Purpose | Local Path | Preprocessing Tasks | Notes |
| --- | --- | --- | --- | --- | --- |
| Cloud access logs | `paultimothymooney/amazon-cloudfront-logs` | Populate the Log Analyst agent with real HTTP request traffic, status codes, and edge metadata. | `data/raw/logs/cloudfront/` | Convert tab-delimited logs to Parquet, normalize timestamps to UTC, sample 7-day windows, tag known incident windows. | Public domain sample logs released for analytics training; keep only anonymized fields. |
| Infrastructure metrics | `numenta/NAB` | Provide CPU/memory time series for the Metric Analyst, including labeled anomalies for evaluation. | `data/raw/metrics/nab/` | Extract `realAWSCloudwatch` streams, resample to hourly cadence, add rolling statistics, split train/test windows. | NAB is open under Apache 2.0; document any derived features. |
| Support communications | `aslanahmedov/tech-support-ticket-classification` | Seed the Operations Planner agent with real-world ticket language to categorize severity and route actions. | `data/raw/communications/tickets/` | Clean HTML, detect language, classify severity labels, build embeddings cache for fast retrieval. | Dataset licensed for research; cite original author in documentation. |

## Synthetic Augmentation
- **Location:** `data/synthetic/`
- **Generators:** Implemented in `scripts/generate_synthetic_data.py` (to be authored). Modules cover:
  - **Incident emails:** Parameterized templates for vendor outages, customer escalations, and maintenance notifications.
  - **Database logs:** Multi-technology samples (Postgres, MySQL, MongoDB) emphasizing backup failures, replication lag, and access breaches.
  - **Resource spikes:** Procedural CPU/memory curves introducing burst patterns not present in NAB to stress-test forecasting.
- **Usage:** Synthetic data is blended with real samples during evaluation to ensure agents handle edge cases and legacy formats.

## Ingestion Workflow
1. **Authenticate to Kaggle:** Ensure `~/.kaggle/kaggle.json` is present or use environment tokens in Kaggle notebooks.
2. **Download:**
   ```bash
   kaggle datasets download -d paultimothymooney/amazon-cloudfront-logs -p data/raw/logs --unzip
   kaggle datasets download -d numenta/NAB -p data/raw/metrics --unzip
   kaggle datasets download -d aslanahmedov/tech-support-ticket-classification -p data/raw/communications --unzip
   ```
3. **Run preprocessing scripts:**
   ```bash
   python scripts/preprocess_cloudfront_logs.py
   python scripts/preprocess_nab_metrics.py
   python scripts/preprocess_support_tickets.py
   ```
4. **Validate:** Each script outputs schema summaries in `data/reports/` and logs to `history.d` when major updates occur.

## Compliance & Licensing
- Retain LICENSE or README files from each dataset within `data/raw/<modality>/LICENSE`.
- Cite dataset authors in project documentation and the final Kaggle submission write-up.
- Ensure no personally identifiable information (PII) is introduced during synthetic augmentation; all generated records must be fictional.

## Update Cadence
- Real datasets are static snapshots; re-download only if upstream authors publish revisions.
- Synthetic generators should be versioned via Git tags. Update the changelog whenever new templates or statistical profiles are introduced.

With these sources locked in, subsequent tasks can focus on tool wrappers, evaluation suites, and deployment without revisiting data provenance decisions.
