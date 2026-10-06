# Skill: reading the MarketTrace agent-feed

A workflow for an AI agent using the MarketTrace agent-feed MCP tools. The
feed reports **facts and measured history, not predictions** — every
interpretation is yours.

## Workflow

1. **`get_market_state(symbol)` first.** One call returns the whole
   cross-exchange picture: funding + trailing 2-year percentile, open interest,
   volume, CVD, order-book imbalance, liquidations, basis, plus fact
   `drivers`. Use it for orientation before anything else.
2. **Weigh each metric by its `coverage`.** Every field carries a coverage
   entry (venues, window depth, freshness, `partial` reason). A number with
   `partial: true` / `reason: accruing` is thin — trust it less. Check
   `feed.tools` against the tools you can call; if the feed lists more, your
   connector's catalog is stale (reconnect).
3. **Base rate via `get_conditional_outcomes(...)`.** Before treating a
   condition as meaningful ("funding is at the 92nd percentile"), ask what
   *actually happened* after it historically. This replaces folklore with
   measured forward-return distributions from the feed's own data.
4. **Trend via `get_state_history(fields, ...)`.** The snapshot is a moment;
   history is the shape. Is OI building or unwinding? Is funding rising all
   week? Pull the time series of the exact fields you care about.
5. **Exact price math via `get_ohlcv` / liquidation flow via
   `get_liquidations_recent`** when you need candles (ATR, ranges, realized
   vol) or the recent long/short liquidation split. Candles carry `delta`
   (taker buy − taker sell, base units); their running sum is the window's CVD.
6. **Levels and flow inside the move.** `get_volume_profile` gives the
   reference levels (POC, value area, naked POCs) per UTC day;
   `get_big_trades` lists the large aggressive orders and per-side totals for
   a window (at most 12 h per call); `get_footprint_events` lists absorbed or
   pulled order-book walls and thin-book minutes (at most 24 h per call; the
   event archive starts 2026-10-03, earlier windows are honestly empty);
   `get_stacked_imbalances` lists stacked diagonal buy/sell imbalance runs per
   candle (1m…1h, ratio 2/3/4; the same rule as the MarketTrace footprint chart).

## Scales (read them literally)

- `*_pct` / percentile fields → **0–100**.
- `*_ratio` fields (e.g. `taker_buy_ratio`, `liq.long_ratio`,
  `hit_rate_up`) → **0–1**.
- `rel.*` (e.g. `volume.rel.1w`) → **multiplier of the trailing median**
  (1.4 = 140% of median).
- `obi.skew` → **−1..+1**; positive = **bid-heavy** (more resting bids).
- `cvd.delta_usd` → positive = **net taker buying** over the window.
- `basis_bps` → positive = **perp trading above spot** index.
- `delta` (candles) → positive = **net taker buying**, BASE units like `v`.
- `aggressor` (big trades) → `buy` = the taker bought, `sell` = the taker sold.
- `wall_side` (footprint events) → `bid` = resting buy orders, `ask` = resting
  sell orders; `*_usd` sizes are whole dollars.

## Semantics that are easy to misread

- **`history_silent` is an answer, not an error.** In
  `get_conditional_outcomes`, a horizon goes `history_silent` when too few
  independent matches exist to measure (`n_effective < 12`). It means: *the
  history is silent — you would be trading on belief, so size accordingly.*
  Its stats are `null` on purpose; never substitute a guess.
- **`n_effective` vs `n_matches`.** Overlapping forward windows are not
  independent samples. `n_matches` is raw; `n_effective` is after
  overlap-collapse and is what the statistics use. Judge confidence by
  `n_effective`.
- **Depth bands beyond `visibility.visible_to_bps` are lower bounds**, not
  measurements. Don't compare a bid band vs an ask band once either side has
  outgrown its visible depth.
- **Truncated lists keep complete counts.** `get_big_trades` keeps the
  LARGEST trades and `get_footprint_events` the NEWEST events when a window
  holds more than `limit`; `totals` / `counts` always cover the whole window,
  and `truncated: true` says the list was cut.
- **Percentile conditions need a sample floor.** An as-of percentile exists
  only once its series has `coverage.warmup_samples` points (a rank among a
  couple of points is degenerate). Raw-value conditions have no such floor.

## Tone

Report and reason over what the feed measured. It gives you history and
coverage-honest facts; the trade decision, and its risk, are the agent's.
Past conditional distributions do not imply future returns.
