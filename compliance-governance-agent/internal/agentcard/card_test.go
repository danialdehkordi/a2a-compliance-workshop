package agentcard

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestHandleAgentCard(t *testing.T) {
	baseURL := "https://example-agent.run.app"
	handler := HandleAgentCard(baseURL)

	req := httptest.NewRequest(http.MethodGet, "/.well-known/agent.json", nil)
	rec := httptest.NewRecorder()

	handler(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("expected status 200, got %d. Body: %s", rec.Code, rec.Body.String())
	}

	contentType := rec.Header().Get("Content-Type")
	if contentType != "application/json" {
		t.Errorf("expected Content-Type application/json, got %s", contentType)
	}

	var card AgentCard
	if err := json.NewDecoder(rec.Body).Decode(&card); err != nil {
		t.Fatalf("failed to decode AgentCard JSON: %v", err)
	}

	if card.Name != "Compliance & Governance Agent (Go)" {
		t.Errorf("unexpected name: %s", card.Name)
	}
	if card.URL != baseURL {
		t.Errorf("expected URL %s, got %s", baseURL, card.URL)
	}
	if card.Version != "1.0.0" {
		t.Errorf("expected version 1.0.0, got %s", card.Version)
	}
	if len(card.Protocols) != 2 || card.Protocols[0] != "JSON-RPC 2.0" || card.Protocols[1] != "A2A/1.0" {
		t.Errorf("unexpected protocols: %v", card.Protocols)
	}
}
