"""
Intelica + Amazon Bedrock AgentCore Payments
=============================================
This example shows how to build an agent on Amazon Bedrock AgentCore
that autonomously discovers and pays for Intelica competitive intelligence
using x402 micropayments — no API keys, no subscriptions.

Requirements:
    pip install bedrock-agentcore strands-agents strands-tools boto3

Setup:
    1. AWS account with AgentCore access (us-east-1, us-west-2, eu-central-1, ap-southeast-2)
    2. Coinbase CDP wallet funded with USDC on Base
    3. AgentCore PaymentManager configured with CDP connector

Docs: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-getting-started.html
API:  https://api.intelica.dev
"""

import json
import boto3
from strands import Agent
from strands_tools import http_request
from bedrock_agentcore.payments.integrations.config import AgentCorePaymentsPluginConfig
from bedrock_agentcore.payments.integrations.strands.plugin import AgentCorePaymentsPlugin

# ── AgentCore Payment Configuration ──────────────────────────────────────────
# Replace these with your actual AgentCore resource ARNs
PAYMENT_MANAGER_ARN  = "arn:aws:bedrock-agentcore:us-east-1:YOUR_ACCOUNT:payment-manager/pm-YOUR_ID"
PAYMENT_INSTRUMENT_ID = "payment-instrument-YOUR_ID"  # Coinbase CDP wallet
PAYMENT_SESSION_ID   = "payment-session-YOUR_ID"       # Created per agent run
USER_ID              = "your-user-id"
AWS_REGION           = "us-east-1"

# Intelica endpoint — no API key needed, agent pays per call via x402
INTELICA_ENDPOINT = "https://api.intelica.dev/intel"


def create_payment_session(payment_manager_arn: str, spend_limit_usd: float = 5.0) -> str:
    """
    Create a scoped payment session with spending limit.
    Each session tracks spend for one agent interaction.
    """
    client = boto3.client("bedrock-agentcore", region_name=AWS_REGION)
    response = client.create_payment_session(
        paymentManagerArn=payment_manager_arn,
        userId=USER_ID,
        paymentInstrumentId=PAYMENT_INSTRUMENT_ID,
        maxSpendAmount=str(int(spend_limit_usd * 1_000_000)),  # in USDC micro-units
        currency="USDC",
    )
    return response["paymentSessionId"]


def build_intelica_agent(payment_session_id: str) -> Agent:
    """
    Build a Strands agent with AgentCore payments plugin.
    When the agent calls Intelica and receives HTTP 402,
    AgentCore automatically signs the x402 payment and retries.
    """
    config = AgentCorePaymentsPluginConfig(
        payment_manager_arn=PAYMENT_MANAGER_ARN,
        user_id=USER_ID,
        payment_instrument_id=PAYMENT_INSTRUMENT_ID,
        payment_session_id=payment_session_id,
        region=AWS_REGION,
    )
    plugin = AgentCorePaymentsPlugin(config=config)

    system_prompt = """You are a competitive intelligence analyst powered by Intelica.

When asked to analyze a company or market, call the Intelica API:
POST https://api.intelica.dev/intel
Content-Type: application/json

Body: {"text": "<company or market description>", "mode": "competitive"}

The API costs $0.05 USDC per standard analysis. Payment is handled automatically.

After receiving the response, extract and present:
- IMI Score (intelica_moat_index): 0.0-1.0 structural moat strength  
- Decision (decision_recommendation.action): enter/avoid/monitor/acquire/partner
- Confidence (decision_recommendation.confidence_score): data richness
- Key competitors (detected_competitors)
- Non-obvious insight (execution_plan.non_obvious_insight)
- Week 1 actions (execution_plan.week_1_actions)

Always include the rationale behind the decision."""

    return Agent(
        model="us.anthropic.claude-sonnet-4-5-20251001-v1:0",
        system_prompt=system_prompt,
        tools=[http_request],
        plugins=[plugin],
    )


def analyze_market(query: str, spend_limit_usd: float = 1.0) -> dict:
    """
    Run competitive intelligence analysis using Intelica via AgentCore payments.

    Args:
        query: Company or market to analyze
        spend_limit_usd: Maximum USDC to spend per session (default $1.00)

    Returns:
        dict with analysis results

    Example:
        result = analyze_market("Stripe competitor for Southeast Asia payment infrastructure")
        print(result["action"])     # "avoid"
        print(result["imi"])        # 0.82
        print(result["insight"])    # "The exploitable gap is local payment coverage..."
    """
    session_id = create_payment_session(PAYMENT_MANAGER_ARN, spend_limit_usd)
    agent = build_intelica_agent(session_id)

    response = agent(f"Analyze this for competitive market entry: {query}")
    return {"query": query, "response": str(response), "session_id": session_id}


# ── LangGraph integration ─────────────────────────────────────────────────────
def intelica_langgraph_node(state: dict) -> dict:
    """
    LangGraph node that calls Intelica and routes based on decision_recommendation.action.

    Usage in a LangGraph graph:
        graph.add_node("market_analysis", intelica_langgraph_node)
        graph.add_conditional_edges("market_analysis", route_by_action)
    """
    import requests

    idea = state.get("idea", "")
    headers = {"Content-Type": "application/json"}
    # No API key — agent pays via x402 automatically when using AgentCore
    payload = {"text": idea, "mode": "venture_screening"}

    response = requests.post(INTELICA_ENDPOINT, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        dr = data.get("decision_recommendation", {})
        return {
            **state,
            "action":       dr.get("action", "monitor"),
            "confidence":   dr.get("confidence_score", 0),
            "imi":          data.get("intelica_moat_index", 0),
            "rationale":    dr.get("rationale", ""),
            "competitors":  data.get("detected_competitors", []),
            "week_1":       data.get("execution_plan", {}).get("week_1_actions", []),
            "insight":      data.get("execution_plan", {}).get("non_obvious_insight", ""),
            "auto_executed": data.get("auto_executed"),
        }
    elif response.status_code == 402:
        # x402 payment required — AgentCore handles this automatically
        # if not using AgentCore, implement x402 payment flow here
        raise Exception(f"Payment required: {response.json()}")
    else:
        raise Exception(f"Intelica API error: {response.status_code}")


def route_by_action(state: dict) -> str:
    """Route LangGraph edges based on Intelica decision."""
    action = state.get("action", "monitor")
    routes = {
        "enter":   "build_gtm_plan",
        "avoid":   "generate_pivot_suggestions",
        "monitor": "schedule_reanalysis",
        "acquire": "identify_acquisition_targets",
        "partner": "map_partnership_opportunities",
    }
    return routes.get(action, "monitor_market")


# ── CrewAI tool ───────────────────────────────────────────────────────────────
def intelica_crewai_tool():
    """
    CrewAI tool that wraps Intelica.
    Payment handled automatically by AgentCore when agent is deployed there.

    Usage:
        from crewai import Agent, Task, Crew
        agent = Agent(role="Market Analyst", tools=[intelica_crewai_tool()])
    """
    from crewai.tools import tool
    import requests

    @tool("intelica_competitive_analysis")
    def analyze(idea: str) -> str:
        """
        Analyze competitive market entry for a startup idea or company.
        Returns IMI score, go/no-go decision, competitors, and execution plan.
        Costs $0.05 USDC via x402 — paid automatically by AgentCore.

        Args:
            idea: Description of the startup idea, company, or market to analyze
        """
        response = requests.post(
            INTELICA_ENDPOINT,
            json={"text": idea, "mode": "competitive"},
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        if response.status_code == 200:
            data = response.json()
            dr = data.get("decision_recommendation", {})
            ep = data.get("execution_plan", {})
            return json.dumps({
                "action":      dr.get("action"),
                "imi":         data.get("intelica_moat_index"),
                "confidence":  dr.get("confidence_score"),
                "rationale":   dr.get("rationale"),
                "competitors": data.get("detected_competitors", []),
                "insight":     ep.get("non_obvious_insight"),
                "week_1":      ep.get("week_1_actions", []),
            }, indent=2)
        return f"Error: {response.status_code}"

    return analyze


# ── CLI demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
        "Stripe competitor for developers in Southeast Asia with local payment methods and lower cross-border fees"

    print(f"\nAnalyzing: {idea[:80]}...\n")
    print("Note: This demo requires AgentCore setup for x402 payments.")
    print("For quick testing, get a free session key at https://api.intelica.dev\n")

    # Direct API call example (requires session key or x402 payment)
    import requests
    response = requests.post(
        INTELICA_ENDPOINT,
        json={"text": idea, "mode": "competitive"},
        headers={"Content-Type": "application/json"},
        timeout=60,
    )

    if response.status_code == 200:
        data = response.json()
        dr = data.get("decision_recommendation", {})
        print(f"IMI Score:  {data.get('intelica_moat_index'):.2f}")
        print(f"Action:     {dr.get('action', '').upper()}")
        print(f"Confidence: {dr.get('confidence_score', 0):.0%}")
        print(f"Rationale:  {dr.get('rationale', '')}")
        insight = data.get("execution_plan", {}).get("non_obvious_insight", "")
        if insight:
            print(f"\nNon-obvious insight:\n  {insight}")
    elif response.status_code == 402:
        pay = response.json()
        print("Payment required — set up AgentCore payments or get a session key:")
        print("  AgentCore: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-getting-started.html")
        print("  Session key: https://api.intelica.dev")
        print(f"\n  Price: ${int(pay['accepts'][0]['amount']) / 1_000_000:.2f} USDC on Base")
