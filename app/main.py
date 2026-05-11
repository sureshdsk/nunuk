import argparse
import os
import shutil
import subprocess
import sys
import time

from dotenv import load_dotenv
from openai import APIStatusError, OpenAI

DEFAULT_MODEL = "anthropic/claude-haiku-4.5"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
SYSTEM_PROMPT = "You are a helpful, concise coding assistant."
MAX_RETRIES = 10
RETRY_BASE_DELAY = 0.5


def doctor() -> int:
    load_dotenv()
    failed = 0

    py = sys.version_info
    if (py.major, py.minor) >= (3, 12):
        print(f"python: {py.major}.{py.minor}.{py.micro} OK")
    else:
        print(f"python: {py.major}.{py.minor} FAIL (need >=3.12)")
        failed += 1

    uv_path = shutil.which("uv")
    if uv_path:
        result = subprocess.run(
            ["uv", "--version"], capture_output=True, text=True, check=False
        )
        version = result.stdout.strip() or "unknown"
        print(f"uv: {version} OK")
    else:
        print("uv: missing FAIL")
        failed += 1

    if os.environ.get("OPENROUTER_API_KEY"):
        print("OPENROUTER_API_KEY: set OK")
    else:
        print("OPENROUTER_API_KEY: missing FAIL")
        failed += 1

    model = os.environ.get("MODEL", DEFAULT_MODEL)
    print(f"MODEL: {model}")

    if failed == 0:
        print("OK")
        return 0
    return 1


def _base_url() -> str:
    if os.environ.get("LLM_PROVIDER") == "mock":
        url = os.environ.get("MOCK_LLM_BASE_URL")
        if not url:
            print("MOCK_LLM_BASE_URL must be set when LLM_PROVIDER=mock", file=sys.stderr)
            sys.exit(1)
        return url
    return OPENROUTER_BASE_URL


def chat(prompt: str) -> str:
    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY is not set", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=_base_url(), max_retries=0)
    model = os.environ.get("MODEL", DEFAULT_MODEL)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    stream = None
    for attempt in range(MAX_RETRIES):
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
            )
            break
        except APIStatusError as exc:
            if exc.status_code == 429 or exc.status_code >= 500:
                delay = min(2 ** attempt * RETRY_BASE_DELAY, 8)
                print(
                    f"retry {attempt + 1}/{MAX_RETRIES}: {exc.status_code}, waiting {delay:.1f}s",
                    file=sys.stderr,
                )
                time.sleep(delay)
                continue
            raise

    if stream is None:
        print(
            f"error: max retries ({MAX_RETRIES}) exceeded, giving up",
            file=sys.stderr,
        )
        sys.exit(1)

    collected = []
    for chunk in stream:
        delta = getattr(chunk.choices[0].delta, "content", None) or ""
        if delta:
            print(delta, end="", flush=True)
            collected.append(delta)
    print()
    return "".join(collected)


def main() -> int:
    parser = argparse.ArgumentParser(prog="agent", description="Course coding agent.")
    parser.add_argument("--doctor", action="store_true", help="Verify the dev environment.")
    parser.add_argument("-p", "--prompt", help="Single-shot prompt to send to the model.")
    args = parser.parse_args()

    if args.doctor:
        return doctor()

    if args.prompt:
        chat(args.prompt)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
