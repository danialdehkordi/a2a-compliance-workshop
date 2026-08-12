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

		var req JSONRPCRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid JSON-RPC request", http.StatusBadRequest)
			return
		}

		if req.Method != "message/send" {
			res := JSONRPCResponse{
				JSONRPC: "2.0",
				ID:      req.ID,
				Error:   map[string]interface{}{"code": -32601, "message": "Method not found"},
			}
			json.NewEncoder(w).Encode(res)
			return
		}

		var msg A2AMessage
		if err := json.Unmarshal(req.Params, &msg); err != nil {
			res := JSONRPCResponse{
				JSONRPC: "2.0",
				ID:      req.ID,
				Error:   map[string]interface{}{"code": -32602, "message": "Invalid params"},
			}
			json.NewEncoder(w).Encode(res)
			return
		}

		facts := policy.ContractFacts{
			CaseID:          "case-default",
			VendorName:      "Acme Corp",
			ContractValue:   450000.0,
			TermYears:       3,
			LiabilityCap:    "limited",
			InsuranceAmount: 2000000.0,
		}
		variance := policy.HistoricalVariance{}

		if len(msg.Message.Parts) > 0 {
			data := msg.Message.Parts[0].Data
			if data.CaseID != "" {
				facts.CaseID = data.CaseID
			}
			if data.Facts.VendorName != "" {
				facts = data.Facts
			}
			variance = data.Variance
		}

		result := policy.EvaluateContractPolicy(facts, variance)

		res := JSONRPCResponse{
			JSONRPC: "2.0",
			ID:      req.ID,
			Result:  result,
		}

		json.NewEncoder(w).Encode(res)
	}
}
