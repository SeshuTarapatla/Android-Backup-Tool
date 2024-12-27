from base64 import b64decode
from datetime import datetime
from os import environ
from pathlib import Path, PurePosixPath

from utils import load_set
from utils.android import DEVICE_MODEL


DATA_DIR          = Path("data")
DEVICE_ROOT       = PurePosixPath("sdcard")
BACKUP_ROOT       = Path("D:/Backup")

ANDROID_DIR       = DEVICE_ROOT/"Android"
ANDROID_MEDIA_DIR = ANDROID_DIR/"media"
BACKUP_DIR        = BACKUP_ROOT/DEVICE_MODEL
CLEANED_METADATA  = DATA_DIR/"cleaned_metadata.bin"
DATAFRAME         = DATA_DIR/"dataframe.csv"
DATAFRAME_COLUMNS = ["File", "Type", "Size", "Date", "Path"]
DELTA_COLUMNS     = ["File", "Type", "Size", "Size_old", "Date", "Date_old", "Path", "Kind"]
DELTA_DATAFRAME   = DATA_DIR/"deltaframe.csv"
DELTA_DIR         = BACKUP_ROOT/"Delta"/DEVICE_MODEL
DEVICE_DATAFRAME  = BACKUP_DIR/DATAFRAME.name
IGNORE_DIRS       = load_set("./data/dirs.ignore")
IGNORE_TYPES      = load_set("./data/types.ignore")
RAR_EXECUTABLE    = Path("C:/Program Files/WinRAR/WinRAR.exe")
RAW_METADATA      = Path("raw_metadata.bin")
RECYCLE_BIN       = BACKUP_DIR/"Recycle Bin"
REQUIRED_PACKAGES = load_set("./data/required_packages.txt")
MYPASS            = b64decode(str(environ.get("MYPASS")).encode("utf-8")).decode("utf-8")
TIMESTAMP         = datetime.now().strftime("%Y%m%d%H%M%S")
