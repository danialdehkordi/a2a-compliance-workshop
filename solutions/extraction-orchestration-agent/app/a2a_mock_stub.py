"""Mock A2A response generator for offline local development."""

def generate_mock_a2a_response(case_id: str, facts: dict, variance: dict) -> dict:
    value = facts.get("contract_value", 0.0)
    liability = facts.get("liability_cap", "limited")
    
    violations = []
    if value > 500000.0:
        violations.append(f"Contract value ${value:,.2f} exceeds hard policy cap of $500,000.00")
    if liability == "unlimited":
        violations.append("Prohibited clause: Unlimited liability is prohibited by corporate policy")
    if variance.get("variance_flagged", False):
        violations.append(f"Historical Variance Alert: Value is +{variance.get('value_variance_pct', 0)}% above baseline")

    verdict = "REVIEW" if violations else "PASS"

    cert_html = f"""
    <div style="font-family: sans-serif; max-width: 600px; border: 2px solid {'#e53e3e' if verdict == 'REVIEW' else '#38a169'}; border-radius: 8px; padding: 16px; background: white;">
        <h3 style="color: {'#c53030' if verdict == 'REVIEW' else '#276749'}; margin-top:0;">🛡️ Compliance Audit Certificate</h3>
        <p><strong>Case ID:</strong> {case_id}</p>
        <p><strong>Vendor Name:</strong> {facts.get('vendor_name', 'Unknown')}</p>
        <p><strong>Verdict:</strong> <span style="background:{'#c53030' if verdict == 'REVIEW' else '#276749'}; color:white; padding:2px 8px; border-radius:4px;">{verdict}</span></p>
        <ul>{"".join(f'<li style="color:#c53030;">{v}</li>' for v in violations)}</ul>
    </div>
    """

    return {
        "jsonrpc": "2.0",
        "id": case_id,
        "result": {
            "case_id": case_id,
            "status": "COMPLETED",
            "verdict": verdict,
            "violations": violations,
            "certificate_html": cert_html
        }
    }
