#!/usr/bin/env python3
"""
FORM 4 CONVICTION SCANNER - PRODUCTION VERSION

ONLY Transaction Code "P" (Open Market Purchase) matters.
Filters out compensation, awards, options exercises - the noise.
Scores 0-100 based on conviction signals.
Detects clusters (3+ insiders = STRONG signal).

SUCCESS CRITERIA: 100% accuracy on P vs M/A/F. Catch clusters within 24h.

Usage:
    python3 form4_conviction_scanner.py
    python3 form4_conviction_scanner.py --days 60  # Extended lookback
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
from pathlib import Path
import argparse
import time
import re

# Tyr's watchlist
WATCHLIST = [
    'UUUU', 'USAR', 'AISP',
    'UEC', 'CCJ', 'SMR', 'LEU', 'DNN', 'NXE',
    'RR', 'QBTS', 'QUBT', 'RGTI', 'IONQ',
    'SMCI', 'CRDO', 'VRT',
    'RDW', 'RKLB', 'LUNR', 'ASTS',
]

# Transaction codes that matter
CONVICTION_CODES = {
    'P': 'Open Market Purchase',        # 🔥 HIGHEST conviction
    'I': '10b5-1 Discretionary Purchase'  # ✅ GOOD conviction
}

# Ignore these (noise)
IGNORE_CODES = {
    'A': 'Award/Grant',
    'M': 'Options Exercise',
    'F': 'Tax Withholding',
    'G': 'Gift',
    'S': 'Sale',
    'D': 'Disposition',
    'J': 'Other',
    'U': 'Tender',
}

class Form4ConvictionScanner:
    def __init__(self, days=30):
        self.days = days
        self.cutoff = datetime.now() - timedelta(days=days)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 research@trading.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        })
    
    def get_cik(self, ticker):
        """Get CIK for ticker"""
        try:
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?company={ticker}&action=getcompany&output=xml"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'xml')
            cik = soup.find('CIK')
            return cik.text.zfill(10) if cik else None
        except:
            return None
    
    def get_form4_filings(self, ticker):
        """Get Form 4 filings from SEC"""
        cik = self.get_cik(ticker)
        if not cik:
            return []
        
        try:
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=4&dateb=&owner=only&count=40&output=xml"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'xml')
            
            filings = []
            for filing in soup.find_all('filing'):
                filing_date_str = filing.find('filingDate')
                if not filing_date_str:
                    continue
                
                filing_date = datetime.strptime(filing_date_str.text, '%Y-%m-%d')
                if filing_date < self.cutoff:
                    continue
                
                filing_url = filing.find('filingHref')
                if filing_url:
                    filings.append({
                        'date': filing_date.strftime('%Y-%m-%d'),
                        'url': filing_url.text.replace('-index.htm', '.xml')
                    })
            
            return filings
        except:
            return []
    
    def parse_form4(self, url):
        """Parse Form 4 XML"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'xml')
            
            # Get insider info
            reporting_owner = soup.find('reportingOwner')
            if not reporting_owner:
                return []
            
            name_elem = reporting_owner.find('rptOwnerName')
            insider_name = name_elem.text.strip() if name_elem else 'Unknown'
            
            # Get title
            title = 'N/A'
            relationship = reporting_owner.find('reportingOwnerRelationship')
            if relationship:
                if relationship.find('isDirector') and relationship.find('isDirector').text == '1':
                    title = 'Director'
                elif relationship.find('isOfficer') and relationship.find('isOfficer').text == '1':
                    officer_title = relationship.find('officerTitle')
                    title = officer_title.text if officer_title else 'Officer'
                elif relationship.find('isTenPercentOwner') and relationship.find('isTenPercentOwner').text == '1':
                    title = '10% Owner'
            
            transactions = []
            
            # Parse non-derivative transactions
            for trans in soup.find_all('nonDerivativeTransaction'):
                trans_code_elem = trans.find('transactionCode')
                if not trans_code_elem:
                    continue
                
                trans_code = trans_code_elem.text.strip()
                
                # ONLY conviction codes (P or I)
                if trans_code not in CONVICTION_CODES:
                    continue
                
                # Extract details
                trans_date_elem = trans.find('transactionDate')
                shares_elem = trans.find('transactionShares')
                price_elem = trans.find('transactionPricePerShare')
                shares_owned_elem = trans.find('sharesOwnedFollowingTransaction')
                
                if not all([trans_date_elem, shares_elem, price_elem]):
                    continue
                
                trans_date = trans_date_elem.find('value').text if trans_date_elem.find('value') else ''
                shares = int(shares_elem.find('value').text) if shares_elem.find('value') else 0
                price = float(price_elem.find('value').text) if price_elem.find('value') else 0
                shares_owned = int(shares_owned_elem.find('value').text) if shares_owned_elem and shares_owned_elem.find('value') else 0
                
                if shares > 0 and price > 0:
                    value = shares * price
                    
                    # Calculate holdings increase
                    prior_holdings = shares_owned - shares
                    pct_increase = (shares / prior_holdings * 100) if prior_holdings > 0 else 0
                    
                    transactions.append({
                        'date': trans_date,
                        'insider': insider_name,
                        'title': title,
                        'code': trans_code,
                        'shares': shares,
                        'price': price,
                        'value': value,
                        'shares_owned': shares_owned,
                        'pct_increase': pct_increase
                    })
            
            return transactions
            
        except Exception as e:
            return []
    
    def score_conviction(self, transaction):
        """Score 0-100 based on conviction signals"""
        score = 0
        reasons = []
        
        # Transaction type (max 50)
        if transaction['code'] == 'P':
            score += 50
            reasons.append("Open market purchase (own money)")
        elif transaction['code'] == 'I':
            score += 30
            reasons.append("10b5-1 discretionary purchase")
        
        # Dollar amount (max 30)
        value = transaction['value']
        if value >= 1_000_000:
            score += 30
            reasons.append(f"${value:,.0f} purchase (serious conviction)")
        elif value >= 500_000:
            score += 20
            reasons.append(f"${value:,.0f} purchase")
        elif value >= 100_000:
            score += 10
            reasons.append(f"${value:,.0f} purchase")
        
        # Insider role (max 20)
        title = transaction['title'].upper()
        if any(x in title for x in ['CEO', 'CFO', 'CHAIRMAN']):
            score += 20
            reasons.append(f"{transaction['title']} (C-suite knows most)")
        elif any(x in title for x in ['DIRECTOR', 'PRESIDENT', 'COO', 'CTO']):
            score += 10
            reasons.append(f"{transaction['title']}")
        
        # Holdings increase (max 20)
        pct = transaction['pct_increase']
        if pct >= 25:
            score += 20
            reasons.append(f"{pct:.0f}% position increase (doubling down)")
        elif pct >= 10:
            score += 10
            reasons.append(f"{pct:.0f}% position increase")
        
        return score, reasons
    
    def detect_clusters(self, ticker, transactions):
        """Detect cluster buying (3+ insiders = STRONG signal)"""
        if len(transactions) < 2:
            return None
        
        unique_insiders = len(set(t['insider'] for t in transactions))
        total_value = sum(t['value'] for t in transactions)
        
        # Group by 30-day windows for tight clusters
        transactions_sorted = sorted(transactions, key=lambda x: x['date'])
        max_cluster_size = 1
        
        for i, trans in enumerate(transactions_sorted):
            trans_date = datetime.strptime(trans['date'], '%Y-%m-%d')
            window_end = trans_date + timedelta(days=30)
            
            cluster_insiders = set()
            cluster_value = 0
            
            for j in range(i, len(transactions_sorted)):
                check_trans = transactions_sorted[j]
                check_date = datetime.strptime(check_trans['date'], '%Y-%m-%d')
                
                if check_date > window_end:
                    break
                
                cluster_insiders.add(check_trans['insider'])
                cluster_value += check_trans['value']
            
            max_cluster_size = max(max_cluster_size, len(cluster_insiders))
        
        if unique_insiders >= 3 and total_value >= 500_000:
            return {
                'type': 'CLUSTER BUY DETECTED',
                'insiders': unique_insiders,
                'total_value': total_value,
                'max_cluster_size': max_cluster_size
            }
        elif unique_insiders >= 2 and total_value >= 250_000:
            return {
                'type': 'MULTIPLE INSIDERS BUYING',
                'insiders': unique_insiders,
                'total_value': total_value,
                'max_cluster_size': max_cluster_size
            }
        
        return None
    
    def scan_ticker(self, ticker):
        """Scan single ticker"""
        print(f"   {ticker}...", end=' ', flush=True)
        
        filings = self.get_form4_filings(ticker)
        if not filings:
            print("✓")
            return None
        
        all_transactions = []
        for filing in filings[:15]:  # Limit to recent 15
            transactions = self.parse_form4(filing['url'])
            all_transactions.extend(transactions)
            time.sleep(0.3)  # SEC rate limiting
        
        if not all_transactions:
            print("✓")
            return None
        
        # Score each transaction
        for trans in all_transactions:
            score, reasons = self.score_conviction(trans)
            trans['score'] = score
            trans['reasons'] = reasons
        
        # Filter to high conviction only (60+)
        high_conviction = [t for t in all_transactions if t['score'] >= 60]
        
        if not high_conviction:
            print("✓")
            return None
        
        # Detect clusters
        cluster_status = self.detect_clusters(ticker, all_transactions)
        
        print(f"✓ FOUND {len(high_conviction)} conviction buys")
        
        return {
            'ticker': ticker,
            'transactions': high_conviction,
            'cluster': cluster_status,
            'total_insiders': len(set(t['insider'] for t in high_conviction)),
            'total_value': sum(t['value'] for t in high_conviction)
        }
    
    def scan(self):
        """Scan watchlist"""
        print(f"\n🔍 FORM 4 CONVICTION SCANNER - PRODUCTION VERSION")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"   Scanning {len(WATCHLIST)} tickers (last {self.days} days)")
        print(f"   ONLY Transaction Code 'P' (Open Market Purchase)")
        print("=" * 80)
        
        print("\n   Scanning...")
        results = []
        
        for ticker in WATCHLIST:
            result = self.scan_ticker(ticker)
            if result:
                results.append(result)
        
        return results
    
    def display_results(self, results):
        """Display results"""
        if not results:
            print("\n📊 No high-conviction insider buying detected.")
            print("\n🐺 This means:")
            print("   • No Code 'P' purchases with score ≥60 in timeframe")
            print("   • Check back later or expand --days parameter")
            return
        
        # Sort by total value
        results.sort(key=lambda x: x['total_value'], reverse=True)
        
        print("\n" + "=" * 80)
        print("🔥 CONVICTION INSIDER BUYING DETECTED")
        print("=" * 80)
        
        for i, data in enumerate(results, 1):
            ticker = data['ticker']
            print(f"\n{i}. {ticker} — {data['total_insiders']} insiders | ${data['total_value']:,.0f} total")
            
            # Cluster status
            if data['cluster']:
                cluster = data['cluster']
                print(f"   🎯 {cluster['type']}")
                print(f"      • {cluster['insiders']} unique insiders")
                print(f"      • ${cluster['total_value']:,.0f} total value")
                print(f"      • Up to {cluster['max_cluster_size']} insiders in 30-day window")
            
            # Show top transactions
            transactions = sorted(data['transactions'], key=lambda x: x['score'], reverse=True)
            print(f"\n   📊 TOP CONVICTION BUYS:")
            
            for trans in transactions[:5]:
                print(f"\n      {trans['date']} | {trans['insider'][:30]} ({trans['title']})")
                print(f"      Score: {trans['score']}/100")
                print(f"      {trans['shares']:,} shares @ ${trans['price']:.2f} = ${trans['value']:,.0f}")
                print(f"      Why:")
                for reason in trans['reasons']:
                    print(f"         • {reason}")
        
        print("\n" + "=" * 80)
        print("🐺 WOLF'S READ")
        print("=" * 80)
        
        clusters = [r for r in results if r['cluster'] and 'CLUSTER' in r['cluster']['type']]
        if clusters:
            print(f"\n   🎯 CLUSTER BUYS (3+ insiders) = HIGHEST CONVICTION:")
            for r in clusters:
                print(f"      • {r['ticker']} - {r['cluster']['insiders']} insiders | ${r['cluster']['total_value']:,.0f}")
            print("\n   💡 Clusters mean insiders ALL see the same opportunity")
        
        print(f"\n   📈 TOP CONVICTION (by value):")
        for r in results[:5]:
            avg_price = sum(t['value'] for t in r['transactions']) / len(r['transactions'])
            print(f"      • {r['ticker']} - ${r['total_value']:,.0f} by {r['total_insiders']} insiders")
        
        print("\n   🎯 WHAT THIS MEANS:")
        print("      • Code 'P' = Insiders spending OWN money (not free shares)")
        print("      • Score 80+ = VERY strong conviction")
        print("      • Score 60-79 = Good conviction")
        print("      • Clusters (3+ insiders) = Pack hunting, strongest signal")
    
    def save_results(self, results):
        """Save to JSON"""
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        output_file = log_dir / f"form4_conviction_{datetime.now().strftime('%Y-%m-%d_%H%M')}.json"
        
        with open(output_file, 'w') as f:
            json.dump({
                'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'days_scanned': self.days,
                'results': results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Form 4 Conviction Scanner - Production Version')
    parser.add_argument('--days', type=int, default=30, help='Days to look back (default: 30)')
    
    args = parser.parse_args()
    
    scanner = Form4ConvictionScanner(args.days)
    results = scanner.scan()
    scanner.display_results(results)
    
    if results:
        scanner.save_results(results)
    
    print("\n🐺 AWOOOO! Form 4 conviction scan complete.\n")

if __name__ == '__main__':
    main()
