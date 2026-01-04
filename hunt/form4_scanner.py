#!/usr/bin/env python3
"""
🐺 FORM 4 INSIDER PURCHASE SCANNER
===================================

The cleanest edge there is:
When a CEO spends $200k of their own cash buying shares, THEY KNOW SOMETHING.

This scanner:
- Pulls Form 4 filings from SEC EDGAR (free, real-time)
- Filters for OPEN MARKET PURCHASES only (Transaction Code P)
- Ignores options exercises, compensation, gifts
- Checks if ticker is in our universe
- Alerts when an insider BUYS with their own money

Not patterns. Not guessing. Following people with actual information.

Built by Brokkr for the Wolf Pack
AWOOOO 🐺
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time
import re
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# OUR UNIVERSE - Tickers we care about
# ============================================================================

UNIVERSE = {
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ', 'LAES'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'BKSY', 'MNTS', 'ASTS', 'SPIR', 'PL', 
              'GSAT', 'SIDU', 'SATL', 'IRDM', 'VSAT'],
    'NUCLEAR': ['LEU', 'CCJ', 'UUUU', 'UEC', 'SMR', 'OKLO', 'DNN', 'NXE', 
                'LTBR', 'CEG', 'TLN', 'VST', 'NNE'],
    'BATTERY_METALS': ['MP', 'LAC', 'ALB', 'FCX', 'AG', 'HL', 'KGC'],
    'AI_INFRA': ['CORZ', 'VRT', 'PWR', 'EME', 'LITE', 'FN', 'WOLF', 'IREN',
                 'SOUN', 'PATH', 'UPST', 'AI', 'SMCI', 'DELL', 'HPE', 'NTAP', 
                 'PSTG', 'WDC', 'STX', 'ANET'],
    'MEMORY_SEMI': ['MU', 'WDC', 'SNDK', 'STX', 'COHR', 'PSTG', 'SMCI', 
                    'ANET', 'CRDO'],
    'SEMICONDUCTORS': ['NVDA', 'AMD', 'ALAB', 'ARM', 'TSM', 'ASML', 'KLAC',
                       'LRCX', 'AMAT', 'MRVL', 'BBAI', 'INTC', 'AVGO', 'QCOM'],
    'SPATIAL': ['KOPN', 'OLED', 'HIMX', 'VUZI', 'U', 'META', 'AAPL', 'GOOGL', 
                'MSFT', 'SNAP'],
    'ROBOTICS': ['TER', 'ZBRA', 'SYM', 'ROK', 'DE', 'ISRG'],
    'DEFENSE_AI': ['AISP', 'PLTR', 'KTOS', 'AVAV', 'RCAT'],
    'CRYPTO': ['MARA', 'RIOT', 'CLSK', 'HUT', 'BITF', 'COIN', 'CIFR'],
    'FINTECH': ['SOFI', 'AFRM', 'UPST', 'PYPL', 'NU'],
    'BIOTECH': ['CRSP', 'EDIT', 'NTLA', 'BEAM', 'RXRX', 'SDGR'],
    'EV_HYDROGEN': ['TSLA', 'RIVN', 'LCID', 'PLUG', 'FCEL', 'BE', 'BLNK', 'CHPT']
}

# Flatten universe into a set for fast lookup
ALL_TICKERS = set()
TICKER_TO_SECTOR = {}
for sector, tickers in UNIVERSE.items():
    for ticker in tickers:
        ALL_TICKERS.add(ticker.upper())
        TICKER_TO_SECTOR[ticker.upper()] = sector

# SEC EDGAR endpoints
SEC_FORM4_RSS = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&company=&dateb=&owner=only&count=100&output=atom"
SEC_FORM4_RSS_400 = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&company=&dateb=&owner=only&count=400&output=atom"
SEC_BASE_URL = "https://www.sec.gov"

# Headers required by SEC
HEADERS = {
    'User-Agent': 'WolfPack Trading Research contact@wolfpack.dev',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'www.sec.gov'
}

# ============================================================================
# FORM 4 PARSING
# ============================================================================

def get_recent_form4_filings() -> List[Dict]:
    """
    Fetch recent Form 4 filings from SEC EDGAR RSS feed
    Returns list of filing metadata
    """
    try:
        response = requests.get(SEC_FORM4_RSS, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        # Parse the Atom feed
        root = ET.fromstring(response.content)
        
        # Namespace for Atom feed
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        filings = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns)
            link = entry.find('atom:link', ns)
            updated = entry.find('atom:updated', ns)
            summary = entry.find('atom:summary', ns)
            
            if title is not None and link is not None:
                filing = {
                    'title': title.text,
                    'link': link.get('href'),
                    'updated': updated.text if updated is not None else None,
                    'summary': summary.text if summary is not None else None
                }
                filings.append(filing)
        
        return filings
        
    except Exception as e:
        print(f"Error fetching Form 4 RSS: {e}")
        return []

def extract_ticker_from_title(title: str) -> Optional[str]:
    """
    Extract ticker symbol from Form 4 filing title
    Title format: "4 - Company Name (0001234567) (Issuer)"
    """
    if not title:
        return None
    
    # The ticker might be in the company name or we need to look it up
    # For now, we'll need to get it from the filing details
    return None

def parse_form4_xml(filing_url: str) -> Optional[Dict]:
    """
    Parse the actual Form 4 XML to extract transaction details
    
    Key fields we need:
    - issuerTradingSymbol (ticker)
    - rptOwnerName (insider name)
    - transactionCode (P = Purchase, S = Sale, etc)
    - transactionShares
    - transactionPricePerShare
    - transactionDate
    """
    try:
        # Get the filing index page
        response = requests.get(filing_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        # Find the XML file link in the filing
        xml_pattern = r'href="([^"]*\.xml)"'
        matches = re.findall(xml_pattern, response.text)
        
        # Look for the primary document (not the -index.xml)
        xml_url = None
        for match in matches:
            if '-index' not in match and match.endswith('.xml'):
                if match.startswith('/'):
                    xml_url = SEC_BASE_URL + match
                else:
                    xml_url = filing_url.rsplit('/', 1)[0] + '/' + match
                break
        
        if not xml_url:
            return None
        
        # Rate limit - SEC requires max 10 requests per second
        time.sleep(0.15)
        
        # Fetch and parse the XML
        xml_response = requests.get(xml_url, headers=HEADERS, timeout=30)
        xml_response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(xml_response.content)
        
        # Extract key fields (handle namespaces)
        # Form 4 XML has various namespace possibilities
        
        def find_text(element, *tags):
            """Find text in element, trying multiple tag variations"""
            for tag in tags:
                # Try direct
                el = element.find(tag)
                if el is not None and el.text:
                    return el.text.strip()
                # Try with .// prefix
                el = element.find('.//' + tag)
                if el is not None and el.text:
                    return el.text.strip()
            return None
        
        # Get issuer info
        ticker = find_text(root, 'issuerTradingSymbol', 'issuer/issuerTradingSymbol')
        company_name = find_text(root, 'issuerName', 'issuer/issuerName')
        
        # Get owner info
        owner_name = find_text(root, 'rptOwnerName', 'reportingOwner/reportingOwnerId/rptOwnerName')
        owner_title = find_text(root, 'officerTitle', 'reportingOwner/reportingOwnerRelationship/officerTitle')
        is_director = find_text(root, 'isDirector', 'reportingOwner/reportingOwnerRelationship/isDirector')
        is_officer = find_text(root, 'isOfficer', 'reportingOwner/reportingOwnerRelationship/isOfficer')
        is_ten_percent = find_text(root, 'isTenPercentOwner', 'reportingOwner/reportingOwnerRelationship/isTenPercentOwner')
        
        # Get transactions - look for nonDerivativeTransaction elements
        transactions = []
        
        for trans in root.findall('.//nonDerivativeTransaction'):
            trans_code = find_text(trans, 'transactionCode', 
                                   'transactionCoding/transactionCode')
            trans_shares = find_text(trans, 'transactionShares',
                                     'transactionAmounts/transactionShares/value')
            trans_price = find_text(trans, 'transactionPricePerShare',
                                    'transactionAmounts/transactionPricePerShare/value')
            trans_date = find_text(trans, 'transactionDate',
                                   'transactionDate/value')
            acq_disp = find_text(trans, 'transactionAcquiredDisposedCode',
                                 'transactionAmounts/transactionAcquiredDisposedCode/value')
            
            if trans_code:
                transactions.append({
                    'code': trans_code,
                    'shares': float(trans_shares) if trans_shares else 0,
                    'price': float(trans_price) if trans_price else 0,
                    'date': trans_date,
                    'acquired_disposed': acq_disp  # A = Acquired, D = Disposed
                })
        
        if not ticker:
            return None
        
        return {
            'ticker': ticker.upper(),
            'company_name': company_name,
            'owner_name': owner_name,
            'owner_title': owner_title,
            'is_director': is_director == '1' or is_director == 'true',
            'is_officer': is_officer == '1' or is_officer == 'true',
            'is_ten_percent': is_ten_percent == '1' or is_ten_percent == 'true',
            'transactions': transactions,
            'filing_url': filing_url
        }
        
    except Exception as e:
        # Silently skip problematic filings
        return None

def is_open_market_purchase(transaction: Dict) -> bool:
    """
    Check if transaction is an open market purchase (the signal we want)
    
    Transaction Codes:
    P = Open market or private purchase
    S = Open market or private sale
    A = Grant, award or acquisition
    D = Disposition (sale)
    F = Payment of exercise price or tax liability
    M = Exercise or conversion of derivative security
    G = Gift
    J = Other acquisition or disposition
    """
    code = transaction.get('code', '').upper()
    acq_disp = transaction.get('acquired_disposed', '').upper()
    
    # We want: Transaction Code P AND Acquired (not disposed)
    return code == 'P' and acq_disp == 'A'

def scan_for_insider_purchases(days_back: int = 7, our_universe_only: bool = True, extended: bool = False) -> List[Dict]:
    """
    Main scanner function
    
    Scans recent Form 4 filings for open market purchases
    Optionally filters to only our universe of tickers
    
    Returns list of insider purchase signals
    """
    print("\n" + "="*80)
    print("🐺 FORM 4 INSIDER PURCHASE SCANNER")
    print("="*80)
    print(f"Scanning for open market purchases...")
    print(f"Filter: {'Our Universe Only' if our_universe_only else 'All Tickers'}")
    print(f"Mode: {'Extended (400 filings)' if extended else 'Standard (100 filings)'}")
    print()
    
    # Get recent filings
    print("Fetching recent Form 4 filings from SEC EDGAR...")
    
    # Use extended feed if requested
    feed_url = SEC_FORM4_RSS_400 if extended else SEC_FORM4_RSS
    
    try:
        response = requests.get(feed_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        # Parse the Atom feed
        root = ET.fromstring(response.content)
        
        # Namespace for Atom feed
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        filings = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns)
            link = entry.find('atom:link', ns)
            updated = entry.find('atom:updated', ns)
            summary = entry.find('atom:summary', ns)
            
            if title is not None and link is not None:
                filing = {
                    'title': title.text,
                    'link': link.get('href'),
                    'updated': updated.text if updated is not None else None,
                    'summary': summary.text if summary is not None else None
                }
                filings.append(filing)
    except Exception as e:
        print(f"Error fetching Form 4 RSS: {e}")
        filings = []
    
    print(f"Found {len(filings)} recent filings")
    
    purchases = []
    processed = 0
    
    for filing in filings:
        processed += 1
        if processed % 10 == 0:
            print(f"  Processing... {processed}/{len(filings)}")
        
        # Parse the filing
        filing_data = parse_form4_xml(filing['link'])
        
        if not filing_data:
            continue
        
        ticker = filing_data['ticker']
        
        # Filter to our universe if requested
        if our_universe_only and ticker not in ALL_TICKERS:
            continue
        
        # Check for open market purchases
        for trans in filing_data['transactions']:
            if is_open_market_purchase(trans):
                total_value = trans['shares'] * trans['price']
                
                # Only care about meaningful purchases (> $10,000)
                if total_value < 10000:
                    continue
                
                purchase = {
                    'ticker': ticker,
                    'sector': TICKER_TO_SECTOR.get(ticker, 'OTHER'),
                    'company': filing_data['company_name'],
                    'insider': filing_data['owner_name'],
                    'title': filing_data['owner_title'] or '',
                    'is_director': filing_data['is_director'],
                    'is_officer': filing_data['is_officer'],
                    'is_10pct_owner': filing_data['is_ten_percent'],
                    'shares': int(trans['shares']),
                    'price': round(trans['price'], 2),
                    'total_value': round(total_value, 2),
                    'date': trans['date'],
                    'filing_url': filing_data['filing_url']
                }
                purchases.append(purchase)
    
    print(f"\nProcessed {processed} filings")
    print(f"Found {len(purchases)} insider purchases in our universe")
    
    return purchases

def display_purchases(purchases: List[Dict]):
    """Display insider purchases in a clean format"""
    
    if not purchases:
        print("\n" + "="*80)
        print("No insider purchases found in our universe (this is actually common)")
        print("="*80)
        print("\nInsider buying is RARE - that's why it's such a strong signal!")
        print("Run this daily to catch signals when they appear.")
        return
    
    print("\n" + "="*80)
    print("🎯 INSIDER PURCHASES DETECTED")
    print("="*80)
    
    # Sort by total value (biggest purchases first)
    purchases.sort(key=lambda x: x['total_value'], reverse=True)
    
    for p in purchases:
        print(f"\n{'='*60}")
        print(f"🐺 {p['ticker']} - {p['sector']}")
        print(f"{'='*60}")
        print(f"   Company: {p['company']}")
        print(f"   Insider: {p['insider']}")
        if p['title']:
            print(f"   Title: {p['title']}")
        
        roles = []
        if p['is_officer']:
            roles.append('Officer')
        if p['is_director']:
            roles.append('Director')
        if p['is_10pct_owner']:
            roles.append('10%+ Owner')
        if roles:
            print(f"   Role: {', '.join(roles)}")
        
        print(f"\n   💰 PURCHASE DETAILS:")
        print(f"   Shares: {p['shares']:,}")
        print(f"   Price: ${p['price']:.2f}")
        print(f"   Total Value: ${p['total_value']:,.2f}")
        print(f"   Date: {p['date']}")
        print(f"\n   📄 Filing: {p['filing_url']}")

def run_scanner(our_universe_only: bool = True, extended: bool = False):
    """Run the full scanner and display results"""
    purchases = scan_for_insider_purchases(our_universe_only=our_universe_only, extended=extended)
    display_purchases(purchases)
    
    print("\n" + "="*80)
    print("🐺 Scanner complete. AWOOOO!")
    print("="*80)
    
    return purchases

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Form 4 Insider Purchase Scanner')
    parser.add_argument('--all', action='store_true', 
                        help='Scan all tickers, not just our universe')
    parser.add_argument('--extended', action='store_true',
                        help='Scan 400 filings instead of 100')
    
    args = parser.parse_args()
    
    purchases = run_scanner(our_universe_only=not args.all, extended=args.extended)
