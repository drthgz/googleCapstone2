# Cloud Cost Estimate & Bill of Materials

This document outlines expected Google Cloud costs for deploying the Enterprise IT Operations Agent and highlights opportunities to operate within the free tier during development.

## Services & Assumptions
| Service | Purpose | Assumed Usage | Pricing Reference | Est. Monthly Cost |
| --- | --- | --- | --- | --- |
| **Cloud Run** | Host Streamlit dashboard (demo only) | 0.5 vCPU / 0.5 GB, 10 hours active per month, minimal requests | [Cloud Run pricing](https://cloud.google.com/run/pricing) | ~$0 (within free tier: 180k vCPU-sec, 360k GiB-sec) |
| **Vertex AI (Gemini 2.5 Flash Lite)** | LLM inference for agents | 50k input tokens + 50k output tokens per month | [Generative AI pricing](https://cloud.google.com/vertex-ai/pricing) | ~$0.10 (per 1K tokens ~$0.00075–$0.0015) |
| **Artifact Registry / Container Build** | Store Streamlit container image | 1 GB storage, 2 builds per month | [Artifact Registry pricing](https://cloud.google.com/artifact-registry/pricing) | <$0.10 (first GB storage ~free) |
| **Cloud Storage (optional)** | Host processed datasets/backups | 5 GB standard storage | [Cloud Storage pricing](https://cloud.google.com/storage/pricing) | ~$0.10 |
| **Firestore / Memory Store (optional)** | Persist agent sessions/history | Free tier (1 GiB storage, 50K reads/day) | [Firestore pricing](https://cloud.google.com/firestore/pricing) | ~$0 (stay within free tier) |
| **Cloud Logging / Monitoring** | Observability for deployed services | Low volume logs/metrics | [Cloud Logging pricing](https://cloud.google.com/stackdriver/pricing) | ~$0 (free ingestion up to 50 GiB) |

> Use the [Google Cloud Pricing Calculator](https://cloud.google.com/products/calculator) to refine these estimates. Save the calculator link or PDF for the final submission.

## Free Tier Feasibility
- **Development:** Local notebooks, Kaggle environment, and Try ADK web run without incurring GCP costs.
- **Vertex AI Usage:** Google provides a limited free monthly quota for Generative AI API usage; light testing typically stays within it. Larger evaluation runs may incur minimal charges.
- **Cloud Run:** The free tier covers sporadic demos. Only sustained traffic or heavier CPU/memory allocations push costs above zero.
- **Storage & Builds:** Keeping artifacts small and occasionally cleaning up ensures costs remain negligible.

## Recommendations
1. **Monitor Usage:** Enable budget alerts in Google Cloud Console to receive notifications if spend exceeds $1.
2. **Short-Lived Deployments:** Spin up Cloud Run only for demos/recordings, then scale to zero or delete the service.
3. **Token Accounting:** Log request volumes during evaluation to keep Vertex AI usage predictable.
4. **Document Costs:** Include this BoM and calculator link in the Kaggle write-up, LinkedIn article, and video.

Overall, the project can be executed almost entirely within GCP’s free allowances. Any paid usage is expected to be well under $1/month given the current workload assumptions.
