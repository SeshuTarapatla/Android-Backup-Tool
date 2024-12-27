from datetime import datetime
from pathlib import PurePosixPath

from pandas import DataFrame, concat

from app.vars import (
    ANDROID_DIR,
    ANDROID_MEDIA_DIR,
    CLEANED_METADATA,
    DATA_DIR,
    DATAFRAME,
    DATAFRAME_COLUMNS,
    DEVICE_ROOT,
    IGNORE_DIRS,
    IGNORE_TYPES,
    RAW_METADATA,
    REQUIRED_PACKAGES,
)
from utils import UTF_8, UTF_8_SIG, log
from utils.android import device


def fetch() -> None:
    """Wrapper function to pull, clean & parse metadata dataframe in one go.
    """
    log.stage("Metadata")
    pull()
    clean()
    parse()


def pull() -> None:
    """Function that generates the raw metadata report of all files in the device
    """
    # variables
    src_file = f"{DEVICE_ROOT/RAW_METADATA}"
    dst_file = f"{DATA_DIR/RAW_METADATA}"
    # command to generate metadata file
    command = f"ls -llR {DEVICE_ROOT}/ > {src_file}"
    log.info(f"Executing: {command}")
    # execute the command and pull the file
    device.shell(command)
    device.pull(src_file, dst_file)
    # remove it's own entry from report
    with open(dst_file, "r+", encoding=UTF_8) as frw:
        lines = frw.readlines()
        for index, line in enumerate(lines):
            if RAW_METADATA.name in line:
                del lines[index]
        frw.seek(0)
        frw.truncate()
        frw.writelines(lines)
    log.info(f"Raw metadata pulled into   > {dst_file}")


def clean() -> None:
    """Function to clean the raw metadata. Removes sub-directories and empty directories.
    """
    # variables
    src_file = f"{DATA_DIR/RAW_METADATA}"
    dst_file = CLEANED_METADATA
    # read raw metadata from src_file
    with open(src_file, "r", encoding=UTF_8) as fr:
        raw_data = fr.read().split("\n\n")
    cleaned_data = []
    # clean metadata for each dir iteratively
    for raw_dir in raw_data:
        lines = raw_dir.splitlines()
        dir_name = lines[0].replace(":", "/")
        if skip_this_dir(dir_name):
            continue
        files = list(filter(lambda line: line.startswith("-r"), lines[3:]))
        if len(files) == 0:
            continue
        cleaned_dir = "\n".join([dir_name] + files)
        cleaned_data.append(cleaned_dir)
    # save cleaned metadata into dst_file
    with open(dst_file, "w", encoding=UTF_8) as fw:
        fw.write("\n\n".join(cleaned_data))
    log.info(f"Raw metadata cleaned into  > {dst_file}")


def skip_this_dir(dir_name: str) -> bool:
    """Function that checks to skip Android folder directory or not

    Args:
        dir_name (str): Directory path

    Returns:
        bool: Skip True or False
    """
    # Skip the dir if it's a part of dirs.ignore set
    if any([dir_name.startswith(ignore_dir) for ignore_dir in IGNORE_DIRS]):
        return True
    # Skip the dir if it belongs to Android dir but not in required packages
    dir_path = PurePosixPath(dir_name)
    if dir_path.is_relative_to(ANDROID_DIR):
        if dir_path.is_relative_to(ANDROID_MEDIA_DIR):
            try:
                package = dir_path.parts[3]
                if package not in REQUIRED_PACKAGES:
                    return True
            except IndexError:
                return True
        else:
            return True
    return False


def parse() -> None:
    """Function that parses String metadata into Pandas DF
    """
    # variables
    src_file = CLEANED_METADATA
    dst_file = DATAFRAME
    # read cleaned metadata from src_file
    with open(src_file, "r", encoding=UTF_8) as fr:
        data = fr.read().split("\n\n")
    # convert each dir string into frames
    frames = map(to_frame, data)
    # concat into single dataframe
    dataframe = concat(frames, ignore_index=True)
    # drop files of type ignore
    ignore_mask = dataframe['Type'].apply(lambda x: str(x).removeprefix(".").upper() in IGNORE_TYPES)
    dataframe = dataframe[~ignore_mask]
    # export dataframe as csv
    dataframe.to_csv(dst_file, index=False, encoding=UTF_8_SIG)
    log.info(f"DataFrame exported as csv  > {dst_file}")


def to_frame(dir_data: str) -> DataFrame:
    """Generates a dataframe for a given dir string from metadata

    Args:
        dir_data (str): Data of a single dir in string

    Returns:
        DataFrame: Dir string coverted into dataframe
    """
    def to_record(line: str) -> dict:
        """Helper function that converts a given line string to dataframe record/row

        Args:
            line (str): input line as string

        Returns:
            dict: line converted to record/row as dict
        """
        parts = line.split()
        record = {
            "File": " ".join(parts[8:]),
            "Type": PurePosixPath(parts[-1]).suffix,
            "Size": int(parts[4]),
            "Date": datetime.fromisoformat(" ".join(parts[5:7])),
            "Path": PurePosixPath(f"{dir_name}/{line[line.index(parts[8]):]}")
            # Line index is used for path to avoid issues with files having multiple spaces in their names
        }
        return record

    # split blob string into lines & parse dataframe
    lines = dir_data.splitlines()
    dir_name = lines[0]
    records = map(to_record, lines[1:])
    return DataFrame(records, columns=DATAFRAME_COLUMNS)
