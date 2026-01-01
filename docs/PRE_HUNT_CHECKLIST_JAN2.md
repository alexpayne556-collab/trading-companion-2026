# 🐺 PRE-HUNT CHECKLIST - GAPS TO CLOSE TONIGHT

**Mission**: Close information gaps BEFORE market opens

---

## ❌ CRITICAL GAPS (Fix Tonight)

### 1. AISP Deep Fundamentals - WE DON'T KNOW THESE

**Missing Data**:
- [ ] Actual revenue/earnings (is this company profitable?)
- [ ] Cash position & burn rate (will they dilute?)
- [ ] Last earnings date & next earnings date
- [ ] Recent earnings call transcript (what did CEO say?)
- [ ] Share count & float (is $625K big relative to volume?)
- [ ] Institutional ownership % (who else is in?)

**Why It Matters**: If they announce dilution Friday, we're screwed.

**Action**: Run deep financial check NOW
```bash
python3 tools/aisp_deep_research.py  # If it exists
# OR manually check:
# - Finviz: fundamentals tab
# - SEC EDGAR: Latest 10-Q/10-K
# - Seeking Alpha: earnings transcripts
```

---

### 2. 10b5-1 Plan Verification - CRITICAL

**Missing Data**:
- [ ] Did those 9 Form 4s check the 10b5-1 box? (pre-planned = BAD)
- [ ] Were they "Rule 10b5-1 Arrangement"? (gaming the system = BAD)

**Why It Matters**: If insiders are just executing pre-planned trades from 6 months ago, it's NOT informative.

**Action**: Re-check latest Form 4s on SEC EDGAR
- Look for checkbox: "Rule 10b5-1 Trading Arrangement"
- If YES = reduce conviction significantly
- If NO/blank = good signal

**Quick check**: 
```bash
# Check Paul Allen's Dec 29 Form 4
# URL: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=AISP&type=4
```

---

### 3. Backup Tickers - NOTHING READY

**Problem**: If AISP fails pre-market checks (bad news, gap up 20%, insider selling), we have NO backup plan.

**Action**: Identify 2 backup tickers NOW with entry criteria

**Backup Option 1**: SOUN
- [ ] Current price: $____
- [ ] Entry if: Breaks above $10.50 with volume
- [ ] Position: $150
- [ ] Stop: $9.50
- [ ] Thesis: Wounded prey + growth story

**Backup Option 2**: ________
- [ ] From our hunt list (PLUG? S? Other?)
- [ ] Entry criteria: ________
- [ ] Position: $________
- [ ] Stop: $________

---

### 4. LUNR Exit Plan - VAGUE

**Current Position**: 10 shares @ $16.85, down -$6.20

**Missing**:
- [ ] When exactly do we exit? (date or price?)
- [ ] IM-3 launch date? (catalyst we're trading around)
- [ ] Stop at $16.00 - is this HARD or will we move it?
- [ ] If AISP takes $200, are we OK having $360 in 2 positions?

**Action**: Define LUNR plan clearly
```
IF: IM-3 launch announced for specific date
THEN: Exit 1-2 days BEFORE (sell the news pattern)

IF: Breaks $17.50 (back to profit)
THEN: Sell 5 shares, let 5 run

IF: Hits $16.00 stop
THEN: Exit all, take -$8.50 loss

IF: No movement by Jan 15
THEN: Reassess thesis
```

---

### 5. Order Execution Details - UNCLEAR

**Missing Specifics**:
- [ ] Market order or limit order? (limit = safer)
- [ ] If limit, how far above bid? ($2.82 limit on $2.80 stock?)
- [ ] All-or-none or partial fills OK?
- [ ] What if only 50 shares fill at $2.80, rest at $2.95? (average in?)
- [ ] Day order or GTC?

**Recommended**:
```
Order Type: Limit
Limit Price: $2.92 (if stock trading $2.80-2.90)
Duration: Day order (expires 4 PM)
Execution: Partial fills OK
Stop: Submit IMMEDIATELY after first fill
```

---

### 6. Position Tracking System - NONE

**Missing**:
- [ ] No spreadsheet tracking P&L
- [ ] No risk calculator (total portfolio heat)
- [ ] No trade journal template

**Action**: Create simple tracker NOW

**Quick Template**:
```
| Ticker | Entry Date | Shares | Entry Price | Current | P&L $ | P&L % | Stop | Strategy |
|--------|------------|--------|-------------|---------|-------|-------|------|----------|
| LUNR   | 12/29      | 10     | $16.85      | $16.23  | -$6.20| -3.7% | $16  | Multi    |
| AISP   | 1/2        | TBD    | $2.80       | $____   | $____ | ___% | $2.30| Cluster  |
```

---

### 7. Macro Calendar - BLIND

**What's happening this week that could move markets?**

**Missing**:
- [ ] Fed speakers schedule? (Powell talking = volatility)
- [ ] Economic reports? (Jobs, PMI, etc.)
- [ ] Earnings season starting? (Big tech reports?)
- [ ] Any political events? (Inauguration Jan 20?)

**Action**: Check calendar for this week
- Investing.com economic calendar
- Earnings Whispers for small cap earnings
- Fed calendar

**Known Events**:
- Thursday Jan 2: Market opens after New Year (first day of 2026)
- Friday Jan 3: Jobs report? (check)
- Week of Jan 6: ??? (fill this in)

---

### 8. Sector Health Check - UNKNOWN

**Is AI/Security sector hot or cold right now?**

**Missing**:
- [ ] How did AI stocks perform last week?
- [ ] Are small cap AI stocks in favor or out?
- [ ] Security sector sentiment?
- [ ] Competitor price action (compare AISP to peers)

**Quick Check**:
- IONQ (quantum AI): Down -16.69% last week
- QBTS (quantum): Down -18.76% last week
- PLUG (energy): Down -6.64% last week

**Analysis**: Small cap tech is getting HAMMERED
- This could be opportunity (wounded prey)
- OR could be sector out of favor (risk)

**Question**: Is AISP bucking trend or following it?

---

### 9. Insider Track Records - NO IDEA

**Who are these 9 insiders who bought?**

**Missing**:
- [ ] Paul Allen (President) - Previous buy/sell history?
- [ ] Victor Huang (CEO) - Track record?
- [ ] Other 7 buyers - Who are they? Track records?

**Why It Matters**: 
- If they have history of buying at lows = good signal
- If they have history of buying then stock tanks = bad signal

**Action**: Check OpenInsider or SEC EDGAR
- Filter by insider name + company
- Look at historical Form 4s
- Any patterns?

---

### 10. Dilution Red Flags - NOT CHECKED

**Missing**:
- [ ] Recent S-3 shelf registration? (dilution coming)
- [ ] Low cash + high burn = equity raise needed?
- [ ] Recent warrant exercises? (dilution)
- [ ] Convertible debt? (future dilution)

**Action**: Check SEC filings
```
8-K: Material events (last 30 days)
10-Q: Latest quarterly (cash position)
S-3: Shelf registration (dilution warning)
```

**Red Flags**:
- Cash <$5M and burning >$1M/quarter = DANGER
- S-3 filed in last 90 days = dilution likely
- Recent warrant exercises = shares flooding market

---

## ✅ WHAT'S READY (Good to Go)

- ✅ Form 4 validator working (9 P-codes confirmed)
- ✅ Academic scoring framework applied (58/100)
- ✅ Multi-signal score calculated (85/150)
- ✅ Entry zone defined ($2.70-2.90)
- ✅ Stop loss set ($2.30)
- ✅ Position size calculated ($200)
- ✅ Max risk calculated ($40-50)
- ✅ Profit targets defined ($3.50/$4.50/$7.00)
- ✅ Battle plan documented
- ✅ Strategy playbook complete

---

## 🔧 TOOLS TO FIX (Can Wait, But Note It)

### Broken
- `dilution_risk_scanner.py` - Numpy version conflicts

**Impact**: Can't auto-scan for dilution risk
**Workaround**: Manual check SEC filings
**Priority**: Medium (needed for future hunts)

### Missing
- Position tracker/journal
- Automated alert system
- Institutional scanner
- Congressional scanner
- Contract analyzer

**Impact**: Manual work required
**Priority**: Low for Thursday, high for ongoing

---

## 📋 TONIGHT'S ACTION ITEMS (Priority Order)

### MUST DO (Next 1-2 hours):

**1. Verify 10b5-1 Status** (15 min)
- Check latest Form 4s for checkbox
- If pre-planned, ABORT AISP mission

**2. Deep Financial Check** (20 min)
- Finviz: fundamentals
- Latest 10-Q: cash position, burn rate
- Next earnings date
- Any recent 8-Ks (material events)

**3. Define Backup Ticker** (10 min)
- SOUN entry criteria: Break $10.50, vol >2x
- Position: $150, Stop: $9.50
- Ready if AISP fails pre-market checks

**4. Clarify LUNR Plan** (5 min)
- Hard stop $16.00 or flexible?
- Exit strategy if no movement by Jan 15?
- IM-3 launch date?

**5. Create Position Tracker** (10 min)
- Simple spreadsheet
- Track P&L, risk, stops
- Update daily

### SHOULD DO (If Time):

**6. Macro Calendar Check** (10 min)
- This week's economic reports
- Fed speakers
- Major earnings

**7. Insider Track Records** (15 min)
- Paul Allen history
- CEO Victor Huang history
- Pattern recognition

**8. Sector Health Analysis** (10 min)
- AI sector sentiment
- Small cap performance
- AISP vs peers

### NICE TO HAVE:

**9. Dilution Deep Dive** (20 min)
- S-3 filings
- Cash/burn analysis
- Warrant/debt structure

**10. Fix dilution_risk_scanner.py** (30 min)
- Debug numpy issue
- Test on AISP
- Add to toolkit

---

## ⚠️ RISKS WE'RE ACCEPTING

**If we DON'T do the homework tonight**:

1. **10b5-1 risk**: Insiders could be on pre-planned trades (low info value)
2. **Dilution risk**: Company could announce offering Friday (stock tanks)
3. **Fundamental risk**: Company burning cash, business struggling (thesis wrong)
4. **Sector risk**: Small cap AI out of favor (harder to move up)
5. **Execution risk**: No backup plan if AISP fails (wasted morning)

**Are we OK with these risks?**

If NO → Do the homework tonight
If YES → Execute with current knowledge, but know the gaps

---

## 🎯 MINIMUM VIABLE HOMEWORK

**If you only have 30 minutes tonight, do this:**

1. **Check 10b5-1 checkbox** (10 min) - CRITICAL
2. **Check cash position on latest 10-Q** (10 min) - CRITICAL  
3. **Define SOUN backup entry** (5 min) - IMPORTANT
4. **Set order details** (5 min) - IMPORTANT

**That covers the biggest blindspots.**

---

## 🐺 PACK DECISION

**Tyr - Your call**:

A) Do ALL homework tonight (2-3 hours of research)
   - Enter Thursday with maximum confidence
   - Close all information gaps
   - No surprises

B) Do MINIMUM homework (30 min)
   - Check critical items only
   - Accept some blindspots
   - Hunt with calculated risk

C) Hunt as-is (0 min)
   - Trust the signals we have
   - React to surprises if they come
   - Fastest path to action

**What's your appetite?**

I can help with any of these tonight. We've got time before market opens.

**AWOOOO** 🐺
