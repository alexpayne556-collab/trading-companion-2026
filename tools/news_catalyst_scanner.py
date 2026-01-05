#!/usr/bin/env python3
"""
NEWS CATALYST SCANNER - FIND THE STORY BEFORE THE POP

Scans Yahoo Finance news for tickers mentioned in last 12 hours.
The big moves start with NEWS. Find the story, find the winner.

Usage:
    python3 news_catalyst_scanner.py
    python3 news_catalyst_scanner.py --hours 6  # Last 6 hours only
"""

import yfinance as yf
from datetime import datetime, timedelta
import json
from pathlib import Path
import argparse
import time
from collections import defaultdict

# Extended watchlist
WATCHLIST = [
    # Your positions
    'UUUU', 'USAR', 'AISP',
    # Nuclear
    'UEC', 'CCJ', 'SMR', 'LEU', 'DNN', 'NXE', 'OKLO',
    # Quantum (CES catalyst)
    'QBTS', 'IONQ', 'RGTI', 'QUBT', 'ARQQ',
    # Rare earth
    'MP', 'ALB', 'LAC',
    # Defense
    'CACI', 'LDOS', 'BAH', 'SAIC', 'CRWD', 'PANW',
    # Drones
    'AVAV', 'UAVS', 'JOBY', 'ACHR',
    # Space
    'ASTS', 'RKLB', 'LUNR', 'RDW', 'IRDM',
    # Crypto
    'COIN', 'HOOD', 'MSTR', 'MARA', 'RIOT',
    # Semi equipment
    'AMAT', 'LRCX', 'KLAC',
    # AI
    'NVDA', 'AMD', 'SMCI', 'DELL', 'PLTR', 'AI',
    # Robotics
    'ISRG', 'PATH', 'RR',
    # EV
    'TSLA', 'RIVN', 'LCID', 'ENVX',
]

class NewsCatalystScanner:
    def __init__(self, hours_back=12):
        self.hours_back = hours_back
        self.cutoff_time = datetime.now() - timedelta(hours=hours_back)
    
    def get_recent_news(self, ticker):
        """Get recent news for ticker"""
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if not news:
                return []
            
            recent_news = []
            for article in news[:10]:  # Check last 10 articles
                # Parse published time
                pub_time = article.get('providerPublishTime', 0)
                if pub_time:
                    pub_datetime = datetime.fromtimestamp(pub_time)
                    
                    # Check if within our window
                    if pub_datetime >= self.cutoff_time:
                        recent_news.append({
                            'title': article.get('title', 'No title'),
                            'publisher': article.get('publisher', 'Unknown'),
                            'link': article.get('link', ''),
                            'published': pub_datetime.strftime('%Y-%m-%d %H:%M ET'),
                            'hours_ago': (datetime.now() - pub_datetime).seconds // 3600
                        })
            
            return recent_news
            
        except Exception as e:
            return []
    
    def scan(self):
        """Scan for news catalysts"""
        print(f"\n📰 NEWS CATALYST SCANNER")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"   Scanning {len(WATCHLIST)} tickers")
        print(f"   Window: Last {self.hours_back} hours")
        print("=" * 80)
        
        print("\n   Scanning for recent news...")
        results = {}
        
        for ticker in WATCHLIST:
            print(f"      {ticker}...", end=' ', flush=True)
            
            news = self.get_recent_news(ticker)
            if news:
                results[ticker] = news
                print(f"✓ {len(news)} articles")
            else:
                print("✓")
            
            time.sleep(0.3)  # Rate limiting
        
        return results
    
    def display_results(self, results):
        """Display news catalysts"""
        if not results:
            print("\n📊 No recent news found on watchlist tickers.")
            print("\n🐺 This could mean:")
            print("   • Quiet news day")
            print("   • Try expanding --hours parameter")
            print("   • Check financial news sites manually")
            return
        
        # Count articles per ticker
        article_counts = {ticker: len(articles) for ticker, articles in results.items()}
        sorted_tickers = sorted(article_counts.items(), key=lambda x: x[1], reverse=True)
        
        print("\n" + "=" * 80)
        print("📰 NEWS CATALYSTS DETECTED")
        print("=" * 80)
        
        print(f"\n🔥 MOST MENTIONED ({len(results)} tickers with news):")
        print("=" * 80)
        
        for ticker, count in sorted_tickers:
            news_list = results[ticker]
            
            print(f"\n📌 {ticker} - {count} articles in last {self.hours_back}h")
            print("─" * 80)
            
            for article in news_list[:3]:  # Show top 3
                print(f"\n   📰 {article['title']}")
                print(f"      {article['publisher']} | {article['published']} ({article['hours_ago']}h ago)")
                print(f"      {article['link']}")
        
        print("\n" + "=" * 80)
        print("🐺 WOLF'S READ")
        print("=" * 80)
        
        # High-frequency tickers (3+ articles)
        high_freq = [ticker for ticker, count in sorted_tickers if count >= 3]
        
        if high_freq:
            print(f"\n   🚨 HIGH NEWS VOLUME (3+ articles):")
            for ticker in high_freq:
                count = article_counts[ticker]
                print(f"      • {ticker}: {count} articles = WATCH CLOSELY")
            print("\n   💡 Multiple articles = catalyst brewing, watch for price action")
        
        # Your positions
        your_tickers = ['UUUU', 'USAR', 'AISP']
        your_news = [ticker for ticker in your_tickers if ticker in results]
        
        if your_news:
            print(f"\n   🎯 YOUR POSITIONS WITH NEWS:")
            for ticker in your_news:
                count = len(results[ticker])
                latest = results[ticker][0]
                print(f"      • {ticker}: {count} articles")
                print(f"        Latest: \"{latest['title']}\"")
            print("\n   ⚠️ Read these BEFORE market open!")
        
        print("\n   🎯 WHAT TO DO:")
        print("      • Read full articles for tickers with 3+ mentions")
        print("      • Positive news + sector strength = buy opportunity")
        print("      • Negative news + volume = sell signal")
        print("      • News + pre-market gap = momentum trade setup")
        
        # Keyword analysis
        print("\n   💡 HOT KEYWORDS TO WATCH:")
        print("      • 'partnership', 'contract', 'deal' = BULLISH")
        print("      • 'upgrade', 'target raised' = BULLISH")
        print("      • 'downgrade', 'miss', 'warning' = BEARISH")
        print("      • 'investigation', 'lawsuit' = BEARISH")
    
    def save_results(self, results):
        """Save to JSON"""
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        output_file = log_dir / f"news_catalyst_{datetime.now().strftime('%Y-%m-%d_%H%M')}.json"
        
        with open(output_file, 'w') as f:
            json.dump({
                'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'hours_scanned': self.hours_back,
                'results': results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='News Catalyst Scanner')
    parser.add_argument('--hours', type=int, default=12, help='Hours to look back (default: 12)')
    
    args = parser.parse_args()
    
    scanner = NewsCatalystScanner(args.hours)
    results = scanner.scan()
    scanner.display_results(results)
    
    if results:
        scanner.save_results(results)
    
    print("\n🐺 AWOOOO! News catalyst scan complete.\n")
    print("💡 TIP: Run this at 6 AM to see overnight news before market opens")

if __name__ == '__main__':
    main()
