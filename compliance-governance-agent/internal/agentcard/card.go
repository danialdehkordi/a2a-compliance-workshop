/*
===============================================================================
🏛️ WORKSHOP EXERCISES: Group B - Go Agent Card Handler
===============================================================================
Welcome, Group B (Go Governance & Policy Team)!

Your challenge in this file:
  • Exercise 1: Implement `HandleAgentCard()` at `/.well-known/agent.json`

Complete solutions are available in `solutions/compliance-governance-agent/`
if you need a reference during the workshop.
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
TODO (Group B - Exercise 1): Serve the A2A Agent Card
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
		// YOUR CODE HERE (Exercise 1)
		// -------------------------------------------------------------------------
		card := AgentCard{
			Name:        "Compliance & Governance Agent (Go - TODO: Complete Exercise 1)",
			Description: "Deterministic policy validator for contract limits.",
			URL:         baseURL,
			Version:     "1.0.0",
			Protocols:   []string{"JSON-RPC 2.0", "A2A/1.0"},
		}

		json.NewEncoder(w).Encode(card)
	}
}
