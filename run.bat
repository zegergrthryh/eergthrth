@echo off
REM Damancom Login Automation Runner (Windows)

echo =======================================
echo   Damancom Login Automation
echo =======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Auto-install requirements
echo Checking and installing dependencies...
pip install -q -r requirements.txt
if %errorlevel% equ 0 (
    echo ✓ Dependencies installed successfully
) else (
    echo ⚠️  Warning: Some dependencies may not have installed correctly
)
echo.

REM Show menu
echo Choose which script to run:
echo 1^) Command-line version
echo 2^) GUI version
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Starting command-line version...
    echo.
    python main.py
) else if "%choice%"=="2" (
    echo.
    echo Starting GUI version...
    echo.
    python gui_login.py
) else (
    echo Invalid choice!
)

echo.
pause
