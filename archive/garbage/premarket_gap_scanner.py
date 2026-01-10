#!/usr/bin/env python3
"""
PRE-MARKET GAP SCANNER - PRODUCTION VERSION

Scans watchlist tickers for gaps >5%.
Correlates with overnight news and SEC filings.
Production-grade for Tyr's trading.

Usage:
    python3 premarket_gap_scanner.py
    python3 premarket_gap_scanner.py --threshold 3.0  # Lower threshold
"""

import yfinance as yf
from datetime import datetime, timedelta
import json
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import argparse
import time

# Full watchlist from Tyr's theses
WATCHLIST = [
    # Current positions
    'UUUU', 'USAR', 'AISP',
    # Nuclear
    'UEC', 'CCJ', 'SMR', 'LEU', 'DNN', 'NXE',
    # Quantum/Robotics/CES
    'RR', 'QBTS', 'QUBT', 'RGTI', 'IONQ',
    # AI Infrastructure
    'SMCI', 'CRDO', 'VRT',
    # Space
    'RDW', 'RKLB', 'LUNR', 'ASTS',
]

class PremarketGapScanner:
    def __init__(self, threshold=5.0):
        self.threshold = threshold
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_premarket_data(self, ticker):
        """Get pre-market price and volume"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get previous close
            hist = stock.history(period='2d')
            if len(hist) < 1:
                return None
            
            prev_close = hist['Close'].iloc[-1]
            
            # Get current pre-market/regular market price
            info = stock.info
            current_price = info.get('preMarketPrice') or info.get('currentPrice') or info.get('regularMarketPrice')
            
            if not current_price:
                return None
            
            # Pre-market volume
            pm_volume = info.get('preMarketVolume', 0)
            
            # Average volume for comparison
            avg_volume = info.get('averageVolume', 0)
            
            gap_pct = ((current_price - prev_close) / prev_close) * 100
            
            return {
                'ticker': ticker,
                'prev_close': prev_close,
                'current': current_price,
                'gap_pct': gap_pct,
                'pm_volume': pm_volume,
                'avg_volume': avg_volume,
                'volume_ratio': pm_volume / avg_volume if avg_volume > 0 else 0
            }
            
        except Exception as e:
            return None
    
    def search_overnight_news(self, ticker):
        """Search for overnight news"""
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if not news:
                return []
            
            # Get news from last 24 hours
            cutoff = datetime.now() - timedelta(hours=24)
            recent_news = []
            
            for article in news[:5]:  # Check top 5
                pub_time = datetime.fromtimestamp(article.get('providerPublishTime', 0))
                if pub_time > cutoff:
                    recent_news.append({
                        'title': article.get('title', ''),
                        'publisher': article.get('publisher', ''),
                        'time': pub_time.strftime('%Y-%m-%d %H:%M')
                    })
            
            return recent_news
            
        except:
            return []
    
    def check_overnight_filings(self, ticker):
        """Check for overnight SEC filings"""
        try:
            # Check last 24 hours for 8-K or Form 4
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=&dateb=&owner=include&count=10&output=xml"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'xml')
            
            filings = []
            cutoff = datetime.now() - timedelta(hours=24)
            
            for filing in soup.find_all('filing'):
                filing_type = filing.find('type')
                filing_date = filing.find('filingDate')
                
                if filing_type and filing_date:
                    f_type = filing_type.text.strip()
                    f_date = datetime.strptime(filing_date.text, '%Y-%m-%d')
                    
                    if f_date.date() >= cutoff.date() and f_type in ['8-K', '4']:
                        filings.append({
                            'type': f_type,
                            'date': f_date.strftime('%Y-%m-%d')
                        })
            
            return filings
            
        except:
            return []
    
    def determine_catalyst(self, ticker, news, filings):
        """Determine likely catalyst for gap"""
        catalysts = []
        
        # Check news headlines
        for article in news:
            title_lower = article['title'].lower()
            
            # Contract awards
            if any(kw in title_lower for kw in ['contract', 'award', 'deal', 'partnership']):
                catalysts.append(f"📰 {article['title'][:60]}...")
            # Earnings/guidance
            elif any(kw in title_lower for kw in ['earnings', 'guidance', 'revenue', 'profit']):
                catalysts.append(f"📊 {article['title'][:60]}...")
            # Product news
            elif any(kw in title_lower for kw in ['launch', 'product', 'demo', 'unveil']):
                catalysts.append(f"🚀 {article['title'][:60]}...")
            # General positive
            elif any(kw in title_lower for kw in ['surges', 'jumps', 'rallies', 'soars']):
                catalysts.append(f"📈 {article['title'][:60]}...")
            else:
                catalysts.append(f"📰 {article['title'][:60]}...")
        
        # Check SEC filings
        for filing in filings:
            if filing['type'] == '8-K':
                catalysts.append(f"📋 8-K filed {filing['date']} (check for material events)")
            elif filing['type'] == '4':
                catalysts.append(f"👤 Form 4 filed {filing['date']} (insider transaction)")
        
        # If no specific catalyst found
        if not catalysts:
            catalysts.append("⚠️ No specific catalyst identified - momentum/sector move")
        
        return catalysts
    
    def scan(self):
        """Run the scan"""
        print(f"\n🌅 PRE-MARKET GAP SCANNER - PRODUCTION VERSION")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"   Scanning {len(WATCHLIST)} tickers for gaps ≥{self.threshold}%")
        print(f"   Correlating with overnight news and SEC filings")
        print("=" * 80)
        
        gaps_up = []
        gaps_down = []
        no_gaps = []
        
        print("\n   Scanning...", end='', flush=True)
        
        for i, ticker in enumerate(WATCHLIST):
            if i % 5 == 0:
                print('.', end='', flush=True)
            
            data = self.get_premarket_data(ticker)
            
            if not data:
                continue
            
            # Categorize
            if data['gap_pct'] >= self.threshold:
                # Search for catalyst
                news = self.search_overnight_news(ticker)
                filings = self.check_overnight_filings(ticker)
                catalysts = self.determine_catalyst(ticker, news, filings)
                
                data['news'] = news
                data['filings'] = filings
                data['catalysts'] = catalysts
                
                gaps_up.append(data)
                
            elif data['gap_pct'] <= -self.threshold:
                # Search for catalyst
                news = self.search_overnight_news(ticker)
                filings = self.check_overnight_filings(ticker)
                catalysts = self.determine_catalyst(ticker, news, filings)
                
                data['news'] = news
                data['filings'] = filings
                data['catalysts'] = catalysts
                
                gaps_down.append(data)
                
            else:
                no_gaps.append(data['ticker'])
            
            time.sleep(0.3)  # Rate limiting
        
        print(" ✓ Done!")
        
        return gaps_up, gaps_down, no_gaps
    
    def display_results(self, gaps_up, gaps_down, no_gaps):
        """Display scan results"""
        
        if gaps_up:
            gaps_up.sort(key=lambda x: x['gap_pct'], reverse=True)
            
            print("\n" + "=" * 80)
            print("🟢 GAPPING UP:")
            print("=" * 80)
            
            for gap in gaps_up:
                print(f"\n{gap['ticker']} +{gap['gap_pct']:.2f}% (${gap['current']:.2f} vs ${gap['prev_close']:.2f} close)")
                print(f"   Pre-market Volume: {gap['pm_volume']:,} ({gap['volume_ratio']:.1f}x avg)")
                
                print(f"   Catalyst:")
                for catalyst in gap['catalysts']:
                    print(f"      • {catalyst}")
        
        if gaps_down:
            gaps_down.sort(key=lambda x: x['gap_pct'])
            
            print("\n" + "=" * 80)
            print("🔴 GAPPING DOWN:")
            print("=" * 80)
            
            for gap in gaps_down:
                print(f"\n{gap['ticker']} {gap['gap_pct']:.2f}% (${gap['current']:.2f} vs ${gap['prev_close']:.2f} close)")
                print(f"   Pre-market Volume: {gap['pm_volume']:,} ({gap['volume_ratio']:.1f}x avg)")
                
                print(f"   Catalyst:")
                for catalyst in gap['catalysts']:
                    print(f"      • {catalyst}")
        
        if no_gaps:
            print("\n" + "=" * 80)
            print(f"⚪ NO SIGNIFICANT GAPS (within ±{self.threshold}%):")
            print("=" * 80)
            print(f"   {', '.join(no_gaps)}")
        
        print("\n" + "=" * 80)
        print("🐺 WOLF'S READ")
        print("=" * 80)
        
        if gaps_up:
            print(f"\n   🟢 {len(gaps_up)} stocks gapping up - Watch for:")
            print("      • Gaps that HOLD into open = strength")
            print("      • Gaps that FADE by 10 AM = sell the news")
            print("      • High volume = institutional, low volume = retail")
        
        if gaps_down:
            print(f"\n   🔴 {len(gaps_down)} stocks gapping down - Watch for:")
            print("      • Dips WITH catalysts = potential bounce")
            print("      • Dips WITHOUT catalysts = sector weakness")
            print("      • Check if positions need stops adjusted")
        
        print("\n   ⏰ NEXT STEPS:")
        print("      • Run again at 8:30 AM and 9:15 AM for updates")
        print("      • Check ATP for any additional movers not on watchlist")
        print("      • Prepare entry/exit plans based on gaps")
    
    def save_results(self, gaps_up, gaps_down, no_gaps):
        """Save results to file"""
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        output_file = log_dir / f"premarket_scan_{datetime.now().strftime('%Y-%m-%d_%H%M')}.json"
        
        with open(output_file, 'w') as f:
            json.dump({
                'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'threshold': self.threshold,
                'gaps_up': gaps_up,
                'gaps_down': gaps_down,
                'no_gaps': no_gaps
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Pre-Market Gap Scanner - Production Version')
    parser.add_argument('--threshold', type=float, default=5.0, help='Gap threshold percentage (default: 5.0)')
    
    args = parser.parse_args()
    
    scanner = PremarketGapScanner(args.threshold)
    gaps_up, gaps_down, no_gaps = scanner.scan()
    scanner.display_results(gaps_up, gaps_down, no_gaps)
    scanner.save_results(gaps_up, gaps_down, no_gaps)
    
    print("\n🐺 AWOOOO! Pre-market scan complete.\n")

if __name__ == '__main__':
    main()
