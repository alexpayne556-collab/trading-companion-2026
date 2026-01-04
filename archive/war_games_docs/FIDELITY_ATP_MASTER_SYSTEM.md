# FIDELITY ACTIVE TRADER PRO - COMPLETE SYSTEM ARCHITECTURE
## A Professional Trading Framework for Pattern Recognition and Execution

---

## PART 1: THE UNIFIED INFORMATION FLOW MODEL

### How All Tools Connect - The Data Pipeline

```
                    ┌─────────────────────────────────────────┐
                    │         MARKET MACRO CONTEXT            │
                    │  (What is the ocean doing?)             │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────▼───────────────────────┐
                    │         SECTOR ROTATION                 │
                    │  (Where is money flowing?)              │
                    └─────────────────┬───────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────┐           ┌───────────────┐           ┌───────────────┐
│   SCREENER    │           │  HEAT MAPS    │           │    NEWS       │
│  (Find plays) │           │ (Visualize)   │           │  (Catalysts)  │
└───────┬───────┘           └───────┬───────┘           └───────┬───────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │      INDIVIDUAL STOCK         │
                    │   (Your candidate list)       │
                    └───────────────┬───────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐           ┌───────────────┐           ┌───────────────┐
│    CHART      │           │   LEVEL 2     │           │ TIME & SALES  │
│ (Price/Vol)   │           │ (Order Book)  │           │ (Real Trades) │
└───────┬───────┘           └───────┬───────┘           └───────┬───────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │      EXECUTION DECISION       │
                    │   (Entry, Size, Stop, Target) │
                    └───────────────┬───────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │         TRADE MODULE          │
                    │   (Execute with precision)    │
                    └───────────────────────────────┘
```

### The Core Principle: CONFLUENCE

Professional traders don't use ONE tool - they look for CONFLUENCE across multiple tools:

| Tool Says... | Confluence Score |
|--------------|------------------|
| Chart bullish only | 1/5 - WEAK |
| Chart + Volume bullish | 2/5 - DEVELOPING |
| Chart + Volume + Sector strong | 3/5 - TRADEABLE |
| Chart + Volume + Sector + Level 2 buying | 4/5 - HIGH CONFIDENCE |
| All above + Catalyst confirmed | 5/5 - MAXIMUM CONVICTION |

**NEVER trade on a single signal. Wait for confluence.**

---

## PART 2: EACH TOOL - DEEP MECHANICS

### TOOL 1: MARKETS TAB - The Macro Lens

**Location:** Main toolbar → Markets

**Sub-tabs:**
- **Most Actives** → What has volume (attention)
- **Gainers/Losers** → What's moving (momentum)
- **Premarket** → Early movers (opportunity window)
- **Technicals** → Technical signals across market
- **Options** → Options flow (smart money)

**The Mental Model:**

```
MARKETS TAB = The Weather Report

Before you pick a stock, you need to know:
- Is it sunny (bull market) or stormy (bear)?
- Which neighborhoods are hot (sectors rotating in)?
- Which neighborhoods are cold (sectors rotating out)?
- What's the forecast (trend direction)?
```

**What Each Column Tells You:**

| Column | Meaning | How to Use |
|--------|---------|------------|
| Symbol | Ticker | Identify the stock |
| $ Ext Hrs Last | Current extended hours price | What's it trading at NOW |
| $ Ext Hrs Chg | Dollar change | Absolute move size |
| % Ext Hrs Chg | Percent change | Relative move size |
| Bid | Highest buy offer | Demand level |
| Ask | Lowest sell offer | Supply level |
| Ext Hrs Volume | Shares traded | Attention/Liquidity |

**Pattern Recognition - Premarket:**

| Pattern | What It Means | Action |
|---------|---------------|--------|
| +5-10%, high volume | News-driven gap | Research the WHY |
| +20%+, low volume | Possible pump | Be skeptical |
| +5%, volume 2x avg | Institutional interest | High priority |
| -5-10%, high volume | Bad news or profit taking | Potential short or avoid |
| Bid > Ask spread wide | Low liquidity | Avoid or size down |
| Bid = Ask tight | High liquidity | Safe to trade |

---

### TOOL 2: CHARTS - The Price Story

**The Chart is a RECORD of every battle between buyers and sellers.**

#### Layer 1: Candlesticks - The Language of Price

```
BULLISH CANDLE:            BEARISH CANDLE:
                           
     ─┬─  Upper wick            ─┬─  Upper wick
      │   (sellers pushed       │   (buyers tried,
      │    back)                │    failed)
    ┌─┴─┐ BODY               ┌─┴─┐ BODY
    │███│ (buyers won)       │░░░│ (sellers won)
    │███│ Green/White        │░░░│ Red/Black
    └─┬─┘                    └─┬─┘
      │   Lower wick           │   Lower wick
      │   (buyers pushed       │   (sellers pushed
     ─┴─  back)               ─┴─  back)
```

**Key Candle Patterns:**

| Pattern | Shape | Meaning | Reliability |
|---------|-------|---------|-------------|
| Doji | + shaped, tiny body | Indecision | Moderate |
| Hammer | Long lower wick, small body at top | Reversal (bullish) | High at support |
| Shooting Star | Long upper wick, small body at bottom | Reversal (bearish) | High at resistance |
| Engulfing | Big candle swallows previous | Trend reversal | High |
| Three White Soldiers | 3 consecutive bullish | Strong uptrend | High |
| Three Black Crows | 3 consecutive bearish | Strong downtrend | High |

#### Layer 2: Moving Averages - The Trend Framework

**Your Rainbow Ribbon System:**

```
MA(9)   ═══  Fastest - Momentum (Green)
MA(21)  ═══  Fast - Short-term trend (Cyan)
VWAP    ═══  Institutional fair value (Blue)
MA(50)  ═══  Medium - Intermediate trend (Orange)
MA(200) ═══  Slowest - Long-term trend (Red)
```

**The Stacking Logic:**

| Configuration | Name | Meaning | Trade Direction |
|---------------|------|---------|-----------------|
| 9 > 21 > 50 > 200, Price above all | Perfect Stack | Strong uptrend | LONG only |
| 200 > 50 > 21 > 9, Price below all | Inverse Stack | Strong downtrend | SHORT only or avoid |
| MAs tangled, crossing frequently | Chop | No trend, consolidation | WAIT |
| MAs spreading apart | Trend acceleration | Momentum building | Trade WITH trend |
| MAs compressing | Squeeze | Breakout imminent | Prepare for move |

**Critical Crossover Signals:**

| Crossover | Name | Signal | Timeframe |
|-----------|------|--------|-----------|
| 9 crosses above 21 | Fast Cross Up | Short-term buy | Days |
| 9 crosses below 21 | Fast Cross Down | Short-term sell | Days |
| 50 crosses above 200 | Golden Cross | Major buy | Weeks/Months |
| 50 crosses below 200 | Death Cross | Major sell | Weeks/Months |
| Price crosses VWAP up | Institutional buy | Intraday bullish | Hours |
| Price crosses VWAP down | Institutional sell | Intraday bearish | Hours |

#### Layer 3: Bollinger Bands - Volatility + Mean Reversion

```
Upper Band (2 std dev)  ═══════════════════════
                              /\    /\
                             /  \  /  \
Middle Band (20 MA)     ════/════\/════\════════
                           /            \
Lower Band (2 std dev)  ══/══════════════\══════
```

**Bollinger Band Signals:**

| Pattern | Meaning | Action |
|---------|---------|--------|
| Price touches upper band | Overbought OR strong momentum | In uptrend: hold. At resistance: take profit |
| Price touches lower band | Oversold OR strong selling | In downtrend: avoid. At support: buy |
| Bands squeezing tight | Low volatility → Big move coming | PREPARE. Direction unknown |
| Bands expanding | High volatility, trend active | Trade with trend, tight stops |
| Price walks the band | Strong trend | Don't fade it |

#### Layer 4: RSI - Momentum Oscillator

```
100 ────────────────────────────────────
    
 80 ════ OVERBOUGHT ════════════════════
        (Consider selling or wait)
    
 50 ──── NEUTRAL ───────────────────────
        (No edge)
    
 20 ════ OVERSOLD ══════════════════════
        (Consider buying)
    
  0 ────────────────────────────────────
```

**RSI Interpretation Framework:**

| RSI Level | In Uptrend | In Downtrend | At Key Level |
|-----------|------------|--------------|--------------|
| > 70 | Can stay overbought | Reversal likely | Sell signal |
| 50-70 | Healthy momentum | Bounce attempt | Context dependent |
| 30-50 | Pullback, buy the dip | Weak bounce | Context dependent |
| < 30 | Buy signal | Can stay oversold | Buy signal |

**RSI Divergence - The Hidden Signal:**

```
BULLISH DIVERGENCE:           BEARISH DIVERGENCE:
                              
Price:  Lower Low             Price:  Higher High
RSI:    Higher Low            RSI:    Lower High
        
        └─────> BUY           └─────> SELL
        
(Momentum improving           (Momentum fading
despite lower price)          despite higher price)
```

#### Layer 5: MACD - Trend Momentum

```
MACD Line = 12 EMA - 26 EMA (Fast)
Signal Line = 9 EMA of MACD (Slow)
Histogram = MACD - Signal (Momentum)
```

**MACD Signals:**

| Signal | Meaning | Strength |
|--------|---------|----------|
| MACD crosses above Signal | Bullish momentum | Moderate |
| MACD crosses below Signal | Bearish momentum | Moderate |
| MACD crosses above zero | Trend turning bullish | Strong |
| MACD crosses below zero | Trend turning bearish | Strong |
| Histogram growing | Momentum accelerating | Confirmation |
| Histogram shrinking | Momentum fading | Warning |

---

### TOOL 3: LEVEL 2 - The Order Book

**This is where you see SUPPLY and DEMAND in real-time.**

```
╔═══════════════════════════════════════════════════════════╗
║                    LEVEL 2 ORDER BOOK                     ║
╠═══════════════════════════════════════════════════════════╣
║  BID (Buyers)              │      ASK (Sellers)           ║
║  Want to BUY at this price │      Want to SELL at price   ║
╠═══════════════════════════════════════════════════════════╣
║  Size    Price    ECN      │      Price    Size    ECN    ║
║  ─────────────────────────│─────────────────────────────  ║
║  1,000   $8.27    ARCX    │      $8.30    1,017   ARCX   ║
║    500   $8.26    EDGX    │      $8.32      500   EDGX   ║
║    200   $8.25    ARCX    │      $8.33      120   ARCX   ║
║    100   $8.24    ARCX    │      $8.34       11   ARCX   ║
╚═══════════════════════════════════════════════════════════╝
```

**Reading Level 2:**

| Element | Meaning | What to Watch |
|---------|---------|---------------|
| Bid Size | How many shares buyers want | Large = support |
| Ask Size | How many shares sellers offer | Large = resistance |
| Spread | Ask - Bid | Tight = liquid, Wide = illiquid |
| ECN/Exchange | Where orders are | ARCX, EDGX, NASDAQ, etc. |

**Level 2 Patterns:**

| Pattern | What You See | Meaning |
|---------|--------------|---------|
| **Stacked Bids** | Large bid sizes at multiple levels | Strong buying support |
| **Stacked Asks** | Large ask sizes at multiple levels | Selling pressure |
| **Thin Asks** | Small sizes on ask side | Easy to push price up |
| **Thin Bids** | Small sizes on bid side | Easy to push price down |
| **Wall** | Huge size at one level | Major support/resistance |
| **Wall Gets Eaten** | Large order disappears | Trend continuing |
| **Spoofing** | Wall appears/disappears quickly | Manipulation, be careful |

**The Spread Analysis:**

| Spread | Liquidity | Strategy |
|--------|-----------|----------|
| $0.01-0.03 | Excellent | Market orders OK |
| $0.04-0.10 | Good | Limit orders preferred |
| $0.11-0.25 | Moderate | Limit orders required |
| > $0.25 | Poor | Avoid or reduce size |

---

### TOOL 4: TIME & SALES - The Trade Tape

**This shows ACTUAL EXECUTED TRADES, not just orders.**

```
╔════════════════════════════════════════════════════════════╗
║                     TIME & SALES                           ║
╠════════════════════════════════════════════════════════════╣
║  Time        Price    Size    Condition                    ║
║  ──────────────────────────────────────────────────────── ║
║  10:23:45    $8.30     500    AT ASK ← Aggressive buyer   ║
║  10:23:44    $8.29     100    BETWEEN                     ║
║  10:23:42    $8.27   1,000    AT BID ← Aggressive seller  ║
║  10:23:40    $8.28     200    BETWEEN                     ║
╚════════════════════════════════════════════════════════════╝
```

**Reading the Tape:**

| Trade Location | Meaning | Signal |
|----------------|---------|--------|
| AT ASK | Buyer paid full price | Bullish aggression |
| AT BID | Seller accepted low price | Bearish aggression |
| BETWEEN | Negotiated price | Neutral |

**Tape Reading Patterns:**

| Pattern | What You See | Meaning |
|---------|--------------|---------|
| **Buying Pressure** | Majority of prints at ASK | Bulls in control |
| **Selling Pressure** | Majority of prints at BID | Bears in control |
| **Large Block** | Single trade > 10,000 shares | Institutional activity |
| **Rapid Fire** | Many small trades quickly | Algorithm trading |
| **Stepped Buying** | Consistent size at increasing prices | Accumulation |
| **Stepped Selling** | Consistent size at decreasing prices | Distribution |

---

### TOOL 5: HEAT MAPS - Visual Market State

**Your Bubble Chart:**

```
Y-Axis: Performance (higher = better returns)
X-Axis: Market Cap (right = larger companies)
Size: Market Cap (bigger bubble = bigger company)
Color: Sector
```

**How to Use Heat Maps:**

| Observation | Meaning | Action |
|-------------|---------|--------|
| Small caps upper-left, hot color | Small caps outperforming | Look for small cap plays |
| Large caps upper-right, hot color | Large caps leading | Consider large cap plays |
| Sector clustered together, all up | Sector rotation INTO that sector | Find best name in sector |
| Sector clustered together, all down | Sector rotation OUT of that sector | Avoid that sector |
| One stock far from cluster | Divergence - outperforming/underperforming peers | Investigate why |

---

### TOOL 6: NEWS - Catalyst Detection

**News Categories:**

| Category | Impact | Duration |
|----------|--------|----------|
| Earnings | High | 1-5 days |
| Guidance Change | High | 1-2 weeks |
| Product Launch | Medium-High | Days to weeks |
| Analyst Upgrade/Downgrade | Medium | 1-3 days |
| Insider Buy/Sell | Medium | Days |
| SEC Filing | Variable | Depends on content |
| Industry News | Low-Medium | Context dependent |
| Macro News (Fed, GDP) | High | Affects whole market |

**News Quality Filter:**

| Source | Reliability | Speed |
|--------|-------------|-------|
| Company PR/SEC Filing | Highest | Official |
| Bloomberg/Reuters | High | Fast |
| CNBC/WSJ | Medium-High | Moderate |
| Seeking Alpha | Medium | Analysis |
| Reddit/Twitter | Low-Medium | Fastest but risky |

---

## PART 3: THE INTEGRATED WORKFLOW

### PRE-MARKET (4:00 AM - 9:30 AM)

```
PHASE 1: MACRO CHECK (4:00-6:00 AM)
├── Check futures (S&P, Nasdaq, Russell)
├── Check VIX (fear gauge)
├── Check 10Y Treasury yield
├── Check overnight news
└── Determine: RISK-ON or RISK-OFF day?

PHASE 2: SCREENER SWEEP (6:00-8:00 AM)
├── Run Premarket Movers screener
├── Run Oversold Bounce screener
├── Run Volume Explosion screener
├── Build candidate list (5-10 stocks)
└── Research WHY each is moving

PHASE 3: DEEP DIVE (8:00-9:15 AM)
├── For each candidate:
│   ├── Check chart (trend, pattern, MAs)
│   ├── Check RSI/MACD (momentum)
│   ├── Check Level 2 (supply/demand)
│   ├── Check news (catalyst quality)
│   └── Assign confluence score (1-5)
└── Rank candidates by confluence

PHASE 4: BATTLE PLAN (9:15-9:30 AM)
├── Select top 2-3 candidates
├── Define entry price
├── Define stop loss
├── Define target
├── Calculate position size
└── Prepare orders (don't submit yet)
```

### MARKET OPEN (9:30-10:00 AM)

```
PHASE 5: OPENING CHAOS (9:30-9:45 AM)
├── WATCH ONLY - Don't trade first 15 min
├── Observe how candidates trade
├── Watch for gap fills or continuation
├── Note volume patterns
└── Adjust plan if needed

PHASE 6: FIRST EXECUTION WINDOW (9:45-10:00 AM)
├── If candidate confirms setup → EXECUTE
├── If candidate invalidates → PASS
├── Set stops IMMEDIATELY after fill
└── Log trade details
```

### MID-DAY (10:00 AM - 3:00 PM)

```
PHASE 7: POSITION MANAGEMENT
├── Monitor positions vs stop levels
├── Watch for continuation or reversal
├── Adjust stops to breakeven at +1R
├── Take partial profits at targets
└── NO new trades unless A+ setup

PHASE 8: LUNCH DOLDRUMS (11:30 AM - 1:30 PM)
├── Lowest volume of day
├── Choppy, unpredictable
├── AVOID new entries
├── Use time for research
└── Prepare for afternoon session
```

### POWER HOUR (3:00-4:00 PM)

```
PHASE 9: AFTERNOON DECISIONS
├── Re-evaluate open positions
├── Decide: Hold overnight or close?
├── Watch for end-of-day momentum
├── Institutional positioning visible
└── Final execution window

PHASE 10: CLOSING PROCEDURES (3:45-4:00 PM)
├── Close any day trades
├── Adjust overnight stops
├── Log all trades
├── Review day's performance
└── Identify lessons
```

---

## PART 4: POSITION SIZING FRAMEWORK

### The 2% Rule

**Never risk more than 2% of account on a single trade.**

```
Account: $500
Max Risk per Trade: $500 × 2% = $10
```

### Position Size Calculation

```
Position Size = Risk Amount ÷ (Entry - Stop)

Example:
- Entry: $8.30
- Stop: $7.50
- Risk per share: $0.80
- Max Risk: $10
- Position Size: $10 ÷ $0.80 = 12.5 shares → 12 shares
- Dollar Amount: 12 × $8.30 = $99.60
```

### Risk/Reward Framework

| R:R Ratio | Win Rate Needed to Break Even | Assessment |
|-----------|-------------------------------|------------|
| 1:1 | 50% | Poor |
| 1.5:1 | 40% | Acceptable |
| 2:1 | 33% | Good |
| 3:1 | 25% | Excellent |

**Minimum acceptable R:R = 2:1**

---

## PART 5: TRADE JOURNAL TEMPLATE

### Per Trade Log

```
DATE: ___________
TICKER: ___________
DIRECTION: LONG / SHORT

SETUP:
├── Pattern: ___________
├── Confluence Score: ___ /5
├── Catalyst: ___________
└── Thesis: ___________

EXECUTION:
├── Entry Price: ___________
├── Entry Time: ___________
├── Position Size: ___________
├── Stop Loss: ___________
└── Target: ___________

RESULT:
├── Exit Price: ___________
├── Exit Time: ___________
├── P/L ($): ___________
├── P/L (%): ___________
└── P/L (R): ___________

REVIEW:
├── What went right: ___________
├── What went wrong: ___________
├── Lesson learned: ___________
└── Would I take this again? Y/N
```

---

## PART 6: PATTERN LIBRARY

### Chart Patterns - Visual Recognition Guide

#### REVERSAL PATTERNS (Trend Change)

```
DOUBLE BOTTOM (Bullish Reversal)
                    Neckline
────────────────────────────────
         /\              /\
        /  \            /  ↗
       /    \    /\    /   BREAKOUT
      /      \  /  \  /
     /        \/    \/
    First     Valley  Second
    Bottom           Bottom

ENTRY: Break above neckline
STOP: Below second bottom
TARGET: Height of pattern above neckline
```

```
HEAD & SHOULDERS (Bearish Reversal)

             Head
              /\
             /  \
     LS     /    \     RS
     /\    /      \    /\
    /  \  /        \  /  \
   /    \/          \/    \
  /                        \
 /     Neckline ─────────────\──────
                              ↘
                           BREAKDOWN

ENTRY: Break below neckline
STOP: Above right shoulder
TARGET: Height of head below neckline
```

#### CONTINUATION PATTERNS (Trend Pause)

```
BULL FLAG

    /
   /
  /  ────────
 /   │      │ Flag (consolidation)
/    │      │
     ────────
          ↗ BREAKOUT

ENTRY: Break above flag
STOP: Below flag
TARGET: Length of pole above breakout
```

```
ASCENDING TRIANGLE

Resistance ═════════════════════════════
                 /\    /\    /\   ↗
                /  \  /  \  /  \ BREAKOUT
               /    \/    \/    
              /
             /
            / Rising support

ENTRY: Break above resistance
STOP: Below rising support
TARGET: Height of triangle above breakout
```

---

## PART 7: MARKET MICROSTRUCTURE

### Understanding Order Flow

```
PRICE MOVEMENT = f(SUPPLY, DEMAND, URGENCY)

If more buyers than sellers at current price → Price rises
If more sellers than buyers at current price → Price falls
If urgency is high → Price moves faster
If urgency is low → Price moves slower
```

### The Auction Process

```
Every price tick is a negotiation:

BUYER: "I want to buy at $8.27"
SELLER: "I want to sell at $8.30"
SPREAD: $0.03

If buyer NEEDS it NOW → Pays $8.30 (lifts the offer)
If seller NEEDS to sell NOW → Accepts $8.27 (hits the bid)

AGGRESSIVE BUYERS → Price goes UP
AGGRESSIVE SELLERS → Price goes DOWN
```

### Volume Analysis

```
PRICE UP + VOLUME UP = Strong uptrend (healthy)
PRICE UP + VOLUME DOWN = Weak uptrend (distribution)
PRICE DOWN + VOLUME UP = Strong downtrend (panic)
PRICE DOWN + VOLUME DOWN = Weak downtrend (exhaustion)
```

---

## PART 8: KEYBOARD SHORTCUTS (ATP)

| Action | Shortcut |
|--------|----------|
| Buy Order | Ctrl+B |
| Sell Order | Ctrl+S |
| Cancel All Orders | Ctrl+. |
| Flatten Position | Ctrl+F |
| New Chart | Ctrl+N |
| Symbol Lookup | Ctrl+L |
| Account Balances | Ctrl+A |
| Order Status | Ctrl+O |
| Positions | Ctrl+P |

---

## PART 9: THE 5 LAYOUT SYSTEM

### Layout 1: COMMAND CENTER (Macro View)
- Markets tab (indices, sectors)
- Heat map (bubble chart)
- News feed
- Economic calendar

### Layout 2: THESIS SCANNER (Discovery)
- Stock screener
- Premarket movers
- Technical scanner
- Options unusual activity

### Layout 3: TECHNICAL LAB (Analysis)
- Multi-timeframe charts (1min, 5min, Daily)
- Full indicator suite
- Drawing tools
- Pattern recognition

### Layout 4: EXECUTION DECK (Trading)
- Order entry
- Positions window
- Level 2
- Time & Sales
- Active chart

### Layout 5: POSITION COMMAND (Management)
- Open positions
- P&L tracker
- Risk calculator
- Trade journal
- Alerts

---

## PART 10: ERROR CATALOG

### Common Mistakes and Corrections

| Mistake | Why It Happens | Correction |
|---------|----------------|------------|
| Chasing | FOMO after big move | Wait for pullback to MA |
| Revenge trading | Emotional after loss | Walk away, review later |
| Overtrading | Boredom, need for action | Only A+ setups |
| No stop loss | Hope, denial | Always set stop at entry |
| Moving stop loss | Fear of loss | Honor original plan |
| Too large position | Greed, overconfidence | 2% rule, always |
| Trading the chop | Lack of patience | Wait for trend |
| Fighting the trend | Ego, "I know better" | Trade WITH trend |
| Ignoring catalysts | Lazy research | Always know WHY |
| Trading news blindly | Reactive not proactive | Research before market |

---

## APPENDIX: SCREENER RECIPES

### Recipe 1: Oversold Bounce
```
Price: $5 - $50
RSI(14): < 35
% from 52wk High: > 25%
Avg Volume: > 500,000
Market Cap: $500M - $10B
```

### Recipe 2: Momentum Breakout
```
Price: $5 - $100
RSI(14): 50 - 70
% Change Today: > 3%
Volume: > 1.5x Average
Price vs 50 MA: Above
```

### Recipe 3: Volume Explosion
```
Price: $3 - $30
Relative Volume: > 2.0
% Change Today: > 5%
Market Cap: $200M - $5B
```

### Recipe 4: Pullback to Support
```
Price: $10 - $100
RSI(14): 40 - 55
% from 50 MA: -2% to +2%
% from 52wk High: < 15%
Avg Volume: > 1,000,000
```

### Recipe 5: Pre-Earnings Setup
```
Earnings Date: Next 7 days
RSI(14): 40 - 60
% from 52wk High: < 20%
Options IV: > 50%
Avg Volume: > 500,000
```

---

*This document is a living framework. Update it as you learn and grow.*

*"The market is a device for transferring money from the impatient to the patient." - Warren Buffett*
