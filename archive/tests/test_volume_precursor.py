#!/usr/bin/env python3
"""
VOLUME PRECURSOR TEST
High volume + low price move = accumulation before breakout?
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("INSIGHT #2: VOLUME PRECURSOR SCANNER")
print("=" * 70)

# Test on quantum stocks (high volatility, proven runners)
tickers = ['IONQ', 'RGTI', 'QBTS', 'SIDU', 'LUNR']

all_signals = []

for ticker in tickers:
    print(f"\nTesting {ticker}...")
    df = yf.download(ticker, start='2024-01-01', progress=False)
    
    if len(df) < 30:
        continue
    
    # Handle multi-column structure
    if isinstance(df['Close'], pd.DataFrame):
        close = df['Close'].iloc[:, 0].values
        volume = df['Volume'].iloc[:, 0].values
    else:
        close = df['Close'].values
        volume = df['Volume'].values
    
    dates = df.index.tolist()
    
    # Calculate 20-day average volume
    for i in range(20, len(close)-10):
        avg_vol = np.mean(volume[i-20:i])
        rel_vol = volume[i] / avg_vol if avg_vol > 0 else 0
        
        price_chg = abs((close[i] - close[i-1]) / close[i-1]) * 100
        
        # Signal: 2x volume but <3% price move
        if rel_vol >= 2.0 and price_chg < 3.0:
            # Check next 10 days
            entry = close[i]
            exit_10d = close[min(i+10, len(close)-1)]
            ret = ((exit_10d - entry) / entry) * 100
            
            all_signals.append({
                'ticker': ticker,
                'date': dates[i].strftime('%Y-%m-%d'),
                'rel_vol': rel_vol,
                'price_chg': price_chg,
                'return_10d': ret
            })

print(f"\n{'=' * 70}")
print(f"TOTAL SIGNALS: {len(all_signals)}")
print(f"{'=' * 70}")

if len(all_signals) >= 15:
    rets = np.array([s['return_10d'] for s in all_signals])
    
    win_rate = (rets > 0).mean() * 100
    avg_ret = rets.mean()
    
    print(f"\nSTRATEGY PERFORMANCE:")
    print(f"  Win Rate: {win_rate:.1f}%")
    print(f"  Avg Return (10d): {avg_ret:.2f}%")
    print(f"  Total Signals: {len(rets)}")
    
    # Monte Carlo vs random entries
    print(f"\nMONTE CARLO TEST...")
    
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
    
    # Run 1000 Monte Carlo simulations
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
    print(f"  Random baseline: {mc_mean:+.2f}%")
    print(f"  Outperformance: {avg_ret - mc_mean:+.2f}%")
    print(f"  P-value: {p_value:.4f}")
    print(f"  Effect size (Cohen's d): {cohens_d:.2f}")
    print(f"  Std devs above random: {std_devs:.2f}")
    
    print(f"\n{'=' * 70}")
    if p_value < 0.05 and abs(std_devs) > 2.0 and abs(cohens_d) > 0.5:
        print("✅ VERDICT: REAL EDGE DETECTED")
    elif p_value < 0.10:
        print("⚠️  VERDICT: MARGINAL EDGE")
    else:
        print("❌ VERDICT: NO STATISTICAL EDGE")
    print(f"{'=' * 70}")
    
    # Show top signals
    print(f"\nTOP 10 SIGNALS BY RETURN:")
    sorted_signals = sorted(all_signals, key=lambda x: x['return_10d'], reverse=True)
    for s in sorted_signals[:10]:
        print(f"{s['date']} {s['ticker']}: {s['rel_vol']:.1f}x vol, {s['price_chg']:.1f}% move → {s['return_10d']:+.1f}% (10d)")
else:
    print("Not enough signals for statistical test")
