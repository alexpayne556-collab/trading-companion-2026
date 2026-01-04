#!/usr/bin/env python3
"""
🐺 HUNT #1b: PRE-RUN SIGNATURE (REFINED)
Find the FIRST day of each distinct 10%+ run, not every day in it
"""

import yfinance as yf
import numpy as np
import pandas as pd
from scipy import stats

print("=" * 70)
print("🐺 HUNT #1b: PRE-RUN SIGNATURE (DISTINCT RUNS)")
print("Finding the START of each explosion")
print("=" * 70)

tickers = ['SIDU', 'RGTI', 'QBTS', 'RCAT', 'LUNR', 'ASTS', 'IONQ']

all_run_starts = []
all_normal = []

for ticker in tickers:
    print(f"\nHunting {ticker}...")
    df = yf.download(ticker, start='2024-01-01', progress=False)
    
    if len(df) < 30:
        continue
    
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
    
    # Find DISTINCT runs (at least 10 days apart)
    run_starts = []
    last_run = -30  # Start far back
    
    for i in range(25, len(close)-10):
        # Skip if too close to last run
        if i - last_run < 10:
            continue
        
        # Check for 10%+ move in next 10 days
        max_gain = 0
        peak_day = i
        for j in range(1, 11):
            if i + j < len(close):
                gain = ((close[i+j] - close[i]) / close[i]) * 100
                if gain > max_gain:
                    max_gain = gain
                    peak_day = i + j
        
        if max_gain >= 10:
            last_run = i
            
            # Calculate pre-run characteristics
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
            
            # Day before CLV (more specific)
            day_range = high[i-1] - low[i-1]
            day_before_clv = (close[i-1] - low[i-1]) / day_range if day_range > 0 else 0.5
            
            high_20 = max(high[i-20:i])
            pct_from_high = ((close[i] - high_20) / high_20) * 100
            
            up_vol = sum(volume[k] for k in range(i-20, i) if close[k] > close[k-1])
            down_vol = sum(volume[k] for k in range(i-20, i) if close[k] < close[k-1])
            updown_ratio = up_vol / down_vol if down_vol > 0 else 1
            
            # Consecutive down days before
            down_days = 0
            for k in range(i-1, max(i-10, 0), -1):
                if close[k] < close[k-1]:
                    down_days += 1
                else:
                    break
            
            # RSI proxy (up moves / total moves)
            ups = sum(1 for k in range(i-14, i) if close[k] > close[k-1])
            rsi_proxy = (ups / 14) * 100
            
            run_starts.append({
                'ticker': ticker,
                'date': dates[i].strftime('%Y-%m-%d'),
                'max_gain': max_gain,
                'vol_ratio_prerun': vol_ratio_prerun,
                'day_vol_ratio': day_vol_ratio,
                'price_5d': price_5d,
                'avg_clv': avg_clv,
                'day_before_clv': day_before_clv,
                'pct_from_high': pct_from_high,
                'updown_ratio': updown_ratio,
                'down_days_before': down_days,
                'rsi_proxy': rsi_proxy
            })
            all_run_starts.append(run_starts[-1])
    
    print(f"  Found {len(run_starts)} distinct runs")
    
    # Collect normal days (not near any run)
    for i in range(25, len(close)-10):
        is_near_run = False
        for rs in run_starts:
            run_date = dates.index(pd.Timestamp(rs['date']))
            if abs(i - run_date) < 15:
                is_near_run = True
                break
        
        if not is_near_run:
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
            
            day_range = high[i-1] - low[i-1]
            day_before_clv = (close[i-1] - low[i-1]) / day_range if day_range > 0 else 0.5
            
            high_20 = max(high[i-20:i])
            pct_from_high = ((close[i] - high_20) / high_20) * 100
            
            up_vol = sum(volume[k] for k in range(i-20, i) if close[k] > close[k-1])
            down_vol = sum(volume[k] for k in range(i-20, i) if close[k] < close[k-1])
            updown_ratio = up_vol / down_vol if down_vol > 0 else 1
            
            down_days = 0
            for k in range(i-1, max(i-10, 0), -1):
                if close[k] < close[k-1]:
                    down_days += 1
                else:
                    break
            
            ups = sum(1 for k in range(i-14, i) if close[k] > close[k-1])
            rsi_proxy = (ups / 14) * 100
            
            all_normal.append({
                'vol_ratio_prerun': vol_ratio_prerun,
                'day_vol_ratio': day_vol_ratio,
                'price_5d': price_5d,
                'avg_clv': avg_clv,
                'day_before_clv': day_before_clv,
                'pct_from_high': pct_from_high,
                'updown_ratio': updown_ratio,
                'down_days_before': down_days,
                'rsi_proxy': rsi_proxy
            })

print(f"\n{'=' * 70}")
print(f"DISTINCT RUN STARTS: {len(all_run_starts)}")
print(f"NORMAL DAYS: {len(all_normal)}")
print(f"{'=' * 70}")

# ANALYZE
print("\n" + "=" * 70)
print("PRE-RUN SIGNATURE ANALYSIS")
print("=" * 70)

metrics = ['vol_ratio_prerun', 'day_vol_ratio', 'price_5d', 'avg_clv', 
           'day_before_clv', 'pct_from_high', 'updown_ratio', 
           'down_days_before', 'rsi_proxy']

print(f"\n{'Metric':<20} {'Pre-Run':<12} {'Normal':<12} {'Diff':<10} {'P-value':<10}")
print("-" * 70)

significant = []

for metric in metrics:
    exp_vals = [e[metric] for e in all_run_starts]
    norm_vals = [n[metric] for n in all_normal]
    
    exp_mean = np.mean(exp_vals)
    norm_mean = np.mean(norm_vals)
    diff = exp_mean - norm_mean
    
    t_stat, p_val = stats.ttest_ind(exp_vals, norm_vals)
    
    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
    
    print(f"{metric:<20} {exp_mean:<12.2f} {norm_mean:<12.2f} {diff:<+10.2f} {p_val:<10.4f} {sig}")
    
    if p_val < 0.05:
        significant.append((metric, exp_mean, norm_mean, p_val, diff))

print(f"\n{'=' * 70}")
print("🎯 SIGNIFICANT SIGNATURES:")
print("=" * 70)

for metric, exp, norm, p, diff in significant:
    direction = "HIGHER" if diff > 0 else "LOWER"
    print(f"  • {metric}: {exp:.2f} vs {norm:.2f} ({direction} before runs, p={p:.4f})")

# Show the runs
print(f"\n{'=' * 70}")
print("ALL DISTINCT RUNS:")
print("=" * 70)

sorted_runs = sorted(all_run_starts, key=lambda x: x['max_gain'], reverse=True)
for r in sorted_runs[:25]:
    print(f"{r['date']} {r['ticker']:5} +{r['max_gain']:.0f}% | "
          f"5d vol={r['vol_ratio_prerun']:.1f}x | "
          f"CLV(yday)={r['day_before_clv']:.2f} | "
          f"high={r['pct_from_high']:.0f}% | "
          f"down days={r['down_days_before']}")
