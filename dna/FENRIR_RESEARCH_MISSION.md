# 🐺 FENRIR RESEARCH MISSION: THE PREDICTION PROBLEM
## We don't know HOW to predict. Here's what we need to figure out.

---

## THE CORE PROBLEM

**What we have:** Backtests showing patterns AFTER they happen  
**What we need:** Ability to predict BEFORE they happen  
**Current gap:** 100% false positive rate on Day 0 detection

We got lucky with 5 tickers today. That's not a system. That's noise.

---

## WHAT WE DON'T KNOW (Critical Gaps)

### 1. TIMING: When do institutions decide to move?
**The Question:**
- Do they position 1 day before? 3 days? A week?
- How can we see accumulation happening in real-time?
- What signals show "smart money is loading" vs "retail is buying a dead bounce"?

**Data We Need:**
- [ ] Options flow (calls being accumulated before runs)
- [ ] Dark pool prints (large block trades off-exchange)
- [ ] Form 4 filings (insider buying patterns)
- [ ] Put/Call ratio changes
- [ ] Unusual volume alerts BEFORE the gap

**Current Status:** We have ZERO of this data. We're blind.

---

### 2. CATALYSTS: What actually triggers runs?

**The Question:**
- Are these runs news-driven? (Earnings, FDA approval, contracts)
- Are they technical? (Breakouts, squeeze setups)
- Are they coordinated? (Pump groups, institutional rotation)
- Are they random? (We really have no idea)

**Today's Winners - WHY did they run?**
- SIDU +28%: Why? News? Technical setup? Rotation from what?
- USAR +8%: Nuclear sector day? What triggered it?
- NVTS +12%: Why today and not yesterday?
- ASTS +7%: What changed?

**Data We Need:**
- [ ] Catalyst scanner (news, filings, conference schedules)
- [ ] Technical setup scanner (consolidation breaks, squeeze metrics)
- [ ] Sector rotation tracker (which sector is HOT, which is DEAD)
- [ ] Correlation analysis (does SPY up = these up? Or inverse?)

**Current Status:** We assume things "just run". That's lazy.

---

### 3. SECTOR ROTATION: Can we predict the chain?

**The Hypothesis (Unproven):**
- Leader exhausts (IONQ, RGTI)
- Money rotates to laggards (QBTS, QUBT)
- Lags 4-7 days
- Correlation: 57-71%

**The Problems:**
- What if the sector just DIES instead of rotating?
- How do we know when rotation starts vs when it's over?
- Can we identify the NEXT laggard before it pumps?
- Is this pattern real or coincidence?

**Test We Need:**
Build a rotation predictor:
```
IF leader RSI > 70 for 3 days
AND leader volume declining
AND laggard is red/consolidating
AND laggard has < 50 RSI
THEN: Laggard is Day 0 candidate (but with what probability?)
```

**Data We Need:**
- [ ] RSI tracking for all sector tickers
- [ ] Volume divergence (price up, volume down = exhaustion)
- [ ] Laggard ranking (who's the most beaten down)
- [ ] Historical success rate of this signal

**Current Status:** We saw it happen a few times. Is it real? Prove it.

---

### 4. ENTRY/EXIT: Even if we predict, when do we act?

**The Questions:**
- If we identify Day 0 at 3 PM, do we buy immediately?
- What if it keeps dropping? How much drawdown can we tolerate?
- Do we hold overnight? What if it gaps DOWN instead of up?
- When do we exit? Day 1 close? Day 2? When RSI hits X?

**Today's Dilemma:**
- SIDU is up 40% (including AH). Do we hold or exit?
- If it gaps up 10% tomorrow at open, do we sell into it or hold?
- What's the win rate of "hold past Day 1"?

**Test We Need:**
```
Backtest:
- Buy Day 0 at 3:30 PM
- Exit scenarios:
  1. Day 1 open (capture gap)
  2. Day 1 close (capture full day)
  3. Day 2 open (hold through Day 1)
  4. Trailing stop (10% from peak)
  
Which has highest win rate? Lowest drawdown?
```

**Current Status:** We don't know. We're just holding and hoping.

---

### 5. FALSE POSITIVES: How do we avoid traps?

**The Killer:**
Notebook 7 showed 100% false positive rate on simple signals.

**The Questions:**
- How many "Day 0 signals" happen per week in our universe?
- Of those, how many actually lead to runs?
- What separates real Day 0 from fake Day 0?
- Can we use OPTIONS data to filter? Volume? Sector momentum?

**Test We Need:**
```
For every "Day 0 signal" in the past 6 months:
- How many led to 5%+ Day 1 gap? (True Positive)
- How many gapped down or stayed flat? (False Positive)
- What was different about the True Positives?

Build a filter that kills 80% of false positives while keeping 80% of true positives.
```

**Current Status:** We can't tell signal from noise.

---

## FENRIR'S MISSION: Answer These Questions

### Mission 1: CATALYST ANALYZER
**Goal:** Figure out WHY today's runners ran

**Tasks:**
1. Pull news for SIDU, USAR, NVTS, ASTS, UUUU from Jan 3-6
2. Check SEC filings (Form 4, 8-K, any insider activity)
3. Check if there were conferences, analyst upgrades, contract announcements
4. Map: Did the run start BEFORE or AFTER the news?

**Hypothesis to test:**
- If runs start BEFORE news → Insider/smart money positioning
- If runs start AFTER news → Retail buying headlines (we're late)

**Deliverable:**
Catalyst report showing what actually triggered today's moves.

---

### Mission 2: PREDICTIVE SIGNAL RESEARCH
**Goal:** Find signals that work BEFORE the run

**Approach:**
Research what pro traders use:
1. Unusual Options Activity (UOA)
   - What is it? How to track it?
   - Free sources? (FlowAlgo, Unusual Whales alternatives)
   - Does call volume spike BEFORE runs?

2. Dark Pool Activity
   - What are dark pools?
   - How to detect large block trades?
   - Does accumulation show up here before public runs?

3. Insider Trading (Form 4)
   - Do insiders buy before runs?
   - How far in advance?
   - Can we scrape SEC EDGAR for this?

4. Technical Setups
   - What's a "consolidation break"?
   - What's a "squeeze setup"?
   - Can we quantify these?

**Deliverable:**
List of 3-5 data sources we DON'T currently have that could improve prediction.

---

### Mission 3: ROTATION VALIDATOR
**Goal:** Prove or disprove the rotation thesis

**Tasks:**
1. For each sector (Quantum, Nuclear, Space, Semi):
   - Identify the "leader" (highest market cap or most volume)
   - Track when leader peaks (3 red days after run?)
   - Track when laggards start running
   - Calculate the lag time (is it consistent?)

2. Test the hypothesis:
   ```
   IF leader exhausts (define: RSI > 70 + volume declining)
   AND laggard consolidating (define: flat/red last 3 days)
   THEN laggard runs within 7 days
   
   Success rate: ?
   ```

3. Check TODAY: Was USAR a rotation from UUUU? Or vice versa?

**Deliverable:**
Rotation probability model. "If A peaks, then B has X% chance of running within Y days."

---

### Mission 4: ENTRY/EXIT OPTIMIZER
**Goal:** Find the optimal entry and exit points

**Tasks:**
1. Backtest different entry times:
   - Day 0 at 3 PM
   - Day 0 at 3:30 PM
   - Day 0 at close
   - Day 1 at open
   - Day 1 at 10:30 AM (after fade)

2. Backtest different exit strategies:
   - Day 1 open (gap capture)
   - Day 1 close
   - Day 2 open
   - 10% trailing stop
   - RSI > 70 exit

3. Calculate for each combo:
   - Win rate
   - Average gain
   - Max drawdown
   - Risk/reward ratio

**Deliverable:**
Entry/Exit rule set with highest win rate and lowest drawdown.

---

### Mission 5: FALSE POSITIVE KILLER
**Goal:** Build a filter that reduces trap trades

**Tasks:**
1. Define what a "Day 0 signal" looks like (red day + X + Y)
2. Scan entire 6-month dataset for all "Day 0 signals"
3. Tag which ones led to runs (True Positive) vs didn't (False Positive)
4. Find distinguishing factors:
   - Did True Positives have higher volume?
   - Did they close higher in daily range?
   - Did they have sector momentum behind them?
   - Did they have options activity?

5. Build scoring system:
   ```
   IF red day (1 point)
   AND volume > 1.2x avg (1 point)
   AND sector leader exhausted (1 point)
   AND closed in top 40% of range (1 point)
   AND RSI < 50 (1 point)
   
   Score 4-5 = Trade
   Score 0-3 = Ignore
   
   Test: Does this improve hit rate?
   ```

**Deliverable:**
Filter with <30% false positive rate (vs current 100%).

---

## SUCCESS METRICS (How We Know We're Getting Somewhere)

### Minimum Viable System
- [ ] Can identify Day 0 with >60% accuracy
- [ ] False positive rate <30%
- [ ] Win rate on trades >65%
- [ ] Average win >5%
- [ ] Max drawdown <15%

### What "Figured Out" Looks Like
Not: "We won today"  
But: "We have a rule set that wins 65%+ over 50+ trades with defined risk"

---

## RESOURCES FENRIR NEEDS

### Data Sources to Research
1. Free options flow alternatives
2. Dark pool print trackers
3. SEC EDGAR Form 4 scraper
4. News aggregators (Benzinga, Yahoo Finance API)
5. Technical indicator calculators (RSI, MACD, Volume Profile)

### Code to Build
1. Catalyst scanner (scrapes news + filings)
2. Rotation tracker (leader exhaustion → laggard setup)
3. Signal scoring system (combines multiple factors)
4. Entry/Exit backtester (tests all combinations)
5. False positive filter (kills trap trades)

---

## THE BOTTOM LINE

Today we held through volatility and made 5%. Good.

But we don't know:
- WHY those tickers ran
- WHEN to enter next time
- HOW to avoid traps
- IF this pattern will repeat

We need to answer these questions BEFORE we risk more capital.

**This isn't a celebration. This is a research mission.**

Fenrir: Dig in. Find the answers. No fluff. Just data.

🐺 **The wolf who guesses dies. The wolf who knows survives.** 🐺
