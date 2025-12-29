# LAYOUT 2: THE FILTER
## Separating Real Opportunities from Noise

---

## PURPOSE OF THIS LAYOUT

Layout 2 answers: **"Is this ticker ACTUALLY worth my money and attention?"**

You take the 3-5 candidates from L1 and filter them down to 1-2 REAL opportunities.

Most "hot stocks" from L1 will FAIL this filter. That's the point.

**You still don't trade from this layout. You VALIDATE.**

---

## WHAT YOU'LL BUILD

```
┌─────────────────────────────────────────────────────────────────┐
│                     LAYOUT 2: THE FILTER                        │
├─────────────────────────────┬───────────────────────────────────┤
│                             │                                   │
│   WATCHLIST (List View)     │   DAILY CHART                     │
│                             │                                   │
│   Your sector watchlist     │   Shows:                          │
│   with KEY COLUMNS:         │   • Overall trend                 │
│                             │   • Where price is vs MAs         │
│   • Symbol                  │   • Volume confirmation           │
│   • Last                    │                                   │
│   • Chg%                    │   Indicators:                     │
│   • Volume                  │   • 9 EMA (yellow)                │
│   • Vol % Avg ← KEY         │   • 21 EMA (blue)                 │
│                             │   • 50 SMA (white)                │
│   Symbol Group: GREEN       │   • Volume bars                   │
│                             │                                   │
│   35% width                 │   Symbol Group: GREEN             │
│                             │   35% width                       │
├─────────────────────────────┼───────────────────────────────────┤
│                             │                                   │
│   (Watchlist continues      │   5-MINUTE CHART                  │
│    or News panel)           │                                   │
│                             │   Shows:                          │
│                             │   • Intraday trend                │
│                             │   • VWAP position                 │
│                             │                                   │
│                             │   Indicators:                     │
│                             │   • 9 EMA                         │
│                             │   • VWAP (critical)               │
│                             │   • Volume bars                   │
│                             │                                   │
│                             │   Symbol Group: GREEN             │
│                             │   30% width                       │
└─────────────────────────────┴───────────────────────────────────┘
```

---

## STEP-BY-STEP BUILD INSTRUCTIONS

### STEP 1: Add Watchlist in List View

1. **Tools** → **Watchlist**
2. Position on LEFT side (about 35% width)
3. Make sure it's in **LIST view** (not Heatmap)
4. Load your sector watchlist (same one that was hot in L1)

### STEP 2: Configure Watchlist Columns (CRITICAL)

Click the **Columns** button or gear icon and add these columns IN THIS ORDER:

| Column | What It Shows | Why It Matters |
|--------|---------------|----------------|
| Symbol | Ticker name | Identification |
| Last | Current price | Know the price |
| Chg% | Today's % change | How much it's moved |
| Volume | Shares traded today | Raw activity |
| **Vol % Avg** | Volume vs average | THE KEY FILTER |

**Vol % Avg is your most important column.**

- Below 100% = below average volume (no institutional interest)
- 100-150% = normal to slightly elevated
- 150-200% = something is happening
- 200%+ = significant activity, likely news/catalyst
- 300%+ = major move, institutions involved

**SORT the watchlist by Vol % Avg (descending)**
This puts the highest volume stocks at the top.

### STEP 3: Set Watchlist Symbol Group

1. Look for a colored square or "Symbol Group" dropdown in the watchlist
2. Set it to **GREEN**
3. This will link it to your charts

### STEP 4: Add Daily Chart

1. **Tools** → **Chart**
2. Position on TOP RIGHT (about 35% width)
3. Set timeframe to **DAILY** (click where it says the timeframe)
4. Add indicators:

**How to Add Indicators:**
1. Click **Indicators** button (usually top right of chart)
2. Search for each indicator
3. Add them one by one

**Add These:**
| Indicator | Settings | Color |
|-----------|----------|-------|
| EMA | Period: 9 | Yellow |
| EMA | Period: 21 | Blue |
| SMA | Period: 50 | White |
| Volume | Default | Default |

5. Set Symbol Group to **GREEN**

### STEP 5: Add 5-Minute Chart

1. **Tools** → **Chart** (opens another chart)
2. Position on BOTTOM RIGHT (about 30% width)
3. Set timeframe to **5 MIN**
4. Add indicators:

| Indicator | Settings | Color |
|-----------|----------|-------|
| EMA | Period: 9 | Yellow |
| VWAP | Default | Purple or Dotted |
| Volume | Default | Default |

5. Set Symbol Group to **GREEN**

### STEP 6: Test the Linking

1. Click on any ticker in your watchlist
2. BOTH charts should update to show that ticker
3. If they don't update, check that all three tools have Symbol Group = GREEN

### STEP 7: Save the Layout

1. Save as **"L2 - Filter"**

---

## HOW TO USE LAYOUT 2

### THE FILTER PROCESS (5 minutes)

**Step 1: Sort by Volume**
- Make sure watchlist is sorted by Vol % Avg (highest first)
- The top stocks have the most unusual volume

**Step 2: Click Through Top 5-7 Names**

For each ticker, quickly check:

**DAILY CHART - THE TREND CHECK**

| What You See | What It Means | Action |
|--------------|---------------|--------|
| Price above ALL MAs | Strong uptrend | ✓ PASS |
| Price above 50 SMA, pulling back to 21 EMA | Healthy pullback | ✓ PASS |
| Price below 50 SMA | Weaker, needs more proof | ⚠ CAUTION |
| Price below 200 SMA | Downtrend | ✗ FAIL |
| Price far above 9 EMA | Extended, might pullback | ⚠ WAIT |

**5-MIN CHART - THE INTRADAY CHECK**

| What You See | What It Means | Action |
|--------------|---------------|--------|
| Price above VWAP | Buyers winning today | ✓ PASS |
| Price holding above 9 EMA | Intraday momentum up | ✓ PASS |
| Price below VWAP | Sellers winning | ⚠ CAUTION |
| Price rejected at VWAP multiple times | Weak | ✗ FAIL |

**Step 3: Apply the Filter Checklist**

For each candidate, answer YES or NO:

```
FILTER CHECKLIST:

□ Vol % Avg > 150%?                    
  YES = Continue | NO = Skip

□ Daily: Price above 21 EMA?           
  YES = Continue | NO = Skip (unless clear reversal setup)

□ Daily: Volume bars showing increase?  
  YES = Continue | NO = Weak move

□ 5-Min: Price above VWAP?             
  YES = Continue | NO = Wait for reclaim

□ Do I know WHY it's moving? (Catalyst)
  YES = Stronger | NO = Still OK if technicals are perfect

RESULT: 
- 4-5 YES = STRONG CANDIDATE → Move to L3
- 3 YES = MAYBE → Watch but don't prioritize  
- 0-2 YES = SKIP → Not worth your capital
```

---

## REAL EXAMPLES

### EXAMPLE 1: STRONG CANDIDATE ✓

**RCAT showing in L1 heatmap, up 4%**

L2 Analysis:
- Vol % Avg: 220% ✓
- Daily: Price above 9, 21, 50 EMA ✓
- Daily: Volume bars highest in 5 days ✓
- 5-Min: Price above VWAP, holding ✓
- News: "Army contract award" ✓

**VERDICT: Move to L3, plan the trade**

### EXAMPLE 2: WEAK CANDIDATE ✗

**OPTT showing in L1 heatmap, up 3%**

L2 Analysis:
- Vol % Avg: 110% ✗ (barely above normal)
- Daily: Price below 50 SMA ✗
- Daily: Volume not impressive ✗
- 5-Min: Price chopping around VWAP ✗
- News: Nothing specific ✗

**VERDICT: Skip, not a real setup**

### EXAMPLE 3: WAIT FOR CONFIRMATION ⚠

**IONQ showing green, up 2.5%**

L2 Analysis:
- Vol % Avg: 180% ✓
- Daily: Price at 50 SMA resistance ⚠
- Daily: Volume building ✓
- 5-Min: Price just below VWAP ⚠
- News: Sector news, not company specific ⚠

**VERDICT: Add to watchlist, wait for either:**
- Price to break above 50 SMA with volume → Then L3
- Price to reclaim VWAP and hold → Then L3
- If it fails and drops → Skip

---

## KEY COLUMN EXPLAINED: VOL % AVG

This is your single most important filter. Here's why:

**Volume precedes price.**

Before a big move happens:
1. Smart money (institutions) starts buying
2. They can't hide - their buying shows up as volume
3. Price hasn't moved much yet
4. Volume % Avg spikes to 150%, 200%, 300%
5. THEN price makes its big move

**By filtering for high Vol % Avg, you're finding stocks where smart money is ALREADY involved.**

| Vol % Avg | What's Happening | Your Action |
|-----------|------------------|-------------|
| 50-100% | Normal/quiet day | Ignore |
| 100-150% | Slightly elevated | Monitor |
| 150-200% | Something happening | Investigate |
| 200-300% | Significant activity | Strong candidate |
| 300%+ | Major institutional activity | Highest priority |

---

## COMMON MISTAKES TO AVOID

### MISTAKE 1: Ignoring Volume
- "But it's up 5%!"
- If volume is below average, the move is WEAK
- It will likely fade
- No volume = no conviction = no trade

### MISTAKE 2: Chasing Extended Stocks
- Stock is up 15% and way above all moving averages
- RSI is 80+
- You want to buy because "it's going up"
- DON'T. Wait for a pullback to support.

### MISTAKE 3: Overcomplicating
- You only need 2-3 minutes per ticker in L2
- Glance at volume, glance at daily trend, glance at VWAP
- If it doesn't obviously pass, move on
- Don't talk yourself into bad setups

### MISTAKE 4: Too Many Candidates
- You should exit L2 with 1-2 real candidates, max 3
- If you have 5+ candidates, your filter is too loose
- Be more selective

---

## WHAT YOU DO NEXT

**If you have 1-2 strong candidates:**
→ Move to Layout 3 (Sniper) to plan exact entry/stop/target

**If nothing passed the filter:**
→ Go back to L1
→ Check a different sector
→ Or wait - not every day has good setups

**If you're unsure about a candidate:**
→ Add it to a "watch" list
→ Set an alert for key levels
→ Check back in 30-60 minutes

---

## CHECKLIST BEFORE LEAVING L2

Before moving to L3, confirm:

- [ ] I have 1-2 candidates (not 5+)
- [ ] Each candidate has Vol % Avg > 150%
- [ ] Each candidate's daily trend is up (above key MAs)
- [ ] Each candidate is above or near VWAP
- [ ] I can explain why each is moving (catalyst or sector strength)
- [ ] I'm not just picking the biggest % gainer

---

## SUMMARY

| What You Do | What You Learn | Time |
|-------------|----------------|------|
| Sort by Vol % Avg | Which stocks have unusual activity | 30 sec |
| Check Daily Chart | Is the trend your friend? | 60 sec each |
| Check 5-Min + VWAP | Are buyers in control today? | 30 sec each |
| Apply filter checklist | Should I spend more time on this? | 30 sec each |

**Output from L2:** 1-2 validated candidates ready for trade planning in L3

---

*Next: Layout 3 - The Sniper*
