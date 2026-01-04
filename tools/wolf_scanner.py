#!/usr/bin/env python3
"""
🐺 WOLF PACK SCANNER
Live scanner for all 3 validated edges
Run this to see current signals
"""

import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime

print("=" * 70)
print("🐺 WOLF PACK SCANNER")
print(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 70)

tickers = ['SIDU', 'RGTI', 'QBTS', 'RCAT', 'LUNR', 'ASTS', 'IONQ']

results = {
    'wolf_signal': [],
    'prerun_predictor': [],
    'capitulation': []
}

for ticker in tickers:
    print(f"\nScanning {ticker}...", end=" ")
    
    df = yf.download(ticker, period='3mo', progress=False)
    
    if len(df) < 30:
        print("Insufficient data")
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
    
    # Current state (last day)
    i = len(close) - 1
    
    # Calculate all metrics
    base_vol = np.mean(volume[max(0, i-20):i])
    rel_vol = volume[i] / base_vol if base_vol > 0 else 1
    
    prev_close = close[i-1] if i > 0 else close[i]
    daily_chg = ((close[i] - prev_close) / prev_close) * 100
    price_chg_abs = abs(daily_chg)
    
    # Up/down volume ratio
    up_vol = sum(volume[j] for j in range(max(0, i-20), i) if close[j] > close[j-1])
    down_vol = sum(volume[j] for j in range(max(0, i-20), i) if close[j] < close[j-1])
    vol_ratio = up_vol / down_vol if down_vol > 0 else 1
    
    # Distance from 20-day high
    high_20 = max(high[max(0, i-20):i])
    pct_from_high = ((close[i] - high_20) / high_20) * 100
    days_from_high = min(j for j in range(min(20, i)) if high[i-j-1] == high_20) if i > 0 else 0
    
    # 5-day metrics
    price_5d = ((close[i] - close[max(0, i-5)]) / close[max(0, i-5)]) * 100 if i >= 5 else 0
    
    clvs = []
    for k in range(max(0, i-5), i):
        day_range = high[k] - low[k]
        if day_range > 0:
            clvs.append((close[k] - low[k]) / day_range)
        else:
            clvs.append(0.5)
    avg_clv = np.mean(clvs) if clvs else 0.5
    
    # 5-day volume ratio
    prerun_vol = np.mean(volume[max(0, i-5):i])
    vol_ratio_prerun = prerun_vol / base_vol if base_vol > 0 else 1
    
    # CLV today
    day_range = high[i] - low[i]
    clv_today = (close[i] - low[i]) / day_range if day_range > 0 else 0.5
    
    # ===== CHECK WOLF SIGNAL =====
    wolf_signal = (
        rel_vol > 2.0 and
        price_chg_abs < 2 and
        vol_ratio > 2.5 and
        days_from_high < 5
    )
    
    # ===== CHECK PRE-RUN PREDICTOR (5 criteria) =====
    prerun_score = 0
    if vol_ratio_prerun > 1.0:
        prerun_score += 1
    if rel_vol > 1.0:
        prerun_score += 1
    if price_5d > -2:
        prerun_score += 1
    if avg_clv > 0.45:
        prerun_score += 1
    if vol_ratio > 1.2:
        prerun_score += 1
    
    # ===== CHECK CAPITULATION =====
    capitulation = (
        -40 <= pct_from_high <= -15 and
        rel_vol > 1.5 and
        clv_today < 0.5
    )
    
    # Store results
    ticker_data = {
        'ticker': ticker,
        'price': close[i],
        'date': dates[i].strftime('%Y-%m-%d'),
        'rel_vol': rel_vol,
        'vol_ratio': vol_ratio,
        'pct_from_high': pct_from_high,
        'daily_chg': daily_chg,
        'prerun_score': prerun_score,
        'clv_today': clv_today
    }
    
    if wolf_signal:
        results['wolf_signal'].append(ticker_data)
    if prerun_score >= 4:
        results['prerun_predictor'].append(ticker_data)
    if capitulation:
        results['capitulation'].append(ticker_data)
    
    # Print status
    signals = []
    if wolf_signal:
        signals.append("🐺 WOLF")
    if prerun_score >= 4:
        signals.append(f"📈 PRE-RUN({prerun_score}/5)")
    if capitulation:
        signals.append("💀 CAPITULATION")
    
    if signals:
        print(" | ".join(signals))
    else:
        print(f"No signals (score={prerun_score}/5, {pct_from_high:.0f}% from high)")

# ===== DISPLAY SIGNALS =====

print(f"\n{'=' * 70}")
print("🐺 WOLF SIGNALS (p=0.023, +37.87% avg, 78% WR)")
print("=" * 70)

if results['wolf_signal']:
    for r in results['wolf_signal']:
        print(f"  {r['ticker']:5} ${r['price']:.2f} | {r['rel_vol']:.1f}x vol | ratio={r['vol_ratio']:.1f} | {r['pct_from_high']:.0f}% from high")
else:
    print("  No Wolf Signals today")

print(f"\n{'=' * 70}")
print("📈 PRE-RUN PREDICTOR (p=0.0000, +17.27% avg, 58% WR)")
print("=" * 70)

if results['prerun_predictor']:
    for r in results['prerun_predictor']:
        print(f"  {r['ticker']:5} ${r['price']:.2f} | Score {r['prerun_score']}/5 | {r['pct_from_high']:.0f}% from high | {r['daily_chg']:+.1f}% today")
else:
    print("  No Pre-Run signals (score >= 4)")

print(f"\n{'=' * 70}")
print("💀 CAPITULATION HUNTER (p=0.004, +19.95% avg, 58% WR)")
print("=" * 70)

if results['capitulation']:
    for r in results['capitulation']:
        print(f"  {r['ticker']:5} ${r['price']:.2f} | {r['pct_from_high']:.0f}% down | {r['rel_vol']:.1f}x vol | CLV={r['clv_today']:.2f}")
else:
    print("  No Capitulation signals")

print(f"\n{'=' * 70}")
print("TICKER STATUS")
print("=" * 70)

# Print all tickers with their current state
for ticker in tickers:
    df = yf.download(ticker, period='3mo', progress=False)
    if len(df) < 2:
        continue
    
    if isinstance(df['Close'], pd.DataFrame):
        close = df['Close'].iloc[:, 0].values
        high = df['High'].iloc[:, 0].values
    else:
        close = df['Close'].values
        high = df['High'].values
    
    price = close[-1]
    high_20 = max(high[-20:])
    pct_from = ((price - high_20) / high_20) * 100
    
    status = "📍 Near high" if pct_from > -10 else "⚠️ Wounded" if pct_from > -25 else "💀 Deep wound"
    print(f"  {ticker:5} ${price:.2f} | {pct_from:+.0f}% from 20d high {status}")

print(f"\n{'=' * 70}")
print("🐺 PACK READY FOR MONDAY")
print("=" * 70)
