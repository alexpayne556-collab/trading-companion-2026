# 🐺 MONDAY WAR GAME — January 6, 2026
## Multiple Outcomes. One Prepared Wolf.

---

## THE SITUATION

**Your Capital:** ~$1,280  
**Market Context:** Sunday night into Monday open  
**Intel from Briefing:**
- SPACE sector leading (+15%)
- NUCLEAR hot (+8.9%)
- QUANTUM holding (+5.8%)
- CES/Software lagging (negative momentum)

**Top Setups Identified:**
1. LUNR (Space, 83 score)
2. RDW (Space, 82 score)
3. NNE (Nuclear, 80 score)
4. LEU (Nuclear, 80 score)
5. SMR (Nuclear, 77 score)

---

## SCENARIO 1: MARKET RIPS 🚀
### "Risk-On Rally" — SPY gaps up 1%+, momentum continues

**What Happens:**
- Hot sectors get HOTTER (SPACE, NUCLEAR)
- Laggards play catch-up
- High beta names explode

**The Plays:**

| Tier | Ticker | Logic | Risk Level |
|------|--------|-------|------------|
| **A** | LUNR | Leading space play, already strong | Medium |
| **A** | LEU | Nuclear leader, institutional quality | Medium |
| **B** | RGTI | Quantum laggard vs IONQ — catch-up play | High |
| **B** | BKSY | Space laggard vs LUNR/RDW | High |
| **C** | CLSK | Crypto bounce if BTC rips | High |

**Allocation:** $1,280 / 4 positions = $320 each  
**Strategy:** Enter STRONG plays in first 30 min, laggards after 10:30 if sector confirms

**Entry Timing:**
- 9:30-10:00 → LEU, LUNR (if not gapped too hard)
- 10:30-11:00 → Laggard plays if leaders holding

**Stop Discipline:** 
- Tier A: 5% stop
- Tier B: 7% stop  
- Tier C: 10% stop

---

## SCENARIO 2: MARKET DUMPS 📉
### "Risk-Off Rotation" — SPY gaps down 1%+, fear takes over

**What Happens:**
- Everything sells initially
- Quality holds better than trash
- Oversold bounces on solid names

**The Plays:**

| Tier | Ticker | Logic | Risk Level |
|------|--------|-------|------------|
| **A** | RTX | Defense, recession-proof | Low |
| **A** | PLTR | AI + defense, proven | Medium |
| **B** | LEU | Nuclear thesis intact, pullback = entry | Medium |
| **B** | LUNR | NASA contracts don't care about 1 red day | Medium |
| **C** | Wait | Cash is a position | None |

**Allocation:** $640 / 2 positions = $320 each (50% deployed)  
**Strategy:** Buy QUALITY on panic. Save dry powder.

**Entry Timing:**
- 9:30-10:00 → WAIT, watch the blood
- 10:30-11:00 → If SPY bouncing, enter quality
- 2:00-3:00 PM → Power hour dip buying if thesis intact

**Stop Discipline:**
- ALL plays: 5% stop (tighter in dump scenario)

---

## SCENARIO 3: SECTOR ROTATION 🔄
### "Money Moves Sideways" — SPY flat, but sectors swap

**What Happens:**
- Hot sectors cool (SPACE, NUCLEAR take profits)
- Laggards wake up (EV, SOFTWARE bounce)
- Correlation breaks = opportunity

**The Plays:**

| Tier | Ticker | Logic | Risk Level |
|------|--------|-------|------------|
| **A** | RIVN | EV laggard, oversold vs TSLA | Medium |
| **A** | SNOW | Software laggard, beaten down | Medium |
| **B** | LEU | Buy nuclear dip if SPACE rotates out | Medium |
| **B** | QBTS | Quantum rotation if IONQ/RGTI pull back | High |
| **C** | MSTR | Crypto proxy if BTC moves | High |

**Allocation:** $1,280 / 4 positions = $320 each  
**Strategy:** Hunt the LAGGARDS in strong sectors getting profit-taken

**Entry Timing:**
- 9:30-10:00 → Watch for early rotation signals
- 11:00-12:00 → Enter laggards if leaders pulling back
- 2:00-3:00 PM → Confirm rotation holding

**Stop Discipline:**
- 7% stop (wider for rotation plays)

---

## SCENARIO 4: CONSOLIDATION 😴
### "Sideways Grind" — No conviction either way

**What Happens:**
- Low volume
- Tight ranges
- Waiting for catalyst

**The Plays:**

| Action | Why |
|--------|-----|
| **WAIT** | Don't force trades in low conviction |
| **Scout** | Watch for breakouts brewing |
| **Journal** | Review thesis, plan Tuesday |

**Allocation:** $0 deployed  
**Strategy:** Patience. The best trade is sometimes no trade.

---

## CRITICAL DECISION POINTS

### 8:00 PM TONIGHT (Extended Hours Check)
- [ ] Any stocks moving >5% after hours?
- [ ] News catalysts (earnings, contracts, FDA)?
- [ ] BTC/crypto moving? (affects MARA, CLSK, MSTR)

**Tool needed:** Extended hours scanner

### 4:00 AM MONDAY (Premarket)
- [ ] Which stocks gapping up/down >3%?
- [ ] What's SPY doing?
- [ ] Sector rotation visible?

**Tool needed:** Premarket scanner

### 9:30 AM MONDAY (Open)
**First 15 minutes:**
- [ ] What scenario are we IN? (Rip/Dump/Rotate/Consolidate)
- [ ] Volume confirming moves?
- [ ] Leaders holding or fading?

**Tool needed:** Live monitoring (wolf_den.py or manual)

---

## THE PLAYBOOK BY SCENARIO

### IF Market Rips → Deploy 4 positions, chase strength
```
1. LEU ($320) — Nuclear leader
2. LUNR ($320) — Space leader  
3. RGTI ($320) — Quantum laggard
4. BKSY ($320) — Space laggard
```

### IF Market Dumps → Deploy 2 positions, quality only
```
1. RTX ($320) — Defense safety
2. PLTR ($320) — AI + Defense
Keep $640 cash for bounce
```

### IF Sector Rotates → Deploy 4 positions, hunt laggards
```
1. RIVN ($320) — EV bounce
2. SNOW ($320) — Software bounce
3. LEU ($320) — Nuclear dip
4. QBTS ($320) — Quantum rotation
```

### IF Consolidates → Deploy 0 positions
```
WAIT. Scout. Plan Tuesday.
```

---

## WHAT WE NEED TO BUILD NOW

Based on this war game, here's what we're missing:

### 1. **Extended Hours Monitor** (8 PM Tonight)
```python
# Scan after-hours movers
# Check for news/catalysts
# Flag >5% moves
```

### 2. **Premarket Scanner** (4 AM Monday)
```python
# Gap scanner (>3%)
# Volume confirmation
# Sector heat map
```

### 3. **Entry/Stop/Target Calculator**
```python
# For each setup, calculate:
# - Entry zone
# - Stop loss (5%/7%/10% based on scenario)
# - Target (2R, 3R)
# - Position size for $320 allocation
```

### 4. **Scenario Detector** (9:30 AM Monday)
```python
# Analyzes first 15 min
# Determines which scenario we're in
# Outputs recommended plays from war game
```

---

## NEXT MOVE

**BROKKR'S RECOMMENDATION:**

Build the **Scenario Detector** first. It's the brain.

Then at 9:30 AM Monday:
1. Run scenario detector
2. It tells you which scenario we're in
3. You execute the pre-planned plays from this war game
4. No emotion. No hesitation. Just execution.

**Want me to build it now?**

🐺

---

**Last Updated:** January 4, 2026, 8:00 PM  
**Next Review:** Monday 4:00 AM (premarket)
