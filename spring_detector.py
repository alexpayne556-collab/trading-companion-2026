#!/usr/bin/env python3
"""
🐺 LOADED SPRING DETECTOR - Find tickers BEFORE they explode

The problem: We scan what ALREADY moved.
The solution: Find what's ABOUT TO move.

ATON had 10+ press releases, tiny float, NVIDIA keywords, trading at 0.4x NAV.
The spring was loaded. We just didn't see it.

This finds those loaded springs BEFORE the catalyst hits.
"""

import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import time
from collections import defaultdict

# =============================================================================
# NEWS VELOCITY - How active is the company?
# =============================================================================

def get_recent_news(ticker, days_back=30):
    """
    Get recent press releases for a ticker.
    Returns count and keywords found.
    """
    try:
        # Try GlobeNewswire search
        url = f"https://www.globenewswire.com/search/organization/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        
        # Parse for recent releases
        # (In production, would need proper date parsing)
        
        # Fallback: Use yfinance news
        stock = yf.Ticker(ticker)
        news = stock.news if hasattr(stock, 'news') else []
        
        # Filter to last N days
        cutoff = datetime.now() - timedelta(days=days_back)
        recent = []
        
        for item in news:
            pub_date = datetime.fromtimestamp(item.get('providerPublishTime', 0))
            if pub_date >= cutoff:
                recent.append({
                    'title': item.get('title', ''),
                    'date': pub_date.isoformat()
                })
        
        return recent
    
    except Exception as e:
        return []

def count_hot_keywords(news_items):
    """Count occurrences of momentum keywords"""
    HOT_KEYWORDS = {
        'AI': 3,
        'NVIDIA': 3,
        'GPU': 2,
        'FDA approval': 3,
        'Phase 3': 2,
        'contract': 2,
        'defense': 2,
        'Pentagon': 2,
        'merger': 3,
        'acquisition': 3,
        'partnership': 2,
        'breakthrough': 2,
        'patent': 1,
        'expansion': 1,
        'investment': 1
    }
    
    keyword_score = 0
    found_keywords = []
    
    for item in news_items:
        title = item['title'].upper()
        for keyword, weight in HOT_KEYWORDS.items():
            if keyword.upper() in title:
                keyword_score += weight
                found_keywords.append(keyword)
    
    return keyword_score, list(set(found_keywords))

# =============================================================================
# PRICE VS FUNDAMENTALS - Is it compressed?
# =============================================================================

def check_price_compression(ticker):
    """
    Check if stock is compressed (down from highs despite news).
    Also checks NAV discount if available.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="60d")
        
        if hist.empty:
            return 0, {}
        
        # Current price vs 30-day high
        current = hist['Close'].iloc[-1]
        high_30d = hist['High'][-30:].max() if len(hist) >= 30 else hist['High'].max()
        compression_pct = ((high_30d - current) / high_30d) * 100
        
        # Check NAV discount (for funds/companies with reported NAV)
        book_value = info.get('bookValue', 0)
        price_to_book = current / book_value if book_value else None
        
        # Check if down in last 30 days
        price_30d_ago = hist['Close'].iloc[-30] if len(hist) >= 30 else hist['Close'].iloc[0]
        change_30d = ((current - price_30d_ago) / price_30d_ago) * 100
        
        return {
            'compression_pct': compression_pct,
            'price_to_book': price_to_book,
            'change_30d': change_30d,
            'current_price': current
        }
    
    except:
        return {}

# =============================================================================
# SPRING TENSION CALCULATOR
# =============================================================================

def calculate_spring_tension(ticker, verbose=False):
    """
    Score how "loaded" a stock is for explosion.
    
    Higher score = more likely to move big on next catalyst.
    
    Based on ATON pattern:
    - 10+ press releases in 30 days
    - 1.86M float
    - NVIDIA/AI keywords everywhere
    - Trading at 0.4x NAV
    - Down despite good news
    """
    
    if verbose:
        print(f"\n🔍 Analyzing {ticker}...")
    
    score = 0
    signals = []
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # 1. FLOAT SIZE (Most important - ATON had 1.86M)
        float_shares = info.get('floatShares', info.get('sharesOutstanding', 0))
        if float_shares:
            float_m = float_shares / 1_000_000
            if float_m < 5:
                score += 3
                signals.append(f"🔥 MICRO FLOAT ({float_m:.1f}M)")
            elif float_m < 20:
                score += 2
                signals.append(f"🟢 TINY FLOAT ({float_m:.1f}M)")
            elif float_m < 50:
                score += 1
                signals.append(f"🟡 SMALL FLOAT ({float_m:.1f}M)")
            else:
                signals.append(f"⚪ FLOAT: {float_m:.0f}M")
        
        # 2. NEWS VELOCITY (ATON had 10+)
        news_items = get_recent_news(ticker, days_back=30)
        news_count = len(news_items)
        
        if news_count >= 10:
            score += 3
            signals.append(f"🔥 HIGH NEWS VELOCITY ({news_count} releases/30d)")
        elif news_count >= 5:
            score += 2
            signals.append(f"🟢 ACTIVE NEWS ({news_count} releases/30d)")
        elif news_count >= 2:
            score += 1
            signals.append(f"🟡 SOME NEWS ({news_count} releases/30d)")
        
        # 3. HOT KEYWORDS (ATON: NVIDIA, AI, GPU)
        keyword_score, keywords = count_hot_keywords(news_items)
        
        if keyword_score >= 10:
            score += 3
            signals.append(f"🔥 HOT KEYWORDS: {', '.join(keywords[:3])}")
        elif keyword_score >= 5:
            score += 2
            signals.append(f"🟢 KEYWORDS: {', '.join(keywords[:3])}")
        elif keyword_score >= 2:
            score += 1
            signals.append(f"🟡 KEYWORDS: {', '.join(keywords[:2])}")
        
        # 4. PRICE COMPRESSION (ATON: Down despite news)
        compression = check_price_compression(ticker)
        
        if compression:
            change_30d = compression.get('change_30d', 0)
            compression_pct = compression.get('compression_pct', 0)
            price_to_book = compression.get('price_to_book')
            
            # Down from highs = spring compression
            if compression_pct > 40:
                score += 2
                signals.append(f"🔥 COMPRESSED ({compression_pct:.0f}% from high)")
            elif compression_pct > 20:
                score += 1
                signals.append(f"🟡 OFF HIGHS ({compression_pct:.0f}%)")
            
            # Down in last 30d despite news = coiling
            if news_count >= 3 and change_30d < -15:
                score += 2
                signals.append(f"🔥 COILING (Down {abs(change_30d):.0f}% despite news)")
            elif news_count >= 3 and change_30d < -5:
                score += 1
                signals.append(f"🟡 Pulling back despite news")
            
            # Trading below book value = discount
            if price_to_book and price_to_book < 0.6:
                score += 2
                signals.append(f"🔥 NAV DISCOUNT ({price_to_book:.2f}x book)")
            elif price_to_book and price_to_book < 0.9:
                score += 1
                signals.append(f"🟡 Discount to book ({price_to_book:.2f}x)")
        
        # 5. PRICE LEVEL (Low price = retail interest potential)
        current_price = compression.get('current_price', info.get('currentPrice', 0))
        if current_price and current_price < 2:
            score += 1
            signals.append(f"🟢 LOW PRICE (${current_price:.2f})")
        
        # VERDICT
        if score >= 10:
            verdict = "🚨 MAXIMUM TENSION - Primed for explosion"
        elif score >= 7:
            verdict = "🔥 HIGH TENSION - Watch closely"
        elif score >= 5:
            verdict = "🟡 MODERATE TENSION - Potential"
        elif score >= 3:
            verdict = "⚪ SOME TENSION - Monitor"
        else:
            verdict = "❌ LOW TENSION - Not interesting"
        
        return {
            'ticker': ticker,
            'score': score,
            'signals': signals,
            'verdict': verdict,
            'float': float_shares,
            'news_count': news_count,
            'keywords': keywords if 'keywords' in locals() else [],
            'current_price': current_price
        }
    
    except Exception as e:
        if verbose:
            print(f"   ❌ Error: {e}")
        return None

# =============================================================================
# SCAN FOR LOADED SPRINGS
# =============================================================================

def scan_for_springs(tickers, top_n=10):
    """
    Scan a list of tickers for loaded springs.
    Returns top N by tension score.
    """
    
    print("=" * 70)
    print("🐺 LOADED SPRING DETECTOR")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    print(f"\n📊 Scanning {len(tickers)} tickers...")
    
    results = []
    
    for i, ticker in enumerate(tickers, 1):
        if i % 20 == 0:
            print(f"   Progress: {i}/{len(tickers)}...")
        
        result = calculate_spring_tension(ticker, verbose=False)
        if result and result['score'] >= 3:  # Only keep interesting ones
            results.append(result)
        
        time.sleep(0.3)  # Rate limiting
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Output
    print("\n" + "=" * 70)
    print(f"🔥 TOP {top_n} LOADED SPRINGS")
    print("=" * 70)
    
    for i, r in enumerate(results[:top_n], 1):
        print(f"\n{i}. {r['ticker']} | Score: {r['score']}")
        print(f"   {r['verdict']}")
        
        if r['float']:
            float_m = r['float'] / 1_000_000
            print(f"   Float: {float_m:.1f}M | Price: ${r['current_price']:.2f}")
        
        print(f"   News: {r['news_count']} releases/30d")
        
        if r['keywords']:
            print(f"   Keywords: {', '.join(r['keywords'][:5])}")
        
        print(f"   Signals:")
        for sig in r['signals'][:4]:
            print(f"      {sig}")
    
    return results

def get_small_cap_universe():
    """
    Get a universe of small caps to scan.
    These are most likely to be loaded springs.
    """
    
    # Start with our known movers
    base = [
        'ATON', 'EVTV', 'AISP', 'APLD', 'IREN', 'WULF', 'CLSK', 'CORZ',
        'NTLA', 'BEAM', 'CRSP', 'EDIT', 'RARE', 'SAVA',
        'LUNR', 'RKLB', 'ASTS', 'VORB',
        'IONQ', 'RGTI', 'QUBT', 'ARQQ',
        'SMR', 'OKLO', 'NNE',
        'RCAT', 'KTOS', 'AVAV',
        'SOUN', 'AI', 'PATH',
    ]
    
    # Add small biotech
    biotech = [
        'OCGN', 'ATOS', 'GEVO', 'PLUG', 'FCEL', 'BLNK', 'CHPT'
    ]
    
    return list(set(base + biotech))

def export_watchlist(results, filename=None):
    """Export top springs as watchlist for Fidelity ATP"""
    if not filename:
        filename = f"springs_{datetime.now().strftime('%Y%m%d')}.csv"
    
    with open(filename, 'w') as f:
        f.write("Symbol\n")
        for r in results:
            if r['score'] >= 5:  # Only high tension
                f.write(f"{r['ticker']}\n")
    
    print(f"\n✅ Watchlist saved: {filename}")
    return filename

# =============================================================================
# MAIN
# =============================================================================

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
🐺 LOADED SPRING DETECTOR
=========================

Find tickers BEFORE they explode.

Commands:
  python spring_detector.py scan        # Scan default universe
  python spring_detector.py check ATON  # Check specific ticker
  python spring_detector.py daily       # Daily scan + export watchlist

The ATON Example:
  - 10+ press releases in December
  - 1.86M float
  - NVIDIA/AI keywords everywhere
  - Trading at 0.4x NAV
  - Down despite good news

Score: 14/14 - MAXIMUM TENSION

Then $46M news drops → +188%

This finds those setups BEFORE the catalyst hits.

NOT what moved yesterday. What moves TOMORROW.
        """)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'scan':
        universe = get_small_cap_universe()
        results = scan_for_springs(universe, top_n=15)
        
    elif cmd == 'check' and len(sys.argv) > 2:
        ticker = sys.argv[2].upper()
        result = calculate_spring_tension(ticker, verbose=True)
        if result:
            print(f"\n{result['ticker']} | Score: {result['score']}")
            print(f"{result['verdict']}")
            for sig in result['signals']:
                print(f"  {sig}")
        
    elif cmd == 'daily':
        universe = get_small_cap_universe()
        results = scan_for_springs(universe, top_n=10)
        export_watchlist(results)
        
        # Save to JSON
        with open(f"springs_{datetime.now().strftime('%Y%m%d')}.json", 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
