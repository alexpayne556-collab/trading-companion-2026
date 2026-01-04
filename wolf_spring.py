#!/usr/bin/env python3
"""
🐺 WOLF SPRING - Find Coiled Springs BEFORE They Run

THE PATTERN (from studying winners):
- LUNR was +7% off lows, -15% week before -> then +94%
- RKLB was +2% off lows, -13% week before -> then +92%
- OKLO was +10% off lows, -10% week before -> then +101%
- SIDU was +23% off lows, -8% week before -> then +462%

WHAT TO SCAN FOR:
1. Near 20-day lows (within 15%) - hasn't run yet
2. Last 5 days flat or down - coiling
3. Tight trading range - building energy
4. Hot sector - nuclear, space, quantum, AI
5. Short interest - fuel for squeeze

This finds stocks BEFORE the move, not DURING.
"""

import yfinance as yf
import pandas as pd
import argparse
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# UNIVERSE - Hot sectors where big runners come from
# ============================================================================

SECTORS = {
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ', 'LAES'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'BKSY', 'ASTS', 'SPIR', 'SIDU', 'SATL', 'MNTS', 'PL'],
    'NUCLEAR': ['LEU', 'CCJ', 'UUUU', 'UEC', 'SMR', 'OKLO', 'NNE', 'DNN', 'NXE', 'LTBR'],
    'AI_INFRA': ['SMCI', 'VRT', 'PWR', 'SOUN', 'AI', 'PATH', 'UPST', 'BBAI', 'BIGC'],
    'SEMICONDUCTORS': ['MU', 'AMD', 'ARM', 'MRVL', 'ALAB', 'CRDO', 'WOLF', 'ACLS'],
    'DEFENSE_AI': ['PLTR', 'KTOS', 'RCAT', 'AVAV', 'NNOX'],
    'BIOTECH': ['CRSP', 'EDIT', 'NTLA', 'BEAM', 'VERV', 'RXRX'],
    'EV_CLEAN': ['RIVN', 'LCID', 'PLUG', 'FCEL', 'BE', 'CHPT', 'QS'],
}

def get_all_tickers():
    """Get all tickers from all sectors"""
    all_tickers = set()
    for sector, tickers in SECTORS.items():
        all_tickers.update(tickers)
    return list(all_tickers)

def get_sector(ticker):
    """Get sector for a ticker"""
    for sector, tickers in SECTORS.items():
        if ticker in tickers:
            return sector
    return 'OTHER'

# ============================================================================
# SPRING DETECTOR - Find coiled stocks ready to explode
# ============================================================================

def analyze_spring(ticker):
    """
    Analyze if a stock is a coiled spring ready to run.
    
    Returns dict with:
    - spring_score: 0-100 (higher = more coiled)
    - near_lows: bool
    - week_change: % change last 5 days
    - range_tightness: how tight the range is
    - has_shorts: bool
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='3mo')
        
        if len(hist) < 25:
            return None
            
        # Current price
        current = hist['Close'].iloc[-1]
        
        # ====================================================================
        # METRIC 1: Near 20-day lows (within 15%)?
        # Winners were 2-23% off lows before running
        # ====================================================================
        low_20d = hist['Low'].iloc[-20:].min()
        pct_off_lows = (current / low_20d - 1) * 100
        
        # Best if 0-15% off lows (hasn't run yet)
        if pct_off_lows <= 15:
            near_lows_score = 30  # Full points
        elif pct_off_lows <= 25:
            near_lows_score = 20  # Partial
        elif pct_off_lows <= 35:
            near_lows_score = 10  # Getting extended
        else:
            near_lows_score = 0   # Already ran
            
        # ====================================================================
        # METRIC 2: Last 5 days flat or down (coiling)?
        # Winners were -3% to -15% in week before
        # ====================================================================
        if len(hist) >= 5:
            week_ago = hist['Close'].iloc[-6]
            week_change = (current / week_ago - 1) * 100
        else:
            week_change = 0
            
        # Best if flat to slightly down (coiling)
        if -15 <= week_change <= 5:
            coiling_score = 25  # Perfect coiling
        elif -20 <= week_change <= 10:
            coiling_score = 15  # Still ok
        else:
            coiling_score = 0   # Either dumping or already running
            
        # ====================================================================
        # METRIC 3: Tight trading range (building energy)?
        # RDW had 8.6% range, PLTR had 9.2%
        # ====================================================================
        recent = hist.iloc[-5:]  # Last 5 days
        high = recent['High'].max()
        low = recent['Low'].min()
        avg = recent['Close'].mean()
        range_pct = (high - low) / avg * 100
        
        if range_pct <= 10:
            range_score = 25  # Very tight
        elif range_pct <= 15:
            range_score = 20  # Tight
        elif range_pct <= 20:
            range_score = 10  # Moderate
        else:
            range_score = 0   # Wide/volatile
            
        # ====================================================================
        # METRIC 4: Volume dry up (calm before storm)?
        # Low volume during consolidation = building pressure
        # ====================================================================
        avg_vol_20d = hist['Volume'].iloc[-20:].mean()
        recent_vol = hist['Volume'].iloc[-5:].mean()
        vol_ratio = recent_vol / avg_vol_20d if avg_vol_20d > 0 else 1
        
        if vol_ratio <= 0.8:
            vol_score = 20  # Volume dried up - spring coiling
        elif vol_ratio <= 1.0:
            vol_score = 15  # Normal
        else:
            vol_score = 5   # Volume already picking up
            
        # ====================================================================
        # TOTAL SPRING SCORE
        # ====================================================================
        spring_score = near_lows_score + coiling_score + range_score + vol_score
        
        # Get short interest if available
        try:
            info = stock.info
            short_pct = info.get('shortPercentOfFloat', 0) or 0
            short_pct = short_pct * 100 if short_pct < 1 else short_pct
        except:
            short_pct = 0
            
        return {
            'ticker': ticker,
            'sector': get_sector(ticker),
            'price': current,
            'spring_score': spring_score,
            'pct_off_lows': pct_off_lows,
            'week_change': week_change,
            'range_pct': range_pct,
            'vol_ratio': vol_ratio,
            'short_pct': short_pct,
            'near_lows_score': near_lows_score,
            'coiling_score': coiling_score,
            'range_score': range_score,
            'vol_score': vol_score,
        }
        
    except Exception as e:
        return None

# ============================================================================
# MAIN SCANNER
# ============================================================================

def scan_for_springs(min_score=50):
    """Scan universe for coiled springs"""
    
    print()
    print('='*70)
    print('🐺 WOLF SPRING SCANNER - Finding Coiled Springs BEFORE They Run')
    print('='*70)
    print()
    print('The Pattern (from studying winners):')
    print('  • LUNR: +7% off lows, -15% week before  -> then +94%')
    print('  • RKLB: +2% off lows, -13% week before  -> then +92%')
    print('  • OKLO: +10% off lows, -10% week before -> then +101%')
    print()
    print('Scanning for: Near lows + Coiling + Tight range + Volume dry')
    print('='*70)
    print()
    
    tickers = get_all_tickers()
    springs = []
    
    for i, ticker in enumerate(tickers):
        print(f'\r  Scanning {i+1}/{len(tickers)}: {ticker}...', end='', flush=True)
        result = analyze_spring(ticker)
        if result and result['spring_score'] >= min_score:
            springs.append(result)
    
    print('\r' + ' '*50)
    print()
    
    if not springs:
        print('No coiled springs found with score >= {min_score}')
        return []
        
    # Sort by spring score
    springs.sort(key=lambda x: x['spring_score'], reverse=True)
    
    # Display results
    print('🎯 COILED SPRINGS (Ready to Run)')
    print('='*70)
    print()
    print(f'{"TICKER":<8} {"SECTOR":<12} {"SCORE":<6} {"OFF LOWS":<10} {"5D CHG":<8} {"RANGE":<8} {"SI%":<6}')
    print('-'*70)
    
    for s in springs[:15]:
        status = '🔥' if s['spring_score'] >= 70 else '⚡' if s['spring_score'] >= 60 else '💫'
        print(f"{status} {s['ticker']:<6} {s['sector']:<12} {s['spring_score']:<6.0f} "
              f"+{s['pct_off_lows']:<8.0f}% {s['week_change']:+6.1f}% "
              f"{s['range_pct']:<7.1f}% {s['short_pct']:<5.0f}%")
    
    print()
    print('='*70)
    print()
    print('READING THE SCORES:')
    print('  • 70+ = TIGHTLY COILED (best setups)')
    print('  • 60+ = BUILDING PRESSURE')
    print('  • 50+ = WORTH WATCHING')
    print()
    print('WHY THIS WORKS:')
    print('  • Near lows = hasnt run yet (youre early)')
    print('  • Week flat/down = coiling, building energy')
    print('  • Tight range = pressure building')
    print('  • Low volume = calm before storm')
    print()
    
    return springs

def deep_dive(ticker):
    """Deep analysis of a single spring"""
    
    result = analyze_spring(ticker)
    if not result:
        print(f'Could not analyze {ticker}')
        return
        
    print()
    print('='*70)
    print(f'🔬 SPRING ANALYSIS: {ticker}')
    print('='*70)
    print()
    print(f'  SPRING SCORE: {result["spring_score"]}/100')
    print()
    print(f'  BREAKDOWN:')
    print(f'  ├─ Near Lows:    {result["near_lows_score"]}/30  (+{result["pct_off_lows"]:.0f}% off 20d low)')
    print(f'  ├─ Coiling:      {result["coiling_score"]}/25  ({result["week_change"]:+.1f}% last 5 days)')
    print(f'  ├─ Tight Range:  {result["range_score"]}/25  ({result["range_pct"]:.1f}% 5-day range)')
    print(f'  └─ Volume Dry:   {result["vol_score"]}/20  ({result["vol_ratio"]:.2f}x avg volume)')
    print()
    
    if result['short_pct'] > 10:
        print(f'  ⚠️  SHORT INTEREST: {result["short_pct"]:.0f}% - SQUEEZE FUEL!')
    
    print()
    
    # What would need to happen
    if result['spring_score'] >= 70:
        print('  STATUS: TIGHTLY COILED 🔥')
        print('  This looks like LUNR/RKLB before their runs.')
        print('  Watch for: Volume spike + break of 5-day high')
    elif result['spring_score'] >= 60:
        print('  STATUS: BUILDING PRESSURE ⚡')
        print('  Getting coiled but not quite there.')
        print('  Watch for: Another few days of tight action')
    else:
        print('  STATUS: EARLY STAGE 💫')
        print('  May need more time to coil.')
    print()
    print('='*70)

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='🐺 Wolf Spring - Find Coiled Springs')
    parser.add_argument('command', nargs='?', default='scan', 
                        help='scan | TICKER for deep dive')
    parser.add_argument('--min-score', type=int, default=50,
                        help='Minimum spring score (default: 50)')
    
    args = parser.parse_args()
    
    if args.command == 'scan':
        scan_for_springs(args.min_score)
    else:
        # Assume it's a ticker
        deep_dive(args.command.upper())

if __name__ == '__main__':
    main()
