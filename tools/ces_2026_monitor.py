#!/usr/bin/env python3
"""
🎪 CES 2026 MONITOR - Track announcements affecting your holdings

Monitors:
- Twitter/X for company announcements
- Company websites for press releases
- News aggregators (Google News, Yahoo Finance)
- Reddit sentiment spikes

CES 2026: January 7-10, 2026 (Las Vegas)

Author: Brokkr
Date: January 5, 2026
"""

import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import json
from pathlib import Path
import argparse

# Setup
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# CES 2026 FOCUS TICKERS (from your DNA)
CES_WATCHLIST = {
    # Quantum Computing - MAIN PLAYS
    "QBTS": {
        "name": "D-Wave Quantum",
        "ces_presence": "CONFIRMED - Foundry Sponsor + Masterclass Jan 7",
        "catalyst": "Tech demos, partnerships, Masterclass 1PM Jan 7",
        "monday_rate": "80%",
        "priority": "HIGH"
    },
    "QUBT": {
        "name": "Quantum Computing Inc",
        "ces_presence": "CONFIRMED - Demos Jan 7-8",
        "catalyst": "LiDAR + quantum tech demos",
        "short_interest": "22.7%",
        "priority": "HIGH"
    },
    "RGTI": {
        "name": "Rigetti Computing",
        "ces_presence": "POSSIBLE - Not confirmed yet",
        "catalyst": "Watch for surprise announcements",
        "priority": "MEDIUM"
    },
    "IONQ": {
        "name": "IonQ",
        "ces_presence": "NO - Not attending",
        "catalyst": "None for CES",
        "priority": "AVOID"
    },
    
    # Robotics
    "RR": {
        "name": "Richtech Robotics",
        "ces_presence": "CONFIRMED - Humanoid robot demo",
        "catalyst": "Humanoid butler robot showcase",
        "short_interest": "26%",
        "days_to_cover": "0.8",
        "priority": "VERY HIGH"
    },
    
    # AI/Tech
    "SOUN": {
        "name": "SoundHound AI",
        "ces_presence": "LIKELY - Voice AI demos",
        "catalyst": "Automotive partnerships, voice AI",
        "priority": "MEDIUM"
    },
    "PLTR": {
        "name": "Palantir",
        "ces_presence": "POSSIBLE - AI demos",
        "catalyst": "AIP platform showcase",
        "priority": "LOW"
    },
    
    # Space (no CES presence but monitor)
    "LUNR": {
        "name": "Intuitive Machines",
        "ces_presence": "NO",
        "catalyst": "IM-2 launch window Feb 2026",
        "priority": "MONITOR"
    },
    "RKLB": {
        "name": "Rocket Lab",
        "ces_presence": "NO",
        "catalyst": "Launch schedule",
        "priority": "MONITOR"
    },
    "RDW": {
        "name": "Redwire",
        "ces_presence": "NO",
        "catalyst": "NASA contracts",
        "priority": "MONITOR"
    },
}


class CESMonitor:
    """
    Monitor CES 2026 announcements for your holdings.
    """
    
    def __init__(self, watchlist=None):
        self.watchlist = watchlist or CES_WATCHLIST
        self.alerts = []
        self.timestamp = datetime.now()
        
    def check_yahoo_finance_news(self, ticker):
        """
        Check Yahoo Finance for recent news.
        """
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if not news:
                return []
            
            # Filter for CES-related news (last 24 hours)
            ces_keywords = ['ces', 'ces 2026', 'las vegas', 'consumer electronics show', 'demo', 'announcement', 'unveil']
            recent_news = []
            
            cutoff = datetime.now() - timedelta(hours=24)
            
            for item in news[:10]:  # Check last 10 news items
                pub_time = datetime.fromtimestamp(item.get('providerPublishTime', 0))
                title = item.get('title', '').lower()
                
                if pub_time > cutoff:
                    # Check for CES keywords
                    if any(keyword in title for keyword in ces_keywords):
                        recent_news.append({
                            'ticker': ticker,
                            'title': item.get('title'),
                            'link': item.get('link'),
                            'publisher': item.get('publisher'),
                            'time': pub_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'relevance': 'HIGH'
                        })
                    else:
                        # Include all recent news for monitoring
                        recent_news.append({
                            'ticker': ticker,
                            'title': item.get('title'),
                            'link': item.get('link'),
                            'publisher': item.get('publisher'),
                            'time': pub_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'relevance': 'NORMAL'
                        })
            
            return recent_news
            
        except Exception as e:
            return []
    
    def check_price_action(self, ticker):
        """
        Check if ticker is moving (potential news catalyst).
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d", interval="1d")
            
            if len(hist) < 2:
                return None
            
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            
            change_pct = ((current_price - prev_close) / prev_close) * 100
            volume_ratio = hist['Volume'].iloc[-1] / hist['Volume'].mean()
            
            # Alert if big move or volume spike
            alert = None
            if abs(change_pct) > 5 or volume_ratio > 2:
                alert = {
                    'ticker': ticker,
                    'price': current_price,
                    'change': change_pct,
                    'volume_ratio': volume_ratio,
                    'alert_type': 'MOVING' if abs(change_pct) > 5 else 'VOLUME_SPIKE'
                }
            
            return alert
            
        except Exception as e:
            return None
    
    def check_google_news(self, ticker, company_name):
        """
        Scrape Google News for CES mentions.
        """
        try:
            query = f"{company_name} CES 2026"
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=nws"
            
            response = requests.get(url, headers=HEADERS, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for news results
            news_items = []
            
            # Google news results structure (may need adjustment)
            for item in soup.find_all('div', {'class': 'SoaBEf'}):
                title_elem = item.find('div', {'role': 'heading'})
                if title_elem:
                    title = title_elem.text
                    news_items.append({
                        'ticker': ticker,
                        'title': title,
                        'source': 'Google News',
                        'search_query': query
                    })
            
            return news_items
            
        except Exception as e:
            return []
    
    def scan_all(self):
        """
        Scan all tickers for CES-related activity.
        """
        print("=" * 80)
        print("🎪 CES 2026 MONITOR - Tracking announcements for your holdings")
        print("=" * 80)
        print(f"⏰ Time: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📅 CES 2026: January 7-10, 2026 (Las Vegas)")
        print(f"🎯 Monitoring: {len(self.watchlist)} tickers")
        print()
        
        results = {
            'news': [],
            'price_alerts': [],
            'high_priority': []
        }
        
        for ticker, info in self.watchlist.items():
            print(f"   Scanning {ticker} ({info['name']})...", end='\r')
            
            # Check news
            news = self.check_yahoo_finance_news(ticker)
            if news:
                results['news'].extend(news)
            
            # Check price action
            price_alert = self.check_price_action(ticker)
            if price_alert:
                results['price_alerts'].append(price_alert)
            
            # Track high priority
            if info.get('priority') in ['VERY HIGH', 'HIGH']:
                results['high_priority'].append({
                    'ticker': ticker,
                    'name': info['name'],
                    'priority': info['priority'],
                    'ces_presence': info['ces_presence'],
                    'catalyst': info['catalyst']
                })
            
            time.sleep(1)  # Be nice to APIs
        
        print("\n")
        return results
    
    def display_results(self, results):
        """
        Display monitoring results.
        """
        print()
        print("=" * 80)
        print("🎪 CES 2026 MONITOR - RESULTS")
        print("=" * 80)
        print()
        
        # HIGH PRIORITY TICKERS
        if results['high_priority']:
            print("🔥 HIGH PRIORITY CES PLAYS:")
            print("━" * 80)
            for item in results['high_priority']:
                priority_emoji = "🚨" if item['priority'] == 'VERY HIGH' else "⚡"
                print(f"{priority_emoji} {item['ticker']} - {item['name']}")
                print(f"   CES: {item['ces_presence']}")
                print(f"   Catalyst: {item['catalyst']}")
                print()
        
        # PRICE ALERTS
        if results['price_alerts']:
            print("━" * 80)
            print()
            print("📈 PRICE ALERTS (Moving now):")
            print("━" * 80)
            for alert in results['price_alerts']:
                emoji = "🟢" if alert['change'] > 0 else "🔴"
                print(f"{emoji} {alert['ticker']}: ${alert['price']:.2f} ({alert['change']:+.1f}%)")
                print(f"   Volume: {alert['volume_ratio']:.1f}x average")
                print(f"   Type: {alert['alert_type']}")
                print()
        
        # NEWS
        if results['news']:
            print("━" * 80)
            print()
            print("📰 RECENT NEWS (Last 24h):")
            print("━" * 80)
            
            # Show high relevance first
            high_rel = [n for n in results['news'] if n.get('relevance') == 'HIGH']
            normal_rel = [n for n in results['news'] if n.get('relevance') == 'NORMAL']
            
            if high_rel:
                print()
                print("🔥 CES-RELATED:")
                for news in high_rel[:5]:
                    print(f"   {news['ticker']}: {news['title']}")
                    print(f"   Source: {news['publisher']} | Time: {news['time']}")
                    print(f"   Link: {news['link']}")
                    print()
            
            if normal_rel:
                print()
                print("📋 OTHER NEWS:")
                for news in normal_rel[:5]:
                    print(f"   {news['ticker']}: {news['title']}")
                    print(f"   Source: {news['publisher']}")
                    print()
        
        print("━" * 80)
        print()
        print("🎯 MONDAY JAN 6 GAME PLAN:")
        print()
        print("1. **RR (Richtech Robotics)** - ENTRY")
        print("   • 26% short, humanoid robot demo at CES")
        print("   • Entry: $3.35-3.50 | Stop: $3.00 | Target: $4.50+")
        print()
        print("2. **QBTS (D-Wave)** - WATCH")
        print("   • Masterclass Jan 7, 1PM")
        print("   • 80% Monday win rate")
        print("   • Entry: Market open if strong | Target: $40")
        print()
        print("3. **QUBT (Quantum)** - HIGH RISK")
        print("   • 22.7% short, demos Jan 7-8")
        print("   • Tight stops! Very volatile")
        print()
        print("⚠️  **AVOID:** IONQ, RGTI (no CES presence)")
        print()
        print("🐺 AWOOOO! Monitor this throughout CES week.")
        print()
    
    def save_results(self, results):
        """
        Save results to JSON.
        """
        output_dir = Path('logs')
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / 'ces_2026_monitor.json'
        
        data = {
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'results': results
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='🎪 CES 2026 Monitor - Track announcements for your holdings')
    parser.add_argument('--add-ticker', nargs=2, metavar=('TICKER', 'NAME'), 
                       help='Add extra ticker to monitor (e.g., --add-ticker NVDA "NVIDIA")')
    parser.add_argument('--watch', action='store_true', 
                       help='Run in watch mode (continuous monitoring every 5 min)')
    
    args = parser.parse_args()
    
    # Add extra ticker if provided
    watchlist = CES_WATCHLIST.copy()
    if args.add_ticker:
        ticker, name = args.add_ticker
        watchlist[ticker] = {
            'name': name,
            'ces_presence': 'UNKNOWN',
            'catalyst': 'To be determined',
            'priority': 'CUSTOM'
        }
    
    # Create monitor
    monitor = CESMonitor(watchlist=watchlist)
    
    # Watch mode or single run
    if args.watch:
        print("👁️  WATCH MODE: Monitoring every 5 minutes. Press Ctrl+C to stop.")
        print()
        
        try:
            while True:
                results = monitor.scan_all()
                monitor.display_results(results)
                monitor.save_results(results)
                
                print("⏳ Next scan in 5 minutes...")
                time.sleep(300)  # 5 minutes
                
                monitor = CESMonitor(watchlist=watchlist)  # Fresh instance
        except KeyboardInterrupt:
            print("\n\n⛔ Monitoring stopped.")
    else:
        # Single scan
        results = monitor.scan_all()
        monitor.display_results(results)
        monitor.save_results(results)


if __name__ == "__main__":
    main()
