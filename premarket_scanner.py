#!/usr/bin/env python3
"""
🐺 WOLF PACK PRE-MARKET GAP SCANNER v1.0
Catches overnight movers before market open

Run at 4am-9:30am EST to catch:
- Gap ups/downs on news
- Pre-market volume spikes
- Overnight catalyst reactions

Usage:
    python premarket_scanner.py                    # Scan watchlist
    python premarket_scanner.py --min-gap 5       # Min 5% gap
    python premarket_scanner.py --min-volume 100000  # Min 100k pre-market volume
    
AWOOOO 🐺
"""

import argparse
import json
from datetime import datetime, timedelta
from typing import Optional
import time

# Try to import yfinance, give instructions if not installed
try:
    import yfinance as yf
except ImportError:
    print("❌ yfinance not installed!")
    print("Run: pip install yfinance --break-system-packages")
    exit(1)

# ============================================================
# CONFIGURATION
# ============================================================

# Wolf Pack Watchlist - Tyr's hunting grounds
WATCHLIST = [
    # AI Infrastructure (The Fuel)
    "MU",      # Micron - Memory king
    "VRT",     # Vertiv - Cooling
    "CCJ",     # Cameco - Nuclear/Uranium
    
    # Defense
    "BBAI",    # BigBear AI - In Tyr's range
    "PLTR",    # Palantir
    "RKLB",    # Rocket Lab
    "LHX",     # L3Harris
    "NOC",     # Northrop
    
    # Space
    "LUNR",    # Intuitive Machines
    
    # Tyr's Price Range ($2-20)
    "SIDU",    # Sidus Space - Contract play
    "SOUN",    # SoundHound
    "IONQ",    # Quantum (careful - bubble)
    "RIG",     # Transocean - Energy
    
    # Tax-Loss Bounce Candidates
    "NKE",     # Nike - Insider buying
    "TTD",     # Trade Desk - Oversold
    
    # Natural Gas
    "AR",      # Antero Resources
]

# Expanded list for broader scanning
EXPANDED_WATCHLIST = WATCHLIST + [
    "NVDA", "AMD", "AVGO", "MRVL",  # Semiconductors
    "OKLO", "SMR", "LEU",            # Nuclear
    "ASTS", "SPCE",                   # Space
    "RGTI", "QBTS",                   # Quantum (lottery)
    "GEV", "VST", "CEG",              # Power
]


# ============================================================
# SCANNER FUNCTIONS
# ============================================================

def get_premarket_data(ticker: str) -> Optional[dict]:
    """
    Get pre-market data for a ticker.
    Returns gap %, pre-market price, volume info.
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get current quote info
        info = stock.info
        
        # Get previous close and current pre/post market price
        prev_close = info.get('previousClose', 0)
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        pre_market_price = info.get('preMarketPrice', 0)
        post_market_price = info.get('postMarketPrice', 0)
        
        # Use pre-market if available, otherwise post-market, otherwise current
        active_price = pre_market_price or post_market_price or current_price
        
        if not prev_close or not active_price:
            return None
        
        # Calculate gap
        gap_percent = ((active_price - prev_close) / prev_close) * 100
        
        # Volume data
        avg_volume = info.get('averageVolume', 0)
        pre_market_volume = info.get('preMarketVolume', 0)
        regular_volume = info.get('regularMarketVolume', 0)
        
        # Get company name
        name = info.get('shortName', ticker)
        
        # Market cap for context
        market_cap = info.get('marketCap', 0)
        
        return {
            'ticker': ticker,
            'name': name,
            'prev_close': round(prev_close, 2),
            'current_price': round(active_price, 2),
            'pre_market_price': round(pre_market_price, 2) if pre_market_price else None,
            'gap_percent': round(gap_percent, 2),
            'avg_volume': avg_volume,
            'pre_market_volume': pre_market_volume,
            'regular_volume': regular_volume,
            'market_cap': market_cap,
            'price_source': 'pre-market' if pre_market_price else ('post-market' if post_market_price else 'regular')
        }
        
    except Exception as e:
        print(f"  ⚠️ Error fetching {ticker}: {e}")
        return None


def scan_for_gaps(
    watchlist: list,
    min_gap: float = 3.0,
    max_gap: float = 50.0,
    min_volume: int = 0,
    show_all: bool = False
) -> list:
    """
    Scan watchlist for pre-market gaps.
    
    Args:
        watchlist: List of tickers to scan
        min_gap: Minimum gap % to report (absolute value)
        max_gap: Maximum gap % (filter out data errors)
        min_volume: Minimum pre-market volume
        show_all: Show all tickers, not just gappers
    
    Returns:
        List of gap alerts sorted by gap size
    """
    print(f"\n🐺 WOLF PACK PRE-MARKET SCANNER")
    print(f"=" * 50)
    print(f"Scanning {len(watchlist)} tickers...")
    print(f"Min Gap: {min_gap}% | Max Gap: {max_gap}%")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"=" * 50)
    
    alerts = []
    
    for i, ticker in enumerate(watchlist):
        # Progress indicator
        print(f"  Scanning {ticker}... ({i+1}/{len(watchlist)})", end='\r')
        
        data = get_premarket_data(ticker)
        
        if data is None:
            continue
        
        gap = data['gap_percent']
        abs_gap = abs(gap)
        
        # Check if it meets criteria
        meets_gap = abs_gap >= min_gap and abs_gap <= max_gap
        meets_volume = data['pre_market_volume'] >= min_volume if data['pre_market_volume'] else True
        
        if meets_gap and meets_volume:
            alerts.append(data)
        elif show_all:
            alerts.append(data)
        
        # Small delay to avoid rate limiting
        time.sleep(0.1)
    
    # Clear the progress line
    print(" " * 60, end='\r')
    
    # Sort by absolute gap size (biggest movers first)
    alerts.sort(key=lambda x: abs(x['gap_percent']), reverse=True)
    
    return alerts


def display_alerts(alerts: list, show_details: bool = True):
    """
    Display gap alerts in a nice format.
    """
    if not alerts:
        print("\n📭 No significant gaps found.")
        print("   This could mean:")
        print("   - Markets are calm overnight")
        print("   - Pre-market hasn't opened yet (starts 4am EST)")
        print("   - Try lowering --min-gap threshold")
        return
    
    print(f"\n🎯 FOUND {len(alerts)} MOVERS:\n")
    
    # Separate gappers up vs down
    gap_ups = [a for a in alerts if a['gap_percent'] > 0]
    gap_downs = [a for a in alerts if a['gap_percent'] < 0]
    
    if gap_ups:
        print("📈 GAP UPS:")
        print("-" * 60)
        for alert in gap_ups:
            direction = "🟢"
            print(f"{direction} {alert['ticker']:6} | {alert['gap_percent']:+6.2f}% | "
                  f"${alert['prev_close']:7.2f} → ${alert['current_price']:7.2f}")
            if show_details and alert['pre_market_volume']:
                vol_str = f"{alert['pre_market_volume']:,}"
                print(f"         Pre-market vol: {vol_str} | Source: {alert['price_source']}")
        print()
    
    if gap_downs:
        print("📉 GAP DOWNS:")
        print("-" * 60)
        for alert in gap_downs:
            direction = "🔴"
            print(f"{direction} {alert['ticker']:6} | {alert['gap_percent']:+6.2f}% | "
                  f"${alert['prev_close']:7.2f} → ${alert['current_price']:7.2f}")
            if show_details and alert['pre_market_volume']:
                vol_str = f"{alert['pre_market_volume']:,}"
                print(f"         Pre-market vol: {vol_str} | Source: {alert['price_source']}")
        print()


def check_news_catalysts(ticker: str) -> list:
    """
    Quick check for recent news on a ticker.
    Returns list of recent headlines.
    """
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        if not news:
            return []
        
        # Get headlines from last 24 hours
        recent = []
        cutoff = datetime.now() - timedelta(hours=24)
        
        for article in news[:5]:  # Top 5 articles
            title = article.get('title', '')
            publisher = article.get('publisher', '')
            link = article.get('link', '')
            
            recent.append({
                'title': title,
                'publisher': publisher,
                'link': link
            })
        
        return recent
        
    except Exception as e:
        return []


def investigate_mover(ticker: str):
    """
    Deep dive on a specific mover - get price data + news.
    """
    print(f"\n🔍 INVESTIGATING {ticker}")
    print("=" * 50)
    
    # Get price data
    data = get_premarket_data(ticker)
    if data:
        print(f"\n📊 PRICE DATA:")
        print(f"   Previous Close: ${data['prev_close']}")
        print(f"   Current Price:  ${data['current_price']} ({data['price_source']})")
        print(f"   Gap: {data['gap_percent']:+.2f}%")
        if data['pre_market_volume']:
            print(f"   Pre-market Vol: {data['pre_market_volume']:,}")
        print(f"   Avg Volume: {data['avg_volume']:,}")
    
    # Get news
    print(f"\n📰 RECENT NEWS:")
    news = check_news_catalysts(ticker)
    if news:
        for i, article in enumerate(news, 1):
            print(f"   {i}. {article['title'][:60]}...")
            print(f"      Source: {article['publisher']}")
    else:
        print("   No recent news found")
    
    print()


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='🐺 Wolf Pack Pre-Market Gap Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python premarket_scanner.py                    # Scan Wolf Pack watchlist
    python premarket_scanner.py --expanded         # Scan expanded list
    python premarket_scanner.py --min-gap 5        # Only gaps > 5%
    python premarket_scanner.py --ticker BBAI      # Investigate specific ticker
    python premarket_scanner.py --all              # Show all tickers
    
Best run between 4am-9:30am EST for pre-market data.

AWOOOO 🐺
        """
    )
    
    parser.add_argument('--min-gap', type=float, default=3.0,
                        help='Minimum gap %% to report (default: 3.0)')
    parser.add_argument('--max-gap', type=float, default=50.0,
                        help='Maximum gap %% - filters errors (default: 50.0)')
    parser.add_argument('--min-volume', type=int, default=0,
                        help='Minimum pre-market volume (default: 0)')
    parser.add_argument('--ticker', type=str,
                        help='Investigate a specific ticker')
    parser.add_argument('--expanded', action='store_true',
                        help='Use expanded watchlist')
    parser.add_argument('--all', action='store_true',
                        help='Show all tickers, not just gappers')
    parser.add_argument('--no-details', action='store_true',
                        help='Hide volume details')
    
    args = parser.parse_args()
    
    # Single ticker investigation
    if args.ticker:
        investigate_mover(args.ticker.upper())
        return
    
    # Select watchlist
    watchlist = EXPANDED_WATCHLIST if args.expanded else WATCHLIST
    
    # Run the scan
    alerts = scan_for_gaps(
        watchlist=watchlist,
        min_gap=args.min_gap,
        max_gap=args.max_gap,
        min_volume=args.min_volume,
        show_all=args.all
    )
    
    # Display results
    display_alerts(alerts, show_details=not args.no_details)
    
    # If we found big movers, offer to investigate
    if alerts:
        print("\n💡 TIP: Run with --ticker SYMBOL to investigate a specific mover")
        print("   Example: python premarket_scanner.py --ticker BBAI")
    
    print("\n🐺 AWOOOO - Happy hunting!")


if __name__ == "__main__":
    main()
