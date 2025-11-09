# MyBella Quick Setup Launcher for PowerShell
# Runs the setup script from the scripts folder

Write-Host "🚀 MyBella Quick Setup Launcher" -ForegroundColor Green
Write-Host "=" * 40

# Get the script directory and project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$setupScript = Join-Path $scriptDir "backend\scripts\setup\setup.ps1"

# Check if setup script exists
if (!(Test-Path $setupScript)) {
    Write-Host "❌ Setup script not found at: $setupScript" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Running setup from: $setupScript" -ForegroundColor Yellow
Write-Host ""

# Run the setup script
& $setupScript

Write-Host ""
Write-Host "✨ Setup launcher complete!" -ForegroundColor Green