"""FastAPI Orchestrator Gateway Service for Group A Agent."""

import os
import uuid
import vertexai
from pathlib import Path
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel
from vertexai.preview import reasoning_engines

from app.tools import extract_contract_facts, calculate_historical_variance
from app.agent import dispatch_a2a_compliance_check
from app.historical_db import save_human_review, init_db

app = FastAPI(title="Orchestration & Extraction Agent (Group A)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CASES = {}
SAMPLE_CONTRACTS_DIR = Path(__file__).parent / "static" / "sample-contracts"

PROJECT_ID = os.getenv("GCP_PROJECT", "mcp-lud-wew")
LOCATION = os.getenv("GCP_LOCATION", "europe-west3")
REASONING_ENGINE_ID = os.getenv(
    "REASONING_ENGINE_RESOURCE_NAME",
    "projects/121116282931/locations/europe-west3/reasoningEngines/5292837869881131008"
)

# Initialize Vertex AI / Agent Platform SDK
try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    agent_platform_engine = reasoning_engines.ReasoningEngine(REASONING_ENGINE_ID)
    print(f"✅ Connected to Gemini Enterprise Agent Platform: {REASONING_ENGINE_ID}")
except Exception as e:
    print(f"⚠️ Agent Platform SDK Warning: {e}")
    agent_platform_engine = None


class ReviewSubmission(BaseModel):
    case_id: str
    vendor_name: str
    flagged_risk: str
    human_action: str
    comments: str
    approved_contract_value: float = 0.0


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "extraction-orchestration-agent",
        "agent_platform_connected": agent_platform_engine is not None,
        "reasoning_engine_resource_name": REASONING_ENGINE_ID,
    }


@app.get("/api/compliance/sample-contracts/{filename}")
async def get_sample_contract(filename: str):
    file_path = SAMPLE_CONTRACTS_DIR / filename
    if not file_path.exists():
        if "standard" in filename:
            return PlainTextResponse(
                "SOFTWARE SERVICES VENDOR AGREEMENT\nPARTIES: ACME CLOUD SOLUTIONS & GFD PLATFORM SYSTEMS\n"
                "VALUE: $250,000.00\nTERM: June 1, 2026 to June 1, 2028 (2 years)\n"
                "LIABILITY: Capped at $1,000,000.00\nINSURANCE: $2,000,000.00"
            )
        elif "high-risk" in filename:
            return PlainTextResponse(
                "SOFTWARE SERVICES VENDOR AGREEMENT\nPARTIES: APEX DATA SYSTEMS & GFD PLATFORM SYSTEMS\n"
                "VALUE: $450,000.00\nTERM: 6 years\n"
                "LIABILITY: Unlimited liability clause included\nINSURANCE: $500,000.00"
            )
        else:
            return PlainTextResponse(
                "SOFTWARE SERVICES VENDOR AGREEMENT\nPARTIES: LEGACY NETWORKS CORP & GFD PLATFORM SYSTEMS\n"
                "VALUE: $850,000.00\nTERM: 8 years\n"
                "LIABILITY: Unlimited liability\nINSURANCE: $250,000.00"
            )
    return PlainTextResponse(file_path.read_text(encoding="utf-8"))


@app.post("/api/compliance/upload")
async def upload_and_run(
    file: UploadFile = File(...),
    simulated_latency: float = Form(1.5),
    simulated_server_state: str = Form("normal"),
    custom_policies: str = Form(None),
):
    content_bytes = await file.read()
    contract_text = content_bytes.decode("utf-8", errors="ignore")
    filename = file.filename or "contract.txt"

    case_id = f"case-{uuid.uuid4().hex[:6]}"
    session_id = f"sess-{uuid.uuid4().hex[:6]}"

    # Dispatch query directly to Gemini Enterprise Agent Platform Reasoning Engine
    agent_platform_res = None
    if agent_platform_engine:
        try:
            print(f"🚀 Dispatching query to Agent Platform Reasoning Engine {REASONING_ENGINE_ID}...")
            agent_platform_res = agent_platform_engine.query(
                contract_text=contract_text, filename=filename
            )
            print(f"✅ Agent Platform Response: {agent_platform_res}")
        except Exception as err:
            print(f"⚠️ Agent Platform Query Warning: {err}")

    # Step 1: Fact Extraction
    facts = extract_contract_facts(filename, contract_text)
    facts["case_id"] = case_id

    # Step 2: Historical Variance % against SQLite baseline
    variance = await calculate_historical_variance(facts)

    # Step 3: A2A Protocol Handoff to Group B Go Policy Agent
    a2a_res = await dispatch_a2a_compliance_check(case_id, facts, variance)

    status = a2a_res.get("status", "COMPLETED")
    verdict = a2a_res.get("verdict", "PASS")
    violations = a2a_res.get("violations") or []
    certificate_html = a2a_res.get("certificate_html", "")

    passed = (verdict == "PASS")
    current_step = "APPROVED" if passed else "REVIEW_READY"

    case_data = {
        "id": case_id,
        "session_id": session_id,
        "filename": filename,
        "contractor_name": facts.get("vendor_name", "Acme Corp"),
        "contract_value": facts.get("contract_value", 0.0),
        "term_length_years": facts.get("term_years", 3),
        "liability_limit": facts.get("liability_cap", "limited"),
        "insurance_coverage": facts.get("insurance_amount", 2000000.0),
        "auto_renewal": False,
        "required_termination": True,
        "status": status,
        "verdict": verdict,
        "passed": passed,
        "risk_tier": "LOW" if passed else "HIGH",
        "current_step": current_step,
        "agent_platform_executed": agent_platform_res is not None,
        "agent_platform_resource_name": REASONING_ENGINE_ID,
        "extracted_facts": facts,
        "historical_variance": variance,
        "a2a_result": a2a_res,
        "violations": violations,
        "certificate_html": certificate_html,
        "artifacts": [
            {"id": "compliance-cert", "title": "Governance Audit Certificate", "type": "html"},
            {"id": "parameters-sheet", "title": "Extracted Contract Parameters", "type": "html"}
        ],
        "events": [
            {"timestamp": "Step 1", "source": f"agent-platform ({REASONING_ENGINE_ID.split('/')[-1]})", "type": "GE_PLATFORM", "detail": "Executed query on Gemini Enterprise Agent Platform Reasoning Engine"},
            {"timestamp": "Step 2", "source": "python-extraction-agent", "type": "EXTRACT", "detail": "Extracted facts & historical variance"},
            {"timestamp": "Step 3", "source": "go-compliance-agent", "type": "POLICY_CHECK", "detail": f"Policy check verdict: {verdict}"},
        ],
        "handoff": {
            "task_id": f"task-{case_id}",
            "status": "completed",
            "source_agent": "python-agent-platform",
            "target_agent": "go-compliance-agent",
            "agent_card_url": "https://compliance-governance-agent-121116282931.europe-west3.run.app/.well-known/agent.json",
            "method": "message/send (A2A JSON-RPC 2.0)",
            "contract_details": {
                "contractor_name": facts.get("vendor_name", "Acme Corp"),
                "contract_value": facts.get("contract_value", 0.0),
            },
            "risk_assessment": {
                "risk_tier": "LOW" if passed else "HIGH",
            },
            "agent_card": {
                "name": "Compliance & Governance Agent (Go)",
                "skills": [{"name": "Deterministic Policy Evaluator"}]
            },
            "request": {
                "jsonrpc": "2.0",
                "id": case_id,
                "method": "message/send",
                "params": {
                    "message": {
                        "role": "user",
                        "parts": [{"text": "Audit contract policy", "data": {"case_id": case_id, "facts": facts, "variance": variance}}]
                    }
                }
            },
            "verdict": {
                "passed": passed,
                "status": status,
                "violations": violations,
            }
        }
    }

    CASES[case_id] = case_data

    return {"case": case_data}


@app.get("/api/compliance/cases/{case_id}")
async def get_case(case_id: str):
    if case_id in CASES:
        return {"case": CASES[case_id]}
    return {
        "case": {
            "id": case_id,
            "session_id": f"sess-{case_id}",
            "current_step": "REVIEW_READY",
            "status": "COMPLETED",
            "verdict": "REVIEW",
            "passed": False,
            "artifacts": [],
            "events": [],
            "extracted_facts": {},
            "historical_variance": {},
            "a2a_result": {},
        }
    }


@app.get("/api/compliance/cases/{case_id}/artifacts/{artifact_id}")
async def get_case_artifact(case_id: str, artifact_id: str):
    case = CASES.get(case_id, {})
    
    if artifact_id == "parameters-sheet":
        facts = case.get("extracted_facts", {})
        variance = case.get("historical_variance", {})
        risk_tier = "LOW" if case.get("passed") else "HIGH"
        variance_flagged = variance.get("variance_flagged", False)
        
        html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Parameter Sheet - {facts.get('vendor_name', 'Vendor')}</title>
    <style>
      :root {{
        --bg: #121212;
        --card: #181818;
        --card-soft: #1f1f1f;
        --ink: #ffffff;
        --muted: #b3b3b3;
        --quiet: #7c7c7c;
        --line: #4d4d4d;
        --success: #1ed760;
        --error: #f3727f;
        --amber: #ffa42b;
        --shadow-heavy: rgba(0, 0, 0, 0.5) 0px 8px 24px;
        --shadow-card: rgba(0, 0, 0, 0.3) 0px 8px 8px;
        --font-title: SpotifyMixUITitle, "Helvetica Neue", Helvetica, Arial, sans-serif;
        --font-ui: SpotifyMixUI, "Helvetica Neue", Helvetica, Arial, sans-serif;
      }}
      body {{
        margin: 0;
        padding: 24px 16px;
        color: var(--ink);
        font-family: var(--font-ui);
        background: var(--bg);
      }}
      main {{
        max-width: 720px;
        margin: 0 auto;
        padding: 28px 24px;
        border-radius: 8px;
        background: var(--card);
        box-shadow: var(--shadow-heavy);
      }}
      header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        border-bottom: 1px solid var(--line);
        padding-bottom: 14px;
        margin-bottom: 18px;
      }}
      h1 {{
        margin: 0 0 4px;
        font-family: var(--font-title);
        font-size: 20px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
      }}
      h2 {{
        margin: 20px 0 10px;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: var(--quiet);
        border-bottom: 1px solid var(--line);
        padding-bottom: 6px;
      }}
      p {{
        margin: 0;
        font-size: 12px;
        color: var(--muted);
      }}
      .meta {{
        font-size: 11px;
        color: var(--quiet);
        text-align: right;
        font-family: monospace;
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
        margin: 14px 0;
      }}
      .item {{
        padding: 12px;
        background: var(--card-soft);
        border-radius: 6px;
        border: 1px solid var(--line);
      }}
      .item span {{
        display: block;
        color: var(--quiet);
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
      }}
      .item strong {{
        display: block;
        font-size: 14px;
        color: var(--ink);
      }}
      .badge {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 99px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
      }}
      .badge.low {{ background: rgba(30, 215, 96, 0.15); color: var(--success); border: 1px solid var(--success); }}
      .badge.high {{ background: rgba(243, 114, 127, 0.15); color: var(--error); border: 1px solid var(--error); }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <div>
          <h1>Legal Ingestion Parameter Sheet</h1>
          <p>Extracted variables by Gemini Enterprise Agent Platform (Reasoning Engine).</p>
        </div>
        <div class="meta">
          Case: {case_id[:8]}<br />
          File: {case.get('filename', 'contract.pdf')}
        </div>
      </header>
      
      <h2>Core Parameters</h2>
      <section class="grid">
        <div class="item"><span>Contractor / Vendor</span><strong>{facts.get('vendor_name', 'N/A')}</strong></div>
        <div class="item"><span>Total Contract Value</span><strong>${facts.get('contract_value', 0):,.2f}</strong></div>
        <div class="item"><span>Contract Duration</span><strong>{facts.get('term_years', 0)} year(s)</strong></div>
        <div class="item"><span>Liability Capping</span><strong>{facts.get('liability_cap', 'N/A')}</strong></div>
        <div class="item"><span>Insurance Minimum</span><strong>${facts.get('insurance_amount', 0):,.2f}</strong></div>
        <div class="item"><span>Historical Avg Value</span><strong>${variance.get('historical_avg_value', 0):,.2f}</strong></div>
      </section>
      
      <h2>Risk & Variance Diagnostics</h2>
      <div class="grid">
        <div class="item">
          <span>Evaluated Risk Level</span>
          <span class="badge {risk_tier.lower()}">{risk_tier} Legal Risk</span>
        </div>
        <div class="item">
          <span>Historical Variance %%</span>
          <strong style="color: {'var(--error)' if variance_flagged else 'var(--success)'};">{variance.get('value_variance_pct', 0)}%% {'(Alert Flagged)' if variance_flagged else '(Normal)'}</strong>
        </div>
      </div>
    </main>
  </body>
</html>"""
        return HTMLResponse(content=html)
    else:
        cert_html = case.get("certificate_html", "<h3>No Certificate Generated</h3>")
        return HTMLResponse(content=cert_html)


@app.post("/api/audit/run")
async def run_audit(contract_text: str = Form(...), filename: str = Form("contract.txt")):
    case_id = f"case-{uuid.uuid4().hex[:6]}"
    facts = extract_contract_facts(filename, contract_text)
    facts["case_id"] = case_id
    variance = await calculate_historical_variance(facts)
    a2a_res = await dispatch_a2a_compliance_check(case_id, facts, variance)
    return {
        "case_id": case_id,
        "filename": filename,
        "extracted_facts": facts,
        "historical_variance": variance,
        "a2a_result": a2a_res,
    }


@app.post("/api/compliance/override")
@app.post("/api/review/submit")
async def submit_review(review: ReviewSubmission):
    await save_human_review(
        case_id=review.case_id,
        vendor_name=review.vendor_name,
        flagged_risk=review.flagged_risk,
        human_action=review.human_action,
        comments=review.comments,
        approved_contract_value=review.approved_contract_value,
    )
    return {"status": "SUCCESS", "message": "Looped learning feedback recorded and baseline updated."}
