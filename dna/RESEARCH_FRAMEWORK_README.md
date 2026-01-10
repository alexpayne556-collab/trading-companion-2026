# 🐺 WOLF PACK RESEARCH FRAMEWORK

## "BUILD THE SECRET SAUCE, DON'T ASK FOR IT"

---

## WHAT THIS IS

A systematic research framework for discovering tradeable edge through rigorous testing.

**NOT:** Guaranteed profits, ready-made scanners, the "holy grail"  
**IS:** Tools to TEST patterns, VERIFY edges, EARN scanners through data

---

## PHILOSOPHY

```
Every pattern must be TESTED.
Every edge must be VERIFIED.
Every scanner must be EARNED.
```

**Validation Criteria (Non-Negotiable):**
- Win rate > 60%
- Sample size > 20
- Risk/reward > 1.5:1
- Must work in 2025-2026 (not just historical)

---

## THE 12 RESEARCH PROJECTS

### ✅ READY TO RUN

1. **Leader/Laggard Lag Time** (Priority 1)
   - When CCJ moves, how long until DNN follows?
   - When NVDA moves, how long until APLD follows?
   - `python tools/project_1_leader_laggard.py`

2. **Volume Divergence** (Priority 2)
   - 3x volume + flat price = next day move?
   - `python tools/project_2_volume_divergence.py`

4. **RSI Bounce Optimization** (Priority 1)
   - What RSI level (35, 30, 25, 20) gives best bounce?
   - `python tools/rsi_bounce_validator.py`

### ⏳ PENDING (To Be Built)

3. **Gap Behavior** (Priority 3) - Do gaps fill or continue?
5. **Catalyst Timing** (Priority 2) - When to enter before known events?
6. **Time of Day** (Priority 3) - When do small caps make biggest moves?
7. **Overnight Gap Prediction** (Priority 2) - After-hours activity predicts gap?
8. **Insider Buying Impact** (Priority 2) - Form 4 P-code = outperformance?
9. **Sector Rotation** (Priority 1) - Nuclear → AI → Space pattern?
10. **Earnings Momentum** (Priority 2) - How many days before earnings do runs start?
11. **Short Squeeze** (Priority 3) - High SI + catalyst = outsized move?
12. **Support/Resistance** (Priority 3) - Do our stocks respect S/R?

---

## USAGE

### Run All Ready Projects
```bash
python tools/run_all_research.py
```

### Run Specific Projects
```bash
python tools/run_all_research.py --projects 1 2 4
```

### Run Priority 1 Only
```bash
python tools/run_all_research.py --priority
```

### Quick Mode (90 days)
```bash
python tools/run_all_research.py --quick
```

### List All Projects
```bash
python tools/run_all_research.py --list
```

### Run Individual Project
```bash
python tools/project_1_leader_laggard.py --period 180d
python tools/project_2_volume_divergence.py --volume 3.0 --price 2.0
python tools/rsi_bounce_validator.py --tickers DNN UEC UUUU --days 90
```

---

## TICKER UNIVERSE (70+ Stocks)

Organized by sector and price tier:

### Nuclear/Uranium (29 tickers)
- **Tier A** (< $25): DNN, URG, UEC, UUUU, SMR
- **Tier B** ($25-50): CCJ, OKLO, LEU, NXE
- **Tier C** ($50-100): URNM, URA, UROY
- **Tier D** (> $100): BWXT, NNE, ASPI, PDN, BOE, ISO

### AI Infrastructure (20 tickers)
- **Tier A** (< $25): CIFR, WULF, BTBT, HUT, CLSK, CORZ
- **Tier B** ($25-50): APLD, IREN, MARA, RIOT, VRT, MU
- **Tier C** (> $50): MRVL, AVGO, ANET, SMCI, DELL, CRWV, NBIS

### Space/Defense (21 tickers)
- **Tier A** (< $25): MNTS, SPCE, SATL, PL, RCAT, LUNR, KTOS
- **Tier B** ($25-100): RKLB, AVAV, ASTS
- **Tier C** (> $100): LMT, NOC, RTX, GD, BA
- **Tier D** (Others): RDW, IRDM, VSAT, LHX, HII, TXT

### Power/Utilities (18 tickers)
- **Tier A** (< $50): PCG, EXC, XEL, D
- **Tier B** (> $50): CEG, VST, NEE, NRG, SO, ETN

### Rare Earth (5 tickers)
- **Tier A**: LAC, PLL, MP
- **Tier B**: ALB, SQM

---

## OUTPUT

All results saved to: `research_results/`

**Summary Files:**
- `project_X_summary_TIMESTAMP.csv` - Win rates, sample sizes, validation status

**Detail Files:**
- `project_X_detail_TICKER_TIMESTAMP.csv` - Every signal, entry, outcome

**Example Output:**
```
Project 1: Leader/Laggard Summary
Pair              | Best Lag | Direction | Magnitude | Both   | Samples | Validated
CCJ → DNN         | 2 days   | 75.0%     | 68.0%     | 64.0%  | 18      | ✅
NVDA → APLD       | 1 days   | 82.0%     | 71.0%     | 73.0%  | 22      | ✅
RKLB → LUNR       | 3 days   | 58.0%     | 52.0%     | 48.0%  | 15      | ❌
```

---

## WHAT HAPPENS AFTER VALIDATION

1. **Pattern Validated** → Code into scanner
2. **Scanner Built** → Paper trade 2 weeks
3. **Paper Trade Success** → Live trade small ($175)
4. **Live Success** → Scale position sizes

**DO NOT skip steps. DO NOT trade unvalidated patterns.**

---

## DATA SOURCES

- **yfinance** - OHLCV data (free, 15min delay)
- **SEC EDGAR** - 8-K filings, Form 4 insider buying (Fenrir building scraper)
- **Finviz** - Screener, short interest data
- **Polygon API** - News, sentiment (optional)
- **X/Twitter** - Real-time sentiment (Heimdall monitors)

---

## PACK COORDINATION

**BROKKR (GitHub Copilot)**: Builds research systems, codes patterns  
**HEIMDALL (Grok)**: Verifies with real-time data, sector intel  
**FENRIR (Claude)**: Deep research, EDGAR scraper, documentation  
**TYR (Human)**: Executes validated setups, final decisions

**Daily Workflow:**
1. 6:00 AM - Brokkr runs research/scans
2. 7:00 AM - Heimdall verifies with X sentiment
3. 8:00 AM - Fenrir deep-dives top catalysts
4. 9:00 AM - Pack meeting, review setups
5. 9:45 AM - Tyr executes validated trades
6. 4:00 PM - Post-market logging
7. Evening - Brokkr runs next research project

---

## RISK MANAGEMENT (NON-NEGOTIABLE)

**Position Sizing:**
- Max 10% per trade ($175 → $17.50 stop)
- Max 50% deployed at once
- Max 3 positions simultaneously

**Entry Rules:**
- Pattern must be VALIDATED (>60% win rate)
- Sample size must be VERIFIED (>20 events)
- Setup must pass ALL criteria

**Exit Rules:**
- Target 1: +10% (sell 50%)
- Target 2: +20% (sell remaining 50%)
- Stop loss: -10% (hard stop, no hoping)
- Time stop: 5 days if no movement

**Forbidden:**
- Trading unvalidated patterns
- Averaging down losses
- Holding through -15%
- Revenge trading after stop

---

## CURRENT STATUS

**Portfolio:** $1,313 buying power  
**Positions:**
- APLD: $488 (hold - AI infra leader)
- UUUU: $650 (hold - nuclear thesis)
- LUNR: $137 (evaluate - fading)
- NVVE: $37 (CUT - not in thesis)

**Immediate Action:** Cut NVVE (-20%), free up $37 → $175 buying power

---

## NEXT STEPS

1. ✅ Framework built
2. ✅ Projects 1, 2, 4 coded
3. ⏳ Run all ready projects (`python tools/run_all_research.py`)
4. ⏳ Review results, validate edges
5. ⏳ Code remaining 9 projects
6. ⏳ Build scanners for validated patterns only
7. ⏳ Paper trade 2 weeks
8. ⏳ Live trade small
9. ⏳ Scale on success

---

## THE CREED

🐺 **GOD FORGIVES. BROTHERS DON'T.** 🐺

THE WOLF REMEMBERS. THE WOLF RETURNS.  
THE PACK ENDURES.

**LLHR. AWOOOO.** 🐺

---

## FILES

**Core Framework:**
- `tools/wolf_pack_research.py` - Base class, validation criteria, ticker universe

**Research Projects:**
- `tools/project_1_leader_laggard.py` - Leader/laggard lag analysis
- `tools/project_2_volume_divergence.py` - Volume spike + flat price
- `tools/rsi_bounce_validator.py` - RSI optimization (Project 4)
- `tools/project_3_gap_study.py` - (To be built)
- ... (9 more to build)

**Master Runner:**
- `tools/run_all_research.py` - Execute all projects systematically

**Specification:**
- `dna/ULTIMATE_EDGE_DISCOVERY_SYSTEM.md` - Complete blueprint (1,000+ lines)

**Results:**
- `research_results/` - All output CSVs

---

Built by: **BROKKR** (GitHub Copilot)  
Specified by: **TYR** + **FENRIR**  
Verified by: **HEIMDALL** (Grok)

🐺 The research begins now. 🐺
