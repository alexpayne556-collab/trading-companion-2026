#!/usr/bin/env python3
"""
🐺 SEC 8-K CONTRACT SCANNER - THE 15-MINUTE EDGE
=================================================
Catch material contracts 15-60 minutes BEFORE news coverage

SEC 8-K Item 1.01 = Material Definitive Agreements
This is where contract awards appear FIRST.

ATP Pro shows news AFTER media picks it up.
WE see the 8-K filing hit EDGAR FIRST.

AWOOOO 🐺 LLHR
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
import time
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# COLORS
# =============================================================================
class Colors:
    BRIGHT_GREEN = '\033[92m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# =============================================================================
# AI FUEL CHAIN WATCHLIST
# =============================================================================

AI_FUEL_CHAIN = {
    'NUCLEAR': ['UUUU', 'SMR', 'LEU', 'OKLO', 'CCJ', 'DNN', 'UEC', 'NXE', 'NNE'],
    'UTILITIES': ['NEE', 'VST', 'CEG', 'WMB'],
    'COOLING': ['VRT', 'MOD', 'NVT'],
    'PHOTONICS': ['LITE', 'AAOI', 'COHR', 'GFS'],
    'NETWORKING': ['ANET', 'CRDO', 'FN', 'CIEN'],
    'STORAGE': ['MU', 'WDC', 'STX'],
    'CHIPS': ['AMD', 'MRVL', 'AVGO', 'INTC', 'AMKR'],
    'DC_BUILDERS': ['SMCI', 'EME', 'CLS', 'FIX'],
    'DC_REITS': ['EQIX', 'DLR'],
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'ASTS', 'SIDU', 'BKSY', 'PL'],
    'AI_SOFTWARE': ['PLTR', 'AI', 'SOUN', 'PATH', 'UPST']
}

PRIORITY_TICKERS = ['UUUU', 'SIDU', 'LUNR', 'MU', 'LITE', 'VRT', 'SMR', 'LEU', 'RDW', 'OKLO']

ALL_WATCHLIST = []
for tickers in AI_FUEL_CHAIN.values():
    ALL_WATCHLIST.extend(tickers)

# =============================================================================
# CONTRACT KEYWORDS
# =============================================================================

# High-value keywords (30 points each)
TIER_1_KEYWORDS = [
    "department of defense", "dod", "pentagon",
    "department of energy", "doe", 
    "nasa", "artemis", "lunar gateway",
    "awarded contract", "contract award",
    "received contract", "secured contract",
    "billion", "million contract"
]

# Government agencies (20 points each)
GOVERNMENT_AGENCIES = [
    "air force", "usaf", "space force", "ussf",
    "navy", "army", "marines", "national guard",
    "darpa", "dia", "nsa", "nro",
    "department of homeland security", "dhs",
    "nuclear regulatory commission", "nrc",
    "federal energy regulatory", "ferc"
]

# Contract indicators (15 points each)
CONTRACT_INDICATORS = [
    "indefinite delivery", "idiq",
    "firm fixed price", "cost plus",
    "performance period", "base period",
    "option period", "contract value",
    "purchase agreement", "supply agreement"
]

# AI Infrastructure keywords (10 points each)
AI_INFRASTRUCTURE = [
    "data center", "hyperscale", "ai infrastructure",
    "cooling system", "liquid cooling",
    "gpu cluster", "ai training", "inference",
    "nuclear power", "small modular reactor", "smr",
    "uranium enrichment", "nuclear fuel"
]

# =============================================================================
# SEC EDGAR FUNCTIONS
# =============================================================================

SEC_HEADERS = {
    'User-Agent': 'Trading Research trading@example.com',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'www.sec.gov'
}

def get_recent_8k_filings(hours=4):
    """Get recent 8-K filings from SEC EDGAR RSS feed"""
    try:
        # SEC EDGAR RSS feed for 8-K filings
        url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&output=atom"
        
        response = requests.get(url, headers=SEC_HEADERS, timeout=15)
        
        if response.status_code != 200:
            print(f"   Error: SEC EDGAR returned {response.status_code}")
            return []
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # Namespace for ATOM feed
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        filings = []
        cutoff = datetime.now() - timedelta(hours=hours)
        
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns)
            link = entry.find('atom:link', ns)
            updated = entry.find('atom:updated', ns)
            
            if title is not None and link is not None:
                title_text = title.text
                
                # Extract ticker from title (format: "8-K - TICKER NAME (0001234567)")
                ticker_match = re.search(r'8-K\s+-\s+(\w+)', title_text)
                ticker = ticker_match.group(1) if ticker_match else None
                
                # Get filing date
                if updated is not None:
                    try:
                        filing_date = datetime.strptime(updated.text[:19], '%Y-%m-%dT%H:%M:%S')
                        
                        if filing_date < cutoff:
                            continue
                    except:
                        filing_date = datetime.now()
                else:
                    filing_date = datetime.now()
                
                filings.append({
                    'ticker': ticker,
                    'title': title_text,
                    'link': link.get('href'),
                    'date': filing_date
                })
        
        return filings
        
    except Exception as e:
        print(f"   Error fetching 8-K filings: {e}")
        return []

def extract_filing_text(filing_url):
    """Extract text from SEC filing"""
    try:
        response = requests.get(filing_url, headers=SEC_HEADERS, timeout=15)
        
        if response.status_code != 200:
            return ""
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text content
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up
        text = re.sub(r'\s+', ' ', text)
        
        return text.lower()
        
    except Exception as e:
        return ""

def score_filing(text, ticker):
    """Score an 8-K filing for contract relevance"""
    score = 0
    matches = []
    
    # Tier 1 keywords (30 points each)
    for kw in TIER_1_KEYWORDS:
        if kw.lower() in text:
            score += 30
            matches.append(f"⭐⭐⭐ {kw}")
    
    # Government agencies (20 points each)
    for agency in GOVERNMENT_AGENCIES:
        if agency.lower() in text:
            score += 20
            matches.append(f"⭐⭐ {agency}")
    
    # Contract indicators (15 points each)
    for indicator in CONTRACT_INDICATORS:
        if indicator.lower() in text:
            score += 15
            matches.append(f"⭐ {indicator}")
    
    # AI Infrastructure (10 points each)
    for ai_kw in AI_INFRASTRUCTURE:
        if ai_kw.lower() in text:
            score += 10
            matches.append(f"🤖 {ai_kw}")
    
    # Dollar amounts
    dollar_patterns = [
        r'\$\s*(\d+\.?\d*)\s*billion',
        r'\$\s*(\d+\.?\d*)\s*million'
    ]
    
    for pattern in dollar_patterns:
        match = re.search(pattern, text)
        if match:
            amount = float(match.group(1))
            if 'billion' in pattern:
                score += 50
                matches.append(f"💰 ${amount}B contract")
            else:
                score += 30
                matches.append(f"💰 ${amount}M contract")
    
    # Watchlist bonus
    if ticker and ticker.upper() in ALL_WATCHLIST:
        score += 30
        matches.append(f"⭐ IN WATCHLIST")
    
    # Priority ticker bonus
    if ticker and ticker.upper() in PRIORITY_TICKERS:
        score += 20
        matches.append(f"🔥 PRIORITY TICKER")
    
    return score, list(set(matches))[:10]

# =============================================================================
# SCANNING FUNCTIONS
# =============================================================================

def scan_8k_contracts(hours=4, min_score=30):
    """Scan recent 8-K filings for contracts"""
    
    print("\n" + "="*100)
    print(f"{Colors.CYAN}{Colors.BOLD}🔍 SEC 8-K CONTRACT SCANNER - THE 15-MINUTE EDGE 🔍{Colors.END}")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print(f"   Scanning last {hours} hours for material contracts")
    print(f"   Looking for: DOE/DOD/NASA contracts, dollar amounts, AI infrastructure")
    print("="*100)
    
    # Get recent filings
    print(f"\n   Fetching recent 8-K filings from SEC EDGAR...", end="", flush=True)
    filings = get_recent_8k_filings(hours)
    print(f" ✓ Found {len(filings)} filings")
    
    if not filings:
        print(f"\n   No recent 8-K filings found")
        return []
    
    # Score each filing
    results = []
    
    print(f"\n   Analyzing filings for contract keywords...", end="", flush=True)
    for i, filing in enumerate(filings):
        if i % 5 == 0:
            print(".", end="", flush=True)
        
        # Extract filing text
        text = extract_filing_text(filing['link'])
        
        if not text:
            continue
        
        # Score the filing
        score, matches = score_filing(text, filing['ticker'])
        
        if score >= min_score:
            filing['score'] = score
            filing['matches'] = matches
            results.append(filing)
        
        time.sleep(0.5)  # Rate limit
    
    print(" ✓ Done!")
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results

def display_contract_alerts(results):
    """Display contract alerts"""
    
    if not results:
        print(f"\n   {Colors.GREEN}No high-value contracts found in recent filings{Colors.END}")
        return
    
    print(f"\n{Colors.RED}{Colors.BOLD}{'='*100}")
    print(f"🚨 CONTRACT ALERTS - FILED BEFORE NEWS COVERAGE! 🚨")
    print(f"{'='*100}{Colors.END}")
    
    for i, filing in enumerate(results, 1):
        ticker = filing.get('ticker', 'UNKNOWN').upper()
        priority = "⭐" if ticker in PRIORITY_TICKERS else ""
        watchlist = "📍" if ticker in ALL_WATCHLIST else ""
        
        time_ago = datetime.now() - filing['date']
        hours_ago = time_ago.total_seconds() / 3600
        
        if hours_ago < 1:
            time_str = f"{int(time_ago.total_seconds() / 60)} minutes ago"
        else:
            time_str = f"{hours_ago:.1f} hours ago"
        
        print(f"\n{i}. {Colors.BRIGHT_GREEN}{Colors.BOLD}{ticker}{priority}{watchlist}{Colors.END} — Score: {filing['score']} — Filed {time_str}")
        print(f"   {filing['title'][:80]}")
        print(f"   Link: {filing['link']}")
        
        if filing['matches']:
            print(f"   Matches: {', '.join(filing['matches'][:5])}")
    
    # Priority ticker summary
    priority_hits = [r for r in results if r.get('ticker', '').upper() in PRIORITY_TICKERS]
    
    if priority_hits:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}{'='*100}")
        print(f"⭐ PRIORITY TICKER HITS")
        print(f"{'='*100}{Colors.END}")
        
        for hit in priority_hits:
            print(f"\n   {hit['ticker']} — Score: {hit['score']}")
            print(f"   Filed: {hit['date'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   🔗 {hit['link']}")
    
    # Wolf's read
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*100}")
    print(f"🐺 WOLF'S 8-K READ")
    print(f"{'='*100}{Colors.END}")
    
    if results:
        top = results[0]
        print(f"\n   🎯 TOP HIT: {top['ticker']} (Score: {top['score']})")
        print(f"   Filed {(datetime.now() - top['date']).total_seconds() / 60:.0f} minutes ago")
        print(f"\n   🚀 THE EDGE:")
        print(f"      • SEC filing hit EDGAR: NOW")
        print(f"      • News coverage typically: 15-60 minutes LATER")
        print(f"      • You have the edge BEFORE the crowd")
        print(f"\n   📋 NEXT STEPS:")
        print(f"      1. Read the full 8-K filing (link above)")
        print(f"      2. Check Level 2 in ATP Pro for building volume")
        print(f"      3. Enter position BEFORE news breaks")
        print(f"      4. Set alerts for news coverage")

def continuous_scan(interval=600):
    """Run continuous scanning"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}🐺 CONTINUOUS 8-K SCANNING MODE 🐺{Colors.END}")
    print(f"   Checking SEC EDGAR every {interval/60:.0f} minutes")
    print(f"   Press Ctrl+C to stop\n")
    
    try:
        while True:
            results = scan_8k_contracts(hours=2, min_score=30)
            display_contract_alerts(results)
            
            print(f"\n   Next scan in {interval/60:.0f} minutes... (Ctrl+C to stop)")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}🐺 Scanner stopped.{Colors.END}")

# =============================================================================
# MAIN
# =============================================================================

def main():
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--continuous":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 600
            continuous_scan(interval)
        elif sys.argv[1] == "--hours":
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 4
            results = scan_8k_contracts(hours=hours, min_score=30)
            display_contract_alerts(results)
        else:
            print("Usage:")
            print("  python sec_8k_contract_scanner.py              # Scan last 4 hours")
            print("  python sec_8k_contract_scanner.py --hours 8    # Scan last 8 hours")
            print("  python sec_8k_contract_scanner.py --continuous # Continuous mode")
    else:
        results = scan_8k_contracts(hours=4, min_score=30)
        display_contract_alerts(results)
    
    print(f"\n{'='*100}")
    print(f"{Colors.CYAN}{Colors.BOLD}🐺 AWOOOO! SEE IT FIRST! LLHR! 🐺{Colors.END}")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    main()
