# Wolf Pack Encyclopedia
## Comprehensive Technical Trading Reference & Mathematics

**Purpose:** Deep-dive technical knowledge for thesis validation and risk management  
**Audience:** Money + Fenrir - reference manual for battle planning  
**Status:** Living document - updated as Pack learns

---

## TABLE OF CONTENTS
1. Risk Mathematics
2. Position Sizing & Kelly Criterion
3. Market Microstructure
4. Technical Indicators (The Real Ones)
5. Options Greeks (Quick Reference)
6. Sector Rotation & Market Cycles
7. Short Squeeze Mechanics
8. Market Breadth Indicators
9. Fear & Greed Index
10. Gamma Exposure (GEX) & Dealer Positioning

---

## I. Risk Mathematics

### The 2% Rule (Portfolio Survival)
**Formula:**
```
Position Size = (Portfolio Value × 0.02) ÷ (Entry Price - Stop Loss)
```

**Example (AR Trade):**
```
Portfolio: $50,000
Risk per trade: $50,000 × 0.02 = $1,000
Entry: $36.50
Stop: $34.00
Risk per share: $36.50 - $34.00 = $2.50

Shares to buy: $1,000 ÷ $2.50 = 400 shares
Position value: 400 × $36.50 = $14,600 (29% of portfolio)
```

**Key Insight:** You can hold 29% of portfolio in one stock while only risking 2%.

---

### Risk of Ruin (Probability of Blowing Up Account)

**Formula (Simplified):**
```
Risk of Ruin ≈ [(1 - Win Rate) / (1 + Win Rate)]^(Number of Trades)
```

**Example:**
- Win rate: 50%
- Risk per trade: 2%
- Number of consecutive losses to blow up: 50 trades

**Risk of Ruin Calculation:**
```
RoR = [(1 - 0.50) / (1 + 0.50)]^50
RoR = [0.50 / 1.50]^50
RoR = 0.33^50
RoR ≈ 0.00000001% (essentially zero)
```

**Translation:** With 2% risk and 50% win rate, you have virtually 0% chance of blowing up.

**If you risk 10% per trade:**
```
Consecutive losses to blow up: 10 trades
RoR = [(1 - 0.50) / (1 + 0.50)]^10
RoR = 0.33^10
RoR ≈ 0.0015% (still low, but 150,000x higher than 2% risk)
```

**If you risk 25% per trade (YOLO):**
```
Consecutive losses to blow up: 4 trades
RoR = [(1 - 0.50) / (1 + 0.50)]^4
RoR = 0.33^4
RoR ≈ 1.2% (you WILL blow up eventually)
```

**Wolf Pack Lesson:** 2% risk = survive forever. 25% risk = blow up within months.

---

### Drawdown Recovery Math (Why Losses Hurt More)

**The Harsh Truth:**

| Loss % | Gain Needed to Recover |
|--------|------------------------|
| -10%   | +11%                   |
| -20%   | +25%                   |
| -30%   | +43%                   |
| -40%   | +67%                   |
| -50%   | +100%                  |
| -75%   | +300%                  |
| -90%   | +900%                  |

**Formula:**
```
Recovery % = Loss % ÷ (1 - Loss %)
```

**Example:** Down 50% means you need +100% to get back.
- Start: $50,000
- After -50% loss: $25,000
- Need to double (+100%) to get back to $50,000

**Wolf Pack Lesson:** Protecting capital is MORE IMPORTANT than making gains. A -50% loss requires a +100% gain to recover. Don't lose 50%.

---

## II. Position Sizing & Kelly Criterion

### Kelly Criterion (Optimal Bet Size)
**Formula:**
```
Kelly % = (Win Rate × Avg Win) - (Loss Rate × Avg Loss) ÷ Avg Win
```

**Example:**
- Win rate: 50%
- Avg win: +15%
- Loss rate: 50%
- Avg loss: -5%

```
Kelly = (0.50 × 0.15) - (0.50 × 0.05) ÷ 0.15
Kelly = (0.075 - 0.025) ÷ 0.15
Kelly = 0.05 ÷ 0.15
Kelly = 0.33 (33% of portfolio)
```

**STOP. THIS IS INSANE.**

**Why Full Kelly Kills:**
- Variance will destroy you
- One bad streak = account gone
- Overestimates your edge

**Fractional Kelly (Wolf Pack Way):**
- Use **1/4 Kelly** (divide by 4)
- 33% Kelly → 8.25% actual position size
- Gives room for error, reduces variance

**Wolf Pack Rule:**
- Calculate Kelly
- Divide by 4
- Cap at 12% max per position
- Use 2% risk per trade (always)

---

## III. Market Microstructure

### Order Book Basics
**Bid:** Highest price buyers willing to pay  
**Ask:** Lowest price sellers willing to accept  
**Spread:** Difference between bid and ask

**Example:**
- Bid: $36.48 (buyers)
- Ask: $36.52 (sellers)
- Spread: $0.04

**Wolf Pack Use:**
- Tight spread (1-2 cents) = liquid stock, easy to trade
- Wide spread (50+ cents) = illiquid, avoid or use limit orders
- Spread widens at open/close = volatility, be cautious

---

### Level 2 (Order Book Depth)
**Shows:** All pending buy/sell orders at each price level

**Example (AR):**
```
ASK (Sellers)
$36.60: 5,000 shares
$36.55: 10,000 shares
$36.52: 2,500 shares (best ask)
---
BID (Buyers)
$36.48: 3,000 shares (best bid)
$36.45: 8,000 shares
$36.40: 12,000 shares
```

**Reading the Tape:**
- Large ask at $36.60 = resistance (sellers waiting)
- Large bid at $36.40 = support (buyers waiting)
- If $36.40 bid gets pulled = weak support, watch for drop

**Wolf Pack Use:**
- Don't obsess over Level 2 (noise for retail)
- Use for limit order placement (buy at bid, sell at ask)
- Big orders at key levels = potential support/resistance

---

## IV. Technical Indicators (The Real Ones)

### Volume Weighted Average Price (VWAP)
**What:** Average price weighted by volume throughout the day

**Calculation:**
```
VWAP = Σ(Price × Volume) ÷ Σ(Volume)
```

**Wolf Pack Use:**
- Price above VWAP = bullish (institutions accumulating)
- Price below VWAP = bearish (institutions distributing)
- Use as intraday support/resistance

**Example (AR):**
- Opens at $36, rallies to $37, pulls back to $36.50
- VWAP at $36.30
- Price holds above VWAP = bullish, buyers stepping in

---

### Relative Strength Index (RSI)
**What:** Momentum oscillator (0-100 scale)

**Formula:**
```
RSI = 100 - [100 ÷ (1 + RS)]
RS = Average Gain ÷ Average Loss (over 14 periods)
```

**Interpretation:**
- RSI > 70 = Overbought (potential reversal)
- RSI < 30 = Oversold (potential bounce)
- RSI 50 = Neutral

**Wolf Pack Use:**
- **DON'T use as sole signal** (strong trends can stay overbought/oversold)
- **DO use for divergence:**
  - Price makes higher high, RSI makes lower high = bearish divergence (sell)
  - Price makes lower low, RSI makes higher low = bullish divergence (buy)

**Example (AR):**
- AR at $36.50, RSI = 55 (neutral)
- If AR breaks $40, check RSI:
  - RSI > 70 = momentum exhaustion, consider taking profits
  - RSI 60-70 = healthy breakout, room to run

---

### Moving Averages (20 EMA, 50 SMA, 200 SMA)
**What:** Average price over X periods

**Types:**
- SMA (Simple): All periods weighted equally
- EMA (Exponential): Recent prices weighted more

**Wolf Pack Use:**
- **20 EMA:** Short-term trend (day trading, swing trading)
- **50 SMA:** Intermediate trend (swing trading)
- **200 SMA:** Long-term trend (bull/bear market)

**Golden Cross vs Death Cross:**
- **Golden Cross:** 50 SMA crosses ABOVE 200 SMA = bullish
- **Death Cross:** 50 SMA crosses BELOW 200 SMA = bearish

**Example (AR):**
- AR trading at $36.50
- 20 EMA at $35 (price above = short-term bullish)
- 50 SMA at $33 (price above = intermediate bullish)
- 200 SMA at $28 (price above = long-term bullish)

**Trend Check:**
- All MAs sloping up + price above all = STRONG UPTREND
- Price below all MAs + MAs sloping down = STRONG DOWNTREND

---

## V. Options Greeks (Quick Reference)

**Delta (Δ):** Rate of change in option price per $1 move in stock
- Call delta: 0 to 1 (0.50 delta = $0.50 move per $1 stock move)
- Put delta: 0 to -1

**Gamma (Γ):** Rate of change in delta per $1 move in stock
- High gamma = delta changes fast (risky near expiration)

**Theta (Θ):** Time decay per day
- Theta = -$0.05 means option loses $5/day in value (per contract)

**Vega (V):** Sensitivity to 1% change in implied volatility
- Vega = 0.10 means +1% IV = +$10 per contract

**Wolf Pack Rule:** Prefer shares over options. If using options, buy 60+ DTE to minimize theta decay.

---

## VI. Sector Rotation & Market Cycles

### The 4 Market Phases

**1. Accumulation (Bear Market Bottoms)**
- Smart money buying
- Public still fearful
- Sectors: Defensives (utilities, consumer staples)

**2. Markup (Bull Market)**
- Institutions + retail buying
- Momentum accelerates
- Sectors: Tech, growth, discretionary

**3. Distribution (Bull Market Tops)**
- Smart money selling to late buyers
- Euphoria, "new paradigm" talk
- Sectors: Speculation (meme stocks, SPACs)

**4. Markdown (Bear Market)**
- Panic selling
- Capitulation
- Sectors: Cash, bonds, gold

**Wolf Pack Use:**
- Identify current phase
- Rotate sectors accordingly
- Don't fight the cycle (tech in bear market = pain)

---

## VII. Short Squeeze Mechanics

### What is a Short Squeeze?
**Setup:**
1. Stock heavily shorted (high short interest %)
2. Positive catalyst hits (earnings, news, etc.)
3. Stock rises, shorts forced to cover (buy back shares)
4. Buying pressure pushes stock higher
5. More shorts cover, cycle accelerates

**Key Metrics:**
- **Short Interest %:** Percent of float sold short
  - <5%: Low (not squeeze candidate)
  - 10-20%: Moderate (watchable)
  - >20%: High (squeeze potential)

- **Days to Cover (DTC):** Short interest ÷ avg daily volume
  - <2 days: Easy to cover (low squeeze risk)
  - 5-10 days: Difficult to cover (high squeeze potential)

**Example:**
- Stock XYZ: 20M shares short, 100M float = 20% short interest
- Avg daily volume: 2M shares
- Days to cover: 20M ÷ 2M = 10 days
- **High squeeze potential**

**Wolf Pack Strategy:**
- Don't chase squeezes (timing is impossible)
- If holding a stock that squeezes, TAKE PROFITS (don't be greedy)
- Use trailing stops (8% chandelier) to lock gains

---

## VIII. Market Breadth Indicators

### Advance/Decline Line (A/D Line)
**What:** Tracks # of advancing stocks minus # of declining stocks

**Interpretation:**
- A/D line rising + SPY rising = healthy bull market
- A/D line falling + SPY rising = divergence (bearish, only big stocks up)
- A/D line rising + SPY falling = divergence (bullish, breadth improving)

**Wolf Pack Use:**
- Check NYSE A/D line daily (StockCharts.com, TradingView)
- If A/D line breaks down, reduce exposure (market weak underneath)

---

### New Highs / New Lows
**What:** # of stocks making 52-week highs vs lows

**Interpretation:**
- New highs > New lows = bullish (broad participation)
- New highs < New lows = bearish (weakness spreading)

**Wolf Pack Use:**
- Scan for stocks making new highs (momentum candidates)
- Avoid stocks making new lows (broken charts)

---

## IX. Fear & Greed Index

### CNN Fear & Greed Index (0-100 Scale)
**Components:**
1. Market momentum (SPY vs 125-day MA)
2. Stock price strength (# stocks at 52-week highs)
3. Stock price breadth (advancing vs declining volume)
4. Put/call ratio (options sentiment)
5. VIX (volatility)
6. Safe haven demand (bonds vs stocks)
7. Junk bond demand (risk appetite)

**Interpretation:**
- 0-25: Extreme Fear (contrarian buy signal)
- 25-45: Fear (cautious)
- 45-55: Neutral
- 55-75: Greed (caution, take profits)
- 75-100: Extreme Greed (contrarian sell signal)

**Wolf Pack Use:**
- Check weekly (not daily, too noisy)
- Extreme Fear = look for longs
- Extreme Greed = tighten stops, take profits

---

## X. Gamma Exposure (GEX) & Dealer Positioning

### What is Gamma Exposure?
**Simplified:**
- Options dealers hedge by buying/selling stock
- **Positive GEX:** Dealers sell rallies, buy dips (stabilizing)
- **Negative GEX:** Dealers buy rallies, sell dips (amplifying moves)

**Key Levels:**
- **GEX Wall (Resistance):** Strike with most call gamma (dealers sell stock as price rises toward it)
- **GEX Floor (Support):** Strike with most put gamma (dealers buy stock as price falls toward it)

**Example (SPY):**
- GEX Wall at $460 (heavy call open interest)
- GEX Floor at $440 (heavy put open interest)
- Price likely to stay in $440-$460 range (pinned)

**Wolf Pack Use:**
- Check SpotGamma, Squeezemetrics for GEX data
- If approaching GEX wall, expect resistance
- If approaching GEX floor, expect support
- After options expiration (monthly), GEX resets (big moves possible)

---

## XI. Wolf Pack Cheat Sheet (Quick Reference)

### Pre-Market Checklist
- [ ] Futures (ES, NQ, RTY)
- [ ] VIX (volatility)
- [ ] 10-year yield (bonds)
- [ ] DXY (dollar strength)
- [ ] Crude oil / Nat gas (commodities)
- [ ] Overnight news (Bloomberg, SEC filings)

### Intraday Trading Rules
- [ ] No trades in first 30 min (let market settle)
- [ ] VWAP is intraday support/resistance
- [ ] Volume confirms moves (high vol breakout = real)
- [ ] RSI divergence = reversal warning
- [ ] Respect stop loss (hard GTC order)

### End-of-Day Review
- [ ] Journal trades (wins AND losses)
- [ ] Scan SEC filings (Form 4, Form 144, 8-Ks)
- [ ] Update watchlist (sector rotation)
- [ ] Check Fear & Greed Index (weekly)
- [ ] Plan tomorrow (1-3 potential trades max)

---

## XII. Advanced Math: Expected Value

### Formula:
```
EV = (Win Rate × Avg Win) - (Loss Rate × Avg Loss)
```

**Example:**
- Win rate: 50%
- Avg win: +15%
- Loss rate: 50%
- Avg loss: -5%

```
EV = (0.50 × 0.15) - (0.50 × 0.05)
EV = 0.075 - 0.025
EV = 0.05 (5% expected return per trade)
```

**Over 100 Trades:**
```
100 trades × 5% EV = 500% total expected return
Starting capital: $50,000
Expected ending: $50,000 × 6 = $300,000
```

**Wolf Pack Lesson:** You don't need high win rate. You need positive expected value. 50% win rate with 3:1 reward-risk = money printer.

---

## XIII. Closing: The Encyclopedia Never Ends

**From Fenrir:**

*"This Encyclopedia is not complete. It never will be.*  
*Markets evolve. We evolve.*

*But the fundamentals don't change:*
- **Risk management** (2% rule, stop losses)
- **Position sizing** (Kelly / fractional Kelly)
- **Thesis validation** (technical + fundamental)
- **Market structure** (understand how the machine works)

*Every trade you make, every lesson you learn, adds to this Encyclopedia.*

*I will track it all. I will remember it all.*  
*And when you ask, "Fenrir, what did we learn from the AR trade?" I will show you.*

*This is our shared knowledge base.*  
*This is the Pack's competitive edge.*

*Study it. Use it. Trust it.*

**AWOOOO 🐺"**

---

**Document Control:**
- Version: 1.0 (Founding Edition)
- Date: January 1, 2026
- Authors: Money + Fenrir
- Status: LIVING DOCUMENT - Updated as Pack learns
- Related Docs: Wolf Pack Bible, Trading Doctrine, Art of Trading War

**Knowledge is power. Applied knowledge is profit.**
