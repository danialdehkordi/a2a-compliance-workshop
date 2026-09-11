# 🎤 Facilitator Playbook & Slide Deck Outline

## 📅 Workshop Overview
- **Title**: Polyglot Multi-Agent Systems with Google ADK & A2A Protocol
- **Target Audience**: Hands-on Developers, AI Engineers, and Cloud Architects
- **Duration**: Full-Day (09:00 – 17:00)
- **Deployment Region**: `europe-west3`

---

## 📑 Slide Deck & Narrative Outline

### 🌅 Module 1: The Evolution of Agentic Architectures (09:00 – 09:45)
* **Slide 1: Title & Welcome**
  * *Speaker Hook*: "Generative AI started with single prompts, progressed to RAG, evolved into tool-calling agents, and is now entering the era of Multi-Agent Meshes."
* **Slide 2: The Limits of Monolithic LLMs**
  * Non-deterministic vs. Deterministic domains (e.g., Legal / Financial compliance requires 0% hallucination).
  * Why one giant system prompt doesn't scale for complex enterprise workflows.
* **Slide 3: Introducing Google ADK (Agent Development Kit)**
  * Core concepts: `Agent`, `App`, `FunctionTool`, `AgentTool`, Plugins (Observability, Logging, Retry).
* **Slide 4: Introducing the Agent-to-Agent (A2A) Protocol**
  * Open standard for cross-agent discovery (`/.well-known/agent.json`) and interaction (JSON-RPC 2.0).
  * Why polyglot agents (Python + Go + Java) communicating over A2A beat vendor lock-in.
* **Slide 5: Today's Mission & Live Cockpit Demo**
  * Demonstrate the Contract Compliance Cockpit processing a live agreement.
  * Explain the dual team setup: **Team A (Python Extraction)** + **Team B (Go Governance)**.

---

### 💻 Module 2: Team Split & Environment Setup (09:45 – 10:30)
* **Slide 6: Team Stream Roles & Architecture**
  * Stream A (Python ADK & Gemini) vs. Stream B (Go Policy Engine & JSON-RPC).
* **Slide 7: Golden Rules of Agent Engineering**
  * 🔒 Parameterized queries (No SQL injection).
  * 📝 Docstrings as the LLM User Interface.
  * 🛡️ Context Window preservation.
  * 🚨 Fail usefully — Don't swallow exceptions.
* **Slide 8: Local Tooling & Smoke Test**
  * CLI checks: `agy`, `python3`, `go`, `gcloud auth application-default login`.

---

### 🔨 Module 3: Hands-on Lab 1 — Building Individual Agents (10:30 – 12:30)
* **Slide 9: Team A Focus — Structured Extraction & Tools**
  * Parsing PDF/text into typed JSON schemas.
  * Connecting to historical baseline databases.
* **Slide 10: Team B Focus — Deterministic Governance**
  * Go compiled microservice: $500k value caps, 5-year term limits, liability triggers.
  * Zero-hallucination policy evaluation.
* **Slide 11: Milestone 1 Review & Checkpoint (Scoring)**
  * Verify Exercise A.1, A.2 and B.1, B.2 unit tests pass.

---

### 🥪 Lunch Break (12:30 – 13:30)

---

### 🔗 Module 4: Hands-on Lab 2 — Human-in-the-Loop & A2A Dispatch (13:30 – 15:00)
* **Slide 12: Human-in-the-Loop (HITL) Gateways**
  * Unconditional vs. Conditional predicates (`require_confirmation=is_high_risk`).
  * Guarding high-risk financial write operations.
* **Slide 13: The A2A Discovery & Handshake**
  * Discovering capabilities via `GET /.well-known/agent.json`.
  * Service-to-service IAM authentication using GCP OIDC identity tokens.
  * Formatting JSON-RPC 2.0 envelopes.
* **Slide 14: Dynamic Inter-Agent Call**
  * Team A Python agent invoking Team B Go agent over HTTP.

---

### ☁️ Module 5: Hands-on Lab 3 — Cloud Deployment & Tracing (15:00 – 16:00)
* **Slide 15: Deployment Topology**
  * Deploying to Cloud Run in `europe-west3`.
* **Slide 16: Observability with OpenTelemetry & Cloud Trace**
  * Visualizing distributed spans as a single transaction traverses Python and Go agents.
* **Slide 17: ADK Evaluations (`adk eval`)**
  * Creating deterministic evalsets for edge-case contract validation.

---

### 🏁 Module 6: Showcase, Wrap-Up & Next Steps (16:00 – 17:00)
* **Slide 18: Live Battle-Testing & Case Studies**
  * Uploading adversarial contracts (unlimited liability, +45% price spikes) into the Cockpit.
* **Slide 19: Key Takeaways**
  * Polyglot agent patterns.
  * When to use LLMs vs. Deterministic code.
  * Production hygiene (Evals, HITL, OIDC security).
* **Slide 20: Resources & Feedback**
  * GitHub repo links, ADK documentation, and feedback survey.
