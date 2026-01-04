#!/usr/bin/env python3
"""
STACKED TEST: Best signals combined
- Volume Precursor (p=0.076)
- Plus Trend Health filter (proven edge)
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("STACKED: VOLUME PRECURSOR + TREND HEALTH FILTER")
print("=" * 70)

tickers = ['IONQ', 'RGTI', 'QBTS', 'SIDU', 'LUNR', 'RCAT', 'ASTS']

stacked_signals = []
precursor_only = []

for ticker in tickers:
    print(f"Testing {ticker}...")
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
    
    for i in range(25, len(close)-10):
        # Volume precursor conditions
        base_vol = np.mean(volume[i-20:i])
        rel_vol = volume[i] / base_vol if base_vol > 0 else 1
        
        prev_close = close[i-1] if i > 0 else close[i]
        price_chg = abs((close[i] - prev_close) / prev_close * 100)
        
        # Trend health calculation
        up_vol = sum(volume[j] for j in range(i-20, i) if close[j] > close[j-1])
        down_vol = sum(volume[j] for j in range(i-20, i) if close[j] < close[j-1])
        vol_ratio = up_vol / down_vol if down_vol > 0 else 1
        
        # Days since 20-day high
        high_20 = max(high[i-20:i])
        days_from_high = min(j for j in range(20) if high[i-j-1] == high_20)
        
        # Volume precursor: high vol + flat price
        if rel_vol > 2.0 and price_chg < 2:
            entry = close[i]
            exit_10d = close[min(i+10, len(close)-1)]
            ret = ((exit_10d - entry) / entry) * 100
            
            precursor_only.append(ret)
            
            # STACK: Also require healthy trend
            if vol_ratio > 1.2 and days_from_high < 10:
                stacked_signals.append({
                    'ticker': ticker,
                    'date': dates[i].strftime('%Y-%m-%d'),
                    'rel_vol': rel_vol,
                    'vol_ratio': vol_ratio,
                    'days_from_high': days_from_high,
                    'return': ret
                })

print(f"\n{'=' * 70}")
print(f"Volume Precursor alone: {len(precursor_only)} signals")
print(f"+ Trend Health filter: {len(stacked_signals)} signals")
print(f"{'=' * 70}")

# Compare both
if len(stacked_signals) >= 10:
    stacked_rets = np.array([s['return'] for s in stacked_signals])
    precursor_rets = np.array(precursor_only)
    
    print(f"\nVOLUME PRECURSOR ALONE:")
    print(f"  Win Rate: {(precursor_rets > 0).mean() * 100:.1f}%")
    print(f"  Avg Return: {precursor_rets.mean():+.2f}%")
    
    print(f"\n+ TREND HEALTH FILTER:")
    print(f"  Win Rate: {(stacked_rets > 0).mean() * 100:.1f}%")
    print(f"  Avg Return: {stacked_rets.mean():+.2f}%")
    print(f"  Improvement: {stacked_rets.mean() - precursor_rets.mean():+.2f}%")
    
    # Monte Carlo on stacked
    print(f"\nMONTE CARLO...")
    
    random_returns = []
    for ticker in tickers:
        df = yf.download(ticker, start='2024-01-01', progress=False)
        if isinstance(df['Close'], pd.DataFrame):
            close = df['Close'].iloc[:, 0].values
        else:
            close = df['Close'].values
        
        for i in range(len(close)-10):
            ret = ((close[i+10] - close[i]) / close[i]) * 100
            random_returns.append(ret)
    
    random_returns = np.array(random_returns)
    
    mc_results = []
    for _ in range(1000):
        sample = np.random.choice(random_returns, size=len(stacked_rets))
        mc_results.append(sample.mean())
    
    mc_results = np.array(mc_results)
    mc_mean = mc_results.mean()
    mc_std = mc_results.std()
    
    avg_ret = stacked_rets.mean()
    p_value = (mc_results >= avg_ret).mean()
    std_devs = (avg_ret - mc_mean) / mc_std if mc_std > 0 else 0
    
    print(f"\nRESULTS:")
    print(f"  Stacked Strategy: {avg_ret:+.2f}%")
    print(f"  Random: {mc_mean:+.2f}%")
    print(f"  Outperformance: {avg_ret - mc_mean:+.2f}%")
    print(f"  P-value: {p_value:.4f}")
    print(f"  Effect size: {std_devs:.2f}")
    
    print(f"\n{'=' * 70}")
    if p_value < 0.05:
        print("✅ VERDICT: STACKED SIGNALS HIT P < 0.05!")
    elif p_value < 0.10:
        print("⚠️  VERDICT: MARGINAL EDGE")
    else:
        print("❌ VERDICT: NO EDGE")
    print(f"{'=' * 70}")
    
    # Show best signals
    print(f"\nBEST STACKED SIGNALS:")
    sorted_signals = sorted(stacked_signals, key=lambda x: x['return'], reverse=True)
    for s in sorted_signals[:10]:
        print(f"{s['date']} {s['ticker']}: {s['rel_vol']:.1f}x vol, vol_ratio={s['vol_ratio']:.2f}, {s['days_from_high']}d from high → {s['return']:+.1f}%")
else:
    print(f"Only {len(stacked_signals)} stacked signals (too few)")
