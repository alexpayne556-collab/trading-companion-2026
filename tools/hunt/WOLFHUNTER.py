#!/usr/bin/env python3
"""
===============================================================================
🐺 WOLFHUNTER - BRUTE FORCE PATTERN DISCOVERY ENGINE
===============================================================================
This is NOT a human-scale tool.
This tests THOUSANDS of pattern combinations in parallel.
This finds what humans CAN'T see.

Built by Brokkr for the Wolf Pack
January 3, 2026

AWOOOO 🐺
===============================================================================
"""

import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats
from itertools import combinations, product
from joblib import Parallel, delayed
import warnings
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import multiprocessing

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION - MACHINE SCALE
# ============================================================================

# The FULL universe - not 43 tickers, HUNDREDS
UNIVERSE = {
    # Original sectors
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'BKSY', 'ASTS', 'SPIR', 'PL', 'IRDM'],
    'NUCLEAR': ['LEU', 'CCJ', 'UUUU', 'UEC', 'SMR', 'OKLO', 'DNN', 'NXE', 'CEG', 'VST'],
    'AI_CHIPS': ['NVDA', 'AMD', 'AVGO', 'MRVL', 'ARM', 'TSM', 'ASML', 'AMAT', 'LRCX', 'KLAC'],
    'AI_SOFTWARE': ['PLTR', 'AI', 'PATH', 'SNOW', 'MDB', 'DDOG', 'NET', 'CRWD', 'ZS', 'PANW'],
    'MEMORY': ['MU', 'WDC', 'STX', 'NAND', 'AEHR'],
    'CRYPTO': ['MARA', 'RIOT', 'CLSK', 'COIN', 'MSTR', 'HUT', 'BITF', 'CIFR'],
    'BIOTECH': ['MRNA', 'BNTX', 'NVAX', 'VRTX', 'REGN', 'BIIB', 'GILD', 'AMGN'],
    'DEFENSE': ['LMT', 'RTX', 'NOC', 'GD', 'BA', 'LDOS', 'KTOS', 'RCAT'],
    'EV': ['TSLA', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'CHPT', 'BLNK'],
    'FINTECH': ['SQ', 'PYPL', 'AFRM', 'UPST', 'SOFI', 'NU', 'HOOD'],
    'CLEAN_ENERGY': ['ENPH', 'SEDG', 'FSLR', 'RUN', 'PLUG', 'BE', 'NOVA'],
    'METALS': ['MP', 'LAC', 'ALB', 'FCX', 'NEM', 'GOLD', 'SLV'],
    # Add major indices for regime detection
    'INDICES': ['SPY', 'QQQ', 'IWM', 'VIX', 'TLT', 'GLD', 'BTC-USD'],
}

# All tickers flat
ALL_TICKERS = []
TICKER_SECTOR = {}
for sector, tickers in UNIVERSE.items():
    for ticker in tickers:
        if ticker not in ALL_TICKERS:
            ALL_TICKERS.append(ticker)
            TICKER_SECTOR[ticker] = sector

print(f"🐺 WOLFHUNTER initialized with {len(ALL_TICKERS)} tickers across {len(UNIVERSE)} sectors")

# ============================================================================
# THE CONDITIONS POOL - 50+ VARIABLES
# ============================================================================

CONDITIONS = {
    # Relative Volume conditions
    'rel_vol_1d': [
        ('rel_vol_1d > 1.5', lambda df: df['rel_vol_1d'] > 1.5),
        ('rel_vol_1d > 2.0', lambda df: df['rel_vol_1d'] > 2.0),
        ('rel_vol_1d > 2.5', lambda df: df['rel_vol_1d'] > 2.5),
        ('rel_vol_1d > 3.0', lambda df: df['rel_vol_1d'] > 3.0),
        ('rel_vol_1d < 0.5', lambda df: df['rel_vol_1d'] < 0.5),  # Volume dry-up
    ],
    'rel_vol_5d': [
        ('rel_vol_5d > 1.2', lambda df: df['rel_vol_5d'] > 1.2),
        ('rel_vol_5d > 1.5', lambda df: df['rel_vol_5d'] > 1.5),
        ('rel_vol_5d > 2.0', lambda df: df['rel_vol_5d'] > 2.0),
    ],
    
    # Price change conditions
    'price_change_1d': [
        ('chg_1d < -5%', lambda df: df['chg_1d'] < -0.05),
        ('chg_1d < -3%', lambda df: df['chg_1d'] < -0.03),
        ('chg_1d < -2%', lambda df: df['chg_1d'] < -0.02),
        ('chg_1d > 2%', lambda df: df['chg_1d'] > 0.02),
        ('chg_1d > 3%', lambda df: df['chg_1d'] > 0.03),
        ('chg_1d > 5%', lambda df: df['chg_1d'] > 0.05),
        ('chg_1d flat (-1% to 1%)', lambda df: (df['chg_1d'] > -0.01) & (df['chg_1d'] < 0.01)),
    ],
    'price_change_5d': [
        ('chg_5d < -15%', lambda df: df['chg_5d'] < -0.15),
        ('chg_5d < -10%', lambda df: df['chg_5d'] < -0.10),
        ('chg_5d < -5%', lambda df: df['chg_5d'] < -0.05),
        ('chg_5d > 5%', lambda df: df['chg_5d'] > 0.05),
        ('chg_5d > 10%', lambda df: df['chg_5d'] > 0.10),
        ('chg_5d > 15%', lambda df: df['chg_5d'] > 0.15),
    ],
    'price_change_10d': [
        ('chg_10d < -20%', lambda df: df['chg_10d'] < -0.20),
        ('chg_10d < -10%', lambda df: df['chg_10d'] < -0.10),
        ('chg_10d > 10%', lambda df: df['chg_10d'] > 0.10),
        ('chg_10d > 20%', lambda df: df['chg_10d'] > 0.20),
    ],
    
    # Distance from highs/lows
    'dist_from_high_10d': [
        ('< 5% from 10d high', lambda df: df['dist_high_10d'] < 0.05),
        ('< 10% from 10d high', lambda df: df['dist_high_10d'] < 0.10),
        ('> 20% from 10d high', lambda df: df['dist_high_10d'] > 0.20),
        ('> 30% from 10d high', lambda df: df['dist_high_10d'] > 0.30),
    ],
    'dist_from_low_10d': [
        ('< 5% from 10d low', lambda df: df['dist_low_10d'] < 0.05),
        ('< 10% from 10d low', lambda df: df['dist_low_10d'] < 0.10),
        ('> 20% from 10d low', lambda df: df['dist_low_10d'] > 0.20),
        ('> 30% from 10d low', lambda df: df['dist_low_10d'] > 0.30),
    ],
    'dist_from_high_20d': [
        ('< 5% from 20d high', lambda df: df['dist_high_20d'] < 0.05),
        ('> 25% from 20d high', lambda df: df['dist_high_20d'] > 0.25),
        ('> 40% from 20d high', lambda df: df['dist_high_20d'] > 0.40),
    ],
    
    # CLV (Close Location Value) - where price closed in daily range
    'clv_1d': [
        ('clv_1d < 0.2 (closed near low)', lambda df: df['clv'] < 0.2),
        ('clv_1d > 0.5 (closed upper half)', lambda df: df['clv'] > 0.5),
        ('clv_1d > 0.7 (closed near high)', lambda df: df['clv'] > 0.7),
        ('clv_1d > 0.8 (closed very near high)', lambda df: df['clv'] > 0.8),
    ],
    'clv_5d_avg': [
        ('clv_5d_avg < 0.3', lambda df: df['clv_5d'] < 0.3),
        ('clv_5d_avg > 0.5', lambda df: df['clv_5d'] > 0.5),
        ('clv_5d_avg > 0.6', lambda df: df['clv_5d'] > 0.6),
        ('clv_5d_avg > 0.7', lambda df: df['clv_5d'] > 0.7),
    ],
    
    # RSI conditions
    'rsi_14': [
        ('rsi < 25 (oversold)', lambda df: df['rsi_14'] < 25),
        ('rsi < 30 (oversold)', lambda df: df['rsi_14'] < 30),
        ('rsi < 40', lambda df: df['rsi_14'] < 40),
        ('rsi > 60', lambda df: df['rsi_14'] > 60),
        ('rsi > 70 (overbought)', lambda df: df['rsi_14'] > 70),
        ('rsi 40-60 (neutral)', lambda df: (df['rsi_14'] > 40) & (df['rsi_14'] < 60)),
    ],
    
    # Volatility conditions
    'volatility': [
        ('atr_pct > 5%', lambda df: df['atr_pct'] > 0.05),
        ('atr_pct > 7%', lambda df: df['atr_pct'] > 0.07),
        ('atr_pct < 3%', lambda df: df['atr_pct'] < 0.03),
        ('bb_squeeze (bands tight)', lambda df: df['bb_width'] < df['bb_width'].rolling(20).mean() * 0.5),
    ],
    
    # Volume patterns
    'volume_trend': [
        ('vol_increasing (3d)', lambda df: (df['Volume'] > df['Volume'].shift(1)) & (df['Volume'].shift(1) > df['Volume'].shift(2))),
        ('vol_decreasing (3d)', lambda df: (df['Volume'] < df['Volume'].shift(1)) & (df['Volume'].shift(1) < df['Volume'].shift(2))),
        ('vol_spike (> 3x avg)', lambda df: df['rel_vol_1d'] > 3.0),
    ],
    
    # Day of week
    'day_of_week': [
        ('monday', lambda df: df.index.dayofweek == 0),
        ('friday', lambda df: df.index.dayofweek == 4),
        ('tuesday', lambda df: df.index.dayofweek == 1),
    ],
    
    # Trend conditions
    'trend': [
        ('above_sma_20', lambda df: df['Close'] > df['sma_20']),
        ('below_sma_20', lambda df: df['Close'] < df['sma_20']),
        ('above_sma_50', lambda df: df['Close'] > df['sma_50']),
        ('below_sma_50', lambda df: df['Close'] < df['sma_50']),
        ('sma_20 > sma_50 (uptrend)', lambda df: df['sma_20'] > df['sma_50']),
        ('sma_20 < sma_50 (downtrend)', lambda df: df['sma_20'] < df['sma_50']),
    ],
    
    # Gap patterns
    'gaps': [
        ('gap_up > 2%', lambda df: (df['Open'] - df['Close'].shift(1)) / df['Close'].shift(1) > 0.02),
        ('gap_up > 5%', lambda df: (df['Open'] - df['Close'].shift(1)) / df['Close'].shift(1) > 0.05),
        ('gap_down < -2%', lambda df: (df['Open'] - df['Close'].shift(1)) / df['Close'].shift(1) < -0.02),
        ('gap_down < -5%', lambda df: (df['Open'] - df['Close'].shift(1)) / df['Close'].shift(1) < -0.05),
    ],
    
    # Candle patterns
    'candles': [
        ('doji (body < 10% of range)', lambda df: abs(df['Close'] - df['Open']) < (df['High'] - df['Low']) * 0.1),
        ('big_green (> 3% up)', lambda df: (df['Close'] - df['Open']) / df['Open'] > 0.03),
        ('big_red (> 3% down)', lambda df: (df['Open'] - df['Close']) / df['Open'] > 0.03),
        ('hammer', lambda df: ((df['High'] - df['Low']) > 3 * abs(df['Close'] - df['Open'])) & (df['Close'] > df['Open']) & ((df['Close'] - df['Low']) > 0.6 * (df['High'] - df['Low']))),
    ],
    
    # Range conditions
    'range': [
        ('tight_range_3d (< 5%)', lambda df: (df['High'].rolling(3).max() - df['Low'].rolling(3).min()) / df['Close'] < 0.05),
        ('tight_range_5d (< 7%)', lambda df: (df['High'].rolling(5).max() - df['Low'].rolling(5).min()) / df['Close'] < 0.07),
        ('wide_range_3d (> 15%)', lambda df: (df['High'].rolling(3).max() - df['Low'].rolling(3).min()) / df['Close'] > 0.15),
    ],
    
    # Consecutive patterns
    'consecutive': [
        ('3_up_days', lambda df: (df['Close'] > df['Open']) & (df['Close'].shift(1) > df['Open'].shift(1)) & (df['Close'].shift(2) > df['Open'].shift(2))),
        ('3_down_days', lambda df: (df['Close'] < df['Open']) & (df['Close'].shift(1) < df['Open'].shift(1)) & (df['Close'].shift(2) < df['Open'].shift(2))),
        ('higher_lows_3d', lambda df: (df['Low'] > df['Low'].shift(1)) & (df['Low'].shift(1) > df['Low'].shift(2))),
        ('lower_highs_3d', lambda df: (df['High'] < df['High'].shift(1)) & (df['High'].shift(1) < df['High'].shift(2))),
    ],
}

# Count total conditions
total_conditions = sum(len(v) for v in CONDITIONS.values())
print(f"📊 Total condition types: {len(CONDITIONS)}")
print(f"📊 Total individual conditions: {total_conditions}")


# ============================================================================
# DATA LOADING AND FEATURE ENGINEERING
# ============================================================================

def load_all_data(period='2y'):
    """Load data for ALL tickers at once - machine scale"""
    print(f"\n🐺 Loading {len(ALL_TICKERS)} tickers with {period} of data...")
    
    data = {}
    
    # Download all at once for efficiency
    try:
        df = yf.download(ALL_TICKERS, period=period, progress=True, group_by='ticker', threads=True)
        
        for ticker in ALL_TICKERS:
            try:
                if len(ALL_TICKERS) > 1:
                    ticker_df = df[ticker].copy()
                else:
                    ticker_df = df.copy()
                
                if len(ticker_df) < 60:  # Need at least 60 days
                    continue
                
                ticker_df = ticker_df.dropna()
                if len(ticker_df) < 60:
                    continue
                    
                data[ticker] = ticker_df
            except Exception as e:
                continue
        
    except Exception as e:
        print(f"Batch download failed: {e}, trying individual...")
        for ticker in ALL_TICKERS:
            try:
                ticker_df = yf.download(ticker, period=period, progress=False)
                if len(ticker_df) >= 60:
                    data[ticker] = ticker_df
            except:
                continue
    
    print(f"✅ Loaded {len(data)} tickers successfully")
    return data


def engineer_features(df):
    """Add ALL technical features needed for pattern detection"""
    df = df.copy()
    
    # Basic returns
    df['chg_1d'] = df['Close'].pct_change(1)
    df['chg_3d'] = df['Close'].pct_change(3)
    df['chg_5d'] = df['Close'].pct_change(5)
    df['chg_10d'] = df['Close'].pct_change(10)
    df['chg_20d'] = df['Close'].pct_change(20)
    
    # Forward returns (what we're predicting)
    df['fwd_1d'] = df['Close'].shift(-1) / df['Close'] - 1
    df['fwd_3d'] = df['Close'].shift(-3) / df['Close'] - 1
    df['fwd_5d'] = df['Close'].shift(-5) / df['Close'] - 1
    df['fwd_10d'] = df['Close'].shift(-10) / df['Close'] - 1
    df['fwd_20d'] = df['Close'].shift(-20) / df['Close'] - 1
    
    # Volume features
    df['vol_sma_20'] = df['Volume'].rolling(20).mean()
    df['rel_vol_1d'] = df['Volume'] / df['vol_sma_20']
    df['rel_vol_5d'] = df['Volume'].rolling(5).mean() / df['vol_sma_20']
    
    # CLV - Close Location Value
    df['clv'] = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'] + 0.0001)
    df['clv'] = (df['clv'] + 1) / 2  # Normalize to 0-1
    df['clv_5d'] = df['clv'].rolling(5).mean()
    
    # Distance from highs/lows
    df['high_10d'] = df['High'].rolling(10).max()
    df['low_10d'] = df['Low'].rolling(10).min()
    df['high_20d'] = df['High'].rolling(20).max()
    df['low_20d'] = df['Low'].rolling(20).min()
    df['high_50d'] = df['High'].rolling(50).max()
    df['low_50d'] = df['Low'].rolling(50).min()
    
    df['dist_high_10d'] = (df['high_10d'] - df['Close']) / df['high_10d']
    df['dist_low_10d'] = (df['Close'] - df['low_10d']) / df['low_10d']
    df['dist_high_20d'] = (df['high_20d'] - df['Close']) / df['high_20d']
    df['dist_low_20d'] = (df['Close'] - df['low_20d']) / df['low_20d']
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / (loss + 0.0001)
    df['rsi_14'] = 100 - (100 / (1 + rs))
    
    # Moving averages
    df['sma_10'] = df['Close'].rolling(10).mean()
    df['sma_20'] = df['Close'].rolling(20).mean()
    df['sma_50'] = df['Close'].rolling(50).mean()
    df['ema_12'] = df['Close'].ewm(span=12).mean()
    df['ema_26'] = df['Close'].ewm(span=26).mean()
    
    # Bollinger Bands
    df['bb_mid'] = df['sma_20']
    df['bb_std'] = df['Close'].rolling(20).std()
    df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
    df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_mid']
    df['bb_pct'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'] + 0.0001)
    
    # ATR (Average True Range)
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift(1))
    low_close = abs(df['Low'] - df['Close'].shift(1))
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr_14'] = tr.rolling(14).mean()
    df['atr_pct'] = df['atr_14'] / df['Close']
    
    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    
    return df.dropna()


# ============================================================================
# THE PATTERN TESTER - PARALLEL EXECUTION
# ============================================================================

def test_pattern_combo(combo, all_data, hold_days=10, min_signals=30):
    """Test a single pattern combination across all stocks"""
    
    combo_name = " AND ".join([c[0] for c in combo])
    all_signals = []
    all_forward_returns = []
    
    for ticker, df in all_data.items():
        try:
            # Apply all conditions
            mask = pd.Series([True] * len(df), index=df.index)
            for cond_name, cond_func in combo:
                try:
                    cond_result = cond_func(df)
                    if isinstance(cond_result, pd.Series):
                        mask = mask & cond_result.fillna(False)
                    else:
                        mask = mask & False
                except:
                    mask = mask & False
            
            # Get signals
            signals = df[mask]
            
            if len(signals) > 0:
                # Get forward returns
                fwd_col = f'fwd_{hold_days}d'
                if fwd_col in df.columns:
                    returns = signals[fwd_col].dropna()
                    all_forward_returns.extend(returns.tolist())
                    all_signals.extend([(ticker, idx) for idx in signals.index])
        
        except Exception as e:
            continue
    
    # Need minimum signals
    if len(all_forward_returns) < min_signals:
        return None
    
    returns = np.array(all_forward_returns)
    
    # Calculate statistics
    mean_return = np.mean(returns)
    median_return = np.median(returns)
    win_rate = np.mean(returns > 0)
    std_return = np.std(returns)
    
    # Monte Carlo test
    n_simulations = 500  # Reduced for speed in brute force
    random_means = []
    
    for _ in range(n_simulations):
        random_returns = []
        for ticker, df in all_data.items():
            try:
                fwd_col = f'fwd_{hold_days}d'
                if fwd_col in df.columns:
                    sample = df[fwd_col].dropna().sample(min(len(returns) // len(all_data) + 1, len(df)), replace=True)
                    random_returns.extend(sample.tolist())
            except:
                continue
        if len(random_returns) >= min_signals:
            random_means.append(np.mean(random_returns[:len(returns)]))
    
    if len(random_means) < 100:
        return None
    
    # P-value
    p_value = np.mean([rm >= mean_return for rm in random_means])
    
    # Effect size (Cohen's d)
    pooled_std = np.std(random_means)
    if pooled_std > 0:
        effect_size = (mean_return - np.mean(random_means)) / pooled_std
    else:
        effect_size = 0
    
    return {
        'pattern': combo_name,
        'conditions': [c[0] for c in combo],
        'n_conditions': len(combo),
        'n_signals': len(all_forward_returns),
        'mean_return': mean_return,
        'median_return': median_return,
        'win_rate': win_rate,
        'std_return': std_return,
        'p_value': p_value,
        'effect_size': effect_size,
        'sharpe': mean_return / std_return if std_return > 0 else 0,
        'hold_days': hold_days,
    }


def generate_pattern_combinations(n_conditions_list=[2, 3, 4], max_combos=5000):
    """Generate all meaningful pattern combinations"""
    
    # Flatten all conditions
    all_conditions = []
    for category, conds in CONDITIONS.items():
        for cond in conds:
            all_conditions.append((category, cond))
    
    print(f"📊 Total conditions available: {len(all_conditions)}")
    
    all_combos = []
    
    for n in n_conditions_list:
        # Generate combinations
        for combo_indices in combinations(range(len(all_conditions)), n):
            combo = [all_conditions[i][1] for i in combo_indices]
            categories = [all_conditions[i][0] for i in combo_indices]
            
            # Skip if multiple conditions from same category (usually redundant)
            if len(set(categories)) < len(categories) * 0.7:
                continue
            
            all_combos.append(combo)
            
            if len(all_combos) >= max_combos:
                break
        
        if len(all_combos) >= max_combos:
            break
    
    print(f"📊 Generated {len(all_combos)} pattern combinations to test")
    return all_combos


# ============================================================================
# THE MAIN HUNT - BRUTE FORCE PATTERN DISCOVERY
# ============================================================================

def hunt_patterns(data, n_jobs=-1, max_patterns=3000):
    """The main hunt - test thousands of patterns in parallel"""
    
    print("\n" + "=" * 70)
    print("🐺 WOLFHUNTER - BRUTE FORCE PATTERN DISCOVERY")
    print("=" * 70)
    
    # Engineer features for all tickers
    print("\n🔧 Engineering features for all tickers...")
    processed_data = {}
    for ticker, df in data.items():
        try:
            processed_data[ticker] = engineer_features(df)
        except:
            continue
    
    print(f"✅ Processed {len(processed_data)} tickers")
    
    # Generate pattern combinations
    print("\n📊 Generating pattern combinations...")
    combos = generate_pattern_combinations(
        n_conditions_list=[2, 3, 4],
        max_combos=max_patterns
    )
    
    # Determine number of parallel jobs
    n_jobs = multiprocessing.cpu_count() if n_jobs == -1 else n_jobs
    print(f"\n⚡ Testing {len(combos)} patterns using {n_jobs} parallel workers...")
    
    # Test all patterns in parallel
    results = Parallel(n_jobs=n_jobs, verbose=10)(
        delayed(test_pattern_combo)(combo, processed_data, hold_days=10, min_signals=30)
        for combo in combos
    )
    
    # Filter valid results
    valid_results = [r for r in results if r is not None]
    print(f"\n✅ Got {len(valid_results)} valid pattern results")
    
    # Filter significant patterns
    significant = [
        r for r in valid_results 
        if r['p_value'] < 0.05 and r['effect_size'] > 0.3
    ]
    
    highly_significant = [
        r for r in valid_results 
        if r['p_value'] < 0.01 and r['effect_size'] > 0.5
    ]
    
    # Sort by effect size
    significant.sort(key=lambda x: x['effect_size'], reverse=True)
    highly_significant.sort(key=lambda x: x['effect_size'], reverse=True)
    
    return valid_results, significant, highly_significant


def print_discovery_report(all_results, significant, highly_significant):
    """Print the discovery report"""
    
    print("\n" + "=" * 80)
    print("🐺 WOLFHUNTER DISCOVERY REPORT")
    print("=" * 80)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Patterns tested: {len(all_results)}")
    print(f"   Significant (p<0.05, effect>0.3): {len(significant)}")
    print(f"   HIGHLY Significant (p<0.01, effect>0.5): {len(highly_significant)}")
    
    if len(highly_significant) > 0:
        print("\n" + "=" * 80)
        print("🔥 HIGHLY SIGNIFICANT PATTERNS (p<0.01, effect>0.5)")
        print("=" * 80)
        
        for i, r in enumerate(highly_significant[:30], 1):
            print(f"\n{'='*60}")
            print(f"🎯 PATTERN #{i}")
            print(f"{'='*60}")
            print(f"Conditions: {' AND '.join(r['conditions'])}")
            print(f"N Conditions: {r['n_conditions']}")
            print(f"Signals: {r['n_signals']}")
            print(f"Mean Return ({r['hold_days']}d): {r['mean_return']*100:.2f}%")
            print(f"Win Rate: {r['win_rate']*100:.1f}%")
            print(f"P-Value: {r['p_value']:.4f}")
            print(f"Effect Size: {r['effect_size']:.3f}")
            print(f"Sharpe: {r['sharpe']:.3f}")
    
    if len(significant) > len(highly_significant):
        print("\n" + "=" * 80)
        print("📈 OTHER SIGNIFICANT PATTERNS (p<0.05, effect>0.3)")
        print("=" * 80)
        
        remaining = [s for s in significant if s not in highly_significant]
        for i, r in enumerate(remaining[:20], 1):
            print(f"\n{i}. {r['pattern'][:80]}...")
            print(f"   Return: {r['mean_return']*100:.2f}%, WR: {r['win_rate']*100:.1f}%, p={r['p_value']:.4f}, effect={r['effect_size']:.3f}")
    
    return highly_significant, significant


def save_results(all_results, significant, highly_significant, filename='pattern_library.json'):
    """Save all discovered patterns to JSON"""
    
    output = {
        'discovery_date': datetime.now().isoformat(),
        'total_patterns_tested': len(all_results),
        'significant_patterns': len(significant),
        'highly_significant_patterns': len(highly_significant),
        'highly_significant': highly_significant[:50],
        'significant': significant[:100],
    }
    
    filepath = os.path.join('/workspaces/trading-companion-2026/hunt', filename)
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to {filepath}")
    return filepath


# ============================================================================
# LEVEL 2: MULTI-DIMENSIONAL PATTERN FINDER
# ============================================================================

def find_multidimensional_patterns(data, n_dimensions=5, min_signals=20):
    """Find complex multi-dimensional patterns humans can't see"""
    
    print("\n" + "=" * 70)
    print("🧠 MULTI-DIMENSIONAL PATTERN DISCOVERY")
    print(f"   Searching for {n_dimensions}-dimensional patterns...")
    print("=" * 70)
    
    # Engineer features
    processed_data = {}
    for ticker, df in data.items():
        try:
            processed_data[ticker] = engineer_features(df)
        except:
            continue
    
    # Generate 5-condition combinations (more complex patterns)
    combos = generate_pattern_combinations(
        n_conditions_list=[5, 6],
        max_combos=2000
    )
    
    print(f"⚡ Testing {len(combos)} multi-dimensional patterns...")
    
    # Test in parallel
    n_jobs = multiprocessing.cpu_count()
    results = Parallel(n_jobs=n_jobs, verbose=5)(
        delayed(test_pattern_combo)(combo, processed_data, hold_days=10, min_signals=min_signals)
        for combo in combos
    )
    
    valid = [r for r in results if r is not None]
    significant = [r for r in valid if r['p_value'] < 0.01 and r['effect_size'] > 0.5]
    significant.sort(key=lambda x: x['mean_return'], reverse=True)
    
    print(f"\n🎯 Found {len(significant)} multi-dimensional patterns!")
    
    return significant


# ============================================================================
# LEVEL 3: LEADING INDICATOR FINDER
# ============================================================================

def find_leading_indicators(data):
    """Find what predicts moves BEFORE they happen"""
    
    print("\n" + "=" * 70)
    print("🔮 LEADING INDICATOR DISCOVERY")
    print("=" * 70)
    
    # Process data
    processed_data = {}
    for ticker, df in data.items():
        try:
            processed_data[ticker] = engineer_features(df)
        except:
            continue
    
    # Cross-asset analysis
    # Look at how one ticker's move predicts another's
    
    leading_indicators = []
    
    # SPY as market leader
    if 'SPY' in processed_data:
        spy_df = processed_data['SPY']
        
        for ticker, df in processed_data.items():
            if ticker in ['SPY', 'QQQ', 'IWM', 'VIX']:
                continue
            
            try:
                # Merge on date
                merged = df.join(spy_df[['chg_1d', 'rel_vol_1d']].rename(columns={
                    'chg_1d': 'spy_chg_1d',
                    'rel_vol_1d': 'spy_vol'
                }), how='inner')
                
                if len(merged) < 100:
                    continue
                
                # Test: SPY down + high vol -> stock bounces?
                condition = (merged['spy_chg_1d'] < -0.01) & (merged['spy_vol'] > 1.5)
                signals = merged[condition]
                
                if len(signals) >= 20:
                    returns = signals['fwd_5d'].dropna()
                    if len(returns) >= 20:
                        mean_ret = returns.mean()
                        win_rate = (returns > 0).mean()
                        
                        if mean_ret > 0.03 and win_rate > 0.55:
                            leading_indicators.append({
                                'ticker': ticker,
                                'leader': 'SPY',
                                'pattern': 'SPY down + high vol -> bounce',
                                'mean_return': mean_ret,
                                'win_rate': win_rate,
                                'n_signals': len(returns)
                            })
            except:
                continue
    
    # Sector leader analysis
    print(f"\n🔮 Found {len(leading_indicators)} potential leading indicators")
    
    for ind in sorted(leading_indicators, key=lambda x: x['mean_return'], reverse=True)[:10]:
        print(f"\n   {ind['ticker']}: {ind['pattern']}")
        print(f"   Return: {ind['mean_return']*100:.2f}%, WR: {ind['win_rate']*100:.1f}%, Signals: {ind['n_signals']}")
    
    return leading_indicators


# ============================================================================
# LEVEL 4: REGIME DETECTOR
# ============================================================================

def build_regime_detector(data):
    """Build a market regime detector"""
    
    print("\n" + "=" * 70)
    print("🌡️ REGIME DETECTION")
    print("=" * 70)
    
    # Use SPY as market proxy
    if 'SPY' not in data:
        print("Need SPY for regime detection")
        return None
    
    spy = engineer_features(data['SPY'].copy())
    
    # Define regimes
    regimes = []
    
    for idx in spy.index:
        try:
            row = spy.loc[idx]
            
            # Bull/Bear based on SMA
            if row['Close'] > row['sma_50']:
                trend = 'BULL'
            else:
                trend = 'BEAR'
            
            # Volatility regime
            if row['atr_pct'] > 0.03:
                vol_regime = 'HIGH_VOL'
            else:
                vol_regime = 'LOW_VOL'
            
            regimes.append({
                'date': idx,
                'trend': trend,
                'volatility': vol_regime,
                'regime': f"{trend}_{vol_regime}"
            })
        except:
            continue
    
    regime_df = pd.DataFrame(regimes).set_index('date')
    
    # Count regime days
    print("\n📊 Regime Distribution:")
    for regime in regime_df['regime'].unique():
        count = (regime_df['regime'] == regime).sum()
        pct = count / len(regime_df) * 100
        print(f"   {regime}: {count} days ({pct:.1f}%)")
    
    return regime_df


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    
    print("\n" + "=" * 80)
    print("🐺 WOLFHUNTER - MACHINE-SCALE PATTERN DISCOVERY")
    print("=" * 80)
    print("This is NOT a human-scale tool.")
    print("Testing THOUSANDS of patterns. Finding what humans CAN'T.")
    print("=" * 80)
    
    # Load all data
    data = load_all_data(period='2y')
    
    if len(data) < 20:
        print("⚠️ Need more tickers for meaningful analysis")
        exit(1)
    
    # LEVEL 1: Brute force pattern discovery
    all_results, significant, highly_significant = hunt_patterns(
        data, 
        n_jobs=-1,
        max_patterns=2000  # Start with 2000, can scale up
    )
    
    # Print report
    print_discovery_report(all_results, significant, highly_significant)
    
    # Save results
    save_results(all_results, significant, highly_significant)
    
    # LEVEL 2: Multi-dimensional patterns
    if len(data) >= 30:
        multi_dim = find_multidimensional_patterns(data, n_dimensions=5)
        
        if multi_dim:
            print("\n🧠 TOP MULTI-DIMENSIONAL PATTERNS:")
            for i, p in enumerate(multi_dim[:5], 1):
                print(f"\n{i}. {p['pattern'][:100]}...")
                print(f"   Return: {p['mean_return']*100:.2f}%, p={p['p_value']:.4f}")
    
    # LEVEL 3: Leading indicators
    leading = find_leading_indicators(data)
    
    # LEVEL 4: Regime detection
    regimes = build_regime_detector(data)
    
    print("\n" + "=" * 80)
    print("🐺 HUNT COMPLETE")
    print("=" * 80)
    print(f"\n📊 FINAL TALLY:")
    print(f"   Patterns Tested: {len(all_results)}")
    print(f"   Significant Discoveries: {len(significant)}")
    print(f"   HIGHLY Significant: {len(highly_significant)}")
    print(f"   Leading Indicators: {len(leading) if leading else 0}")
    
    print("\n🐺 AWOOOO! The hunt never ends. This is just the beginning.")
