from pathlib import Path
from shutil import copy2, move
from subprocess import run
from typing import NamedTuple

from colorama import Fore
from pandas import DataFrame, concat, read_csv
from send2trash import send2trash

from app.vars import (
    BACKUP_DIR,
    BACKUP_ROOT,
    CLEANED_METADATA,
    DATA_DIR,
    DATAFRAME,
    DELTA_COLUMNS,
    DELTA_DATAFRAME,
    DELTA_DIR,
    DEVICE_DATAFRAME,
    MYPASS,
    RAR_EXECUTABLE,
    RAW_METADATA,
    TIMESTAMP,
)
from utils import UTF_8_SIG, log
from utils.android import DEVICE_MODEL
from utils.terminal import colorize, previous_line


class DeltaNamedTuple(NamedTuple):
    """A named tuple to enable typing hints for Deltaframe itertuples.
    """
    Index: int
    File: str
    Type: str
    Size: int
    Size_old: int
    Date: str
    Date_old: str
    Path: str
    Kind: str

    
def calculate() -> None:
    """Function to calculate the delta between current backup and existing backup to perform minimal operations
    """
    # Separate stage to calculate delta
    log.stage("Delta")
    log.info("Calculating Delta for minimal operations")
    # variables
    src_file = DATAFRAME
    dst_file = DELTA_DATAFRAME
    cmp_file = DEVICE_DATAFRAME
    # read both dataframes
    current_df = read_csv(src_file, encoding=UTF_8_SIG)
    if cmp_file.exists():
        backed_up_df = read_csv(cmp_file, encoding=UTF_8_SIG)
    else:
        backed_up_df = DataFrame(columns=current_df.columns)
    # calculate delta as additions, deletions and modifications
    additions = current_df[~current_df["Path"].isin(backed_up_df["Path"])].copy()
    deletions = backed_up_df[~backed_up_df["Path"].isin(current_df["Path"])].copy()
    merged = current_df.merge(backed_up_df, on="Path", suffixes=("", "_old"))
    modifications = merged[(merged['Size'] != merged['Size_old']) | (merged['Date'] != merged['Date_old'])].copy()
    # add operation tag as kind
    additions["Kind"] = "add"
    deletions["Kind"] = "remove"
    modifications['Kind'] = "modify"
    # concat into single delta frame and save
    delta_df = concat([additions, deletions, modifications])[DELTA_COLUMNS]
    delta_df.to_csv(dst_file, index=False, encoding=UTF_8_SIG)
    log.info(f"Delta DataFrame saved as   > {dst_file}")
    # print stats
    log.info(
        f"Total operations:          > "
        f"{colorize(len(delta_df), Fore.BLUE)} ["
        f"{colorize(f"+{len(additions)}", Fore.GREEN)}, "
        f"{colorize(f"~{len(modifications)}", Fore.YELLOW)}, "
        f"{colorize(f"-{len(deletions)}", Fore.RED)}]"
    )
    
def size() -> int:
    """Function that calculates the size of delta backup. Used to determine whether the delta is big enough to archive and merge with main backup dir or not.

    Returns:
        int: Size of delta dir
    """
    # Recursively calculate the size of DELTA_DIR
    total_delta_size = sum([file.stat().st_size for file in DELTA_DIR.rglob("*") if file.is_file()])
    return total_delta_size

def archive() -> None:
    """Function that creates password protected rar archives of 1GB each for online backup.
    """
    # Copying Dataframes into delta dir
    previous_line()
    # skip if rar exe is not available
    if not RAR_EXECUTABLE.exists():
        return
    copy2(DATAFRAME, BACKUP_ROOT/f"dataframe-{TIMESTAMP}.csv")
    copy2(DELTA_DATAFRAME, BACKUP_ROOT/f"deltaframe-{TIMESTAMP}.csv")
    cleanup()
    # current date as time stamp for delta archives
    rar_name = f"{DEVICE_MODEL}-{TIMESTAMP}.rar"
    rar_path = BACKUP_ROOT/rar_name
    # Subprocess args with all required flags to create rar archives
    args = [RAR_EXECUTABLE, "a", "-m0", "-v1024m", f"-hp{MYPASS}", "-ep1", rar_path, DELTA_DIR]
    log.info(f"Archiving delta for online backup | Timestamp: {TIMESTAMP}")
    resp = run(args, shell=True)
    if resp.returncode != 0:
        # If archive process is interrupted exit program without merge
        log.error("Delta archiving is interrupted")
    total_rars = len(list(filter(lambda x: x.suffix == ".rar", BACKUP_ROOT.iterdir())))
    log.info(f"Archive complete. Total archives created: {total_rars}")


def cleanup(delete_df=False) -> None:
    """Function cleansup the Data dir of repo

    Args:
        delete_df (bool, optional): Flag that decides whether to delete main df or move it to delta_dir. Defaults to False.
    """
    send2trash([DATA_DIR/RAW_METADATA, CLEANED_METADATA])
    replace(DELTA_DATAFRAME, DELTA_DIR)
    if delete_df:
        send2trash(DATAFRAME)
    else:
        replace(DATAFRAME, DELTA_DIR)
    

def replace(src: Path, dst: Path) -> None:
    """A modified move function that replaces the file if exists instead of raising an OSError

    Args:
        src (Path): Source file
        dst (Path): Destination folder
    """
    try:
        move(src, dst)
    except OSError:
        return


def merge() -> None:
    """Function that finally merges delta into one single device backup
    """
    # Create backup dir for device if not exists
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    # Move everything in delta dir to backup dir
    # [move(x, BACKUP_DIR) for x in DELTA_DIR.iterdir()]
    for src_file in DELTA_DIR.rglob("*"):
        if src_file.is_file():
            dst_file = BACKUP_DIR/src_file.relative_to(DELTA_DIR)
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            move(src_file, dst_file)
    # delete Delta dir
    send2trash(BACKUP_ROOT/"Delta")
    # log updates and exit
    log.info("Delta merged with Device backup folder")
    log.info("Backup complete!")
    