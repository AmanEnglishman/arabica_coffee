@echo off
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: Run as Administrator.
    pause & exit /b 1
)

set SERVICE_NAME=ArabicaPrinter
set DIR=%~dp0
set NSSM=%DIR%nssm.exe

where nssm >nul 2>&1
if not errorlevel 1 set NSSM=nssm

echo Stopping and removing service %SERVICE_NAME%...
%NSSM% stop %SERVICE_NAME%
%NSSM% remove %SERVICE_NAME% confirm

echo Done.
pause
