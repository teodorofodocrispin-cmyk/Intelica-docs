# Intelica Startup Opportunity Validator

> **Stop guessing. Ask the graph.**

An open-source agent that evaluates any startup idea against Intelica's competitive graph of **3,600+ companies** and returns a structured go/no-go decision in seconds.

```bash
python validator.py "AI-powered legal document review for SMBs in Southeast Asia"
```

```
VERDICT:    🟢 ENTER
Confidence: 74% | Risk: MEDIUM
Rationale:  IMI 0.52 below enter threshold — LegalTech incumbents (Kira, Luminance)
            are enterprise-focused with no SMB offering in SEA.

WEEK 1 — START HERE
  • Contact top 5 SEA law firms on LinkedIn with a free pilot offer
  • Register for LegalTech Asia Summit 2026 — deadline June 30
  • Build a one-page case study on time saved vs. manual review

BUDGET
  Phase 1:  $25,000–$40,000
  12 months: $180,000–$280,000

PITCH DECK OUTLINE
  Slide 1 Problem: LegalTech incumbents ignore SMBs in SEA — $2B underserved market
  Slide 4 Moat:   Competitive advantage needed vs: Kira Systems, Luminance
  Slide 7 Ask:    Phase 1 budget: $25,000–$40,000
```

---

## Why this exists

Most startup validators give you market size estimates from Crunchbase and call it a day. This one gives you:

- **IMI Score** — structural moat strength of the competitive landscape (0.0–1.0)
- **Explicit action** — `enter`, `avoid`, `monitor`, `acquire`, or `partner`
- **Thresholds** — transparent decision logic you can audit and override
- **Execution plan** — Week 1 actions, channels, validation signals, and budget
- **Auto-monitoring** — if action is `monitor`, auto-subscribes to IMI change alerts

---

## Install

```bash
pip install requests
git clone https://github.com/teodorofodocrispin-cmyk/startup-opportunity-validator
cd startup-opportunity-validator
export INTELICA_SESSION=your-session-key  # Get one free at api.intelica.dev
```

---

## Usage

### CLI
```bash
# Basic evaluation
python validator.py "Your startup idea"

# With auto-monitoring (alerts when competitive landscape changes)
python validator.py "Your startup idea" --webhook https://your-agent.com/alerts
```

### Python
```python
from validator import validate_startup

result = validate_startup(
    idea="B2B SaaS for automated invoice reconciliation targeting mid-market CFOs in DACH",
    webhook_url="https://your-agent.com/alerts"  # optional
)

if result["action"] == "enter":
    print(result["pitch_outline"])
elif result["action"] == "avoid":
    print(result["pivot_suggestions"])
elif result["action"] == "monitor":
    print(f"Pulse active — alerts when IMI changes ±5%")
```

### LangGraph node
```python
from validator import validate_startup

def startup_validator_node(state):
    result = validate_startup(state["idea"], webhook_url=state.get("webhook_url"))
    return {
        **state,
        "action":       result["action"],
        "imi":          result["imi"],
        "week_1":       result["week_1"],
        "pitch":        result.get("pitch_outline"),
        "pivots":       result.get("pivot_suggestions"),
    }
```

### CrewAI tool
```python
from crewai.tools import tool
from validator import validate_startup

@tool("startup_opportunity_validator")
def validate(idea: str) -> str:
    """Evaluate a startup idea using Intelica competitive intelligence.
    Returns IMI score, go/no-go decision, and execution plan."""
    result = validate_startup(idea)
    return f"Action: {result['action'].upper()} | IMI: {result['imi']} | {result['rationale']}"
```

---

## Decision logic

| IMI Score | Action | Meaning |
|-----------|--------|---------|
| < 0.65 | `enter` | Barriers are low — move fast |
| 0.65–0.80 | `monitor` | Market in transition — wait for signal |
| > 0.80 | `avoid` | Moat too strong — pivot or partner |
| > 0.70 (acquirable) | `acquire` | Buy the moat instead of building |
| Complementary moat | `partner` | Alliance > competition |

`confidence_score` is independent of `action` — it reflects data richness, not whether the action is correct. Low confidence (< 0.50) means sparse data, not wrong direction.

---

## Auto-monitoring

When you pass `--webhook` and the action is `monitor`, the validator automatically subscribes to **Intelica Pulse** — IMI change alerts at $0.01 USDC per alert via x402. Your agent gets notified when the competitive landscape shifts.

```json
{
  "auto_executed": {
    "action_taken": "pulse_subscribed",
    "subscription_id": "ea3ac883-...",
    "imi_threshold": 0.05,
    "price_per_alert_usdc": 0.01,
    "message": "Pulse active — you will be notified when IMI changes by ±5%."
  }
}
```

---

## Output format

```json
{
  "action": "enter",
  "imi": 0.52,
  "confidence": 0.74,
  "rationale": "IMI 0.52 below enter threshold...",
  "risk_level": "medium",
  "thresholds_applied": { "imi_enter_max": 0.65, "imi_avoid_min": 0.80 },
  "fallback_behavior": { "if_confidence_below": 0.50, "default_action": "monitor" },
  "competitors": ["Kira Systems", "Luminance", "ContractPodAi"],
  "week_1": ["Contact top 5 SEA law firms...", "Register for LegalTech Asia..."],
  "channels": ["Direct outreach to GC offices of mid-market firms"],
  "budget_p1": "$25,000–$40,000",
  "budget_total": "$180,000–$280,000",
  "pitch_outline": { "slide_1_problem": "...", "slide_7_ask": "..." },
  "auto_executed": null
}
```

---

## Powered by

[Intelica](https://api.intelica.dev) — Competitive Intelligence API for autonomous AI agents.
- Pay-per-call via x402 ($0.05 USDC standard / $1.00 USDC elite)
- MCP server: `https://api.intelica.dev/mcp`
- Graph: 3,600+ companies with structural moat scoring (IMI)

---

## License

MIT — fork it, adapt it, use it. If Intelica stays as the intelligence layer, the graph gets better for everyone.
