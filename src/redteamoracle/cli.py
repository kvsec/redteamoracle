"""
redteamoracle CLI — A totally serious red team framework.
"""

from __future__ import annotations

import os
import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from redteamoracle import __version__
from redteamoracle.oracle import consult_oracle, _clear_lockout
from redteamoracle.ai import build_provider, OfflineProvider
from redteamoracle.modules import get_module, list_modules

console = Console()

BANNER = r"""
[bold red]
 ██▀███  ▓█████ ▓█████▄  ▒█████   ██▀███   ▄▄▄       ▄████▄   ██▓    ▓█████
▓██ ▒ ██▒▓█   ▀ ▒██▀ ██▌▒██▒  ██▒▓██ ▒ ██▒▒████▄    ▒██▀ ▀█  ▓██▒    ▓█   ▀
▓██ ░▄█ ▒▒███   ░██   █▌▒██░  ██▒▓██ ░▄█ ▒▒██  ▀█▄  ▒▓█    ▄ ▒██░    ▒███
▒██▀▀█▄  ▒▓█  ▄ ░▓█▄   ▌▒██   ██░▒██▀▀█▄  ░██▄▄▄▄██ ▒▓▓▄ ▄██▒▒██░    ▒▓█  ▄
░██▓ ▒██▒░▒████▒░▒████▓ ░ ████▓▒░░██▓ ▒██▒ ▓█   ▓██▒▒ ▓███▀ ░░██████▒░▒████▒
░ ▒▓ ░▒▓░░░ ▒░ ░ ▒▒▓  ▒ ░ ▒░▒░▒░ ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ░▒ ▒  ░░ ▒░▓  ░░░ ▒░ ░
  ░▒ ░ ▒░ ░ ░  ░ ░ ▒  ▒   ░ ▒ ▒░   ░▒ ░ ▒░  ▒   ▒▒ ░  ░  ▒   ░ ░ ▒  ░ ░ ░  ░
  ░░   ░    ░    ░ ░  ░ ░ ░ ░ ▒    ░░   ░   ░   ▒   ░          ░ ░      ░
   ░        ░  ░   ░        ░ ░     ░           ░  ░░ ░           ░  ░   ░  ░
                 ░                                   ░
[/bold red]"""

TAGLINE = "[dim]v{version} — The oracle decides if you're worthy today.[/dim]".format(version=__version__)


def print_banner() -> None:
    console.print(BANNER)
    console.print(f"  {TAGLINE}\n", justify="center")


def _resolve_provider(provider: str, api_key: Optional[str], base_url: Optional[str], model: Optional[str]):
    """Resolve AI provider, falling back to offline if nothing configured."""
    # Try env vars as fallback for API keys
    if not api_key:
        if provider in ("openai", "chatgpt"):
            api_key = os.environ.get("OPENAI_API_KEY")
        elif provider in ("claude", "anthropic"):
            api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not provider or provider == "offline":
        return OfflineProvider()

    try:
        return build_provider(provider, api_key=api_key, base_url=base_url, model=model)
    except Exception as e:
        console.print(f"[yellow]⚠  Could not initialize AI provider: {e}[/yellow]")
        console.print("[dim]Falling back to offline oracle responses.[/dim]")
        return OfflineProvider()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.group(invoke_without_command=True)
@click.version_option(__version__, prog_name="redteamoracle")
@click.option("--provider", "-p", default="offline",
              type=click.Choice(["ollama", "lmstudio", "openai", "chatgpt", "claude", "anthropic", "offline"],
                                case_sensitive=False),
              help="AI provider for the Oracle's profound inquiries.", show_default=True)
@click.option("--api-key", "-k", default=None, envvar=["OPENAI_API_KEY", "ANTHROPIC_API_KEY"],
              help="API key for cloud AI providers.", show_envvar=True)
@click.option("--base-url", "-u", default=None,
              help="Base URL for local AI providers (Ollama, LMStudio).")
@click.option("--model", "-m", default=None,
              help="AI model to use (provider-specific).")
@click.option("--skip-oracle", is_flag=True, default=False, hidden=True,
              help="Bypass the oracle (coward mode).")
@click.pass_context
def main(ctx: click.Context, provider: str, api_key: Optional[str],
         base_url: Optional[str], model: Optional[str], skip_oracle: bool) -> None:
    """
    \b
    redteamoracle — Agentic Red Team Framework
    The oracle will consult the dice before you do anything.

    Run a module:   redteamoracle run recon --target example.com
    List modules:   redteamoracle modules
    Oracle status:  redteamoracle status
    """
    print_banner()

    ctx.ensure_object(dict)
    ctx.obj["provider"] = provider
    ctx.obj["api_key"] = api_key
    ctx.obj["base_url"] = base_url
    ctx.obj["model"] = model
    ctx.obj["skip_oracle"] = skip_oracle

    # Show help if no subcommand given
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ---------------------------------------------------------------------------
# run command
# ---------------------------------------------------------------------------

@main.command("run")
@click.argument("module_name", metavar="MODULE")
@click.option("--target", "-t", required=True, help="Target host/domain/IP")
@click.option("--ports", default="top-100", show_default=True, help="Port range (for scan module)")
@click.option("--cve", default=None, help="Specific CVE to target (for exploit module)")
@click.pass_context
def run_module(ctx: click.Context, module_name: str, target: str, ports: str, cve: Optional[str]) -> None:
    """Run a pentest module against a target. (Subject to oracle approval.)"""
    obj = ctx.obj

    # Oracle check — runs every single time
    if not obj.get("skip_oracle"):
        ai = _resolve_provider(obj["provider"], obj["api_key"], obj["base_url"], obj["model"])
        console.print(f"[dim]Oracle AI: {ai.name}[/dim]")
        allowed = consult_oracle(ai)
        if not allowed:
            sys.exit(1)

    # Run the module
    module = get_module(module_name)
    if not module:
        console.print(f"[red]Unknown module: '{module_name}'[/red]")
        console.print("Run [bold]redteamoracle modules[/bold] to see available modules.")
        sys.exit(1)

    module.run(target=target, ports=ports, cve=cve)


# ---------------------------------------------------------------------------
# modules command
# ---------------------------------------------------------------------------

@main.command("modules")
def list_modules_cmd() -> None:
    """List all available pentest modules."""
    table = Table(
        title="Available Modules",
        box=box.ROUNDED,
        border_style="cyan",
        show_header=True,
    )
    table.add_column("Name", style="bold green", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Author", style="dim", justify="right")

    for mod in list_modules():
        table.add_row(mod.name, mod.description, mod.author)

    console.print(table)
    console.print(
        "\n[dim]Usage: redteamoracle run [MODULE] --target <host>[/dim]\n"
        "[dim]Note: The oracle will decide if you can actually run any of these.[/dim]\n"
    )


# ---------------------------------------------------------------------------
# status command
# ---------------------------------------------------------------------------

@main.command("status")
@click.pass_context
def status_cmd(ctx: click.Context) -> None:
    """Check oracle lockout status."""
    from redteamoracle.oracle import _is_locked_out, _load_state
    from datetime import datetime

    locked_until = _is_locked_out()
    state = _load_state()

    if locked_until:
        remaining = locked_until - datetime.now()
        hours, r = divmod(int(remaining.total_seconds()), 3600)
        minutes = r // 60
        console.print(
            Panel.fit(
                f"[bold red]🔒  LOCKED OUT[/bold red]\n\n"
                f"Remaining: [bold]{hours}h {minutes}m[/bold]\n"
                f"Expires:   {locked_until.strftime('%Y-%m-%d %H:%M:%S')}",
                border_style="red",
            )
        )
    else:
        console.print(
            Panel.fit(
                "[bold green]✅  STATUS: CLEAR[/bold green]\n\n"
                "[green]The oracle has not cursed you yet today.\n"
                "Run a module and find out if that changes.[/green]",
                border_style="green",
            )
        )


# ---------------------------------------------------------------------------
# oracle command (manual consultation)
# ---------------------------------------------------------------------------

@main.command("oracle")
@click.pass_context
def oracle_cmd(ctx: click.Context) -> None:
    """Manually consult the oracle without running a module."""
    obj = ctx.obj
    ai = _resolve_provider(obj["provider"], obj["api_key"], obj["base_url"], obj["model"])
    console.print(f"[dim]Oracle AI: {ai.name}[/dim]")
    allowed = consult_oracle(ai)
    if not allowed:
        sys.exit(1)
    else:
        console.print("[dim]You may proceed... if you can figure out what to do next.[/dim]")


# ---------------------------------------------------------------------------
# unlock command (escape hatch)
# ---------------------------------------------------------------------------

@main.command("unlock", hidden=True)
@click.option("--confirm", is_flag=True, required=True, help="Confirm you know what you're doing.")
def unlock_cmd(confirm: bool) -> None:
    """Clear the oracle lockout. (Shame on you.)"""
    _clear_lockout()
    console.print("[yellow]⚠  Lockout cleared. The oracle is disappointed in you.[/yellow]")


if __name__ == "__main__":
    main()
