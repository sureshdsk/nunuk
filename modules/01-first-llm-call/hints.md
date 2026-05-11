# Hints — Module 01 (First LLM Call)

Three levels. Try for 30 minutes between peeks.

<details>
<summary><strong>Level 1 — a nudge</strong></summary>

The OpenAI SDK accepts a `base_url` parameter on the client constructor. That's the lever that lets one SDK talk to OpenRouter, your mock server, or OpenAI proper — by changing one URL.

The chat-completion shape is `client.chat.completions.create(model=..., messages=[...])`. `messages` is a list of dicts with `role` and `content` keys.

</details>

<details>
<summary><strong>Level 2 — partial code</strong></summary>

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def _base_url() -> str:
    if os.environ.get("LLM_PROVIDER") == "mock":
        return os.environ["MOCK_LLM_BASE_URL"]
    return "https://openrouter.ai/api/v1"

def chat(prompt: str) -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY not set")

    client = OpenAI(api_key=api_key, base_url=_base_url())
    model = os.environ.get("MODEL", "anthropic/claude-haiku-4.5")

    # TODO: call client.chat.completions.create with model and messages
    # TODO: extract assistant content and return it
```

</details>

<details>
<summary><strong>Level 3 — near-complete</strong></summary>

```python
def chat(prompt: str) -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY not set")

    client = OpenAI(api_key=api_key, base_url=_base_url())
    model = os.environ.get("MODEL", "anthropic/claude-haiku-4.5")

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or ""
```

The `or ""` matters: when we get to tool calls (Module 05), `content` can legally be `None`. Returning empty string keeps the print at the call site working. Wire it in `main()`:

```python
if args.prompt:
    print(chat(args.prompt))
    return 0
```

</details>
