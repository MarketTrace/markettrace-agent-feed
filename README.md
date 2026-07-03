# MarketTrace agent-feed

**Read-only crypto perps microstructure for AI agents** — normalized
cross-exchange market state with self-declared coverage and freshness on
every metric. Facts and normalization, no verdicts: the agent interprets.

- **Hosted MCP**: `https://api.markettrace.ai/mcp` (Streamable HTTP, OAuth — no API keys)
- **Official registry**: [`ai.markettrace/agent-feed`](https://registry.modelcontextprotocol.io/v0/servers?search=ai.markettrace)
- **Docs**: https://markettrace.ai/agents

This repo is the **front door** — connection configs, the interface contract,
and a thin stdio bridge. The data pipeline itself (4-venue ingest, archives,
normalization) is not open source.

---

## What it serves

6 assets (BTC, ETH, SOL, BNB, XRP, DOGE) across **Binance, Bybit, OKX,
Hyperliquid**:

| Tool | What it answers |
|---|---|
| `get_market_state` | One normalized snapshot: funding + multi-year percentile, OI, volume, CVD, order-book imbalance, liquidations, basis, drivers. *"Is ETH positioning stretched?"* |
| `get_funding_percentile` | Current funding ranked against its own multi-year history (0–100) + same-sign streak. |
| `get_liquidations_recent` | Cross-exchange liquidation totals for a window: USD, long/short split. |
| `get_ohlcv` | Consolidated cross-exchange candles (5m…1d) for ATR/range/RV math. |
| `get_conditional_outcomes` | Measured forward-return history after a stated condition — base rates instead of folklore. *"What happened historically after funding above the 90th percentile?"* |
| `get_state_history` | Time series of any numeric state field from the 15-minute archive — the trend view behind the snapshot. |

**Honesty model:** every metric carries a `coverage` entry (venues, window
depth, freshness); thin history answers with disclosed depth instead of
made-up numbers; conditional outcomes go `history_silent` below the evidence
floor; every response self-declares its age. Reports history, not predictions.

## Connect

**Claude (web/desktop):** Settings → Connectors → *Add custom connector* →
`https://api.markettrace.ai/mcp` → authorize (email magic link).

**Claude Code:**

```bash
claude mcp add --transport http markettrace https://api.markettrace.ai/mcp
```

**Stdio-only clients** (via the standard OAuth-capable bridge):

```bash
npx -y mcp-remote https://api.markettrace.ai/mcp
```

More client configs in [`examples/mcp-configs.md`](examples/mcp-configs.md).

## Local stdio bridge (this repo)

[`mcp_server.py`](mcp_server.py) is a zero-dependency stdio bridge: it starts
and answers introspection (`initialize`, `tools/list`) with no credentials —
the bundled [`tools.json`](tools.json) is a snapshot of the hosted server's
own contract. Tool **calls** are proxied to the hosted endpoint when
`MARKETTRACE_BEARER` is set; without it they return a pointer to the hosted
OAuth endpoint instead of data. It holds no methodology — just a client.

```bash
python3 mcp_server.py            # Python 3.9+, no dependencies
```

Or with Docker:

```bash
docker build -t markettrace-bridge . && docker run -i markettrace-bridge
```

## Things to ask

- *"What's the market state for BTC — is positioning stretched?"*
- *"What happened historically after funding above the 90th percentile?"*
- *"How did open interest build over the last 3 days?"*
- *"How much got liquidated on ETH in the last hour — longs or shorts?"*

## Terms

Informational market data only — **not financial advice**.
[Privacy Policy](https://markettrace.ai/privacy) ·
[Terms of Service](https://markettrace.ai/terms) ·
Contact: support@markettrace.ai

The bridge in this repo is MIT-licensed ([LICENSE](LICENSE)); the hosted
service is governed by the Terms above.
