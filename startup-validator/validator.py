"""
Intelica Startup Opportunity Validator
=======================================
Open-source agent that evaluates any startup idea against Intelica's
competitive graph of 3,600+ companies and returns a structured
go/no-go decision with execution plan.

Install:
    pip install requests

Usage:
    python validator.py "Your startup idea here"
    python validator.py "AI-powered legal document review for SMBs"

Get a free session key at: https://api.intelica.dev
"""

import requests
import sys
import json
import os

INTELICA_SESSION = os.getenv("INTELICA_SESSION", "your-session-key")
INTELICA_API     = "https://api.intelica.dev/intel"


def validate_startup(idea: str, webhook_url: str = None) -> dict:
    """
    Evaluate a startup idea using Intelica competitive intelligence.
    Returns a structured decision with execution plan.

    Args:
        idea: Startup idea in plain text (50+ words recommended)
        webhook_url: Optional — if provided and action=monitor,
                     auto-subscribes to IMI change alerts ($0.01/alert)

    Returns:
        dict with keys: action, confidence, rationale, risk_level,
                        imi, competitors, execution_plan, pitch_outline (if enter)
    """
    payload = {
        "text": idea,
        "mode": "venture_screening",
    }

    if webhook_url:
        payload["auto_execute"] = True
        payload["webhook_url"]  = webhook_url

    response = requests.post(
        INTELICA_API,
        headers={"X-SESSION": INTELICA_SESSION, "Content-Type": "application/json"},
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        raise Exception(f"Intelica API error {response.status_code}: {response.text}")

    result      = response.json()
    dr          = result.get("decision_recommendation", {})
    ep          = result.get("execution_plan", {})
    ms          = result.get("market_score", {})
    brief       = result.get("executive_brief", {})
    action      = dr.get("action", "monitor")
    competitors = result.get("detected_competitors", [])
    imi         = result.get("intelica_moat_index", 0)

    output = {
        "idea":          idea[:120],
        "imi":           imi,
        "action":        action,
        "confidence":    dr.get("confidence_score", 0),
        "rationale":     dr.get("rationale", ""),
        "risk_level":    dr.get("risk_level", "medium"),
        "thresholds":    dr.get("thresholds_applied", {}),
        "fallback":      dr.get("fallback_behavior", {}),
        "market":        ms.get("market_maturity", "unknown"),
        "threat":        ms.get("threat_level", "unknown"),
        "competitors":   competitors,
        "leader":        brief.get("leader", ""),
        "recent_move":   brief.get("recent_move", ""),
        "critical_risk": brief.get("critical_risk", ""),
        "week_1":        ep.get("week_1_actions", []),
        "channels":      ep.get("priority_channels", []),
        "barriers":      ep.get("barriers", []),
        "signals":       ep.get("validation_signals", []),
        "insight":       ep.get("non_obvious_insight", ""),
        "budget_p1":     ep.get("budget_guidance", {}).get("phase_1_usd", "N/A"),
        "budget_total":  ep.get("budget_guidance", {}).get("total_12m_usd", "N/A"),
        "auto_executed": result.get("auto_executed"),
    }

    # Generate pitch outline if action=enter
    if action == "enter":
        output["pitch_outline"] = _build_pitch_outline(output)

    # Generate pivot suggestions if action=avoid
    if action == "avoid":
        output["pivot_suggestions"] = _build_pivots(output)

    return output


def _build_pitch_outline(data: dict) -> dict:
    """Generate a pitch deck outline based on Intelica's execution plan."""
    return {
        "slide_1_problem":   f"Market gap: {data['insight'] or 'Underserved segment identified'}",
        "slide_2_solution":  f"Your startup addresses a market with IMI {data['imi']:.2f} — barriers exist but are surmountable.",
        "slide_3_market":    f"Market maturity: {data['market']}. Threat level: {data['threat']}.",
        "slide_4_moat":      f"Competitive advantage needed vs: {', '.join(data['competitors'][:2]) or 'fragmented market'}",
        "slide_5_gtm":       f"Week 1 priority: {data['week_1'][0] if data['week_1'] else 'Define go-to-market channels'}",
        "slide_6_traction":  f"Validation signal: {data['signals'][0] if data['signals'] else 'Define measurable traction metric'}",
        "slide_7_ask":       f"Phase 1 budget: {data['budget_p1']}",
    }


def _build_pivots(data: dict) -> list:
    """Suggest pivot directions when the market has too strong a moat."""
    return [
        f"Vertical niche: target a sub-segment that {data['competitors'][0] if data['competitors'] else 'incumbents'} ignores",
        f"Geographic arbitrage: enter markets where {data['leader'] or 'the leader'} has no local presence",
        f"Distribution pivot: reach the same customer through {data['channels'][0] if data['channels'] else 'an alternative channel'} that bypasses incumbent moat",
    ]


def _print_verdict(data: dict):
    """Pretty-print the validator output."""
    ACTION_ICONS = {
        "enter":   "🟢 ENTER",
        "avoid":   "🔴 AVOID",
        "monitor": "🟡 MONITOR",
        "acquire": "🔵 ACQUIRE",
        "partner": "🟣 PARTNER",
    }

    print(f"\n{'='*60}")
    print(f"INTELICA STARTUP OPPORTUNITY VALIDATOR")
    print(f"{'='*60}")
    print(f"Idea:       {data['idea']}")
    print(f"IMI Score:  {data['imi']:.2f}  (avoid threshold: {data['thresholds'].get('imi_avoid_min', 0.80)}, enter threshold: {data['thresholds'].get('imi_enter_max', 0.65)})")
    print(f"Market:     {data['market'].title()} | Threat: {data['threat'].upper()}")
    print(f"\n{'─'*60}")
    print(f"VERDICT:    {ACTION_ICONS.get(data['action'], data['action'].upper())}")
    print(f"Confidence: {data['confidence']:.0%} | Risk: {data['risk_level'].upper()}")
    print(f"Rationale:  {data['rationale']}")
    print(f"{'─'*60}")

    if data['competitors']:
        print(f"\nCOMPETITORS")
        for c in data['competitors'][:3]:
            print(f"  • {c}")

    if data['insight']:
        print(f"\nNON-OBVIOUS INSIGHT")
        print(f"  {data['insight']}")

    if data['action'] == "enter" and data.get('week_1'):
        print(f"\nWEEK 1 — START HERE")
        for a in data['week_1'][:3]:
            print(f"  • {a}")
        print(f"\nBUDGET")
        print(f"  Phase 1:  {data['budget_p1']}")
        print(f"  12 months: {data['budget_total']}")
        print(f"\nPITCH DECK OUTLINE")
        for k, v in data.get('pitch_outline', {}).items():
            slide = k.replace('slide_', 'Slide ').replace('_', ' ').title()
            print(f"  {slide}: {v}")

    if data['action'] == "avoid" and data.get('pivot_suggestions'):
        print(f"\nPIVOT SUGGESTIONS")
        for p in data['pivot_suggestions']:
            print(f"  • {p}")

    if data['action'] == "monitor":
        fb = data.get('fallback', {})
        print(f"\nMONITOR PROTOCOL")
        print(f"  Re-run analysis when: IMI drops below {data['thresholds'].get('imi_enter_max', 0.65)} or a major competitor exits")
        if fb.get('escalation_required'):
            print(f"  ⚠️  Escalation recommended — confidence below 40%, data is sparse")

    if data.get('auto_executed'):
        ae = data['auto_executed']
        print(f"\nAUTO-EXECUTED")
        print(f"  ✅ {ae.get('message', 'Pulse subscription active')}")

    print(f"\n{'='*60}")
    print(f"Powered by Intelica — api.intelica.dev")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validator.py \"Your startup idea\"")
        print("       python validator.py \"idea\" --webhook https://your-agent.com/alerts")
        sys.exit(1)

    idea = sys.argv[1]
    webhook = None

    if "--webhook" in sys.argv:
        idx = sys.argv.index("--webhook")
        if idx + 1 < len(sys.argv):
            webhook = sys.argv[idx + 1]

    if not INTELICA_SESSION or INTELICA_SESSION == "your-session-key":
        print("⚠️  Set your session key: export INTELICA_SESSION=your-key")
        print("   Get one free at: https://api.intelica.dev")
        sys.exit(1)

    print(f"Analyzing: {idea[:80]}...")
    data = validate_startup(idea, webhook_url=webhook)
    _print_verdict(data)

    # Save JSON output
    with open("validator_output.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Full JSON saved to: validator_output.json")
