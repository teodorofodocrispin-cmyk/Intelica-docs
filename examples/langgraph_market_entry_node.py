"""
Intelica + LangGraph — Market Entry Decision Graph (No External LLM)
=====================================================================
Intelica already made the decision. The graph just executes it.

decision_recommendation.action routes automatically:
  - "enter"   → print GTM plan from execution_plan
  - "avoid"   → print why and list alternatives
  - "monitor" → subscribe to Intelica Pulse + print trigger signals
  - "acquire" → print acquisition brief
  - "partner" → print partnership angle

Install:
    pip install langgraph requests

Usage:
    python langgraph_market_entry_node.py
"""

import requests
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END


INTELICA_SESSION = "your-session-key"  # Get one at https://api.intelica.dev


# ── State ─────────────────────────────────────────────────────────────────────

class MarketState(TypedDict):
    query: str
    action: str
    confidence: float
    rationale: str
    risk_level: str
    imi: float
    competitors: list
    execution_plan: dict
    executive_brief: dict
    unique_angle: str
    final_output: str


# ── Node 1: Call Intelica ─────────────────────────────────────────────────────

def intelica_node(state: MarketState) -> MarketState:
    """Call Intelica and extract decision_recommendation."""
    print(f"\n[Intelica] Analyzing: {state['query'][:60]}...")

    response = requests.post(
        "https://api.intelica.dev/intel",
        headers={"X-SESSION": INTELICA_SESSION, "Content-Type": "application/json"},
        json={"text": state["query"], "mode": "market_entry_execution"},
        timeout=60
    )

    if response.status_code != 200:
        raise Exception(f"Intelica error: {response.status_code} — {response.text}")

    result = response.json()
    market_score = result.get("market_score", {})
    decision = result.get("decision_recommendation", {})

    print(f"[Intelica] IMI: {market_score.get('intelica_moat_index', 'N/A')}")
    print(f"[Intelica] Action: {decision.get('action', 'monitor').upper()}")
    print(f"[Intelica] Confidence: {decision.get('confidence_score', 0):.0%}")
    print(f"[Intelica] Rationale: {decision.get('rationale', '')}")

    return {
        **state,
        "action":         decision.get("action", "monitor"),
        "confidence":     decision.get("confidence_score", 0.5),
        "rationale":      decision.get("rationale", ""),
        "risk_level":     decision.get("risk_level", "medium"),
        "imi":            market_score.get("intelica_moat_index", 0.5),
        "competitors":    result.get("detected_competitors", []),
        "execution_plan": result.get("execution_plan", {}),
        "executive_brief":result.get("executive_brief", {}),
        "unique_angle":   result.get("unique_angle", ""),
    }


# ── Node 2–6: Action nodes (pure Python, no LLM) ─────────────────────────────

def enter_node(state: MarketState) -> MarketState:
    plan = state["execution_plan"]
    week1 = plan.get("week_1_actions", ["No actions specified"])
    channels = plan.get("priority_channels", ["No channels specified"])
    budget = plan.get("budget_guidance", {}).get("phase_1_usd", "N/A")
    signals = plan.get("validation_signals", [])
    insight = plan.get("non_obvious_insight", "")

    output = f"""
╔══════════════════════════════════════════════════════╗
║  ACTION: ENTER  |  IMI: {state['imi']:.2f}  |  Confidence: {state['confidence']:.0%}  ║
╚══════════════════════════════════════════════════════╝

RATIONALE
{state['rationale']}

WEEK 1 — START HERE
{chr(10).join(f'  • {a}' for a in week1)}

PRIORITY CHANNELS
{chr(10).join(f'  • {c}' for c in channels)}

PHASE 1 BUDGET
  {budget}

VALIDATION SIGNALS (60 days)
{chr(10).join(f'  • {s}' for s in signals)}

NON-OBVIOUS INSIGHT
  {insight}

RISK LEVEL: {state['risk_level'].upper()}
"""
    return {**state, "final_output": output}


def avoid_node(state: MarketState) -> MarketState:
    brief = state["executive_brief"]
    competitors = state["competitors"]

    output = f"""
╔══════════════════════════════════════════════════════╗
║  ACTION: AVOID  |  IMI: {state['imi']:.2f}  |  Confidence: {state['confidence']:.0%}  ║
╚══════════════════════════════════════════════════════╝

RATIONALE
{state['rationale']}

WHY THE MOAT IS TOO STRONG
  Leader:        {brief.get('leader', 'N/A')}
  Recent move:   {brief.get('recent_move', 'N/A')}
  Critical risk: {brief.get('critical_risk', 'N/A')}

INCUMBENTS TO AVOID COMPETING WITH
{chr(10).join(f'  • {c}' for c in competitors[:3])}

UNIQUE ANGLE (if you still want in)
  {state['unique_angle']}

CONDITION TO REVISIT
  Re-run this analysis if IMI drops below 0.65 or a major incumbent exits.

RISK LEVEL: {state['risk_level'].upper()}
"""
    return {**state, "final_output": output}


def monitor_node(state: MarketState) -> MarketState:
    # Subscribe to Intelica Pulse automatically
    pulse_status = "not subscribed"
    try:
        pulse_resp = requests.post(
            "https://api.intelica.dev/pulse/subscribe",
            headers={"X-SESSION": INTELICA_SESSION, "Content-Type": "application/json"},
            json={
                "session_id": INTELICA_SESSION,
                "watch_company": state["query"][:100],
                "imi_threshold": 0.05,
                "webhook_url": "https://your-agent.com/intelica-alerts"
            },
            timeout=20
        )
        pulse_status = "✅ subscribed" if pulse_resp.status_code == 200 else f"⚠ {pulse_resp.status_code}"
    except Exception as e:
        pulse_status = f"⚠ {str(e)[:40]}"

    plan = state["execution_plan"]
    signals = plan.get("validation_signals", [])
    barriers = plan.get("barriers", [])

    output = f"""
╔══════════════════════════════════════════════════════╗
║  ACTION: MONITOR  |  IMI: {state['imi']:.2f}  |  Confidence: {state['confidence']:.0%}  ║
╚══════════════════════════════════════════════════════╝

RATIONALE
{state['rationale']}

INTELICA PULSE
  Status: {pulse_status}
  Alert threshold: IMI change ≥ 5%
  Webhook: https://your-agent.com/intelica-alerts
  (Replace with your endpoint — agent will be notified automatically)

BARRIERS FORMING (watch these)
{chr(10).join(f'  • {b}' for b in barriers[:3])}

TRIGGER SIGNALS — UPGRADE TO "ENTER" IF:
{chr(10).join(f'  • {s}' for s in signals[:3])}

NEXT INTELICA RUN
  Re-analyze in 30 days or when Pulse fires.

RISK LEVEL: {state['risk_level'].upper()}
"""
    return {**state, "final_output": output}


def acquire_node(state: MarketState) -> MarketState:
    competitors = state["competitors"]
    brief = state["executive_brief"]

    output = f"""
╔══════════════════════════════════════════════════════╗
║  ACTION: ACQUIRE  |  IMI: {state['imi']:.2f}  |  Confidence: {state['confidence']:.0%}  ║
╚══════════════════════════════════════════════════════╝

RATIONALE
{state['rationale']}

ACQUISITION CANDIDATES
{chr(10).join(f'  {i+1}. {c}' for i, c in enumerate(competitors[:3]))}

STRATEGIC RATIONALE
  Leader:      {brief.get('leader', 'N/A')}
  Recent move: {brief.get('recent_move', 'N/A')}
  Moat value:  IMI {state['imi']:.2f} — acquiring this moat is cheaper than building it.

DUE DILIGENCE PRIORITIES
  1. Verify exclusivity agreements and IP ownership
  2. Assess customer concentration risk
  3. Map team retention risk post-acquisition

RISK LEVEL: {state['risk_level'].upper()}
"""
    return {**state, "final_output": output}


def partner_node(state: MarketState) -> MarketState:
    competitors = state["competitors"]
    plan = state["execution_plan"]
    partner_types = plan.get("partner_types", [])

    output = f"""
╔══════════════════════════════════════════════════════╗
║  ACTION: PARTNER  |  IMI: {state['imi']:.2f}  |  Confidence: {state['confidence']:.0%}  ║
╚══════════════════════════════════════════════════════╝

RATIONALE
{state['rationale']}

PARTNER CANDIDATES
{chr(10).join(f'  {i+1}. {c}' for i, c in enumerate(competitors[:3]))}

PARTNER TYPES INTELICA IDENTIFIED
{chr(10).join(f'  • {p}' for p in partner_types[:3])}

UNIQUE ANGLE FOR OUTREACH
  {state['unique_angle']}

FIRST 3 STEPS
  1. Map which candidate has the weakest internal distribution in your target region
  2. Request intro through a mutual connection — avoid cold outreach
  3. Lead with data: show them the IMI gap your partnership would close

RISK LEVEL: {state['risk_level'].upper()}
"""
    return {**state, "final_output": output}


# ── Router ────────────────────────────────────────────────────────────────────

def route(state: MarketState) -> Literal["enter", "avoid", "monitor", "acquire", "partner"]:
    action = state.get("action", "monitor")
    return action if action in {"enter", "avoid", "monitor", "acquire", "partner"} else "monitor"


# ── Build Graph ───────────────────────────────────────────────────────────────

def build_graph():
    g = StateGraph(MarketState)

    g.add_node("intelica", intelica_node)
    g.add_node("enter",   enter_node)
    g.add_node("avoid",   avoid_node)
    g.add_node("monitor", monitor_node)
    g.add_node("acquire", acquire_node)
    g.add_node("partner", partner_node)

    g.set_entry_point("intelica")
    g.add_conditional_edges("intelica", route, {
        "enter":   "enter",
        "avoid":   "avoid",
        "monitor": "monitor",
        "acquire": "acquire",
        "partner": "partner",
    })
    for node in ["enter", "avoid", "monitor", "acquire", "partner"]:
        g.add_edge(node, END)

    return g.compile()


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else (
        "NNormal trail running brand APAC market entry — "
        "outdoor apparel targeting Thailand and Southeast Asia"
    )

    print(f"\n{'='*56}")
    print("INTELICA MARKET ENTRY DECISION GRAPH")
    print(f"Query: {query[:56]}")
    print(f"{'='*56}")

    app = build_graph()
    final = app.invoke({
        "query":          query,
        "action":         "",
        "confidence":     0.0,
        "rationale":      "",
        "risk_level":     "",
        "imi":            0.0,
        "competitors":    [],
        "execution_plan": {},
        "executive_brief":{},
        "unique_angle":   "",
        "final_output":   "",
    })

    print(final["final_output"])
