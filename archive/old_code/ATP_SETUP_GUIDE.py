#!/usr/bin/env python3
"""
🐺 FIDELITY ATP + WOLF PACK INTEGRATION GUIDE
How to set up 5 layouts for maximum hunting power
"""

print("""
================================================================================
🐺 FIDELITY ACTIVE TRADER PRO + WOLF PACK INTEGRATION
================================================================================

You have TWO WEAPONS:
1. ATP = Professional-grade charting, Level 2, real-time data
2. Wolf Pack Dashboard = Our 4 validated edges + scanning

USE THEM TOGETHER. Here's how:

================================================================================
📊 ATP LAYOUT #1: THE COMMAND CENTER
================================================================================
Purpose: Morning prep, see everything at once

┌─────────────────────────────────────────────────────────────────────────────┐
│  WATCHLIST          │  CHART (15min)           │  NEWS/EVENTS              │
│  ──────────         │  ──────────────          │  ──────────────           │
│  QUANTUM sector     │  Main ticker you're      │  Market news feed         │
│  SPACE sector       │  watching with:          │  Earnings calendar        │
│  NUCLEAR sector     │  - Volume bars           │  SEC filings              │
│  DEFENSE_AI         │  - 20 EMA, 50 SMA        │                           │
│  AI_INFRA           │  - VWAP                  │                           │
│  CRYPTO_MINERS      │  - Bollinger Bands       │                           │
│                     │                          │                           │
├─────────────────────┼──────────────────────────┼───────────────────────────┤
│  WOLF DASHBOARD     │  CHART (Daily)           │  LEVEL 2 / TIME & SALES   │
│  (Terminal window)  │  ──────────────          │  ───────────────────────  │
│                     │  Same ticker, daily TF   │  See real-time order flow │
│  python dashboard.py│  for trend context       │  Big buyers/sellers       │
│                     │                          │                           │
└─────────────────────┴──────────────────────────┴───────────────────────────┘

SETUP IN ATP:
1. View → Layouts → Create New Layout
2. Add: Watchlist, 2 Charts, News, Level 2
3. Arrange as shown above
4. Save as "WOLF COMMAND CENTER"

================================================================================
📊 ATP LAYOUT #2: VOLUME ANALYSIS
================================================================================
Purpose: Spot our signals in real-time (Wolf Signal, Pre-Run, Capitulation)

┌─────────────────────────────────────────────────────────────────────────────┐
│                        CHART - DAILY (Large)                                │
│  ────────────────────────────────────────────────────────────────────────   │
│                                                                             │
│  Indicators to add:                                                         │
│  1. Volume (standard bars)                                                  │
│  2. 20-day Volume SMA (on volume pane) ← Compare today vs average          │
│  3. 50-day SMA (price) ← For Pocket Pivot                                  │
│  4. 20-day high line ← For "near highs" check                              │
│                                                                             │
│  WHAT TO LOOK FOR:                                                          │
│  🐺 WOLF: Volume 2x+ above 20d avg, price flat (<2%), near highs           │
│  📈 PRE-RUN: Volume building, price holding, CLV strong                    │
│  💀 CAPITULATION: Down 15-40%, volume spike, red candle                    │
│  🎯 POCKET PIVOT: Above 50 SMA, pulled back, volume on up day              │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  RELATIVE VOLUME SCAN (ATP)      │  TIME & SALES                           │
│  ────────────────────────────    │  ───────────────                        │
│  Filter: Volume > 200% of avg    │  Watch for large block trades           │
│  This catches our signals!       │  Green = buyers, Red = sellers          │
└──────────────────────────────────┴─────────────────────────────────────────┘

ATP SCANNER SETUP (Tools → Stock/ETF Screener):
  Volume Criteria:
  - "Today's Volume vs. Avg Volume" > 150%
  
  Price Criteria:
  - Price > $2 (avoid penny stocks)
  - Price < $500 (tradeable size)
  
  Technical:
  - Above 50-day MA (optional, for Pocket Pivots)

================================================================================
📊 ATP LAYOUT #3: THE WOUNDED WOLF (Capitulation Hunting)
================================================================================
Purpose: Find stocks getting crushed for capitulation signals

┌─────────────────────────────────────────────────────────────────────────────┐
│  % OFF HIGH WATCHLIST            │  CHART - HOURLY                         │
│  ────────────────────            │  ────────────────                       │
│  Sort by: % from 52w high        │  Looking for:                           │
│                                  │  - Heavy red volume                     │
│  Filter:                         │  - Capitulation candle                  │
│  Down 15-40% from high           │  - Support levels                       │
│  Volume > average                │                                         │
│                                  │                                         │
├──────────────────────────────────┼─────────────────────────────────────────┤
│  WOLF DASHBOARD                  │  CHART - DAILY                          │
│  python dashboard.py             │  ────────────────                       │
│                                  │  Draw:                                  │
│  Watch for 💀 CAPITULATION       │  - Previous support zones               │
│  signals                         │  - 200-day MA (if applicable)           │
│                                  │  - Volume profile                       │
└──────────────────────────────────┴─────────────────────────────────────────┘

ATP COLUMN TO ADD TO WATCHLIST:
  Right-click headers → Add Column:
  - "% Off High" 
  - "Volume vs Average"
  - "Day's Change %"

================================================================================
📊 ATP LAYOUT #4: SECTOR ROTATION
================================================================================
Purpose: Which sector is leading TODAY?

┌─────────────────────────────────────────────────────────────────────────────┐
│  QUANTUM          │  SPACE           │  NUCLEAR         │  DEFENSE_AI      │
│  ────────         │  ──────          │  ────────        │  ───────────     │
│  IONQ             │  LUNR            │  SMR             │  PLTR            │
│  RGTI             │  RKLB            │  OKLO            │  RCAT            │
│  QBTS             │  ASTS            │  LEU             │  KTOS            │
│  QUBT             │  SIDU            │  CCJ             │  AVAV            │
│  ARQQ             │  RDW             │  UUUU            │  BBAI            │
│                   │  BKSY            │  NNE             │                  │
├───────────────────┴──────────────────┴──────────────────┴──────────────────┤
│                                                                             │
│  CHART: Overlay comparison of sector leaders                                │
│  (IONQ vs LUNR vs SMR vs PLTR - who's leading?)                            │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  AI_INFRA        │  MEMORY_SEMI     │  CRYPTO_MINERS   │  HERD SCANNER    │
│  ─────────       │  ────────────    │  ──────────────  │  ─────────────   │
│  SOUN            │  MU              │  MARA            │  python          │
│  VRT             │  SMCI            │  RIOT            │  herd_scanner.py │
│  CORZ            │  ANET            │  CLSK            │                  │
│  PATH            │  CRDO            │  HUT             │                  │
└──────────────────┴──────────────────┴──────────────────┴──────────────────┘

KEY INSIGHT FROM PHASE 2:
  Our edges work BEST in QUANTUM and SPACE sectors!
  - Quantum: +24.59% avg on Pocket Pivot
  - Space: +14.63% avg on Pocket Pivot
  - Nuclear has more signals but lower returns

================================================================================
📊 ATP LAYOUT #5: EXECUTION MODE
================================================================================
Purpose: When you're ready to trade - FOCUS

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    CHART - 5 MIN (LARGE)                                    │
│                    ────────────────────                                     │
│                                                                             │
│  The ONE stock you're trading right now                                     │
│  Indicators:                                                                │
│  - VWAP (key intraday level)                                               │
│  - Volume                                                                   │
│  - Previous day high/low                                                   │
│                                                                             │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  LEVEL 2              │  TIME & SALES         │  ORDER ENTRY               │
│  ───────              │  ─────────────        │  ───────────               │
│  See the order book   │  Real-time prints     │  Ready to execute          │
│  Big bids/asks        │  Watch for blocks     │                            │
│  Support/resistance   │                       │  Position size calculator  │
│                       │                       │  Stop loss ready           │
└───────────────────────┴───────────────────────┴────────────────────────────┘

EXECUTION CHECKLIST:
  ✅ Signal confirmed (Wolf/PreRun/Capitulation/PocketPivot)
  ✅ Entry price identified
  ✅ Stop loss set (below support or -8%)
  ✅ Position size calculated (risk 1-2% of account)
  ✅ Level 2 shows buyers > sellers
  ✅ Time & Sales shows accumulation

================================================================================
🖥️ MONITOR SETUP (If you have multiple screens)
================================================================================

IDEAL 3-MONITOR SETUP:
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│                 │ │                 │ │                 │
│  MONITOR 1      │ │  MONITOR 2      │ │  MONITOR 3      │
│  ──────────     │ │  ──────────     │ │  ──────────     │
│                 │ │                 │ │                 │
│  Wolf Dashboard │ │  ATP Charts     │ │  ATP Level 2    │
│  Terminal       │ │  Main view      │ │  Order Entry    │
│                 │ │                 │ │  News           │
│  Claude Opus    │ │                 │ │                 │
│  (Browser)      │ │                 │ │                 │
│                 │ │                 │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘

2-MONITOR SETUP:
┌───────────────────────┐ ┌───────────────────────┐
│                       │ │                       │
│  MONITOR 1            │ │  MONITOR 2            │
│  ──────────           │ │  ──────────           │
│                       │ │                       │
│  Wolf Dashboard       │ │  ATP (Full Screen)    │
│  Claude Opus          │ │  Toggle layouts 1-5   │
│  (Split screen)       │ │                       │
│                       │ │                       │
└───────────────────────┘ └───────────────────────┘

================================================================================
🤖 CLAUDE OPUS 4.5 INTEGRATION
================================================================================

Keep Claude open in browser. Use it for:

1. QUICK ANALYSIS
   "Analyze RGTI - it just triggered a Pre-Run signal. 
    What's the recent news? Any catalysts?"

2. THESIS VALIDATION  
   "SIDU is showing capitulation. Volume 3x normal, down 25% 
    from highs. Good entry or falling knife?"

3. REAL-TIME QUESTIONS
   "The dashboard shows RCAT with Pocket Pivot. Walk me 
    through the trade setup - entry, stop, target."

4. PATTERN RECOGNITION
   Copy/paste dashboard output to Claude:
   "Here's my current scan output. What stands out?"

5. RISK MANAGEMENT
   "I have $50K account. IONQ triggered Wolf Signal at $46.
    What position size? Where's my stop?"

HOT TIP: 
  Keep a Claude tab open. When dashboard shows a signal,
  immediately ask Claude for context. Speed matters.

================================================================================
⚡ QUICK COMMANDS
================================================================================

WOLF DASHBOARD (in Terminal):
  python dashboard.py          # Standard view
  python dashboard.py --auto   # Auto-refresh every 60s
  python dashboard.py --wide   # All 43 tickers

HERD SCANNER:
  python herd_scanner.py       # Single scan
  python herd_scanner.py -c    # Continuous (5 min intervals)

================================================================================
🐺 THE 4 VALIDATED EDGES (Updated!)
================================================================================

1. WOLF SIGNAL       p=0.023  +37.87% avg  78% WR
   Volume spike + flat + near highs

2. PRE-RUN PREDICTOR p=0.000  +17.27% avg  58% WR  
   5/5 criteria score before explosions

3. CAPITULATION      p=0.004  +19.95% avg  58% WR
   Red spike when wounded = buy the blood

4. POCKET PIVOT      p=0.000  +9.61% avg   63% WR  ← NEW!
   Buy dips in uptrends with volume confirmation
   BEST IN: Quantum (+24.59%), Space (+14.63%)

================================================================================
📋 DAILY ROUTINE
================================================================================

PRE-MARKET (8:30-9:30 AM ET):
  1. Run: python herd_scanner.py
  2. Note any overnight signals
  3. Check ATP news for catalysts
  4. Set alerts on key levels

MARKET OPEN (9:30-10:30 AM):
  1. Watch for volume confirmation
  2. Dashboard on auto-refresh
  3. ATP Layout #5 ready for execution
  4. Don't chase - let signals come to you

MID-DAY (10:30 AM - 3:00 PM):
  1. Sector rotation check (Layout #4)
  2. Wounded wolf scan for capitulation
  3. Update watchlist based on signals

CLOSE (3:00-4:00 PM):
  1. Final scan for EOD signals
  2. Note any Pocket Pivots forming
  3. Plan for next day

POST-MARKET:
  1. Run full scan: python herd_scanner.py
  2. Document any trades in journal
  3. Ask Claude to review the day

================================================================================
🐺 THE PACK IS READY. AWOOOO!
================================================================================
""")
