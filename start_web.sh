#!/bin/bash

# ModSmith Web Server Launcher
# Professional startup script for the web interface

echo "🚀 ModSmith Web Interface Launcher"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "mc" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv mc
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source mc/bin/activate

# Install/update requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "🔑 Please edit .env and add your GEMINI_API_KEY:"
    echo "   nano .env"
    echo ""
    echo "Then run this script again."
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
