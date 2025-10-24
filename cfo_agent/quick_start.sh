#!/bin/bash

# CFO Agent Quick Start Script

echo "🚀 CFO Agent Quick Start"
echo "========================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY and SUPABASE_DB_URL"
    echo ""
    read -p "Press Enter after updating .env file..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

echo ""
echo "🎯 Starting CFO Agent server..."
echo "   Server will be available at: http://localhost:8000"
echo "   API docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python app.py
