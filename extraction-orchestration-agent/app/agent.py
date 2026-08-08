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


async def dispatch_a2a_compliance_check(case_id: str, facts: dict, variance: dict) -> dict:
    if USE_MOCK:
        return generate_mock_a2a_response(case_id, facts, variance)

    token = _get_identity_token(REMOTE_AGENT_CARD_URL)
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            card_res = await client.get(REMOTE_AGENT_CARD_URL, headers=headers)
            card_res.raise_for_status()
            card_data = card_res.json()
            endpoint = card_data.get("url", REMOTE_AGENT_CARD_URL.replace("/.well-known/agent.json", ""))
        except Exception as e:
            print(f"[A2A Warning] Failed to discover Agent Card ({e}), falling back to direct endpoint.")
            endpoint = REMOTE_AGENT_CARD_URL.replace("/.well-known/agent.json", "")

        payload = {
            "jsonrpc": "2.0",
            "id": case_id,
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "text": f"Evaluate contract policy for case {case_id}",
                            "data": {
                                "case_id": case_id,
                                "facts": facts,
                                "variance": variance,
                            }
                        }
                    ]
                }
            }
        }

        token = _get_identity_token(endpoint)
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            res = await client.post(endpoint, json=payload, headers=headers)
            res.raise_for_status()
            return res.json().get("result", {})
        except Exception as e:
            print(f"[A2A Error] Failed to execute JSON-RPC handoff: {e}")
            return generate_mock_a2a_response(case_id, facts, variance)
