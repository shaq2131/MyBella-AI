# MyBella Setup Script for Windows PowerShell
# Run this script to set up the MyBella environment

Write-Host "🚀 MyBella Setup Starting..." -ForegroundColor Green
Write-Host "=" * 50

# Check Python installation
Write-Host "🔍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        Write-Host "✅ $pythonVersion detected" -ForegroundColor Green
    } else {
        Write-Host "❌ Python not found. Please install Python 3.8 or higher" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8 or higher" -ForegroundColor Red
    exit 1
}

# Get the project root (3 levels up from this script)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $scriptPath))
Set-Location $projectRoot

# Create virtual environment (recommended)
Write-Host "🔧 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    if ($?) {
        Write-Host "✅ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    }
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
if ($?) {
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "⚠️  Could not activate virtual environment, continuing with global Python" -ForegroundColor Yellow
}

# Upgrade pip
Write-Host "📦 Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
$directories = @(
    "backend\database\instances\uploads",
    "backend\database\instances\uploads\profile_pics",
    "backend\database\instances\uploads\persona_pics",
    "logs"
)

foreach ($dir in $directories) {
    $fullPath = Join-Path $projectRoot $dir
    if (!(Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    } else {
        Write-Host "✅ Directory already exists: $dir" -ForegroundColor Green
    }
}

# Install requirements
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements-minimal.txt") {
    pip install -r requirements-minimal.txt
    if ($?) {
        Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    }
} elseif (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if ($?) {
        Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    }
} else {
    Write-Host "❌ No requirements file found" -ForegroundColor Red
}

# Setup environment file
Write-Host "⚙️  Setting up environment..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env file from .env.example" -ForegroundColor Green
    } else {
        Write-Host "⚠️  No .env.example found, you'll need to create .env manually" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Display next steps
Write-Host ""
Write-Host "🎉 Setup completed! Next steps:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Configure your API keys in the .env file:" -ForegroundColor Cyan
Write-Host "   - Add your OpenAI API key for AI chat"
Write-Host "   - Add your ElevenLabs API key for voice synthesis"
Write-Host "   - (Optional) Add Firebase and Pinecone keys for enhanced features"
Write-Host ""
Write-Host "2. Run the application:" -ForegroundColor Cyan
Write-Host "   python mybella.py"
Write-Host ""
Write-Host "3. Open your browser and go to:" -ForegroundColor Cyan
Write-Host "   http://127.0.0.1:5000"
Write-Host ""
Write-Host "📚 API Documentation:" -ForegroundColor Magenta
Write-Host "   - OpenAI API: https://platform.openai.com/api-keys"
Write-Host "   - ElevenLabs API: https://elevenlabs.io/"
Write-Host "   - Firebase: https://console.firebase.google.com/"
Write-Host "   - Pinecone: https://www.pinecone.io/"
Write-Host ""
Write-Host "✨ Setup complete! Happy coding! ✨" -ForegroundColor Green