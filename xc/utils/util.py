from importlib.util import find_spec
import os
import platform
import subprocess
import sys
import ensurepip
from typing import Dict, List, Optional, Tuple
from art import tprint
from loguru import logger


def is_windows_os() -> bool:
    """Determine if current operating system is Windows.

    Returns:
        bool: True if Windows, False otherwise
    """
    return platform.system().lower() == "windows"


def is_linux_os() -> bool:
    """Determine if current operating system is Linux.

    Returns:
        bool: True if Linux, False otherwise
    """
    return platform.system().lower() == "linux"


def is_macos_os() -> bool:
    """Determine if current operating system is macOS.

    Returns:
        bool: True if macOS, False otherwise
    """
    return platform.system().lower() == "darwin"


def print_banner():
    """Print stylized Quanta banner using ASCII art.

    Uses the art library's tprint function with the alpha font to create
    an ASCII art banner displaying "Quanta".
    """
    tprint("XC", font="alpha")


def check_and_install_package(
    package_name: str, package_url: Optional[str] = None
) -> Tuple[bool, str]:
    """Check if a Python package is installed and install if needed.

    Args:
        package_name (str): Name of the package to check/install
        package_url (Optional[str], optional): URL or path to the package to install.
            If empty, install from PyPI. Defaults to None.

    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True if installation successful, False otherwise
            - str: Status message describing the result
    """
    if not package_name:
        return False, "Package name cannot be empty"

    # Check if package is already installed
    if find_spec(package_name) is not None:
        return True, f"{package_name} package is already installed"

    logger.warning(f"{package_name} package is not installed, attempting to install...")

    try:
        # Ensure pip is available and up to date
        ensurepip.bootstrap(upgrade=True)

        # Determine install source
        install_target = package_url if package_url is not None else package_name
        source = "from " + (package_url if package_url is not None else "PyPI")

        # Install package using pip
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", install_target],
            stderr=subprocess.PIPE,
        )

        # Verify installation was successful
        if find_spec(package_name) is not None:
            return True, f"Successfully installed {package_name} package {source}"
        else:
            return False, f"Package installation completed but {package_name} not found"

    except subprocess.CalledProcessError as e:
        return False, f"Failed to install {package_name} package {source}: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error installing {package_name}: {str(e)}"


def check_env_vars(required_vars: List[str]) -> Tuple[bool, Dict[str, str], str]:
    """
    Check required environment variables.

    Args:
        required_vars (List[str]): List of environment variable names to check.

    Returns:
        Tuple containing:
        - Boolean indicating if all required vars are present
        - Dict of environment variables
        - Success/error message
    """
    if not required_vars:
        return True, {}, "No environment variables required"

    env_vars: Dict[str, str] = {}
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if value is None:
            missing_vars.append(var)
        else:
            env_vars[var] = value

    if missing_vars:
        return (
            False,
            env_vars,
            f"Missing required environment variables: {', '.join(missing_vars)}",
        )

    return True, env_vars, "All required environment variables are present"


def print_tmux_shortcuts():
    """
    Display a comprehensive guide of TMux keyboard shortcuts and commands.

    This function prints a well-formatted list of commonly used TMux shortcuts,
    organized by functional categories including session management, window
    operations, pane controls, and copy mode functionality.
    """
    shortcuts = {
        "Session Management": {
            "tmux new -s <name>": "Create a new named TMux session",
            "tmux ls": "List all active TMux sessions",
            "tmux attach -t <name>": "Attach to an existing session by name",
            "tmux kill-session -t <name>": "Terminate a specific session",
            "prefix + d": "Detach from the current session",
            "tmux kill-server": "Terminate TMux server and all sessions",
        },
        "Window Management": {
            "prefix + c": "Create a new window",
            "prefix + w": "Display interactive window list",
            "prefix + n": "Move to next window",
            "prefix + p": "Move to previous window",
            "prefix + <number>": "Switch to window by index number",
            "prefix + &": "Kill the current window",
            "prefix + ,": "Rename current window",
            "prefix + .": "Move window to different index",
        },
        "Pane Management": {
            "prefix + %": "Split current pane vertically",
            'prefix + "': "Split current pane horizontally",
            "prefix + o": "Rotate through panes",
            "prefix + ;": "Toggle between last active panes",
            "prefix + x": "Kill current pane",
            "prefix + z": "Toggle pane zoom/fullscreen",
            "prefix + <arrow>": "Switch focus to pane in direction",
            "prefix + {": "Swap current pane with previous",
            "prefix + }": "Swap current pane with next",
        },
        "Copy Mode (vi mode)": {
            "prefix + [": "Enter copy mode",
            "prefix + ]": "Paste from buffer",
            "space": "Start selection",
            "enter": "Copy selected text",
            "q": "Exit copy mode",
            "?": "Search backward",
            "/": "Search forward",
            "n": "Next search match",
            "N": "Previous search match",
        },
    }

    print("\nTMux Command Reference (default prefix: Ctrl+b)")
    print("=" * 50)

    for category, items in shortcuts.items():
        print(f"\n{category}")
        print("-" * len(category))
        for key, description in items.items():
            # Align commands and descriptions for better readability
            print(f"{key:<30} : {description}")
