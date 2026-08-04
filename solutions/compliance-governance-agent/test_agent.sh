#!/bin/bash
# Local cURL test script for Group B Go Agent
PORT=${PORT:-8888}
BASE_URL="http://localhost:${PORT}"

echo "=========================================================="
echo "1. Fetching A2A Agent Card from ${BASE_URL}/.well-known/agent.json"
echo "=========================================================="
curl -s "${BASE_URL}/.well-known/agent.json" | python3 -m json.tool

echo ""
echo "=========================================================="
echo "2. Dispatching A2A JSON-RPC message/send Audit Payload"
echo "=========================================================="
curl -s -X POST "${BASE_URL}/" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "case-test-101",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{
          "text": "Audit request",
          "data": {
            "case_id": "case-test-101",
            "facts": {
              "vendor_name": "Acme Corp",
              "contract_value": 650000.0,
              "term_years": 3,
              "liability_cap": "unlimited",
              "insurance_amount": 2000000.0
            },
            "variance": {
              "variance_flagged": true,
              "liability_spike": true,
              "value_variance_pct": 28.6
            }
          }
        }]
      }
    }
  }' | python3 -m json.tool
