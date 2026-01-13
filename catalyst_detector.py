#!/usr/bin/env python3
"""
🐺 CATALYST DETECTOR - Catch Material News FAST

Scans news sources for material events:
- Dollar amounts relative to market cap
- Key triggers: FDA, contract, merger, NVIDIA, AI
- Float analysis for squeeze potential

Built by BROKKR after Fenrir couldn't deliver.
"""

import yfinance as yf
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
import sys
import os

# Add webapp to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'webapp'))

try:
    from intelligence_db import log_alert, log_catalyst
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


# High-impact keywords and their weights
KEYWORDS = {
    'critical': {  # Score +3
        'fda approval': 3,
        'fda cleared': 3,
        'phase 3': 3,
        'breakthrough': 3,
        'merger': 3,
        'acquisition': 3,
        'acquired': 3,
        'buyout': 3,
    },
    'high': {  # Score +2
        'nvidia': 2,
        'contract': 2,
        'partnership': 2,
        'deal': 2,
        'agreement': 2,
        'revenue': 2,
        'earnings': 2,
        'guidance': 2,
        'ai infrastructure': 2,
        'government contract': 2,
        'defense contract': 2,
    },
    'medium': {  # Score +1
        'expansion': 1,
        'launch': 1,
        'patent': 1,
        'clinical': 1,
        'trial': 1,
        'data': 1,
        'results': 1,
    }
}


def extract_dollar_amount(text):
    """Extract dollar amounts from text"""
    # Match patterns like $46M, $1.5B, $500,000
    patterns = [
        r'\$(\d+(?:\.\d+)?)\s*([BMK])',  # $46M, $1.5B
        r'\$(\d{1,3}(?:,\d{3})+)',  # $1,500,000
        r'\$(\d+(?:\.\d+)?)\s*(?:million|billion)',  # $46 million
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount = float(match.group(1).replace(',', ''))
            if len(match.groups()) > 1:
                multiplier = match.group(2).upper() if match.group(2) else ''
                if multiplier == 'B' or 'billion' in text.lower():
                    amount *= 1_000_000_000
                elif multiplier == 'M' or 'million' in text.lower():
                    amount *= 1_000_000
                elif multiplier == 'K':
                    amount *= 1_000
            return amount
    return None


def extract_ticker(text):
    """Try to extract ticker from headline or body"""
    # Common patterns: "XYZ Inc", "XYZ Corp", "(NASDAQ: XYZ)", "(NYSE: XYZ)"
    patterns = [
        r'\((?:NASDAQ|NYSE|AMEX|OTC):\s*([A-Z]{1,5})\)',
        r'\(([A-Z]{1,5})\)',
        r'^([A-Z]{2,5})\s+(?:Inc|Corp|Ltd|LLC)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def get_ticker_context(ticker):
    """Get float, market cap, price for context"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            'float': info.get('floatShares', 0),
            'market_cap': info.get('marketCap', 0),
            'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
            'shares_outstanding': info.get('sharesOutstanding', 0),
        }
    except:
        return None


def score_headline(headline, body=''):
    """Score a news headline for trading relevance"""
    text = (headline + ' ' + body).lower()
    
    score = 0
    flags = []
    
    for category, keywords in KEYWORDS.items():
        for keyword, weight in keywords.items():
            if keyword in text:
                score += weight
                flags.append(f"{category.upper()}: {keyword}")
    
    # Extract dollar amount
    dollar = extract_dollar_amount(headline + ' ' + body)
    if dollar:
        flags.append(f"$$: ${dollar:,.0f}")
    
    return score, flags, dollar


def calculate_materiality(dollar_amount, market_cap):
    """Calculate how material the news is relative to company size"""
    if not dollar_amount or not market_cap or market_cap == 0:
        return None
    
    return (dollar_amount / market_cap) * 100


def scrape_globenewswire():
    """Scrape GlobeNewswire for latest releases"""
    url = 'https://www.globenewswire.com/news-release'
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        releases = []
        for item in soup.select('.news-release'):
            headline = item.select_one('.headline')
            if headline:
                releases.append({
                    'source': 'GlobeNewswire',
                    'headline': headline.get_text(strip=True),
                    'timestamp': datetime.now().isoformat()
                })
        
        return releases[:20]  # Latest 20
    except Exception as e:
        print(f"Error scraping GlobeNewswire: {e}")
        return []


def scrape_prnewswire():
    """Scrape PRNewswire for latest releases"""
    url = 'https://www.prnewswire.com/news-releases/news-releases-list/'
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        releases = []
        for item in soup.select('.newsreleaseconsolidatelink'):
            headline = item.get_text(strip=True)
            if headline:
                releases.append({
                    'source': 'PRNewswire',
                    'headline': headline,
                    'timestamp': datetime.now().isoformat()
                })
        
        return releases[:20]
    except Exception as e:
        print(f"Error scraping PRNewswire: {e}")
        return []


def analyze_catalyst(headline, body=''):
    """Full catalyst analysis"""
    
    result = {
        'headline': headline,
        'score': 0,
        'flags': [],
        'dollar_amount': None,
        'ticker': None,
        'context': None,
        'materiality': None,
        'alert_level': 'LOW'
    }
    
    # Score the headline
    score, flags, dollar = score_headline(headline, body)
    result['score'] = score
    result['flags'] = flags
    result['dollar_amount'] = dollar
    
    # Extract ticker
    ticker = extract_ticker(headline + ' ' + body)
    result['ticker'] = ticker
    
    # Get ticker context if found
    if ticker:
        context = get_ticker_context(ticker)
        result['context'] = context
        
        # Calculate materiality
        if context and dollar:
            materiality = calculate_materiality(dollar, context.get('market_cap', 0))
            result['materiality'] = materiality
            
            # Set alert level based on materiality
            if materiality and materiality > 50:
                result['alert_level'] = 'CRITICAL'
            elif materiality and materiality > 20:
                result['alert_level'] = 'HIGH'
            elif score >= 3:
                result['alert_level'] = 'MEDIUM'
    
    return result


def simulate_aton():
    """Simulate what the detector would have caught for ATON"""
    
    print("\n" + "="*70)
    print("SIMULATION: ATON $46M NVIDIA Deal Detection")
    print("="*70)
    
    headline = "AlphaTON Capital Closes $46M AI Infrastructure Expansion to Address Significant NVIDIA GPU Demand"
    
    result = analyze_catalyst(headline)
    
    # Override ticker since ATON might not be in headline
    result['ticker'] = 'ATON'
    result['context'] = get_ticker_context('ATON')
    
    if result['context'] and result['dollar_amount']:
        result['materiality'] = calculate_materiality(
            result['dollar_amount'], 
            result['context'].get('market_cap', 0)
        )
    
    print(f"\n📰 Headline: {headline[:80]}...")
    print(f"\n📊 Score: {result['score']}")
    print(f"   Flags: {result['flags']}")
    print(f"   Dollar Amount: ${result['dollar_amount']:,.0f}" if result['dollar_amount'] else "   No dollar amount")
    print(f"\n🏷️  Extracted Ticker: {result['ticker']}")
    
    if result['context']:
        ctx = result['context']
        print(f"\n📈 Ticker Context:")
        print(f"   Float: {ctx.get('float', 'N/A'):,}")
        print(f"   Market Cap: ${ctx.get('market_cap', 0):,.0f}")
        print(f"   Price: ${ctx.get('price', 0):.2f}")
    
    if result['materiality']:
        print(f"\n⚠️  MATERIALITY: {result['materiality']:.0f}% of market cap")
        
        if result['materiality'] > 50:
            print("\n🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨")
            print("ALERT: Deal size EXCEEDS market cap!")
            print("This is EXTREMELY material. High probability of major move.")
            print("ACTION: Monitor immediately for entry opportunity.")
            print("🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨")
    
    return result


def scan_live_news():
    """Scan live news sources for catalysts"""
    
    print("\n" + "="*70)
    print("🐺 CATALYST DETECTOR")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    all_news = []
    
    # Scrape sources
    print("\n📰 Scraping GlobeNewswire...")
    gnw = scrape_globenewswire()
    print(f"   Found {len(gnw)} releases")
    all_news.extend(gnw)
    
    print("\n📰 Scraping PRNewswire...")
    prn = scrape_prnewswire()
    print(f"   Found {len(prn)} releases")
    all_news.extend(prn)
    
    # Analyze each
    print(f"\n📊 Analyzing {len(all_news)} news items...")
    
    alerts = []
    for news in all_news:
        result = analyze_catalyst(news['headline'])
        result['source'] = news['source']
        result['timestamp'] = news['timestamp']
        
        if result['score'] >= 2:
            alerts.append(result)
    
    # Print alerts
    print("\n" + "="*70)
    print(f"🚨 CATALYST ALERTS (Score >= 2)")
    print("="*70)
    
    if not alerts:
        print("\nNo high-scoring catalysts detected.")
    else:
        for alert in sorted(alerts, key=lambda x: x['score'], reverse=True):
            print(f"\n📰 [{alert['source']}] {alert['headline'][:70]}...")
            print(f"   Score: {alert['score']} | Flags: {', '.join(alert['flags'][:3])}")
            if alert['ticker']:
                print(f"   Ticker: {alert['ticker']}")
            if alert['dollar_amount']:
                print(f"   Amount: ${alert['dollar_amount']:,.0f}")
            if alert['materiality']:
                print(f"   Materiality: {alert['materiality']:.0f}% of market cap")
            
            # Log to database
            if DB_AVAILABLE and alert['ticker']:
                log_catalyst(
                    alert['ticker'],
                    f"{alert['source']}: {alert['headline'][:100]}",
                    'HEADLINE',
                    {'score': alert['score'], 'flags': alert['flags']}
                )
    
    return alerts


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Catalyst detector - Catch material news fast')
    parser.add_argument('command', choices=['scan', 'simulate', 'test'],
                       help='scan=live news, simulate=ATON example, test=single headline')
    parser.add_argument('--headline', help='Test a specific headline')
    
    args = parser.parse_args()
    
    if args.command == 'simulate':
        simulate_aton()
    elif args.command == 'scan':
        scan_live_news()
    elif args.command == 'test' and args.headline:
        result = analyze_catalyst(args.headline)
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
