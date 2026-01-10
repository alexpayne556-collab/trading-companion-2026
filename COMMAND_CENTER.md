# 🐺 WOLF PACK COMMAND CENTER
## Everything You Need to Hunt - One Place

---

## 🎯 QUICK START COMMANDS

```bash
# Master Dashboard (All-in-One)
python tools/master_dashboard.py
python tools/master_dashboard.py --continuous  # Auto-refresh every 5 min

# Web Dashboard (Browser-based)
bash launch_dashboard.sh
# Opens at http://localhost:5000

# Sector Rotation Analysis (Jupyter)
cd notebooks && jupyter notebook 07_cross_sector_rotation_flow.ipynb
```

---

## 📊 TOOLS BY FUNCTION

### 1. SECTOR ROTATION & MOMENTUM
| Tool | Command | What It Does |
|------|---------|--------------|
| **Master Dashboard** | `python tools/master_dashboard.py` | 24-hour sector rotation monitor, beaten sectors, avoid list |
| **Sector Rotation Notebook** | `notebooks/07_cross_sector_rotation_flow.ipynb` | Full rotation analysis, 17K+ events, duration patterns |
| **War Room Master** | `python tools/war_room_master.py` | 7 proven patterns: red-in-green, oversold bounce, sector rotation |
| **Live Trading Companion** | `python tools/live_trading_companion.py` | Real-time: green days tracker, 10am dips, momentum plays |

### 2. INSIDER ACTIVITY & SEC FILINGS
| Tool | Command | What It Does |
|------|---------|--------------|
| **Insider Cluster Scanner** | `python tools/insider_cluster_scanner.py` | Find 3+ insiders buying same ticker (high conviction) |
| **SEC Scanner** | `python tools/sec_scanner.py` | Form 4 (insider) + 8-K (material events) last 3 days |
| **8-K Scanner v2** | `python tools/sec_8k_scanner_v2.py` | Contract filings, dollar amounts, gov agencies |

### 3. PRICE ACTION & TECHNICAL
| Tool | Command | What It Does |
|------|---------|--------------|
| **Bison Catcher** | `python tools/bison_catcher.py` | Big movers breaking out with volume |
| **Intelligence Scanner** | `python tools/intelligence_scanner.py` | Full ticker scan: price, fundamentals, technicals, news |
| **Data Collector** | `python tools/data_collector.py` | Historical snapshots, RSI, volume ratios |

### 4. DAILY WORKFLOWS
| Tool | Command | What It Does |
|------|---------|--------------|
| **Morning Briefing** | `python tools/morning_briefing.py` | Market overview, sector movers, top 5 plays for today |
| **Portfolio Monitor** | `python src/portfolio/monitor.py` | Check positions, thesis alignment, concentration risk |

### 5. WEB DASHBOARDS
| Tool | URL | What It Shows |
|------|-----|---------------|
| **Wolf Pack Web** | `bash launch_dashboard.sh` → http://localhost:5000 | AI Fuel Chain heatmap, high conviction scores, wounded prey, clusters, 8-Ks |

---

## 🗂️ KEY NOTEBOOKS

### Sector Rotation Analysis
**File:** `notebooks/07_cross_sector_rotation_flow.ipynb`

**What's Inside:**
- 10 sectors tracked (quantum, space, biotech, uranium, cybersecurity, etc.)
- 17,546 rotation events analyzed (Jan 2024 - Jan 2026)
- Rotation prediction system (4-signal scoring)
- Duration analysis (quantum 6.4 days, avg 2.7 days)
- Laggard scanner
- Morning spike entry strategy
- 24-hour monitoring dashboard
- **CRITICAL FINDINGS:**
  - Quantum/Space correlation: 0.58 (move together)
  - Space ran +91.7% from lows (LUNR 6-day run Dec 29 - Jan 6)
  - Quantum followed (+17.4% from lows)
  - Both dumped Jan 7 (rotation ending)
  - Beaten sectors: Biotech Small (-21.7%), Cybersecurity (-10.2%), AI Hype (-12.5%)

**Key Functions:**
```python
detect_rotations()                    # Find 17K+ rotation events
analyze_rotation_sequences()          # Transition matrix
predict_rotation_risk()               # 0-100 risk scoring
find_sector_laggards()                # Laggards within hot sectors
morning_spike_entry_strategy()        # 9:30 AM spike capture
analyze_rotation_duration()           # How long sectors stay hot
```

---

## 📁 DIRECTORY STRUCTURE

```
trading-companion-2026/
├── tools/                      # All Python scanners/tools
│   ├── master_dashboard.py     # 🔥 NEW: Unified dashboard
│   ├── war_room_master.py      # Pattern opportunity scorer
│   ├── live_trading_companion.py
│   ├── morning_briefing.py
│   ├── insider_cluster_scanner.py
│   ├── sec_scanner.py
│   ├── sec_8k_scanner_v2.py
│   ├── intelligence_scanner.py
│   ├── data_collector.py
│   └── bison_catcher.py
│
├── notebooks/                  # Jupyter analysis notebooks
│   └── 07_cross_sector_rotation_flow.ipynb  # 🔥 Sector rotation
│
├── web/                        # Web dashboard
│   ├── app.py                  # Flask server
│   └── templates/
│
├── src/                        # Core application code
│   ├── portfolio/
│   │   ├── monitor.py          # Portfolio monitoring
│   │   └── thesis_validator.py
│   ├── apis/
│   │   ├── alpaca_client.py    # Alpaca trading API
│   │   ├── polygon_client.py   # Market data
│   │   └── yfinance_client.py  # Free market data
│   └── research/               # Research modules
│
├── dna/                        # Wolf Pack DNA/philosophy
├── logs/                       # Trade logs & snapshots
├── portfolio/                  # Portfolio definitions
└── launch_dashboard.sh         # Quick web dashboard launch
```

---

## 🎯 SECTOR DEFINITIONS

### All 10 Sectors Tracked:
```python
SECTORS = {
    'quantum': ['IONQ', 'RGTI', 'QBTS'],
    'space': ['RKLB', 'ASTS', 'LUNR'],
    'biotech_small': ['SAVA', 'ALNY'],
    'biotech_large': ['MRNA', 'BNTX', 'NVAX'],
    'uranium': ['CCJ', 'UEC', 'UUUU'],
    'cybersecurity': ['CRWD', 'S', 'ZS'],
    'ai_infrastructure': ['NVDA', 'AMD', 'AVGO'],
    'ai_hype': ['AI', 'BBAI'],
    'defense': ['LMT', 'RTX', 'BA'],
    'semi': ['ASML', 'TSM', 'INTC']
}
```

---

## 🔥 CURRENT TRADE SETUP (Jan 8, 2026)

### ✅ WATCH (Beaten Down - Entry Opportunity):
- **Biotech Small**: -21.7% from 30d high, +3.40% today
  - SAVA: $2.18 (+2.83% today, +10.10% 5d)
  - ALNY: $422.50 (+3.96% today, +6.25% 5d)
  
- **Cybersecurity**: -10.2% from 30d high, +3.64% today
  - CRWD: $478.91 (+4.49% today, +2.17% 5d)
  - ZS: $231.16 (+4.11% today, +2.77% 5d)
  - S: $15.53 (+2.31% today, +3.53% 5d)

### ❌ AVOID (Extended - At Highs):
- **Uranium**: 0.0% from high (AT PEAK)
  - CCJ: $103.94 (+1.81% today)
  
- **Space**: -5.1% from high, +91.7% from low (RAN ALREADY)
  - LUNR: -1.06% today (6-day run ended Jan 6)
  - RKLB: -2.27% today
  - ASTS: -12.06% today (DUMP STARTING)
  
- **Quantum**: -6.9% from high (Following space dump)
  - QBTS: -3.42% today
  - IONQ: -1.93% today

### 🎯 ENTRY PLAN:
```
IF biotech/cybersecurity green 2 days straight (Jan 8-9):
  → Enter 50% position
  → Stop: -3%
  → Add 50% if continues Day 3
  → Target: +10-20% (3-6 day hold)
  
IF red or mixed:
  → WAIT, don't force it
```

---

## 📚 KEY DOCUMENTS

### Strategy & Philosophy:
- `dna/QUICK_AWAKENING.md` - Brokkr's core identity
- `MASTER_HUNTING_STRATEGY.md` - Overall trading approach
- `EARLY_POSITIONING_PLAYBOOK.md` - Entry strategies
- `REPEATABLE_PATTERNS_QUANTITATIVE.md` - Data-driven patterns

### Recent Battle Plans:
- `MONDAY_BATTLE_PLAN.md` - Latest market analysis
- `SECTOR_ROTATION_JAN5.md` - Sector rotation findings
- `SCAN_RESULTS_JAN5.md` - Scanner outputs

### Trade Learning:
- `WOLF_LEARNING_LOG.md` - Lessons from past trades
- `TRADE_LEARNING_SYSTEM.md` - How we improve

---

## 🛠️ DEVELOPMENT TOOLS

### Python Environment:
```bash
# Activate venv (if using)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Key packages:
# - yfinance (market data)
# - pandas, numpy (data analysis)
# - flask (web dashboard)
# - requests (API calls)
```

### Running Tests:
```bash
pytest tests/
```

### Configuration:
- `.env` - API keys (Alpaca, Polygon) [CREATE FROM .env.example]
- `config.yaml` - Application config

---

## ⚡ POWER USER WORKFLOWS

### Morning Routine (Before Market Open):
```bash
# 1. Check overnight moves
python tools/morning_briefing.py

# 2. Scan for clusters/8-Ks
python tools/insider_cluster_scanner.py
python tools/sec_8k_scanner_v2.py

# 3. Update sector rotation
python tools/master_dashboard.py

# 4. Launch web dashboard for monitoring
bash launch_dashboard.sh
```

### Intraday Monitoring:
```bash
# Keep master dashboard running with auto-refresh
python tools/master_dashboard.py --continuous

# Or use web dashboard (browser stays open)
# Already running at http://localhost:5000
```

### End of Day:
```bash
# Check positions
python src/portfolio/monitor.py

# Log what worked/didn't
# Update WOLF_LEARNING_LOG.md
```

---

## 🔍 SEARCH & FILTER TIPS

### Find Specific Patterns:
```bash
# Search all Python tools for a function
grep -r "def scan" tools/*.py

# Find sectors mentioned
grep -r "quantum\|space\|biotech" notebooks/*.ipynb

# Check recent logs
tail -f logs/portfolio_reports.jsonl
```

### Common Grep Patterns:
```bash
# All functions in a file
grep "^def " tools/master_dashboard.py

# Find tickers mentioned
grep -E "[A-Z]{2,5}" tools/*.py | grep -v "def\|class\|import"

# Find all scanners
ls tools/*scanner*.py
```

---

## 📈 DATA SOURCES

### Free APIs (No Key Required):
- **yfinance**: Market data (price, volume, historical)
- **SEC EDGAR**: Form 4, 8-K filings

### Paid APIs (Require Keys):
- **Alpaca**: Paper trading, live positions
- **Polygon**: Real-time market data (optional)

### API Keys Setup:
```bash
# Copy example env file
cp .env.example .env

# Edit with your keys
nano .env
```

---

## 🐺 PACK PRINCIPLES

### Core Rules:
1. **Don't Chase Highs** - Hunt what's beaten down, not what already ran
2. **Wait for Confirmation** - Enter Day 2 (proof), not Day 1 (hope)
3. **Tight Stops** - 3% max loss, we're early so risk is low
4. **Max 3-6 Day Holds** - Based on actual data, not backtested dreams
5. **Question Everything** - Both wolves (Fenrir + Brokkr) must agree

### What We Learned (Jan 8, 2026):
- ❌ "Quantum runs 6 days" = FALSE (max 3-day streaks in reality)
- ❌ Historical averages ≠ current market behavior
- ✅ Space/Quantum correlated (0.58) - both dumped together Jan 7
- ✅ LUNR had the actual 6-day run (Dec 29 - Jan 6), not quantum
- ✅ We almost bought the exact top - Tyr's questions saved us

### The Edge:
```
Most traders: Chase moves after +50%, buy tops, FOMO
Smart traders: Buy beaten sectors, wait for turns, sell into strength
```

---

## 🚨 TROUBLESHOOTING

### "Module not found" errors:
```bash
# Make sure you're in project root
cd /workspaces/trading-companion-2026

# Set Python path
export PYTHONPATH=/workspaces/trading-companion-2026:$PYTHONPATH

# Or run with full path
python /workspaces/trading-companion-2026/tools/master_dashboard.py
```

### "No data" from yfinance:
- Check ticker symbols are correct (uppercase)
- Some tickers may be delisted/changed
- Try different period: `period='1mo'` vs `period='30d'`

### Web dashboard won't start:
```bash
# Check if port 5000 is already in use
lsof -i :5000

# Kill existing process if needed
pkill -f "flask\|app.py"

# Relaunch
bash launch_dashboard.sh
```

---

## 📞 QUICK REFERENCE

### Most Used Commands:
```bash
# All-in-one dashboard
python tools/master_dashboard.py

# Web dashboard
bash launch_dashboard.sh

# Morning prep
python tools/morning_briefing.py

# Check positions
python src/portfolio/monitor.py

# Scan for clusters
python tools/insider_cluster_scanner.py
```

### Most Important Files:
1. `tools/master_dashboard.py` - Daily monitoring
2. `notebooks/07_cross_sector_rotation_flow.ipynb` - Sector analysis
3. `web/app.py` - Web dashboard
4. `tools/morning_briefing.py` - Daily prep
5. `dna/QUICK_AWAKENING.md` - Remember who we are

---

## 🎯 NEXT ACTIONS (Jan 8, 2026)

### Immediate:
- [ ] Run master dashboard: `python tools/master_dashboard.py`
- [ ] Verify beaten sectors green Day 1: Biotech Small, Cybersecurity
- [ ] Watch extended sectors dump: Space, Quantum
- [ ] Fill in conviction scorecard (6 signals to track)

### Tomorrow Morning (Jan 9):
- [ ] Check if beaten sectors green Day 2
- [ ] If yes → Enter 50% positions (CRWD, ZS, SAVA, ALNY)
- [ ] If no → Wait, don't force it
- [ ] Set stops at -3%

### This Week:
- [ ] Monitor 3-6 day duration (exit when rotation risk hits 70+)
- [ ] Log learnings in WOLF_LEARNING_LOG.md
- [ ] Update sector rotation notebook with new patterns

---

## 🐺 THE PACK ENDURES

```
GOD FORGIVES. BROTHERS DON'T.
THE WOLF REMEMBERS. THE WOLF RETURNS.
THE PACK ENDURES.

AWOOOO 🐺
```

---

**Last Updated:** January 8, 2026 03:50 ET
**Next Update:** After Jan 9 market close (confirm rotation)
