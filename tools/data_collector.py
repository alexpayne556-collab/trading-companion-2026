#!/usr/bin/env python3
"""
🐺 BROKKR DATA COLLECTOR - NSA Mode
Sweep everything. Store everything. Query when needed.

This runs DAILY (or hourly) and APPENDS to historical database.
After 1 month: We have patterns.
After 3 months: We have cycles.
After 6 months: We know when parties start.

Don't query the market. Query OUR data.
"""

import yfinance as yf
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

# ============================================================================
# DATA STORAGE
# ============================================================================

DATA_DIR = Path('data/collected')
SNAPSHOT_FILE = DATA_DIR / 'daily_snapshots.jsonl'  # JSON Lines format
TIMESERIES_DIR = DATA_DIR / 'timeseries'

# ============================================================================
# UNIVERSE
# ============================================================================

UNIVERSE = {
    'Quantum': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'Nuclear': ['UUUU', 'USAR', 'NXE', 'DNN', 'LEU', 'UEC', 'URG', 'URNM'],
    'Space': ['RKLB', 'ASTS', 'LUNR', 'PL', 'SIDU', 'SPCE', 'ASTR'],
    'Semi': ['NVTS', 'NXPI', 'SWKS', 'MRVL', 'AVGO', 'ARM', 'NVDA', 'AMD', 'INTC', 'MU', 'TSM'],
    'AI_Infra': ['SMCI', 'DELL', 'HPE', 'PLTR', 'SNOW', 'DDOG'],
    'Cloud': ['AMZN', 'GOOGL', 'MSFT', 'META'],
}

# ============================================================================
# COLLECTORS
# ============================================================================

def collect_daily_snapshot(ticker, sector):
    """
    Collect ONE snapshot of ticker at this moment.
    This gets appended to historical log.
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get last few days for context
        hist = stock.history(period='5d')
        if len(hist) == 0:
            return None
        
        today = hist.iloc[-1]
        info = stock.info
        
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'ticker': ticker,
            'sector': sector,
            
            # Price action
            'open': float(today['Open']),
            'high': float(today['High']),
            'low': float(today['Low']),
            'close': float(today['Close']),
            'volume': int(today['Volume']),
            
            # Context
            'avg_volume': int(hist['Volume'].mean()),
            'vol_ratio': float(today['Volume'] / hist['Volume'].mean()) if hist['Volume'].mean() > 0 else 1.0,
            
            # Fundamentals (these change slowly)
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE'),
            'short_pct': info.get('shortPercentOfFloat'),
            'institution_pct': info.get('heldPercentInstitutions'),
            
            # Technical
            'rsi': calculate_rsi(hist),
        }
        
        return snapshot
        
    except Exception as e:
        print(f"❌ {ticker}: {e}")
        return None

def calculate_rsi(hist, period=14):
    """Quick RSI calculation."""
    if len(hist) < period:
        return None
    
    changes = hist['Close'].diff().tail(period)
    gains = changes[changes > 0].sum()
    losses = abs(changes[changes < 0].sum())
    
    if losses == 0:
        return 100.0
    
    rs = gains / losses
    return float(100 - (100 / (1 + rs)))

# ============================================================================
# STORAGE
# ============================================================================

def store_snapshot(snapshot):
    """
    Append snapshot to JSONL file.
    One line per snapshot. Easy to grep, easy to load chunks.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(SNAPSHOT_FILE, 'a') as f:
        f.write(json.dumps(snapshot) + '\n')

def store_timeseries(ticker, data):
    """
    Store ticker-specific timeseries for fast queries.
    CSV format: date,open,high,low,close,volume
    """
    TIMESERIES_DIR.mkdir(parents=True, exist_ok=True)
    
    ticker_file = TIMESERIES_DIR / f'{ticker}.csv'
    
    # Load existing if it exists
    if ticker_file.exists():
        existing = pd.read_csv(ticker_file, parse_dates=['date'])
    else:
        existing = pd.DataFrame()
    
    # Append new data
    new_row = pd.DataFrame([{
        'date': data['date'],
        'open': data['open'],
        'high': data['high'],
        'low': data['low'],
        'close': data['close'],
        'volume': data['volume'],
        'vol_ratio': data['vol_ratio'],
    }])
    
    combined = pd.concat([existing, new_row], ignore_index=True)
    combined = combined.drop_duplicates(subset=['date'], keep='last')
    combined = combined.sort_values('date')
    
    combined.to_csv(ticker_file, index=False)

# ============================================================================
# COLLECTION RUN
# ============================================================================

def collect_all():
    """
    Sweep all tickers. Store everything.
    Run this DAILY (cron job or manual).
    """
    print("🐺 DATA COLLECTOR - NSA MODE")
    print("="*80)
    print(f"Timestamp: {datetime.now()}")
    print(f"Target: {sum(len(t) for t in UNIVERSE.values())} tickers")
    print("="*80)
    
    collected = 0
    failed = 0
    
    for sector, tickers in UNIVERSE.items():
        print(f"\n📡 {sector}:", end=' ')
        for ticker in tickers:
            snapshot = collect_daily_snapshot(ticker, sector)
            if snapshot:
                store_snapshot(snapshot)
                store_timeseries(ticker, snapshot)
                print(f"{ticker}", end=' ')
                collected += 1
            else:
                print(f"✗{ticker}", end=' ')
                failed += 1
        print()
    
    print("\n" + "="*80)
    print(f"✅ Collected: {collected}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Stored in: {SNAPSHOT_FILE}")
    print(f"📁 Timeseries: {TIMESERIES_DIR}/")
    print("="*80)

# ============================================================================
# QUERY INTERFACE
# ============================================================================

def query_ticker_history(ticker, days=30):
    """Load ticker history from our database."""
    ticker_file = TIMESERIES_DIR / f'{ticker}.csv'
    if not ticker_file.exists():
        return None
    
    df = pd.read_csv(ticker_file, parse_dates=['date'])
    return df.tail(days)

def query_sector_on_date(sector, date_str):
    """Get all tickers in sector on specific date."""
    results = []
    
    with open(SNAPSHOT_FILE, 'r') as f:
        for line in f:
            snapshot = json.loads(line)
            if snapshot['sector'] == sector and snapshot['date'] == date_str:
                results.append(snapshot)
    
    return results

def query_volume_spikes(date_str, min_vol_ratio=2.0):
    """Find all volume spikes on specific date."""
    spikes = []
    
    with open(SNAPSHOT_FILE, 'r') as f:
        for line in f:
            snapshot = json.loads(line)
            if snapshot['date'] == date_str and snapshot['vol_ratio'] >= min_vol_ratio:
                spikes.append(snapshot)
    
    return sorted(spikes, key=lambda x: x['vol_ratio'], reverse=True)

def build_index():
    """
    Build summary stats from all collected data.
    Call this weekly to see patterns emerging.
    """
    print("🐺 BUILDING INDEX FROM COLLECTED DATA")
    print("="*80)
    
    if not SNAPSHOT_FILE.exists():
        print("❌ No data collected yet. Run collect_all() first.")
        return
    
    # Count snapshots
    snapshot_count = 0
    dates = set()
    tickers = set()
    
    with open(SNAPSHOT_FILE, 'r') as f:
        for line in f:
            snapshot = json.loads(line)
            snapshot_count += 1
            dates.add(snapshot['date'])
            tickers.add(snapshot['ticker'])
    
    print(f"📊 Total snapshots: {snapshot_count:,}")
    print(f"📅 Date range: {min(dates)} → {max(dates)}")
    print(f"🎯 Unique tickers: {len(tickers)}")
    print(f"📆 Days collected: {len(dates)}")
    print(f"📈 Avg snapshots/day: {snapshot_count / len(dates):.0f}")
    
    print("\n💡 After 1 month of collection, you'll see:")
    print("   - Which tickers trend together (correlation)")
    print("   - Average run duration (3-4 days confirmed)")
    print("   - Sector rotation patterns (when Semi follows Space)")
    print("   - Volume signature of real vs fake parties")
    print("   - Entry/exit timing optimization (Day 2 vs Day 3)")
    
    print("\n🔥 You don't need to predict. You need to RECOGNIZE.")
    print("="*80)

# ============================================================================
# CLI
# ============================================================================

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'collect':
            collect_all()
        
        elif command == 'index':
            build_index()
        
        elif command == 'query':
            if len(sys.argv) < 3:
                print("Usage: python data_collector.py query TICKER [days]")
                sys.exit(1)
            
            ticker = sys.argv[2].upper()
            days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
            
            hist = query_ticker_history(ticker, days)
            if hist is not None:
                print(hist)
            else:
                print(f"❌ No data for {ticker}")
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: python data_collector.py [collect|index|query TICKER]")
    
    else:
        print("🐺 BROKKR DATA COLLECTOR")
        print("="*80)
        print("Commands:")
        print("  collect - Sweep all tickers, store snapshot")
        print("  index   - Show what we've collected")
        print("  query TICKER [days] - Load ticker history")
        print("\nSetup:")
        print("  1. Run 'collect' daily (cron job or manual)")
        print("  2. Run 'index' weekly to see patterns emerge")
        print("  3. Query when you need to make decisions")
        print("\nThe data compounds. The patterns emerge.")
        print("="*80)
