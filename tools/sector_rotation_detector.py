#!/usr/bin/env python3
"""
SECTOR ROTATION DETECTOR - PRODUCTION VERSION

Scans 15+ sectors, detects rotation, finds hottest names.
Shows you WHERE the money is flowing TODAY.

SUCCESS CRITERIA: Catch sector rotation 1-2 days before mainstream notices.

Usage:
    python3 sector_rotation_detector.py
    python3 sector_rotation_detector.py --top 5  # Top 5 sectors only
    python3 sector_rotation_detector.py --min-gain 3  # Only sectors up 3%+
"""

import yfinance as yf
from datetime import datetime, timedelta
import json
from pathlib import Path
import argparse
import time
from collections import defaultdict

# Sector definitions with tickers
SECTORS = {
    'NUCLEAR_URANIUM': {
        'name': '☢️ Nuclear/Uranium',
        'tickers': ['UUUU', 'UEC', 'LEU', 'CCJ', 'DNN', 'NXE', 'SMR', 'OKLO'],
        'thesis': 'AI data centers + Russian ban + SMRs'
    },
    'RARE_EARTH': {
        'name': '🌍 Rare Earth/Critical Minerals',
        'tickers': ['USAR', 'MP', 'ALB', 'LAC', 'SQM'],
        'thesis': 'US supply chain independence + EV batteries'
    },
    'QUANTUM': {
        'name': '⚛️ Quantum Computing',
        'tickers': ['QBTS', 'IONQ', 'RGTI', 'QUBT', 'ARQQ'],
        'thesis': 'CES 2026 catalyst + commercial revenue starting'
    },
    'ROBOTICS_AI': {
        'name': '🤖 Robotics/Physical AI',
        'tickers': ['ISRG', 'PATH', 'IRBT', 'RR', 'MKFG'],
        'thesis': 'Physical AI era + CES demos + automation'
    },
    'SPACE_SATELLITE': {
        'name': '🚀 Space/Satellite',
        'tickers': ['ASTS', 'RKLB', 'LUNR', 'IRDM', 'GSAT', 'RDW'],
        'thesis': 'Direct-to-cell + moon missions + space economy'
    },
    'DEFENSE_CYBER': {
        'name': '🛡️ Defense/Cybersecurity',
        'tickers': ['AISP', 'CACI', 'LDOS', 'BAH', 'SAIC', 'CRWD', 'PANW'],
        'thesis': 'NATO spending + Trump defense budget + cyber threats'
    },
    'CRYPTO_FINTECH': {
        'name': '₿ Crypto/Fintech',
        'tickers': ['COIN', 'HOOD', 'MSTR', 'MARA', 'RIOT', 'SOFI'],
        'thesis': 'Bitcoin rally + retail trading boom + crypto adoption'
    },
    'SEMI_EQUIPMENT': {
        'name': '🔧 Semiconductor Equipment',
        'tickers': ['AMAT', 'LRCX', 'KLAC', 'ASML', 'ENTG'],
        'thesis': 'AI chip buildout + picks & shovels play'
    },
    'AI_INFRASTRUCTURE': {
        'name': '🏢 AI Infrastructure/Data Centers',
        'tickers': ['VRT', 'SMCI', 'DELL', 'CRDO', 'NVDA', 'AMD'],
        'thesis': 'AI buildout + cooling + connectivity + compute'
    },
    'AI_SOFTWARE': {
        'name': '💻 AI Software',
        'tickers': ['PLTR', 'AI', 'SNOW', 'DDOG', 'NET', 'MDB'],
        'thesis': 'AI application layer + enterprise adoption'
    },
    'ENERGY_UTILITIES': {
        'name': '⚡ Energy/Utilities',
        'tickers': ['CEG', 'VST', 'EXC', 'PCG', 'AEP', 'DUK'],
        'thesis': 'Data center power demand + nuclear revival'
    },
    'EV_BATTERIES': {
        'name': '🔋 EV/Batteries',
        'tickers': ['TSLA', 'RIVN', 'LCID', 'ALB', 'ENVX', 'QS'],
        'thesis': 'EV adoption + battery tech + Trump tariffs'
    },
    'BIOTECH': {
        'name': '🧬 Biotech',
        'tickers': ['MRNA', 'BNTX', 'VRTX', 'REGN', 'GILD', 'CRSP'],
        'thesis': 'mRNA tech + gene editing + cancer immunotherapy'
    },
    'DRONES': {
        'name': '🛸 Drones/UAV',
        'tickers': ['AVAV', 'UAVS', 'JOBY', 'ACHR', 'LILM'],
        'thesis': 'China drone ban + military drones + air taxis'
    },
    'SEMICONDUCTORS': {
        'name': '💾 Semiconductors',
        'tickers': ['NVDA', 'AMD', 'AVGO', 'TSM', 'INTC', 'QCOM'],
        'thesis': 'AI chips + data center demand + edge computing'
    },
}

class SectorRotationDetector:
    def __init__(self, min_gain=0, top_n=None):
        self.min_gain = min_gain
        self.top_n = top_n
        self.sector_cache = {}
    
    def get_ticker_data(self, ticker):
        """Get today's performance for a ticker"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            current = info.get('currentPrice') or info.get('regularMarketPrice')
            prev_close = info.get('previousClose')
            volume = info.get('volume', 0)
            avg_volume = info.get('averageVolume', 1)
            
            if not current or not prev_close:
                return None
            
            change_pct = ((current - prev_close) / prev_close) * 100
            vol_ratio = volume / avg_volume if avg_volume > 0 else 1.0
            
            return {
                'ticker': ticker,
                'current': current,
                'prev_close': prev_close,
                'change_pct': change_pct,
                'volume': volume,
                'avg_volume': avg_volume,
                'vol_ratio': vol_ratio
            }
        except Exception as e:
            return None
    
    def scan_sector(self, sector_key, sector_data):
        """Scan single sector"""
        print(f"   {sector_data['name']}...", end=' ', flush=True)
        
        ticker_results = []
        for ticker in sector_data['tickers']:
            data = self.get_ticker_data(ticker)
            if data:
                ticker_results.append(data)
            time.sleep(0.2)  # Rate limiting
        
        if not ticker_results:
            print("✗ No data")
            return None
        
        # Calculate sector metrics
        avg_change = sum(t['change_pct'] for t in ticker_results) / len(ticker_results)
        total_vol_ratio = sum(t['vol_ratio'] for t in ticker_results) / len(ticker_results)
        
        # Find top performers
        ticker_results.sort(key=lambda x: x['change_pct'], reverse=True)
        top_movers = ticker_results[:3]
        
        # Count winners vs losers
        winners = len([t for t in ticker_results if t['change_pct'] > 0])
        losers = len([t for t in ticker_results if t['change_pct'] < 0])
        
        print(f"✓ {avg_change:+.2f}% avg")
        
        return {
            'sector': sector_key,
            'name': sector_data['name'],
            'thesis': sector_data['thesis'],
            'avg_change': avg_change,
            'vol_ratio': total_vol_ratio,
            'winners': winners,
            'losers': losers,
            'total_tickers': len(ticker_results),
            'top_movers': top_movers,
            'all_tickers': ticker_results
        }
    
    def detect_rotation(self):
        """Scan all sectors"""
        print(f"\n🔍 SECTOR ROTATION DETECTOR - PRODUCTION VERSION")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"   Scanning {len(SECTORS)} sectors")
        if self.min_gain > 0:
            print(f"   Filter: Only sectors up {self.min_gain}%+")
        print("=" * 80)
        
        print("\n   Scanning sectors...")
        results = []
        
        for sector_key, sector_data in SECTORS.items():
            result = self.scan_sector(sector_key, sector_data)
            if result:
                results.append(result)
        
        # Filter by min gain
        if self.min_gain > 0:
            results = [r for r in results if r['avg_change'] >= self.min_gain]
        
        # Sort by performance
        results.sort(key=lambda x: x['avg_change'], reverse=True)
        
        # Limit to top N if specified
        if self.top_n:
            results = results[:self.top_n]
        
        return results
    
    def display_results(self, results):
        """Display sector rotation results"""
        if not results:
            print("\n📊 No sectors meet criteria.")
            print("\n🐺 Try lowering --min-gain or removing filters")
            return
        
        print("\n" + "=" * 80)
        print("🔥 SECTOR ROTATION - HOT MONEY FLOW")
        print("=" * 80)
        
        # Overall market sentiment
        avg_sector_change = sum(r['avg_change'] for r in results) / len(results)
        hot_sectors = len([r for r in results if r['avg_change'] > 2])
        cold_sectors = len([r for r in results if r['avg_change'] < -2])
        
        print(f"\n📈 MARKET OVERVIEW:")
        print(f"   Average sector performance: {avg_sector_change:+.2f}%")
        print(f"   Hot sectors (>2%): {hot_sectors}")
        print(f"   Cold sectors (<-2%): {cold_sectors}")
        
        # Hot sectors
        hot = [r for r in results if r['avg_change'] > 0]
        if hot:
            print(f"\n🔥 HOT SECTORS ({len(hot)}):")
            print("=" * 80)
            
            for i, sector in enumerate(hot, 1):
                # Determine strength
                if sector['avg_change'] >= 5:
                    strength = "🔥🔥🔥 FIRE"
                elif sector['avg_change'] >= 3:
                    strength = "🔥🔥 VERY HOT"
                elif sector['avg_change'] >= 1:
                    strength = "🔥 HOT"
                else:
                    strength = "♨️ WARM"
                
                # Volume confirmation
                vol_signal = "📊 VOLUME" if sector['vol_ratio'] > 1.2 else ""
                
                print(f"\n{i}. {sector['name']}")
                print(f"   Performance: {sector['avg_change']:+.2f}% avg | {strength} {vol_signal}")
                print(f"   Breadth: {sector['winners']}/{sector['total_tickers']} winners")
                print(f"   Thesis: {sector['thesis']}")
                
                print(f"\n   💎 TOP MOVERS:")
                for mover in sector['top_movers'][:3]:
                    vol_flag = "📊" if mover['vol_ratio'] > 1.5 else ""
                    print(f"      • {mover['ticker']}: {mover['change_pct']:+.2f}% | ${mover['current']:.2f} {vol_flag}")
        
        # Cold sectors (contrarian opportunities)
        cold = [r for r in results if r['avg_change'] < 0]
        if cold:
            print(f"\n❄️ COLD SECTORS ({len(cold)}) - Contrarian Watch:")
            print("=" * 80)
            
            for sector in cold[-5:]:  # Show worst 5
                print(f"\n   {sector['name']}: {sector['avg_change']:+.2f}% avg")
                print(f"   Breadth: {sector['losers']}/{sector['total_tickers']} losers")
                
                # Show what's holding up
                best = sector['top_movers'][0]
                print(f"   Best in sector: {best['ticker']} {best['change_pct']:+.2f}%")
        
        print("\n" + "=" * 80)
        print("🐺 WOLF'S READ")
        print("=" * 80)
        
        # Identify rotation patterns
        if hot:
            print(f"\n   🎯 MONEY IS ROTATING INTO:")
            for sector in hot[:5]:
                # Calculate conviction score
                conviction = 0
                if sector['avg_change'] > 3: conviction += 30
                elif sector['avg_change'] > 1: conviction += 20
                
                if sector['vol_ratio'] > 1.2: conviction += 20
                
                breadth_pct = sector['winners'] / sector['total_tickers']
                if breadth_pct > 0.8: conviction += 30
                elif breadth_pct > 0.6: conviction += 20
                
                if sector['avg_change'] > 5 and sector['vol_ratio'] > 1.3:
                    conviction += 20  # Breakout signal
                
                conviction_label = ""
                if conviction >= 80:
                    conviction_label = "🔥 HIGHEST CONVICTION"
                elif conviction >= 60:
                    conviction_label = "✅ STRONG"
                elif conviction >= 40:
                    conviction_label = "👀 WATCH"
                else:
                    conviction_label = "⚠️ WEAK"
                
                print(f"      • {sector['name']}: {sector['avg_change']:+.2f}% | {conviction_label}")
        
        if cold:
            print(f"\n   ❄️ MONEY IS ROTATING OUT OF:")
            for sector in sorted(cold, key=lambda x: x['avg_change'])[:3]:
                print(f"      • {sector['name']}: {sector['avg_change']:+.2f}%")
        
        # Trading suggestions
        print("\n   💡 WHAT THIS MEANS FOR TRADING:")
        print("      • Focus new entries on HOT sectors with volume confirmation")
        print("      • Consider taking profits in COLD sectors showing weakness")
        print("      • Watch for COLD sectors bouncing = rotation opportunity")
        print("      • Breadth matters: 80%+ winners = sector-wide move, not just 1 name")
    
    def save_results(self, results):
        """Save to JSON"""
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        output_file = log_dir / f"sector_rotation_{datetime.now().strftime('%Y-%m-%d_%H%M')}.json"
        
        with open(output_file, 'w') as f:
            json.dump({
                'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'results': results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Sector Rotation Detector - Production Version')
    parser.add_argument('--min-gain', type=float, default=0, help='Minimum sector gain % (default: 0)')
    parser.add_argument('--top', type=int, help='Show only top N sectors')
    
    args = parser.parse_args()
    
    detector = SectorRotationDetector(args.min_gain, args.top)
    results = detector.detect_rotation()
    detector.display_results(results)
    
    if results:
        detector.save_results(results)
    
    print("\n🐺 AWOOOO! Sector rotation scan complete.\n")

if __name__ == '__main__':
    main()
