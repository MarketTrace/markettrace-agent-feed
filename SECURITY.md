# Security Policy

## Reporting a vulnerability

Email **support@markettrace.ai** with details and reproduction steps.
Please do not open a public issue for security reports.

We aim to acknowledge reports on a best-effort basis and will keep you
updated on remediation. There is no paid bug-bounty program.

## Scope

- The hosted agent-feed endpoint: `https://api.markettrace.ai` (including
  `/mcp` and the OAuth resource-server metadata).
- The stdio front-door bridge in this repository (`mcp_server.py`).

The feed is **read-only**: it serves public market data and cannot trade,
move funds, or accept write operations. Authentication is OAuth (Stytch);
the service never asks for exchange API keys or wallet credentials.

## Out of scope

- Denial-of-service / volumetric testing against the hosted endpoint.
- Findings in third-party dependencies without a demonstrated impact on the
  service.
- The upstream exchange feeds (Binance, Bybit, OKX, Hyperliquid).

## Handling of your report

We do not publish reporter details without consent. If a fix affects users,
we will note it in the relevant release.
