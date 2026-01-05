#!/usr/bin/env python3
"""
🐺 PREMARKET GAP SCANNER
========================
Scans for stocks gapping in premarket (4AM-9:30AM ET)
Designed for swing traders hunting early momentum

Usage:
    python premarket_gap_scanner.py              # Run once
    python premarket_gap_scanner.py --live       # Auto-refresh every 60s
    python premarket_gap_scanner.py --watchlist  # Only show watchlist stocks
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time
import argparse
import sys
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================

# Your watchlist - stocks you're actively tracking
WATCHLIST = [
    'UUUU', 'RDW', 'LUNR', 'RKLB', 'SMR', 'OKLO',  # Nuclear/Space
    'IONQ', 'QBTS', 'RGTI', 'QUBT', 'ARQQ',        # Quantum
    'SOUN', 'VRT', 'PATH', 'AI', 'CORZ',           # AI Infra
    'MU', 'SMCI', 'ANET',                           # Memory/Semi
    'ASTS', 'BKSY', 'SPIR', 'PL',                   # Space
    'LEU', 'CCJ', 'DNN', 'NXE', 'NNE', 'UEC'       # Nuclear
]

# Universe to scan (expand this as needed)
SCAN_UNIVERSE = [
    # Space
    'LUNR', 'RKLB', 'RDW', 'BKSY', 'ASTS', 'SPIR', 'PL', 'SIDU',
    # Nuclear  
    'LEU', 'CCJ', 'UUUU', 'UEC', 'SMR', 'OKLO', 'DNN', 'NXE', 'NNE',
    # Quantum
    'IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ', 'LAES',
    # AI Infrastructure
    'CORZ', 'VRT', 'SOUN', 'PATH', 'UPST', 'AI', 'IREN',
    # Memory/Semi
    'MU', 'WDC', 'SMCI', 'ANET', 'CRDO', 'COHR',
    # Crypto miners
    'MARA', 'RIOT', 'CLSK', 'HUT', 'BITF',
    # Clean Energy
    'PLUG', 'FCEL', 'BE', 'ENPH', 'RUN',
    # EV
    'RIVN', 'LCID', 'NIO',
    # Software/Other
    'PLTR', 'SNOW', 'NET', 'DDOG'
]

# Sector mapping
SECTOR_MAP = {
    'LUNR': 'Space', 'RKLB': 'Space', 'RDW': 'Space', 'BKSY': 'Space',
    'ASTS': 'Space', 'SPIR': 'Space', 'PL': 'Space', 'SIDU': 'Space',
    'LEU': 'Nuclear', 'CCJ': 'Nuclear', 'UUUU': 'Nuclear', 'UEC': 'Nuclear',
    'SMR': 'Nuclear', 'OKLO': 'Nuclear', 'DNN': 'Nuclear', 'NXE': 'Nuclear', 'NNE': 'Nuclear',
    'IONQ': 'Quantum', 'RGTI': 'Quantum', 'QBTS': 'Quantum', 'QUBT': 'Quantum',
    'ARQQ': 'Quantum', 'LAES': 'Quantum',
    'CORZ': 'AI Infra', 'VRT': 'AI Infra', 'SOUN': 'AI Infra', 'PATH': 'AI Infra',
    'UPST': 'AI Infra', 'AI': 'AI Infra', 'IREN': 'AI Infra',
    'MU': 'Memory', 'WDC': 'Memory', 'SMCI': 'Memory', 'ANET': 'Memory',
    'CRDO': 'Memory', 'COHR': 'Memory',
    'MARA': 'Crypto', 'RIOT': 'Crypto', 'CLSK': 'Crypto', 'HUT': 'Crypto', 'BITF': 'Crypto',
    'PLUG': 'Clean', 'FCEL': 'Clean', 'BE': 'Clean', 'ENPH': 'Clean', 'RUN': 'Clean',
    'RIVN': 'EV', 'LCID': 'EV', 'NIO': 'EV', 'TSLA': 'EV',
    'PLTR': 'Software', 'SNOW': 'Software', 'NET': 'Software', 'DDOG': 'Software'
}

# Filters
MIN_PRICE = 2.0
MAX_PRICE = 50.0
MIN_PREMARKET_VOLUME = 100000  # 100K minimum premarket volume

# ============================================================
# SCANNER FUNCTIONS
# ============================================================

def get_eastern_time():
    """Get current time in Eastern timezone"""
    eastern = pytz.timezone('US/Eastern')
    return datetime.now(eastern)

def is_premarket_hours():
    """Check if we're in premarket hours (4AM-9:30AM ET)"""
    et_now = get_eastern_time()
    premarket_start = et_now.replace(hour=4, minute=0, second=0, microsecond=0)
    premarket_end = et_now.replace(hour=9, minute=30, second=0, microsecond=0)
    return premarket_start <= et_now <= premarket_end

def is_market_hours():
    """Check if regular market is open"""
    et_now = get_eastern_time()
    market_open = et_now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = et_now.replace(hour=16, minute=0, second=0, microsecond=0)
    weekday = et_now.weekday()
    return weekday < 5 and market_open <= et_now <= market_close

def get_premarket_data(ticker):
    """
    Fetch premarket data for a single ticker
    Returns dict with premarket price, previous close, volume, gap %
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get current quote (includes premarket if available)
        info = stock.fast_info
        
        # Get historical data for previous close
        hist = stock.history(period='5d', prepost=True)
        
        if len(hist) < 2:
            return None
        
        # Previous regular session close
        # Filter to regular hours only for previous close
        regular_hist = stock.history(period='5d', prepost=False)
        if len(regular_hist) < 1:
            return None
        
        prev_close = regular_hist['Close'].iloc[-1]
        
        # Current price (premarket or last)
        current_price = info.last_price if hasattr(info, 'last_price') else None
        
        if current_price is None:
            # Fallback: use latest from prepost history
            prepost_hist = stock.history(period='1d', prepost=True, interval='1m')
            if len(prepost_hist) > 0:
                current_price = prepost_hist['Close'].iloc[-1]
            else:
                return None
        
        # Calculate gap
        if prev_close and prev_close > 0:
            gap_pct = ((current_price - prev_close) / prev_close) * 100
        else:
            gap_pct = 0
        
        # Get premarket volume (approximate from today's prepost data)
        today_prepost = stock.history(period='1d', prepost=True, interval='1m')
        if len(today_prepost) > 0:
            # Filter to premarket hours only
            et_tz = pytz.timezone('US/Eastern')
            today_prepost.index = today_prepost.index.tz_convert(et_tz)
            
            now_et = get_eastern_time()
            today_start = now_et.replace(hour=4, minute=0, second=0, microsecond=0)
            market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
            
            premarket_data = today_prepost[
                (today_prepost.index >= today_start) & 
                (today_prepost.index < market_open)
            ]
            premarket_volume = premarket_data['Volume'].sum() if len(premarket_data) > 0 else 0
        else:
            premarket_volume = 0
        
        return {
            'ticker': ticker,
            'price': current_price,
            'prev_close': prev_close,
            'gap_pct': gap_pct,
            'pm_volume': premarket_volume,
            'sector': SECTOR_MAP.get(ticker, 'Other'),
            'watchlist': ticker in WATCHLIST
        }
        
    except Exception as e:
        return None

def scan_premarket_gaps(tickers=None, watchlist_only=False):
    """
    Scan all tickers for premarket gaps
    Returns sorted DataFrame of gappers
    """
    if tickers is None:
        tickers = SCAN_UNIVERSE
    
    if watchlist_only:
        tickers = [t for t in tickers if t in WATCHLIST]
    
    results = []
    
    print(f"\n⚡ Scanning {len(tickers)} tickers for premarket gaps...")
    
    for i, ticker in enumerate(tickers):
        data = get_premarket_data(ticker)
        if data:
            # Apply filters
            if MIN_PRICE <= data['price'] <= MAX_PRICE:
                if data['pm_volume'] >= MIN_PREMARKET_VOLUME or data['watchlist']:
                    results.append(data)
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"  Scanned {i + 1}/{len(tickers)}...", end='\r')
    
    print(f"  ✓ Scan complete. Found {len(results)} movers.          ")
    
    # Convert to DataFrame and sort
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values('gap_pct', ascending=False, key=abs)
        return df
    
    return pd.DataFrame()

def display_results(df):
    """Display scan results in clean terminal format"""
    et_now = get_eastern_time()
    
    print("\n" + "=" * 75)
    print(f"🐺 PREMARKET GAP SCANNER — {et_now.strftime('%I:%M %p ET')}")
    print("=" * 75)
    
    if len(df) == 0:
        print("\n  No premarket movers found matching criteria.")
        print("  (Min volume: 100K, Price: $2-$50)")
        return
    
    # Header
    print(f"\n{'TICKER':<8} | {'PRICE':>8} | {'GAP %':>8} | {'PM VOL':>10} | {'SECTOR':<10} | {'WATCH':>5}")
    print("-" * 75)
    
    # Rows
    for _, row in df.head(20).iterrows():
        watch_flag = "⭐" if row['watchlist'] else ""
        gap_color = "+" if row['gap_pct'] >= 0 else ""
        
        vol_str = f"{row['pm_volume']/1000:.0f}K" if row['pm_volume'] >= 1000 else f"{row['pm_volume']:.0f}"
        if row['pm_volume'] >= 1000000:
            vol_str = f"{row['pm_volume']/1000000:.1f}M"
        
        print(f"{row['ticker']:<8} | ${row['price']:>7.2f} | {gap_color}{row['gap_pct']:>6.1f}% | {vol_str:>10} | {row['sector']:<10} | {watch_flag:>5}")
    
    # Summary
    print("-" * 75)
    
    # Highlight watchlist movers
    watchlist_movers = df[df['watchlist'] == True]
    if len(watchlist_movers) > 0:
        print(f"\n⭐ WATCHLIST MOVERS:")
        for _, row in watchlist_movers.iterrows():
            direction = "🟢 UP" if row['gap_pct'] > 0 else "🔴 DOWN"
            print(f"   {row['ticker']}: {row['gap_pct']:+.1f}% {direction}")
    
    # Big gappers alert
    big_gaps = df[abs(df['gap_pct']) > 5]
    if len(big_gaps) > 0:
        print(f"\n🚨 BIG GAPS (>5%):")
        for _, row in big_gaps.head(5).iterrows():
            print(f"   {row['ticker']}: {row['gap_pct']:+.1f}% @ ${row['price']:.2f}")

def run_live_scanner(watchlist_only=False, refresh_interval=60):
    """Run scanner in live mode with auto-refresh"""
    print("\n🐺 PREMARKET GAP SCANNER — LIVE MODE")
    print(f"   Refreshing every {refresh_interval} seconds")
    print("   Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Clear screen (cross-platform)
            print("\033[2J\033[H", end="")
            
            # Check if in premarket hours
            et_now = get_eastern_time()
            if is_market_hours():
                print(f"\n⚠️ Regular market is OPEN ({et_now.strftime('%I:%M %p ET')})")
                print("   Premarket scanner is for 4:00 AM - 9:30 AM ET")
                print("   Showing last available premarket data...\n")
            elif not is_premarket_hours():
                weekday = et_now.weekday()
                if weekday >= 5:
                    print(f"\n⚠️ Markets closed (Weekend)")
                else:
                    print(f"\n⚠️ Outside premarket hours ({et_now.strftime('%I:%M %p ET')})")
                    print("   Premarket: 4:00 AM - 9:30 AM ET")
            
            # Run scan
            df = scan_premarket_gaps(watchlist_only=watchlist_only)
            display_results(df)
            
            print(f"\n   Next refresh in {refresh_interval} seconds... (Ctrl+C to stop)")
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n\n🐺 Scanner stopped. Good hunting!")

def main():
    parser = argparse.ArgumentParser(description='Premarket Gap Scanner')
    parser.add_argument('--live', action='store_true', help='Run in live mode with auto-refresh')
    parser.add_argument('--watchlist', action='store_true', help='Only scan watchlist stocks')
    parser.add_argument('--refresh', type=int, default=60, help='Refresh interval in seconds (default: 60)')
    
    args = parser.parse_args()
    
    if args.live:
        run_live_scanner(watchlist_only=args.watchlist, refresh_interval=args.refresh)
    else:
        df = scan_premarket_gaps(watchlist_only=args.watchlist)
        display_results(df)

if __name__ == "__main__":
    main()
