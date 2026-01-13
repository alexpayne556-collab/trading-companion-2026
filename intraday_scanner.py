#!/usr/bin/env python3
"""
🐺 INTRADAY SCANNER - Catch Moves AS THEY HAPPEN

Not EOD scans. INTRADAY 1-minute data.

Detects:
- Volume buildup (last 30 min vs avg)
- Price breakouts (new HOD)
- Momentum shifts (5-min vs 30-min trend)

THIS is how you catch ATON at +40% before it goes +39% more.
Real-time detection. Not tomorrow's news.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, time as dt_time
import time
import pytz
import sys
import os

# Add webapp to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'webapp'))

try:
    from intelligence_db import log_scan, log_alert
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


def is_market_hours():
    """Check if market is open (9:30 AM - 4:00 PM ET)"""
    et_tz = pytz.timezone('America/New_York')
    now_et = datetime.now(et_tz)
    
    # Check if weekend
    if now_et.weekday() >= 5:
        return False
    
    market_open = dt_time(9, 30)
    market_close = dt_time(16, 0)
    
    current_time = now_et.time()
    
    return market_open <= current_time <= market_close


def get_intraday_data(ticker, period='1d', interval='1m'):
    """Get intraday data for ticker"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        return hist
    except:
        return None


def detect_volume_buildup(hist, lookback_minutes=30):
    """
    Detect if volume is building in last N minutes
    Compare to average minute volume today
    """
    
    if len(hist) < lookback_minutes + 30:
        return None
    
    # Last N minutes volume
    recent_vol = hist['Volume'].tail(lookback_minutes).sum()
    
    # Average volume per N-minute window today
    total_vol = hist['Volume'].sum()
    num_windows = len(hist) // lookback_minutes
    avg_window_vol = total_vol / max(1, num_windows)
    
    if avg_window_vol == 0:
        return None
    
    # Compare
    buildup_pct = ((recent_vol - avg_window_vol) / avg_window_vol) * 100
    
    return {
        'recent_volume': recent_vol,
        'avg_window_volume': avg_window_vol,
        'buildup_pct': buildup_pct,
        'is_building': buildup_pct >= 50  # 50%+ more volume than avg
    }


def detect_price_breakout(hist):
    """
    Detect if price just broke to new high of day (HOD)
    """
    
    if len(hist) < 10:
        return None
    
    current_price = hist['Close'].iloc[-1]
    prev_hod = hist['High'].iloc[:-5].max()  # HOD before last 5 minutes
    
    is_breakout = current_price > prev_hod
    
    return {
        'current_price': current_price,
        'prev_hod': prev_hod,
        'is_breakout': is_breakout,
        'breakout_pct': ((current_price - prev_hod) / prev_hod) * 100 if prev_hod > 0 else 0
    }


def detect_momentum_shift(hist):
    """
    Detect momentum shift: 5-min trend vs 30-min trend
    If 5-min slope > 30-min slope = acceleration
    """
    
    if len(hist) < 30:
        return None
    
    # Last 5 minutes
    recent_5m = hist['Close'].tail(5)
    slope_5m = (recent_5m.iloc[-1] - recent_5m.iloc[0]) / 5
    
    # Last 30 minutes
    recent_30m = hist['Close'].tail(30)
    slope_30m = (recent_30m.iloc[-1] - recent_30m.iloc[0]) / 30
    
    # Is 5-min trend stronger?
    is_accelerating = slope_5m > slope_30m and slope_5m > 0
    
    return {
        'slope_5m': slope_5m,
        'slope_30m': slope_30m,
        'is_accelerating': is_accelerating
    }


def scan_ticker_intraday(ticker):
    """
    Full intraday scan for one ticker
    Returns dict with all signals
    """
    
    hist = get_intraday_data(ticker)
    
    if hist is None or len(hist) < 30:
        return None
    
    # Current price data
    current = hist.iloc[-1]
    open_price = hist.iloc[0]['Open']
    price_change_pct = ((current['Close'] - open_price) / open_price) * 100
    
    # Run detections
    volume_signal = detect_volume_buildup(hist)
    breakout_signal = detect_price_breakout(hist)
    momentum_signal = detect_momentum_shift(hist)
    
    # Aggregate signals
    signals = []
    
    if volume_signal and volume_signal['is_building']:
        signals.append(f"Volume building: +{volume_signal['buildup_pct']:.0f}% last 30min")
    
    if breakout_signal and breakout_signal['is_breakout']:
        signals.append(f"New HOD breakout: {breakout_signal['breakout_pct']:+.1f}%")
    
    if momentum_signal and momentum_signal['is_accelerating']:
        signals.append("Momentum accelerating")
    
    # Only return if we have signals
    if not signals:
        return None
    
    return {
        'ticker': ticker,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'price': current['Close'],
        'price_change_pct': price_change_pct,
        'volume': current['Volume'],
        'signals': signals,
        'volume_signal': volume_signal,
        'breakout_signal': breakout_signal,
        'momentum_signal': momentum_signal
    }


def scan_watchlist_intraday(watchlist_file='dynamic_watchlist.txt'):
    """
    Scan entire watchlist for intraday signals
    """
    
    print(f"🐺 INTRADAY SCANNER - {datetime.now().strftime('%H:%M:%S')}")
    
    if not is_market_hours():
        print("⏸️  Market closed - Intraday scanner paused")
        return []
    
    # Read watchlist
    try:
        with open(watchlist_file, 'r') as f:
            tickers = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"❌ Watchlist file not found: {watchlist_file}")
        print("   Run market_discovery.py first to generate watchlist")
        return []
    
    print(f"📊 Scanning {len(tickers)} tickers for intraday signals...\n")
    
    detections = []
    
    for i, ticker in enumerate(tickers, 1):
        try:
            result = scan_ticker_intraday(ticker)
            
            if result:
                detections.append(result)
                
                # Print detection
                print(f"🎯 {result['ticker']:6s} ${result['price']:8.2f} ({result['price_change_pct']:+6.2f}%)")
                for signal in result['signals']:
                    print(f"   • {signal}")
                print()
                
                # Log to database
                if DB_AVAILABLE:
                    log_alert('INTRADAY_SIGNAL', ticker,
                             f"Intraday: {ticker} {result['price_change_pct']:+.1f}% - {', '.join(result['signals'])}",
                             result)
            
            # Progress update
            if i % 20 == 0:
                print(f"   Progress: {i}/{len(tickers)} scanned...")
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            continue
    
    print(f"\n✅ Scan complete: {len(detections)} signals detected")
    
    return detections


def continuous_scan(interval_seconds=300):
    """
    Run intraday scanner continuously during market hours
    interval_seconds: How often to scan (default 5 minutes)
    """
    
    print("🐺 CONTINUOUS INTRADAY SCANNER")
    print("="*70)
    print(f"Scan interval: {interval_seconds} seconds")
    print("Watching for: Volume buildup, HOD breakouts, momentum acceleration")
    print("Press Ctrl+C to stop")
    print("="*70)
    
    while True:
        try:
            if is_market_hours():
                detections = scan_watchlist_intraday()
                
                if detections:
                    print(f"\n🚨 {len(detections)} tickers with intraday signals!")
                else:
                    print(f"\n💤 No strong signals this scan")
                
                print(f"\n⏰ Next scan in {interval_seconds} seconds...")
            else:
                print(f"\n⏸️  Market closed - Next check in {interval_seconds} seconds")
            
            time.sleep(interval_seconds)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Scanner stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print(f"   Retrying in {interval_seconds} seconds...")
            time.sleep(interval_seconds)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Intraday scanner - Catch moves as they happen')
    parser.add_argument('--ticker', help='Scan single ticker')
    parser.add_argument('--watchlist', default='dynamic_watchlist.txt', 
                       help='Watchlist file (default: dynamic_watchlist.txt)')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuously during market hours')
    parser.add_argument('--interval', type=int, default=300,
                       help='Scan interval in seconds (default: 300 = 5 min)')
    
    args = parser.parse_args()
    
    if args.ticker:
        # Single ticker scan
        result = scan_ticker_intraday(args.ticker)
        if result:
            print(f"\n🎯 {result['ticker']} - {result['price_change_pct']:+.1f}%")
            for signal in result['signals']:
                print(f"   • {signal}")
        else:
            print(f"No signals for {args.ticker}")
    
    elif args.continuous:
        # Continuous scanning
        continuous_scan(args.interval)
    
    else:
        # Single watchlist scan
        scan_watchlist_intraday(args.watchlist)


if __name__ == "__main__":
    main()
