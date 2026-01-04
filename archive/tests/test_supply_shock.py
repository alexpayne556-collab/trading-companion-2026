#!/usr/bin/env python3
"""
SUPPLY SHOCK TEST
Short interest * volume spike / float = squeeze potential?
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("INSIGHT #3: SUPPLY SHOCK CALCULATOR")
print("=" * 70)

# Test on known squeezers
test_cases = [
    {'ticker': 'SIDU', 'short_pct': 14.71, 'float_m': 35},
    {'ticker': 'LUNR', 'short_pct': 12.3, 'float_m': 280},
    {'ticker': 'RCAT', 'short_pct': 8.5, 'float_m': 15},
    {'ticker': 'IONQ', 'short_pct': 5.2, 'float_m': 200},
    {'ticker': 'RGTI', 'short_pct': 11.8, 'float_m': 180},
    {'ticker': 'QBTS', 'short_pct': 18.2, 'float_m': 45},
]

signals = []

for case in test_cases:
    ticker = case['ticker']
    print(f"\nTesting {ticker}...")
    
    df = yf.download(ticker, start='2024-01-01', progress=False)
    
    if len(df) < 30:
        continue
    
    if isinstance(df['Close'], pd.DataFrame):
        close = df['Close'].iloc[:, 0].values
        volume = df['Volume'].iloc[:, 0].values
    else:
        close = df['Close'].values
        volume = df['Volume'].values
    
    dates = df.index.tolist()
    
    # Find volume spikes
    for i in range(20, len(close)-5):
        avg_vol = np.mean(volume[i-20:i])
        vol_spike = volume[i] / avg_vol if avg_vol > 0 else 0
        
        if vol_spike >= 3.0:  # 3x+ volume
            # Calculate supply shock score
            float_mult = case['float_m'] / 10  # Normalize to 10M
            shock_score = (case['short_pct'] * vol_spike) / max(float_mult, 0.1)
            
            # Check next 5 days
            entry = close[i]
            exit_5d = close[min(i+5, len(close)-1)]
            ret = ((exit_5d - entry) / entry) * 100
            
            signals.append({
                'ticker': ticker,
                'date': dates[i].strftime('%Y-%m-%d'),
                'shock_score': shock_score,
                'vol_spike': vol_spike,
                'short_pct': case['short_pct'],
                'return_5d': ret
            })

print(f"\n{'=' * 70}")
print(f"TOTAL SIGNALS: {len(signals)}")
print(f"{'=' * 70}")

if len(signals) >= 15:
    # Test: high shock score (>50) vs low (<50)
    high_shock = [s for s in signals if s['shock_score'] > 50]
    low_shock = [s for s in signals if s['shock_score'] <= 50]
    
    if high_shock and low_shock:
        high_rets = np.array([s['return_5d'] for s in high_shock])
        low_rets = np.array([s['return_5d'] for s in low_shock])
        
        print(f"\nHIGH SHOCK SCORE (>50): {len(high_shock)} signals")
        print(f"  Win Rate: {(high_rets > 0).mean() * 100:.1f}%")
        print(f"  Avg Return: {high_rets.mean():.2f}%")
        
        print(f"\nLOW SHOCK SCORE (≤50): {len(low_shock)} signals")
        print(f"  Win Rate: {(low_rets > 0).mean() * 100:.1f}%")
        print(f"  Avg Return: {low_rets.mean():.2f}%")
        
        print(f"\nDIFFERENCE: {high_rets.mean() - low_rets.mean():+.2f}%")
        
        # Statistical test
        from scipy import stats as sp_stats
        t_stat, p_value = sp_stats.ttest_ind(high_rets, low_rets)
        
        print(f"\nT-TEST:")
        print(f"  T-statistic: {t_stat:.2f}")
        print(f"  P-value: {p_value:.4f}")
        
        # Effect size
        pooled_std = np.sqrt((high_rets.std()**2 + low_rets.std()**2) / 2)
        cohens_d = (high_rets.mean() - low_rets.mean()) / pooled_std if pooled_std > 0 else 0
        print(f"  Effect size (Cohen's d): {cohens_d:.2f}")
        
        print(f"\n{'=' * 70}")
        if p_value < 0.05 and abs(cohens_d) > 0.5:
            print("✅ VERDICT: SHOCK SCORE PREDICTS RETURNS")
        elif p_value < 0.10:
            print("⚠️  VERDICT: MARGINAL PREDICTIVE POWER")
        else:
            print("❌ VERDICT: SHOCK SCORE DOESN'T PREDICT")
        print(f"{'=' * 70}")
    
    # Show extreme scores
    print(f"\nTOP 10 BY SHOCK SCORE:")
    sorted_signals = sorted(signals, key=lambda x: x['shock_score'], reverse=True)
    for s in sorted_signals[:10]:
        print(f"{s['date']} {s['ticker']}: Score={s['shock_score']:.1f} ({s['vol_spike']:.1f}x vol, {s['short_pct']:.1f}% SI) → {s['return_5d']:+.1f}%")
else:
    print("Not enough signals for statistical test")
