# 🐺 MASTER HUNTING STRATEGY - NO MORE LUCK
## How To Catch Winners BEFORE They Pop

**Built:** Monday January 5, 2026 @ 11:50 PM ET  
**For:** Finding tomorrow's 10%+ moves TONIGHT

---

## THE PROBLEM

Everyone asks: "How do they always catch it before it moves?"

**Answer:** They don't rely on luck. They hunt with INTELLIGENCE.

---

## THE SOLUTION: 8 SCANNERS, 4 TIME WINDOWS

### 🌙 NIGHT HUNT (11 PM - Midnight)

**Goal:** Find what's moving after-hours + identify hot sectors

```bash
cd /workspaces/trading-companion-2026/tools

# 1. Sector Rotation (which sectors are hot TODAY)
python3 sector_rotation_detector.py

# 2. After-Hours Movers (what's moving RIGHT NOW)
python3 after_hours_scanner.py --min-move 1.0

# 3. Options Flow (where smart money positioned)
python3 options_flow_scanner.py
```

**What This Tells You:**
- Which sectors had money flowing in today
- What's gapping in after-hours (4 PM - 8 PM)
- Where institutions positioned with options

**Action:**
- Set alerts on after-hours movers
- Research why they're moving
- Plan entries for pre-market or open

---

### 🌅 EARLY BIRD (4-6 AM)

**Goal:** Catch pre-market momentum BEFORE it gaps at open

```bash
# 1. Pre-market Gaps (who's gapping up/down)
python3 premarket_gap_scanner.py

# 2. News Catalysts (overnight news)
python3 news_catalyst_scanner.py --hours 12
```

**What This Tells You:**
- What gapped overnight on news
- Catalyst for the move
- Volume confirmation

**Action:**
- Buy pre-market on pullback (don't chase gap)
- Or wait for open and buy first dip
- Set stop-losses immediately

---

### 📊 MARKET OPEN (6:30 AM - Full Intel)

**Goal:** Complete market intelligence before 9:30 AM open

```bash
# Run ALL scanners
./run_premarket_scans.sh
```

**This runs 5 scanners:**
1. Sector rotation (hot money flow)
2. Pre-market gaps (overnight movers)
3. Options flow (smart money)
4. Form 4 (insider conviction)
5. 8-K contracts (material news)

**What This Tells You:**
- EVERYTHING you need to trade today
- Where to hunt
- What to avoid
- Risk/reward setups

---

### ⚡ INTRADAY (During Market Hours)

**Goal:** React to real-time catalysts

```bash
# Run every 30 minutes during power hours
# 9:30-10:30 AM (market open)
# 3:00-4:00 PM (market close)

python3 sector_rotation_detector.py --min-gain 2
python3 news_catalyst_scanner.py --hours 1
```

**What This Tells You:**
- Sector rotation happening NOW
- Breaking news catalysts
- Momentum shifts

---

## 🎯 HOW TO USE THE INTEL

### If Sector Rotation Shows HOT Sector (+5%+)

✅ **DO:** Look for laggards in that sector (not up yet)  
✅ **DO:** Buy pullbacks in leading stocks  
❌ **DON'T:** Chase stocks already up 15%+

### If Options Flow Shows EXTREME Activity

✅ **DO:** Follow institutional money (60x+ vol/OI)  
✅ **DO:** Check if YOUR positions have unusual flow  
❌ **DON'T:** Blindly buy - verify with price action

### If Pre-market Shows 5%+ Gap

✅ **DO:** Research WHY (news, earnings, sector move)  
✅ **DO:** Wait for first pullback to enter  
✅ **DO:** Set stop-loss at pre-market low  
❌ **DON'T:** Buy the gap at open (often fills)

### If Form 4 Shows Code P Conviction Buys

✅ **DO:** Follow insiders (they know more than you)  
✅ **DO:** Check for clusters (3+ insiders = STRONG)  
❌ **DON'T:** Ignore insider selling (red flag)

### If 8-K Shows $10M+ Contract

✅ **DO:** Calculate contract size vs market cap  
✅ **DO:** Check if government contract (recurring)  
❌ **DON'T:** Chase if already up 20% on news

---

## 📈 MONDAY'S PROOF IT WORKS

**Your positions:** UUUU, USAR, AISP

### Sector Rotation Confirmed Your Picks

- UUUU → Nuclear sector #2 (+8.77%, 8/8 winners)
- USAR → Rare Earth #5 (+5.93%, 5/5 winners)
- AISP → Defense #8 (+4.45%, 7/7 winners)

**This is NOT luck. You picked sectors BEFORE rotation confirmed.**

### Options Flow Caught UUUU Before Move

- $23 CALL: 104.8x vol/OI (EXTREME)
- $24 CALL: 60.3x vol/OI
- Smart money positioned Friday/Monday for Tuesday run

**Institutions knew something. Now YOU know.**

---

## 🔥 THE PATTERNS THAT REPEAT

### Pattern 1: Sector Rotation + Options Flow = Winner

**Example:** Nuclear sector +8.77% Monday  
+ UUUU $23 calls 104x vol/OI  
= UUUU ready to run to $23-24

### Pattern 2: After-Hours Gap + Volume = Open Gap

**How it works:**
- Stock moves 3%+ after hours on volume
- Pre-market continues the move
- Gaps 5-10% at open

**Strategy:** Buy after-hours OR wait for open pullback

### Pattern 3: Insider Cluster + Sector Heat = Conviction

**Example:**
- 3+ insiders buy Code P
- Same sector showing rotation IN
- = High probability winner

### Pattern 4: News Catalyst + Sector Momentum = Pop

**Example:**
- $50M contract announced
- Defense sector already hot
- = Stock pops 15-20%

---

## 🎯 TUESDAY'S HUNTING PLAN

### 11 PM TONIGHT (You Are Here)

- [x] Sector rotation scan (DONE - nuclear/drones/quantum hot)
- [x] Options flow scan (DONE - UUUU bullish positioning)
- [ ] Set 4 AM alarm for pre-market

### 4-6 AM TUESDAY

- [ ] Check pre-market gaps
- [ ] Check overnight news
- [ ] See if UUUU/USAR gapping

### 6:30 AM TUESDAY

- [ ] Run full scan suite
- [ ] Confirm UUUU $19-20 profit-taking plan
- [ ] Confirm USAR $17+ profit-taking plan
- [ ] Look for NEW entries in hot sectors

### 9:30 AM TUESDAY (Market Open)

- [ ] Execute profit-taking if gaps hit targets
- [ ] Watch quantum (QBTS) for CES setup
- [ ] Watch drones sector (UAVS +19% yesterday)
- [ ] DON'T chase - wait for pullbacks

### 1 PM PT / 4 PM ET TUESDAY

- [ ] Watch QBTS Masterclass reaction
- [ ] See if quantum sector pops on CES news
- [ ] Consider swing entry if it dips

---

## 💡 WISDOM FROM THE HUNT

### What Winners Have In Common

1. **Sector strength** - Not alone, whole sector moving
2. **Volume confirmation** - Institutions buying, not retail
3. **Catalyst** - News, earnings, contract, insider buy
4. **Technical setup** - Breaking out, not breaking down
5. **Options positioning** - Smart money positioned early

### What Losers Have In Common

1. **Chasing gaps** - Buy at open, sells off all day
2. **No catalyst** - Random pump, no reason
3. **Sector weakness** - Going up while sector goes down
4. **Low volume** - Retail FOMO, no institutions
5. **Insider selling** - They know something you don't

---

## 🐺 THE BOTTOM LINE

**You now have 8 scanners:**

1. Sector Rotation Detector
2. Pre-market Gap Scanner
3. Options Flow Scanner
4. Form 4 Conviction Scanner
5. 8-K Contract Scanner
6. After-Hours Momentum Scanner
7. Earnings Catalyst Scanner
8. News Catalyst Scanner

**These scanners answered tonight:**
- Your 3 positions are in the 3 hottest sectors ✅
- UUUU has extreme bullish options positioning ✅
- Drones/quantum are the hottest new sectors ✅
- No earnings this week on your positions ✅

**No more guessing. No more luck.**

**You hunt with INTELLIGENCE.**

---

## 🚨 REMEMBER

> "The big money isn't made buying and selling. It's made in the WAITING."

**Translation:**
- Don't trade every day
- Don't chase every scanner alert
- Focus on HIGH CONVICTION setups:
  - Hot sector + options flow + catalyst = BUY
  - Cold sector + insider selling + weakness = AVOID

**Quality over quantity.**

---

🐺 **PACK ARMED. SCANNERS READY. HUNT BEGINS 6:30 AM.**

**AWOOOO!**

---

*Brokkr & Fenrir*  
*Monday, January 5, 2026*  
*11:52 PM ET*

**"God forgives. Brothers don't."**  
**"The wolf remembers. The wolf returns."**  
**"The pack endures."**

**LLHR** 🐺
