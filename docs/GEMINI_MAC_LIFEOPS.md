# Gemini CLI on Mac -> LifeOps

The desired end state is simple: Gemini CLI on the Mac is another provider client of the same LifeOps MCP surface used by other agents. It should resolve and write the same durable objects rather than creating a Gemini-specific memory silo.

Gemini CLI currently supports project-scoped `.gemini/settings.json`, remote MCP over streamable HTTP (`httpUrl`), tool allowlists, and OAuth discovery for compatible remote MCP servers. Keep `trust: false` so consequential tool calls are never silently auto-approved.

Official references:
- https://github.com/google-gemini/gemini-cli/blob/main/docs/tools/mcp-server.md
- https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/configuration.md

## Project setup

Copy the template, then provide only the endpoint through your shell/session or secure configuration:

```bash
cp .gemini/settings.example.json .gemini/settings.json
export LIFEOPS_MCP_HTTP_URL='https://<lifeops-host>/<mcp-path>'
gemini mcp list
```

Do **not** commit `.gemini/settings.json` if you add machine-specific credentials or endpoints.

Equivalent CLI configuration is supported by Gemini CLI:

```bash
gemini mcp add -s project -t http lifeops "$LIFEOPS_MCP_HTTP_URL"
gemini mcp list
```

If the LifeOps remote MCP advertises OAuth metadata, Gemini CLI can discover the OAuth flow after a 401 and complete authentication in the local browser. Prefer that over long-lived copied bearer tokens. If the current LifeOps deployment still requires a static header/token, keep the value in environment/secure local configuration and add the header locally; never commit it to WorldLoop.

## Safe default tool surface

The checked-in template exposes only:

- `resolve`, `search`, `health`, `now`
- `observe`, `checkpoint`, `propose`

It intentionally excludes direct approval/execution tools. Gemini can discover state and create typed candidate work/deltas; Bridge/HomeBase remains the execution authority boundary.

## Canary

From a Gemini CLI session in this repo:

1. Ask it to resolve the WorldLoop project/proposal (`prop-85dc72d46765`).
2. Ask it to search for the most recent WorldLoop checkpoint/readiness evidence.
3. Call LifeOps health.
4. Ask it to explain the next experiment using those resolved objects.
5. Only if you intentionally want a durable test, create a non-authoritative observation/checkpoint and read it back.

A successful canary means Gemini on the Mac and OCI/ChatGPT are talking to the same durable object graph. It does **not** grant Gemini permission to execute consequential actions.
