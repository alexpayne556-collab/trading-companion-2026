#!/usr/bin/env python3
"""
🐺 AI FUEL CHAIN HEATMAP
========================
Tracks the ENTIRE $5.2 trillion AI infrastructure ecosystem
All 7 layers. All sectors. Real-time strength ranking.

Usage:
    python ai_fuel_chain_heatmap.py              # Run once
    python ai_fuel_chain_heatmap.py --live       # Auto-refresh
    python ai_fuel_chain_heatmap.py --detailed   # Show all tickers
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time
import argparse
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# THE AI FUEL CHAIN — $5.2 TRILLION ECOSYSTEM
# ============================================================

AI_FUEL_CHAIN = {
    '1_POWER_NUCLEAR': {
        'name': '🔌 POWER (Nuclear)',
        'description': 'The oxygen. AI needs 1GW+ per campus.',
        'tickers': ['UUUU', 'SMR', 'LEU', 'OKLO', 'CCJ', 'DNN', 'UEC', 'NXE', 'NNE'],
        'catalyst': 'Data centers need 750K homes worth of power EACH'
    },
    '2_POWER_UTILITIES': {
        'name': '🔌 POWER (Utilities)',
        'description': 'Grid expansion and generation.',
        'tickers': ['NEE', 'VST', 'CEG', 'WMB'],
        'catalyst': 'Peak demand doubling from 2.8GW to 7GW by 2030'
    },
    '3_COOLING': {
        'name': '🧊 COOLING',
        'description': 'The blood. Rack density hitting 1000kW by 2029.',
        'tickers': ['VRT', 'MOD', 'NVT', 'JCI'],
        'catalyst': 'NVIDIA racks at 132kW now, 240kW coming'
    },
    '4_NETWORKING': {
        'name': '🔗 NETWORKING',
        'description': 'The nerves. Data movement bottlenecks.',
        'tickers': ['ANET', 'CRDO', 'FN', 'CIEN'],
        'catalyst': 'Cluster efficiency = competitive advantage'
    },
    '5_PHOTONICS': {
        'name': '💡 PHOTONICS',
        'description': 'THE EMERGING PLAY. Light > Copper.',
        'tickers': ['LITE', 'AAOI', 'GFS', 'COHR'],
        'catalyst': 'LITE 4x in 2025. Copper wall forcing adoption.'
    },
    '6_CHIPS': {
        'name': '🧠 CHIPS',
        'description': 'The brain. NVIDIA alternatives.',
        'tickers': ['AMD', 'MRVL', 'AVGO', 'INTC', 'AMKR'],
        'catalyst': 'AMD OpenAI partnership. Custom ASICs rising.'
    },
    '7_STORAGE': {
        'name': '💾 STORAGE',
        'description': 'The memory. WDC +300% in 2025.',
        'tickers': ['MU', 'WDC', 'STX'],
        'catalyst': 'HBM demand exploding for AI training'
    },
    '8_DATACENTER_REITS': {
        'name': '🏢 DATA CENTER REITs',
        'description': 'The body. Real estate for AI.',
        'tickers': ['EQIX', 'DLR'],
        'catalyst': 'Hyperscale buildout accelerating'
    },
    '9_DATACENTER_BUILDERS': {
        'name': '🏗️ DC BUILDERS',
        'description': 'Construction and deployment.',
        'tickers': ['EME', 'FIX', 'CLS', 'SMCI'],
        'catalyst': 'Turning blueprints into live capacity'
    },
    '10_QUANTUM': {
        'name': '⚛️ QUANTUM',
        'description': 'Speculative. Next frontier.',
        'tickers': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
        'catalyst': 'Long-term bet on quantum supremacy'
    },
    '11_SPACE_DEFENSE': {
        'name': '🚀 SPACE/DEFENSE',
        'description': 'Your current holdings.',
        'tickers': ['SIDU', 'LUNR', 'RKLB', 'RDW', 'ASTS', 'BKSY', 'PL'],
        'catalyst': 'SIDU $151B contract. Defense spending.'
    },
    '12_AI_SOFTWARE': {
        'name': '🤖 AI SOFTWARE',
        'description': 'The applications layer.',
        'tickers': ['PLTR', 'AI', 'PATH', 'SOUN', 'UPST'],
        'catalyst': 'Enterprise AI adoption accelerating'
    }
}

# Priority watchlist (your core positions)
PRIORITY_WATCHLIST = [
    'UUUU', 'SMR', 'LEU', 'OKLO', 'CCJ',  # Nuclear
    'VRT', 'LITE', 'COHR',                 # Cooling/Photonics
    'SIDU', 'LUNR', 'RDW', 'RKLB',         # Space/Defense
    'MU', 'AMD', 'MRVL',                   # Chips/Storage
    'IONQ', 'RGTI', 'QBTS'                 # Quantum
]

# ============================================================
# SCANNER FUNCTIONS
# ============================================================

def get_eastern_time():
    """Get current time in Eastern timezone"""
    eastern = pytz.timezone('US/Eastern')
    return datetime.now(eastern)

def get_sector_data(sector_key, sector_info):
    """Fetch data for all tickers in a sector"""
    results = []
    
    for ticker in sector_info['tickers']:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1mo', prepost=True)
            
            if len(hist) < 5:
                continue
            
            current = hist['Close'].iloc[-1]
            
            # 1-day change
            if len(hist) >= 2:
                prev = hist['Close'].iloc[-2]
                change_1d = ((current - prev) / prev) * 100
            else:
                change_1d = 0
            
            # 5-day change
            if len(hist) >= 5:
                prev_5d = hist['Close'].iloc[-5]
                change_5d = ((current - prev_5d) / prev_5d) * 100
            else:
                change_5d = 0
            
            # 20-day change
            if len(hist) >= 20:
                prev_20d = hist['Close'].iloc[-20]
                change_20d = ((current - prev_20d) / prev_20d) * 100
            else:
                change_20d = change_5d
            
            # Volume ratio
            avg_vol = hist['Volume'].tail(20).mean()
            today_vol = hist['Volume'].iloc[-1]
            vol_ratio = today_vol / avg_vol if avg_vol > 0 else 1
            
            # Distance from 20-day high
            high_20 = hist['High'].tail(20).max()
            pct_from_high = ((current - high_20) / high_20) * 100
            
            results.append({
                'ticker': ticker,
                'sector': sector_key,
                'sector_name': sector_info['name'],
                'price': current,
                'change_1d': change_1d,
                'change_5d': change_5d,
                'change_20d': change_20d,
                'vol_ratio': vol_ratio,
                'pct_from_high': pct_from_high,
                'priority': ticker in PRIORITY_WATCHLIST
            })
            
        except Exception as e:
            pass
    
    return results

def calculate_sector_strength(results):
    """Calculate aggregate sector strength"""
    sector_stats = {}
    
    for sector_key in AI_FUEL_CHAIN.keys():
        sector_data = [r for r in results if r['sector'] == sector_key]
        
        if sector_data:
            avg_1d = sum(r['change_1d'] for r in sector_data) / len(sector_data)
            avg_5d = sum(r['change_5d'] for r in sector_data) / len(sector_data)
            avg_20d = sum(r['change_20d'] for r in sector_data) / len(sector_data)
            avg_vol = sum(r['vol_ratio'] for r in sector_data) / len(sector_data)
            
            # Strength score: weighted momentum
            strength = avg_5d * 0.5 + avg_1d * 0.3 + avg_20d * 0.2
            
            sector_stats[sector_key] = {
                'name': AI_FUEL_CHAIN[sector_key]['name'],
                'change_1d': avg_1d,
                'change_5d': avg_5d,
                'change_20d': avg_20d,
                'vol_ratio': avg_vol,
                'strength': strength,
                'count': len(sector_data),
                'description': AI_FUEL_CHAIN[sector_key]['description']
            }
    
    return sector_stats

def scan_full_ecosystem(detailed=False):
    """Scan the entire AI fuel chain"""
    all_results = []
    
    print("\n⚡ SCANNING AI FUEL CHAIN ECOSYSTEM...")
    print("   $5.2 TRILLION by 2030. Every layer. Every ticker.\n")
    
    total_tickers = sum(len(s['tickers']) for s in AI_FUEL_CHAIN.values())
    scanned = 0
    
    for sector_key, sector_info in AI_FUEL_CHAIN.items():
        sector_results = get_sector_data(sector_key, sector_info)
        all_results.extend(sector_results)
        scanned += len(sector_info['tickers'])
        print(f"   {sector_info['name']}: {len(sector_results)} tickers", end='\r')
    
    print(f"\n   ✓ Scanned {len(all_results)} tickers across {len(AI_FUEL_CHAIN)} sectors")
    
    return all_results

def display_heatmap(results, sector_stats, detailed=False):
    """Display the AI fuel chain heatmap"""
    et_now = get_eastern_time()
    
    print("\n" + "=" * 85)
    print(f"🐺 AI FUEL CHAIN HEATMAP — {et_now.strftime('%I:%M %p ET')} — $5.2 TRILLION ECOSYSTEM")
    print("=" * 85)
    
    # Sort sectors by strength
    sorted_sectors = sorted(sector_stats.items(), key=lambda x: x[1]['strength'], reverse=True)
    
    print("\n📊 SECTOR STRENGTH RANKING (Strongest → Weakest)\n")
    print(f"{'Rank':<5} | {'SECTOR':<25} | {'1-DAY':>8} | {'5-DAY':>8} | {'20-DAY':>8} | {'VOL':>6} | {'HEAT':<12}")
    print("-" * 85)
    
    for i, (sector_key, stats) in enumerate(sorted_sectors, 1):
        # Heat indicator
        if stats['strength'] > 15:
            heat = "🔥🔥🔥 FIRE"
        elif stats['strength'] > 8:
            heat = "🔥🔥 HOT"
        elif stats['strength'] > 3:
            heat = "🔥 WARM"
        elif stats['strength'] > 0:
            heat = "➖ FLAT"
        else:
            heat = "❄️ COLD"
        
        print(f"{i:<5} | {stats['name']:<25} | {stats['change_1d']:>+7.1f}% | {stats['change_5d']:>+7.1f}% | {stats['change_20d']:>+7.1f}% | {stats['vol_ratio']:>5.1f}x | {heat}")
    
    # Top movers across all sectors
    print("\n" + "=" * 85)
    print("🎯 TOP 15 STRONGEST PLAYS ACROSS ALL SECTORS")
    print("=" * 85)
    
    # Sort by 5-day momentum
    sorted_all = sorted(results, key=lambda x: x['change_5d'], reverse=True)[:15]
    
    print(f"\n{'TICKER':<8} | {'SECTOR':<18} | {'PRICE':>9} | {'1-DAY':>8} | {'5-DAY':>8} | {'FROM HIGH':>10} | {'⭐':>3}")
    print("-" * 85)
    
    for r in sorted_all:
        star = "⭐" if r['priority'] else ""
        sector_short = r['sector_name'][:18]
        print(f"{r['ticker']:<8} | {sector_short:<18} | ${r['price']:>8.2f} | {r['change_1d']:>+7.1f}% | {r['change_5d']:>+7.1f}% | {r['pct_from_high']:>+9.1f}% | {star:>3}")
    
    # Priority watchlist status
    print("\n" + "=" * 85)
    print("⭐ YOUR PRIORITY WATCHLIST")
    print("=" * 85)
    
    priority_results = [r for r in results if r['priority']]
    priority_sorted = sorted(priority_results, key=lambda x: x['change_5d'], reverse=True)
    
    print(f"\n{'TICKER':<8} | {'SECTOR':<18} | {'PRICE':>9} | {'1-DAY':>8} | {'5-DAY':>8} | {'STATUS':<15}")
    print("-" * 85)
    
    for r in priority_sorted:
        if r['change_5d'] > 10:
            status = "🔥 RUNNING"
        elif r['change_5d'] > 5:
            status = "📈 STRONG"
        elif r['change_5d'] > 0:
            status = "✓ POSITIVE"
        elif r['change_5d'] > -5:
            status = "⚠️ WEAK"
        else:
            status = "🔴 BLEEDING"
        
        sector_short = r['sector_name'][:18]
        print(f"{r['ticker']:<8} | {sector_short:<18} | ${r['price']:>8.2f} | {r['change_1d']:>+7.1f}% | {r['change_5d']:>+7.1f}% | {status}")
    
    # Detailed view if requested
    if detailed:
        print("\n" + "=" * 85)
        print("📋 DETAILED SECTOR BREAKDOWN")
        print("=" * 85)
        
        for sector_key, sector_info in AI_FUEL_CHAIN.items():
            sector_results = sorted([r for r in results if r['sector'] == sector_key], 
                                   key=lambda x: x['change_5d'], reverse=True)
            
            if sector_results:
                print(f"\n{sector_info['name']}")
                print(f"   {sector_info['description']}")
                print(f"   Catalyst: {sector_info['catalyst']}")
                print("-" * 60)
                
                for r in sector_results:
                    star = "⭐" if r['priority'] else "  "
                    print(f"   {star} {r['ticker']:<6} ${r['price']:>8.2f} | 1d: {r['change_1d']:>+6.1f}% | 5d: {r['change_5d']:>+6.1f}%")
    
    # Summary
    print("\n" + "=" * 85)
    print("🐺 WOLF'S READ")
    print("=" * 85)
    
    # Find hottest and coldest
    hottest = sorted_sectors[0]
    coldest = sorted_sectors[-1]
    
    print(f"""
    🔥 HOTTEST SECTOR: {hottest[1]['name']}
       5-Day: {hottest[1]['change_5d']:+.1f}% | {hottest[1]['description']}
    
    ❄️ COLDEST SECTOR: {coldest[1]['name']}
       5-Day: {coldest[1]['change_5d']:+.1f}%
    
    💰 MONEY FLOW: {'RISK ON' if hottest[1]['strength'] > 5 else 'CAUTIOUS' if hottest[1]['strength'] > 0 else 'RISK OFF'}
    """)

def run_live_scanner(detailed=False, refresh_interval=120):
    """Run scanner in live mode"""
    print("\n🐺 AI FUEL CHAIN HEATMAP — LIVE MODE")
    print(f"   Tracking $5.2 trillion ecosystem")
    print(f"   Refreshing every {refresh_interval} seconds")
    print("   Press Ctrl+C to stop\n")
    
    try:
        while True:
            print("\033[2J\033[H", end="")
            
            results = scan_full_ecosystem(detailed=detailed)
            sector_stats = calculate_sector_strength(results)
            display_heatmap(results, sector_stats, detailed=detailed)
            
            print(f"\n   Next refresh in {refresh_interval} seconds... (Ctrl+C to stop)")
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n\n🐺 Scanner stopped. Good hunting!")

def main():
    parser = argparse.ArgumentParser(description='AI Fuel Chain Heatmap Scanner')
    parser.add_argument('--live', action='store_true', help='Run in live mode')
    parser.add_argument('--detailed', action='store_true', help='Show detailed sector breakdown')
    parser.add_argument('--refresh', type=int, default=120, help='Refresh interval (default: 120s)')
    
    args = parser.parse_args()
    
    if args.live:
        run_live_scanner(detailed=args.detailed, refresh_interval=args.refresh)
    else:
        results = scan_full_ecosystem(detailed=args.detailed)
        sector_stats = calculate_sector_strength(results)
        display_heatmap(results, sector_stats, detailed=args.detailed)

if __name__ == "__main__":
    main()
