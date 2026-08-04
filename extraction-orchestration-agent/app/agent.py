"""
===============================================================================
🏛️ WORKSHOP EXERCISES: Group A - ADK RemoteA2aAgent Handoff
===============================================================================
In this module, you wire up the A2A protocol handoff to Group B's Go Agent:
1. Fetch Group B's Agent Card (`/.well-known/agent.json`)
2. Package facts & variance into JSON-RPC 2.0 `message/send` payload
3. Post payload to Group B and return compliance verdict & certificate HTML

Complete solutions are available in `solutions/extraction-orchestration-agent/app/agent.py`
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
    except Exception:
        return None


async def dispatch_a2a_compliance_check(case_id: str, facts: dict, variance: dict) -> dict:
    """
    ===========================================================================
    TODO (Group A - Exercise 3): Dispatch A2A Handoff to Group B Go Agent
    ===========================================================================
    Steps to implement:
      1. If `USE_MOCK` is true, return `generate_mock_a2a_response(case_id, facts, variance)`.
      2. Construct JSON-RPC 2.0 payload:
         {
           "jsonrpc": "2.0",
           "id": case_id,
           "method": "message/send",
           "params": {
             "message": {
               "role": "user",
               "parts": [{ "text": "Audit request", "data": { "case_id": case_id, "facts": facts, "variance": variance } }]
             }
           }
         }
      3. Use `httpx.AsyncClient()` to GET `REMOTE_AGENT_CARD_URL` to discover Group B's endpoint.
      4. POST the JSON-RPC payload to Group B and return the JSON response!
    ===========================================================================
    """
    if USE_MOCK:
        return generate_mock_a2a_response(case_id, facts, variance)

    # -------------------------------------------------------------------------
    # YOUR CODE HERE (Exercise 3)
    # -------------------------------------------------------------------------
    raise NotImplementedError(
        "TODO (Group A - Exercise 3): Implement A2A protocol handoff in app/agent.py!\n"
        "Reference solution available in solutions/extraction-orchestration-agent/app/agent.py"
    )
