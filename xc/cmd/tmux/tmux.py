import libtmux
from libtmux.exc import (
    TmuxSessionExists,
    TmuxCommandNotFound,
    LibTmuxException,
    TmuxObjectDoesNotExist,
    BadSessionName,
)
from libtmux._internal.query_list import ObjectDoesNotExist
from rich.table import Table
from rich.console import Console
import typer
from typing import Optional
from xc.utils.util import is_windows_os

# Initialize core objects
console = Console()
server: Optional[libtmux.Server] = None
if not is_windows_os():
    try:
        server = libtmux.Server()
    except TmuxCommandNotFound:
        typer.secho("TMux is not installed on this system", fg=typer.colors.RED)
        raise SystemExit(1)
    except LibTmuxException as e:
        typer.secho(f"Failed to connect to TMux server: {str(e)}", fg=typer.colors.RED)
        raise SystemExit(1)

tmux_app = typer.Typer(help="TMux session management commands", no_args_is_help=True)


@tmux_app.command("ls")
def list_sessions() -> None:
    """Lists all tmux sessions and their details.

    Displays a formatted table showing:
    - Session name
    - Number of windows
    - Creation timestamp
    - Attachment status (✓/✗)

    Raises:
        LibTmuxException: If there is an error accessing or listing the sessions.
    """
    if is_windows_os():
        typer.secho("TMux is not supported on Windows", fg=typer.colors.RED)
        return

    try:
        table = Table(title="TMux Sessions")
        table.add_column("Session Name", style="cyan")
        table.add_column("Windows", justify="right")
        table.add_column("Created At", style="green")
        table.add_column("Attached", justify="center")

        if server is not None:
            for session in server.sessions:
                # Check if session is attached by looking at attached flag
                is_attached = session.get("session_attached") == "1"
                table.add_row(
                    session.name,
                    str(len(session.windows)),
                    session.get("session_created"),
                    "✓" if is_attached else "✗",
                )
        typer.echo()
        console.print(table)
        typer.echo()
    except LibTmuxException as e:
        typer.secho(f"Error listing sessions: {str(e)}", fg=typer.colors.RED)


@tmux_app.command(name="new")
def new(
    name: str = typer.Argument(..., help="Name of the new session"),
) -> None:
    """Creates a new tmux session.

    Args:
        name: The name for the new session. Must be unique.

    Raises:
        TmuxSessionExists: If a session with the given name exists.
        BadSessionName: If the session name is invalid.
        LibTmuxException: If session creation fails for any other reason.
    """
    if is_windows_os():
        typer.secho("TMux is not supported on Windows", fg=typer.colors.RED)
        return

    try:
        # Create new session
        if server is not None:
            session = server.new_session(
                session_name=name,
                attach=False,
            )
            typer.secho(f"Created new session: {session.name}", fg=typer.colors.GREEN)
            typer.echo()
    except TmuxSessionExists:
        typer.secho(f"Session '{name}' already exists", fg=typer.colors.RED)
    except BadSessionName as e:
        typer.secho(str(e), fg=typer.colors.RED)
    except LibTmuxException as e:
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
        TmuxObjectDoesNotExist: If the specified session does not exist.
        LibTmuxException: If the session cannot be killed.
    """
    if is_windows_os():
        typer.secho("TMux is not supported on Windows", fg=typer.colors.RED)
        return

    try:
        if server is not None:
            session = server.sessions.get(session_name=name)
            if not session:
                typer.secho(f"Session '{name}' does not exist", fg=typer.colors.RED)
                return

            if not force and not typer.confirm(
                f"Are you sure you want to kill session '{name}'?"
            ):
                return

            session.kill_session()
            typer.secho(f"Killed session: {name}", fg=typer.colors.GREEN)
            typer.echo()
    except (TmuxObjectDoesNotExist, ObjectDoesNotExist):
        typer.secho(f"Could not find session '{name}'", fg=typer.colors.RED)
    except LibTmuxException as e:
        typer.secho(f"Error killing session: {str(e)}", fg=typer.colors.RED)


@tmux_app.command(name="attach")
def attach(
    name: str = typer.Argument(..., help="Name of the session to attach"),
) -> None:
    """Attaches the terminal to an existing tmux session.

    Args:
        name: Name of the session to attach to. Must exist.

    Raises:
        TmuxObjectDoesNotExist: If the specified session does not exist.
        LibTmuxException: If the session cannot be attached to.
    """
    if is_windows_os():
        typer.secho("TMux is not supported on Windows", fg=typer.colors.RED)
        return

    try:
        if server is not None:
            session = server.sessions.get(session_name=name)
            if not session:
                typer.secho(f"Session '{name}' does not exist", fg=typer.colors.RED)
                return

            session.attach_session()
    except (TmuxObjectDoesNotExist, ObjectDoesNotExist):
        typer.secho(f"Could not find session '{name}'", fg=typer.colors.RED)
    except LibTmuxException as e:
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
        TmuxObjectDoesNotExist: If the specified session does not exist.
        TmuxSessionExists: If a session with new_name already exists.
        BadSessionName: If the new session name is invalid.
        LibTmuxException: If the session cannot be renamed.
    """
    if is_windows_os():
        typer.secho("TMux is not supported on Windows", fg=typer.colors.RED)
        return

    try:
        if server is not None:
            session = server.sessions.get(session_name=old_name)
            if not session:
                typer.secho(f"Session '{old_name}' does not exist", fg=typer.colors.RED)
                return

            session.rename_session(new_name)
            typer.secho(
                f"Renamed session from '{old_name}' to '{new_name}'",
                fg=typer.colors.GREEN,
            )
            typer.echo()
    except (TmuxObjectDoesNotExist, ObjectDoesNotExist):
        typer.secho(f"Could not find session '{old_name}'", fg=typer.colors.RED)
    except TmuxSessionExists:
        msg = f"Session '{new_name}' already exists"
        typer.secho(msg, fg=typer.colors.RED)
    except BadSessionName as e:
        typer.secho(str(e), fg=typer.colors.RED)
    except LibTmuxException as e:
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
        TmuxObjectDoesNotExist: If the specified session does not exist.
        LibTmuxException: If windows cannot be listed.
    """
    if is_windows_os():
        typer.secho("TMux is not supported on Windows", fg=typer.colors.RED)
        return

    try:
        if server is not None:
            session = server.sessions.get(session_name=session_name)
            if not session:
                typer.secho(
                    f"Session '{session_name}' does not exist", fg=typer.colors.RED
                )
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
            console.print(table)
            typer.echo()
    except (TmuxObjectDoesNotExist, ObjectDoesNotExist):
        typer.secho(f"Could not find session '{session_name}'", fg=typer.colors.RED)
    except LibTmuxException as e:
        typer.secho(f"Error listing windows: {str(e)}", fg=typer.colors.RED)
