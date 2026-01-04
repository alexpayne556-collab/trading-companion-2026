#!/usr/bin/env python3
"""
Direct test - bypassing imports that seem to have issues
"""

import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from scipy import stats

print("Testing Correlation Break Strategy...")
print("=" * 70)

# Manually test the concept
# IONQ and RGTI correlation break - when IONQ runs, does RGTI catch up?

# Get data
print("\nFetching data...")
ionq = yf.download('IONQ', start='2024-06-01', end='2025-12-31', progress=False)
rgti = yf.download('RGTI', start='2024-06-01', end='2025-12-31', progress=False)

# Calculate rolling correlation
window = 20
ionq_ret = ionq['Close'].pct_change()
rgti_ret = rgti['Close'].pct_change()
correlation = ionq_ret.rolling(window).corr(rgti_ret)

avg_corr = float(correlation.mean())
print(f"Average correlation: {avg_corr:.3f}")

# Find divergences
signals = []

for i in range(window, len(ionq)-5):
    if correlation.iloc[i] > 0.7:  # Normally correlated
        # Check for gap
        ionq_move = ((ionq['Close'].iloc[i] - ionq['Close'].iloc[i-1]) / ionq['Close'].iloc[i-1]) * 100
        rgti_move = ((rgti['Close'].iloc[i] - rgti['Close'].iloc[i-1]) / rgti['Close'].iloc[i-1]) * 100
        
        gap = abs(ionq_move - rgti_move)
        
        if gap > 8:  # Significant divergence
            # Which lagged?
            if ionq_move > rgti_move:
                # RGTI lagged - buy RGTI
                entry_price = rgti['Close'].iloc[i]
                exit_price = rgti['Close'].iloc[min(i+5, len(rgti)-1)]
                ret = ((exit_price - entry_price) / entry_price) * 100
                signals.append({
                    'date': rgti.index[i],
                    'ticker': 'RGTI',
                    'return': ret
                })

print(f"\nFound {len(signals)} signals")

if signals:
    returns = [s['return'] for s in signals]
    returns = np.array(returns)
    
    win_rate = (returns > 0).mean() * 100
    avg_return = returns.mean()
    
    print(f"\nBASIC RESULTS:")
    print(f"  Win Rate: {win_rate:.1f}%")
    print(f"  Avg Return: {avg_return:+.2f}%")
    
    # Monte Carlo
    print(f"\nRunning Monte Carlo...")
    
    # Get random returns from RGTI
    random_returns = []
    for i in range(len(rgti)-5):
        entry = rgti['Close'].iloc[i]
        exit_val = rgti['Close'].iloc[i+5]
        ret = ((exit_val - entry) / entry) * 100
        random_returns.append(ret)
    
    random_returns = np.array(random_returns)
    
    mc_results = []
    for _ in range(1000):
        sample = np.random.choice(random_returns, size=len(returns), replace=True)
        mc_results.append(sample.mean())
    
    mc_results = np.array(mc_results)
    mc_mean = mc_results.mean()
    mc_std = mc_results.std()
    
    p_value = (mc_results >= avg_return).mean()
    cohens_d = (avg_return - mc_mean) / mc_std if mc_std > 0 else 0
    std_devs = cohens_d
    
    print(f"\nMONTE CARLO:")
    print(f"  Strategy: {avg_return:+.2f}%")
    print(f"  Random: {mc_mean:+.2f}%")
    print(f"  P-value: {p_value:.4f}")
    print(f"  Effect size: {cohens_d:.2f}")
    print(f"  Std devs above random: {std_devs:.1f}")
    
    print("\n" + "=" * 70)
    if p_value < 0.05 and abs(std_devs) > 2:
        print("✅ REAL EDGE")
    elif p_value < 0.10:
        print("⚠️  MARGINAL")
    else:
        print("❌ NO EDGE")
    print("=" * 70)
