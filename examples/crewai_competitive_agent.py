"""
Intelica + CrewAI — Competitive Decision Agent
===============================================
A CrewAI agent that analyzes a market, reads decision_recommendation,
and autonomously decides the next action: enter, avoid, monitor, acquire, or partner.

Install:
    pip install crewai requests

Usage:
    python crewai_competitive_agent.py
"""

import requests
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool


INTELICA_SESSION = "your-session-key"  # Get one at https://api.intelica.dev


# ── Tool ──────────────────────────────────────────────────────────────────────

@tool("competitive_intelligence")
def analyze_market(query: str) -> str:
    """
    Analyze a company or market using Intelica.
    Returns IMI score, detected competitors, and a decision_recommendation
    with explicit action (enter/avoid/monitor/acquire/partner),
    confidence_score, rationale, and risk_level.
    """
    response = requests.post(
        "https://api.intelica.dev/intel",
        headers={"X-SESSION": INTELICA_SESSION, "Content-Type": "application/json"},
        json={"text": query, "mode": "competitive"},
        timeout=60
    )
    result = response.json()

    market_score = result.get("market_score", {})
    decision = result.get("decision_recommendation", {})
    competitors = result.get("detected_competitors", [])
    brief = result.get("executive_brief", {})

    return f"""
INTELICA ANALYSIS
=================
Company/Market: {result.get('company_or_product', 'Unknown')}
IMI Score: {market_score.get('intelica_moat_index', 'N/A')}
Threat Level: {market_score.get('threat_level', 'N/A')}
Market Maturity: {market_score.get('market_maturity', 'N/A')}

DECISION RECOMMENDATION
=======================
Action:           {decision.get('action', 'monitor').upper()}
Confidence:       {decision.get('confidence_score', 0.5):.0%}
Risk Level:       {decision.get('risk_level', 'medium')}
Rationale:        {decision.get('rationale', 'N/A')}

COMPETITIVE LANDSCAPE
=====================
Leader:           {brief.get('leader', 'N/A')}
Recent Move:      {brief.get('recent_move', 'N/A')}
Critical Risk:    {brief.get('critical_risk', 'N/A')}
Top Competitors:  {', '.join(competitors[:3])}

Unique Angle:     {result.get('unique_angle', 'N/A')}
"""


# ── Agents ────────────────────────────────────────────────────────────────────

market_analyst = Agent(
    role="Market Intelligence Analyst",
    goal="Analyze competitive markets and extract actionable intelligence using Intelica",
    backstory=(
        "You are a senior market analyst specialized in competitive intelligence. "
        "You use Intelica to evaluate any market or company and interpret the results "
        "to produce clear, data-backed recommendations. You always anchor your conclusions "
        "to the decision_recommendation field and the IMI score."
    ),
    tools=[analyze_market],
    verbose=True
)

strategy_advisor = Agent(
    role="Market Entry Strategy Advisor",
    goal="Translate competitive intelligence into a concrete go/no-go decision and next steps",
    backstory=(
        "You are a strategic advisor who reads market intelligence reports and decides "
        "whether to enter, avoid, monitor, acquire, or partner. You always explain the "
        "reasoning clearly and propose 3 concrete next actions based on the decision."
    ),
    verbose=True
)


# ── Tasks ─────────────────────────────────────────────────────────────────────

def build_crew(market_query: str) -> Crew:
    analyze_task = Task(
        description=f"""
        Use the competitive_intelligence tool to analyze this market or company:
        "{market_query}"

        Extract and summarize:
        1. The IMI score and what it means for this market
        2. The decision_recommendation (action, confidence, rationale, risk)
        3. The top 3 competitors and what makes them strong
        4. The unique angle or gap that could be exploited
        """,
        expected_output=(
            "A structured market intelligence summary with IMI score, "
            "decision recommendation, competitor landscape, and key opportunity."
        ),
        agent=market_analyst
    )

    strategy_task = Task(
        description="""
        Based on the market intelligence report from the analyst:

        1. State the recommended action (enter/avoid/monitor/acquire/partner) and why
        2. Assess whether the confidence_score justifies acting now or waiting
        3. Propose exactly 3 concrete next actions the team should take this week
        4. Flag the single biggest risk if the recommendation is wrong

        Be direct. No hedging. The team needs a clear decision.
        """,
        expected_output=(
            "A go/no-go decision with justification, 3 concrete next actions, "
            "and the primary risk to monitor."
        ),
        agent=strategy_advisor
    )

    return Crew(
        agents=[market_analyst, strategy_advisor],
        tasks=[analyze_task, strategy_task],
        process=Process.sequential,
        verbose=True
    )


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Example: evaluate the B2B SaaS competitive intelligence market
    market_query = (
        "AlphaSense competitive intelligence platform for enterprise — "
        "AI-powered market intelligence, financial research, and competitive tracking"
    )

    print(f"\n{'='*60}")
    print(f"INTELICA COMPETITIVE DECISION AGENT")
    print(f"Query: {market_query}")
    print(f"{'='*60}\n")

    crew = build_crew(market_query)
    result = crew.kickoff()

    print(f"\n{'='*60}")
    print("FINAL STRATEGY DECISION")
    print(f"{'='*60}")
    print(result)
