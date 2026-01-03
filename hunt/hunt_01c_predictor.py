#!/usr/bin/env python3
"""
🐺 HUNT #1c: BUILD THE PREDICTOR
Use the 5 significant signatures to predict runs
Monte Carlo validate
"""

import yfinance as yf
import numpy as np
import pandas as pd
from scipy import stats

print("=" * 70)
print("🐺 BUILDING THE PRE-RUN PREDICTOR")
print("Using 5 significant signatures")
print("=" * 70)

tickers = ['SIDU', 'RGTI', 'QBTS', 'RCAT', 'LUNR', 'ASTS', 'IONQ']

# THRESHOLDS (based on the pre-run averages)
# - 5d volume ratio > 1.0 (vs 0.82 normal)
# - Day volume > 1.0 (vs 0.73 normal)
# - 5d price > -2% (vs -4.46 normal)  
# - 5d CLV > 0.45 (vs 0.42 normal)
# - Up/down ratio > 1.2 (vs 1.11 normal)

all_signals = []
all_returns = []

for ticker in tickers:
    print(f"Scanning {ticker}...")
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
    
    # Collect all 10d returns for Monte Carlo
    for i in range(len(close)-10):
        ret = ((close[i+10] - close[i]) / close[i]) * 100
        all_returns.append(ret)
    
    for i in range(25, len(close)-10):
        # Calculate the 5 signatures
        base_vol = np.mean(volume[i-20:i-5])
        
        # 1. 5-day volume ratio
        prerun_vol = np.mean(volume[i-5:i])
        vol_ratio_prerun = prerun_vol / base_vol if base_vol > 0 else 1
        
        # 2. Signal day volume
        day_vol_ratio = volume[i] / base_vol if base_vol > 0 else 1
        
        # 3. 5-day price change
        price_5d = ((close[i] - close[i-5]) / close[i-5]) * 100
        
        # 4. 5-day CLV
        clvs = []
        for k in range(i-5, i):
            day_range = high[k] - low[k]
            if day_range > 0:
                clvs.append((close[k] - low[k]) / day_range)
            else:
                clvs.append(0.5)
        avg_clv = np.mean(clvs)
        
        # 5. Up/down volume ratio
        up_vol = sum(volume[k] for k in range(i-20, i) if close[k] > close[k-1])
        down_vol = sum(volume[k] for k in range(i-20, i) if close[k] < close[k-1])
        updown_ratio = up_vol / down_vol if down_vol > 0 else 1
        
        # COUNT how many criteria met
        score = 0
        if vol_ratio_prerun > 1.0:
            score += 1
        if day_vol_ratio > 1.0:
            score += 1
        if price_5d > -2:
            score += 1
        if avg_clv > 0.45:
            score += 1
        if updown_ratio > 1.2:
            score += 1
        
        # Outcome
        entry = close[i]
        exit_10d = close[min(i+10, len(close)-1)]
        ret = ((exit_10d - entry) / entry) * 100
        
        all_signals.append({
            'ticker': ticker,
            'date': dates[i].strftime('%Y-%m-%d'),
            'score': score,
            'return': ret,
            'vol_prerun': vol_ratio_prerun,
            'day_vol': day_vol_ratio,
            'price_5d': price_5d,
            'clv': avg_clv,
            'updown': updown_ratio
        })

# Analyze by score
print(f"\n{'=' * 70}")
print("RESULTS BY SCORE (out of 5)")
print("=" * 70)

all_returns = np.array(all_returns)

for score in range(6):
    signals = [s for s in all_signals if s['score'] == score]
    if len(signals) >= 10:
        rets = np.array([s['return'] for s in signals])
        win_rate = (rets > 0).mean() * 100
        avg_ret = rets.mean()
        hit_10 = (rets >= 10).mean() * 100  # % that hit 10%+
        
        print(f"\nScore {score}/5: {len(signals)} signals")
        print(f"  Win Rate: {win_rate:.1f}%")
        print(f"  Avg Return: {avg_ret:+.2f}%")
        print(f"  Hit 10%+: {hit_10:.1f}%")

# Focus on high scores
print(f"\n{'=' * 70}")
print("TESTING SCORE >= 4 (4 or 5 criteria met)")
print("=" * 70)

high_score_signals = [s for s in all_signals if s['score'] >= 4]
high_rets = np.array([s['return'] for s in high_score_signals])

print(f"\nSignals: {len(high_score_signals)}")
print(f"Win Rate: {(high_rets > 0).mean() * 100:.1f}%")
print(f"Avg Return: {high_rets.mean():+.2f}%")
print(f"Hit 10%+: {(high_rets >= 10).mean() * 100:.1f}%")

# Monte Carlo
print(f"\nMONTE CARLO (1000 simulations)...")

mc_results = []
for _ in range(1000):
    sample = np.random.choice(all_returns, size=len(high_rets))
    mc_results.append(sample.mean())

mc_results = np.array(mc_results)
mc_mean = mc_results.mean()
mc_std = mc_results.std()

avg_ret = high_rets.mean()
p_value = (mc_results >= avg_ret).mean()
effect_size = (avg_ret - mc_mean) / mc_std if mc_std > 0 else 0

print(f"\nSTATISTICAL VALIDATION:")
print(f"  Strategy: {avg_ret:+.2f}%")
print(f"  Random: {mc_mean:+.2f}%")
print(f"  Outperformance: {avg_ret - mc_mean:+.2f}%")
print(f"  P-value: {p_value:.4f}")
print(f"  Effect: {effect_size:.2f}")

print(f"\n{'=' * 70}")
if p_value < 0.05:
    print("✅ PRE-RUN PREDICTOR HIT P < 0.05!")
elif p_value < 0.10:
    print("⚠️  MARGINAL")
else:
    print("❌ NO EDGE")
print(f"{'=' * 70}")

# Perfect score signals
print(f"\n{'=' * 70}")
print("PERFECT SCORE (5/5) SIGNALS:")
print("=" * 70)

perfect = [s for s in all_signals if s['score'] == 5]
perfect = sorted(perfect, key=lambda x: x['return'], reverse=True)

for s in perfect[:15]:
    win = "✓" if s['return'] > 0 else "✗"
    print(f"{s['date']} {s['ticker']:5} | {s['return']:+.1f}% {win}")

if len(perfect) >= 5:
    perf_rets = np.array([s['return'] for s in perfect])
    print(f"\nPerfect score: {len(perfect)} signals, {(perf_rets > 0).mean()*100:.0f}% WR, {perf_rets.mean():+.1f}% avg")
