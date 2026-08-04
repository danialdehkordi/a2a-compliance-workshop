# 🏛️ Enterprise Multi-Agent A2A Compliance Workshop

Welcome to the hands-on repository for the **Enterprise Multi-Agent A2A Compliance Workshop**.

This repository demonstrates how to build, test, and deploy a production-grade **Contract Compliance Application** on Google Cloud and **Gemini Enterprise Agent Platform** using two autonomous teams.

---

## 📁 Monorepo Structure

Everything you need for the workshop is contained in this single repository:

```
a2a-compliance-workshop/
├── extraction-orchestration-agent/   <── GROUP A / STAGE 1 (Python ADK + Gemini + Field Extractor + Looped Learning)
├── compliance-governance-agent/      <── GROUP B / STAGE 2 (Go A2A Agent Card + Deterministic Policy Engine)
├── cockpit-frontend/                 <── STAGE 3 (Interactive User Review Cockpit UI)
├── solutions/                        <── REFERENCE SOLUTIONS (Complete Working Implementations)
│   ├── extraction-orchestration-agent/
│   └── compliance-governance-agent/
└── README.md                         <── Master Workshop Guide
```

---

## 🎯 Architecture & A2A Decoupling Blueprint

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ GROUP A (STAGE 1): extraction-orchestration-agent (Python ADK)                          │
│                                                                                         │
│  FastAPI Upload Route ──► Gemini Field Extractor ──► Historical Variance Calculator    │
│                                 │                                                       │
│                                 ▼                                                       │
│                      ADK RemoteA2aAgent                                                 │
│               (Includes Mock Stub for Offline Dev)                                      │
└─────────────────────────────────┬───────────────────────────────────────────────────────┘
                                  │
                                  │ A2A Handshake: GET /.well-known/agent.json
                                  │ A2A Payload: POST JSON-RPC 2.0 message/send
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ GROUP B (STAGE 2): compliance-governance-agent (Go Policy Engine)                       │
│                                                                                         │
│  /.well-known/agent.json ──► JSON-RPC 2.0 Handler ──► Deterministic Policy Checker       │
│                                                            │                            │
│                                                            ▼                            │
│                                                 Audit Certificate HTML                  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Workshop Hands-On Challenge

* **Group A / Stage 1 (Python ADK & Field Extraction Team)**:
  Work inside `extraction-orchestration-agent/`. Complete `TODO 1` (Contract Fact Extractor), `TODO 2` (Historical Variance Engine), and `TODO 3` (`RemoteA2aAgent` Handoff).
* **Group B / Stage 2 (Go Governance & Policy Engine Team)**:
  Work inside `compliance-governance-agent/`. Complete `TODO 1` (A2A Agent Card), `TODO 2` (JSON-RPC Router), and `TODO 3` (Deterministic Policy Engine).
* **Stage 3 (User Cockpit Dashboard)**:
  Work inside `cockpit-frontend/`. Connect the UI to Group A's API Gateway.
* **Solutions**:
  If you get stuck during the hackathon, inspect complete working solutions in `solutions/`.

---

## 🚀 Cloud Deployment Sequence

1. **Stage 1 (Group A Deployment)**:
   Deploy `extraction-orchestration-agent` to Gemini Enterprise Agent Platform / Cloud Run.
2. **Stage 2 (Group B Deployment)**:
   Deploy `compliance-governance-agent` to Gemini Enterprise Agent Platform / Cloud Run. Set Group A's `REMOTE_A2A_AGENT_CARD_URL` to Group B's live URL.
3. **Stage 3 (Frontend Deployment)**:
   Deploy `cockpit-frontend` pointing to Group A's live Orchestration API Gateway.
