#!/bin/bash

# ModSmith Setup Script
# Installs system dependencies and prepares the environment

echo "� ModSmith System Setup"
echo "========================"

# Check if we're on Ubuntu/Debian
if command -v apt &> /dev/null; then
    echo "📦 Installing system dependencies..."
    sudo apt update
    sudo apt install -y python3 python3-venv python3-pip python3-full
    echo "✅ System dependencies installed!"
else
    echo "ℹ️  This script is designed for Ubuntu/Debian systems."
    echo "Please install Python 3.8+, python3-venv, and python3-pip manually."
fi

echo ""
echo "🚀 Ready to run ModSmith!"
echo "Next steps:"
echo "1. Copy .env.example to .env and add your Gemini API key"
echo "2. Run: ./start_web.sh"
echo ""
fi

echo "✅ Setup complete!"
echo ""
echo "🚀 Virtual environment is now activated!"
echo "You can now run: python mod_generator.py"
echo ""
echo "💡 To reactivate later, run: source mc/bin/activate"

# Keep the environment activated by starting a new shell
echo "🔄 Starting new shell with activated environment..."
exec bash
