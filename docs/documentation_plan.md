# Documentation Plan

This guide outlines all written deliverables required for the capstone submission, internal coordination, and public sharing (LinkedIn/blog/video).

## 1. Core Repository Docs
### README.md (current)
- Problem statement, success metrics, architecture snapshot.
- Links to supporting docs (data sources, architecture overview, evaluation plan, deployment strategy, cost estimate).
- Planning checklist, updated as tasks complete.
- **Action:** Keep README concise; link to detailed docs instead of duplicating content.

### docs/
- `mission_background.md`: narrative and motivation.
- `architecture_overview.md`: diagrams, agent flows, tooling layers, deployment roadmap.
- `data_sources.md`: ingestion plan with commands.
- `rubric_mapping.md`: requirements tracking.
- `evaluation_plan.md`: scenarios, metrics, automation plan.
- `deployment_strategy.md`: step-by-step rollout.
- `cost_estimate.md`: bill of materials and free tier guidance.
- **Upcoming:** `setup_guide.md` (detailed environment setup + Kaggle/Vertex authentication) and `submission_outline.md` (structure for Kaggle write-up).

## 2. Setup & Usage Guides
- **Local Setup Guide (`docs/setup_guide.md`, to be created):**
  - Python environment creation, dependency installation.
  - Google Cloud credential configuration (local + Kaggle secrets).
  - Data download scripts and preprocessing commands.
  - Running notebooks, evaluation suite, Streamlit app.
- **Deployment Guide (`docs/deployment_guide.md`, derived from deployment strategy):**
  - Step-by-step instructions with CLI commands for ADK web, Streamlit, Cloud Run.
  - Troubleshooting section (common errors, IAM permissions, token quotas).

## 3. Submission Materials
- **Kaggle Write-up Outline (`docs/submission_outline.md`):**
  - Problem & value summary.
  - Architecture & agent features (aligned to rubric concepts).
  - Data sources, evaluation metrics, results.
  - Deployment & cost overview.
  - Lessons learned + future work.
- **LinkedIn Blog Draft:**
  - Recount problem inspiration, agent design, key insights, screenshots.
  - Call-to-action linking to GitHub/Kaggle.
- **Video Script:**
  - 2–3 minute walkthrough covering problem, architecture diagram, live demo, outcomes.
  - Plan screen captures and narration points.

## 4. Evidence Artifacts
- Store evaluation outputs (`reports/evaluation/`), screenshots (`assets/screenshots/`), and deployment logs for reference.
- Latest Streamlit walkthrough captures: `UI_BasicRun.png`, `UI_Dashboard.png`, `UI_AgentsTextual_Response.png` for runbook and submission visuals.
- Maintain `history.d` as an ongoing changelog for easy retrospective writes.

## 5. Review & Publishing Timeline
1. Finish core implementation.
2. Update docs with real metrics/screenshots.
3. Draft LinkedIn post and video script.
4. Record video and capture final screenshots.
5. Finalize Kaggle write-up (linking repo, video, docs).

Keeping this plan updated ensures each documentation deliverable is accounted for and aligned with the competition rubric and storytelling goals.
