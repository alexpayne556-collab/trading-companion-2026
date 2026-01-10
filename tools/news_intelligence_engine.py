#!/usr/bin/env python3
"""
🐺 NEWS INTELLIGENCE ENGINE
Aggregates news from multiple FREE sources and correlates with price moves
"""

import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from pathlib import Path

class NewsAggregator:
    """Collect news from multiple free sources"""
    
    def __init__(self):
        self.sources = {}
        self.cache_dir = Path("data/news_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_yahoo_news(self, ticker):
        """Get news from Yahoo Finance (FREE unlimited)"""
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            parsed = []
            for article in news[:10]:  # Last 10 articles
                parsed.append({
                    'source': 'Yahoo Finance',
                    'ticker': ticker,
                    'title': article.get('title', ''),
                    'link': article.get('link', ''),
                    'publisher': article.get('publisher', ''),
                    'timestamp': datetime.fromtimestamp(article.get('providerPublishTime', 0)),
                    'type': 'news'
                })
            
            return parsed
        except Exception as e:
            print(f"⚠️  Yahoo news error for {ticker}: {e}")
            return []
    
    def get_sec_filings(self, ticker, cik=None):
        """Get SEC EDGAR filings (FREE unlimited)"""
        try:
            # Get company CIK if not provided
            if not cik:
                # Map ticker to CIK (would need a lookup table)
                # For now, return empty
                return []
            
            url = f"https://data.sec.gov/submissions/CIK{cik:010d}.json"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return []
            
            data = response.json()
            recent_filings = data.get('filings', {}).get('recent', {})
            
            parsed = []
            for i in range(min(10, len(recent_filings.get('form', [])))):
                form_type = recent_filings['form'][i]
                
                # Only care about material events
                if form_type in ['8-K', '10-K', '10-Q', '4', 'S-1']:
                    parsed.append({
                        'source': 'SEC EDGAR',
                        'ticker': ticker,
                        'title': f"{form_type} Filing",
                        'link': f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}",
                        'publisher': 'SEC',
                        'timestamp': datetime.strptime(recent_filings['filingDate'][i], '%Y-%m-%d'),
                        'type': 'filing',
                        'form_type': form_type
                    })
            
            return parsed
        except Exception as e:
            print(f"⚠️  SEC filing error for {ticker}: {e}")
            return []
    
    def aggregate_news(self, ticker):
        """Aggregate all news sources for ticker"""
        all_news = []
        
        # Yahoo Finance news
        all_news.extend(self.get_yahoo_news(ticker))
        
        # SEC filings (if we have CIK)
        # all_news.extend(self.get_sec_filings(ticker))
        
        # Sort by timestamp
        all_news.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return all_news


class NewsImpactAnalyzer:
    """Analyze correlation between news and price moves"""
    
    def __init__(self):
        self.impact_cache = {}
    
    def get_price_impact(self, ticker, news_time, hours_after=24):
        """
        Calculate price impact after news event
        
        Returns:
            dict with: return_1h, return_4h, return_24h, volume_spike
        """
        try:
            # Get intraday data if possible, otherwise daily
            stock = yf.Ticker(ticker)
            
            # Get data around news time
            start = news_time - timedelta(days=1)
            end = news_time + timedelta(hours=hours_after)
            
            df = stock.history(start=start, end=end, interval='1h')
            
            if len(df) < 2:
                # Fall back to daily data
                df = stock.history(start=start, end=end)
                if len(df) < 2:
                    return None
            
            # Find closest price before news
            before_price = None
            after_prices = {}
            
            for timestamp, row in df.iterrows():
                if timestamp <= news_time and before_price is None:
                    before_price = row['Close']
                elif timestamp > news_time:
                    hours_diff = (timestamp - news_time).total_seconds() / 3600
                    
                    if hours_diff <= 1 and '1h' not in after_prices:
                        after_prices['1h'] = row['Close']
                    if hours_diff <= 4 and '4h' not in after_prices:
                        after_prices['4h'] = row['Close']
                    if hours_diff <= 24 and '24h' not in after_prices:
                        after_prices['24h'] = row['Close']
            
            if not before_price:
                return None
            
            # Calculate returns
            impact = {
                'before_price': before_price,
                'return_1h': ((after_prices.get('1h', before_price) - before_price) / before_price * 100) if '1h' in after_prices else None,
                'return_4h': ((after_prices.get('4h', before_price) - before_price) / before_price * 100) if '4h' in after_prices else None,
                'return_24h': ((after_prices.get('24h', before_price) - before_price) / before_price * 100) if '24h' in after_prices else None,
            }
            
            return impact
            
        except Exception as e:
            print(f"⚠️  Price impact error: {e}")
            return None
    
    def analyze_news_type_impact(self, ticker, lookback_days=90):
        """
        Backtest: which news types move the stock?
        
        Returns:
            DataFrame with news type impact statistics
        """
        aggregator = NewsAggregator()
        
        print(f"📊 Analyzing news impact for {ticker} (last {lookback_days} days)...")
        
        # Get historical news
        news = aggregator.aggregate_news(ticker)
        
        results = []
        
        for article in news:
            # Only analyze news from lookback period
            if article['timestamp'] < datetime.now() - timedelta(days=lookback_days):
                continue
            
            # Calculate price impact
            impact = self.get_price_impact(ticker, article['timestamp'])
            
            if impact:
                results.append({
                    'ticker': ticker,
                    'timestamp': article['timestamp'],
                    'source': article['source'],
                    'title': article['title'],
                    'type': article['type'],
                    'return_1h': impact.get('return_1h'),
                    'return_4h': impact.get('return_4h'),
                    'return_24h': impact.get('return_24h'),
                })
            
            time.sleep(0.5)  # Rate limiting
        
        df = pd.DataFrame(results)
        
        if len(df) == 0:
            print(f"❌ No data for {ticker}")
            return None
        
        # Summary statistics
        print(f"\n✅ Found {len(df)} news events for {ticker}")
        print(f"\nAverage impact:")
        print(f"  1h:  {df['return_1h'].mean():+.2f}%")
        print(f"  4h:  {df['return_4h'].mean():+.2f}%")
        print(f"  24h: {df['return_24h'].mean():+.2f}%")
        
        return df


class NewsSignalGenerator:
    """Generate trading signals from news"""
    
    def __init__(self):
        self.analyzer = NewsImpactAnalyzer()
        self.aggregator = NewsAggregator()
        
        # These will be learned from backtesting
        self.bullish_keywords = [
            'beat', 'exceed', 'surge', 'growth', 'acquisition', 'contract', 
            'partnership', 'breakthrough', 'approved', 'upgrade', 'outperform',
            'buy', 'strong', 'positive', 'revenue', 'earnings beat'
        ]
        
        self.bearish_keywords = [
            'miss', 'decline', 'loss', 'lawsuit', 'downgrade', 'weak',
            'disappointing', 'concern', 'investigation', 'cut', 'lower',
            'sell', 'negative', 'warning', 'guidance cut'
        ]
    
    def calculate_sentiment(self, title):
        """Simple keyword-based sentiment"""
        title_lower = title.lower()
        
        bullish_count = sum(1 for word in self.bullish_keywords if word in title_lower)
        bearish_count = sum(1 for word in self.bearish_keywords if word in title_lower)
        
        if bullish_count > bearish_count:
            return 'bullish', bullish_count
        elif bearish_count > bullish_count:
            return 'bearish', bearish_count
        else:
            return 'neutral', 0
    
    def scan_for_signals(self, tickers):
        """
        Scan multiple tickers for news-based signals
        
        Returns:
            List of actionable signals
        """
        print("🐺 NEWS SIGNAL SCANNER")
        print("="*70)
        print()
        
        signals = []
        
        for ticker in tickers:
            print(f"Scanning {ticker}...")
            
            news = self.aggregator.aggregate_news(ticker)
            
            # Only look at news from last 24 hours
            recent_news = [n for n in news if n['timestamp'] > datetime.now() - timedelta(hours=24)]
            
            if not recent_news:
                continue
            
            # Analyze sentiment
            for article in recent_news:
                sentiment, strength = self.calculate_sentiment(article['title'])
                
                if sentiment != 'neutral' and strength > 0:
                    signals.append({
                        'ticker': ticker,
                        'timestamp': article['timestamp'],
                        'title': article['title'],
                        'source': article['source'],
                        'sentiment': sentiment,
                        'strength': strength,
                        'signal': 'BUY' if sentiment == 'bullish' else 'AVOID'
                    })
        
        # Sort by strength
        signals.sort(key=lambda x: x['strength'], reverse=True)
        
        print(f"\n✅ Found {len(signals)} news signals")
        print()
        
        for i, sig in enumerate(signals[:10], 1):
            print(f"{i}. {sig['ticker']:6} - {sig['signal']:5} (Strength: {sig['strength']})")
            print(f"   {sig['title'][:80]}")
            print(f"   {sig['timestamp'].strftime('%Y-%m-%d %H:%M')}")
            print()
        
        return signals


def main():
    """Demo of news intelligence system"""
    
    print("🐺 NEWS INTELLIGENCE ENGINE DEMO")
    print("="*70)
    print()
    
    # Test tickers
    test_tickers = ['WULF', 'CIFR', 'IREN', 'IONQ', 'RGTI']
    
    print("1. AGGREGATING NEWS...")
    print()
    
    aggregator = NewsAggregator()
    for ticker in test_tickers[:2]:  # Just test 2
        news = aggregator.aggregate_news(ticker)
        print(f"\n{ticker}: {len(news)} news items")
        
        for article in news[:3]:
            print(f"  • {article['timestamp'].strftime('%Y-%m-%d')}: {article['title'][:60]}")
    
    print("\n" + "="*70)
    print("2. GENERATING SIGNALS...")
    print()
    
    signal_gen = NewsSignalGenerator()
    signals = signal_gen.scan_for_signals(test_tickers)
    
    print("\n" + "="*70)
    print("3. BACKTEST IMPACT (Optional - takes time)")
    print()
    print("To backtest news impact:")
    print("  analyzer = NewsImpactAnalyzer()")
    print("  df = analyzer.analyze_news_type_impact('WULF', lookback_days=30)")
    print()
    
    print("🐺 News intelligence system operational. LLHR.")
    print()


if __name__ == "__main__":
    main()
