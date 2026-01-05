#!/usr/bin/env python3
"""
SEC 8-K CONTRACT SCANNER V2 - Fixed Filters

Only scans relevant sectors. Better keyword matching with context.
Filters out pharma/biotech/banking false positives.

Usage:
    python3 sec_8k_scanner_v2.py --hours 24
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
from pathlib import Path
import argparse
import time
import re

# Only these sectors matter
RELEVANT_SECTORS = {
    'uranium', 'nuclear', 'energy', 'mining', 'fuel',
    'aerospace', 'defense', 'space', 'satellite', 'launch',
    'technology', 'software', 'artificial intelligence', 'ai', 'robotics',
    'rare earth', 'metals', 'materials', 'lithium', 'battery'
}

# Ignore these completely
IGNORE_SECTORS = {
    'pharmaceutical', 'biotech', 'bio-tech', 'healthcare', 'medical', 'clinical',
    'bank', 'financial services', 'insurance', 'reit', 'mortgage',
    'retail', 'consumer', 'restaurant', 'food', 'beverage'
}

# Our watchlist
WATCHLIST = [
    'UUUU', 'USAR', 'AISP',
    'UEC', 'CCJ', 'SMR', 'LEU', 'DNN', 'NXE',
    'RR', 'QBTS', 'QUBT', 'RGTI', 'IONQ',
    'SMCI', 'CRDO', 'VRT',
    'RDW', 'RKLB', 'LUNR', 'ASTS',
]

class SEC8KScanner:
    def __init__(self, hours=24):
        self.hours = hours
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def is_relevant_sector(self, company_name):
        """Check if company is in relevant sector"""
        name_lower = company_name.lower()
        
        # Check ignore list first
        for ignore in IGNORE_SECTORS:
            if ignore in name_lower:
                return False
        
        # Check relevant sectors
        for relevant in RELEVANT_SECTORS:
            if relevant in name_lower:
                return True
        
        return False  # Default to False - only scan relevant sectors
    
    def get_recent_8k_filings(self):
        """Fetch recent 8-K filings from SEC EDGAR"""
        try:
            url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&count=100&output=atom"
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'xml')
            entries = soup.find_all('entry')
            
            filings = []
            cutoff = datetime.now() - timedelta(hours=self.hours)
            
            for entry in entries:
                title = entry.find('title')
                link = entry.find('link')
                updated = entry.find('updated')
                
                if not (title and link and updated):
                    continue
                
                # Parse filing time
                filing_time = datetime.fromisoformat(updated.text.replace('Z', '+00:00'))
                if filing_time.replace(tzinfo=None) < cutoff:
                    continue
                
                # Extract ticker and company name
                title_text = title.text
                match = re.search(r'8-K - (.+?) \((\d+)\)', title_text)
                if match:
                    company_name = match.group(1).strip()
                    
                    # Extract ticker (usually first word)
                    ticker = company_name.split()[0] if company_name else 'UNKNOWN'
                    
                    # Sector filter
                    if not self.is_relevant_sector(company_name):
                        continue
                    
                    filings.append({
                        'ticker': ticker,
                        'company': company_name,
                        'link': link.get('href'),
                        'filed': filing_time,
                        'hours_ago': (datetime.now() - filing_time.replace(tzinfo=None)).total_seconds() / 3600
                    })
            
            return filings
            
        except Exception as e:
            print(f"Error fetching filings: {e}")
            return []
    
    def analyze_filing(self, filing):
        """Analyze 8-K content for material contracts"""
        try:
            response = self.session.get(filing['link'], timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text().lower()
            
            score = 0
            matches = []
            
            # Government agencies WITH context
            agencies = [
                ('department of defense', 60), ('department of energy', 60),
                ('dod contract', 60), ('doe contract', 60),
                ('nasa awarded', 50), ('nasa contract', 50),
                ('air force contract', 50), ('navy contract', 50), ('army contract', 50),
                ('space force', 50), ('darpa', 40)
            ]
            
            for keyword, points in agencies:
                if keyword in text:
                    # Look for dollar amounts nearby
                    pos = text.find(keyword)
                    context = text[max(0, pos-200):min(len(text), pos+200)]
                    
                    if any(x in context for x in ['$', 'million', 'billion']):
                        score += points
                        matches.append(f"🎯 {keyword.upper()} ($ found)")
                    else:
                        score += points // 2
                        matches.append(f"⚠️ {keyword}")
            
            # Contract awards
            contracts = [
                ('awarded contract', 40), ('contract award', 40),
                ('purchase order', 30), ('supply agreement', 30),
                ('received contract', 40), ('secured contract', 40)
            ]
            
            for keyword, points in contracts:
                if keyword in text:
                    pos = text.find(keyword)
                    context = text[max(0, pos-100):min(len(text), pos+100)]
                    
                    # Must have dollar amount
                    if '$' in context or 'million' in context or 'billion' in context:
                        score += points
                        matches.append(f"💰 {keyword}")
            
            # Sector-specific keywords
            if 'uranium' in text and ('supply' in text or 'contract' in text):
                score += 30
                matches.append("⚛️ uranium supply/contract")
            
            if 'satellite' in text and ('launch' in text or 'contract' in text):
                score += 30
                matches.append("🛰️ satellite launch/contract")
            
            if 'ai infrastructure' in text or 'data center contract' in text:
                score += 30
                matches.append("🤖 AI infrastructure")
            
            # Return only if high score
            if score >= 60:
                return {
                    'ticker': filing['ticker'],
                    'company': filing['company'],
                    'score': min(score, 100),
                    'matches': matches[:5],
                    'filed_hours_ago': filing['hours_ago'],
                    'link': filing['link']
                }
            
            return None
            
        except Exception as e:
            return None
    
    def scan(self):
        """Run the scan"""
        print(f"\n🔍 SEC 8-K CONTRACT SCANNER V2")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"   Scanning last {self.hours} hours")
        print(f"   Relevant sectors only: Nuclear, Space, Defense, AI, Rare Earth")
        print("=" * 80)
        
        print(f"\n   Fetching recent 8-K filings...", end=' ')
        filings = self.get_recent_8k_filings()
        print(f"✓ Found {len(filings)} relevant filings")
        
        if not filings:
            print("\n   No relevant 8-K filings found in this timeframe.")
            return []
        
        print(f"\n   Analyzing filings for contracts...")
        results = []
        
        for filing in filings:
            result = self.analyze_filing(filing)
            if result:
                results.append(result)
            time.sleep(0.5)  # Rate limiting
        
        return results
    
    def display_results(self, results):
        """Display results"""
        if not results:
            print("\n📊 No material contracts detected in recent 8-K filings.")
            print("\n🐺 Either:")
            print("   • No contracts awarded recently")
            print("   • Contracts announced but below our thresholds")
            print("   • Check back later or expand time window")
            return
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        print("\n" + "=" * 80)
        print("🚨 MATERIAL CONTRACTS DETECTED")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['ticker']} — Score: {result['score']}/100 — Filed {result['filed_hours_ago']:.1f}h ago")
            print(f"   {result['company']}")
            print(f"   Link: {result['link']}")
            print(f"   Matches:")
            for match in result['matches']:
                print(f"      • {match}")
        
        print("\n" + "=" * 80)
        print("🐺 WOLF'S READ")
        print("=" * 80)
        print("\n   ⚡ THE EDGE: These contracts hit SEC EDGAR before news media")
        print("   ⏱️  You have 15-60 minutes before Bloomberg/Reuters picks it up")
        print("   🎯 High scores (70+) = Strong government/major contract indicators")
        print("\n   📊 CHECK ATP NOW:")
        for result in results[:3]:
            print(f"      • {result['ticker']} - Is it moving yet?")
    
    def save_results(self, results):
        """Save to JSON"""
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        output_file = log_dir / 'sec_8k_contracts.json'
        
        with open(output_file, 'w') as f:
            json.dump({
                'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'hours_scanned': self.hours,
                'results': results
            }, f, indent=2)
        
        print(f"\n💾 Saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='SEC 8-K Contract Scanner V2')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back')
    parser.add_argument('--watch', action='store_true', help='Continuous monitoring')
    parser.add_argument('--interval', type=int, default=30, help='Minutes between scans')
    
    args = parser.parse_args()
    
    scanner = SEC8KScanner(args.hours)
    
    if args.watch:
        print(f"\n🐺 WATCH MODE - Scanning every {args.interval} minutes")
        print("   Press Ctrl+C to stop\n")
        
        try:
            while True:
                results = scanner.scan()
                scanner.display_results(results)
                if results:
                    scanner.save_results(results)
                
                print(f"\n⏰ Next scan in {args.interval} minutes...")
                time.sleep(args.interval * 60)
        except KeyboardInterrupt:
            print("\n\n🐺 Watch stopped. AWOOOO!")
    else:
        results = scanner.scan()
        scanner.display_results(results)
        if results:
            scanner.save_results(results)
        
        print("\n🐺 AWOOOO! Scan complete.\n")

if __name__ == '__main__':
    main()
