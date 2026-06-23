# INTELICA — Master Context Document
> Last updated: June 23, 2026
> Read this file at the start of any new chat session to restore full project context.

---

## 1. WHO IS IV

Ivar Garcés (Iv), solo developer based in Bogotá, Colombia. GitHub: `teodorofodocrispin-cmyk`. Uses Claude as primary technical and strategic collaborator. Builds two bootstrapped products simultaneously: **Intelica** and **TrustBoost PII Sanitizer**. No team, no external funding. Communicates in Spanish and English.

---

## 2. INTELICA — PRODUCT OVERVIEW

**What it is:** Competitive intelligence API for AI agents and founders. Analyzes any company or market and returns structured JSON with moat scoring (IMI), competitor mapping, executive brief, and strategic recommendations — benchmarked against a real-time graph of 3,600+ companies.

**Live URL:** https://api.intelica.dev  
**Version:** v4.5.5  
**Stack:** FastAPI + Claude Haiku (standard) / Claude Sonnet (elite) + Supabase + Render  
**GitHub:** https://github.com/teodorofodocrispin-cmyk/Intelica  
**Docs:** https://teodorofodocrispin-cmyk.github.io/Intelica-docs/  

---

## 3. INFRASTRUCTURE

### Supabase
- **Project ID:** `yuytelqrwsnaqgvbvyef`
- **URL:** `https://yuytelqrwsnaqgvbvyef.supabase.co`
- **MCP connection:** Connect via Supabase MCP at start of each session
- **Key tables:**
  - `intel_cache` — 6h TTL cache for analysis results
  - `intel_audit` — permanent ledger of every API call (READ ONLY — never delete)
  - `intel_access` — session keys for human users (X-SESSION auth)
  - `intel_api_keys` — API keys with USDC balance (X-API-KEY auth)
  - `intel_pending_payments` — payment polling (never delete without WHERE)
  - `intel_graph_nodes` — **NEVER DELETE** — competitive graph nodes
  - `intel_graph_edges` — **NEVER DELETE** — competitive graph edges
  - `intel_budgets` / `intel_budget_usage` — per-operator budget limits
  - `intel_trend` — trend snapshots per analysis
  - `intel_session_history` — session query history
  - `intel_pulse_subscriptions` — Intelica Pulse webhook subscriptions
  - `intel_pulse_snapshots` — IMI snapshots for Pulse delta comparison
  - `demo_rate_limit` — rate limiting for /demo endpoint

### Render
- **Deploy:** Auto-deploy from GitHub main branch
- **Build command:** Uses Tsinghua PyPI mirror for `httpcore`
- **Env vars:** `ANTHROPIC_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `EXA_API_KEY`, `HELIUS_API_KEY`, `HELIUS_WEBHOOK_SECRET=intelica-helius-2026`

### GitHub
- **Token:** `GH_TOKEN_IN_ENV`
- **Main repo:** `teodorofodocrispin-cmyk/Intelica` (main.py — 4,200+ lines)
- **Docs repo:** `teodorofodocrispin-cmyk/Intelica-docs`

---

## 4. WALLETS AND PAYMENTS

| Network | Asset | Wallet |
|---|---|---|
| Base mainnet | USDC `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | `0x1d6bA7ac2461fd0E17D6A4C7bc1c9Ce365EfC4FF` |
| Solana mainnet | USDC `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | `45q8KyCAGSHHd6qYP2ZkEJh22SzeQeXRfyFsENcx3KN6` |

**Pricing:**
- Standard modes: $0.05 USDC/call (claude-haiku-4-5-20251001)
- Elite modes: $1.00 USDC/call (claude-sonnet-4-6)
- Batch: $0.20 USDC / up to 10 companies
- Human plans: Starter $15/30 reports/10 days, Pro $30/100 reports/30 days

**Elite modes:** `market_entry_execution`, `regulatory_compliance`, `venture_screening`, `risk_assessment`, `sales_enablement`

**Payment protocols:** x402 (Base + Solana), X-SESSION (human plans), X-API-KEY (pre-loaded balance)

---

## 5. FEATURES (v4.5.5 — as of June 23, 2026)

### Core endpoints
- `POST /intel` — main analysis endpoint
- `POST /batch` — up to 10 companies at once
- `POST /demo` — free limited preview (3/hour/IP)
- `POST /mcp` — MCP server (JSON-RPC 2.0)
- `POST /message/send` — A2A protocol (Google ADK / LangGraph compatible)
- `GET /graph` — competitive graph subgraph query
- `GET /graph/market-share/{sector}` — market saturation report
- `GET /access/status` — session status + history + suggested_next_analysis
- `POST /pulse/subscribe` — Intelica Pulse webhook subscription
- `GET /pulse/status` — subscription status
- `DELETE /pulse/unsubscribe/{id}` — deactivate subscription

### Feature history (chronological)
- v4.0: `/llms.txt`, 5 context modes, Market Score with `agent_recommendation`
- v4.1: A2A `/message/send`, auto language/market detection (8 languages)
- v4.2: Intelligence Budget per operator (`intel_budgets`)
- v4.3: Multilingual support (EN/ES/PT/DE/FR/IT/JA/KO/ZH) with regional context
- v4.4: Trend Tracking via `intel_trend` snapshots
- v4.5.0: Competitive Graph (`intel_graph_nodes`/`intel_graph_edges`)
- v4.5.3: Executive Brief + IMI branding
- v4.5.4: Session History + `suggested_next_analysis`
- v4.5.5: **Intelica Pulse** — autonomous IMI change alerts via webhook + x402

### Intelica Pulse (v4.5.5)
Agents subscribe to IMI change alerts for specific companies. Background job runs every 6h, compares current IMI vs snapshot, fires webhook if delta ≥ threshold. Price: $0.01 USDC/alert via x402.

### Discovery layer
- `/llms.txt`, `/llms-full.txt`, `/openapi.json`
- `/.well-known/ai-plugin.json`, `/.well-known/mcp.json`, `/.well-known/x402.json`
- `/.well-known/agent.json`, `/robots.txt`, `/sitemap.xml`
- `AGENTS.md`, `.cursor/rules`, `plugin.json`, `manifest.json`

---

## 6. COMPETITIVE GRAPH

**Current state (June 23, 2026):**
- Nodes: **3,603** companies
- Edges: **3,697** relationships
- IMI average: **0.638**
- IMI max: **0.920** (FANUC + Google DeepMind)
- Elite nodes (IMI ≥ 0.80): 72
- High threat nodes: 450

**GOLDEN RULES — NEVER VIOLATE:**
1. `intel_graph_nodes` and `intel_graph_edges`: **NEVER delete, truncate, or reset. Ever.**
2. `intel_audit`: READ ONLY. Never delete. First external payment: seq_id=42 (Japan, June 12, 2026).
3. Never delete any Supabase data without explicit confirmation from Iv.

---

## 7. ACTIVE OUTREACH

### Hot contacts (priority)
| Contact | Company | Status | Notes |
|---|---|---|---|
| Felix Chan | HK, APAC Commercial Director | 🔥 Active | Session key `FELIX-CHAN-HK-2026` (5 reports, Pro, expires Jul 22). Message with demo instructions sent June 23. Waiting for him to use the demo. |
| Stella Kim | REALIZER (Korea) | 🔥 Active | Partnership discussion. Gave live demo with Reis Robotics case. Follow-up pending. |
| Keamogetswe Moretsi | Tenax (GCC pharma) | 🏛️ Pending | Offered institutional intro to Jermaine (head of regulatory practice). Not yet contacted. |

### Sent (awaiting response)
- **Lisbeth Hadingham** (Co-Founder Inflexx.ai) — US fintech entry thesis validation
- **Alex Romanovich** (CEO GlobalEdgeMarkets) — Intelica as quantitative layer for GEM

### LinkedIn post cadence
Every Monday with real Competitive Graph data. First post published June 22, 2026.

### Outreach rules
- Only pursue ⭐⭐⭐⭐⭐ profiles
- Messages position Intelica as complementary to existing work
- No cold pitch — always open with validated insight from the graph

---

## 8. GITHUB DISTRIBUTION (Issues opened June 23, 2026)

| Repo | Stars | Issue | Type |
|---|---|---|---|
| brightdata/trendscan | High | #1 | CrewAI integration drop-in |
| ramamoorthy07/Multi-Agent-Market-Research | Builder | #1 | CrewAI + Gemini replacement |
| SalmaSalahEldin/LangGraph-Market-Research | Builder | #1 | LangGraph + Tavily node |
| ARUNAGIRINATHAN-K/awesome-ai-agents-2026 | 300+ | #118 | Directory listing (responded — waiting review) |
| RaviKunapareddy/Sales-Multi-Agent-AI | Builder | #3 | sales_enablement node |
| TensorBlock/awesome-mcp-servers | ⭐750 | #857 | MCP directory |
| ashishpatel26/500-AI-Agents-Projects | ⭐32,942 | #134 | Mega directory |
| NirDiamant/GenAI_Agents | ⭐22,805 | #124 | GenAI tutorials |
| Salesably/awesome-ai-agents-for-sales | Niche | #8 | Sales directory |
| e2b-dev/awesome-ai-agents | ⭐28,443 | #1143 | Mega directory |

**Also merged/approved:**
- punkpeye/awesome-mcp-servers — merged
- xpaysh/awesome-x402 PR #481 — merged
- Glama.ai — approved (glama.ai/mcp/servers/teodorofodocrispin-cmyk/trustboost-api)
- x402scout.com, x402-list.com, skills.sh — approved

---

## 9. ACTIVE SESSIONS

| Session Key | Plan | Reports | Expires | User |
|---|---|---|---|---|
| `FELIX-CHAN-HK-2026` | Pro | 5/5 | Jul 22, 2026 | Felix Chan (HK) |
| `NAOYA-INTELICA-EARLY-TESTER` | Pro | 100 | Jul 11, 2026 | Naoya (Japan/KOHOMADHA) |
| `TEOCRISPIN-INTELICA-GRAPH` | Pro | ~165 remaining | Active | Iv (internal testing) |

---

## 10. INTEGRATION SNIPPETS

### CrewAI
```python
@tool("competitive_intelligence")
def analyze_competitor(company_description: str) -> str:
    response = requests.post(
        "https://api.intelica.dev/intel",
        headers={"Content-Type": "application/json", "X-SESSION": "your-key"},
        json={"text": company_description, "mode": "competitive"}
    )
    return response.json()
```

### LangChain
```python
@tool
def intelica_analyze(query: str) -> dict:
    """Analyze company competitive position. Returns IMI score and recommendations."""
    r = httpx.post("https://api.intelica.dev/intel",
        headers={"X-SESSION": "your-key"},
        json={"text": query, "mode": "competitive"})
    return r.json()
```

### Intelica Pulse (subscribe)
```bash
curl -X POST https://api.intelica.dev/pulse/subscribe \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your-key", "watch_company": "Stripe", "imi_threshold": 0.05, "webhook_url": "https://your-agent.com/alerts"}'
```

---

## 11. PENDING ITEMS

| Item | Priority | Notes |
|---|---|---|
| Felix Chan response | 🔥 | Waiting for him to use demo at intelica.html |
| Jermaine / Tenax contact | 🔥 | Intro from Keamogetswe — most valuable institutional contact |
| Stella Kim follow-up | 🔥 | Send real pipeline case |
| Intelica Pulse → after first payment | ⏳ | Already implemented — activate for Felix/Naoya once payment received |
| openapi.json /graph description in Spanish | 🔧 | Known issue |
| Glama ticket #108008695 | 🔧 | Update URL to api.intelica.dev/mcp |
| pay.sh PR #105 (solana-foundation/pay-skills) | 🔧 | Waiting on Rish |

---

## 12. HOW TO START A NEW SESSION

Paste this at the start of any new chat:

> "Fetch https://raw.githubusercontent.com/teodorofodocrispin-cmyk/Intelica-docs/main/CONTEXT.md and load full project context. Then connect to Supabase project yuytelqrwsnaqgvbvyef and confirm connection with: SELECT count(*) FROM intel_graph_nodes"

---

## 13. TRUSTBOOST (secondary product)

**URL:** https://api.trustboost.dev  
**Version:** v2.6.0  
**Stack:** FastAPI + GPT-4o-mini + Supabase (`furzsqnvoydwwdartkgt`) + Render  
**Supabase tables:** audit_log, trial_requests, paid_requests, used_tx, agent_budgets, budget_usage, wallet_scores  
**Solana wallet:** `giu4VciTkfWJNG1oeP6SzHEJwmabikJSMB91GaFNWE4`  
**First real user:** 2026-05-12, Supabase id:20 — preserved  
**Golden rule:** Never alter the core sanitization model — all changes strictly additive.  
**GitHub token:** stored in Render env vars

---

*This document is auto-maintained. Update it at the end of each major session.*
