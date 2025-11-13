@echo off
REM Weekend Planner Assistant - Quick Start Script (Windows)
REM Run this to set up and test your environment

echo ===============================================
echo Weekend Planner Assistant - Quick Setup
echo ===============================================
echo.

REM Step 1: Check Python
echo Step 1: Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo   X Python not found! Please install Python 3.10+
    pause
    exit /b 1
) else (
    python --version
    echo   OK Python found
)
echo.

REM Step 2: Create virtual environment
echo Step 2: Setting up virtual environment...
if exist "venv" (
    echo   OK Virtual environment already exists
) else (
    python -m venv venv
    if errorlevel 1 (
        echo   X Failed to create virtual environment
        pause
        exit /b 1
    ) else (
        echo   OK Virtual environment created
    )
)
echo.

REM Step 3: Activate virtual environment
echo Step 3: Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo   ! Activation may have failed, continuing anyway...
) else (
    echo   OK Virtual environment activated
)
echo.

REM Step 4: Install dependencies
echo Step 4: Installing Python packages...
echo   This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo   ! Some dependencies may have failed to install
) else (
    echo   OK Dependencies installed
)
echo.

REM Step 5: Check .env file
echo Step 5: Checking configuration...
if exist ".env" (
    echo   OK .env file exists
) else (
    echo   ! .env file not found. Creating from example...
    copy .env.example .env >nul
    echo   OK Created .env file
    echo   ! Please edit .env and add your API keys!
)
echo.

REM Step 6: Test configuration
echo Step 6: Testing API configuration...
echo.
python test_config.py
echo.

REM Done
echo ===============================================
echo Setup Complete!
echo ===============================================
echo.
echo Next steps:
echo 1. Edit .env file with your API keys (if not done)
echo 2. Run: python main.py
echo 3. Or try examples: python example_usage.py
echo.
echo For detailed instructions, see SETUP.md
echo.
pause
