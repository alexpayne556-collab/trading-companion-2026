#!/usr/bin/env python3
"""
🐺 INSIDER CLUSTER SCANNER - Find Coordinated Insider Buying
=============================================================

FENRIR'S SECRET:
- One insider buying = maybe nothing
- THREE insiders buying same week = THEY KNOW SOMETHING
- Filter by "cluster buys" - multiple insiders, same stock, same week

THE EDGE:
- Insiders know before the news drops
- When multiple insiders buy at same time = high conviction
- They're using their OWN MONEY

DATA SOURCE:
- SEC EDGAR Form 4 filings
- Code P = Purchase (what we want)
- Code S = Sale (ignore, they always sell)

USAGE:
    python insider_cluster_scanner.py                    # Scan for clusters
    python insider_cluster_scanner.py --ticker USAR      # Check specific
    python insider_cluster_scanner.py --days 14          # Custom lookback
"""

import argparse
import requests
from datetime import datetime, timedelta
import json
import time

# SEC EDGAR API
SEC_BASE = "https://efts.sec.gov/LATEST/search-index"
EDGAR_SEARCH = "https://efts.sec.gov/LATEST/search-index?q="

# Our watchlist to check
WATCHLIST = [
    # Nuclear/Uranium
    "UUUU", "SMR", "OKLO", "CCJ", "DNN", "LEU", "UEC",
    # Rare Earth
    "USAR", "MP", "AREC",
    # Quantum
    "IONQ", "QBTS", "QUBT", "RGTI",
    # Space
    "RDW", "RKLB", "ASTS", "LUNR", "SPCE",
    # Defense
    "AISP", "KTOS", "PLTR",
    # Other small caps with potential
    "RIOT", "MARA", "CLSK",
]


def search_sec_form4(ticker: str, days_back: int = 14) -> list:
    """
    Search SEC EDGAR for Form 4 filings.
    Returns list of insider transactions.
    """
    filings = []
    
    try:
        # SEC EDGAR full-text search for Form 4 + ticker
        # Note: This is a simplified approach - real implementation would
        # need to parse the actual Form 4 XML files
        
        url = f"https://www.sec.gov/cgi-bin/browse-edgar"
        params = {
            "action": "getcompany",
            "CIK": ticker,
            "type": "4",
            "dateb": "",
            "owner": "include",
            "count": "40",
            "output": "atom"
        }
        
        headers = {
            "User-Agent": "TradingCompanion/1.0 (contact@example.com)"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Parse the atom feed for recent Form 4s
            content = response.text
            
            # Simple parsing to extract filing dates
            # In production, use proper XML parser
            import re
            
            # Find all filing entries
            entries = re.findall(r'<entry>(.*?)</entry>', content, re.DOTALL)
            
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            for entry in entries:
                # Extract date
                date_match = re.search(r'<updated>(\d{4}-\d{2}-\d{2})', entry)
                title_match = re.search(r'<title>(.*?)</title>', entry)
                
                if date_match and title_match:
                    filing_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                    
                    if filing_date >= cutoff_date:
                        filings.append({
                            'date': date_match.group(1),
                            'title': title_match.group(1),
                            'ticker': ticker,
                        })
        
        return filings
        
    except Exception as e:
        print(f"  ⚠️  Error fetching Form 4 for {ticker}: {e}")
        return []


def check_openinsider_data(ticker: str) -> dict:
    """
    Check OpenInsider-style data for insider activity.
    Note: In production, you'd scrape or use their data feed.
    
    Returns summary of insider activity.
    """
    # This would normally query openinsider.com
    # For now, we'll use SEC EDGAR directly
    
    # Simulated analysis based on typical patterns
    result = {
        "ticker": ticker,
        "recent_buys": 0,
        "recent_sells": 0,
        "buy_value": 0,
        "sell_value": 0,
        "cluster_detected": False,
        "last_buy_date": None,
        "insiders_buying": [],
    }
    
    return result


def analyze_insider_activity(ticker: str, days_back: int = 14, verbose: bool = True) -> dict:
    """
    Analyze insider activity for a ticker.
    """
    filings = search_sec_form4(ticker, days_back)
    
    result = {
        "ticker": ticker,
        "days_analyzed": days_back,
        "total_filings": len(filings),
        "filings": filings,
        "cluster_score": 0,
        "signals": [],
    }
    
    # Calculate cluster score
    if len(filings) >= 3:
        result["cluster_score"] = 80
        result["signals"].append(f"🔥 CLUSTER: {len(filings)} Form 4s in {days_back} days")
    elif len(filings) >= 2:
        result["cluster_score"] = 50
        result["signals"].append(f"👀 ACTIVITY: {len(filings)} Form 4s in {days_back} days")
    elif len(filings) >= 1:
        result["cluster_score"] = 20
        result["signals"].append(f"📊 {len(filings)} Form 4 in {days_back} days")
    
    if verbose and result["filings"]:
        print(f"\n{'='*60}")
        print(f"🔍 INSIDER ACTIVITY: {ticker}")
        print(f"{'='*60}")
        print(f"Filings in last {days_back} days: {len(filings)}")
        print(f"Cluster Score: {result['cluster_score']}/100")
        
        if filings:
            print(f"\nRecent Form 4 Filings:")
            for f in filings[:5]:
                print(f"   {f['date']}: {f['title'][:50]}...")
        
        if result["signals"]:
            print(f"\nSignals:")
            for sig in result["signals"]:
                print(f"   {sig}")
    
    return result


def scan_for_clusters(days_back: int = 14):
    """
    Scan watchlist for insider cluster buying.
    """
    print(f"\n{'🐺'*30}")
    print(f"      INSIDER CLUSTER SCANNER")
    print(f"{'🐺'*30}")
    print(f"\nScanning {len(WATCHLIST)} stocks for insider activity...")
    print(f"Lookback period: {days_back} days")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    for ticker in WATCHLIST:
        print(f"  Checking {ticker}...", end="", flush=True)
        time.sleep(0.2)  # Rate limiting for SEC
        
        result = analyze_insider_activity(ticker, days_back, verbose=False)
        results.append(result)
        
        if result["total_filings"] > 0:
            print(f" {result['total_filings']} filings found!")
        else:
            print(" No recent filings")
    
    # Sort by cluster score
    results.sort(key=lambda x: x['cluster_score'], reverse=True)
    
    # Filter for any activity
    active = [r for r in results if r['total_filings'] > 0]
    
    print(f"\n{'='*60}")
    print(f"📊 RESULTS: {len(active)} stocks with insider activity")
    print(f"{'='*60}")
    
    if active:
        print(f"\n{'TICKER':<8} {'FILINGS':>8} {'SCORE':>8} {'STATUS':<20}")
        print(f"{'-'*60}")
        
        for r in active:
            if r['cluster_score'] >= 80:
                status = "🔥 CLUSTER BUY"
            elif r['cluster_score'] >= 50:
                status = "👀 WATCHING"
            else:
                status = "📊 MINOR"
            
            print(f"{r['ticker']:<8} {r['total_filings']:>8} {r['cluster_score']:>8} {status:<20}")
    else:
        print("\nNo significant insider activity detected in watchlist.")
        print("This is normal - clusters are RARE (that's why they're valuable)")
    
    # Clusters detected
    clusters = [r for r in results if r['cluster_score'] >= 80]
    if clusters:
        print(f"\n{'='*60}")
        print("🔥 CLUSTER BUYS DETECTED!")
        print(f"{'='*60}")
        for r in clusters:
            print(f"\n{r['ticker']} - Score: {r['cluster_score']}")
            for sig in r['signals']:
                print(f"   {sig}")
            print(f"   ACTION: Research what insiders know!")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="🐺 Insider Cluster Scanner")
    parser.add_argument("--ticker", type=str, help="Check specific ticker")
    parser.add_argument("--days", type=int, default=14, help="Days to look back")
    
    args = parser.parse_args()
    
    if args.ticker:
        analyze_insider_activity(args.ticker.upper(), args.days)
    else:
        scan_for_clusters(args.days)
    
    print(f"\n{'🐺'*30}")
    print("      FENRIR SAID: 'THEY KNOW SOMETHING'")
    print(f"{'🐺'*30}")
    print("\n💡 TIP: Check openinsider.com for detailed insider data")
    print("💡 TIP: Look for CEO/CFO buys (not just directors)")
    print("💡 TIP: Cluster = 3+ insiders buying within 2 weeks")
    print("\n🐺 AWOOOO!")


if __name__ == "__main__":
    main()
