# Module 25 — Structured Output

> Track 6 — Planning & Memory
> Branch: `module/25-structured-output`

## What you'll build

Support for an `--output-schema <file.json>` flag that loads a JSON Schema and forces the agent's final assistant message to validate against it. Two implementation paths share the same surface: a native path for providers that support structured outputs (OpenAI `response_format={"type": "json_schema", ...}`, Anthropic tool-use-as-schema), and a prompt-engineered fallback that re-prompts on validation failure for providers that don't. The `Provider` protocol from Module 24 grows a `supports_structured_output()` capability check.

## Why it matters

Tool calls already have typed arguments — your agent already speaks "structured" on the way in. The missing half is structured *output*: the agent's final response. Production agents (pydantic-deepagents' `output_type=PydanticModel`, OpenAI Assistants' Response API) lean on this so downstream code can `result.score`, `result.summary`, `result.issues` instead of regex-scraping prose. Plan Mode (Module 27) and the capstone (Module 39) will both benefit.

## Prerequisites

24-provider-abstraction

Run `runner test --module 24` to confirm the prior module is green before starting (if applicable).

## Learning goals

By the end of this module you can:

- [ ] Load a JSON Schema from a file and pass it through to a provider's structured-output API.
- [ ] Validate provider responses against the schema and surface a typed error on mismatch.
- [ ] Implement a prompt-engineered fallback (re-prompt with the schema and the validation error) for providers that don't support structured outputs natively.
- [ ] Extend the `Provider` protocol with `supports_structured_output()` and route accordingly.

## What's already done for you

The starter branch contains:

- All of Modules 00-24 solved.
- A `jsonschema` dependency in `pyproject.toml`.
- An `--output-schema` arg slot in `app/cli.py` with `# TODO` markers.
- `app/providers/__init__.py` has a `supports_structured_output` method stub on the protocol.
- Two sample schemas in `fixtures/schemas/`: `code-review.json` and `summary.json`.

## Your task

1. In `app/cli.py`, accept `--output-schema PATH` and load the JSON Schema at startup.
2. In `app/providers/openai_provider.py`, implement `supports_structured_output() -> True` and wire the schema into `response_format`.
3. In `app/providers/anthropic_provider.py`, implement structured output via the "tool-use as schema" trick (single forced tool call whose schema is the output schema). Return its arguments as the final content.
4. In `app/agent.py`, after the loop terminates:
   - If a schema is set, validate the final assistant message with `jsonschema.validate`.
   - On `ValidationError`, if the provider doesn't support structured output natively, re-prompt once with the schema and the validation error appended; otherwise exit non-zero with the error.
5. When schema is set and validation passes, print **only** the JSON (no rendered markdown).

## Test contract

- **`valid response matches schema`**: mock returns valid JSON matching `code-review.json` → stdout parses as JSON and validates → `exit_code == 0`.
- **`invalid response triggers re-prompt`** (fallback provider only): mock returns bad JSON first, valid JSON second → agent makes two completions, exits 0.
- **`invalid response with native support fails fast`**: mock returns bad JSON, native provider → agent exits non-zero with `schema validation` in stderr.
- **`unsupported provider falls back, not crashes`**: provider without native support handles schema via re-prompt; observable via `stderr_contains "fallback"` or via call count.

Run locally:

```bash
runner test --module 25
```

## Hints

Try for at least 30 minutes before peeking. Hints are progressive — see [`hints.md`](./hints.md).

## Stretch

Optional extensions for finishers — see [`stretch.md`](./stretch.md).

## Reference

External reading and concept primers — see [`reference.md`](./reference.md).
