"""
Intelica + LangGraph — Market Entry Decision Graph
===================================================
A LangGraph workflow where Intelica acts as the decision node.
The graph reads decision_recommendation.action and routes automatically:
  - "enter"   → build GTM plan
  - "avoid"   → find alternative market
  - "monitor" → subscribe to Intelica Pulse for alerts
  - "acquire" → generate acquisition brief
  - "partner" → identify partnership angle

Install:
    pip install langgraph langchain-openai requests

Usage:
    python langgraph_market_entry_node.py
"""

import requests
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI


INTELICA_SESSION = "your-session-key"  # Get one at https://api.intelica.dev
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ── State ─────────────────────────────────────────────────────────────────────

class MarketState(TypedDict):
    query: str                      # Input: market or company to evaluate
    intelica_result: dict           # Raw Intelica response
    action: str                     # decision_recommendation.action
    confidence: float               # decision_recommendation.confidence_score
    rationale: str                  # decision_recommendation.rationale
    risk_level: str                 # decision_recommendation.risk_level
    imi: float                      # Intelica Moat Index
    competitors: list               # detected_competitors
    execution_plan: dict            # execution_plan from Intelica
    final_output: str               # Final decision + next steps


# ── Nodes ─────────────────────────────────────────────────────────────────────

def intelica_analysis_node(state: MarketState) -> MarketState:
    """Call Intelica API and extract decision_recommendation."""
    response = requests.post(
        "https://api.intelica.dev/intel",
        headers={"X-SESSION": INTELICA_SESSION, "Content-Type": "application/json"},
        json={"text": state["query"], "mode": "market_entry_execution"},
        timeout=60
    )
    result = response.json()
    market_score = result.get("market_score", {})
    decision = result.get("decision_recommendation", {})

    return {
        **state,
        "intelica_result": result,
        "action": decision.get("action", "monitor"),
        "confidence": decision.get("confidence_score", 0.5),
        "rationale": decision.get("rationale", ""),
        "risk_level": decision.get("risk_level", "medium"),
        "imi": market_score.get("intelica_moat_index", 0.5),
        "competitors": result.get("detected_competitors", []),
        "execution_plan": result.get("execution_plan", {}),
    }


def enter_market_node(state: MarketState) -> MarketState:
    """Build a concrete GTM plan based on Intelica's execution_plan."""
    plan = state["execution_plan"]
    week1 = plan.get("week_1_actions", [])
    channels = plan.get("priority_channels", [])
    budget = plan.get("budget_guidance", {}).get("phase_1_usd", "N/A")

    prompt = f"""
    Intelica recommends ENTERING this market (confidence: {state['confidence']:.0%}).
    Rationale: {state['rationale']}
    IMI: {state['imi']} — barriers are surmountable.

    Week 1 actions from Intelica: {week1}
    Priority channels: {channels}
    Phase 1 budget: {budget}

    Write a 5-bullet Go-To-Market action plan for this week. Be specific and direct.
    """
    response = llm.invoke(prompt)
    return {**state, "final_output": f"ACTION: ENTER\n\n{response.content}"}


def avoid_market_node(state: MarketState) -> MarketState:
    """Explain why to avoid and suggest adjacent opportunities."""
    competitors_str = ", ".join(state["competitors"][:3])
    prompt = f"""
    Intelica recommends AVOIDING this market (confidence: {state['confidence']:.0%}).
    Rationale: {state['rationale']}
    IMI: {state['imi']} — moat is too strong.
    Top incumbents: {competitors_str}

    1. Explain in 2 sentences why this market should be avoided now.
    2. Suggest 2 adjacent market opportunities where the moat is weaker.
    3. State one condition that would change this recommendation.
    """
    response = llm.invoke(prompt)
    return {**state, "final_output": f"ACTION: AVOID\n\n{response.content}"}


def monitor_market_node(state: MarketState) -> MarketState:
    """Subscribe to Intelica Pulse and define monitoring criteria."""
    # Subscribe to Pulse for automatic IMI change alerts
    pulse_response = requests.post(
        "https://api.intelica.dev/pulse/subscribe",
        headers={"X-SESSION": INTELICA_SESSION, "Content-Type": "application/json"},
        json={
            "session_id": INTELICA_SESSION,
            "watch_company": state["query"][:100],
            "imi_threshold": 0.05,
            "webhook_url": "https://your-agent.com/intelica-alerts"
        },
        timeout=30
    )
    pulse_status = "subscribed" if pulse_response.status_code == 200 else "manual monitoring required"

    prompt = f"""
    Intelica recommends MONITORING this market (confidence: {state['confidence']:.0%}).
    Rationale: {state['rationale']}
    IMI: {state['imi']} — market is in transition.
    Pulse subscription: {pulse_status}

    Define 3 specific trigger signals that would upgrade this to "enter" recommendation.
    Each signal must be measurable and have a clear timeline.
    """
    response = llm.invoke(prompt)
    return {**state, "final_output": f"ACTION: MONITOR (Pulse: {pulse_status})\n\n{response.content}"}


def acquire_market_node(state: MarketState) -> MarketState:
    """Generate an acquisition brief for the target."""
    competitors_str = ", ".join(state["competitors"][:3])
    prompt = f"""
    Intelica recommends ACQUIRING a player in this market (confidence: {state['confidence']:.0%}).
    Rationale: {state['rationale']}
    IMI: {state['imi']} — strong moat, but acquirable.
    Acquisition candidates: {competitors_str}

    Write a concise acquisition brief:
    1. Primary acquisition target and why
    2. Strategic rationale (what moat does it add?)
    3. 3 due diligence questions to answer before proceeding
    """
    response = llm.invoke(prompt)
    return {**state, "final_output": f"ACTION: ACQUIRE\n\n{response.content}"}


def partner_market_node(state: MarketState) -> MarketState:
    """Identify the best partnership angle."""
    competitors_str = ", ".join(state["competitors"][:3])
    prompt = f"""
    Intelica recommends PARTNERING in this market (confidence: {state['confidence']:.0%}).
    Rationale: {state['rationale']}
    IMI: {state['imi']} — complementary moats, alliance > competition.
    Potential partners: {competitors_str}

    Write a partnership brief:
    1. Best partner candidate and what they bring
    2. What you bring to the partnership
    3. 3 concrete first steps to initiate the conversation
    """
    response = llm.invoke(prompt)
    return {**state, "final_output": f"ACTION: PARTNER\n\n{response.content}"}


# ── Router ────────────────────────────────────────────────────────────────────

def route_decision(state: MarketState) -> Literal["enter", "avoid", "monitor", "acquire", "partner"]:
    """Route based on Intelica's decision_recommendation.action."""
    action = state.get("action", "monitor")
    print(f"\n→ Intelica decision: {action.upper()} (confidence: {state.get('confidence', 0):.0%}, risk: {state.get('risk_level', 'medium')})")
    print(f"→ Rationale: {state.get('rationale', '')}\n")
    return action if action in {"enter", "avoid", "monitor", "acquire", "partner"} else "monitor"


# ── Graph ─────────────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(MarketState)

    graph.add_node("intelica_analysis", intelica_analysis_node)
    graph.add_node("enter", enter_market_node)
    graph.add_node("avoid", avoid_market_node)
    graph.add_node("monitor", monitor_market_node)
    graph.add_node("acquire", acquire_market_node)
    graph.add_node("partner", partner_market_node)

    graph.set_entry_point("intelica_analysis")

    graph.add_conditional_edges(
        "intelica_analysis",
        route_decision,
        {
            "enter": "enter",
            "avoid": "avoid",
            "monitor": "monitor",
            "acquire": "acquire",
            "partner": "partner",
        }
    )

    for node in ["enter", "avoid", "monitor", "acquire", "partner"]:
        graph.add_edge(node, END)

    return graph.compile()


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    market_query = (
        "NNormal trail running brand APAC market entry — "
        "outdoor apparel and footwear targeting Thailand and Southeast Asia"
    )

    print(f"\n{'='*60}")
    print("INTELICA MARKET ENTRY DECISION GRAPH")
    print(f"Query: {market_query}")
    print(f"{'='*60}\n")

    app = build_graph()
    final_state = app.invoke({
        "query": market_query,
        "intelica_result": {},
        "action": "",
        "confidence": 0.0,
        "rationale": "",
        "risk_level": "",
        "imi": 0.0,
        "competitors": [],
        "execution_plan": {},
        "final_output": ""
    })

    print(f"\n{'='*60}")
    print("FINAL OUTPUT")
    print(f"{'='*60}")
    print(final_state["final_output"])
