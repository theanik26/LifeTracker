@echo off
title LifeTrack Launcher
echo ===================================================
echo     LifeTrack - Measure Progress, Not Comparisons
echo ===================================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your system PATH.
    echo Please install Python version 3.8 or higher and try again.
    echo.
    pause
    exit /b
)

:: Create Virtual Environment if not exists
if not exist .venv (
    echo [INFO] Creating Python virtual environment venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b
    )
    echo [INFO] Virtual environment created successfully.
)

:: Activate Virtual Environment and install requirements
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate

echo [INFO] Checking and installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b
)

echo.
echo [SUCCESS] LifeTrack is starting up...
echo [SUCCESS] Your browser will open automatically in a few seconds.
echo [SUCCESS] To close the application, close this command window.
echo.

:: Run Flask App
python app.py

pause
