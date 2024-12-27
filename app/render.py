from collections import deque
from typing import Any, Self

from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    Task,
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.text import Text

from utils import log
from utils.terminal import terminal_width


class TimeColumn(ProgressColumn):
    """Helper class that combines both the time related columns `TimeElapsedColumn` & `TimeRemainingColumn` into a single formatted renderable
    """
    def render(self, task: Task) -> Text:
        """Function that renders time_remaining / time_elapsed for a given `task` of rich.Progress

        Args:
            task (Task): task instance of rich.progress

        Returns:
            Text: Time columns formatted into rich text object
        """
        elapsed = TimeElapsedColumn().render(task)
        remaining = TimeRemainingColumn().render(task)
        return Text(f"[{remaining}/{elapsed}]", style="cyan italic")


def progress_bar() -> Progress:
    """Function that generates a rich Progress instance with fixed template

    Returns:
        Progress: Progress bar instance
    """
    return Progress(
            SpinnerColumn(),
            BarColumn(),
            TaskProgressColumn(style="bold"),
            DownloadColumn(),
            TimeColumn(),
            TransferSpeedColumn(),
        )


class Render:
    """Class that actually renders the backup process in an eye-candy way using rich live rendering
    """
    def __init__(self) -> None:
        # File panel attributes
        self.max_line_length = terminal_width - 10
        self.panel_lines = 5
        self.panel_queue = deque([""]*self.panel_lines, maxlen=self.panel_lines)
        self.panel_processed = 0
        self.panel_total = 0
        # self.files_panel = Panel("", title=f"Files processed: {self.panel_processed} | Total: {self.panel_total}", title_align="left", height=self.panel_lines+2, width=terminal_width-5, padding=(0,1))
        self.files_panel = Panel("", title=f"Files processed: {self.panel_processed} | Total: {self.panel_total}", title_align="left", width=terminal_width-5, padding=(0,1))
        # Main progress bar
        self.main_progress_title = "Progress"
        self.main_progress_bar = progress_bar()
        # Alt progress bar
        self.alt_progress_title = ""
        self.alt_progress_bar = progress_bar()
        # Console Live object
        self.renders = [
            self.files_panel,
            Text(),
            self.main_progress_title,
            self.main_progress_bar,
            Text(),
            self.alt_progress_title,
            self.alt_progress_bar
        ]
        self.live = Live(Group(*self.renders), auto_refresh=True, refresh_per_second=10)
    
    def insert_into_files_panel(self, file: str, kind: str) -> None:
        """Function that insert an input `file`s string into files panel

        Args:
            file (str): input file string
        """
        # reset encoding to avoid terminal glitches
        file = file.encode("ascii", errors="replace").decode("ascii")
        match(kind):
            case "add":
                ind = "[bold bright_green]▲[/]"
            case "modify":
                ind = "[bold yellow1]►[/]"
            case "remove":
                ind = "[bold bright_red]▼[/]"
            case _:
                ind = "[bold bright_blue]◄[/]"
        # insert file string into queue
        self.panel_queue.append(f"{ind} {file}")
        # update the panel render
        self.files_panel.renderable = "\n".join(self.panel_queue)

    def update_files_panel_title(self, current: int = 0):
        """Function used to update files panel title, processed by total count display

        Args:
            current (int, optional): total files processed. Defaults to 0.
        """
        self.panel_processed = current
        self.files_panel.title = f"[bold]Files processed: [cyan]{current}[/cyan] | Total: [cyan]{self.panel_total}[/cyan]"

    def update_alt_progress_title(self, file: str = "") -> None:
        """Function that updates the alt progress bar title with input `file` name. If no input is given function resets the title to be blank.

        Args:
            file (str, optional): Input file name. Defaults to "".
        """
        # update the variable first
        self.alt_progress_title = file
        # update the renders list
        self.renders[5] = self.alt_progress_title
        # update the live render
        self.live.update(Group(*self.renders))
    
    def __enter__(self) -> Self:
        """Function to use render class with context. Starts the rich.live rendering

        Returns:
            Self: return `self`
        """
        self.live.start()
        return self

    def __exit__(self, exc_type: type, exc_val: Any, exc_tb: Any) -> None:
        """Function to use the render class with content. Stops the rich.live rendering and prints a log message if context is closed due to exception.

        Args:
            exc_type (_type_): exception type
            exc_val (_type_): exception message
            exc_tb (_type_): exception traceback
        """
        self.live.stop()
        if exc_tb:
            log.error(f"{exc_type.__name__} {exc_val}")
            