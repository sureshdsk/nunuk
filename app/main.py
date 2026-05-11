import argparse
import os
import shutil
import subprocess
import sys

from dotenv import load_dotenv

from app.agent import run

DEFAULT_MODEL = "anthropic/claude-haiku-4.5"


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
        result = run(args.prompt)
        print(result)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
