#!/usr/bin/env python3
"""
Direct opportunity finder - watches your tickers and scrapes for catalysts
"""

import yfinance as yf
from datetime import datetime
import time
import sys
import os

# Add webapp to path for database access
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'webapp'))
try:
    from intelligence_db import log_scan, log_alert
    DB_AVAILABLE = True
except:
    DB_AVAILABLE = False
    print("⚠️  Database not available - running in read-only mode")

# Load universe from file
def load_universe():
    """Load trading universe from file"""
    universe_file = '/workspaces/trading-companion-2026/universe.txt'
    tickers = []
    
    if os.path.exists(universe_file):
        with open(universe_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Extract ticker (first word on line)
                ticker = line.split()[0]
                if ticker and ticker.isupper():
                    tickers.append(ticker)
    
    # Fallback to core watchlist if file doesn't exist
    if not tickers:
        tickers = [
            'ATON', 'EVTV', 'LVLU', 'PASW', 'ALMS', 'BEAM', 'MNTS', 'VCIG',
            'OMH', 'RARE', 'NTLA', 'XBIO', 'SRPT', 'ARWR', 'IONS', 'EXAS',
            'VRTX', 'REGN', 'BIIB', 'ATXI', 'WKHS', 'MU', 'ARDX', 'SATL',
            'BLNK', 'DAWN'
        ]
    
    return tickers

WATCHLIST = load_universe()

def get_price_data(ticker):
    """Get current price and daily change"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1d', interval='5m')
        
        if hist.empty or len(hist) < 2:
            # Try daily data
            hist = stock.history(period='5d')
            if hist.empty:
                return None
        
        current = float(hist['Close'].iloc[-1])
        open_price = float(hist['Open'].iloc[0])
        change_pct = ((current - open_price) / open_price) * 100
        volume = int(hist['Volume'].sum()) if 'Volume' in hist else 0
        
        # Get previous close for reference
        prev_close = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else open_price
        
        return {
            'ticker': ticker,
            'price': current,
            'open': open_price,
            'prev_close': prev_close,
            'change_pct': change_pct,
            'volume': volume
        }
    except Exception as e:
        return None

def scan_watchlist():
    """Scan watchlist for movements"""
    print("\n" + "="*100)
    print(f"🎯 WATCHLIST SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100 + "\n")
    
    movers = []
    quiet = []
    
    for ticker in WATCHLIST:
        data = get_price_data(ticker)
        if data:
            change = data['change_pct']
            price = data['price']
            volume = data['volume']
            
            # Determine tier
            tier = None
            if abs(change) >= 100:
                tier = 'WHALE'
            elif abs(change) >= 20:
                tier = 'FISH'
            elif abs(change) >= 10:
                tier = 'BASS'
            elif abs(change) >= 5:
                tier = 'NIBBLE'
            
            # LOG TO DATABASE - THE KEY FIX
            if DB_AVAILABLE:
                log_scan(ticker, price, volume, change, tier)
                
                # Also log alert for significant moves
                if abs(change) >= 20:
                    log_alert(tier, ticker, f"{tier}: {ticker} {change:+.1f}%", 
                             {'price': price, 'volume': volume, 'change_pct': change})
            
            status_icon = "🔥" if abs(change) >= 5 else ("📈" if change > 0 else "📉")
            
            line = f"{status_icon} {ticker:6s} ${price:8.2f}  {change:+6.1f}%"
            
            if abs(change) >= 5:
                line += "  ⚠️  ALERT"
                movers.append((ticker, change, price))
            
            print(line)
            quiet.append(ticker)
        else:
            print(f"❌ {ticker:6s} - No data")
        
        time.sleep(0.3)  # Rate limit
    
    # Summary
    print("\n" + "-"*100)
    if movers:
        print(f"\n🚨 {len(movers)} MOVERS DETECTED:\n")
        for ticker, change, price in sorted(movers, key=lambda x: abs(x[1]), reverse=True):
            tier = "🐋 WHALE" if abs(change) >= 100 else ("🦈 FISH" if abs(change) >= 20 else ("🐟 BASS" if abs(change) >= 10 else "🦐 NIBBLE"))
            print(f"   {tier}: {ticker} {change:+.1f}% @ ${price:.2f}")
    else:
        print(f"\n📊 Market Status: Quiet ({len(quiet)} tickers checked, no >5% moves)")
    
    print("\n" + "="*100 + "\n")
    
    return movers

def watch_mode(interval=60):
    """Continuous watching"""
    print(f"\n👁️  WATCHING {len(WATCHLIST)} TICKERS (checking every {interval}s)\n")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            movers = scan_watchlist()
            print(f"Next scan in {interval} seconds...")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\nStopped watching")

def check_single(ticker):
    """Check single ticker in detail"""
    print(f"\n📊 {ticker.upper()} DETAIL")
    print("="*80 + "\n")
    
    data = get_price_data(ticker)
    if data:
        print(f"Current Price:    ${data['price']:.2f}")
        print(f"Open:             ${data['open']:.2f}")
        print(f"Change:           {data['change_pct']:+.2f}%")
        print(f"Volume:           {data['volume']:,}")
        
        if abs(data['change_pct']) >= 5:
            print(f"\n⚠️  SIGNIFICANT MOVEMENT DETECTED")
        
        # Try to get info
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if 'shortName' in info:
                print(f"\nName:             {info['shortName']}")
            if 'marketCap' in info:
                print(f"Market Cap:       ${info['marketCap']:,}")
        except:
            pass
    else:
        print(f"❌ Could not fetch data for {ticker}")
    
    print()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Trading Intelligence Scanner')
    parser.add_argument('mode', nargs='?', default='scan', 
                       choices=['scan', 'watch', 'check'],
                       help='scan: One-time scan | watch: Continuous | check TICKER: Single ticker')
    parser.add_argument('ticker', nargs='?', help='Ticker for check mode')
    parser.add_argument('--interval', type=int, default=60, help='Watch interval (seconds)')
    
    args = parser.parse_args()
    
    if args.mode == 'scan':
        scan_watchlist()
    elif args.mode == 'watch':
        watch_mode(args.interval)
    elif args.mode == 'check':
        if not args.ticker:
            print("Usage: python scanner.py check ATON")
        else:
            check_single(args.ticker.upper())
