#!/usr/bin/env python3
"""
Production Trading Dashboard - Direct live data with learning system
"""

from flask import Flask, render_template, jsonify
import yfinance as yf
from datetime import datetime
import threading
import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from intelligence_db import (
    log_scan, log_alert, log_catalyst,
    get_pattern_stats, get_ticker_history, get_recent_catalysts,
    get_active_positions, get_recent_alerts
)

sys.path.insert(0, '/workspaces/trading-companion-2026')
try:
    from news_scraper import NewsAggregator, HOT_KEYWORDS, SEARCH_KEYWORDS
    NEWS_SCRAPER = NewsAggregator()
except:
    NEWS_SCRAPER = None
    print("⚠️  News scraper not available")

app = Flask(__name__)

# Initialize learning database on import (not at module level)
def init_db():
    from intelligence_db import init_intelligence_db
    init_intelligence_db()
    
threading.Thread(target=init_db, daemon=True).start()

# Load universe from file
def load_universe():
    """Load trading universe from file"""
    universe_file = '/workspaces/trading-companion-2026/universe.txt'
    tickers = []
    
    if os.path.exists(universe_file):
        with open(universe_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                ticker = line.split()[0]
                if ticker and ticker.isupper():
                    tickers.append(ticker)
    
    # Fallback
    if not tickers:
        tickers = ['ATON', 'EVTV', 'LVLU', 'NTLA', 'BEAM', 'RARE']
    
    return tickers

# State
WATCHLIST = load_universe()
CACHE = {'last_scan': None, 'movements': [], 'stats': {}, 'catalysts': []}
CACHE_LOCK = threading.Lock()


def get_price_data(ticker):
    """Get live price data"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1d', interval='5m')
        
        if hist.empty or len(hist) < 2:
            hist = stock.history(period='5d')
            if hist.empty:
                return None
        
        current = float(hist['Close'].iloc[-1])
        open_price = float(hist['Open'].iloc[0])
        change_pct = ((current - open_price) / open_price) * 100
        volume = int(hist['Volume'].sum()) if 'Volume' in hist else 0
        
        return {
            'ticker': ticker,
            'price': current,
            'open': open_price,
            'change_pct': change_pct,
            'volume': volume
        }
    except:
        return None


def scan_watchlist():
    """Scan all tickers and log to learning database"""
    movements = []
    stats = {'whale': 0, 'fish': 0, 'bass': 0, 'nibble': 0, 'total': 0}
    
    for ticker in WATCHLIST:
        data = get_price_data(ticker)
        if data:
            change = data['change_pct']
            
            # Log every scan to learning database
            tier = None
            if abs(change) >= 5:
                # Classify
                if abs(change) >= 100:
                    tier = 'WHALE'
                    stats['whale'] += 1
                elif abs(change) >= 20:
                    tier = 'FISH'
                    stats['fish'] += 1
                elif abs(change) >= 10:
                    tier = 'BASS'
                    stats['bass'] += 1
                else:
                    tier = 'NIBBLE'
                    stats['nibble'] += 1
                
                stats['total'] += 1
                
                movements.append({
                    'symbol': ticker,
                    'price': round(data['price'], 2),
                    'change_pct': round(change, 1),
                    'volume': data['volume'],
                    'tier': tier,
                    'detected_at': datetime.now().isoformat()
                })
                
                # Log alert for significant moves
                if abs(change) >= 20:
                    log_alert(tier, ticker, f"{tier}: {ticker} {change:+.1f}%", {
                        'price': data['price'],
                        'volume': data['volume']
                    })
            
            # Log all scans (for learning)
            log_scan(ticker, data['price'], data['volume'], change, tier)
        
        time.sleep(0.2)
    
    return movements, stats


def auto_refresh():
    """Background refresh every 60s"""
    scan_counter = 0
    while True:
        try:
            # Scan prices
            movements, stats = scan_watchlist()
            with CACHE_LOCK:
                CACHE['movements'] = movements
                CACHE['stats'] = stats
                CACHE['last_scan'] = datetime.now().isoformat()
            print(f"✅ Scanned: {stats['total']} movers found")
            
            # Scrape news every 10 scans (10 minutes)
            scan_counter += 1
            if NEWS_SCRAPER and scan_counter % 10 == 0:
                try:
                    print("📰 Scraping news...")
                    catalysts = []
                    for keywords in SEARCH_KEYWORDS[:3]:  # Limit to 3 searches
                        articles = NEWS_SCRAPER.scrape_all(keywords, [])
                        hot = NEWS_SCRAPER.filter_hot_news(articles, HOT_KEYWORDS)
                        for article in hot[:5]:  # Top 5 per search
                            catalysts.append(article)
                            # Log to database
                            tickers = article.get('tickers', [])
                            if tickers:
                                log_catalyst(
                                    tickers[0],
                                    'NEWS',
                                    article['title'],
                                    article['url'],
                                    ', '.join(keywords)
                                )
                    
                    with CACHE_LOCK:
                        CACHE['catalysts'] = catalysts[-20:]  # Keep last 20
                    print(f"📰 Found {len(catalysts)} catalysts")
                except Exception as e:
                    print(f"⚠️  News scrape error: {e}")
                    
        except Exception as e:
            print(f"❌ Scan error: {e}")
        
        time.sleep(60)


@app.route('/')
def index():
    return render_template('full.html')


@app.route('/api/scan')
def api_scan():
    """Force immediate scan"""
    movements, stats = scan_watchlist()
    with CACHE_LOCK:
        CACHE['movements'] = movements
        CACHE['stats'] = stats
        CACHE['last_scan'] = datetime.now().isoformat()
    
    return jsonify({
        'movements': movements,
        'stats': stats,
        'last_scan': CACHE['last_scan']
    })


@app.route('/api/data')
def api_data():
    """Get cached data"""
    with CACHE_LOCK:
        return jsonify({
            'movements': CACHE['movements'],
            'stats': CACHE['stats'],
            'last_scan': CACHE['last_scan']
        })


@app.route('/api/intelligence/patterns')
def api_patterns():
    """Get pattern learning statistics"""
    patterns = {}
    for pattern in ['GPU_WHALE', 'CLINICAL_BINARY', 'DEFENSE_RUNNER', 'MULTIDAY_RUNNER']:
        stats = get_pattern_stats(pattern)
        if stats:
            patterns[pattern] = stats
    return jsonify(patterns)


@app.route('/api/intelligence/history/<ticker>')
def api_history(ticker):
    """Get historical data for a ticker"""
    history = get_ticker_history(ticker.upper(), days=30)
    return jsonify(history)


@app.route('/api/intelligence/catalysts')
def api_catalysts():
    """Get recent catalysts"""
    catalysts = get_recent_catalysts(hours=24)
    return jsonify(catalysts)


@app.route('/api/intelligence/positions')
def api_positions():
    """Get active positions"""
    positions = get_active_positions()
    return jsonify(positions)


@app.route('/api/intelligence/alerts')
def api_alerts():
    """Get recent alerts"""
    alerts = get_recent_alerts(count=50)
    return jsonify(alerts)


@app.route('/api/forensics/<ticker>')
def api_forensics(ticker):
    """Deep forensic analysis of a ticker's recent move"""
    try:
        from forensics import analyze_move
        from datetime import datetime
        
        # Analyze today's move
        today = datetime.now().strftime('%Y-%m-%d')
        result = analyze_move(ticker.upper(), today)
        
        return jsonify(result if result else {'error': 'No data'})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/catalysts/live')
def api_catalysts_live():
    """Get cached catalysts from news scraper"""
    with CACHE_LOCK:
        catalysts = CACHE.get('catalysts', [])
    return jsonify(catalysts)


if __name__ == '__main__':
    print("\n" + "="*80)
    print("🎯 PRODUCTION TRADING DASHBOARD")
    print("="*80)
    print(f"URL: http://localhost:8080")
    print(f"Watching: {len(WATCHLIST)} tickers")
    print(f"Auto-refresh: Every 60 seconds")
    print("="*80 + "\n")
    
    # Start background refresh
    refresh_thread = threading.Thread(target=auto_refresh, daemon=True)
    refresh_thread.start()
    
    # Initial scan
    movements, stats = scan_watchlist()
    CACHE['movements'] = movements
    CACHE['stats'] = stats
    CACHE['last_scan'] = datetime.now().isoformat()
    
    print(f"✅ Initial scan: {stats['total']} movers\n")
    
    app.run(host='0.0.0.0', port=8080, debug=False)
