"""
===============================================================================
🏛️ COMPLETE REFERENCE SOLUTION: Group A ADK A2A Handoff
===============================================================================
This is the complete reference solution for Group A Exercise 3.
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
    try:
        parts = target_url.split("/")
        audience = f"{parts[0]}//{parts[2]}" if len(parts) >= 3 else target_url
        auth_req = google.auth.transport.requests.Request()
        return google.oauth2.id_token.fetch_id_token(auth_req, audience)
    except Exception:
        return None


async def dispatch_a2a_compliance_check(case_id: str, facts: dict, variance: dict) -> dict:
    if USE_MOCK:
        return generate_mock_a2a_response(case_id, facts, variance)

    payload = {
        "jsonrpc": "2.0",
        "id": case_id,
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [
                    {
                        "text": f"Audit request for {facts['vendor_name']}",
                        "data": {
                            "case_id": case_id,
                            "facts": facts,
                            "variance": variance,
                        },
                    }
                ],
            }
        },
    }

    try:
        headers = {"Content-Type": "application/json"}
        token = _get_identity_token(REMOTE_AGENT_CARD_URL)
        if token:
            headers["Authorization"] = f"Bearer {token}"

        async with httpx.AsyncClient(timeout=8.0) as client:
            card_res = await client.get(REMOTE_AGENT_CARD_URL, headers=headers)
            card = card_res.json()
            rpc_url = card.get("url", REMOTE_AGENT_CARD_URL.replace("/.well-known/agent.json", "/"))

            if rpc_url.startswith("http://localhost") and "run.app" in REMOTE_AGENT_CARD_URL:
                rpc_url = REMOTE_AGENT_CARD_URL.replace("/.well-known/agent.json", "/")

            rpc_token = _get_identity_token(rpc_url)
            if rpc_token:
                headers["Authorization"] = f"Bearer {rpc_token}"

            rpc_res = await client.post(rpc_url, json=payload, headers=headers)
            return rpc_res.json()
    except Exception as exc:
        res = generate_mock_a2a_response(case_id, facts, variance)
        res["warning"] = f"Remote agent unreachable ({exc}). Used local mock stub."
        return res
