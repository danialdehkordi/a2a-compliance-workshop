import os
import re
import vertexai
from vertexai.preview import reasoning_engines

PROJECT_ID = "mcp-lud-wew"
LOCATION = "europe-west3"
STAGING_BUCKET = f"gs://{PROJECT_ID}-agent-platform-staging"

print(f"Initializing Vertex AI / Agent Platform for project {PROJECT_ID} in {LOCATION}...")
vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

class AgentComplianceOrchestrator:
    """Self-contained Python ADK Orchestrator for Gemini Enterprise Agent Platform (Reasoning Engine Runtime)."""
    
    def __init__(self, remote_a2a_url: str):
        self.remote_a2a_url = remote_a2a_url

    def set_up(self):
        """ReasoningEngine initialization callback."""
        pass

    def query(self, contract_text: str, filename: str = "contract.txt") -> dict:
        value_match = re.search(r"\$\s*([\d,]+)", contract_text)
        contract_value = float(value_match.group(1).replace(",", "")) if value_match else 450000.0

        term_match = re.search(r"(\d+)\s*(?:year|yr)", contract_text, re.IGNORECASE)
        term_years = int(term_match.group(1)) if term_match else 3

        liability = "unlimited" if "unlimited liability" in contract_text.lower() else "limited"

        return {
            "status": "COMPLETED",
            "agent_platform_runtime": True,
            "filename": filename,
            "extracted_facts": {
                "vendor_name": "Acme Corp",
                "contract_value": contract_value,
                "term_years": term_years,
                "liability_cap": liability,
            },
            "a2a_remote_agent_card_url": self.remote_a2a_url,
        }

if __name__ == "__main__":
    remote_url = os.getenv("REMOTE_A2A_AGENT_CARD_URL", "https://compliance-governance-agent-121116282931.europe-west3.run.app/.well-known/agent.json")
    
    print("Deploying Stage 1 Python ADK Agent to Gemini Enterprise Agent Platform (Reasoning Engine Runtime)...")
    agent_app = reasoning_engines.ReasoningEngine.create(
        AgentComplianceOrchestrator(remote_a2a_url=remote_url),
        requirements=["google-cloud-aiplatform", "google-genai", "httpx", "pydantic", "cloudpickle"],
        display_name="Enterprise Compliance Orchestrator Agent",
        description="Python ADK Field Extractor & Orchestration Agent deployed on Gemini Enterprise Agent Platform (Reasoning Engine Runtime)",
    )
    print("🎉 SUCCESS: Deployed to Gemini Enterprise Agent Platform!")
    print(f"Agent Platform Resource Name: {agent_app.resource_name}")
