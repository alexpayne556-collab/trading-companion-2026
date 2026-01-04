#!/usr/bin/env python3
"""
TREND HEALTH TEST
Volume ratio (up days vs down days) predicts trend continuation?
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("INSIGHT #7: TREND HEALTH METRIC")
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
        open_p = df['Open'].iloc[:, 0].values
        volume = df['Volume'].iloc[:, 0].values
    else:
        close = df['Close'].values
        open_p = df['Open'].values
        volume = df['Volume'].values
    
    dates = df.index.tolist()
    
    # Calculate trend health over 20-day windows
    for i in range(20, len(close)-10):
        window = slice(i-20, i)
        
        # Volume on up days vs down days
        up_vol = sum(volume[j] for j in range(i-20, i) if close[j] > open_p[j])
        down_vol = sum(volume[j] for j in range(i-20, i) if close[j] < open_p[j])
        
        vol_ratio = up_vol / max(down_vol, 1)
        
        # Days since high
        highs = close[i-20:i]
        days_since_high = len(highs) - np.argmax(highs) - 1
        
        # Time factor
        time_factor = 1 / (1 + days_since_high * 0.1)
        
        health_score = vol_ratio * time_factor
        
        # Check next 10 days
        entry = close[i]
        exit_10d = close[min(i+10, len(close)-1)]
        ret = ((exit_10d - entry) / entry) * 100
        
        signals.append({
            'ticker': ticker,
            'date': dates[i].strftime('%Y-%m-%d'),
            'health_score': health_score,
            'vol_ratio': vol_ratio,
            'days_since_high': days_since_high,
            'return_10d': ret
        })

print(f"\nTOTAL SIGNALS: {len(signals)}")

if len(signals) >= 50:
    # Test: healthy (>1.5) vs exhausted (<0.8)
    healthy = [s for s in signals if s['health_score'] > 1.5]
    exhausted = [s for s in signals if s['health_score'] < 0.8]
    
    if healthy and exhausted:
        healthy_rets = np.array([s['return_10d'] for s in healthy])
        exhausted_rets = np.array([s['return_10d'] for s in exhausted])
        
        print(f"\n{'=' * 70}")
        print(f"HEALTHY TRENDS (score >1.5): {len(healthy)} signals")
        print(f"  Win Rate: {(healthy_rets > 0).mean() * 100:.1f}%")
        print(f"  Avg Return (10d): {healthy_rets.mean():.2f}%")
        
        print(f"\nEXHAUSTED TRENDS (score <0.8): {len(exhausted)} signals")
        print(f"  Win Rate: {(exhausted_rets > 0).mean() * 100:.1f}%")
        print(f"  Avg Return (10d): {exhausted_rets.mean():.2f}%")
        
        diff = healthy_rets.mean() - exhausted_rets.mean()
        print(f"\nDIFFERENCE: {diff:+.2f}%")
        
        # Statistical test
        from scipy import stats as sp_stats
        t_stat, p_value = sp_stats.ttest_ind(healthy_rets, exhausted_rets)
        
        pooled_std = np.sqrt((healthy_rets.std()**2 + exhausted_rets.std()**2) / 2)
        cohens_d = diff / pooled_std if pooled_std > 0 else 0
        
        print(f"\nSTATISTICS:")
        print(f"  T-statistic: {t_stat:.2f}")
        print(f"  P-value: {p_value:.4f}")
        print(f"  Effect size: {cohens_d:.2f}")
        
        print(f"\n{'=' * 70}")
        if p_value < 0.05 and abs(cohens_d) > 0.5:
            print("✅ VERDICT: TREND HEALTH PREDICTS RETURNS")
        elif p_value < 0.10:
            print("⚠️  VERDICT: MARGINAL PREDICTIVE POWER")
        else:
            print("❌ VERDICT: NO PREDICTIVE POWER")
        print(f"{'=' * 70}")
else:
    print("Not enough signals")
