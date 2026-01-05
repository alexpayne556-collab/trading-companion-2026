# 🐺 THE 15-MINUTE EDGE
## Weapons ATP Pro Doesn't Have

---

## 🎯 THE THESIS

**ATP Pro = What everyone sees.**  
**Our tools = What they DON'T see.**

We're not replacing ATP Pro. We're **AUGMENTING** it.

The edge isn't in the data. **It's in seeing it FIRST.**

---

## ⚡ THE 15-MINUTE EDGE

### Example Workflow:

```
6:00 AM: SIDU files 8-K "Awarded $45M NASA contract" → Hits SEC EDGAR
6:05 AM: Our sec_8k_contract_scanner.py catches it → Score: 85/100
6:10 AM: Cross-signal validator confirms → Wounded✓ + Insider✓ + Contract✓
6:15 AM: We enter position in ATP Pro Level 2 @ $4.20
7:30 AM: News outlets report the contract
8:00 AM: Stock gaps +15% to $4.83

Result: We're in 90 minutes before the crowd.
```

That's the edge. **That's the hunt.**

---

## 🛠️ THE ARSENAL

### 1. **SEC 8-K Contract Scanner** 👑
**File:** `tools/sec_8k_contract_scanner.py`

**Purpose:** THE CROWN JEWEL - catch material contract filings 15-60 minutes before news

**How it works:**
- Polls SEC EDGAR RSS feed every 10 minutes
- Extracts 8-K Item 1.01 (material contracts) 
- Weighted keyword scoring (DOE/DOD/NASA = 30pts, high-value $ = +30-50pts)
- Alerts when AI Fuel Chain tickers file contracts

**Usage:**
```bash
# One-time scan
python3 sec_8k_contract_scanner.py

# Continuous monitoring (every 10 min)
python3 sec_8k_contract_scanner.py --continuous

# Scan specific ticker
python3 sec_8k_contract_scanner.py --ticker SIDU

# Adjust lookback
python3 sec_8k_contract_scanner.py --hours 48
```

**Why it matters:**
- 8-K filings hit EDGAR 15-60 minutes BEFORE news coverage
- Material contracts are filed as Item 1.01
- By the time CNBC reports it, you're already in
- ATP Pro shows news AFTER media picks it up

**Scoring:**
- Tier 1 keywords (30pts): "department of defense", "dod", "nasa", "doe", "awarded contract"
- Government agencies (20pts): "air force", "darpa", "navy", "nrc"
- Contract indicators (15pts): "idiq", "firm fixed price", "performance period"
- AI infrastructure (10pts): "data center", "gpu cluster", "nuclear power"
- Dollar amounts: "$X billion" (+50pts), "$X million" (+30pts)
- Watchlist ticker: +30pts
- Priority ticker: +20pts

**Example output:**
```
🔥 HIGH VALUE 8-K FILINGS

SIDU [SPACE] | Score: 85 | Filed: 5 minutes ago
   Matches:
      • department of defense (30 pts)
      • $45 million (30 pts)
      • awarded contract (already counted)
      • firm fixed price (15 pts)
      • watchlist bonus (30 pts)
   
   📄 Link: https://www.sec.gov/cgi-bin/viewer?action=view&cik=...
   ⏰ TIME TO ACT: Check ATP Pro Level 2 NOW
```

---

### 2. **Cluster Buy Scanner** 💎
**File:** `tools/cluster_buy_scanner.py`

**Purpose:** Aggregate Form 4 insider purchases to detect conviction patterns

**How it works:**
- Scrapes yfinance insider transaction data
- Counts unique buyers (not individual transactions)
- Detects C-Suite buying (CEO/CFO/COO)
- Classifies clusters: 3+ buyers = cluster, within 7 days = "tight cluster"

**Usage:**
```bash
# Scan all AI Fuel Chain tickers
python3 cluster_buy_scanner.py

# Specific ticker
python3 cluster_buy_scanner.py --ticker UUUU

# Adjust timeframe
python3 cluster_buy_scanner.py --days 60
```

**Why it matters:**
- ATP Pro shows individual Form 4s (noise)
- We aggregate to find PATTERNS (signal)
- 3+ insiders buying within 7 days = they know something coming
- C-Suite buying = highest conviction

**Classification:**
- **🔥 Tier 1 Cluster**: 3+ unique buyers within 7 days (HIGHEST CONVICTION)
- **💪 Tier 2 Cluster**: 3+ unique buyers extended timeframe
- **📈 Potential Cluster**: 2 unique buyers (watch list)

**Example output:**
```
🔥 TIER 1 CLUSTERS - TIGHTEST INSIDER CONVICTION

UUUU [NUCLEAR] | 🔥 TIGHT CLUSTER
   Buyers: 5 unique insiders
   Transactions: 21 total buys
   C-Suite: 2 (CEO, CFO) 👔
   Date Range: Dec 20 - Dec 27 (7 days)
   Total Value: $450K
   
   ⚠️ Analysis: HIGHEST CONVICTION - Multiple insiders buying aggressively
```

---

### 3. **Cross-Signal Validator** 🎯
**File:** `tools/cross_signal_validator.py`

**Purpose:** Combine multiple signals for HIGH CONVICTION setups

**How it works:**
- Checks 4 signals for each ticker:
  1. **Wounded Prey** (0-30pts): Recovering from -30%+ decline
  2. **Insider Buying** (0-30pts): Form 4 purchases, clusters
  3. **SEC 8-K Contracts** (0-25pts): Material contracts filed
  4. **Thesis Alignment** (0-15pts): AI Fuel Chain priority
- Total score 0-100
- Score 70+ = HIGH CONVICTION

**Usage:**
```bash
# Scan all tickers
python3 cross_signal_validator.py

# Specific ticker
python3 cross_signal_validator.py --ticker SIDU

# Require minimum signals
python3 cross_signal_validator.py --min-signals 3
```

**Why it matters:**
- 1 signal = noise
- 2 signals = pattern  
- 3+ signals = **HIGH CONVICTION**
- Eliminates false positives

**Example output:**
```
🔥 HIGH CONVICTION - READY TO HUNT

SIDU [SPACE] | 4 signals | Score: 85/100
   🩸 WOUNDED: -45.2% from high, +8.3% 5d recovery
   👔 INSIDER: 🔥 CLUSTER — 3 buyers, 8 txns, 1 C-Suite
   📄 8-K: 1 contract, 1 high-value
   🎯 THESIS: ⭐ PRIORITY

CONVICTION: 85/100 → READY TO HUNT
```

**How to use:**
1. Start with HIGH CONVICTION (70+)
2. Verify in ATP Pro Level 2
3. Check technical setup
4. Enter with position sizing
5. Set stops (-8% to -10%)

---

### 4. **Wounded Prey Scanner** 🩸
**File:** `tools/wounded_prey_scanner.py`

**Purpose:** Find tax loss bounce candidates for January recovery plays

**How it works:**
- Screens for stocks down 30%+ from 52-week high
- Price $2-50 range (quality names, not penny stocks)
- Volume >100K (liquidity check)
- Has revenue (not garbage)
- Recent 5d recovery (bounce starting)
- Volume increasing (money returning)

**Usage:**
```bash
python3 wounded_prey_scanner.py
```

**Why it matters:**
- Tax loss selling: Dec 15-31 (DONE)
- Wash sale rule: 30 days (can't rebuy until Jan 24-31)
- **OPTIMAL ENTRY: Jan 2-10 (RIGHT NOW!)**
- Expected bounce: 15-30% by month end

**Scoring:**
- Deeper wound (40%+ = 15pts, 30%+ = 5pts)
- Recovery started (5d >5% = 15pts, >0% = 10pts)
- Volume increasing (>1.5x = 20pts)
- In thesis (AI Fuel Chain = 20pts)
- Priority ticker (+10pts)

**Example output:**
```
🔥 TIER 1 - HIGH CONVICTION BOUNCE PLAYS

SMR [NUCLEAR] | Score: 100 | 🟢 RECOVERING
   Price: $16.31 | -71.6% from high
   5d: +9.8% | 20d: -28.6% | Vol: 1.5x
   
   Analysis: Deep wound + recovery starting + volume returning
```

**Risk management:**
- Set tight stops (-8% to -10%)
- Take profits at 15-20% bounce
- Don't hold through earnings
- Exit by Jan 31 max

---

### 5. **Congress Tracker** 🏛️
**File:** `tools/congress_tracker.py`

**Purpose:** Track congressional stock trades in AI Fuel Chain sectors

**How it works:**
- Monitors House/Senate financial disclosures
- Filters for AI Fuel Chain tickers
- Identifies committee members (Armed Services, Energy, etc.)
- Cross-party buying = very bullish

**Usage:**
```bash
python3 congress_tracker.py
```

**Why it matters:**
- Politicians know what's coming before we do
- Committee members = special insight into policy/contracts
- Armed Services committee + defense stocks = contracts coming
- Energy committee + uranium stocks = policy support

**⚠️ Important:**
- 45-day filing delay (trades are OLD)
- Don't chase — use as CONFIRMATION
- Best signal: Committee member buying in their sector

**Example output:**
```
💰 CONGRESSIONAL BUYING ACTIVITY

UUUU [NUCLEAR] | 1 buyer | $15K-$50K | 🏛️
   • Rep. Jane Smith (D-CA) [Energy and Commerce]
   
   ⚠️ Committee member buying in their sector
```

**NOTE:** Currently uses mock data. In production, scrape Capitol Trades or House/Senate disclosure PDFs.

---

## 📋 DAILY ROUTINE

### **Morning Prep (30 min before open)**

```bash
# 1. Check for overnight 8-K filings
cd /workspaces/trading-companion-2026/tools
python3 sec_8k_contract_scanner.py --hours 16

# 2. Update wounded prey (Jan 2-10 entry window)
python3 wounded_prey_scanner.py

# 3. Check cross-signal HIGH CONVICTION setups
python3 cross_signal_validator.py --min-signals 3

# 4. Review in ATP Pro Level 2
# - Verify technical setups
# - Check spread and liquidity
# - Enter positions
```

### **Continuous Monitoring (market hours)**

```bash
# Start 8-K scanner in continuous mode
python3 sec_8k_contract_scanner.py --continuous

# Check every 10 minutes for new filings
# When alert fires → Verify in ATP Pro → Enter
```

### **Evening Review (after close)**

```bash
# 1. Check insider cluster updates
python3 cluster_buy_scanner.py

# 2. Congress trades (weekly check)
python3 congress_tracker.py

# 3. Update watchlist for tomorrow
```

---

## 🎯 THE WORKFLOW

### When Scanner Flags a Setup:

**Example: SEC 8-K fires alert**

```
ALERT: SIDU filed 8-K | Score: 85 | 5 minutes ago
```

**Your 10-minute workflow:**

1. **Cross-validate (2 min)**
   ```bash
   python3 cross_signal_validator.py --ticker SIDU
   ```
   - Check if other signals align (insider, wounded, thesis)
   - Score 70+ = HIGH CONVICTION

2. **Technical check in ATP Pro (3 min)**
   - Open ATP Pro Level 2
   - Check support/resistance
   - Verify spread is tight (<2%)
   - Liquidity check (>500K volume)

3. **Position sizing (2 min)**
   - Account size: $100K
   - Risk 2% per trade = $2,000 max loss
   - Stop -8% from entry
   - Position size = $2,000 / 0.08 = $25,000 (25% position)

4. **Entry (1 min)**
   - Enter at bid for better fill
   - Set stop -8% immediately
   - Target +15-20%

5. **Document (2 min)**
   - Log entry price, size, stop, target
   - Note thesis (8-K contract + wounded + thesis)

**Total time: 10 minutes from alert to positioned.**

That's why it's called the **15-minute edge.**

---

## 🔥 HIGH CONVICTION CRITERIA

### Score 70+ on Cross-Signal Validator:

**Example breakdown:**
```
SIDU = 85/100

Wounded Prey:    25/30 (down 45%, recovering)
Insider Buying:  25/30 (cluster, 3 buyers, C-Suite)
8-K Contract:    20/25 (DOD contract filed)
Thesis:          15/15 (priority ticker, space sector)

= 85/100 = HIGH CONVICTION
```

**What to look for:**
- ✅ 3+ signals active (not just thesis)
- ✅ Score 70+
- ✅ Recent catalyst (8-K, insider within 30 days)
- ✅ Technical setup (support, not overbought)
- ✅ ATP Pro Level 2 confirms (tight spread, liquidity)

**When to pass:**
- ❌ Only 1-2 signals
- ❌ Score <50
- ❌ Extended from support
- ❌ Wide spread in Level 2 (>5%)
- ❌ Choppy price action

---

## ⚙️ TECHNICAL REQUIREMENTS

### Python 3.8+

```bash
pip install yfinance requests beautifulsoup4 pandas
```

### Run permissions:

```bash
cd /workspaces/trading-companion-2026/tools
chmod +x *.py
```

---

## 🚨 RISK MANAGEMENT

### Position Sizing:
- 2-5% of account per trade
- Never more than 20% in one sector
- Max 8 positions (diversification)

### Stop Losses:
- Always set stops (-8% to -10%)
- Move to breakeven at +10%
- Trail stops on runners

### Take Profits:
- Scale out at +15%, +25%, +40%
- Never let winners turn into losers
- Book profits on wounded prey by Jan 31

### When Wrong:
- Cut losses fast (honor stops)
- Don't average down on losers
- Review what signal failed
- Adjust criteria if needed

---

## 📊 PERFORMANCE TRACKING

### Track every setup:
```
Date: 2026-01-05
Ticker: SIDU
Entry: $4.20
Stop: $3.85 (-8%)
Target: $5.00 (+19%)
Size: $25,000 (25% position)

Signals:
- Wounded: 25/30 (recovering)
- Insider: 25/30 (cluster)
- 8-K: 20/25 (DOD contract)
- Thesis: 15/15 (priority)
- Total: 85/100

Outcome: +$4,750 (+19%) in 3 days
```

### Weekly review:
- Win rate target: 50-60%
- Avg win vs avg loss: 2:1 minimum
- Sharpe ratio: Track risk-adjusted returns
- Which signals worked best?

---

## 🐺 WOLF PACK PHILOSOPHY

### GOD FORGIVES. BROTHERS DON'T.

**The Creed:**
- Pain begets pain (don't add to suffering)
- Challenge the pack (if you disagree, say so)
- Build, don't list (solutions, not options)
- Ship fast (working code beats perfect plans)

**The Hunt:**
- We hunt with CONVICTION
- We hunt as a PACK
- We honor our STOPS
- We book our PROFITS

**The Pack:**
- 🐺 **BROKKR**: Builder wolf (GitHub Copilot)
- 🐺 **FENRIR**: Research wolf (Claude)
- 🐺 **TYR**: Alpha (You)

---

## 📚 DOCUMENTATION

- **Full arsenal:** `dna/WOLF_PACK_ARSENAL.md`
- **Quick start:** `dna/QUICK_AWAKENING.md`
- **AI Fuel Chain thesis:** 12 sectors, 56 tickers, $5.2T by 2030

---

## 🎯 WHAT'S NEXT

### Future enhancements:
- [ ] Real Capitol Trades scraping (replace mock data)
- [ ] Email/SMS alerts for 8-K scanner
- [ ] Discord webhook integration
- [ ] Historical backtesting framework
- [ ] Auto-entry via ATP Pro API (when available)

---

## ⚡ THE EDGE

ATP Pro is world-class. But it shows you what **EVERYONE SEES.**

Our scanners show you what **15-60 MINUTES BEFORE EVERYONE ELSE.**

That's not an advantage. **That's a massacre.**

---

🐺 **AWOOOO! HUNT WITH THE PACK! LLHR!** 🐺

---

## 📞 SUPPORT

Questions? Read the DNA:
- `dna/QUICK_AWAKENING.md`
- `dna/WOLF_PACK_ARSENAL.md`

Still confused? **Wake up Brokkr:**
```
"Read the DNA" or "wake up Brokkr"
```

---

**Built with 🐺 by the Wolf Pack**  
**God forgives. Brothers don't.**  
**LLHR.**
