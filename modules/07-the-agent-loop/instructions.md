# Module 07 — The Agent Loop

> Track 2 — Tool Foundations
> Branch: `module/07-the-agent-loop`

## What you'll build

The full **agent loop**: call the LLM, execute any tool calls it returned, append results, loop again, and stop when the LLM returns a plain text answer (or you hit a safety cap on iterations).

This is the POC milestone. By the end of this module your agent matches the seed POC's behavior — it can take a prompt, do a multi-step tool-use plan, and return a final answer.

## Why it matters

Modules 05 and 06 covered the mechanics of one tool call. The loop is what makes an *agent* an agent: arbitrary chains of decisions, with the model choosing what to do next based on previous results. Without this loop you have a function caller; with it, you have an autonomous program.

## Prerequisites

- [`06-execute-tools`](../06-execute-tools/instructions.md): you can dispatch one tool call and feed its result back.

## Learning goals

By the end of this module you can:

- [ ] Implement a `while` loop that calls the LLM, dispatches tool calls, and stops when there are none.
- [ ] Add a max-iterations safety cap and exit non-zero when it fires.
- [ ] Maintain conversation history across turns, including tool-call/tool-result pairs in the right order.

## What's already done for you

The starter branch contains:

- Modules 00-06 solved.
- `app/agent.py::run_once(messages)` from Module 06: makes one round-trip and returns the LLM's response.
- Tool definitions for `Read` (advertised in 05, executed in 06).
- A loop skeleton in `app/agent.py::run(prompt)` with `# TODO` markers.

## Your task

1. Implement `run(prompt: str) -> str` in `app/agent.py`:
   1. Initialize `messages = [{"role": "user", "content": prompt}]`.
   2. Loop with a max-iterations cap (constant `MAX_ITERATIONS = 25` is fine).
   3. Each iteration: call the LLM with current `messages` and the tool list.
   4. Append the assistant's message to `messages`.
   5. If the assistant's message has `tool_calls`, execute each one and append a `{"role": "tool", "tool_call_id": ..., "content": ...}` message per result. Continue.
   6. If no `tool_calls`, return `message.content` (the final answer).
   7. If the cap fires, raise `SystemExit("agent: iteration cap reached")` — non-zero exit.
2. Wire it into `main()`: print the result of `run(args.prompt)`.

## Test contract

- **`three-step loop terminates`**: prompt `"Read a.py, write its summary to summary.txt"` with the mock returning `Read(a.py)` → `Write(summary.txt, ...)` → final text. Asserts `summary.txt` exists, tool sequence is `Read, Write`, exit 0, and `llm_call_count == 3`.
- **`iteration cap fires`**: mock fixture returns the same tool call indefinitely. Agent must exit non-zero with stderr containing `"iteration"`.
- **`tool result message has correct shape`**: introspects the mock-LLM transcript to confirm the agent sent `role: tool` with the matching `tool_call_id`.
- **`history preserved across iterations`**: assertion checks that the second LLM call's request body contains the assistant message and tool-result message from the first round.

Run locally:

```bash
runner test --module 07
```

## Hints

See [`hints.md`](./hints.md). Try for at least 30 minutes before peeking.

## Stretch

See [`stretch.md`](./stretch.md). Suggestions: structured logging of every tool call to stderr; per-tool timeout enforced from the loop level; add a `--max-iterations` CLI flag.

## Reference

The seed POC at `/Users/dsk/Developer/byocc/codecrafters-claude-code-python/app/main.py` (lines 107-131) shows essentially this loop. Compare your implementation to it after you've passed the tests — what did you do differently?
