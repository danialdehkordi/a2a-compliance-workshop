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
        html = f"""
        <html style="background:#0f172a; color:#e2e8f0; font-family:sans-serif; padding:16px;">
            <h3 style="color:#38bdf8; margin-top:0;">📋 Extracted Contract Parameters & Historical Variance</h3>
            <p style="font-size:0.85rem; color:#94a3b8;"><strong>GE Agent Platform Engine:</strong> <code>{REASONING_ENGINE_ID}</code></p>
            <table style="width:100%; border-collapse:collapse; background:#1e293b; border-radius:8px; overflow:hidden;">
                <tr style="border-bottom:1px solid #334155;"><th style="padding:10px; text-align:left;">Field</th><th style="padding:10px; text-align:left;">Extracted Value</th></tr>
                <tr style="border-bottom:1px solid #334155;"><td style="padding:10px;">Vendor Name</td><td style="padding:10px; font-weight:bold;">{facts.get('vendor_name', 'N/A')}</td></tr>
                <tr style="border-bottom:1px solid #334155;"><td style="padding:10px;">Contract Value</td><td style="padding:10px; font-weight:bold;">${facts.get('contract_value', 0):,.2f}</td></tr>
                <tr style="border-bottom:1px solid #334155;"><td style="padding:10px;">Term Length</td><td style="padding:10px; font-weight:bold;">{facts.get('term_years', 0)} years</td></tr>
                <tr style="border-bottom:1px solid #334155;"><td style="padding:10px;">Liability Limit</td><td style="padding:10px; font-weight:bold;">{facts.get('liability_cap', 'N/A')}</td></tr>
                <tr style="border-bottom:1px solid #334155;"><td style="padding:10px;">Insurance Minimum</td><td style="padding:10px; font-weight:bold;">${facts.get('insurance_amount', 0):,.2f}</td></tr>
                <tr style="border-bottom:1px solid #334155;"><td style="padding:10px;">Historical Avg Value</td><td style="padding:10px; font-weight:bold;">${variance.get('historical_avg_value', 0):,.2f}</td></tr>
                <tr><td style="padding:10px;">Historical Variance %</td><td style="padding:10px; font-weight:bold; color:{'#f87171' if variance.get('variance_flagged') else '#4ade80'};">{variance.get('value_variance_pct', 0)}%</td></tr>
            </table>
        </html>
        """
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
