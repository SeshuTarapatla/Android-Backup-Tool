from typing import cast

from adbutils import AdbError, adb
from colorama import Fore
from uiautomator2 import Device
from uiautomator2 import connect as adb_connect

from utils import log
from utils.terminal import colorize


def connect_device() -> Device:
    """Function that tries to connect to an ADB device if exists.

    Returns:
        Device: uiautomator2 Device
    """
    serial = ""
    for connected_device in adb.iter_device():
        if "emulator" in connected_device.serial:
            pass
        else:
            serial = connected_device.serial
            break
    log.info("Connecting to a device")
    device = cast(Device, None)
    try:
        device = adb_connect(serial)
        log.update(f"Device connected: {device.device_info.get("model", "Unknown")} ({colorize(device.serial, Fore.CYAN)})")
    except AdbError as exception:
        log.update(exception, task_success=False)
    return device


# Device instance
device        = connect_device()
DEVICE_MODEL  = str(device.device_info.get("model", "Unknown"))
DEVICE_SERIAL = device.serial
