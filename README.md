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

9 assets (BTC, ETH, SOL, BNB, XRP, DOGE, HYPE, ZEC, ENA) across **Binance, Bybit, OKX,
Hyperliquid**:

| Tool | What it answers |
|---|---|
| `get_market_state` | One normalized snapshot: funding + its trailing 2-year percentile, OI, volume, CVD, order-book imbalance, liquidations, basis, drivers. *"Is ETH positioning stretched?"* |
| `get_funding_percentile` | Current funding ranked against its own trailing 2-year window (0–100) + same-sign streak. |
| `get_liquidations_recent` | Cross-exchange liquidation notional estimates for a window: USD, long/short split. |
| `get_ohlcv` | Consolidated cross-exchange candles (5m…1d) with per-candle delta (taker buy − taker sell), for ATR, ranges, CVD and RV math. |
| `get_conditional_outcomes` | Measured forward-return history after a stated condition — base rates instead of folklore. *"What happened historically after funding above the 90th percentile?"* |
| `get_state_history` | Time series of any numeric state field from the 15-minute archive — the trend view behind the snapshot. |
| `get_volume_profile` | Volume-profile levels per UTC day from the consolidated tape: POC, value area high/low, value-area width and its rank, a multi-day composite and naked POCs. *"Is price inside yesterday's value area?"* |
| `get_big_trades` | Large aggressive orders (fills sharing venue, side and timestamp summed into one trade): per-side totals plus the biggest prints with venue, price and USD size. *"Were the whale market orders buying or selling?"* |
| `get_footprint_events` | Order-book wall events from the 1-minute footprint: absorbed and pulled walls with peak, executed and closing size in USD, plus thin-book minutes. *"Were bid walls pulled before this drop?"* |
| `get_stacked_imbalances` | Stacked footprint imbalances from the consolidated tape: diagonal buy and sell runs per candle (1m…1h) with price band and USD size. *"Where did aggressive buyers stack up on BTC this morning?"* |

**Data:** funding rates, open interest, cumulative volume delta (CVD), order-book depth, liquidations, OHLCV candles with per-candle delta, volume-profile levels, large aggressive orders, order-book wall events, stacked footprint imbalances.

**Honesty model:** every metric carries a `coverage` entry (venues, window
depth, freshness); thin history answers with disclosed depth instead of
made-up numbers; conditional outcomes go `history_silent` below the evidence
floor; every response self-declares its age. Reports history, not predictions.

## Connect

**Claude (web/desktop):** Settings → Connectors → *Add custom connector* →
`https://api.markettrace.ai/mcp` → authorize (email magic link).

Every client signs in the same way: it opens a browser, you enter your
email, and a sign-in link arrives. Open it on the same device and in the
same browser where you started.

**Claude Code** (adding the server does not sign you in, so run both):

```bash
claude mcp add --transport http markettrace https://api.markettrace.ai/mcp
claude mcp login markettrace
```

**Codex:**

```bash
codex mcp add markettrace --url https://api.markettrace.ai/mcp
codex mcp login markettrace
```

**Cursor:** add this to `~/.cursor/mcp.json` (or use *Add to Cursor* on
https://markettrace.ai/agents) and sign in when Cursor asks:

```json
{
  "mcpServers": {
    "markettrace": { "url": "https://api.markettrace.ai/mcp" }
  }
}
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

**Refresh the contract:** `tools.json` is a `{version, generated_at, tools}` snapshot of the live server's `tools/list` — regenerate it by capturing that response and stamping the current contract version (mirrors `feed.version` in `get_market_state`).

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
- *"Where are the key volume levels on BTC — any untested POCs nearby?"*
- *"Did a large resting order get absorbed on SOL in the last hour?"*

## Terms

Informational market data only — **not financial advice**.
[Privacy Policy](https://markettrace.ai/privacy) ·
[Terms of Service](https://markettrace.ai/terms) ·
Contact: support@markettrace.ai

The bridge in this repo is MIT-licensed ([LICENSE](LICENSE)); the hosted
service is governed by the Terms above.
