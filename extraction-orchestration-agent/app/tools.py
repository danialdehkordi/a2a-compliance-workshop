"""
===============================================================================
🏛️ STAGE 1 IMPLEMENTATION: Group A - Field Extraction & Historical Variance
===============================================================================
"""

import os
import re
from app.historical_db import get_vendor_baseline

SAMPLE_CONTRACT_DETAILS = {
    "standard-vendor-agreement.pdf": {
        "contract_value": 250000.0,
        "contractor_name": "ACME CLOUD SOLUTIONS",
        "client_name": "GFD PLATFORM SYSTEMS",
        "start_date": "2026-06-01",
        "end_date": "2028-06-01",
        "liability_limit": "$1,000,000.00",
        "insurance_coverage": 2000000.0,
        "auto_renewal": False,
        "has_termination_clause": True,
        "term_length_years": 2,
    },
    "high-risk-liability-contract.pdf": {
        "contract_value": 450000.0,
        "contractor_name": "APEX DATA SYSTEMS",
        "client_name": "GFD PLATFORM SYSTEMS",
        "start_date": "2026-06-01",
        "end_date": "2027-06-01",
        "liability_limit": "unlimited liability",
        "insurance_coverage": 1500000.0,
        "auto_renewal": False,
        "has_termination_clause": True,
        "term_length_years": 1,
    },
    "non-compliant-contract.pdf": {
        "contract_value": 850000.0,
        "contractor_name": "LEGACY NETWORKS CORP",
        "client_name": "GFD PLATFORM SYSTEMS",
        "start_date": "2026-06-01",
        "end_date": "2032-06-01",
        "liability_limit": "unlimited liability",
        "insurance_coverage": 500000.0,
        "auto_renewal": True,
        "has_termination_clause": False,
        "term_length_years": 6,
    },
}

MONTHS = {
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    "may": "05",
    "june": "06",
    "july": "07",
    "august": "08",
    "september": "09",
    "october": "10",
    "november": "11",
    "december": "12",
}


def _money_to_float(value: str) -> float:
    return float(value.replace("$", "").replace(",", ""))


def _iso_date(month: str, day: str, year: str) -> str:
    return f"{year}-{MONTHS[month.lower()]}-{int(day):02d}"


def extract_contract_facts(filename: str, text_content: str) -> dict:
    """Extracts comprehensive legal parameters from contract text.

    TODO EXERCISE A.1:
    Use Antigravity or Gemini to extract key legal facts from the contract text:
    1. Parse contractor/vendor name ('vendor_name') and client name ('client_name').
    2. Extract contract value as a float ('contract_value').
    3. Extract term duration in years ('term_years').
    4. Detect 'unlimited liability' clause ('liability_cap': 'unlimited' vs 'limited').
    5. Extract required insurance coverage floor as float ('insurance_amount').
    6. Include 'filename' in the returned dictionary.

    Reference / Expected Keys:
      - 'vendor_name': str
      - 'contract_value': float
      - 'term_years': int
      - 'liability_cap': 'limited' | 'unlimited'
      - 'insurance_amount': float
      - 'filename': str
    """
    raise NotImplementedError("Exercise A.1: Implement extract_contract_facts() in app/tools.py")



async def calculate_historical_variance(facts: dict) -> dict:
    """Compares extracted contract facts against historical vendor benchmarks in SQLite.

    TODO EXERCISE A.2:
    1. Fetch vendor baseline from SQLite using `await get_vendor_baseline(vendor_name)`.
    2. Calculate percentage variance: ((current_value - baseline_avg) / baseline_avg) * 100.
    3. Detect liability spikes (e.g. current is 'unlimited' while historical max was 'limited').
    4. Set `variance_flagged = True` if value variance > 15.0% or liability spike detected.
    5. Return dictionary with:
       - 'vendor_name': str
       - 'historical_avg_value': float
       - 'current_value': float
       - 'value_variance_pct': float
       - 'variance_flagged': bool
       - 'liability_spike': bool
    """
    raise NotImplementedError("Exercise A.2: Implement calculate_historical_variance() in app/tools.py")


