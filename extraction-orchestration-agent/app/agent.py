"""
===============================================================================
🏛️ STAGE 1 IMPLEMENTATION: Group A - ADK RemoteA2aAgent Handoff
===============================================================================
"""

import os
import httpx
import google.auth.transport.requests
import google.oauth2.id_token

from app.a2a_mock_stub import generate_mock_a2a_response

REMOTE_AGENT_CARD_URL = os.getenv("REMOTE_A2A_AGENT_CARD_URL", "http://localhost:8888/.well-known/agent.json")
USE_MOCK = os.getenv("USE_A2A_MOCK", "false").lower() == "true"


def _get_identity_token(target_url: str) -> str | None:
    """Retrieves GCP Identity Token for Cloud Run service-to-service authentication."""
    try:
        parts = target_url.split("/")
        audience = f"{parts[0]}//{parts[2]}" if len(parts) >= 3 else target_url
        auth_req = google.auth.transport.requests.Request()
        return google.oauth2.id_token.fetch_id_token(auth_req, audience)
    except Exception as e:
        print(f"[Auth Warning] Could not fetch ID token: {e}")
        return None


def is_high_risk_contract(facts: dict, variance: dict | None = None) -> bool:
    """Predicate determining if a contract requires human operator approval before governance dispatch.

    TODO EXERCISE A.3:
    Implement the risk predicate:
    Return True (triggering HITL confirmation) if:
      - contract_value > 500,000.0
      - OR liability_cap == 'unlimited'
      - OR variance is flagged (variance.get('variance_flagged') is True)
    Otherwise return False (automatic low-risk pass-through).
    """
    raise NotImplementedError("Exercise A.3: Implement is_high_risk_contract() in app/agent.py")


async def dispatch_a2a_compliance_check(case_id: str, facts: dict, variance: dict) -> dict:
    """Dispatches extracted facts and variance to Team B's remote Go policy agent via A2A protocol.

    TODO EXERCISE A.4:
    1. Check USE_MOCK: if True, return generate_mock_a2a_response(case_id, facts, variance).
    2. Fetch remote Agent Card from REMOTE_AGENT_CARD_URL (GET /.well-known/agent.json)
       and dynamically resolve the service endpoint URL (card_data.get('url')).
    3. Obtain a GCP OIDC Identity Token for the target endpoint using `_get_identity_token(endpoint)`.
    4. Construct a standard A2A JSON-RPC 2.0 'message/send' payload:
       - jsonrpc: "2.0"
       - id: case_id
       - method: "message/send"
       - params: { "message": { "role": "user", "parts": [ { "data": { "case_id": case_id, "facts": facts, "variance": variance } } ] } }
    5. Send POST request with JSON-RPC payload and Bearer token header.
    6. Return the JSON-RPC 'result' object.
    """
    raise NotImplementedError("Exercise A.4: Implement dispatch_a2a_compliance_check() in app/agent.py")

