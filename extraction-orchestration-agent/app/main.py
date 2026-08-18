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
        
        factors = []
        if facts.get("liability_limit") == "UNLIMITED":
            factors.append("Unlimited liability exposure detected in contract clauses.")
        if facts.get("term_length_years", 1) > 5:
            factors.append(f"Contract duration ({facts.get('term_length_years')} years) exceeds standard 5-year maximum.")
        if facts.get("contract_value", 0) > 500000:
            factors.append(f"Contract value (${facts.get('contract_value', 0):,.2f}) exceeds $500,000 threshold.")
        if variance.get("variance_flagged"):
            factors.append(f"Pricing variance anomaly: {variance.get('price_variance_pct', 0):+.1f}% vs historical benchmark.")
        if not factors:
            factors.append("All primary legal metrics within acceptable bounds.")

        factors_li = "".join([f"<li><strong>{f}</strong></li>" for f in factors])
        
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
        --accent: #1ed760;
        --accent-hover: #1db954;
        --error: #f3727f;
        --amber: #ffa42b;
        --shadow-heavy: rgba(0, 0, 0, 0.5) 0px 8px 24px;
        --shadow-card: rgba(0, 0, 0, 0.3) 0px 8px 8px;
        --shadow-inset: rgb(18, 18, 18) 0px 1px 0px, rgb(124, 124, 124) 0px 0px 0px 1px inset;
        --font-title: SpotifyMixUITitle, CircularSp-Arab, CircularSp-Hebr, CircularSp-Cyrl, CircularSp-Grek, CircularSp-Deva, "Helvetica Neue", Helvetica, Arial, "Hiragino Sans", "Hiragino Kaku Gothic ProN", Meiryo, "MS Gothic", sans-serif;
        --font-ui: SpotifyMixUI, CircularSp-Arab, CircularSp-Hebr, CircularSp-Cyrl, CircularSp-Grek, CircularSp-Deva, "Helvetica Neue", Helvetica, Arial, "Hiragino Sans", "Hiragino Kaku Gothic ProN", Meiryo, "MS Gothic", sans-serif;
      }}
      body {{
        margin: 0;
        padding: clamp(14px, 4vw, 34px);
        color: var(--ink);
        font-family: var(--font-ui);
        background: var(--bg);
      }}
      main {{
        max-width: 800px;
        margin: 0 auto;
        padding: clamp(20px, 4vw, 30px);
        border: 0;
        border-radius: 8px;
        background: var(--card);
        box-shadow: var(--shadow-heavy);
      }}
      header {{
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        align-items: flex-start;
        gap: 20px;
        border-bottom: 1px solid var(--line);
        padding-bottom: 18px;
        margin-bottom: 24px;
      }}
      h1 {{
        margin: 0;
        font-family: var(--font-title);
        font-size: 24px;
        font-weight: 700;
        line-height: 1.18;
      }}
      h2 {{
        margin: 24px 0 10px;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        color: var(--ink);
      }}
      p, li {{
        font-size: 14px;
        line-height: 1.5;
        color: var(--muted);
      }}
      ul {{
        padding-left: 20px;
        margin: 0;
      }}
      .meta {{
        color: var(--quiet);
        font-family: monospace;
        font-size: 11px;
        text-align: right;
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
        margin: 18px 0;
      }}
      .item {{
        border: 0;
        padding: 12px;
        background: var(--card-soft);
        border-radius: 8px;
        box-shadow: var(--shadow-inset);
      }}
      .item span {{
        display: block;
        color: var(--quiet);
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        margin-bottom: 4px;
      }}
      .item strong {{
        display: block;
        font-size: 16px;
      }}
      .badge {{
        display: inline-block;
        padding: 4px 8px;
        border-radius: 99px;
        font-size: 10.5px;
        font-weight: 600;
        text-transform: uppercase;
        border: 1px solid currentColor;
      }}
      .badge.high {{ background: transparent; color: var(--error); }}
      .badge.medium {{ background: transparent; color: var(--amber); }}
      .badge.low {{ background: transparent; color: var(--accent); }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <div>
          <h1>Legal Ingestion Parameter Sheet</h1>
          <p>Extracted variables from raw document text by Extractor Specialist subagent.</p>
        </div>
        <div class="meta">
          Case: {case_id[:8]}<br />
          Ingested: {case.get('filename', 'contract.pdf')}
        </div>
      </header>
      
      <h2>Core Parameters</h2>
      <section class="grid">
        <div class="item"><span>Contractor / Vendor</span><strong>{facts.get("vendor_name", "N/A")}</strong></div>
        <div class="item"><span>Client Entity</span><strong>{facts.get("client_name", "N/A")}</strong></div>
        <div class="item"><span>Total Contract Value</span><strong>${facts.get("contract_value", 0.0):,.2f}</strong></div>
        <div class="item"><span>Contract Duration</span><strong>{facts.get("term_length_years", 1)} year(s) ({facts.get("start_date", "")} to {facts.get("end_date", "")})</strong></div>
        <div class="item"><span>Liability Capping Limits</span><strong>{facts.get("liability_limit", "N/A")}</strong></div>
        <div class="item"><span>Commercial Insurance Coverage</span><strong>${facts.get("insurance_coverage", 0.0):,.2f}</strong></div>
        <div class="item"><span>Auto-Renewal Trigger</span><strong>{ "Yes (Auto-renewal enabled)" if facts.get("auto_renewal") else "No (Term terminates cleanly)" }</strong></div>
        <div class="item"><span>Exit Notices Safety</span><strong>{ "Termination Safety Clause exists" if facts.get("has_termination_clause") else "None (Missing standard exit notices!)" }</strong></div>
      </section>
      
      <h2>Specialist Risk Diagnostics</h2>
      <div class="item" style="margin-bottom: 12px;">
        <span style="margin-bottom: 6px;">Evaluated Risk Level Bounds</span>
        <span class="badge {risk_tier.lower()}">{risk_tier} Legal Risk</span>
      </div>
      <h2>Key Risk Indicators (KRIs)</h2>
      <ul>
        {factors_li}
      </ul>
    </main>
  </body>
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
