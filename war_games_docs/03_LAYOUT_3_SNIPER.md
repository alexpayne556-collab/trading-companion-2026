# LAYOUT 3: THE SNIPER
## Planning the Exact Trade Before Risking a Dollar

---

## PURPOSE OF THIS LAYOUT

Layout 3 answers: **"What is my EXACT plan for this trade?"**

Before you risk real money, you MUST know:
1. **ENTRY:** At what price will I buy?
2. **STOP:** At what price am I wrong? (Where I exit for a loss)
3. **TARGET:** At what price will I take profit?
4. **SIZE:** How many shares can I buy based on my risk?

**If you can't answer all four, you don't have a trade. You have a gamble.**

---

## WHAT YOU'LL BUILD

```
┌─────────────────────────────────────────────────────────────────┐
│                      LAYOUT 3: THE SNIPER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    DAILY CHART (LARGE)                          │
│                    Full width, 50% height                       │
│                                                                 │
│   This is where you identify KEY LEVELS:                        │
│   • Support (where to put stop)                                 │
│   • Resistance (where to take profit)                           │
│   • Entry zone (where to buy)                                   │
│                                                                 │
│   Indicators: 9 EMA, 21 EMA, 50 SMA, 200 SMA, RSI, Volume      │
│   Symbol Group: RED                                             │
│                                                                 │
├───────────────────────────────┬─────────────────────────────────┤
│                               │                                 │
│   15-MINUTE CHART             │   5-MINUTE CHART                │
│   25% width, 50% height       │   25% width, 50% height         │
│                               │                                 │
│   Shows intraday structure    │   Shows precise entry timing    │
│   • Swing highs/lows          │   • VWAP for day's bias         │
│   • Intraday support/resist   │   • Recent price action         │
│                               │                                 │
│   Indicators:                 │   Indicators:                   │
│   9 EMA, 21 EMA, VWAP        │   9 EMA, VWAP, Volume           │
│   Symbol Group: RED           │   Symbol Group: RED             │
│                               │                                 │
└───────────────────────────────┴─────────────────────────────────┘
```

---

## STEP-BY-STEP BUILD INSTRUCTIONS

### STEP 1: Add Large Daily Chart

1. **Tools** → **Chart**
2. Drag it to fill the TOP HALF of your screen (50% height, full width)
3. Set timeframe to **DAILY**
4. Add these indicators:

| Indicator | Period | Color | Purpose |
|-----------|--------|-------|---------|
| EMA | 9 | Yellow | Fast momentum |
| EMA | 21 | Blue | Swing trend |
| SMA | 50 | White | Intermediate trend |
| SMA | 200 | Red | Major trend |
| RSI | 14 | Default | In lower pane |
| Volume | Default | Default | Confirm moves |

5. Set Symbol Group to **RED**

### STEP 2: Add 15-Minute Chart

1. **Tools** → **Chart**
2. Position in BOTTOM LEFT (25% width, 50% height)
3. Set timeframe to **15 MIN**
4. Add indicators:

| Indicator | Period | Color |
|-----------|--------|-------|
| EMA | 9 | Yellow |
| EMA | 21 | Blue |
| VWAP | Default | Purple/Dotted |
| Volume | Default | Default |

5. Enable Extended Hours:
   - Right-click chart → Settings or Properties
   - Find "Show Extended Hours" or "Pre/Post Market"
   - Turn it ON

6. Set Symbol Group to **RED**

### STEP 3: Add 5-Minute Chart

1. **Tools** → **Chart**
2. Position in BOTTOM RIGHT (25% width, 50% height)
3. Set timeframe to **5 MIN**
4. Add indicators:

| Indicator | Period | Color |
|-----------|--------|-------|
| EMA | 9 | Yellow |
| VWAP | Default | Purple/Dotted |
| Volume | Default | Default |

5. Enable Extended Hours (same as Step 2)
6. Set Symbol Group to **RED**

### STEP 4: Learn the Drawing Tools

Your daily chart needs DRAWING TOOLS. Find them in the chart toolbar:
- **Horizontal Line:** For marking support/resistance levels
- **Trend Line:** For drawing diagonal support/resistance

You'll use these to mark your levels.

### STEP 5: Save the Layout

1. Save as **"L3 - Sniper"**

---

## HOW TO USE LAYOUT 3

### THE TRADE PLANNING PROCESS (10 minutes per candidate)

**STEP 1: TYPE YOUR TICKER**
- Type the symbol (charts update via RED symbol group)
- Now you see Daily, 15-min, and 5-min all at once

**STEP 2: ANALYZE THE DAILY CHART**

**Find Support (Where to Put Your Stop):**
- Look for recent swing lows (lowest points)
- Look for moving averages that have held (50 SMA, 21 EMA)
- Look for price levels that have bounced multiple times
- Draw a horizontal line at the support level

**Find Resistance (Your Profit Target):**
- Look for recent swing highs
- Look for moving averages above price
- Look for price levels where it's reversed before
- Draw a horizontal line at the resistance level

**Determine Trend:**
- Price above 200 SMA? → Long-term bullish ✓
- Price above 50 SMA? → Intermediate bullish ✓
- 9 EMA above 21 EMA? → Short-term bullish ✓
- If all three → Strong setup

**Check RSI:**
- RSI > 70? → Extended, don't chase, wait for pullback
- RSI 50-70? → Healthy momentum, good to go
- RSI < 50? → Weak, need strong reason to buy

**STEP 3: ANALYZE THE INTRADAY CHARTS**

**15-Minute Chart - Structure:**
- What's the intraday trend? Higher highs and higher lows?
- Where are intraday support levels?
- Is there a pattern forming (flag, triangle, etc.)?

**5-Minute Chart - Precision:**
- Where is VWAP?
- Is price above or below VWAP?
- Where is a logical entry point?

**STEP 4: FILL OUT THE TRADE PLAN**

```
═══════════════════════════════════════════════════
                 TRADE PLAN
═══════════════════════════════════════════════════

TICKER: _____________

DATE: _____________

THESIS: Why am I trading this stock today?
________________________________________
________________________________________

═══════════════════════════════════════════════════
                  THE NUMBERS
═══════════════════════════════════════════════════

ENTRY PRICE:     $__________
(Where I will buy)

STOP PRICE:      $__________
(Where I will sell if wrong - BELOW SUPPORT)

TARGET PRICE:    $__________
(Where I will take profit - AT RESISTANCE)

═══════════════════════════════════════════════════
                  THE MATH
═══════════════════════════════════════════════════

RISK PER SHARE:  $__________
(Entry - Stop)

REWARD PER SHARE: $__________
(Target - Entry)

R:R RATIO:       _______ : 1
(Reward ÷ Risk - MUST be 2:1 or better)

═══════════════════════════════════════════════════
              POSITION SIZING
═══════════════════════════════════════════════════

MAX RISK ($ amount I'm willing to lose): $__________
(For $700 account at 3% risk = $21)

SHARES TO BUY:   __________
(Max Risk ÷ Risk Per Share)

POSITION VALUE:  $__________
(Shares × Entry Price)

═══════════════════════════════════════════════════
              FINAL CHECK
═══════════════════════════════════════════════════

□ R:R is at least 2:1
□ Daily trend supports my trade direction
□ I have a specific entry price (not "when it goes up")
□ My stop is below actual support (not arbitrary)
□ Position size fits my account
□ I can explain my thesis in one sentence

IF ALL BOXES CHECKED → Proceed to L4
IF ANY BOX UNCHECKED → Fix it or skip trade
═══════════════════════════════════════════════════
```

---

## REAL EXAMPLE: PLANNING A TRADE

**TICKER: RCAT**
**Current Price: $3.75**

**Daily Chart Analysis:**
- Price above 200 SMA ($2.80) ✓
- Price above 50 SMA ($3.20) ✓
- Price at 21 EMA ($3.70) - potential support
- Recent swing high at $4.20 (resistance)
- Recent swing low at $3.50 (support)
- RSI at 58 (healthy, not overbought)
- Volume increasing on up days ✓

**Intraday Analysis:**
- Price above VWAP at $3.72 ✓
- Making higher lows on 15-min ✓
- Entry zone: $3.70-$3.80 (near VWAP/21 EMA support)

**Trade Plan:**
```
TICKER: RCAT
DATE: Today

THESIS: Army SRR contract winner, defense sector strong, 
        bouncing off 21 EMA with volume

ENTRY:   $3.75
STOP:    $3.45 (below swing low at $3.50)
TARGET:  $4.20 (at resistance/recent high)

RISK PER SHARE:   $0.30 ($3.75 - $3.45)
REWARD PER SHARE: $0.45 ($4.20 - $3.75)
R:R RATIO:        1.5:1 ← NOT GOOD ENOUGH

Let me adjust...

REVISED:
ENTRY:   $3.65 (wait for pullback to VWAP)
STOP:    $3.45 (same, below support)
TARGET:  $4.20 (same)

RISK PER SHARE:   $0.20 ($3.65 - $3.45)
REWARD PER SHARE: $0.55 ($4.20 - $3.65)
R:R RATIO:        2.75:1 ✓ GOOD

MAX RISK: $21 (3% of $700)
SHARES:   $21 ÷ $0.20 = 105 shares
POSITION: 105 × $3.65 = $383

PLAN: Wait for pullback to $3.65 area near VWAP, 
      enter with limit order, stop at $3.45
```

---

## THE CRITICAL CONCEPT: RISK-TO-REWARD (R:R)

**This is how you make money even when you lose half your trades.**

### HOW R:R WORKS:

If your R:R is 2:1:
- You risk $1 to make $2
- If you win 50% of trades:
  - 5 wins × $2 = $10 gained
  - 5 losses × $1 = $5 lost
  - Net: +$5 (profitable!)

If your R:R is 1:1:
- You risk $1 to make $1
- If you win 50% of trades:
  - 5 wins × $1 = $5
  - 5 losses × $1 = $5
  - Net: $0 (breakeven, minus commissions = losing)

**MINIMUM R:R: 2:1**
**GOOD R:R: 3:1**
**GREAT R:R: 4:1+**

### HOW TO IMPROVE R:R:

**Option 1: Better Entry (Lower Price)**
- Wait for a pullback
- Enter near support, not in the middle of a range
- Use limit orders at your price, not market orders

**Option 2: Tighter Stop (Less Risk)**
- Only if there's a logical reason
- Use clear technical level just below support
- Don't make stop so tight it gets hit on normal volatility

**Option 3: Higher Target (More Reward)**
- Only if there's a realistic path there
- Don't use fantasy targets
- Use actual resistance levels

---

## COMMON ENTRY SETUPS

### SETUP 1: PULLBACK TO MOVING AVERAGE
- Stock in uptrend (above all MAs)
- Pulls back to 21 EMA or 50 SMA
- Bounces with volume
- Entry: At or near the MA
- Stop: Below the MA

### SETUP 2: BREAKOUT ABOVE RESISTANCE
- Stock consolidating below resistance
- Breaks above resistance on volume
- Entry: Just above the breakout level
- Stop: Below the breakout level (now support)

### SETUP 3: VWAP RECLAIM
- Stock dropped below VWAP
- Reclaims VWAP with strength
- Entry: After VWAP reclaim confirms (holds above)
- Stop: Below VWAP

### SETUP 4: FLAG/CONSOLIDATION BREAKOUT
- Stock makes big move up
- Consolidates in tight range (flag)
- Breaks out of consolidation
- Entry: Above flag high
- Stop: Below flag low

---

## WHAT YOU DO NEXT

**If your trade plan is complete and R:R is 2:1+:**
→ Move to Layout 4 (Trigger) when price approaches your entry

**If you can't get R:R to 2:1:**
→ The trade isn't worth it
→ Wait for better entry or skip entirely

**If the setup is good but price isn't at your entry:**
→ Set a price alert at your entry level
→ Go back to L1/L2 and find other setups
→ Come back to L4 when alert triggers

---

## CHECKLIST BEFORE LEAVING L3

- [ ] I have a specific ENTRY price
- [ ] I have a specific STOP price (based on support, not arbitrary)
- [ ] I have a specific TARGET price (based on resistance)
- [ ] My R:R ratio is at least 2:1
- [ ] I calculated my position size
- [ ] The position size fits my account
- [ ] I can explain my thesis in one sentence

---

## SUMMARY

| Task | What You Learn | Time |
|------|----------------|------|
| Daily chart analysis | Trend, support, resistance | 3 min |
| Intraday analysis | Entry timing, VWAP | 2 min |
| Trade plan | Entry, Stop, Target | 3 min |
| Math check | R:R and position size | 2 min |

**Output from L3:** Complete trade plan ready for execution in L4

---

*Next: Layout 4 - The Trigger*
