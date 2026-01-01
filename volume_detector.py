#!/usr/bin/env python3
"""
🐺 WOLF PACK VOLUME SPIKE DETECTOR v1.0
Catches unusual volume BEFORE price moves

When institutions accumulate, they leave footprints:
- Volume 2-3x normal = something's happening
- Volume 5x+ normal = BIG money moving
- Volume spike + price flat = ACCUMULATION (bullish)
- Volume spike + price drop = DISTRIBUTION (bearish)

Usage:
    python volume_detector.py                      # Scan watchlist
    python volume_detector.py --ticker BBAI        # Single ticker
    python volume_detector.py --threshold 3        # 3x volume minimum
    python volume_detector.py --continuous 30      # Scan every 30 min

AWOOOO 🐺
"""

import argparse
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import json

try:
    import yfinance as yf
except ImportError:
    print("❌ yfinance not installed!")
    print("Run: pip install yfinance --break-system-packages")
    exit(1)

try:
    import pandas as pd
except ImportError:
    print("❌ pandas not installed!")
    print("Run: pip install pandas --break-system-packages")
    exit(1)


# ============================================================
# CONFIGURATION
# ============================================================

# Wolf Pack Watchlist
WATCHLIST = [
    # Tyr's Price Range ($2-20)
    "BBAI",    # BigBear AI
    "SOUN",    # SoundHound
    "LUNR",    # Intuitive Machines
    "SIDU",    # Sidus Space
    "RIG",     # Transocean
    "TELL",    # Tellurian
    
    # AI Infrastructure (The Fuel)
    "MU",      # Micron - Memory
    "VRT",     # Vertiv - Cooling
    "CCJ",     # Cameco - Nuclear
    
    # Defense
    "PLTR",    # Palantir
    "RKLB",    # Rocket Lab
    "KTOS",    # Kratos
    "LHX",     # L3Harris
    
    # Space
    "ASTS",    # AST SpaceMobile
    
    # Tax-Loss Bounce
    "NKE",     # Nike
    "TTD",     # Trade Desk
    
    # Energy
    "AR",      # Antero Resources
]

# Expanded for broader scanning
EXPANDED_WATCHLIST = WATCHLIST + [
    "NVDA", "AMD", "AVGO", "MRVL",  # Semis
    "OKLO", "SMR", "LEU",            # Nuclear
    "IONQ", "RGTI", "QBTS",          # Quantum (watch for dumps)
    "NOC", "RTX", "GD",              # Defense majors
]


# ============================================================
# VOLUME ANALYSIS FUNCTIONS
# ============================================================

def get_volume_data(ticker: str, days: int = 30) -> Optional[Dict]:
    """
    Get volume analysis for a ticker.
    
    Returns:
        Dict with volume metrics and spike detection
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 10)  # Buffer
        
        hist = stock.history(start=start_date.strftime('%Y-%m-%d'),
                            end=end_date.strftime('%Y-%m-%d'))
        
        if hist.empty or len(hist) < 10:
            return None
        
        # Calculate metrics
        current_volume = hist['Volume'].iloc[-1]
        avg_volume_20 = hist['Volume'].tail(20).mean()
        avg_volume_10 = hist['Volume'].tail(10).mean()
        avg_volume_5 = hist['Volume'].tail(5).mean()
        
        # Volume ratio (today vs 20-day average)
        volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 0
        
        # Price change today
        if len(hist) >= 2:
            price_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / 
                           hist['Close'].iloc[-2]) * 100
        else:
            price_change = 0
        
        # Price change over 5 days
        if len(hist) >= 5:
            price_change_5d = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / 
                              hist['Close'].iloc[-5]) * 100
        else:
            price_change_5d = 0
        
        # Detect accumulation vs distribution
        # High volume + flat/up price = accumulation
        # High volume + down price = distribution
        signal = "NEUTRAL"
        if volume_ratio >= 2:
            if price_change >= 0:
                signal = "ACCUMULATION"
            else:
                signal = "DISTRIBUTION"
        
        # Get company info
        info = stock.info
        name = info.get('shortName', ticker)
        current_price = hist['Close'].iloc[-1]
        
        # Volume trend (is volume increasing over last 5 days?)
        vol_trend = "FLAT"
        if len(hist) >= 5:
            recent_vol = hist['Volume'].tail(5).tolist()
            if recent_vol[-1] > recent_vol[0] * 1.5:
                vol_trend = "INCREASING"
            elif recent_vol[-1] < recent_vol[0] * 0.5:
                vol_trend = "DECREASING"
        
        return {
            'ticker': ticker,
            'name': name[:25],
            'price': round(current_price, 2),
            'price_change': round(price_change, 2),
            'price_change_5d': round(price_change_5d, 2),
            'current_volume': int(current_volume),
            'avg_volume_20': int(avg_volume_20),
            'volume_ratio': round(volume_ratio, 2),
            'volume_trend': vol_trend,
            'signal': signal,
        }
        
    except Exception as e:
        print(f"  ⚠️ Error analyzing {ticker}: {e}")
        return None


def detect_volume_spikes(
    watchlist: List[str],
    threshold: float = 2.0,
    show_all: bool = False
) -> List[Dict]:
    """
    Scan watchlist for volume spikes.
    
    Args:
        watchlist: List of tickers
        threshold: Minimum volume ratio to flag (2.0 = 2x average)
        show_all: Show all tickers regardless of volume
    
    Returns:
        List of volume spike alerts
    """
    print(f"\n🐺 WOLF PACK VOLUME SPIKE DETECTOR")
    print(f"=" * 55)
    print(f"Scanning {len(watchlist)} tickers...")
    print(f"Threshold: {threshold}x average volume")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"=" * 55)
    
    alerts = []
    
    for i, ticker in enumerate(watchlist):
        print(f"  Analyzing {ticker}... ({i+1}/{len(watchlist)})", end='\r')
        
        data = get_volume_data(ticker)
        
        if data is None:
            continue
        
        # Check if it meets threshold
        if data['volume_ratio'] >= threshold:
            alerts.append(data)
        elif show_all:
            alerts.append(data)
        
        time.sleep(0.2)  # Rate limiting
    
    # Clear progress line
    print(" " * 60, end='\r')
    
    # Sort by volume ratio (highest first)
    alerts.sort(key=lambda x: x['volume_ratio'], reverse=True)
    
    return alerts


def display_volume_alerts(alerts: List[Dict], threshold: float = 2.0):
    """
    Display volume spike alerts in a nice format.
    """
    if not alerts:
        print("\n📭 No volume spikes detected above threshold.")
        print(f"   Try lowering --threshold (current: {threshold}x)")
        return
    
    # Separate by signal type
    accumulation = [a for a in alerts if a['signal'] == 'ACCUMULATION']
    distribution = [a for a in alerts if a['signal'] == 'DISTRIBUTION']
    neutral = [a for a in alerts if a['signal'] == 'NEUTRAL']
    
    print(f"\n🎯 FOUND {len(alerts)} VOLUME EVENTS:\n")
    
    if accumulation:
        print("🟢 ACCUMULATION SIGNALS (Volume UP + Price UP/FLAT):")
        print("-" * 70)
        print(f"{'Ticker':<8} {'Price':>8} {'Chg%':>7} {'Vol Ratio':>10} {'Trend':<12} {'Signal'}")
        print("-" * 70)
        for a in accumulation:
            emoji = "🔥" if a['volume_ratio'] >= 3 else "📈"
            print(f"{emoji} {a['ticker']:<6} ${a['price']:>7.2f} {a['price_change']:>+6.2f}% "
                  f"{a['volume_ratio']:>8.1f}x  {a['volume_trend']:<12} {a['signal']}")
        print()
    
    if distribution:
        print("🔴 DISTRIBUTION SIGNALS (Volume UP + Price DOWN):")
        print("-" * 70)
        print(f"{'Ticker':<8} {'Price':>8} {'Chg%':>7} {'Vol Ratio':>10} {'Trend':<12} {'Signal'}")
        print("-" * 70)
        for a in distribution:
            emoji = "⚠️" if a['volume_ratio'] >= 3 else "📉"
            print(f"{emoji} {a['ticker']:<6} ${a['price']:>7.2f} {a['price_change']:>+6.2f}% "
                  f"{a['volume_ratio']:>8.1f}x  {a['volume_trend']:<12} {a['signal']}")
        print()
    
    if neutral:
        print("⚪ OTHER VOLUME ACTIVITY:")
        print("-" * 70)
        for a in neutral:
            print(f"   {a['ticker']:<6} ${a['price']:>7.2f} {a['price_change']:>+6.2f}% "
                  f"{a['volume_ratio']:>8.1f}x  {a['volume_trend']}")
        print()


def deep_dive_ticker(ticker: str):
    """
    Deep analysis of a single ticker's volume patterns.
    """
    print(f"\n🔍 DEEP DIVE: {ticker}")
    print("=" * 55)
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="3mo")
        
        if hist.empty:
            print("No data available.")
            return
        
        info = stock.info
        
        # Basic info
        print(f"\n📊 COMPANY INFO:")
        print(f"   Name: {info.get('shortName', 'N/A')}")
        print(f"   Sector: {info.get('sector', 'N/A')}")
        print(f"   Market Cap: ${info.get('marketCap', 0):,.0f}")
        
        # Current state
        current_price = hist['Close'].iloc[-1]
        current_vol = hist['Volume'].iloc[-1]
        avg_vol = hist['Volume'].mean()
        
        print(f"\n📈 CURRENT STATE:")
        print(f"   Price: ${current_price:.2f}")
        print(f"   Today's Volume: {current_vol:,.0f}")
        print(f"   Avg Volume (3mo): {avg_vol:,.0f}")
        print(f"   Volume Ratio: {current_vol/avg_vol:.2f}x")
        
        # Find historical spikes
        print(f"\n🔥 VOLUME SPIKE HISTORY (>2x avg):")
        print("-" * 55)
        
        spikes = []
        for i in range(len(hist)):
            if hist['Volume'].iloc[i] > avg_vol * 2:
                date = hist.index[i].strftime('%Y-%m-%d')
                vol = hist['Volume'].iloc[i]
                ratio = vol / avg_vol
                price = hist['Close'].iloc[i]
                
                # Price change that day
                if i > 0:
                    prev_close = hist['Close'].iloc[i-1]
                    pct_change = ((price - prev_close) / prev_close) * 100
                else:
                    pct_change = 0
                
                spikes.append({
                    'date': date,
                    'volume': vol,
                    'ratio': ratio,
                    'price': price,
                    'change': pct_change
                })
        
        # Show last 10 spikes
        for spike in spikes[-10:]:
            signal = "📈" if spike['change'] >= 0 else "📉"
            print(f"   {spike['date']} | {spike['ratio']:.1f}x | "
                  f"${spike['price']:.2f} | {spike['change']:+.2f}% {signal}")
        
        if not spikes:
            print("   No significant volume spikes in last 3 months.")
        
        # Volume trend analysis
        print(f"\n📊 VOLUME TREND:")
        vol_1w = hist['Volume'].tail(5).mean()
        vol_2w = hist['Volume'].tail(10).head(5).mean()
        vol_1m = hist['Volume'].tail(20).mean()
        
        print(f"   Last Week Avg:  {vol_1w:,.0f}")
        print(f"   Prior Week Avg: {vol_2w:,.0f}")
        print(f"   Monthly Avg:    {vol_1m:,.0f}")
        
        if vol_1w > vol_2w * 1.3:
            print(f"   ➡️ Volume INCREASING week over week")
        elif vol_1w < vol_2w * 0.7:
            print(f"   ➡️ Volume DECREASING week over week")
        else:
            print(f"   ➡️ Volume relatively STABLE")
        
        print()
        
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")


def continuous_scan(watchlist: List[str], interval: int, threshold: float):
    """
    Continuously scan for volume spikes.
    """
    print(f"\n🐺 CONTINUOUS VOLUME MONITORING")
    print(f"Scanning every {interval} minutes...")
    print(f"Press Ctrl+C to stop.\n")
    
    scan_count = 0
    
    try:
        while True:
            scan_count += 1
            print(f"\n{'='*55}")
            print(f"SCAN #{scan_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*55}")
            
            alerts = detect_volume_spikes(watchlist, threshold=threshold)
            
            # Only show spikes
            spikes = [a for a in alerts if a['volume_ratio'] >= threshold]
            
            if spikes:
                display_volume_alerts(spikes, threshold)
                
                # Save alerts
                filename = f"volume_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(spikes, f, indent=2, default=str)
                print(f"💾 Alerts saved to {filename}")
            else:
                print(f"\n✅ No volume spikes above {threshold}x threshold.")
            
            print(f"\n⏰ Next scan in {interval} minutes...")
            time.sleep(interval * 60)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped.")
        print(f"Total scans: {scan_count}")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='🐺 Wolf Pack Volume Spike Detector',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Volume Signals:
  ACCUMULATION = High volume + price UP/flat (institutions buying)
  DISTRIBUTION = High volume + price DOWN (institutions selling)
  
Examples:
    python volume_detector.py                      # Scan watchlist
    python volume_detector.py --ticker BBAI        # Deep dive single ticker
    python volume_detector.py --threshold 3        # Only 3x+ volume
    python volume_detector.py --continuous 30      # Scan every 30 min
    python volume_detector.py --expanded           # Larger watchlist

AWOOOO 🐺
        """
    )
    
    parser.add_argument('--ticker', type=str,
                        help='Deep dive analysis on single ticker')
    parser.add_argument('--threshold', type=float, default=2.0,
                        help='Volume ratio threshold (default: 2.0x)')
    parser.add_argument('--continuous', type=int, metavar='MINUTES',
                        help='Continuous scanning interval in minutes')
    parser.add_argument('--expanded', action='store_true',
                        help='Use expanded watchlist')
    parser.add_argument('--all', action='store_true',
                        help='Show all tickers, not just spikes')
    
    args = parser.parse_args()
    
    # Single ticker deep dive
    if args.ticker:
        deep_dive_ticker(args.ticker.upper())
        return
    
    # Select watchlist
    watchlist = EXPANDED_WATCHLIST if args.expanded else WATCHLIST
    
    # Continuous monitoring
    if args.continuous:
        continuous_scan(watchlist, args.continuous, args.threshold)
        return
    
    # Single scan
    alerts = detect_volume_spikes(
        watchlist=watchlist,
        threshold=args.threshold,
        show_all=args.all
    )
    
    display_volume_alerts(alerts, args.threshold)
    
    if alerts:
        print("💡 TIP: Use --ticker SYMBOL for deep dive analysis")
        print("   Example: python volume_detector.py --ticker BBAI")
    
    print("\n🐺 AWOOOO - The volume tells the truth!")


if __name__ == "__main__":
    main()
