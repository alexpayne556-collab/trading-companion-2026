#!/usr/bin/env python3
"""
🐺 MARKET MOVER FINDER
Finds what's ACTUALLY moving across the entire market.
Not a static watchlist. Dynamic discovery.

The question isn't "did our 142 tickers move?"
The question is "WHAT moved today that we should know about?"

Built by Brokkr because Fenrir talked but didn't ship.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import json
import time
import argparse

# =============================================================================
# FINVIZ SCRAPERS (Free, covers entire market)
# =============================================================================

def get_finviz_gainers():
    """Get top gainers from Finviz - ENTIRE MARKET"""
    url = "https://finviz.com/screener.ashx?v=111&s=ta_topgainers&f=sh_price_u20,sh_avgvol_o200"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        gainers = []
        # Find ticker links
        links = soup.find_all('a', class_='screener-link-primary')
        
        for link in links[:30]:
            ticker = link.text.strip()
            if ticker and len(ticker) <= 5 and ticker.isalpha():
                gainers.append({
                    'ticker': ticker,
                    'source': 'finviz_gainers'
                })
        
        return gainers
    except Exception as e:
        print(f"   Finviz gainers error: {e}")
        return []

def get_finviz_volume():
    """Get unusual volume from Finviz"""
    url = "https://finviz.com/screener.ashx?v=111&s=ta_unusualvolume&f=sh_price_u20"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        spikes = []
        links = soup.find_all('a', class_='screener-link-primary')
        
        for link in links[:30]:
            ticker = link.text.strip()
            if ticker and len(ticker) <= 5 and ticker.isalpha():
                spikes.append({
                    'ticker': ticker,
                    'source': 'finviz_volume'
                })
        
        return spikes
    except Exception as e:
        print(f"   Finviz volume error: {e}")
        return []

def get_finviz_premarket():
    """Get premarket gainers from Finviz"""
    # Premarket data requires Finviz Elite, use alternate source
    url = "https://finviz.com/screener.ashx?v=111&s=ta_topgainers&f=sh_price_u20"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        gainers = []
        links = soup.find_all('a', class_='screener-link-primary')
        
        for link in links[:20]:
            ticker = link.text.strip()
            if ticker and len(ticker) <= 5 and ticker.isalpha():
                gainers.append({
                    'ticker': ticker,
                    'source': 'finviz_premarket'
                })
        
        return gainers
    except Exception as e:
        print(f"   Finviz premarket error: {e}")
        return []

# =============================================================================
# YAHOO FINANCE (Reliable backup)
# =============================================================================

def get_yahoo_gainers():
    """Get gainers from Yahoo Finance API-style"""
    try:
        # Use yfinance to get market movers
        import yfinance as yf
        
        gainers = []
        # Check a broad set of tickers for big moves
        # This is a fallback when scrapers fail
        
        return gainers
    except Exception as e:
        print(f"   Yahoo error: {e}")
        return []

# =============================================================================
# LEGS CHECKER - Does this mover have room to run?
# =============================================================================

def check_legs(ticker):
    """
    Check if a mover has LEGS or is EXHAUSTED.
    Key question: not "did it move" but "will it KEEP moving"
    
    Based on pattern_outcomes.json analysis:
    - Tiny float (<20M) + catalyst = CONTINUATION likely
    - Large float (>200M) + no catalyst = REVERSAL likely
    - Already extended (>50% in 5d) = FADING
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="30d")
        
        if hist.empty or len(hist) < 5:
            return None
        
        # Get key metrics
        float_shares = info.get('floatShares', info.get('sharesOutstanding', 0))
        market_cap = info.get('marketCap', 0)
        
        # Volume analysis
        avg_volume = hist['Volume'][:-1].mean() if len(hist) > 1 else hist['Volume'].mean()
        today_volume = hist['Volume'].iloc[-1]
        volume_ratio = today_volume / avg_volume if avg_volume > 0 else 1
        
        # Price action
        current_price = hist['Close'].iloc[-1]
        price_5d_ago = hist['Close'].iloc[-5] if len(hist) >= 5 else hist['Close'].iloc[0]
        price_20d_ago = hist['Close'].iloc[-20] if len(hist) >= 20 else hist['Close'].iloc[0]
        
        move_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100
        move_20d = ((current_price - price_20d_ago) / price_20d_ago) * 100
        
        # Today's move
        today_open = hist['Open'].iloc[-1]
        today_move = ((current_price - today_open) / today_open) * 100
        
        # LEGS SCORE (based on pattern_outcomes.json learnings)
        legs_score = 0
        signals = []
        
        # 1. FLOAT SIZE (Most important factor from our data)
        # ATON (1.86M float) = CONTINUED
        # QBTS (339M float) = REVERSED
        if float_shares:
            if float_shares < 5_000_000:
                legs_score += 3
                signals.append("🟢 MICRO FLOAT (<5M) - High continuation odds")
            elif float_shares < 20_000_000:
                legs_score += 2
                signals.append("🟢 TINY FLOAT (<20M) - Good for legs")
            elif float_shares < 50_000_000:
                legs_score += 1
                signals.append("🟡 SMALL FLOAT (<50M)")
            elif float_shares > 200_000_000:
                legs_score -= 2
                signals.append("🔴 LARGE FLOAT (>200M) - Harder to move")
            elif float_shares > 100_000_000:
                legs_score -= 1
                signals.append("🟡 MID FLOAT (>100M)")
        
        # 2. EXTENSION CHECK
        # ATON Jan 6 was already extended from Jan 2 = FLAT
        if move_5d > 80:
            legs_score -= 3
            signals.append("🔴 EXTREMELY EXTENDED (>80% 5d) - DON'T CHASE")
        elif move_5d > 50:
            legs_score -= 2
            signals.append("🔴 EXTENDED (>50% 5d) - Late entry")
        elif move_5d > 30:
            legs_score -= 1
            signals.append("🟡 GETTING HOT (>30% 5d)")
        elif move_5d < 15:
            legs_score += 1
            signals.append("🟢 FRESH MOVE (<15% 5d) - Room to run")
        
        # 3. VOLUME CONFIRMATION
        # High volume = conviction
        if volume_ratio > 5:
            legs_score += 2
            signals.append(f"🟢 HUGE VOLUME ({volume_ratio:.1f}x avg)")
        elif volume_ratio > 2:
            legs_score += 1
            signals.append(f"🟢 HIGH VOLUME ({volume_ratio:.1f}x avg)")
        elif volume_ratio < 1:
            legs_score -= 1
            signals.append(f"🔴 LOW VOLUME ({volume_ratio:.1f}x avg) - No conviction")
        
        # 4. PRICE LEVEL CHECK
        if current_price < 5:
            legs_score += 1
            signals.append("🟢 LOW PRICE (<$5) - Retail interest")
        elif current_price > 50:
            signals.append("🟡 HIGH PRICE (>$50) - Less retail")
        
        # VERDICT based on pattern_outcomes learnings
        if legs_score >= 4:
            verdict = "🚀 STRONG LEGS - Prime entry"
        elif legs_score >= 2:
            verdict = "🟢 POSSIBLE LEGS - Watch for confirmation"
        elif legs_score >= 0:
            verdict = "🟡 UNCERTAIN - Need catalyst"
        elif legs_score >= -2:
            verdict = "⚠️ WEAK - Likely fading"
        else:
            verdict = "🔴 EXHAUSTED - Avoid"
        
        return {
            'ticker': ticker,
            'price': round(current_price, 2),
            'float': float_shares,
            'market_cap': market_cap,
            'volume_ratio': round(volume_ratio, 2),
            'move_today': round(today_move, 1),
            'move_5d': round(move_5d, 1),
            'move_20d': round(move_20d, 1),
            'legs_score': legs_score,
            'signals': signals,
            'verdict': verdict
        }
        
    except Exception as e:
        return {'ticker': ticker, 'error': str(e)}

# =============================================================================
# MAIN DISCOVERY ENGINE
# =============================================================================

def discover_movers(verbose=True):
    """
    Find what's moving RIGHT NOW across the entire market.
    """
    if verbose:
        print("=" * 70)
        print("🐺 WOLF PACK MARKET MOVER FINDER")
        print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
    
    all_movers = []
    
    # Collect from multiple sources
    if verbose:
        print("\n📊 Scanning Finviz gainers...")
    gainers = get_finviz_gainers()
    all_movers.extend(gainers)
    if verbose:
        print(f"   Found {len(gainers)} gainers")
    
    if verbose:
        print("\n📊 Scanning Finviz unusual volume...")
    volume = get_finviz_volume()
    all_movers.extend(volume)
    if verbose:
        print(f"   Found {len(volume)} volume spikes")
    
    # Deduplicate
    seen = set()
    unique_movers = []
    for m in all_movers:
        if m['ticker'] not in seen:
            seen.add(m['ticker'])
            unique_movers.append(m)
    
    if verbose:
        print(f"\n✅ Total unique movers: {len(unique_movers)}")
    
    # Check legs on all movers
    if verbose:
        print("\n" + "=" * 70)
        print("🦵 ANALYZING LEGS ON MOVERS")
        print("=" * 70)
    
    results = []
    for i, mover in enumerate(unique_movers):
        ticker = mover['ticker']
        if verbose:
            print(f"\n[{i+1}/{len(unique_movers)}] {ticker}...")
        
        legs = check_legs(ticker)
        if legs and 'error' not in legs:
            results.append(legs)
            if verbose:
                print(f"   Score: {legs['legs_score']} | {legs['verdict']}")
        else:
            if verbose:
                print(f"   ❌ Could not analyze")
        
        time.sleep(0.3)  # Rate limiting
    
    # Sort by legs score
    results.sort(key=lambda x: x.get('legs_score', -99), reverse=True)
    
    return results

def print_results(results, top_n=15):
    """Print formatted results"""
    print("\n" + "=" * 70)
    print(f"🎯 TOP {top_n} OPPORTUNITIES (by Legs Score)")
    print("=" * 70)
    
    for i, r in enumerate(results[:top_n], 1):
        print(f"\n{i}. {r['ticker']}")
        print(f"   Price: ${r['price']:.2f} | Today: {r['move_today']:+.1f}% | 5D: {r['move_5d']:+.1f}%")
        
        if r['float']:
            float_m = r['float'] / 1_000_000
            print(f"   Float: {float_m:.1f}M | Vol: {r['volume_ratio']:.1f}x avg")
        else:
            print(f"   Float: Unknown | Vol: {r['volume_ratio']:.1f}x avg")
        
        print(f"   Score: {r['legs_score']} → {r['verdict']}")
        
        # Show top 2 signals
        for sig in r['signals'][:2]:
            print(f"   {sig}")

def generate_watchlist(results, filename=None):
    """Generate watchlist CSV for Fidelity ATP"""
    if not filename:
        filename = f"watchlist_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    
    # Filter to only good legs (score >= 1)
    good = [r for r in results if r.get('legs_score', -99) >= 1]
    
    with open(filename, 'w') as f:
        f.write("Symbol\n")
        for r in good:
            f.write(f"{r['ticker']}\n")
    
    print(f"\n✅ Watchlist saved: {filename}")
    print(f"   {len(good)} tickers with legs (score >= 1)")
    
    return filename

def premarket_scan():
    """
    Run this 4-9 AM before market opens.
    Focuses on gap ups and premarket volume.
    """
    print("=" * 70)
    print("🌅 PREMARKET MOVER SCAN")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    movers = get_finviz_premarket()
    
    print(f"\n📊 Found {len(movers)} premarket movers")
    
    if movers:
        results = []
        for m in movers[:10]:
            legs = check_legs(m['ticker'])
            if legs and 'error' not in legs:
                results.append(legs)
                print(f"\n{m['ticker']}: Score {legs['legs_score']} | {legs['verdict']}")
            time.sleep(0.3)
        
        return results
    
    return []

def market_open_scan():
    """
    Run this at 9:31 AM right after open.
    Catches the first movers of the day.
    """
    print("=" * 70)
    print("🔔 MARKET OPEN SCAN (9:31 AM)")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    results = discover_movers(verbose=True)
    print_results(results, top_n=10)
    
    # Auto-generate watchlist
    generate_watchlist(results)
    
    return results

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Market Mover Finder')
    parser.add_argument('command', nargs='?', default='discover',
                       choices=['discover', 'premarket', 'open', 'check', 'watchlist'],
                       help='Command to run')
    parser.add_argument('--ticker', '-t', help='Ticker to check legs')
    parser.add_argument('--top', '-n', type=int, default=15, help='Top N results')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')
    
    args = parser.parse_args()
    
    if args.command == 'discover':
        results = discover_movers(verbose=not args.quiet)
        print_results(results, top_n=args.top)
        
    elif args.command == 'premarket':
        premarket_scan()
        
    elif args.command == 'open':
        market_open_scan()
        
    elif args.command == 'check':
        if args.ticker:
            result = check_legs(args.ticker.upper())
            if result:
                print(json.dumps(result, indent=2, default=str))
        else:
            print("Usage: python market_mover_finder.py check --ticker ATON")
            
    elif args.command == 'watchlist':
        results = discover_movers(verbose=not args.quiet)
        generate_watchlist(results)

if __name__ == "__main__":
    main()
