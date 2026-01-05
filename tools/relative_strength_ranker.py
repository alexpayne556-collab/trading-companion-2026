#!/usr/bin/env python3
"""
🐺 RELATIVE STRENGTH RANKER
============================
Ranks ALL tickers by relative strength across timeframes
Identifies the STRONGEST plays in the entire universe

Usage:
    python relative_strength_ranker.py                    # Full ranking
    python relative_strength_ranker.py --top 20           # Top 20 only
    python relative_strength_ranker.py --sector NUCLEAR   # Specific sector
    python relative_strength_ranker.py --csv output.csv   # Export to CSV
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
import argparse
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# COMPLETE TICKER UNIVERSE — ALL SECTORS
# ============================================================

UNIVERSE = {
    'NUCLEAR': ['UUUU', 'SMR', 'LEU', 'OKLO', 'CCJ', 'DNN', 'UEC', 'NXE', 'NNE'],
    'UTILITIES': ['NEE', 'VST', 'CEG', 'WMB'],
    'COOLING': ['VRT', 'MOD', 'NVT', 'JCI'],
    'NETWORKING': ['ANET', 'CRDO', 'FN', 'CIEN'],
    'PHOTONICS': ['LITE', 'AAOI', 'COHR', 'GFS'],
    'CHIPS': ['AMD', 'MRVL', 'AVGO', 'INTC', 'AMKR'],
    'STORAGE': ['MU', 'WDC', 'STX'],
    'DC_REITS': ['EQIX', 'DLR'],
    'DC_BUILDERS': ['SMCI', 'EME', 'CLS', 'FIX'],
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'ASTS', 'SIDU', 'BKSY', 'PL'],
    'AI_SOFTWARE': ['PLTR', 'AI', 'SOUN', 'PATH', 'UPST']
}

# Priority watchlist for highlighting
WATCHLIST = ['UUUU', 'SIDU', 'LUNR', 'MU', 'LITE', 'VRT', 'SMR', 'LEU', 'RDW', 'OKLO']

# ============================================================
# STRENGTH CALCULATION
# ============================================================

def calculate_strength(ticker, sector):
    """Calculate comprehensive strength score"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='3mo', prepost=True)
        
        if len(hist) < 20:
            return None
        
        current = hist['Close'].iloc[-1]
        
        # Timeframe changes
        changes = {}
        for period, days in [('1d', 1), ('2d', 2), ('5d', 5), ('10d', 10), ('20d', 20), ('60d', 60)]:
            if len(hist) >= days:
                prev = hist['Close'].iloc[-days]
                changes[period] = ((current - prev) / prev) * 100
            else:
                changes[period] = 0
        
        # 52-week high proximity
        high_52w = hist['High'].max()
        pct_from_high = ((current - high_52w) / high_52w) * 100
        
        # Volume analysis
        avg_volume = hist['Volume'].mean()
        recent_volume = hist['Volume'].iloc[-5:].mean()
        vol_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        
        # STRENGTH SCORE
        # Weights: Recent performance matters MORE
        strength = (
            changes['5d'] * 0.35 +      # 5-day momentum (main)
            changes['2d'] * 0.25 +      # 2-day momentum
            changes['1d'] * 0.15 +      # Today's action
            changes['20d'] * 0.15 +     # 20-day trend
            (vol_ratio - 1) * 5 +       # Volume boost
            (100 + pct_from_high) * 0.1  # Near highs bonus
        )
        
        return {
            'ticker': ticker,
            'sector': sector,
            'price': current,
            '1d': changes['1d'],
            '2d': changes['2d'],
            '5d': changes['5d'],
            '10d': changes['10d'],
            '20d': changes['20d'],
            '60d': changes['60d'],
            'pct_from_high': pct_from_high,
            'vol_ratio': vol_ratio,
            'strength': strength,
            'watchlist': ticker in WATCHLIST
        }
        
    except Exception as e:
        return None

def scan_universe(sectors_filter=None):
    """Scan entire universe for strength"""
    print("\n⚡ SCANNING UNIVERSE FOR RELATIVE STRENGTH...")
    
    results = []
    total = sum(len(t) for s, t in UNIVERSE.items() if not sectors_filter or s in sectors_filter)
    count = 0
    
    for sector, tickers in UNIVERSE.items():
        if sectors_filter and sector not in sectors_filter:
            continue
            
        for ticker in tickers:
            count += 1
            print(f"   Scanning: {ticker} ({count}/{total})       ", end='\r')
            
            data = calculate_strength(ticker, sector)
            if data:
                results.append(data)
    
    print(f"\n   ✓ Scanned {len(results)} tickers")
    
    return results

def get_eastern_time():
    eastern = pytz.timezone('US/Eastern')
    return datetime.now(eastern)

def display_rankings(results, top_n=None, show_watchlist=True):
    """Display strength rankings"""
    et_now = get_eastern_time()
    
    # Sort by strength
    df = pd.DataFrame(results)
    df_sorted = df.sort_values('strength', ascending=False)
    
    if top_n:
        df_sorted = df_sorted.head(top_n)
    
    print("\n" + "=" * 120)
    print(f"🐺 RELATIVE STRENGTH RANKINGS — {et_now.strftime('%I:%M %p ET')}")
    print("=" * 120)
    
    print(f"\n{'Rank':<5} | {'TICKER':<8} | {'SECTOR':<12} | {'PRICE':>10} | {'1-DAY':>8} | {'5-DAY':>8} | {'20-DAY':>8} | {'%52WH':>8} | {'VOL':>6} | {'STRENGTH':>10} |")
    print("-" * 120)
    
    for i, (_, row) in enumerate(df_sorted.iterrows(), 1):
        # Watchlist highlight
        ticker_fmt = row['ticker']
        if row['watchlist']:
            ticker_fmt = f"★{row['ticker']}"
        
        # Strength tier
        if row['strength'] > 20:
            tier = "🔥 MONSTER"
        elif row['strength'] > 10:
            tier = "💪 STRONG"
        elif row['strength'] > 5:
            tier = "📈 GOOD"
        elif row['strength'] > 0:
            tier = "➖ OK"
        else:
            tier = "❄️ WEAK"
        
        print(f"{i:<5} | {ticker_fmt:<8} | {row['sector']:<12} | ${row['price']:>8.2f} | {row['1d']:>+7.1f}% | {row['5d']:>+7.1f}% | {row['20d']:>+7.1f}% | {row['pct_from_high']:>+7.1f}% | {row['vol_ratio']:>5.1f}x | {row['strength']:>+9.1f} | {tier}")
    
    # Sector summary
    print("\n" + "=" * 120)
    print("📊 SECTOR SUMMARY")
    print("=" * 120)
    
    df_full = pd.DataFrame(results)
    sector_stats = df_full.groupby('sector').agg({
        'strength': 'mean',
        '5d': 'mean',
        '1d': 'mean'
    }).sort_values('strength', ascending=False)
    
    print(f"\n{'SECTOR':<15} | {'AVG STRENGTH':>12} | {'AVG 5-DAY':>12} | {'AVG 1-DAY':>12}")
    print("-" * 60)
    
    for sector, row in sector_stats.iterrows():
        print(f"{sector:<15} | {row['strength']:>+11.1f} | {row['5d']:>+11.1f}% | {row['1d']:>+11.1f}%")
    
    # Watchlist tickers sorted
    if show_watchlist:
        watchlist_df = df_full[df_full['watchlist']].sort_values('strength', ascending=False)
        
        print("\n" + "=" * 120)
        print("⭐ YOUR WATCHLIST — RANKED BY STRENGTH")
        print("=" * 120)
        
        for i, (_, row) in enumerate(watchlist_df.iterrows(), 1):
            print(f"   {i}. {row['ticker']:<6} ({row['sector']}) — Strength: {row['strength']:+.1f} | 5d: {row['5d']:+.1f}% | Near High: {row['pct_from_high']:+.1f}%")
    
    # Wolf's read
    print("\n" + "=" * 120)
    print("🐺 WOLF'S HUNTING LIST")
    print("=" * 120)
    
    # Top 5 strongest
    top5 = df_sorted.head(5)
    print("\n🎯 TOP 5 STRONGEST PLAYS:")
    for i, (_, row) in enumerate(top5.iterrows(), 1):
        print(f"   {i}. {row['ticker']} ({row['sector']}) — {row['strength']:+.1f} strength, {row['5d']:+.1f}% (5d)")
    
    # Near highs with strength
    near_highs = df_full[(df_full['pct_from_high'] > -10) & (df_full['strength'] > 5)].sort_values('strength', ascending=False)
    if not near_highs.empty:
        print("\n📍 STRONG & NEAR 52-WEEK HIGHS (within 10%):")
        for i, (_, row) in enumerate(near_highs.head(5).iterrows(), 1):
            print(f"   {i}. {row['ticker']} — {row['pct_from_high']:+.1f}% from high, strength {row['strength']:+.1f}")
    
    # Volume surges
    vol_surge = df_full[df_full['vol_ratio'] > 1.5].sort_values('vol_ratio', ascending=False)
    if not vol_surge.empty:
        print("\n📊 VOLUME SURGES (>1.5x avg):")
        for i, (_, row) in enumerate(vol_surge.head(5).iterrows(), 1):
            print(f"   {i}. {row['ticker']} — {row['vol_ratio']:.1f}x volume, {row['5d']:+.1f}% (5d)")
    
    return df_sorted

def export_csv(df, filename):
    """Export to CSV"""
    df.to_csv(filename, index=False)
    print(f"\n✓ Exported to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Relative Strength Ranker')
    parser.add_argument('--top', type=int, help='Show top N only')
    parser.add_argument('--sector', type=str, help='Filter by sector')
    parser.add_argument('--csv', type=str, help='Export to CSV')
    parser.add_argument('--no-watchlist', action='store_true', help='Hide watchlist section')
    
    args = parser.parse_args()
    
    sectors = None
    if args.sector:
        sectors = [args.sector.upper()]
    
    results = scan_universe(sectors_filter=sectors)
    
    df = display_rankings(
        results, 
        top_n=args.top,
        show_watchlist=not args.no_watchlist
    )
    
    if args.csv:
        export_csv(df, args.csv)

if __name__ == "__main__":
    main()
