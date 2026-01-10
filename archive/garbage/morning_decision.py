#!/usr/bin/env python3
"""
🐺 MORNING DECISION
Run at 9:45 AM. Get YES/NO answer. Execute.

python tools/morning_decision.py
"""

import yfinance as yf
import pandas as pd

UNIVERSE = ['IONQ', 'RGTI', 'QBTS', 'UUUU', 'USAR', 'NXE', 'DNN', 
            'RKLB', 'ASTS', 'LUNR', 'SIDU', 'NVTS', 'NXPI', 'SWKS', 
            'MRVL', 'MU', 'SMCI', 'PLTR']

print("🐺 MORNING DECISION - 9:45 AM")
print("="*80)

# Count movers RIGHT NOW
movers = []

for ticker in UNIVERSE:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='2d')
        
        if len(hist) < 2:
            continue
        
        today = hist.iloc[-1]
        yesterday = hist.iloc[-2]
        
        # Today's move so far
        day_change = ((today['Close'] - today['Open']) / today['Open']) * 100
        
        if day_change > 3:
            movers.append({
                'ticker': ticker,
                'change': day_change,
                'price': today['Close']
            })
    
    except:
        continue

# Sort by change
movers.sort(key=lambda x: x['change'], reverse=True)

print(f"\n📊 MOVERS COUNT: {len(movers)}")
print("-"*80)

for m in movers[:10]:
    print(f"  {m['ticker']:6} {m['change']:+6.2f}%")

print("\n" + "="*80)
print("🎯 THE DECISION:")
print("="*80)

if len(movers) >= 8:
    print("""
✅ 8+ MOVERS - HERD STILL RUNNING

ACTION: HOLD EVERYTHING
- Don't sell anything
- Let it run another day
- This is Day 4 continuation
""")

elif len(movers) >= 5:
    print("""
⚠️  5-7 MOVERS - WEAKENING

ACTION: TRIM 30% OF WINNERS
- SIDU: Sell 5 shares (keep 10)
- NVTS: Sell 3 shares (keep 7)
- USAR: Sell 2 shares (keep 5)
- ASTS: Hold (only 1 share)
- UUUU: Hold (never moved)
""")

elif len(movers) >= 3:
    print("""
🟡 3-4 MOVERS - PARTY ENDING

ACTION: TRIM 50% OF EVERYTHING
- SIDU: Sell 7 shares
- NVTS: Sell 5 shares
- USAR: Sell 3 shares
- ASTS: Hold (only 1 share)
- UUUU: Hold (never moved)
""")

else:
    print("""
🔴 <3 MOVERS - PARTY OVER

ACTION: EXIT EVERYTHING GREEN
- SIDU: Sell ALL 15 shares
- NVTS: Sell ALL 10 shares
- USAR: Sell ALL 7 shares
- ASTS: Sell 1 share
- UUUU: Hold (wait for next party)
""")

print("="*80)
print("Execute this. Don't think. The data decided for you.")
print("="*80)
