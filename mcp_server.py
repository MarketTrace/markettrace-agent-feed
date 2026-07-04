#!/usr/bin/env python3
"""MarketTrace agent-feed — stdio front-door bridge.

This bridge holds NO data and NO methodology — it is an open-source client
for the hosted MarketTrace agent-feed (https://api.markettrace.ai/mcp,
`ai.markettrace/agent-feed` in the official MCP registry).

- `initialize` / `tools/list` are answered locally from the bundled contract
  (tools.json — a snapshot of the hosted server's own tools/list), so the
  bridge starts and answers introspection with no credentials.
- `tools/call` is proxied to the hosted endpoint when MARKETTRACE_BEARER is
  set; without it, calls return an educational pointer to the hosted OAuth
  endpoint instead of data.

Most MCP clients should connect to the hosted endpoint directly (OAuth,
Streamable HTTP) or via `npx mcp-remote https://api.markettrace.ai/mcp`.
Zero dependencies; Python 3.9+.
"""
import json
import os
import sys
import urllib.error
import urllib.request

HOSTED = "https://api.markettrace.ai/mcp"
DOCS = "https://markettrace.ai/agents"
# MCP protocol revisions this bridge understands, newest first. On
# `initialize` we echo the client's version if we support it, else our
# newest (the spec then lets the client decide) — never blindly mirror.
SUPPORTED_PROTOCOLS = ["2025-06-18", "2025-03-26", "2024-11-05"]
PROTOCOL_FALLBACK = SUPPORTED_PROTOCOLS[0]

HERE = os.path.dirname(os.path.abspath(__file__))
# The contract snapshot: {version, generated_at, tools:[...]}. Regenerate
# from the live server (README §"Refresh the contract"); the version here
# is what the bridge reports in serverInfo.
with open(os.path.join(HERE, "tools.json"), encoding="utf-8") as fh:
    _contract = json.load(fh)
TOOLS = _contract["tools"]
CONTRACT_VERSION = _contract.get("version", "0.0.0")

NO_BEARER_HELP = (
    "This is the open-source front-door bridge; it holds no data. "
    f"Connect an MCP client to the hosted endpoint {HOSTED} "
    "(OAuth sign-in — e.g. a Claude custom connector, or "
    f"`npx mcp-remote {HOSTED}` for stdio-only clients), or set the "
    f"MARKETTRACE_BEARER environment variable to proxy calls. Docs: {DOCS}"
)


def send(payload):
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def reply(req_id, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": req_id}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    send(msg)


def call_hosted(request):
    """Forward a JSON-RPC request to the hosted endpoint verbatim; return its
    parsed JSON-RPC response (the hosted server answers JSON or a single SSE
    data frame)."""
    req = urllib.request.Request(
        HOSTED,
        data=json.dumps(request).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {os.environ['MARKETTRACE_BEARER']}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", "replace")
    if resp.headers.get("Content-Type", "").startswith("text/event-stream"):
        for line in body.splitlines():
            if line.startswith("data: "):
                body = line[len("data: "):]
    return json.loads(body)


def handle_tools_call(req):
    if not os.environ.get("MARKETTRACE_BEARER"):
        reply(
            req.get("id"),
            result={
                "content": [{"type": "text", "text": NO_BEARER_HELP}],
                "isError": True,
            },
        )
        return
    try:
        hosted = call_hosted(req)
    except urllib.error.HTTPError as e:
        detail = "authentication failed" if e.code == 401 else f"HTTP {e.code}"
        reply(
            req.get("id"),
            result={
                "content": [
                    {"type": "text", "text": f"Hosted endpoint error: {detail}. {NO_BEARER_HELP}"}
                ],
                "isError": True,
            },
        )
        return
    except Exception:
        reply(req.get("id"), error={"code": -32000, "message": "hosted endpoint unreachable"})
        return
    if "error" in hosted:
        reply(req.get("id"), error=hosted["error"])
    else:
        reply(req.get("id"), result=hosted.get("result"))


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = req.get("method", "")
        if "id" not in req:
            continue  # notification (e.g. notifications/initialized) — no reply
        if method == "initialize":
            requested = (req.get("params") or {}).get("protocolVersion")
            proto = requested if requested in SUPPORTED_PROTOCOLS else PROTOCOL_FALLBACK
            reply(
                req["id"],
                result={
                    "protocolVersion": proto,
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "markettrace-agent-feed-bridge",
                        "version": CONTRACT_VERSION,
                    },
                    "instructions": (
                        "Front-door bridge for the hosted MarketTrace agent-feed. "
                        + NO_BEARER_HELP
                    ),
                },
            )
        elif method == "ping":
            reply(req["id"], result={})
        elif method == "tools/list":
            reply(req["id"], result={"tools": TOOLS})
        elif method == "tools/call":
            handle_tools_call(req)
        else:
            reply(req["id"], error={"code": -32601, "message": f"method not found: {method}"})


if __name__ == "__main__":
    main()
