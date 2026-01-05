# 🐺 QUICK REFERENCE CARD
## The 15-Minute Edge - Cheat Sheet

---

## ⚡ SCANNER COMMANDS

```bash
# Morning prep (all scanners)
cd /workspaces/trading-companion-2026/tools

python3 sec_8k_contract_scanner.py --hours 16        # Overnight 8-Ks
python3 wounded_prey_scanner.py                      # Tax loss bounces
python3 cross_signal_validator.py --min-signals 3   # HIGH CONVICTION
python3 cluster_buy_scanner.py                       # Insider clusters

# Continuous monitoring
python3 sec_8k_contract_scanner.py --continuous      # Every 10 min

# Weekly checks
python3 congress_tracker.py                          # Congressional trades
```

---

## 🎯 CONVICTION SCORING

| Score | Level | Action |
|-------|-------|--------|
| **70-100** | 🔥 HIGH CONVICTION | Ready to hunt — verify & enter |
| **50-69** | 💪 STRONG | Watch closely — needs confirmation |
| **30-49** | 📊 MODERATE | Early watch — wait for more signals |
| **0-29** | ⚪ LOW | Pass — not enough conviction |

---

## 📊 SIGNAL BREAKDOWN

### Cross-Signal Validator (0-100 points):
- **Wounded Prey**: 0-30pts (recovering from -30%+ decline)
- **Insider Buying**: 0-30pts (clusters, C-Suite)
- **8-K Contracts**: 0-25pts (material contract filings)
- **Thesis Alignment**: 0-15pts (AI Fuel Chain priority)

### Insider Clusters:
- **🔥 Tier 1**: 3+ buyers within 7 days (HIGHEST CONVICTION)
- **💪 Tier 2**: 3+ buyers extended timeframe
- **📈 Potential**: 2 buyers (watch list)

### Wounded Prey:
- **Down 40%+** = biggest bounce potential
- **5d recovery >5%** = bounce starting
- **Volume >1.5x** = money returning
- **Jan 2-10** = ENTRY WINDOW (NOW!)

---

## 🚨 10-MINUTE WORKFLOW (Alert → Entry)

```
[1 min]  Scanner fires alert
[2 min]  Cross-validate (check other signals)
[3 min]  ATP Pro Level 2 (check technical/liquidity)
[2 min]  Position sizing (2% risk, calculate stop)
[1 min]  Enter position + set stop
[1 min]  Document entry

= 10 minutes total
```

---

## 💰 POSITION SIZING

```
Account:        $100,000
Risk per trade: 2% = $2,000
Stop loss:      8% from entry
Position size:  $2,000 / 0.08 = $25,000 (25% of account)

Example:
Entry:  $4.20
Stop:   $3.86 (-8% = $0.34)
Size:   $2,000 / $0.34 = 5,882 shares
Cost:   5,882 × $4.20 = $24,704
```

---

## 📈 ENTRY CHECKLIST

Before entering ANY position:

- [ ] Cross-signal score 70+? (3+ signals active)
- [ ] Recent catalyst? (8-K/insider within 30 days)
- [ ] Technical setup clean? (at support, not extended)
- [ ] ATP Pro Level 2 confirms? (tight spread <2%, good liquidity)
- [ ] Position sized correctly? (2% risk max)
- [ ] Stop loss calculated? (-8% to -10%)
- [ ] Target identified? (+15-20% minimum)

**If ANY checkbox is unchecked → PASS**

---

## 🎯 THE PRIORITY 10

Focus on these first:

1. **UUUU** - Uranium (21 insider buys)
2. **SIDU** - Space (current position)
3. **LUNR** - Space (moon lander)
4. **MU** - Memory/HBM (near highs)
5. **LITE** - Photonics (data center backbone)
6. **VRT** - Cooling (AI infrastructure)
7. **SMR** - Nuclear (small modular reactors)
8. **LEU** - Uranium enrichment
9. **RDW** - Space (10 insider buys)
10. **OKLO** - Nuclear (Sam Altman backed)

---

## 🔥 HIGH CONVICTION EXAMPLE

```
SIDU = 85/100

Wounded:  25/30  ✓ Down 45%, +8% 5d recovery
Insider:  25/30  ✓ Cluster: 3 buyers, C-Suite
8-K:      20/25  ✓ $45M DOD contract filed
Thesis:   15/15  ✓ Priority ticker, space sector

= 85/100 → HIGH CONVICTION → READY TO HUNT

ATP Pro confirms:
✓ At support ($4.15-4.25)
✓ Tight spread (1.2%)
✓ Volume: 850K avg

DECISION: Enter 25% position
Entry:  $4.20
Stop:   $3.85 (-8%)
Target: $5.00 (+19%)
```

---

## ⏰ DAILY SCHEDULE

### Pre-Market (8:00-9:30 AM ET)
- [ ] Run overnight 8-K scan (--hours 16)
- [ ] Update wounded prey (Jan focus)
- [ ] Check cross-signal HIGH CONVICTION
- [ ] Build watchlist for the day

### Market Hours (9:30 AM - 4:00 PM ET)
- [ ] Monitor 8-K scanner (continuous mode)
- [ ] Check ATP Pro Level 2 on alerts
- [ ] Enter HIGH CONVICTION setups
- [ ] Manage stops/targets

### After Hours (4:00-5:00 PM ET)
- [ ] Review cluster scanner (new insider buys)
- [ ] Check congress tracker (weekly)
- [ ] Update conviction scores
- [ ] Plan tomorrow's watchlist

---

## 🚨 STOP LOSS RULES

### Initial Stop:
- Set at **-8% to -10%** from entry
- ALWAYS honor stops (no exceptions)

### Breakeven:
- Move stop to breakeven at **+10%** gain

### Trailing:
- Trail stop **50%** of gains on runners
- Example: Up 20% → trail stop to +10%

### When Wrong:
- Cut losses FAST (honor stops)
- Don't average down
- Review what signal failed
- Move to next setup

---

## 📊 RISK MANAGEMENT

| Rule | Limit |
|------|-------|
| Risk per trade | 2-5% max |
| Position size | Up to 25% of account |
| Sector exposure | 20% max per sector |
| Total positions | 8 max (diversification) |
| Stop loss | -8% to -10% |
| Target | +15-20% minimum (2:1 R/R) |

---

## 🎯 TAKE PROFIT STRATEGY

### Scale Out:
- **1/3 position** at +15% (book profit)
- **1/3 position** at +25% (book more)
- **1/3 position** trail with 50% stop

### Wounded Prey Special:
- **Exit ALL by Jan 31** (tax loss bounce over)
- Don't hold through earnings
- Take 15-20% bounce and RUN

---

## 🏛️ CONGRESS SIGNALS

### Strong Buy Signal:
- ✅ Committee member buying in THEIR sector
- ✅ Multiple politicians (bipartisan)
- ✅ Cross-reference with 8-K/insider

### Weak Signal:
- ⚠️ 45-day filing delay (old data)
- ⚠️ Small amounts ($1K-15K)
- ⚠️ Single politician

### How to Use:
- Don't chase
- Use as CONFIRMATION
- Best with other signals

---

## 🐺 WOLF MANTRAS

1. **"The 15-minute edge"**  
   → See SEC filings before news coverage

2. **"3+ signals = HIGH CONVICTION"**  
   → Don't trade on one signal alone

3. **"Entry window: Jan 2-10"**  
   → Tax loss bounce timing is NOW

4. **"Honor your stops"**  
   → Cut losses fast, let winners run

5. **"ATP Pro confirms"**  
   → Always verify technicals in Level 2

6. **"Position size to survive"**  
   → 2% risk per trade, sleep at night

7. **"Book profits"**  
   → Don't let winners turn into losers

8. **"God forgives. Brothers don't."**  
   → Execute your plan or answer to the pack

---

## 🔧 TROUBLESHOOTING

```bash
# Scanner not working?
pip install --upgrade yfinance requests beautifulsoup4 pandas

# Permission denied?
chmod +x /workspaces/trading-companion-2026/tools/*.py

# Import errors?
cd /workspaces/trading-companion-2026
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Wake up Brokkr?
"Read the DNA" or "wake up Brokkr"
```

---

## 📚 FULL DOCS

- **Complete guide**: `/workspaces/trading-companion-2026/THE_15_MINUTE_EDGE.md`
- **Wolf pack arsenal**: `dna/WOLF_PACK_ARSENAL.md`
- **Quick awakening**: `dna/QUICK_AWAKENING.md`

---

🐺 **AWOOOO! HUNT WITH CONVICTION! LLHR!** 🐺

---

**Print this. Tape it to your monitor. Execute the plan.**
