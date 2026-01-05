#!/usr/bin/env python3
"""
FORM 4 CONVICTION SCANNER - Real Insider Buying Only

Filters SEC Form 4 filings for Transaction Code "P" (Open Market Purchase).
Skips all the bullshit: stock awards, compensation, tax withholding, options exercises.

Only shows us when insiders are putting their OWN MONEY on the line.

Usage:
    python3 form4_conviction_scanner.py                    # Scan default watchlist
    python3 form4_conviction_scanner.py --add-ticker TSLA  # Add specific ticker
    python3 form4_conviction_scanner.py --days 60          # Scan last 60 days
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
from pathlib import Path
import argparse
import time

# Transaction codes we CARE about
CONVICTION_CODES = {
    'P': 'Open Market Purchase',  # THE ONLY ONE THAT MATTERS
}

# Transaction codes we IGNORE (no conviction)
IGNORE_CODES = {
    'A': 'Grant/Award',           # Free shares
    'M': 'Options Exercise',      # Converting options
    'F': 'Tax Withholding',       # Automatic
    'D': 'Disposition',           # Selling
    'G': 'Gift',                  # Transfer
    'I': 'Inheritance',           # Transfer
    'S': 'Sale',                  # Selling
    'U': 'Tender Offer',          # Corporate action
    'J': 'Other',                 # Misc
}

# Default watchlist
WATCHLIST = [
    'UUUU', 'USAR', 'AISP',
    'UEC', 'CCJ', 'SMR', 'LEU', 'DNN', 'NXE',
    'RR', 'QBTS', 'QUBT', 'RGTI', 'IONQ',
    'SMCI', 'CRDO', 'VRT',
    'RDW', 'RKLB', 'LUNR', 'ASTS',
]

class Form4ConvictionScanner:
    def __init__(self, watchlist=None, days=30):
        self.watchlist = watchlist or WATCHLIST
        self.days = days
        self.start_date = datetime.now() - timedelta(days=days)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_cik(self, ticker):
        """Get CIK number for ticker from SEC"""
        try:
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?company={ticker}&action=getcompany&output=xml"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'xml')
            cik = soup.find('CIK')
            return cik.text if cik else None
        except:
            return None
    
    def get_form4_filings(self, ticker):
        """Fetch Form 4 filings from SEC EDGAR"""
        cik = self.get_cik(ticker)
        if not cik:
            return []
        
        # Pad CIK to 10 digits
        cik = cik.zfill(10)
        
        try:
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=4&dateb=&owner=only&count=100&output=xml"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'xml')
            
            filings = []
            for filing in soup.find_all('filing'):
                filing_date_str = filing.find('filingDate')
                if not filing_date_str:
                    continue
                
                filing_date = datetime.strptime(filing_date_str.text, '%Y-%m-%d')
                if filing_date < self.start_date:
                    continue
                
                filing_url = filing.find('filingHref')
                if filing_url:
                    filings.append({
                        'date': filing_date.strftime('%Y-%m-%d'),
                        'url': filing_url.text
                    })
            
            return filings
            
        except Exception as e:
            return []
    
    def parse_form4(self, url):
        """Parse Form 4 XML to extract transaction details"""
        try:
            # Get the XML document
            doc_url = url.replace('-index.htm', '.xml')
            response = self.session.get(doc_url, timeout=10)
            soup = BeautifulSoup(response.content, 'xml')
            
            transactions = []
            
            # Parse non-derivative transactions
            for trans in soup.find_all('nonDerivativeTransaction'):
                trans_code_elem = trans.find('transactionCode')
                if not trans_code_elem:
                    continue
                
                trans_code = trans_code_elem.text.strip()
                
                # ONLY care about Code "P" - Open Market Purchase
                if trans_code != 'P':
                    continue
                
                # Extract transaction details
                trans_date = trans.find('transactionDate')
                shares_elem = trans.find('transactionShares')
                price_elem = trans.find('transactionPricePerShare')
                
                # Get insider name
                reporting_owner = soup.find('reportingOwner')
                name = 'Unknown'
                if reporting_owner:
                    name_elem = reporting_owner.find('rptOwnerName')
                    if name_elem:
                        name = name_elem.text.strip()
                
                # Get title
                title = 'N/A'
                relationship = reporting_owner.find('reportingOwnerRelationship') if reporting_owner else None
                if relationship:
                    if relationship.find('isDirector') and relationship.find('isDirector').text == '1':
                        title = 'Director'
                    elif relationship.find('isOfficer') and relationship.find('isOfficer').text == '1':
                        officer_title = relationship.find('officerTitle')
                        title = officer_title.text if officer_title else 'Officer'
                
                shares = int(shares_elem.find('value').text) if shares_elem and shares_elem.find('value') else 0
                price = float(price_elem.find('value').text) if price_elem and price_elem.find('value') else 0
                
                if shares > 0 and price > 0:
                    transactions.append({
                        'date': trans_date.find('value').text if trans_date and trans_date.find('value') else 'Unknown',
                        'insider': name,
                        'title': title,
                        'shares': shares,
                        'price': price,
                        'value': shares * price,
                        'code': trans_code
                    })
            
            return transactions
            
        except Exception as e:
            return []
    
    def scan_ticker(self, ticker):
        """Scan a single ticker for conviction buys"""
        print(f"   Scanning {ticker}...", end=' ')
        
        filings = self.get_form4_filings(ticker)
        if not filings:
            print("✓")
            return None
        
        all_transactions = []
        for filing in filings[:20]:  # Check last 20 filings
            transactions = self.parse_form4(filing['url'])
            all_transactions.extend(transactions)
            time.sleep(0.5)  # Rate limiting
        
        if all_transactions:
            print(f"✓ FOUND {len(all_transactions)} CONVICTION BUYS")
            return {
                'ticker': ticker,
                'transactions': all_transactions,
                'total_insiders': len(set(t['insider'] for t in all_transactions)),
                'total_value': sum(t['value'] for t in all_transactions),
                'total_shares': sum(t['shares'] for t in all_transactions)
            }
        else:
            print("✓")
            return None
    
    def scan_watchlist(self):
        """Scan all tickers in watchlist"""
        print(f"\n🔍 FORM 4 CONVICTION SCANNER - Real Insider Buying Only")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"   Scanning {len(self.watchlist)} tickers (last {self.days} days)")
        print(f"   ONLY Transaction Code 'P' = Open Market Purchase")
        print("=" * 80)
        
        results = []
        
        for ticker in self.watchlist:
            result = self.scan_ticker(ticker)
            if result:
                results.append(result)
            time.sleep(1)  # SEC rate limiting
        
        return results
    
    def display_results(self, results):
        """Display conviction buying results"""
        if not results:
            print("\n📊 No conviction insider buying detected in watchlist.")
            print("\n🐺 This means:")
            print("   • No insiders putting their money on the line recently")
            print("   • Check back in a few days or expand date range")
            return
        
        # Sort by total value
        results.sort(key=lambda x: x['total_value'], reverse=True)
        
        print("\n" + "=" * 80)
        print("🔥 CONVICTION INSIDER BUYING DETECTED")
        print("=" * 80)
        
        for i, data in enumerate(results, 1):
            ticker = data['ticker']
            print(f"\n{i}. {ticker} — {data['total_insiders']} insiders | ${data['total_value']:,.0f} total")
            print(f"   Total Shares: {data['total_shares']:,}")
            
            # Sort transactions by date (most recent first)
            transactions = sorted(data['transactions'], key=lambda x: x['date'], reverse=True)
            
            print(f"\n   📊 TRANSACTION DETAILS:")
            for trans in transactions[:10]:  # Show top 10
                print(f"      {trans['date']} | {trans['insider'][:30]:<30} | {trans['title'][:15]:<15}")
                print(f"         └─ {trans['shares']:>8,} shares @ ${trans['price']:.2f} = ${trans['value']:,.0f}")
        
        print("\n" + "=" * 80)
        print("🐺 WOLF'S READ ON INSIDER CONVICTION")
        print("=" * 80)
        
        # Identify clusters (3+ insiders in 7 days)
        clusters = []
        for data in results:
            ticker = data['ticker']
            transactions = data['transactions']
            
            # Group by week
            for trans in transactions:
                trans_date = datetime.strptime(trans['date'], '%Y-%m-%d')
                week_start = trans_date - timedelta(days=trans_date.weekday())
                
                # Count insiders in that week
                week_insiders = set()
                week_value = 0
                for t in transactions:
                    t_date = datetime.strptime(t['date'], '%Y-%m-%d')
                    if abs((t_date - week_start).days) <= 7:
                        week_insiders.add(t['insider'])
                        week_value += t['value']
                
                if len(week_insiders) >= 3:
                    clusters.append({
                        'ticker': ticker,
                        'week': week_start.strftime('%Y-%m-%d'),
                        'insiders': len(week_insiders),
                        'value': week_value
                    })
                    break
        
        if clusters:
            print(f"\n   🎯 TIGHT CLUSTERS ({len(clusters)} tickers with 3+ insiders within 7 days):")
            for cluster in sorted(clusters, key=lambda x: x['value'], reverse=True):
                print(f"      • {cluster['ticker']} - {cluster['insiders']} insiders | ${cluster['value']:,.0f} | Week of {cluster['week']}")
            print("\n   💡 Clusters = HIGHEST conviction. Insiders know something.")
        
        print("\n   📈 TOP CONVICTION (by total value):")
        for data in results[:5]:
            print(f"      • {data['ticker']} - ${data['total_value']:,.0f} by {data['total_insiders']} insiders")
        
        print("\n   🎯 WHAT THIS MEANS:")
        print("      • Code 'P' = Insiders buying with their OWN money (not awards/comp)")
        print("      • Multiple insiders = More conviction")
        print("      • Large $ amounts = Strong belief in upside")
        print("      • Recent dates = Timely signal")
        
    def save_results(self, results):
        """Save results to JSON"""
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        output_file = log_dir / 'form4_conviction.json'
        
        with open(output_file, 'w') as f:
            json.dump({
                'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'days_scanned': self.days,
                'results': results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Form 4 Conviction Scanner - Only Code P purchases')
    parser.add_argument('--add-ticker', action='append', help='Add ticker to scan')
    parser.add_argument('--days', type=int, default=30, help='Days to look back (default: 30)')
    
    args = parser.parse_args()
    
    watchlist = WATCHLIST.copy()
    if args.add_ticker:
        watchlist.extend([t.upper() for t in args.add_ticker])
    
    scanner = Form4ConvictionScanner(watchlist, args.days)
    results = scanner.scan_watchlist()
    scanner.display_results(results)
    if results:
        scanner.save_results(results)
    
    print("\n🐺 AWOOOO! Conviction buying scanned.\n")

if __name__ == '__main__':
    main()
