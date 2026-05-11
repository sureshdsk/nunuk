# Hints — Module 07 (The Agent Loop)

Three levels. Try for 30 minutes between peeks.

<details>
<summary><strong>Level 1 — a nudge</strong></summary>

You're building a `while` loop. Each iteration is one round-trip with the LLM. Two things you must track across iterations: the conversation history (`messages`) and the iteration count (`i`).

The termination condition is "the assistant message had no tool_calls." Until then, you keep going. Don't try to be clever about the loop structure — `while True` with an explicit `break` is fine, or `for i in range(MAX)` with a final raise.

Edge case to handle: tool result messages need a `tool_call_id` so the API can correlate them with the assistant's tool calls. Look at the assistant message you just got back to find the IDs.

</details>

<details>
<summary><strong>Level 2 — partial code</strong></summary>

```python
MAX_ITERATIONS = 25

def run(prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]

    for i in range(MAX_ITERATIONS):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS,
        )
        message = response.choices[0].message
        messages.append(message.model_dump())  # serialize for next request

        if not message.tool_calls:
            return message.content or ""

        for tc in message.tool_calls:
            result = execute_tool(tc.function.name, json.loads(tc.function.arguments))
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    # TODO: what should happen here?
```

</details>

<details>
<summary><strong>Level 3 — near-complete</strong></summary>

```python
def run(prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]

    for i in range(MAX_ITERATIONS):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS,
        )
        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            return message.content or ""

        for tc in message.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
                result = execute_tool(tc.function.name, args)
            except Exception as e:
                result = f"tool error: {e}"
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    raise SystemExit("agent: iteration cap reached")
```

The remaining gap is whether to serialize the assistant message with `model_dump()` or to build it manually. `model_dump(exclude_none=True)` is safest — it keeps the OpenAI library's exact shape and avoids the "content is None when only tool_calls present" edge case.

</details>
