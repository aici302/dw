@echo off
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%core"

if "%1"=="--debug" goto DEBUG
if "%1"=="/debug" goto DEBUG
if "%1"=="-d" goto DEBUG

REM Kiem tra neu agent dang chay thi khong khoi tao de tranh loi Already Online
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name like 'python%%'\" | Where-Object CommandLine -like '*agent.py*' | ForEach-Object { exit 10 }; exit 0"
if %ERRORLEVEL% equ 10 (
    echo DWService Agent da dang chay san roi!
    ping -n 2 127.0.0.1 >nul
    exit
)

REM Khoi chay ngam bang pythonw.exe va ghi log vao dwagent.log
start "" /d "%SCRIPT_DIR%core" pythonw.exe agent.py -filelog
exit

:DEBUG
title DWService Agent (Debug Mode)
python.exe agent.py
pause
