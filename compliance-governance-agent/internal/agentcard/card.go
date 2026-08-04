/*
===============================================================================
🏛️ WORKSHOP EXERCISES: Group B (Stage 2) - Go Agent Card Handler
===============================================================================
Welcome, Group B (Stage 2) Developers!

Your hands-on mission in this file:
  • Exercise 1: Implement `HandleAgentCard()` at `/.well-known/agent.json`

Complete working solutions are available in:
  `solutions/compliance-governance-agent/internal/agentcard/card.go`
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

/*
===========================================================================
TODO (Group B / Stage 2 - Exercise 1): Serve the A2A Agent Card
===========================================================================
Implement an HTTP handler function that outputs the Agent Card JSON structure.
Fulfills the A2A Discovery Standard at `/.well-known/agent.json`.

Expected Fields:
  - Name: "Compliance & Governance Agent (Go)"
  - Description: "Deterministic policy validator for contract value limits, liability caps, insurance, and historical variance."
  - URL: baseURL
  - Version: "1.0.0"
  - Protocols: []string{"JSON-RPC 2.0", "A2A/1.0"}
===========================================================================
*/
func HandleAgentCard(baseURL string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Access-Control-Allow-Origin", "*")

		// -------------------------------------------------------------------------
		// TODO (Group B - Exercise 1): Implement Agent Card JSON output here!
		// -------------------------------------------------------------------------
		card := AgentCard{
			Name:        "Compliance & Governance Agent (Go - TODO: Implement Exercise 1)",
			Description: "TODO (Group B / Stage 2 - Exercise 1): Complete HandleAgentCard in internal/agentcard/card.go",
			URL:         baseURL,
			Version:     "0.1.0-STUB",
			Protocols:   []string{"JSON-RPC 2.0", "A2A/1.0"},
		}

		json.NewEncoder(w).Encode(card)
	}
}
