#!/usr/bin/env python3
"""
🐺 HUNT #2: SECTOR HEAT TRANSFER
When one stock runs, does another FOLLOW?
Not correlation - LEADING indicators
"""

import yfinance as yf
import numpy as np
import pandas as pd
from itertools import combinations

print("=" * 70)
print("🐺 HUNT #2: SECTOR HEAT TRANSFER")
print("Does one stock's run PREDICT another?")
print("=" * 70)

# Sector groups
quantum = ['IONQ', 'RGTI', 'QBTS']
space = ['LUNR', 'RCAT', 'ASTS']
all_tickers = quantum + space + ['SIDU']

# Download all data
data = {}
for ticker in all_tickers:
    df = yf.download(ticker, start='2024-01-01', progress=False)
    if len(df) > 30:
        if isinstance(df['Close'], pd.DataFrame):
            data[ticker] = {
                'close': df['Close'].iloc[:, 0].values,
                'volume': df['Volume'].iloc[:, 0].values,
                'dates': df.index.tolist()
            }
        else:
            data[ticker] = {
                'close': df['Close'].values,
                'volume': df['Volume'].values,
                'dates': df.index.tolist()
            }

print(f"Loaded data for: {list(data.keys())}")

# Find runs in each stock
def find_runs(close, dates, threshold=10):
    """Find days that start a 10%+ run in next 10 days"""
    runs = []
    last_run = -15
    for i in range(10, len(close)-10):
        if i - last_run < 10:
            continue
        max_gain = max((close[i+j] - close[i]) / close[i] * 100 for j in range(1, 11))
        if max_gain >= threshold:
            runs.append({
                'idx': i,
                'date': dates[i].strftime('%Y-%m-%d'),
                'gain': max_gain
            })
            last_run = i
    return runs

# Find runs for each ticker
runs = {}
for ticker in data:
    runs[ticker] = find_runs(data[ticker]['close'], data[ticker]['dates'])
    print(f"{ticker}: {len(runs[ticker])} runs")

# TEST: Does a run in stock A predict a run in stock B within next 5 days?
print(f"\n{'=' * 70}")
print("LEAD-LAG ANALYSIS")
print("If A runs, does B run in next 5 days?")
print("=" * 70)

results = []

for leader in data:
    for follower in data:
        if leader == follower:
            continue
        
        # Get common dates
        leader_dates = set(d.strftime('%Y-%m-%d') for d in data[leader]['dates'])
        follower_dates = set(d.strftime('%Y-%m-%d') for d in data[follower]['dates'])
        
        # Count times leader's run was followed by follower's run
        follow_count = 0
        total_leader_runs = 0
        
        for run in runs[leader]:
            total_leader_runs += 1
            run_date = run['date']
            
            # Check if follower had a run in next 1-5 days
            for frun in runs[follower]:
                # Find date difference
                try:
                    l_idx = data[leader]['dates'].index(pd.Timestamp(run_date))
                    f_idx = data[follower]['dates'].index(pd.Timestamp(frun['date']))
                    
                    # Follower runs 1-5 days AFTER leader
                    if 1 <= f_idx - l_idx <= 5:
                        follow_count += 1
                        break
                except:
                    pass
        
        if total_leader_runs > 5:
            follow_rate = follow_count / total_leader_runs * 100
            results.append({
                'leader': leader,
                'follower': follower,
                'runs': total_leader_runs,
                'follows': follow_count,
                'rate': follow_rate
            })

# Sort by follow rate
results = sorted(results, key=lambda x: x['rate'], reverse=True)

print(f"\n{'Leader':<8} → {'Follower':<8} | {'L Runs':<8} {'Follows':<8} {'Rate':<8}")
print("-" * 60)

for r in results:
    sig = "🔥" if r['rate'] > 30 else ""
    print(f"{r['leader']:<8} → {r['follower']:<8} | {r['runs']:<8} {r['follows']:<8} {r['rate']:.1f}% {sig}")

# Now test if we can TRADE this
print(f"\n{'=' * 70}")
print("TRADING THE LEADER-FOLLOWER")
print("Buy follower when leader runs")
print("=" * 70)

# Best pairs
best_pairs = [r for r in results if r['rate'] > 25]

for pair in best_pairs[:5]:
    leader = pair['leader']
    follower = pair['follower']
    
    print(f"\n{leader} → {follower}:")
    
    # When leader runs, buy follower, hold 10 days
    returns = []
    
    for run in runs[leader]:
        try:
            l_date = pd.Timestamp(run['date'])
            l_idx = data[leader]['dates'].index(l_date)
            
            # Find same date in follower
            if l_date in data[follower]['dates']:
                f_idx = data[follower]['dates'].index(l_date)
                
                if f_idx + 10 < len(data[follower]['close']):
                    entry = data[follower]['close'][f_idx]
                    exit_10d = data[follower]['close'][f_idx + 10]
                    ret = ((exit_10d - entry) / entry) * 100
                    returns.append(ret)
        except:
            pass
    
    if len(returns) >= 5:
        rets = np.array(returns)
        print(f"  Signals: {len(rets)}")
        print(f"  Win Rate: {(rets > 0).mean() * 100:.1f}%")
        print(f"  Avg Return: {rets.mean():+.2f}%")
        print(f"  Median: {np.median(rets):+.2f}%")

# Test within-sector heat
print(f"\n{'=' * 70}")
print("SECTOR HEAT TEST")
print("Does ANY quantum run predict the others?")
print("=" * 70)

# Quantum sector signal
quantum_signals = []

for ticker in ['IONQ', 'RGTI', 'QBTS']:
    for run in runs[ticker]:
        quantum_signals.append({
            'date': run['date'],
            'ticker': ticker,
            'gain': run['gain']
        })

# Sort by date
quantum_signals = sorted(quantum_signals, key=lambda x: x['date'])

print(f"Total quantum runs: {len(quantum_signals)}")

# When quantum sector is HOT (2+ runs in 5 days), what happens next?
print("\nChecking sector heat clusters...")
