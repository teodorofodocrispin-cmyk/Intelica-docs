# Intelica

<p align="center">
  <img src="https://raw.githubusercontent.com/teodorofodocrispin-cmyk/Intelica-docs/main/ChatGPT%20Image%207%20jun%202026%2C%2003_21_28%20p.m..png" alt="Intelica Logo" width="300"/>
</p>


**Competitive intelligence API for autonomous AI agents — pay-per-call via x402.**

Analyze any URL or company description and get back structured JSON with market positioning, user pain points, detected competitors, unique angles, and an executable Market Score. Pay $0.05 USDC per call on Base or Solana mainnet. No accounts, no API keys, no subscriptions.

**Live:** `https://api.intelica.dev` · **Version:** v4.5.6

---

## What makes Intelica different

| Feature | Description |
|---|---|
| **5 Context Modes** | `competitive` · `fundraising` · `partnership` · `acquisition` · `market_entry` |
| **Market Score** | `threat_level` · `moat_strength` · `market_maturity` · `agent_recommendation` |
| **Decision** | `action` · `confidence_score` · `rationale` · `risk_level` |
| **8 Languages** | Auto-detects ES, PT, DE, FR, IT, JA, KO, ZH — applies regional market context |
| **Trend Tracking** | Detects changes between analyses — `status: changed`, `changes: [...]` |
| **Competitive Graph** | `GET /graph` — maps relationships between competitors across all analyses |
| **A2A Protocol** | `/message/send` — compatible with LangGraph, CrewAI, AutoGen, Google ADK |
| **Intelligence Budget** | Per-operator daily limits via `operator_id` field |
| **Dual network** | Base mainnet + Solana mainnet — agent pays on whichever network it prefers |

---

## Quick start

```bash
# 1. Without payment → returns 402 with payment instructions
curl -X POST https://api.intelica.dev/intel \
  -H "Content-Type: application/json" \
  -d '{"text": "Notion is an all-in-one workspace for teams"}'

# 2. Free demo (300 char limit)
curl -X POST https://api.intelica.dev/demo \
  -H "Content-Type: application/json" \
  -d '{"text": "Notion is an all-in-one workspace for teams"}'
```

---

## POST /intel

Single competitive intelligence analysis — **$0.05 USDC via x402**.

```json
POST /intel
X-PAYMENT: <x402 signed payment>

{
  "url": "https://notion.so",
  "context": "I'm building a note-taking app for developers",
  "mode": "competitive"
}
```

**Response:**
```json
{
  "source": "https://notion.so",
  "analysis": {
    "company_or_product": "Notion",
    "positioning_summary": "All-in-one workspace combining notes, docs, and databases...",
    "target_customer": "Teams and individuals seeking productivity tools",
    "core_value_props": ["Flexible databases", "Collaborative docs", "Template library"],
    "user_pain_points": ["Complex for new users", "Slow on large pages", "Limited offline support"],
    "detected_competitors": ["Obsidian", "Coda", "Confluence"],
    "unique_angle": "Developer-focused simplicity gap — Notion targets everyone, leaving power users underserved",
    "tone": "professional",
    "confidence": "high",
    "market_score": {
      "threat_level": "high",
      "moat_strength": 0.78,
      "market_maturity": "mature",
      "agent_recommendation": "counter"
    },
    "decision_recommendation": {
      "action": "avoid",
      "confidence_score": 0.91,
      "rationale": "IMI 0.78 exceeds avoid threshold; AlphaSense holds $100M+ in switching costs with enterprise contracts.",
      "risk_level": "high"
    }
  },
  "mode": "competitive",
  "detected_language": "en",
  "market_context": "global",
  "trend": {
    "status": "new",
    "changes": [],
    "snapshot_count": 1
  },
  "cached": false,
  "response_ms": 1240,
  "price_paid_usdc": "0.05"
}
```

---

## Context Modes

Pass `mode` to get context-specific analysis:

| Mode | Use when |
|---|---|
| `competitive` | Standard competitor analysis (default) |
| `fundraising` | Evaluating investor narrative, TAM, traction signals |
| `partnership` | Assessing strategic fit — complement or rival? |
| `acquisition` | Due diligence — moat, technical risk, acquisition thesis |
| `market_entry` | Market gaps, saturation, barriers to entry |

```json
{ "text": "...", "mode": "fundraising" }
```

---

## Market Score

Every analysis includes a `market_score` block with executable fields:

- **`threat_level`** — `high` | `medium` | `low`
- **`moat_strength`** — 0.0 to 1.0 (how hard is it to compete against them)
- **`market_maturity`** — `emerging` | `growing` | `mature` | `declining`
- **`agent_recommendation`** — `monitor` | `counter` | `ignore` | `partner`

---

## 8 Languages — Auto-detected

Intelica detects the language of the content and applies the appropriate regional market context automatically:

| Language | Market Context |
|---|---|
| ES | LATAM / Spain — pricing sensitivity, mobile-first, informal economy |
| PT | Brazil / Portugal — Pix ecosystem, LGPD compliance |
| DE | DACH — enterprise-first, privacy-conscious, structured procurement |
| FR | France / Francophone — European regulatory, state involvement in tech |
| IT | Italy — SME-heavy, design-driven, family business culture |
| JA | Japan — keiretsu structures, quality-obsessed, long sales cycles |
| KO | Korea — chaebol dynamics, Kakao/Naver ecosystem |
| ZH | China — BAT ecosystem, data localization, domestic/international split |

No configuration needed — just pass the content in any language.

---

## Trend Tracking

On repeated analyses of the same company, Intelica compares the current result with the previous snapshot and returns a `trend` object:

```json
"trend": {
  "status": "changed",
  "changes": [
    { "field": "threat_level", "from": "medium", "to": "high" },
    { "field": "agent_recommendation", "from": "monitor", "to": "counter" },
    { "field": "moat_strength", "from": 0.5, "to": 0.7, "delta": 0.2 },
    { "field": "detected_competitors", "added": ["Linear"] }
  ],
  "previous_snapshot": "2026-06-01T00:00:00Z"
}
```

---

## Competitive Graph

`GET /graph` — returns the accumulated competitive relationship map across all analyses.

```bash
# Full graph
curl https://api.intelica.dev/graph

# Subgraph centered on a company
curl "https://api.intelica.dev/graph?company=Notion"
```

Returns nodes (companies), edges (competitive relationships), and `hub_competitors` — companies that appear most frequently as competitors across all analyses.

---

## A2A Protocol

`POST /message/send` — compatible with LangGraph, CrewAI, AutoGen, Google ADK.

```json
POST /message/send

{
  "message": {
    "role": "user",
    "parts": [
      { "type": "text", "text": "mode: fundraising\nAnalyze Notion as a competitor" }
    ]
  }
}
```

Free tier — basic analysis without payment. Upgrade to `/intel` for full analysis with trend tracking and graph updates.

---

## POST /batch

Up to 10 analyses in one call — **$0.20 USDC via x402**.

```json
{
  "items": [
    { "url": "https://notion.so", "mode": "competitive" },
    { "text": "Coda is a collaborative doc platform", "mode": "acquisition" },
    { "url": "https://obsidian.md", "mode": "partnership" }
  ]
}
```

---

## Intelligence Budget

Limit daily analyses per operator pipeline. Pass `operator_id` in any request:

```json
{ "text": "...", "mode": "competitive", "operator_id": "my-pipeline-v1" }
```

Budget enforcement is configured server-side via `intel_budgets` table in Supabase.

---

## Endpoints

| Method | Path | Auth | Price |
|---|---|---|---|
| GET | `/` | None | Free |
| GET | `/health` | None | Free |
| GET | `/pricing` | None | Free |
| GET | `/llms.txt` | None | Free |
| GET | `/graph` | None | Free |
| GET | `/.well-known/x402.json` | None | Free |
| GET | `/agent-card.json` | None | Free |
| POST | `/demo` | None | Free (300 chars) |
| POST | `/message/send` | None | Free (A2A basic) |
| POST | `/mcp` | x402 | $0.05 USDC |
| POST | `/intel` | x402 | $0.05 USDC |
| POST | `/batch` | x402 | $0.20 USDC (up to 10) |

---


## Methodology

### How Intelica works

Every analysis runs through a structured pipeline:

```
Input (URL or text)
  ↓
Input sanitization (HTML strip, prompt injection protection)
  ↓
Language detection (8 languages: EN, ES, PT, DE, FR, IT, JA, KO, ZH)
  ↓
Web search enrichment via Exa (3 verified sources per analysis)
  ↓
Context mode selection (10 specialized modes)
  ↓
Claude Haiku — structured JSON generation
  ↓
Output validation (schema enforcement, range clamping)
  ↓
Trend tracking (snapshot comparison vs previous analysis)
  ↓
Competitive Graph update (nodes + edges in Supabase)
  ↓
Cache (6h TTL, Supabase primary + in-memory fallback)
```

### Data sources

- **Primary:** Content from the URL or text provided by the caller
- **Web enrichment:** Real-time search via [Exa](https://exa.ai) — 3 verified URLs returned as `sources[]` in every analysis
- **LLM inference:** Claude Haiku (Anthropic) generates the structured analysis from the enriched content

### Market Score methodology

The `market_score` object is generated by Claude Haiku and validated against strict ranges:

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `threat_level` | enum | high / medium / low | Competitive threat to the caller |
| `moat_strength` | float | 0.0 → 1.0 | Defensibility of the analyzed company |
| `market_maturity` | enum | emerging / growing / mature / declining | Market lifecycle stage |
| `agent_recommendation` | enum | monitor / counter / ignore / partner | Executable action for the agent |
| `decision_recommendation.action` | enum | enter / avoid / monitor / acquire / partner | Primary recommended action |
| `decision_recommendation.confidence_score` | float | 0.0–1.0 | Confidence in recommendation (≥0.80 = strong signal) |
| `decision_recommendation.rationale` | string | — | One sentence anchored to a specific data point |
| `decision_recommendation.risk_level` | enum | high / medium / low | Downside risk of acting on this recommendation |

All enum values are enforced server-side — the model cannot return values outside these sets. `moat_strength` is clamped to [0.0, 1.0] regardless of LLM output.

### Competitor detection

Competitors are detected by Claude Haiku from the input content + web enrichment context. With Exa integration, detected competitors are cross-referenced against real web sources. The `sources[]` field in the response shows which URLs informed the analysis.

### Confidence scoring

- `high` — sufficient content and web context to produce reliable analysis
- `medium` — partial content, some inference required
- `low` — insufficient content, treat output as directional only

### Cache and freshness

Results are cached for **6 hours** (Supabase primary, in-memory fallback). This is appropriate for most competitive intelligence use cases. For fast-moving markets (crypto, AI, early-stage startups), pass `force_refresh: true` in the request body to bypass cache and run a fresh analysis.

### Limitations

- Analysis quality depends on the richness of the input content
- Competitor detection is LLM-generated — treat as directional, not exhaustive
- Market Score reflects the model's interpretation of the content, not a proprietary scoring database
- Cache TTL of 6h may not capture intraday events in fast-moving markets

## Integration Examples

### LangChain

```python
from langchain.tools import tool
import httpx

@tool
def analyze_competitor(url: str, mode: str = "competitive") -> dict:
    """Analyze a competitor URL using Intelica. Returns structured competitive intelligence."""
    from x402.client import PaymentClient
    client = PaymentClient(wallet_private_key="your_evm_private_key")
    response = client.post(
        "https://api.intelica.dev/intel",
        json={"url": url, "mode": mode}
    )
    return response.json()

# Use in an agent
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")
agent = initialize_agent([analyze_competitor], llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
agent.run("Analyze Notion as a competitor for a note-taking app")
```

### LlamaIndex

```python
from llama_index.core.tools import FunctionTool
import httpx

def intelica_analyze(text: str, mode: str = "competitive") -> str:
    """Analyze a company or product description and return competitive intelligence."""
    from x402.client import PaymentClient
    client = PaymentClient(wallet_private_key="your_evm_private_key")
    response = client.post(
        "https://api.intelica.dev/intel",
        json={"text": text, "mode": mode}
    )
    return str(response.json()["analysis"])

intelica_tool = FunctionTool.from_defaults(fn=intelica_analyze)
```

### Free demo (no payment required)

```python
import httpx

response = httpx.post(
    "https://api.intelica.dev/demo",
    json={"text": "Notion is an all-in-one workspace for notes and databases"}
)
print(response.json()["analysis"]["market_score"])
# {"threat_level": "high", "moat_strength": 0.78, "agent_recommendation": "counter"}
# {"action": "avoid", "confidence_score": 0.91, "rationale": "IMI 0.78 exceeds avoid threshold.", "risk_level": "high"}
```

---

## Payment via x402

**Base mainnet (EVM):**
```python
import httpx
from x402.client import PaymentClient

client = PaymentClient(wallet_private_key="your_evm_private_key")
response = client.post(
    "https://api.intelica.dev/intel",
    json={"url": "https://competitor.com", "mode": "competitive"}
)
```

**Solana mainnet:**
The 402 response includes both Base and Solana payment options. Solana clients use `solana-mainnet` network entry from the `accepts` array.

---

## Deploy your own

1. Fork this repo
2. Connect to [Render](https://render.com) → New Web Service → select repo
3. Render detects `render.yaml` automatically
4. Add environment variables:
   - `ANTHROPIC_API_KEY`
   - `WALLET_ADDRESS` (EVM — Base mainnet)
   - `WALLET_SOLANA` (Solana mainnet)
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
5. Deploy — live in ~2 minutes

---


## Human Access — Buy reports with USDC

For founders, consultants, and investors who need competitive intelligence without an API setup.

| Plan | Reports | Days | Price |
|------|---------|------|-------|
| Starter | 30 | 10 | $15 USDC |
| Pro | 100 | 30 | $30 USDC |

**One page, complete experience:**

👉 **[intelica.dev/intelica.html](https://teodorofodocrispin-cmyk.github.io/Intelica-docs/intelica.html)**

The page guides you through everything in one scroll:
1. See the plans and clear rules — exactly what you're buying
2. Pay in USDC on Solana — session key activated instantly
3. Enter your session key — generate reports immediately
4. Download your report as HTML or JSON

**Additional links:**
- 🔍 [Sample report](https://teodorofodocrispin-cmyk.github.io/Intelica-docs/sample-report-japan.html) — Japan market entry example

Payment network: Solana mainnet · Asset: USDC · No accounts, no subscriptions

---

## Stack

- **Runtime:** FastAPI + Python 3.11
- **LLM:** Claude Haiku 4.5 (Anthropic)
- **Payments:** x402 protocol — USDC on Base + Solana mainnet
- **Facilitator:** PayAI Network
- **Persistence:** Supabase (PostgreSQL)
- **Deploy:** Render (AWS us-east)
- **Wallets:**
  - Base: `0x1d6bA7ac2461fd0E17D6A4C7bc1c9Ce365EfC4FF`
  - Solana: `45q8KyCAGSHHd6qYP2ZkEJh22SzeQeXRfyFsENcx3KN6`

---

## License

MIT

