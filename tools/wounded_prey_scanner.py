#!/usr/bin/env python3
"""
🐺 WOUNDED PREY SCANNER - TAX LOSS BOUNCE HUNTER
=================================================
Find stocks down 30%+ with January bounce potential

TAX LOSS SELLING: Dec 15-31
WASH SALE ENDS: Jan 24-31
OPTIMAL ENTRY: Jan 2-10 (NOW!)

We hunt the wounded, not the dead.

AWOOOO 🐺 LLHR
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# COLORS
# =============================================================================
class Colors:
    BRIGHT_GREEN = '\033[92m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# =============================================================================
# AI FUEL CHAIN
# =============================================================================

AI_FUEL_CHAIN = {
    'NUCLEAR': ['UUUU', 'SMR', 'LEU', 'OKLO', 'CCJ', 'DNN', 'UEC', 'NXE', 'NNE'],
    'UTILITIES': ['NEE', 'VST', 'CEG', 'WMB'],
    'COOLING': ['VRT', 'MOD', 'NVT'],
    'PHOTONICS': ['LITE', 'AAOI', 'COHR', 'GFS'],
    'NETWORKING': ['ANET', 'CRDO', 'FN', 'CIEN'],
    'STORAGE': ['MU', 'WDC', 'STX'],
    'CHIPS': ['AMD', 'MRVL', 'AVGO', 'INTC', 'AMKR'],
    'DC_BUILDERS': ['SMCI', 'EME', 'CLS', 'FIX'],
    'DC_REITS': ['EQIX', 'DLR'],
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'ASTS', 'SIDU', 'BKSY', 'PL'],
    'AI_SOFTWARE': ['PLTR', 'AI', 'SOUN', 'PATH', 'UPST']
}

PRIORITY_TICKERS = ['UUUU', 'SIDU', 'LUNR', 'MU', 'LITE', 'VRT', 'SMR', 'LEU', 'RDW', 'OKLO']

def get_sector_for_ticker(ticker):
    for sector, tickers in AI_FUEL_CHAIN.items():
        if ticker in tickers:
            return sector
    return "OTHER"

# =============================================================================
# WOUNDED PREY DETECTION
# =============================================================================

def analyze_wounded_prey(ticker):
    """Analyze if ticker is wounded prey with bounce potential"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1y', prepost=False)
        
        if len(hist) < 50:
            return None
        
        current = hist['Close'].iloc[-1]
        high_52w = hist['High'].max()
        volume_avg = hist['Volume'].mean()
        
        # Calculate decline from high
        pct_from_high = ((current - high_52w) / high_52w) * 100
        
        # Not wounded enough
        if pct_from_high > -30:
            return None
        
        # Too cheap (penny stock risk)
        if current < 2:
            return None
        
        # Too expensive for our range
        if current > 50:
            return None
        
        # Volume check (needs liquidity)
        if volume_avg < 100000:
            return None
        
        # Recent momentum (is it starting to recover?)
        recent_5d = ((current - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100
        recent_10d = ((current - hist['Close'].iloc[-10]) / hist['Close'].iloc[-10]) * 100
        recent_20d = ((current - hist['Close'].iloc[-20]) / hist['Close'].iloc[-20]) * 100
        
        # Volume trend (is money coming back?)
        recent_vol = hist['Volume'].iloc[-5:].mean()
        vol_ratio = recent_vol / volume_avg
        
        # Fundamentals check
        info = stock.info
        revenue = info.get('totalRevenue', 0)
        market_cap = info.get('marketCap', 0)
        
        # Filter out total garbage
        if revenue == 0 or market_cap == 0:
            return None
        
        # Bounce potential score
        score = 0
        
        # Deeper wound = more potential
        if pct_from_high < -50:
            score += 30
        elif pct_from_high < -40:
            score += 20
        else:
            score += 10
        
        # Recent recovery started
        if recent_5d > 5:
            score += 20
        elif recent_5d > 0:
            score += 10
        
        # Volume increasing
        if vol_ratio > 1.5:
            score += 20
        elif vol_ratio > 1.2:
            score += 10
        
        # In our thesis
        if ticker in sum(AI_FUEL_CHAIN.values(), []):
            score += 20
        
        # Priority ticker
        if ticker in PRIORITY_TICKERS:
            score += 10
        
        return {
            'ticker': ticker,
            'sector': get_sector_for_ticker(ticker),
            'price': current,
            'high_52w': high_52w,
            'pct_from_high': pct_from_high,
            'change_5d': recent_5d,
            'change_10d': recent_10d,
            'change_20d': recent_20d,
            'vol_ratio': vol_ratio,
            'avg_volume': volume_avg,
            'revenue': revenue,
            'market_cap': market_cap,
            'bounce_score': score
        }
        
    except Exception as e:
        return None

def scan_wounded_prey():
    """Scan AI Fuel Chain for wounded prey"""
    
    all_tickers = []
    for tickers in AI_FUEL_CHAIN.values():
        all_tickers.extend(tickers)
    
    print("\n" + "="*100)
    print(f"{Colors.CYAN}{Colors.BOLD}🎯 WOUNDED PREY SCANNER - TAX LOSS BOUNCE HUNTER 🎯{Colors.END}")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print(f"   Scanning {len(all_tickers)} tickers for January bounce potential")
    print(f"   Criteria: Down 30%+, Price $2-50, Volume >100K, Has revenue")
    print("="*100)
    
    print(f"\n   {Colors.YELLOW}📅 TAX LOSS BOUNCE TIMING:{Colors.END}")
    print(f"      • Tax loss selling: Dec 15-31 (DONE)")
    print(f"      • Wash sale rule: 30 days (ends Jan 24-31)")
    print(f"      • OPTIMAL ENTRY: Jan 2-10 (RIGHT NOW!)")
    print(f"      • Expected bounce: 15-30% by month end\n")
    
    results = []
    
    print(f"   Scanning", end="", flush=True)
    for i, ticker in enumerate(all_tickers):
        if i % 10 == 0:
            print(".", end="", flush=True)
        
        prey = analyze_wounded_prey(ticker)
        if prey:
            results.append(prey)
    
    print(" ✓ Done!")
    
    # Sort by bounce score
    results.sort(key=lambda x: x['bounce_score'], reverse=True)
    
    return results

def display_wounded_prey_report(results):
    """Display wounded prey report"""
    
    if not results:
        print(f"\n   {Colors.GREEN}No wounded prey matching criteria found{Colors.END}")
        return
    
    # Tier 1: High conviction bounces
    tier_1 = [r for r in results if r['bounce_score'] >= 60]
    tier_2 = [r for r in results if 40 <= r['bounce_score'] < 60]
    tier_3 = [r for r in results if r['bounce_score'] < 40]
    
    if tier_1:
        print(f"\n{Colors.RED}{Colors.BOLD}{'='*100}")
        print(f"🔥 TIER 1 - HIGH CONVICTION BOUNCE PLAYS")
        print(f"{'='*100}{Colors.END}")
        
        print(f"\n   {'TICKER':<8} | {'SECTOR':<12} | {'PRICE':>8} | {'FROM HIGH':>10} | {'5D CHG':>8} | {'VOL':>6} | {'SCORE':>7}")
        print(f"   {'─'*8}─┼─{'─'*12}─┼─{'─'*8}─┼─{'─'*10}─┼─{'─'*8}─┼─{'─'*6}─┼─{'─'*7}")
        
        for r in tier_1:
            priority = "⭐" if r['ticker'] in PRIORITY_TICKERS else ""
            recovery = "🟢" if r['change_5d'] > 5 else "📈" if r['change_5d'] > 0 else ""
            
            print(f"   {r['ticker']:<6}{priority:<2} | {r['sector']:<12} | ${r['price']:>7.2f} | {r['pct_from_high']:>+9.1f}% | {r['change_5d']:>+7.1f}% | {r['vol_ratio']:>5.1f}x | {r['bounce_score']:>7} {recovery}")
    
    if tier_2:
        print(f"\n{Colors.YELLOW}{'='*100}")
        print(f"📈 TIER 2 - GOOD BOUNCE POTENTIAL")
        print(f"{'='*100}{Colors.END}")
        
        for r in tier_2[:10]:
            priority = "⭐" if r['ticker'] in PRIORITY_TICKERS else ""
            print(f"   {r['ticker']:<6}{priority} [{r['sector']:<12}] | ${r['price']:>7.2f} | {r['pct_from_high']:>+9.1f}% from high | Score: {r['bounce_score']}")
    
    if tier_3:
        print(f"\n{Colors.GREEN}{'='*100}")
        print(f"➖ TIER 3 - WATCH LIST")
        print(f"{'='*100}{Colors.END}")
        
        for r in tier_3[:10]:
            priority = "⭐" if r['ticker'] in PRIORITY_TICKERS else ""
            print(f"   {r['ticker']:<6}{priority} [{r['sector']:<12}] | ${r['price']:>7.2f} | {r['pct_from_high']:>+9.1f}% from high")
    
    # Sector breakdown
    print(f"\n{Colors.CYAN}{'='*100}")
    print(f"📊 WOUNDED PREY BY SECTOR")
    print(f"{'='*100}{Colors.END}")
    
    sector_stats = {}
    for r in results:
        sector = r['sector']
        if sector not in sector_stats:
            sector_stats[sector] = {'count': 0, 'avg_decline': 0, 'high_conviction': 0}
        
        sector_stats[sector]['count'] += 1
        sector_stats[sector]['avg_decline'] += r['pct_from_high']
        if r['bounce_score'] >= 60:
            sector_stats[sector]['high_conviction'] += 1
    
    for sector in sector_stats:
        sector_stats[sector]['avg_decline'] /= sector_stats[sector]['count']
    
    sorted_sectors = sorted(sector_stats.items(), key=lambda x: x[1]['high_conviction'], reverse=True)
    
    print(f"\n   {'SECTOR':<15} | {'WOUNDED':>8} | {'AVG DECLINE':>12} | {'HIGH CONV':>10}")
    print(f"   {'─'*15}─┼─{'─'*8}─┼─{'─'*12}─┼─{'─'*10}")
    
    for sector, stats in sorted_sectors:
        heat = "🔥" if stats['high_conviction'] > 0 else ""
        print(f"   {sector:<15} | {stats['count']:>8} | {stats['avg_decline']:>+11.1f}% | {stats['high_conviction']:>10} {heat}")
    
    # Priority tickers
    priority_prey = [r for r in results if r['ticker'] in PRIORITY_TICKERS]
    
    if priority_prey:
        print(f"\n{Colors.YELLOW}{'='*100}")
        print(f"⭐ PRIORITY TICKERS - WOUNDED STATUS")
        print(f"{'='*100}{Colors.END}")
        
        for r in priority_prey:
            recovery = "🟢 RECOVERING" if r['change_5d'] > 5 else "📈 TURNING" if r['change_5d'] > 0 else "⚠️ FALLING"
            
            print(f"\n   {Colors.BOLD}{r['ticker']}{Colors.END} [{r['sector']}] — Score: {r['bounce_score']}")
            print(f"      Price: ${r['price']:.2f} | {r['pct_from_high']:+.1f}% from high (${r['high_52w']:.2f})")
            print(f"      5d: {r['change_5d']:+.1f}% | 20d: {r['change_20d']:+.1f}% | Vol: {r['vol_ratio']:.1f}x")
            print(f"      Status: {recovery}")
    
    # Wolf's read
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*100}")
    print(f"🐺 WOLF'S WOUNDED PREY READ")
    print(f"{'='*100}{Colors.END}")
    
    if tier_1:
        print(f"\n   🎯 TOP BOUNCE PLAYS:")
        for r in tier_1[:3]:
            print(f"      → {r['ticker']}: {r['pct_from_high']:+.1f}% from high, bounce score {r['bounce_score']}")
    
    print(f"\n   📅 TIMING STRATEGY:")
    print(f"      • NOW (Jan 2-10): ENTRY WINDOW")
    print(f"      • Tax loss sellers can't rebuy until Jan 24-31 (wash sale)")
    print(f"      • Expected bounce: 15-30% by month end")
    print(f"      • Exit BEFORE earnings or by Jan 31")
    
    print(f"\n   🎯 WHAT TO LOOK FOR:")
    print(f"      • Down 40%+ = biggest bounce potential")
    print(f"      • Recent 5d recovery (>5%) = bounce starting")
    print(f"      • Volume increasing (>1.5x) = money returning")
    print(f"      • In our thesis sectors = quality names, not garbage")
    
    print(f"\n   ⚠️ RISK MANAGEMENT:")
    print(f"      • These are WOUNDED, not dead")
    print(f"      • Set tight stops (-8% to -10%)")
    print(f"      • Take profits at 15-20% bounce")
    print(f"      • Don't hold through earnings")

# =============================================================================
# MAIN
# =============================================================================

def main():
    results = scan_wounded_prey()
    display_wounded_prey_report(results)
    
    print(f"\n{'='*100}")
    print(f"{Colors.CYAN}{Colors.BOLD}🐺 AWOOOO! HUNT THE WOUNDED! LLHR! 🐺{Colors.END}")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    main()
