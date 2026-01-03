#!/usr/bin/env python3
"""
BREAKOUT ENERGY TEST
Failed resistance tests build energy for eventual breakout?
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("INSIGHT #6: BREAKOUT ENERGY SCORE")
print("=" * 70)

tickers = ['IONQ', 'RGTI', 'QBTS', 'SIDU', 'LUNR', 'RCAT']

signals = []

for ticker in tickers:
    print(f"Testing {ticker}...")
    
    df = yf.download(ticker, start='2024-01-01', progress=False)
    
    if len(df) < 60:
        continue
    
    if isinstance(df['Close'], pd.DataFrame):
        close = df['Close'].iloc[:, 0].values
        high = df['High'].iloc[:, 0].values
    else:
        close = df['Close'].values
        high = df['High'].values
    
    dates = df.index.tolist()
    
    # Find resistance levels and test for breakouts
    for i in range(60, len(close)-10):
        # Look back 60 days for resistance
        lookback = high[i-60:i]
        
        # Resistance = 90th percentile of highs
        resistance = np.percentile(lookback, 90)
        
        # Count tests in last 30 days
        recent_highs = high[i-30:i]
        tests = sum(1 for h in recent_highs if abs(h - resistance) / resistance < 0.02)
        
        if tests >= 2:  # At least 2 tests
            # Check if we break resistance today
            if high[i] > resistance * 1.02:  # 2% breakout
                # Calculate energy score
                days_consolidating = 30  # Using 30 day window
                energy_score = tests * 10 + days_consolidating * 0.5
                
                # Check next 10 days
                entry = close[i]
                exit_10d = close[min(i+10, len(close)-1)]
                ret = ((exit_10d - entry) / entry) * 100
                
                signals.append({
                    'ticker': ticker,
                    'date': dates[i].strftime('%Y-%m-%d'),
                    'energy_score': energy_score,
                    'tests': tests,
                    'resistance': resistance,
                    'breakout_price': high[i],
                    'return_10d': ret
                })

print(f"\nBREAKOUT SIGNALS: {len(signals)}")

if len(signals) >= 15:
    # Test: high energy (>40) vs low energy (≤40)
    high_energy = [s for s in signals if s['energy_score'] > 40]
    low_energy = [s for s in signals if s['energy_score'] <= 40]
    
    if high_energy and low_energy:
        high_rets = np.array([s['return_10d'] for s in high_energy])
        low_rets = np.array([s['return_10d'] for s in low_energy])
        
        print(f"\n{'=' * 70}")
        print(f"HIGH ENERGY (>40): {len(high_energy)} signals")
        print(f"  Win Rate: {(high_rets > 0).mean() * 100:.1f}%")
        print(f"  Avg Return: {high_rets.mean():.2f}%")
        
        print(f"\nLOW ENERGY (≤40): {len(low_energy)} signals")
        print(f"  Win Rate: {(low_rets > 0).mean() * 100:.1f}%")
        print(f"  Avg Return: {low_rets.mean():.2f}%")
        
        diff = high_rets.mean() - low_rets.mean()
        print(f"\nDIFFERENCE: {diff:+.2f}%")
        
        from scipy import stats as sp_stats
        t_stat, p_value = sp_stats.ttest_ind(high_rets, low_rets)
        
        pooled_std = np.sqrt((high_rets.std()**2 + low_rets.std()**2) / 2)
        cohens_d = diff / pooled_std if pooled_std > 0 else 0
        
        print(f"\nSTATISTICS:")
        print(f"  P-value: {p_value:.4f}")
        print(f"  Effect size: {cohens_d:.2f}")
        
        print(f"\n{'=' * 70}")
        if p_value < 0.05 and abs(cohens_d) > 0.5:
            print("✅ VERDICT: ENERGY SCORE PREDICTS BREAKOUT SIZE")
        elif p_value < 0.10:
            print("⚠️  VERDICT: MARGINAL PREDICTIVE POWER")
        else:
            print("❌ VERDICT: NO PREDICTIVE POWER")
        print(f"{'=' * 70}")
        
        # Show top signals
        print(f"\nTOP 10 BY ENERGY:")
        sorted_signals = sorted(signals, key=lambda x: x['energy_score'], reverse=True)
        for s in sorted_signals[:10]:
            print(f"{s['date']} {s['ticker']}: Energy={s['energy_score']:.0f} ({s['tests']} tests) → {s['return_10d']:+.1f}%")
    else:
        print("\nAll signals same energy level")
else:
    print("Not enough breakout signals")
