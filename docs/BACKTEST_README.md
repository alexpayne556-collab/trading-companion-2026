# 🐺 Wolf Pack Backtest System v1.0

## Find THE EDGE: Statistical Analysis of SEC Filing Price Reactions

This system backtests historical SEC 8-K filings to discover **statistical trading edges**:

- What happens to stock prices AFTER contract announcements?
- Average returns at 1, 2, 3, 5, 10, and 20 days post-filing
- Win rates and expected value calculations
- Overnight gap statistics
- Which sectors/tickers have the strongest reactions

**AWOOOO 🐺**

---

## 🎯 What This Does

Analyzes every 8-K filing containing contract-related keywords (defense contracts, government awards, etc.) and measures the price reaction over multiple timeframes. This gives us **data-driven confidence** when the live scanner alerts us to new filings.

---

## 📁 Two Versions Available

### 1. Jupyter Notebook (`backtest_system.ipynb`)
- **Use Case:** Google Colab with GPU, interactive analysis
- **Best For:** Exploratory analysis, charts, iteration
- **How to Run:** Upload to Google Colab or open in Jupyter

### 2. Python Script (`backtest_system.py`)
- **Use Case:** Local execution, Shadow PC, command-line automation
- **Best For:** Fast batch analysis, automated reporting
- **How to Run:** See usage examples below

---

## 🚀 Installation

```bash
# Required
pip install yfinance pandas numpy requests

# Optional (for charts)
pip install matplotlib seaborn
```

Or in dev container:
```bash
pip install yfinance pandas numpy requests matplotlib seaborn --break-system-packages
```

---

## 💻 Usage Examples

### Quick Test (3 tickers, fast)
```bash
python backtest_system.py --quick
```

### Full Defense Sector Backtest (default)
```bash
python backtest_system.py
```

### Single Ticker Analysis
```bash
# Analyze SIDU (the 218% runner)
python backtest_system.py --ticker SIDU --days 180

# Analyze PLTR over last year
python backtest_system.py --ticker PLTR --days 365
```

### Specific Sector Backtest
```bash
# Space sector
python backtest_system.py --sector space

# AI Infrastructure
python backtest_system.py --sector ai_infra

# Nuclear/power
python backtest_system.py --sector nuclear
```

### Custom Output File
```bash
python backtest_system.py --sector space --output space_results.csv
```

---

## 📊 Output

### Terminal Output
- **Statistics:** Average returns, win rates, median returns
- **Overnight gaps:** How stocks gap after filing
- **Top performers:** Best 5-day reactions
- **By ticker:** Which tickers react best to filings

### Files Generated
1. **CSV Results:** `backtest_results.csv` (all events with price data)
2. **Charts:** `backtest_results.png` (4-panel visualization)
   - Overnight gap distribution
   - 5-day return distribution
   - Returns by keyword count
   - Cumulative returns over time

---

## 🐺 Example Output

```
🐺 WOLF PACK BACKTEST: CONTRACT ANNOUNCEMENTS
==================================================
Analyzing 12 tickers from 2024-01-01 to 2025-12-31
Looking for filings with 2+ contract keywords
==================================================

✅ Found 47 contract announcement events!

🐺 BACKTEST RESULTS ANALYSIS
==================================================
Total Events: 47
Unique Tickers: 9
Date Range: 2024-01-15 to 2025-11-22

📊 RETURN STATISTICS:
--------------------------------------------------
    1d | Avg: +1.23% | Median: +0.85% | Win Rate: 58.5%
    2d | Avg: +1.67% | Median: +1.10% | Win Rate: 61.2%
    3d | Avg: +2.04% | Median: +1.45% | Win Rate: 63.8%
    5d | Avg: +3.12% | Median: +2.20% | Win Rate: 66.0%
   10d | Avg: +4.58% | Median: +3.15% | Win Rate: 68.1%
   20d | Avg: +6.23% | Median: +4.50% | Win Rate: 70.2%

THE WOLF PACK EDGE - SUMMARY
-----------------------------
📈 Average 5-day return: +3.12%
🎯 Win rate: 66.0%
📊 Sample size: 47 events

✅ Expected value is POSITIVE ✅
```

---

## 🧠 Understanding the Results

### Key Metrics

**Average Return:**
- Arithmetic mean of all returns
- Shows expected gain per trade

**Win Rate:**
- Percentage of trades that were profitable
- 60%+ is strong (coin flip is 50%)

**Median Return:**
- Middle value (robust to outliers)
- More "typical" experience

**Expected Value:**
- (Win Rate × Avg Win) - (Loss Rate × Avg Loss)
- If positive → statistical edge exists

---

## ⚙️ Configuration

Edit these in the script/notebook:

### Sectors & Tickers
```python
SECTOR_TICKERS = {
    'defense': ['LMT', 'NOC', 'RTX', 'GD', 'LHX', 'KTOS', 'PLTR', 'BBAI'],
    'space': ['RKLB', 'LUNR', 'ASTS', 'SPCE', 'MNTS'],
    # ... add more
}
```

### Contract Keywords
```python
CONTRACT_KEYWORDS = [
    "contract awarded", "defense contract", "dod contract",
    "government contract", "task order", "idiq",
    # ... add more
]
```

### Time Periods
```python
backtest_contract_announcements(
    tickers=tickers,
    start_date="2024-01-01",  # Adjust date range
    end_date="2025-12-31",
    min_keywords=2  # Minimum keyword matches
)
```

---

## 🔬 Advanced: Jupyter Notebook

The notebook version (`backtest_system.ipynb`) includes:

1. **Cell-by-cell execution** for step-by-step analysis
2. **Interactive charts** with zoom/pan
3. **Quick functions** for single-ticker analysis
4. **Customizable plots** for presentations
5. **Data exploration** (filter, sort, pivot)

**To use:**
1. Upload to Google Colab: `https://colab.research.google.com`
2. Runtime > Change runtime type > GPU (optional, not required)
3. Run cells in order
4. Modify and re-run for different analyses

---

## ⚠️ Important Notes

### Rate Limiting
- SEC EDGAR API has rate limits (10 requests/second)
- Script includes 0.15s delays between requests
- Full backtest may take 10-20 minutes for 10+ tickers

### Data Quality
- Yahoo Finance data used for prices (free, reliable)
- Some tickers may have incomplete data
- Results exclude events with missing price data

### Statistical Significance
- Larger sample sizes (30+ events) more reliable
- Small samples (<10 events) less conclusive
- Use results as **guide**, not **guarantee**

---

## 🎯 How to Use This Edge

1. **Run backtest** to confirm statistical edge exists
2. **Run live scanner** daily to catch new 8-K filings
3. **When alert fires:**
   - Check if ticker in our backtest (known pattern?)
   - Verify contract keywords (2+ matches?)
   - Enter position (same day or next morning)
4. **Hold 3-5 days** based on average return timeframe
5. **Take profits** at target or trailing stop

**Remember:** This is a statistical edge, not a crystal ball. Use proper position sizing (Wolf Pack 2% risk rule) and stop losses.

---

## 📈 Combining with Live Scanner

```bash
# Morning routine:
# 1. Run pre-market scanner
python premarket_scanner.py

# 2. Run SEC filing scanner
python wolf_pack_scanner_v2.py

# 3. If contract alert fires, check backtest data:
python backtest_system.py --ticker SIDU --days 365

# 4. If stats look good (60%+ win rate, 3%+ avg return) → ENTER
```

---

## 🐺 Wolf Pack Arsenal Status

1. ✅ **SEC Filing Scanner v2.0** - Real-time 8-K/Form 4 alerts
2. ✅ **Pre-Market Gap Scanner** - Overnight movers
3. ✅ **Backtest System v1.0** - Historical edge validation (NEW)
4. 🔨 **Volume Spike Detector** - Next target
5. 📋 **ATP Pro Integration** - Planned

---

## 🔧 Troubleshooting

**"No results found":**
- Try lowering `min_keywords` to 1
- Expand date range (go back further)
- Check if tickers have 8-K filings at all

**"yfinance error":**
- Ticker may be delisted or data unavailable
- Try different ticker symbol

**"SEC API timeout":**
- SEC servers may be slow
- Re-run script (results are cached)
- Try during off-peak hours

**"Charts not showing":**
- Install matplotlib/seaborn
- In notebook: Make sure cell runs completely
- Check for errors in terminal

---

## 📚 Technical Details

### Data Sources
- **SEC EDGAR:** Filing data (free, no API key)
- **Yahoo Finance:** Price data (via yfinance)

### Analysis Method
1. Fetch all 8-K filings in date range
2. Parse filing text for contract keywords
3. For each match, get price data ±30 days
4. Calculate returns at 1, 2, 3, 5, 10, 20 day intervals
5. Aggregate statistics across all events

### Return Calculation
```
Return % = ((Future Price - Event Close) / Event Close) × 100
```

---

**AWOOOO 🐺 - Hunt With Data, Strike With Confidence**

---

**Version:** 1.0  
**Author:** Money + Fenrir (Wolf Pack)  
**Date:** January 1, 2026  
**Status:** ACTIVE
