#!/usr/bin/env python3
"""
🐺 NEWS CATALYST TRACKER
=========================
Tracks news catalysts across the AI fuel chain
Searches for contracts, partnerships, government announcements

Uses free RSS/news APIs

Usage:
    python news_catalyst_tracker.py                  # Full scan
    python news_catalyst_tracker.py --sector NUCLEAR # Specific sector
    python news_catalyst_tracker.py --live           # Auto-refresh mode
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pytz
import argparse
import time
import re
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# SECTOR KEYWORDS FOR NEWS TRACKING
# ============================================================

SECTOR_KEYWORDS = {
    'NUCLEAR': {
        'tickers': ['UUUU', 'SMR', 'LEU', 'OKLO', 'CCJ', 'DNN', 'UEC', 'NXE', 'NNE'],
        'keywords': ['uranium', 'nuclear', 'SMR', 'small modular reactor', 'nuclear power', 'NRC', 'DOE nuclear', 'data center power', 'energy fuel'],
        'priority_terms': ['contract', 'award', 'DOE', 'government', 'hyperscaler', 'Microsoft', 'Google', 'Amazon']
    },
    'COOLING': {
        'tickers': ['VRT', 'MOD', 'NVT'],
        'keywords': ['data center cooling', 'liquid cooling', 'thermal management', 'rack density', 'AI cooling'],
        'priority_terms': ['contract', 'hyperscaler', 'GPU cooling', 'NVIDIA']
    },
    'PHOTONICS': {
        'tickers': ['LITE', 'AAOI', 'COHR', 'GFS'],
        'keywords': ['optical', 'photonics', 'transceiver', 'silicon photonics', 'data center interconnect', '800G', '1.6T'],
        'priority_terms': ['hyperscaler', 'NVIDIA', 'AI network', 'bandwidth']
    },
    'NETWORKING': {
        'tickers': ['ANET', 'CRDO', 'FN', 'CIEN'],
        'keywords': ['data center networking', 'ethernet', 'switching', 'AI cluster', 'InfiniBand'],
        'priority_terms': ['hyperscaler', 'cloud', 'AI infrastructure']
    },
    'STORAGE': {
        'tickers': ['MU', 'WDC', 'STX'],
        'keywords': ['HBM', 'high bandwidth memory', 'NAND', 'SSD', 'AI memory', 'data storage'],
        'priority_terms': ['NVIDIA', 'AI training', 'GPU memory']
    },
    'CHIPS': {
        'tickers': ['AMD', 'MRVL', 'AVGO', 'INTC', 'AMKR'],
        'keywords': ['AI chip', 'GPU', 'accelerator', 'semiconductor', 'AI inference', 'AI training'],
        'priority_terms': ['hyperscaler', 'custom chip', 'data center']
    },
    'QUANTUM': {
        'tickers': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
        'keywords': ['quantum computing', 'quantum', 'qubit', 'quantum advantage', 'quantum supremacy'],
        'priority_terms': ['government', 'DOE', 'contract', 'breakthrough']
    },
    'SPACE': {
        'tickers': ['LUNR', 'RKLB', 'RDW', 'ASTS', 'SIDU', 'BKSY', 'PL'],
        'keywords': ['space', 'satellite', 'lunar', 'defense', 'launch', 'NASA', 'SpaceX'],
        'priority_terms': ['contract', 'award', 'government', 'DOD', 'NASA']
    },
    'AI_SOFTWARE': {
        'tickers': ['PLTR', 'AI', 'SOUN', 'PATH', 'UPST'],
        'keywords': ['AI software', 'enterprise AI', 'machine learning', 'AI platform', 'generative AI'],
        'priority_terms': ['contract', 'enterprise', 'government', 'partnership']
    },
    'DC_BUILDERS': {
        'tickers': ['SMCI', 'EME', 'CLS', 'FIX', 'EQIX', 'DLR'],
        'keywords': ['data center', 'AI infrastructure', 'hyperscale', 'colocation', 'server'],
        'priority_terms': ['hyperscaler', 'expansion', 'new facility', 'contract']
    }
}

# Free news sources
NEWS_SOURCES = [
    {
        'name': 'Google News',
        'url': 'https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en',
        'type': 'rss'
    },
    {
        'name': 'Yahoo Finance',
        'url': 'https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US',
        'type': 'rss'
    }
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# ============================================================
# NEWS FETCHING FUNCTIONS
# ============================================================

def fetch_google_news(query, max_results=10):
    """Fetch news from Google News RSS"""
    try:
        url = NEWS_SOURCES[0]['url'].format(query=query.replace(' ', '+'))
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            return []
        
        root = ET.fromstring(response.content)
        items = []
        
        for item in root.findall('.//item')[:max_results]:
            title = item.find('title')
            link = item.find('link')
            pub_date = item.find('pubDate')
            
            if title is not None:
                items.append({
                    'title': title.text,
                    'link': link.text if link is not None else '',
                    'date': pub_date.text if pub_date is not None else '',
                    'source': 'Google News'
                })
        
        return items
    except Exception as e:
        return []

def fetch_yahoo_news(ticker, max_results=5):
    """Fetch news from Yahoo Finance RSS"""
    try:
        url = NEWS_SOURCES[1]['url'].format(ticker=ticker)
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            return []
        
        root = ET.fromstring(response.content)
        items = []
        
        for item in root.findall('.//item')[:max_results]:
            title = item.find('title')
            link = item.find('link')
            pub_date = item.find('pubDate')
            
            if title is not None:
                items.append({
                    'title': title.text,
                    'link': link.text if link is not None else '',
                    'date': pub_date.text if pub_date is not None else '',
                    'source': 'Yahoo Finance'
                })
        
        return items
    except Exception as e:
        return []

def score_headline(headline, keywords, priority_terms):
    """Score a headline based on keyword matches"""
    headline_lower = headline.lower()
    score = 0
    matches = []
    
    for kw in keywords:
        if kw.lower() in headline_lower:
            score += 1
            matches.append(kw)
    
    for pt in priority_terms:
        if pt.lower() in headline_lower:
            score += 3  # Priority terms worth more
            matches.append(f"⭐{pt}")
    
    return score, matches

def scan_sector_news(sector_name, sector_info, max_per_ticker=5):
    """Scan news for a sector"""
    results = []
    
    # Search for each ticker
    for ticker in sector_info['tickers']:
        news = fetch_yahoo_news(ticker, max_per_ticker)
        for item in news:
            score, matches = score_headline(
                item['title'], 
                sector_info['keywords'], 
                sector_info['priority_terms']
            )
            item['ticker'] = ticker
            item['sector'] = sector_name
            item['score'] = score
            item['matches'] = matches
            results.append(item)
        time.sleep(0.3)  # Rate limit
    
    # Search for sector keywords
    for kw in sector_info['keywords'][:3]:  # Top 3 keywords
        news = fetch_google_news(kw, 5)
        for item in news:
            score, matches = score_headline(
                item['title'], 
                sector_info['keywords'], 
                sector_info['priority_terms']
            )
            item['ticker'] = 'SECTOR'
            item['sector'] = sector_name
            item['score'] = score
            item['matches'] = matches
            # Check if related to any tickers
            for t in sector_info['tickers']:
                if t in item['title'].upper():
                    item['ticker'] = t
                    item['score'] += 2
            results.append(item)
        time.sleep(0.3)
    
    return results

def scan_all_news(sectors_filter=None):
    """Scan all sectors for news"""
    print(f"\n⚡ SCANNING NEWS CATALYSTS...")
    
    all_news = []
    
    for sector_name, sector_info in SECTOR_KEYWORDS.items():
        if sectors_filter and sector_name not in sectors_filter:
            continue
        
        print(f"   Scanning {sector_name}...", end='\r')
        news = scan_sector_news(sector_name, sector_info)
        all_news.extend(news)
    
    print(f"\n   ✓ Found {len(all_news)} news items")
    
    return all_news

def get_eastern_time():
    eastern = pytz.timezone('US/Eastern')
    return datetime.now(eastern)

def display_news_report(all_news):
    """Display news report"""
    et_now = get_eastern_time()
    
    print("\n" + "=" * 100)
    print(f"🐺 NEWS CATALYST TRACKER — {et_now.strftime('%I:%M %p ET')}")
    print("=" * 100)
    
    # High score items (catalysts)
    high_score = [n for n in all_news if n['score'] >= 2]
    high_score_sorted = sorted(high_score, key=lambda x: x['score'], reverse=True)
    
    print(f"\n🔥 HIGH-PRIORITY CATALYSTS (Score >= 2)\n")
    
    if high_score_sorted:
        for n in high_score_sorted[:15]:
            ticker_str = f"[{n['ticker']}]" if n['ticker'] != 'SECTOR' else f"[{n['sector']}]"
            print(f"   {ticker_str:<12} | Score: {n['score']} | {n['title'][:70]}...")
            if n['matches']:
                print(f"                  Matches: {', '.join(n['matches'][:5])}")
    else:
        print("   No high-priority catalysts found")
    
    # By sector
    print("\n" + "=" * 100)
    print("📰 NEWS BY SECTOR")
    print("=" * 100)
    
    sectors_seen = set()
    for n in all_news:
        sectors_seen.add(n['sector'])
    
    for sector in sorted(sectors_seen):
        sector_news = [n for n in all_news if n['sector'] == sector]
        sector_sorted = sorted(sector_news, key=lambda x: x['score'], reverse=True)
        
        print(f"\n{sector}:")
        
        # Deduplicate by title similarity
        seen_titles = set()
        for n in sector_sorted[:5]:
            title_key = n['title'][:50]
            if title_key in seen_titles:
                continue
            seen_titles.add(title_key)
            
            ticker_str = n['ticker'] if n['ticker'] != 'SECTOR' else ''
            print(f"   [{ticker_str:<6}] {n['title'][:75]}...")
    
    # Contract/Award mentions
    print("\n" + "=" * 100)
    print("💰 CONTRACT/AWARD MENTIONS")
    print("=" * 100)
    
    contract_news = [n for n in all_news if any(term in n['title'].lower() for term in ['contract', 'award', 'deal', 'partnership', 'agreement'])]
    
    if contract_news:
        for n in contract_news[:10]:
            print(f"   [{n['ticker']}] {n['title'][:80]}...")
    else:
        print("   No contract/award mentions found")
    
    # Government/DOE mentions
    print("\n" + "=" * 100)
    print("🏛️ GOVERNMENT/REGULATORY MENTIONS")
    print("=" * 100)
    
    gov_news = [n for n in all_news if any(term in n['title'].lower() for term in ['government', 'doe', 'nasa', 'dod', 'congress', 'bill', 'regulation', 'nrc'])]
    
    if gov_news:
        for n in gov_news[:10]:
            print(f"   [{n['ticker']}] {n['title'][:80]}...")
    else:
        print("   No government mentions found")
    
    # Wolf's catalyst read
    print("\n" + "=" * 100)
    print("🐺 WOLF'S CATALYST READ")
    print("=" * 100)
    
    # Find hottest sector by news score
    sector_scores = {}
    for n in all_news:
        if n['sector'] not in sector_scores:
            sector_scores[n['sector']] = 0
        sector_scores[n['sector']] += n['score']
    
    if sector_scores:
        hottest = max(sector_scores.items(), key=lambda x: x[1])
        print(f"\n   🔥 HOTTEST NEWS SECTOR: {hottest[0]} (score: {hottest[1]})")
    
    # Tickers with most mentions
    ticker_counts = {}
    for n in all_news:
        if n['ticker'] != 'SECTOR':
            if n['ticker'] not in ticker_counts:
                ticker_counts[n['ticker']] = 0
            ticker_counts[n['ticker']] += 1
    
    if ticker_counts:
        print("\n   📊 MOST MENTIONED TICKERS:")
        for ticker, count in sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"      {ticker}: {count} mentions")
    
    # Potential catalyst plays
    catalyst_plays = [n for n in high_score_sorted if n['ticker'] != 'SECTOR'][:5]
    if catalyst_plays:
        print("\n   🎯 POTENTIAL CATALYST PLAYS:")
        for n in catalyst_plays:
            print(f"      {n['ticker']} — {n['title'][:60]}...")

def run_live_scanner(sectors=None, refresh_interval=300):
    """Run in live mode"""
    print("\n🐺 NEWS CATALYST TRACKER — LIVE MODE")
    print(f"   Refreshing every {refresh_interval} seconds")
    print("   Press Ctrl+C to stop\n")
    
    try:
        while True:
            print("\033[2J\033[H", end="")
            news = scan_all_news(sectors)
            display_news_report(news)
            print(f"\n   Next refresh in {refresh_interval} seconds... (Ctrl+C to stop)")
            time.sleep(refresh_interval)
    except KeyboardInterrupt:
        print("\n\n🐺 Tracker stopped.")

def main():
    parser = argparse.ArgumentParser(description='News Catalyst Tracker')
    parser.add_argument('--sector', type=str, help='Filter by sector')
    parser.add_argument('--live', action='store_true', help='Run in live mode')
    parser.add_argument('--refresh', type=int, default=300, help='Refresh interval')
    
    args = parser.parse_args()
    
    sectors = None
    if args.sector:
        sectors = [args.sector.upper()]
    
    if args.live:
        run_live_scanner(sectors, args.refresh)
    else:
        news = scan_all_news(sectors)
        display_news_report(news)

if __name__ == "__main__":
    main()
