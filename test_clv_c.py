#!/usr/bin/env python3
"""
TEST C: VOLUME PRECURSOR + CLV FILTER
Building on what already showed promise (p=0.076)
Adding the missing piece: WHERE does price close?
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("TEST C: VOLUME PRECURSOR + CLV FILTER")
print("=" * 70)

tickers = ['IONQ', 'RGTI', 'QBTS', 'SIDU', 'LUNR', 'RCAT', 'ASTS']

all_signals = []

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
    
    for i in range(20, len(close)-10):
        avg_vol = np.mean(volume[i-20:i])
        rel_vol = volume[i] / avg_vol if avg_vol > 0 else 0
        
        price_chg = abs((close[i] - close[i-1]) / close[i-1]) * 100
        
        # Calculate CLV (Close Location Value)
        day_range = high[i] - low[i]
        if day_range > 0:
            clv = (close[i] - low[i]) / day_range
        else:
            clv = 0.5  # Neutral if no range
        
        # SIGNAL: Vol ≥2x, |price| <3%, CLV >0.6
        if rel_vol >= 2.0 and price_chg < 3.0 and clv > 0.6:
            entry = close[i]
            exit_10d = close[min(i+10, len(close)-1)]
            ret = ((exit_10d - entry) / entry) * 100
            
            all_signals.append({
                'ticker': ticker,
                'date': dates[i].strftime('%Y-%m-%d'),
                'rel_vol': rel_vol,
                'price_chg': price_chg,
                'clv': clv,
                'return_10d': ret
            })

print(f"\n{'=' * 70}")
print(f"SIGNALS WITH CLV FILTER: {len(all_signals)}")
print(f"{'=' * 70}")

if len(all_signals) >= 15:
    rets = np.array([s['return_10d'] for s in all_signals])
    
    win_rate = (rets > 0).mean() * 100
    avg_ret = rets.mean()
    
    print(f"\nSTRATEGY PERFORMANCE:")
    print(f"  Win Rate: {win_rate:.1f}%")
    print(f"  Avg Return (10d): {avg_ret:.2f}%")
    print(f"  Total Signals: {len(rets)}")
    
    # Monte Carlo
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
        sample = np.random.choice(random_returns, size=len(rets))
        mc_results.append(sample.mean())
    
    mc_results = np.array(mc_results)
    mc_mean = mc_results.mean()
    mc_std = mc_results.std()
    
    p_value = (mc_results >= avg_ret).mean()
    std_devs = (avg_ret - mc_mean) / mc_std if mc_std > 0 else 0
    cohens_d = std_devs
    
    print(f"\nRESULTS:")
    print(f"  Strategy: {avg_ret:+.2f}%")
    print(f"  Random: {mc_mean:+.2f}%")
    print(f"  Outperformance: {avg_ret - mc_mean:+.2f}%")
    print(f"  P-value: {p_value:.4f}")
    print(f"  Effect size: {cohens_d:.2f}")
    print(f"  Std devs: {std_devs:.2f}")
    
    print(f"\n{'=' * 70}")
    if p_value < 0.05 and abs(std_devs) > 2.0 and abs(cohens_d) > 0.5:
        print("✅ VERDICT: REAL EDGE DETECTED")
        print("   CLV filter pushed it over the threshold!")
    elif p_value < 0.10:
        print("⚠️  VERDICT: MARGINAL EDGE")
        print(f"   Improvement: Original p=0.076 → CLV filtered p={p_value:.3f}")
    else:
        print("❌ VERDICT: NO EDGE")
    print(f"{'=' * 70}")
    
    # Show top signals
    print(f"\nTOP 10 SIGNALS:")
    sorted_signals = sorted(all_signals, key=lambda x: x['return_10d'], reverse=True)
    for s in sorted_signals[:10]:
        print(f"{s['date']} {s['ticker']}: {s['rel_vol']:.1f}x vol, {s['price_chg']:.1f}% move, CLV={s['clv']:.2f} → {s['return_10d']:+.1f}%")
    
    # Compare to original Volume Precursor (no CLV filter)
    print(f"\n{'=' * 70}")
    print("COMPARISON TO ORIGINAL:")
    print(f"  Original Volume Precursor: 29 signals, p=0.076")
    print(f"  With CLV >0.6 filter: {len(all_signals)} signals, p={p_value:.3f}")
    print(f"  Signal reduction: {((29 - len(all_signals)) / 29 * 100):.1f}%")
else:
    print("Not enough signals")
