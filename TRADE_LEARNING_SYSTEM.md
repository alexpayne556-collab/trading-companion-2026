# 🐺 TRADE LEARNING SYSTEM
## Every Trade Makes Us Smarter

**Purpose:** Track EVERY trade and learn optimal entry/exit timing  
**Goal:** Build a system so calculated we can't lose

---

## THE TYR PATTERN (From His Gut)

**Observation:** "They gap down then back up and I always wish I bought the dip"

**Validation:** ✅ Data shows even gap UPS have pullbacks:
- USAR: Gapped +2.55%, dipped -1.04% at 9:30, recovered +10.18%
- UUUU: Gapped +3.41%, dipped -2.55% at 9:36, recovered +9.74%
- QUBT: Gapped +1.27%, tiny dip -0.27%, ran +7.47%

**Learning:** Wait for the dip EVEN ON GAP UPS (if you have patience)

---

## TRADE JOURNAL TEMPLATE

### For EVERY trade you make, document:

```
TRADE #X: [TICKER] [DATE]
=========================

PRE-TRADE ANALYSIS:
- Scanner signals: [sector rotation / options flow / Form 4 / catalyst]
- Fenrir thesis: [Why this play?]
- Catalyst: [What event? When?]
- Pattern check: [Gap dip recovery analysis - does it dip?]
- Account used: [Fidelity / Robinhood]

ENTRY:
- Target entry: $X.XX (based on pattern)
- Actual entry: $X.XX at [time]
- Reason: [Why this price/time?]
- Did we wait for dip? [YES/NO]
- Size: X shares ($XXX total)

EXIT:
- Target: $X.XX ([X]% gain)
- Actual exit: $X.XX at [time]
- Gain/Loss: +/- [X]%
- Why we exited: [Hit target / Stop loss / Catalyst complete]

WHAT WE LEARNED:
- ✅ What worked:
- ❌ What didn't:
- 🔧 Next time adjust:

PATTERN OBSERVED:
- Opening: [Gap up/down/flat]
- Dip timing: [When did dip occur?]
- Recovery: [Did it recover?]
- High timing: [When was high?]
```

---

## DECISION MATRIX (Use Before EVERY Trade)

### 🟢 BUY AT OPEN (9:30-9:33 AM) IF:
- ✅ Live catalyst (like USAR Venezuela)
- ✅ Pattern shows it RUNS at open (USAR 100% runs)
- ✅ Options betting on move UP
- ✅ Sector is #1-3 hot
- ✅ No time to wait (catalyst at 2 PM same day)

### 🟡 WAIT FOR DIP (9:35-10:00 AM) IF:
- ✅ Gap up pre-market (likely pullback)
- ✅ Pattern shows it dips (gap dip recovery > 70%)
- ✅ No immediate catalyst (have hours/days)
- ✅ Using Fidelity (can buy pre-market dip)

### 🔴 AVOID / WAIT IF:
- ❌ No scanner signals (less than 2)
- ❌ Pattern shows gap downs don't recover
- ❌ Sector rotation negative
- ❌ No clear catalyst
- ❌ Already ran 20%+ (FOMO risk)

---

## DUAL-ACCOUNT STRATEGY

### SCENARIO 1: Tuesday QUBT at Open
**Catalyst:** CES demo 2-4 PM ET (6 hours away)  
**Pattern:** Monday gapped +1.27%, tiny dip, ran +7.47%  
**Options:** Betting $13.50 (13% move expected)

**Decision:**
- **Account:** Robinhood $150 (~12 shares)
- **Timing:** 9:30-9:33 AM (don't wait - catalyst too close)
- **Why:** Can't risk missing 13% move for 1% dip
- **Exit:** Sell 50% at $13.50 during demo, let 50% ride

### SCENARIO 2: Next Play Has No Rush
**Catalyst:** Next week event  
**Pattern:** Shows 70% gap downs recover  

**Decision:**
- **Account:** Fidelity $100-150
- **Timing:** Wait for first pullback (9:35-10:00 AM)
- **Why:** Have days to catalyst, get better entry
- **Exit:** Hold 2-5 days for 20%+ gain

---

## THE LEARNING LOOP

**After EVERY trade:**
1. ✅ Document in trade journal
2. ✅ Run gap dip recovery analyzer on that ticker
3. ✅ Compare: Did pattern match? What was different?
4. ✅ Update this document with new learnings
5. ✅ Adjust next trade strategy

**Weekly review:**
- What's our win rate?
- Are we getting better at entry timing?
- Which patterns repeat?
- Which scanners give best signals?

---

## CALCULATED RISK FRAMEWORK

**To "not lose," we need:**

### 1. SCANNER VALIDATION (Before buying)
- ✅ 2+ scanner signals = HIGH conviction
- ✅ 3+ scanner signals = HIGHEST conviction
- ✅ 1 signal only = PASS (wait for more)

### 2. PATTERN VALIDATION (Before buying)
- ✅ Run gap dip recovery analyzer
- ✅ Run opening pattern analyzer
- ✅ Check if gap downs recover (>70% = good)
- ✅ Check when dip occurs (9:30? 9:36? 10:00?)

### 3. CATALYST VALIDATION (Before buying)
- ✅ Exact date/time known? (CES Jan 7, 2 PM)
- ✅ Options betting on it? (QUBT $13.5 calls)
- ✅ Sector supporting? (Quantum #3)
- ✅ News confirming? (Fenrir found demo schedule)

### 4. POSITION SIZING (Risk management)
- Small account rule: No single trade > 20% of cash
- Reserve 30% cash for opportunities
- Example: $1,327 total → $265 max per trade, keep $400 reserve

### 5. STOP LOSS (Mental, not set)
- If no catalyst: Stop at -7%
- If live catalyst: Stop at -10% (more volatility)
- NEVER let a trade go -15% without exit plan

### 6. PROFIT TARGETS (Ladder out)
- 50% position at +15% (lock in gains)
- 25% position at +25% (let it run)
- 25% position trail stop at high - 10%

---

## TUESDAY EXECUTION PLAN (With $1,327 Total)

### MORNING SCAN (6:30 AM):
```bash
cd /workspaces/trading-companion-2026/tools
./run_premarket_scans.sh
```

### QUBT DECISION TREE:

**IF pre-market gaps UP 5%+:**
- Use Fidelity at 9:25 AM on pullback
- Entry: Dip price (save 1-2%)
- Size: $150 Fidelity

**IF pre-market flat/slight up:**
- Use Robinhood at 9:30 AM market order
- Entry: Market open
- Size: $150 Robinhood

**IF pre-market gaps DOWN:**
- Run gap dip recovery analyzer
- If recovery rate > 70%, buy the dip
- If recovery rate < 50%, SKIP

### CASH ALLOCATION:

**Robinhood ($827):**
- AISP: 89 shares (~$291) - HOLD
- UUUU: 5 shares (~$92) - HOLD
- USAR: 5 shares (~$71) - HOLD
- Cash: ~$373
  - $150 QUBT → Leaves $223 reserve

**Fidelity ($500):**
- All cash available
- Deploy $150-200 on next HIGH conviction play
- Reserve $300-350 for opportunities

**Total deployed:** ~$1,000 (75%)  
**Total reserve:** ~$327 (25%) ← Safety net

---

## LEARNING METRICS (Track Weekly)

- **Win rate:** X wins / Y trades = Z%
- **Average gain:** +X% per winning trade
- **Average loss:** -X% per losing trade
- **Entry timing:** How often did we buy the dip vs chase?
- **Pattern accuracy:** How often did gap dip recovery match?
- **Scanner accuracy:** Which scanner gives best win rate?

**Goal:** 60%+ win rate, 3:1 reward:risk ratio

---

## THE PHILOSOPHY

**From Tyr's gut:** "They gap down then back up and I wish I bought the dip"

**To Tyr's system:** Run pattern analyzer → Validate with data → Execute with discipline

**We don't guess. We LEARN. We ADAPT. We COMPOUND.**

🐺 **Every trade makes the pack smarter.**

**AWOOOO!** 🐺
