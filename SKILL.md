---
name: intelica
version: 4.6.0
description: >
  Competitive intelligence API for autonomous AI agents. Analyzes any URL or
  company description and returns structured JSON with market positioning, pain points,
  competitors, battlecard, verified sources, market signals, and executable Market Score.
  Pay-per-call via x402 on Base and Solana mainnet. No API keys required.
trigger: >
  Use when an agent needs to analyze a competitor, evaluate market positioning,
  assess market entry, screen investments, prepare sales battlecards, evaluate
  regulatory compliance, or analyze DeFi protocols before a strategic decision.
requires: []
env: []
---

# Intelica — Competitive Intelligence Skill

Intelica provides competitive intelligence for AI agents and human founders. Call it before any strategic decision requiring market context.

## When to use

- Agent needs competitor analysis before a strategic decision
- Founder needs a market entry report for a new geography
- Agent is evaluating a DeFi protocol before entering a position
- Sales agent needs a battlecard before a live demo
- VC agent screening investment opportunities
- Compliance officer evaluating regulatory risk (EU AI Act, GDPR)
- Agent monitoring competitors over time (Trend Tracking)
- Non-English market analysis (auto-detects 8 languages)

## How to call

### Step 1 — Free demo (no payment)
```
POST https://api.intelica.dev/demo
Content-Type: application/json

{
  "text": "Notion is an all-in-one workspace for teams",
  "mode": "competitive"
}
```

### Step 2 — Full analysis with x402 payment
```
POST https://api.intelica.dev/intel
Content-Type: application/json

{
  "url": "https://notion.so",
  "mode": "competitive",
  "context": "I'm building a note-taking app for developers"
}
# Returns HTTP 402 with Base + Solana payment options
# After payment, retry with X-PAYMENT header
```

### Step 3 — HTML Report for humans ($0.50)
```
POST https://api.intelica.dev/intel
X-PAYMENT: <x402 signed payment>
Content-Type: application/json

{
  "text": "Notion workspace",
  "mode": "sales_enablement",
  "format": "report"
}
# Returns HTML report with verdict badge, gauges, battlecard
```

### Step 4 — Batch (up to 10 analyses for $0.20)
```
POST https://api.intelica.dev/batch
X-PAYMENT: <x402 signed payment>
Content-Type: application/json

{
  "items": [
    { "url": "https://notion.so", "mode": "competitive" },
    { "text": "Coda collaborative doc platform", "mode": "acquisition" },
    { "url": "https://uniswap.org", "mode": "crypto_protocol" }
  ]
}
```

## Context Modes

| Mode | Price | Use when |
|------|-------|----------|
| `competitive` | $0.05 | Standard competitor analysis (default) |
| `fundraising` | $0.05 | Investor narrative, TAM, traction signals |
| `partnership` | $0.05 | Strategic fit — complement or rival? |
| `acquisition` | $0.05 | Due diligence — moat, technical risk |
| `market_entry` | $0.05 | Market gaps, saturation, barriers to entry |
| `crypto_protocol` | $0.05 | DeFi moat, tokenomics, regulatory risk |
| `venture_screening` | $1.00 | Investment thesis + deal-breakers |
| `regulatory_compliance` | $1.00 | EU AI Act, GDPR, HIPAA exposure |
| `risk_assessment` | $1.00 | Business model stability, operational risk |
| `sales_enablement` | $1.00 | Battlecard + objection handler |

## Output fields

```json
{
  "analysis": {
    "company_or_product": "string",
    "positioning_summary": "string",
    "target_customer": "string",
    "core_value_props": ["string"],
    "user_pain_points": ["string"],
    "detected_competitors": ["string"],
    "unique_angle": "string",
    "tone": "professional | casual | technical | aggressive",
    "confidence": "high | medium | low",
    "sources": ["url1", "url2", "url3"],
    "market_signals": {
      "funding_signal": "raised $275m series c",
      "headcount_signal": "5000 employees",
      "pricing_signal": "starting from $8/month",
      "recent_coverage": "3 recent article(s) from 2025-2026"
    },
    "battlecard": {
      "headline": "string",
      "their_weakness": "string",
      "your_angle": "string",
      "proof_point": "string",
      "objection_handler": "string"
    },
    "market_score": {
      "threat_level": "high | medium | low",
      "moat_strength": 0.0,
      "market_maturity": "emerging | growing | mature | declining",
      "agent_recommendation": "monitor | counter | ignore | partner"
    }
  },
  "mode": "string",
  "detected_language": "en | es | pt | de | fr | it | ja | ko | zh",
  "market_context": "string",
  "trend": {
    "status": "new | stable | changed",
    "changes": []
  }
}
```

## Advanced options

- `force_refresh: true` — bypass 6h cache for fast-moving markets (crypto, AI, startups)
- `format: "report"` — returns HTML report for humans ($0.50 USDC)
- `operator_id` — enforce daily budget limits per pipeline

## A2A Protocol

Compatible with LangGraph, CrewAI, AutoGen, Google ADK:

```
POST https://api.intelica.dev/message/send
{
  "message": {
    "role": "user",
    "parts": [
      { "type": "text", "text": "mode: sales_enablement\nAnalyze Notion as a competitor" }
    ]
  }
}
```

## Languages supported

Auto-detects: EN, ES (LATAM/Spain), PT (Brazil/Portugal), DE (DACH), FR (France), IT (Italy), JA (Japan — keiretsu context), KO (Korea — chaebol context), ZH (China — BAT context).

## Payment details

- Networks: Base mainnet + Solana mainnet
- Standard: $0.05 USDC / Elite: $1.00 USDC / Report: $0.50 USDC
- Facilitators: PayAI (primary) + Coinbase CDP (fallback)
- x402 manifest: https://api.intelica.dev/.well-known/x402.json

## Spend-aware usage

- Use `/demo` to validate input format before paying
- Use `/batch` for multiple analyses — $0.20 for up to 10
- Results cached 6 hours — same company twice costs once
- Pass `force_refresh: true` for real-time crypto/AI analysis
- Pass `context` to get analysis relative to your product

## Links

- Live API: https://api.intelica.dev
- OpenAPI: https://api.intelica.dev/openapi.json
- AGENTS.md: https://github.com/teodorofodocrispin-cmyk/Intelica-docs/blob/main/AGENTS.md
- Glama MCP: https://glama.ai/mcp/servers/teodorofodocrispin-cmyk/intelica-mcp
