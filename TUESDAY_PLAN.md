# 🐺 TUESDAY JAN 7 GAMEPLAN
## Pre-Market Brief & Action Plan

**Generated:** Monday, January 5, 2026 - 6:15 PM ET  
**For:** Tuesday, January 7, 2026 Market Open

---

## CURRENT POSITIONS (AS OF MONDAY CLOSE)

| Ticker | Monday Move | Status | Action Plan |
|--------|-------------|--------|-------------|
| **UUUU** | +10.61% | 🔥 Thesis working | Watch $19-20 for partial profit |
| **USAR** | +12.45% | 🔥 Venezuela news | CES meetings this week = watch for PR |
| **AISP** | +5.53% | ✅ Steady | Hold with stop below entry |

**Account Growth:** $779 → $827 (+6.16% Monday, +14% month, +25% last month)

---

## OVERNIGHT / PRE-MARKET CHECKLIST (6:30 AM Tuesday)

Run these scans before market open:

```bash
# 1. Check for overnight gaps
cd /workspaces/trading-companion-2026/tools
python3 premarket_gap_scanner.py

# 2. Check for any 8-K filings overnight
python3 sec_8k_scanner_v2.py --hours 12

# 3. Check CES monitor for news
python3 ces_2026_monitor.py
```

**What to look for:**
- UUUU/USAR gapping up or down?
- Any material 8-K contracts filed overnight?
- Any CES announcements from Sunday/Monday evening?

---

## MARKET OPEN PLAN (9:30 AM)

### IF UUUU GAPS UP TO $19-20+:
- ✅ **Take 50% profit** - Lock in gains from $779 → $827 run
- ✅ Let other 50% ride with stop at $17
- ✅ Reason: Above where insiders sold ($15.58), nuclear thesis still valid but take some chips off

### IF USAR GAPS UP TO $17+:
- ⚠️ **Watch first 30 minutes** - Venezuela news is DONE (happened Monday)
- ✅ If it holds gains and CES PR drops → Hold
- ✅ If no news and it fades → Take 70% profit
- ✅ Reason: News-driven spike, next catalyst is CES meetings (unknown timing)

### IF POSITIONS FLAT/DOWN:
- ✅ **Hold** - Thesis hasn't changed
- ✅ UUUU: Nuclear demand is real (AI data centers need power)
- ✅ USAR: CES meetings Jan 6-9, earnings Feb 5
- ✅ AISP: Insider conviction play, no catalyst needed

---

## CES 2026 WATCH LIST (Tuesday Jan 7)

**D-Wave (QBTS) Masterclass - 1 PM PT / 4 PM ET**
- Don't chase if it gaps up at open
- Watch after 4 PM for any announcements
- If it dumps during market hours, could be entry for Wednesday

**Richtech Robotics (RR)**
- Humanoid demo this week
- Already up 10.8% Friday
- If it pulls back to $3.40-3.50 with volume = entry
- If it gaps to $4.50+ = too late

**Quantum Computing (QUBT)**
- Demos Jan 7-8
- Already up 11.3% Friday
- High risk - only enter with tight stops

**DON'T CHASE:** If these gap up 5-10% at open, they're extended. Let them fade, then reassess.

---

## RED FLAGS TO WATCH

### 🚨 Friday Jobs Report (Jan 10, 8:30 AM)
- This is the BINARY RISK EVENT
- Cut 30-50% of positions by Wednesday close
- Don't get caught holding through Friday morning

### ⚠️ USAR Profit-Taking Risk
- +12.45% Monday after +19% Friday = 2-day rip
- Some profit-taking likely Tuesday
- If it gaps down, don't panic - check for CES news first

### ⚠️ Nuclear Sector Consolidation
- UUUU +10.61% is strong but extended short-term
- Could pull back to $16-17 before next leg up
- This would be HEALTHY, not a thesis break

---

## NEW ENTRY WATCH LIST

**ONLY consider if:**
1. You have day trades available (PDT check)
2. Setup is HIGH CONVICTION (70+ score)
3. Entry is clear with defined stop loss

**Potential plays:**
- None identified yet - wait for pre-market scan results
- CES plays already ran - don't chase
- Space plays (RDW, RKLB) extended - wait for pullback

**Best strategy:** MANAGE current winners, don't add new losers

---

## DISCIPLINE RULES (PDT RESTRICTIONS)

**You CAN'T:**
- Day trade more than 3x in 5 rolling days
- Sell same-day purchases without burning a day trade

**You CAN:**
- Sell positions bought yesterday or earlier (not a day trade)
- Take profits on UUUU/USAR Tuesday without PDT hit
- Add to positions if conviction is high

**Day Trade Budget:**
- Use ONLY for: emergency stop loss, or extraordinary profit-taking
- NOT for: routine exits, "feels like it might fade" trades

---

## FENRIR'S RESEARCH DELIVERED

**Jensen's CES Keynote (Monday 4 PM ET):**
- Physical AI focus = robotics, autonomous vehicles
- Validates nuclear thesis (AI needs power 24/7)
- Validates rare earth thesis (motors need magnets)

**USAR Venezuela Catalyst:**
- Maduro removed, opens doors for rare earth mining
- This news is DONE - already priced in Monday
- Next catalyst: CES customer meetings this week

**UUUU Multiple Tailwinds:**
- Winter energy demand ✅
- AI data center power needs ✅
- Trump admin nuclear support ✅
- Rare earth production milestone ✅

**Jobs Report Context:**
- Expected: +55-60K jobs, 4.5% unemployment
- Hot jobs = Fed stays hawkish = risk-off
- Cold jobs = rate cut hopes = risk-on
- Either way, volatility = manage risk Wed close

---

## ACTION SUMMARY

**Pre-market (6:30 AM):**
- [ ] Run pre-market gap scanner
- [ ] Check 8-K scanner for overnight filings
- [ ] Review CES monitor for news
- [ ] Check ATP for any overnight developments

**Market Open (9:30 AM):**
- [ ] Watch UUUU - if $19-20+, take 50% profit
- [ ] Watch USAR - if $17+ with no news, take 70% profit
- [ ] Don't chase CES gaps
- [ ] Update stop losses on remaining positions

**During Day:**
- [ ] Watch QBTS Masterclass at 4 PM ET for announcements
- [ ] Monitor for any 8-K contract filings (run scanner at 12 PM, 3 PM)
- [ ] Check if RR pulls back to $3.40-3.50 for entry

**End of Day:**
- [ ] Review what worked/didn't
- [ ] Plan Wednesday (jobs report risk mgmt)
- [ ] Check account total vs $827 baseline

---

## BROKKR'S TOOLS READY TO USE

**New scanners built (what ATP doesn't have):**
```bash
# Options flow - unusual call/put activity
python3 options_flow_scanner.py --watch

# Form 4 conviction - only Code "P" purchases
python3 form4_conviction_scanner.py --days 60

# 8-K contracts - fixed filters, relevant sectors only
python3 sec_8k_scanner_v2.py --hours 24 --watch

# Pre-market gaps - quick morning scan
python3 premarket_gap_scanner.py
```

**All committed to git. All executable. All ready.**

---

## THE GOAL

**Not** to capture every move.  
**Not** to trade 20 tickers.  
**Not** to use every scanner.

**Goal:** Protect Monday's gains. Grow the account consistently. Stay disciplined.

$827 is the new baseline. Don't give it back.

---

🐺 **LLHR**

**God forgives. Brothers don't.**  
**The wolf remembers. The wolf returns.**

*Brokkr*  
*Monday, January 5, 2026 - 6:30 PM ET*  
*Tools built. Plan ready. Tyr leads.*
