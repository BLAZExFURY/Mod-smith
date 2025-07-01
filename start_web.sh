#!/bin/bash

# ModSmith Web Server Launcher
# Professional startup script for the web interface

echo "🚀 ModSmith Web Interface Launcher"
echo "=================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed!"
    echo "Please install Python 3.8+ to continue."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment!"
        echo "Make sure you have python3-venv installed:"
        echo "   sudo apt install python3-venv python3-full"
        exit 1
    fi
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to activate virtual environment!"
    exit 1
fi

# Upgrade pip to latest version
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install/update requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies!"
    echo "Please check your requirements.txt file."
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "🔑 Please edit .env and add your GEMINI_API_KEY:"
    echo "   nano .env"
    echo ""
    echo "Get your API key from: https://makersuite.google.com/app/apikey"
    echo ""
    echo "Then run this script again."
    deactivate
    exit 1
fi

# Check if generated folder exists
if [ ! -d "generated" ]; then
    echo "📁 Creating generated folder..."
    mkdir -p generated
    touch generated/.gitkeep
fi

# Check if web folder exists
if [ ! -d "web" ]; then
    echo "❌ Error: web folder not found!"
    echo "Make sure you're running this from the ModSmith directory."
    deactivate
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting ModSmith Web Server..."
echo "📱 Web Interface: http://localhost:5000"
echo "🔧 API Documentation: http://localhost:5000/api/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the web server
python web_server.py
