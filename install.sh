#!/bin/bash

# scAgent Installation Script
echo "🚀 Installing scAgent..."

# Check if Python 3.11+ is available
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if [[ $(echo "$python_version >= $required_version" | bc -l) -eq 1 ]]; then
    echo "✅ Python $python_version found"
else
    echo "❌ Python 3.11+ is required. Found: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install the package in development mode
echo "📥 Installing scAgent..."
pip install -e .

# Install additional dependencies
echo "📥 Installing additional dependencies..."
pip install requests tabulate

echo "✅ Installation complete!"
echo ""
echo "To use scAgent:"
echo "1. Activate the virtual environment: source .venv/bin/activate"
echo "2. Run tests: python test_scagent.py"
echo "3. Use CLI: scagent --help"
echo ""
echo "Configuration:"
echo "- Database: 10.28.1.24:5432"
echo "- Model API: http://10.28.1.21:30080/v1"
echo "- Edit scAgent/settings.yml to modify settings" 