@echo off
echo 🙏 Sahay AI - Quick Start Setup
echo ===============================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

echo ✅ Python is installed

REM Create virtual environment
echo 🔧 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Please:
    echo    1. Copy .env.template to .env
    echo    2. Add your IBM WatsonX credentials
    echo    3. Run this script again
    pause
    exit /b 1
)

REM Check if PM-KISAN PDF exists
if not exist "data\pm_kisan_rules.pdf" (
    echo ⚠️  PM-KISAN PDF not found. Please:
    echo    1. Copy PMKisanSamanNidhi.PDF to data\pm_kisan_rules.pdf
    echo    2. Run this script again
    pause
    exit /b 1
)

REM Run data ingestion
echo 🗄️  Running data ingestion pipeline...
python src\ingest.py

if errorlevel 1 (
    echo ❌ Data ingestion failed. Please check the error messages above.
    pause
    exit /b 1
)

echo ✅ Data ingestion completed successfully
echo 🚀 Starting Sahay AI application...
streamlit run src\app.py
