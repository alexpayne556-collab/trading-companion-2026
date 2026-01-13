#!/usr/bin/env python3
"""
REAL TRADING INTELLIGENCE - No BS, Just Results

Scrapes news, detects catalysts, alerts on opportunities
No paid APIs required
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'webapp'))

from news_scraper import NewsAggregator, HOT_KEYWORDS, SEARCH_KEYWORDS
from real_alerts import AlertSystem
import yfinance as yf
from datetime import datetime
import time
import argparse

def check_price_movement(ticker, baseline=None):
    """Check if ticker is moving"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1d', interval='5m')
        
        if hist.empty:
            return None
        
        current = float(hist['Close'].iloc[-1])
        
        if baseline:
            change_pct = ((current - baseline) / baseline) * 100
        else:
            open_price = float(hist['Open'].iloc[0])
            change_pct = ((current - open_price) / open_price) * 100
        
        return {
            'ticker': ticker,
            'price': current,
            'change_pct': change_pct,
            'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0
        }
    except:
        return None

def scan_for_opportunities():
    """Main scanning logic"""
    print("\n" + "="*80)
    print("🎯 SCANNING FOR OPPORTUNITIES")
    print("="*80 + "\n")
    
    alerts = AlertSystem()
    scraper = NewsAggregator()
    
    # 1. Scrape news for all keyword sets
    print("📰 Scraping news sources...")
    all_news = []
    for keywords in SEARCH_KEYWORDS:
        print(f"   Searching: {' + '.join(keywords)}")
        articles = scraper.scrape_all(keywords, [])
        all_news.extend(articles)
        time.sleep(1)
    
    # 2. Filter for hot news
    hot_news = scraper.filter_hot_news(all_news, HOT_KEYWORDS)
    
    print(f"\n📊 RESULTS:")
    print(f"   Total articles: {len(all_news)}")
    print(f"   Hot catalysts: {len(hot_news)}")
    
    # 3. Extract tickers and check prices
    if hot_news:
        print(f"\n🔥 HOT NEWS FOUND:\n")
        
        tickers_to_check = set()
        for article in hot_news[:10]:  # Top 10
            print(f"   • {article['title']}")
            print(f"     Source: {article['source']} | URL: {article['url'][:50]}...")
            
            if article.get('tickers'):
                tickers_to_check.update(article['tickers'])
            
            # Alert on hot news
            alerts.news_alert(
                article['title'],
                article.get('tickers', []),
                article['url']
            )
        
        # 4. Check prices for mentioned tickers
        if tickers_to_check:
            print(f"\n💰 CHECKING PRICES FOR: {', '.join(list(tickers_to_check)[:10])}")
            
            for ticker in list(tickers_to_check)[:10]:  # Limit to 10
                movement = check_price_movement(ticker)
                if movement:
                    change = movement['change_pct']
                    price = movement['price']
                    
                    print(f"   {ticker}: ${price:.2f} ({change:+.1f}%)")
                    
                    if abs(change) >= 100:
                        alerts.whale_alert(ticker, change, price, catalyst='News detected')
                    elif abs(change) >= 20:
                        alerts.fish_alert(ticker, change, price, catalyst='News detected')
                
                time.sleep(0.5)
    else:
        print("\n   No hot catalysts found in this scan")
    
    print("\n" + "="*80)
    print(f"Scan complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

def watch_ticker(ticker, alert_threshold=5.0):
    """Watch a specific ticker continuously"""
    print(f"\n👁️  WATCHING {ticker} - Alert on {alert_threshold}%+ moves\n")
    
    alerts = AlertSystem()
    
    # Get baseline
    baseline_data = check_price_movement(ticker)
    if not baseline_data:
        print(f"❌ Could not fetch {ticker}")
        return
    
    baseline = baseline_data['price']
    print(f"Baseline: ${baseline:.2f}\n")
    
    try:
        while True:
            current = check_price_movement(ticker, baseline)
            if current:
                change = current['change_pct']
                price = current['price']
                
                status = "📈" if change > 0 else "📉"
                print(f"{status} {ticker}: ${price:.2f} ({change:+.1f}%) | {datetime.now().strftime('%H:%M:%S')}")
                
                if abs(change) >= alert_threshold:
                    if abs(change) >= 100:
                        alerts.whale_alert(ticker, change, price)
                    elif abs(change) >= 20:
                        alerts.fish_alert(ticker, change, price)
            
            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        print(f"\n\nStopped watching {ticker}")

def show_recent_alerts():
    """Show recent alerts from log"""
    alerts = AlertSystem()
    recent = alerts.get_recent_alerts(50)
    
    print("\n" + "="*80)
    print("📋 RECENT ALERTS")
    print("="*80 + "\n")
    
    if recent:
        for line in recent:
            print(line.strip())
    else:
        print("No alerts yet")
    
    print()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Real Trading Intelligence')
    parser.add_argument('command', choices=['scan', 'watch', 'alerts'], 
                       help='scan: Search for opportunities | watch TICKER: Monitor ticker | alerts: Show recent alerts')
    parser.add_argument('ticker', nargs='?', help='Ticker to watch')
    parser.add_argument('--threshold', type=float, default=5.0, help='Alert threshold %')
    
    args = parser.parse_args()
    
    if args.command == 'scan':
        scan_for_opportunities()
    elif args.command == 'watch':
        if not args.ticker:
            print("❌ Provide ticker: python hunt.py watch ATON")
        else:
            watch_ticker(args.ticker.upper(), args.threshold)
    elif args.command == 'alerts':
        show_recent_alerts()
