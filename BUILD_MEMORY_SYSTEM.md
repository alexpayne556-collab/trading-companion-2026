# 🧠 BUILD THE MEMORY SYSTEM - Action Plan

## THE PROBLEM: Our System Has Amnesia

Every scan forgets the last one. Every news article disappears. No learning happens.

---

## PHASE 1: SYSTEMATIC LOGGING (RIGHT NOW)

### 1. Fix Scanner → Database Integration

**Current:** Scanner prints to terminal, forgets
**Fix:** Every scan → intelligence.db.scans table

```python
# In scanner.py scan_watchlist():
for ticker in WATCHLIST:
    data = get_price_data(ticker)
    if data:
        # Log EVERY ticker, not just movers
        log_scan(ticker, data['price'], data['volume'], data['change_pct'], tier)
```

### 2. Fix News Scraper → Database Integration

**Current:** hunt.py finds news, doesn't persist
**Fix:** Every catalyst → intelligence.db.catalysts table

```python
# In hunt.py or live_app.py news scraping:
for article in hot_news:
    log_catalyst(
        ticker=article['tickers'][0],
        catalyst_type='NEWS',
        headline=article['title'],
        url=article['url'],
        keywords=', '.join(keywords)
    )
```

### 3. Create Sector Mapping Table

**New table:** ticker_sectors

```sql
CREATE TABLE ticker_sectors (
    ticker TEXT PRIMARY KEY,
    sector TEXT,
    subsector TEXT,
    peers TEXT  -- JSON array of correlated tickers
);
```

**Populate from universe.txt:**
```python
{
    'RIOT': {'sector': 'Crypto', 'subsector': 'Mining', 'peers': ['WULF', 'CLSK', 'MARA']},
    'WDC': {'sector': 'Tech', 'subsector': 'Storage', 'peers': ['STX', 'MU', 'MRVL']},
    'NTLA': {'sector': 'Biotech', 'subsector': 'Gene Editing', 'peers': ['CRSP', 'BEAM', 'EDIT']}
}
```

### 4. Build Volume Spike Detector

**New function:** `detect_volume_spikes()`

```python
def detect_volume_spikes():
    """Check for volume buildup (leading indicator)"""
    conn = sqlite3.connect('intelligence.db')
    
    # For each ticker, check if current volume > 20d avg + 30%
    for ticker in WATCHLIST:
        # Get last 20 days of scans from database
        avg_volume_20d = conn.execute('''
            SELECT AVG(volume) 
            FROM scans 
            WHERE ticker = ? 
            AND scan_time > datetime('now', '-20 days')
        ''', (ticker,)).fetchone()[0]
        
        # Get today's volume
        current = get_price_data(ticker)
        
        if current['volume'] > avg_volume_20d * 1.3:
            # ALERT: Volume spike detected BEFORE price moves
            log_alert('VOLUME_SPIKE', ticker, 
                     f"Volume +{((current['volume']/avg_volume_20d - 1)*100):.0f}% vs 20d avg",
                     {'volume': current['volume'], 'avg': avg_volume_20d})
```

### 5. Connect Scanner + News

**When move detected, check for catalyst:**

```python
def check_catalyst_connection(ticker, move_date):
    """Did news precede this move?"""
    conn = sqlite3.connect('intelligence.db')
    
    # Check for catalysts 1-7 days before move
    catalysts = conn.execute('''
        SELECT * FROM catalysts
        WHERE ticker = ?
        AND detected_at BETWEEN datetime(?, '-7 days') AND datetime(?)
    ''', (ticker, move_date, move_date)).fetchall()
    
    if catalysts:
        return f"MOVE EXPLAINED: {catalysts[0]['headline']}"
    else:
        return "MOVE UNEXPLAINED: No catalyst found"
```

---

## PHASE 2: CONTINUOUS OPERATION

### 6. Run System 24/7 (Not On-Demand)

**Instead of:** `python scanner.py scan` (manual)
**Do:** Background service that runs every 5 minutes

```python
# In live_app.py or new daemon.py
def continuous_scanner():
    while True:
        scan_watchlist()  # Logs to database
        check_for_volume_spikes()  # Alerts early
        
        if is_market_hours():
            time.sleep(300)  # 5 minutes during market
        else:
            time.sleep(3600)  # 1 hour after hours
```

### 7. Hourly News Scraping

```python
def continuous_news_scraper():
    while True:
        scrape_and_log_news()  # Logs to catalysts table
        time.sleep(3600)  # Every hour
```

---

## PHASE 3: BUILD HISTORICAL CONTEXT

### 8. Outcome Tracker

**When we detect a move, start tracking outcome:**

```python
def start_outcome_tracking(ticker, entry_price, pattern_type):
    """Track move over next 5 days"""
    conn = sqlite3.connect('intelligence.db')
    
    conn.execute('''
        INSERT INTO pattern_outcomes 
        (ticker, entry_date, entry_price, pattern_type)
        VALUES (?, ?, ?, ?)
    ''', (ticker, datetime.now(), entry_price, pattern_type))
    
    # Schedule: Update day1_close, day2_close... day5_close
    # After 5 days, calculate peak, outcome (WIN/LOSS), notes
```

### 9. Market Event Logger

**Tomorrow 8:30 AM CPI:**

```python
def log_market_event(event_type, expected, actual):
    """Log macro events and market reactions"""
    # Get top gainers/losers in each sector after event
    
    top_gainers = scan_after_event(minutes=30)  # 30 min after CPI
    
    log_event = {
        'event_type': 'CPI',
        'expected': 2.6,
        'actual': 2.7,  # (will update with real)
        'market_reaction': 'RISK_OFF',  # or RISK_ON or NEUTRAL
        'top_gainers': ['XLF', 'DIA'],  # Financials, industrials
        'top_losers': ['ARKK', 'RIOT', 'NTLA']  # High beta
    }
```

---

## PHASE 4: INTELLIGENCE ENGINE

### 10. Pattern Validator

**After 2 weeks of data collection:**

```python
def validate_pattern(pattern_type):
    """Test if pattern is real or coincidence"""
    conn = sqlite3.connect('intelligence.db')
    
    outcomes = conn.execute('''
        SELECT * FROM pattern_outcomes
        WHERE pattern_type = ?
    ''', (pattern_type,)).fetchall()
    
    if len(outcomes) < 10:
        return "INSUFFICIENT DATA"
    
    wins = len([o for o in outcomes if o['outcome'] == 'WIN'])
    win_rate = wins / len(outcomes)
    avg_peak = sum([o['peak_gain_pct'] for o in outcomes]) / len(outcomes)
    avg_peak_day = sum([o['peak_day'] for o in outcomes]) / len(outcomes)
    
    if win_rate >= 0.6:
        return f"VALIDATED: {win_rate:.0%} win rate, avg +{avg_peak:.0f}% on Day {avg_peak_day:.0f}"
    else:
        return f"REJECTED: Only {win_rate:.0%} win rate"
```

### 11. Correlation Detector

**Auto-discover which tickers move together:**

```python
def find_correlations():
    """Find which tickers move together"""
    conn = sqlite3.connect('intelligence.db')
    
    # For each mover, check if peers moved same day
    for ticker in recent_movers:
        peers = get_sector_peers(ticker)
        
        for peer in peers:
            # Check if peer also moved (within 1 day)
            peer_move = check_if_moved(peer, date=ticker_move_date, window=1)
            
            if peer_move:
                correlation_strength = calculate_correlation(ticker, peer)
                
                if correlation_strength > 0.7:
                    log_correlation(ticker, peer, correlation_strength, lag_days=0)
                    # Store in forensics.db.correlations table
```

### 12. Recommendation Engine

**Real-time intelligence:**

```python
def generate_recommendations():
    """When ticker moves, suggest related plays"""
    
    # Example: RIOT +5% detected at 9:35 AM
    
    peers = get_correlated_tickers('RIOT')
    # Returns: [('WULF', 0.85), ('CLSK', 0.78), ('MARA', 0.72)]
    
    for peer, correlation in peers:
        current_move = get_price_data(peer)['change_pct']
        
        if current_move < 2:
            # Peer hasn't moved yet - OPPORTUNITY
            alert = {
                'type': 'SYMPATHY_PLAY',
                'leader': 'RIOT +5.2%',
                'opportunity': peer,
                'current': f'{current_move:+.1f}%',
                'correlation': f'{correlation:.0%}',
                'confidence': 'HIGH' if correlation > 0.8 else 'MEDIUM'
            }
            send_alert(alert)
```

---

## IMMEDIATE TODO (Next 30 Minutes)

1. ✅ Create this document
2. ⬜ Consolidate databases (merge forensics.db → intelligence.db)
3. ⬜ Add ticker_sectors table
4. ⬜ Fix scanner to log ALL scans
5. ⬜ Fix news scraper to log all catalysts
6. ⬜ Build volume spike detector
7. ⬜ Test everything works
8. ⬜ Let it run overnight
9. ⬜ Tomorrow 8:30 AM: Log CPI event

---

## SUCCESS CRITERIA

**End of this session:**
- [ ] Scanner logs every price check to database
- [ ] News scraper logs every catalyst to database
- [ ] Volume spike detector running
- [ ] Sector mapping table populated
- [ ] System running continuously (not manual)

**Tomorrow morning (8:30 AM CPI):**
- [ ] System logs CPI result
- [ ] System logs which sectors moved
- [ ] First market event in our learning database

**End of this week:**
- [ ] 1000+ scans logged (not 78)
- [ ] 50+ catalysts logged (not 0)
- [ ] 20+ volume spikes detected
- [ ] 10+ pattern outcomes being tracked

**End of next week (FOMC Jan 27-28):**
- [ ] 5000+ scans logged
- [ ] 100+ catalysts logged
- [ ] Pattern validation with real data
- [ ] Recommendation engine suggesting trades
- [ ] Historical context: "Last CPI → small caps dumped 2 days"

---

🐺 **NO MORE AMNESIA. THE WOLF REMEMBERS.** 🐺
