# Let's create a sample .env template file as well
env_template_content = """# IBM WatsonX Credentials
# Get these from your IBM Cloud account
WATSONX_API_KEY=your_watsonx_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_id_here

# Optional: Custom model configurations
# WATSONX_MODEL_ID=ibm/granite-13b-chat-v2
# WATSONX_API_ENDPOINT=https://us-south.ml.cloud.ibm.com

# Instructions:
# 1. Copy this file to .env (without .template extension)
# 2. Replace the placeholder values with your actual IBM WatsonX credentials
# 3. Never commit the .env file to version control (it's already in .gitignore)
"""

# Save .env.template
with open("sahay-ai-hackathon/.env.template", "w", encoding="utf-8") as f:
    f.write(env_template_content)

print("✅ Created .env.template file for easy setup")

# Let's also create a quick start script
quick_start_content = '''#!/bin/bash

# Sahay AI Quick Start Script
echo "🙏 Sahay AI - Quick Start Setup"
echo "==============================="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

echo "✅ Python is installed"

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip and try again."
    exit 1
fi

echo "✅ pip is available"

# Create virtual environment
echo "🔧 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # macOS/Linux
    source venv/bin/activate
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please:"
    echo "   1. Copy .env.template to .env"
    echo "   2. Add your IBM WatsonX credentials"
    echo "   3. Run this script again"
    exit 1
fi

# Check if PM-KISAN PDF exists
if [ ! -f "data/pm_kisan_rules.pdf" ]; then
    echo "⚠️  PM-KISAN PDF not found. Please:"
    echo "   1. Copy PMKisanSamanNidhi.PDF to data/pm_kisan_rules.pdf"
    echo "   2. Run this script again"
    exit 1
fi

# Run data ingestion
echo "🗄️  Running data ingestion pipeline..."
python src/ingest.py

if [ $? -eq 0 ]; then
    echo "✅ Data ingestion completed successfully"
    echo "🚀 Starting Sahay AI application..."
    streamlit run src/app.py
else
    echo "❌ Data ingestion failed. Please check the error messages above."
    exit 1
fi
'''

# Save quick start script
with open("sahay-ai-hackathon/quick_start.sh", "w", encoding="utf-8") as f:
    f.write(quick_start_content)

# Make it executable
import stat
os.chmod("sahay-ai-hackathon/quick_start.sh", stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

print("✅ Created quick_start.sh script for automated setup")

# Create a Windows batch file version too
quick_start_bat_content = '''@echo off
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
call venv\\Scripts\\activate.bat

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
if not exist "data\\pm_kisan_rules.pdf" (
    echo ⚠️  PM-KISAN PDF not found. Please:
    echo    1. Copy PMKisanSamanNidhi.PDF to data\\pm_kisan_rules.pdf
    echo    2. Run this script again
    pause
    exit /b 1
)

REM Run data ingestion
echo 🗄️  Running data ingestion pipeline...
python src\\ingest.py

if errorlevel 1 (
    echo ❌ Data ingestion failed. Please check the error messages above.
    pause
    exit /b 1
)

echo ✅ Data ingestion completed successfully
echo 🚀 Starting Sahay AI application...
streamlit run src\\app.py
'''

# Save Windows batch file
with open("sahay-ai-hackathon/quick_start.bat", "w", encoding="utf-8") as f:
    f.write(quick_start_bat_content)

print("✅ Created quick_start.bat script for Windows users")

print("\n🎉 Complete Sahay AI project generated successfully!")
print("📁 Total files created: 13")
print("\n📋 Final checklist:")
print("   ✅ Project structure")
print("   ✅ Python source code")
print("   ✅ Requirements and dependencies") 
print("   ✅ Documentation (README.md)")
print("   ✅ Environment template")
print("   ✅ Setup scripts (Linux/Windows)")
print("   ✅ Git configuration")