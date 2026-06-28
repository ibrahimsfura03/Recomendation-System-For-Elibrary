#!/bin/bash

# E-Library Setup Script
# One-command installation for all dependencies

echo "======================================"
echo "E-Library Book Recommendation System"
echo "Setup Script"
echo "======================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

if [ ! -d "venv" ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "🆙 Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1

# Install dependencies
echo "📚 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✅ Setup Complete!"
    echo "======================================"
    echo ""
    echo "To start the application:"
    echo "  1. Activate venv: source venv/bin/activate"
    echo "  2. Run app:       python app.py"
    echo "  3. Open browser:  http://localhost:5000"
    echo ""
    echo "CLI Tools:"
    echo "  python run_hybrid.py"
    echo "  python run_recommendation.py"
    echo "  python run_content.py"
    echo "======================================"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
