"""TMux session management commands for XC toolkit.

This module provides a command-line interface for managing tmux sessions using the libtmux library.
It allows users to:
- List existing sessions and their details
- Create new sessions with custom names and options
- Kill existing sessions
- Attach to running sessions
- Rename sessions
- List windows within sessions

Example usage:
    # List all sessions
    xc tmux ls
    xc tmux l

    # Create new session
    xc tmux new my-session
    xc tmux n my-session

    # Kill session
    xc tmux kill my-session
    xc tmux k my-session

    # Attach to session
    xc tmux attach my-session
    xc tmux a my-session
"""

from typing import Optional
import libtmux
from rich.table import Table
from rich.console import Console
import typer
from loguru import logger

# Initialize core objects
console = Console()
server = libtmux.Server()
tmux_app = typer.Typer(help="TMux session management commands", no_args_is_help=True)


@tmux_app.command("ls")
def list_sessions() -> None:
    """Lists all tmux sessions and their details.

    Displays a formatted table containing:
    - Session name
    - Number of windows
    - Creation timestamp
    - Attachment status (✓/✗)

    Raises:
        Exception: If there is an error accessing or listing the sessions.
    """
    try:
        table = Table(title="TMux Sessions")
        table.add_column("Session Name", style="cyan")
        table.add_column("Windows", justify="right")
        table.add_column("Created At", style="green")
        table.add_column("Attached", justify="center")

        for session in server.sessions:
            # Check if session is attached by looking at attached flag
            is_attached = session.get("session_attached") == "1"
            table.add_row(
                session.name,
                str(len(session.windows)),
                session.get("session_created"),
                "✓" if is_attached else "✗",
            )
        console.print(table)
    except Exception as e:
        logger.error(f"Failed to list sessions: {str(e)}")
        typer.secho(f"Error listing sessions: {str(e)}", fg=typer.colors.RED)


@tmux_app.command(name="new")
def new(
    name: str = typer.Argument(..., help="Name of the new session"),
    window_name: Optional[str] = typer.Option(
        None, "--window", "-w", help="Name of the initial window"
    ),
    start_directory: Optional[str] = typer.Option(
        None, "--directory", "-d", help="Starting directory"
    ),
) -> None:
    """Creates a new tmux session with the specified configuration.

    Args:
        name: The name for the new session. Must be unique.
        window_name: Optional name for the initial window in the session.
        start_directory: Optional working directory path for the new session.

    Raises:
        libtmux.exc.TmuxSessionExists: If a session with the given name exists.
        Exception: If session creation fails for any other reason.
    """
    try:
        # Check if session already exists
        if server.sessions.get(session_name=name):
            logger.warning(f"Session '{name}' already exists")
            typer.secho(f"Session '{name}' already exists", fg=typer.colors.RED)
            return

        # Create new session
        session = server.new_session(
            session_name=name,
            window_name=window_name,
            start_directory=start_directory,
            attach=False,
        )
        logger.info(f"Created new session: {session.name}")
        typer.secho(f"Created new session: {session.name}", fg=typer.colors.GREEN)
    except Exception as e:
        logger.error(f"Failed to create session: {str(e)}")
        typer.secho(f"Error creating session: {str(e)}", fg=typer.colors.RED)


@tmux_app.command(name="kill")
def kill(
    name: str = typer.Argument(..., help="Name of the session to kill"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force kill without confirmation"
    ),
) -> None:
    """Terminates a tmux session.

    Args:
        name: Name of the session to terminate.
        force: If True, kills the session without asking for confirmation.
            If False, prompts for confirmation before killing.

    Raises:
        Exception: If the session cannot be found or killed.
    """
    try:
        session = server.sessions.get(session_name=name)
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


@tmux_app.command(name="attach")
def attach(
    name: str = typer.Argument(..., help="Name of the session to attach"),
) -> None:
    """Attaches the terminal to an existing tmux session.

    Args:
        name: Name of the session to attach to. Must exist.

    Raises:
        Exception: If the session cannot be found or attached to.
    """
    try:
        session = server.sessions.get(session_name=name)
        if not session:
            logger.warning(f"Session '{name}' not found")
            typer.secho(f"Session '{name}' not found", fg=typer.colors.RED)
            return

        session.attach_session()
        logger.info(f"Attached to session: {name}")
    except Exception as e:
        logger.error(f"Failed to attach to session: {str(e)}")
        typer.secho(f"Error attaching to session: {str(e)}", fg=typer.colors.RED)


@tmux_app.command(name="rename")
def rename(
    old_name: str = typer.Argument(..., help="Current session name"),
    new_name: str = typer.Argument(..., help="New session name"),
) -> None:
    """Renames an existing tmux session.

    Args:
        old_name: Current name of the session to rename.
        new_name: New name to assign to the session.

    Raises:
        Exception: If the session cannot be found or renamed.
    """
    try:
        session = server.sessions.get(session_name=old_name)
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


@tmux_app.command(name="windows")
def windows(
    session_name: str = typer.Argument(..., help="Name of the session"),
) -> None:
    """Lists all windows in a tmux session.

    Displays a formatted table containing:
    - Window ID
    - Window name
    - Active status (✓/✗)

    Args:
        session_name: Name of the session to list windows for.

    Raises:
        Exception: If the session cannot be found or windows cannot be listed.
    """
    try:
        session = server.sessions.get(session_name=session_name)
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
        console.print(table)
    except Exception as e:
        logger.error(f"Failed to list windows: {str(e)}")
        typer.secho(f"Error listing windows: {str(e)}", fg=typer.colors.RED)
