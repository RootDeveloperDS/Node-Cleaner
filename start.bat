@echo off
echo Starting Developer Disk Cleaner...

:: Navigate to the directory where this script is located
cd /d "%~dp0"

:: Ensure dependencies are installed (this is fast if they are already present)
echo Checking dependencies...
python -m pip install -r requirements.txt >nul 2>&1

:: Run the main application
echo Launching...
python main.py

:: If the application crashes, pause so the user can read the error message
if %errorlevel% neq 0 (
    echo.
    echo Application crashed with error code %errorlevel%.
    pause
)
