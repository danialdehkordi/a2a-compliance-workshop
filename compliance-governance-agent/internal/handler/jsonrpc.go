/*
===============================================================================
🏛️ STAGE 2 IMPLEMENTATION: Group B - Go JSON-RPC 2.0 Router
===============================================================================
*/

package handler

import (
	"encoding/json"
	"net/http"

	"compliance-governance-agent/internal/policy"
)

type JSONRPCRequest struct {
	JSONRPC string          `json:"jsonrpc"`
	ID      interface{}     `json:"id"`
	Method  string          `json:"method"`
	Params  json.RawMessage `json:"params"`
}

type JSONRPCResponse struct {
	JSONRPC string      `json:"jsonrpc"`
	ID      interface{} `json:"id"`
	Result  interface{} `json:"result,omitempty"`
	Error   interface{} `json:"error,omitempty"`
}

type A2AMessage struct {
	Message struct {
		Parts []struct {
			Text string `json:"text"`
			Data struct {
				CaseID   string                    `json:"case_id"`
				Facts    policy.ContractFacts      `json:"facts"`
				Variance policy.HistoricalVariance `json:"variance"`
			} `json:"data"`
		} `json:"parts"`
	} `json:"message"`
}

func HandleJSONRPC() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		// TODO EXERCISE B.2:
		// 1. Decode incoming JSON-RPC 2.0 request into `var req JSONRPCRequest`.
		// 2. Validate that req.Method is "message/send" (return JSON-RPC error code -32601 if not).
		// 3. Unmarshal req.Params into `A2AMessage` struct (return JSON-RPC error code -32602 if invalid).
		// 4. Extract ContractFacts and HistoricalVariance from msg.Message.Parts[0].Data.
		// 5. Call policy.EvaluateContractPolicy(facts, variance).
		// 6. Wrap result in JSONRPCResponse{JSONRPC: "2.0", ID: req.ID, Result: result} and encode as JSON.
		http.Error(w, "Exercise B.2: Implement HandleJSONRPC() in internal/handler/jsonrpc.go", http.StatusNotImplemented)
	}
}

