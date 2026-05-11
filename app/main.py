import argparse
import os
import shutil
import subprocess
import sys

from dotenv import load_dotenv

from app.agent import Agent
from app.config import DEFAULT_MODEL
from app.exceptions import AgentError
from app.llm import LLMClient
from app.repl import run as repl
from app.tools import ToolRegistry


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


def main() -> int:
    parser = argparse.ArgumentParser(prog="agent", description="Course coding agent.")
    parser.add_argument("--doctor", action="store_true", help="Verify the dev environment.")
    parser.add_argument("-p", "--prompt", help="Single-shot prompt to send to the model.")
    args = parser.parse_args()

    if args.doctor:
        return doctor()

    if args.prompt:
        try:
            llm = LLMClient()
            tools = ToolRegistry.with_defaults()
            agent = Agent(llm, tools)
            result = agent.run(args.prompt)
            print(result)
            return 0
        except AgentError as e:
            print(str(e), file=sys.stderr)
            return 1

    return repl()


if __name__ == "__main__":
    sys.exit(main())
