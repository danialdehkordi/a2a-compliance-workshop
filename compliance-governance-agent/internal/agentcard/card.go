/*
===============================================================================
🏛️ STAGE 2 IMPLEMENTATION: Group B - Go Agent Card Handler
===============================================================================
*/

package agentcard

import (
	"encoding/json"
	"net/http"
)

type AgentCard struct {
	Name        string   `json:"name"`
	Description string   `json:"description"`
	URL         string   `json:"url"`
	Version     string   `json:"version"`
	Protocols   []string `json:"protocols"`
}

func HandleAgentCard(baseURL string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Access-Control-Allow-Origin", "*")

		card := AgentCard{
			Name:        "Compliance & Governance Agent (Go)",
			Description: "Deterministic policy validator for contract value limits, liability caps, insurance, and historical variance.",
			URL:         baseURL,
			Version:     "1.0.0",
			Protocols:   []string{"JSON-RPC 2.0", "A2A/1.0"},
		}

		json.NewEncoder(w).Encode(card)
	}
}
