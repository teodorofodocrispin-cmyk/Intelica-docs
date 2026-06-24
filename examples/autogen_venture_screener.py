"""
Intelica + AutoGen — Venture Screening Multi-Agent
===================================================
A multi-agent AutoGen workflow that screens a startup or market
using Intelica's venture_screening mode. Two agents collaborate:
  - Screener: calls Intelica and extracts the investment signal
  - Investment Committee: reads decision_recommendation and gives
    a structured invest/pass/watch verdict with reasoning.

Install:
    pip install pyautogen requests

Usage:
    python autogen_venture_screener.py
"""

import requests
import json
import autogen


INTELICA_SESSION = "your-session-key"  # Get one at https://api.intelica.dev

# ── LLM Config ───────────────────────────────────────────────────────────────

llm_config = {
    "model": "gpt-4o-mini",
    "api_key": "your-openai-api-key",
    "temperature": 0.1,
}


# ── Intelica Tool ─────────────────────────────────────────────────────────────

def run_venture_screen(company_description: str) -> str:
    """
    Screen a startup or market using Intelica venture_screening mode.
    Returns IMI, investment signals, and decision_recommendation.
    """
    response = requests.post(
        "https://api.intelica.dev/intel",
        headers={"X-SESSION": INTELICA_SESSION, "Content-Type": "application/json"},
        json={"text": company_description, "mode": "venture_screening"},
        timeout=60
    )

    if response.status_code != 200:
        return f"Error calling Intelica: {response.status_code}"

    result = response.json()
    market_score = result.get("market_score", {})
    decision = result.get("decision_recommendation", {})
    brief = result.get("executive_brief", {})
    plan = result.get("execution_plan", {})

    return json.dumps({
        "company": result.get("company_or_product", "Unknown"),
        "imi": market_score.get("intelica_moat_index", 0),
        "threat_level": market_score.get("threat_level", "unknown"),
        "market_maturity": market_score.get("market_maturity", "unknown"),
        "decision": {
            "action": decision.get("action", "monitor"),
            "confidence": decision.get("confidence_score", 0.5),
            "rationale": decision.get("rationale", ""),
            "risk_level": decision.get("risk_level", "medium")
        },
        "investment_thesis": result.get("positioning_summary", ""),
        "top_risks": result.get("user_pain_points", [])[:3],
        "moat_factors": result.get("core_value_props", [])[:3],
        "competitors": result.get("detected_competitors", [])[:3],
        "unique_angle": result.get("unique_angle", ""),
        "leader": brief.get("leader", ""),
        "recent_move": brief.get("recent_move", ""),
        "critical_risk": brief.get("critical_risk", ""),
        "barriers": plan.get("barriers", [])[:2],
        "validation_signals": plan.get("validation_signals", [])[:2],
    }, indent=2)


# ── Agents ────────────────────────────────────────────────────────────────────

screener = autogen.AssistantAgent(
    name="Venture_Screener",
    system_message="""You are a venture capital analyst. Your job is to:
1. Call run_venture_screen() with the company description provided
2. Parse the JSON result carefully
3. Summarize the key investment signals in this format:

INTELICA SCREEN RESULTS
=======================
Company: [name]
IMI Score: [score] ([interpretation: <0.50=weak moat, 0.50-0.65=moderate, 0.65-0.80=strong, >0.80=very strong])
Market Stage: [maturity]

DECISION SIGNAL
===============
Action: [action in caps]
Confidence: [confidence as percentage]
Risk Level: [risk_level]
Rationale: [rationale]

INVESTMENT SIGNALS
==================
Thesis: [investment_thesis]
Unique Angle: [unique_angle]
Top Moat Factors: [moat_factors as bullets]
Top Risks: [top_risks as bullets]
Key Competitors: [competitors]
Validation Signals: [validation_signals]

Pass this summary to the Investment_Committee for the final verdict.""",
    llm_config=llm_config,
    function_map={"run_venture_screen": run_venture_screen}
)

committee = autogen.AssistantAgent(
    name="Investment_Committee",
    system_message="""You are a senior investment committee member. 
Based on the Intelica screen results from the Venture_Screener, you must deliver:

INVESTMENT COMMITTEE VERDICT
=============================
DECISION: INVEST / PASS / WATCH

Confidence Adjustment: [agree/adjust the confidence and explain why]

Key Reasons: [3 bullet points — most important factors in your decision]

Due Diligence Priority: [2 things to verify before committing capital]

Terms Consideration: [if INVEST — what valuation ceiling or structure makes sense given the IMI and risk level]

Red Line: [the single condition that would flip this decision]

Be direct. No hedging. The committee needs a clear answer.
When done, say TERMINATE.""",
    llm_config=llm_config,
)

user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=6,
    is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
    function_map={"run_venture_screen": run_venture_screen},
    code_execution_config=False,
)


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    target = (
        "Parano.ai — AI-native competitive intelligence platform for B2B sales teams. "
        "Real-time battlecards, competitor tracking, and win/loss analysis. "
        "YC-backed, $3M seed, 40 enterprise customers."
    )

    print(f"\n{'='*60}")
    print("INTELICA VENTURE SCREENING AGENT")
    print(f"Target: {target[:80]}...")
    print(f"{'='*60}\n")

    # Register the tool for both agents
    autogen.register_function(
        run_venture_screen,
        caller=screener,
        executor=user_proxy,
        name="run_venture_screen",
        description="Screen a startup using Intelica venture_screening mode. Returns IMI, moat analysis, and decision_recommendation."
    )

    user_proxy.initiate_chat(
        screener,
        message=f"""Screen this investment target using Intelica and then pass results to Investment_Committee:

{target}

Use run_venture_screen() first, then summarize for the committee.""",
        max_turns=6
    )
