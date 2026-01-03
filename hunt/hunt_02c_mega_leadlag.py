#!/usr/bin/env python3
"""
🐺 HUNT #2c: MEGA LEAD-LAG TEST
Test ALL the best lead-lag pairs with proper stats
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("🐺 MEGA LEAD-LAG TEST")
print("Testing all promising leader-follower pairs")
print("=" * 70)

# Best pairs from initial analysis
pairs = [
    ('ASTS', 'RCAT', 60.0),
    ('IONQ', 'RCAT', 57.6),
    ('RGTI', 'RCAT', 52.6),
    ('RCAT', 'LUNR', 52.6),
    ('LUNR', 'RGTI', 51.4),
    ('LUNR', 'IONQ', 48.6),
    ('ASTS', 'QBTS', 48.6),
    ('IONQ', 'SIDU', 45.5),
]

# Download all data once
all_tickers = list(set([p[0] for p in pairs] + [p[1] for p in pairs]))
data = {}

for ticker in all_tickers:
    df = yf.download(ticker, start='2024-01-01', progress=False)
    if isinstance(df['Close'], pd.DataFrame):
        data[ticker] = df['Close'].iloc[:, 0]
    else:
        data[ticker] = df['Close']

print(f"Loaded: {list(data.keys())}")

# Test each pair
results = []

for leader, follower, follow_rate in pairs:
    # Align dates
    common = data[leader].index.intersection(data[follower].index)
    l_prices = data[leader][common]
    f_prices = data[follower][common]
    
    # Find leader runs (10%+ in 10 days)
    runs = []
    last_run = -15
    
    for i in range(10, len(l_prices)-10):
        if i - last_run < 10:
            continue
        
        entry = l_prices.iloc[i]
        max_gain = max((l_prices.iloc[i+j] - entry) / entry * 100 for j in range(1, 11))
        
        if max_gain >= 10:
            runs.append(i)
            last_run = i
    
    # Trade follower when leader runs
    signals = []
    for idx in runs:
        if idx + 10 < len(f_prices):
            entry = f_prices.iloc[idx]
            exit_10d = f_prices.iloc[idx + 10]
            ret = ((exit_10d - entry) / entry) * 100
            signals.append(ret)
    
    if len(signals) >= 10:
        rets = np.array(signals)
        
        # Collect random returns for MC
        random_rets = []
        for i in range(len(f_prices)-10):
            ret = ((f_prices.iloc[i+10] - f_prices.iloc[i]) / f_prices.iloc[i]) * 100
            random_rets.append(ret)
        random_rets = np.array(random_rets)
        
        # Monte Carlo
        mc_results = []
        for _ in range(1000):
            sample = np.random.choice(random_rets, size=len(rets))
            mc_results.append(sample.mean())
        
        mc_results = np.array(mc_results)
        mc_mean = mc_results.mean()
        mc_std = mc_results.std()
        
        avg_ret = rets.mean()
        p_value = (mc_results >= avg_ret).mean()
        effect = (avg_ret - mc_mean) / mc_std if mc_std > 0 else 0
        
        results.append({
            'leader': leader,
            'follower': follower,
            'follow_rate': follow_rate,
            'signals': len(rets),
            'win_rate': (rets > 0).mean() * 100,
            'avg_return': avg_ret,
            'random': mc_mean,
            'p_value': p_value,
            'effect': effect
        })

# Display results
print(f"\n{'=' * 70}")
print("LEAD-LAG TEST RESULTS")
print("=" * 70)

print(f"\n{'Pair':<15} {'Sigs':<6} {'WR%':<8} {'Avg Ret':<10} {'Random':<10} {'P-val':<8} {'Effect':<8}")
print("-" * 75)

for r in sorted(results, key=lambda x: x['p_value']):
    sig = "✅" if r['p_value'] < 0.05 else "⚠️" if r['p_value'] < 0.10 else ""
    pair = f"{r['leader']}→{r['follower']}"
    print(f"{pair:<15} {r['signals']:<6} {r['win_rate']:<8.1f} {r['avg_return']:<+10.2f} {r['random']:<+10.2f} {r['p_value']:<8.4f} {r['effect']:<+8.2f} {sig}")

# Check if any hit p < 0.05
winners = [r for r in results if r['p_value'] < 0.05]
marginals = [r for r in results if 0.05 <= r['p_value'] < 0.10]

print(f"\n{'=' * 70}")
if winners:
    print(f"✅ {len(winners)} PAIRS HIT P < 0.05!")
    for w in winners:
        print(f"   {w['leader']} → {w['follower']}: p={w['p_value']:.4f}, +{w['avg_return']:.1f}%")
elif marginals:
    print(f"⚠️  {len(marginals)} pairs marginal (p < 0.10)")
else:
    print("❌ No statistically significant lead-lag found")
print(f"{'=' * 70}")
