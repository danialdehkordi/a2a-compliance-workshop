"""FastAPI Orchestrator Gateway Service for Group A Agent."""

import uuid
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
    return {"status": "HEALTHY", "service": "extraction-orchestration-agent"}


@app.post("/api/audit/run")
async def run_audit(contract_text: str = Form(...), filename: str = Form("contract.txt")):
    """
    Executes end-to-end multi-agent pipeline:
    1. Extract Facts (Gemini / RegEx)
    2. Calculate Historical Variance % against SQLite baseline
    3. Handoff via A2A to Group B Go Policy Agent
    """
    case_id = f"case-{uuid.uuid4().hex[:6]}"

    # Step 1: Extract Facts
    facts = extract_contract_facts(filename, contract_text)
    facts["case_id"] = case_id

    # Step 2: Calculate Historical Variance
    variance = await calculate_historical_variance(facts)

    # Step 3: Dispatch A2A Handoff
    a2a_res = await dispatch_a2a_compliance_check(case_id, facts, variance)

    return {
        "case_id": case_id,
        "filename": filename,
        "extracted_facts": facts,
        "historical_variance": variance,
        "a2a_result": a2a_res,
    }


@app.post("/api/review/submit")
async def submit_review(review: ReviewSubmission):
    """
    Looped Learning Endpoint: Records human reviewer override and updates
    vendor baseline models in SQLite.
    """
    await save_human_review(
        case_id=review.case_id,
        vendor_name=review.vendor_name,
        flagged_risk=review.flagged_risk,
        human_action=review.human_action,
        comments=review.comments,
        approved_contract_value=review.approved_contract_value,
    )
    return {"status": "SUCCESS", "message": "Looped learning feedback recorded and baseline updated."}
