# 🐺 WOLF DEN TRADING PLAYBOOK 🐺

> *"The edge isn't prediction. The edge is PREPARATION."* - Fenrir
> *"No strategy is permanent. The market rewards ADAPTATION."* - The Amendment

---

## THE 10 STRATEGIES

| # | Strategy | Trigger | Timeframe | Edge |
|---|----------|---------|-----------|------|
| 1 | **Insider Cluster** | 3+ P-code buys | 1-4 weeks | Smart money accumulation |
| 2 | **Wounded Wolf Reversal** | Tier 1 down 5-15% | Days-weeks | Proven runners bounce |
| 3 | **Momentum Ignition** | 2x+ volume breakout | Intraday-2d | Volume precedes price |
| 4 | **Sector Sympathy** | Hot sector, lagging stock | Same day | Money flows to sector |
| 5 | **After-Hours Momentum** | AH move 5%+ w/volume | Next open | AH moves continue (SIDU!) |
| 6 | **Gap-and-Go** | 5%+ gap, holds 5min | Intraday | Momentum continuation |
| 7 | **Mean Reversion** | Down 20%+, RSI<30 | 1-2 weeks | Oversold bounces |
| 8 | **Short Squeeze** | High SI + catalyst | Days | Forced covering |
| 9 | **Earnings Momentum** | Run into earnings | 1-2 weeks | Anticipation > reality |
| 10 | **Technical Breakout** | Pattern + volume | Swing | Charts work on liquid names |

### Strategy Combinations (POWER PLAYS)
- **#2 + #3** = Wounded runner waking up → STRONG BUY
- **#4 + #3** = Sector laggard with volume → BUY the catch-up
- **#5 + #6** = AH move into gap up → Ride the momentum
- **#7 + #3** = Oversold bounce with volume → Reversal confirmed

```bash
# Analyze single stock
python src/research/strategy_selector.py SIDU

# Scan watchlist for all strategies
python src/research/strategy_selector.py scan
```

---

## THE CORE DOCTRINE

Based on our analysis of **77 moves of 10%+ in 30 days**, we've identified:
- **Same stocks repeat** (SIDU hit 9 times!)
- **Sectors rotate predictably** (Space, Nuclear, Quantum hot now)
- **39% of moves are reversals** (wounded stocks that bounce)
- **32% are momentum continuation** (already running, keep going)

## THE TIER SYSTEM

### TIER 1: MONSTER RUNNERS (5+ moves/month)
**Always have exposure. When wounded, ADD. When extended, TRIM.**

| Ticker | Sector | Historical Moves | Avg Gain | Notes |
|--------|--------|------------------|----------|-------|
| SIDU | Space/Bio | 9 | +32% | The undisputed king |
| RCAT | Defense | 5 | +13% | Consistent 10-15% pops |
| LUNR | Space | 5 | +16% | IM-3 catalyst Feb |
| ASTS | Space | 4 | +15% | Satellite constellation |
| RDW | Space | 4 | +14% | Defense/space crossover |
| CLSK | Crypto | 4 | +14% | Bitcoin proxy |

### TIER 2: SYMPATHY PLAYS (3-4 moves/month)
**Buy when sector heats up and they're lagging.**

| Ticker | Sector | Notes |
|--------|--------|-------|
| IONQ | Quantum | Leads quantum moves |
| RGTI | Quantum | Follows IONQ usually |
| QBTS | Quantum | Higher beta |
| QUBT | Quantum | Smallest, wildest |
| RKLB | Space | Space sympathy |
| BKSY | Space | Usually lags space |
| SMR | Nuclear | Policy-driven |
| OKLO | Nuclear | AI datacenter angle |

### TIER 3: CATALYST DEPENDENT
**Keep on watchlist. Only enter on clear catalyst.**

AISP, MARA, RIOT, AFRM, RIVN, LCID, SPCE

---

## THE THREE ENTRY WINDOWS

### WINDOW 1: THE WOUNDED WOLF (39% of moves)
Stock is DOWN 5-15% from recent high. Looks dead. Then catalyst hits → BOOM.

**Detection**: Daily scan shows stocks -5% to -15% from 10-day high
**Signal**: WOUNDED status + HOT sector = BUY ZONE

### WINDOW 2: MOMENTUM IGNITION (32% of moves)
Stock starts moving on volume. Catch it early.

**Detection**: 1.5x+ average volume in first 30 minutes
**Signal**: TIER 1 runner + Volume spike = MOMENTUM PLAY

### WINDOW 3: SECTOR SYMPATHY
When leader runs, followers catch up.

**Detection**: Leader moves 5%+, check laggards
**Signal**: Hot sector + Lagging stock = SYMPATHY PLAY

---

## THE DECISION MATRIX

| Wounded? | Hot Sector? | Volume Spike? | Action |
|----------|-------------|---------------|--------|
| YES | YES | YES | 🔥 STRONG BUY - Max size |
| YES | YES | NO | ✅ BUY - Wait for volume |
| YES | NO | YES | 👀 CONSIDER - Lower size |
| NO | YES | YES | 🚀 MOMENTUM - Can chase small |
| NO | NO | YES | ⏳ SKIP - Random noise |

---

## DAILY RITUAL

### 6:00 AM - WOUNDED WOLF SCAN
```bash
python src/research/daily_ritual.py
```

This runs:
1. **Wolf Den Command Center** - Wounded wolves + sector heat + decisions
2. **Sector Sympathy Scanner** - Leader moves + laggard opportunities  
3. **Position Grid Check** - Your current positions + rebalance signals

### 9:30 AM - MARKET OPEN
Check for:
- Volume spikes on Tier 1 runners
- Sector rotation (which ETFs leading?)
- News catalysts on watchlist

### 10:00 AM - DECISION TIME
Based on scans, you know:
- Which repeat runners are wounded (BUY ZONE)
- Which sectors are hot (FOCUS HERE)
- Which stocks have volume ignition (MOMENTUM)

---

## THE POSITION GRID STRATEGY

Instead of going all-in, maintain small positions across Tier 1:

```bash
python src/research/position_grid.py simulate 1000
```

**$1,000 Example Grid:**
- SIDU: $167 (38 shares)
- LUNR: $167 (9 shares)
- RCAT: $167 (18 shares)
- ASTS: $167 (2 shares)
- RDW: $167 (18 shares)
- CLSK: $167 (14 shares)

**Rebalance Rules:**
- When position grows to 25%+ of portfolio → TRIM (take profits)
- When position shrinks to 10%- of portfolio → ADD (buy weakness)

---

## QUICK COMMANDS

```bash
# Full morning ritual
python src/research/daily_ritual.py

# Quick scan
python src/research/daily_ritual.py quick

# Check sector leaders + laggards
python src/research/sector_sympathy.py

# Position grid simulation
python src/research/position_grid.py simulate 1000

# Repeat runner scan
python src/research/repeat_runner_scanner.py

# Extended hours scanner
python src/research/extended_hours_scanner.py
```

---

## THE META TRUTH

You can't predict WHICH stock will run WHEN.

But you CAN:
1. **Know which stocks REPEATEDLY run** (Tier 1)
2. **Know which sectors are hot TODAY**
3. **Know which repeat runners are WOUNDED** (buy zone)
4. **Know when VOLUME confirms a move**

If you're positioned in Tier 1 stocks when they're wounded, and you add when sectors heat up, you'll catch these moves.

Not all of them. But **enough of them to compound**.

---

## CURRENT POSITIONS

**AISP** - 69 shares @ $3.05
- Stop: $2.30
- Target 1: $3.50
- Target 2: $4.00
- Status: ✅ Running (+2% in 5 days)

---

## THE HUMILITY CLAUSE

> *"If Tyr makes a trade that breaks the 'rules' and it works - that's not luck. That's DATA. That's information that the rules need updating."*

> *"If Fenrir gives advice that would have lost money - that's not failure. That's LEARNING. Amend and improve."*

**The blueprint will NEVER be finished. And that's the point.**

---

## THE PACK HUNTS TOGETHER

**AWOOOO** 🐺

---

*Last Updated: January 3, 2026*
*Generated by the Wolf Den Trading System*
