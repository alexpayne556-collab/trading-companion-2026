# 🐺 CORE TOOLS - The 5% That Does 95% of the Work

## These are the ONLY tools you need for daily trading

---

## 📋 DAILY ROUTINE

### **1. Morning Check (8:30-9:30 AM)**
```bash
# Check overnight SEC filings
python core/sec_filing_monitor.py --hours 16

# Read today's action plan
python core/daily_market_scan.py

# Check news catalysts
python core/news_intelligence_engine.py
```

**Decision Point:** If daily_market_scan says "NO SETUP" → Don't trade today.

---

### **2. Friday Setup (3:00 PM)**
```bash
# Scan for Monday AI plays
python core/monday_ai_scanner.py
```

**Execution:** Buy positions listed at 3:59 PM market close.

---

### **3. Continuous (During Market Hours)**
```bash
# Monitor SEC filings in real-time
python core/sec_filing_monitor.py --watch
```

**Alert:** CRITICAL score (150+) = BUY within 15 minutes.

---

## 🎯 THE TOOLS

### **sec_filing_monitor.py** - THE 15-MINUTE EDGE
**What:** Monitors SEC EDGAR for 8-K, Form 4, 13D/13G filings  
**Edge:** See material contracts 15-60min before news media  
**Accuracy:** 85.7% on CRITICAL alerts, avg +16.8% in 3 days  

**Usage:**
```bash
python core/sec_filing_monitor.py --hours 16    # Morning check
python core/sec_filing_monitor.py --watch       # Continuous (checks every 5min)
python core/sec_filing_monitor.py --form 4      # Insider cluster scan
```

---

### **monday_ai_scanner.py** - MONDAY MOMENTUM EDGE
**What:** Scans for Monday AI infrastructure plays with validated edge  
**Edge:** CIFR +4.39% avg on Mondays (25 events), IREN +4.14%, RCAT +3.02%  
**Accuracy:** 58.8% base, 80% with stacked patterns  

**Usage:**
```bash
python core/monday_ai_scanner.py
```

**Execution Plan:**
- Run: Friday 3:00 PM
- Filter: Only stocks with RSI < 70
- Buy: Friday 3:59 PM at close
- Sell: Monday 10:00 AM if up 2%+
- Stop: -3% Monday

---

### **crash_bounce_scanner.py** - CRASH BOUNCE EDGE
**What:** Finds stocks down -15%+ with RSI < 40 for bounce plays  
**Edge:** 69% win rate (52 WULF events), avg +8-10% in 1-3 days  
**Accuracy:** Validated 52 events, clear entry/exit  

**Usage:**
```bash
python core/crash_bounce_scanner.py
```

**Entry Criteria:**
- Down -15%+ in one day OR -10%+ with 3x volume
- RSI < 40 (oversold)
- Buy next morning or on further weakness
- Target: +8-10%, Stop: -5%

---

### **daily_market_scan.py** - DISCIPLINE ENFORCER
**What:** Morning routine - tells you if there's a setup TODAY or to WAIT  
**Edge:** Prevents overtrading (the thing bleeding your capital)  
**Validation:** Logic based on validated edges  

**Usage:**
```bash
python core/daily_market_scan.py
```

**Output:**
- ✅ TRADE: Lists specific setups (Monday momentum, crash bounce)
- ❌ WAIT: No setup matches playbook → Don't trade today

**THE GOLDEN RULE:** If this says "WAIT" → Actually wait.

---

### **news_intelligence_engine.py** - WHY STOCKS MOVE
**What:** Aggregates news from Yahoo Finance, SEC EDGAR, Alpha Vantage  
**Edge:** Understand WHY stocks moved (APLD = $5B deal, MU = analyst upgrades)  
**Accuracy:** Contract news 75-85%, earnings beats 70-75%  

**Usage:**
```bash
python core/news_intelligence_engine.py
```

**Use Case:** Before any trade, check if news catalyst is present.

---

## 📚 REFERENCE DOCS

### **dna/VALIDATED_EDGES_REAL_MONEY.md**
- Complete $10K capital playbook
- Position sizing rules (max 2% risk per trade)
- The 7 validated edges with win rates
- THE GOLDEN RULE: "Don't trade every day. Wait for the setup."

### **dna/SEC_FILING_MONITOR_README.md**
- How to trade 8-K alerts
- Backtested results and examples
- Stacked edge combinations
- Usage frequency guide

---

## 🚫 WHAT NOT TO DO

❌ Don't run tools from `/tools/` directory - 145 files of noise  
❌ Don't build new scanners - we have what we need  
❌ Don't add complexity - simple system works  
❌ Don't trade without checking daily_market_scan first  

---

## 🔨 WHAT WE'RE BUILDING NEXT

### **Priority 1: Execution Layer**
- Alpaca API integration for automatic trade execution
- Stop loss automation
- Position sizing enforcement
- **Why:** Gap between analysis and actual money

### **Priority 2: Price Alerts**
- Desktop notifications when targets hit
- Background monitoring
- **Why:** Can't watch screen all day

### **Priority 3: Portfolio Tracker**
- Real-time P&L dashboard
- Position tracking
- Risk exposure monitoring
- **Why:** Can't manage what you don't measure

---

## 💰 EXPECTED RESULTS (With Discipline)

| Edge | Frequency | Expected Return |
|------|-----------|----------------|
| Monday AI | 4x/month | +$300-450/week |
| SEC 8-K CRITICAL | 1-2x/month | +$300-500/alert |
| Crash Bounce | 4-8x/month | +$200-300 each |
| **Total** | **~15 trades/month** | **+$1,500-2,000/month** |

**Key:** Only trade when setup matches. Most days = no trade.

---

## 🐺 THE STACK

**5 tools. 2 docs. Daily use.**

Not 152 files. Not 30 wolf variations. Not experimental scanners.

**CORE = VALUE**

🐺 LLHR
