#!/bin/bash
# ============================================================================
# RAG System - Quick Setup Script
# ============================================================================

set -e  # Exit on any error

echo "=========================================="
echo "RAG SYSTEM - SETUP SCRIPT"
echo "=========================================="
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found: Python $python_version"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "   Virtual environment already exists"
else
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "   ✅ Dependencies installed"

# Create .env if doesn't exist
echo ""
if [ -f ".env" ]; then
    echo "⚙️  .env file already exists"
else
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "   ✅ .env created - PLEASE EDIT WITH YOUR CREDENTIALS"
fi

# Create directories
echo ""
echo "📁 Creating directories..."
mkdir -p output
mkdir -p logs
echo "   ✅ Directories created"

# Verify configuration
echo ""
echo "🔍 Verifying configuration..."
python -m 0_foundation.config

echo ""
echo "=========================================="
echo "✅ SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "NEXT STEPS:"
echo "1. Edit .env file with your credentials:"
echo "   nano .env"
echo ""
echo "2. Set up database in Supabase:"
echo "   - Open Supabase SQL Editor"
echo "   - Run setup_database.sql"
echo ""
echo "3. Verify everything works:"
echo "   python -m 0_foundation.config"
echo ""
echo "=========================================="
