# Deployment Strategy

This guide explains how the Enterprise IT Operations Agent moves from notebooks to production-ready experiences that satisfy Kaggle's Enterprise Agent rubric.

## Targets & Rationale
1. **Try ADK Web (baseline)**
   - Purpose: Provide an interactive debugging UI and meet ADK best practices.
   - Deliverable: `it_ops_observability` module with `create_agent()` used by `adk web`.
2. **Streamlit Dashboard (stakeholder UI)**
   - Purpose: Offer business stakeholders an intuitive cockpit for incident review, capacity planning, and SLA audits.
   - Deliverable: `app/streamlit_dashboard.py` leveraging ADK runners via function calls or REST endpoints.
3. **Cloud Run Deployment (production path)**
   - Purpose: Demonstrate deployability and support rubric bonus points.
   - Deliverable: Containerized Streamlit app with environment-configured credentials and logging.

## Implementation Checklist
### 1. ADK Web Module
- [ ] Finalize `src/it_ops_observability/__init__.py` exporting `create_agent`.
- [ ] Verify local launch via `adk web it_ops_observability`.
- [ ] Capture screenshots and note CLI commands for documentation.

### 2. Streamlit Dashboard
- [ ] Scaffold Streamlit app with sidebar controls (incident selection, log filters, time range).
- [ ] Integrate ADK runner calls (async handling or background tasks) to fetch responses.
- [ ] Display key metrics (charts), summaries, and action recommendations.
- [ ] Add configuration for API keys (dotenv or secret manager) and note security considerations.
- [ ] Provide local run instructions (`streamlit run app/streamlit_dashboard.py`).

### 3. Containerization & Cloud Run
- [ ] Write Dockerfile based on official Streamlit/ADK images.
- [ ] Include startup script to preload models, set environment variables, and run health checks.
- [ ] Configure Google Cloud Build or manual `gcloud builds submit` workflow.
- [ ] Deploy to Cloud Run (`gcloud run deploy`) with min instances, CPU/memory limits, and ingress rules.
- [ ] Validate authentication (service accounts, IAM), logging, and scaling behavior.

## Deliverables & Documentation
- Add deployment steps to README or separate `docs/deployment_guide.md` (to be created) with command snippets and troubleshooting tips.
- Record a short demo (GIF/video) showing the Streamlit app running locally and on Cloud Run.
- Note any cost considerations and teardown instructions (delete Cloud Run services, release static IPs).

## Timeline Integration
- Streamlit prototype after core agent tools are stable.
- Containerization and Cloud Run deployment during polish phase before final submission.
- Ensure evaluation runs are possible both locally and in the deployed environment.

Following this strategy ensures the project showcases a credible path from prototype to production, aligning with Kaggle grading and stakeholder expectations.
