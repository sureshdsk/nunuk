import argparse
import os
import shutil
import subprocess
import sys

from dotenv import load_dotenv
from openai import OpenAI

DEFAULT_MODEL = "anthropic/claude-haiku-4.5"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
SYSTEM_PROMPT = "You are a helpful, concise coding assistant."


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

    client = OpenAI(api_key=api_key, base_url=_base_url())
    model = os.environ.get("MODEL", DEFAULT_MODEL)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or ""


def main() -> int:
    parser = argparse.ArgumentParser(prog="agent", description="Course coding agent.")
    parser.add_argument("--doctor", action="store_true", help="Verify the dev environment.")
    parser.add_argument("-p", "--prompt", help="Single-shot prompt to send to the model.")
    args = parser.parse_args()

    if args.doctor:
        return doctor()

    if args.prompt:
        print(chat(args.prompt))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
