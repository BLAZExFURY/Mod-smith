#!/bin/bash
# ModSmith Setup Script

echo "🔨 ModSmith Setup Script"
echo "========================"

# Check if Python 3.11 is available
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11 not found. Please install Python 3.11 first."
    exit 1
fi

echo "✅ Python 3.11 found"

# Create virtual environment if it doesn't exist
if [ ! -d "mc" ]; then
    echo "📦 Creating virtual environment..."
    python3.11 -m venv mc
else
    echo "📦 Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source mc/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "🔑 IMPORTANT: Please edit .env and add your Gemini API key!"
    echo "   Get your API key from: https://makersuite.google.com/app/apikey"
    echo ""
else
    echo "⚙️  .env file already exists"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Gemini API key"
echo "2. Run: source mc/bin/activate"
echo "3. Run: python mod_generator.py"
