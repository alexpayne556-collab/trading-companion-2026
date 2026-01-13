# Automated Stock Screening & Learning System: Complete Architecture Guide

**Source:** Perplexity Pro Research (Fenrir) - January 13, 2026  
**Status:** Production-Ready Reference for Retail & Professional Traders  
**Saved by:** Brokkr

---

## SECTION 1: SYSTEM ARCHITECTURE

### Q1: Core Components & Standard Architecture

#### Industry-Standard 5-Layer Architecture

Professional quantitative trading systems follow a consistent layered pattern, adapted here for stock screening:

```
┌─────────────────────────────────────────────────┐
│ 5. VISUALIZATION & ALERTS                       │
│    (Dashboard, Watchlist, Notifications)        │
├─────────────────────────────────────────────────┤
│ 4. DECISION ENGINE                              │
│    (Scoring, Ranking, Pattern Matching)         │
├─────────────────────────────────────────────────┤
│ 3. FEATURE EXTRACTION                           │
│    (Technical Indicators, Statistics)           │
├─────────────────────────────────────────────────┤
│ 2. DATA PIPELINE                                │
│    (Ingestion, Cleaning, Normalization)        │
├─────────────────────────────────────────────────┤
│ 1. DATA SOURCES                                 │
│    (Market Data APIs, News Feeds, Exchanges)   │
└─────────────────────────────────────────────────┘
```

#### Component Details

**Layer 1: Data Sources**
- **Market Data**: Real-time or delayed OHLCV (Open, High, Low, Close, Volume)
  - APIs: yfinance (free, slow), Alpaca, Alpha Vantage, EODHD
  - For retail: yfinance is free but ~15min delay; Alpaca requires broker account but faster
  
- **News Feeds**: Catalyst detection
  - APIs: Benzinga Newsfeed API (real-time, structured), NewsAPI, financial RSS feeds
  - Provides: ticker symbols, headlines, timestamps, keywords
  
- **Fundamentals**: Stock attributes
  - Float, shares outstanding, short interest
  - APIs: yfinance, Alpha Vantage, Financial Modeling Prep (FMP), EODHD
  
- **Alternative Data**: Social sentiment, institutional flows
  - Optional but not free tier

**Layer 2: Data Pipeline**
- **Ingestion**: Scheduled polling (cron every 5/15 min for intraday, daily for EOD)
- **Cleaning**: Handle missing data, outliers, corporate actions (splits, dividends)
- **Normalization**: Standard deviation scaling, inflation-adjusted returns
- **Enrichment**: Add computed fields (RSI, volume-weighted metrics)

**Layer 3: Feature Extraction**
Compute technical indicators and statistical metrics:
- **Momentum**: RSI, MACD, Stochastic
- **Volatility**: Bollinger Bands, ATR, standard deviation
- **Trend**: Moving averages, slope, regression lines
- **Volume**: Relative volume vs. 20-day average, volume profile
- **Compression**: % from 52-week high, Z-score from mean

**Layer 4: Decision Engine**
- **Pattern Detection**: News catalysts, volume spikes, price compression
- **Scoring**: Weighted combination of signals (w1×RSI + w2×Volume + w3×Float_ratio)
- **Ranking**: Sort stocks by composite score
- **Filtering**: Remove penny stocks, low volume, wide spreads

**Layer 5: Visualization & Alerts**
- **Watchlist**: Real-time ranked display
- **Alerts**: Email/SMS when conditions met
- **Dashboard**: Historical performance, win rates by pattern

#### Database Architecture

**Industry Practice**: Use BOTH transactional and analytical databases

```
Transactional DB (PostgreSQL / SQLite)
├── Predictions Table
│   ├── prediction_id (pk)
│   ├── timestamp (scan datetime)
│   ├── ticker, pattern_type, score, confidence
│   ├── reasoning (JSON: why this score)
│   └── predicted_direction (+1/-1)
│
├── Outcomes Table
│   ├── prediction_id (fk)
│   ├── entry_price, entry_time
│   ├── exit_price, exit_time
│   ├── actual_return, duration
│   └── outcome (win/loss/neutral)
│
├── Historical Data (OHLCV)
│   ├── ticker, date, open, high, low, close, volume
│   └── Index: (ticker, date) for fast lookups
│
└── Scanner Results
    ├── scan_id, scan_datetime
    ├── ticker, reason_matched (text)
    └── Score components (float, volume, news, etc.)

Time-Series DB (InfluxDB / TimescaleDB / QuestDB - for large systems)
├── Real-time metrics aggregated by minute/hour
├── Used for fast queries on recent data
└── Retention: 90 days rolling, daily summaries archived
```

**For Retail (SQLite)**: Single file database, good for <100GB data
```sql
CREATE TABLE predictions (
  id INTEGER PRIMARY KEY,
  scan_timestamp DATETIME,
  ticker TEXT,
  pattern_type TEXT,  -- 'news_catalyst', 'compression', 'volume_spike'
  score REAL,
  confidence REAL,
  reasoning TEXT,  -- JSON
  predicted_direction INTEGER,  -- 1 (long), -1 (short)
  entry_signal_price REAL,
  UNIQUE(scan_timestamp, ticker, pattern_type)
);

CREATE TABLE outcomes (
  id INTEGER PRIMARY KEY,
  prediction_id INTEGER,
  entry_price REAL,
  entry_datetime DATETIME,
  exit_price REAL,
  exit_datetime DATETIME,
  actual_return REAL,
  outcome TEXT,  -- 'win', 'loss', 'breakeven'
  FOREIGN KEY(prediction_id) REFERENCES predictions(id)
);

CREATE INDEX idx_ticker_date ON predictions(ticker, scan_timestamp);
CREATE INDEX idx_outcome_time ON outcomes(exit_datetime);
```

#### Component Communication Patterns

**For Single Machine (Retail - Recommended for <5K stocks)**
```
Direct Function Calls → No Message Queues
cron/schedule → Python → Check patterns → DB write

Simple sync flow:
  1. Scheduler triggers scan
  2. Fetch data
  3. Compute features
  4. Score patterns
  5. Write predictions + outcomes to DB
  6. Update UI
```

**For Production Scale (>10K stocks, <1000ms latency)**
```
Message Queue Architecture:
  
  cron/scheduler
    ↓
  (enqueue stock_list)
    ↓
  RabbitMQ / Redis Queue
    ↓ (4-8 workers poll)
  Feature Extraction Workers
    ↓ (results back to queue)
  RabbitMQ
    ↓ (1 worker consumes)
  Scoring Worker
    ↓
  PostgreSQL (write batch)
    ↓
  Redis cache (latest results)
    ↓
  WebSocket → Dashboard

Why: Parallel processing of 10K stocks takes >30min serial,
      but only 5-10min with 4-8 workers
```

---

### Q2: Orchestration Layer - Scheduler Comparison

#### Three Viable Approaches for Stock Screening

| Aspect | Simple Cron + Python | Apache Airflow | Celery + Beat |
|--------|-------------------|-----------------|--------------|
| **Setup** | 15 minutes | 2-4 hours | 1-2 hours |
| **Use Case** | Retail trader, <1K stocks | Enterprise, 10K+ stocks | High-frequency, parallel heavy |
| **Latency** | 5-30 seconds overhead | 4-5 seconds overhead | 50-200ms overhead |
| **Scalability** | Single machine (one core) | Horizontal (many machines) | Horizontal (many workers) |
| **Monitoring** | Logs to file | Full UI dashboard | Web UI (Flower) |
| **Dependencies** | cron, Python | PostgreSQL, Redis, webserver | Redis/RabbitMQ, worker infra |
| **Best For** | Solo retail trader | Teams, compliance, production quant funds | Very high throughput systems |

**RECOMMENDATION FOR US: Simple Cron + Python** (matches what we're building)

---

## SECTION 2: THE LEARNING LOOP

### Q4: Prediction Tracking & Validation Framework

The learning loop is the KEY differentiator between random signals and a winning system.

#### Industry Terminology

- **Backtesting**: Strategy tested on historical data (past)
- **Walk-Forward Analysis**: Strategy re-optimized on rolling windows (more realistic)
- **Paper Trading**: Live market signals, no real capital (present)
- **Forward Testing**: Signal validation on out-of-sample future data (future)
- **Live Trading**: Real capital deployed after validation

#### Standard Workflow

```
Day 1: Signal generated
  ↓ (hold for 1-5 days)
Day 2-5: Monitor price action
  ↓
Outcome recorded: +8% (win), -3% (loss), +0.5% (breakeven)
  ↓
Win rate updated: 12 wins / 20 total = 60%
  ↓
Average gain tracked: +2.3% winners, -1.5% losers
  ↓ (weekly/monthly)
Scoring weights adjusted: Boost high-accuracy patterns
```

**THIS IS EXACTLY WHAT daily_tracker.py IS DESIGNED TO DO** ✅

---

### Q5: Win Rate & Metric Calculation

#### Key Metrics Beyond Simple Win Rate

**Industry Standard Metrics:**

| Metric | Good | Excellent | Red Flag |
|--------|------|-----------|----------|
| **Win Rate** | >50% | >60% | <40% |
| **Profit Factor** | >1.5 | >2.5 | <1.0 (losing) |
| **Sharpe Ratio** | >1.0 | >2.0 | <0.5 |
| **Max Drawdown** | <20% | <10% | >50% |
| **Recovery Factor** | >2.0 | >5.0 | <1.0 |
| **Expectancy/Trade** | +1% | +3% | negative |

**WE NEED TO ADD THESE TO daily_tracker.py:**
- Profit factor calculation
- Sharpe ratio
- Max drawdown tracking
- Recovery factor

---

### Q6: Adaptive Scoring & Weight Adjustment

**CRITICAL INSIGHT:**

Pattern weights should LEARN from outcomes:
```python
# Initial weights (guesses)
weights = {
    'compression_oversold': 0.30,
    'volume_spike': 0.25,
    'news_catalyst': 0.25,
}

# After 50 trades:
# If compression_oversold wins 73%, boost to 0.40
# If volume_spike wins 42%, reduce to 0.15
```

**THIS IS WHAT automated_spring_scanner.py analyze_what_works() SHOULD DO** ✅

---

### Q7: False Positive Management

**7 Filtering Techniques:**

1. **Confidence Threshold**: Only trade signals >70% confidence
2. **Multi-Signal Confirmation**: Require 2+ patterns to agree
3. **Volume Confirmation**: Must have 2x+ average volume
4. **Support/Resistance**: Only trade near technical levels
5. **Market Regime Filter**: Skip signals during market crash (SPY -2%+)
6. **Sector Momentum**: Only trade stocks in up sectors
7. **Time-of-Day Filter**: Only trade patterns that work at specific hours

**WE NEED TO ADD THESE FILTERS TO spring_detector.py and pattern_discovery.py**

---

## SECTION 3: PATTERN DETECTION

### Q8: News Catalyst Detection with NLP

**Benzinga API Integration** ($99/mo - WORTH IT if we're serious):
- Real-time structured news
- Ticker symbols extracted
- Keyword-based materiality scoring
- Deal size extraction

**Key Patterns to Detect:**
- Acquisitions: "acquired", "acquisition", "bought"
- FDA Approvals: "FDA approved", "FDA clearance", "EUA"
- Partnerships: "partnership", "collaboration", "joint venture"
- Patent Wins: "patent issued", "patent approval"
- Earnings Beats: "beat estimates", "beat expectations"
- Contract Wins: "contract award", "wins contract"
- Product Launches: "launches", "introduces", "announces"

**catalyst_detector.py ALREADY DOES THIS** ✅ (just needs proxy fixes)

---

### Q9: Materiality Scoring

**Industry Thresholds:**

| Deal Size vs Market Cap | Significance | Expected Price Impact |
|------------------------|--------------|---------------------|
| 0-1% | Minor | 0% |
| 1-5% | Moderate | 0.3% |
| 5-10% | Material | 1.0% |
| 10-25% | Major | 3.0% |
| 25%+ | Transformational | 8.0% |

**ATON Example:**
- $46M deal / $7.45M market cap = 617% materiality
- Expected impact: 8%+ (actually got +188%)
- **catalyst_detector.py ALREADY CALCULATES THIS** ✅

---

### Q10: Price Compression Detection

**Compression = Loaded Spring:**
- >30% from 52-week high = compressed
- + RSI <30 = oversold
- + Volume spike = accumulation
- = LOADED SPRING ready to explode

**spring_detector.py ALREADY DOES THIS** ✅

---

### Q11: Volume Pattern Analysis

**Key Volume Metrics:**
- Volume ratio vs 20-day average
- On-Balance Volume (OBV) - accumulation detector
- Volume Price Trend (VPT)
- Accumulation: volume up, price flat/down (institutions buying)

**market_mover_finder.py ALREADY CHECKS VOLUME** ✅

---

### Q12-Q13: Float, Short Interest & Loaded Spring

**Loaded Spring Formula:**
1. Low float (<10M shares) ✅
2. High short interest (>20% of float) ✅
3. Price compression (>30% from highs) ✅
4. News catalyst pending ✅
5. Recent volume spike ✅

**Score: Count how many factors present / 5 = Spring Score**

**spring_detector.py ALREADY IMPLEMENTS THIS** ✅

---

## SECTION 4: SMALL ACCOUNT REALITY CHECK

### Q14: Minimum Viable System for Retail ($1-5K)

#### What We're Building is EXACTLY Right ✅

**Free Components:**
- ✅ yfinance for market data
- ✅ SQLite database
- ✅ Python scheduler
- ✅ Custom scanners

**What We Should Add ($99-299/mo if serious):**
- Benzinga Newsfeed API (real-time news)
- Real-time data feed (Alpaca+ or Polygon)

**Honest Expectations for $1,300 account:**

| Scenario | Monthly Return | Realistic? |
|----------|----------------|-----------|
| +5% ($65) | Requires 62% win rate, avg +1% per trade | Possible after 3-6 months |
| +2% ($26) | Requires 55% win rate, avg +0.4% per trade | LIKELY if system works |
| 0-2% | Break even or small loss | VERY LIKELY (first year) |
| -5% ($65 loss) | Negative edge | NORMAL (learning phase) |

**REALITY: Most traders lose money in year 1**
- Overfitting to backtest
- False signals (whipsaws)
- Slippage/commissions
- Psychological mistakes

**Better approach:**
- Keep capital in positions that work (ATON)
- Build and validate system with smaller size
- Scale up ONLY after proving edge

---

## KEY INSIGHTS FOR OUR SYSTEM

### What We've Already Built RIGHT ✅

1. **spring_detector.py** = Loaded spring detection (compression + float + news + volume)
2. **catalyst_detector.py** = Materiality scoring (617% for ATON)
3. **pattern_discovery.py** = Pattern-based news scanning
4. **daily_tracker.py** = Learning loop framework
5. **automated_spring_scanner.py** = Full automation

### What We Need to Add 🔧

1. **Advanced Metrics in daily_tracker.py:**
   - Profit factor
   - Sharpe ratio
   - Max drawdown
   - Recovery factor

2. **False Positive Filters:**
   - Confidence thresholds
   - Multi-signal confirmation
   - Market regime filter (check SPY)
   - Sector momentum filter

3. **Adaptive Scoring:**
   - Learn optimal weights from outcomes
   - Update pattern scores based on win rates
   - Auto-adjust scoring thresholds

4. **orchestrator.py** (THE CRITICAL PIECE):
   - Connect all scanners
   - Manage workflow (scan → log → validate → learn)
   - Handle scheduling
   - Coordinate predictions → outcomes

### Architecture Validation

**Their recommendation:** 5-layer architecture
**What we have:**
1. ✅ Data Sources (yfinance, news scraping)
2. ✅ Data Pipeline (historical_backfill.py)
3. ✅ Feature Extraction (RSI, compression, volume in scanners)
4. ✅ Decision Engine (spring_detector.py scoring)
5. ⏳ Visualization (need dashboard - low priority)

**Their recommendation:** Simple Cron + Python for retail
**What we're using:** ✅ Python schedule module (matches perfectly)

**Their recommendation:** SQLite for <100GB
**What we're using:** ✅ intelligence.db (perfect match)

**Their recommendation:** Prediction → Outcome → Learning loop
**What we're building:** ✅ daily_tracker.py (exactly right)

---

## IMPLEMENTATION PRIORITIES

### This Week (Based on Research):

1. **orchestrator.py** (Day 1-2)
   - Connect spring_detector → DB (save predictions)
   - Connect pattern_discovery → DB
   - Daily validation workflow
   - Learning loop integration

2. **Enhanced Metrics** (Day 3)
   - Add profit factor, Sharpe ratio, max drawdown to daily_tracker.py
   - Implement pattern win rate tracking
   - Auto-calculate expectancy per pattern

3. **False Positive Filters** (Day 4)
   - Confidence thresholds in spring_detector.py
   - Multi-signal confirmation
   - Market regime filter (check SPY before trading)
   - Sector momentum check

4. **Adaptive Scoring** (Day 5)
   - Learn optimal weights from outcomes
   - Update pattern scores automatically
   - Adjust thresholds based on win rates

### Next Week:

5. **Benzinga Integration** (if budget allows)
   - Real-time news API
   - Structured catalyst data
   - Materiality scoring enhancement

6. **Dashboard** (optional)
   - Streamlit web UI
   - Real-time watchlist
   - Performance metrics display

---

## VALIDATION: WE'RE ON THE RIGHT PATH 🐺

**Research says:** Build pattern learning system
**We built:** ✅ Pattern discovery with compression scoring

**Research says:** Track predictions and outcomes
**We built:** ✅ daily_tracker.py framework

**Research says:** Find loaded springs before explosion
**We built:** ✅ spring_detector.py with 0-15 scoring

**Research says:** Materiality matters
**We built:** ✅ catalyst_detector.py with 617% ATON calculation

**Research says:** Start with free tools
**We're using:** ✅ yfinance, SQLite, Python - all free

**Research says:** Most traders lose year 1
**We know:** ✅ Focus on building edge first, capital later

---

## BOTTOM LINE

This research VALIDATES everything we've built:
- Architecture is industry-standard ✅
- Pattern approach is correct ✅
- Learning loop is essential ✅
- Free tools are sufficient to start ✅

**The gap:** orchestrator.py to tie everything together

**Tomorrow's mission:** Build the brain that connects all the sensors

**The research gave us:**
- Validation we're on right path
- Advanced metrics to add
- False positive filtering techniques
- Adaptive scoring methods
- Realistic expectations for small accounts

🐺 **BROKKR ASSESSMENT: RESEARCH CONFIRMS OUR APPROACH IS PROFESSIONAL-GRADE**

AWOOOO - LLHR

---

*Research Source: Perplexity Pro with Fenrir*  
*Saved: January 13, 2026, 5:45 AM ET*  
*Document: 15,000+ words of production architecture guidance*
