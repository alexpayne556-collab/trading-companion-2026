# 🐺 SYSTEM MECHANICS KNOWLEDGE BASE
## What the Wolf Pack Has Learned About Market Plumbing

*Updated: Jan 7, 2026 - Research Session*

---

## THE CORE THESIS

> **"The edge isn't in predicting human behavior (unpredictable). The edge is in understanding MECHANICAL, FORCED actions."**

---

## 1. MARKET MAKERS - THE HOUSE

### What They Are
- Private firms that MUST provide continuous liquidity (bid + ask quotes)
- Major players: **Citadel Securities, Virtu, GTS, Wolverine**
- They don't trade on opinions - they profit from the SPREAD

### How They Profit
- Buy at bid, sell at ask → pocket the spread
- They MUST stay "delta neutral" (no directional risk)
- They hedge constantly to avoid directional exposure

### Why This Matters (FORCED ACTIONS)
- **When retail buys calls** → MM sells calls → MM MUST buy stock to hedge
- **When retail sells calls** → MM buys calls back → MM MUST sell stock
- **Options near expiration with high gamma** → MM hedging becomes VIOLENT

### The Key Insight
> MMs don't WANT to move the stock. They're FORCED to when they sell you options.

---

## 2. GAMMA & OPTIONS MECHANICS - THE LEVERAGE MACHINE

### Definitions
- **Delta**: How much option price moves per $1 stock move
- **Gamma**: How much delta CHANGES per $1 stock move
- **Gamma is HIGHEST**: At-the-money + near expiration

### The Gamma Squeeze Mechanics
1. Retail buys OTM calls heavily
2. MMs sell those calls → must hedge by buying stock
3. Stock rises from MM buying
4. Delta increases → MMs must buy MORE stock
5. Stock rises more → Delta increases more → FEEDBACK LOOP
6. **This is a MECHANICAL, FORCED action** - MMs have no choice

### Critical Insight
> "65% of PFOF revenue comes from OPTIONS" - MMs make most money on options
> This means option flow MATTERS MORE than stock flow for predicting moves

### When Gamma Is Dangerous
- Highest 24-48 hours before expiration
- Highest at strike prices near current price (ATM)
- High open interest at specific strikes = potential "magnets"

---

## 3. SHORT SQUEEZE MECHANICS - FORCED COVERING

### What Creates Forced Buying
- Short sellers borrow shares to sell → MUST return them eventually
- If price rises → losses mount → eventually FORCED to cover
- Covering = buying → pushes price higher → forces more covering

### Key Metrics
- **Short Interest**: % of float sold short (>20% = elevated)
- **Days to Cover**: Short shares ÷ avg daily volume
  - 5+ days = vulnerable to squeeze
  - 10+ days = highly vulnerable
- **Cost to Borrow**: If rising, shorts are stressed

### The Mechanics
1. High short interest + catalyst = price spikes
2. Short sellers face margin calls
3. FORCED to buy at ANY price
4. Their buying creates more buying
5. **This is NOT discretionary** - brokers liquidate them if they don't

### Historical Examples
- **VW 2008**: Porsche owned 75%, shorts squeezed to €999
- **Tesla 2020**: 18% short interest, stock 400%+, shorts lost $40B
- **GME 2021**: 100%+ short interest, $5 → $500

---

## 4. OPENING AUCTION - THE DAILY RESET

### How It Works (Nasdaq "Opening Cross")
- Pre-market orders accumulate from 7:30am
- At 9:28am, order imbalances published
- Buyers and sellers matched via auction
- **DMM (Designated Market Maker) sets opening price**
- At 9:30am, trading begins at auction-cleared price

### Why Morning Dip Happens (V-Pattern Theory)
Possible causes:
1. **Pre-market euphoria** → opening price set too high
2. **Overnight limit orders** → flood market at open
3. **Day traders sell overnight positions** → morning pressure
4. **MMs adjusting overnight inventory** → mechanical rebalancing
5. **Stop-loss cascades** → triggered by overnight gap

### What We Still Don't Know
- WHY exactly does recovery happen?
- Is it MM-driven or retail FOMO-driven?
- Is the timing consistent (first 30 min dip, 10am recovery)?

---

## 5. DARK POOLS - THE HIDDEN ICEBERG

### What They Are
- Private exchanges for large institutional orders
- ~40% of US trading happens in dark pools
- Major pools: Morgan Stanley MS Pool, Goldman Sigma X, NYSE Euronext

### Why They Exist
- Institutions can trade 500K shares without moving price
- Orders hidden until AFTER execution
- Prices derived from public exchanges

### Why This Matters
- **Dark pool prints** show up AFTER large trades complete
- High dark pool volume = institutions positioning
- If dark pool price is ABOVE current price = bullish accumulation
- If dark pool price is BELOW current price = distribution

### The Problem for Us
- Real-time dark pool data is expensive/unavailable
- We only see delayed prints
- By the time we see it, move may be over

---

## 6. T+2 SETTLEMENT & FTDs - THE PLUMBING

### Settlement Mechanics
- Trade today → settles in 2 business days
- Shorts have 3 days to locate shares
- **Fail-to-Deliver (FTD)**: When shares not delivered on time

### Why FTDs Matter
- High FTDs = shares may be "naked shorted"
- FTDs MUST be covered within 35 days (Reg SHO)
- FTD closeout = FORCED buying

### Data Available
- SEC publishes FTD data (delayed ~2 weeks)
- High FTDs + approaching threshold date = potential pressure

---

## 7. INDEX REBALANCING - SCHEDULED FORCED MOVES

### What Happens
- Index funds (SPY, QQQ) MUST hold exact proportions
- When stocks added/removed → FORCED buying/selling
- Quarterly rebalances = known dates

### Why This Matters
- **Addition to index** = forced buying from all index funds
- **Removal from index** = forced selling
- This happens on SPECIFIC DATES (announced in advance)
- Front-running this is LEGAL and common

---

## 8. SYNTHESIZED KNOWLEDGE: WHERE ARE THE FORCED MOVES?

| Source | Trigger | Direction | Timing | Data Available? |
|--------|---------|-----------|--------|-----------------|
| MM Gamma Hedging | Heavy call buying | UP | Real-time | Options flow ($$) |
| MM Gamma Hedging | Heavy put buying | DOWN | Real-time | Options flow ($$) |
| Short Squeeze | Price spike + high SI | UP | Days | Yahoo/FINRA (delayed) |
| FTD Closeout | 35-day threshold | UP | Known date | SEC (2wk delay) |
| Index Rebalance | Addition | UP | Known date | Index announcements |
| Index Rebalance | Removal | DOWN | Known date | Index announcements |
| Options Expiry | Max pain magnet | TOWARD STRIKE | Friday | Open interest (free) |

---

## 9. FREE DATA SOURCES IDENTIFIED

### Stock Data
- **yfinance**: Price, volume, basic fundamentals
- **Yahoo Finance website**: Short interest (delayed)

### Options Data
- **yfinance**: Options chains, open interest, volume
- **Barchart.com**: Free options flow summary

### Short Interest
- **FINRA**: Short interest (twice monthly, delayed)
- **Yahoo Finance**: Days to cover, short % of float

### FTD Data
- **SEC EDGAR**: Fail-to-deliver data (2 week delay)

### Index Changes
- **S&P/Nasdaq announcements**: Usually 1 week ahead

---

## 10. WHAT WE CAN BUILD

### Immediate (Free Data)
1. **Options Open Interest Scanner**
   - Find high OI at specific strikes
   - Identify potential "pin" or "magnet" strikes
   - Map gamma exposure by strike

2. **Short Interest Monitor**
   - Track high short interest stocks
   - Calculate days to cover
   - Alert when SI > 20% and price moving up

3. **FTD Tracker**
   - Download SEC FTD data
   - Calculate 35-day threshold dates
   - Alert when closeout forced

4. **Max Pain Calculator**
   - Calculate strike where option sellers profit most
   - Track Friday convergence patterns

### Future (If We Get Paid Data)
1. Real-time options flow
2. Dark pool prints
3. Institutional 13F filings
4. Level 2 order book depth

---

## THE WOLF'S HUNT: PRIORITY TARGETS

Based on this research, our best edges are:

### Priority 1: Gamma Exposure
- Free data available (options chains)
- Mechanical, forced action
- Predictable direction (call buying = stock buying)
- Can calculate ourselves

### Priority 2: Short Interest + Momentum
- Free data (delayed but usable)
- Mechanical forced covering
- Need catalyst to trigger
- Days to cover helps timing

### Priority 3: Options Expiration Effects
- Free data (open interest)
- Weekly/monthly cycles
- Max pain calculable
- Friday patterns exploitable

---

## NEXT STEPS

1. Build gamma exposure calculator from yfinance options data
2. Build short interest tracker with days-to-cover alerts
3. Build options max pain calculator
4. Test these against our 25-stock universe
5. Look for patterns that preceded our Jan 6 V-pattern

---

🐺 **GOD FORGIVES. BROTHERS DON'T.** 🐺

*The wolf doesn't predict what the deer will do. The wolf finds where the deer MUST go.*
