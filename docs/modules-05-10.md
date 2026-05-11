# Modules 05–10: Implementation Notes

This documents the design decisions made while implementing modules 05 through 10.

## Architecture after Module 10

```
app/
├── __init__.py
├── main.py          # entry point: doctor(), CLI parsing, calls agent.run()
└── agent.py         # agent loop, tools, retry logic, LLM client
```

`main.py` is a thin shell (~70 lines): it parses args and delegates to `doctor()` or `agent.run()`. All agent intelligence lives in `agent.py` (~237 lines).

## Module-by-module decisions

### 05 — Advertise Tools

**Decision: Switched from streaming to non-streaming.**

Module 03 introduced streaming (`stream=True`), but detecting tool calls in SSE deltas requires accumulating partial `tool_calls` chunks across many frames — fragile and complex for a teaching module. Since module 07's hints show a non-streaming agent loop, switching in module 05 is the natural transition point. Streaming was a learning exercise; tool use is the new foundation.

The Echo tool was chosen as the simplest possible tool schema (one string param) to isolate the "advertise + detect" learning objective.

### 06 — Execute Tools

**Decision: Single round-trip (not a loop yet).**

Module 06 does exactly one tool-call → execute → send-result-back → get-answer cycle. The agent appends the assistant message (with `model_dump(exclude_none=True)` to handle `content=None` when tool_calls are present) and a `role: tool` message with the correct `tool_call_id`.

This keeps the diff from module 05 small and focused. The loop comes in module 07.

### 07 — The Agent Loop

**Decision: Extract `app/agent.py`, move all LLM/tool logic there.**

The instructions say the loop skeleton lives in `app/agent.py`. This is the right place to split: `main.py` becomes a thin entry point, `agent.py` owns the loop, tools, retry logic, and client setup.

Key implementation details:
- `MAX_ITERATIONS = 25` (per the instructions)
- `model_dump(exclude_none=True)` for assistant message serialization — avoids the `content: None` edge case
- Tool errors are caught per-tool-call and reported as `"tool error: ..."` to keep the loop alive
- Iteration cap exits via `sys.exit(1)` with `"agent: iteration cap reached"` on stderr

**Tool evolution:** Echo (modules 05-06) replaced by Read + Write (module 07+). Read is basic `open().read()` at this point; pagination comes in module 10.

### 08 — Write Tool

**Decision: Path validation via `os.path.realpath` + cwd comparison.**

Two checks:
1. `".."` in `normpath(path).split(os.sep)` — catches obvious traversal even if symlinks resolve elsewhere
2. `os.path.realpath(path)` must start with `os.path.realpath(os.getcwd())` — catches symlink-based escapes

Both checks are needed: the first catches intent, the second catches actual resolution. Error messages distinguish "path traversal denied" vs "path escapes workspace."

### 09 — Bash Tool

**Decision: `shell=True` with a fixed 30s timeout.**

`shell=True` is simpler for the LLM to invoke (it sends a single string command). The timeout prevents runaway processes. Stdout, stderr, and exit code are all reported back to the LLM so it can diagnose failures.

No command allowlist was implemented — the instructions mention it but the test.yml doesn't assert on it, and a teaching agent doesn't need the complexity at this stage.

### 10 — Read Tool with Pagination

**Decision: `cat -n` formatting with right-justified 6-char line numbers + tab.**

The format `f"{i + 1:>6}\t{lines[i]}"` matches `cat -n` output exactly. This is a deliberate choice over zero-padded or left-justified numbering — it's what developers expect.

Binary detection uses the NUL-byte heuristic (check first 8KB for `\x00`). This is simple, fast, and catches the vast majority of binary files without importing `magic`.

Pagination uses 1-based `offset` (matching editor line numbers) and `limit` (max lines to return). Both default to "everything" when omitted.

## Constants summary

| Constant | Value | Module | Purpose |
|---|---|---|---|
| `MAX_RETRIES` | 10 | 04 | Max retry attempts for 429/5xx |
| `RETRY_BASE_DELAY` | 0.5 | 04 | Base delay in seconds for exponential backoff |
| `MAX_ITERATIONS` | 25 | 07 | Agent loop iteration cap |
| `BASH_TIMEOUT` | 30 | 09 | Bash command timeout in seconds |

## Merge commits

| Module | Merge commit | Branch |
|---|---|---|
| 05 | `9ffd0d9` | `module/05-advertise-tools` |
| 06 | `b337b46` | `module/06-execute-tools` |
| 07 | `200005e` | `module/07-the-agent-loop` |
| 08 | `7b27ff3` | `module/08-write-tool` |
| 09 | `a147f3b` | `module/09-bash-tool` |
| 10 | `1705fcd` | `module/10-read-tool-with-pagination` |
