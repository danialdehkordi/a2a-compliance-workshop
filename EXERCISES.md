# 🏛️ Enterprise Multi-Agent Workshop: Hands-On Challenge Guide

Welcome to the **Enterprise Multi-Agent Compliance Workshop**!

In this full-day challenge, you will design and build a production-grade, polyglot multi-agent compliance mesh using **Google ADK (Agent Development Kit)**, **A2A (Agent-to-Agent Protocol)**, and **Gemini on Google Cloud**.

Participants work in two collaborative engineering streams:
- **👥 Team A (Python ADK & Agent Platform)**: Focuses on LLM fact extraction, database variance checking, Human-in-the-Loop (HITL) gates, and dynamic A2A dispatch (`extraction-orchestration-agent/`).
- **⚙️ Team B (Go Governance & Policy Engine)**: Focuses on A2A Agent Card discovery (`/.well-known/agent.json`), JSON-RPC 2.0 routing, and deterministic policy rule enforcement (`compliance-governance-agent/`).

---

## 🏆 Workshop Scoring Matrix

| Task | Stream | Description | Max Points |
| :--- | :--- | :--- | :--- |
| **A.1** | Team A | LLM Contract Fact Extraction with Gemini & Schema Validation | **1,000 pts** |
| **A.2** | Team A | Historical Baseline Tool & Context Window Protection | **1,000 pts** |
| **A.3** | Team A | Human-in-the-Loop (HITL) Policy Confirmation Gate | **1,500 pts** |
| **A.4** | Team A | A2A Protocol Discovery & JSON-RPC Client Dispatch | **2,000 pts** |
| **B.1** | Team B | A2A Agent Card Discovery Endpoint (`/.well-known/agent.json`) | **1,000 pts** |
| **B.2** | Team B | A2A JSON-RPC 2.0 Request Router & Unmarshaling | **1,500 pts** |
| **B.3** | Team B | Deterministic Policy Evaluation & Audit Badge Rendering | **1,500 pts** |
| **Joint 1** | All | End-to-End A2A Mesh Integration & Cockpit Review | **2,500 pts** |
| **Joint 2** | All | ADK Evaluations (`adk eval`) & Cloud Trace Verification | **1,500 pts** |
| **Total** | | | **12,500 pts** |

---

## 🛡️ Golden Rules for Building Production Agent Tools
*(Evaluated during code review & verification)*

> ### 1. 🔒 Security First (No SQL / Prompt Injections)
> Always use parameterized inputs for database queries (`aiosqlite`, BigQuery, etc.). Never interpolate raw user/LLM strings with f-strings into SQL statements.
>
> ### 2. 📝 Docstrings are the LLM User Interface
> LLMs do not read your function code; they read your docstrings and type annotations. Write explicit parameter descriptions and return schemas.
>
> ### 3. 🛡️ Protect the Context Window
> Return clean, concise text or structured JSON snippets. Never dump massive unfiltered blobs or raw binary files into the model context.
>
> ### 4. 🚨 Fail Usefully — Don't Swallow Exceptions
> Expected business outcomes (e.g., *"Vendor not found in baseline database"*) are valid return strings. Infrastructure failures (network timeouts, IAM auth errors) must raise exceptions so ADK retry and reflection machinery can trigger.

---

## 👥 Team A Exercises: Python ADK & Agent Platform

### ❓ Exercise A.1: LLM Contract Fact Extraction
- **Target File**: `extraction-orchestration-agent/app/tools.py`
- **Task**: Implement `extract_contract_facts(filename, contract_text)`. Extract typed legal parameters (`vendor_name`, `contract_value`, `term_years`, `liability_cap`, `insurance_amount`, `auto_renewal`) from unstructured agreements using Gemini.
- **Goal**: Return a typed Python dictionary.

```python
# TODO EXERCISE A.1:
# 1. Parse contract value ($ float)
# 2. Extract term length in years (int)
# 3. Detect "unlimited liability" clause (str)
# 4. Extract required insurance coverage floor (float)
```

---

### ❓ Exercise A.2: Historical Baseline Variance Calculation
- **Target File**: `extraction-orchestration-agent/app/tools.py`
- **Task**: Implement `calculate_historical_variance(facts)`. Query the vendor's historical benchmark from the SQLite database (`get_vendor_baseline`) and calculate `value_variance_pct`. Flag `variance_flagged = True` if the current contract value exceeds baseline by >15%.
- **Formula**: `((current_value - historical_avg) / historical_avg) * 100`

---

### ❓ Exercise A.3: Human-in-the-Loop (HITL) Gate for High-Risk Contracts
- **Target File**: `extraction-orchestration-agent/app/agent.py`
- **Task**: Implement an ADK `FunctionTool` confirmation predicate:
  - Contracts with **unlimited liability** or **value > $500k** must trigger human operator sign-off before dispatching to governance.
  - Standard/low-risk contracts pass through automatically without interrupting the operator.

```python
from google.adk.tools import FunctionTool

def is_high_risk_contract(facts: dict) -> bool:
    """Predicate: returns True if contract requires human sign-off."""
    return facts.get("contract_value", 0) > 500000 or facts.get("liability_cap") == "unlimited"

# Wrap dispatch with conditional confirmation:
governance_tool = FunctionTool(dispatch_a2a_compliance_check, require_confirmation=is_high_risk_contract)
```

---

### ❓ Exercise A.4: A2A Protocol Discovery & JSON-RPC Dispatch
- **Target File**: `extraction-orchestration-agent/app/agent.py`
- **Task**: Implement `dispatch_a2a_compliance_check(case_id, facts, variance)`.
  1. Fetch Team B's remote Agent Card (`GET /.well-known/agent.json`).
  2. Acquire a Google Cloud OIDC Identity Token for IAM service-to-service authentication.
  3. Construct a standard A2A JSON-RPC 2.0 `message/send` payload and POST to Team B's endpoint.

---

## ⚙️ Team B Exercises: Go Compliance Policy Engine

### ❓ Exercise B.1: A2A Agent Card Discovery Endpoint
- **Target File**: `compliance-governance-agent/internal/agentcard/card.go`
- **Task**: Implement `HandleAgentCard(baseURL)`. Return a standard JSON `AgentCard` advertising name, capabilities, version `"1.0.0"`, protocols `["JSON-RPC 2.0", "A2A/1.0"]`, and the dynamically resolved `baseURL`.

---

### ❓ Exercise B.2: A2A JSON-RPC Request Router
- **Target File**: `compliance-governance-agent/internal/handler/jsonrpc.go`
- **Task**: Implement `HandleJSONRPC()`. Unmarshal incoming A2A JSON-RPC 2.0 `message/send` requests, validate envelope headers, extract `ContractFacts` and `HistoricalVariance`, and route to the deterministic policy engine.

---

### ❓ Exercise B.3: Deterministic Policy Evaluation Engine
- **Target File**: `compliance-governance-agent/internal/policy/engine.go`
- **Task**: Implement `EvaluateContractPolicy(facts, variance)` to enforce zero-hallucination compliance:
  1. `ContractValue > $500,000.00` → Flagged
  2. `TermYears > 5` → Flagged
  3. `InsuranceAmount < $1,000,000.00` → Flagged
  4. `LiabilityCap == "unlimited"` → Flagged
  5. `VarianceFlagged == true` → Flagged
  - Return `PASS` if 0 violations, or `REVIEW` if violations exist, along with an official rendered HTML audit certificate badge.

---

## 🚀 Joint Integration & Production Evaluation

### ❓ Joint Exercise 1: Multi-Agent Mesh Deployment
- Deploy Team A (FastAPI / ADK Gateway) to Cloud Run in `europe-west3`.
- Deploy Team B (Go Policy Engine) to Cloud Run in `europe-west3`.
- Launch `cockpit-frontend/index.html` and run live contract audits.

### ❓ Joint Exercise 2: Automated ADK Evaluations (`adk eval`)
- Run deterministic eval suites to ensure model extraction accuracy across edge cases:
```bash
adk eval extraction_agent tests/extraction_evalset.json
```
- Verify distributed OpenTelemetry traces across the Python and Go agent boundaries in Google Cloud Trace.

