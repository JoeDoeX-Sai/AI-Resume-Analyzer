@echo off
REM Setup script for AI Resume Analyzer backend (Windows)

echo Setting up AI Resume Analyzer Backend...

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Download spaCy model
echo Downloading spaCy NLP model...
python -m spacy download en_core_web_sm

echo.
echo Setup complete!
echo.
echo To start the backend server:
echo   1. Activate virtual environment: venv\Scripts\activate.bat
echo   2. Run: python app.py
echo.
pause
