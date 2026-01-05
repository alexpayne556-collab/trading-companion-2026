#!/usr/bin/env python3
"""
wolf_battlefield.py - THE FULL BATTLEFIELD SCANNER

Scans EVERYTHING. Ranks EVERYTHING. Finds setups BEFORE they run.
Not dependent on any single catalyst. Not tunnel vision on CES.

THE REAL QUESTION: What's about to move and WHY?

Looks for:
1. WOUNDED PREY - Recently crushed, now stabilizing (catch the bounce)
2. COILED SPRINGS - Tight range, low volume, compression before explosion
3. ACCUMULATION - Volume without price move (someone's loading)
4. SECTOR LAGGARDS - Peers ran, this one hasn't (catch-up play)
5. PRESSURE BUILDS - Shorts + Options + Volume converging
6. MOMENTUM STARTS - Breaking out of base, early stage

Usage:
    python wolf_battlefield.py scan              # Full battlefield scan
    python wolf_battlefield.py wounded           # Wounded prey only
    python wolf_battlefield.py coiled            # Coiled springs only  
    python wolf_battlefield.py laggards          # Sector laggards
    python wolf_battlefield.py tomorrow          # Best setups for tomorrow

AWOOOO 🐺
"""

import argparse
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════════
# THE EXPANDED UNIVERSE - 200+ tickers across 12 sectors
# ═══════════════════════════════════════════════════════════════════════════

SECTORS = {
    "QUANTUM": ["QBTS", "QUBT", "IONQ", "RGTI", "ARQQ"],
    
    "SPACE": ["RKLB", "LUNR", "RDW", "ASTS", "SPIR", "BKSY", "PL", "GSAT", "IRDM"],
    
    "DEFENSE": ["RCAT", "PLTR", "KTOS", "AVAV", "LMT", "NOC", "RTX", "GD", "BA"],
    
    "NUCLEAR": ["SMR", "NNE", "LEU", "OKLO", "CCJ", "UEC", "UUUU", "DNN", "URG", "NXE", "BWXT"],
    
    "AI_INFRA": ["NVDA", "AMD", "SMCI", "ARM", "AVGO", "MRVL", "MU", "TSM", "ASML"],
    
    "SEMICONDUCTORS": ["AMAT", "LRCX", "KLAC", "QCOM", "TXN", "ADI", "ON", "MCHP", "WOLF", "MPWR"],
    
    "ROBOTICS": ["RR", "ISRG", "PATH", "TER", "CGNX", "ROK", "NOVT"],
    
    "CRYPTO_MINERS": ["MARA", "RIOT", "CLSK", "CIFR", "HUT", "BTBT", "BITF", "CORZ", "IREN"],
    
    "CLEAN_ENERGY": ["FSLR", "ENPH", "SEDG", "RUN", "PLUG", "BE", "STEM", "ARRY"],
    
    "BIOTECH": ["MRNA", "BNTX", "NVAX", "CRSP", "EDIT", "NTLA", "BEAM", "RXRX"],
    
    "SOFTWARE": ["SNOW", "DDOG", "CRWD", "ZS", "NET", "MDB", "CFLT", "ESTC"],
    
    "EV": ["TSLA", "RIVN", "LCID", "NIO", "XPEV", "LI", "CHPT", "BLNK", "QS"],
    
    "HIGH_SHORT": ["CVNA", "UPST", "AFRM", "SOFI", "HOOD", "COIN", "SNAP", "PINS"],
}

ALL_TICKERS = list(set([t for tickers in SECTORS.values() for t in tickers]))

# ═══════════════════════════════════════════════════════════════════════════
# PATTERN DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def analyze_ticker(ticker: str) -> dict:
    """Deep analysis of a single ticker - find ALL patterns"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")
        
        if hist.empty or len(hist) < 40:
            return None
        
        # Basic metrics
        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        daily_chg = ((current - prev) / prev) * 100
        
        # Volume analysis
        vol_today = hist['Volume'].iloc[-1]
        vol_avg_20 = hist['Volume'].tail(20).mean()
        vol_avg_5 = hist['Volume'].tail(5).mean()
        vol_ratio = vol_today / vol_avg_20 if vol_avg_20 > 0 else 0
        
        # Price ranges
        high_20 = hist['High'].tail(20).max()
        low_20 = hist['Low'].tail(20).min()
        high_52 = hist['High'].max()
        low_52 = hist['Low'].min()
        
        range_20 = (high_20 - low_20) / low_20 * 100 if low_20 > 0 else 0
        range_position = (current - low_20) / (high_20 - low_20) if (high_20 - low_20) > 0 else 0.5
        
        # From 52w high/low
        from_52_high = ((current - high_52) / high_52) * 100
        from_52_low = ((current - low_52) / low_52) * 100
        
        # Momentum
        week_chg = ((current - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100 if len(hist) >= 5 else 0
        month_chg = ((current - hist['Close'].iloc[-20]) / hist['Close'].iloc[-20]) * 100 if len(hist) >= 20 else 0
        
        # Volatility (ATR proxy)
        daily_ranges = (hist['High'] - hist['Low']).tail(14)
        avg_range = daily_ranges.mean()
        volatility = (avg_range / current) * 100 if current > 0 else 0
        
        # Short interest
        try:
            info = stock.info
            short_pct = info.get('shortPercentOfFloat', 0) * 100 if info.get('shortPercentOfFloat') else 0
            float_shares = info.get('floatShares', 0)
            market_cap = info.get('marketCap', 0)
        except:
            short_pct = 0
            float_shares = 0
            market_cap = 0
        
        # ═══════════════════════════════════════════════════════════════════
        # PATTERN SCORING
        # ═══════════════════════════════════════════════════════════════════
        
        patterns = []
        setup_score = 0
        
        # 1. WOUNDED PREY (max 25 pts)
        # Down big from highs, now stabilizing
        wounded_score = 0
        if from_52_high <= -40 and week_chg > -5:
            wounded_score = 25
            patterns.append("🩸 WOUNDED PREY: Down 40%+ from high, stabilizing")
        elif from_52_high <= -30 and week_chg > -3:
            wounded_score = 18
            patterns.append("🩸 Wounded: Down 30%+ from high, finding floor")
        elif from_52_high <= -20 and daily_chg > 0:
            wounded_score = 10
            patterns.append("📉 Beaten down, showing life")
        setup_score += wounded_score
        
        # 2. COILED SPRING (max 25 pts)
        # Tight range + low volume = compression
        coiled_score = 0
        vol_dry = vol_avg_5 < vol_avg_20 * 0.7  # Volume drying up
        tight_range = range_20 < 15  # Less than 15% range in 20 days
        near_lows = range_position < 0.3
        
        if tight_range and vol_dry and near_lows:
            coiled_score = 25
            patterns.append("🌀 COILED SPRING: Tight range + dry volume + near lows")
        elif tight_range and vol_dry:
            coiled_score = 15
            patterns.append("🌀 Compression: Tight range, volume drying")
        elif tight_range and near_lows:
            coiled_score = 10
            patterns.append("📊 Consolidating near support")
        setup_score += coiled_score
        
        # 3. ACCUMULATION (max 20 pts)
        # Volume without big price move = someone loading
        accum_score = 0
        recent_vol_spike = vol_ratio >= 1.5 and abs(daily_chg) < 3
        week_vol_high = vol_avg_5 > vol_avg_20 * 1.3
        
        if week_vol_high and abs(week_chg) < 5:
            accum_score = 20
            patterns.append("🔍 ACCUMULATION: High volume, little price change")
        elif recent_vol_spike:
            accum_score = 12
            patterns.append("🔍 Quiet accumulation today")
        setup_score += accum_score
        
        # 4. BREAKOUT SETUP (max 20 pts)
        # Near highs with momentum
        breakout_score = 0
        if range_position >= 0.95 and week_chg > 5:
            breakout_score = 20
            patterns.append("🚀 BREAKOUT: At highs with momentum")
        elif range_position >= 0.85 and daily_chg > 2:
            breakout_score = 12
            patterns.append("🚀 Breaking out of range")
        elif range_position >= 0.80:
            breakout_score = 5
            patterns.append("📈 Near top of range")
        setup_score += breakout_score
        
        # 5. SHORT SQUEEZE POTENTIAL (max 15 pts)
        squeeze_score = 0
        if short_pct >= 25 and daily_chg > 3:
            squeeze_score = 15
            patterns.append(f"💥 SQUEEZE SETUP: {short_pct:.0f}% short + momentum")
        elif short_pct >= 20:
            squeeze_score = 10
            patterns.append(f"⚠️ High short interest: {short_pct:.0f}%")
        elif short_pct >= 15:
            squeeze_score = 5
            patterns.append(f"📊 Elevated short: {short_pct:.0f}%")
        setup_score += squeeze_score
        
        # 6. VOLUME SIGNAL (bonus pts)
        if vol_ratio >= 3:
            setup_score += 10
            patterns.append(f"🔥 Volume explosion: {vol_ratio:.1f}x avg")
        elif vol_ratio >= 2:
            setup_score += 5
            patterns.append(f"📊 Elevated volume: {vol_ratio:.1f}x avg")
        
        # Determine primary pattern
        primary_pattern = "NONE"
        if wounded_score >= 18:
            primary_pattern = "WOUNDED"
        elif coiled_score >= 15:
            primary_pattern = "COILED"
        elif accum_score >= 12:
            primary_pattern = "ACCUM"
        elif breakout_score >= 12:
            primary_pattern = "BREAKOUT"
        elif squeeze_score >= 10:
            primary_pattern = "SQUEEZE"
        
        return {
            'ticker': ticker,
            'price': current,
            'daily_chg': daily_chg,
            'week_chg': week_chg,
            'month_chg': month_chg,
            'vol_ratio': vol_ratio,
            'short_pct': short_pct,
            'from_high': from_52_high,
            'range_pos': range_position,
            'setup_score': setup_score,
            'primary_pattern': primary_pattern,
            'patterns': patterns,
            'volatility': volatility,
            'market_cap': market_cap,
        }
        
    except Exception as e:
        return None


def get_sector_performance() -> dict:
    """Calculate sector performance for laggard detection"""
    sector_perf = {}
    
    for sector, tickers in SECTORS.items():
        week_changes = []
        for ticker in tickers[:5]:  # Sample first 5
            try:
                hist = yf.Ticker(ticker).history(period="1mo")
                if len(hist) >= 5:
                    chg = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100
                    week_changes.append(chg)
            except:
                pass
        if week_changes:
            sector_perf[sector] = np.mean(week_changes)
    
    return sector_perf


def find_laggards(results: list, sector_perf: dict) -> list:
    """Find stocks lagging their sector (catch-up plays)"""
    laggards = []
    
    for r in results:
        # Find which sector this ticker belongs to
        ticker_sector = None
        for sector, tickers in SECTORS.items():
            if r['ticker'] in tickers:
                ticker_sector = sector
                break
        
        if ticker_sector and ticker_sector in sector_perf:
            sector_avg = sector_perf[ticker_sector]
            # Laggard = sector up but this stock isn't
            if sector_avg > 5 and r['week_chg'] < sector_avg - 10:
                gap = sector_avg - r['week_chg']
                laggards.append({
                    **r,
                    'sector': ticker_sector,
                    'sector_perf': sector_avg,
                    'laggard_gap': gap
                })
    
    laggards.sort(key=lambda x: x['laggard_gap'], reverse=True)
    return laggards


# ═══════════════════════════════════════════════════════════════════════════
# SCANNERS
# ═══════════════════════════════════════════════════════════════════════════

def scan_all() -> list:
    """Scan entire universe"""
    print(f"\n🔍 Scanning {len(ALL_TICKERS)} tickers across {len(SECTORS)} sectors...")
    
    results = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(analyze_ticker, t): t for t in ALL_TICKERS}
        
        completed = 0
        for future in as_completed(futures):
            completed += 1
            if completed % 25 == 0:
                print(f"   Progress: {completed}/{len(ALL_TICKERS)}")
            
            result = future.result()
            if result:
                results.append(result)
    
    results.sort(key=lambda x: x['setup_score'], reverse=True)
    return results


def print_battlefield(results: list, title: str = "BATTLEFIELD SCAN", limit: int = 20):
    """Print scan results"""
    print(f"""
{'='*80}
🐺 {title}
{'='*80}
{'TICKER':<7} {'PRICE':>9} {'DAY':>7} {'WEEK':>7} {'VOL':>6} {'SHORT':>6} {'SCORE':>6} {'PATTERN':<12}
{'-'*80}""")
    
    for r in results[:limit]:
        vol_str = f"{r['vol_ratio']:.1f}x" if r['vol_ratio'] > 0 else "-"
        short_str = f"{r['short_pct']:.0f}%" if r['short_pct'] > 0 else "-"
        
        # Score indicator
        if r['setup_score'] >= 40:
            ind = "🔥"
        elif r['setup_score'] >= 25:
            ind = "⚡"
        else:
            ind = "✅"
        
        print(f"{r['ticker']:<7} ${r['price']:>8.2f} {r['daily_chg']:>+6.1f}% {r['week_chg']:>+6.1f}% {vol_str:>6} {short_str:>6} {r['setup_score']:>4} {ind} {r['primary_pattern']:<10}")
    
    print(f"{'='*80}\n")


def print_detailed(results: list, limit: int = 10):
    """Print detailed patterns for top results"""
    print("🎯 TOP SETUPS - DETAILED ANALYSIS:\n")
    
    for i, r in enumerate(results[:limit], 1):
        sector = "?"
        for s, tickers in SECTORS.items():
            if r['ticker'] in tickers:
                sector = s
                break
        
        print(f"{i}. {r['ticker']} @ ${r['price']:.2f} | {sector} | Score: {r['setup_score']}")
        print(f"   Day: {r['daily_chg']:+.1f}% | Week: {r['week_chg']:+.1f}% | Month: {r['month_chg']:+.1f}%")
        print(f"   From 52w High: {r['from_high']:.1f}% | Short: {r['short_pct']:.1f}%")
        for p in r['patterns']:
            print(f"   {p}")
        print()


def full_scan():
    """Full battlefield reconnaissance"""
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🐺 WOLF BATTLEFIELD - FULL RECONNAISSANCE                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  NO TUNNEL VISION. NO SINGLE CATALYST. THE WHOLE MARKET.                     ║
║                                                                              ║
║  Sectors: {len(SECTORS):<68} ║
║  Tickers: {len(ALL_TICKERS):<68} ║
║                                                                              ║
║  Looking for: WOUNDED PREY | COILED SPRINGS | ACCUMULATION | BREAKOUTS       ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    results = scan_all()
    
    # Print top setups
    print_battlefield(results, "TOP SETUPS BY SCORE", 25)
    print_detailed(results, 10)
    
    # Sector breakdown
    print("📊 BEST SETUP BY SECTOR:\n")
    for sector in SECTORS.keys():
        sector_results = [r for r in results if r['ticker'] in SECTORS[sector]]
        if sector_results:
            top = sector_results[0]
            pattern = top['primary_pattern'] if top['primary_pattern'] != "NONE" else "-"
            print(f"  {sector:<15} {top['ticker']:<6} Score:{top['setup_score']:>3} {top['daily_chg']:>+6.1f}% {pattern}")
    
    print()
    
    # Pattern breakdown
    print("📋 PATTERN SUMMARY:\n")
    patterns_found = {"WOUNDED": [], "COILED": [], "ACCUM": [], "BREAKOUT": [], "SQUEEZE": []}
    for r in results:
        if r['primary_pattern'] in patterns_found:
            patterns_found[r['primary_pattern']].append(r['ticker'])
    
    for pattern, tickers in patterns_found.items():
        if tickers:
            print(f"  {pattern:<10}: {', '.join(tickers[:8])}")
    
    print()


def scan_wounded():
    """Find wounded prey - beaten down stocks showing life"""
    print("\n🩸 WOUNDED PREY SCAN - Beaten down, now stabilizing\n")
    results = scan_all()
    wounded = [r for r in results if r['primary_pattern'] == "WOUNDED" or r['from_high'] <= -30]
    wounded.sort(key=lambda x: x['from_high'])
    print_battlefield(wounded, "WOUNDED PREY", 15)
    print_detailed(wounded[:5], 5)


def scan_coiled():
    """Find coiled springs - tight compression before explosion"""
    print("\n🌀 COILED SPRINGS SCAN - Compression before explosion\n")
    results = scan_all()
    coiled = [r for r in results if r['primary_pattern'] == "COILED"]
    print_battlefield(coiled, "COILED SPRINGS", 15)
    print_detailed(coiled[:5], 5)


def scan_laggards():
    """Find sector laggards - catch-up plays"""
    print("\n🐢 SECTOR LAGGARDS - Catch-up plays\n")
    
    print("Calculating sector performance...")
    sector_perf = get_sector_performance()
    
    print("\n📊 SECTOR PERFORMANCE (1 Week):\n")
    for sector, perf in sorted(sector_perf.items(), key=lambda x: x[1], reverse=True):
        print(f"  {sector:<15} {perf:>+6.1f}%")
    print()
    
    results = scan_all()
    laggards = find_laggards(results, sector_perf)
    
    if laggards:
        print(f"\n🎯 LAGGARDS (Sector running, stock isn't):\n")
        print(f"{'TICKER':<7} {'PRICE':>9} {'STOCK':>8} {'SECTOR':>8} {'GAP':>8} {'SECTOR':<15}")
        print("-" * 70)
        for l in laggards[:15]:
            print(f"{l['ticker']:<7} ${l['price']:>8.2f} {l['week_chg']:>+7.1f}% {l['sector_perf']:>+7.1f}% {l['laggard_gap']:>+7.1f}% {l['sector']:<15}")
    else:
        print("No significant laggards found.")


def scan_tomorrow():
    """Best setups for tomorrow - actionable now"""
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🐺 TOMORROW'S HUNT - ACTIONABLE SETUPS                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  What's set up to move? Not what moved today. What moves TOMORROW.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    results = scan_all()
    
    # Tomorrow's setups = high score + not already extended
    tomorrow = []
    for r in results:
        # Skip already extended (up >15% this week)
        if r['week_chg'] > 15:
            continue
        # Skip dead money (no patterns)
        if r['setup_score'] < 15:
            continue
        # Prioritize setups over momentum
        tomorrow.append(r)
    
    tomorrow.sort(key=lambda x: x['setup_score'], reverse=True)
    
    print_battlefield(tomorrow, "TOMORROW'S TOP SETUPS", 20)
    print_detailed(tomorrow, 10)
    
    # Capital allocation suggestion
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║  💰 SUGGESTED ALLOCATION ($740 across 5 sectors)                             ║
╠══════════════════════════════════════════════════════════════════════════════╣""")
    
    # Pick top from different sectors
    used_sectors = set()
    picks = []
    for r in tomorrow:
        sector = None
        for s, tickers in SECTORS.items():
            if r['ticker'] in tickers:
                sector = s
                break
        if sector and sector not in used_sectors:
            used_sectors.add(sector)
            picks.append((r, sector))
            if len(picks) >= 5:
                break
    
    for i, (r, sector) in enumerate(picks, 1):
        print(f"║  {i}. {r['ticker']:<6} | ${148:>5} | {sector:<15} | {r['primary_pattern']:<10} | Score:{r['setup_score']:>3} ║")
    
    print("""╠══════════════════════════════════════════════════════════════════════════════╣
║  5 positions × $148 each = $740 total                                        ║
║  If ONE fails, 4 others survive. DIVERSIFICATION.                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="🐺 Wolf Battlefield - Full Market Reconnaissance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python wolf_battlefield.py scan          # Full battlefield scan
  python wolf_battlefield.py wounded       # Wounded prey (beaten down)
  python wolf_battlefield.py coiled        # Coiled springs (compression)
  python wolf_battlefield.py laggards      # Sector laggards (catch-up)
  python wolf_battlefield.py tomorrow      # Best setups for tomorrow

NO TUNNEL VISION. THE WHOLE MARKET.
AWOOOO 🐺
        """
    )
    
    parser.add_argument(
        "command",
        choices=["scan", "wounded", "coiled", "laggards", "tomorrow"],
        nargs="?",
        default="scan",
        help="Scan type"
    )
    
    args = parser.parse_args()
    
    if args.command == "scan":
        full_scan()
    elif args.command == "wounded":
        scan_wounded()
    elif args.command == "coiled":
        scan_coiled()
    elif args.command == "laggards":
        scan_laggards()
    elif args.command == "tomorrow":
        scan_tomorrow()


if __name__ == "__main__":
    main()
