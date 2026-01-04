#!/usr/bin/env python3
"""
🐺 WOLF STALKER - Detect Smart Money Accumulation

THE EDGE:
- Volume moves AFTER someone decides to buy
- Price moves AFTER volume
- That someone KNOWS MORE THAN US

THE SIGNAL:
- VOLUME > 2x AVERAGE
- PRICE MOVE < 5%
- NO NEWS (quiet accumulation)
= SOMEONE IS BUYING BEFORE WE KNOW WHY

Our job isn't to BE them. Our job is to DETECT them.
That's how you catch LEU before it runs.
"""

import yfinance as yf
import pandas as pd
import argparse
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# UNIVERSE - Expanded watchlist
# ============================================================================

SECTORS = {
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ', 'LAES'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'BKSY', 'ASTS', 'SPIR', 'SIDU', 'SATL', 'MNTS', 'PL'],
    'NUCLEAR': ['LEU', 'CCJ', 'UUUU', 'UEC', 'SMR', 'OKLO', 'NNE', 'DNN', 'NXE', 'LTBR'],
    'AI_INFRA': ['SMCI', 'VRT', 'PWR', 'SOUN', 'AI', 'PATH', 'UPST', 'BBAI'],
    'SEMICONDUCTORS': ['MU', 'AMD', 'ARM', 'MRVL', 'ALAB', 'CRDO', 'WOLF', 'ACLS', 'ASML'],
    'DEFENSE_AI': ['PLTR', 'KTOS', 'RCAT', 'AVAV', 'NNOX', 'LMT', 'RTX', 'NOC'],
    'BIOTECH': ['CRSP', 'EDIT', 'NTLA', 'BEAM', 'RXRX'],
    'EV_CLEAN': ['RIVN', 'LCID', 'PLUG', 'FCEL', 'BE', 'CHPT', 'QS'],
    'FINTECH': ['SOFI', 'AFRM', 'NU', 'UPST', 'LC', 'HOOD'],
}

# Add more tickers for broader scanning
EXTRA_WATCHLIST = [
    # Recent runners we want to track
    'AISP', 'FN', 'GEVO', 'STEM', 'ENVX', 'LAZR', 'LIDR',
    # Meme/squeeze history
    'GME', 'AMC', 'KOSS', 'BB',
    # High short interest names
    'CVNA', 'FFIE', 'MULN', 'GOEV',
]

def get_all_tickers():
    """Get all tickers"""
    all_tickers = set()
    for tickers in SECTORS.values():
        all_tickers.update(tickers)
    all_tickers.update(EXTRA_WATCHLIST)
    return list(all_tickers)

def get_sector(ticker):
    """Get sector for a ticker"""
    for sector, tickers in SECTORS.items():
        if ticker in tickers:
            return sector
    return 'OTHER'

# ============================================================================
# ACCUMULATION DETECTOR
# ============================================================================

def detect_accumulation(ticker):
    """
    Detect unusual volume with small price move = accumulation
    
    THE SIGNAL:
    - Volume > 2x average (someone buying big)
    - Price < 5% move (not a breakout yet, quiet accumulation)
    - This means: BIG BUYING, SMALL PRICE IMPACT = SMART MONEY
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1mo')
        
        if len(hist) < 10:
            return None
            
        # Today's data
        today = hist.iloc[-1]
        today_vol = today['Volume']
        today_open = today['Open']
        today_close = today['Close']
        today_change = (today_close / today_open - 1) * 100
        
        # Average volume (20 day)
        avg_vol = hist['Volume'].iloc[:-1].mean()
        vol_ratio = today_vol / avg_vol if avg_vol > 0 else 0
        
        # 5-day average volume for comparison
        vol_5d = hist['Volume'].iloc[-6:-1].mean()
        vol_vs_5d = today_vol / vol_5d if vol_5d > 0 else 0
        
        # Price context
        high_20d = hist['High'].max()
        low_20d = hist['Low'].min()
        pct_of_range = (today_close - low_20d) / (high_20d - low_20d) * 100 if (high_20d - low_20d) > 0 else 50
        
        # Week change
        week_ago = hist['Close'].iloc[-6] if len(hist) >= 6 else hist['Close'].iloc[0]
        week_change = (today_close / week_ago - 1) * 100
        
        # Get short interest
        try:
            info = stock.info
            short_pct = info.get('shortPercentOfFloat', 0) or 0
            short_pct = short_pct * 100 if short_pct < 1 else short_pct
            float_shares = info.get('floatShares', 0) or 0
        except:
            short_pct = 0
            float_shares = 0
            
        # ====================================================================
        # THE ACCUMULATION SCORE
        # High volume + Small price move = Smart money accumulating
        # ====================================================================
        
        accum_score = 0
        signals = []
        
        # VOLUME SPIKE (most important)
        if vol_ratio >= 3:
            accum_score += 40
            signals.append(f'🔥 {vol_ratio:.1f}x avg volume!')
        elif vol_ratio >= 2:
            accum_score += 30
            signals.append(f'⚡ {vol_ratio:.1f}x avg volume')
        elif vol_ratio >= 1.5:
            accum_score += 15
            signals.append(f'📈 {vol_ratio:.1f}x avg volume')
            
        # SMALL PRICE MOVE (quiet accumulation)
        if abs(today_change) <= 2:
            accum_score += 25
            signals.append(f'🤫 Only {today_change:+.1f}% on big volume')
        elif abs(today_change) <= 5:
            accum_score += 15
            signals.append(f'📊 {today_change:+.1f}% move')
        elif today_change > 5:
            accum_score += 5  # Still interesting but already moving
            signals.append(f'🚀 {today_change:+.1f}% breakout')
            
        # NEAR LOWS (accumulation zone)
        if pct_of_range <= 30:
            accum_score += 20
            signals.append('💰 Near 20d lows (accumulation zone)')
        elif pct_of_range <= 50:
            accum_score += 10
            signals.append('📍 Mid-range')
            
        # SHORT INTEREST (squeeze potential)
        if short_pct >= 20:
            accum_score += 15
            signals.append(f'🎯 {short_pct:.0f}% short (squeeze fuel)')
        elif short_pct >= 10:
            accum_score += 10
            signals.append(f'📌 {short_pct:.0f}% short')
            
        return {
            'ticker': ticker,
            'sector': get_sector(ticker),
            'price': today_close,
            'change_today': today_change,
            'vol_ratio': vol_ratio,
            'vol_vs_5d': vol_vs_5d,
            'accum_score': accum_score,
            'pct_of_range': pct_of_range,
            'week_change': week_change,
            'short_pct': short_pct,
            'float_shares': float_shares,
            'signals': signals,
            'volume': today_vol,
            'avg_volume': avg_vol,
        }
        
    except Exception as e:
        return None

# ============================================================================
# MAIN SCANNER
# ============================================================================

def scan_accumulation(min_vol_ratio=1.5, max_price_change=10):
    """
    Scan for accumulation signals
    
    Args:
        min_vol_ratio: Minimum volume vs 20d average (default 1.5x)
        max_price_change: Max price change to still be "quiet" (default 10%)
    """
    
    print()
    print('='*70)
    print('🐺 WOLF STALKER - Detecting Smart Money Accumulation')
    print('='*70)
    print()
    print('THE SIGNAL:')
    print('  VOLUME > 2x AVERAGE (someone buying big)')
    print('  PRICE MOVE < 5% (quiet accumulation)')
    print('  = SMART MONEY IS ACCUMULATING')
    print()
    print('  "Volume moves AFTER someone decides to buy."')
    print('  "Price moves AFTER volume."')
    print('  "Our job is to DETECT them. FOLLOW them."')
    print()
    print('='*70)
    print()
    
    tickers = get_all_tickers()
    results = []
    
    for i, ticker in enumerate(tickers):
        print(f'\r  Scanning {i+1}/{len(tickers)}: {ticker}...', end='', flush=True)
        result = detect_accumulation(ticker)
        if result and result['vol_ratio'] >= min_vol_ratio:
            results.append(result)
    
    print('\r' + ' '*50)
    print()
    
    if not results:
        print(f'No accumulation signals found with volume >= {min_vol_ratio}x')
        return []
        
    # Sort by accumulation score, then volume ratio
    results.sort(key=lambda x: (x['accum_score'], x['vol_ratio']), reverse=True)
    
    # ========================================================================
    # CATEGORY 1: QUIET ACCUMULATION (high vol, small move)
    # ========================================================================
    quiet = [r for r in results if abs(r['change_today']) <= 5 and r['vol_ratio'] >= 2]
    
    if quiet:
        print('🎯 QUIET ACCUMULATION (Big Volume, Small Move = Smart Money)')
        print('='*70)
        print()
        print(f'{"TICKER":<8} {"VOL":<8} {"TODAY":<8} {"SIGNALS"}')
        print('-'*70)
        
        for r in quiet[:10]:
            vol_str = f'{r["vol_ratio"]:.1f}x'
            chg_str = f'{r["change_today"]:+.1f}%'
            print(f'🔥 {r["ticker"]:<6} {vol_str:<8} {chg_str:<8} {" | ".join(r["signals"][:2])}')
        print()
        
    # ========================================================================
    # CATEGORY 2: BREAKOUTS (high vol, price moving)
    # ========================================================================
    breakouts = [r for r in results if r['change_today'] > 5 and r['vol_ratio'] >= 2]
    
    if breakouts:
        print('🚀 BREAKOUTS (Volume Confirmed Moves)')
        print('='*70)
        print()
        print(f'{"TICKER":<8} {"VOL":<8} {"TODAY":<8} {"WEEK":<8} {"SHORT%"}')
        print('-'*70)
        
        for r in breakouts[:10]:
            vol_str = f'{r["vol_ratio"]:.1f}x'
            chg_str = f'{r["change_today"]:+.1f}%'
            week_str = f'{r["week_change"]:+.1f}%'
            si_str = f'{r["short_pct"]:.0f}%' if r['short_pct'] > 0 else '-'
            print(f'🚀 {r["ticker"]:<6} {vol_str:<8} {chg_str:<8} {week_str:<8} {si_str}')
        print()
        
    # ========================================================================
    # CATEGORY 3: UNUSUAL ACTIVITY (any significant volume)
    # ========================================================================
    unusual = [r for r in results if r not in quiet and r not in breakouts and r['vol_ratio'] >= 1.5]
    
    if unusual:
        print('📊 UNUSUAL ACTIVITY (Volume Above Normal)')
        print('='*70)
        print()
        print(f'{"TICKER":<8} {"VOL":<8} {"TODAY":<8} {"RANGE":<10} {"SHORT%"}')
        print('-'*70)
        
        for r in unusual[:10]:
            vol_str = f'{r["vol_ratio"]:.1f}x'
            chg_str = f'{r["change_today"]:+.1f}%'
            range_str = f'{r["pct_of_range"]:.0f}% hi/lo'
            si_str = f'{r["short_pct"]:.0f}%' if r['short_pct'] > 0 else '-'
            print(f'📈 {r["ticker"]:<6} {vol_str:<8} {chg_str:<8} {range_str:<10} {si_str}')
        print()
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print('='*70)
    print('HOW TO USE THIS:')
    print('='*70)
    print()
    print('  🎯 QUIET ACCUMULATION = BEST SIGNALS')
    print('     Big volume + Small move = Smart money buying quietly')
    print('     They know something. We don\'t know what. BUY ANYWAY.')
    print()
    print('  🚀 BREAKOUTS = CONFIRMATION')
    print('     Move already started, but volume confirms it\'s real')
    print('     Can still ride momentum')
    print()
    print('  📊 UNUSUAL = WATCH LIST')
    print('     Something happening, not sure what')
    print('     Add to watchlist, dig deeper')
    print()
    print('  NEXT STEP: Check for news. If NO NEWS = even better signal!')
    print()
    print('='*70)
    
    return results

def deep_dive(ticker):
    """Deep analysis of accumulation in a single stock"""
    
    result = detect_accumulation(ticker)
    if not result:
        print(f'Could not analyze {ticker}')
        return
        
    print()
    print('='*70)
    print(f'🔬 ACCUMULATION ANALYSIS: {ticker}')
    print('='*70)
    print()
    print(f'  PRICE: ${result["price"]:.2f}')
    print(f'  TODAY: {result["change_today"]:+.1f}%')
    print(f'  WEEK:  {result["week_change"]:+.1f}%')
    print()
    print(f'  VOLUME ANALYSIS:')
    print(f'  ├─ Today Volume: {result["volume"]:,.0f}')
    print(f'  ├─ Avg Volume:   {result["avg_volume"]:,.0f}')
    print(f'  └─ Ratio:        {result["vol_ratio"]:.1f}x average')
    print()
    print(f'  POSITION IN RANGE: {result["pct_of_range"]:.0f}% (0=low, 100=high)')
    print()
    
    if result['short_pct'] > 0:
        print(f'  SHORT INTEREST: {result["short_pct"]:.1f}%')
    
    print()
    print('  SIGNALS:')
    for signal in result['signals']:
        print(f'    {signal}')
    print()
    
    # Assessment
    print('  ASSESSMENT:')
    if result['vol_ratio'] >= 2 and abs(result['change_today']) <= 5:
        print('  🎯 QUIET ACCUMULATION DETECTED')
        print('  Someone is buying heavily without moving price.')
        print('  This is the signal. They know something.')
        print('  Consider: Small position, see what develops.')
    elif result['vol_ratio'] >= 2 and result['change_today'] > 5:
        print('  🚀 BREAKOUT IN PROGRESS')
        print('  Volume confirms the move is real.')
        print('  Can ride momentum but higher risk entry.')
    elif result['vol_ratio'] >= 1.5:
        print('  📊 UNUSUAL ACTIVITY')
        print('  Something happening. Watch closely.')
        print('  Look for news. If no news = more interesting.')
    else:
        print('  ⏸️  NORMAL ACTIVITY')
        print('  No unusual accumulation detected.')
    
    print()
    print('='*70)

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='🐺 Wolf Stalker - Detect Accumulation')
    parser.add_argument('command', nargs='?', default='scan',
                        help='scan | TICKER for deep dive')
    parser.add_argument('--min-vol', type=float, default=1.5,
                        help='Minimum volume ratio (default: 1.5x)')
    
    args = parser.parse_args()
    
    if args.command == 'scan':
        scan_accumulation(min_vol_ratio=args.min_vol)
    else:
        deep_dive(args.command.upper())

if __name__ == '__main__':
    main()
