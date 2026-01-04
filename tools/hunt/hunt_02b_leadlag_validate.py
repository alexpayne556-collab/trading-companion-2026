#!/usr/bin/env python3
"""
🐺 HUNT #2b: VALIDATE LEAD-LAG
LUNR runs → Buy RGTI
60% follow rate, 71% win rate
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("🐺 VALIDATING: LUNR → RGTI LEAD-LAG")
print("When LUNR runs 10%+, buy RGTI")
print("=" * 70)

# Download data
lunr = yf.download('LUNR', start='2024-01-01', progress=False)
rgti = yf.download('RGTI', start='2024-01-01', progress=False)

if isinstance(lunr['Close'], pd.DataFrame):
    lunr_close = lunr['Close'].iloc[:, 0]
    rgti_close = rgti['Close'].iloc[:, 0]
else:
    lunr_close = lunr['Close']
    rgti_close = rgti['Close']

# Align dates
common_dates = lunr_close.index.intersection(rgti_close.index)
lunr_close = lunr_close[common_dates]
rgti_close = rgti_close[common_dates]

print(f"Common dates: {len(common_dates)}")

# Find LUNR runs
lunr_runs = []
last_run = -15

for i in range(10, len(lunr_close)-10):
    if i - last_run < 10:
        continue
    
    # Check for 10%+ gain in next 10 days
    entry = lunr_close.iloc[i]
    max_gain = 0
    for j in range(1, 11):
        gain = ((lunr_close.iloc[i+j] - entry) / entry) * 100
        max_gain = max(max_gain, gain)
    
    if max_gain >= 10:
        lunr_runs.append({
            'idx': i,
            'date': common_dates[i],
            'gain': max_gain
        })
        last_run = i

print(f"LUNR runs found: {len(lunr_runs)}")

# For each LUNR run, buy RGTI
signals = []
all_rgti_returns = []

# Collect all RGTI 10-day returns for Monte Carlo
for i in range(len(rgti_close)-10):
    ret = ((rgti_close.iloc[i+10] - rgti_close.iloc[i]) / rgti_close.iloc[i]) * 100
    all_rgti_returns.append(ret)

# Trade signals
for run in lunr_runs:
    idx = run['idx']
    
    if idx + 10 < len(rgti_close):
        entry = rgti_close.iloc[idx]
        exit_10d = rgti_close.iloc[idx + 10]
        ret = ((exit_10d - entry) / entry) * 100
        
        signals.append({
            'date': run['date'].strftime('%Y-%m-%d'),
            'lunr_gain': run['gain'],
            'rgti_return': ret
        })

print(f"\n{'=' * 70}")
print("LEAD-LAG SIGNALS:")
print("=" * 70)

for s in sorted(signals, key=lambda x: x['rgti_return'], reverse=True):
    win = "✓" if s['rgti_return'] > 0 else "✗"
    print(f"{s['date']} LUNR +{s['lunr_gain']:.0f}% → RGTI {s['rgti_return']:+.1f}% {win}")

# Statistics
rets = np.array([s['rgti_return'] for s in signals])

print(f"\n{'=' * 70}")
print("PERFORMANCE:")
print("=" * 70)
print(f"Signals: {len(rets)}")
print(f"Win Rate: {(rets > 0).mean() * 100:.1f}%")
print(f"Avg Return: {rets.mean():+.2f}%")
print(f"Median: {np.median(rets):+.2f}%")

# Monte Carlo
print(f"\nMONTE CARLO...")

all_rgti_returns = np.array(all_rgti_returns)

mc_results = []
for _ in range(1000):
    sample = np.random.choice(all_rgti_returns, size=len(rets))
    mc_results.append(sample.mean())

mc_results = np.array(mc_results)
mc_mean = mc_results.mean()
mc_std = mc_results.std()

avg_ret = rets.mean()
p_value = (mc_results >= avg_ret).mean()
effect_size = (avg_ret - mc_mean) / mc_std if mc_std > 0 else 0

print(f"\nSTATISTICAL VALIDATION:")
print(f"  Strategy: {avg_ret:+.2f}%")
print(f"  Random RGTI: {mc_mean:+.2f}%")
print(f"  Outperformance: {avg_ret - mc_mean:+.2f}%")
print(f"  P-value: {p_value:.4f}")
print(f"  Effect: {effect_size:.2f}")

print(f"\n{'=' * 70}")
if p_value < 0.05:
    print("✅ LEAD-LAG CONFIRMED! P < 0.05")
elif p_value < 0.10:
    print("⚠️  MARGINAL")
else:
    print("❌ NO EDGE")
print(f"{'=' * 70}")
