"""Interactive REPL UI for the agent.

`rich` styles the output. `prompt_toolkit` drives input, giving us
arrow-key history, line editing, multi-line entry (Esc-Enter), and
Ctrl-C/Ctrl-D semantics that match the standard Python REPL.

When stdin or stdout is not a TTY (the test runner pipes stdin via
`printf '...\\n' | ./agent`) we fall back to plain `input()` so
behavior stays deterministic and prompt_toolkit's terminal probing
doesn't crash on closed pipes.

Future module hooks live at the points marked `# Module XX:` below.
"""
import sys
from collections.abc import Callable
from contextlib import nullcontext
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from app.agent import Agent
from app.exceptions import AgentError
from app.llm import LLMClient
from app.tools import ToolRegistry


PROMPT_PLAIN = "> "
HELP_BODY = """\
[bold]Commands[/bold]
  [cyan]/help[/cyan]   show this message
  [cyan]/exit[/cyan]   quit the session

[dim]Up/Down browse history. Ctrl-D on an empty line exits.
Multi-line input: Esc then Enter.[/dim]"""


class ReplUI:
    """Styled REPL frontend with a TTY/non-TTY split.

    All output flows through `self.console` so the test runner can capture
    a clean stream and a future Module 15 swap to markdown rendering only
    has to change `show_assistant`.
    """

    def __init__(self) -> None:
        self.console = Console()
        self._is_tty = sys.stdin.isatty() and sys.stdout.isatty()
        self._session = self._build_session() if self._is_tty else None

    def _build_session(self):
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import InMemoryHistory
        # Module 29 (persistent session memory) will swap this for a
        # FileHistory pointing at ~/.nunuk/history so command recall
        # survives across `./agent` invocations.
        return PromptSession(history=InMemoryHistory())

    def banner(self) -> None:
        if not self._is_tty:
            return
        body = Text.from_markup(
            "Type [bold cyan]/help[/bold cyan] for commands. "
            "[dim]Ctrl-D to exit.[/dim]"
        )
        self.console.print(
            Panel.fit(body, title="[bold cyan]nunuk[/bold cyan]", border_style="cyan")
        )

    def help(self) -> None:
        self.console.print(Panel.fit(HELP_BODY, border_style="dim"))

    def read_input(self) -> str:
        """Read one line. EOFError on Ctrl-D / closed stdin propagates.

        In TTY mode KeyboardInterrupt during line editing is consumed
        (matching the standard Python REPL: Ctrl-C clears the buffer
        and redraws the prompt). In non-TTY mode it propagates so the
        runner can SIGINT a stuck session cleanly.
        """
        if self._session is None:
            return input(PROMPT_PLAIN)

        from prompt_toolkit.formatted_text import HTML

        while True:
            try:
                return self._session.prompt(HTML("<ansicyan><b>></b></ansicyan> "))
            except KeyboardInterrupt:
                continue

    def thinking(self, label: str = "thinking"):
        """Spinner shown while a turn is in flight.

        Returns a context manager. In non-TTY mode it is a no-op so the
        runner sees a clean stdout. The spinner auto-clears on exit so
        the assistant reply appears in its place.

        Module 03 (streaming) replaces this with token-by-token output —
        the spinner stops as soon as the first chunk arrives. A small
        enhancement on top of Module 06 will swap the label to the
        current tool name while a tool is executing (`thinking` →
        `Read a.py` → `Bash …`) by threading a callback through
        Agent.run that updates `Status.update(...)`.
        """
        if not self._is_tty:
            return nullcontext()
        return self.console.status(f"[cyan]{label}…[/cyan]", spinner="dots")

    def show_assistant(self, text: str) -> None:
        # Module 15 (markdown render) will replace this with
        # `self.console.print(Markdown(text))` so fenced code blocks,
        # bullets, and headings render rather than printing as raw text.
        # Module 16 (diff display) will additionally detect Edit-tool
        # diffs in the stream and render them through rich.syntax.
        self.console.print(text)

    def show_error(self, message: str) -> None:
        self.console.print(f"[bold red]error:[/bold red] {message}")

    def show_info(self, message: str) -> None:
        self.console.print(f"[dim]{message}[/dim]")

    def farewell(self) -> None:
        if self._is_tty:
            self.console.print()


SlashHandler = Callable[[Agent, ReplUI], Optional[str]]


def _cmd_exit(_agent: Agent, _ui: ReplUI) -> str:
    return "exit"


def _cmd_help(_agent: Agent, ui: ReplUI) -> None:
    ui.help()
    return None


# Module 18 (slash commands) extends this registry with /clear (reset
# Agent._messages back to just the system prompt), /history (dump the
# message buffer), /tools (list registered tools), /model (swap model
# mid-session). Module 27 (plan mode) adds /plan to flip a session
# flag the agent consults before tool execution.
SLASH_COMMANDS: dict[str, SlashHandler] = {
    "/exit": _cmd_exit,
    "/help": _cmd_help,
}


def dispatch_slash(line: str, agent: Agent, ui: ReplUI) -> Optional[str]:
    handler = SLASH_COMMANDS.get(line)
    if handler is None:
        ui.show_error(f"unknown command: {line}. Try /help.")
        return None
    return handler(agent, ui)


def run() -> int:
    try:
        llm = LLMClient()
        tools = ToolRegistry.with_defaults()
        agent = Agent(llm, tools)
    except AgentError as e:
        print(str(e), file=sys.stderr)
        return 1

    ui = ReplUI()
    ui.banner()

    while True:
        try:
            line = ui.read_input()
        except (EOFError, KeyboardInterrupt):
            ui.farewell()
            return 0

        line = line.strip()
        if not line:
            continue

        if line.startswith("/"):
            if dispatch_slash(line, agent, ui) == "exit":
                return 0
            continue

        try:
            # Module 03's streaming was dropped during the refactor. A
            # follow-up will pipe LLMClient.create(stream=True) chunks
            # through `ui.console.print(end="", flush=True)` so each
            # token lands as it arrives — at which point the spinner
            # below is replaced by progressive output. Module 19
            # (cancellation) hooks the same loop: SIGINT while streaming
            # aborts the turn and reconciles Agent._messages.
            # Module 20 (history truncation) will trim Agent._messages
            # before each call once the token budget is exceeded.
            # Module 21 (stuck-loop detection) will inspect the recent
            # tool-call pattern and break out if the same call repeats.
            with ui.thinking():
                result = agent.run(line)
            ui.show_assistant(result)
        except KeyboardInterrupt:
            # Module 19 will replace this with a proper in-flight cancel
            # that also rolls back the partial assistant message from
            # Agent._messages. For now we just bail out of the turn so
            # the REPL itself doesn't die.
            ui.show_info("interrupted")
        except AgentError as e:
            ui.show_error(str(e))
