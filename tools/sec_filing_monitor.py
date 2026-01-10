#!/usr/bin/env python3
"""
🐺 ULTIMATE SEC FILING MONITOR - THE 15-MINUTE EDGE
===================================================

Monitors SEC EDGAR in REAL-TIME for material events BEFORE the news.

THE EDGE:
- 8-K Item 1.01 = Material contracts (see 15-60min before media)
- 8-K Item 5.02 = Executive changes (CEO/CFO departures)
- Form 4 clusters = Insider buying (3+ insiders = strong signal)
- S-1/S-3 = New offerings (dilution = bad)
- 13D/13G = 5%+ ownership changes (activist investors)

USAGE:
    python sec_filing_monitor.py              # Monitor all watchlist
    python sec_filing_monitor.py --watch      # Continuous monitoring
    python sec_filing_monitor.py --hours 24   # Last 24 hours

🐺 LLHR. SEE IT FIRST. TRADE IT SECOND. 🐺
"""

import argparse
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import re
from collections import defaultdict
import time
import json

# =============================================================================
# WATCHLIST
# =============================================================================

WATCHLIST = {
    'AI_INFRA': ['WULF', 'CIFR', 'IREN', 'APLD', 'CLSK', 'BTBT', 'CORZ', 'HIVE', 'MARA', 'RIOT'],
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'SPACE': ['RKLB', 'LUNR', 'ASTS', 'SPIR', 'BKSY', 'RDW', 'SIDU'],
    'NUCLEAR': ['SMR', 'OKLO', 'DNN', 'UEC', 'UUUU', 'CCJ', 'LEU', 'NXE'],
    'DEFENSE': ['PLTR', 'KTOS', 'RCAT', 'AVAV'],
    'CHIPS': ['NVDA', 'AMD', 'INTC', 'ARM', 'MRVL', 'SMCI'],
}

ALL_TICKERS = [t for group in WATCHLIST.values() for t in group]

# =============================================================================
# HIGH-VALUE KEYWORDS FOR 8-K ANALYSIS
# =============================================================================

CONTRACT_KEYWORDS = {
    'TIER_1': {  # 50 points each
        'keywords': [
            'department of defense', 'dod contract', 'pentagon',
            'department of energy', 'doe contract',
            'nasa contract', 'space force', 'darpa',
            'billion', 'multibillion'
        ],
        'score': 50
    },
    'TIER_2': {  # 30 points each
        'keywords': [
            'awarded contract', 'contract award', 'material contract',
            'definitive agreement', 'purchase agreement',
            'million contract', 'supply agreement',
            'microsoft', 'amazon', 'google', 'meta', 'oracle'
        ],
        'score': 30
    },
    'TIER_3': {  # 15 points each
        'keywords': [
            'ai infrastructure', 'data center', 'hyperscale',
            'nuclear power', 'uranium', 'enrichment',
            'quantum computing', 'satellite', 'launch'
        ],
        'score': 15
    }
}

# =============================================================================
# SEC EDGAR API
# =============================================================================

SEC_HEADERS = {
    'User-Agent': 'Wolf Pack Trading research@wolfpack.trading',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'www.sec.gov'
}

def get_recent_filings(form_type='8-K', hours=4):
    """
    Get recent SEC filings from EDGAR RSS feed
    
    Args:
        form_type: '8-K', '4', '13D', '13G', 'S-1', etc.
        hours: Look back this many hours
    
    Returns:
        List of filing dicts with ticker, date, link
    """
    try:
        # SEC EDGAR RSS feed
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type={form_type}&output=atom"
        
        print(f"  Fetching {form_type} filings from SEC EDGAR...")
        response = requests.get(url, headers=SEC_HEADERS, timeout=20)
        
        if response.status_code != 200:
            print(f"  ⚠️  SEC returned status {response.status_code}")
            return []
        
        # Parse ATOM XML
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError:
            print(f"  ⚠️  Failed to parse SEC XML response")
            return []
        
        # ATOM namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        filings = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for entry in root.findall('atom:entry', ns):
            try:
                # Extract fields
                title_elem = entry.find('atom:title', ns)
                link_elem = entry.find('atom:link', ns)
                updated_elem = entry.find('atom:updated', ns)
                
                if not all([title_elem, link_elem, updated_elem]):
                    continue
                
                title = title_elem.text
                link = link_elem.get('href')
                
                # Parse date
                updated_text = updated_elem.text
                try:
                    filing_date = datetime.strptime(updated_text[:19], '%Y-%m-%dT%H:%M:%S')
                except:
                    filing_date = datetime.now()
                
                # Only recent filings
                if filing_date < cutoff_time:
                    continue
                
                # Extract ticker from title
                # Format: "8-K - TICKER NAME (CIK)"
                ticker_match = re.search(r'^\w+-\w+\s+-\s+([A-Z]+)', title)
                ticker = ticker_match.group(1) if ticker_match else None
                
                if ticker:
                    filings.append({
                        'form_type': form_type,
                        'ticker': ticker,
                        'title': title,
                        'link': link,
                        'date': filing_date,
                        'age_minutes': int((datetime.now() - filing_date).total_seconds() / 60)
                    })
            
            except Exception as e:
                continue
        
        return filings
    
    except Exception as e:
        print(f"  ⚠️  Error fetching filings: {e}")
        return []


def fetch_filing_text(filing_url):
    """Fetch and extract text from SEC filing"""
    try:
        # Get the filing index page
        response = requests.get(filing_url, headers=SEC_HEADERS, timeout=20)
        
        if response.status_code != 200:
            return ""
        
        # The RSS feed gives us the index page
        # We need to find the actual document link
        # Look for .txt or .html document
        
        doc_links = re.findall(r'href="([^"]+\.txt)"', response.text)
        if not doc_links:
            doc_links = re.findall(r'href="([^"]+\.html)"', response.text)
        
        if not doc_links:
            return ""
        
        # Get the first document
        doc_url = doc_links[0]
        if not doc_url.startswith('http'):
            base = 'https://www.sec.gov'
            doc_url = base + doc_url if doc_url.startswith('/') else base + '/' + doc_url
        
        # Fetch document content
        doc_response = requests.get(doc_url, headers=SEC_HEADERS, timeout=20)
        
        if doc_response.status_code == 200:
            # Clean and return text
            text = re.sub(r'<[^>]+>', ' ', doc_response.text)  # Remove HTML
            text = re.sub(r'\s+', ' ', text)  # Clean whitespace
            return text.lower()
        
        return ""
    
    except Exception as e:
        return ""


def analyze_8k_filing(filing, watchlist_only=True):
    """
    Analyze an 8-K filing for material contracts/events
    
    Returns:
        dict with score, keywords found, and alert level
    """
    ticker = filing['ticker']
    
    # Only analyze watchlist tickers unless specified
    if watchlist_only and ticker not in ALL_TICKERS:
        return None
    
    # Fetch filing text
    text = fetch_filing_text(filing['link'])
    
    if not text:
        return None
    
    # Score the filing
    score = 0
    found_keywords = []
    
    for tier, info in CONTRACT_KEYWORDS.items():
        for keyword in info['keywords']:
            if keyword in text:
                score += info['score']
                found_keywords.append((keyword, info['score']))
    
    # Dollar amount detection
    dollar_patterns = [
        (r'\$[\d,]+\s*billion', 100),  # Billions
        (r'\$[\d,]+\s*million', 50),   # Millions
    ]
    
    for pattern, points in dollar_patterns:
        matches = re.findall(pattern, text)
        if matches:
            score += points * len(matches)
            found_keywords.append((f"Dollar amount: {matches[0]}", points))
    
    # Determine alert level
    if score >= 150:
        alert = '🚨 CRITICAL'
    elif score >= 80:
        alert = '⚠️  HIGH'
    elif score >= 40:
        alert = '🔔 MEDIUM'
    else:
        alert = '📋 LOW'
    
    return {
        'ticker': ticker,
        'score': score,
        'alert': alert,
        'keywords': found_keywords,
        'date': filing['date'],
        'age_minutes': filing['age_minutes'],
        'link': filing['link']
    }


def scan_form4_clusters(hours=24):
    """
    Scan for Form 4 insider buying clusters
    
    Returns:
        dict of tickers with multiple insider buys
    """
    print(f"\n📊 Scanning Form 4 (Insider Trades) last {hours}h...")
    
    filings = get_recent_filings('4', hours=hours)
    
    if not filings:
        print("  No Form 4 filings found")
        return {}
    
    # Group by ticker
    ticker_filings = defaultdict(list)
    for f in filings:
        if f['ticker'] in ALL_TICKERS:
            ticker_filings[f['ticker']].append(f)
    
    # Find clusters (3+ filings = cluster)
    clusters = {}
    for ticker, forms in ticker_filings.items():
        if len(forms) >= 3:
            clusters[ticker] = {
                'count': len(forms),
                'first_filing': min(f['date'] for f in forms),
                'last_filing': max(f['date'] for f in forms),
                'signal': '🐺 CLUSTER BUY' if len(forms) >= 3 else '📈 Multiple'
            }
    
    return clusters


def monitor_filings_continuous(interval_seconds=300):
    """
    Continuous monitoring mode
    
    Args:
        interval_seconds: Check every N seconds (default 5min)
    """
    print("🐺 CONTINUOUS SEC FILING MONITOR")
    print("="*70)
    print(f"Checking every {interval_seconds}s for new filings...")
    print(f"Watchlist: {len(ALL_TICKERS)} tickers")
    print("Press Ctrl+C to stop")
    print()
    
    seen_filings = set()
    
    while True:
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking SEC EDGAR...")
            
            # Check 8-Ks (last 15 minutes only in continuous mode)
            filings_8k = get_recent_filings('8-K', hours=0.25)
            
            new_filings = []
            for filing in filings_8k:
                filing_id = f"{filing['ticker']}_{filing['date'].isoformat()}"
                if filing_id not in seen_filings:
                    seen_filings.add(filing_id)
                    new_filings.append(filing)
            
            if new_filings:
                print(f"  ✅ Found {len(new_filings)} new 8-K filings")
                
                for filing in new_filings:
                    if filing['ticker'] in ALL_TICKERS:
                        print(f"\n  🔔 NEW: {filing['ticker']} filed 8-K {filing['age_minutes']}min ago")
                        
                        # Analyze it
                        analysis = analyze_8k_filing(filing)
                        if analysis and analysis['score'] > 0:
                            print(f"     {analysis['alert']} - Score: {analysis['score']}")
                            if analysis['keywords']:
                                print(f"     Keywords: {', '.join([k[0] for k in analysis['keywords'][:3]])}")
            else:
                print("  No new watchlist filings")
            
            # Wait before next check
            time.sleep(interval_seconds)
        
        except KeyboardInterrupt:
            print("\n\n🐺 Monitoring stopped. LLHR.")
            break
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            time.sleep(interval_seconds)


def main():
    parser = argparse.ArgumentParser(description='SEC Filing Monitor')
    parser.add_argument('--hours', type=int, default=4, help='Look back N hours')
    parser.add_argument('--watch', action='store_true', help='Continuous monitoring')
    parser.add_argument('--form', type=str, default='8-K', help='Form type to scan')
    args = parser.parse_args()
    
    print("🐺 SEC FILING MONITOR - THE 15-MINUTE EDGE")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Watchlist: {len(ALL_TICKERS)} tickers")
    print()
    
    if args.watch:
        monitor_filings_continuous()
        return
    
    # One-time scan
    print(f"📋 Scanning {args.form} filings (last {args.hours}h)...")
    
    filings = get_recent_filings(args.form, hours=args.hours)
    
    if not filings:
        print(f"\n❌ No {args.form} filings found in last {args.hours}h")
        return
    
    print(f"  ✅ Found {len(filings)} total filings")
    
    # Filter to watchlist
    watchlist_filings = [f for f in filings if f['ticker'] in ALL_TICKERS]
    
    if not watchlist_filings:
        print(f"\n❌ No watchlist tickers filed {args.form} in last {args.hours}h")
        return
    
    print(f"  🎯 {len(watchlist_filings)} from watchlist tickers")
    print()
    
    # Analyze each filing
    if args.form == '8-K':
        print("🔍 ANALYZING 8-K FILINGS FOR MATERIAL CONTRACTS...")
        print()
        
        analyzed = []
        for filing in watchlist_filings:
            print(f"  Analyzing {filing['ticker']}... ", end='', flush=True)
            analysis = analyze_8k_filing(filing, watchlist_only=False)
            if analysis:
                analyzed.append(analysis)
                print(f"{analysis['alert']} (Score: {analysis['score']})")
            else:
                print("No keywords")
        
        # Sort by score
        analyzed.sort(key=lambda x: x['score'], reverse=True)
        
        print()
        print("="*70)
        print("📊 RESULTS")
        print("="*70)
        
        if not analyzed or analyzed[0]['score'] == 0:
            print("\n❌ No material contracts found")
        else:
            for i, result in enumerate(analyzed, 1):
                if result['score'] > 0:
                    print(f"\n{i}. {result['ticker']:6} - {result['alert']}")
                    print(f"   Score: {result['score']:3}  |  Filed: {result['age_minutes']}min ago")
                    print(f"   Keywords found:")
                    for kw, pts in result['keywords'][:5]:
                        print(f"     • {kw} (+{pts})")
                    print(f"   Link: {result['link']}")
    
    # Form 4 cluster analysis
    if args.form == '4':
        clusters = scan_form4_clusters(hours=args.hours)
        
        if clusters:
            print("\n🐺 INSIDER BUYING CLUSTERS DETECTED:")
            print()
            for ticker, info in clusters.items():
                print(f"  {info['signal']} {ticker}")
                print(f"    {info['count']} insiders bought")
                print(f"    Over {(info['last_filing'] - info['first_filing']).days} days")
                print()
    
    print()
    print("🐺 LLHR. SEE IT FIRST. TRADE IT SECOND. 🐺")
    print()


if __name__ == "__main__":
    main()
