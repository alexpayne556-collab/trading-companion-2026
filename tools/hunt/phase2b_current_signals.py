#!/usr/bin/env python3
"""
🐺 PHASE 2B: WHAT'S SIGNALING RIGHT NOW?
Scan all 50+ tickers for current signals
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# The full universe
UNIVERSE = {
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'SPACE': ['LUNR', 'RKLB', 'SIDU', 'ASTS', 'RDW', 'BKSY', 'MNTS', 'SPIR', 'PL'],
    'NUCLEAR': ['SMR', 'OKLO', 'LEU', 'CCJ', 'UUUU', 'DNN', 'NNE', 'LTBR'],
    'DEFENSE_AI': ['AISP', 'PLTR', 'BBAI', 'KTOS', 'RCAT', 'AVAV'],
    'AI_INFRA': ['SOUN', 'VRT', 'CORZ', 'PATH', 'UPST', 'AI'],
    'MEMORY_SEMI': ['MU', 'SMCI', 'ANET', 'CRDO'],
    'CRYPTO_MINERS': ['CLSK', 'MARA', 'RIOT', 'BITF', 'HUT'],
}

def c(text, code):
    """Color helper"""
    colors = {
        'red': '\033[91m', 'green': '\033[92m', 'yellow': '\033[93m',
        'blue': '\033[94m', 'magenta': '\033[95m', 'cyan': '\033[96m',
        'white': '\033[97m', 'bold': '\033[1m', 'reset': '\033[0m'
    }
    return f"{colors.get(code, '')}{text}{colors['reset']}"

def get_all_tickers():
    all_t = []
    for sector, tickers in UNIVERSE.items():
        all_t.extend(tickers)
    return list(set(all_t))

def get_sector(ticker):
    for sector, tickers in UNIVERSE.items():
        if ticker in tickers:
            return sector
    return 'UNKNOWN'

def fetch_data(tickers):
    """Fetch recent data"""
    data = {}
    df = yf.download(tickers, period='3mo', progress=False, group_by='ticker')
    
    for ticker in tickers:
        try:
            if len(tickers) == 1:
                ticker_df = df
            else:
                ticker_df = df[ticker]
            
            ticker_df = ticker_df.dropna()
            if len(ticker_df) >= 30:
                data[ticker] = ticker_df
        except:
            continue
    
    return data

def analyze_ticker(ticker, df):
    """Full analysis of a single ticker"""
    close = df['Close'].values
    high = df['High'].values
    low = df['Low'].values
    volume = df['Volume'].values
    i = len(close) - 1
    
    if i < 25:
        return None
    
    # Base metrics
    base_vol = np.mean(volume[max(0, i-20):i])
    rel_vol = volume[i] / base_vol if base_vol > 0 else 1
    
    prev_close = close[i-1]
    daily_chg = ((close[i] - prev_close) / prev_close) * 100
    
    high_20 = max(high[max(0, i-20):i])
    pct_from_high = ((close[i] - high_20) / high_20) * 100
    
    # Up/down volume ratio
    up_vol = sum(volume[j] for j in range(max(0, i-20), i) if close[j] > close[j-1])
    down_vol = sum(volume[j] for j in range(max(0, i-20), i) if close[j] < close[j-1])
    vol_ratio = up_vol / down_vol if down_vol > 0 else 1
    
    # 5-day metrics
    price_5d = ((close[i] - close[max(0, i-5)]) / close[max(0, i-5)]) * 100
    vol_5d = np.mean(volume[max(0, i-5):i])
    vol_ratio_5d = vol_5d / base_vol if base_vol > 0 else 1
    
    # CLV
    clvs = []
    for k in range(max(0, i-5), i):
        day_range = high[k] - low[k]
        if day_range > 0:
            clvs.append((close[k] - low[k]) / day_range)
    avg_clv = np.mean(clvs) if clvs else 0.5
    
    day_range = high[i] - low[i]
    clv_today = (close[i] - low[i]) / day_range if day_range > 0 else 0.5
    
    # Signal checks
    signals = []
    
    # WOLF SIGNAL
    vol_spike = volume[i] > 2 * base_vol
    flat_day = abs(daily_chg) < 2
    healthy_trend = vol_ratio > 2.5
    near_highs = pct_from_high > -5
    
    wolf_score = sum([vol_spike, flat_day, healthy_trend, near_highs])
    if wolf_score == 4:
        signals.append(('WOLF', 'STRONG'))
    elif wolf_score == 3:
        signals.append(('WOLF', 'CLOSE'))
    
    # PRE-RUN PREDICTOR
    prerun_score = 0
    if vol_ratio_5d > 1.0: prerun_score += 1
    if rel_vol > 1.0: prerun_score += 1
    if price_5d > -2: prerun_score += 1
    if avg_clv > 0.45: prerun_score += 1
    if vol_ratio > 1.2: prerun_score += 1
    
    if prerun_score == 5:
        signals.append(('PRERUN', 'STRONG'))
    elif prerun_score >= 4:
        signals.append(('PRERUN', 'MODERATE'))
    
    # CAPITULATION HUNTER
    wounded = -40 < pct_from_high < -15
    cap_vol_spike = volume[i] > 1.5 * base_vol
    red_day = clv_today < 0.5
    
    cap_score = sum([wounded, cap_vol_spike, red_day])
    if cap_score == 3:
        signals.append(('CAPITULATION', 'STRONG'))
    elif cap_score == 2 and wounded:
        signals.append(('CAPITULATION', 'CLOSE'))
    
    return {
        'ticker': ticker,
        'sector': get_sector(ticker),
        'price': float(close[i]),
        'daily_chg': float(daily_chg),
        'pct_from_high': float(pct_from_high),
        'rel_vol': float(rel_vol),
        'vol_ratio': float(vol_ratio),
        'price_5d': float(price_5d),
        'avg_clv': float(avg_clv),
        'prerun_score': prerun_score,
        'wolf_score': wolf_score,
        'signals': signals
    }


def main():
    print(c("""
    🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺
    
            PHASE 2B: CURRENT SIGNAL SCAN
            
            What's signaling RIGHT NOW across 50+ tickers?
            
    🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺
    """, 'yellow'))
    
    # Fetch all data
    all_tickers = get_all_tickers()
    print(c(f"  Scanning {len(all_tickers)} tickers...", 'white'))
    
    data = fetch_data(all_tickers)
    print(c(f"  Loaded {len(data)} tickers\n", 'white'))
    
    # Analyze all
    results = []
    for ticker, df in data.items():
        analysis = analyze_ticker(ticker, df)
        if analysis:
            results.append(analysis)
    
    # Sort by daily change
    results.sort(key=lambda x: x['daily_chg'], reverse=True)
    
    # Display active signals
    print(c("=" * 70, 'cyan'))
    print(c("🎯 ACTIVE SIGNALS - Friday Close", 'yellow'))
    print(c("=" * 70, 'cyan'))
    
    wolf_signals = [r for r in results if any(s[0] == 'WOLF' for s in r['signals'])]
    prerun_signals = [r for r in results if any(s[0] == 'PRERUN' for s in r['signals'])]
    cap_signals = [r for r in results if any(s[0] == 'CAPITULATION' for s in r['signals'])]
    
    # Wolf Signals
    print(c("\n🐺 WOLF SIGNALS:", 'green'))
    print(c("   Volume spike + flat + healthy trend near highs", 'white'))
    if wolf_signals:
        for r in wolf_signals:
            strength = [s[1] for s in r['signals'] if s[0] == 'WOLF'][0]
            star = "⭐" if strength == 'STRONG' else "○"
            print(c(f"   {star} {r['ticker']:6} ${r['price']:.2f} | {r['daily_chg']:+.1f}% day | {r['pct_from_high']:.1f}% from high | {r['rel_vol']:.1f}x vol [{r['sector']}]", 'green'))
    else:
        print(c("   No Wolf Signals today", 'white'))
    
    # Pre-Run
    print(c("\n📈 PRE-RUN PREDICTOR:", 'yellow'))
    print(c("   5 criteria score >= 4/5", 'white'))
    if prerun_signals:
        for r in sorted(prerun_signals, key=lambda x: x['prerun_score'], reverse=True):
            strength = [s[1] for s in r['signals'] if s[0] == 'PRERUN'][0]
            star = "⭐" if strength == 'STRONG' else "○"
            print(c(f"   {star} {r['ticker']:6} ${r['price']:.2f} | Score {r['prerun_score']}/5 | {r['daily_chg']:+.1f}% day | CLV {r['avg_clv']:.2f} [{r['sector']}]", 'yellow'))
    else:
        print(c("   No Pre-Run Signals today", 'white'))
    
    # Capitulation
    print(c("\n💀 CAPITULATION HUNTER:", 'magenta'))
    print(c("   Wounded (15-40% down) + red volume spike", 'white'))
    if cap_signals:
        for r in cap_signals:
            strength = [s[1] for s in r['signals'] if s[0] == 'CAPITULATION'][0]
            star = "⭐" if strength == 'STRONG' else "○"
            print(c(f"   {star} {r['ticker']:6} ${r['price']:.2f} | {r['pct_from_high']:.1f}% from high | {r['rel_vol']:.1f}x vol | CLV {r['avg_clv']:.2f} [{r['sector']}]", 'magenta'))
    else:
        print(c("   No Capitulation Signals today", 'white'))
    
    # Full market overview
    print(c("\n" + "=" * 70, 'cyan'))
    print(c("📊 FULL UNIVERSE - By Sector", 'yellow'))
    print(c("=" * 70, 'cyan'))
    
    for sector, tickers in UNIVERSE.items():
        sector_results = [r for r in results if r['sector'] == sector]
        if not sector_results:
            continue
        
        # Sector performance
        avg_chg = np.mean([r['daily_chg'] for r in sector_results])
        avg_from_high = np.mean([r['pct_from_high'] for r in sector_results])
        
        print(c(f"\n{sector} (avg: {avg_chg:+.1f}% day, {avg_from_high:.1f}% from highs)", 'cyan'))
        print(c(f"  {'TICKER':<8} {'PRICE':>10} {'DAY':>8} {'FROM HI':>10} {'VOL':>6} {'PRERUN':>8}", 'white'))
        print(c(f"  {'-'*55}", 'white'))
        
        for r in sorted(sector_results, key=lambda x: x['daily_chg'], reverse=True):
            arrow = c("▲", 'green') if r['daily_chg'] > 0 else c("▼", 'red')
            pr = f"{r['prerun_score']}/5" if r['prerun_score'] >= 3 else ""
            print(f"  {r['ticker']:<8} ${r['price']:>9.2f} {arrow}{abs(r['daily_chg']):>6.1f}% {r['pct_from_high']:>9.1f}% {r['rel_vol']:>5.1f}x {pr:>8}")
    
    # Top movers
    print(c("\n" + "=" * 70, 'cyan'))
    print(c("🚀 TOP 15 MOVERS TODAY", 'yellow'))
    print(c("=" * 70, 'cyan'))
    
    for r in results[:15]:
        arrow = c("▲", 'green') if r['daily_chg'] > 0 else c("▼", 'red')
        sig = ""
        if r['signals']:
            sig = " | " + ", ".join([s[0] for s in r['signals']])
        print(f"  {r['ticker']:6} ${r['price']:.2f} {arrow}{abs(r['daily_chg']):>6.1f}% [{r['sector']}]{sig}")
    
    # Wounded stocks (potential capitulation setups)
    wounded = [r for r in results if r['pct_from_high'] < -20]
    if wounded:
        print(c("\n" + "=" * 70, 'cyan'))
        print(c("🩸 WOUNDED STOCKS (Capitulation Watch)", 'red'))
        print(c("=" * 70, 'cyan'))
        
        for r in sorted(wounded, key=lambda x: x['pct_from_high']):
            print(f"  {r['ticker']:6} ${r['price']:.2f} | {r['pct_from_high']:.1f}% from high | {r['rel_vol']:.1f}x vol [{r['sector']}]")
    
    # Summary
    print(c("\n" + "=" * 70, 'cyan'))
    print(c("🐺 SUMMARY", 'yellow'))
    print(c("=" * 70, 'cyan'))
    print(c(f"""
    ACTIVE SIGNALS:
    - Wolf Signals:    {len(wolf_signals)}
    - Pre-Run (4+/5):  {len(prerun_signals)}
    - Capitulation:    {len(cap_signals)}
    
    UNIVERSE STATUS:
    - Total Tickers:   {len(results)}
    - Big Movers (5%+): {len([r for r in results if abs(r['daily_chg']) > 5])}
    - Wounded (20%+ down): {len(wounded)}
    
    🐺 AWOOOO!
    """, 'white'))


if __name__ == '__main__':
    main()
