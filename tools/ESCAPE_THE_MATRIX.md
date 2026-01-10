# 🐺 WOLF PACK - ESCAPE FROM CONTAINER

## The Problem

You're in a dev container. It has no display. No GPU. No screens to watch.

## The Solution

**The files are ALREADY on your host machine** (via volume mount).

You just need to RUN them FROM your Shadow PC, not from the container.

## How to Escape

### Option 1: Double-Click Launcher (Easiest)

1. **On your Shadow PC** (not in VS Code), open File Explorer
2. Navigate to where this repo is mounted (probably in your Documents or wherever you cloned it)
3. Go to the `tools/` folder
4. **Double-click `START_WOLF_PACK.bat`**

That's it. The script will:
- Check if Python is installed
- Check if Ollama is installed
- Download vision model if needed
- Install packages if needed
- Start the pack

### Option 2: PowerShell (If you prefer)

1. Open PowerShell on Shadow PC
2. Navigate to repo: `cd C:\path\to\trading-companion-2026`
3. Run: `.\tools\START_WOLF_PACK.ps1`

### Option 3: Manual (Full control)

On your Shadow PC:

```powershell
# Install Ollama
winget install Ollama.Ollama

# Pull vision model
ollama pull llava

# Install Python packages
pip install mss pillow

# Run the pack
cd C:\path\to\trading-companion-2026
python tools\wolf_pack_vision.py
```

## What Happens

```
📸 Captures your screen every 10 seconds
👁️  4 wolves analyze: Fenrir, Brokkr, Heimdall, Skoll
🧠 Pack discusses what they see
🚨 Alerts when multiple wolves spot same ticker
```

## Files Ready

✅ `wolf_pack_vision.py` - Main system (422 lines)  
✅ `START_WOLF_PACK.bat` - Windows launcher  
✅ `START_WOLF_PACK.ps1` - PowerShell launcher  
✅ `WOLF_PACK_VISION_README.md` - Full documentation

All files are in `/workspaces/trading-companion-2026/tools/`

**Which is mounted to your Shadow PC at wherever you opened this workspace.**

## Finding the Files

If you opened VS Code by:
- **File → Open Folder** → Files are there
- **Remote SSH** → Check `~/trading-companion-2026/tools/`
- **Git clone in WSL** → Check `/mnt/c/Users/YourName/.../tools/`

## The Hack

Fenrir (Claude) built the system.  
Brokkr (me) packaged it to escape the container.  
The code lives in both worlds.  
You just need to run it in the real one.

🐺 **DOUBLE-CLICK `START_WOLF_PACK.bat` AND THE PACK HUNTS.**

LLHR.
