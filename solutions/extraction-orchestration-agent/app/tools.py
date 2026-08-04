"""Reference Solution for Group A Tools."""

import re
from app.historical_db import get_vendor_baseline


def extract_contract_facts(filename: str, text_content: str) -> dict:
    value_match = re.search(r"\$\s*([\d,]+)", text_content)
    contract_value = float(value_match.group(1).replace(",", "")) if value_match else 450000.0

    term_match = re.search(r"(\d+)\s*(?:year|yr)", text_content, re.IGNORECASE)
    term_years = int(term_match.group(1)) if term_match else 3

    insurance_amount = 2000000.0
    liability = "unlimited" if "unlimited liability" in text_content.lower() else "limited"

    vendor_name = "Acme Corp"
    if "globex" in text_content.lower():
        vendor_name = "Globex Logistics"
    elif "initech" in text_content.lower():
        vendor_name = "Initech Software"

    return {
        "filename": filename,
        "vendor_name": vendor_name,
        "contract_value": contract_value,
        "term_years": term_years,
        "liability_cap": liability,
        "insurance_amount": insurance_amount,
    }


async def calculate_historical_variance(facts: dict) -> dict:
    vendor = facts["vendor_name"]
    baseline = await get_vendor_baseline(vendor)

    avg_val = baseline["avg_contract_value"]
    current_val = facts["contract_value"]

    value_increase_pct = 0.0
    if avg_val > 0:
        value_increase_pct = round(((current_val - avg_val) / avg_val) * 100, 1)

    liability_spike = facts["liability_cap"] == "unlimited" and baseline["max_historical_liability"] == "limited"

    return {
        "vendor_name": vendor,
        "historical_avg_value": avg_val,
        "current_value": current_val,
        "value_variance_pct": value_increase_pct,
        "variance_flagged": value_increase_pct > 15.0 or liability_spike,
        "liability_spike": liability_spike,
    }
