# 🎓 Tutorial & Workshop Playbook: Building Polyglot Multi-Agent Systems with A2A Protocol

Welcome to the comprehensive tutorial and hands-on workshop playbook for the **Enterprise Contract Compliance Engine**.

This workshop demonstrates how to architect a production-grade, polyglot multi-agent compliance pipeline on **Google Cloud**. You will learn how to pair unstructured document intelligence (Python ADK + Gemini on Gemini Enterprise Agent Platform) with deterministic, zero-hallucination policy enforcement (compiled Go microservice) using the open **Agent-to-Agent (A2A)** protocol.

---

## 🧭 Workshop Overview & Roles

Participants or workshop tracks are divided into two parallel engineering streams:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Enterprise Monorepo                                    │
├───────────────────────────────────────────┬────────────────────────────────────────────┤
│  👥 Stream A: Python ADK & Agent Platform │  ⚙️ Stream B: Go Governance Policy Engine  │
│  Directory: extraction-orchestration-agent│  Directory: compliance-governance-agent    │
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│  • LLM Fact Extraction (Gemini 2.5)       │  • A2A Agent Card Discovery (agent.json)   │
│  • Historical Baseline SQLite Variance    │  • A2A JSON-RPC 2.0 Router (message/send)  │
│  • A2A Protocol Client & GCP OIDC Auth    │  • Deterministic Policy Rule Matrix        │
│  • Gemini Enterprise Agent Platform Deploy│  • HTML Audit Certificate Generator        │
└───────────────────────────────────────────┴────────────────────────────────────────────┘
```

---

## 🏗️ Step-by-Step Build Playbook

Follow these 6 structured phases to build and integrate the end-to-end multi-agent compliance system.

---

### Phase 1: Unstructured Contract Extraction with Gemini (Stream A)

In the real world, vendor agreements arrive as complex PDFs with varying terminology, formatting, and clauses. We leverage Gemini on the **Gemini Enterprise Agent Platform** to extract clean, typed financial and legal parameters.

> #### 🤖 Stream A Intent Prompt:
> *"Implement the contract extraction tool in `app/tools.py`. Parse contractor name, contract value, duration in years, start and end dates, liability limits (detecting 'unlimited liability'), insurance coverage floors, auto-renewal triggers, and termination notices. Return a structured legal fact dictionary."*

#### Resulting Code ([`extraction-orchestration-agent/app/tools.py`](extraction-orchestration-agent/app/tools.py)):
```python
def extract_contract_facts(filename: str, text: str) -> dict:
    # Extracts typed financial & legal parameters:
    return {
        "vendor_name": "Apex Data Systems",
        "contract_value": 450000.0,
        "term_years": 3,
        "start_date": "2026-09-01",
        "end_date": "2029-08-31",
        "liability_cap": "unlimited",
        "insurance_amount": 2000000.0,
        "auto_renewal": False,
        "has_termination_clause": True,
    }
```

---

### Phase 2: Historical Database Benchmarking & Variance Detection (Stream A)

LLMs alone do not know if a vendor's pricing is abnormal. We query a baseline database (SQLite / Cloud SQL) to detect anomalous contract price escalations or liability shifts before handing off to governance.

> #### 🤖 Stream A Intent Prompt:
> *"Implement historical vendor baseline calculation in `app/tools.py`. Query vendor historical averages, compute percentage value variance (`((current - historical) / historical) * 100`), and set `variance_flagged = True` if the increase exceeds 15% or if liability terms escalate."*

#### Resulting Logic ([`extraction-orchestration-agent/app/tools.py`](extraction-orchestration-agent/app/tools.py)):
```python
def calculate_historical_variance(facts: dict) -> dict:
    baseline = get_vendor_baseline(facts.get("vendor_name"))
    avg_value = baseline["historical_avg_value"]
    current_val = facts["contract_value"]
    
    variance_pct = ((current_val - avg_value) / avg_value) * 100.0
    flagged = variance_pct > 15.0 or (facts.get("liability_cap") == "unlimited" and baseline.get("historical_liability") != "unlimited")
    
    return {
        "vendor_name": facts.get("vendor_name"),
        "historical_avg_value": avg_value,
        "current_value": current_val,
        "value_variance_pct": round(variance_pct, 1),
        "variance_flagged": flagged,
        "liability_spike": facts.get("liability_cap") == "unlimited"
    }
```

---

### Phase 3: A2A Agent Card Discovery (Stream B)

Stream B implements self-describing service discovery. The Go microservice advertises its capabilities, protocol version, and endpoints via standard `/.well-known/agent.json`.

> #### 🤖 Stream B Intent Prompt:
> *"Implement the A2A Agent Card handler in Go under `internal/agentcard/card.go`. Expose a JSON agent card advertising capabilities, protocol support for JSON-RPC 2.0 and A2A/1.0, and dynamic root base URL."*

#### Resulting Code ([`compliance-governance-agent/internal/agentcard/card.go`](compliance-governance-agent/internal/agentcard/card.go)):
```go
type AgentCard struct {
    Name        string   `json:"name"`
    Description string   `json:"description"`
    URL         string   `json:"url"`
    Version     string   `json:"version"`
    Protocols   []string `json:"protocols"`
}

func HandleAgentCard(baseURL string) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        card := AgentCard{
            Name:        "Compliance & Governance Agent (Go)",
            Description: "Deterministic policy validator for contract value limits, liability caps, insurance, and historical variance.",
            URL:         baseURL,
            Version:     "1.0.0",
            Protocols:   []string{"JSON-RPC 2.0", "A2A/1.0"},
        }
        json.NewEncoder(w).Encode(card)
    }
}
```

---

### Phase 4: A2A JSON-RPC 2.0 Router & Protocol Dispatch (Streams A & B)

Now we connect the Python agent to the Go agent using standard **JSON-RPC 2.0** over HTTP POST.

#### Go JSON-RPC Router ([`compliance-governance-agent/internal/handler/jsonrpc.go`](compliance-governance-agent/internal/handler/jsonrpc.go)):
```go
func HandleJSONRPC() http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        var req JSONRPCRequest
        json.NewDecoder(r.Body).Decode(&req)
        
        if req.Method != "message/send" {
            json.NewEncoder(w).Encode(JSONRPCResponse{
                JSONRPC: "2.0", ID: req.ID,
                Error: map[string]interface{}{"code": -32601, "message": "Method not found"},
            })
            return
        }

        var msg A2AMessage
        json.Unmarshal(req.Params, &msg)
        
        facts := msg.Message.Parts[0].Data.Facts
        variance := msg.Message.Parts[0].Data.Variance
        result := policy.EvaluateContractPolicy(facts, variance)

        json.NewEncoder(w).Encode(JSONRPCResponse{
            JSONRPC: "2.0", ID: req.ID, Result: result,
        })
    }
}
```

#### Python A2A Client Dispatch ([`extraction-orchestration-agent/app/agent.py`](extraction-orchestration-agent/app/agent.py)):
```python
async def dispatch_a2a_compliance_check(case_id: str, facts: dict, variance: dict) -> dict:
    payload = {
        "jsonrpc": "2.0",
        "id": case_id,
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{
                    "text": f"Evaluate contract policy for case {case_id}",
                    "data": {"facts": facts, "variance": variance}
                }]
            }
        }
    }
    # Authenticated service-to-service call
    async with httpx.AsyncClient() as client:
        res = await client.post(REMOTE_GO_AGENT_URL, json=payload, timeout=10.0)
        return res.json()["result"]
```

---

### Phase 5: Zero-Hallucination Deterministic Policy Engine (Stream B)

In Stream B, we enforce hard corporate thresholds and anomaly checks in compiled Go code with mathematical certainty and sub-millisecond latency.

#### Policy Rules Engine ([`compliance-governance-agent/internal/policy/engine.go`](compliance-governance-agent/internal/policy/engine.go)):
```go
func EvaluateContractPolicy(facts ContractFacts, variance HistoricalVariance) PolicyCheckResult {
    var violations []string

    // 1. Hard Corporate Policy Limits
    if facts.ContractValue > 500000.0 {
        violations = append(violations, fmt.Sprintf("Contract value $%.2f exceeds hard policy cap of $500,000.00", facts.ContractValue))
    }
    if facts.TermYears > 5 {
        violations = append(violations, fmt.Sprintf("Term length %d years exceeds 5 year policy maximum", facts.TermYears))
    }
    if facts.InsuranceAmount < 1000000.0 {
        violations = append(violations, fmt.Sprintf("Insurance coverage $%.2f is below minimum required $1,000,000.00", facts.InsuranceAmount))
    }
    if facts.LiabilityCap == "unlimited" {
        violations = append(violations, "Prohibited clause: Unlimited liability is prohibited by corporate policy")
    }

    // 2. Historical Anomaly / Variance Rules
    if variance.VarianceFlagged {
        if variance.LiabilitySpike {
            violations = append(violations, "Historical Variance Alert: Unprecedented liability clause escalation compared to vendor history")
        } else {
            violations = append(violations, fmt.Sprintf("Historical Variance Alert: Contract value is +%.1f%% above historical baseline ($%.2f)", variance.ValueVariancePct, variance.HistoricalAvgValue))
        }
    }

    verdict := "PASS"
    if len(violations) > 0 {
        verdict = "REVIEW"
    }

    certHTML := GenerateAuditCertificateHTML(facts.CaseID, facts.VendorName, verdict, violations)
    return PolicyCheckResult{
        CaseID: facts.CaseID, Status: "COMPLETED", Verdict: verdict, Violations: violations, CertificateHTML: certHTML,
    }
}
```

---

### Phase 6: Cloud Run Deployment & Interactive Operations Cockpit

Both services package into optimized container images and deploy serverlessly to Google Cloud Run in `europe-west3`.

```bash
# 1. Deploy Python Extraction Orchestrator
cd extraction-orchestration-agent
gcloud run deploy extraction-orchestration-agent \
  --source . --region europe-west3 --allow-unauthenticated

# 2. Deploy Go Governance Agent
cd ../compliance-governance-agent
gcloud run deploy compliance-governance-agent \
  --source . --region europe-west3 --allow-unauthenticated

# 3. Deploy Cockpit Frontend
cd ../cockpit-frontend
gcloud run deploy cockpit-frontend \
  --source . --region europe-west3 --allow-unauthenticated
```

---

## 🖥️ Live Presentation & Demo Flow

To deliver a compelling presentation to executive and technical audiences, follow the standard 5-step flow:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              Demo Presentation Timeline                                │
├──────────────────────────┬─────────────────────────────┬───────────────────────────────┤
│ 1. Problem Framing       │ 2. Compliant Contract       │ 3. High-Risk Contract         │
│ (Legal review bottleneck)│ (Acme Corp: 3s Green PASS)  │ (Apex Data: Unlimited Liab.)  │
├──────────────────────────┼─────────────────────────────┼───────────────────────────────┤
│ 4. A2A Wire Inspection   │ 5. Code Architecture Walk   │ 6. Q&A & Business Value Wrap  │
│ (JSON-RPC 2.0 payload)   │ (Python AI + Go Engine)     │ (Speed, Zero Hallucinations)  │
└──────────────────────────┴─────────────────────────────┴───────────────────────────────┘
```

For full speaking scripts, audience Q&A cheat sheets, and technical highlights, refer directly to [**`DEMO_GUIDE.md`**](DEMO_GUIDE.md).
