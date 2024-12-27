from typing import NamedTuple

from colorama import Fore
from pandas import DataFrame, concat, read_csv

from app.vars import DATAFRAME, DELTA_COLUMNS, DELTA_DATAFRAME, DEVICE_DATAFRAME
from utils import UTF_8_SIG, log
from utils.terminal import colorize


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
    