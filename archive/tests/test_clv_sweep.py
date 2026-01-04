#!/usr/bin/env python3
"""
TEST A: SIMPLE ACCUMULATION + CLV THRESHOLD SWEEP
Find optimal CLV threshold
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("SWEEPING CLV THRESHOLDS")
print("=" * 70)

tickers = ['IONQ', 'RGTI', 'QBTS', 'SIDU', 'LUNR', 'RCAT', 'ASTS']

# Test multiple CLV thresholds
clv_thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]

for clv_thresh in clv_thresholds:
    all_signals = []
    
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
        
        for i in range(20, len(close)-10):
            avg_vol = np.mean(volume[i-20:i])
            rel_vol = volume[i] / avg_vol if avg_vol > 0 else 0
            
            price_chg = abs((close[i] - close[i-1]) / close[i-1]) * 100
            
            day_range = high[i] - low[i]
            if day_range > 0:
                clv = (close[i] - low[i]) / day_range
            else:
                clv = 0.5
            
            # SIGNAL: Vol ≥2x, |price| <3%, CLV > threshold
            if rel_vol >= 2.0 and price_chg < 3.0 and clv > clv_thresh:
                entry = close[i]
                exit_10d = close[min(i+10, len(close)-1)]
                ret = ((exit_10d - entry) / entry) * 100
                
                all_signals.append(ret)
    
    if len(all_signals) >= 15:
        rets = np.array(all_signals)
        
        # Quick Monte Carlo
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
        for _ in range(500):  # Faster
            sample = np.random.choice(random_returns, size=len(rets))
            mc_results.append(sample.mean())
        
        mc_results = np.array(mc_results)
        mc_mean = mc_results.mean()
        mc_std = mc_results.std()
        
        p_value = (mc_results >= rets.mean()).mean()
        std_devs = (rets.mean() - mc_mean) / mc_std if mc_std > 0 else 0
        
        win_rate = (rets > 0).mean() * 100
        
        print(f"\nCLV >{clv_thresh:.1f}:")
        print(f"  Signals: {len(rets)}")
        print(f"  WR: {win_rate:.1f}%")
        print(f"  Avg: {rets.mean():+.2f}%")
        print(f"  P-value: {p_value:.4f}")
        print(f"  Effect: {std_devs:.2f}")
        
        if p_value < 0.05:
            print(f"  ✅ SIGNIFICANT!")
    else:
        print(f"\nCLV >{clv_thresh:.1f}: Only {len(all_signals)} signals (too few)")

print("\n" + "=" * 70)
print("OPTIMAL THRESHOLD ANALYSIS COMPLETE")
print("=" * 70)
