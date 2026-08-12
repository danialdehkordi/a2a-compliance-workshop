# Group B (Stage 2): Go Compliance & Governance Agent

This repository contains the Group B (Stage 2) starter code for the **Enterprise Multi-Agent Compliance Workshop**.

## 🚀 Quickstart Local Testing

```bash
# 1. Run unit tests
go test -v ./...

# 2. Run local HTTP server
go run cmd/server/main.go

# 3. Test Agent Card & JSON-RPC payload in another terminal
bash test_agent.sh
```

## 🛠️ Your Workshop Exercises (Group B / Stage 2)

1. **`TODO 1` ([`internal/agentcard/card.go`](file:///home/user/a2a-compliance-workshop/compliance-governance-agent/internal/agentcard/card.go))**: Serve the A2A Agent Card at `/.well-known/agent.json`.
2. **`TODO 2` ([`internal/handler/jsonrpc.go`](file:///home/user/a2a-compliance-workshop/compliance-governance-agent/internal/handler/jsonrpc.go))**: Parse incoming A2A `message/send` requests and unmarshal JSON-RPC data.
3. **`TODO 3` ([`internal/policy/engine.go`](file:///home/user/a2a-compliance-workshop/compliance-governance-agent/internal/policy/engine.go))**: Implement the deterministic policy engine rules ($500k cap, 5-yr term, liability rules, variance alerts).
