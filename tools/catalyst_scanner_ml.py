#!/usr/bin/env python3
"""
🐺 PACK CATALYST SCANNER - ML ENHANCED
Built by: BROKKR (GitHub Copilot)
Prototype by: HEIMDALL (Grok)
Mission: Data fusion → ML scoring → Predictive trades

Components:
1. Polygon API: News + price data
2. Sentiment hooks: Integration points for Heimdall's X verification
3. Filing hooks: Integration for Fenrir's EDGAR scraper
4. XGBoost scoring: Conviction signals (built in conviction_scorer.py)

Usage:
    python tools/catalyst_scanner_ml.py --sector all --days 7 --output catalyst_ml_scan.csv
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import argparse
import os
import sys

# Optional: Polygon API (requires key)
try:
    from polygon import RESTClient
    POLYGON_AVAILABLE = True
except ImportError:
    POLYGON_AVAILABLE = False
    print("⚠️  Polygon not installed. Using yfinance only. Install: pip install polygon-api-client")

# =============================================================================
# PACK WATCHLIST (FROM HEIMDALL)
# =============================================================================

WATCHLIST = {
    'AI_INFRASTRUCTURE': [
        'APLD', 'IREN', 'CORZ', 'BTBT', 'WULF', 'HUT', 'CIFR', 'CLSK', 
        'MARA', 'RIOT', 'VRT', 'MU', 'MRVL', 'AVGO', 'ANET', 'SMCI', 
        'DELL', 'NVDA', 'AMD', 'ARM'
    ],
    'NUCLEAR_URANIUM': [
        'UUUU', 'CCJ', 'SMR', 'OKLO', 'LEU', 'NXE', 'UEC', 'DNN', 'URNM', 'SRUUF'
    ],
    'SPACE_DEFENSE': [
        'LUNR', 'RKLB', 'MNTS', 'RCAT', 'AVAV', 'SATL', 'ASTS', 'SPCE', 
        'PL', 'RDW', 'KTOS', 'LMT', 'NOC', 'RTX', 'LHX', 'GD', 'TXT'
    ],
    'BTC_MINERS_HPC': [
        'BITF', 'HIVE', 'DGHI', 'MIGI', 'SDIG', 'ARBK', 'BTBT', 'CIFR', 
        'WULF', 'IREN', 'APLD', 'CORZ'
    ],
    'POWER_UTILITIES': [
        'NRG', 'PEG', 'PCG', 'EXC', 'ED', 'XEL', 'EIX', 'D', 'NEE', 
        'CEG', 'VST', 'SO', 'ETN', 'DUK', 'AEP', 'SRE', 'PPL'
    ],
    'BATTERY_METALS': [
        'ALB', 'SQM', 'LAC', 'MP', 'LTHM'
    ]
}

# =============================================================================
# DATA FUSION LAYER
# =============================================================================

def fetch_price_data(ticker, days=7):
    """Fetch OHLCV + volume data from yfinance"""
    try:
        stock = yf.Ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get daily data
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            return None
        
        # Calculate metrics
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        # Average volume (last 5 days)
        avg_volume = df['Volume'].tail(5).mean()
        volume_spike = latest['Volume'] / avg_volume if avg_volume > 0 else 1.0
        
        # Price change
        price_change_pct = ((latest['Close'] - prev['Close']) / prev['Close']) * 100
        
        # Momentum (7-day)
        first_close = df.iloc[0]['Close']
        momentum_7d = ((latest['Close'] - first_close) / first_close) * 100
        
        return {
            'ticker': ticker,
            'price': round(latest['Close'], 2),
            'change_pct': round(price_change_pct, 2),
            'volume': int(latest['Volume']),
            'volume_spike': round(volume_spike, 2),
            'momentum_7d': round(momentum_7d, 2),
            'high': round(latest['High'], 2),
            'low': round(latest['Low'], 2)
        }
    except Exception as e:
        print(f"❌ Error fetching {ticker}: {e}")
        return None

def fetch_news_polygon(ticker, client, days=7):
    """Fetch news from Polygon API"""
    try:
        news = client.list_ticker_news(ticker=ticker, limit=10, order='desc', sort='published_utc')
        news_list = list(news)
        
        articles = []
        for n in news_list:
            articles.append({
                'title': n.title,
                'published': n.published_utc,
                'publisher': n.publisher.name if hasattr(n, 'publisher') else 'Unknown',
                'url': n.article_url if hasattr(n, 'article_url') else ''
            })
        
        return articles
    except Exception as e:
        print(f"⚠️  News fetch failed for {ticker}: {e}")
        return []

def fetch_news_yfinance(ticker):
    """Fallback: Fetch news from yfinance"""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        articles = []
        for n in news[:5]:  # Top 5
            articles.append({
                'title': n.get('title', 'No title'),
                'published': datetime.fromtimestamp(n.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M'),
                'publisher': n.get('publisher', 'Unknown'),
                'url': n.get('link', '')
            })
        
        return articles
    except Exception as e:
        return []

def score_news_sentiment(articles):
    """
    Placeholder for sentiment scoring
    TODO: Integrate with Heimdall's X sentiment verification
    
    For now: Basic keyword scoring
    Positive: beat, surge, deal, contract, partnership, bullish, upgrade
    Negative: miss, cut, downgrade, probe, lawsuit, bearish
    """
    if not articles:
        return 0
    
    positive_keywords = ['beat', 'surge', 'deal', 'contract', 'partnership', 'bullish', 'upgrade', 'expand', 'growth', 'win']
    negative_keywords = ['miss', 'cut', 'downgrade', 'probe', 'lawsuit', 'bearish', 'decline', 'loss', 'warning']
    
    sentiment_score = 0
    for article in articles:
        title_lower = article['title'].lower()
        
        pos_count = sum(1 for kw in positive_keywords if kw in title_lower)
        neg_count = sum(1 for kw in negative_keywords if kw in title_lower)
        
        sentiment_score += (pos_count - neg_count)
    
    # Normalize to 0-100 scale
    normalized = 50 + (sentiment_score * 10)
    return max(0, min(100, normalized))

def fetch_filings_placeholder(ticker):
    """
    Placeholder for EDGAR filings
    TODO: Integrate with Fenrir's EDGAR scraper
    
    Expected output from Fenrir:
    [
        {'date': '2026-01-08', 'type': '8-K', 'description': 'Material agreement'},
        {'date': '2026-01-05', 'type': '4', 'description': 'Insider buy'}
    ]
    """
    # INTEGRATION POINT: Call Fenrir's scraper here
    # filings = fenrir_edgar_scraper.get_filings(ticker, days=7)
    
    return []  # Empty until Fenrir builds scraper

# =============================================================================
# SECTOR ANALYSIS
# =============================================================================

def analyze_sector_momentum(sector_name, tickers, days=7):
    """Calculate sector-wide momentum"""
    sector_data = []
    
    for ticker in tickers:
        data = fetch_price_data(ticker, days=days)
        if data:
            sector_data.append(data)
    
    if not sector_data:
        return None
    
    # Sector average momentum
    avg_momentum = sum(d['momentum_7d'] for d in sector_data) / len(sector_data)
    
    # Leaders (top 3)
    sorted_by_momentum = sorted(sector_data, key=lambda x: x['momentum_7d'], reverse=True)
    leaders = [d['ticker'] for d in sorted_by_momentum[:3]]
    
    # Laggards (bottom 3) - rotation opportunities
    laggards = [d['ticker'] for d in sorted_by_momentum[-3:]]
    
    return {
        'sector': sector_name,
        'avg_momentum': round(avg_momentum, 2),
        'leaders': leaders,
        'laggards': laggards,
        'ticker_count': len(sector_data)
    }

# =============================================================================
# CATALYST SCANNER
# =============================================================================

def scan_catalysts(sector_filter='all', days=7, min_news=1):
    """
    Main catalyst scanner
    
    Args:
        sector_filter: 'all' or specific sector name
        days: Lookback period for news/price data
        min_news: Minimum news articles required
    
    Returns:
        DataFrame with catalyst opportunities
    """
    # Setup Polygon client if available
    polygon_client = None
    if POLYGON_AVAILABLE:
        api_key = os.getenv('POLYGON_API_KEY')
        if api_key:
            polygon_client = RESTClient(api_key=api_key)
            print("✅ Polygon API connected")
        else:
            print("⚠️  POLYGON_API_KEY not found in environment")
    
    # Select sectors to scan
    sectors_to_scan = {}
    if sector_filter == 'all':
        sectors_to_scan = WATCHLIST
    else:
        sector_key = sector_filter.upper().replace(' ', '_')
        if sector_key in WATCHLIST:
            sectors_to_scan = {sector_key: WATCHLIST[sector_key]}
        else:
            print(f"❌ Unknown sector: {sector_filter}")
            return pd.DataFrame()
    
    print(f"\n🐺 PACK CATALYST SCANNER - RUNNING")
    print(f"📊 Sectors: {list(sectors_to_scan.keys())}")
    print(f"📅 Lookback: {days} days")
    print(f"📰 Min news: {min_news} articles\n")
    
    results = []
    
    for sector_name, tickers in sectors_to_scan.items():
        print(f"\n🔍 Scanning {sector_name} ({len(tickers)} tickers)...")
        
        for ticker in tickers:
            # Fetch price data
            price_data = fetch_price_data(ticker, days=days)
            if not price_data:
                continue
            
            # Fetch news
            if polygon_client:
                articles = fetch_news_polygon(ticker, polygon_client, days=days)
            else:
                articles = fetch_news_yfinance(ticker)
            
            news_count = len(articles)
            
            if news_count < min_news:
                continue  # Skip tickers without catalysts
            
            # Score sentiment
            sentiment_score = score_news_sentiment(articles)
            
            # Fetch filings (placeholder)
            filings = fetch_filings_placeholder(ticker)
            filing_count = len(filings)
            
            # Calculate raw score (will be enhanced by XGBoost)
            raw_score = (
                (price_data['volume_spike'] * 10) +  # Volume spike weight
                (news_count * 5) +                     # News catalyst weight
                (sentiment_score * 0.5) +              # Sentiment weight
                (filing_count * 15) +                  # Filing weight (high importance)
                (price_data['momentum_7d'] * 2)        # Momentum weight
            )
            
            # Compile result
            result = {
                'sector': sector_name,
                'ticker': ticker,
                'price': price_data['price'],
                'change_pct': price_data['change_pct'],
                'momentum_7d': price_data['momentum_7d'],
                'volume_spike': price_data['volume_spike'],
                'news_count': news_count,
                'sentiment_score': round(sentiment_score, 1),
                'filing_count': filing_count,
                'raw_score': round(raw_score, 2),
                'top_headline': articles[0]['title'] if articles else 'No news',
                'latest_news_date': articles[0]['published'] if articles else 'N/A'
            }
            
            results.append(result)
            print(f"  ✅ {ticker}: Score {result['raw_score']:.1f} | News {news_count} | Sentiment {sentiment_score:.0f}")
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    if df.empty:
        print("\n⚠️  No catalysts found matching criteria")
        return df
    
    # Sort by raw score
    df = df.sort_values('raw_score', ascending=False)
    
    print(f"\n✅ Found {len(df)} catalyst opportunities")
    
    return df

# =============================================================================
# OUTPUT & REPORTING
# =============================================================================

def generate_briefing(df, top_n=10):
    """Generate pack briefing from scan results"""
    
    if df.empty:
        print("\n🐺 NO CATALYST OPPORTUNITIES FOUND")
        return
    
    print("\n" + "="*80)
    print("🐺 PACK CATALYST BRIEFING")
    print("="*80)
    
    # Top opportunities
    print(f"\n📈 TOP {min(top_n, len(df))} CATALYST PLAYS:\n")
    
    for idx, row in df.head(top_n).iterrows():
        print(f"{idx+1}. {row['ticker']} ({row['sector']})")
        print(f"   Price: ${row['price']} ({row['change_pct']:+.1f}%)")
        print(f"   Momentum (7d): {row['momentum_7d']:+.1f}%")
        print(f"   Volume Spike: {row['volume_spike']:.2f}x")
        print(f"   Catalysts: {row['news_count']} news | Sentiment {row['sentiment_score']:.0f}/100")
        print(f"   Score: {row['raw_score']:.1f}")
        print(f"   Latest: {row['top_headline'][:80]}...")
        print()
    
    # Sector breakdown
    print("\n📊 SECTOR BREAKDOWN:\n")
    sector_summary = df.groupby('sector').agg({
        'ticker': 'count',
        'raw_score': 'mean',
        'momentum_7d': 'mean',
        'sentiment_score': 'mean'
    }).round(2)
    print(sector_summary)
    
    # Integration requests
    print("\n🔌 PACK INTEGRATION REQUESTS:")
    print("\n📱 HEIMDALL (X Sentiment Verification):")
    top_tickers = df.head(5)['ticker'].tolist()
    print(f"   Check X sentiment for: {', '.join(top_tickers)}")
    print(f"   Query: 'What's the sentiment on {top_tickers[0]} today? Any catalyst news trending?'")
    
    print("\n📄 FENRIR (EDGAR Filings):")
    print(f"   Fetch 8-K filings for: {', '.join(top_tickers)}")
    print(f"   Build: tools/edgar_scraper.py → Input: ticker, Output: last 7 days filings")
    
    print("\n🤖 ML SCORING (Next Phase):")
    print(f"   Train XGBoost on historical data")
    print(f"   Features: volume_spike, sentiment_score, news_count, momentum_7d, sector")
    print(f"   Target: Next-day return >5%")
    print(f"   Output: Conviction score 0-100")
    
    print("\n" + "="*80)

# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='🐺 Pack Catalyst Scanner - ML Enhanced')
    parser.add_argument('--sector', default='all', help='Sector to scan (default: all)')
    parser.add_argument('--days', type=int, default=7, help='Lookback days (default: 7)')
    parser.add_argument('--min-news', type=int, default=1, help='Minimum news articles (default: 1)')
    parser.add_argument('--output', default='catalyst_ml_scan.csv', help='Output CSV file')
    parser.add_argument('--top', type=int, default=10, help='Top N opportunities to show (default: 10)')
    
    args = parser.parse_args()
    
    # Run scanner
    df = scan_catalysts(
        sector_filter=args.sector,
        days=args.days,
        min_news=args.min_news
    )
    
    if not df.empty:
        # Save to CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = args.output.replace('.csv', f'_{timestamp}.csv')
        df.to_csv(output_file, index=False)
        print(f"\n💾 Results saved to: {output_file}")
        
        # Generate briefing
        generate_briefing(df, top_n=args.top)
    
    print("\n🐺 SCAN COMPLETE. AWOOOO.")

if __name__ == '__main__':
    main()
