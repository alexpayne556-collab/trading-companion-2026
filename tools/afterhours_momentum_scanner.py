#!/usr/bin/env python3
"""
🐺 AFTER HOURS MOMENTUM SCANNER
===============================
Scans for stocks moving in after hours (4PM-8PM ET)
Designed for swing traders catching overnight momentum

Usage:
    python afterhours_momentum_scanner.py              # Run once
    python afterhours_momentum_scanner.py --live       # Auto-refresh every 60s
    python afterhours_momentum_scanner.py --watchlist  # Only show watchlist stocks
    python afterhours_momentum_scanner.py --alert 3    # Alert on >3% moves
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

# Universe to scan
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
MIN_AH_VOLUME = 50000  # 50K minimum after hours volume

# ============================================================
# SCANNER FUNCTIONS
# ============================================================

def get_eastern_time():
    """Get current time in Eastern timezone"""
    eastern = pytz.timezone('US/Eastern')
    return datetime.now(eastern)

def is_after_hours():
    """Check if we're in after hours (4PM-8PM ET)"""
    et_now = get_eastern_time()
    ah_start = et_now.replace(hour=16, minute=0, second=0, microsecond=0)
    ah_end = et_now.replace(hour=20, minute=0, second=0, microsecond=0)
    weekday = et_now.weekday()
    return weekday < 5 and ah_start <= et_now <= ah_end

def is_market_hours():
    """Check if regular market is open"""
    et_now = get_eastern_time()
    market_open = et_now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = et_now.replace(hour=16, minute=0, second=0, microsecond=0)
    weekday = et_now.weekday()
    return weekday < 5 and market_open <= et_now <= market_close

def get_afterhours_data(ticker):
    """
    Fetch after hours data for a single ticker
    Returns dict with AH price, regular close, volume, change %
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get data with extended hours
        hist_prepost = stock.history(period='2d', prepost=True, interval='1m')
        hist_regular = stock.history(period='2d', prepost=False)
        
        if len(hist_regular) < 1:
            return None
        
        # Regular session close
        regular_close = hist_regular['Close'].iloc[-1]
        
        # Get after hours data
        if len(hist_prepost) > 0:
            et_tz = pytz.timezone('US/Eastern')
            hist_prepost.index = hist_prepost.index.tz_convert(et_tz)
            
            et_now = get_eastern_time()
            today_ah_start = et_now.replace(hour=16, minute=0, second=0, microsecond=0)
            today_ah_end = et_now.replace(hour=20, minute=0, second=0, microsecond=0)
            
            # Filter to after hours today
            ah_data = hist_prepost[
                (hist_prepost.index >= today_ah_start) & 
                (hist_prepost.index <= today_ah_end)
            ]
            
            if len(ah_data) > 0:
                ah_price = ah_data['Close'].iloc[-1]
                ah_volume = ah_data['Volume'].sum()
            else:
                # No AH data yet, use latest available
                ah_price = hist_prepost['Close'].iloc[-1]
                ah_volume = 0
        else:
            ah_price = regular_close
            ah_volume = 0
        
        # Calculate change from close
        if regular_close and regular_close > 0:
            ah_change_pct = ((ah_price - regular_close) / regular_close) * 100
        else:
            ah_change_pct = 0
        
        # Calculate average AH volume for relative volume
        # (simplified - using recent daily volume as proxy)
        avg_daily_vol = hist_regular['Volume'].mean() if len(hist_regular) > 0 else 0
        # AH typically ~5-10% of daily volume
        estimated_avg_ah_vol = avg_daily_vol * 0.05 if avg_daily_vol > 0 else 1
        relative_vol = ah_volume / estimated_avg_ah_vol if estimated_avg_ah_vol > 0 else 0
        
        return {
            'ticker': ticker,
            'ah_price': ah_price,
            'regular_close': regular_close,
            'ah_change_pct': ah_change_pct,
            'ah_volume': ah_volume,
            'relative_vol': relative_vol,
            'sector': SECTOR_MAP.get(ticker, 'Other'),
            'watchlist': ticker in WATCHLIST
        }
        
    except Exception as e:
        return None

def scan_afterhours_momentum(tickers=None, watchlist_only=False):
    """
    Scan all tickers for after hours momentum
    Returns sorted DataFrame of movers
    """
    if tickers is None:
        tickers = SCAN_UNIVERSE
    
    if watchlist_only:
        tickers = [t for t in tickers if t in WATCHLIST]
    
    results = []
    
    print(f"\n⚡ Scanning {len(tickers)} tickers for after hours momentum...")
    
    for i, ticker in enumerate(tickers):
        data = get_afterhours_data(ticker)
        if data:
            # Apply filters
            if MIN_PRICE <= data['ah_price'] <= MAX_PRICE:
                if data['ah_volume'] >= MIN_AH_VOLUME or data['watchlist']:
                    results.append(data)
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"  Scanned {i + 1}/{len(tickers)}...", end='\r')
    
    print(f"  ✓ Scan complete. Found {len(results)} movers.          ")
    
    # Convert to DataFrame and sort by absolute change
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values('ah_change_pct', ascending=False, key=abs)
        return df
    
    return pd.DataFrame()

def display_results(df, alert_threshold=None):
    """Display scan results in clean terminal format"""
    et_now = get_eastern_time()
    
    print("\n" + "=" * 80)
    print(f"🐺 AFTER HOURS MOMENTUM SCANNER — {et_now.strftime('%I:%M %p ET')}")
    print("=" * 80)
    
    if len(df) == 0:
        print("\n  No after hours movers found matching criteria.")
        print("  (Min volume: 50K, Price: $2-$50)")
        return
    
    # Header
    print(f"\n{'TICKER':<8} | {'AH PRICE':>9} | {'CHANGE':>8} | {'AH VOL':>10} | {'REL VOL':>8} | {'SECTOR':<10} | {'WATCH':>5}")
    print("-" * 80)
    
    # Rows
    for _, row in df.head(20).iterrows():
        watch_flag = "⭐" if row['watchlist'] else ""
        change_sign = "+" if row['ah_change_pct'] >= 0 else ""
        
        vol_str = f"{row['ah_volume']/1000:.0f}K" if row['ah_volume'] >= 1000 else f"{row['ah_volume']:.0f}"
        if row['ah_volume'] >= 1000000:
            vol_str = f"{row['ah_volume']/1000000:.1f}M"
        
        rel_vol_str = f"{row['relative_vol']:.1f}x" if row['relative_vol'] > 0 else "—"
        
        print(f"{row['ticker']:<8} | ${row['ah_price']:>8.2f} | {change_sign}{row['ah_change_pct']:>6.1f}% | {vol_str:>10} | {rel_vol_str:>8} | {row['sector']:<10} | {watch_flag:>5}")
    
    print("-" * 80)
    
    # Alerts for big movers
    alerts = []
    
    # Watchlist alerts
    watchlist_movers = df[df['watchlist'] == True]
    if len(watchlist_movers) > 0:
        print(f"\n⭐ WATCHLIST MOVERS:")
        for _, row in watchlist_movers.iterrows():
            direction = "🟢 UP" if row['ah_change_pct'] > 0 else "🔴 DOWN"
            print(f"   {row['ticker']}: {row['ah_change_pct']:+.1f}% {direction} @ ${row['ah_price']:.2f}")
            
            # Check alert threshold
            if alert_threshold and abs(row['ah_change_pct']) >= alert_threshold:
                alerts.append(row)
    
    # Big movers alert
    big_movers = df[abs(df['ah_change_pct']) > 5]
    if len(big_movers) > 0:
        print(f"\n🚨 BIG MOVES (>5%):")
        for _, row in big_movers.head(5).iterrows():
            direction = "🟢" if row['ah_change_pct'] > 0 else "🔴"
            print(f"   {direction} {row['ticker']}: {row['ah_change_pct']:+.1f}% @ ${row['ah_price']:.2f}")
    
    # High relative volume
    high_rvol = df[df['relative_vol'] > 2.0]
    if len(high_rvol) > 0:
        print(f"\n📊 HIGH RELATIVE VOLUME (>2x normal AH):")
        for _, row in high_rvol.head(5).iterrows():
            print(f"   {row['ticker']}: {row['relative_vol']:.1f}x normal AH volume")
    
    # Sound alert for threshold breaches
    if alerts:
        print("\n" + "🔔" * 20)
        print("🚨🚨🚨 ALERT: WATCHLIST STOCKS MOVING 🚨🚨🚨")
        for row in alerts:
            print(f"   {row['ticker']}: {row['ah_change_pct']:+.1f}% (threshold: {alert_threshold}%)")
        print("🔔" * 20)
        # Terminal bell
        print('\a')

def run_live_scanner(watchlist_only=False, refresh_interval=60, alert_threshold=3.0):
    """Run scanner in live mode with auto-refresh"""
    print("\n🐺 AFTER HOURS MOMENTUM SCANNER — LIVE MODE")
    print(f"   Refreshing every {refresh_interval} seconds")
    print(f"   Alert threshold: {alert_threshold}% (watchlist stocks)")
    print("   Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Clear screen
            print("\033[2J\033[H", end="")
            
            # Check if in after hours
            et_now = get_eastern_time()
            if is_market_hours():
                print(f"\n⚠️ Regular market is OPEN ({et_now.strftime('%I:%M %p ET')})")
                print("   After hours scanner is for 4:00 PM - 8:00 PM ET")
                print("   Showing last available data...\n")
            elif not is_after_hours():
                weekday = et_now.weekday()
                hour = et_now.hour
                if weekday >= 5:
                    print(f"\n⚠️ Markets closed (Weekend)")
                elif hour < 16:
                    print(f"\n⚠️ Before after hours ({et_now.strftime('%I:%M %p ET')})")
                    print("   After hours: 4:00 PM - 8:00 PM ET")
                else:
                    print(f"\n⚠️ After hours session ended ({et_now.strftime('%I:%M %p ET')})")
                    print("   After hours: 4:00 PM - 8:00 PM ET")
            
            # Run scan
            df = scan_afterhours_momentum(watchlist_only=watchlist_only)
            display_results(df, alert_threshold=alert_threshold)
            
            print(f"\n   Next refresh in {refresh_interval} seconds... (Ctrl+C to stop)")
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n\n🐺 Scanner stopped. Good hunting!")

def main():
    parser = argparse.ArgumentParser(description='After Hours Momentum Scanner')
    parser.add_argument('--live', action='store_true', help='Run in live mode with auto-refresh')
    parser.add_argument('--watchlist', action='store_true', help='Only scan watchlist stocks')
    parser.add_argument('--refresh', type=int, default=60, help='Refresh interval in seconds (default: 60)')
    parser.add_argument('--alert', type=float, default=3.0, help='Alert threshold %% for watchlist stocks (default: 3.0)')
    
    args = parser.parse_args()
    
    if args.live:
        run_live_scanner(
            watchlist_only=args.watchlist, 
            refresh_interval=args.refresh,
            alert_threshold=args.alert
        )
    else:
        df = scan_afterhours_momentum(watchlist_only=args.watchlist)
        display_results(df, alert_threshold=args.alert)

if __name__ == "__main__":
    main()
