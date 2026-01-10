#!/usr/bin/env python3
"""
AFTER-HOURS MOMENTUM SCANNER - CATCH IT TONIGHT

Scans for unusual after-hours volume + price action.
The big moves often START after hours, BEFORE pre-market.

If something is ripping at 11 PM, it gaps up at 9:30 AM.

Usage:
    python3 after_hours_scanner.py
    python3 after_hours_scanner.py --min-volume 100000  # 100K+ volume
"""

import yfinance as yf
from datetime import datetime, timedelta
import json
from pathlib import Path
import argparse
import time

# Extended watchlist - all sectors
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
    # Drones (hottest sector today)
    'AVAV', 'UAVS', 'JOBY', 'ACHR',
    # Space
    'ASTS', 'RKLB', 'LUNR', 'RDW', 'IRDM',
    # Crypto
    'COIN', 'HOOD', 'MSTR', 'MARA', 'RIOT',
    # Semi equipment
    'AMAT', 'LRCX', 'KLAC', 'ASML',
    # AI Infrastructure
    'NVDA', 'AMD', 'SMCI', 'DELL', 'VRT', 'CRDO',
    # AI Software
    'PLTR', 'AI', 'SNOW', 'DDOG', 'NET',
    # Robotics
    'ISRG', 'PATH', 'RR',
    # EV/Battery
    'TSLA', 'RIVN', 'LCID', 'ENVX',
    # Wildcards (high beta, news-driven)
    'GME', 'AMC', 'BBBY', 'WISH', 'SOFI',
]

class AfterHoursScanner:
    def __init__(self, min_volume=50000, min_move=2.0):
        self.min_volume = min_volume
        self.min_move = min_move
    
    def get_after_hours_data(self, ticker):
        """Get after-hours price and volume"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get today's data including after-hours
            hist = stock.history(period='1d', interval='1m', prepost=True)
            
            if hist.empty:
                return None
            
            # Get regular market close (4 PM ET)
            regular_hours = hist.between_time('09:30', '16:00')
            if regular_hours.empty:
                return None
            
            regular_close = regular_hours['Close'].iloc[-1]
            
            # Get after-hours data (4 PM - 8 PM ET)
            after_hours = hist.between_time('16:00', '20:00')
            
            if after_hours.empty:
                return None
            
            # Current after-hours price
            current_price = after_hours['Close'].iloc[-1]
            ah_volume = after_hours['Volume'].sum()
            
            # Calculate move
            move_pct = ((current_price - regular_close) / regular_close) * 100
            
            # Get info for context
            info = stock.info
            avg_volume = info.get('averageVolume', 0)
            market_cap = info.get('marketCap', 0)
            
            return {
                'ticker': ticker,
                'regular_close': regular_close,
                'current_price': current_price,
                'move_pct': move_pct,
                'ah_volume': ah_volume,
                'avg_volume': avg_volume,
                'market_cap': market_cap,
                'last_update': after_hours.index[-1].strftime('%H:%M ET')
            }
            
        except Exception as e:
            return None
    
    def scan(self):
        """Scan for after-hours movers"""
        print(f"\n🌙 AFTER-HOURS MOMENTUM SCANNER")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"   Scanning {len(WATCHLIST)} tickers")
        print(f"   Filter: {self.min_move:+.1f}% move + {self.min_volume:,} volume")
        print("=" * 80)
        
        print("\n   Scanning after-hours action...")
        results = []
        
        for ticker in WATCHLIST:
            print(f"      {ticker}...", end=' ', flush=True)
            
            data = self.get_after_hours_data(ticker)
            
            if data and abs(data['move_pct']) >= self.min_move and data['ah_volume'] >= self.min_volume:
                results.append(data)
                print(f"✓ {data['move_pct']:+.2f}% ({data['ah_volume']:,} vol)")
            else:
                print("✓")
            
            time.sleep(0.3)  # Rate limiting
        
        return results
    
    def display_results(self, results):
        """Display after-hours movers"""
        if not results:
            print("\n📊 No significant after-hours movement detected.")
            print("\n🐺 This could mean:")
            print("   • Quiet night, wait for pre-market")
            print("   • Try lowering --min-move threshold")
            print("   • Check back at 4 AM for pre-market action")
            return
        
        # Separate movers
        movers_up = sorted([r for r in results if r['move_pct'] > 0], 
                          key=lambda x: x['move_pct'], reverse=True)
        movers_down = sorted([r for r in results if r['move_pct'] < 0], 
                            key=lambda x: x['move_pct'])
        
        print("\n" + "=" * 80)
        print("🔥 AFTER-HOURS MOMENTUM DETECTED")
        print("=" * 80)
        
        if movers_up:
            print(f"\n📈 MOVING UP ({len(movers_up)}):")
            print("=" * 80)
            
            for i, data in enumerate(movers_up, 1):
                # Determine strength
                if data['move_pct'] >= 10:
                    strength = "🚀 ROCKET"
                elif data['move_pct'] >= 5:
                    strength = "🔥 HOT"
                elif data['move_pct'] >= 3:
                    strength = "♨️ WARM"
                else:
                    strength = "📈 UP"
                
                # Volume analysis
                vol_ratio = data['ah_volume'] / (data['avg_volume'] * 0.25) if data['avg_volume'] > 0 else 0
                vol_signal = f"📊 {vol_ratio:.1f}x normal AH volume" if vol_ratio > 1.5 else ""
                
                # Market cap
                if data['market_cap'] > 0:
                    if data['market_cap'] > 10_000_000_000:
                        cap = f"${data['market_cap']/1_000_000_000:.1f}B"
                    else:
                        cap = f"${data['market_cap']/1_000_000:.0f}M"
                else:
                    cap = "N/A"
                
                print(f"\n{i}. {data['ticker']} {strength}")
                print(f"   Regular Close: ${data['regular_close']:.2f}")
                print(f"   After-Hours: ${data['current_price']:.2f} ({data['move_pct']:+.2f}%)")
                print(f"   AH Volume: {data['ah_volume']:,} {vol_signal}")
                print(f"   Market Cap: {cap}")
                print(f"   Last Update: {data['last_update']}")
        
        if movers_down:
            print(f"\n📉 MOVING DOWN ({len(movers_down)}):")
            print("=" * 80)
            
            for i, data in enumerate(movers_down, 1):
                if data['move_pct'] <= -10:
                    strength = "💥 CRATER"
                elif data['move_pct'] <= -5:
                    strength = "🔻 DUMP"
                elif data['move_pct'] <= -3:
                    strength = "📉 DOWN"
                else:
                    strength = "⬇️ WEAK"
                
                vol_ratio = data['ah_volume'] / (data['avg_volume'] * 0.25) if data['avg_volume'] > 0 else 0
                vol_signal = f"📊 {vol_ratio:.1f}x normal AH volume" if vol_ratio > 1.5 else ""
                
                if data['market_cap'] > 0:
                    if data['market_cap'] > 10_000_000_000:
                        cap = f"${data['market_cap']/1_000_000_000:.1f}B"
                    else:
                        cap = f"${data['market_cap']/1_000_000:.0f}M"
                else:
                    cap = "N/A"
                
                print(f"\n{i}. {data['ticker']} {strength}")
                print(f"   Regular Close: ${data['regular_close']:.2f}")
                print(f"   After-Hours: ${data['current_price']:.2f} ({data['move_pct']:+.2f}%)")
                print(f"   AH Volume: {data['ah_volume']:,} {vol_signal}")
                print(f"   Market Cap: {cap}")
                print(f"   Last Update: {data['last_update']}")
        
        print("\n" + "=" * 80)
        print("🐺 WOLF'S READ")
        print("=" * 80)
        
        # Key signals
        big_movers = [r for r in results if abs(r['move_pct']) >= 5]
        high_volume = [r for r in results if r['ah_volume'] > r['avg_volume'] * 0.5]
        
        if big_movers:
            print(f"\n   🚨 BIG MOVERS (5%+ after hours):")
            for r in big_movers:
                print(f"      • {r['ticker']}: {r['move_pct']:+.2f}% | ${r['current_price']:.2f}")
            print("\n   💡 Big after-hours moves often continue into pre-market and open")
        
        if high_volume:
            print(f"\n   📊 HIGH VOLUME (>50% normal AH volume):")
            for r in high_volume:
                vol_pct = (r['ah_volume'] / (r['avg_volume'] * 0.25)) * 100
                print(f"      • {r['ticker']}: {r['ah_volume']:,} volume ({vol_pct:.0f}% of normal AH)")
            print("\n   💡 Unusual volume = news catalyst or institutional positioning")
        
        print("\n   🎯 WHAT TO DO:")
        print("      • Research WHY these are moving (news, earnings, PR)")
        print("      • Set alerts for pre-market continuation (4-6 AM)")
        print("      • If 5%+ AH move + volume, often gaps at open")
        print("      • Don't chase at open - wait for pullback or confirmation")
        
        # Sector analysis
        your_tickers = ['UUUU', 'USAR', 'AISP']
        your_movers = [r for r in results if r['ticker'] in your_tickers]
        
        if your_movers:
            print(f"\n   🎯 YOUR POSITIONS:")
            for r in your_movers:
                print(f"      • {r['ticker']}: {r['move_pct']:+.2f}% after hours")
            print("\n   ⚠️ Watch these at pre-market open!")
    
    def save_results(self, results):
        """Save to JSON"""
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        output_file = log_dir / f"after_hours_{datetime.now().strftime('%Y-%m-%d_%H%M')}.json"
        
        with open(output_file, 'w') as f:
            json.dump({
                'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'results': results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='After-Hours Momentum Scanner')
    parser.add_argument('--min-move', type=float, default=2.0, help='Minimum move % (default: 2.0)')
    parser.add_argument('--min-volume', type=int, default=50000, help='Minimum volume (default: 50000)')
    
    args = parser.parse_args()
    
    scanner = AfterHoursScanner(args.min_volume, args.min_move)
    results = scanner.scan()
    scanner.display_results(results)
    
    if results:
        scanner.save_results(results)
    
    print("\n🐺 AWOOOO! After-hours scan complete.\n")
    print("💡 TIP: Run again at 4 AM, 5 AM, 6 AM to catch pre-market momentum")

if __name__ == '__main__':
    main()
