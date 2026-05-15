# Quick setup script for Windows
# تشغيل هذا الملف من PowerShell لإعداد البوت

Write-Host "================================"
Write-Host "🤖 Exam Bot Setup (Windows)" -ForegroundColor Green
Write-Host "================================"
Write-Host ""

# Check if Python is installed
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ Python is not installed" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org"
    exit 1
}

Write-Host "✅ Python found: " -NoNewline -ForegroundColor Green
python --version
Write-Host ""

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install requirements
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check if .env exists
Write-Host ""
if (Test-Path .env) {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host ""
    Write-Host "❌ Important: Edit .env and add your BOT_TOKEN" -ForegroundColor Red
    Write-Host "   Get token from @BotFather on Telegram" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================"
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "================================"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Edit .env and add your BOT_TOKEN"
Write-Host "2. Run: python bot.py"
Write-Host ""
