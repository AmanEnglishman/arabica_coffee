@echo off
echo === Arabica Print Client — Windows Build ===

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org
    pause & exit /b 1
)

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

:: Get escpos package directory for data files
for /f "tokens=*" %%i in ('python -c "import escpos, os; print(os.path.dirname(escpos.__file__))"') do set ESCPOS_DIR=%%i
echo escpos dir: %ESCPOS_DIR%

:: Build exe
echo Building executable...
python -m PyInstaller --onefile ^
    --name arabica-printer ^
    --add-data "%ESCPOS_DIR%\capabilities.json;escpos" ^
    --hidden-import=websockets ^
    --hidden-import=websockets.legacy ^
    --hidden-import=websockets.legacy.client ^
    --hidden-import=escpos ^
    --hidden-import=escpos.printer ^
    --hidden-import=requests ^
    --distpath dist ^
    client.py

if errorlevel 1 (
    echo ERROR: Build failed.
    pause & exit /b 1
)

:: Copy config.json next to the exe
copy /Y config.json dist\config.json >nul
echo Copied config.json to dist\

echo.
echo Build successful: dist\arabica-printer.exe
echo Run install_windows.bat to register as Windows Service.
pause
