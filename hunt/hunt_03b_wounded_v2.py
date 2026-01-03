#!/usr/bin/env python3
"""
🐺 HUNT #3b: WOUNDED WOLF v2
Volume spike when DOWN from highs
Looser vol ratio requirement
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("🐺 HUNT #3b: WOUNDED WOLF v2")
print("Volume spike when down 15-40% from highs")
print("=" * 70)

tickers = ['SIDU', 'RGTI', 'QBTS', 'RCAT', 'LUNR', 'ASTS', 'IONQ']

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
        low = df['Low'].iloc[:, 0].values
        volume = df['Volume'].iloc[:, 0].values
    else:
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        volume = df['Volume'].values
    
    dates = df.index.tolist()
    
    # Collect all returns
    for i in range(len(close)-10):
        ret = ((close[i+10] - close[i]) / close[i]) * 100
        all_returns.append(ret)
    
    for i in range(25, len(close)-10):
        # Volume spike
        base_vol = np.mean(volume[i-20:i])
        rel_vol = volume[i] / base_vol if base_vol > 0 else 1
        
        if rel_vol < 1.5:  # At least 1.5x volume
            continue
        
        # Distance from 20-day high
        high_20 = max(high[i-20:i])
        pct_from_high = ((close[i] - high_20) / high_20) * 100
        
        # Target: Down 15-40% (wounded but not dead)
        if not (-40 <= pct_from_high <= -15):
            continue
        
        # CLV on spike day (buyers winning despite downtrend?)
        day_range = high[i] - low[i]
        clv = (close[i] - low[i]) / day_range if day_range > 0 else 0.5
        
        # Price change on spike day
        prev_close = close[i-1] if i > 0 else close[i]
        daily_chg = ((close[i] - prev_close) / prev_close) * 100
        
        # Outcome
        entry = close[i]
        exit_10d = close[min(i+10, len(close)-1)]
        ret = ((exit_10d - entry) / entry) * 100
        
        signals.append({
            'ticker': ticker,
            'date': dates[i].strftime('%Y-%m-%d'),
            'pct_from_high': pct_from_high,
            'rel_vol': rel_vol,
            'clv': clv,
            'daily_chg': daily_chg,
            'return': ret
        })

print(f"\n{'=' * 70}")
print(f"WOUNDED WOLF SIGNALS FOUND: {len(signals)}")
print("(Volume spike when 15-40% down)")
print("=" * 70)

if len(signals) >= 15:
    all_returns = np.array(all_returns)
    
    # Analyze by CLV (high CLV = buyers winning on spike day)
    high_clv = [s for s in signals if s['clv'] > 0.5]
    low_clv = [s for s in signals if s['clv'] <= 0.5]
    
    print(f"\nHIGH CLV (>0.5) - Buyers won on spike day:")
    if len(high_clv) >= 10:
        rets = np.array([s['return'] for s in high_clv])
        print(f"  Signals: {len(rets)}")
        print(f"  Win Rate: {(rets > 0).mean() * 100:.1f}%")
        print(f"  Avg Return: {rets.mean():+.2f}%")
        
        mc_results = [np.random.choice(all_returns, size=len(rets)).mean() for _ in range(1000)]
        mc_results = np.array(mc_results)
        p_value = (mc_results >= rets.mean()).mean()
        effect = (rets.mean() - mc_results.mean()) / mc_results.std()
        
        print(f"  P-value: {p_value:.4f}")
        print(f"  Effect: {effect:.2f}")
        if p_value < 0.05:
            print(f"  ✅ HIT!")
    
    print(f"\nLOW CLV (<=0.5) - Sellers won on spike day:")
    if len(low_clv) >= 10:
        rets = np.array([s['return'] for s in low_clv])
        print(f"  Signals: {len(rets)}")
        print(f"  Win Rate: {(rets > 0).mean() * 100:.1f}%")
        print(f"  Avg Return: {rets.mean():+.2f}%")
        
        mc_results = [np.random.choice(all_returns, size=len(rets)).mean() for _ in range(1000)]
        mc_results = np.array(mc_results)
        p_value = (mc_results >= rets.mean()).mean()
        effect = (rets.mean() - mc_results.mean()) / mc_results.std()
        
        print(f"  P-value: {p_value:.4f}")
        print(f"  Effect: {effect:.2f}")
        if p_value < 0.05:
            print(f"  ✅ HIT!")
    
    # Try green day filter
    print(f"\nGREEN DAY FILTER (daily_chg > 0):")
    green = [s for s in signals if s['daily_chg'] > 0]
    if len(green) >= 10:
        rets = np.array([s['return'] for s in green])
        print(f"  Signals: {len(rets)}")
        print(f"  Win Rate: {(rets > 0).mean() * 100:.1f}%")
        print(f"  Avg Return: {rets.mean():+.2f}%")
        
        mc_results = [np.random.choice(all_returns, size=len(rets)).mean() for _ in range(1000)]
        mc_results = np.array(mc_results)
        p_value = (mc_results >= rets.mean()).mean()
        effect = (rets.mean() - mc_results.mean()) / mc_results.std()
        
        print(f"  P-value: {p_value:.4f}")
        print(f"  Effect: {effect:.2f}")
        if p_value < 0.05:
            print(f"  ✅ HIT!")

# Show best signals
print(f"\n{'=' * 70}")
print("TOP WOUNDED WOLF SIGNALS:")
print("=" * 70)

sorted_signals = sorted(signals, key=lambda x: x['return'], reverse=True)
for s in sorted_signals[:20]:
    win = "✓" if s['return'] > 0 else "✗"
    print(f"{s['date']} {s['ticker']:5} {s['pct_from_high']:+.0f}% | {s['rel_vol']:.1f}x vol | CLV={s['clv']:.2f} | day {s['daily_chg']:+.1f}% | {s['return']:+.1f}% {win}")
