#!/usr/bin/env python3
"""
TEST 3: DIVERGENT ACCUMULATION
Price looks weak but CLV shows buyers winning over 5 days
This is the "smart money loading" signature
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("TEST 3: DIVERGENT ACCUMULATION")
print("Price looks weak, but buyers keep winning")
print("=" * 70)

tickers = ['IONQ', 'RGTI', 'QBTS', 'SIDU', 'LUNR', 'RCAT', 'ASTS']

divergent_signals = []
normal_signals = []

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
        # 5-day window analysis
        window = slice(i-5, i)
        
        # Price change over 5 days
        price_5d = ((close[i] - close[i-5]) / close[i-5]) * 100
        
        # Average CLV over 5 days
        clvs = []
        for j in range(i-5, i):
            day_range = high[j] - low[j]
            if day_range > 0:
                clvs.append((close[j] - low[j]) / day_range)
            else:
                clvs.append(0.5)
        avg_clv = np.mean(clvs)
        
        # Average relative volume
        base_vol = np.mean(volume[i-25:i-5])
        window_vol = np.mean(volume[i-5:i])
        rel_vol = window_vol / base_vol if base_vol > 0 else 1
        
        # Check outcome
        entry = close[i]
        exit_10d = close[min(i+10, len(close)-1)]
        ret = ((exit_10d - entry) / entry) * 100
        
        # DIVERGENT: Price flat/down but buyers winning
        if -5 <= price_5d <= 2 and avg_clv > 0.55 and rel_vol > 1.3:
            divergent_signals.append({
                'ticker': ticker,
                'date': dates[i].strftime('%Y-%m-%d'),
                'price_5d': price_5d,
                'avg_clv': avg_clv,
                'rel_vol': rel_vol,
                'return': ret
            })
        # NORMAL: Price up and buyers winning (expected)
        elif price_5d > 2 and avg_clv > 0.55:
            normal_signals.append({
                'ticker': ticker,
                'date': dates[i].strftime('%Y-%m-%d'),
                'price_5d': price_5d,
                'avg_clv': avg_clv,
                'rel_vol': rel_vol,
                'return': ret
            })

print(f"\n{'=' * 70}")
print(f"DIVERGENT (Price weak, buyers winning): {len(divergent_signals)}")
print(f"NORMAL (Price up, buyers winning): {len(normal_signals)}")
print(f"{'=' * 70}")

if len(divergent_signals) >= 15:
    div_rets = np.array([s['return'] for s in divergent_signals])
    
    win_rate = (div_rets > 0).mean() * 100
    avg_ret = div_rets.mean()
    
    print(f"\nDIVERGENT ACCUMULATION SIGNALS:")
    print(f"  Signals: {len(div_rets)}")
    print(f"  Win Rate: {win_rate:.1f}%")
    print(f"  Avg Return: {avg_ret:+.2f}%")
    print(f"  Median: {np.median(div_rets):+.2f}%")
    
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
        sample = np.random.choice(random_returns, size=len(div_rets))
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
    print(f"  Effect size: {std_devs:.2f}")
    
    print(f"\n{'=' * 70}")
    if p_value < 0.05 and abs(std_devs) > 2.0:
        print("✅ VERDICT: DIVERGENT ACCUMULATION IS REAL EDGE")
    elif p_value < 0.10:
        print("⚠️  VERDICT: MARGINAL EDGE")
    else:
        print("❌ VERDICT: NO EDGE")
    print(f"{'=' * 70}")
    
    # Show top signals
    print(f"\nTOP 10 DIVERGENT SIGNALS:")
    sorted_signals = sorted(divergent_signals, key=lambda x: x['return'], reverse=True)
    for s in sorted_signals[:10]:
        print(f"{s['date']} {s['ticker']}: 5d price {s['price_5d']:+.1f}%, CLV={s['avg_clv']:.2f}, {s['rel_vol']:.1f}x vol → {s['return']:+.1f}%")
else:
    print(f"Only {len(divergent_signals)} divergent signals (too few)")
