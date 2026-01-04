#!/usr/bin/env python3
"""
🐺 PHASE 2: WIDEN THE HUNT
Test all 3 validated edges across the FULL UNIVERSE
50+ tickers across 7 sectors
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# THE FULL UNIVERSE
# =============================================================================

UNIVERSE = {
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'SPACE': ['LUNR', 'RKLB', 'SIDU', 'ASTS', 'RDW', 'BKSY', 'MNTS', 'SPIR', 'PL'],
    'NUCLEAR': ['SMR', 'OKLO', 'LEU', 'CCJ', 'UUUU', 'DNN', 'NNE', 'LTBR'],
    'DEFENSE_AI': ['AISP', 'PLTR', 'BBAI', 'KTOS', 'RCAT', 'AVAV'],
    'AI_INFRA': ['SOUN', 'VRT', 'CORZ', 'PATH', 'UPST', 'AI'],
    'MEMORY_SEMI': ['MU', 'SMCI', 'ANET', 'CRDO'],
    'CRYPTO_MINERS': ['CLSK', 'MARA', 'RIOT', 'BITF', 'HUT'],
}

# Original validation set
ORIGINAL_PACK = ['SIDU', 'RGTI', 'QBTS', 'RCAT', 'LUNR', 'ASTS', 'IONQ']

def get_all_tickers():
    """Get all unique tickers"""
    all_t = []
    for sector, tickers in UNIVERSE.items():
        all_t.extend(tickers)
    return list(set(all_t))

def fetch_data(tickers, period='2y'):
    """Fetch data for all tickers"""
    print(f"  Fetching {len(tickers)} tickers...")
    data = {}
    
    # Batch download
    df = yf.download(tickers, period=period, progress=False, group_by='ticker')
    
    for ticker in tickers:
        try:
            if len(tickers) == 1:
                ticker_df = df
            else:
                ticker_df = df[ticker]
            
            if len(ticker_df) < 50:
                continue
                
            ticker_df = ticker_df.dropna()
            if len(ticker_df) < 50:
                continue
                
            data[ticker] = ticker_df
        except Exception as e:
            continue
    
    print(f"  Loaded {len(data)} tickers with valid data")
    return data

# =============================================================================
# THE 3 VALIDATED SIGNALS
# =============================================================================

def check_wolf_signal(close, high, low, volume, i):
    """
    Wolf Signal: Volume spike + flat day + healthy trend
    Original: p=0.023, +37.87% avg, 78% WR
    """
    if i < 25:
        return False
    
    # Base volume (20-day avg excluding last 5)
    base_vol = np.mean(volume[max(0, i-20):i])
    
    # Criteria
    vol_spike = volume[i] > 2 * base_vol
    
    prev_close = close[i-1] if i > 0 else close[i]
    daily_chg = abs((close[i] - prev_close) / prev_close) * 100
    flat_day = daily_chg < 2
    
    # Up/down volume ratio
    up_vol = sum(volume[j] for j in range(max(0, i-20), i) if close[j] > close[j-1])
    down_vol = sum(volume[j] for j in range(max(0, i-20), i) if close[j] < close[j-1])
    vol_ratio = up_vol / down_vol if down_vol > 0 else 1
    healthy_trend = vol_ratio > 2.5
    
    # Near highs
    high_20 = max(high[max(0, i-20):i])
    pct_from_high = ((close[i] - high_20) / high_20) * 100
    near_highs = pct_from_high > -5
    
    return vol_spike and flat_day and healthy_trend and near_highs


def check_prerun_signal(close, high, low, volume, i, min_score=4):
    """
    Pre-Run Predictor: 5 signatures before explosions
    Original: p=0.0000, +17.27% avg (5/5), 57.9% WR
    """
    if i < 25:
        return False, 0
    
    score = 0
    
    # Base metrics
    base_vol = np.mean(volume[max(0, i-20):i])
    
    # 1. 5-day volume ratio > 1.0
    vol_5d = np.mean(volume[max(0, i-5):i])
    if vol_5d / base_vol > 1.0:
        score += 1
    
    # 2. Signal day volume > 1.0
    if volume[i] / base_vol > 1.0:
        score += 1
    
    # 3. 5-day price change > -2%
    price_5d = ((close[i] - close[max(0, i-5)]) / close[max(0, i-5)]) * 100
    if price_5d > -2:
        score += 1
    
    # 4. 5-day avg CLV > 0.45
    clvs = []
    for k in range(max(0, i-5), i):
        day_range = high[k] - low[k]
        if day_range > 0:
            clvs.append((close[k] - low[k]) / day_range)
    avg_clv = np.mean(clvs) if clvs else 0.5
    if avg_clv > 0.45:
        score += 1
    
    # 5. Up/down volume ratio > 1.2
    up_vol = sum(volume[j] for j in range(max(0, i-20), i) if close[j] > close[j-1])
    down_vol = sum(volume[j] for j in range(max(0, i-20), i) if close[j] < close[j-1])
    vol_ratio = up_vol / down_vol if down_vol > 0 else 1
    if vol_ratio > 1.2:
        score += 1
    
    return score >= min_score, score


def check_capitulation(close, high, low, volume, i):
    """
    Capitulation Hunter: Red spike when wounded
    Original: p=0.004, +19.95% avg, 58% WR
    """
    if i < 25:
        return False
    
    # Wounded: 15-40% from 20-day high
    high_20 = max(high[max(0, i-20):i])
    pct_from_high = ((close[i] - high_20) / high_20) * 100
    wounded = -40 < pct_from_high < -15
    
    # Volume spike
    base_vol = np.mean(volume[max(0, i-20):i])
    vol_spike = volume[i] > 1.5 * base_vol
    
    # Red day (CLV < 0.5)
    day_range = high[i] - low[i]
    clv = (close[i] - low[i]) / day_range if day_range > 0 else 0.5
    red_day = clv < 0.5
    
    return wounded and vol_spike and red_day

# =============================================================================
# BACKTEST ENGINE
# =============================================================================

def backtest_signal(data, signal_func, signal_name, forward_days=10):
    """Backtest a signal across all data"""
    results = []
    
    for ticker, df in data.items():
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        volume = df['Volume'].values
        dates = df.index.tolist()
        
        for i in range(25, len(close) - forward_days):
            # Check signal
            if signal_name == 'prerun':
                triggered, score = signal_func(close, high, low, volume, i)
            else:
                triggered = signal_func(close, high, low, volume, i)
                score = None
            
            if triggered:
                # Calculate forward return
                entry_price = close[i]
                exit_price = close[i + forward_days]
                ret = ((exit_price - entry_price) / entry_price) * 100
                
                # Find sector
                sector = 'UNKNOWN'
                for s, tickers in UNIVERSE.items():
                    if ticker in tickers:
                        sector = s
                        break
                
                results.append({
                    'ticker': ticker,
                    'date': dates[i],
                    'sector': sector,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'return': ret,
                    'win': ret > 0,
                    'big_win': ret > 10,
                    'score': score,
                    'in_original': ticker in ORIGINAL_PACK
                })
    
    return pd.DataFrame(results)


def analyze_results(df, signal_name):
    """Analyze backtest results"""
    if len(df) == 0:
        print(f"  No signals found for {signal_name}")
        return None
    
    print(f"\n{'='*70}")
    print(f"🐺 {signal_name.upper()} - UNIVERSE BACKTEST")
    print(f"{'='*70}")
    
    # Overall stats
    total = len(df)
    wins = df['win'].sum()
    wr = wins / total * 100
    avg_ret = df['return'].mean()
    big_wins = df['big_win'].sum()
    
    print(f"\nOVERALL STATS:")
    print(f"  Signals: {total}")
    print(f"  Win Rate: {wr:.1f}%")
    print(f"  Avg Return: {avg_ret:+.2f}%")
    print(f"  10%+ Winners: {big_wins} ({big_wins/total*100:.1f}%)")
    
    # Original pack vs new tickers
    orig = df[df['in_original']]
    new = df[~df['in_original']]
    
    print(f"\nORIGINAL PACK (7 tickers) vs NEW TICKERS:")
    if len(orig) > 0:
        print(f"  Original: {len(orig)} signals, {orig['win'].mean()*100:.1f}% WR, {orig['return'].mean():+.2f}% avg")
    if len(new) > 0:
        print(f"  New:      {len(new)} signals, {new['win'].mean()*100:.1f}% WR, {new['return'].mean():+.2f}% avg")
    
    # By sector
    print(f"\nBY SECTOR:")
    print(f"  {'SECTOR':<15} {'SIGNALS':>8} {'WIN RATE':>10} {'AVG RET':>10} {'10%+ WINS':>10}")
    print(f"  {'-'*55}")
    
    sector_stats = []
    for sector in UNIVERSE.keys():
        sector_df = df[df['sector'] == sector]
        if len(sector_df) > 0:
            s_wr = sector_df['win'].mean() * 100
            s_ret = sector_df['return'].mean()
            s_big = sector_df['big_win'].sum()
            print(f"  {sector:<15} {len(sector_df):>8} {s_wr:>9.1f}% {s_ret:>+9.2f}% {s_big:>10}")
            sector_stats.append({
                'sector': sector,
                'signals': len(sector_df),
                'win_rate': s_wr,
                'avg_return': s_ret,
                'big_wins': s_big
            })
    
    # Best sector
    if sector_stats:
        best = max(sector_stats, key=lambda x: x['avg_return'])
        print(f"\n  🏆 BEST SECTOR: {best['sector']} ({best['avg_return']:+.2f}% avg)")
    
    # Top individual catches
    print(f"\nTOP 10 CATCHES:")
    top = df.nlargest(10, 'return')
    for _, row in top.iterrows():
        print(f"  {row['ticker']:6} {row['date'].strftime('%Y-%m-%d')} {row['return']:+.1f}% [{row['sector']}]")
    
    return df


def monte_carlo_by_sector(df, n_simulations=1000):
    """Monte Carlo validation by sector"""
    print(f"\n{'='*70}")
    print(f"🎲 MONTE CARLO VALIDATION BY SECTOR")
    print(f"{'='*70}")
    
    for sector in UNIVERSE.keys():
        sector_df = df[df['sector'] == sector]
        if len(sector_df) < 10:
            continue
        
        actual_mean = sector_df['return'].mean()
        
        # Random sampling
        all_returns = df['return'].values
        random_means = []
        
        for _ in range(n_simulations):
            sample = np.random.choice(all_returns, size=len(sector_df), replace=True)
            random_means.append(np.mean(sample))
        
        # P-value
        p_value = np.mean([r >= actual_mean for r in random_means])
        
        sig = "✅" if p_value < 0.05 else "❌"
        print(f"  {sector:<15} actual={actual_mean:+.2f}% p={p_value:.4f} {sig}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("""
    🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺
    
                    PHASE 2: WIDEN THE HUNT
                    
           Testing 3 edges across 50+ tickers
           7 sectors • 2 years of data
           
    🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺
    """)
    
    # Get all tickers
    all_tickers = get_all_tickers()
    print(f"Universe: {len(all_tickers)} tickers across {len(UNIVERSE)} sectors")
    
    # Fetch data
    data = fetch_data(all_tickers)
    
    # Test each signal
    print("\n" + "="*70)
    print("BACKTESTING WOLF SIGNAL...")
    wolf_results = backtest_signal(data, check_wolf_signal, 'wolf')
    wolf_df = analyze_results(wolf_results, 'WOLF SIGNAL')
    
    print("\n" + "="*70)
    print("BACKTESTING PRE-RUN PREDICTOR...")
    prerun_results = backtest_signal(data, lambda c,h,l,v,i: check_prerun_signal(c,h,l,v,i,4), 'prerun')
    prerun_df = analyze_results(prerun_results, 'PRE-RUN PREDICTOR (4+/5)')
    
    print("\n" + "="*70)
    print("BACKTESTING CAPITULATION HUNTER...")
    cap_results = backtest_signal(data, check_capitulation, 'capitulation')
    cap_df = analyze_results(cap_results, 'CAPITULATION HUNTER')
    
    # Monte Carlo for each
    if wolf_df is not None and len(wolf_df) > 20:
        monte_carlo_by_sector(wolf_df)
    
    if cap_df is not None and len(cap_df) > 20:
        monte_carlo_by_sector(cap_df)
    
    # Summary
    print(f"\n{'='*70}")
    print("🐺 PHASE 2 SUMMARY")
    print(f"{'='*70}")
    print("""
    Questions answered:
    1. Do edges hold across sectors? → Check sector breakdown above
    2. Which sectors have best hit rates? → Check 🏆 BEST SECTOR
    3. New patterns? → Compare original pack vs new tickers
    """)
    
    print("\n🐺 AWOOOO! Phase 2 complete!")
