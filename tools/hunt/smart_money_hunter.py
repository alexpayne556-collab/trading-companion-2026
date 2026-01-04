#!/usr/bin/env python3
"""
🐺 SMART MONEY HUNTER - FULL MARKET INSIDER SCAN
=================================================

Scans the ENTIRE MARKET for insider buying.
Finds what the smart money is doing EVERYWHERE.
Then tells you which ones match our themes.

This is the wolf going OFF THE LEASH.

Built by Brokkr for the Wolf Pack
AWOOOO 🐺
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time
import re
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# EXPANDED UNIVERSE - Sectors we LOVE
# ============================================================================

# Our core themes
THEME_KEYWORDS = {
    'QUANTUM': ['quantum', 'qubit', 'computing', 'ionq', 'rigetti'],
    'SPACE': ['space', 'satellite', 'lunar', 'rocket', 'orbit', 'aerospace', 'aviation', 'aircraft'],
    'NUCLEAR': ['nuclear', 'uranium', 'reactor', 'energy', 'power', 'utilities'],
    'AI': ['artificial intelligence', ' ai ', 'machine learning', 'neural', 'gpu', 'chip', 'software'],
    'SEMICONDUCTOR': ['semiconductor', 'chip', 'wafer', 'foundry', 'memory', 'processor', 'silicon'],
    'CLEAN_ENERGY': ['solar', 'wind', 'battery', 'lithium', 'ev', 'electric vehicle', 'hydrogen', 'renewable', 'clean'],
    'BIOTECH': ['biotech', 'gene', 'crispr', 'therapy', 'pharma', 'drug', 'medical', 'health'],
    'CRYPTO': ['crypto', 'bitcoin', 'blockchain', 'mining', 'digital asset'],
    'FINTECH': ['fintech', 'payment', 'banking', 'financial technology', 'bank'],
    'ROBOTICS': ['robot', 'automation', 'autonomous', 'drone', 'evtol', 'flying'],
    'DEFENSE': ['defense', 'military', 'aerospace', 'security'],  # Track but flag
    'GOLD_PRECIOUS': ['gold', 'silver', 'precious', 'metal', 'mining'],
}

# Expanded watchlist - tickers we already love
CORE_UNIVERSE = set([
    # Quantum
    'IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ', 'LAES',
    # Space
    'LUNR', 'RKLB', 'RDW', 'BKSY', 'MNTS', 'ASTS', 'SPIR', 'PL', 
    'GSAT', 'SIDU', 'SATL', 'IRDM', 'VSAT',
    # eVTOL / Aviation (NEWLY ADDED from smart money scan)
    'JOBY', 'ACHR', 'LILM', 'EVTL',
    # Nuclear
    'LEU', 'CCJ', 'UUUU', 'UEC', 'SMR', 'OKLO', 'DNN', 'NXE', 
    'LTBR', 'CEG', 'TLN', 'VST', 'NNE',
    # Battery/Metals
    'MP', 'LAC', 'ALB', 'FCX', 'AG', 'HL', 'KGC',
    # AI Infrastructure
    'CORZ', 'VRT', 'PWR', 'EME', 'LITE', 'FN', 'WOLF', 'IREN',
    'SOUN', 'PATH', 'UPST', 'AI', 'SMCI', 'DELL', 'HPE', 'NTAP', 
    'PSTG', 'WDC', 'STX', 'ANET',
    # Semiconductors
    'NVDA', 'AMD', 'ARM', 'TSM', 'ASML', 'KLAC', 'LRCX', 'AMAT', 
    'MRVL', 'BBAI', 'INTC', 'AVGO', 'QCOM', 'MU', 'CRDO', 'COHR',
    # Spatial/VR
    'KOPN', 'OLED', 'HIMX', 'VUZI', 'U', 'META', 'AAPL', 'GOOGL', 'MSFT', 'SNAP',
    # Robotics
    'TER', 'ZBRA', 'SYM', 'ROK', 'DE', 'ISRG',
    # Defense AI (track but flag)
    'AISP', 'PLTR', 'KTOS', 'AVAV', 'RCAT',
    # Crypto
    'MARA', 'RIOT', 'CLSK', 'HUT', 'BITF', 'COIN', 'CIFR',
    # Fintech
    'SOFI', 'AFRM', 'UPST', 'PYPL', 'NU',
    # Biotech
    'CRSP', 'EDIT', 'NTLA', 'BEAM', 'RXRX', 'SDGR',
    # EV/Clean
    'TSLA', 'RIVN', 'LCID', 'PLUG', 'FCEL', 'BE', 'BLNK', 'CHPT',
    # Additional high-growth
    'PLTR', 'SNOW', 'NET', 'DDOG', 'ZS', 'CRWD', 'S', 'PANW',
    'SHOP', 'SQ', 'ABNB', 'UBER', 'LYFT', 'DASH', 'RBLX',
    # Gold/Precious (from scan - value play)
    'ASA', 'GLD', 'SLV', 'GOLD', 'NEM',
])

# SEC EDGAR
SEC_BASE_URL = "https://www.sec.gov"
HEADERS = {
    'User-Agent': 'WolfPack Trading Research wolfpack@example.com',
    'Accept-Encoding': 'gzip, deflate',
}

# ============================================================================
# SMART MONEY DETECTION
# ============================================================================

def get_form4_index_page(start: int = 0, count: int = 100) -> str:
    """Get the Form 4 filing index page from SEC"""
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&company=&dateb=&owner=only&count={count}&start={start}&output=atom"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching SEC: {e}")
        return ""

def parse_form4_feed(feed_xml: str) -> List[Dict]:
    """Parse Form 4 Atom feed"""
    filings = []
    
    try:
        root = ET.fromstring(feed_xml)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns)
            link = entry.find('atom:link', ns)
            updated = entry.find('atom:updated', ns)
            
            if title is not None and link is not None:
                filings.append({
                    'title': title.text,
                    'link': link.get('href'),
                    'updated': updated.text if updated is not None else None
                })
    except:
        pass
    
    return filings

def parse_form4_filing(filing_url: str) -> Optional[Dict]:
    """Parse individual Form 4 filing for transaction details"""
    try:
        # Get filing page
        response = requests.get(filing_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        # Find XML file - skip xsl transformed version
        xml_matches = re.findall(r'href="([^"]*\.xml)"', response.text)
        xml_url = None
        
        for match in xml_matches:
            # Skip xsl transformed and index files
            if 'xsl' in match.lower() or '-index' in match.lower():
                continue
            if match.endswith('.xml'):
                if match.startswith('/'):
                    xml_url = SEC_BASE_URL + match
                else:
                    xml_url = filing_url.rsplit('/', 1)[0] + '/' + match
                break
        
        if not xml_url:
            return None
        
        # Rate limit
        time.sleep(0.12)
        
        # Get XML
        xml_response = requests.get(xml_url, headers=HEADERS, timeout=30)
        xml_response.raise_for_status()
        
        root = ET.fromstring(xml_response.content)
        
        # Extract issuer info
        ticker_el = root.find('.//issuerTradingSymbol')
        company_el = root.find('.//issuerName')
        
        ticker = ticker_el.text.strip() if ticker_el is not None and ticker_el.text else None
        company = company_el.text.strip() if company_el is not None and company_el.text else None
        
        if not ticker:
            return None
        
        # Extract owner info
        owner_el = root.find('.//rptOwnerName')
        title_el = root.find('.//officerTitle')
        is_director_el = root.find('.//isDirector')
        is_officer_el = root.find('.//isOfficer')
        is_ten_pct_el = root.find('.//isTenPercentOwner')
        
        owner = owner_el.text.strip() if owner_el is not None and owner_el.text else None
        title = title_el.text.strip() if title_el is not None and title_el.text else None
        is_director = is_director_el.text in ['true', '1'] if is_director_el is not None and is_director_el.text else False
        is_officer = is_officer_el.text in ['true', '1'] if is_officer_el is not None and is_officer_el.text else False
        is_ten_pct = is_ten_pct_el.text in ['true', '1'] if is_ten_pct_el is not None and is_ten_pct_el.text else False
        
        # Get transactions
        purchases = []
        sales = []
        
        for trans in root.findall('.//nonDerivativeTransaction'):
            code_el = trans.find('.//transactionCode')
            shares_el = trans.find('.//transactionShares/value')
            price_el = trans.find('.//transactionPricePerShare/value')
            date_el = trans.find('.//transactionDate/value')
            acq_el = trans.find('.//transactionAcquiredDisposedCode/value')
            
            code = code_el.text.strip() if code_el is not None and code_el.text else None
            
            try:
                shares = float(shares_el.text) if shares_el is not None and shares_el.text else 0
            except:
                shares = 0
            
            try:
                price = float(price_el.text) if price_el is not None and price_el.text else 0
            except:
                price = 0
            
            date = date_el.text.strip() if date_el is not None and date_el.text else None
            acq = acq_el.text.strip() if acq_el is not None and acq_el.text else None
            
            if code == 'P' and acq == 'A':  # Open market purchase, acquired
                purchases.append({
                    'shares': shares,
                    'price': price,
                    'value': shares * price,
                    'date': date
                })
            elif code == 'S' and acq == 'D':  # Sale, disposed
                sales.append({
                    'shares': shares,
                    'price': price,
                    'value': shares * price,
                    'date': date
                })
        
        return {
            'ticker': ticker.upper(),
            'company': company,
            'owner': owner,
            'title': title,
            'is_director': is_director,
            'is_officer': is_officer,
            'is_ten_pct': is_ten_pct,
            'purchases': purchases,
            'sales': sales,
            'filing_url': filing_url
        }
        
    except Exception as e:
        return None

def classify_company(company_name: str, ticker: str) -> List[str]:
    """Classify company into themes based on name"""
    themes = []
    
    if not company_name:
        return themes
    
    name_lower = company_name.lower()
    
    for theme, keywords in THEME_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                themes.append(theme)
                break
    
    # Check if in core universe
    if ticker.upper() in CORE_UNIVERSE:
        themes.append('CORE_UNIVERSE')
    
    return list(set(themes))

def calculate_conviction_score(filing: Dict) -> float:
    """
    Calculate conviction score for an insider purchase
    
    Factors:
    - Total $ value (bigger = more conviction)
    - Insider role (CEO/CFO > Director > 10% owner)
    - Purchase as % of likely net worth (rough estimate)
    """
    if not filing['purchases']:
        return 0
    
    total_value = sum(p['value'] for p in filing['purchases'])
    
    # Base score from value
    if total_value >= 1000000:
        score = 100
    elif total_value >= 500000:
        score = 80
    elif total_value >= 100000:
        score = 60
    elif total_value >= 50000:
        score = 40
    elif total_value >= 25000:
        score = 25
    elif total_value >= 10000:
        score = 15
    else:
        score = 5
    
    # Boost for role
    title = (filing.get('title') or '').lower()
    if 'ceo' in title or 'chief executive' in title:
        score *= 1.5
    elif 'cfo' in title or 'chief financial' in title:
        score *= 1.4
    elif 'coo' in title or 'president' in title:
        score *= 1.3
    elif filing['is_director']:
        score *= 1.2
    elif filing['is_ten_pct']:
        score *= 1.1
    
    return min(score, 100)

# ============================================================================
# MAIN HUNTER
# ============================================================================

def hunt_smart_money(num_filings: int = 400, min_value: float = 10000) -> Tuple[List[Dict], Dict]:
    """
    Hunt for smart money across the ENTIRE market
    
    Returns:
    - List of all insider purchases found
    - Dict of statistics
    """
    print("\n" + "="*80)
    print("🐺 SMART MONEY HUNTER - FULL MARKET SCAN")
    print("="*80)
    print(f"Scanning {num_filings} most recent Form 4 filings...")
    print(f"Minimum purchase value: ${min_value:,.0f}")
    print()
    
    all_purchases = []
    seen_purchases = set()  # Dedupe by ticker+owner+date+value
    
    stats = {
        'total_filings': 0,
        'filings_with_purchases': 0,
        'total_purchase_value': 0,
        'purchases_by_theme': defaultdict(list),
        'core_universe_purchases': [],
        'big_purchases': [],  # > $100k
        'mega_purchases': [],  # > $500k
    }
    
    # Fetch filings in batches
    filings = []
    for start in range(0, num_filings, 100):
        print(f"  Fetching filings {start+1}-{min(start+100, num_filings)}...")
        feed = get_form4_index_page(start=start, count=min(100, num_filings - start))
        batch = parse_form4_feed(feed)
        filings.extend(batch)
        time.sleep(0.2)
    
    print(f"\nFound {len(filings)} filings to process")
    print("Processing filings (this takes a minute)...\n")
    
    processed = 0
    for filing in filings:
        processed += 1
        if processed % 50 == 0:
            print(f"  Processed {processed}/{len(filings)}...")
        
        data = parse_form4_filing(filing['link'])
        if not data:
            continue
        
        stats['total_filings'] += 1
        
        # Check for purchases
        if not data['purchases']:
            continue
        
        total_value = sum(p['value'] for p in data['purchases'])
        
        if total_value < min_value:
            continue
        
        # Dedupe check
        dedup_key = f"{data['ticker']}_{data['owner']}_{data['purchases'][0]['date']}_{int(total_value)}"
        if dedup_key in seen_purchases:
            continue
        seen_purchases.add(dedup_key)
        
        stats['filings_with_purchases'] += 1
        stats['total_purchase_value'] += total_value
        
        # Classify
        themes = classify_company(data['company'], data['ticker'])
        conviction = calculate_conviction_score(data)
        
        purchase_record = {
            'ticker': data['ticker'],
            'company': data['company'],
            'owner': data['owner'],
            'title': data['title'],
            'is_director': data['is_director'],
            'is_officer': data['is_officer'],
            'is_ten_pct': data['is_ten_pct'],
            'shares': sum(p['shares'] for p in data['purchases']),
            'avg_price': total_value / sum(p['shares'] for p in data['purchases']) if sum(p['shares'] for p in data['purchases']) > 0 else 0,
            'total_value': total_value,
            'date': data['purchases'][0]['date'] if data['purchases'] else None,
            'themes': themes,
            'conviction_score': conviction,
            'filing_url': data['filing_url'],
            'in_core_universe': data['ticker'] in CORE_UNIVERSE
        }
        
        all_purchases.append(purchase_record)
        
        # Categorize
        for theme in themes:
            stats['purchases_by_theme'][theme].append(purchase_record)
        
        if purchase_record['in_core_universe']:
            stats['core_universe_purchases'].append(purchase_record)
        
        if total_value >= 500000:
            stats['mega_purchases'].append(purchase_record)
        elif total_value >= 100000:
            stats['big_purchases'].append(purchase_record)
    
    print(f"\nProcessing complete!")
    
    return all_purchases, stats

def display_results(purchases: List[Dict], stats: Dict):
    """Display the hunt results"""
    
    print("\n" + "="*80)
    print("🎯 SMART MONEY HUNT RESULTS")
    print("="*80)
    
    print(f"\n📊 OVERVIEW:")
    print(f"   Total filings scanned: {stats['total_filings']}")
    print(f"   Filings with purchases: {stats['filings_with_purchases']}")
    print(f"   Total $ purchased: ${stats['total_purchase_value']:,.2f}")
    
    # MEGA PURCHASES (>$500k)
    if stats['mega_purchases']:
        print("\n" + "="*80)
        print("💎 MEGA PURCHASES (>$500k) - MAXIMUM CONVICTION")
        print("="*80)
        
        for p in sorted(stats['mega_purchases'], key=lambda x: x['total_value'], reverse=True):
            print(f"\n🐺 {p['ticker']} - ${p['total_value']:,.0f}")
            print(f"   Company: {p['company']}")
            print(f"   Insider: {p['owner']}")
            if p['title']:
                print(f"   Title: {p['title']}")
            print(f"   Shares: {p['shares']:,.0f} @ ${p['avg_price']:.2f}")
            print(f"   Date: {p['date']}")
            print(f"   Conviction Score: {p['conviction_score']:.0f}/100")
            if p['themes']:
                print(f"   Themes: {', '.join(p['themes'])}")
            if p['in_core_universe']:
                print(f"   ⭐ IN OUR UNIVERSE!")
            print(f"   📄 {p['filing_url']}")
    
    # BIG PURCHASES ($100k-$500k)
    if stats['big_purchases']:
        print("\n" + "="*80)
        print("💰 BIG PURCHASES ($100k-$500k) - HIGH CONVICTION")
        print("="*80)
        
        for p in sorted(stats['big_purchases'], key=lambda x: x['total_value'], reverse=True)[:15]:
            themes_str = f" [{', '.join(p['themes'])}]" if p['themes'] else ""
            universe_str = " ⭐" if p['in_core_universe'] else ""
            print(f"\n  {p['ticker']}: ${p['total_value']:,.0f} by {p['owner'][:30]}{themes_str}{universe_str}")
            if p['title']:
                print(f"    └─ {p['title']}")
    
    # CORE UNIVERSE PURCHASES
    if stats['core_universe_purchases']:
        print("\n" + "="*80)
        print("⭐ PURCHASES IN OUR UNIVERSE - DIRECT SIGNALS")
        print("="*80)
        
        for p in sorted(stats['core_universe_purchases'], key=lambda x: x['total_value'], reverse=True):
            print(f"\n🎯 {p['ticker']} - ${p['total_value']:,.0f}")
            print(f"   Insider: {p['owner']}")
            print(f"   Conviction: {p['conviction_score']:.0f}/100")
    
    # BY THEME
    print("\n" + "="*80)
    print("📊 PURCHASES BY THEME")
    print("="*80)
    
    theme_totals = {}
    for theme, purchases_list in stats['purchases_by_theme'].items():
        if theme == 'CORE_UNIVERSE':
            continue
        total = sum(p['total_value'] for p in purchases_list)
        theme_totals[theme] = total
    
    for theme in sorted(theme_totals.keys(), key=lambda x: theme_totals[x], reverse=True):
        total = theme_totals[theme]
        count = len(stats['purchases_by_theme'][theme])
        print(f"\n  {theme}: ${total:,.0f} across {count} purchases")
        
        # Show top 3 in each theme
        for p in sorted(stats['purchases_by_theme'][theme], key=lambda x: x['total_value'], reverse=True)[:3]:
            print(f"    └─ {p['ticker']}: ${p['total_value']:,.0f} by {p['owner'][:25]}")
    
    # DISCOVERY - New tickers to research
    print("\n" + "="*80)
    print("🔍 NEW TICKERS TO RESEARCH (Not in our universe but theme-aligned)")
    print("="*80)
    
    new_tickers = []
    for p in purchases:
        if not p['in_core_universe'] and p['themes'] and p['total_value'] >= 25000:
            new_tickers.append(p)
    
    if new_tickers:
        for p in sorted(new_tickers, key=lambda x: x['conviction_score'], reverse=True)[:20]:
            themes_str = ', '.join([t for t in p['themes'] if t != 'CORE_UNIVERSE'])
            print(f"\n  {p['ticker']}: ${p['total_value']:,.0f} (Score: {p['conviction_score']:.0f})")
            print(f"    └─ {p['company'][:50]}")
            print(f"    └─ Themes: {themes_str}")
            print(f"    └─ Buyer: {p['owner'][:40]}")
    else:
        print("\n  No theme-aligned purchases found outside our universe")
    
    # ALL PURCHASES SUMMARY
    print("\n" + "="*80)
    print(f"📋 ALL {len(purchases)} PURCHASES FOUND (sorted by value)")
    print("="*80)
    
    for p in sorted(purchases, key=lambda x: x['total_value'], reverse=True)[:30]:
        universe_mark = "⭐" if p['in_core_universe'] else "  "
        themes_str = f" [{', '.join(p['themes'][:2])}]" if p['themes'] else ""
        print(f"  {universe_mark} {p['ticker']:6} ${p['total_value']:>12,.0f}  {p['owner'][:25]:25}{themes_str}")

def run_full_hunt(num_filings: int = 1000):
    """Run the complete smart money hunt"""
    
    purchases, stats = hunt_smart_money(num_filings=num_filings, min_value=10000)
    display_results(purchases, stats)
    
    print("\n" + "="*80)
    print("🐺 HUNT COMPLETE")
    print("="*80)
    print("\nThe wolf has surveyed the entire herd.")
    print("Smart money flows revealed.")
    print("\nAWOOOO 🐺\n")
    
    return purchases, stats

# ============================================================================
# MAIN
# ============================================================================

def save_results_to_json(purchases: List[Dict], stats: Dict):
    """Save results to JSON for dashboard consumption"""
    import json
    from pathlib import Path
    
    # Ensure logs directory exists
    logs_dir = Path('/workspaces/trading-companion-2026/logs')
    logs_dir.mkdir(exist_ok=True)
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'total_purchases': len(purchases),
        'total_value': sum(p.get('total_value', 0) for p in purchases),
        'unique_tickers': len(set(p.get('ticker', '') for p in purchases)),
        'mega_purchases': stats.get('mega_purchases', []),
        'big_purchases': stats.get('big_purchases', []),
        'core_universe': stats.get('core_universe_purchases', []),
        'purchases': purchases
    }
    
    # Save to file
    output_path = logs_dir / 'smart_money_latest.json'
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n📁 Results saved to {output_path}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Money Hunter')
    parser.add_argument('--filings', type=int, default=1000, 
                        help='Number of filings to scan (default: 1000)')
    parser.add_argument('--min-value', type=int, default=10000,
                        help='Minimum purchase value (default: $10,000)')
    
    args = parser.parse_args()
    
    purchases, stats = hunt_smart_money(num_filings=args.filings, min_value=args.min_value)
    display_results(purchases, stats)
    
    # Save to JSON for dashboard
    save_results_to_json(purchases, stats)
    
    print("\n🐺 HUNT COMPLETE. AWOOOO!\n")
