"""TMux session management commands for XC toolkit.

This module provides a command-line interface for managing tmux sessions using the libtmux library.
It includes commands for listing, creating, killing, attaching to, and renaming tmux sessions,
as well as listing windows within sessions.

Typical usage example:

    # List all tmux sessions
    xc tmux ls

    # Create a new session
    xc tmux new my-session

    # Kill a session
    xc tmux kill my-session

    # Attach to a session
    xc tmux attach my-session
"""

from typing import Optional
import libtmux
from rich.table import Table
import typer
from loguru import logger

# Initialize tmux server
server = libtmux.Server()

# Create tmux command app
tmux_app = typer.Typer(help="TMux session management commands", no_args_is_help=True)


@tmux_app.command("ls")
def list_sessions() -> None:
    """Lists all tmux sessions with their details.

    Displays a table showing session name, number of windows, creation time,
    and attachment status for each tmux session.

    Raises:
        Exception: If there is an error listing the sessions.
    """
    try:
        table = Table(title="TMux Sessions")
        table.add_column("Session Name", style="cyan")
        table.add_column("Windows", justify="right")
        table.add_column("Created At", style="green")
        table.add_column("Attached", justify="center")

        for session in server.list_sessions():
            table.add_row(
                session.name,
                str(len(session.windows)),
                session.get("session_created"),
                "✓" if session.attached else "✗",
            )
        typer.echo()
        typer.echo(table)
        typer.echo()
    except Exception as e:
        logger.error(f"Failed to list sessions: {str(e)}")
        typer.secho(f"Error listing sessions: {str(e)}", fg=typer.colors.RED)


@tmux_app.command()
def new(
    name: str = typer.Argument(..., help="Name of the new session"),
    window_name: Optional[str] = typer.Option(
        None, "--window", "-w", help="Name of the initial window"
    ),
    start_directory: Optional[str] = typer.Option(
        None, "--directory", "-d", help="Starting directory"
    ),
) -> None:
    """Creates a new tmux session with optional window name and start directory.

    Args:
        name: The name for the new session.
        window_name: Optional name for the initial window.
        start_directory: Optional starting directory path.

    Raises:
        libtmux.exc.TmuxSessionExists: If a session with the given name already exists.
        Exception: If there is an error creating the session.
    """
    try:
        session = server.new_session(
            session_name=name, window_name=window_name, start_directory=start_directory
        )
        logger.info(f"Created new session: {session.name}")
        typer.secho(f"Created new session: {session.name}", fg=typer.colors.GREEN)
    except libtmux.exc.TmuxSessionExists:
        logger.warning(f"Session '{name}' already exists")
        typer.secho(f"Session '{name}' already exists", fg=typer.colors.RED)
    except Exception as e:
        logger.error(f"Failed to create session: {str(e)}")
        typer.secho(f"Error creating session: {str(e)}", fg=typer.colors.RED)


@tmux_app.command()
def kill(
    name: str = typer.Argument(..., help="Name of the session to kill"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force kill without confirmation"
    ),
) -> None:
    """Kills a tmux session with optional force flag.

    Args:
        name: The name of the session to kill.
        force: If True, kills without confirmation prompt.

    Raises:
        Exception: If there is an error killing the session.
    """
    try:
        session = server.find_where({"session_name": name})
        if not session:
            logger.warning(f"Session '{name}' not found")
            typer.secho(f"Session '{name}' not found", fg=typer.colors.RED)
            return

        if not force and not typer.confirm(
            f"Are you sure you want to kill session '{name}'?"
        ):
            return

        session.kill_session()
        logger.info(f"Killed session: {name}")
        typer.secho(f"Killed session: {name}", fg=typer.colors.GREEN)
    except Exception as e:
        logger.error(f"Failed to kill session: {str(e)}")
        typer.secho(f"Error killing session: {str(e)}", fg=typer.colors.RED)


@tmux_app.command()
def attach(
    name: str = typer.Argument(..., help="Name of the session to attach"),
) -> None:
    """Attaches to an existing tmux session.

    Args:
        name: The name of the session to attach to.

    Raises:
        Exception: If there is an error attaching to the session.
    """
    try:
        session = server.find_where({"session_name": name})
        if not session:
            logger.warning(f"Session '{name}' not found")
            typer.secho(f"Session '{name}' not found", fg=typer.colors.RED)
            return

        session.attach_session()
        logger.info(f"Attached to session: {name}")
    except Exception as e:
        logger.error(f"Failed to attach to session: {str(e)}")
        typer.secho(f"Error attaching to session: {str(e)}", fg=typer.colors.RED)


@tmux_app.command()
def rename(
    old_name: str = typer.Argument(..., help="Current session name"),
    new_name: str = typer.Argument(..., help="New session name"),
) -> None:
    """Renames an existing tmux session.

    Args:
        old_name: The current name of the session.
        new_name: The new name to give the session.

    Raises:
        Exception: If there is an error renaming the session.
    """
    try:
        session = server.find_where({"session_name": old_name})
        if not session:
            logger.warning(f"Session '{old_name}' not found")
            typer.secho(f"Session '{old_name}' not found", fg=typer.colors.RED)
            return

        session.rename_session(new_name)
        logger.info(f"Renamed session from '{old_name}' to '{new_name}'")
        typer.secho(
            f"Renamed session from '{old_name}' to '{new_name}'", fg=typer.colors.GREEN
        )
    except Exception as e:
        logger.error(f"Failed to rename session: {str(e)}")
        typer.secho(f"Error renaming session: {str(e)}", fg=typer.colors.RED)


@tmux_app.command()
def windows(
    session_name: str = typer.Argument(..., help="Name of the session"),
) -> None:
    """Lists all windows in a tmux session.

    Displays a table showing window ID, name and active status for each window
    in the specified session.

    Args:
        session_name: The name of the session to list windows for.

    Raises:
        Exception: If there is an error listing the windows.
    """
    try:
        session = server.find_where({"session_name": session_name})
        if not session:
            logger.warning(f"Session '{session_name}' not found")
            typer.secho(f"Session '{session_name}' not found", fg=typer.colors.RED)
            return

        table = Table(title=f"Windows in Session: {session_name}")
        table.add_column("Window ID", style="cyan", justify="right")
        table.add_column("Name", style="green")
        table.add_column("Active", justify="center")

        for window in session.windows:
            table.add_row(
                str(window.index),
                window.name,
                "✓" if window.get("window_active") == "1" else "✗",
            )
        typer.echo()
        typer.echo(table)
        typer.echo()
    except Exception as e:
        logger.error(f"Failed to list windows: {str(e)}")
        typer.secho(f"Error listing windows: {str(e)}", fg=typer.colors.RED)
