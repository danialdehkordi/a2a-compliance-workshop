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
	agentCardURL := fmt.Sprintf("%s/.well-known/agent.json", baseURL)
	mux.HandleFunc("/.well-known/agent.json", agentcard.HandleAgentCard(agentCardURL))

	// A2A JSON-RPC Message Router
	mux.HandleFunc("/", handler.HandleJSONRPC())

	log.Printf("🚀 Compliance Governance Agent (Go) listening on port %s", port)
	log.Printf("📌 Agent Card URL: %s", agentCardURL)

	if err := http.ListenAndServe(":"+port, mux); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}
