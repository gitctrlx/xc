import os
from typing import Optional
import typer
from rich.table import Table
from rich.console import Console

from xc.utils import is_windows_os

# Initialize rich console and proxy command ap
console = Console()
proxy_app = typer.Typer(
    help="Proxy configuration management commands", no_args_is_help=True
)

# Default proxy configuration
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7890


def _get_proxy_commands(proxy_url: Optional[str] = None, unset: bool = False) -> str:
    """Get shell commands for setting/unsetting proxy based on OS.

    Args:
        proxy_url: The proxy server URL to configure (for set commands)
        unset: Whether to return unset commands

    Returns:
        str: Shell commands for proxy configuration
    """
    if is_windows_os():
        if unset:
            return """$env:http_proxy = ""; $env:https_proxy = "" """
        return f"""$env:http_proxy = "{proxy_url}"; $env:https_proxy = "{proxy_url}" """
    else:
        if unset:
            return """unset http_proxy https_proxy"""
        return f"""export http_proxy="{proxy_url}" https_proxy="{proxy_url}" """


@proxy_app.command()
def set(
    host: str = typer.Option(DEFAULT_HOST, "--host", "-h", help="Proxy host address"),
    port: int = typer.Option(DEFAULT_PORT, "--port", "-p", help="Proxy port number"),
) -> None:
    """Show commands for configuring system-wide proxy settings.

    Displays appropriate commands for setting proxy configuration based on the
    current operating system. Uses default host (127.0.0.1) and port (7890) if not specified.

    Args:
        host: The proxy server host address
        port: The proxy server port number
    """
    proxy_url = f"http://{host}:{port}"
    os_type = "Windows" if is_windows_os() else "Unix"

    typer.secho(f"\nProxy Configuration Commands ({os_type}):", fg=typer.colors.CYAN)
    typer.secho(_get_proxy_commands(proxy_url), fg=typer.colors.GREEN)
    typer.echo()


@proxy_app.command()
def unset() -> None:
    """Show commands for removing system-wide proxy configuration.

    Displays appropriate commands for removing proxy configuration based on the
    current operating system.
    """
    os_type = "Windows" if is_windows_os() else "Unix"

    typer.secho(f"\nProxy Removal Commands ({os_type}):", fg=typer.colors.CYAN)
    typer.secho(_get_proxy_commands(unset=True), fg=typer.colors.YELLOW)
    typer.echo()


@proxy_app.command()
def show() -> None:
    """Display current proxy configuration.

    Shows a formatted table of all proxy-related environment variables
    and their current values.
    """
    proxy_vars = ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]

    table = Table(title="System Proxy Configuration")
    table.add_column("Variable", style="cyan")
    table.add_column("Value", style="green")

    for var in proxy_vars:
        value = os.environ.get(var, "")
        status = value if value else "not configured"
        table.add_row(var, status)

    typer.echo()
    console.print(table)
    typer.echo()
