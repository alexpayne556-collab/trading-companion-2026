#!/usr/bin/env python3
"""
🐺 INSIDER BUYING SCANNER
==========================
Tracks insider buying across the AI fuel chain
Identifies clusters of insider activity

Uses SEC EDGAR Form 4 filings

Usage:
    python insider_buying_scanner.py                 # Scan all tickers
    python insider_buying_scanner.py --ticker UUUU  # Single ticker
    python insider_buying_scanner.py --days 30      # Last 30 days only
"""

import requests
import json
from datetime import datetime, timedelta
import pytz
import argparse
import time
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# UNIVERSE FOR INSIDER TRACKING
# ============================================================

INSIDER_UNIVERSE = {
    'NUCLEAR': ['UUUU', 'SMR', 'LEU', 'OKLO', 'CCJ', 'DNN', 'UEC', 'NXE', 'NNE'],
    'COOLING': ['VRT', 'MOD', 'NVT'],
    'PHOTONICS': ['LITE', 'AAOI', 'COHR'],
    'NETWORKING': ['ANET', 'CRDO', 'FN'],
    'STORAGE': ['MU', 'WDC', 'STX'],
    'CHIPS': ['AMD', 'MRVL', 'AVGO', 'AMKR'],
    'DC_BUILDERS': ['SMCI', 'EME', 'CLS'],
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'ASTS', 'SIDU', 'BKSY'],
    'AI_SOFTWARE': ['PLTR', 'AI', 'SOUN', 'PATH', 'UPST']
}

# SEC EDGAR API headers
HEADERS = {
    'User-Agent': 'TradingCompanion/1.0 (trading.research@example.com)',
    'Accept': 'application/json'
}

# ============================================================
# SEC EDGAR FUNCTIONS
# ============================================================

def get_cik_from_ticker(ticker):
    """Get CIK number from ticker using SEC ticker-to-CIK mapping"""
    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for item in data.values():
                if item.get('ticker', '').upper() == ticker.upper():
                    # CIK needs to be padded to 10 digits
                    cik = str(item['cik_str']).zfill(10)
                    return cik
        return None
    except Exception as e:
        return None

def get_insider_filings(cik, ticker, days=90):
    """Get Form 4 filings from SEC EDGAR"""
    try:
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        filings = data.get('filings', {}).get('recent', {})
        
        if not filings:
            return []
        
        # Filter for Form 4s
        form_4_indices = []
        forms = filings.get('form', [])
        dates = filings.get('filingDate', [])
        
        cutoff = datetime.now() - timedelta(days=days)
        
        for i, form in enumerate(forms):
            if form == '4':
                try:
                    filing_date = datetime.strptime(dates[i], '%Y-%m-%d')
                    if filing_date >= cutoff:
                        form_4_indices.append({
                            'date': dates[i],
                            'accession': filings.get('accessionNumber', [])[i] if i < len(filings.get('accessionNumber', [])) else None
                        })
                except:
                    pass
        
        return form_4_indices
        
    except Exception as e:
        return []

def analyze_insider_activity(ticker, days=90):
    """Analyze insider activity for a ticker"""
    print(f"   Checking {ticker}...", end='\r')
    
    cik = get_cik_from_ticker(ticker)
    if not cik:
        return {'ticker': ticker, 'error': 'CIK not found', 'filings': []}
    
    filings = get_insider_filings(cik, ticker, days)
    
    # Count recent filings
    last_30d = len([f for f in filings if (datetime.now() - datetime.strptime(f['date'], '%Y-%m-%d')).days <= 30])
    last_60d = len([f for f in filings if (datetime.now() - datetime.strptime(f['date'], '%Y-%m-%d')).days <= 60])
    
    # Cluster detection
    is_cluster = last_30d >= 3  # 3+ filings in 30 days = cluster
    
    return {
        'ticker': ticker,
        'cik': cik,
        'total_filings': len(filings),
        'last_30d': last_30d,
        'last_60d': last_60d,
        'is_cluster': is_cluster,
        'filings': filings[:10]  # Keep last 10
    }

def scan_all_insiders(days=90):
    """Scan all tickers for insider activity"""
    print(f"\n⚡ SCANNING INSIDER ACTIVITY (Last {days} days)...")
    
    results = []
    
    for sector, tickers in INSIDER_UNIVERSE.items():
        for ticker in tickers:
            data = analyze_insider_activity(ticker, days)
            data['sector'] = sector
            results.append(data)
            time.sleep(0.2)  # Rate limit
    
    print(f"\n   ✓ Scanned {len(results)} tickers")
    
    return results

def get_eastern_time():
    eastern = pytz.timezone('US/Eastern')
    return datetime.now(eastern)

def display_insider_report(results, days):
    """Display insider activity report"""
    et_now = get_eastern_time()
    
    print("\n" + "=" * 90)
    print(f"🐺 INSIDER BUYING SCANNER — {et_now.strftime('%I:%M %p ET')}")
    print(f"   Showing Form 4 filings from last {days} days")
    print("=" * 90)
    
    # Sort by filing count
    results_sorted = sorted(results, key=lambda x: x.get('total_filings', 0), reverse=True)
    
    # Cluster alerts first
    clusters = [r for r in results_sorted if r.get('is_cluster')]
    
    if clusters:
        print("\n🔥 CLUSTER ALERTS (3+ filings in 30 days)")
        print("-" * 60)
        for r in clusters:
            print(f"   🚨 {r['ticker']} ({r['sector']}): {r['last_30d']} filings in 30 days!")
    
    # Full table
    print(f"\n📊 INSIDER ACTIVITY SUMMARY\n")
    print(f"{'TICKER':<8} | {'SECTOR':<12} | {'TOTAL':>8} | {'30-DAY':>8} | {'60-DAY':>8} | {'STATUS':<15}")
    print("-" * 75)
    
    for r in results_sorted:
        if r.get('error'):
            print(f"{r['ticker']:<8} | {'N/A':<12} | {'—':>8} | {'—':>8} | {'—':>8} | No data")
            continue
        
        status = ""
        if r.get('is_cluster'):
            status = "🔥 CLUSTER"
        elif r['total_filings'] >= 5:
            status = "📈 Active"
        elif r['total_filings'] >= 1:
            status = "➖ Some"
        else:
            status = "❄️ None"
        
        print(f"{r['ticker']:<8} | {r['sector']:<12} | {r['total_filings']:>8} | {r['last_30d']:>8} | {r['last_60d']:>8} | {status}")
    
    # Recent filings detail
    print("\n" + "=" * 90)
    print("📝 RECENT FORM 4 FILINGS")
    print("=" * 90)
    
    all_filings = []
    for r in results_sorted:
        for f in r.get('filings', []):
            all_filings.append({
                'ticker': r['ticker'],
                'sector': r['sector'],
                'date': f['date']
            })
    
    # Sort by date
    all_filings_sorted = sorted(all_filings, key=lambda x: x['date'], reverse=True)
    
    print(f"\n{'DATE':<12} | {'TICKER':<8} | {'SECTOR':<15}")
    print("-" * 40)
    
    for f in all_filings_sorted[:25]:  # Last 25
        print(f"{f['date']:<12} | {f['ticker']:<8} | {f['sector']}")
    
    # Wolf's read
    print("\n" + "=" * 90)
    print("🐺 WOLF'S INSIDER READ")
    print("=" * 90)
    
    active_sectors = {}
    for r in results_sorted:
        if r.get('total_filings', 0) >= 1:
            sector = r['sector']
            if sector not in active_sectors:
                active_sectors[sector] = 0
            active_sectors[sector] += r['total_filings']
    
    if active_sectors:
        sector_sorted = sorted(active_sectors.items(), key=lambda x: x[1], reverse=True)
        print("\n📊 INSIDER ACTIVITY BY SECTOR:")
        for sector, count in sector_sorted[:5]:
            print(f"   {sector}: {count} total filings")
    
    if clusters:
        print("\n🎯 CLUSTER ANALYSIS:")
        print("   Multiple insiders buying = they know something")
        print("   Clusters detected in:")
        for c in clusters:
            print(f"   → {c['ticker']} — WATCH THIS ONE")

def main():
    parser = argparse.ArgumentParser(description='Insider Buying Scanner')
    parser.add_argument('--ticker', type=str, help='Scan single ticker')
    parser.add_argument('--days', type=int, default=90, help='Days to scan (default: 90)')
    
    args = parser.parse_args()
    
    if args.ticker:
        result = analyze_insider_activity(args.ticker.upper(), args.days)
        result['sector'] = 'MANUAL'
        display_insider_report([result], args.days)
    else:
        results = scan_all_insiders(args.days)
        display_insider_report(results, args.days)

if __name__ == "__main__":
    main()
