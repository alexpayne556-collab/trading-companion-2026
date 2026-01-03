#!/usr/bin/env python3
"""
🐺 PHASE 2C: NEW PATTERN DISCOVERY
Going off leash - finding patterns we haven't tested yet
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
    """Calculate p-value via Monte Carlo"""
    actual_mean = np.mean(signal_returns)
    random_means = []
    for _ in range(n):
        sample = np.random.choice(all_returns, size=len(signal_returns), replace=True)
        random_means.append(np.mean(sample))
    p_value = np.mean([r >= actual_mean for r in random_means])
    return p_value, actual_mean

# =============================================================================
# NEW PATTERN 1: SQUEEZE BREAKOUT
# Bollinger Band squeeze + volume breakout
# =============================================================================

def test_squeeze_breakout(data, forward_days=10):
    """
    Squeeze: Bollinger Bands narrow (low volatility)
    Then: Volume spike + price breaks upper band
    """
    print("\n" + "="*70)
    print("🔍 NEW PATTERN: SQUEEZE BREAKOUT")
    print("="*70)
    print("Logic: Low volatility squeeze → Volume spike → Price breaks out")
    
    all_returns = []
    signal_returns = []
    
    for ticker, df in data.items():
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        volume = df['Volume'].values
        
        for i in range(30, len(close) - forward_days):
            # Bollinger Bands (20-day)
            sma20 = np.mean(close[i-20:i])
            std20 = np.std(close[i-20:i])
            upper_band = sma20 + 2 * std20
            
            # Band width (squeeze indicator)
            band_width = (4 * std20) / sma20
            
            # Historical band width (look for squeeze)
            hist_widths = []
            for j in range(i-20, i):
                h_sma = np.mean(close[j-20:j])
                h_std = np.std(close[j-20:j])
                hist_widths.append((4 * h_std) / h_sma)
            avg_width = np.mean(hist_widths)
            
            # Volume
            base_vol = np.mean(volume[i-20:i-5])
            rel_vol = volume[i] / base_vol if base_vol > 0 else 1
            
            # Forward return (for all days)
            fwd_ret = ((close[i + forward_days] - close[i]) / close[i]) * 100
            all_returns.append(fwd_ret)
            
            # SQUEEZE BREAKOUT SIGNAL
            squeeze = band_width < avg_width * 0.7  # Bands 30% narrower than normal
            vol_spike = rel_vol > 1.5
            price_break = close[i] > upper_band
            
            if squeeze and vol_spike and price_break:
                signal_returns.append(fwd_ret)
    
    if len(signal_returns) < 10:
        print(f"  Not enough signals: {len(signal_returns)}")
        return
    
    p_val, avg_ret = monte_carlo(signal_returns, all_returns)
    wr = np.mean([r > 0 for r in signal_returns]) * 100
    
    print(f"\n  RESULTS:")
    print(f"  Signals: {len(signal_returns)}")
    print(f"  Win Rate: {wr:.1f}%")
    print(f"  Avg Return: {avg_ret:+.2f}%")
    print(f"  P-value: {p_val:.4f} {'✅ SIGNIFICANT!' if p_val < 0.05 else '❌'}")

# =============================================================================
# NEW PATTERN 2: GAP AND GO
# Morning gap up + first hour volume confirms
# =============================================================================

def test_gap_and_go(data, forward_days=5):
    """
    Gap up > 5% at open
    First day closes strong (CLV > 0.6)
    """
    print("\n" + "="*70)
    print("🔍 NEW PATTERN: GAP AND GO")
    print("="*70)
    print("Logic: Gap up > 5% + strong close = momentum continuation")
    
    all_returns = []
    signal_returns = []
    
    for ticker, df in data.items():
        close = df['Close'].values
        open_p = df['Open'].values
        high = df['High'].values
        low = df['Low'].values
        
        for i in range(5, len(close) - forward_days):
            prev_close = close[i-1]
            
            # Gap %
            gap = ((open_p[i] - prev_close) / prev_close) * 100
            
            # CLV
            day_range = high[i] - low[i]
            clv = (close[i] - low[i]) / day_range if day_range > 0 else 0.5
            
            # Forward return
            fwd_ret = ((close[i + forward_days] - close[i]) / close[i]) * 100
            all_returns.append(fwd_ret)
            
            # GAP AND GO SIGNAL
            big_gap = gap > 5
            strong_close = clv > 0.6
            
            if big_gap and strong_close:
                signal_returns.append(fwd_ret)
    
    if len(signal_returns) < 10:
        print(f"  Not enough signals: {len(signal_returns)}")
        return
    
    p_val, avg_ret = monte_carlo(signal_returns, all_returns)
    wr = np.mean([r > 0 for r in signal_returns]) * 100
    
    print(f"\n  RESULTS:")
    print(f"  Signals: {len(signal_returns)}")
    print(f"  Win Rate: {wr:.1f}%")
    print(f"  Avg Return: {avg_ret:+.2f}%")
    print(f"  P-value: {p_val:.4f} {'✅ SIGNIFICANT!' if p_val < 0.05 else '❌'}")

# =============================================================================
# NEW PATTERN 3: VOLUME CLIMAX REVERSAL
# Extreme volume + extreme price = exhaustion
# =============================================================================

def test_volume_climax(data, forward_days=10):
    """
    After big run (up 50%+ in 20 days)
    Volume spikes to 5x+ normal
    = Potential exhaustion top
    """
    print("\n" + "="*70)
    print("🔍 NEW PATTERN: VOLUME CLIMAX (Exhaustion)")
    print("="*70)
    print("Logic: After big run + extreme volume = potential top")
    
    all_returns = []
    signal_returns = []
    
    for ticker, df in data.items():
        close = df['Close'].values
        volume = df['Volume'].values
        
        for i in range(25, len(close) - forward_days):
            # 20-day price change
            price_20d = ((close[i] - close[i-20]) / close[i-20]) * 100
            
            # Volume spike
            base_vol = np.mean(volume[i-25:i-5])
            rel_vol = volume[i] / base_vol if base_vol > 0 else 1
            
            # Forward return
            fwd_ret = ((close[i + forward_days] - close[i]) / close[i]) * 100
            all_returns.append(fwd_ret)
            
            # CLIMAX SIGNAL (potential SHORT or take profits)
            big_run = price_20d > 50
            extreme_vol = rel_vol > 5
            
            if big_run and extreme_vol:
                signal_returns.append(fwd_ret)  # Track what happens AFTER climax
    
    if len(signal_returns) < 10:
        print(f"  Not enough signals: {len(signal_returns)}")
        return
    
    p_val, avg_ret = monte_carlo(signal_returns, all_returns)
    wr = np.mean([r < 0 for r in signal_returns]) * 100  # Win = stock goes DOWN
    
    print(f"\n  RESULTS (tracking if stocks DROP after climax):")
    print(f"  Signals: {len(signal_returns)}")
    print(f"  % That Dropped: {wr:.1f}%")
    print(f"  Avg Return: {avg_ret:+.2f}%")
    print(f"  P-value: {p_val:.4f}")
    print(f"  {'✅ CLIMAX = TAKE PROFITS!' if avg_ret < 0 else '❌ Not a reliable top'}")

# =============================================================================
# NEW PATTERN 4: POCKET PIVOT
# Volume spike on up day during pullback in uptrend
# =============================================================================

def test_pocket_pivot(data, forward_days=10):
    """
    Stock in uptrend (above 50-day MA)
    Pulls back
    Volume spike on up day = pocket pivot
    """
    print("\n" + "="*70)
    print("🔍 NEW PATTERN: POCKET PIVOT")
    print("="*70)
    print("Logic: Uptrend + pullback + volume spike on up day")
    
    all_returns = []
    signal_returns = []
    
    for ticker, df in data.items():
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        volume = df['Volume'].values
        
        for i in range(55, len(close) - forward_days):
            # 50-day MA
            ma50 = np.mean(close[i-50:i])
            above_ma = close[i] > ma50
            
            # Recent pullback (5-10% from recent high)
            high_10 = max(high[i-10:i])
            pct_from_high = ((close[i] - high_10) / high_10) * 100
            in_pullback = -10 < pct_from_high < -3
            
            # Up day
            up_day = close[i] > close[i-1]
            
            # Volume spike (higher than any down volume in last 10 days)
            down_vols = [volume[j] for j in range(i-10, i) if close[j] < close[j-1]]
            max_down_vol = max(down_vols) if down_vols else 0
            vol_spike = volume[i] > max_down_vol
            
            # Forward return
            fwd_ret = ((close[i + forward_days] - close[i]) / close[i]) * 100
            all_returns.append(fwd_ret)
            
            # POCKET PIVOT SIGNAL
            if above_ma and in_pullback and up_day and vol_spike:
                signal_returns.append(fwd_ret)
    
    if len(signal_returns) < 10:
        print(f"  Not enough signals: {len(signal_returns)}")
        return
    
    p_val, avg_ret = monte_carlo(signal_returns, all_returns)
    wr = np.mean([r > 0 for r in signal_returns]) * 100
    
    print(f"\n  RESULTS:")
    print(f"  Signals: {len(signal_returns)}")
    print(f"  Win Rate: {wr:.1f}%")
    print(f"  Avg Return: {avg_ret:+.2f}%")
    print(f"  P-value: {p_val:.4f} {'✅ SIGNIFICANT!' if p_val < 0.05 else '❌'}")

# =============================================================================
# NEW PATTERN 5: RELATIVE STRENGTH LEADER
# Stock holding up better than sector/market during selloff
# =============================================================================

def test_relative_strength(data, forward_days=10):
    """
    When sector down, stock holds flat or green
    = Relative strength leader
    """
    print("\n" + "="*70)
    print("🔍 NEW PATTERN: RELATIVE STRENGTH LEADER")
    print("="*70)
    print("Logic: When others drop, leaders hold = strength")
    
    all_returns = []
    signal_returns = []
    
    # First, compute sector average returns for each day
    sector_returns = {}
    for ticker, df in data.items():
        close = df['Close'].values
        dates = df.index.tolist()
        for i in range(1, len(close)):
            date = dates[i]
            daily_ret = ((close[i] - close[i-1]) / close[i-1]) * 100
            if date not in sector_returns:
                sector_returns[date] = []
            sector_returns[date].append(daily_ret)
    
    # Calculate market average per day
    market_avg = {date: np.mean(rets) for date, rets in sector_returns.items()}
    
    for ticker, df in data.items():
        close = df['Close'].values
        dates = df.index.tolist()
        
        for i in range(5, len(close) - forward_days):
            date = dates[i]
            if date not in market_avg:
                continue
            
            # Today's return
            daily_ret = ((close[i] - close[i-1]) / close[i-1]) * 100
            mkt_ret = market_avg[date]
            
            # Relative strength = stock vs market
            relative = daily_ret - mkt_ret
            
            # Forward return
            fwd_ret = ((close[i + forward_days] - close[i]) / close[i]) * 100
            all_returns.append(fwd_ret)
            
            # RS LEADER SIGNAL
            # Market down but stock up or flat
            market_weak = mkt_ret < -2
            stock_strong = daily_ret > 0
            
            if market_weak and stock_strong:
                signal_returns.append(fwd_ret)
    
    if len(signal_returns) < 10:
        print(f"  Not enough signals: {len(signal_returns)}")
        return
    
    p_val, avg_ret = monte_carlo(signal_returns, all_returns)
    wr = np.mean([r > 0 for r in signal_returns]) * 100
    
    print(f"\n  RESULTS:")
    print(f"  Signals: {len(signal_returns)}")
    print(f"  Win Rate: {wr:.1f}%")
    print(f"  Avg Return: {avg_ret:+.2f}%")
    print(f"  P-value: {p_val:.4f} {'✅ SIGNIFICANT!' if p_val < 0.05 else '❌'}")

# =============================================================================
# NEW PATTERN 6: EARNINGS MOMENTUM
# After big earnings gap, continuation pattern
# =============================================================================

def test_earnings_momentum(data, forward_days=10):
    """
    Big gap (>10%) = likely earnings
    If holds gains for 3 days = momentum continues
    """
    print("\n" + "="*70)
    print("🔍 NEW PATTERN: POST-GAP MOMENTUM")
    print("="*70)
    print("Logic: Big gap + holds 3 days = continuation")
    
    all_returns = []
    signal_returns = []
    
    for ticker, df in data.items():
        close = df['Close'].values
        open_p = df['Open'].values
        
        for i in range(5, len(close) - forward_days):
            prev_close = close[i-4]  # 3 days ago
            gap_day_close = close[i-3]
            gap_day_open = open_p[i-3]
            
            # Was there a big gap 3 days ago?
            gap = ((gap_day_open - prev_close) / prev_close) * 100
            big_gap = gap > 10
            
            # Has it held gains for 3 days?
            held_gains = close[i] > gap_day_close * 0.95  # Within 5% of gap day close
            
            # Forward return
            fwd_ret = ((close[i + forward_days] - close[i]) / close[i]) * 100
            all_returns.append(fwd_ret)
            
            if big_gap and held_gains:
                signal_returns.append(fwd_ret)
    
    if len(signal_returns) < 10:
        print(f"  Not enough signals: {len(signal_returns)}")
        return
    
    p_val, avg_ret = monte_carlo(signal_returns, all_returns)
    wr = np.mean([r > 0 for r in signal_returns]) * 100
    
    print(f"\n  RESULTS:")
    print(f"  Signals: {len(signal_returns)}")
    print(f"  Win Rate: {wr:.1f}%")
    print(f"  Avg Return: {avg_ret:+.2f}%")
    print(f"  P-value: {p_val:.4f} {'✅ SIGNIFICANT!' if p_val < 0.05 else '❌'}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("""
    🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺
    
              PHASE 2C: NEW PATTERN DISCOVERY
              
              Going OFF LEASH
              Testing 6 new patterns
              
    🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺
    """)
    
    print("Fetching 2 years of data for 43 tickers...")
    tickers = get_all_tickers()
    data = fetch_data(tickers)
    print(f"Loaded {len(data)} tickers\n")
    
    # Test all new patterns
    test_squeeze_breakout(data)
    test_gap_and_go(data)
    test_volume_climax(data)
    test_pocket_pivot(data)
    test_relative_strength(data)
    test_earnings_momentum(data)
    
    print("\n" + "="*70)
    print("🐺 NEW PATTERN DISCOVERY COMPLETE")
    print("="*70)
    print("""
    Look for p-values < 0.05 = EDGE FOUND!
    
    Next: Add winning patterns to the arsenal
    
    🐺 AWOOOO!
    """)
