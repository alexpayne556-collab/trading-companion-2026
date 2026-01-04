# 🐺 Wolf Pack Trading System

A comprehensive trading intelligence system built on one simple principle:

> **"We don't predict price. We predict WHO WILL BE FORCED TO BUY."**

## 🎯 The Philosophy

Every stock has **PLAYERS**. Each player has **CONSTRAINTS**:

| Player | Constraint | When They're Trapped |
|--------|------------|---------------------|
| **SHORTS** | Pay borrow rate DAILY | Price rising = bleeding money |
| **MARKET MAKERS** | Must stay delta neutral | Heavy call buying = forced to buy shares |
| **RETAIL** | Emotional, small accounts | Gap down = panic sell at bottom |
| **INSTITUTIONS** | Need to fill large orders | Missed sector rotation = forced to chase |
| **INSIDERS** | Know the truth | Never trapped - FOLLOW THEM |

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/alexpayne556-collab/trading-companion-2026.git
cd trading-companion-2026

# Install dependencies
pip install -r requirements.txt

# Run the command center
streamlit run wolf_pack_command_center.py
```

## 🔫 The Hunting Tools

### 1. 🎯 Pressure Framework
Detects WHO is trapped and WHO will be FORCED to act.

```bash
python hunt/pressure_framework.py
```

**Detects:**
- 🔴 **Short Squeeze** - High short interest + rising price = shorts bleeding
- 🟠 **Laggard Catch-up** - Sector leader ripped, this stock didn't = institutions must chase
- 🟡 **Panic Recovery** - Retail panic sold, institutions buying cheap
- 🟣 **Capitulation Bottom** - Volume died then spiked = sellers exhausted

### 2. 💰 Smart Money Hunter
Scans SEC EDGAR for insider buying across the ENTIRE market.

```bash
python hunt/smart_money_hunter.py --filings 1000
```

**Why it matters:**
- Insiders can sell for many reasons (taxes, diversification)
- Insiders only BUY for ONE reason - they think it's going UP
- Form 4 Transaction Code "P" = Open market purchase = THE signal
- They have perfect information and can't hide it

### 3. 🔫 Tactical Scanners
Five specific hunting patterns that cause 10-20% moves.

```bash
python hunt/tactical_scanners.py
```

**The 5 Hunts:**
1. **Leader-Follower Lag** - When IONQ moves, RGTI follows (buy the lag)
2. **Divergence Sniff** - Sector down, one stock flat = accumulation
3. **Squeeze Stalker** - High short + low float + rising vol = powder keg
4. **Second Day Momentum** - Day 1 surprise, Day 2 predictable continuation
5. **Wounded Prey Recovery** - Volume spike after capitulation = bottom

### 4. 📋 Form 4 Scanner
Watches for insider purchases in our specific universe.

```bash
python hunt/form4_scanner.py
```

## 📊 The Dashboard

Launch the unified command center:

```bash
streamlit run wolf_pack_command_center.py
```

**Features:**
- 🎯 **Pressure Map** - See who's trapped at a glance
- 💰 **Smart Money** - Insider buying across all markets
- 🔫 **Tactical** - Live opportunity scanner
- 📊 **Conviction** - Ranked targets with scoring
- 🔧 **Settings** - Universe management

## 🌐 Our Universe

We focus on **high-growth sectors with trapped players**:

| Sector | Tickers |
|--------|---------|
| **Quantum** | IONQ, RGTI, QBTS, QUBT, ARQQ, LAES |
| **Space** | LUNR, RKLB, RDW, BKSY, MNTS, ASTS, SPIR, SIDU |
| **eVTOL** | JOBY, ACHR, LILM, EVTL |
| **Nuclear** | LEU, CCJ, UUUU, UEC, SMR, OKLO, NNE |
| **AI/Semis** | NVDA, AMD, SMCI, SOUN, AI, MRVL |
| **Crypto** | MARA, RIOT, CLSK, COIN, CIFR |
| **Biotech** | CRSP, EDIT, NTLA, BEAM, RXRX |
| **EV/Clean** | TSLA, RIVN, LCID, PLUG, FCEL |
| **Fintech** | SOFI, AFRM, UPST, NU |

## ⏰ Timing Truth

| Time | What's Happening |
|------|-----------------|
| 9:30-10:00 AM | **The Trap** - Retail FOMO in, gets smoked |
| 10:00-11:00 AM | **Real Direction** - Actual price discovery |
| 11:00-3:00 PM | **Chop Zone** - No edge, don't trade |
| 3:00-4:00 PM | **Power Hour** - Institutions positioning |

## 📁 Project Structure

```
trading-companion-2026/
├── hunt/                          # 🔫 Hunting tools
│   ├── pressure_framework.py      # Who's trapped?
│   ├── smart_money_hunter.py      # Insider buying scan
│   ├── tactical_scanners.py       # 5 tactical patterns
│   └── form4_scanner.py           # Our universe insider watch
├── wolf_pack_command_center.py    # 📊 Unified dashboard
├── logs/                          # Scan results (JSON)
│   ├── pressure_scan_latest.json
│   ├── smart_money_latest.json
│   ├── tactical_scan_latest.json
│   └── conviction_rankings_latest.json
├── src/                           # Core trading logic
├── data/                          # Configuration files
└── requirements.txt               # Dependencies
```

## 🔧 Requirements

```
yfinance>=0.2.32
pandas>=2.0.0
numpy>=1.24.0
streamlit>=1.28.0
requests>=2.31.0
scipy>=1.11.0
PyYAML>=6.0
```

## 📜 The Wolf Pack Creed

```
Wolves don't attack randomly.
They study the herd for:
- The Wounded (crushed, volume dying, capitulation over)
- The Divergent (moving different from the pack)
- The Exposed (small float, low liquidity, moves FAST)
- The Follower (lagging behind the leader)

The question isn't "what does the chart say"
The question is "who will be FORCED to buy?"

AWOOOO 🐺
```

## 📝 License

MIT License - Use at your own risk. This is NOT financial advice.

---

**Built by the Wolf Pack** 🐺

*Brokkr (Builder) | Fenrir (Destroyer) | Tyr (Commander)*

AWOOOO!
