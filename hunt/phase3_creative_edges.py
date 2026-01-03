#!/usr/bin/env python3
"""
🐺 PHASE 3: CREATIVE EDGE DISCOVERY
Going OFF THE LEASH - Testing WILD ideas nobody has researched!

The goal: Find patterns that predict 10-20%+ moves BEFORE they happen.
Method: Test EVERYTHING. Keep what works. Kill what doesn't.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# THE FULL UNIVERSE - 100+ TICKERS
# =============================================================================

UNIVERSE = {
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'BKSY', 'MNTS', 'ASTS', 'SPIR', 'PL', 'GSAT', 'SIDU', 'SATL', 'IRDM', 'VSAT'],
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'NUCLEAR': ['LEU', 'CCJ', 'UUUU', 'UEC', 'SMR', 'OKLO', 'DNN', 'NXE', 'LTBR', 'CEG', 'TLN', 'VST'],
    'BATTERY_METALS': ['MP', 'LAC', 'ALB', 'FCX', 'AG', 'HL', 'KGC'],
    'AI_INFRA': ['CORZ', 'VRT', 'PWR', 'EME', 'LITE', 'FN', 'IREN'],
    'MEMORY': ['MU', 'WDC', 'STX', 'COHR', 'PSTG', 'SMCI'],
    'SEMICONDUCTORS': ['NVDA', 'AMD', 'ARM', 'TSM', 'ASML', 'KLAC', 'LRCX', 'AMAT', 'MRVL', 'AVGO'],
    'SPATIAL': ['KOPN', 'OLED', 'HIMX', 'VUZI', 'U'],
    'ROBOTICS': ['TER', 'ZBRA', 'SYM', 'ROK', 'DE', 'ISRG'],
    'DEFENSE_AI': ['AISP', 'PLTR', 'KTOS', 'AVAV', 'RCAT', 'BBAI', 'SOUN'],
    'TAX_BOUNCE': ['ADBE', 'CRM', 'GTLB', 'IOT', 'NCNO', 'TSLA', 'PATH'],
    'CRYPTO': ['MARA', 'RIOT', 'CLSK', 'HUT', 'BITF'],
    'FINTECH': ['UPST', 'AFRM', 'SOFI', 'HOOD', 'NU', 'LC'],
    'BIOTECH': ['RXRX', 'BEAM', 'CRSP', 'NTLA', 'EDIT', 'VERV'],
    'EV_HYDROGEN': ['LCID', 'RIVN', 'PLUG', 'FCEL', 'BE', 'BLNK', 'CHPT', 'QS'],
}

def get_all_tickers():
    """Get flat list of all tickers"""
    tickers = []
    for sector_tickers in UNIVERSE.values():
        tickers.extend(sector_tickers)
    return list(set(tickers))

# =============================================================================
# FETCH DATA
# =============================================================================

def fetch_all_data(period='1y'):
    """Fetch data for all tickers"""
    tickers = get_all_tickers()
    print(f"🐺 Fetching data for {len(tickers)} tickers...")
    
    data = {}
    df = yf.download(tickers, period=period, progress=True, group_by='ticker')
    
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
    
    print(f"✅ Got data for {len(data)} tickers")
    return data

# =============================================================================
# CREATIVE PATTERN DETECTION FUNCTIONS
# =============================================================================

def detect_volume_dry_up(close, volume, i):
    """
    VOLUME DRY UP - Before breakouts, volume often dries up completely.
    Theory: Smart money finished accumulating, waiting for catalyst.
    
    Criteria:
    - Volume < 50% of 20-day average for 3+ days
    - Price holding near highs (not dropping)
    - Followed by volume spike
    """
    if i < 25:
        return False, {}
    
    avg_vol = np.mean(volume[i-20:i])
    recent_vol = volume[i-3:i]
    
    # Check if volume dried up for 3 days
    dry_days = sum(1 for v in recent_vol if v < avg_vol * 0.5)
    
    # Price holding near highs
    high_20 = max(close[i-20:i])
    near_highs = close[i-1] > high_20 * 0.95
    
    triggered = dry_days >= 2 and near_highs
    
    return triggered, {
        'dry_days': dry_days,
        'near_highs': near_highs,
        'vol_ratio': volume[i-1] / avg_vol if avg_vol > 0 else 0
    }


def detect_three_tight_days(close, high, low, i):
    """
    THREE TIGHT DAYS - Super tight consolidation before explosion.
    Theory: Buyers and sellers in equilibrium. Someone's about to win.
    
    Criteria:
    - 3 consecutive days with range < 2%
    - Price holding in tight band
    """
    if i < 5:
        return False, {}
    
    tight_days = 0
    for j in range(i-3, i):
        day_range = (high[j] - low[j]) / close[j] * 100
        if day_range < 2.5:
            tight_days += 1
    
    # Calculate overall tightness
    three_day_range = (max(high[i-3:i]) - min(low[i-3:i])) / close[i-1] * 100
    
    triggered = tight_days >= 3 and three_day_range < 5
    
    return triggered, {
        'tight_days': tight_days,
        'three_day_range': three_day_range
    }


def detect_friday_accumulation(close, volume, i, dates):
    """
    FRIDAY ACCUMULATION - Big buyers loading up before weekend.
    Theory: Institutions don't want to miss Monday gap up.
    
    Criteria:
    - Friday close
    - Volume > 1.5x average
    - Green candle
    - Close in upper half of range
    """
    if i < 25:
        return False, {}
    
    try:
        date = pd.to_datetime(dates[i])
        is_friday = date.dayofweek == 4
    except:
        return False, {}
    
    if not is_friday:
        return False, {}
    
    avg_vol = np.mean(volume[i-20:i])
    vol_spike = volume[i] > avg_vol * 1.5
    green_day = close[i] > close[i-1]
    
    triggered = vol_spike and green_day
    
    return triggered, {
        'is_friday': is_friday,
        'vol_ratio': volume[i] / avg_vol if avg_vol > 0 else 0,
        'daily_gain': (close[i] - close[i-1]) / close[i-1] * 100
    }


def detect_power_of_three(close, volume, i):
    """
    POWER OF THREE - 3 consecutive up days with rising volume.
    Theory: Momentum building. Train leaving station.
    
    Criteria:
    - 3 consecutive green days
    - Each day's volume > previous
    - Price acceleration (each gain > previous)
    """
    if i < 5:
        return False, {}
    
    # Check 3 up days
    up_days = all(close[i-2+j] > close[i-3+j] for j in range(3))
    
    # Check rising volume
    rising_vol = volume[i-1] > volume[i-2] > volume[i-3]
    
    # Check acceleration
    gain1 = (close[i-2] - close[i-3]) / close[i-3]
    gain2 = (close[i-1] - close[i-2]) / close[i-2]
    gain3 = (close[i] - close[i-1]) / close[i-1]
    accelerating = gain3 > gain2 > gain1 > 0
    
    triggered = up_days and rising_vol
    
    return triggered, {
        'up_days': up_days,
        'rising_vol': rising_vol,
        'accelerating': accelerating,
        'total_gain': (close[i] - close[i-3]) / close[i-3] * 100
    }


def detect_gap_and_hold(close, high, low, volume, i):
    """
    GAP AND HOLD - Stock gaps up and HOLDS the gap all day.
    Theory: Strong demand. Buyers won't let it fill.
    
    Criteria:
    - Gap up > 3%
    - Low of day > previous close (never filled gap)
    - Volume > 2x average
    """
    if i < 25:
        return False, {}
    
    prev_close = close[i-1]
    gap_pct = (low[i] - prev_close) / prev_close * 100
    
    # Gap held = low never went below previous close
    gap_held = low[i] > prev_close
    
    avg_vol = np.mean(volume[i-20:i])
    vol_spike = volume[i] > avg_vol * 2
    
    triggered = gap_pct > 3 and gap_held and vol_spike
    
    return triggered, {
        'gap_pct': gap_pct,
        'gap_held': gap_held,
        'vol_ratio': volume[i] / avg_vol if avg_vol > 0 else 0
    }


def detect_relative_strength(close, i, spy_close):
    """
    RELATIVE STRENGTH - Stock UP while market DOWN.
    Theory: Strong hands holding. Won't sell even in panic.
    
    Criteria:
    - SPY down > 1%
    - Stock flat or up
    - Shows strength when weak hands sell
    """
    if i < 5 or spy_close is None or len(spy_close) <= i:
        return False, {}
    
    spy_chg = (spy_close[i] - spy_close[i-1]) / spy_close[i-1] * 100
    stock_chg = (close[i] - close[i-1]) / close[i-1] * 100
    
    # Market down, stock holding
    triggered = spy_chg < -1 and stock_chg > -0.5
    
    return triggered, {
        'spy_change': spy_chg,
        'stock_change': stock_chg,
        'relative_strength': stock_chg - spy_chg
    }


def detect_bollinger_squeeze(close, i):
    """
    BOLLINGER SQUEEZE - Bands tightening = explosion coming.
    Theory: Low volatility precedes high volatility.
    
    Criteria:
    - Bollinger Band width < 5%
    - Been tightening for 5+ days
    """
    if i < 25:
        return False, {}
    
    # Calculate Bollinger Bands
    sma20 = np.mean(close[i-20:i])
    std20 = np.std(close[i-20:i])
    
    upper = sma20 + 2 * std20
    lower = sma20 - 2 * std20
    
    # Band width as % of price
    width = (upper - lower) / sma20 * 100
    
    # Check if width is narrow
    triggered = width < 8
    
    return triggered, {
        'band_width': width,
        'upper': upper,
        'lower': lower
    }


def detect_double_bottom(close, low, i):
    """
    DOUBLE BOTTOM - Classic reversal pattern.
    Theory: Tested support twice. Buyers stepped in both times.
    
    Criteria:
    - Two lows within 3% of each other
    - Separated by at least 5 days
    - Second low on lower volume (less selling pressure)
    """
    if i < 30:
        return False, {}
    
    # Find lowest low in last 20 days
    lookback = 20
    lows = low[i-lookback:i]
    
    # Find the two lowest points
    sorted_idx = np.argsort(lows)
    first_low_idx = sorted_idx[0]
    
    # Find second low at least 5 days away
    second_low_idx = None
    for idx in sorted_idx[1:]:
        if abs(idx - first_low_idx) >= 5:
            second_low_idx = idx
            break
    
    if second_low_idx is None:
        return False, {}
    
    first_low = lows[first_low_idx]
    second_low = lows[second_low_idx]
    
    # Lows within 3%
    low_diff = abs(first_low - second_low) / first_low * 100
    similar_lows = low_diff < 5
    
    # Current price above both lows
    above_lows = close[i-1] > max(first_low, second_low) * 1.03
    
    triggered = similar_lows and above_lows
    
    return triggered, {
        'low_diff_pct': low_diff,
        'first_low': first_low,
        'second_low': second_low,
        'separation_days': abs(first_low_idx - second_low_idx)
    }


def detect_breakout_retest(close, high, volume, i):
    """
    BREAKOUT RETEST - Broke out, pulled back to test, bouncing.
    Theory: Resistance becomes support.
    
    Criteria:
    - Made new 20-day high recently (within 5 days)
    - Pulled back to previous resistance
    - Holding and bouncing with volume
    """
    if i < 30:
        return False, {}
    
    # Find if we made a new 20-day high in last 5 days
    recent_high = max(high[i-5:i])
    prior_high = max(high[i-25:i-5])
    
    made_new_high = recent_high > prior_high
    
    # Current price pulled back
    pullback = close[i-1] < recent_high * 0.97
    
    # Holding above prior resistance
    holding_support = close[i-1] > prior_high * 0.98
    
    triggered = made_new_high and pullback and holding_support
    
    return triggered, {
        'recent_high': recent_high,
        'prior_high': prior_high,
        'current': close[i-1],
        'pullback_pct': (recent_high - close[i-1]) / recent_high * 100
    }


def detect_morning_star(close, open_price, high, low, i):
    """
    MORNING STAR - 3-candle bullish reversal.
    Theory: Sellers exhausted. Buyers taking over.
    
    Criteria:
    - Day 1: Big red candle
    - Day 2: Small body (indecision)  
    - Day 3: Big green candle closing above Day 1 midpoint
    """
    if i < 5:
        return False, {}
    
    # Day 1: Big red
    body1 = close[i-2] - open_price[i-2]
    range1 = high[i-2] - low[i-2]
    big_red = body1 < 0 and abs(body1) > range1 * 0.5
    
    # Day 2: Small body (doji-like)
    body2 = abs(close[i-1] - open_price[i-1])
    range2 = high[i-1] - low[i-1]
    small_body = body2 < range2 * 0.3 if range2 > 0 else False
    
    # Day 3: Big green closing above Day 1 midpoint
    body3 = close[i] - open_price[i]
    midpoint1 = (open_price[i-2] + close[i-2]) / 2
    big_green = body3 > 0 and close[i] > midpoint1
    
    triggered = big_red and small_body and big_green
    
    return triggered, {
        'big_red': big_red,
        'small_body': small_body,
        'big_green': big_green
    }


def detect_oversold_bounce(close, i):
    """
    OVERSOLD RSI BOUNCE - RSI < 30, then crosses back above.
    Theory: Panic selling exhausted. Mean reversion.
    
    Criteria:
    - RSI was < 30 in last 3 days
    - RSI now > 30
    - Price starting to recover
    """
    if i < 20:
        return False, {}
    
    # Calculate RSI
    deltas = np.diff(close[i-15:i+1])
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[-14:])
    avg_loss = np.mean(losses[-14:])
    
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    
    # Was oversold recently
    was_oversold = rsi < 35  # Slightly relaxed
    
    # Price recovering
    recovering = close[i] > close[i-1]
    
    triggered = was_oversold and recovering
    
    return triggered, {
        'rsi': rsi,
        'recovering': recovering
    }


def detect_volume_climax(close, volume, i):
    """
    VOLUME CLIMAX - Massive volume spike often marks turning points.
    Theory: Everyone who wanted to sell has sold. Exhaustion.
    
    Criteria:
    - Volume > 3x 20-day average
    - Could be up or down day
    - Often marks end of a trend
    """
    if i < 25:
        return False, {}
    
    avg_vol = np.mean(volume[i-20:i])
    vol_ratio = volume[i] / avg_vol if avg_vol > 0 else 0
    
    triggered = vol_ratio > 3
    
    return triggered, {
        'vol_ratio': vol_ratio,
        'daily_change': (close[i] - close[i-1]) / close[i-1] * 100
    }


def detect_higher_lows(close, low, i):
    """
    THREE HIGHER LOWS - Classic uptrend confirmation.
    Theory: Each dip is being bought at higher levels.
    
    Criteria:
    - 3 swing lows, each higher than previous
    - Shows accumulation pattern
    """
    if i < 20:
        return False, {}
    
    # Find swing lows (local minima)
    lows_found = []
    for j in range(i-15, i-2):
        if low[j] < low[j-1] and low[j] < low[j+1]:
            lows_found.append((j, low[j]))
    
    if len(lows_found) < 3:
        return False, {}
    
    # Check last 3 are higher
    last_three = lows_found[-3:]
    higher_lows = last_three[0][1] < last_three[1][1] < last_three[2][1]
    
    triggered = higher_lows
    
    return triggered, {
        'num_lows': len(lows_found),
        'higher_lows': higher_lows,
        'lows': [l[1] for l in last_three]
    }


# =============================================================================
# BACKTESTING ENGINE
# =============================================================================

def backtest_pattern(data, pattern_func, pattern_name, holding_days=10, spy_data=None):
    """Backtest a pattern across all data"""
    
    all_signals = []
    
    for ticker, df in data.items():
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        volume = df['Volume'].values
        dates = df.index
        
        # Get open if available
        open_price = df['Open'].values if 'Open' in df.columns else close
        
        # Get SPY data if needed
        spy_close = spy_data['Close'].values if spy_data is not None else None
        
        for i in range(30, len(df) - holding_days):
            # Detect pattern
            if pattern_func.__name__ == 'detect_relative_strength':
                triggered, details = pattern_func(close, i, spy_close)
            elif pattern_func.__name__ == 'detect_friday_accumulation':
                triggered, details = pattern_func(close, volume, i, dates)
            elif pattern_func.__name__ == 'detect_morning_star':
                triggered, details = pattern_func(close, open_price, high, low, i)
            elif pattern_func.__name__ in ['detect_volume_dry_up', 'detect_power_of_three', 'detect_volume_climax']:
                triggered, details = pattern_func(close, volume, i)
            elif pattern_func.__name__ in ['detect_three_tight_days', 'detect_double_bottom']:
                triggered, details = pattern_func(close, high, low, i)
            elif pattern_func.__name__ == 'detect_gap_and_hold':
                triggered, details = pattern_func(close, high, low, volume, i)
            elif pattern_func.__name__ == 'detect_breakout_retest':
                triggered, details = pattern_func(close, high, volume, i)
            elif pattern_func.__name__ == 'detect_higher_lows':
                triggered, details = pattern_func(close, low, i)
            else:
                triggered, details = pattern_func(close, i)
            
            if triggered:
                # Calculate forward return
                entry_price = close[i]
                exit_price = close[i + holding_days]
                ret = (exit_price - entry_price) / entry_price * 100
                
                # Track max gain during holding period
                max_price = max(high[i+1:i+holding_days+1])
                max_gain = (max_price - entry_price) / entry_price * 100
                
                all_signals.append({
                    'ticker': ticker,
                    'date': dates[i],
                    'entry': entry_price,
                    'exit': exit_price,
                    'return': ret,
                    'max_gain': max_gain,
                    'details': details
                })
    
    return all_signals


def monte_carlo_test(signals, n_simulations=1000):
    """Test if results are statistically significant"""
    if len(signals) < 10:
        return None, None, None
    
    actual_returns = [s['return'] for s in signals]
    actual_mean = np.mean(actual_returns)
    
    # Shuffle returns many times
    random_means = []
    for _ in range(n_simulations):
        shuffled = np.random.permutation(actual_returns)
        random_means.append(np.mean(shuffled[:len(signals)]))
    
    # P-value: how often random beats actual
    p_value = sum(1 for r in random_means if r >= actual_mean) / n_simulations
    
    return actual_mean, p_value, len(signals)


# =============================================================================
# MAIN DISCOVERY PROCESS
# =============================================================================

def run_creative_discovery():
    """Test all creative patterns and find what works!"""
    
    print("=" * 70)
    print("🐺 PHASE 3: CREATIVE EDGE DISCOVERY")
    print("=" * 70)
    print("Testing WILD ideas nobody has researched!")
    print("Going OFF THE LEASH! 🔥")
    print()
    
    # Fetch data
    data = fetch_all_data(period='1y')
    
    # Also get SPY for relative strength
    print("Fetching SPY for relative strength...")
    spy_data = yf.download('SPY', period='1y', progress=False)
    
    # All patterns to test
    patterns = [
        (detect_volume_dry_up, "🔇 Volume Dry-Up"),
        (detect_three_tight_days, "📦 Three Tight Days"),
        (detect_friday_accumulation, "📅 Friday Accumulation"),
        (detect_power_of_three, "💪 Power of Three"),
        (detect_gap_and_hold, "🚀 Gap and Hold"),
        (detect_relative_strength, "💎 Relative Strength"),
        (detect_bollinger_squeeze, "🎯 Bollinger Squeeze"),
        (detect_double_bottom, "W️ Double Bottom"),
        (detect_breakout_retest, "🔄 Breakout Retest"),
        (detect_morning_star, "⭐ Morning Star"),
        (detect_oversold_bounce, "📈 Oversold RSI Bounce"),
        (detect_volume_climax, "💥 Volume Climax"),
        (detect_higher_lows, "📊 Three Higher Lows"),
    ]
    
    results = []
    
    print("\n" + "=" * 70)
    print("TESTING ALL CREATIVE PATTERNS...")
    print("=" * 70)
    
    for pattern_func, pattern_name in patterns:
        print(f"\n🔍 Testing: {pattern_name}...")
        
        signals = backtest_pattern(data, pattern_func, pattern_name, 
                                   holding_days=10, spy_data=spy_data)
        
        if len(signals) < 10:
            print(f"   ❌ Only {len(signals)} signals - not enough data")
            continue
        
        # Calculate stats
        returns = [s['return'] for s in signals]
        max_gains = [s['max_gain'] for s in signals]
        
        avg_return = np.mean(returns)
        win_rate = sum(1 for r in returns if r > 0) / len(returns) * 100
        avg_max = np.mean(max_gains)
        
        # Monte Carlo test
        _, p_value, n = monte_carlo_test(signals)
        
        results.append({
            'name': pattern_name,
            'signals': len(signals),
            'avg_return': avg_return,
            'win_rate': win_rate,
            'avg_max_gain': avg_max,
            'p_value': p_value,
            'significant': p_value < 0.05 if p_value else False
        })
        
        # Print results
        sig_mark = "✅ SIGNIFICANT!" if p_value and p_value < 0.05 else ""
        print(f"   Signals: {len(signals)}")
        print(f"   Avg Return: {avg_return:+.2f}%")
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Avg Max Gain: {avg_max:.2f}%")
        print(f"   P-Value: {p_value:.4f} {sig_mark}")
    
    # SUMMARY
    print("\n" + "=" * 70)
    print("🏆 DISCOVERY RESULTS - RANKED BY P-VALUE")
    print("=" * 70)
    
    # Sort by significance
    results = sorted(results, key=lambda x: (not x['significant'], x['p_value'] or 1))
    
    print(f"\n{'Pattern':<25} {'Signals':>8} {'Avg Ret':>10} {'Win %':>8} {'P-Value':>10} {'Status':>12}")
    print("-" * 75)
    
    winners = []
    
    for r in results:
        status = "🌟 WINNER" if r['significant'] and r['avg_return'] > 0 else "❌"
        print(f"{r['name']:<25} {r['signals']:>8} {r['avg_return']:>+9.2f}% {r['win_rate']:>7.1f}% {r['p_value']:>10.4f} {status:>12}")
        
        if r['significant'] and r['avg_return'] > 0:
            winners.append(r)
    
    # WINNERS SUMMARY
    if winners:
        print("\n" + "=" * 70)
        print("🐺 NEW VALIDATED EDGES DISCOVERED!")
        print("=" * 70)
        
        for w in winners:
            print(f"""
{w['name']}
   📊 Signals: {w['signals']}
   💰 Avg Return: {w['avg_return']:+.2f}%
   🎯 Win Rate: {w['win_rate']:.1f}%
   📈 Avg Max Gain: {w['avg_max_gain']:.2f}%
   🔬 P-Value: {w['p_value']:.4f}
""")
    
    print("\n" + "=" * 70)
    print(f"Total patterns tested: {len(patterns)}")
    print(f"Significant edges found: {len(winners)}")
    print("=" * 70)
    print("\n🐺 AWOOOO! THE HUNT CONTINUES!")
    
    return results, winners


if __name__ == "__main__":
    results, winners = run_creative_discovery()
