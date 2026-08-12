package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"compliance-governance-agent/internal/agentcard"
	"compliance-governance-agent/internal/handler"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8888"
	}

	baseURL := os.Getenv("BASE_URL")
	if baseURL == "" {
		baseURL = fmt.Sprintf("http://localhost:%s", port)
	}

	mux := http.NewServeMux()

	// A2A Agent Card Discovery Route
	mux.HandleFunc("/.well-known/agent.json", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodGet {
			agentcard.HandleAgentCard(baseURL)(w, r)
		} else {
			handler.HandleJSONRPC()(w, r)
		}
	})

	// A2A JSON-RPC Message Router
	mux.HandleFunc("/", handler.HandleJSONRPC())

	log.Printf("🚀 Compliance Governance Agent (Go) listening on port %s", port)
	log.Printf("📌 Root Base URL: %s", baseURL)

	if err := http.ListenAndServe(":"+port, mux); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}
