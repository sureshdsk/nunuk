# Module 24 — Provider Abstraction

> Track 5 — Robustness
> Branch: `module/24-provider-abstraction`

## What you'll build

**The pivot.** A `Provider` protocol that hides the difference between LLM providers, plus two implementations: `OpenAIProvider` (covers OpenRouter) and `AnthropicProvider` (native Messages API). Selectable via `LLM_PROVIDER=openai|anthropic|mock`.

After this module, every subsequent module talks to whichever provider is configured. The provider-specific cruft you've accumulated (cache_control markers, tokenizer differences, usage-metadata field names) lives behind the abstraction and stops contaminating your agent code.

## Why it matters

Real coding agents support multiple providers — partly for resilience, partly because different models excel at different things, partly because users have credits with different vendors. Doing this refactor now (after you've felt the pain in Modules 20-22) means the abstraction is grounded in real constraints, not ceremony. You'll know exactly what the abstraction needs to expose because you've already needed those things.

## Prerequisites

- [`23-prompt-caching`](../23-prompt-caching/instructions.md): you've used `cache_control` markers and verified cache hits.
- All of Tracks 1-4 solved.

## Learning goals

By the end of this module you can:

- [ ] Define a `Provider` Protocol with the right contract for chat completions.
- [ ] Normalize the response shape: tool calls, usage, cache reads.
- [ ] Implement `OpenAIProvider` and `AnthropicProvider` against the protocol.
- [ ] Pass the same behavioral test against both providers using the same mock fixture (with provider-specific wire format).

## What's already done for you

The starter branch contains:

- All of Modules 00-23 solved.
- `app/llm.py` has the existing OpenAI-SDK-pointed-at-OpenRouter code.
- A `Protocol` definition stub in `app/providers/__init__.py`.
- Empty `app/providers/openai_provider.py` and `app/providers/anthropic_provider.py`.
- An `anthropic` package added to `pyproject.toml`.
- The mock-LLM server now optionally serves Anthropic Messages API on `/v1/messages` (enabled when the test sets `MOCK_LLM_ANTHROPIC=1`).

## Your task

1. Define `Provider` protocol in `app/providers/__init__.py`:
   ```python
   class Provider(Protocol):
       def chat(self, *, messages: list[dict], tools: list[dict], stream: bool = False) -> ProviderResponse:
           ...
   ```
   `ProviderResponse` is a small dataclass with `content`, `tool_calls`, `usage`, `cache_read_tokens`, `finish_reason`.
2. Implement `OpenAIProvider` in `app/providers/openai_provider.py`:
   - Wraps the existing OpenAI SDK client.
   - Translates `ChatCompletion` response into `ProviderResponse`.
3. Implement `AnthropicProvider` in `app/providers/anthropic_provider.py`:
   - Uses the `anthropic` SDK (Messages API).
   - Translates message format: OpenAI's `tools` → Anthropic's `tools` (different shape).
   - Translates response format: Anthropic's `content` blocks (text, tool_use) → unified `content` + `tool_calls`.
4. Add a factory in `app/providers/__init__.py`:
   ```python
   def get_provider() -> Provider:
       kind = os.environ.get("LLM_PROVIDER", "openai")
       ...
   ```
5. Refactor `app/agent.py` to call `provider.chat(...)` instead of the OpenAI client directly.

## Test contract

- **`OpenAI provider — three-step loop`**: existing fixture from Module 07 still passes with `LLM_PROVIDER=openai` (mock).
- **`Anthropic provider — three-step loop`**: same fixture, but mock serves Anthropic Messages format. Behavior identical: `summary.txt` exists with same content; tool sequence Read → Write; exit 0.
- **`provider switch by env`**: identical prompt under both providers produces same observable output (sampled via mock fixtures).
- **`unknown provider errors clearly`**: `LLM_PROVIDER=badname` exits non-zero with stderr explaining valid values.

Run locally:

```bash
runner test --module 24
```

## Hints

See [`hints.md`](./hints.md). Try for at least 30 minutes before peeking.

## Stretch

See [`stretch.md`](./stretch.md). Suggestions: add a `MockProvider` that doesn't go through HTTP at all (faster CI); add cost/latency telemetry into `ProviderResponse`; add a passthrough provider that round-robins between OpenAI and Anthropic for resilience.

## Reference

See [`reference.md`](./reference.md). The Anthropic Messages API differs from OpenAI's Chat Completions in ~6 places that matter for this refactor — they're enumerated there.
