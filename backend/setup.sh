#!/bin/bash
# Setup script for AI Resume Analyzer backend

echo "🔧 Setting up AI Resume Analyzer Backend..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
echo "🧠 Downloading spaCy NLP model..."
python -m spacy download en_core_web_sm

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the backend server:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run: python app.py"
echo ""
