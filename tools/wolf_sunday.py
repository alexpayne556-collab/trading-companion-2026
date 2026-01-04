#!/usr/bin/env python3
"""
🐺 WOLF SUNDAY - Pre-Monday Battle Plan

Run this Sunday evening after 8pm (when futures open).
Gives you the exact game plan for Monday's open.

THE PATTERN WE FOUND:
- Oct 13: QBTS -5.8% Friday -> +23% Monday
- Oct 13: IONQ -8.8% Friday -> +16% Monday
- Oct 13: RGTI -6.8% Friday -> +25% Monday

Friday dip + weekend = Monday explosion
OR
Friday run + continuation = Monday momentum

This scanner tells you which scenario we're in.
"""

import yfinance as yf
import argparse
from datetime import datetime

# ============================================================================
# THE PROVEN REPEATERS - These are our targets
# ============================================================================

REPEATERS = {
    # Quantum (proven to repeat)
    'QBTS': {'runs': 5, 'sector': 'QUANTUM'},
    'IONQ': {'runs': 3, 'sector': 'QUANTUM'},
    'RGTI': {'runs': 5, 'sector': 'QUANTUM'},
    'QUBT': {'runs': 3, 'sector': 'QUANTUM'},
    
    # Nuclear (proven to repeat)
    'LEU': {'runs': 3, 'sector': 'NUCLEAR'},
    'SMR': {'runs': 3, 'sector': 'NUCLEAR'},
    'OKLO': {'runs': 4, 'sector': 'NUCLEAR'},
    'NNE': {'runs': 2, 'sector': 'NUCLEAR'},
    
    # Space (proven to repeat)
    'LUNR': {'runs': 2, 'sector': 'SPACE'},
    'RKLB': {'runs': 4, 'sector': 'SPACE'},
    'RDW': {'runs': 2, 'sector': 'SPACE'},
    
    # Semiconductors
    'WOLF': {'runs': 2, 'sector': 'SEMI'},
    
    # Defense/AI
    'PLTR': {'runs': 2, 'sector': 'DEFENSE'},
    'RCAT': {'runs': 2, 'sector': 'DEFENSE'},
}

# ============================================================================
# ANALYZE FRIDAY'S ACTION
# ============================================================================

def analyze_friday():
    """Analyze what happened Friday to predict Monday"""
    
    results = {
        'friday_dip': [],      # Dipped Friday = Monday setup
        'friday_run': [],      # Ran Friday = Continuation or pullback
        'coiling': [],         # Quiet Friday = Building energy
    }
    
    for ticker, info in REPEATERS.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='5d')
            stock_info = stock.info
            
            if len(hist) < 2:
                continue
                
            friday = hist.iloc[-1]
            thursday = hist.iloc[-2]
            
            fri_change = (friday['Close'] / thursday['Close'] - 1) * 100
            
            # Volume analysis
            avg_vol = hist['Volume'].iloc[:-1].mean()
            vol_ratio = friday['Volume'] / avg_vol if avg_vol > 0 else 1
            
            # Week context
            week_open = hist['Open'].iloc[0]
            week_change = (friday['Close'] / week_open - 1) * 100
            
            # Position in range
            high_5d = hist['High'].max()
            low_5d = hist['Low'].min()
            
            # Dip from recent high
            high_3mo = stock.history(period='3mo')['High'].max()
            dip_from_high = (1 - friday['Close'] / high_3mo) * 100
            
            # Short interest
            short_pct = stock_info.get('shortPercentOfFloat', 0) or 0
            short_pct = short_pct * 100 if short_pct < 1 else short_pct
            
            data = {
                'ticker': ticker,
                'sector': info['sector'],
                'runs': info['runs'],
                'price': friday['Close'],
                'fri_change': fri_change,
                'week_change': week_change,
                'vol_ratio': vol_ratio,
                'dip_from_high': dip_from_high,
                'short_pct': short_pct,
            }
            
            # Categorize
            if fri_change < -3:
                results['friday_dip'].append(data)
            elif fri_change > 5:
                results['friday_run'].append(data)
            else:
                results['coiling'].append(data)
                
        except:
            continue
            
    return results

# ============================================================================
# GENERATE MONDAY GAME PLAN
# ============================================================================

def generate_game_plan():
    """Generate the Monday morning game plan"""
    
    print()
    print('='*70)
    print('🐺 WOLF SUNDAY - Monday Battle Plan')
    print('='*70)
    print(f'  Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    print('='*70)
    print()
    
    results = analyze_friday()
    
    # Count setups
    dippers = len(results['friday_dip'])
    runners = len(results['friday_run'])
    coilers = len(results['coiling'])
    
    # Determine primary scenario
    if runners > dippers + coilers:
        primary = 'CONTINUATION'
    elif dippers > 2:
        primary = 'DIP_BUY'
    else:
        primary = 'MIXED'
    
    print(f'FRIDAY SUMMARY:')
    print(f'  Dipped (Monday setup): {dippers}')
    print(f'  Ran hard: {runners}')
    print(f'  Coiling: {coilers}')
    print()
    print(f'PRIMARY SCENARIO: {primary}')
    print()
    
    # ========================================================================
    # FRIDAY DIPPERS - Monday explosion candidates
    # ========================================================================
    if results['friday_dip']:
        print('='*70)
        print('🎯 FRIDAY DIPPERS - Potential Monday Explosion')
        print('='*70)
        print()
        print('THE PATTERN: Friday dip -> Monday explosion')
        print('  Oct 13: QBTS -5.8% Fri -> +23% Mon')
        print('  Oct 13: IONQ -8.8% Fri -> +16% Mon')
        print()
        
        for d in sorted(results['friday_dip'], key=lambda x: x['fri_change']):
            print(f"  {d['ticker']:<6} Friday: {d['fri_change']:+.1f}%  Vol: {d['vol_ratio']:.1f}x")
            print(f"         Price: ${d['price']:.2f}  Short: {d['short_pct']:.0f}%")
            print(f"         Runs: {d['runs']} in 6mo  Dip from high: -{d['dip_from_high']:.0f}%")
            print()
        
        print('  PLAY: Watch pre-market. If bouncing with volume = BUY EARLY')
        print('        Stop: 8-10% below entry')
        print('        Target: +20-30%')
        print()
    
    # ========================================================================
    # FRIDAY RUNNERS - Continuation or pullback?
    # ========================================================================
    if results['friday_run']:
        print('='*70)
        print('🚀 FRIDAY RUNNERS - Continuation Watch')
        print('='*70)
        print()
        
        for d in sorted(results['friday_run'], key=lambda x: x['fri_change'], reverse=True):
            status = 'EXTENDED' if d['dip_from_high'] < 10 else 'STILL IN RANGE'
            print(f"  {d['ticker']:<6} Friday: {d['fri_change']:+.1f}%  Week: {d['week_change']:+.1f}%")
            print(f"         Price: ${d['price']:.2f}  Short: {d['short_pct']:.0f}%  {status}")
            print()
        
        print('  IF PRE-MARKET GAPS UP:')
        print('    -> Can ride momentum, but TIGHT STOP (5%)')
        print('    -> These already ran, risk of pullback')
        print()
        print('  IF PRE-MARKET GAPS DOWN:')
        print('    -> WAIT. Let them dip 10-15%')
        print('    -> Theyre proven repeaters, theyll come back')
        print()
    
    # ========================================================================
    # COILING - Watch for breakout
    # ========================================================================
    if results['coiling']:
        print('='*70)
        print('⏳ COILING - Watch for Breakout')
        print('='*70)
        print()
        
        for d in results['coiling']:
            print(f"  {d['ticker']:<6} Friday: {d['fri_change']:+.1f}%  Vol: {d['vol_ratio']:.1f}x")
            print(f"         Dip from high: -{d['dip_from_high']:.0f}%  Short: {d['short_pct']:.0f}%")
        print()
        print('  PLAY: Watch for volume spike = breakout signal')
        print()
    
    # ========================================================================
    # THE ACTUAL GAME PLAN
    # ========================================================================
    print('='*70)
    print('📋 MONDAY MORNING CHECKLIST')
    print('='*70)
    print()
    print('  6:00 AM - Check futures (ES, NQ)')
    print('    Green = Risk on, momentum plays work')
    print('    Red = Caution, wait for dip buys')
    print()
    print('  7:00 AM - Check pre-market movers')
    print('    Look for: PROVEN REPEATERS with volume')
    print('    If Friday dipper is bouncing = ENTRY SIGNAL')
    print()
    print('  9:00 AM - First 30 min is chaos')
    print('    WAIT. Let it settle.')
    print('    Unless pre-market was screaming green')
    print()
    print('  9:30 AM - Make your move')
    print('    Scenario 1 (continuation): Buy momentum, tight stop')
    print('    Scenario 2 (pullback): Wait for dip, buy later')
    print('    Scenario 3 (rotation): Buy laggards bouncing')
    print()
    print('='*70)
    print('THE EDGE:')
    print('='*70)
    print()
    print('  We know these are PROVEN REPEATERS.')
    print('  QBTS has run 5 times in 6 months.')
    print('  If it dips, history says it runs again.')
    print()
    print('  We dont guess. We wait for the setup.')
    print('  When the setup comes, we execute.')
    print('  Thats the edge.')
    print()
    print('='*70)
    print('AWOOOO 🐺')
    print('='*70)
    
    return results

# ============================================================================
# QUICK TICKER CHECK
# ============================================================================

def check_ticker(ticker):
    """Quick check on a single ticker"""
    
    ticker = ticker.upper()
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1mo')
        info = stock.info
        
        if len(hist) < 5:
            print(f'Not enough data for {ticker}')
            return
            
        # Current state
        current = hist.iloc[-1]
        yesterday = hist.iloc[-2]
        
        today_change = (current['Close'] / yesterday['Close'] - 1) * 100
        
        # Week
        week_ago = hist['Close'].iloc[-6] if len(hist) >= 6 else hist['Close'].iloc[0]
        week_change = (current['Close'] / week_ago - 1) * 100
        
        # Volume
        avg_vol = hist['Volume'].iloc[:-1].mean()
        vol_ratio = current['Volume'] / avg_vol
        
        # Dip from high
        high = hist['High'].max()
        dip = (1 - current['Close'] / high) * 100
        
        # Short
        short_pct = info.get('shortPercentOfFloat', 0) or 0
        short_pct = short_pct * 100 if short_pct < 1 else short_pct
        
        print()
        print('='*70)
        print(f'🔍 {ticker} Quick Check')
        print('='*70)
        print()
        print(f'  Price: ${current["Close"]:.2f}')
        print(f'  Friday: {today_change:+.1f}%')
        print(f'  Week: {week_change:+.1f}%')
        print(f'  Volume: {vol_ratio:.1f}x average')
        print(f'  Dip from high: -{dip:.0f}%')
        print(f'  Short Interest: {short_pct:.0f}%')
        print()
        
        # Assessment
        if today_change < -5:
            print('  STATUS: 🎯 FRIDAY DIP - Monday setup')
            print('  PLAY: Watch pre-market. Bounce = buy')
        elif today_change > 10:
            print('  STATUS: 🚀 RUNNING HOT')
            print('  PLAY: Can ride but tight stop. Or wait for dip.')
        elif 20 <= dip <= 40:
            print('  STATUS: 💰 IN THE DIP ZONE')
            print('  PLAY: Good entry area if proven repeater')
        else:
            print('  STATUS: 📊 NEUTRAL')
            print('  PLAY: Watch for volume signal')
        
        print()
        print('='*70)
        
    except Exception as e:
        print(f'Error checking {ticker}: {e}')

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='🐺 Wolf Sunday - Monday Battle Plan')
    parser.add_argument('command', nargs='?', default='plan',
                        help='plan | check TICKER')
    parser.add_argument('ticker', nargs='?', help='Ticker to check')
    
    args = parser.parse_args()
    
    if args.command == 'plan':
        generate_game_plan()
    elif args.command == 'check' and args.ticker:
        check_ticker(args.ticker)
    else:
        # Assume it's a ticker
        check_ticker(args.command)

if __name__ == '__main__':
    main()
