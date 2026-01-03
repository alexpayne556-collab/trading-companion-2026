#!/usr/bin/env python3
"""
🐺 HUNT #4: TIMING PATTERN
Is there a rhythm? Do runs happen every X weeks?
After pullbacks of Y%?
"""

import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

print("=" * 70)
print("🐺 HUNT #4: TIMING PATTERN")
print("Looking for rhythms in the repeat runners")
print("=" * 70)

tickers = ['SIDU', 'RGTI', 'QBTS', 'RCAT', 'LUNR', 'ASTS', 'IONQ']

all_runs = []

for ticker in tickers:
    df = yf.download(ticker, start='2024-01-01', progress=False)
    
    if len(df) < 30:
        continue
    
    if isinstance(df['Close'], pd.DataFrame):
        close = df['Close'].iloc[:, 0].values
        high = df['High'].iloc[:, 0].values
    else:
        close = df['Close'].values
        high = df['High'].values
    
    dates = df.index.tolist()
    
    # Find runs
    runs = []
    last_run = -15
    
    for i in range(10, len(close)-10):
        if i - last_run < 10:
            continue
        
        entry = close[i]
        max_gain = max((close[i+j] - entry) / entry * 100 for j in range(1, 11))
        
        if max_gain >= 10:
            # Calculate pullback from prior high
            prior_high = max(high[:i]) if i > 0 else high[0]
            pullback = ((close[i] - prior_high) / prior_high) * 100
            
            runs.append({
                'ticker': ticker,
                'date': dates[i],
                'idx': i,
                'gain': max_gain,
                'pullback': pullback
            })
            last_run = i
    
    # Calculate days between runs
    for j, run in enumerate(runs):
        if j > 0:
            days_since_last = (run['date'] - runs[j-1]['date']).days
            run['days_since_last'] = days_since_last
        else:
            run['days_since_last'] = None
        
        all_runs.append(run)

print(f"Total runs across all tickers: {len(all_runs)}")

# Analyze days between runs
days_between = [r['days_since_last'] for r in all_runs if r['days_since_last'] is not None]
days_between = np.array(days_between)

print(f"\n{'=' * 70}")
print("TIMING BETWEEN RUNS")
print("=" * 70)
print(f"Average days between runs: {days_between.mean():.1f}")
print(f"Median days between runs: {np.median(days_between):.1f}")
print(f"Std dev: {days_between.std():.1f}")

# Distribution
print(f"\nDAYS BETWEEN RUNS DISTRIBUTION:")
for bucket in [(10, 15), (15, 20), (20, 30), (30, 45), (45, 60), (60, 90), (90, 1000)]:
    count = sum(1 for d in days_between if bucket[0] <= d < bucket[1])
    pct = count / len(days_between) * 100
    print(f"  {bucket[0]}-{bucket[1]} days: {count} ({pct:.1f}%)")

# After how much pullback do runs start?
print(f"\n{'=' * 70}")
print("PULLBACK BEFORE RUNS")
print("=" * 70)

pullbacks = [r['pullback'] for r in all_runs]
pullbacks = np.array(pullbacks)

print(f"Average pullback before run: {pullbacks.mean():.1f}%")
print(f"Median pullback: {np.median(pullbacks):.1f}%")

# Distribution
print(f"\nPULLBACK DISTRIBUTION:")
for bucket in [(-10, 0), (-20, -10), (-30, -20), (-40, -30), (-50, -40), (-100, -50)]:
    count = sum(1 for p in pullbacks if bucket[0] <= p < bucket[1])
    pct = count / len(pullbacks) * 100
    print(f"  {bucket[0]}% to {bucket[1]}%: {count} ({pct:.1f}%)")

# CAN WE TRADE THE TIMING?
print(f"\n{'=' * 70}")
print("TESTING: BUY AFTER X DAYS OF NO RUN")
print("=" * 70)

# If stock hasn't run in 20+ days and is down 15%+, is that predictive?
for days_thresh in [15, 20, 25, 30]:
    for pullback_thresh in [-10, -15, -20]:
        signals = []
        
        for ticker in tickers:
            df = yf.download(ticker, start='2024-01-01', progress=False)
            
            if len(df) < 50:
                continue
            
            if isinstance(df['Close'], pd.DataFrame):
                close = df['Close'].iloc[:, 0].values
                high = df['High'].iloc[:, 0].values
            else:
                close = df['Close'].values
                high = df['High'].values
            
            dates = df.index.tolist()
            
            # Find ticker's runs
            ticker_runs = [r for r in all_runs if r['ticker'] == ticker]
            run_dates = set(r['date'] for r in ticker_runs)
            
            for i in range(30, len(close)-10):
                # Check if enough days since last run
                days_since = days_thresh + 1  # Assume long time if no prior run
                for run in ticker_runs:
                    if run['date'] < dates[i]:
                        days = (dates[i] - run['date']).days
                        if days < days_since:
                            days_since = days
                
                if days_since < days_thresh:
                    continue
                
                # Check pullback
                high_30 = max(high[max(0, i-30):i])
                pullback = ((close[i] - high_30) / high_30) * 100
                
                if pullback > pullback_thresh:
                    continue
                
                # Outcome
                entry = close[i]
                exit_10d = close[min(i+10, len(close)-1)]
                ret = ((exit_10d - entry) / entry) * 100
                
                signals.append(ret)
        
        if len(signals) >= 50:
            rets = np.array(signals)
            win_rate = (rets > 0).mean() * 100
            avg_ret = rets.mean()
            hit_10 = (rets >= 10).mean() * 100
            
            status = "🔥" if win_rate > 55 and avg_ret > 10 else ""
            print(f"{days_thresh}+ days, {pullback_thresh}%+ down: {len(signals)} sigs, {win_rate:.0f}% WR, {avg_ret:+.1f}% avg, {hit_10:.0f}% hit 10%+ {status}")

# Day of week analysis
print(f"\n{'=' * 70}")
print("DAY OF WEEK ANALYSIS")
print("=" * 70)

dow_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
dow_names = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri'}

for run in all_runs:
    dow = run['date'].weekday()
    dow_counts[dow] += 1

total = sum(dow_counts.values())
for dow, count in dow_counts.items():
    pct = count / total * 100
    print(f"  {dow_names[dow]}: {count} runs ({pct:.1f}%)")
