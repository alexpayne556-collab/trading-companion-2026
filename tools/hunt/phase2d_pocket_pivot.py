#!/usr/bin/env python3
"""
🐺 PHASE 2D: DEEP DIVE - POCKET PIVOT
New edge discovered! Let's validate it thoroughly.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

UNIVERSE = {
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'SPACE': ['LUNR', 'RKLB', 'SIDU', 'ASTS', 'RDW', 'BKSY', 'MNTS', 'SPIR', 'PL'],
    'NUCLEAR': ['SMR', 'OKLO', 'LEU', 'CCJ', 'UUUU', 'DNN', 'NNE', 'LTBR'],
    'DEFENSE_AI': ['AISP', 'PLTR', 'BBAI', 'KTOS', 'RCAT', 'AVAV'],
    'AI_INFRA': ['SOUN', 'VRT', 'CORZ', 'PATH', 'UPST', 'AI'],
    'MEMORY_SEMI': ['MU', 'SMCI', 'ANET', 'CRDO'],
    'CRYPTO_MINERS': ['CLSK', 'MARA', 'RIOT', 'BITF', 'HUT'],
}

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
    data = {}
    df = yf.download(tickers, period='2y', progress=False, group_by='ticker')
    
    for ticker in tickers:
        try:
            if len(tickers) == 1:
                ticker_df = df
            else:
                ticker_df = df[ticker]
            ticker_df = ticker_df.dropna()
            if len(ticker_df) >= 60:
                data[ticker] = ticker_df
        except:
            continue
    return data

def monte_carlo(signal_returns, all_returns, n=1000):
    actual_mean = np.mean(signal_returns)
    random_means = []
    for _ in range(n):
        sample = np.random.choice(all_returns, size=len(signal_returns), replace=True)
        random_means.append(np.mean(sample))
    p_value = np.mean([r >= actual_mean for r in random_means])
    effect_size = (actual_mean - np.mean(all_returns)) / np.std(all_returns)
    return p_value, actual_mean, effect_size


def pocket_pivot_signal(close, high, low, volume, i):
    """
    POCKET PIVOT:
    1. Stock above 50-day MA (uptrend)
    2. Pulling back 3-10% from recent high
    3. Up day
    4. Volume > any down day volume in last 10 days
    """
    if i < 55:
        return False, {}
    
    # 50-day MA
    ma50 = np.mean(close[i-50:i])
    above_ma = close[i] > ma50
    
    # Recent pullback
    high_10 = max(high[i-10:i])
    pct_from_high = ((close[i] - high_10) / high_10) * 100
    in_pullback = -10 < pct_from_high < -3
    
    # Up day
    up_day = close[i] > close[i-1]
    
    # Volume > any down volume in last 10 days
    down_vols = [volume[j] for j in range(i-10, i) if close[j] < close[j-1]]
    max_down_vol = max(down_vols) if down_vols else 0
    vol_spike = volume[i] > max_down_vol
    
    # Base volume
    base_vol = np.mean(volume[i-20:i-5])
    rel_vol = volume[i] / base_vol if base_vol > 0 else 1
    
    metrics = {
        'ma50': ma50,
        'pct_from_high': pct_from_high,
        'rel_vol': rel_vol,
        'above_ma': above_ma,
        'in_pullback': in_pullback,
        'up_day': up_day,
        'vol_spike': vol_spike
    }
    
    triggered = above_ma and in_pullback and up_day and vol_spike
    return triggered, metrics


def backtest_pocket_pivot(data, forward_days=10):
    """Full backtest with sector breakdown"""
    
    all_returns = []
    signal_results = []
    
    for ticker, df in data.items():
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        volume = df['Volume'].values
        dates = df.index.tolist()
        
        for i in range(55, len(close) - forward_days):
            # Forward return
            fwd_ret = ((close[i + forward_days] - close[i]) / close[i]) * 100
            all_returns.append(fwd_ret)
            
            # Check signal
            triggered, metrics = pocket_pivot_signal(close, high, low, volume, i)
            
            if triggered:
                signal_results.append({
                    'ticker': ticker,
                    'sector': get_sector(ticker),
                    'date': dates[i],
                    'price': close[i],
                    'return': fwd_ret,
                    'win': fwd_ret > 0,
                    'big_win': fwd_ret > 10,
                    'pct_from_high': metrics['pct_from_high'],
                    'rel_vol': metrics['rel_vol']
                })
    
    return pd.DataFrame(signal_results), all_returns


def main():
    print("""
    🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺
    
              PHASE 2D: POCKET PIVOT DEEP DIVE
              
              NEW EDGE DISCOVERED!
              Let's validate it thoroughly.
              
    🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺
    """)
    
    print("Loading data...")
    tickers = get_all_tickers()
    data = fetch_data(tickers)
    print(f"Loaded {len(data)} tickers\n")
    
    # Backtest
    df, all_returns = backtest_pocket_pivot(data)
    
    if len(df) == 0:
        print("No signals found!")
        return
    
    # Overall stats
    print("="*70)
    print("🎯 POCKET PIVOT - FULL VALIDATION")
    print("="*70)
    
    p_val, avg_ret, effect = monte_carlo(df['return'].values, all_returns)
    wr = df['win'].mean() * 100
    big_wins = df['big_win'].sum()
    
    print(f"""
    OVERALL STATS:
    Signals: {len(df)}
    Win Rate: {wr:.1f}%
    Avg Return: {avg_ret:+.2f}%
    10%+ Winners: {big_wins} ({big_wins/len(df)*100:.1f}%)
    
    P-value: {p_val:.4f} {'✅ SIGNIFICANT!' if p_val < 0.05 else '❌'}
    Effect Size: {effect:.2f}
    """)
    
    # By sector
    print("="*70)
    print("BY SECTOR:")
    print("="*70)
    print(f"  {'SECTOR':<15} {'SIGNALS':>8} {'WIN RATE':>10} {'AVG RET':>10} {'P-VALUE':>10}")
    print(f"  {'-'*55}")
    
    sector_stats = []
    for sector in UNIVERSE.keys():
        sector_df = df[df['sector'] == sector]
        if len(sector_df) >= 10:
            sector_returns = sector_df['return'].values
            s_pval, s_avg, _ = monte_carlo(sector_returns, all_returns)
            s_wr = sector_df['win'].mean() * 100
            sig = "✅" if s_pval < 0.05 else ""
            print(f"  {sector:<15} {len(sector_df):>8} {s_wr:>9.1f}% {s_avg:>+9.2f}% {s_pval:>9.4f} {sig}")
            sector_stats.append({
                'sector': sector,
                'signals': len(sector_df),
                'win_rate': s_wr,
                'avg_return': s_avg,
                'p_value': s_pval
            })
    
    # Best sectors
    if sector_stats:
        best = sorted(sector_stats, key=lambda x: x['avg_return'], reverse=True)
        print(f"\n  🏆 BEST: {best[0]['sector']} ({best[0]['avg_return']:+.2f}%)")
    
    # Top catches
    print("\n" + "="*70)
    print("TOP 15 CATCHES:")
    print("="*70)
    
    top = df.nlargest(15, 'return')
    for _, row in top.iterrows():
        print(f"  {row['ticker']:6} {row['date'].strftime('%Y-%m-%d')} {row['return']:+6.1f}% | {row['pct_from_high']:.1f}% pullback, {row['rel_vol']:.1f}x vol [{row['sector']}]")
    
    # Current signals
    print("\n" + "="*70)
    print("📍 CURRENT POCKET PIVOT SIGNALS:")
    print("="*70)
    
    for ticker, ticker_df in data.items():
        close = ticker_df['Close'].values
        high = ticker_df['High'].values
        low = ticker_df['Low'].values
        volume = ticker_df['Volume'].values
        
        i = len(close) - 1
        triggered, metrics = pocket_pivot_signal(close, high, low, volume, i)
        
        if triggered:
            print(f"  ⭐ {ticker:6} ${close[i]:.2f} | {metrics['pct_from_high']:.1f}% pullback, {metrics['rel_vol']:.1f}x vol [{get_sector(ticker)}]")
        elif metrics.get('in_pullback') and metrics.get('above_ma'):
            # Close to triggering
            print(f"  ○ {ticker:6} ${close[i]:.2f} | {metrics['pct_from_high']:.1f}% pullback, WATCHING [{get_sector(ticker)}]")
    
    print(f"""
    
    🐺 POCKET PIVOT - ADDED TO ARSENAL!
    
    FORMULA:
    1. Stock above 50-day MA (uptrend)
    2. Pulled back 3-10% from 10-day high
    3. Up day (close > yesterday)
    4. Volume > any down day in last 10 days
    
    STATS: p={p_val:.4f}, {wr:.1f}% WR, {avg_ret:+.2f}% avg
    
    WHY IT WORKS:
    This is institutional accumulation during a pullback.
    Big money buying the dip in an uptrend.
    Volume surge = conviction.
    
    🐺 AWOOOO!
    """)


if __name__ == '__main__':
    main()
