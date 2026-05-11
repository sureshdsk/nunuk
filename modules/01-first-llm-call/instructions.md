# Module 01 — First LLM Call

> Track 1 — LLM Plumbing
> Branch: `module/01-first-llm-call`

## What you'll build

Your first conversation with an LLM. Given a prompt via `-p "..."`, your agent will send a single chat completion request to OpenRouter and print the assistant's reply.

This is the smallest possible useful program — but it's the foundation everything else stands on. Get this right and the next 35 modules are mostly elaboration.

## Why it matters

Every coding agent — Claude Code, Cursor, Aider, the seed POC for this course — starts with exactly this loop: format a message, send it to an LLM API, get a response back. The OpenAI SDK + OpenRouter base URL combo we use here will carry you all the way to Module 22 before you need to abstract it.

## Prerequisites

- [`00-setup`](../00-setup/instructions.md): your environment is healthy; `runner test --module 00` is green.

## Learning goals

By the end of this module you can:

- [ ] Construct an OpenAI client pointed at OpenRouter.
- [ ] Send a chat completion request with one user message.
- [ ] Extract the assistant's text from `response.choices[0].message.content`.
- [ ] Switch the agent into mock-LLM mode via `LLM_PROVIDER=mock` + `MOCK_LLM_BASE_URL`.

## What's already done for you

The starter branch contains:

- Module 00's `--doctor` solved.
- `app/main.py` with `argparse` already handling `-p` (prompt) and `--doctor`.
- `pyproject.toml` declaring `openai>=2.15.0` and `python-dotenv`.
- A `chat()` stub in `app/main.py` with TODO markers.

## Your task

1. In `app/main.py`, implement the `chat(prompt: str) -> str` function:
   1. Construct an `OpenAI` client with `api_key=OPENROUTER_API_KEY` and `base_url`.
   2. Determine `base_url` from env: if `LLM_PROVIDER == "mock"`, use `MOCK_LLM_BASE_URL`; otherwise use `https://openrouter.ai/api/v1`.
   3. Call `client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])`.
   4. Return `response.choices[0].message.content`.
2. Wire it into `main()`: when `args.prompt` is set, print `chat(args.prompt)` and exit 0.

## Test contract

Tests run against the mock-LLM. Fixtures are in `fixtures/llm/`.

- **`prints assistant response`**: prompt `"Say exactly: hello"`, mock returns `"hello"`, stdout contains `hello`, exit 0.
- **`uses MOCK_LLM_BASE_URL when mock mode`**: the mock-LLM server records that the request hit it (not OpenRouter).
- **`fails clearly when API key missing`**: with `OPENROUTER_API_KEY` unset, exit non-zero, stderr explains.

Run locally:

```bash
runner test --module 01
```

## Hints

See [`hints.md`](./hints.md). Try for at least 30 minutes before peeking.

## Stretch

See [`stretch.md`](./stretch.md). Suggestions: handle the edge case where `response.choices[0].message.content` is `None` (it can be when the model returns only tool calls — relevant for Module 05 but worth thinking about now).

## Reference

See [`reference.md`](./reference.md).
