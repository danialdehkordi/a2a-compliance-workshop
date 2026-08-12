# Group A (Stage 1): Python ADK Field Extractor & Orchestration Agent

This repository contains the Group A (Stage 1) starter code for the **Enterprise Multi-Agent Compliance Workshop**.

## 🚀 Quickstart Local Testing

```bash
# 1. Install dependencies
uv sync

# 2. Run local unit tests
uv run python -m pytest

# 3. Start local server (Runs with local A2A mock stub by default)
USE_A2A_MOCK="true" uv run uvicorn app.main:app --reload --port 8000
```

## 🛠️ Your Workshop Exercises (Group A / Stage 1)

1. **`TODO 1` ([`app/tools.py`](file:///home/user/a2a-compliance-workshop/extraction-orchestration-agent/app/tools.py))**: Implement Gemini 2.0 Pydantic Schema Extractor or RegEx pattern matcher.
2. **`TODO 2` ([`app/tools.py`](file:///home/user/a2a-compliance-workshop/extraction-orchestration-agent/app/tools.py))**: Calculate percentage variance against SQLite baseline.
3. **`TODO 3` ([`app/agent.py`](file:///home/user/a2a-compliance-workshop/extraction-orchestration-agent/app/agent.py))**: Wire up `RemoteA2aAgent` to dispatch JSON-RPC payloads to Group B's live Agent Card URL.
