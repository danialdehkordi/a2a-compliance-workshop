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


def test_is_high_risk_contract():
    from app.agent import is_high_risk_contract

    # Low risk contract
    low_risk = {"contract_value": 250000.0, "liability_cap": "limited"}
    assert is_high_risk_contract(low_risk, {"variance_flagged": False}) is False

    # High value > $500k
    high_val = {"contract_value": 600000.0, "liability_cap": "limited"}
    assert is_high_risk_contract(high_val, {"variance_flagged": False}) is True

    # Unlimited liability
    unlimited = {"contract_value": 100000.0, "liability_cap": "unlimited"}
    assert is_high_risk_contract(unlimited, {"variance_flagged": False}) is True

    # Variance flagged
    flagged_var = {"contract_value": 100000.0, "liability_cap": "limited"}
    assert is_high_risk_contract(flagged_var, {"variance_flagged": True}) is True


@pytest.mark.asyncio
async def test_dispatch_a2a_compliance_check_mock(monkeypatch):
    from app.agent import dispatch_a2a_compliance_check

    monkeypatch.setenv("USE_A2A_MOCK", "true")
    import app.agent
    app.agent.USE_MOCK = True

    facts = {
        "vendor_name": "Acme Corp",
        "contract_value": 650000.0,
        "term_years": 3,
        "liability_cap": "unlimited",
    }
    variance = {"variance_flagged": True, "value_variance_pct": 85.7}

    res = await dispatch_a2a_compliance_check("test-case-101", facts, variance)
    assert "verdict" in res
    assert res["verdict"] == "REVIEW"
    assert "certificate_html" in res

