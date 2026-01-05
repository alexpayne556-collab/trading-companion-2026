#!/usr/bin/env python3
"""
🐺 BIG RUNNER HUNTER - Find 50-200% Moves BEFORE They Happen

Scans for:
- Low float (under 20M)
- Insider cluster buying (3+ insiders)
- Upcoming catalyst (earnings)
- High short interest (15%+)
- Near 52-week low

For PDT-restricted swing traders who need to catch runners BEFORE the move.

Author: Brokkr
Date: January 5, 2026
"""

import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import argparse
import time
import json
from pathlib import Path

# Setup
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# AI Fuel Chain universe (our existing watchlist)
AI_FUEL_CHAIN = [
    # Nuclear
    "UUUU", "SMR", "LEU", "OKLO", "CCJ", "DNN", "UEC", "NXE", "NNE",
    # Space
    "LUNR", "RKLB", "RDW", "ASTS", "SIDU", "BKSY", "PL",
    # Quantum
    "IONQ", "RGTI", "QBTS", "QUBT", "ARQQ",
    # AI
    "PLTR", "AI", "SOUN", "PATH", "UPST",
    # Infrastructure
    "VRT", "MOD", "NVT", "LITE", "AAOI", "COHR", "GFS", "ANET", "CRDO",
    # Data Centers
    "FN", "CIEN", "MU", "WDC", "STX", "SMCI",
    # Power/Utilities
    "NEE", "VST", "CEG", "WMB", "EME", "CLS", "FIX", "EQIX", "DLR"
]


class BigRunnerScanner:
    """
    Find stocks ready to make 50-200% moves.
    """
    
    def __init__(self, universe=None):
        self.universe = universe or AI_FUEL_CHAIN
        self.results = []
        self.timestamp = datetime.now()
        
    def get_openinsider_clusters(self):
        """
        Scrape OpenInsider for recent cluster buying.
        Multiple insiders buying = conviction signal.
        """
        print("📡 Scanning OpenInsider for cluster buying...")
        
        # OpenInsider URL - Cluster buying, $2-50 price, last 14 days
        url = "http://openinsider.com/screener?s=&o=&pl=2&ph=50&ll=&lh=&fd=14&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&vl=25&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=100&page=1"
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the table
            table = soup.find('table', {'class': 'tinytable'})
            if not table:
                print("⚠️  OpenInsider table not found")
                return {}
            
            # Parse rows
            clusters = {}
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 4:
                    continue
                
                # Extract ticker (usually in column with link)
                ticker_link = row.find('a', href=lambda x: x and '/screener?s=' in x)
                if not ticker_link:
                    continue
                    
                ticker = ticker_link.text.strip()
                
                if ticker not in clusters:
                    clusters[ticker] = {
                        'count': 0,
                        'total_value': 0,
                        'insiders': []
                    }
                
                clusters[ticker]['count'] += 1
                
                # Try to extract value (usually has $ sign)
                value_col = None
                for col in cols:
                    text = col.text.strip()
                    if '$' in text:
                        try:
                            # Remove $ and commas, convert to float
                            value = float(text.replace('$', '').replace(',', '').replace('+', ''))
                            value_col = value
                            break
                        except:
                            pass
                
                if value_col:
                    clusters[ticker]['total_value'] += value_col
            
            # Filter for clusters (3+ insiders)
            real_clusters = {k: v for k, v in clusters.items() if v['count'] >= 3}
            
            print(f"✅ Found {len(real_clusters)} tickers with cluster buying")
            return real_clusters
            
        except Exception as e:
            print(f"⚠️  OpenInsider scrape failed: {e}")
            return {}
    
    def get_finviz_short_interest(self, ticker):
        """
        Scrape Finviz for short interest data.
        """
        try:
            url = f"https://finviz.com/quote.ashx?t={ticker}"
            response = requests.get(url, headers=HEADERS, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the fundamentals table
            tables = soup.find_all('table', {'class': 'snapshot-table2'})
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    for i, cell in enumerate(cells):
                        if 'Short Float' in cell.text:
                            if i + 1 < len(cells):
                                short_text = cells[i + 1].text.strip()
                                # Extract percentage
                                if '%' in short_text:
                                    return float(short_text.replace('%', ''))
            
            return 0
            
        except Exception as e:
            return 0
    
    def analyze_ticker(self, ticker, insider_data=None):
        """
        Analyze a single ticker against all criteria.
        Returns score and breakdown.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1y")
            
            if hist.empty:
                return None
            
            # Get current price
            current_price = hist['Close'].iloc[-1]
            
            # Skip if outside price range
            if current_price < 2 or current_price > 50:
                return None
            
            # Initialize score components
            score_breakdown = {
                'float_score': 0,
                'short_score': 0,
                'insider_score': 0,
                'catalyst_score': 0,
                'position_score': 0
            }
            
            # 1. FLOAT SCORE (0-25 points)
            shares_float = info.get('floatShares', info.get('sharesOutstanding', 0))
            float_m = shares_float / 1_000_000 if shares_float else 999
            
            if float_m < 10:
                score_breakdown['float_score'] = 25
            elif float_m < 20:
                score_breakdown['float_score'] = 15
            elif float_m < 50:
                score_breakdown['float_score'] = 5
            
            # 2. SHORT INTEREST SCORE (0-20 points)
            short_pct = info.get('shortPercentOfFloat', 0)
            if short_pct == 0:
                # Try Finviz scrape
                short_pct = self.get_finviz_short_interest(ticker)
            
            short_pct = short_pct * 100 if short_pct < 1 else short_pct  # Convert to percentage
            
            if short_pct > 30:
                score_breakdown['short_score'] = 20
            elif short_pct > 20:
                score_breakdown['short_score'] = 15
            elif short_pct > 15:
                score_breakdown['short_score'] = 10
            
            # 3. INSIDER BUYING SCORE (0-30 points)
            insider_count = 0
            insider_value = 0
            
            if insider_data and ticker in insider_data:
                insider_count = insider_data[ticker]['count']
                insider_value = insider_data[ticker]['total_value']
                
                if insider_count >= 3:
                    score_breakdown['insider_score'] = 30
                elif insider_count == 2:
                    score_breakdown['insider_score'] = 20
                elif insider_count == 1:
                    score_breakdown['insider_score'] = 10
            
            # 4. CATALYST SCORE (0-15 points)
            # Check for earnings date
            earnings_date = info.get('earningsDate')
            days_to_earnings = 999
            
            if earnings_date:
                try:
                    if isinstance(earnings_date, list):
                        earnings_date = earnings_date[0]
                    
                    # Convert timestamp to datetime
                    if hasattr(earnings_date, 'timestamp'):
                        earnings_dt = datetime.fromtimestamp(earnings_date.timestamp())
                    else:
                        earnings_dt = earnings_date
                    
                    days_to_earnings = (earnings_dt - datetime.now()).days
                    
                    if 0 < days_to_earnings <= 7:
                        score_breakdown['catalyst_score'] = 15
                    elif 7 < days_to_earnings <= 14:
                        score_breakdown['catalyst_score'] = 10
                except:
                    pass
            
            # 5. PRICE POSITION SCORE (0-10 points)
            high_52w = hist['High'].max()
            low_52w = hist['Low'].min()
            
            pct_from_low = ((current_price - low_52w) / low_52w) * 100
            
            if pct_from_low < 10:
                score_breakdown['position_score'] = 10
            elif pct_from_low < 20:
                score_breakdown['position_score'] = 5
            
            # TOTAL SCORE
            total_score = sum(score_breakdown.values())
            
            # Build result
            result = {
                'ticker': ticker,
                'score': total_score,
                'price': current_price,
                'float_m': round(float_m, 2),
                'short_pct': round(short_pct, 1),
                'insider_count': insider_count,
                'insider_value': insider_value,
                'days_to_earnings': days_to_earnings if days_to_earnings < 999 else None,
                'pct_from_low': round(pct_from_low, 1),
                'pct_from_high': round(((high_52w - current_price) / high_52w) * 100, 1),
                'market_cap': info.get('marketCap', 0),
                'volume': hist['Volume'].iloc[-1],
                'avg_volume': hist['Volume'].mean(),
                'score_breakdown': score_breakdown
            }
            
            return result
            
        except Exception as e:
            print(f"⚠️  Error analyzing {ticker}: {e}")
            return None
    
    def scan(self):
        """
        Scan the universe and find big runner setups.
        """
        print("=" * 80)
        print("🐺 BIG RUNNER HUNTER - SCANNING FOR 50-200% SETUPS")
        print("=" * 80)
        print(f"⏰ Time: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Universe: {len(self.universe)} tickers")
        print()
        
        # Step 1: Try to load existing insider cluster data from our cluster scanner
        insider_data = {}
        try:
            cluster_file = Path('logs/cluster_results.json')
            if cluster_file.exists():
                with open(cluster_file) as f:
                    cluster_data = json.load(f)
                    # Convert to format we need
                    for cluster in cluster_data.get('clusters', []):
                        ticker = cluster['ticker']
                        insider_data[ticker] = {
                            'count': cluster.get('insider_count', 0),
                            'total_value': cluster.get('total_value', 0)
                        }
                print(f"✅ Loaded {len(insider_data)} tickers with insider buying from cluster scanner")
        except:
            pass
        
        # Step 2: Supplement with OpenInsider if available
        openinsider_data = self.get_openinsider_clusters()
        for ticker, data in openinsider_data.items():
            if ticker not in insider_data:
                insider_data[ticker] = data
        
        # Step 3: Analyze each ticker
        print()
        print(f"🔍 Analyzing {len(self.universe)} tickers...")
        print()
        
        for i, ticker in enumerate(self.universe, 1):
            print(f"   [{i}/{len(self.universe)}] Scanning {ticker}...", end='\r')
            
            result = self.analyze_ticker(ticker, insider_data)
            if result:  # Keep ALL results for debugging
                self.results.append(result)
            
            time.sleep(0.3)  # Be nice to APIs
        
        print("\n")
        
        # Sort by score
        self.results.sort(key=lambda x: x['score'], reverse=True)
        
        return self.results
    
    def display_results(self, min_score=50):
        """
        Display results in clean format.
        """
        high_conviction = [r for r in self.results if r['score'] >= 70]
        watch_list = [r for r in self.results if 50 <= r['score'] < 70]
        moderate = [r for r in self.results if 30 <= r['score'] < 50]
        
        print()
        print("=" * 80)
        print("🐺 BIG RUNNER HUNTER - RESULTS")
        print("=" * 80)
        print()
        
        if high_conviction:
            print("🔥 HIGH CONVICTION (70+ Score):")
            print("━" * 80)
            print()
            
            for result in high_conviction:
                self.print_ticker_card(result)
        else:
            print("🔥 HIGH CONVICTION (70+ Score): None found")
            print()
        
        if watch_list and min_score <= 50:
            print("━" * 80)
            print()
            print("👀 WATCH LIST (50-69 Score):")
            print("━" * 80)
            print()
            
            for result in watch_list:
                self.print_ticker_card(result)
        elif not watch_list and min_score <= 50:
            print("👀 WATCH LIST (50-69 Score): None found")
            print()
        
        if moderate and min_score <= 30:
            print("━" * 80)
            print()
            print("💪 MODERATE (30-49 Score):")
            print("━" * 80)
            print()
            
            for result in moderate[:10]:  # Show top 10
                print(f"{result['ticker']} - {result['score']}/100 | ${result['price']:.2f} | Float: {result['float_m']:.1f}M | Short: {result['short_pct']:.1f}%")
        
        # Show top 5 by score regardless
        if self.results and not high_conviction and not watch_list:
            print()
            print("━" * 80)
            print("📊 TOP 5 BY SCORE:")
            print("━" * 80)
            print()
            for result in self.results[:5]:
                self.print_ticker_card(result)
        
        print("━" * 80)
        print()
        print(f"📊 SUMMARY:")
        print(f"   • HIGH CONVICTION: {len(high_conviction)} setups")
        print(f"   • WATCH LIST: {len(watch_list)} setups")
        print(f"   • MODERATE: {len(moderate)} setups")
        print(f"   • Total scanned: {len(self.universe)} tickers")
        print(f"   • Total with data: {len(self.results)} tickers")
        print()
        print("🐺 AWOOOO! Hunt complete.")
        print()
    
    def print_ticker_card(self, result):
        """
        Print a single ticker card.
        """
        print(f"TICKER: {result['ticker']} | Score: {result['score']}/100")
        print(f"├── Price: ${result['price']:.2f} | Float: {result['float_m']:.1f}M | Short: {result['short_pct']:.1f}%")
        
        if result['insider_count'] > 0:
            print(f"├── Insiders: {result['insider_count']} buys last 30 days (${result['insider_value']:,.0f} total)")
        else:
            print(f"├── Insiders: No recent buying")
        
        if result['days_to_earnings']:
            print(f"├── Catalyst: Earnings in {result['days_to_earnings']} days")
        else:
            print(f"├── Catalyst: None detected")
        
        print(f"├── Position: {result['pct_from_low']:.1f}% above 52-week low")
        
        # Why is this a setup?
        reasons = []
        if result['score_breakdown']['float_score'] >= 15:
            reasons.append("low float")
        if result['score_breakdown']['short_score'] >= 10:
            reasons.append(f"{result['short_pct']:.0f}% short")
        if result['score_breakdown']['insider_score'] >= 20:
            reasons.append("insider cluster")
        if result['score_breakdown']['catalyst_score'] >= 10:
            reasons.append("earnings soon")
        if result['score_breakdown']['position_score'] >= 5:
            reasons.append("near lows")
        
        why = ", ".join(reasons) if reasons else "multiple signals"
        print(f"└── WHY: {why.capitalize()}")
        print()
    
    def save_results(self):
        """
        Save results to JSON for later analysis.
        """
        output_dir = Path('logs')
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / 'big_runner_results.json'
        
        # Convert numpy types to Python types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            elif hasattr(obj, 'item'):  # numpy types
                return obj.item()
            else:
                return obj
        
        clean_results = convert_types(self.results)
        
        data = {
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'scanned': len(self.universe),
            'found': len(self.results),
            'results': clean_results
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='🐺 Big Runner Hunter - Find 50-200% moves BEFORE they happen')
    parser.add_argument('--min-score', type=int, default=50, help='Minimum score to display (default: 50)')
    parser.add_argument('--insider-only', action='store_true', help='Only show tickers with insider buying')
    parser.add_argument('--add-tickers', nargs='+', help='Add extra tickers to scan')
    
    args = parser.parse_args()
    
    # Build universe
    universe = AI_FUEL_CHAIN.copy()
    if args.add_tickers:
        universe.extend(args.add_tickers)
    
    # Create scanner
    scanner = BigRunnerScanner(universe=universe)
    
    # Scan
    results = scanner.scan()
    
    # Filter if insider-only
    if args.insider_only:
        results = [r for r in results if r['insider_count'] > 0]
        scanner.results = results
    
    # Display
    scanner.display_results(min_score=args.min_score)
    
    # Save
    scanner.save_results()


if __name__ == "__main__":
    main()
