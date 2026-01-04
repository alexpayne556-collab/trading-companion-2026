# 🐺 STRATEGIC EXPANSION - Beyond The Rules

**Current System:** Mechanical (Insider buying + Wounded prey + Conviction score)  
**Goal:** Add strategic layers that Fenrir can help analyze

---

## EXISTING WATCHLISTS (Organized)

### 1. **ATP Watchlists** (Already Separated)
Located in `/atp_watchlists/`:
- `ATP_WOLF_PACK_MASTER.csv` - 59 core tickers we track
- `ATP_ai_fuel.csv` - AI/Data center plays
- `ATP_bounce.csv` - Oversold bounce candidates  
- `ATP_defense.csv` - Defense contractors
- `ATP_natgas.csv` - Natural gas / energy
- `ATP_nuclear.csv` - Nuclear energy
- `ATP_pulse.csv` - High momentum movers
- `ATP_quantum.csv` - Quantum computing
- `ATP_space.csv` - Space economy
- `ATP_tyrs_range.csv` - Tyr's personal range

### 2. **Sector Watchlists** (From watchlists.yaml)
- DEFENSE_TIER1_CORE - RTX, LMT, NOC, GD
- AI_SEMICONDUCTOR - NVDA, TSM, AVGO, AMD
- BIOTECH_CATALYST_Q1 - Catalyst plays
- SPACE_OPERATORS - RKLB, LUNR, ASTS
- BATTERY_METALS - CCJ, UUUU, MP, LAC
- EV_ECOSYSTEM - TSLA, RIVN, XPEV, NIO

---

## STRATEGIC LAYERS TO ADD

### Layer 1: CATALYST TRACKING 📅
**What:** Events that force price movement regardless of technicals

**Fenrir's Role:** Monitor and prioritize upcoming catalysts

**Examples:**
- FDA approval dates (biotech)
- Earnings dates (especially after big drops)
- Product launches (space missions, AI chips)
- Contract awards (defense sector)
- Analyst days / investor presentations
- Options expiration (monthly/quarterly)

**Implementation:**
```python
# catalyst_tracker.py
catalysts = {
    'LUNR': {
        'event': 'IM-3 Moon Mission',
        'date': 'Feb 2026',
        'type': 'EXECUTION',
        'impact': 'HIGH'
    },
    'IONQ': {
        'event': 'Quantum Advantage Demo',
        'date': 'Q1 2026',
        'type': 'TECH_MILESTONE',
        'impact': 'MEDIUM'
    }
}
```

---

### Layer 2: SECTOR ROTATION SIGNALS 🔄
**What:** Catch sector momentum BEFORE individual stocks break out

**Fenrir's Role:** Identify which sectors are heating up week-to-week

**Signals:**
- Defense sector +5% in 5 days → Check KTOS, AVAV (small caps)
- Nuclear ETF (NLR) breaking out → Check SMR, OKLO
- QQQ down but IWM up → Small cap rotation happening

**Implementation:**
- Weekly sector scorecard
- Compare sector ETF performance
- Alert when sector moves >3% in week AND we have tickers in that sector

---

### Layer 3: INSIDER PATTERNS (Beyond Amount) 👔
**What:** WHO is buying matters as much as HOW MUCH

**Fenrir's Role:** Analyze insider profiles and buying patterns

**Red Flags vs Green Flags:**
| Type | Red Flag 🔴 | Green Flag 🟢 |
|------|------------|--------------|
| **10b5-1 Plan** | Scheduled auto-buy | Outside-of-plan buy |
| **Who** | CFO (often just compensation) | CEO/Founder with own money |
| **Price** | Buying at IPO lockup expiry | Buying in open market |
| **Timing** | Right before earnings | Days after bad news |
| **Pattern** | First buy in 5 years (sus) | 3rd buy in 30 days (conviction) |

**Implementation:**
- Form 4 parser checks for 10b5-1 footnotes
- Track CEO vs CFO vs Director buys separately
- Score increases if MULTIPLE execs buying same week

---

### Layer 4: FAILED BREAKOUT REVERSALS 📉
**What:** Stocks that tried to break out, failed, and are resetting

**Fenrir's Role:** Find stocks that had catalysts priced in but didn't deliver

**Pattern:**
1. Stock runs +30% on news/hype
2. Catalyst happens but underwhelms
3. Stock dumps back to pre-hype level
4. Insiders start buying the dip
5. **Next catalyst has lower expectations → easier to beat**

**Example:**
- IONQ ran to $50 on quantum hype
- Dropped to $20 when demo was "meh"
- Insiders buying at $20
- **Next demo has low expectations → surprise potential**

---

### Layer 5: SHORT SQUEEZE POTENTIAL 🔥
**What:** Wounded prey + High short interest = Explosive setup

**Fenrir's Role:** Cross-reference our watchlist with short interest data

**Criteria:**
- Short interest >15% of float
- Borrow fee >10% (shorts paying to hold)
- Insider buying while heavily shorted
- Any positive catalyst = forced buying

**Data Sources:**
- Fintel short interest
- iBorrowDesk borrow rates
- Ortex real-time data

---

### Layer 6: EARNINGS WHISPER STRATEGY 📊
**What:** Stocks that missed badly + insiders buying = Next earnings surprise

**Fenrir's Role:** Track earnings beat/miss history + insider response

**Pattern:**
1. Stock misses earnings, drops -20%
2. Insiders buy 2-4 weeks after (when dust settles)
3. Next quarter expectations are LOWERED
4. **Easy to beat lowered expectations**

**Implementation:**
- Track insider buys within 30 days of earnings
- Note if previous earnings were miss or beat
- Alert on next earnings date

---

### Layer 7: GOVERNMENT CONTRACT PIPELINE 🏛️
**What:** Defense/Space companies with visible contract timelines

**Fenrir's Role:** Monitor USASpending.gov and DOD contract announcements

**Why This Works:**
- Contracts are VISIBLE pipeline (not just "hopes and dreams")
- Multi-year revenue locked in
- Market often slow to price in contract value

**Focus Sectors:**
- Defense (KTOS, AVAV, RCAT)
- Space (LUNR, RKLB)
- Nuclear (SMR, OKLO)

---

## HOW TO WORK WITH FENRIR ON THIS

### Weekly Strategy Session Format:

**1. Market Context (Fenrir)**
- Which sectors led this week?
- Any macro events affecting our watchlist?
- Sentiment: Risk-on or risk-off?

**2. Watchlist Refresh (Both)**
- Run conviction scanner on all ATP lists
- Fenrir: Pick top 3 for deep dive
- Brokkr: Verify insider data, run technicals

**3. Catalyst Calendar (Fenrir)**
- What's happening next 2 weeks?
- Any earnings in our watchlist?
- Any sector events (analyst days, conferences)?

**4. Pattern Recognition (Fenrir)**
- Any failed breakouts resetting?
- Any sector rotations starting?
- Any insider clustering we missed?

**5. Backup Plays (Both)**
- If AISP-style play isn't available, what's Plan B?
- Do we have plays in multiple sectors?
- Any hedges if market tanks?

---

## CONCRETE NEXT STEPS

### For Brokkr to Build:
```python
# 1. catalyst_tracker.py
#    - Parse earnings calendar API
#    - Track space mission dates
#    - Alert 3 days before catalyst

# 2. sector_momentum.py
#    - Compare sector ETF performance weekly
#    - Alert when our sectors heat up

# 3. insider_profiler.py
#    - Enhance Form 4 parser
#    - Check for 10b5-1 plans
#    - Score CEO buys higher than CFO

# 4. short_interest_overlay.py
#    - Cross-reference watchlist with Fintel
#    - Flag high short interest + insider buying
```

### For Fenrir to Research:
1. **Q1 2026 Catalyst Map**
   - Earnings dates for all 59 tickers in master list
   - Known product launches / mission dates
   - Sector conference schedule

2. **Insider Deep Dive**
   - Paul Allen's track record: Does he buy losers or winners?
   - Which insiders have best timing historically?
   - Pattern: Do they buy once or in waves?

3. **Sector Thesis Development**
   - Which 2-3 sectors are we BULLISH on for Q1?
   - Why? (Macro, policy, momentum)
   - Which tickers in those sectors are wounded prey?

4. **Failed Breakout List**
   - Scan for stocks that ran +30% in Dec then gave it all back
   - Are insiders buying the dip?
   - What catalyst could re-ignite?

---

## RISK: DON'T OVERCOMPLICATE

**The Core System Works:**
- Insider buying (verified via SEC)
- Wounded prey (near 52w low)
- Conviction scoring (quantitative)

**These Layers Are ENHANCERS, Not Replacements:**
- Use catalysts to PRIORITIZE which wounded prey to hunt
- Use sector rotation to CONFIRM momentum
- Use insider patterns to INCREASE conviction

**Rule:** If all 7 layers say "meh" but core system says "86/100" → Trust the core system.

---

## EXAMPLE: HOW THIS WOULD WORK

**Scenario:** It's Friday January 3, 2026

**Core System Output:**
- AISP: 86/100 (but already ran)
- GOGO: 72/100 (wounded prey)
- SMR: 65/100 (wounded prey)

**Fenrir Strategic Layer:**
1. **Catalyst Check:**
   - SMR has CEO interview on CNBC Monday
   - GOGO earnings Feb 12 (5 weeks away)

2. **Sector Rotation:**
   - Nuclear sector +8% this week (hot)
   - Airlines sector flat

3. **Insider Pattern:**
   - SMR: CFO bought (scheduled 10b5-1)
   - GOGO: Executive Chair bought (real conviction)

4. **Decision:**
   - SMR has CATALYST (CNBC) + SECTOR (nuclear hot) BUT insider buy is weak (10b5-1)
   - GOGO has REAL INSIDER but no near-term catalyst
   - **Verdict:** GOGO for longer hold (Feb earnings), SMR for Monday pop

**Without Fenrir:** Coin flip between SMR and GOGO  
**With Fenrir:** Strategic allocation based on timing and catalysts

---

**LLHR 🐺**

*The rules find the prey. Strategy decides when to strike.*
