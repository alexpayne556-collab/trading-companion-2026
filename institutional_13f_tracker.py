#!/usr/bin/env python3
"""
🐺 INSTITUTIONAL 13F TRACKER - Who's buying/selling

Tracks institutional ownership changes from 13F filings.
Shows smart money flows.

Author: Brokkr
Date: January 2, 2026
"""

import requests
import pandas as pd
from datetime import datetime
import json

def get_institutional_holders(ticker):
    """Get institutional holders from Yahoo Finance."""
    try:
        url = f"https://finance.yahoo.com/quote/{ticker}/holders"
        
        # Use yfinance instead for reliability
        import yfinance as yf
        stock = yf.Ticker(ticker)
        
        holders = stock.institutional_holders
        
        if holders is None or holders.empty:
            return []
        
        # Convert to list of dicts
        results = []
        for idx, row in holders.iterrows():
            results.append({
                'holder': row['Holder'],
                'shares': row['Shares'],
                'date_reported': row['Date Reported'],
                'pct_out': row['% Out'],
                'value': row.get('Value', 0)
            })
        
        return results
        
    except Exception as e:
        print(f"   ❌ Failed to get institutional data for {ticker}: {e}")
        return []

def analyze_institutional_flow(ticker):
    """Analyze if institutions are buying or selling."""
    holders = get_institutional_holders(ticker)
    
    if not holders:
        return {
            'ticker': ticker,
            'status': 'NO_DATA',
            'top_holders': [],
            'analysis': 'No institutional data available'
        }
    
    # Get top 5 holders
    top_5 = holders[:5]
    
    # Simple analysis
    total_shares = sum([h['shares'] for h in holders])
    total_pct = sum([h['pct_out'] for h in holders])
    
    analysis = {
        'ticker': ticker,
        'status': 'TRACKED',
        'total_holders': len(holders),
        'top_holders': [
            {
                'name': h['holder'],
                'shares': f"{h['shares']:,}",
                'pct': f"{h['pct_out']:.2f}%",
                'date': h['date_reported']
            }
            for h in top_5
        ],
        'total_institutional_pct': f"{total_pct:.1f}%",
        'concentration': 'HIGH' if top_5[0]['pct_out'] > 10 else 'DISTRIBUTED',
        'analysis': f"{len(holders)} institutions hold {total_pct:.1f}% of float"
    }
    
    return analysis

def scan_watchlist_institutions(watchlist):
    """Scan entire watchlist for institutional activity."""
    print("🏦 INSTITUTIONAL 13F TRACKER")
    print("=" * 70)
    
    results = []
    
    for ticker in watchlist:
        print(f"\n📊 Analyzing {ticker}...")
        data = analyze_institutional_flow(ticker)
        results.append(data)
        
        if data['status'] == 'TRACKED':
            print(f"   ✅ {data['total_holders']} institutions, {data['total_institutional_pct']} of float")
            print(f"   Top holder: {data['top_holders'][0]['name']} ({data['top_holders'][0]['pct']})")
        else:
            print(f"   ⚠️  No data available")
    
    return results

def main():
    """Main execution."""
    import yaml
    
    # Load watchlist from config
    try:
        with open('wolf_den_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        watchlist = [config['watchlist']['primary']] + config['watchlist']['backup'] + config['watchlist']['positions']
    except:
        # Fallback watchlist
        watchlist = ['AISP', 'SOUN', 'LUNR', 'BBAI', 'SMR']
    
    print(f"🐺 Scanning {len(watchlist)} tickers for institutional activity...\n")
    
    results = scan_watchlist_institutions(watchlist)
    
    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'watchlist': watchlist,
        'results': results
    }
    
    with open('logs/institutional_13f_latest.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Results saved to logs/institutional_13f_latest.json")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
