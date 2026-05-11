import os
import subprocess
from abc import ABC, abstractmethod

from app.config import BASH_TIMEOUT


class Tool(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def schema(self) -> dict: ...

    @abstractmethod
    def execute(self, args: dict) -> str: ...


class ReadTool(Tool):
    @property
    def name(self) -> str:
        return "Read"

    @property
    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "Read",
                "description": (
                    "Read file contents with cat -n style line numbers. "
                    "Supports pagination via offset and limit."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to read.",
                        },
                        "offset": {
                            "type": "integer",
                            "description": "1-based starting line number. Defaults to 1.",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of lines to return.",
                        },
                    },
                    "required": ["file_path"],
                },
            },
        }

    def execute(self, args: dict) -> str:
        path = args.get("file_path", "")
        try:
            if self._is_binary(path):
                return f"error: binary file: {path}"
            with open(path) as f:
                lines = f.readlines()
            offset = args.get("offset", 1)
            limit = args.get("limit", len(lines))
            start = max(offset - 1, 0)
            end = min(start + limit, len(lines))
            return "".join(
                f"{i + 1:>6}\t{lines[i]}" for i in range(start, end)
            )
        except FileNotFoundError:
            return f"error: file not found: {path}"
        except Exception as e:
            return f"error: {e}"

    @staticmethod
    def _is_binary(path: str) -> bool:
        try:
            with open(path, "rb") as f:
                chunk = f.read(8192)
            return b"\x00" in chunk
        except Exception:
            return False


class WriteTool(Tool):
    @property
    def name(self) -> str:
        return "Write"

    @property
    def schema(self) -> dict:
        return {
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
        }

    def execute(self, args: dict) -> str:
        path = args.get("file_path", "")
        content = args.get("content", "")
        err = self._validate_path(path)
        if err:
            return err
        with open(path, "w") as f:
            f.write(content)
        return f"Wrote {path}"

    @staticmethod
    def _validate_path(path: str) -> str:
        resolved = os.path.realpath(path)
        cwd = os.path.realpath(os.getcwd())
        if ".." in os.path.normpath(path).split(os.sep):
            return f"error: path traversal denied: {path}"
        if not resolved.startswith(cwd + os.sep) and resolved != cwd:
            return f"error: path escapes workspace: {path}"
        return ""


class BashTool(Tool):
    @property
    def name(self) -> str:
        return "Bash"

    @property
    def schema(self) -> dict:
        return {
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
        }

    def execute(self, args: dict) -> str:
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


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    @property
    def schemas(self) -> list[dict]:
        return [t.schema for t in self._tools.values()]

    def execute(self, name: str, args: dict) -> str:
        tool = self._tools.get(name)
        if tool is None:
            return f"unknown tool: {name}"
        return tool.execute(args)

    @classmethod
    def with_defaults(cls) -> "ToolRegistry":
        registry = cls()
        registry.register(ReadTool())
        registry.register(WriteTool())
        registry.register(BashTool())
        return registry
