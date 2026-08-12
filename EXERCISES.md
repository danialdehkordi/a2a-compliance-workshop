# 🏛️ Enterprise Multi-Agent Workshop Exercises

Welcome to the hands-on exercises for the **Enterprise Multi-Agent Compliance Workshop**!

Participants split into two parallel engineering teams working in this unified monorepo:
- **Team A**: Python ADK Extractor & Orchestrator Agent (`extraction-orchestration-agent/`)
- **Team B**: Go Compliance & Governance Policy Engine (`compliance-governance-agent/`)

---

## 👥 Team A Exercises: Python ADK & Agent Platform

### ❓ Exercise A.1: LLM Contract Fact Extraction
- **Target File**: `extraction-orchestration-agent/app/tools.py`
- **Task**: Implement `extract_contract_facts(filename, contract_text)`. Extract legal parameters (`vendor_name`, `contract_value`, `term_years`, `liability_cap`, `insurance_amount`) from unstructured contract text using Gemini / RegEx fallback.
- **Goal**: Return a clean Python dictionary of extracted facts.

```python
# TODO EXERCISE A.1:
# 1. Parse contract value ($)
# 2. Extract term length in years
# 3. Detect "unlimited liability" clause
# 4. Extract insurance coverage amount
```

---

### ❓ Exercise A.2: Historical Baseline Variance Calculation
- **Target File**: `extraction-orchestration-agent/app/tools.py`
- **Task**: Implement `calculate_historical_variance(facts)`. Query the vendor's historical average from SQLite DB (`get_vendor_baseline`) and calculate `value_variance_pct`. Set `variance_flagged = True` if current contract value is >20% above historical baseline.
- **Formula**: `((current_value - historical_avg) / historical_avg) * 100`

```python
# TODO EXERCISE A.2:
# 1. Fetch vendor historical baseline from database
# 2. Compute percentage value increase
# 3. Flag variance if increase > 20% or liability clause escalated
```

---

### ❓ Exercise A.3: A2A Protocol Discovery & JSON-RPC Dispatch
- **Target File**: `extraction-orchestration-agent/app/agent.py`
- **Task**: Implement `dispatch_a2a_compliance_check(case_id, facts, variance)`.
  1. Fetch Team B's remote Agent Card from `REMOTE_A2A_AGENT_CARD_URL` (`GET /.well-known/agent.json`).
  2. Acquire a GCP OIDC Identity Token for IAM service-to-service authentication.
  3. Construct an A2A JSON-RPC 2.0 `message/send` request and POST to Team B's agent.

```python
# TODO EXERCISE A.3:
# 1. GET REMOTE_A2A_AGENT_CARD_URL
# 2. Acquire google.oauth2.id_token
# 3. Construct JSON-RPC 2.0 payload and POST to Go agent endpoint
```

---

### ❓ Exercise A.4: Deploy to Gemini Enterprise Agent Platform
- **Target File**: `extraction-orchestration-agent/deploy_to_agent_platform.py`
- **Task**: Package the Python ADK agent as a `vertexai.preview.reasoning_engines.ReasoningEngine` resource and deploy to region `europe-west3`.

---

## ⚙️ Team B Exercises: Go Compliance Policy Engine

### ❓ Exercise B.1: A2A Agent Card Discovery Endpoint
- **Target File**: `compliance-governance-agent/internal/agentcard/card.go`
- **Task**: Implement `HandleAgentCard(baseURL)`. Return a JSON `AgentCard` advertising name, description, version `"1.0.0"`, protocols `["JSON-RPC 2.0", "A2A/1.0"]`, and the dynamic `baseURL`.

```go
// TODO EXERCISE B.1:
// Construct and return AgentCard JSON struct with dynamic baseURL
```

---

### ❓ Exercise B.2: A2A JSON-RPC Request Router
- **Target File**: `compliance-governance-agent/internal/handler/jsonrpc.go`
- **Task**: Implement `HandleJSONRPC()`. Unmarshal incoming A2A JSON-RPC 2.0 `message/send` requests, extract `ContractFacts` and `HistoricalVariance` from message parts, call `policy.EvaluateContractPolicy()`, and encode a JSON-RPC 2.0 success response.

```go
// TODO EXERCISE B.2:
// Decode JSON-RPC 2.0 request envelope
// Extract facts & variance from message parts
// Call policy.EvaluateContractPolicy(facts, variance)
// Return JSON-RPC 2.0 response
```

---

### ❓ Exercise B.3: Deterministic Policy Engine Evaluation
- **Target File**: `compliance-governance-agent/internal/policy/engine.go`
- **Task**: Implement `EvaluateContractPolicy(facts, variance)`. Evaluate hard corporate rules:
  1. `ContractValue > $500,000.00` → Flagged
  2. `TermYears > 5` → Flagged
  3. `InsuranceAmount < $1,000,000.00` → Flagged
  4. `LiabilityCap == "unlimited"` → Flagged
  5. `VarianceFlagged == true` → Flagged
  Return `PASS` if 0 violations, or `REVIEW` if any violations exist, with a rendered HTML audit certificate badge.

```go
// TODO EXERCISE B.3:
// Enforce policy rules and return PolicyCheckResult struct
```

---

### ❓ Exercise B.4: Cloud Run Multi-Stage Dockerfile
- **Target File**: `compliance-governance-agent/Dockerfile`
- **Task**: Write a multi-stage Dockerfile compiling Go in `golang:1.22-alpine` and deploying in `alpine:latest` listening on `${PORT:-8080}`.

---

## 🚀 Joint Integration Exercise

1. Deploy Team A Gateway to Cloud Run.
2. Deploy Team B Policy Agent to Cloud Run.
3. In `cockpit-frontend/index.html`, set `API_ORIGIN` to Team A's Cloud Run URL.
4. Open the Cockpit UI and run live sample audits!
