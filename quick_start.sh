#!/bin/bash

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
