#!/bin/bash
# Quick setup script للمشروع
# قم بتشغيل هذا الملف لإعداد البوت بسرعة

echo "================================"
echo "🤖 Exam Bot Setup"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python from https://www.python.org"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "❌ Important: Edit .env and add your BOT_TOKEN"
    echo "   Get token from @BotFather on Telegram"
else
    echo ""
    echo "✅ .env file already exists"
fi

echo ""
echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your BOT_TOKEN"
echo "2. Run: python bot.py"
echo ""
