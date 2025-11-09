# Project Cleanup Script
# Removes temporary files, organizes documentation, cleans cache

Write-Host "🧹 Starting MyBella Project Cleanup..." -ForegroundColor Cyan
Write-Host ""

# 1. Remove Python cache files
Write-Host "📦 Cleaning Python cache files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Include "__pycache__","*.pyc","*.pyo" | Remove-Item -Recurse -Force
Write-Host "   ✅ Removed __pycache__ directories and .pyc files" -ForegroundColor Green

# 2. Create scripts directory if it doesn't exist
Write-Host ""
Write-Host "📁 Organizing migration scripts..." -ForegroundColor Yellow
if (-not (Test-Path ".\scripts")) {
    New-Item -ItemType Directory -Path ".\scripts" | Out-Null
}
if (-not (Test-Path ".\scripts\migrations")) {
    New-Item -ItemType Directory -Path ".\scripts\migrations" | Out-Null
}
if (-not (Test-Path ".\scripts\utils")) {
    New-Item -ItemType Directory -Path ".\scripts\utils" | Out-Null
}

# Move migration scripts
$migrationScripts = @(
    "create_cbt_games_tables.py",
    "create_wellness_tables.py",
    "migrate_db.py",
    "migrate_gender.py",
    "migrate_voice_system.py"
)

foreach ($script in $migrationScripts) {
    if (Test-Path $script) {
        Move-Item -Path $script -Destination ".\scripts\migrations\" -Force
        Write-Host "   ✅ Moved $script to scripts/migrations/" -ForegroundColor Green
    }
}

# Move utility scripts
$utilScripts = @(
    "cleanup_old_tables.py",
    "generate_wellness_models.py",
    "check_db.py",
    "init_personas.py"
)

foreach ($script in $utilScripts) {
    if (Test-Path $script) {
        Move-Item -Path $script -Destination ".\scripts\utils\" -Force
        Write-Host "   ✅ Moved $script to scripts/utils/" -ForegroundColor Green
    }
}

# 3. Create docs directory and organize documentation
Write-Host ""
Write-Host "📚 Organizing documentation..." -ForegroundColor Yellow
if (-not (Test-Path ".\docs")) {
    New-Item -ItemType Directory -Path ".\docs" | Out-Null
}
if (-not (Test-Path ".\docs\voice")) {
    New-Item -ItemType Directory -Path ".\docs\voice" | Out-Null
}
if (-not (Test-Path ".\docs\cbt")) {
    New-Item -ItemType Directory -Path ".\docs\cbt" | Out-Null
}

# Move voice documentation
$voiceDocs = @(
    "VOICE_COMPARISON.md",
    "VOICE_DOCUMENTATION_INDEX.md",
    "VOICE_QUICK_REFERENCE.md",
    "VOICE_QUICK_START.md",
    "VOICE_SYSTEM_MIGRATION.md",
    "VOICE_TESTING_GUIDE.md",
    "VOICE_TROUBLESHOOTING.md"
)

foreach ($doc in $voiceDocs) {
    if (Test-Path $doc) {
        Move-Item -Path $doc -Destination ".\docs\voice\" -Force
        Write-Host "   ✅ Moved $doc to docs/voice/" -ForegroundColor Green
    }
}

# Move CBT documentation
$cbtDocs = @(
    "CBT_COMPLETION_SUMMARY.md",
    "CBT_IMPLEMENTATION_STATUS.md",
    "TESTING_GUIDE.md"
)

foreach ($doc in $cbtDocs) {
    if (Test-Path $doc) {
        Move-Item -Path $doc -Destination ".\docs\cbt\" -Force
        Write-Host "   ✅ Moved $doc to docs/cbt/" -ForegroundColor Green
    }
}

# Keep important docs in root
Write-Host "   ℹ️  Keeping README.md, PERSONA_SYSTEM.md in root" -ForegroundColor Cyan

# 4. Clean up old backup files
Write-Host ""
Write-Host "🗑️  Removing backup files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Include "*.bak","*.backup","*~" | Remove-Item -Force
Write-Host "   ✅ Removed backup files" -ForegroundColor Green

# 5. Remove TODO file (implementation complete)
Write-Host ""
Write-Host "📋 Cleaning up TODO files..." -ForegroundColor Yellow
if (Test-Path "PRODUCTION_READINESS_TODO.md") {
    Remove-Item "PRODUCTION_READINESS_TODO.md" -Force
    Write-Host "   ✅ Removed PRODUCTION_READINESS_TODO.md (implementation complete)" -ForegroundColor Green
}

# 6. Summary
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "✨ Cleanup Complete!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 New Project Structure:" -ForegroundColor Yellow
Write-Host "   scripts/" -ForegroundColor Cyan
Write-Host "     └─ migrations/    (database migration scripts)"
Write-Host "     └─ utils/         (utility scripts)"
Write-Host "   docs/" -ForegroundColor Cyan
Write-Host "     └─ voice/         (voice system documentation)"
Write-Host "     └─ cbt/           (CBT tools documentation)"
Write-Host "   backend/            (application backend)"
Write-Host "   frontend/           (application frontend)"
Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Review docs/cbt/CBT_COMPLETION_SUMMARY.md for implementation details"
Write-Host "   2. Review docs/cbt/TESTING_GUIDE.md for testing instructions"
Write-Host "   3. Start the app: python mybella.py"
Write-Host "   4. Access wellness hub: http://localhost:5000/wellness/hub"
Write-Host ""
Write-Host "🚀 MyBella is ready for production!" -ForegroundColor Green
