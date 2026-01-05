#!/usr/bin/env python3
"""
WOLF SIGNAL v2 - Stricter version
Vol ratio > 2.5 for higher confidence
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("🐺 THE WOLF SIGNAL v2 (STRICTER)")
print("Volume Ratio > 2.5")
print("=" * 70)

tickers = ['IONQ', 'RGTI', 'QBTS', 'SIDU', 'LUNR', 'RCAT', 'ASTS']

signals = []
all_returns = []

for ticker in tickers:
    print(f"Scanning {ticker}...")
    df = yf.download(ticker, start='2024-01-01', progress=False)
    
    if len(df) < 30:
        continue
    
    if isinstance(df['Close'], pd.DataFrame):
        close = df['Close'].iloc[:, 0].values
        high = df['High'].iloc[:, 0].values
        volume = df['Volume'].iloc[:, 0].values
    else:
        close = df['Close'].values
        high = df['High'].values
        volume = df['Volume'].values
    
    dates = df.index.tolist()
    
    for i in range(len(close)-10):
        ret = ((close[i+10] - close[i]) / close[i]) * 100
        all_returns.append(ret)
    
    for i in range(25, len(close)-10):
        base_vol = np.mean(volume[i-20:i])
        rel_vol = volume[i] / base_vol if base_vol > 0 else 1
        if rel_vol <= 2.0:
            continue
        
        prev_close = close[i-1] if i > 0 else close[i]
        price_chg = abs((close[i] - prev_close) / prev_close * 100)
        if price_chg >= 2:
            continue
        
        up_vol = sum(volume[j] for j in range(i-20, i) if close[j] > close[j-1])
        down_vol = sum(volume[j] for j in range(i-20, i) if close[j] < close[j-1])
        vol_ratio = up_vol / down_vol if down_vol > 0 else 1
        
        # STRICTER: Vol ratio > 2.5
        if vol_ratio <= 2.5:
            continue
        
        high_20 = max(high[i-20:i])
        days_from_high = min(j for j in range(20) if high[i-j-1] == high_20)
        if days_from_high >= 5:
            continue
        
        entry = close[i]
        exit_10d = close[min(i+10, len(close)-1)]
        ret = ((exit_10d - entry) / entry) * 100
        
        signals.append({
            'ticker': ticker,
            'date': dates[i].strftime('%Y-%m-%d'),
            'entry': entry,
            'rel_vol': rel_vol,
            'vol_ratio': vol_ratio,
            'days_from_high': days_from_high,
            'return': ret
        })

print(f"\n{'=' * 70}")
print(f"WOLF SIGNALS v2 FOUND: {len(signals)}")
print(f"{'=' * 70}")

if len(signals) >= 5:
    rets = np.array([s['return'] for s in signals])
    
    win_rate = (rets > 0).mean() * 100
    avg_ret = rets.mean()
    
    print(f"\nPERFORMANCE:")
    print(f"  Win Rate: {win_rate:.1f}%")
    print(f"  Avg Return: {avg_ret:+.2f}%")
    print(f"  Median: {np.median(rets):+.2f}%")
    
    # Monte Carlo
    print(f"\nMONTE CARLO...")
    random_returns = np.array(all_returns)
    
    mc_results = []
    for _ in range(1000):
        sample = np.random.choice(random_returns, size=len(rets))
        mc_results.append(sample.mean())
    
    mc_results = np.array(mc_results)
    mc_mean = mc_results.mean()
    mc_std = mc_results.std()
    
    p_value = (mc_results >= avg_ret).mean()
    effect_size = (avg_ret - mc_mean) / mc_std if mc_std > 0 else 0
    
    print(f"\nRESULTS:")
    print(f"  Strategy: {avg_ret:+.2f}%")
    print(f"  Random: {mc_mean:+.2f}%")
    print(f"  Outperformance: {avg_ret - mc_mean:+.2f}%")
    print(f"  P-value: {p_value:.4f}")
    print(f"  Effect: {effect_size:.2f}")
    
    print(f"\n{'=' * 70}")
    if p_value < 0.05:
        print("✅ CONFIRMED: P < 0.05")
    elif p_value < 0.10:
        print("⚠️  MARGINAL")
    else:
        print("❌ NO EDGE")
    print(f"{'=' * 70}")
    
    print(f"\nALL SIGNALS:")
    for s in sorted(signals, key=lambda x: x['date']):
        win = "✓" if s['return'] > 0 else "✗"
        print(f"  {s['date']} {s['ticker']:5} | ratio={s['vol_ratio']:.1f} | {s['return']:+.1f}% {win}")
