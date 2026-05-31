@echo off
:: Must be run as Administrator
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: Run this script as Administrator.
    pause & exit /b 1
)

set SERVICE_NAME=ArabicaPrinter
set DISPLAY_NAME=Arabica Print Client
set DIR=%~dp0
set EXE=%DIR%dist\arabica-printer.exe
set LOG_DIR=%DIR%logs

:: Check exe exists
if not exist "%EXE%" (
    echo ERROR: %EXE% not found. Run build_windows.bat first.
    pause & exit /b 1
)

:: Check NSSM
where nssm >nul 2>&1
if errorlevel 1 (
    echo NSSM not found. Downloading...
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile '%TEMP%\nssm.zip'"
    powershell -Command "Expand-Archive '%TEMP%\nssm.zip' -DestinationPath '%TEMP%\nssm' -Force"
    copy "%TEMP%\nssm\nssm-2.24\win64\nssm.exe" "%DIR%nssm.exe" >nul
    set NSSM=%DIR%nssm.exe
) else (
    set NSSM=nssm
)

:: Create logs dir
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Remove existing service if any
%NSSM% stop %SERVICE_NAME% >nul 2>&1
%NSSM% remove %SERVICE_NAME% confirm >nul 2>&1

:: Install service
echo Installing service %SERVICE_NAME%...
%NSSM% install %SERVICE_NAME% "%EXE%"
%NSSM% set %SERVICE_NAME% AppDirectory "%DIR%"
%NSSM% set %SERVICE_NAME% DisplayName "%DISPLAY_NAME%"
%NSSM% set %SERVICE_NAME% Description "Arabica Coffee receipt printer WebSocket client"
%NSSM% set %SERVICE_NAME% Start SERVICE_AUTO_START
%NSSM% set %SERVICE_NAME% AppStdout "%LOG_DIR%\stdout.log"
%NSSM% set %SERVICE_NAME% AppStderr "%LOG_DIR%\stderr.log"
%NSSM% set %SERVICE_NAME% AppRotateFiles 1
%NSSM% set %SERVICE_NAME% AppRotateBytes 5242880
%NSSM% set %SERVICE_NAME% AppRestartDelay 5000

:: Start service
echo Starting service...
%NSSM% start %SERVICE_NAME%

echo.
echo Service "%DISPLAY_NAME%" installed and started.
echo Manage: services.msc  or  nssm stop/start ArabicaPrinter
pause
