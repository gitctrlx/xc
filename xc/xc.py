"""XC - A lightweight and versatile toolkit for Linux workflow.

This module serves as the main entry point for the XC CLI application.
It provides command-line interface functionality using Typer.
"""

from typing import Optional
import typer
from loguru import logger

from .utils.util import print_banner
from . import __version__

# Initialize Typer app with descriptive help text and disabled completion
app = typer.Typer(
    name="xc",
    help="A lightweight and versatile toolkit designed to simplify Linux workflows",
    add_completion=False,
)


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
