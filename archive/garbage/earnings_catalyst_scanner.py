#!/usr/bin/env python3
"""
EARNINGS CATALYST SCANNER - KNOW BEFORE IT MOVES

Scans upcoming earnings reports to find catalysts BEFORE they pop.
Focuses on pre-market earnings that gap at open.

Strategy:
- Buy day before earnings if technical setup + sector strength
- OR buy at open if earnings beat + guidance raise

Usage:
    python3 earnings_catalyst_scanner.py
    python3 earnings_catalyst_scanner.py --days 3  # Next 3 days
"""

import yfinance as yf
from datetime import datetime, timedelta
import json
from pathlib import Path
import argparse
import time

# Watchlist - focus on your sectors
WATCHLIST = [
    # Your positions
    'UUUU', 'USAR', 'AISP',
    # Nuclear
    'UEC', 'CCJ', 'SMR', 'LEU', 'DNN', 'NXE', 'OKLO',
    # Quantum
    'QBTS', 'IONQ', 'RGTI', 'QUBT',
    # Rare earth
    'MP', 'ALB', 'LAC',
    # Defense
    'CACI', 'LDOS', 'BAH', 'SAIC', 'CRWD', 'PANW',
    # Drones
    'AVAV', 'UAVS', 'JOBY',
    # Space
    'ASTS', 'RKLB', 'LUNR', 'RDW',
    # Crypto
    'COIN', 'HOOD', 'MSTR', 'MARA',
    # Semi equipment
    'AMAT', 'LRCX', 'KLAC',
    # AI
    'NVDA', 'AMD', 'SMCI', 'PLTR', 'AI',
    # Robotics
    'ISRG', 'PATH',
    # EV
    'TSLA', 'RIVN', 'LCID',
]

class EarningsCatalystScanner:
    def __init__(self, days_ahead=7):
        self.days_ahead = days_ahead
        self.today = datetime.now().date()
        self.end_date = self.today + timedelta(days=days_ahead)
    
    def get_earnings_date(self, ticker):
        """Get upcoming earnings date"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get earnings date
            earnings_date = info.get('earningsDate')
            if not earnings_date:
                return None
            
            # yfinance returns a tuple of dates sometimes
            if isinstance(earnings_date, list) and len(earnings_date) > 0:
                earnings_date = earnings_date[0]
            
            # Convert to datetime
            if isinstance(earnings_date, int):
                earnings_date = datetime.fromtimestamp(earnings_date).date()
            elif isinstance(earnings_date, str):
                earnings_date = datetime.strptime(earnings_date, '%Y-%m-%d').date()
            
            # Check if within our window
            if earnings_date < self.today or earnings_date > self.end_date:
                return None
            
            # Get additional context
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            target_price = info.get('targetMeanPrice', 0)
            analyst_rating = info.get('recommendationKey', 'N/A')
            market_cap = info.get('marketCap', 0)
            pe_ratio = info.get('trailingPE', 0)
            
            # Calculate upside if target exists
            upside = ((target_price - current_price) / current_price * 100) if target_price and current_price else 0
            
            return {
                'ticker': ticker,
                'earnings_date': earnings_date.strftime('%Y-%m-%d'),
                'days_until': (earnings_date - self.today).days,
                'current_price': current_price,
                'target_price': target_price,
                'upside': upside,
                'analyst_rating': analyst_rating,
                'market_cap': market_cap,
                'pe_ratio': pe_ratio
            }
            
        except Exception as e:
            return None
    
    def scan(self):
        """Scan for upcoming earnings"""
        print(f"\n📅 EARNINGS CATALYST SCANNER")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"   Scanning {len(WATCHLIST)} tickers")
        print(f"   Window: Next {self.days_ahead} days")
        print("=" * 80)
        
        print("\n   Scanning earnings calendar...")
        results = []
        
        for ticker in WATCHLIST:
            print(f"      {ticker}...", end=' ', flush=True)
            
            data = self.get_earnings_date(ticker)
            if data:
                results.append(data)
                print(f"✓ {data['earnings_date']} ({data['days_until']}d)")
            else:
                print("✓")
            
            time.sleep(0.3)  # Rate limiting
        
        return results
    
    def display_results(self, results):
        """Display earnings calendar"""
        if not results:
            print("\n📊 No earnings in the next {self.days_ahead} days.")
            print("\n🐺 Your watchlist tickers don't report this week.")
            return
        
        # Sort by date
        results.sort(key=lambda x: x['days_until'])
        
        print("\n" + "=" * 80)
        print("📅 UPCOMING EARNINGS CATALYSTS")
        print("=" * 80)
        
        # Group by date
        by_date = {}
        for r in results:
            date = r['earnings_date']
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(r)
        
        for date in sorted(by_date.keys()):
            tickers_on_date = by_date[date]
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            days_until = (date_obj - self.today).days
            
            # Determine if pre-market or after-close (assume pre-market)
            day_name = date_obj.strftime('%A')
            
            print(f"\n📆 {day_name}, {date} ({days_until} days)")
            print("─" * 80)
            
            for data in tickers_on_date:
                # Determine opportunity level
                opportunity = ""
                if data['upside'] > 20:
                    opportunity = "🚀 HIGH UPSIDE"
                elif data['upside'] > 10:
                    opportunity = "📈 UPSIDE"
                elif data['upside'] < -10:
                    opportunity = "⚠️ DOWNSIDE RISK"
                
                # Analyst rating signal
                rating_signal = ""
                if data['analyst_rating'] in ['strong_buy', 'buy']:
                    rating_signal = "✅ BUY RATING"
                elif data['analyst_rating'] in ['hold']:
                    rating_signal = "⚪ HOLD RATING"
                elif data['analyst_rating'] in ['sell', 'strong_sell']:
                    rating_signal = "🔻 SELL RATING"
                
                # Market cap
                if data['market_cap'] > 0:
                    if data['market_cap'] > 10_000_000_000:
                        cap = f"${data['market_cap']/1_000_000_000:.1f}B"
                    else:
                        cap = f"${data['market_cap']/1_000_000:.0f}M"
                else:
                    cap = "N/A"
                
                print(f"\n   {data['ticker']} - ${data['current_price']:.2f} | {cap} {opportunity}")
                if data['target_price'] > 0:
                    print(f"   Analyst Target: ${data['target_price']:.2f} ({data['upside']:+.1f}% upside)")
                if rating_signal:
                    print(f"   {rating_signal}")
                if data['pe_ratio'] > 0:
                    print(f"   P/E: {data['pe_ratio']:.1f}")
        
        print("\n" + "=" * 80)
        print("🐺 WOLF'S READ")
        print("=" * 80)
        
        # Tomorrow's earnings
        tomorrow = (self.today + timedelta(days=1)).strftime('%Y-%m-%d')
        tomorrow_earnings = [r for r in results if r['earnings_date'] == tomorrow]
        
        if tomorrow_earnings:
            print(f"\n   🚨 EARNINGS TOMORROW ({len(tomorrow_earnings)}):")
            for r in tomorrow_earnings:
                print(f"      • {r['ticker']}: ${r['current_price']:.2f}")
                if r['upside'] > 10:
                    print(f"        → {r['upside']:+.1f}% analyst upside = WATCH")
            print("\n   💡 These can gap 5-20% on earnings beats")
            print("   Strategy:")
            print("      • If sector is HOT + analysts bullish → buy day before")
            print("      • If earnings beat + guidance raise → buy at open pullback")
            print("      • If earnings miss → avoid or short")
        
        # This week
        this_week = [r for r in results if r['days_until'] <= 7]
        high_upside = [r for r in this_week if r['upside'] > 15]
        
        if high_upside:
            print(f"\n   📈 HIGH UPSIDE SETUPS (15%+ target):")
            for r in high_upside:
                print(f"      • {r['ticker']}: ${r['current_price']:.2f} → ${r['target_price']:.2f} ({r['upside']:+.1f}%)")
                print(f"        Earnings: {r['earnings_date']} ({r['days_until']}d)")
        
        # Your positions
        your_tickers = ['UUUU', 'USAR', 'AISP']
        your_earnings = [r for r in results if r['ticker'] in your_tickers]
        
        if your_earnings:
            print(f"\n   🎯 YOUR POSITIONS:")
            for r in your_earnings:
                print(f"      • {r['ticker']}: Earnings {r['earnings_date']} ({r['days_until']}d)")
            print("\n   ⚠️ Plan your exit strategy BEFORE earnings!")
        
        print("\n   🎯 EARNINGS STRATEGY:")
        print("      • Buy day before if: Sector hot + analyst upgrade + technical setup")
        print("      • Sell into earnings if: Already up 10%+ + no conviction")
        print("      • Buy after beat if: Stock dips on good news (overreaction)")
        print("      • NEVER hold through earnings without conviction")
    
    def save_results(self, results):
        """Save to JSON"""
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        output_file = log_dir / f"earnings_catalyst_{datetime.now().strftime('%Y-%m-%d_%H%M')}.json"
        
        with open(output_file, 'w') as f:
            json.dump({
                'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'results': results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Earnings Catalyst Scanner')
    parser.add_argument('--days', type=int, default=7, help='Days ahead to scan (default: 7)')
    
    args = parser.parse_args()
    
    scanner = EarningsCatalystScanner(args.days)
    results = scanner.scan()
    scanner.display_results(results)
    
    if results:
        scanner.save_results(results)
    
    print("\n🐺 AWOOOO! Earnings catalyst scan complete.\n")

if __name__ == '__main__':
    main()
