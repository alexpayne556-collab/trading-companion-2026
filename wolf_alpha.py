#!/usr/bin/env python3
"""
🐺 WOLF ALPHA - The Unified Scanner

Catches runners BEFORE they explode by combining:
1. Volume spike (someone accumulating)
2. Tiny float (moves fast when it goes)
3. Near lows (spring coiled)
4. Short interest (squeeze fuel)

WHAT THIS CATCHES:
- DVLT had 3.0x volume day before +55% run
- LVRO had 2.8x volume + 5.8M float before +144% run
- BNAI had 2.8M float before +63% run

THE EDGE: Tiny float + Volume spike = SOMEONE KNOWS SOMETHING
"""

import yfinance as yf
import pandas as pd
import argparse
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# EXPANDED UNIVERSE - Cast a wider net
# ============================================================================

# Core sectors we track
SECTORS = {
    'AI': ['DVLT', 'BNAI', 'AI', 'SOUN', 'BBAI', 'PATH', 'UPST', 'PRCT'],
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ', 'LAES'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'BKSY', 'ASTS', 'SPIR', 'SIDU', 'SATL', 'MNTS', 'PL'],
    'NUCLEAR': ['LEU', 'CCJ', 'UUUU', 'UEC', 'SMR', 'OKLO', 'NNE', 'DNN', 'NXE', 'LTBR'],
    'SEMICONDUCTORS': ['MU', 'AMD', 'ARM', 'MRVL', 'ALAB', 'CRDO', 'WOLF', 'ACLS', 'ASML'],
    'DEFENSE': ['PLTR', 'KTOS', 'RCAT', 'AVAV', 'NNOX', 'LMT', 'RTX'],
    'BIOTECH': ['CRSP', 'EDIT', 'NTLA', 'BEAM', 'RXRX', 'SAVA'],
    'EV_CLEAN': ['RIVN', 'LCID', 'PLUG', 'FCEL', 'BE', 'CHPT', 'QS', 'STEM', 'ENVX'],
    'FINTECH': ['SOFI', 'AFRM', 'NU', 'UPST', 'LC', 'HOOD'],
    'AGRICULTURE': ['LVRO', 'AGRI', 'FMC', 'CTVA'],
}

# High-risk/high-reward small caps
SMALL_CAP_MOVERS = [
    'DVLT', 'LVRO', 'BNAI', 'AISP', 'FN', 'GEVO', 'LAZR', 'LIDR',
    'GME', 'AMC', 'KOSS', 'BB', 'EXPR',
    'CVNA', 'GOEV', 'VIEW', 'ARRY', 'RUN',
]

def get_all_tickers():
    """Get all tickers from all sources"""
    all_tickers = set()
    for tickers in SECTORS.values():
        all_tickers.update(tickers)
    all_tickers.update(SMALL_CAP_MOVERS)
    return list(all_tickers)

def get_sector(ticker):
    """Get sector for a ticker"""
    for sector, tickers in SECTORS.items():
        if ticker in tickers:
            return sector
    return 'SMALLCAP'

# ============================================================================
# THE ALPHA SCANNER
# ============================================================================

def scan_alpha(ticker):
    """
    The unified alpha scan - find setups BEFORE they run
    
    Scoring:
    - Volume spike (40 pts) - someone accumulating
    - Tiny float (30 pts) - moves fast
    - Near lows (20 pts) - spring coiled
    - Short interest (10 pts) - squeeze fuel
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1mo')
        info = stock.info
        
        if len(hist) < 10:
            return None
            
        # Current data
        today = hist.iloc[-1]
        price = today['Close']
        vol_today = today['Volume']
        
        # Average volume (20d)
        avg_vol = hist['Volume'].iloc[:-1].mean()
        vol_ratio = vol_today / avg_vol if avg_vol > 0 else 0
        
        # Today's price change
        if len(hist) >= 2:
            yesterday_close = hist['Close'].iloc[-2]
            today_change = (price / yesterday_close - 1) * 100
        else:
            today_change = 0
            
        # Week change
        if len(hist) >= 6:
            week_ago = hist['Close'].iloc[-6]
            week_change = (price / week_ago - 1) * 100
        else:
            week_change = 0
            
        # Float
        float_shares = info.get('floatShares', 0) or 0
        
        # Short interest
        short_pct = info.get('shortPercentOfFloat', 0) or 0
        short_pct = short_pct * 100 if short_pct < 1 else short_pct
        
        # Near lows?
        low_20d = hist['Low'].min()
        pct_off_lows = (price / low_20d - 1) * 100
        
        # Market cap
        mcap = info.get('marketCap', 0) or 0
        
        # ====================================================================
        # ALPHA SCORE
        # ====================================================================
        alpha_score = 0
        signals = []
        
        # VOLUME SPIKE (most important - 40 pts)
        if vol_ratio >= 3:
            alpha_score += 40
            signals.append(f'🔥 VOLUME {vol_ratio:.1f}x (BIG accumulation)')
        elif vol_ratio >= 2:
            alpha_score += 30
            signals.append(f'⚡ Volume {vol_ratio:.1f}x (accumulation)')
        elif vol_ratio >= 1.5:
            alpha_score += 15
            signals.append(f'📈 Volume {vol_ratio:.1f}x')
            
        # TINY FLOAT (30 pts)
        if float_shares > 0:
            if float_shares < 10e6:
                alpha_score += 30
                signals.append(f'💎 TINY float ({float_shares/1e6:.1f}M) - moves FAST')
            elif float_shares < 30e6:
                alpha_score += 20
                signals.append(f'📌 Small float ({float_shares/1e6:.1f}M)')
            elif float_shares < 50e6:
                alpha_score += 10
                signals.append(f'📊 Moderate float ({float_shares/1e6:.1f}M)')
                
        # NEAR LOWS (20 pts) - coiled spring
        if pct_off_lows <= 10:
            alpha_score += 20
            signals.append(f'💰 At 20d lows (+{pct_off_lows:.0f}%)')
        elif pct_off_lows <= 20:
            alpha_score += 15
            signals.append(f'📍 Near lows (+{pct_off_lows:.0f}%)')
        elif pct_off_lows <= 30:
            alpha_score += 5
            
        # SHORT INTEREST (10 pts)
        if short_pct >= 20:
            alpha_score += 10
            signals.append(f'🎯 {short_pct:.0f}% SHORT (squeeze fuel)')
        elif short_pct >= 10:
            alpha_score += 5
            signals.append(f'📌 {short_pct:.0f}% short')
            
        # BONUS: Small price move on big volume = QUIET ACCUMULATION
        if vol_ratio >= 2 and abs(today_change) <= 5:
            alpha_score += 15
            signals.append('🤫 BIG vol, small move = QUIET ACCUMULATION')
            
        return {
            'ticker': ticker,
            'sector': get_sector(ticker),
            'price': price,
            'today_change': today_change,
            'week_change': week_change,
            'vol_ratio': vol_ratio,
            'float_shares': float_shares,
            'float_str': f'{float_shares/1e6:.1f}M' if float_shares else '?',
            'short_pct': short_pct,
            'pct_off_lows': pct_off_lows,
            'alpha_score': alpha_score,
            'signals': signals,
            'mcap': mcap,
        }
        
    except Exception as e:
        return None

# ============================================================================
# MAIN SCANNER
# ============================================================================

def run_alpha_scan(min_score=30, min_vol=1.0):
    """
    Run the unified alpha scan
    """
    print()
    print('='*70)
    print('🐺 WOLF ALPHA - Catching Runners BEFORE They Explode')
    print('='*70)
    print()
    print('WHAT THIS CATCHES:')
    print('  • DVLT: 3.0x volume day before +55% run')
    print('  • LVRO: 2.8x volume + 5.8M float before +144% run')
    print('  • BNAI: 2.8M tiny float before +63% run')
    print()
    print('THE FORMULA:')
    print('  Volume Spike + Tiny Float + Near Lows + Shorts = 🚀')
    print()
    print('='*70)
    print()
    
    tickers = get_all_tickers()
    results = []
    
    for i, ticker in enumerate(tickers):
        print(f'\r  Scanning {i+1}/{len(tickers)}: {ticker}...', end='', flush=True)
        result = scan_alpha(ticker)
        if result and result['alpha_score'] >= min_score and result['vol_ratio'] >= min_vol:
            results.append(result)
    
    print('\r' + ' '*60)
    print()
    
    if not results:
        print(f'No signals found with score >= {min_score}')
        return []
        
    # Sort by alpha score
    results.sort(key=lambda x: x['alpha_score'], reverse=True)
    
    # ========================================================================
    # HOT SETUPS (high score + volume)
    # ========================================================================
    hot = [r for r in results if r['alpha_score'] >= 50 and r['vol_ratio'] >= 1.5]
    
    if hot:
        print('🔥 HOT SETUPS (High Alpha Score + Volume)')
        print('='*70)
        print()
        print(f'{"TICKER":<8} {"SCORE":<6} {"VOL":<6} {"FLOAT":<10} {"TODAY":<8} {"SIGNALS"}')
        print('-'*70)
        
        for r in hot[:10]:
            vol_str = f'{r["vol_ratio"]:.1f}x'
            chg_str = f'{r["today_change"]:+.1f}%'
            sig = r['signals'][0] if r['signals'] else ''
            print(f'🔥 {r["ticker"]:<6} {r["alpha_score"]:<6.0f} {vol_str:<6} {r["float_str"]:<10} {chg_str:<8} {sig}')
        print()
        
    # ========================================================================
    # COILED SPRINGS (near lows + setup forming)
    # ========================================================================
    coiled = [r for r in results if r['pct_off_lows'] <= 20 and r['alpha_score'] >= 30]
    coiled = [r for r in coiled if r not in hot]  # Don't duplicate
    
    if coiled:
        print('💎 COILED SPRINGS (Near Lows, Setup Forming)')
        print('='*70)
        print()
        print(f'{"TICKER":<8} {"SCORE":<6} {"OFF LOW":<8} {"FLOAT":<10} {"SI%":<6} {"WEEK"}')
        print('-'*70)
        
        for r in coiled[:10]:
            low_str = f'+{r["pct_off_lows"]:.0f}%'
            si_str = f'{r["short_pct"]:.0f}%' if r['short_pct'] > 0 else '-'
            week_str = f'{r["week_change"]:+.1f}%'
            print(f'💎 {r["ticker"]:<6} {r["alpha_score"]:<6.0f} {low_str:<8} {r["float_str"]:<10} {si_str:<6} {week_str}')
        print()
        
    # ========================================================================
    # TINY FLOATS (explosive potential)
    # ========================================================================
    tiny = [r for r in results if r['float_shares'] > 0 and r['float_shares'] < 20e6]
    tiny = [r for r in tiny if r not in hot and r not in coiled]
    
    if tiny:
        print('🎯 TINY FLOATS (Explosive Potential)')
        print('='*70)
        print()
        print(f'{"TICKER":<8} {"FLOAT":<10} {"VOL":<6} {"TODAY":<8} {"SI%":<6}')
        print('-'*70)
        
        for r in tiny[:10]:
            vol_str = f'{r["vol_ratio"]:.1f}x'
            chg_str = f'{r["today_change"]:+.1f}%'
            si_str = f'{r["short_pct"]:.0f}%' if r['short_pct'] > 0 else '-'
            print(f'🎯 {r["ticker"]:<6} {r["float_str"]:<10} {vol_str:<6} {chg_str:<8} {si_str:<6}')
        print()
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print('='*70)
    print('THE WORKFLOW:')
    print('='*70)
    print()
    print('  1. 🔥 HOT SETUPS = Check NOW (volume + signals aligned)')
    print('  2. 💎 COILED SPRINGS = Watch for breakout')
    print('  3. 🎯 TINY FLOATS = Know these names (they move FAST)')
    print()
    print('  CROSS-REFERENCE with ATP:')
    print('  - Pre-market volume spikes')
    print('  - Options activity (unusual calls)')
    print('  - Breaking 52-week highs on volume')
    print()
    print('  If ATP shows volume + this scan shows setup = EXECUTE')
    print()
    print('='*70)
    
    return results

def analyze_ticker(ticker):
    """Deep dive on a single ticker"""
    
    result = scan_alpha(ticker.upper())
    if not result:
        print(f'Could not analyze {ticker}')
        return
        
    print()
    print('='*70)
    print(f'🔬 ALPHA ANALYSIS: {ticker.upper()}')
    print('='*70)
    print()
    print(f'  ALPHA SCORE: {result["alpha_score"]}/100')
    print()
    print(f'  PRICE:  ${result["price"]:.2f}')
    print(f'  TODAY:  {result["today_change"]:+.1f}%')
    print(f'  WEEK:   {result["week_change"]:+.1f}%')
    print()
    print(f'  VOLUME: {result["vol_ratio"]:.1f}x average')
    print(f'  FLOAT:  {result["float_str"]}')
    print(f'  SHORT:  {result["short_pct"]:.1f}%')
    print(f'  OFF 20D LOW: +{result["pct_off_lows"]:.0f}%')
    print()
    
    if result['signals']:
        print('  SIGNALS:')
        for sig in result['signals']:
            print(f'    {sig}')
        print()
    
    # Assessment
    if result['alpha_score'] >= 60:
        print('  ⚡ HIGH ALPHA - Multiple signals aligned')
        print('  This is the type of setup that precedes big moves.')
    elif result['alpha_score'] >= 40:
        print('  📊 MODERATE ALPHA - Some signals present')
        print('  Worth watching. Wait for volume confirmation.')
    else:
        print('  📍 LOW ALPHA - Setup not ready')
        print('  May need more time to develop.')
    
    print()
    print('='*70)

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='🐺 Wolf Alpha - Unified Scanner')
    parser.add_argument('command', nargs='?', default='scan',
                        help='scan | TICKER for analysis')
    parser.add_argument('--min-score', type=int, default=30,
                        help='Minimum alpha score (default: 30)')
    parser.add_argument('--min-vol', type=float, default=1.0,
                        help='Minimum volume ratio (default: 1.0)')
    
    args = parser.parse_args()
    
    if args.command == 'scan':
        run_alpha_scan(min_score=args.min_score, min_vol=args.min_vol)
    else:
        analyze_ticker(args.command)

if __name__ == '__main__':
    main()
