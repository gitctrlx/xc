"""XC - A lightweight and versatile toolkit for Linux workflow.

This module serves as the main entry point for the XC CLI application.
It provides command-line interface functionality using Typer.
"""

from typing import Optional
import typer
from loguru import logger

from . import __version__

from .utils import print_banner

from .cmd.tmux import tmux_app
from .cmd.proxy import proxy_app

# Initialize Typer app with descriptive help text and disabled completion
app = typer.Typer(
    name="xc",
    help="A lightweight and versatile toolkit designed to simplify Linux workflows",
    add_completion=False,
)

# Add tmux commands as a sub-command group
app.add_typer(tmux_app, name="tmux", help="TMux session management commands")

# Add proxy commands as a sub-command group
app.add_typer(proxy_app, name="proxy", help="Proxy configuration management commands")


def version_callback(value: bool) -> None:
    """Handle the --version flag by displaying version information.

    Args:
        value (bool): Flag indicating whether version info should be shown

    Raises:
        typer.Exit: Exits the application after displaying version
    """
    if value:
        print_banner()
        logger.info(f"XC Version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version information and exit",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """XC CLI main entry point.

    A lightweight and versatile toolkit designed to simplify and enhance Linux workflows
    with powerful utilities and automation capabilities.

    Args:
        version: Optional flag to display version information
    """
    pass


if __name__ == "__main__":
    app()
