from os import get_terminal_size
from sys import stdout
from typing import Any

from colorama import Style


def colorize(data: str|Any, color: str, bright: bool = True) -> str:
    """Wrapper function to colorize a given `data` string to Fore.color

    Args:
        data (str): Input string to color
        color (str): Any Fore.color
        bright (bool, optional): Flag that sets Style BRIGHT. Defaults to True.

    Returns:
        str: data with colorama styling
    """
    return f"{color}{Style.BRIGHT if bright else ""}{data}{Style.RESET_ALL}"

def write_out(ascii: str) -> None:
    """Function that writes and flushes ascii codes to terminal

    Args:
        ascii (str): Ascii string
    """
    stdout.write(ascii)
    stdout.flush()


def clear_line() -> None:
    """Function that clears the current line
    """
    write_out("\033[K")


def previous_line() -> None:
    """Function that jumps the cursor to previous line
    """
    write_out("\033[F")


def clear_previous_lines(n: int = 1) -> None:
    """Wrapper function that clears `n` previous lines

    Args:
        n (int, optional): Number of previous lines to be cleared. Defaults to 1.
    """
    for i in range(n):
        previous_line()
        clear_line()


def clear_screen() -> None:
    """Function that clears the entire screen
    """
    write_out("\033c")


try:
    terminal_width = get_terminal_size().columns
    clear_screen()
except OSError:
    ...