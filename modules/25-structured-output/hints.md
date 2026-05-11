# Hints — Module 25 (Structured Output)

Three levels. Try for 30 minutes between peeks.

<details>
<summary><strong>Level 1 — a nudge</strong></summary>

OpenAI's `response_format={"type": "json_schema", "json_schema": {"name": ..., "schema": ..., "strict": True}}` is the cleanest path — the model guarantees valid JSON without you needing to re-prompt. For Anthropic, define a single tool whose `input_schema` is your output schema, then force `tool_choice={"type": "tool", "name": "..."}`. The fallback prompt is just `"Respond ONLY with JSON matching this schema:\n\n{schema}"` appended to the system prompt.

</details>

<details>
<summary><strong>Level 2 — partial code</strong></summary>

```python
# app/providers/openai_provider.py
def chat(self, *, messages, tools=None, output_schema=None, stream=False):
    kwargs = {"model": self.model, "messages": messages}
    if tools:
        kwargs["tools"] = tools
    if output_schema is not None:
        kwargs["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "out",
                "schema": output_schema,
                "strict": True,
            },
        }
    response = self.client.chat.completions.create(**kwargs)
    ...

def supports_structured_output(self) -> bool:
    return True
```

</details>

<details>
<summary><strong>Level 3 — near-complete</strong></summary>

The agent-loop tail (`app/agent.py`):

```python
import json, jsonschema

def finalize(content: str, schema: dict | None, provider: Provider) -> str:
    if schema is None:
        return content
    try:
        data = json.loads(content)
        jsonschema.validate(data, schema)
        return json.dumps(data)  # canonical
    except (json.JSONDecodeError, jsonschema.ValidationError) as e:
        if provider.supports_structured_output():
            print(f"schema validation failed: {e}", file=sys.stderr)
            sys.exit(2)
        # Fallback re-prompt
        messages.append({"role": "system",
                         "content": f"Your previous response did not match the schema. Error: {e}. Respond ONLY with valid JSON matching the schema."})
        retry = provider.chat(messages=messages)
        data = json.loads(retry.content)
        jsonschema.validate(data, schema)
        return json.dumps(data)
```

</details>
