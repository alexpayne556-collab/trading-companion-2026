#!/usr/bin/env python3
"""
🐺 MARKET DISCOVERY - Find What's Actually Moving
Not 142 tickers. THE ENTIRE MARKET.

Scans for:
- Top % gainers (all day)
- Unusual volume (2x+ average)
- New 52-week highs
- Gap ups > 5%

Returns: Tickers we SHOULD be watching, not hardcoded list.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time
import sys
import os

# Add webapp to path for database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'webapp'))

try:
    from intelligence_db import log_scan, log_alert
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("⚠️  Database not available, running in discovery-only mode")


def get_sp500_tickers():
    """Get S&P 500 tickers as baseline universe"""
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    try:
        tables = pd.read_html(url)
        sp500 = tables[0]
        return sp500['Symbol'].str.replace('.', '-').tolist()
    except:
        return []


def get_nasdaq100_tickers():
    """Get NASDAQ 100 tickers"""
    url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
    try:
        tables = pd.read_html(url)
        nasdaq = tables[4]  # The constituents table
        return nasdaq['Ticker'].str.replace('.', '-').tolist()
    except:
        return []


def get_russell2000_sample():
    """
    Russell 2000 is huge, get a sample of high-volume small caps
    Using top liquid names that trade > 1M shares/day
    """
    # Sample of liquid small caps
    return ['SOUN', 'AISP', 'PTON', 'PLUG', 'CLOV', 'SOFI', 'HOOD', 'LCID', 
            'RIVN', 'XOS', 'MULN', 'NKLA', 'BYND', 'OPEN', 'WISH', 'BBBY',
            'COIN', 'MARA', 'RIOT', 'WULF', 'CLSK', 'BTBT', 'CIFR', 'IREN']


def build_discovery_universe():
    """
    Build extended universe: S&P 500 + NASDAQ 100 + liquid small caps
    ~700-800 tickers total (manageable for daily scans)
    """
    print("🔍 Building discovery universe...")
    
    sp500 = get_sp500_tickers()
    nasdaq = get_nasdaq100_tickers()
    smallcaps = get_russell2000_sample()
    
    # Combine and dedupe
    all_tickers = list(set(sp500 + nasdaq + smallcaps))
    
    print(f"✅ Universe: {len(all_tickers)} tickers")
    print(f"   - S&P 500: {len(sp500)}")
    print(f"   - NASDAQ 100: {len(nasdaq)}")
    print(f"   - Small caps: {len(smallcaps)}")
    
    return all_tickers


def scan_for_movers(universe, min_volume=100000, min_price=1.0):
    """
    Scan universe for unusual activity
    
    Returns dict with:
    - gainers: Top % gainers
    - volume_spikes: Unusual volume vs avg
    - new_highs: 52-week highs
    - gap_ups: Premarket/open gaps
    """
    
    print(f"\n🚀 Scanning {len(universe)} tickers for movers...")
    
    movers = {
        'gainers': [],
        'volume_spikes': [],
        'new_highs': [],
        'gap_ups': []
    }
    
    count = 0
    for ticker in universe:
        count += 1
        if count % 100 == 0:
            print(f"   Progress: {count}/{len(universe)} tickers...")
        
        try:
            stock = yf.Ticker(ticker)
            
            # Get today's data
            hist = stock.history(period='2d', interval='1d')
            if len(hist) < 2:
                continue
            
            today = hist.iloc[-1]
            yesterday = hist.iloc[-2]
            
            # Basic filters
            if today['Close'] < min_price:
                continue
            if today['Volume'] < min_volume:
                continue
            
            # Calculate metrics
            price_change = ((today['Close'] - yesterday['Close']) / yesterday['Close']) * 100
            
            # Get 20-day average volume for comparison
            hist_20d = stock.history(period='1mo', interval='1d')
            if len(hist_20d) >= 10:
                avg_volume = hist_20d['Volume'].mean()
                volume_spike = ((today['Volume'] - avg_volume) / avg_volume) * 100
            else:
                volume_spike = 0
            
            # Get 52-week high
            hist_1y = stock.history(period='1y', interval='1d')
            if len(hist_1y) > 0:
                high_52w = hist_1y['High'].max()
                near_high = (today['Close'] / high_52w) >= 0.98  # Within 2%
            else:
                near_high = False
            
            # Gap detection (open vs previous close)
            gap_pct = ((today['Open'] - yesterday['Close']) / yesterday['Close']) * 100
            
            # Categorize
            if price_change >= 5.0:
                movers['gainers'].append({
                    'ticker': ticker,
                    'change': price_change,
                    'volume': today['Volume'],
                    'volume_spike': volume_spike,
                    'price': today['Close']
                })
            
            if volume_spike >= 100:  # 2x average volume
                movers['volume_spikes'].append({
                    'ticker': ticker,
                    'volume_spike': volume_spike,
                    'change': price_change,
                    'volume': today['Volume'],
                    'price': today['Close']
                })
            
            if near_high and price_change >= 2.0:
                movers['new_highs'].append({
                    'ticker': ticker,
                    'change': price_change,
                    'price': today['Close'],
                    'high_52w': high_52w
                })
            
            if gap_pct >= 5.0:
                movers['gap_ups'].append({
                    'ticker': ticker,
                    'gap': gap_pct,
                    'change': price_change,
                    'price': today['Close']
                })
            
            # Log to database if significant move
            if DB_AVAILABLE and abs(price_change) >= 5.0:
                log_scan(ticker, today['Close'], today['Volume'], price_change, 'DISCOVERED')
                
                if abs(price_change) >= 10.0:
                    log_alert('DISCOVERED', ticker, 
                             f"Market Discovery: {ticker} {price_change:+.1f}%",
                             {'volume': int(today['Volume']), 'volume_spike': volume_spike})
            
            time.sleep(0.1)  # Rate limiting
            
        except Exception as e:
            continue
    
    # Sort results
    movers['gainers'].sort(key=lambda x: x['change'], reverse=True)
    movers['volume_spikes'].sort(key=lambda x: x['volume_spike'], reverse=True)
    movers['new_highs'].sort(key=lambda x: x['change'], reverse=True)
    movers['gap_ups'].sort(key=lambda x: x['gap'], reverse=True)
    
    return movers


def print_discovery_report(movers):
    """Print formatted discovery report"""
    
    print("\n" + "="*70)
    print("🎯 MARKET DISCOVERY REPORT")
    print("="*70)
    
    print(f"\n📈 TOP GAINERS (Top 20)")
    print("-" * 70)
    for i, m in enumerate(movers['gainers'][:20], 1):
        print(f"{i:2d}. {m['ticker']:6s} {m['change']:+7.2f}%  Vol: {m['volume']:>12,}  "
              f"VolSpike: {m['volume_spike']:+6.1f}%  ${m['price']:.2f}")
    
    print(f"\n💥 UNUSUAL VOLUME (Top 20)")
    print("-" * 70)
    for i, m in enumerate(movers['volume_spikes'][:20], 1):
        print(f"{i:2d}. {m['ticker']:6s} Vol +{m['volume_spike']:6.1f}%  "
              f"Price: {m['change']:+6.2f}%  Vol: {m['volume']:>12,}  ${m['price']:.2f}")
    
    print(f"\n🔥 NEW 52-WEEK HIGHS (Top 15)")
    print("-" * 70)
    for i, m in enumerate(movers['new_highs'][:15], 1):
        print(f"{i:2d}. {m['ticker']:6s} {m['change']:+7.2f}%  "
              f"Price: ${m['price']:.2f}  52W High: ${m['high_52w']:.2f}")
    
    print(f"\n⚡ GAP UPS >5% (Top 15)")
    print("-" * 70)
    for i, m in enumerate(movers['gap_ups'][:15], 1):
        print(f"{i:2d}. {m['ticker']:6s} Gap: {m['gap']:+6.2f}%  "
              f"Day Change: {m['change']:+6.2f}%  ${m['price']:.2f}")
    
    print("\n" + "="*70)


def export_dynamic_watchlist(movers, output_file='dynamic_watchlist.txt'):
    """
    Export discovered movers to a dynamic watchlist file
    This replaces the static universe.txt
    """
    
    # Combine all tickers from all categories (dedupe)
    all_movers = set()
    
    for m in movers['gainers'][:30]:
        all_movers.add(m['ticker'])
    for m in movers['volume_spikes'][:30]:
        all_movers.add(m['ticker'])
    for m in movers['new_highs'][:20]:
        all_movers.add(m['ticker'])
    for m in movers['gap_ups'][:20]:
        all_movers.add(m['ticker'])
    
    # Sort alphabetically
    sorted_movers = sorted(list(all_movers))
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(f"# DYNAMIC WATCHLIST - Generated {datetime.now()}\n")
        f.write(f"# Found {len(sorted_movers)} tickers with unusual activity\n\n")
        
        for ticker in sorted_movers:
            f.write(f"{ticker}\n")
    
    print(f"\n✅ Exported {len(sorted_movers)} tickers to {output_file}")
    return sorted_movers


def main():
    """Run market discovery scan"""
    
    print("🐺 MARKET DISCOVERY - Finding What's Actually Moving\n")
    
    # Build extended universe
    universe = build_discovery_universe()
    
    # Scan for movers
    movers = scan_for_movers(universe)
    
    # Print report
    print_discovery_report(movers)
    
    # Export dynamic watchlist
    export_dynamic_watchlist(movers)
    
    print("\n🎯 Discovery complete. These are the tickers that are ACTUALLY moving.")
    print("   Not our hardcoded 142. Real market movers TODAY.")


if __name__ == "__main__":
    main()
