# Reference — Module 25 (Structured Output)

Primary concepts, terminology, and external links.

## Concepts

Structured output is the dual of structured tool input: instead of the model producing free-form text, it produces JSON conforming to a schema you supply. Providers expose this in two shapes. OpenAI's `response_format: json_schema` enforces the schema in the decoder so the response is guaranteed valid. Anthropic doesn't have a direct equivalent yet but the same effect is achievable by defining a single tool whose `input_schema` is your output schema and forcing the model to call it. The portable fallback — useful for the mock-LLM and any provider without native support — is to append the schema to the prompt and re-prompt once on validation failure.

## Glossary terms used

See [`docs/glossary.md`](../../docs/glossary.md) for definitions of any unfamiliar terms.

## External reading

- [OpenAI — Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs).
- [Anthropic — Tool use with forced calling](https://docs.anthropic.com/en/docs/build-with-claude/tool-use).
- [pydantic-deepagents — `output_type=PydanticModel`](https://github.com/vstorm-co/pydantic-deepagents) (search the README for "Structured Output").
- [JSON Schema specification](https://json-schema.org/specification.html) — the format both providers consume.

## Implementation references

- The `Provider` protocol from Module 24 (`app/providers/__init__.py`) is where the new `supports_structured_output()` capability lands.
- The mock-LLM (`runner/mock_llm/`) needs a "wire" knob to simulate native-vs-fallback behavior in tests — see `docs/architecture/mock-llm.md`.
