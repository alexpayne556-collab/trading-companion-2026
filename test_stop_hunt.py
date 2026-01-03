#!/usr/bin/env python3
"""
STOP HUNT TEST (Daily Approximation)
Wick below support + recovery = buy signal?
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("INSIGHT #5: STOP HUNT RECOVERY")
print("=" * 70)

tickers = ['IONQ', 'RGTI', 'QBTS', 'SIDU', 'LUNR', 'RCAT', 'ASTS']

signals = []

for ticker in tickers:
    print(f"Testing {ticker}...")
    
    df = yf.download(ticker, start='2024-01-01', progress=False)
    
    if len(df) < 30:
        continue
    
    if isinstance(df['Close'], pd.DataFrame):
        close = df['Close'].iloc[:, 0].values
        low = df['Low'].iloc[:, 0].values
        high = df['High'].iloc[:, 0].values
        volume = df['Volume'].iloc[:, 0].values
    else:
        close = df['Close'].values
        low = df['Low'].values
        high = df['High'].values
        volume = df['Volume'].values
    
    dates = df.index.tolist()
    
    # Find stop hunt patterns
    for i in range(20, len(close)-5):
        # Support = 20-day low
        support = min(close[i-20:i])
        
        # Check for wick below support that recovered
        broke_support = low[i] < support * 0.98  # 2% below
        recovered = close[i] > support  # Closed above
        
        # Volume spike
        avg_vol = np.mean(volume[i-20:i])
        vol_spike = volume[i] / avg_vol if avg_vol > 0 else 0
        
        if broke_support and recovered and vol_spike > 1.5:
            # Stop hunt detected
            entry = close[i]
            exit_5d = close[min(i+5, len(close)-1)]
            ret = ((exit_5d - entry) / entry) * 100
            
            signals.append({
                'ticker': ticker,
                'date': dates[i].strftime('%Y-%m-%d'),
                'support': support,
                'wick_low': low[i],
                'close': close[i],
                'vol_spike': vol_spike,
                'return_5d': ret
            })

print(f"\nSTOP HUNT SIGNALS: {len(signals)}")

if len(signals) >= 15:
    rets = np.array([s['return_5d'] for s in signals])
    
    win_rate = (rets > 0).mean() * 100
    avg_ret = rets.mean()
    
    print(f"\n{'=' * 70}")
    print(f"STRATEGY PERFORMANCE:")
    print(f"  Signals: {len(rets)}")
    print(f"  Win Rate: {win_rate:.1f}%")
    print(f"  Avg Return (5d): {avg_ret:.2f}%")
    
    # Monte Carlo
    print(f"\nMONTE CARLO...")
    
    random_returns = []
    for ticker in tickers:
        df = yf.download(ticker, start='2024-01-01', progress=False)
        if isinstance(df['Close'], pd.DataFrame):
            close = df['Close'].iloc[:, 0].values
        else:
            close = df['Close'].values
        
        for i in range(len(close)-5):
            ret = ((close[i+5] - close[i]) / close[i]) * 100
            random_returns.append(ret)
    
    random_returns = np.array(random_returns)
    
    mc_results = []
    for _ in range(1000):
        sample = np.random.choice(random_returns, size=len(rets))
        mc_results.append(sample.mean())
    
    mc_results = np.array(mc_results)
    mc_mean = mc_results.mean()
    mc_std = mc_results.std()
    
    p_value = (mc_results >= avg_ret).mean()
    std_devs = (avg_ret - mc_mean) / mc_std if mc_std > 0 else 0
    
    print(f"\nRESULTS:")
    print(f"  Strategy: {avg_ret:+.2f}%")
    print(f"  Random: {mc_mean:+.2f}%")
    print(f"  Outperformance: {avg_ret - mc_mean:+.2f}%")
    print(f"  P-value: {p_value:.4f}")
    print(f"  Std devs: {std_devs:.2f}")
    
    print(f"\n{'=' * 70}")
    if p_value < 0.05 and abs(std_devs) > 2.0:
        print("✅ VERDICT: REAL EDGE")
    elif p_value < 0.10:
        print("⚠️  VERDICT: MARGINAL EDGE")
    else:
        print("❌ VERDICT: NO EDGE")
    print(f"{'=' * 70}")
    
    # Show best signals
    print(f"\nTOP 10 STOP HUNTS:")
    sorted_signals = sorted(signals, key=lambda x: x['return_5d'], reverse=True)
    for s in sorted_signals[:10]:
        pct_below = ((s['support'] - s['wick_low']) / s['support']) * 100
        print(f"{s['date']} {s['ticker']}: {pct_below:.1f}% below support ({s['vol_spike']:.1f}x vol) → {s['return_5d']:+.1f}%")
else:
    print("Not enough signals")
