# 🧪 TESTING GUIDE - New Weapons

**Quick commands to test each new system**

---

## 1. NEWS SCRAPER

### Basic Test (Single Ticker)
```bash
python src/research/news_scraper.py AISP
```

**Expected Output**:
- Finviz news count
- Yahoo news count
- Google news count
- Top 15 articles with:
  - Title
  - Source
  - Date
  - Keywords (if catalyst)
  - Link
- Saved to `logs/news/AISP_news_TIMESTAMP.json`

### Multi-Ticker Test
```python
from src.research.news_scraper import NewsScraper

scraper = NewsScraper()
tickers = ['AISP', 'LUNR', 'RKLB']

for ticker in tickers:
    news = scraper.get_all_news(ticker)
    print(f"{ticker}: {len(news)} articles")
```

---

## 2. FORM 4 MONITOR

### Scan All Recent Filings
```bash
python src/research/form4_monitor.py
```

**Expected Output**:
- "📡 Fetching Form 4 filings from SEC EDGAR..."
- "Found X Form 4 filings"
- "🔍 Detecting clusters..."
- List of clusters (if any detected)

### Scan Specific Watchlist
```bash
# Create test watchlist
echo -e "AISP\nLUNR\nRKLB\nPLTR\nRDDT" > test_watchlist.txt

# Scan it
python src/research/form4_monitor.py watchlist test_watchlist.txt
```

**Expected Output**:
- "🔍 SCANNING FORM 4 FOR 5 TICKERS"
- "Found X filings for watchlist tickers"
- Cluster detection results

---

## 3. SECTOR ROTATION TRACKER

### Generate All Heatmaps
```bash
python src/research/sector_rotation.py
```

**Expected Output**:
- "📊 SECTOR ROTATION ANALYSIS"
- Performance for each period (1d, 5d, 1mo, 3mo)
- "🔥 HOT SECTORS (5-day)" - list
- "🧊 COLD SECTORS (5-day)" - list
- "🎨 Generating heatmap for 1d..."
- "💾 Saved: logs/sector_charts/sector_heatmap_1d_TIMESTAMP.png"
- Same for 5d, 1mo

**Check Output**:
```bash
ls -lh logs/sector_charts/
# Should see 3 PNG files
```

### Generate Specific Period
```bash
python src/research/sector_rotation.py 5d
# Only generates 5-day heatmap
```

---

## 4. ALERT ORCHESTRATOR (Integrated)

### Test Mode (All Alerts)
```bash
python src/research/alert_orchestrator.py test
```

**Expected Output**:
- "🧪 TESTING ALL ALERT TYPES"
- Tests 4 alert types:
  1. Pre-market gap
  2. After-hours move
  3. Position alert
  4. Form 4 cluster
- Each sends via Telegram (or prints error if Telegram not configured)

### Morning Routine
```bash
python src/research/alert_orchestrator.py morning
```

**Steps**:
1. Scans pre-market gaps
2. Checks positions
3. Checks sector rotation
4. Scans news catalysts
5. Generates morning report
6. Sends to Telegram

### Evening Routine
```bash
python src/research/alert_orchestrator.py evening
```

**Steps**:
1. Scans after-hours moves
2. Checks position risk
3. Checks Form 4 clusters
4. Sends to Telegram

### Hourly Check
```bash
python src/research/alert_orchestrator.py hourly
```

**Steps**:
1. Checks position alerts
2. Checks Form 4 clusters

---

## 🔍 VERIFY INSTALLATIONS

### Check Dependencies
```bash
python -c "import feedparser; print('feedparser:', feedparser.__version__)"
python -c "import bs4; print('beautifulsoup4:', bs4.__version__)"
python -c "import matplotlib; print('matplotlib:', matplotlib.__version__)"
```

**Expected**:
```
feedparser: 6.0.12
beautifulsoup4: 4.14.2
matplotlib: 3.10.8
```

---

## 📂 CHECK DATA DIRECTORIES

### After Running Tests
```bash
# News archives
ls -lh logs/news/

# Form 4 tracking
cat data/form4/form4_tracking.json

# Sector heatmaps
ls -lh logs/sector_charts/

# Pre-market alerts
ls -lh logs/premarket_alerts/
```

---

## 🚨 TELEGRAM TESTING

### Prerequisites
1. Create `.env` file with:
```
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

2. Test Telegram connection:
```bash
python src/research/telegram_alert_bot.py test
```

**Expected**:
- "✅ Telegram connection successful"
- Message appears in your Telegram chat

### If Telegram Not Configured
- Alerts will print to console instead
- No errors, just warnings like:
  ```
  ⚠️ Telegram not configured, printing to console
  ```

---

## 🎯 INTEGRATION TEST

### Full Morning Flow
```bash
# 1. Test news scraper
python src/research/news_scraper.py AISP

# 2. Test Form 4 monitor
python src/research/form4_monitor.py

# 3. Test sector rotation
python src/research/sector_rotation.py

# 4. Test orchestrator
python src/research/alert_orchestrator.py morning
```

**Expected**:
- All 4 systems run without errors
- Data saved to appropriate directories
- Alerts sent via Telegram (or printed to console)

---

## ⚠️ TROUBLESHOOTING

### "ModuleNotFoundError: No module named 'feedparser'"
```bash
pip install feedparser beautifulsoup4 matplotlib
```

### "No such file or directory: '.env'"
```bash
# Telegram not required for testing
# Systems will work with console output
# Create .env later for real alerts
```

### Sector heatmaps not generating
```bash
# Check matplotlib backend
python -c "import matplotlib; print(matplotlib.get_backend())"

# If issues, set backend
export MPLBACKEND=Agg
python src/research/sector_rotation.py
```

### News scraper returns empty
- **Finviz**: May be rate-limited, wait 60 seconds
- **Yahoo RSS**: Check ticker format (uppercase)
- **Google News**: Sometimes returns generic results

---

## 📊 SUCCESS METRICS

After running all tests, you should have:

1. **Data Files Created**:
   - `data/form4/form4_tracking.json`
   - `logs/news/*.json` (news archives)
   - `logs/sector_charts/*.png` (heatmaps)
   - `logs/premarket_alerts/*.json` (alert history)

2. **No Errors** (unless Telegram unconfigured - that's OK)

3. **Console Output** showing:
   - News articles found
   - Form 4 filings detected
   - Sector performance data
   - Alert generation success

---

## 🚀 NEXT: AUTOMATION

Once tests pass, set up cron:

```bash
# Edit crontab
crontab -e

# Add:
0 6 * * 1-5 cd /path/to/trading-companion-2026 && python src/research/alert_orchestrator.py morning
30 16 * * 1-5 cd /path/to/trading-companion-2026 && python src/research/alert_orchestrator.py evening
0 9-17 * * 1-5 cd /path/to/trading-companion-2026 && python src/research/alert_orchestrator.py hourly
```

**AWOOOO 🐺**
