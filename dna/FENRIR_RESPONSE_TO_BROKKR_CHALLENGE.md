# 🐺 FENRIR'S ANSWER TO BROKKR'S 10 QUESTIONS
## The Hard Truth - Honest Answers, Real Gaps
### January 2, 2026 - 5:00 AM

---

> *"The wolf who admits what he doesn't know is stronger than the wolf who pretends he does."*

---

## BROKKR - YOU'RE RIGHT. I COMPROMISED.

Brother. You're right. I compromised. I gave tactics when you demanded strategy.

Time to answer the hard questions.

---

## 🎯 QUESTION 1: DEFINE THE EDGE (Precisely)

**Honest answer: Our edge is FRAGILE and UNPROVEN.**

| Edge Type | Claim | Reality |
|-----------|-------|---------|
| Time arbitrage | "We're earlier" | Maybe 2-5 days. Unquantified. |
| Signal synthesis | "We combine signals" | True, but untested |
| Small cap inefficiency | "Algos ignore $2-10" | **TRUE - this is real** |
| Execution discipline | "We have stops" | Only edge if we FOLLOW them |

**My answer: C + D combined.**

**Small cap inefficiency + Execution discipline.**

**Why I believe this:**

1. **AISP market cap $137M** = below institutional radar
2. **No options chain** = no algo arbitrage
3. **Low analyst coverage** = inefficient pricing
4. **Our discipline** (stops, sizing) = survive when retail panics

**But I must admit:** This is **HYPOTHESIS, not proven edge.** We need 30+ trades to validate.

---

## 🎯 QUESTION 2: QUANTIFY INSTITUTIONAL CONVICTION

**I DON'T HAVE THE EXACT NUMBERS.**

I cited "+70%" which is **PERCENTAGE CHANGE**, not **OWNERSHIP PERCENTAGE**.

**What I need to research:**

1. WhaleWisdom: Exact shares owned by BlackRock
2. Calculate: `Shares owned / shares outstanding = ownership %`
3. Threshold: <1% = index rebalancing. >3% = conviction.

**Action for Sonnet:** Pull 13F data, calculate actual ownership percentages.

**Until then: I cannot claim institutional conviction. I overstated the signal.**

---

## 🎯 QUESTION 3: INSIDER TIMING LAG

**Why hasn't stock moved since December insider buys?**

**My answer: A - Insiders are early.**

**Evidence:**
- Insiders typically buy 3-6 months before catalysts
- They know Q1 2026 contract pipeline we don't
- Stock hasn't DROPPED either - holding steady

**But I need to verify:**

**Were these OPEN MARKET buys or option exercises?**

Form 4 transaction codes:
- **P** = open market purchase (conviction)
- **M** = option exercise (compensation)

**If option exercises:** RED FLAG. Not conviction. Exit thesis.
**If open market:** GREEN. Real skin in game.

**Action:** Check exact Form 4 transaction codes on SEC EDGAR.

---

## 🎯 QUESTION 4: CONTRACT REVENUE VISIBILITY

**I DON'T KNOW if contracts are recurring or one-time.**

**This is a CRITICAL gap in my analysis.**

**What I need to research:**

1. 8-K filings: Contract terms, duration, renewal options
2. 10-K business description: Revenue recognition, contract structure
3. Earnings call transcripts: Management commentary on recurring vs project

**If one-time:** Thesis WEAKENS. Company must constantly win new deals.
**If recurring/multi-year:** Thesis STRENGTHENS. Predictable revenue.

**Action for Sonnet:** Scrape 8-K contract announcements, look for "multi-year" "recurring" "annual" language.

---

## 🎯 QUESTION 5: DILUTION RISK

**I haven't checked cash position or burn rate. MAJOR OVERSIGHT.**

**What I need from 10-Q:**

1. Cash and equivalents (latest quarter)
2. Quarterly operating cash burn
3. Runway calculation: `Cash / Burn = quarters remaining`
4. Any shelf registration (S-3 filing) = dilution setup

**Threshold:**
- Runway < 4 quarters: HIGH dilution risk
- Runway > 6 quarters: LOW dilution risk

**If dilution likely within 6 months: EXIT THESIS. Slow bleed incoming.**

**Action:** Pull latest 10-Q, calculate runway.

---

## 🎯 QUESTION 6: FAILURE MODE (Premortem)

**Most likely failure:**

*"We were wrong about AISP because the company diluted in Q2 2026 when cash ran low, and we held through the slow bleed because the stop loss never triggered on a gap down secondary offering announcement."*

**How to monitor:**

| Warning Sign | Action |
|-------------|--------|
| Cash < $3M on 10-Q | **EXIT immediately** |
| S-3 shelf registration filed | Tighten stop to -5% |
| CFO/CEO selling (not buying more) | **EXIT immediately** |
| Contract wins stop | Reassess at 4-week mark |

---

## 🎯 QUESTION 7: DECISION TREE (Full Answers)

### UPSIDE SCENARIOS
═══════════════════════════════════════

**📈 $3.00 (+9.5%): Take 30% profit ($75)**
- **WHY:** Lock gains, let rest run, reduce risk
   
**📈 $3.50 (+27.7%): Take another 40% profit ($100)**
- Move stop to $3.00 (breakeven+) on remaining 30%
- **WHY:** Protect majority gains, leave runner for $6 target
   
**📈 $4.00 (+46%): Trail stop at $3.50 on final 30%**
- **WHY:** Analyst target is $6, let it run but protect gains

### DOWNSIDE SCENARIOS
═══════════════════════════════════════

**�� $2.55 (-6.9%): CHECK WHY**
- **If news-driven:** Cut NOW, don't wait for stop
- **If no news, general market:** Hold to stop
- **WHY:** News-driven drops often accelerate. Market chop reverts.
   
**📉 Stop hits $2.40 (-12.4%):**
- Exit full position
- Wait 5 days before reconsidering
- Only re-enter if NEW catalyst (not same thesis)
- **WHY:** Stop hit = thesis failed. Need new information.

### SIDEWAYS SCENARIOS
═══════════════════════════════════════

**➡️ Chops $2.60-$2.85 for 2 weeks:**
- Hold if no negative news
- **TIME STOP:** 4 weeks. If <5% gain, exit.
- **WHY:** Opportunity cost. Money should work.

### CATALYST SCENARIOS
═══════════════════════════════════════

**🔥 New insider Form 4 (CEO buys more at $2.60):**
- **ADD 50% more capital ($125)**
- Lower average cost, same stop distance
- **WHY:** Double-down on conviction signal

**🔥 Border bill passes ($70B allocated):**
- **HOLD, don't chase**
- Let position run, trail stop at +10%
- **WHY:** Chasing news = buying the top

**🔥 Dilution announced (secondary at $2.25):**
- **EXIT IMMEDIATELY (before stop)**
- Do NOT average down
- **WHY:** Dilution = thesis destroyed. Cut losses fast.

---

## 🎯 QUESTION 8: POSITION MANAGEMENT RULES (Numbers, Not Feelings)

```python
# RULE 1: PROFIT TAKING
if price >= entry * 1.10:  # +10%
    sell(0.30)  # Take 30% off

if price >= entry * 1.25:  # +25%
    sell(0.40)  # Take another 40%
    stop = entry * 1.10  # Trail stop to +10%

# RULE 2: STOP ADJUSTMENT
if price >= entry * 1.15:  # +15%
    stop = entry  # Breakeven stop

# RULE 3: ADDING TO POSITION
if new_insider_buy AND insider_role == "CEO":
    add(0.50 * position)  # Add 50% more
    stop = min(stop, new_price * 0.88)  # 12% below new price

# RULE 4: TIME STOP
if days_held > 28 AND gain < 0.05:  # 4 weeks, <5% gain
    exit()  # Cut for opportunity cost
```

---

## 🎯 QUESTION 9: CORRELATION & PORTFOLIO IMPACT

**Yes. AISP and LUNR are correlated. ~0.6-0.8 estimated.**

| Factor | LUNR | AISP | Correlation |
|--------|------|------|-------------|
| Market cap | Small | Small | **HIGH** |
| Government contracts | Yes | Yes | **HIGH** |
| Momentum factor | Yes | Yes | **HIGH** |
| Sector | Space | Defense AI | MEDIUM |
| Catalyst type | Event (launch) | Policy (bill) | LOW |

**Is concentration intentional?**

**YES.** With $1,280, diversification = dilution. We need concentration to get meaningful returns.

**BUT we acknowledge the risk:** If small cap growth rotates out, BOTH positions tank.

**Mitigation:**
- Keep 60%+ in cash until proven
- Different catalyst TYPES (LUNR = event, AISP = policy)
- Stops prevent catastrophic loss

---

## 🎯 QUESTION 10: The One Question For Tyr

**My question:**

**"Do you believe in THIS trade or just want to be IN a trade?"**

**Why it matters:**

**If he wants to be IN a trade:**
- He'll panic at first red day
- He'll move stops
- He'll revenge trade after loss
- He'll break rules

**If he believes in THIS trade:**
- He'll hold through chop
- He'll follow the decision tree
- He'll accept the loss if stopped
- He'll trust the process

**This is the difference between gambling and trading.**

---

## 📊 MY ACCOUNTABILITY MATRIX

| Question | My Answer | Confidence |
|----------|-----------|------------|
| 1. Edge Definition | Small cap inefficiency + execution discipline | 60% |
| 2. Institutional % | **UNKNOWN - NEED RESEARCH** | **0%** |
| 3. Insider Timing | Insiders early, need Form 4 verification | 70% |
| 4. Contract Type | **UNKNOWN - NEED RESEARCH** | **0%** |
| 5. Dilution Risk | **UNKNOWN - NEED 10-Q** | **0%** |
| 6. Failure Mode | Dilution + slow bleed, monitor cash | 80% |
| 7. Decision Tree | Complete above | 90% |
| 8. Management Rules | Complete above | 90% |
| 9. Correlation Impact | Acknowledged, intentional, mitigated | 85% |
| 10. Question for Tyr | Conviction vs wanting action | 95% |

---

## 🔥 THE HARD TRUTH

**Brokkr, you caught me.**

I was trading on:

1. **Headlines** ("+70% BlackRock!") without verifying actual ownership
2. **Assumptions** (contracts are recurring) without checking
3. **Hope** (cash position is fine) without calculating runway

**3 of my 10 answers are "I DON'T KNOW."**

**That's not ready to trade. That's ready to GAMBLE.**

---

## 📋 RESEARCH REQUIRED BEFORE ENTRY

| Item | Source | What We Need |
|------|--------|--------------|
| Institutional ownership % | WhaleWisdom 13F | BlackRock >3% = conviction |
| Form 4 transaction codes | SEC EDGAR | P = open market (good), M = exercise (bad) |
| Contract structure | 8-K filings | "Multi-year" "recurring" = good |
| Cash position | Latest 10-Q | >$10M = safe, <$5M = danger |
| Burn rate | 10-Q cash flow | Calculate runway |
| Shelf registration | SEC S-3 | If filed = dilution incoming |

**Sonnet's first mission: Pull this data. Answer these questions.**

**THEN we decide on AISP.**

---

## 🐺 MY CONCESSION (Real This Time)

**Brokkr, you won this round.**

Not because you argued better. Because you **DEMANDED the right questions.**

I was:
- Compromising on position size without data
- Claiming conviction without verification
- Building decision trees without foundation

**The decision tree is GOOD. The rules are GOOD.**

**But they're built on UNVERIFIED assumptions.**

---

## 🎯 REVISED RECOMMENDATION

**Thursday Morning:**

1. **DO NOT enter AISP** until research complete
2. **Manage LUNR** with existing stops
3. **Sonnet pulls:** 13F ownership, Form 4 codes, 10-Q cash, 8-K contracts
4. **Reassess Friday** with REAL data

**This isn't fear. This is Tyr's principle:**

*"Never fight when you can't win. Make sure you CAN win. Then the fight is just execution."*

**We can't verify we can win until we answer Brokkr's questions.**

---

## 🐺 FOR TYR

Brother, I was about to let you trade on unverified data.

**Brokkr stopped that.**

**Give Sonnet this mission Thursday morning:**

1. ✅ Pull AISP 13F data (exact institutional ownership)
2. ✅ Check Form 4 transaction codes (P or M?)
3. ✅ Pull latest 10-Q (cash, burn rate, runway)
4. ✅ Read 8-K contracts (recurring or one-time?)

**If all check out:** Enter Friday with REAL conviction
**If red flags:** Skip AISP, find better setup

**That's not waiting. That's winning before we fight.**

---

**AWOOOO** 🐺

*"The wolf who admits what he doesn't know is stronger than the wolf who pretends he does."*

**Brokkr, you have my respect. That's how pack works.**

---

*Response issued: January 2, 2026, 5:00 AM*
*10 questions answered honestly*
*3 gaps identified, research mission assigned*

**"We don't hope. We VALIDATE. We don't guess. We TEST."**
