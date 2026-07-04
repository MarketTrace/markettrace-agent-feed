FROM python:3.12-slim
WORKDIR /app
COPY mcp_server.py tools.json ./
# Drop root: the bridge needs no privileges (stdio + outbound HTTPS only).
USER nobody
# No dependencies. The bridge starts and answers introspection (initialize,
# tools/list) with zero credentials; tool calls need MARKETTRACE_BEARER or an
# OAuth-capable client pointed at the hosted endpoint.
ENTRYPOINT ["python", "mcp_server.py"]
