# Storytelling Assets Plan

This document outlines the narrative assets needed for the capstone submission and public sharing. Each section lists owners, objectives, required artifacts, and next actions.

## 1. LinkedIn Blog Post
- **Objective:** Announce the Enterprise IT Operations Supervisor Agent, highlight the problem/value, and drive traffic to the GitHub repository.
- **Audience:** Engineering leaders, SRE/DevOps practitioners, AI agent enthusiasts.
- **Structure Outline:**
  1. Hook: describe the incident command pain point with a recent anecdote.
  2. Problem framing: quantify delays in manual triage.
  3. Solution overview: introduce the multi-agent supervisor, link to architecture diagram.
  4. Demo highlights: embed screenshots from the Streamlit UI and evaluation artifacts.
  5. Call-to-action: invite readers to try the demo, star the repo, or follow the Kaggle submission.
- **Assets Needed:**
  - Streamlit dashboard screenshot (`assets/screenshots/UI_Dashboard.png`).
  - Transcript screenshot (`assets/screenshots/UI_AgentsTextual_Response.png`).
  - Architecture diagram (`assets/enterprise_it_ops_architecture.png`).
- **Next Actions:**
  - Draft copy (Nov 30).
  - Peer review and final edit (Dec 1 AM).
  - Schedule publication for Dec 2 after submission lock-in.

## 2. Submission Video (≤3 Minutes)
- **Objective:** Fulfill Kaggle bonus rubric by showcasing the problem, architecture, live demo, and build process.
- **Storyboard:**
  1. **Intro (0:00–0:20):** Title card + narrator summarizes the operations pain point.
  2. **Problem & Impact (0:20–0:50):** Animated bullets on MTTR delays; overlay metrics from README.
  3. **Architecture Walkthrough (0:50–1:20):** Pan across the architecture diagram while narrating agent roles and tool calls.
  4. **Demo (1:20–2:10):** Screen capture of Streamlit run (dashboard refresh + transcript highlights).
  5. **Results & Metrics (2:10–2:40):** Show pytest screenshot, metrics JSON snippets, and runtime stats.
  6. **Closing CTA (2:40–3:00):** Invite viewers to read the write-up and explore the repo.
- **Assets Needed:**
  - High-resolution screenshots (already captured in `assets/screenshots/`).
  - Recorded Streamlit session (to be captured Nov 30).
  - Voice-over script (draft by Nov 30, finalize Dec 1).
- **Next Actions:**
  - Capture demo footage using OBS or QuickTime (Nov 30).
  - Assemble video in preferred editor (Dec 1 AM).
  - Upload unlisted YouTube link for inclusion in submission (Dec 1 PM).

## 3. Internal Talking Points / FAQ
- **Objective:** Provide a quick-reference sheet for live demos or Q&A sessions.
- **Contents:**
  - Key metrics (MTTR reduction target, utilization stats, runtime timings).
  - Architecture elevator pitch (one-liner per agent + tool).
  - Risk mitigation notes (deterministic fallbacks, quota handling, secret management).
  - Future roadmap bullets (memory services, remediation automations, Cloud Run deployment).
- **Next Actions:**
  - Draft FAQ sheet (Dec 1).
  - Store under `docs/talking_points.md` or append to README appendix if needed.

## 4. Evidence Bundle Tracking
- **Objective:** Ensure every artifact referenced in storytelling assets is versioned and stored.
- **Checklist:**
  - ✅ Streamlit dashboard screenshots (`assets/screenshots/`).
  - ✅ Evaluation transcript (`reports/evaluation/examples/2025-11-28_adk_supervisor_verbose_run_v2.txt`).
  - ✅ Metrics JSON (`reports/evaluation/examples/metrics_2025-11-29.json`).
  - ◻️ Recorded video (pending capture Nov 30).
  - ◻️ Final LinkedIn copy (pending draft).

## 5. Publishing Timeline (High Level)
- Nov 30: Draft LinkedIn post, record Streamlit walkthrough, draft video script.
- Dec 1 (AM): Edit LinkedIn copy, assemble video, prepare FAQ sheet.
- Dec 1 (PM): Submit Kaggle write-up with video link and evidence bundle.
- Dec 2: Publish LinkedIn post and share highlights internally.

---
*Last updated: 2025-11-29*
