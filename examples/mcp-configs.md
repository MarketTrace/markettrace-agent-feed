# Client configs

The hosted endpoint is `https://api.markettrace.ai/mcp` (Streamable HTTP,
OAuth). Prefer connecting to it directly; the stdio bridge in this repo is a
fallback for clients that cannot do either OAuth or remote MCP.

## Claude (web / desktop)

Settings → Connectors → **Add custom connector** →
`https://api.markettrace.ai/mcp` → authorize when prompted (email magic link).

## Claude Code

```bash
claude mcp add --transport http markettrace https://api.markettrace.ai/mcp
```

## Cursor (`~/.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "markettrace": { "url": "https://api.markettrace.ai/mcp" }
  }
}
```

## Stdio-only clients — via mcp-remote (handles OAuth)

```json
{
  "mcpServers": {
    "markettrace": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://api.markettrace.ai/mcp"]
    }
  }
}
```

## This repo's bridge (introspection without credentials)

```json
{
  "mcpServers": {
    "markettrace-bridge": {
      "command": "python3",
      "args": ["/path/to/mcp_server.py"],
      "env": { "MARKETTRACE_BEARER": "<optional bearer for proxied calls>" }
    }
  }
}
```
