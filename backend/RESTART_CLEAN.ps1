# ===================================================================
# RESTART BACKEND WITH CLEAN CACHE
# ===================================================================

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🧹 Cleaning Cache Files..." -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Navigate to backend directory
Set-Location $PSScriptRoot

# Delete __pycache__ directories
Write-Host "🗑️  Removing __pycache__ directories..." -ForegroundColor Gray
Get-ChildItem -Path . -Filter __pycache__ -Recurse -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "   Removing: $($_.FullName)" -ForegroundColor DarkGray
    Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
}

# Delete .pyc files
Write-Host "🗑️  Removing .pyc files..." -ForegroundColor Gray
Get-ChildItem -Path . -Filter *.pyc -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "   Removing: $($_.FullName)" -ForegroundColor DarkGray
    Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "✅ Cache cleaned successfully!" -ForegroundColor Green
Write-Host ""

# Test parse_array_field
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🧪 Testing parse_array_field function..." -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

try {
    python test_parse_fix.py
    
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host "🚀 Starting Django Server..." -ForegroundColor Yellow
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⚠️  Django server will start now." -ForegroundColor Yellow
    Write-Host "   Watch for '🔍 RAW REQUEST DATA' in logs when submitting." -ForegroundColor Yellow
    Write-Host ""
    
    # Start Django server
    python manage.py runserver 8000
    
} catch {
    Write-Host ""
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
