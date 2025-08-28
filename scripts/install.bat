@echo off
echo Installing Edge Favorites to PDF Converter...
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Install package
echo Installing package...
pip install -e .

echo.
echo Installation complete!
echo.
echo To use the converter:
echo   1. Run: venv\Scripts\activate.bat
echo   2. Run: edge2pdf --help
echo.
pause