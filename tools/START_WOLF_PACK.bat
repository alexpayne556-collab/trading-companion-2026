@echo off
REM 🐺 WOLF PACK VISION - Windows Launcher
REM Double-click this file on your Shadow PC to start the pack

echo ====================================================================
echo 🐺 WOLF PACK VISION LAUNCHER
echo ====================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Install Python 3.12+ first.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if Ollama is installed
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama not found. Installing Ollama...
    echo.
    echo Visit: https://ollama.com/download/windows
    echo.
    echo After installing, run this script again.
    pause
    exit /b 1
)

echo ✅ Ollama found
echo.

REM Check if llava model is pulled
ollama list | find "llava" >nul
if errorlevel 1 (
    echo 📥 Downloading vision model (4.7GB, one-time only)...
    ollama pull llava
    if errorlevel 1 (
        echo ❌ Failed to download model
        pause
        exit /b 1
    )
)

echo ✅ Vision model ready
echo.

REM Install Python packages if needed
echo 📦 Checking Python packages...
python -c "import mss" >nul 2>&1
if errorlevel 1 (
    echo Installing mss...
    pip install mss
)

python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing pillow...
    pip install pillow
)

echo ✅ All packages ready
echo.

REM Start Ollama server in background if not running
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo 🚀 Starting Ollama server...
    start /B ollama serve
    timeout /t 3 >nul
)

echo ✅ Ollama server running
echo.

REM Get the script directory
set SCRIPT_DIR=%~dp0

REM Change to repo root (one level up from tools)
cd /d "%SCRIPT_DIR%.."

echo ====================================================================
echo 🐺 STARTING WOLF PACK
echo ====================================================================
echo.
echo The pack will now watch your screens.
echo Press Ctrl+C to stop.
echo.

REM Run the wolf pack
python tools\wolf_pack_vision.py

pause
