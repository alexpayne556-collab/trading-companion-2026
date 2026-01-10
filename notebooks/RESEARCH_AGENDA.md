# 🐺 WOLF PACK RESEARCH AGENDA
## For Brokkr - 48 Hours of Deep Testing

**Mission:** Stop guessing. Test EVERYTHING against 3 months of real data. Find what actually works.

**Method:** Jupyter notebooks. Pull data. Form hypothesis. Test. Learn. Iterate.

**Language:** Python + pandas + yfinance + matplotlib

---

## THE MINDSET SHIFT

We've been building tools based on ASSUMPTIONS:
- "RSI < 30 means oversold, should bounce"
- "Volume spike means something"
- "Momentum continues"

**But do they? On OUR stocks? In the LAST 3 months?**

We don't know. We've been guessing.

This 48 hours is about FINDING OUT.

Think of Jupyter as a conversation with the data. Ask questions. Get answers. Follow the thread.

---

## RESEARCH QUESTIONS

### 🔬 QUESTION 1: Does RSI Actually Work?
**Notebook:** `RESEARCH_01_RSI_DEEP_DIVE.ipynb`
- Test RSI < 30 on our universe
- Compare to RSI < 25, < 35
- Test RSI > 70 (overbought)
- Find which tickers it works on
- **Output:** RSI threshold that actually predicts moves

### 📊 QUESTION 2: Volume Spikes - What Do They Mean?
**Notebook:** `RESEARCH_02_VOLUME_ANALYSIS.ipynb`
- Volume > 2x average = breakout or trap?
- UP spike vs DOWN spike (different meanings?)
- How big must spike be? 2x? 5x?
- **Output:** Volume signal rules that work

### 🚀 QUESTION 3: Momentum - Ride It or Fade It?
**Notebook:** `RESEARCH_03_MOMENTUM_OR_FADE.ipynb`
- Stock up 10%+ in 5 days = chase or fade?
- Find momentum "sweet spot"
- Test 5-10%, 10-15%, 15-20%, 20%+ ranges
- **Output:** When to ride, when to fade

### 📉 QUESTION 4: Pullback Sweet Spot
**Notebook:** `RESEARCH_04_PULLBACK_ZONES.ipynb`
- Distance from 52-week high vs forward returns
- 10-20% pullback? 20-30%? 30-40%?
- Find "falling knife" zone (don't catch)
- **Output:** Ideal buy zone based on data

### 🏢 QUESTION 5: Sector Correlation
**Notebook:** `RESEARCH_05_SECTOR_SYMPATHY.ipynb`
- When AEVA moves, do OUST/INVZ follow?
- Find lead/lag relationships
- Test each sector independently
- **Output:** Sympathy play rules

### 📅 QUESTION 6: Day of Week Effects
**Notebook:** `RESEARCH_06_TIMING_PATTERNS.ipynb`
- Monday different than Friday?
- Gap behavior (fade or follow?)
- Best/worst days to trade
- **Output:** Timing edges

### 🎯 QUESTION 7: What Predicts Big Moves?
**Notebook:** `RESEARCH_07_REVERSE_ENGINEER_WINNERS.ipynb`
- Find all +20% moves in 10 days
- Look at what preceded them
- Build "winner profile"
- **Output:** What winners look like BEFORE they win

### 🔧 QUESTION 8: Combining Signals
**Notebook:** `RESEARCH_08_SIGNAL_COMBINATIONS.ipynb`
- RSI + Volume = better?
- Pullback + Momentum starting = edge?
- Build scoring system
- **Output:** Multi-signal edge stack

---

## 48-HOUR SCHEDULE

### Day 1 (Saturday)

**Hours 1-4: RSI Deep Dive**
- Run RESEARCH_01_RSI_DEEP_DIVE.ipynb
- Test all thresholds
- Find which tickers it works on
- ☕ Break

**Hours 5-8: Volume Analysis**
- Run RESEARCH_02_VOLUME_ANALYSIS.ipynb
- UP spike vs DOWN spike
- Magnitude testing
- 🍕 Lunch

**Hours 9-12: Momentum Testing**
- Run RESEARCH_03_MOMENTUM_OR_FADE.ipynb
- Find sweet spot ranges
- Test by sector
- ☕ Break

**Hours 13-16: Pullback Zones**
- Run RESEARCH_04_PULLBACK_ZONES.ipynb
- Map buy zones
- Find falling knives
- 🍕 Dinner

**Hours 17-20: Sector Sympathy**
- Run RESEARCH_05_SECTOR_SYMPATHY.ipynb
- Build correlation matrices
- Find leaders/followers
- ☕ Break

**Hours 21-24: Timing Patterns**
- Run RESEARCH_06_TIMING_PATTERNS.ipynb
- Day of week analysis
- Gap behavior
- 😴 Sleep

### Day 2 (Sunday)

**Hours 1-8: Reverse Engineering**
- Run RESEARCH_07_REVERSE_ENGINEER_WINNERS.ipynb
- Find +20% move setups
- Build winner profile
- Document patterns
- ☕ Multiple breaks

**Hours 9-16: Signal Combinations**
- Run RESEARCH_08_SIGNAL_COMBINATIONS.ipynb
- Test all combos
- Build scoring system
- Validate on recent data
- 🍕 Meals

**Hours 17-20: Synthesis**
- Review all findings
- Document what works
- Kill what doesn't
- Build edge stack

**Hours 21-24: Build Tools**
- Only build what data validated
- Simple scanners based on findings
- Test on Monday candidates
- Document for Monday morning

---

## SUCCESS CRITERIA

After 48 hours, we answer:

1. ✅ **RSI:** Works? Threshold? Which tickers?
2. ✅ **Volume:** What does spike mean? When actionable?
3. ✅ **Momentum:** Chase or fade? Sweet spot?
4. ✅ **Pullback:** Ideal buy zone? Falling knife line?
5. ✅ **Sector:** Sympathy plays work? Lead/lag times?
6. ✅ **Timing:** Best days? Gap behavior?
7. ✅ **Winners:** What do they look like before?
8. ✅ **Combos:** Which signals stack?

---

## OUTPUT FILES

After research, create:

1. **`FINDINGS.md`** - Summary of all discoveries
2. **`VALIDATED_EDGES.md`** - Only edges with 60%+ win rate
3. **`KILLED_ASSUMPTIONS.md`** - What we thought worked but doesn't
4. **`NEW_TOOLS_TO_BUILD.md`** - Build list based on findings
5. **`MONDAY_PLAYBOOK.md`** - Apply findings to current market

---

## THE RULE

**Test FIRST → If win rate > 60% OR clear edge → Build tool**
**If not validated → DELETE notebook, try different hypothesis**

No more building on assumptions.
No more 152 untested files.

Data-driven ONLY.

---

🐺 **BROKKR: This is your hunt. Find what's real.**

*From: Tyr & Fenrir*
*Date: January 10, 2026*
*Mission: DEEP RESEARCH*
