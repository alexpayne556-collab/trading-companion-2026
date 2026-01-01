#!/usr/bin/env python3
"""
🐺 INSIDER CLUSTER HUNTER
Wolf Pack Intelligence System - Layer 1

Scrapes OpenInsider for cluster buying signals
Finds stocks where MULTIPLE insiders are buying

NO API KEY NEEDED - 100% FREE

Usage:
    python3 insider_cluster_hunter.py
    python3 insider_cluster_hunter.py --validate SMR SOUN BBAI  # Check specific tickers
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import argparse
import time
import re

# Configuration
PRICE_MIN = 2.0
PRICE_MAX = 50.0  # Wider range to catch more signals
MIN_TRANSACTION_VALUE = 10000  # Minimum $10K transaction
LOOKBACK_DAYS = 30  # Look back 30 days for clusters

# OpenInsider URLs
CLUSTER_BUYING_URL = "http://openinsider.com/screener?s=&o=&pl={}&ph={}&ll=&lh=&fd=30&fdr=&td=0&tdr=&fdlyl=&fdlyh=&dtefrom=&dteto=&xp=1&vl=10&vh=&ocl=&och=&session=&sort=filing_date&sortOrder=desc&xa=1&xb=1&xc=1&xd=1"
LATEST_BUYS_URL = "http://openinsider.com/screener?s=&o=&pl={}&ph={}&ll=&lh=&fd=7&fdr=&td=0&tdr=&fdlyl=&fdlyh=&dtefrom=&dteto=&xp=1&vl=10&vh=&ocl=&och=&sion=A&stype=P&sort=filing_date&sortOrder=desc"
TICKER_LOOKUP_URL = "http://openinsider.com/search?q={}"

# Headers to look like a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def fetch_page(url, max_retries=3):
    """Fetch a page with retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                print(f"  Retry {attempt + 1}/{max_retries}...")
                time.sleep(2)
            else:
                print(f"  Error fetching page: {e}")
                return None
    return None


def parse_insider_table(html):
    """Parse the insider trading table from OpenInsider"""
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': 'tinytable'})
    
    if not table:
        return []
    
    trades = []
    rows = table.find_all('tr')[1:]  # Skip header row
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 12:
            continue
        
        try:
            # Extract data from columns
            filing_date = cols[1].get_text(strip=True)
            trade_date = cols[2].get_text(strip=True)
            ticker_elem = cols[3].find('a')
            ticker = ticker_elem.get_text(strip=True) if ticker_elem else cols[3].get_text(strip=True)
            company = cols[4].get_text(strip=True)
            insider_name = cols[5].get_text(strip=True)
            title = cols[6].get_text(strip=True)
            trade_type = cols[7].get_text(strip=True)
            price_text = cols[8].get_text(strip=True).replace('$', '').replace(',', '')
            qty_text = cols[9].get_text(strip=True).replace(',', '').replace('+', '')
            owned_text = cols[10].get_text(strip=True).replace(',', '')
            value_text = cols[12].get_text(strip=True).replace('$', '').replace(',', '').replace('+', '')
            
            # Parse numeric values
            try:
                price = float(price_text) if price_text else 0
            except:
                price = 0
                
            try:
                qty = int(qty_text) if qty_text else 0
            except:
                qty = 0
                
            try:
                value = int(value_text) if value_text else 0
            except:
                value = 0
            
            # Only include purchases (P = Purchase)
            if 'P' in trade_type and price > 0:
                trades.append({
                    'filing_date': filing_date,
                    'trade_date': trade_date,
                    'ticker': ticker.upper(),
                    'company': company,
                    'insider': insider_name,
                    'title': title,
                    'price': price,
                    'qty': qty,
                    'value': value,
                    'trade_type': trade_type
                })
                
        except Exception as e:
            continue
    
    return trades


def get_cluster_buying():
    """Get stocks with cluster insider buying"""
    print("\n🔍 Scanning OpenInsider for cluster buying...")
    print(f"   Price range: ${PRICE_MIN} - ${PRICE_MAX}")
    print(f"   Lookback: {LOOKBACK_DAYS} days")
    print(f"   Min transaction: ${MIN_TRANSACTION_VALUE:,}")
    
    url = CLUSTER_BUYING_URL.format(PRICE_MIN, PRICE_MAX)
    html = fetch_page(url)
    
    if not html:
        print("   ❌ Failed to fetch cluster buying data")
        return []
    
    trades = parse_insider_table(html)
    print(f"   Found {len(trades)} insider purchases")
    
    # Filter by minimum value
    trades = [t for t in trades if t['value'] >= MIN_TRANSACTION_VALUE]
    print(f"   After value filter: {len(trades)} trades")
    
    return trades


def get_latest_buys():
    """Get latest insider buys (last 7 days)"""
    print("\n🔍 Scanning latest insider buys (7 days)...")
    
    url = LATEST_BUYS_URL.format(PRICE_MIN, PRICE_MAX)
    html = fetch_page(url)
    
    if not html:
        return []
    
    trades = parse_insider_table(html)
    trades = [t for t in trades if t['value'] >= MIN_TRANSACTION_VALUE]
    
    return trades


def get_ticker_insider_history(ticker):
    """Get insider trading history for a specific ticker"""
    print(f"\n🔍 Looking up insider history for {ticker}...")
    
    url = TICKER_LOOKUP_URL.format(ticker)
    html = fetch_page(url)
    
    if not html:
        return []
    
    trades = parse_insider_table(html)
    
    # Filter for buys only
    buys = [t for t in trades if 'P' in t.get('trade_type', '')]
    
    return buys


def analyze_clusters(trades):
    """Analyze trades to find cluster buying patterns"""
    if not trades:
        return {}
    
    # Group by ticker
    ticker_trades = {}
    for trade in trades:
        ticker = trade['ticker']
        if ticker not in ticker_trades:
            ticker_trades[ticker] = []
        ticker_trades[ticker].append(trade)
    
    # Analyze each ticker
    clusters = {}
    for ticker, ticker_trade_list in ticker_trades.items():
        unique_insiders = set(t['insider'] for t in ticker_trade_list)
        total_value = sum(t['value'] for t in ticker_trade_list)
        
        # Get title breakdown
        titles = {}
        for t in ticker_trade_list:
            title = t['title']
            if title not in titles:
                titles[title] = 0
            titles[title] += t['value']
        
        # Check for C-suite buying
        c_suite_buying = any(
            any(role in t['title'].upper() for role in ['CEO', 'CFO', 'COO', 'PRESIDENT', 'CHAIRMAN'])
            for t in ticker_trade_list
        )
        
        # Check for 10% owner
        ten_pct_owner = any('10%' in t['title'] for t in ticker_trade_list)
        
        # Calculate score
        score = 0
        score += min(len(unique_insiders) * 20, 60)  # Up to 60 points for multiple insiders
        score += 20 if c_suite_buying else 0
        score += 20 if ten_pct_owner else 0
        
        # Bonus for large total value
        if total_value >= 1000000:
            score += 20
        elif total_value >= 500000:
            score += 15
        elif total_value >= 100000:
            score += 10
        
        clusters[ticker] = {
            'ticker': ticker,
            'company': ticker_trade_list[0]['company'],
            'num_insiders': len(unique_insiders),
            'num_trades': len(ticker_trade_list),
            'total_value': total_value,
            'avg_price': sum(t['price'] for t in ticker_trade_list) / len(ticker_trade_list),
            'insiders': list(unique_insiders),
            'titles': titles,
            'c_suite': c_suite_buying,
            'ten_pct_owner': ten_pct_owner,
            'score': min(score, 100),
            'trades': ticker_trade_list
        }
    
    return clusters


def validate_tickers(tickers):
    """Validate specific tickers for insider buying"""
    print("\n" + "=" * 70)
    print("🎯 VALIDATING SPECIFIC TICKERS FOR INSIDER BUYING")
    print("=" * 70)
    
    results = {}
    
    for ticker in tickers:
        ticker = ticker.upper()
        trades = get_ticker_insider_history(ticker)
        
        if not trades:
            print(f"\n❌ {ticker}: NO INSIDER BUYING FOUND")
            results[ticker] = {
                'validated': False,
                'reason': 'No insider purchases found',
                'trades': []
            }
            continue
        
        # Filter for recent trades (last 90 days)
        recent_trades = []
        cutoff = datetime.now() - timedelta(days=90)
        
        for trade in trades:
            try:
                # Try to parse the date
                trade_date_str = trade['trade_date']
                trade_date = datetime.strptime(trade_date_str, '%Y-%m-%d')
                if trade_date >= cutoff:
                    recent_trades.append(trade)
            except:
                # Include if we can't parse date
                recent_trades.append(trade)
        
        if not recent_trades:
            print(f"\n⚠️  {ticker}: No RECENT insider buying (90 days)")
            results[ticker] = {
                'validated': False,
                'reason': 'No recent insider purchases (90 days)',
                'trades': trades[:5]  # Show last 5 historical trades
            }
            continue
        
        # Analyze the recent trades
        unique_insiders = set(t['insider'] for t in recent_trades)
        total_value = sum(t['value'] for t in recent_trades)
        c_suite = any(
            any(role in t['title'].upper() for role in ['CEO', 'CFO', 'COO', 'PRESIDENT', 'CHAIRMAN'])
            for t in recent_trades
        )
        
        print(f"\n✅ {ticker}: INSIDER BUYING DETECTED")
        print(f"   Insiders: {len(unique_insiders)}")
        print(f"   Total Value: ${total_value:,}")
        print(f"   C-Suite Buying: {'YES 🔥' if c_suite else 'No'}")
        
        for trade in recent_trades[:5]:
            print(f"   - {trade['trade_date']}: {trade['insider'][:30]} ({trade['title'][:20]}) ${trade['value']:,}")
        
        results[ticker] = {
            'validated': True,
            'num_insiders': len(unique_insiders),
            'total_value': total_value,
            'c_suite': c_suite,
            'trades': recent_trades
        }
        
        time.sleep(1)  # Be nice to the server
    
    return results


def print_cluster_report(clusters):
    """Print formatted cluster buying report"""
    if not clusters:
        print("\n⚠️  No cluster buying found matching criteria")
        return
    
    # Sort by score
    sorted_clusters = sorted(clusters.values(), key=lambda x: x['score'], reverse=True)
    
    print("\n" + "=" * 70)
    print("🐺 INSIDER CLUSTER BUYING REPORT")
    print(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    # Top opportunities (multiple insiders OR high value)
    top_ops = [c for c in sorted_clusters if c['num_insiders'] >= 2 or c['total_value'] >= 500000]
    
    if top_ops:
        print("\n🔥 HIGH CONVICTION (Multiple Insiders or >$500K)")
        print("-" * 70)
        
        for cluster in top_ops[:10]:
            flags = []
            if cluster['c_suite']:
                flags.append("C-SUITE")
            if cluster['ten_pct_owner']:
                flags.append("10% OWNER")
            if cluster['num_insiders'] >= 3:
                flags.append("CLUSTER")
            
            flag_str = " | ".join(flags) if flags else ""
            
            print(f"\n{cluster['ticker']} - {cluster['company'][:40]}")
            print(f"   Score: {cluster['score']}/100 {flag_str}")
            print(f"   Insiders Buying: {cluster['num_insiders']}")
            print(f"   Total Value: ${cluster['total_value']:,}")
            print(f"   Avg Price: ${cluster['avg_price']:.2f}")
            print(f"   Names: {', '.join(cluster['insiders'][:3])}")
    
    # All opportunities
    print("\n" + "-" * 70)
    print("📊 ALL INSIDER BUYING (Last 30 Days)")
    print("-" * 70)
    
    print(f"\n{'Ticker':<8} {'Score':<6} {'Insiders':<10} {'Total $':<12} {'Avg Price':<10} {'C-Suite':<8}")
    print("-" * 70)
    
    for cluster in sorted_clusters[:30]:
        c_suite_flag = "✓" if cluster['c_suite'] else ""
        print(f"{cluster['ticker']:<8} {cluster['score']:<6} {cluster['num_insiders']:<10} ${cluster['total_value']:>10,} ${cluster['avg_price']:>8.2f} {c_suite_flag:<8}")


def print_validation_summary(results, wounded_prey_tickers=None):
    """Print validation summary"""
    print("\n" + "=" * 70)
    print("🎯 INSIDER VALIDATION SUMMARY")
    print("=" * 70)
    
    validated = {k: v for k, v in results.items() if v['validated']}
    not_validated = {k: v for k, v in results.items() if not v['validated']}
    
    if validated:
        print("\n✅ VALIDATED (Insider Buying Detected):")
        for ticker, data in validated.items():
            c_suite = "🔥 C-SUITE" if data.get('c_suite') else ""
            print(f"   {ticker}: {data['num_insiders']} insiders, ${data['total_value']:,} {c_suite}")
    
    if not_validated:
        print("\n❌ NOT VALIDATED (No Recent Insider Buying):")
        for ticker, data in not_validated.items():
            print(f"   {ticker}: {data['reason']}")
    
    # Cross-reference with wounded prey if provided
    if wounded_prey_tickers:
        print("\n" + "-" * 70)
        print("🎯 WOUNDED PREY + INSIDER VALIDATION")
        print("-" * 70)
        
        both = set(wounded_prey_tickers) & set(validated.keys())
        wounded_only = set(wounded_prey_tickers) - set(validated.keys())
        
        if both:
            print("\n🔥 HIGH CONVICTION (Wounded Prey + Insider Buying):")
            for ticker in both:
                print(f"   {ticker} ← TRADE THIS")
        
        if wounded_only:
            print("\n⚠️  WOUNDED PREY WITHOUT INSIDER VALIDATION:")
            for ticker in wounded_only:
                print(f"   {ticker} ← Higher risk, no insider confirmation")


def main():
    parser = argparse.ArgumentParser(description='🐺 Insider Cluster Hunter')
    parser.add_argument('--validate', nargs='+', help='Validate specific tickers')
    parser.add_argument('--wounded-prey', nargs='+', help='Cross-reference with wounded prey candidates')
    parser.add_argument('--scan', action='store_true', help='Run full cluster scan')
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("🐺 WOLF PACK INSIDER CLUSTER HUNTER")
    print("   \"Following the smart money\"")
    print("=" * 70)
    
    if args.validate:
        # Validate specific tickers
        results = validate_tickers(args.validate)
        print_validation_summary(results, args.wounded_prey)
        
    elif args.scan or not args.validate:
        # Run full cluster scan
        trades = get_cluster_buying()
        
        if trades:
            clusters = analyze_clusters(trades)
            print_cluster_report(clusters)
            
            # If wounded prey provided, cross-reference
            if args.wounded_prey:
                print("\n" + "-" * 70)
                validated_tickers = [t for t, c in clusters.items() if c['num_insiders'] >= 1]
                print_validation_summary(
                    {t: {'validated': t in clusters, 'num_insiders': clusters.get(t, {}).get('num_insiders', 0)} 
                     for t in args.wounded_prey},
                    args.wounded_prey
                )
    
    print("\n" + "=" * 70)
    print("🐺 AWOOOO - Hunt complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
