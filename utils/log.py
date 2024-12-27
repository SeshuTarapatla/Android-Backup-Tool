from colorama import Fore, Style

from utils import terminal


def log(prefix: str, suffix: str, prefix_color: str, prefix_bold: bool, end: str) -> None:
    """Funtion that prints a log message

    Args:
        prefix (str): Log level as prefix
        suffix (str): Log message as suffix
        prefix_color (str): Color of the prefix [use colorama]
        prefix_bold (bool): Bool that sets the prefix to be BRIGHT
        end (str): Line ending for print function
    """
    print(f"{prefix_color}{Style.BRIGHT if prefix_bold else ''}{prefix}{Style.RESET_ALL}: {suffix}", end=end, flush=True)


def info(message: str, success_log: bool = False) -> None:
    """Wrapper function for INFO log

    Args:
        message (str): Info message
        success_log (bool, optional): Bool that changes prefix color to green. Defaults to False.
    """
    kwargs = {
        "prefix": "INFO",
        "suffix": message,
        "prefix_color": Fore.GREEN if success_log else Fore.BLUE,
        "prefix_bold": True,
        "end": "\n"
    }
    log(**kwargs)


def error(message: str | Exception) -> None:
    """Wrapper function for ERROR log

    Args:
        message (str): Error message

    Raises:
        SystemExit: Kills the application after logging
    """
    kwargs = {
        "prefix": "ERROR",
        "suffix": message,
        "prefix_color": Fore.RED,
        "prefix_bold": True,
        "end": "\n"
    }
    log(**kwargs)
    raise SystemExit()


def update(message: str | Exception, task_success: bool = True) -> None:
    """Function that updates the previous log based on task success or not

    Args:
        message (str): Log message or Exception
        task_success (bool): Bool that decides to call INFO or ERROR based on task status
    """
    terminal.clear_previous_lines(1)
    info(str(message), success_log=True) if task_success else error(message)


def stage(title: str) -> None:
    """Helper function to print Stage title with line separation

    Args:
        title (str): Stage title
    """
    print()
    info(f"STAGE: {title}")
