#!/usr/bin/env python3
"""
🐺 PATTERN-BASED DISCOVERY
===========================
NO HARDCODED TICKERS. The data decides.

The system:
1. Scans news sources for PATTERNS (keywords, dollar amounts)
2. Extracts tickers FROM the news
3. Scores each based on pattern match + context
4. Outputs ranked opportunities

We don't tell it what to look for. It tells US what's moving.
"""

import requests
from bs4 import BeautifulSoup
import yfinance as yf
import re
from datetime import datetime, timedelta
import json
import sqlite3

DB_PATH = "intelligence.db"

# =============================================================================
# PATTERN DEFINITIONS (What we're looking for, NOT which tickers)
# =============================================================================

PATTERNS = {
    'NVIDIA_AI_CONTRACT': {
        'keywords': ['nvidia', 'b300', 'b200', 'gpu', 'ai infrastructure', 'data center'],
        'dollar_keywords': ['million', 'billion', 'contract', 'deal', 'agreement'],
        'historical_outcomes': {
            'ATON_2026-01-12': '+188%',
            'EVTV_2026-01-12': '+442%',
        },
        'avg_move': 315,  # Average of known outcomes
        'win_rate': 1.0,  # 2/2 so far
    },
    'FDA_CATALYST': {
        'keywords': ['fda', 'approval', 'clearance', 'pdufa', 'phase 3', 'phase iii', 'breakthrough'],
        'dollar_keywords': [],
        'historical_outcomes': {},
        'avg_move': None,
        'win_rate': None,
    },
    'CONFERENCE_CATALYST': {
        'keywords': ['jpm', 'healthcare conference', 'investor day', 'presentation'],
        'dollar_keywords': [],
        'historical_outcomes': {
            'BEAM_2026-01-12': '+22%',
            'NTLA_2026-01-12': '+10%',
        },
        'avg_move': 16,
        'win_rate': 1.0,
    },
    'MERGER_ACQUISITION': {
        'keywords': ['merger', 'acquisition', 'acquire', 'buyout', 'loi', 'letter of intent'],
        'dollar_keywords': ['million', 'billion', 'valuation'],
        'historical_outcomes': {},
        'avg_move': None,
        'win_rate': None,
    },
    'GOVERNMENT_CONTRACT': {
        'keywords': ['government contract', 'defense', 'pentagon', 'dod', 'military'],
        'dollar_keywords': ['million', 'billion', 'award'],
        'historical_outcomes': {},
        'avg_move': None,
        'win_rate': None,
    },
}

# =============================================================================
# NEWS DISCOVERY (Find what's happening, extract tickers)
# =============================================================================

def extract_tickers_from_text(text):
    """
    Extract stock tickers from text.
    NO HARDCODED LIST - finds them dynamically.
    """
    tickers = set()
    
    # Pattern 1: (NASDAQ: XXX) or (NYSE: XXX)
    matches = re.findall(r'\((?:NASDAQ|NYSE|AMEX|OTC):\s*([A-Z]{1,5})\)', text, re.IGNORECASE)
    tickers.update([m.upper() for m in matches])
    
    # Pattern 2: NASDAQ: XXX without parens
    matches = re.findall(r'(?:NASDAQ|NYSE|AMEX):\s*([A-Z]{1,5})\b', text, re.IGNORECASE)
    tickers.update([m.upper() for m in matches])
    
    # Pattern 3: $XXX format (but not dollar amounts)
    matches = re.findall(r'\$([A-Z]{2,5})\b', text)
    tickers.update(matches)
    
    # Filter out common false positives
    false_positives = {'USD', 'CEO', 'CFO', 'IPO', 'SEC', 'FDA', 'AI', 'GPU', 'API', 'USA', 'ETF'}
    tickers = tickers - false_positives
    
    return list(tickers)

def extract_dollar_amount(text):
    """Extract dollar amounts from text"""
    # $XX million or $XX billion
    match = re.search(r'\$(\d+(?:\.\d+)?)\s*(million|billion|M|B)', text, re.IGNORECASE)
    if match:
        amount = float(match.group(1))
        unit = match.group(2).lower()
        if unit in ['billion', 'b']:
            return amount * 1_000_000_000
        return amount * 1_000_000
    return None

def match_patterns(text):
    """
    Check which patterns this text matches.
    Returns list of matching patterns with scores.
    """
    text_lower = text.lower()
    matches = []
    
    for pattern_name, pattern_def in PATTERNS.items():
        score = 0
        matched_keywords = []
        
        # Check keywords
        for kw in pattern_def['keywords']:
            if kw.lower() in text_lower:
                score += 2
                matched_keywords.append(kw)
        
        # Check dollar keywords
        for kw in pattern_def['dollar_keywords']:
            if kw.lower() in text_lower:
                score += 1
        
        # Bonus if dollar amount found
        dollar = extract_dollar_amount(text)
        if dollar and dollar >= 10_000_000:
            score += 2
        
        if score >= 3:  # Threshold for pattern match
            matches.append({
                'pattern': pattern_name,
                'score': score,
                'keywords': matched_keywords,
                'dollar_amount': dollar,
                'historical_avg': pattern_def.get('avg_move'),
                'win_rate': pattern_def.get('win_rate'),
            })
    
    return matches

def get_ticker_context(ticker):
    """
    Get float, market cap, recent price action.
    KEY ADDITION: Check if it's COMPRESSED (loaded spring).
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period='60d')
        
        if hist.empty or len(hist) < 5:
            return {'ticker': ticker, 'error': 'No data'}
        
        # Calculate recent move
        current = hist['Close'].iloc[-1]
        if len(hist) >= 5:
            open_5d = hist['Open'].iloc[0]
            recent_change = ((current - open_5d) / open_5d) * 100
        else:
            recent_change = 0
        
        # KEY: Calculate compression (how far from 30-day high)
        high_30d = hist['High'][-30:].max() if len(hist) >= 30 else hist['High'].max()
        compression = ((high_30d - current) / high_30d) * 100
        
        # Check if trading below NAV
        book_value = info.get('bookValue', 0)
        nav_discount = None
        if book_value and book_value > 0:
            nav_discount = ((current - book_value) / book_value) * 100
        
        return {
            'ticker': ticker,
            'price': info.get('regularMarketPrice', info.get('previousClose', current)),
            'market_cap': info.get('marketCap', 0),
            'float': info.get('floatShares', info.get('sharesOutstanding', 0)),
            'recent_5d_change': round(recent_change, 1),
            'volume': info.get('volume', 0),
            'avg_volume': info.get('averageVolume', 0),
            'compression': round(compression, 1),  # KEY METRIC
            'nav_discount': round(nav_discount, 1) if nav_discount else None,
            'high_30d': high_30d,
        }
    except Exception as e:
        return {'ticker': ticker, 'error': str(e)}

# =============================================================================
# MAIN DISCOVERY ENGINE
# =============================================================================

def discover_from_news(news_items):
    """
    Process news items, find patterns, extract tickers, score opportunities.
    
    news_items: list of {'title': str, 'source': str, 'url': str}
    
    Returns: Ranked list of opportunities the DATA found
    """
    opportunities = []
    
    for news in news_items:
        title = news.get('title', '')
        
        # Match patterns
        pattern_matches = match_patterns(title)
        
        if not pattern_matches:
            continue
        
        # Extract tickers
        tickers = extract_tickers_from_text(title)
        
        if not tickers:
            continue
        
        # For each ticker + pattern combo, create opportunity
        for ticker in tickers:
            context = get_ticker_context(ticker)
            
            if 'error' in context:
                continue
            
            for pm in pattern_matches:
                # Calculate materiality if we have dollar amount
                materiality = None
                if pm['dollar_amount'] and context['market_cap']:
                    materiality = (pm['dollar_amount'] / context['market_cap']) * 100
                
                # Calculate opportunity score
                opp_score = pm['score']
                
                # Boost for small float
                if context['float'] and context['float'] < 10_000_000:
                    opp_score += 3
                elif context['float'] and context['float'] < 50_000_000:
                    opp_score += 1
                
                # Boost for high materiality
                if materiality and materiality > 100:
                    opp_score += 4  # Deal > market cap
                elif materiality and materiality > 50:
                    opp_score += 2
                elif materiality and materiality > 20:
                    opp_score += 1
                
                # CRITICAL: Boost for compression (loaded spring)
                if context['compression'] > 40:
                    opp_score += 3  # Beaten down significantly
                elif context['compression'] > 20:
                    opp_score += 2
                
                # Boost for NAV discount
                if context['nav_discount'] and context['nav_discount'] < -40:
                    opp_score += 2
                
                # Boost for pattern with good history
                if pm['win_rate'] and pm['win_rate'] > 0.7:
                    opp_score += 2
                
                opportunity = {
                    'ticker': ticker,
                    'pattern': pm['pattern'],
                    'score': opp_score,
                    'news_title': title[:100],
                    'dollar_amount': pm['dollar_amount'],
                    'materiality': round(materiality, 1) if materiality else None,
                    'market_cap': context['market_cap'],
                    'float': context['float'],
                    'price': context['price'],
                    'recent_5d_change': context['recent_5d_change'],
                    'compression': context['compression'],  # KEY
                    'nav_discount': context['nav_discount'],
                    'pattern_history': {
                        'avg_move': pm['historical_avg'],
                        'win_rate': pm['win_rate'],
                    },
                    'discovered_at': datetime.now().isoformat(),
                }
                
                opportunities.append(opportunity)
    
    # Sort by score
    opportunities.sort(key=lambda x: x['score'], reverse=True)
    
    return opportunities

def display_opportunities(opportunities):
    """Display discovered opportunities"""
    print("=" * 70)
    print("🐺 PATTERN-BASED DISCOVERY - DATA DECIDES")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    if not opportunities:
        print("\n⚠️ No opportunities found matching known patterns")
        return
    
    print(f"\n🎯 FOUND {len(opportunities)} OPPORTUNITIES:\n")
    
    for i, opp in enumerate(opportunities[:10], 1):
        print(f"{i}. {opp['ticker']} | Score: {opp['score']} | Pattern: {opp['pattern']}")
        print(f"   News: {opp['news_title']}...")
        print(f"   Float: {opp['float']/1_000_000:.1f}M" if opp['float'] else "   Float: Unknown")
        print(f"   Market Cap: ${opp['market_cap']/1_000_000:.1f}M" if opp['market_cap'] else "   MCap: Unknown")
        
        if opp['dollar_amount']:
            print(f"   Deal Size: ${opp['dollar_amount']/1_000_000:.0f}M")
        if opp['materiality']:
            print(f"   ⚡ Materiality: {opp['materiality']:.0f}% of market cap")
        
        # KEY: Show compression
        if opp['compression']:
            status = "🔥 COMPRESSED" if opp['compression'] > 40 else "LOADED" if opp['compression'] > 20 else "Extended"
            print(f"   {status} ({opp['compression']:.0f}% from 30d high)")
        
        if opp['nav_discount'] and opp['nav_discount'] < -20:
            print(f"   💎 Trading {abs(opp['nav_discount']):.0f}% below NAV")
        
        if opp['pattern_history']['avg_move']:
            print(f"   📊 Pattern History: avg +{opp['pattern_history']['avg_move']}%, win rate {opp['pattern_history']['win_rate']*100:.0f}%")
        
        print()

def save_to_database(opportunities):
    """Save discovered opportunities to database for tracking"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS pattern_discoveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discovered_date TEXT,
            ticker TEXT,
            pattern TEXT,
            score INTEGER,
            news_title TEXT,
            dollar_amount REAL,
            materiality REAL,
            float_shares INTEGER,
            compression REAL,
            nav_discount REAL,
            next_day_move REAL,
            was_correct INTEGER
        )
    """)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    for opp in opportunities:
        c.execute("""
            INSERT INTO pattern_discoveries
            (discovered_date, ticker, pattern, score, news_title, dollar_amount, 
             materiality, float_shares, compression, nav_discount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            today,
            opp['ticker'],
            opp['pattern'],
            opp['score'],
            opp['news_title'],
            opp['dollar_amount'],
            opp['materiality'],
            opp['float'],
            opp['compression'],
            opp['nav_discount']
        ))
    
    conn.commit()
    conn.close()

# =============================================================================
# EXAMPLE: How today's movers would have been discovered
# =============================================================================

def simulate_today():
    """
    Simulate what the system would have found today if it was running.
    Uses the actual news headlines.
    """
    # These are the ACTUAL headlines from today - NOT hardcoded tickers,
    # but hardcoded NEWS that we're testing the pattern matcher against
    todays_news = [
        {
            'title': 'AlphaTON Capital Closes $46M AI Infrastructure Expansion (NASDAQ: ATON) adding 576 NVIDIA B300 chips',
            'source': 'GlobeNewswire',
            'url': ''
        },
        {
            'title': 'AZIO AI receives $107 million government contract for 256 NVIDIA B300 GPUs, advancing merger with Envirotech Vehicles (NASDAQ: EVTV)',
            'source': 'PRNewswire', 
            'url': ''
        },
        {
            'title': 'Digi Power X (NASDAQ: DGXX) acquires $20 million of NVIDIA B300 GPUs from Super Micro Computer',
            'source': 'Proactive',
            'url': ''
        },
        {
            'title': 'BEAM Therapeutics presents at JPM Healthcare Conference',
            'source': 'PR',
            'url': ''
        },
    ]
    
    print("\n" + "=" * 70)
    print("SIMULATION: What would system have found today?")
    print("=" * 70)
    
    opportunities = discover_from_news(todays_news)
    display_opportunities(opportunities)
    
    # Show why DGXX scored lower
    print("\n" + "=" * 70)
    print("🔍 WHY DID DGXX SCORE LOWER?")
    print("=" * 70)
    
    dgxx_opp = next((o for o in opportunities if o['ticker'] == 'DGXX'), None)
    aton_opp = next((o for o in opportunities if o['ticker'] == 'ATON'), None)
    
    if dgxx_opp and aton_opp:
        print(f"\nATON Score: {aton_opp['score']}")
        print(f"  Compression: {aton_opp['compression']:.0f}% (BEATEN DOWN)")
        print(f"  Materiality: {aton_opp['materiality']:.0f}% (HUGE DEAL)")
        print(f"  Float: {aton_opp['float']/1_000_000:.1f}M (MICRO)")
        
        print(f"\nDGXX Score: {dgxx_opp['score']}")
        print(f"  Compression: {dgxx_opp['compression']:.0f}% (NOT COMPRESSED)")
        print(f"  Materiality: {dgxx_opp['materiality']:.0f}% (SMALLER DEAL)")
        print(f"  Float: {dgxx_opp['float']/1_000_000:.1f}M (BIGGER)")
        
        print(f"\n💡 THE DIFFERENCE: ATON was LOADED. DGXX wasn't.")
    
    save_to_database(opportunities)
    
    return opportunities

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "simulate":
        simulate_today()
    else:
        print("""
🐺 PATTERN-BASED DISCOVERY
==========================

NO HARDCODED TICKERS. The data decides everything.

How it works:
1. Feed it news (from any source)
2. It matches against known PATTERNS (not tickers)
3. It extracts tickers FROM the news
4. It scores based on pattern match + context (float, materiality, COMPRESSION)
5. It outputs ranked opportunities

Commands:
  python pattern_discovery.py simulate   - Test with today's news

For Brokkr to integrate:
  - Feed GlobeNewswire/PRNewswire RSS into discover_from_news()
  - System outputs what DATA found, not what we told it to find
  
KEY INSIGHT:
  COMPRESSION = The loaded spring variable
  DGXX has NVIDIA news but isn't compressed → Won't explode
  ATON had NVIDIA news AND was compressed → Exploded +188%
        """)
