#!/usr/bin/env python3
"""
🐺 HUNT #3c: CAPITULATION HUNTER
Volume spike + RED day + DOWN from highs = BUY SIGNAL
This is counterintuitive but p=0.003!
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("🐺 CAPITULATION HUNTER")
print("Buy the red spike when wounded")
print("This is the sellers giving up!")
print("=" * 70)

tickers = ['SIDU', 'RGTI', 'QBTS', 'RCAT', 'LUNR', 'ASTS', 'IONQ']

capitulation = []  # Low CLV wounded signals
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
    
    for i in range(len(close)-10):
        ret = ((close[i+10] - close[i]) / close[i]) * 100
        all_returns.append(ret)
    
    for i in range(25, len(close)-10):
        # Volume spike > 1.5x
        base_vol = np.mean(volume[i-20:i])
        rel_vol = volume[i] / base_vol if base_vol > 0 else 1
        
        if rel_vol < 1.5:
            continue
        
        # Distance from 20-day high (15-40% down)
        high_20 = max(high[i-20:i])
        pct_from_high = ((close[i] - high_20) / high_20) * 100
        
        if not (-40 <= pct_from_high <= -15):
            continue
        
        # CLV <= 0.5 (sellers won = red day)
        day_range = high[i] - low[i]
        clv = (close[i] - low[i]) / day_range if day_range > 0 else 0.5
        
        if clv > 0.5:
            continue
        
        # Daily change (expecting red)
        prev_close = close[i-1]
        daily_chg = ((close[i] - prev_close) / prev_close) * 100
        
        # Outcome
        entry = close[i]
        exit_10d = close[min(i+10, len(close)-1)]
        ret = ((exit_10d - entry) / entry) * 100
        
        capitulation.append({
            'ticker': ticker,
            'date': dates[i].strftime('%Y-%m-%d'),
            'pct_from_high': pct_from_high,
            'rel_vol': rel_vol,
            'clv': clv,
            'daily_chg': daily_chg,
            'return': ret
        })

print(f"\n{'=' * 70}")
print(f"CAPITULATION SIGNALS: {len(capitulation)}")
print("=" * 70)

all_returns = np.array(all_returns)
rets = np.array([s['return'] for s in capitulation])

print(f"\nPERFORMANCE:")
print(f"  Signals: {len(rets)}")
print(f"  Win Rate: {(rets > 0).mean() * 100:.1f}%")
print(f"  Avg Return: {rets.mean():+.2f}%")
print(f"  Median: {np.median(rets):+.2f}%")
print(f"  Hit 20%+: {(rets >= 20).mean() * 100:.1f}%")

# Monte Carlo
print(f"\nMONTE CARLO...")
mc_results = []
for _ in range(1000):
    sample = np.random.choice(all_returns, size=len(rets))
    mc_results.append(sample.mean())

mc_results = np.array(mc_results)
mc_mean = mc_results.mean()
mc_std = mc_results.std()

avg_ret = rets.mean()
p_value = (mc_results >= avg_ret).mean()
effect = (avg_ret - mc_mean) / mc_std

print(f"\nSTATISTICAL VALIDATION:")
print(f"  Strategy: {avg_ret:+.2f}%")
print(f"  Random: {mc_mean:+.2f}%")
print(f"  Outperformance: {avg_ret - mc_mean:+.2f}%")
print(f"  P-value: {p_value:.4f}")
print(f"  Effect: {effect:.2f}")

print(f"\n{'=' * 70}")
if p_value < 0.05:
    print("✅ CAPITULATION HUNTER CONFIRMED!")
    print(f"   When stock is wounded (15-40% down)")
    print(f"   And has a big RED spike (CLV < 0.5, 1.5x volume)")
    print(f"   That's sellers giving up. BUY IT.")
else:
    print("❌ No edge")
print(f"{'=' * 70}")

# Deeper cut: what if even redder (CLV < 0.3)?
print(f"\n{'=' * 70}")
print("DEEPER CUT: CLV < 0.3 (VERY red day)")
print("=" * 70)

very_red = [s for s in capitulation if s['clv'] < 0.3]
if len(very_red) >= 10:
    vr_rets = np.array([s['return'] for s in very_red])
    print(f"Signals: {len(vr_rets)}")
    print(f"Win Rate: {(vr_rets > 0).mean() * 100:.1f}%")
    print(f"Avg Return: {vr_rets.mean():+.2f}%")
    
    mc_results = [np.random.choice(all_returns, size=len(vr_rets)).mean() for _ in range(1000)]
    mc_results = np.array(mc_results)
    p_value = (mc_results >= vr_rets.mean()).mean()
    effect = (vr_rets.mean() - np.mean(mc_results)) / np.std(mc_results)
    
    print(f"P-value: {p_value:.4f}")
    print(f"Effect: {effect:.2f}")
    if p_value < 0.05:
        print("✅ VERY RED = EVEN BETTER!")

# Show all signals
print(f"\n{'=' * 70}")
print("ALL CAPITULATION SIGNALS:")
print("=" * 70)

sorted_cap = sorted(capitulation, key=lambda x: x['return'], reverse=True)
for s in sorted_cap:
    win = "✓" if s['return'] > 0 else "✗"
    print(f"{s['date']} {s['ticker']:5} {s['pct_from_high']:+.0f}% | {s['rel_vol']:.1f}x | CLV={s['clv']:.2f} | day {s['daily_chg']:+.1f}% | {s['return']:+.1f}% {win}")
