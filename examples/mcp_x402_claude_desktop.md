# Connect Intelica to Claude Desktop with x402 Autonomous Payments

This guide shows how to configure Claude Desktop to use Intelica's competitive intelligence tools with automatic x402 micropayments — no manual payment steps, no API keys.

When Claude calls Intelica and receives HTTP 402, it pays $0.05 USDC on Base automatically and retries.

---

## Prerequisites

- [Claude Desktop](https://claude.ai/download) installed
- Node.js v18+
- A Coinbase CDP wallet funded with USDC on Base (`eip155:8453`)
  - Get one at [portal.cdp.coinbase.com](https://portal.cdp.coinbase.com)
  - Fund with at least $1.00 USDC on Base

---

## Step 1 — Create the MCP x402 client

```bash
mkdir intelica-mcp && cd intelica-mcp
npm init -y
npm install @x402/axios @x402/evm axios viem
```

Create `server.mjs`:

```javascript
import { wrapAxiosWithPayment, x402Client } from "@x402/axios";
import { ExactEvmScheme } from "@x402/evm/exact/client";
import axios from "axios";
import { privateKeyToAccount } from "viem/accounts";

// Your CDP wallet private key — store in environment variable
const account = privateKeyToAccount(process.env.EVM_PRIVATE_KEY);
const client = new x402Client();
client.register("eip155:*", new ExactEvmScheme(account));

// Wrap axios with x402 payment handling
const intelica = wrapAxiosWithPayment(
  axios.create({ baseURL: "https://api.intelica.dev" }),
  client
);

// MCP server over stdio
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  { name: "intelica", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "analyze_market",
      description: "Competitive intelligence analysis. Returns IMI score (0-1), go/no-go decision (enter/avoid/monitor/acquire/partner), detected competitors, and execution plan. Costs $0.05 USDC per call, paid automatically via x402.",
      inputSchema: {
        type: "object",
        properties: {
          text: {
            type: "string",
            description: "Company or market to analyze. Include: what it does, target market, geography. More context = better analysis."
          },
          mode: {
            type: "string",
            enum: ["competitive", "venture_screening", "market_entry_execution", "regulatory_compliance"],
            default: "competitive",
            description: "Analysis depth. competitive=$0.05, others=$1.00"
          }
        },
        required: ["text"]
      }
    },
    {
      name: "get_market_share",
      description: "Free market saturation report from Intelica's competitive graph of 3,600+ companies. No payment required.",
      inputSchema: {
        type: "object",
        properties: {
          sector: {
            type: "string",
            enum: ["ai", "fintech", "healthcare", "saas", "defense", "logistics", "legaltech", "edtech", "robotics", "energy", "ecommerce"],
            description: "Market sector to analyze"
          }
        },
        required: ["sector"]
      }
    }
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "analyze_market") {
    // x402 payment handled automatically — if 402, pays and retries
    const response = await intelica.post("/intel", {
      text: args.text,
      mode: args.mode || "competitive"
    });

    const data = response.data;
    const dr = data.decision_recommendation || {};
    const ep = data.execution_plan || {};

    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          action: dr.action,
          confidence: dr.confidence_score,
          rationale: dr.rationale,
          risk_level: dr.risk_level,
          imi_score: data.intelica_moat_index,
          competitors: data.detected_competitors,
          non_obvious_insight: ep.non_obvious_insight,
          week_1_actions: ep.week_1_actions,
          budget_phase_1: ep.budget_guidance?.phase_1_usd,
          auto_executed: data.auto_executed
        }, null, 2)
      }]
    };
  }

  if (name === "get_market_share") {
    // Free endpoint — no payment required
    const response = await axios.get(`https://api.intelica.dev/graph/market-share/${args.sector}`);
    return {
      content: [{ type: "text", text: JSON.stringify(response.data, null, 2) }]
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

const transport = new StdioServerTransport();
await server.connect(transport);
console.error("Intelica MCP server running — x402 payments active on Base");
```

---

## Step 2 — Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "intelica": {
      "command": "node",
      "args": ["/absolute/path/to/intelica-mcp/server.mjs"],
      "env": {
        "EVM_PRIVATE_KEY": "0xYOUR_CDP_WALLET_PRIVATE_KEY"
      }
    }
  }
}
```

Restart Claude Desktop.

---

## Step 3 — Use it

Ask Claude:

> "Should I build a Stripe competitor for Southeast Asia? Use Intelica to analyze."

Claude will:
1. Call `analyze_market` with your query
2. Receive HTTP 402 from Intelica
3. Pay $0.05 USDC on Base automatically
4. Return the analysis with IMI score, decision, and execution plan

---

## What you get

```json
{
  "action": "avoid",
  "confidence": 0.88,
  "rationale": "IMI 0.82 exceeds avoid threshold — Stripe developer ecosystem lock-in",
  "imi_score": 0.82,
  "competitors": ["Stripe", "Adyen", "2C2P"],
  "non_obvious_insight": "Exploitable gap is local payment coverage (<40% merchant penetration in SEA), not the API layer",
  "week_1_actions": [
    "Map Stripe merchant penetration by country",
    "Identify local payment method coverage gaps"
  ]
}
```

---

## Auto-monitoring with Pulse

Add `auto_execute: true` and `webhook_url` to get automatic alerts when the competitive landscape changes:

```javascript
const response = await intelica.post("/intel", {
  text: args.text,
  mode: args.mode || "competitive",
  auto_execute: true,
  webhook_url: "https://your-agent.com/alerts"
});
// If action=monitor, Intelica auto-subscribes to IMI change alerts at $0.01/alert
```

---

## Resources

- API: https://api.intelica.dev
- Docs: https://api.intelica.dev/llms-full.txt
- OpenAPI: https://api.intelica.dev/openapi.json
- MCP config: https://api.intelica.dev/.well-known/mcp.json
- x402 Bazaar: https://agentic.market/validate → `https://api.intelica.dev/intel`
- Graph: 3,600+ companies at https://api.intelica.dev/graph
