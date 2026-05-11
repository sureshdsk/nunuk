import json
import os
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
MAX_ITERATIONS = 25

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "Read",
            "description": "Read the contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read.",
                    }
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Write",
            "description": "Write content to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to write.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write.",
                    },
                },
                "required": ["file_path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Bash",
            "description": "Execute a bash command and return its output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute.",
                    }
                },
                "required": ["command"],
            },
        },
    },
]


BASH_TIMEOUT = 30


def _base_url() -> str:
    if os.environ.get("LLM_PROVIDER") == "mock":
        url = os.environ.get("MOCK_LLM_BASE_URL")
        if not url:
            print(
                "MOCK_LLM_BASE_URL must be set when LLM_PROVIDER=mock",
                file=sys.stderr,
            )
            sys.exit(1)
        return url
    return OPENROUTER_BASE_URL


def _call_with_retry(client, model, messages, tools=None):
    response = None
    for attempt in range(MAX_RETRIES):
        try:
            kwargs = {"model": model, "messages": messages}
            if tools:
                kwargs["tools"] = tools
            response = client.chat.completions.create(**kwargs)
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

    if response is None:
        print(
            f"error: max retries ({MAX_RETRIES}) exceeded, giving up",
            file=sys.stderr,
        )
        sys.exit(1)

    return response


def _validate_path(path: str) -> str:
    resolved = os.path.realpath(path)
    cwd = os.path.realpath(os.getcwd())
    if ".." in os.path.normpath(path).split(os.sep):
        return f"error: path traversal denied: {path}"
    if not resolved.startswith(cwd + os.sep) and resolved != cwd:
        return f"error: path escapes workspace: {path}"
    return ""


def _execute_tool(name: str, args: dict) -> str:
    if name == "Read":
        path = args.get("file_path", "")
        try:
            with open(path) as f:
                return f.read()
        except FileNotFoundError:
            return f"error: file not found: {path}"
        except Exception as e:
            return f"error: {e}"
    if name == "Write":
        path = args.get("file_path", "")
        content = args.get("content", "")
        err = _validate_path(path)
        if err:
            return err
        with open(path, "w") as f:
            f.write(content)
        return f"Wrote {path}"
    if name == "Bash":
        command = args.get("command", "")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=BASH_TIMEOUT,
                check=False,
            )
            output = result.stdout
            if result.stderr:
                output += f"\nstderr: {result.stderr}"
            if result.returncode != 0:
                output += f"\nexit code: {result.returncode}"
            return output or "(no output)"
        except subprocess.TimeoutExpired:
            return f"error: command timed out after {BASH_TIMEOUT}s"
    return f"unknown tool: {name}"


def run(prompt: str) -> str:
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

    for _ in range(MAX_ITERATIONS):
        response = _call_with_retry(client, model, messages, tools=TOOLS)
        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            return message.content or ""

        for tc in message.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
                result = _execute_tool(tc.function.name, args)
            except Exception as e:
                result = f"tool error: {e}"
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )

    print("agent: iteration cap reached", file=sys.stderr)
    sys.exit(1)
