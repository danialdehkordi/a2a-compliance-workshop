/*
===============================================================================
🏛️ STAGE 2 IMPLEMENTATION: Group B - Go JSON-RPC 2.0 Router
===============================================================================
*/

package handler

import (
	"encoding/json"
	"fmt"
	"net/http"

	"compliance-governance-agent/internal/policy"
)

type JSONRPCRequest struct {
	JSONRPC string          `json:"jsonrpc"`
	ID      interface{}     `json:"id"`
	Method  string          `json:"method"`
	Params  json.RawMessage `json:"params"`
}

type JSONRPCError struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
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
			res := JSONRPCResponse{
				JSONRPC: "2.0",
				ID:      nil,
				Error: JSONRPCError{
					Code:    -32700,
					Message: "Parse error: " + err.Error(),
				},
			}
			json.NewEncoder(w).Encode(res)
			return
		}

		if req.Method != "message/send" {
			res := JSONRPCResponse{
				JSONRPC: "2.0",
				ID:      req.ID,
				Error: JSONRPCError{
					Code:    -32601,
					Message: "Method not found",
				},
			}
			json.NewEncoder(w).Encode(res)
			return
		}

		var a2aMsg A2AMessage
		if err := json.Unmarshal(req.Params, &a2aMsg); err != nil || len(a2aMsg.Message.Parts) == 0 {
			res := JSONRPCResponse{
				JSONRPC: "2.0",
				ID:      req.ID,
				Error: JSONRPCError{
					Code:    -32602,
					Message: "Invalid params",
				},
			}
			json.NewEncoder(w).Encode(res)
			return
		}

		partData := a2aMsg.Message.Parts[0].Data
		facts := partData.Facts
		if facts.CaseID == "" {
			if partData.CaseID != "" {
				facts.CaseID = partData.CaseID
			} else if req.ID != nil {
				facts.CaseID = fmt.Sprintf("%v", req.ID)
			}
		}

		variance := partData.Variance
		result := policy.EvaluateContractPolicy(facts, variance)

		res := JSONRPCResponse{
			JSONRPC: "2.0",
			ID:      req.ID,
			Result:  result,
		}
		json.NewEncoder(w).Encode(res)
	}
}

