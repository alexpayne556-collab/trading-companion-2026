#!/usr/bin/env python3
"""
🐺 HISTORICAL MOVERS BACKFILL - Get 30-60 Days of Big Movers

Fenrir claimed to have this. He didn't.
I'm building it now.

- Scans for 15%+ moves in past 30-60 days
- Gets volume, float, market cap context
- Calculates forward returns (Day 1-5)
- Outputs JSON for pattern analysis
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import time
import argparse


def get_universe():
    """Get tickers to scan - combines multiple sources"""
    
    # Our existing universe (small/mid caps)
    small_caps = [
        'SOUN', 'AISP', 'PTON', 'PLUG', 'CLOV', 'SOFI', 'HOOD', 'LCID', 
        'RIVN', 'NKLA', 'BYND', 'OPEN',
        'COIN', 'MARA', 'RIOT', 'WULF', 'CLSK', 'BTBT', 'CIFR', 'IREN',
        'ATOS', 'CPOP', 'APLD', 'ATON', 'CORZ',
        'NVAX', 'MRNA', 'BNTX', 'SAVA', 'BMRN', 'RARE', 'BEAM', 'NTLA',
        'CRSP', 'EDIT', 'VRTX', 'IONS', 'SRPT', 'EXAS', 'PACB', 'ILMN',
        'EVTV', 'CREX', 'GEVO', 'BLNK', 'CHPT', 'QS', 'LCID',
        'SPCE', 'RKLB', 'RDW', 'VORB', 'LUNR', 'ASTS',
        'KTOS', 'PLTR', 'PALTR', 'RCAT', 'JOBY', 'LILM', 'ACHR',
        'SMR', 'OKLO', 'NNE', 'CCJ', 'UEC', 'UUUU', 'DNN',
        'IONQ', 'RGTI', 'QUBT', 'ARQQ', 'QBTS',
        'PATH', 'AI', 'UPST', 'AFRM', 'SQ', 'PYPL',
        'TSLA', 'F', 'GM', 'RIVN', 'LCID',
    ]
    
    # Dedupe
    return list(set(small_caps))


def find_big_movers(ticker, start_date, end_date, threshold=15.0):
    """
    Find days where ticker moved 15%+ 
    Returns list of move events with context
    """
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date, interval='1d')
        
        if len(hist) < 5:
            return []
        
        moves = []
        
        for i in range(1, len(hist)):
            today = hist.iloc[i]
            yesterday = hist.iloc[i-1]
            
            # Calculate daily change
            change_pct = ((today['Close'] - yesterday['Close']) / yesterday['Close']) * 100
            
            # Check if big move
            if abs(change_pct) >= threshold:
                # Calculate volume ratio
                avg_vol_20d = hist.iloc[max(0,i-20):i]['Volume'].mean() if i >= 5 else hist.iloc[:i]['Volume'].mean()
                vol_ratio = today['Volume'] / avg_vol_20d if avg_vol_20d > 0 else 0
                
                move_date = hist.index[i].strftime('%Y-%m-%d')
                
                # Get forward returns (Day 1-5)
                forward_returns = {}
                for day in [1, 2, 3, 5]:
                    if i + day < len(hist):
                        future_close = hist.iloc[i + day]['Close']
                        forward_returns[f'day_{day}'] = ((future_close - today['Close']) / today['Close']) * 100
                    else:
                        forward_returns[f'day_{day}'] = None
                
                # Peak gain in next 5 days
                if i + 5 < len(hist):
                    future_highs = hist.iloc[i+1:min(i+6, len(hist))]['High']
                    peak = future_highs.max()
                    peak_gain = ((peak - today['Close']) / today['Close']) * 100
                    
                    # Days to peak
                    peak_idx = future_highs.idxmax()
                    days_to_peak = (peak_idx - hist.index[i]).days
                else:
                    peak_gain = None
                    days_to_peak = None
                
                # Determine outcome
                if forward_returns.get('day_3'):
                    if forward_returns['day_3'] >= 5:
                        outcome = 'WINNER'
                    elif forward_returns['day_3'] <= -5:
                        outcome = 'LOSER'
                    else:
                        outcome = 'FLAT'
                else:
                    outcome = 'UNKNOWN'
                
                moves.append({
                    'ticker': ticker,
                    'date': move_date,
                    'move_pct': round(change_pct, 2),
                    'close': round(today['Close'], 2),
                    'volume': int(today['Volume']),
                    'volume_ratio': round(vol_ratio, 2),
                    'day_1_return': round(forward_returns.get('day_1', 0) or 0, 2),
                    'day_2_return': round(forward_returns.get('day_2', 0) or 0, 2),
                    'day_3_return': round(forward_returns.get('day_3', 0) or 0, 2),
                    'day_5_return': round(forward_returns.get('day_5', 0) or 0, 2),
                    'peak_gain': round(peak_gain, 2) if peak_gain else None,
                    'days_to_peak': days_to_peak,
                    'outcome': outcome
                })
        
        return moves
        
    except Exception as e:
        return []


def backfill_movers(days_back=30, threshold=15.0, output_file='historical_movers.json'):
    """
    Backfill historical movers for pattern analysis
    """
    
    print("🐺 HISTORICAL MOVERS BACKFILL")
    print("="*70)
    print(f"Period: Last {days_back} days")
    print(f"Threshold: {threshold}%+ moves")
    print("="*70)
    
    universe = get_universe()
    print(f"\nScanning {len(universe)} tickers...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back + 10)  # Extra buffer for forward returns
    
    all_movers = []
    
    for i, ticker in enumerate(universe, 1):
        if i % 20 == 0:
            print(f"   Progress: {i}/{len(universe)} tickers...")
        
        moves = find_big_movers(ticker, start_date.strftime('%Y-%m-%d'), 
                                end_date.strftime('%Y-%m-%d'), threshold)
        all_movers.extend(moves)
        
        time.sleep(0.1)  # Rate limiting
    
    # Sort by date
    all_movers.sort(key=lambda x: x['date'], reverse=True)
    
    # Save to JSON
    with open(output_file, 'w') as f:
        json.dump(all_movers, f, indent=2)
    
    print(f"\n✅ Found {len(all_movers)} moves of {threshold}%+")
    print(f"💾 Saved to {output_file}")
    
    # Print summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    # Winners vs losers
    winners = [m for m in all_movers if m['outcome'] == 'WINNER']
    losers = [m for m in all_movers if m['outcome'] == 'LOSER']
    flat = [m for m in all_movers if m['outcome'] == 'FLAT']
    
    total_known = len(winners) + len(losers) + len(flat)
    if total_known > 0:
        print(f"\nOutcomes (Day 3 return):")
        print(f"   Winners (+5%+): {len(winners)} ({len(winners)/total_known*100:.1f}%)")
        print(f"   Losers (-5%+):  {len(losers)} ({len(losers)/total_known*100:.1f}%)")
        print(f"   Flat:           {len(flat)} ({len(flat)/total_known*100:.1f}%)")
    
    # Volume ratio analysis
    high_vol = [m for m in all_movers if m['volume_ratio'] >= 5]
    low_vol = [m for m in all_movers if m['volume_ratio'] < 2]
    
    print(f"\nVolume Analysis:")
    print(f"   High volume (5x+): {len(high_vol)} moves")
    print(f"   Low volume (<2x):  {len(low_vol)} moves")
    
    if high_vol:
        high_vol_winners = len([m for m in high_vol if m['outcome'] == 'WINNER'])
        print(f"   High vol win rate: {high_vol_winners/len(high_vol)*100:.1f}%")
    
    if low_vol:
        low_vol_winners = len([m for m in low_vol if m['outcome'] == 'WINNER'])
        print(f"   Low vol win rate:  {low_vol_winners/len(low_vol)*100:.1f}%")
    
    # Top movers
    print(f"\n🔥 TOP 10 BIGGEST MOVES:")
    print("-" * 70)
    for m in sorted(all_movers, key=lambda x: abs(x['move_pct']), reverse=True)[:10]:
        print(f"   {m['date']} {m['ticker']:6s} {m['move_pct']:+7.1f}%  "
              f"Vol: {m['volume_ratio']:5.1f}x  D3: {m['day_3_return']:+6.1f}%  {m['outcome']}")
    
    return all_movers


def analyze_patterns(movers_file='historical_movers.json'):
    """Analyze patterns from historical movers data"""
    
    with open(movers_file, 'r') as f:
        movers = json.load(f)
    
    print("\n" + "="*70)
    print("🔬 PATTERN ANALYSIS")
    print("="*70)
    
    # Volume threshold analysis
    thresholds = [2, 3, 5, 10]
    
    print("\nVolume Ratio vs Win Rate:")
    print("-" * 50)
    
    for thresh in thresholds:
        subset = [m for m in movers if m['volume_ratio'] >= thresh]
        if subset:
            winners = len([m for m in subset if m['outcome'] == 'WINNER'])
            total = len([m for m in subset if m['outcome'] in ['WINNER', 'LOSER', 'FLAT']])
            if total > 0:
                win_rate = winners / total * 100
                print(f"   Volume >= {thresh}x: {win_rate:.1f}% win rate ({winners}/{total})")
    
    # Extension analysis (how much is left to run?)
    print("\nMove Size vs Continuation:")
    print("-" * 50)
    
    small_moves = [m for m in movers if 15 <= abs(m['move_pct']) <= 30]
    big_moves = [m for m in movers if abs(m['move_pct']) > 30]
    
    if small_moves:
        small_cont = len([m for m in small_moves if m['day_3_return'] and m['day_3_return'] > 0])
        print(f"   15-30% moves: {small_cont/len(small_moves)*100:.1f}% continue D3")
    
    if big_moves:
        big_cont = len([m for m in big_moves if m['day_3_return'] and m['day_3_return'] > 0])
        print(f"   30%+ moves:   {big_cont/len(big_moves)*100:.1f}% continue D3")
    
    # Peak timing
    print("\nPeak Timing (Days to Peak):")
    print("-" * 50)
    
    with_peak = [m for m in movers if m['days_to_peak'] is not None and m['peak_gain'] and m['peak_gain'] > 0]
    if with_peak:
        avg_days = sum(m['days_to_peak'] for m in with_peak) / len(with_peak)
        print(f"   Average days to peak: {avg_days:.1f}")
        
        day1_peak = len([m for m in with_peak if m['days_to_peak'] == 1])
        day2_peak = len([m for m in with_peak if m['days_to_peak'] == 2])
        day3_peak = len([m for m in with_peak if m['days_to_peak'] == 3])
        
        print(f"   Peak Day 1: {day1_peak/len(with_peak)*100:.1f}%")
        print(f"   Peak Day 2: {day2_peak/len(with_peak)*100:.1f}%")
        print(f"   Peak Day 3: {day3_peak/len(with_peak)*100:.1f}%")


def main():
    parser = argparse.ArgumentParser(description='Historical movers backfill and analysis')
    parser.add_argument('command', choices=['backfill', 'analyze'],
                       help='backfill=scan for movers, analyze=analyze existing data')
    parser.add_argument('--days', type=int, default=30, help='Days to look back (default: 30)')
    parser.add_argument('--threshold', type=float, default=15.0, help='Move threshold % (default: 15)')
    parser.add_argument('--output', default='historical_movers.json', help='Output file')
    
    args = parser.parse_args()
    
    if args.command == 'backfill':
        backfill_movers(args.days, args.threshold, args.output)
    elif args.command == 'analyze':
        analyze_patterns(args.output)


if __name__ == "__main__":
    main()
