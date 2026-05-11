import os
import re
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

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


class EditTool(Tool):
    @property
    def name(self) -> str:
        return "Edit"

    @property
    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "Edit",
                "description": (
                    "Replace an exact string in a file. "
                    "Fails if old_string is not found or appears more than once."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to edit.",
                        },
                        "old_string": {
                            "type": "string",
                            "description": "The exact string to replace.",
                        },
                        "new_string": {
                            "type": "string",
                            "description": "The replacement string.",
                        },
                    },
                    "required": ["file_path", "old_string", "new_string"],
                },
            },
        }

    def execute(self, args: dict) -> str:
        path = args.get("file_path", "")
        old_string = args.get("old_string", "")
        new_string = args.get("new_string", "")
        try:
            with open(path) as f:
                content = f.read()
        except FileNotFoundError:
            return f"error: file not found: {path}"
        except Exception as e:
            return f"error: {e}"

        count = content.count(old_string)
        if count == 0:
            return f"error: old_string not found in {path}"
        if count > 1:
            return f"error: old_string appears {count} times in {path}; must be unique"

        updated = content.replace(old_string, new_string, 1)
        with open(path, "w") as f:
            f.write(updated)
        return f"Edited {path}"


class GlobTool(Tool):
    @property
    def name(self) -> str:
        return "Glob"

    @property
    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "Glob",
                "description": (
                    "Fast file pattern matching tool. Returns matching paths "
                    "sorted by modification time (most recent first)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Glob pattern, e.g. '**/*.py' or 'src/*.ts'.",
                        },
                        "path": {
                            "type": "string",
                            "description": "Directory to search in. Defaults to current working directory.",
                        },
                    },
                    "required": ["pattern"],
                },
            },
        }

    def execute(self, args: dict) -> str:
        pattern = args.get("pattern", "")
        search_path = args.get("path", ".")
        base = Path(search_path).resolve()
        if not base.is_dir():
            return f"error: not a directory: {search_path}"
        try:
            matches = sorted(
                base.glob(pattern),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if not matches:
                return "No files matched the pattern."
            return "\n".join(str(m) for m in matches)
        except Exception as e:
            return f"error: {e}"


class GrepTool(Tool):
    @property
    def name(self) -> str:
        return "Grep"

    @property
    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "Grep",
                "description": (
                    "Search file contents for a regex pattern. "
                    "Uses ripgrep (rg) when available, falls back to Python re."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Regular expression pattern to search for.",
                        },
                        "path": {
                            "type": "string",
                            "description": "Directory or file to search in. Defaults to current working directory.",
                        },
                        "glob": {
                            "type": "string",
                            "description": "File glob to filter, e.g. '*.py'. Searches all files if omitted.",
                        },
                        "output_mode": {
                            "type": "string",
                            "description": (
                                "'files_with_matches' to list file paths only, "
                                "'content' to show matching lines with line numbers (default)."
                            ),
                        },
                    },
                    "required": ["pattern"],
                },
            },
        }

    def execute(self, args: dict) -> str:
        pattern = args.get("pattern", "")
        search_path = args.get("path", ".")
        glob_filter = args.get("glob")
        output_mode = args.get("output_mode", "content")

        if shutil.which("rg"):
            return self._run_rg(pattern, search_path, glob_filter, output_mode)
        return self._run_python(pattern, search_path, glob_filter, output_mode)

    def _run_rg(
        self, pattern: str, path: str, glob_filter: str | None, output_mode: str
    ) -> str:
        cmd = ["rg", "--no-heading", "--with-filename", "--line-number"]
        if output_mode == "files_with_matches":
            cmd.append("-l")
        if glob_filter:
            cmd.extend(["--glob", glob_filter])
        cmd.extend(["--", pattern, path])
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=BASH_TIMEOUT, check=False
            )
            if result.returncode == 1:
                return "No matches found."
            if result.returncode != 0:
                return f"error: {result.stderr.strip()}"
            return result.stdout.rstrip("\n")
        except subprocess.TimeoutExpired:
            return f"error: grep timed out after {BASH_TIMEOUT}s"

    def _run_python(
        self, pattern: str, path: str, glob_filter: str | None, output_mode: str
    ) -> str:
        try:
            regex = re.compile(pattern)
        except re.error as e:
            return f"error: invalid regex: {e}"

        base = Path(path).resolve()
        if not base.exists():
            return f"error: path not found: {path}"
        if base.is_file():
            files = [base]
        else:
            glob_pattern = f"**/{glob_filter}" if glob_filter else "**/*"
            files = [p for p in base.glob(glob_pattern) if p.is_file()]

        results = []
        for fpath in files:
            try:
                with open(fpath) as f:
                    lines = f.readlines()
            except Exception:
                continue
            matches = []
            for i, line in enumerate(lines, 1):
                if regex.search(line):
                    matches.append((i, line.rstrip("\n")))
            if matches:
                if output_mode == "files_with_matches":
                    results.append(str(fpath))
                else:
                    for lineno, content in matches:
                        results.append(f"{fpath}:{lineno}:{content}")

        if not results:
            return "No matches found."
        return "\n".join(results)


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
        registry.register(EditTool())
        registry.register(GlobTool())
        registry.register(GrepTool())
        registry.register(BashTool())
        return registry
