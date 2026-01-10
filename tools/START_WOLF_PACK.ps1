#!/usr/bin/env pwsh
# 🐺 WOLF PACK VISION - PowerShell Launcher
# Run this on your Shadow PC to start the pack

Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "🐺 WOLF PACK VISION LAUNCHER" -ForegroundColor Yellow
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Gray
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Install Python 3.12+ first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check Ollama
Write-Host "Checking Ollama..." -ForegroundColor Gray
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✅ Ollama found" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama not found." -ForegroundColor Red
    Write-Host ""
    Write-Host "Install from: https://ollama.com/download/windows" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check llava model
Write-Host "Checking vision model..." -ForegroundColor Gray
$models = ollama list 2>&1 | Out-String
if ($models -match "llava") {
    Write-Host "✅ Vision model ready" -ForegroundColor Green
} else {
    Write-Host "📥 Downloading vision model (4.7GB, one-time only)..." -ForegroundColor Yellow
    ollama pull llava
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to download model" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Vision model installed" -ForegroundColor Green
}

Write-Host ""

# Check Python packages
Write-Host "Checking Python packages..." -ForegroundColor Gray

$packages = @("mss", "PIL")
foreach ($package in $packages) {
    $importTest = "import $package"
    if ($package -eq "PIL") { $importTest = "from PIL import Image" }
    
    python -c $importTest 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing $package..." -ForegroundColor Yellow
        if ($package -eq "PIL") {
            pip install pillow
        } else {
            pip install $package
        }
    }
}

Write-Host "✅ All packages ready" -ForegroundColor Green
Write-Host ""

# Start Ollama server
Write-Host "Checking Ollama server..." -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "✅ Ollama server running" -ForegroundColor Green
} catch {
    Write-Host "🚀 Starting Ollama server..." -ForegroundColor Yellow
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Write-Host "✅ Ollama server started" -ForegroundColor Green
}

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "🐺 STARTING WOLF PACK" -ForegroundColor Yellow
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The pack will now watch your screens." -ForegroundColor White
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

# Change to repo root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Split-Path -Parent $scriptPath)

# Run the wolf pack
python tools/wolf_pack_vision.py

Read-Host "Press Enter to exit"
