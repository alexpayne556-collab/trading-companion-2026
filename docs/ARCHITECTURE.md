# 🐺 WOLF PACK TRADING SYSTEM
## Professional Architecture - Built Founding Night 2026

---

## PROJECT STRUCTURE

```
wolf-pack-system/
│
├── .env                      # API keys (NEVER commit this)
├── .env.example              # Template for .env
├── .gitignore                # Ignore sensitive files
├── requirements.txt          # Python dependencies
├── setup.py                  # Package installation
├── README.md                 # Project documentation
│
├── config/
│   ├── __init__.py
│   ├── settings.py           # Central configuration
│   ├── watchlists.yaml       # Watchlist definitions
│   └── thresholds.yaml       # Signal thresholds
│
├── scanners/
│   ├── __init__.py
│   ├── sec_scanner.py        # 8-K/Form 4 scanner
│   ├── premarket_scanner.py  # Gap scanner
│   ├── volume_scanner.py     # Volume spike detector
│   └── form4_parser.py       # Insider trading parser
│
├── analysis/
│   ├── __init__.py
│   ├── signals.py            # Signal aggregation
│   ├── scoring.py            # Ticker scoring system
│   └── thesis.py             # Thesis generator
│
├── dashboard/
│   ├── __init__.py
│   ├── app.py                # Streamlit dashboard
│   ├── components/           # Dashboard components
│   └── static/               # CSS, images
│
├── data/
│   ├── cache/                # Cached API responses
│   ├── exports/              # ATP watchlists, reports
│   └── logs/                 # Scan logs
│
├── tools/
│   ├── __init__.py
│   ├── command_center.py     # Master orchestrator
│   ├── atp_export.py         # ATP Pro exporter
│   └── alerts.py             # Email/SMS alerts
│
├── tests/
│   ├── __init__.py
│   ├── test_scanners.py
│   └── test_signals.py
│
└── docs/
    ├── DNA.md                # Wolf Pack DNA
    ├── AI_COORDINATION.md    # AI pack guide
    └── TRADING_RULES.md      # Trading doctrine
```

---

## QUICK START

```bash
# 1. Clone and enter directory
cd wolf-pack-system

# 2. Copy env template and add your keys
cp .env.example .env
nano .env  # Add your API keys

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the dashboard
streamlit run dashboard/app.py

# 5. Or run command center
python tools/command_center.py morning
```

---

## API KEYS NEEDED

| Service | Purpose | Free Tier | Get Key |
|---------|---------|-----------|---------|
| SEC EDGAR | Filings | ✅ Free | No key needed |
| Yahoo Finance | Prices | ✅ Free | No key needed |
| Alpha Vantage | Backup data | ✅ 25/day | alphavantage.co |
| Finnhub | Real-time quotes | ✅ 60/min | finnhub.io |
| News API | Headlines | ✅ 100/day | newsapi.org |
| Polygon.io | Pro data | 💰 $29/mo | polygon.io |
| Telegram | Alerts | ✅ Free | @BotFather |
| Twilio | SMS alerts | 💰 Pay per msg | twilio.com |

**Start with FREE tier. Upgrade as needed.**

---

## CURRENT STATE (January 1, 2026)

The Wolf Pack system is currently in **OPERATIONAL** status with the following tools deployed:

### Core Tools (Deployed)
1. **Wolf Pack Scanner v2.0** - SEC filing scanner (8-K contracts + Form 4 insider)
2. **Pre-Market Scanner** - 4am overnight gap detection
3. **Form 4 Parser** - Insider trading analysis (exact dollar amounts)
4. **Backtest System** - Historical filing → price reaction analysis
5. **ATP Watchlist Generator** - Fidelity ATP Pro integration (9 sectors, 57 tickers)
6. **Command Center** - Master orchestrator (signal aggregation & briefings)

### In Development
- Streamlit dashboard (planned)
- Alert system (Telegram/SMS)
- Volume spike detector (standalone)
- Thesis generator (integrated into Command Center)

### Directory Structure
Current implementation is simpler than the full architecture:
- All scanners in root directory (not yet organized into `scanners/`)
- Tools in root directory (not yet in `tools/`)
- Watchlists in `atp_watchlists/` directory
- Documentation in root and `.github/`

**Next Steps:**
- Refactor into proper module structure
- Build Streamlit dashboard
- Add alert system
- Deploy to production schedule (4am daily runs)

---

## WOLF PACK PHILOSOPHY

1. **Hunt the FUEL not the FIRE** - Buy before the run, not during
2. **Chains OFF** - No PDT, no fear, pure execution
3. **Pack coordination** - Fenrir strategizes, Copilot builds, Perplexity scouts, Tyr executes
4. **Signal aggregation** - Multiple data sources → one score → clear decision
5. **Risk management** - 5% max risk per trade, stops BEFORE entry

---

## AWOOOO 🐺

*Built by Tyr & Fenrir*
*Founding Night - January 1, 2026*
*Wolf Pack Forever*
