#!/usr/bin/env python3
"""
STACKED v2: Volume Precursor + STRONGER Trend Health
Hunting for p < 0.05
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("STACKED v2: STRONGER TREND HEALTH FILTER")
print("=" * 70)

tickers = ['IONQ', 'RGTI', 'QBTS', 'SIDU', 'LUNR', 'RCAT', 'ASTS']

# Try different vol_ratio thresholds
for vol_thresh in [1.5, 2.0, 2.5]:
    print(f"\n{'=' * 70}")
    print(f"VOL RATIO THRESHOLD: {vol_thresh}")
    print(f"{'=' * 70}")
    
    signals = []
    
    for ticker in tickers:
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
            
            # Trend health 
            up_vol = sum(volume[j] for j in range(i-20, i) if close[j] > close[j-1])
            down_vol = sum(volume[j] for j in range(i-20, i) if close[j] < close[j-1])
            vol_ratio = up_vol / down_vol if down_vol > 0 else 1
            
            # Days since high
            high_20 = max(high[i-20:i])
            days_from_high = min(j for j in range(20) if high[i-j-1] == high_20)
            
            # Volume precursor + stronger trend health
            if rel_vol > 2.0 and price_chg < 2 and vol_ratio > vol_thresh and days_from_high < 5:
                entry = close[i]
                exit_10d = close[min(i+10, len(close)-1)]
                ret = ((exit_10d - entry) / entry) * 100
                
                signals.append({
                    'ticker': ticker,
                    'date': dates[i].strftime('%Y-%m-%d'),
                    'rel_vol': rel_vol,
                    'vol_ratio': vol_ratio,
                    'days_from_high': days_from_high,
                    'return': ret
                })
    
    if len(signals) >= 8:
        rets = np.array([s['return'] for s in signals])
        
        print(f"Signals: {len(signals)}")
        print(f"Win Rate: {(rets > 0).mean() * 100:.1f}%")
        print(f"Avg Return: {rets.mean():+.2f}%")
        
        # Quick MC
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
        
        avg_ret = rets.mean()
        p_value = (mc_results >= avg_ret).mean()
        std_devs = (avg_ret - mc_mean) / mc_std if mc_std > 0 else 0
        
        print(f"P-value: {p_value:.4f}")
        print(f"Effect: {std_devs:.2f}")
        
        if p_value < 0.05:
            print("✅ HIT P < 0.05!")
        elif p_value < 0.10:
            print("⚠️  Marginal")
        else:
            print("❌ No edge")
    else:
        print(f"Only {len(signals)} signals (too few)")
