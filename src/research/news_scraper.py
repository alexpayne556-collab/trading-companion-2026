#!/usr/bin/env python3
"""
🐺 NEWS SCRAPER - Free News Aggregation

Scrapes news from free sources:
- Finviz (stock-specific news)
- Yahoo Finance RSS
- Google News RSS

No API keys needed - all free web scraping

Author: Brokkr (Brother Mode)
Date: January 2, 2026
"""

import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import List, Dict, Optional
import time


class NewsScraper:
    """
    Scrapes news from free sources
    Filters by ticker and keywords
    """
    
    def __init__(self):
        self.news_dir = Path('logs/news')
        self.news_dir.mkdir(parents=True, exist_ok=True)
        
        # Keywords that signal important catalysts
        self.catalyst_keywords = [
            'contract', 'award', 'partnership', 'agreement',
            'upgrade', 'downgrade', 'initiated', 'coverage',
            'earnings', 'revenue', 'beat', 'miss', 'guidance',
            'fda', 'approval', 'cleared', 'breakthrough',
            'acquisition', 'merger', 'buyout',
            'dividend', 'buyback', 'split'
        ]
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_finviz_news(self, ticker: str) -> List[Dict]:
        """
        Scrape news from Finviz (free, no API key)
        Most reliable source for stock-specific news
        """
        news_items = []
        
        try:
            url = f'https://finviz.com/quote.ashx?t={ticker}'
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return news_items
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news table
            news_table = soup.find('table', {'class': 'fullview-news-outer'})
            
            if not news_table:
                return news_items
            
            # Parse news rows
            rows = news_table.find_all('tr')
            
            for row in rows[:10]:  # Top 10 news items
                try:
                    # Get date/time
                    date_cell = row.find('td', {'align': 'right'})
                    if not date_cell:
                        continue
                    
                    date_text = date_cell.text.strip()
                    
                    # Get link and title
                    link_cell = row.find('a')
                    if not link_cell:
                        continue
                    
                    title = link_cell.text.strip()
                    link = link_cell.get('href', '')
                    
                    # Parse datetime
                    news_datetime = self._parse_finviz_datetime(date_text)
                    
                    # Check for catalyst keywords
                    title_lower = title.lower()
                    matched_keywords = [kw for kw in self.catalyst_keywords if kw in title_lower]
                    
                    news_items.append({
                        'ticker': ticker,
                        'title': title,
                        'link': link,
                        'datetime': news_datetime,
                        'source': 'Finviz',
                        'catalyst_keywords': matched_keywords,
                        'is_catalyst': len(matched_keywords) > 0
                    })
                
                except Exception:
                    continue
        
        except Exception as e:
            print(f"⚠️ Error scraping Finviz for {ticker}: {e}")
        
        return news_items
    
    def get_yahoo_rss_news(self, ticker: str) -> List[Dict]:
        """
        Get news from Yahoo Finance RSS feed (free)
        """
        news_items = []
        
        try:
            url = f'https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US'
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:10]:
                try:
                    title = entry.get('title', '')
                    link = entry.get('link', '')
                    published = entry.get('published', '')
                    
                    # Parse datetime
                    if published:
                        news_datetime = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %z').isoformat()
                    else:
                        news_datetime = datetime.now().isoformat()
                    
                    # Check for catalyst keywords
                    title_lower = title.lower()
                    matched_keywords = [kw for kw in self.catalyst_keywords if kw in title_lower]
                    
                    news_items.append({
                        'ticker': ticker,
                        'title': title,
                        'link': link,
                        'datetime': news_datetime,
                        'source': 'Yahoo Finance',
                        'catalyst_keywords': matched_keywords,
                        'is_catalyst': len(matched_keywords) > 0
                    })
                
                except Exception:
                    continue
        
        except Exception as e:
            print(f"⚠️ Error fetching Yahoo RSS for {ticker}: {e}")
        
        return news_items
    
    def get_google_news(self, ticker: str) -> List[Dict]:
        """
        Get news from Google News RSS (free)
        """
        news_items = []
        
        try:
            url = f'https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en'
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:10]:
                try:
                    title = entry.get('title', '')
                    link = entry.get('link', '')
                    published = entry.get('published', '')
                    
                    # Parse datetime
                    if published:
                        news_datetime = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %Z').isoformat()
                    else:
                        news_datetime = datetime.now().isoformat()
                    
                    # Check for catalyst keywords
                    title_lower = title.lower()
                    matched_keywords = [kw for kw in self.catalyst_keywords if kw in title_lower]
                    
                    news_items.append({
                        'ticker': ticker,
                        'title': title,
                        'link': link,
                        'datetime': news_datetime,
                        'source': 'Google News',
                        'catalyst_keywords': matched_keywords,
                        'is_catalyst': len(matched_keywords) > 0
                    })
                
                except Exception:
                    continue
        
        except Exception as e:
            print(f"⚠️ Error fetching Google News for {ticker}: {e}")
        
        return news_items
    
    def get_all_news(self, ticker: str) -> List[Dict]:
        """
        Aggregate news from all sources
        Returns combined, deduplicated, sorted list
        """
        print(f"\n📰 Fetching news for {ticker}...")
        
        all_news = []
        
        # Finviz (most reliable)
        finviz_news = self.get_finviz_news(ticker)
        all_news.extend(finviz_news)
        print(f"   Finviz: {len(finviz_news)} articles")
        
        time.sleep(1)  # Rate limiting
        
        # Yahoo RSS
        yahoo_news = self.get_yahoo_rss_news(ticker)
        all_news.extend(yahoo_news)
        print(f"   Yahoo: {len(yahoo_news)} articles")
        
        time.sleep(1)  # Rate limiting
        
        # Google News
        google_news = self.get_google_news(ticker)
        all_news.extend(google_news)
        print(f"   Google: {len(google_news)} articles")
        
        # Deduplicate by title similarity
        all_news = self._deduplicate_news(all_news)
        
        # Sort by datetime (newest first)
        all_news.sort(key=lambda x: x['datetime'], reverse=True)
        
        print(f"   Total: {len(all_news)} unique articles")
        
        return all_news
    
    def scan_watchlist_news(self, tickers: List[str]) -> Dict[str, List[Dict]]:
        """
        Scan news for entire watchlist
        Returns dict of {ticker: news_items}
        """
        print(f"\n🔍 SCANNING NEWS FOR {len(tickers)} TICKERS")
        print("=" * 70)
        
        news_by_ticker = {}
        
        for ticker in tickers:
            news = self.get_all_news(ticker)
            
            # Only include if there's catalyst news
            catalyst_news = [n for n in news if n['is_catalyst']]
            
            if catalyst_news:
                news_by_ticker[ticker] = catalyst_news
                print(f"   🎯 {ticker}: {len(catalyst_news)} catalyst articles")
        
        return news_by_ticker
    
    def get_catalyst_alerts(self, tickers: List[str]) -> List[Dict]:
        """
        Get only catalyst news for alert generation
        Returns list of catalyst news items
        """
        news_by_ticker = self.scan_watchlist_news(tickers)
        
        alerts = []
        
        for ticker, news_items in news_by_ticker.items():
            for news in news_items[:3]:  # Top 3 per ticker
                alerts.append({
                    'ticker': ticker,
                    'title': news['title'],
                    'keywords': news['catalyst_keywords'],
                    'link': news['link'],
                    'source': news['source'],
                    'datetime': news['datetime']
                })
        
        return alerts
    
    def _parse_finviz_datetime(self, date_text: str) -> str:
        """Parse Finviz datetime format"""
        try:
            # Finviz formats: "Jan-02-26 08:30PM" or "Today 08:30PM"
            now = datetime.now()
            
            if 'Today' in date_text or 'today' in date_text:
                # Parse time only
                time_part = date_text.split()[-1]
                parsed_time = datetime.strptime(time_part, '%I:%M%p').time()
                dt = datetime.combine(now.date(), parsed_time)
            else:
                # Full date
                dt = datetime.strptime(date_text, '%b-%d-%y %I:%M%p')
            
            return dt.isoformat()
        
        except Exception:
            return datetime.now().isoformat()
    
    def _deduplicate_news(self, news_items: List[Dict]) -> List[Dict]:
        """Remove duplicate news by title similarity"""
        if not news_items:
            return []
        
        unique_news = []
        seen_titles = set()
        
        for news in news_items:
            # Simple deduplication by first 50 chars of title
            title_key = news['title'][:50].lower()
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(news)
        
        return unique_news
    
    def save_news(self, ticker: str, news_items: List[Dict]):
        """Save news to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.news_dir / f'{ticker}_news_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(news_items, f, indent=2)
        
        print(f"💾 Saved to: {filename}")


def main():
    """CLI interface"""
    import sys
    
    scraper = NewsScraper()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].upper()
        
        # Single ticker
        news = scraper.get_all_news(command)
        
        print(f"\n{'='*70}")
        print(f"📰 NEWS FOR {command}")
        print(f"{'='*70}\n")
        
        catalyst_count = 0
        
        for i, item in enumerate(news[:15], 1):
            catalyst_emoji = '🎯' if item['is_catalyst'] else '📄'
            print(f"{i}. {catalyst_emoji} {item['title']}")
            print(f"   Source: {item['source']} | {item['datetime'][:10]}")
            
            if item['catalyst_keywords']:
                print(f"   Keywords: {', '.join(item['catalyst_keywords'])}")
                catalyst_count += 1
            
            print(f"   {item['link']}\n")
        
        print(f"{'='*70}")
        print(f"Total: {len(news)} articles | Catalysts: {catalyst_count}")
        print(f"{'='*70}\n")
        
        # Save
        scraper.save_news(command, news)
    
    else:
        print("Usage: python news_scraper.py TICKER")
        print("Example: python news_scraper.py AISP")


if __name__ == '__main__':
    main()
