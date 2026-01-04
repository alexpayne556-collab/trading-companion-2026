#!/usr/bin/env python3
"""
🐺 WOLF WAVES - Catch Multiple Waves, Not One Lucky Run

THE EUREKA:
- Real companies come back
- You don't need the whole 300% move
- Catch 20-50% waves, take profits, re-enter
- Multiple wins > One hoped-for moonshot

THE SYSTEM:
1. SCAN: Find accumulation (vol spike + small move)
2. ENTER: When pre-market confirms
3. RIDE: Let it run
4. EXIT: First sign of exhaustion OR target hit
5. WAIT: For next accumulation signal
6. RE-ENTER: Catch the next wave

The edge is the PROCESS, not any single trade.
"""

import yfinance as yf
import json
import os
from datetime import datetime, timedelta
import argparse

# ============================================================================
# UNIVERSE - Stocks we track for waves
# ============================================================================

UNIVERSE = [
    # AI
    'DVLT', 'BNAI', 'AISP', 'BBAI', 'SOUN', 'AI', 'PATH', 'UPST',
    # Quantum  
    'IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ',
    # Space
    'LUNR', 'RKLB', 'RDW', 'BKSY', 'ASTS', 'SPIR', 'SIDU', 'MNTS',
    # Nuclear
    'LEU', 'UUUU', 'UEC', 'SMR', 'OKLO', 'NNE', 'DNN', 'NXE',
    # Semi
    'WOLF', 'ACLS', 'ALAB', 'CRDO', 'ARM', 'AMD', 'MRVL',
    # Defense
    'RCAT', 'KTOS', 'PLTR',
    # Biotech
    'RXRX', 'BEAM', 'CRSP',
    # Clean/EV
    'QS', 'PLUG', 'FCEL', 'ENVX',
    # Fintech
    'SOFI', 'AFRM', 'HOOD',
    # Movers
    'LVRO', 'GME', 'AMC', 'CVNA',
]

WAVE_LOG = 'logs/wave_tracker.json'

# ============================================================================
# WAVE PHASES
# ============================================================================

def get_wave_phase(ticker):
    """
    Determine where a stock is in its wave cycle:
    
    1. ACCUMULATION - Vol spike + small move (ENTRY ZONE)
    2. MARKUP - Running up (RIDE IT)
    3. DISTRIBUTION - Vol spike at highs (EXIT ZONE)
    4. MARKDOWN - Dropping (STAY OUT)
    5. BASING - Flat, low volume (WATCH)
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1mo')
        info = stock.info
        
        if len(hist) < 10:
            return None
            
        today = hist.iloc[-1]
        yesterday = hist.iloc[-2]
        
        # Volume analysis
        vol_today = today['Volume']
        avg_vol = hist['Volume'].iloc[:-1].mean()
        vol_ratio = vol_today / avg_vol if avg_vol > 0 else 1
        
        # Price analysis
        price = today['Close']
        today_change = (price / yesterday['Close'] - 1) * 100
        
        # Position in range
        high_20d = hist['High'].max()
        low_20d = hist['Low'].min()
        pct_of_range = (price - low_20d) / (high_20d - low_20d) * 100 if (high_20d - low_20d) > 0 else 50
        
        # Week momentum
        week_ago = hist['Close'].iloc[-6] if len(hist) >= 6 else hist['Close'].iloc[0]
        week_change = (price / week_ago - 1) * 100
        
        # Short interest
        short_pct = info.get('shortPercentOfFloat', 0) or 0
        short_pct = short_pct * 100 if short_pct < 1 else short_pct
        
        float_shares = info.get('floatShares', 0) or 0
        
        # ================================================================
        # DETERMINE PHASE
        # ================================================================
        
        phase = 'UNKNOWN'
        action = ''
        
        # ACCUMULATION: Vol spike + small move + near lows
        if vol_ratio >= 1.5 and abs(today_change) < 10 and pct_of_range < 40:
            phase = 'ACCUMULATION'
            action = '🎯 ENTRY ZONE - Someone buying quietly'
            
        # MARKUP: Rising, good volume, momentum
        elif week_change > 10 and pct_of_range > 50:
            phase = 'MARKUP'
            action = '🚀 RIDING - Let it run, trail stop'
            
        # DISTRIBUTION: Vol spike at highs
        elif vol_ratio >= 2 and pct_of_range > 80:
            phase = 'DISTRIBUTION'
            action = '⚠️ EXIT ZONE - Take profits'
            
        # MARKDOWN: Dropping from highs
        elif week_change < -10 and pct_of_range < 50:
            phase = 'MARKDOWN'
            action = '🔴 STAY OUT - Let it fall'
            
        # BASING: Flat, low volume
        elif abs(week_change) < 5 and vol_ratio < 1.2:
            phase = 'BASING'
            action = '👀 WATCH - Wait for accumulation signal'
            
        # IN-BETWEEN states
        elif vol_ratio >= 1.5 and today_change > 10:
            phase = 'BREAKOUT'
            action = '⚡ BREAKING OUT - Can enter, tighter stop'
        else:
            phase = 'NEUTRAL'
            action = '📊 NEUTRAL - No clear signal'
        
        return {
            'ticker': ticker,
            'price': price,
            'phase': phase,
            'action': action,
            'vol_ratio': vol_ratio,
            'today_change': today_change,
            'week_change': week_change,
            'pct_of_range': pct_of_range,
            'short_pct': short_pct,
            'float': float_shares,
        }
        
    except Exception as e:
        return None

# ============================================================================
# WAVE SCANNER
# ============================================================================

def scan_waves():
    """Scan universe and categorize by wave phase"""
    
    print()
    print('='*70)
    print('🐺 WOLF WAVES - Where Is Each Stock In Its Cycle?')
    print('='*70)
    print()
    print('THE SYSTEM:')
    print('  🎯 ACCUMULATION = Entry zone (buy here)')
    print('  🚀 MARKUP = Ride it (trail stop)')
    print('  ⚠️ DISTRIBUTION = Exit zone (take profits)')
    print('  🔴 MARKDOWN = Stay out (let it fall)')
    print('  👀 BASING = Watch (wait for signal)')
    print()
    print('='*70)
    print()
    
    results = {
        'ACCUMULATION': [],
        'BREAKOUT': [],
        'MARKUP': [],
        'DISTRIBUTION': [],
        'MARKDOWN': [],
        'BASING': [],
        'NEUTRAL': [],
    }
    
    for i, ticker in enumerate(UNIVERSE):
        print(f'\r  Scanning {i+1}/{len(UNIVERSE)}: {ticker}...', end='', flush=True)
        wave = get_wave_phase(ticker)
        if wave:
            results[wave['phase']].append(wave)
    
    print('\r' + ' '*50)
    print()
    
    # Show ACCUMULATION (entry zone)
    if results['ACCUMULATION']:
        print('🎯 ACCUMULATION PHASE - ENTRY ZONE')
        print('='*70)
        print('These are accumulating NOW. The run hasn\'t started.')
        print()
        for w in results['ACCUMULATION']:
            print(f"  {w['ticker']:<8} ${w['price']:<8.2f} Vol: {w['vol_ratio']:.1f}x  "
                  f"Today: {w['today_change']:+.1f}%  Range: {w['pct_of_range']:.0f}%")
            if w['short_pct'] >= 15:
                print(f"           └─ {w['short_pct']:.0f}% SHORT - squeeze fuel")
        print()
        
    # Show BREAKOUT (can still enter)
    if results['BREAKOUT']:
        print('⚡ BREAKOUT PHASE - Can Enter With Tighter Stop')
        print('='*70)
        for w in results['BREAKOUT']:
            print(f"  {w['ticker']:<8} ${w['price']:<8.2f} Vol: {w['vol_ratio']:.1f}x  "
                  f"Today: {w['today_change']:+.1f}%")
        print()
        
    # Show MARKUP (riding)
    if results['MARKUP']:
        print('🚀 MARKUP PHASE - Ride These (Trail Your Stop)')
        print('='*70)
        for w in results['MARKUP']:
            print(f"  {w['ticker']:<8} ${w['price']:<8.2f} Week: {w['week_change']:+.1f}%  "
                  f"Range: {w['pct_of_range']:.0f}%")
        print()
        
    # Show DISTRIBUTION (exit zone)
    if results['DISTRIBUTION']:
        print('⚠️ DISTRIBUTION PHASE - EXIT ZONE')
        print('='*70)
        print('Volume spike at highs = smart money selling. Take profits.')
        print()
        for w in results['DISTRIBUTION']:
            print(f"  {w['ticker']:<8} ${w['price']:<8.2f} Vol: {w['vol_ratio']:.1f}x  "
                  f"Range: {w['pct_of_range']:.0f}%")
        print()
        
    # Show MARKDOWN (stay out)
    if results['MARKDOWN']:
        print('🔴 MARKDOWN PHASE - STAY OUT')
        print('='*70)
        print('These are falling. Wait for basing/accumulation.')
        print()
        for w in results['MARKDOWN']:
            print(f"  {w['ticker']:<8} ${w['price']:<8.2f} Week: {w['week_change']:+.1f}%")
        print()
        
    # Show BASING (watch)
    if results['BASING']:
        print('👀 BASING PHASE - Watch For Accumulation Signal')
        print('='*70)
        for w in results['BASING'][:10]:  # Limit
            print(f"  {w['ticker']:<8} ${w['price']:<8.2f} Week: {w['week_change']:+.1f}%  "
                  f"Vol: {w['vol_ratio']:.1f}x")
        print()
    
    # Summary
    print('='*70)
    print('THE PLAYBOOK:')
    print('='*70)
    print()
    print('  🎯 ACCUMULATION: Enter now, stop 10-12% below')
    print('  ⚡ BREAKOUT: Can enter, tighter stop (8%)')
    print('  🚀 MARKUP: Already in? Trail stop. Not in? Wait.')
    print('  ⚠️ DISTRIBUTION: SELL. Take profits. It\'ll come back.')
    print('  🔴 MARKDOWN: Don\'t catch falling knives.')
    print('  👀 BASING: Add to watchlist. Wait for volume.')
    print()
    print('  The edge: Catch multiple waves, not one lucky run.')
    print('  Real companies come back. That\'s the secret.')
    print()
    print('='*70)
    
    return results

def analyze_ticker(ticker):
    """Deep analysis of a single ticker's wave phase"""
    
    wave = get_wave_phase(ticker.upper())
    if not wave:
        print(f'Could not analyze {ticker}')
        return
        
    print()
    print('='*70)
    print(f"🌊 WAVE ANALYSIS: {ticker.upper()}")
    print('='*70)
    print()
    print(f"  PHASE: {wave['phase']}")
    print(f"  {wave['action']}")
    print()
    print(f"  Price: ${wave['price']:.2f}")
    print(f"  Today: {wave['today_change']:+.1f}%")
    print(f"  Week:  {wave['week_change']:+.1f}%")
    print(f"  Volume: {wave['vol_ratio']:.1f}x average")
    print(f"  Position in Range: {wave['pct_of_range']:.0f}% (0=low, 100=high)")
    
    if wave['short_pct'] > 0:
        print(f"  Short Interest: {wave['short_pct']:.1f}%")
    
    print()
    
    # Give specific advice
    if wave['phase'] == 'ACCUMULATION':
        print('  📋 PLAYBOOK:')
        print('  1. This is ENTRY ZONE')
        print('  2. Enter now or wait for pre-market confirmation')
        print(f'  3. Stop loss: ${wave["price"] * 0.88:.2f} (12% below)')
        print(f'  4. First target: ${wave["price"] * 1.25:.2f} (+25%)')
        print('  5. If it hits target, SELL. Wait for next accumulation.')
        
    elif wave['phase'] == 'MARKUP':
        print('  📋 PLAYBOOK:')
        print('  1. This is RIDING PHASE')
        print('  2. If you\'re in: Trail your stop')
        print(f'  3. Suggested trail stop: ${wave["price"] * 0.90:.2f}')
        print('  4. If not in: Wait for pullback to accumulation')
        print('  5. Don\'t chase - it\'ll come back')
        
    elif wave['phase'] == 'DISTRIBUTION':
        print('  📋 PLAYBOOK:')
        print('  1. This is EXIT ZONE')
        print('  2. If you\'re in: TAKE PROFITS')
        print('  3. Volume spike at highs = smart money selling')
        print('  4. Wait for markdown -> basing -> accumulation')
        print('  5. You\'ll get another entry. Be patient.')
        
    elif wave['phase'] == 'MARKDOWN':
        print('  📋 PLAYBOOK:')
        print('  1. STAY OUT')
        print('  2. Don\'t catch falling knives')
        print('  3. Wait for basing (flat, low volume)')
        print('  4. Then wait for accumulation signal')
        print('  5. It\'ll come back. Real companies always do.')
        
    elif wave['phase'] == 'BASING':
        print('  📋 PLAYBOOK:')
        print('  1. Add to watchlist')
        print('  2. Wait for volume spike + small move')
        print('  3. That\'s your accumulation signal')
        print('  4. Then enter with stop 10-12% below')
        
    print()
    print('='*70)

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='🐺 Wolf Waves - Catch Multiple Waves')
    parser.add_argument('command', nargs='?', default='scan',
                        help='scan | TICKER for analysis')
    
    args = parser.parse_args()
    
    if args.command == 'scan':
        scan_waves()
    else:
        analyze_ticker(args.command)

if __name__ == '__main__':
    main()
