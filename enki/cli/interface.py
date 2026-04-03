"""Rich interactive CLI for Enki AI."""
from __future__ import annotations

import asyncio
import logging
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from enki.core.assistant import Assistant
from enki.plugins import DEFAULT_PLUGINS

app = typer.Typer(
    name="enki",
    help="Enki AI — universal assistant",
    add_completion=False,
)

console = Console()
err_console = Console(stderr=True, style="bold red")

BANNER = """[bold cyan]
  ███████╗███╗   ██╗██╗  ██╗██╗      █████╗ ██╗
  ██╔════╝████╗  ██║██║ ██╔╝██║     ██╔══██╗██║
  █████╗  ██╔██╗ ██║█████╔╝ ██║     ███████║██║
  ██╔══╝  ██║╚██╗██║██╔═██╗ ██║     ██╔══██║██║
  ███████╗██║ ╚████║██║  ██╗██║     ██║  ██║██║
  ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝[/bold cyan]
[dim]  Universal AI Assistant  |  type /help for commands[/dim]
"""


def _print_banner() -> None:
    console.print(BANNER)


def _print_help() -> None:
    console.print(
        Panel(
            "\n".join(
                [
                    "[bold]/help[/bold]   — show this message",
                    "[bold]/reset[/bold]  — clear conversation history",
                    "[bold]/plugins[/bold]— list available plugins",
                    "[bold]/stream[/bold] — toggle streaming mode",
                    "[bold]/exit[/bold]   — quit",
                ]
            ),
            title="Commands",
            border_style="cyan",
        )
    )


async def _run_chat(
    stream: bool,
    provider: Optional[str],
    model: Optional[str],
) -> None:
    from enki.core.config import settings

    if provider:
        settings.provider = provider  # type: ignore[assignment]
    if model:
        if settings.provider == "openai":
            settings.openai_model = model
        else:
            settings.anthropic_model = model

    assistant = Assistant(plugins=DEFAULT_PLUGINS)

    _print_banner()
    console.print(f"[dim]Provider: [cyan]{settings.provider}[/cyan]  |  "
                  f"Plugins: {len(assistant.plugins)}  |  "
                  f"Streaming: {'on' if stream else 'off'}[/dim]\n")

    streaming = stream

    while True:
        try:
            user_input = Prompt.ask("[bold green]You[/bold green]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input.strip():
            continue

        # Built-in commands
        cmd = user_input.strip().lower()
        if cmd in ("/exit", "/quit", "exit", "quit"):
            console.print("[dim]Goodbye![/dim]")
            break
        if cmd == "/help":
            _print_help()
            continue
        if cmd == "/reset":
            assistant.reset()
            console.print("[yellow]Conversation history cleared.[/yellow]")
            continue
        if cmd == "/plugins":
            for p in assistant.plugins:
                console.print(f"  [cyan]{p.name}[/cyan] — {p.description}")
            continue
        if cmd == "/stream":
            streaming = not streaming
            console.print(f"[yellow]Streaming {'enabled' if streaming else 'disabled'}.[/yellow]")
            continue

        console.print()

        if streaming:
            console.print("[bold blue]Enki[/bold blue]: ", end="")
            async for chunk in assistant.stream(user_input):
                console.print(chunk, end="", highlight=False)
            console.print("\n")
        else:
            with console.status("[dim]Thinking…[/dim]", spinner="dots"):
                reply = await assistant.chat(user_input)
            console.print(
                Panel(
                    Markdown(reply),
                    title="[bold blue]Enki[/bold blue]",
                    border_style="blue",
                )
            )
        console.print()


@app.command()
def chat(
    stream: bool = typer.Option(False, "--stream", "-s", help="Stream responses token by token."),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="openai | anthropic"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override model name."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging."),
) -> None:
    """Start an interactive chat session."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    asyncio.run(_run_chat(stream=stream, provider=provider, model=model))


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host"),
    port: int = typer.Option(8000, "--port"),
    reload: bool = typer.Option(False, "--reload"),
) -> None:
    """Start the Enki AI API server."""
    try:
        import uvicorn
    except ImportError:
        err_console.print("uvicorn is not installed. Run: pip install uvicorn[standard]")
        sys.exit(1)

    console.print(f"[green]Starting Enki AI API on http://{host}:{port}[/green]")
    uvicorn.run("enki.api.app:app", host=host, port=port, reload=reload)


# Allow `enki` with no sub-command to drop straight into chat.
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        chat()
