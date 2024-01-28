@echo off
title ADB check
echo Checking . . . & echo.
adb\adb.exe start-server
echo.
adb\adb.exe devices
adb\adb.exe kill-server
pause