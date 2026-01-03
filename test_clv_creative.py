#!/usr/bin/env python3
"""
CREATIVE PIVOT: CLV on VOLUME SPIKES (no price restriction)
Testing if CLV predicts direction on volume days
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("CREATIVE TEST: CLV PREDICTS VOLUME SPIKE OUTCOMES")
print("=" * 70)

tickers = ['IONQ', 'RGTI', 'QBTS', 'SIDU', 'LUNR', 'RCAT', 'ASTS']

high_clv_signals = []
low_clv_signals = []

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
        
        # ANY volume spike ≥2x
        if rel_vol >= 2.0:
            day_range = high[i] - low[i]
            if day_range > 0:
                clv = (close[i] - low[i]) / day_range
            else:
                clv = 0.5
            
            entry = close[i]
            exit_10d = close[min(i+10, len(close)-1)]
            ret = ((exit_10d - entry) / entry) * 100
            
            # Split by CLV
            if clv > 0.6:  # Buyers won
                high_clv_signals.append({
                    'ticker': ticker,
                    'date': dates[i].strftime('%Y-%m-%d'),
                    'clv': clv,
                    'rel_vol': rel_vol,
                    'return': ret
                })
            elif clv < 0.4:  # Sellers won
                low_clv_signals.append({
                    'ticker': ticker,
                    'date': dates[i].strftime('%Y-%m-%d'),
                    'clv': clv,
                    'rel_vol': rel_vol,
                    'return': ret
                })

print(f"\n{'=' * 70}")
print(f"HIGH CLV (>0.6) - Buyers won: {len(high_clv_signals)}")
print(f"LOW CLV (<0.4) - Sellers won: {len(low_clv_signals)}")
print(f"{'=' * 70}")

if high_clv_signals and low_clv_signals:
    high_rets = np.array([s['return'] for s in high_clv_signals])
    low_rets = np.array([s['return'] for s in low_clv_signals])
    
    print(f"\nHIGH CLV (Buyers Won):")
    print(f"  Signals: {len(high_rets)}")
    print(f"  Win Rate: {(high_rets > 0).mean() * 100:.1f}%")
    print(f"  Avg Return: {high_rets.mean():+.2f}%")
    print(f"  Median: {np.median(high_rets):+.2f}%")
    
    print(f"\nLOW CLV (Sellers Won):")
    print(f"  Signals: {len(low_rets)}")
    print(f"  Win Rate: {(low_rets > 0).mean() * 100:.1f}%")
    print(f"  Avg Return: {low_rets.mean():+.2f}%")
    print(f"  Median: {np.median(low_rets):+.2f}%")
    
    diff = high_rets.mean() - low_rets.mean()
    print(f"\nDIFFERENCE: {diff:+.2f}%")
    
    # Statistical test
    from scipy import stats as sp_stats
    t_stat, p_value = sp_stats.ttest_ind(high_rets, low_rets)
    
    pooled_std = np.sqrt((high_rets.std()**2 + low_rets.std()**2) / 2)
    cohens_d = diff / pooled_std if pooled_std > 0 else 0
    
    print(f"\nSTATISTICS:")
    print(f"  T-statistic: {t_stat:.2f}")
    print(f"  P-value: {p_value:.4f}")
    print(f"  Effect size: {cohens_d:.2f}")
    
    print(f"\n{'=' * 70}")
    if p_value < 0.05 and abs(cohens_d) > 0.5:
        print("✅ VERDICT: CLV PREDICTS DIRECTION ON VOLUME SPIKES")
        print("   HIGH CLV = BUY, LOW CLV = AVOID/SHORT")
    elif p_value < 0.10:
        print("⚠️  VERDICT: MARGINAL PREDICTIVE POWER")
    else:
        print("❌ VERDICT: CLV DOESN'T PREDICT")
    print(f"{'=' * 70}")
    
    # Show top high CLV signals
    print(f"\nTOP 10 HIGH CLV SIGNALS:")
    sorted_high = sorted(high_clv_signals, key=lambda x: x['return'], reverse=True)
    for s in sorted_high[:10]:
        print(f"{s['date']} {s['ticker']}: CLV={s['clv']:.2f}, {s['rel_vol']:.1f}x vol → {s['return']:+.1f}%")
else:
    print("Not enough signals in one category")
