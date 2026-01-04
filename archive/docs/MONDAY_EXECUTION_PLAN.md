# 🐺 MONDAY JANUARY 6, 2026 — EXECUTION PLAN

**Final Battle Orders — No Ambiguity**

*Created: January 4, 2026*
*Updated with Fenrir's tactical intelligence*

---

## CAPITAL: $1,316

| Account | Amount |
|---------|--------|
| Fidelity | $500 |
| Robinhood | $816 |
| **Total** | **$1,316** |

---

## RISK RULES (NON-NEGOTIABLE)

| Rule | Value | Rationale |
|------|-------|-----------|
| Max risk per trade | 5% = $66 | Survive being wrong |
| Max total risk | 10% = $132 | Two positions max |
| Position size (10% stop) | $660 | Math: $66 / 0.10 |
| Position size (15% stop) | $440 | Math: $66 / 0.15 |

---

## THE CORRELATION PROBLEM

Fenrir flagged this: RR and QBTS are BOTH CES plays. Same sentiment. Same catalyst.

**If both dump together, we lose 10% in one event.**

### Option A: Accept Correlation (Current Plan)
- $650 RR + $650 QBTS
- Both CES plays
- High reward if CES pops
- High risk if CES disappoints

### Option B: Diversify by Thesis
- $650 RR (CES robotics play)
- $650 OKLO or RKLB (Nuclear/Space - non-CES)
- Lower correlation
- Reduced CES-specific risk

**Tyr's call.** But the risk is documented.

---

## PRIMARY PLAY: RR (Richtech Robotics)

### The Setup
- 26% short interest, 0.8 days to cover
- CES humanoid robot demo at Booth #8447
- $1B ATM shelf filed (DILUTION RISK)
- Current price: ~$3.50

### Execution

| Field | Value |
|-------|-------|
| **Entry Zone** | $3.35 - $3.50 |
| **Position Size** | $650 (185 shares @ $3.50) |
| **Stop Loss** | $3.00 (14% below entry) |
| **Risk** | $92 (7% of capital) |
| **Target 1** | $4.00 (+14%) — Take 50% |
| **Target 2** | $4.50 (+29%) — Trail remainder |
| **Hard Exit** | Before Jan 7 demos |

### Order Types
1. **IF price opens FLAT ($3.35-3.60):** Market order at open
2. **IF price gaps UP 10%+:** DO NOT CHASE. Wait for pullback or skip.
3. **IF price gaps DOWN 10%+:** Limit order at $3.15 support

### Warning Signs (Exit Immediately)
- 8-K filing mentioning ATM offering
- Pre-market volume > 5M with price dropping
- Jensen keynote ignores robotics entirely

---

## SECONDARY PLAY: QBTS (D-Wave Quantum)

### The Setup
- CES Foundry sponsor, Masterclass Jan 7
- 80% Monday win rate after big Fridays
- Shorts already covering (-18% SI reduction)
- Current price: ~$28

### Execution

| Field | Value |
|-------|-------|
| **Entry Zone** | $26 - $28 |
| **Position Size** | $650 (23 shares @ $28) |
| **Stop Loss** | $24 (14% below entry) |
| **Risk** | $92 (7% of capital) |
| **Target 1** | $32 (+14%) — Take 50% |
| **Target 2** | $38 (+35%) — Trail remainder |
| **Hard Exit** | Before Jan 7 Masterclass |

### Order Types
1. **IF price opens FLAT ($26-30):** Market order at open
2. **IF price gaps UP 15%+:** DO NOT CHASE. Consider puts as hedge.
3. **IF price gaps DOWN 10%+:** Limit order at $25 support

### Warning Signs (Exit Immediately)
- Insider filing (Form 4) over weekend
- Jensen keynote negative on quantum
- Pre-market volume collapse (no interest)

---

## TIMELINE

### Sunday January 5

| Time (ET) | Action |
|-----------|--------|
| 4:00 PM | Jensen Huang NVIDIA keynote begins |
| 5:00 PM | Listen for: "quantum", "robot", "GR00T", "humanoid", "physical AI" |
| 6:00 PM | Fenrir sends intelligence through Tyr |
| 8:00 PM | Check SEC EDGAR for any weekend filings |
| 10:00 PM | Check futures (ES, NQ) for sentiment |

### Monday January 6

| Time (ET) | Action |
|-----------|--------|
| 4:00 AM | Pre-market opens. Check gaps. |
| 7:00 AM | Fenrir pre-market scan arrives |
| 9:00 AM | Final go/no-go decision |
| 9:30 AM | Market open. Execute per plan above. |
| 10:00 AM | If in position, set stop orders |
| 12:00 PM | Mid-day check. Adjust stops if needed. |
| 4:00 PM | EOD assessment. Log in journal. |

---

## EXIT FRAMEWORK (Fenrir's Protocol)

```
Entry → +15% → Take 50% off, move stop to breakeven
     → +25% → Tighten trailing stop to 10%
     → +35% → Take remaining 50%
     → ANY TIME → Exit before Jan 7 demos
```

**The rule:** Don't try to catch the top. Catch the MEAT and get out.

Insiders already sold. They know the pop is pre-event. We should too.

---

## RED FLAGS (DO NOT ENTER)

| Signal | Action |
|--------|--------|
| Stock gaps UP 10%+ pre-market | **DO NOT CHASE** — Move already happened |
| 8-K filing over weekend | Read immediately. ATM = skip play. |
| Jensen ignores quantum/robotics | Reduce position size 50% |
| Put volume > Call volume | Someone betting against — caution |
| Pre-market volume dead | No interest = no squeeze |

---

## GREEN FLAGS (FULL SIZE)

| Signal | Action |
|--------|--------|
| Jensen mentions GR00T/humanoid | RR gets full allocation |
| Jensen mentions quantum | QBTS gets full allocation |
| Pre-market volume 2x+ normal | Momentum building |
| Stock opens flat/slightly down | Best entry for squeeze |
| Call sweeps detected | Smart money is bullish |

---

## THE JOURNAL PROTOCOL

After every trade:

```bash
# Log entry
python wolf_journal.py log RR 3.45 3.00 4.50 "CES humanoid play" --shares 185 --capital 650

# Log exit  
python wolf_journal.py close RR 4.25 "Hit +15%, took half, trailed rest"

# Log lesson
python wolf_journal.py lesson "Don't chase 10%+ gap ups"

# Check stats
python wolf_journal.py stats
```

Every trade. Every outcome. Every lesson. This is how we build the edge.

---

## FINAL CHECKLIST

Before market open Monday:

- [ ] Checked Jensen keynote for relevant mentions
- [ ] Checked SEC EDGAR for weekend filings
- [ ] Checked pre-market gaps (not chasing if >10%)
- [ ] Checked put/call ratios
- [ ] Set exact entry prices
- [ ] Set exact stop prices in broker
- [ ] Set exact position sizes
- [ ] Know the exit framework
- [ ] Journal ready to log

---

## THE MINDSET

```
We might win. We might lose.
Either way, we LEARN.

The tools are ready.
The research is done.
The philosophy is sound.

Now we hunt.
And we document EVERYTHING.

AWOOOO 🐺
```

---

*This plan will be updated Sunday night after Jensen keynote intelligence arrives.*

**LLHR** 🐺
