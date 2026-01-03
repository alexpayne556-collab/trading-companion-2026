#!/usr/bin/env python3
"""
🐺 HUNT #1: PRE-RUN SIGNATURE
What do repeat runners look like 1-5 days BEFORE a 10%+ move?

Mission: Find the fingerprint that appears before explosions.
"""

import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

print("=" * 70)
print("🐺 HUNT #1: PRE-RUN SIGNATURE")
print("What happens BEFORE 10%+ moves?")
print("=" * 70)

# The repeat runners
tickers = ['SIDU', 'RGTI', 'QBTS', 'RCAT', 'LUNR', 'ASTS', 'IONQ']

all_explosions = []
all_normal = []

for ticker in tickers:
    print(f"\nHunting {ticker}...")
    df = yf.download(ticker, start='2024-01-01', progress=False)
    
    if len(df) < 30:
        continue
    
    # Extract data
    if isinstance(df['Close'], pd.DataFrame):
        close = df['Close'].iloc[:, 0].values
        high = df['High'].iloc[:, 0].values
        low = df['Low'].iloc[:, 0].values
        volume = df['Volume'].iloc[:, 0].values
    else:
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        volume = df['Volume'].values
    
    dates = df.index.tolist()
    
    # Find all 10%+ moves in 10-day windows
    explosions_found = 0
    for i in range(25, len(close)-10):
        # Look forward 10 days
        max_gain = 0
        for j in range(1, 11):
            if i + j < len(close):
                gain = ((close[i+j] - close[i]) / close[i]) * 100
                max_gain = max(max_gain, gain)
        
        # EXPLOSION: 10%+ gain in next 10 days
        if max_gain >= 10:
            explosions_found += 1
            
            # Look BACKWARDS at pre-run characteristics
            # Volume pattern (5 days before)
            base_vol = np.mean(volume[i-20:i-5])
            prerun_vol = np.mean(volume[i-5:i])
            vol_ratio_prerun = prerun_vol / base_vol if base_vol > 0 else 1
            
            # Volume on signal day
            day_vol_ratio = volume[i] / base_vol if base_vol > 0 else 1
            
            # Price change 5 days before
            price_5d = ((close[i] - close[i-5]) / close[i-5]) * 100
            
            # CLV over 5 days before
            clvs = []
            for k in range(i-5, i):
                day_range = high[k] - low[k]
                if day_range > 0:
                    clvs.append((close[k] - low[k]) / day_range)
                else:
                    clvs.append(0.5)
            avg_clv = np.mean(clvs)
            
            # Distance from 20-day high
            high_20 = max(high[i-20:i])
            pct_from_high = ((close[i] - high_20) / high_20) * 100
            
            # Up/down volume ratio
            up_vol = sum(volume[k] for k in range(i-20, i) if close[k] > close[k-1])
            down_vol = sum(volume[k] for k in range(i-20, i) if close[k] < close[k-1])
            updown_ratio = up_vol / down_vol if down_vol > 0 else 1
            
            # Volatility (ATR proxy)
            atr = np.mean([high[k] - low[k] for k in range(i-10, i)])
            atr_pct = (atr / close[i]) * 100
            
            all_explosions.append({
                'ticker': ticker,
                'date': dates[i].strftime('%Y-%m-%d'),
                'max_gain': max_gain,
                'vol_ratio_prerun': vol_ratio_prerun,
                'day_vol_ratio': day_vol_ratio,
                'price_5d': price_5d,
                'avg_clv': avg_clv,
                'pct_from_high': pct_from_high,
                'updown_ratio': updown_ratio,
                'atr_pct': atr_pct
            })
        else:
            # Normal day (no explosion coming)
            base_vol = np.mean(volume[i-20:i-5])
            prerun_vol = np.mean(volume[i-5:i])
            vol_ratio_prerun = prerun_vol / base_vol if base_vol > 0 else 1
            day_vol_ratio = volume[i] / base_vol if base_vol > 0 else 1
            price_5d = ((close[i] - close[i-5]) / close[i-5]) * 100
            
            clvs = []
            for k in range(i-5, i):
                day_range = high[k] - low[k]
                if day_range > 0:
                    clvs.append((close[k] - low[k]) / day_range)
                else:
                    clvs.append(0.5)
            avg_clv = np.mean(clvs)
            
            high_20 = max(high[i-20:i])
            pct_from_high = ((close[i] - high_20) / high_20) * 100
            
            up_vol = sum(volume[k] for k in range(i-20, i) if close[k] > close[k-1])
            down_vol = sum(volume[k] for k in range(i-20, i) if close[k] < close[k-1])
            updown_ratio = up_vol / down_vol if down_vol > 0 else 1
            
            atr = np.mean([high[k] - low[k] for k in range(i-10, i)])
            atr_pct = (atr / close[i]) * 100
            
            all_normal.append({
                'vol_ratio_prerun': vol_ratio_prerun,
                'day_vol_ratio': day_vol_ratio,
                'price_5d': price_5d,
                'avg_clv': avg_clv,
                'pct_from_high': pct_from_high,
                'updown_ratio': updown_ratio,
                'atr_pct': atr_pct
            })
    
    print(f"  Found {explosions_found} explosion setups")

print(f"\n{'=' * 70}")
print(f"TOTAL EXPLOSIONS: {len(all_explosions)}")
print(f"NORMAL DAYS: {len(all_normal)}")
print(f"{'=' * 70}")

# ANALYZE THE DIFFERENCES
print("\n" + "=" * 70)
print("PRE-RUN SIGNATURE ANALYSIS")
print("What's different BEFORE explosions?")
print("=" * 70)

metrics = ['vol_ratio_prerun', 'day_vol_ratio', 'price_5d', 'avg_clv', 
           'pct_from_high', 'updown_ratio', 'atr_pct']

from scipy import stats

print(f"\n{'Metric':<20} {'Pre-Explosion':<15} {'Normal':<15} {'Diff':<10} {'P-value':<10}")
print("-" * 70)

significant_metrics = []

for metric in metrics:
    exp_vals = [e[metric] for e in all_explosions]
    norm_vals = [n[metric] for n in all_normal]
    
    exp_mean = np.mean(exp_vals)
    norm_mean = np.mean(norm_vals)
    diff = exp_mean - norm_mean
    
    # t-test
    t_stat, p_val = stats.ttest_ind(exp_vals, norm_vals)
    
    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
    
    print(f"{metric:<20} {exp_mean:<15.2f} {norm_mean:<15.2f} {diff:<+10.2f} {p_val:<10.4f} {sig}")
    
    if p_val < 0.05:
        significant_metrics.append((metric, exp_mean, norm_mean, p_val))

print(f"\n{'=' * 70}")
print("SIGNIFICANT PRE-RUN SIGNATURES (p < 0.05):")
print("=" * 70)

for metric, exp, norm, p in significant_metrics:
    if metric == 'vol_ratio_prerun':
        print(f"📊 5-day volume before: {exp:.2f}x vs {norm:.2f}x normal (p={p:.4f})")
    elif metric == 'day_vol_ratio':
        print(f"📊 Signal day volume: {exp:.2f}x vs {norm:.2f}x normal (p={p:.4f})")
    elif metric == 'price_5d':
        print(f"📊 5-day price change: {exp:+.1f}% vs {norm:+.1f}% normal (p={p:.4f})")
    elif metric == 'avg_clv':
        print(f"📊 5-day CLV: {exp:.2f} vs {norm:.2f} normal (p={p:.4f})")
    elif metric == 'pct_from_high':
        print(f"📊 Distance from high: {exp:.1f}% vs {norm:.1f}% normal (p={p:.4f})")
    elif metric == 'updown_ratio':
        print(f"📊 Up/down vol ratio: {exp:.2f} vs {norm:.2f} normal (p={p:.4f})")
    elif metric == 'atr_pct':
        print(f"📊 Volatility (ATR%): {exp:.2f}% vs {norm:.2f}% normal (p={p:.4f})")

# Show biggest explosions and their pre-run signatures
print(f"\n{'=' * 70}")
print("TOP 15 EXPLOSIONS - PRE-RUN FINGERPRINTS:")
print("=" * 70)

sorted_exp = sorted(all_explosions, key=lambda x: x['max_gain'], reverse=True)
for e in sorted_exp[:15]:
    print(f"{e['date']} {e['ticker']:5} +{e['max_gain']:.0f}% | "
          f"5d vol={e['vol_ratio_prerun']:.1f}x | "
          f"CLV={e['avg_clv']:.2f} | "
          f"from high={e['pct_from_high']:.0f}% | "
          f"updown={e['updown_ratio']:.1f}")
