import json

from app.config import MAX_ITERATIONS, SYSTEM_PROMPT
from app.exceptions import IterationCapReached
from app.llm import LLMClient
from app.tools import ToolRegistry


class Agent:
    def __init__(self, llm: LLMClient, tools: ToolRegistry):
        self._llm = llm
        self._tools = tools

    def run(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        for _ in range(MAX_ITERATIONS):
            response = self._llm.create(
                messages, tools=self._tools.schemas
            )
            message = response.choices[0].message
            messages.append(message.model_dump(exclude_none=True))

            if not message.tool_calls:
                return message.content or ""

            for tc in message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                    result = self._tools.execute(tc.function.name, args)
                except Exception as e:
                    result = f"tool error: {e}"
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    }
                )

        raise IterationCapReached("agent: iteration cap reached")
