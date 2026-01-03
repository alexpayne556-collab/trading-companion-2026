#!/usr/bin/env python3
"""
🐺 HUNT #3: WOUNDED WOLF
Does the Wolf Signal work BETTER when stock is down 10-20% from highs?
Buy the dip on confirmed accumulation
"""

import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("🐺 HUNT #3: WOUNDED WOLF")
print("Wolf Signal + Down from highs")
print("=" * 70)

tickers = ['SIDU', 'RGTI', 'QBTS', 'RCAT', 'LUNR', 'ASTS', 'IONQ']

# The original Wolf Signal criteria:
# 1. Volume spike > 2x 20-day avg
# 2. Price change < 2% (flat)
# 3. Volume ratio (up/down) > 2.0
# 4. Within 5 days of 20-day high

wolf_near_high = []  # Wolf signal near highs
wolf_wounded = []     # Wolf signal when DOWN 10-20%
wolf_deep_wound = []  # Wolf signal when DOWN 20%+
all_returns = []

for ticker in tickers:
    print(f"Scanning {ticker}...")
    df = yf.download(ticker, start='2024-01-01', progress=False)
    
    if len(df) < 30:
        continue
    
    if isinstance(df['Close'], pd.DataFrame):
        close = df['Close'].iloc[:, 0].values
        high = df['High'].iloc[:, 0].values
        volume = df['Volume'].iloc[:, 0].values
    else:
        close = df['Close'].values
        high = df['High'].values
        volume = df['Volume'].values
    
    dates = df.index.tolist()
    
    # Collect all returns
    for i in range(len(close)-10):
        ret = ((close[i+10] - close[i]) / close[i]) * 100
        all_returns.append(ret)
    
    for i in range(25, len(close)-10):
        # Check Wolf Signal criteria (relaxed - no near-high requirement)
        base_vol = np.mean(volume[i-20:i])
        rel_vol = volume[i] / base_vol if base_vol > 0 else 1
        
        prev_close = close[i-1] if i > 0 else close[i]
        price_chg = abs((close[i] - prev_close) / prev_close * 100)
        
        up_vol = sum(volume[k] for k in range(i-20, i) if close[k] > close[k-1])
        down_vol = sum(volume[k] for k in range(i-20, i) if close[k] < close[k-1])
        vol_ratio = up_vol / down_vol if down_vol > 0 else 1
        
        # Wolf criteria (volume + flat price + vol ratio)
        if rel_vol > 2.0 and price_chg < 2 and vol_ratio > 2.0:
            # Distance from 20-day high
            high_20 = max(high[i-20:i])
            pct_from_high = ((close[i] - high_20) / high_20) * 100
            
            # Outcome
            entry = close[i]
            exit_10d = close[min(i+10, len(close)-1)]
            ret = ((exit_10d - entry) / entry) * 100
            
            signal = {
                'ticker': ticker,
                'date': dates[i].strftime('%Y-%m-%d'),
                'pct_from_high': pct_from_high,
                'vol_ratio': vol_ratio,
                'return': ret
            }
            
            # Categorize by distance from high
            if pct_from_high > -10:
                wolf_near_high.append(signal)
            elif -20 < pct_from_high <= -10:
                wolf_wounded.append(signal)
            else:
                wolf_deep_wound.append(signal)

print(f"\n{'=' * 70}")
print("WOLF SIGNAL BY DISTANCE FROM HIGH")
print("=" * 70)

all_returns = np.array(all_returns)

def analyze_group(signals, name):
    if len(signals) < 5:
        print(f"\n{name}: Only {len(signals)} signals (too few)")
        return None
    
    rets = np.array([s['return'] for s in signals])
    
    print(f"\n{name}:")
    print(f"  Signals: {len(rets)}")
    print(f"  Win Rate: {(rets > 0).mean() * 100:.1f}%")
    print(f"  Avg Return: {rets.mean():+.2f}%")
    print(f"  Median: {np.median(rets):+.2f}%")
    
    # Monte Carlo
    mc_results = []
    for _ in range(1000):
        sample = np.random.choice(all_returns, size=len(rets))
        mc_results.append(sample.mean())
    
    mc_results = np.array(mc_results)
    mc_mean = mc_results.mean()
    mc_std = mc_results.std()
    
    avg_ret = rets.mean()
    p_value = (mc_results >= avg_ret).mean()
    effect = (avg_ret - mc_mean) / mc_std if mc_std > 0 else 0
    
    print(f"  P-value: {p_value:.4f}")
    print(f"  Effect: {effect:.2f}")
    
    if p_value < 0.05:
        print(f"  ✅ HIT P < 0.05!")
    elif p_value < 0.10:
        print(f"  ⚠️  Marginal")
    
    return {'p': p_value, 'effect': effect, 'avg': avg_ret, 'signals': len(rets)}

analyze_group(wolf_near_high, "WOLF NEAR HIGH (<10% down)")
analyze_group(wolf_wounded, "WOUNDED WOLF (10-20% down)")
analyze_group(wolf_deep_wound, "DEEP WOUND (>20% down)")

# Show best wounded signals
print(f"\n{'=' * 70}")
print("WOUNDED WOLF SIGNALS (10-20% down):")
print("=" * 70)

sorted_wounded = sorted(wolf_wounded, key=lambda x: x['return'], reverse=True)
for s in sorted_wounded[:15]:
    win = "✓" if s['return'] > 0 else "✗"
    print(f"{s['date']} {s['ticker']:5} {s['pct_from_high']:+.0f}% from high | vol_ratio={s['vol_ratio']:.1f} | {s['return']:+.1f}% {win}")

# Show deep wound signals
print(f"\n{'=' * 70}")
print("DEEP WOUND SIGNALS (>20% down):")
print("=" * 70)

sorted_deep = sorted(wolf_deep_wound, key=lambda x: x['return'], reverse=True)
for s in sorted_deep[:15]:
    win = "✓" if s['return'] > 0 else "✗"
    print(f"{s['date']} {s['ticker']:5} {s['pct_from_high']:+.0f}% from high | vol_ratio={s['vol_ratio']:.1f} | {s['return']:+.1f}% {win}")
