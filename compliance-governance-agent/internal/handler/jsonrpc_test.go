package handler

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestHandleJSONRPCMethodNotFound(t *testing.T) {
	handler := HandleJSONRPC()

	reqBody := `{"jsonrpc": "2.0", "id": "1", "method": "invalid/method", "params": {}}`
	req := httptest.NewRequest(http.MethodPost, "/", bytes.NewBufferString(reqBody))
	rec := httptest.NewRecorder()

	handler(rec, req)

	var res JSONRPCResponse
	if err := json.NewDecoder(rec.Body).Decode(&res); err != nil {
		t.Fatalf("failed to decode JSON response: %v", err)
	}

	if res.Error == nil {
		t.Fatalf("expected error for unknown method, got nil")
	}

	errMap, ok := res.Error.(map[string]interface{})
	if !ok {
		t.Fatalf("expected error object, got %T", res.Error)
	}
	if int(errMap["code"].(float64)) != -32601 {
		t.Errorf("expected error code -32601, got %v", errMap["code"])
	}
}

func TestHandleJSONRPCValidMessageSend(t *testing.T) {
	handler := HandleJSONRPC()

	payload := `{
		"jsonrpc": "2.0",
		"id": "case-test-42",
		"method": "message/send",
		"params": {
			"message": {
				"role": "user",
				"parts": [{
					"text": "Audit request",
					"data": {
						"case_id": "case-test-42",
						"facts": {
							"vendor_name": "Acme Corp",
							"contract_value": 250000.0,
							"term_years": 2,
							"liability_cap": "limited",
							"insurance_amount": 2000000.0
						},
						"variance": {
							"variance_flagged": false,
							"liability_spike": false,
							"value_variance_pct": 0.0
						}
					}
				}]
			}
		}
	}`

	req := httptest.NewRequest(http.MethodPost, "/", bytes.NewBufferString(payload))
	rec := httptest.NewRecorder()

	handler(rec, req)

	var res JSONRPCResponse
	if err := json.NewDecoder(rec.Body).Decode(&res); err != nil {
		t.Fatalf("failed to decode JSON response: %v", err)
	}

	if res.ID != "case-test-42" {
		t.Errorf("expected ID case-test-42, got %v", res.ID)
	}
	if res.Result == nil {
		t.Fatalf("expected Result to be non-nil")
	}
}
