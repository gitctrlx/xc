import libtmux
from rich.console import Console

# Initialize core objects
console = Console()
try:
    server = libtmux.Server()
except Exception as e:
    console.print(f"Error connecting to tmux server: {str(e)}", style="red")
    exit(1)


def new(name: str):
    # Create new session
    session = server.new_session(session_name=name, attach=False)
    console.print(f"Created new session: {session.name}", style="green")


if __name__ == "__main__":
    # Example usage
    new("my-session")
