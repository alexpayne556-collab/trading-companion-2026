#!/usr/bin/env python3
"""
OPTIONS FLOW SCANNER - Unusual Options Activity Tracker

Scrapes Barchart.com for unusual options activity on watchlist tickers.
Alerts on large call/put volume that could signal incoming moves.

Usage:
    python3 options_flow_scanner.py                    # Scan default watchlist
    python3 options_flow_scanner.py --add-ticker TSLA  # Add specific ticker
    python3 options_flow_scanner.py --watch            # Continuous monitoring
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import time
import argparse
from pathlib import Path

# Default watchlist - Tyr's current positions + CES plays
WATCHLIST = [
    'UUUU', 'USAR', 'AISP',  # Current positions
    'RR', 'QBTS', 'QUBT', 'RGTI', 'IONQ',  # CES quantum/robotics
    'SMCI', 'CRDO', 'VRT',  # AI infrastructure
    'RDW', 'RKLB', 'LUNR', 'ASTS',  # Space
    'UEC', 'CCJ', 'SMR', 'LEU',  # Nuclear
]

class OptionsFlowScanner:
    def __init__(self, watchlist=None):
        self.watchlist = watchlist or WATCHLIST
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_unusual_options(self, ticker):
        """Scrape Barchart for unusual options activity"""
        url = f"https://www.barchart.com/stocks/quotes/{ticker}/options"
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for unusual activity indicators
            unusual_data = {
                'ticker': ticker,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'unusual_calls': [],
                'unusual_puts': [],
                'total_call_volume': 0,
                'total_put_volume': 0,
                'put_call_ratio': 0
            }
            
            # Parse options chain table
            tables = soup.find_all('table', class_='datatable')
            
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) < 8:
                        continue
                        
                    try:
                        strike = cells[0].text.strip()
                        volume = int(cells[4].text.strip().replace(',', ''))
                        open_interest = int(cells[5].text.strip().replace(',', ''))
                        premium = cells[7].text.strip()
                        
                        # Flag unusual activity: volume > 10x open interest OR volume > 1000
                        if volume > 0 and (volume > 10 * open_interest or volume > 1000):
                            option_type = 'call' if 'call' in str(row).lower() else 'put'
                            
                            option_data = {
                                'strike': strike,
                                'volume': volume,
                                'open_interest': open_interest,
                                'ratio': round(volume / max(open_interest, 1), 2),
                                'premium': premium
                            }
                            
                            if option_type == 'call':
                                unusual_data['unusual_calls'].append(option_data)
                                unusual_data['total_call_volume'] += volume
                            else:
                                unusual_data['unusual_puts'].append(option_data)
                                unusual_data['total_put_volume'] += volume
                                
                    except (ValueError, AttributeError, IndexError):
                        continue
            
            # Calculate put/call ratio
            if unusual_data['total_call_volume'] > 0:
                unusual_data['put_call_ratio'] = round(
                    unusual_data['total_put_volume'] / unusual_data['total_call_volume'], 2
                )
            
            return unusual_data if (unusual_data['unusual_calls'] or unusual_data['unusual_puts']) else None
            
        except Exception as e:
            print(f"   ⚠️  Error scanning {ticker}: {str(e)}")
            return None
    
    def scan_watchlist(self):
        """Scan all tickers in watchlist"""
        print(f"\n🔍 OPTIONS FLOW SCANNER - Unusual Activity Hunter")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"   Scanning {len(self.watchlist)} tickers for unusual options flow")
        print("=" * 80)
        
        results = []
        
        for ticker in self.watchlist:
            print(f"   Checking {ticker}...", end=' ')
            data = self.get_unusual_options(ticker)
            
            if data and (data['unusual_calls'] or data['unusual_puts']):
                results.append(data)
                print(f"✓ UNUSUAL ACTIVITY FOUND")
            else:
                print("✓")
            
            time.sleep(1)  # Rate limiting
        
        return results
    
    def display_results(self, results):
        """Display unusual options activity"""
        if not results:
            print("\n📊 No unusual options activity detected on watchlist.")
            print("\n🐺 This means either:")
            print("   • No big players positioning yet")
            print("   • Activity already happened (check historical)")
            print("   • Our tickers aren't hot right now")
            return
        
        print("\n" + "=" * 80)
        print("🚨 UNUSUAL OPTIONS ACTIVITY DETECTED")
        print("=" * 80)
        
        # Sort by total volume
        results.sort(key=lambda x: x['total_call_volume'] + x['total_put_volume'], reverse=True)
        
        for i, data in enumerate(results, 1):
            ticker = data['ticker']
            total_volume = data['total_call_volume'] + data['total_put_volume']
            
            print(f"\n{i}. {ticker} — Total Volume: {total_volume:,}")
            print(f"   Put/Call Ratio: {data['put_call_ratio']} ", end='')
            
            if data['put_call_ratio'] > 1.5:
                print("🔴 BEARISH")
            elif data['put_call_ratio'] < 0.5:
                print("🟢 BULLISH")
            else:
                print("⚪ NEUTRAL")
            
            if data['unusual_calls']:
                print(f"\n   🟢 UNUSUAL CALLS ({len(data['unusual_calls'])}):")
                for call in sorted(data['unusual_calls'], key=lambda x: x['volume'], reverse=True)[:3]:
                    print(f"      Strike: {call['strike']} | Vol: {call['volume']:,} | OI: {call['open_interest']:,} | Ratio: {call['ratio']}x")
            
            if data['unusual_puts']:
                print(f"\n   🔴 UNUSUAL PUTS ({len(data['unusual_puts'])}):")
                for put in sorted(data['unusual_puts'], key=lambda x: x['volume'], reverse=True)[:3]:
                    print(f"      Strike: {put['strike']} | Vol: {put['volume']:,} | OI: {put['open_interest']:,} | Ratio: {put['ratio']}x")
        
        print("\n" + "=" * 80)
        print("🐺 WOLF'S READ ON OPTIONS FLOW")
        print("=" * 80)
        
        bullish = [r for r in results if r['put_call_ratio'] < 0.5]
        bearish = [r for r in results if r['put_call_ratio'] > 1.5]
        
        if bullish:
            print(f"\n   🟢 BULLISH FLOW ({len(bullish)}):")
            for r in bullish[:5]:
                print(f"      • {r['ticker']} - Call volume: {r['total_call_volume']:,} | P/C: {r['put_call_ratio']}")
        
        if bearish:
            print(f"\n   🔴 BEARISH FLOW ({len(bearish)}):")
            for r in bearish[:5]:
                print(f"      • {r['ticker']} - Put volume: {r['total_put_volume']:,} | P/C: {r['put_call_ratio']}")
        
        print("\n   🎯 WHAT THIS MEANS:")
        print("      • Unusual calls = Smart money betting on upside")
        print("      • High volume vs OI = NEW positions being opened")
        print("      • Low P/C ratio (<0.5) = Bullish sentiment")
        print("      • High P/C ratio (>1.5) = Bearish sentiment or hedging")
        print("\n   ⚠️  REMEMBER: This is 15-30 min delayed. Entry window may have passed.")
        
    def save_results(self, results):
        """Save results to JSON"""
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        output_file = log_dir / 'options_flow.json'
        
        with open(output_file, 'w') as f:
            json.dump({
                'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'results': results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Options Flow Scanner - Find unusual activity')
    parser.add_argument('--add-ticker', action='append', help='Add ticker to scan')
    parser.add_argument('--watch', action='store_true', help='Continuous monitoring mode')
    parser.add_argument('--interval', type=int, default=15, help='Minutes between scans in watch mode')
    
    args = parser.parse_args()
    
    watchlist = WATCHLIST.copy()
    if args.add_ticker:
        watchlist.extend([t.upper() for t in args.add_ticker])
    
    scanner = OptionsFlowScanner(watchlist)
    
    if args.watch:
        print(f"\n🐺 WOLF WATCH MODE - Scanning every {args.interval} minutes")
        print("   Press Ctrl+C to stop\n")
        
        try:
            while True:
                results = scanner.scan_watchlist()
                scanner.display_results(results)
                if results:
                    scanner.save_results(results)
                
                print(f"\n⏰ Next scan in {args.interval} minutes...")
                time.sleep(args.interval * 60)
        except KeyboardInterrupt:
            print("\n\n🐺 Hunt paused. AWOOOO!")
    else:
        results = scanner.scan_watchlist()
        scanner.display_results(results)
        if results:
            scanner.save_results(results)
        
        print("\n🐺 AWOOOO! Options flow scanned.")

if __name__ == '__main__':
    main()
