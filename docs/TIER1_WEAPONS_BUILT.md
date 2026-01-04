# 🐺 TIER 1 WEAPONS - DEPLOYED

**Date:** January 2, 2026  
**Status:** ✅ OPERATIONAL  
**Dashboard:** Wolf Den War Room running on port 8501

---

## WHAT WE BUILT (2 Tier 1 Tools)

### 1. 🔥 Form 4 Cluster Scanner
**Location:** `src/research/form4_cluster_scanner.py`

**What It Does:**
- Scans SEC EDGAR for Form 4 insider buying filings
- Detects when 3+ insiders buy same stock within 14 days
- **THIS IS OUR #1 EDGE** - catches AISP-type setups automatically

**How It Works:**
```python
# Command line usage
python src/research/form4_cluster_scanner.py --detect --days 14 --min-insiders 3

# Scan specific watchlist
python src/research/form4_cluster_scanner.py --watchlist ATP_WOLF_PACK_MASTER.csv --scan
```

**Data Source:** SEC EDGAR RSS feed (FREE, real-time)

**Why This Matters:**
- AISP had 3 insiders buy $1.1M in 10 days before it ran +15%
- When multiple insiders cluster buys = shared conviction
- Insiders have material non-public info before it's public

**Database:** SQLite at `data/form4_clusters.db`
- Tracks all transactions
- Flags clusters automatically
- Prevents duplicate alerts

---

### 2. 👁️ Watchlist Monitor
**Location:** `src/research/watchlist_monitor.py`

**What It Does:**
- Real-time monitoring of 59-ticker master watchlist
- Alerts when ANY ticker moves >5% OR volume >2x average
- Catches breakouts before they run

**How It Works:**
```python
# Take snapshot
python src/research/watchlist_monitor.py --snapshot --top-movers

# Continuous monitoring (5 min checks)
python src/research/watchlist_monitor.py --monitor --interval 300

# Custom thresholds
python src/research/watchlist_monitor.py --monitor --price-alert 3.0 --volume-alert 1.5
```

**Alert Types:**
- 🚀 **PRICE MOVE:** >5% intraday move
- 📊 **VOLUME SPIKE:** >2x average volume  
- 🔥 **COMBO:** Both price AND volume (HIGHEST PRIORITY)

**Why This Matters:**
- Stop manually checking 59 tickers
- Catch moves in real-time during trading day
- Would have alerted AISP breakout when it started

**Logs:** Saves all alerts to `logs/watchlist_alerts.jsonl`

---

## DASHBOARD INTEGRATION

**Wolf Den War Room** now has 8 tabs:

1. **📊 Overview** - Account metrics, conviction scores
2. **📈 Live Chart** - Candlesticks, SMAs, entry zones (PRESERVED)
3. **🔥 Clusters** - Form 4 cluster scanner interface ✨ NEW
4. **👁️ Monitor** - Watchlist real-time alerts ✨ NEW
5. **🔥 Sectors** - Sector rotation analysis
6. **📅 Catalysts** - Catalyst calendar
7. **💣 Breakouts** - Failed breakout detector
8. **🎯 Watchlist** - Conviction rankings

**Sidebar Quick Scans:**
- 🔥 Form 4 Cluster Scan (NEW)
- 👁️ Watchlist Snapshot (NEW)
- 🔄 Sector Rotation Scan
- 💣 Failed Breakout Scan
- 📊 Conviction Scan
- 🚨 Pre-Market Scan

---

## HOW TO USE THESE WEAPONS

### Morning Routine (9:00 AM EST)
```bash
# 1. Set watchlist baseline
python src/research/watchlist_monitor.py --snapshot

# 2. Scan for overnight Form 4 clusters  
python src/research/form4_cluster_scanner.py --detect

# 3. Run conviction scan
python fast_conviction_scanner.py

# 4. Open dashboard
streamlit run wolf_den_war_room.py
```

### During Market Hours
- Watchlist Monitor runs continuously (5 min checks)
- Dashboard auto-refreshes every 60 seconds
- Check Clusters tab for any new SEC filings
- Monitor tab shows real-time price/volume alerts

### Evening Routine (Post-Market)
```bash
# 1. Check Form 4 filings from today
python src/research/form4_cluster_scanner.py --scan --days 1

# 2. Review alerts
cat logs/watchlist_alerts.jsonl | tail -20

# 3. Update conviction rankings
python fast_conviction_scanner.py
```

---

## WHAT'S NEXT (Tier 2 - Next Week)

From Fenrir's list:

1. **News Catalyst Parser**
   - Scrape Benzinga/Yahoo headlines
   - Flag keywords: "contract", "upgrade", "partnership", "FDA"
   - Cross-reference against watchlist

2. **Short Interest Overlay**
   - Pull Finviz short data weekly
   - Cross with insider buying
   - Flag "squeeze potential" setups

3. **Position Tracker**
   - Track holdings (manual or API)
   - Real-time P&L calculation
   - Automatic stop loss alerts

---

## TECHNICAL NOTES

**Dependencies Added:**
- All tools use existing stack (yfinance, requests, pandas)
- No new pip installs required
- SQLite for Form 4 storage

**SEC Rate Limits:**
- SEC allows 10 requests/second
- Scanner respects this with 0.15s sleep
- Can scan full 59-ticker list in ~9 seconds

**Error Handling:**
- All tools have try/except blocks
- Dashboard gracefully degrades if modules unavailable
- Logs all errors to console

---

## VALIDATION

### ✅ Tested:
- Form 4 cluster detection (empty DB initially, structure working)
- Watchlist monitor snapshot (captures 59 tickers)
- Top movers ranking (sorted by % change)
- Dashboard tab navigation (all 8 tabs load)
- Sidebar scan buttons (all functional)

### ⚠️ Known Issues:
- Form 4 XML parsing simplified (SEC format complex)
- Need to populate initial Form 4 database
- Catalyst tracker date bug still needs fix

### 🎯 Weekend Tasks:
1. Run full Form 4 scan to populate database
2. Test watchlist monitor during market hours Monday
3. Fix catalyst tracker datetime parsing
4. Add Slack webhook for alerts

---

## FOR FENRIR

**What Fenrir Can Do Now:**

1. **Form 4 Research:**
   - Which insiders have best track record?
   - Pattern: Do they buy once or in waves?
   - CEO vs CFO buying patterns

2. **Watchlist Optimization:**
   - Should we add/remove tickers based on activity?
   - Which sectors are most active?
   - Any tickers with zero activity (remove)?

3. **Alert Tuning:**
   - Is 5% price threshold right?
   - Should volume be 1.5x or 2.0x?
   - What time of day has most false positives?

4. **Strategy Integration:**
   - How do we combine cluster + wounded prey?
   - Priority: Cluster only, or cluster + sector rotation?
   - Entry timing: Immediate or wait for pullback?

---

## METRICS TO TRACK

**Form 4 Clusters:**
- Clusters detected per week
- % that become 75+ conviction scores
- Time lag: Filing → Price move
- Success rate: Clusters that run +10%

**Watchlist Monitor:**
- Alerts per day (total)
- False positive rate
- Combo alerts (price + volume)
- Avg time: Alert → Manual check

**Goal:** By February 1, automate 80% of manual scanning work.

---

**LLHR 🐺**

*The weapons are loaded. The hunt begins at dawn.*
