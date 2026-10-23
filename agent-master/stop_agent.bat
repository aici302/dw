@echo off
echo Dang dung DWService Agent...

REM Dung pythonw.exe
taskkill /f /im pythonw.exe 2>nul

REM Dung tien trinh python.exe dang chay agent.py bang PowerShell CIM
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*agent.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" 2>nul

REM Dung console window neu co
taskkill /f /fi "WINDOWTITLE eq DWService Agent*" 2>nul

echo Da dung Agent thanh cong!
ping -n 2 127.0.0.1 >nul
