import os
import sys
import time

from dotenv import load_dotenv
from openai import APIStatusError, OpenAI

from app.config import (
    DEFAULT_MODEL,
    MAX_RETRIES,
    OPENROUTER_BASE_URL,
    RETRY_BASE_DELAY,
)
from app.exceptions import ConfigurationError, MaxRetriesExceeded


class LLMClient:
    def __init__(self):
        load_dotenv()
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise ConfigurationError("OPENROUTER_API_KEY is not set")

        self._client = OpenAI(
            api_key=api_key,
            base_url=self._resolve_base_url(),
            max_retries=0,
        )
        self._model = os.environ.get("MODEL", DEFAULT_MODEL)

    def _resolve_base_url(self) -> str:
        if os.environ.get("LLM_PROVIDER") == "mock":
            url = os.environ.get("MOCK_LLM_BASE_URL")
            if not url:
                raise ConfigurationError(
                    "MOCK_LLM_BASE_URL must be set when LLM_PROVIDER=mock"
                )
            return url
        return OPENROUTER_BASE_URL

    def create(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ):
        kwargs: dict = {"model": self._model, "messages": messages}
        if tools:
            kwargs["tools"] = tools

        response = None
        for attempt in range(MAX_RETRIES):
            try:
                response = self._client.chat.completions.create(**kwargs)
                break
            except APIStatusError as exc:
                if exc.status_code == 429 or exc.status_code >= 500:
                    delay = min(2 ** attempt * RETRY_BASE_DELAY, 8)
                    print(
                        f"retry {attempt + 1}/{MAX_RETRIES}: "
                        f"{exc.status_code}, waiting {delay:.1f}s",
                        file=sys.stderr,
                    )
                    time.sleep(delay)
                    continue
                raise

        if response is None:
            raise MaxRetriesExceeded(
                f"max retries ({MAX_RETRIES}) exceeded, giving up"
            )

        return response
