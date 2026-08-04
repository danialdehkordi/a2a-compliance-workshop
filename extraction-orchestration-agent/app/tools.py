"""
===============================================================================
🏛️ WORKSHOP EXERCISES: Group A - Field Extraction & Variance Calculation
===============================================================================
Welcome Group A Developers!

Your hands-on mission in this file:
  • Exercise 1: Implement `extract_contract_facts()`
  • Exercise 2: Implement `calculate_historical_variance()`

Complete solutions are available in `solutions/extraction-orchestration-agent/app/tools.py`
if you need a reference during the workshop.
===============================================================================
"""

from app.historical_db import get_vendor_baseline


def extract_contract_facts(filename: str, text_content: str) -> dict:
    """
    ===========================================================================
    TODO (Group A - Exercise 1): Extract Contract Facts
    ===========================================================================
    Extract key legal fields from unstructured contract text.

    Return Dictionary Requirements:
      - vendor_name (str): Entity name (e.g. 'Acme Corp')
      - contract_value (float): Total contract financial value in USD (e.g. 650000.0)
      - term_years (int): Duration in years (e.g. 3)
      - liability_cap (str): 'limited' or 'unlimited'
      - insurance_amount (float): Required insurance coverage in USD (e.g. 2000000.0)

    HINTS:
      - Option A (Vertex AI): Use `google-genai` SDK with `response_schema`
        and Pydantic to extract structured JSON with Gemini 2.0.
      - Option B (Regex): Use `re.search(r"\$\s*([\d,]+)", text_content)` for contract value,
        `re.search(r"(\d+)\s*(?:year|yr)", text_content)` for term, and
        `"unlimited liability" in text_content.lower()` for liability cap.
    ===========================================================================
    """
    # -------------------------------------------------------------------------
    # YOUR CODE HERE (Exercise 1)
    # -------------------------------------------------------------------------
    raise NotImplementedError(
        "TODO (Group A - Exercise 1): Implement contract fact extraction in app/tools.py!\n"
        "Reference solution available in solutions/extraction-orchestration-agent/app/tools.py"
    )


async def calculate_historical_variance(facts: dict) -> dict:
    """
    ===========================================================================
    TODO (Group A - Exercise 2): Calculate Historical Variance
    ===========================================================================
    Compare extracted facts against historical vendor benchmarks in SQLite.

    Steps:
      1. Fetch baseline: `baseline = await get_vendor_baseline(facts['vendor_name'])`
         (Returns `avg_contract_value` and `max_historical_liability`).
      2. Calculate percentage price increase:
         `value_increase_pct = ((current_val - avg_val) / avg_val) * 100`
      3. Flag variance if:
         - `value_increase_pct > 15.0%` OR
         - `liability_cap == 'unlimited'` while baseline was `'limited'` (liability_spike)

    Return Dictionary Requirements:
      - vendor_name (str)
      - historical_avg_value (float)
      - current_value (float)
      - value_variance_pct (float)
      - variance_flagged (bool)
      - liability_spike (bool)
    ===========================================================================
    """
    # -------------------------------------------------------------------------
    # YOUR CODE HERE (Exercise 2)
    # -------------------------------------------------------------------------
    raise NotImplementedError(
        "TODO (Group A - Exercise 2): Implement historical baseline variance calculation in app/tools.py!\n"
        "Reference solution available in solutions/extraction-orchestration-agent/app/tools.py"
    )
