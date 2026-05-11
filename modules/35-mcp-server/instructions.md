# Module 35 — MCP Server

> Track 7 — Advanced
> Branch: `module/35-mcp-server`

## What you'll build

Your agent, exposed as an **MCP server** over stdio JSON-RPC. Any MCP-compatible client (including a different instance of your own agent from Module 30) can list your tools and invoke them.

By the end of this module, your agent is no longer just a consumer of the ecosystem — it's a participant.

## Why it matters

The Model Context Protocol is becoming the de-facto interop layer for agent tools. If your agent can act as both client (Module 30) and server (this module), it can be composed into any MCP-aware system: Claude Desktop, Claude Code, Cursor, custom orchestrators. This module is what turns your agent from "isolated CLI tool" into "platform component."

## Prerequisites

- [`34-mcp-client`](../34-mcp-client/instructions.md): you've spoken JSON-RPC over stdio in client role and understand the framing.

## Learning goals

By the end of this module you can:

- [ ] Implement an MCP server that handles `initialize`, `tools/list`, `tools/call`.
- [ ] Frame JSON-RPC messages correctly over stdio.
- [ ] Translate your existing tool registry into MCP's `inputSchema` format.
- [ ] Handle errors as JSON-RPC error responses (not stack traces on stdout).

## What's already done for you

The starter branch contains:

- All of Modules 00-34 solved.
- Your existing tool registry (`Read`, `Write`, `Bash`, `Edit`, `Glob`, `Grep`).
- A `agent serve mcp` subcommand entry point with TODO markers.
- A reference MCP server fixture under `fixtures/mcp-clients/` for testing.

## Your task

1. Implement `app/mcp_server.py::run_server()`:
   1. Read JSON-RPC messages from stdin (one JSON object per line, OR Content-Length-framed — pick one and document).
   2. Dispatch by method name:
      - `initialize` → respond with capabilities (`tools: {listChanged: false}`) and protocol version.
      - `notifications/initialized` → no-op (it's a notification).
      - `tools/list` → return your registered tools with name, description, inputSchema.
      - `tools/call` → look up the tool, execute it, return the result.
   3. Errors return a JSON-RPC error response, not an exception on stdout.
2. Wire `agent serve mcp` to call `run_server()`.

## Test contract

This module uses the `protocol-rpc` test type. The runner spawns your server and speaks JSON-RPC to it directly.

- **`initialize handshake`**: client sends `initialize`, server responds with capabilities and protocol version.
- **`tools/list returns expected tools`**: response includes `Read`, `Write`, `Bash`, `Edit`, `Glob`, `Grep` with non-empty descriptions and valid JSON schemas.
- **`tools/call Read returns content`**: client sends `tools/call` for `Read` with a known file path; server reads the file and returns the content.
- **`unknown method returns -32601`**: per JSON-RPC spec.
- **`malformed input doesn't crash`**: server stays alive after a bad request.

Run locally:

```bash
runner test --module 35
```

## Hints

See [`hints.md`](./hints.md). Try for at least 30 minutes before peeking.

## Stretch

See [`stretch.md`](./stretch.md). Suggestions: support `prompts/list` and `prompts/get` (additional MCP capability); add an HTTP/SSE transport in addition to stdio; package your server as a standalone CLI that other people can `npm install`-equivalent.

## Reference

See [`reference.md`](./reference.md). The MCP spec is at <https://modelcontextprotocol.io>.
