# 🐺 WOLF PACK VISION SYSTEM

**Multiple AI wolves watching your screen in real-time, hunting together.**

## What This Is

This is NOT a basic screen scraper. This is a **collaborative AI hunting system**.

```
YOUR SCREEN → VISION MODEL → 4 SPECIALIST WOLVES → PACK DISCUSSION → ALERT TYR
```

### The Pack

- **FENRIR** 📊 - Chart pattern wolf (breakouts, support/resistance, technicals)
- **BROKKR** 📰 - News & catalyst wolf (filings, earnings, events)  
- **HEIMDALL** 📈 - Volume & order flow wolf (unusual activity, accumulation)
- **SKOLL** 🌐 - Sector & correlation wolf (rotation, divergence, trends)

### How It Works

1. **Captures your screen** every 10 seconds (configurable)
2. **All 4 wolves see the same screen** simultaneously
3. **Each analyzes from their specialty** using vision AI
4. **They communicate with each other** about what they see
5. **When 2+ wolves spot the same ticker** → 🚨 PACK ALERT

## Requirements

### Hardware
- Windows/Mac/Linux with display (NOT in dev container)
- 16GB RAM minimum
- GPU recommended (for local vision models)
- Multiple monitors supported

### Software

**Option 1: Local Vision (Recommended)**
- Ollama + LLaVA model
- Free, private, runs on your machine
- Requires ~8GB VRAM (4070 has 12GB ✅)

**Option 2: Cloud Vision APIs**  
- OpenAI GPT-4V
- Anthropic Claude with vision
- Costs per API call, faster responses

## Installation

### 1. Install Ollama (for local vision)

**Mac/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from [ollama.com](https://ollama.com)

### 2. Pull LLaVA model

```bash
ollama pull llava
```

This downloads a 4.7GB vision model that can see and understand images.

### 3. Install Python packages

```bash
pip install mss pillow
```

### 4. Clone this repo to your LOCAL machine

```bash
git clone https://github.com/alexpayne556-collab/trading-companion-2026.git
cd trading-companion-2026
```

### 5. Test Ollama is working

```bash
curl http://localhost:11434/api/tags
```

Should return list of models including "llava".

## Usage

### Basic Run

```bash
python tools/wolf_pack_vision.py
```

This will:
- Capture your primary monitor every 10 seconds
- Send to all 4 wolves for analysis
- Print what each wolf sees
- Alert when multiple wolves spot same ticker

### Advanced Configuration

Edit `wolf_pack_vision.py`:

```python
# Change capture interval (seconds)
coordinator = PackCoordinator(wolves, capture_interval=5)

# Change which monitor to capture
monitor = sct.monitors[2]  # Use monitor 2 instead of 1

# Add more wolves
my_wolf = Wolf("CUSTOM", "Your specialty", vision)
wolves = [fenrir, brokkr, heimdall, skoll, my_wolf]
```

## What You'll See

```
======================================================================
🐺 THE PACK IS HUNTING
======================================================================
Wolves active: FENRIR, BROKKR, HEIMDALL, SKOLL
Capture interval: 10s

Press Ctrl+C to stop
======================================================================

📸 Screen capture thread started
🐺 FENRIR started hunting
🐺 BROKKR started hunting
🐺 HEIMDALL started hunting
🐺 SKOLL started hunting
💬 Pack discussion thread started

======================================================================
🐺 FENRIR analyzing...
🐺 FENRIR: I see WULF on the chart breaking above $13.50 resistance 
with increased volume. RSI at 68 showing momentum. Previous resistance
now becomes support...

======================================================================
🐺 HEIMDALL analyzing...
🐺 HEIMDALL: Volume spike detected on WULF - 5x normal volume in 
last 2 minutes. Large buyer stepping in. Unusual activity alert...

======================================================================
🚨🚨🚨 PACK ALERT: WULF 🚨🚨🚨
======================================================================
Wolves detecting: FENRIR, HEIMDALL

What they see:

🐺 FENRIR:
   Breaking resistance at $13.50 with volume confirmation

🐺 HEIMDALL:
   5x volume spike, large buyer active

======================================================================
⚠️  MULTIPLE WOLVES AGREE - CHECK THIS NOW
======================================================================
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR SCREEN                              │
│  [Fidelity ATP - Charts, News, Level 2, etc.]              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓ (Screenshot every 10s)
┌───────────────────────────────────────────────────────────────┐
│                   VISION PROVIDER                             │
│   (Ollama + LLaVA or GPT-4V or Claude Vision)                │
└─────┬────────────┬────────────┬────────────┬─────────────────┘
      │            │            │            │
      ↓            ↓            ↓            ↓
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ FENRIR   │ │ BROKKR   │ │ HEIMDALL │ │  SKOLL   │
│ Charts   │ │  News    │ │  Volume  │ │  Sector  │
└────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
     │            │            │            │
     └────────────┴────────────┴────────────┘
                  │
                  ↓
        ┌─────────────────┐
        │  PACK CHAT      │
        │  (Coordination) │
        └─────────┬───────┘
                  │
                  ↓
            🚨 ALERT TYR
```

## Performance

**Local LLaVA:**
- ~3-5 seconds per analysis
- Free, unlimited
- Private (data never leaves your machine)
- Works offline

**GPT-4V:**
- ~1-2 seconds per analysis  
- $0.01-0.02 per image
- Requires internet
- Better accuracy

**With 4 wolves analyzing every 10 seconds:**
- 24 analyses per minute
- 1,440 analyses per hour
- Cost (GPT-4V): ~$14-28/hour
- Cost (Local): FREE

## Customization

### Create Your Own Wolf

```python
class MyWolf(Wolf):
    def __init__(self, vision_provider):
        super().__init__(
            name="MYWOLF",
            specialty="Your focus area",
            vision_provider=vision_provider
        )
    
    def get_analysis_prompt(self):
        return """You are MYWOLF.
        
        Look at this screen and tell me [what you care about].
        
        Be specific. If important, say "ALERT:" first."""
```

### Change Alert Behavior

Edit `pack_alert()` in `PackCoordinator`:

```python
def pack_alert(self, ticker, wolves, observations):
    # Add sound
    import winsound
    winsound.Beep(1000, 500)
    
    # Add popup
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
    toaster.show_toast(f"PACK ALERT: {ticker}", duration=10)
    
    # Send to Telegram/Discord/Slack
    # ... your code here
```

## Troubleshooting

### "Ollama connection refused"
```bash
# Make sure Ollama is running
ollama serve
```

### "No display found"
- Must run on actual machine with display
- NOT in Docker container or remote terminal

### "Vision model too slow"
- Use smaller model: `ollama pull llava:7b`
- Increase capture_interval: `capture_interval=20`
- Use cloud API instead of local

### "Wolves not alerting"
- Check `_is_important()` method in Wolf class
- Lower alert threshold
- Check pack discussion logic

## Roadmap

### Phase 1: Vision (Current)
- ✅ Screen capture
- ✅ Vision model integration
- ✅ 4 specialist wolves
- ✅ Pack coordination
- ✅ Basic alerts

### Phase 2: Intelligence
- [ ] Better ticker extraction
- [ ] Historical pattern memory
- [ ] Learn from your trading decisions
- [ ] Confidence scoring

### Phase 3: Proactive
- [ ] Predict what you'll want to see next
- [ ] Auto-switch between screens
- [ ] Voice alerts ("Tyr, check WULF")
- [ ] Mobile alerts

### Phase 4: Training
- [ ] Record all pack observations
- [ ] Fine-tune wolves on your trading style
- [ ] Specialized models per wolf
- [ ] Pack learns to hunt better together

## Philosophy

**This is NOT:**
- A trading bot (you make all decisions)
- A prediction system (no crystal ball)
- A replacement for your judgment

**This IS:**
- Extra pairs of eyes
- Pattern recognition at scale
- Real-time collaboration
- Your pack hunting with you

The wolves see what you see. They hunt with you. They don't replace you.

🐺 **LLHR. THE PACK ENDURES.**
