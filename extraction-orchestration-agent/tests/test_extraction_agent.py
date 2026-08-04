"""Unit test suite for Group A Extraction & Orchestration Agent."""

import pytest
from app.tools import extract_contract_facts, calculate_historical_variance

def test_extract_contract_facts():
    text = "Agreement with Acme Corp for $650,000. Term duration: 3 years. Contractor shall have unlimited liability."
    facts = extract_contract_facts("test.txt", text)
    assert facts["vendor_name"] == "Acme Corp"
    assert facts["contract_value"] == 650000.0
    assert facts["term_years"] == 3
    assert facts["liability_cap"] == "unlimited"

@pytest.mark.asyncio
async def test_calculate_historical_variance():
    facts = {
        "vendor_name": "Acme Corp",
        "contract_value": 650000.0,
        "term_years": 3,
        "liability_cap": "unlimited",
        "insurance_amount": 2000000.0,
    }
    variance = await calculate_historical_variance(facts)
    assert variance["vendor_name"] == "Acme Corp"
    assert variance["value_variance_pct"] == 85.7
    assert variance["variance_flagged"] is True
    assert variance["liability_spike"] is True
