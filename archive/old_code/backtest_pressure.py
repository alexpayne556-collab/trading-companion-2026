#!/usr/bin/env python3
"""
🐺 PRESSURE BACKTEST - PROVE THE SIGNALS WORK
==============================================

Talk is cheap. Show me the data.

This backtests our pressure framework signals:
- When SHORT SQUEEZE signals fired historically, what happened?
- When PANIC RECOVERY signals fired, what happened?
- When CAPITULATION signals fired, what happened?
- When INSIDER BUYING happened, what followed?

We test:
1. Win rate - % of signals that worked
2. Average return - mean gain when right
3. Max drawdown - worst case scenario
4. Profit factor - gross profit / gross loss
5. Optimal holding period - 1d, 3d, 5d, 10d?

This proves (or disproves) our edge.

Built by Brokkr & Fenrir
AWOOOO 🐺
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# BACKTEST DATA STRUCTURES
# ============================================================================

@dataclass
class BacktestResult:
    """Result of a single signal backtest"""
    ticker: str
    signal_date: str
    signal_type: str
    entry_price: float
    
    # Forward returns
    return_1d: float
    return_3d: float
    return_5d: float
    return_10d: float
    return_20d: float
    
    # Max move
    max_gain: float
    max_loss: float
    
    # Was it a winner?
    win_1d: bool
    win_3d: bool
    win_5d: bool
    win_10d: bool

@dataclass 
class BacktestStats:
    """Aggregate statistics for a signal type"""
    signal_type: str
    total_signals: int
    
    # Win rates
    win_rate_1d: float
    win_rate_3d: float
    win_rate_5d: float
    win_rate_10d: float
    
    # Average returns
    avg_return_1d: float
    avg_return_3d: float
    avg_return_5d: float
    avg_return_10d: float
    
    # Risk metrics
    avg_max_gain: float
    avg_max_loss: float
    profit_factor: float
    
    # Best holding period
    best_period: str
    best_win_rate: float
    best_avg_return: float

# ============================================================================
# UNIVERSE FOR BACKTESTING
# ============================================================================

UNIVERSE = {
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT'],
    'SPACE': ['LUNR', 'RKLB', 'ASTS', 'MNTS', 'SPIR'],
    'NUCLEAR': ['LEU', 'CCJ', 'UUUU', 'UEC', 'SMR', 'NNE'],
    'AI_INFRA': ['SMCI', 'SOUN', 'AI', 'NVDA', 'AMD'],
    'CRYPTO': ['MARA', 'RIOT', 'CLSK', 'COIN'],
    'BIOTECH': ['CRSP', 'EDIT', 'NTLA', 'BEAM'],
    'EV_CLEAN': ['RIVN', 'LCID', 'PLUG', 'FCEL'],
    'FINTECH': ['SOFI', 'AFRM', 'UPST']
}

ALL_TICKERS = list(set([t for tickers in UNIVERSE.values() for t in tickers]))

# ============================================================================
# SIGNAL DETECTION (HISTORICAL)
# ============================================================================

def detect_short_squeeze_setup(df: pd.DataFrame, lookback: int = 5) -> List[int]:
    """
    Detect historical short squeeze setups.
    Conditions:
    - Price rising for lookback days
    - Volume increasing
    - Already down significantly from highs (shorts are in profit, will cover)
    """
    signals = []
    
    if len(df) < lookback + 20:
        return signals
    
    for i in range(lookback, len(df) - 20):  # Leave room for forward returns
        # Price rising
        price_change = (df['Close'].iloc[i] - df['Close'].iloc[i-lookback]) / df['Close'].iloc[i-lookback]
        if price_change < 0.03:  # Need 3%+ gain over lookback
            continue
        
        # Volume increasing
        vol_recent = df['Volume'].iloc[i-lookback:i].mean()
        vol_prior = df['Volume'].iloc[i-lookback*2:i-lookback].mean() if i >= lookback*2 else vol_recent
        vol_ratio = vol_recent / vol_prior if vol_prior > 0 else 1
        if vol_ratio < 1.2:  # Need 20%+ volume increase
            continue
        
        # Down from 52-week high (shorts have profits to protect)
        rolling_high = df['High'].iloc[max(0,i-252):i].max()
        from_high = (df['Close'].iloc[i] - rolling_high) / rolling_high
        if from_high > -0.20:  # Need to be 20%+ down from highs
            continue
        
        signals.append(i)
    
    return signals

def detect_panic_recovery_setup(df: pd.DataFrame, lookback: int = 10) -> List[int]:
    """
    Detect panic recovery setups.
    Conditions:
    - Sharp drop in recent past (panic)
    - Now bouncing with volume (recovery)
    - Still down significantly (room to run)
    """
    signals = []
    
    if len(df) < lookback + 20:
        return signals
    
    for i in range(lookback, len(df) - 20):
        # Recent sharp drop
        recent_high = df['High'].iloc[i-lookback:i].max()
        current = df['Close'].iloc[i]
        from_recent_high = (current - recent_high) / recent_high
        
        if from_recent_high > -0.15:  # Need 15%+ drop
            continue
        
        # Now bouncing (today green)
        today_change = (df['Close'].iloc[i] - df['Open'].iloc[i]) / df['Open'].iloc[i]
        if today_change < 0.02:  # Need 2%+ green day
            continue
        
        # Volume spike
        vol_today = df['Volume'].iloc[i]
        vol_avg = df['Volume'].iloc[i-20:i].mean()
        if vol_today < vol_avg * 1.5:  # Need 1.5x volume
            continue
        
        signals.append(i)
    
    return signals

def detect_capitulation_setup(df: pd.DataFrame, lookback: int = 20) -> List[int]:
    """
    Detect capitulation bottom setups.
    Conditions:
    - Major drawdown from highs
    - Volume was dying, now spiking
    - Sign of bottoming
    """
    signals = []
    
    if len(df) < lookback + 20:
        return signals
    
    for i in range(lookback, len(df) - 20):
        # Major drawdown
        high_52w = df['High'].iloc[max(0,i-252):i].max()
        current = df['Close'].iloc[i]
        from_high = (current - high_52w) / high_52w
        
        if from_high > -0.40:  # Need 40%+ drawdown
            continue
        
        # Volume was dying
        vol_prev = df['Volume'].iloc[i-lookback:i-5].mean()
        vol_recent = df['Volume'].iloc[i-5:i].mean()
        
        # Now spiking
        vol_today = df['Volume'].iloc[i]
        vol_spike = vol_today / vol_prev if vol_prev > 0 else 1
        
        if vol_spike < 1.5:  # Need volume spike
            continue
        
        signals.append(i)
    
    return signals

def detect_laggard_setup(df: pd.DataFrame, sector_df: pd.DataFrame, lookback: int = 10) -> List[int]:
    """
    Detect laggard catch-up setups.
    Conditions:
    - Sector leader has moved significantly
    - This stock hasn't moved as much
    - Correlation suggests it should catch up
    """
    signals = []
    
    if len(df) < lookback + 20 or len(sector_df) < lookback + 20:
        return signals
    
    for i in range(lookback, min(len(df), len(sector_df)) - 20):
        # Sector leader move
        leader_change = (sector_df['Close'].iloc[i] - sector_df['Close'].iloc[i-lookback]) / sector_df['Close'].iloc[i-lookback]
        
        if leader_change < 0.10:  # Leader needs 10%+ move
            continue
        
        # This stock lagging
        stock_change = (df['Close'].iloc[i] - df['Close'].iloc[i-lookback]) / df['Close'].iloc[i-lookback]
        
        lag = leader_change - stock_change
        if lag < 0.05:  # Need meaningful lag
            continue
        
        signals.append(i)
    
    return signals

# ============================================================================
# FORWARD RETURN CALCULATION
# ============================================================================

def calculate_forward_returns(df: pd.DataFrame, signal_idx: int) -> Dict:
    """Calculate forward returns from signal date"""
    
    entry_price = df['Close'].iloc[signal_idx]
    
    returns = {
        'entry_price': entry_price,
        'return_1d': 0, 'return_3d': 0, 'return_5d': 0, 
        'return_10d': 0, 'return_20d': 0,
        'max_gain': 0, 'max_loss': 0
    }
    
    # Forward slice
    forward = df.iloc[signal_idx+1:signal_idx+21]
    
    if len(forward) >= 1:
        returns['return_1d'] = (forward['Close'].iloc[0] - entry_price) / entry_price * 100
    if len(forward) >= 3:
        returns['return_3d'] = (forward['Close'].iloc[2] - entry_price) / entry_price * 100
    if len(forward) >= 5:
        returns['return_5d'] = (forward['Close'].iloc[4] - entry_price) / entry_price * 100
    if len(forward) >= 10:
        returns['return_10d'] = (forward['Close'].iloc[9] - entry_price) / entry_price * 100
    if len(forward) >= 20:
        returns['return_20d'] = (forward['Close'].iloc[19] - entry_price) / entry_price * 100
    
    # Max gain/loss in 10 days
    if len(forward) >= 10:
        highs = forward['High'].iloc[:10]
        lows = forward['Low'].iloc[:10]
        returns['max_gain'] = (highs.max() - entry_price) / entry_price * 100
        returns['max_loss'] = (lows.min() - entry_price) / entry_price * 100
    
    return returns

# ============================================================================
# BACKTEST RUNNER
# ============================================================================

def run_backtest_for_signal(signal_type: str, period: str = '2y') -> Tuple[List[BacktestResult], BacktestStats]:
    """Run backtest for a specific signal type"""
    
    print(f"\n🔍 Backtesting {signal_type}...")
    
    results = []
    
    for ticker in ALL_TICKERS:
        try:
            # Download data
            df = yf.download(ticker, period=period, progress=False)
            if df.empty or len(df) < 100:
                continue
            
            # Handle multi-level columns
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Detect signals based on type
            if signal_type == 'SHORT_SQUEEZE':
                signal_indices = detect_short_squeeze_setup(df)
            elif signal_type == 'PANIC_RECOVERY':
                signal_indices = detect_panic_recovery_setup(df)
            elif signal_type == 'CAPITULATION':
                signal_indices = detect_capitulation_setup(df)
            elif signal_type == 'LAGGARD':
                # Need sector leader - use IONQ for quantum, RKLB for space, etc.
                leader_ticker = 'SPY'  # Default
                for sector, tickers in UNIVERSE.items():
                    if ticker in tickers:
                        leader_ticker = tickers[0]  # First ticker is leader
                        break
                
                if leader_ticker == ticker:
                    continue
                    
                leader_df = yf.download(leader_ticker, period=period, progress=False)
                if isinstance(leader_df.columns, pd.MultiIndex):
                    leader_df.columns = leader_df.columns.get_level_values(0)
                signal_indices = detect_laggard_setup(df, leader_df)
            else:
                continue
            
            # Calculate returns for each signal
            for idx in signal_indices:
                returns = calculate_forward_returns(df, idx)
                
                result = BacktestResult(
                    ticker=ticker,
                    signal_date=df.index[idx].strftime('%Y-%m-%d'),
                    signal_type=signal_type,
                    entry_price=returns['entry_price'],
                    return_1d=returns['return_1d'],
                    return_3d=returns['return_3d'],
                    return_5d=returns['return_5d'],
                    return_10d=returns['return_10d'],
                    return_20d=returns['return_20d'],
                    max_gain=returns['max_gain'],
                    max_loss=returns['max_loss'],
                    win_1d=returns['return_1d'] > 0,
                    win_3d=returns['return_3d'] > 0,
                    win_5d=returns['return_5d'] > 0,
                    win_10d=returns['return_10d'] > 0
                )
                results.append(result)
                
        except Exception as e:
            continue
    
    # Calculate aggregate stats
    if not results:
        return [], None
    
    n = len(results)
    
    # Win rates
    wr_1d = sum(1 for r in results if r.win_1d) / n * 100
    wr_3d = sum(1 for r in results if r.win_3d) / n * 100
    wr_5d = sum(1 for r in results if r.win_5d) / n * 100
    wr_10d = sum(1 for r in results if r.win_10d) / n * 100
    
    # Average returns
    avg_1d = sum(r.return_1d for r in results) / n
    avg_3d = sum(r.return_3d for r in results) / n
    avg_5d = sum(r.return_5d for r in results) / n
    avg_10d = sum(r.return_10d for r in results) / n
    
    # Risk metrics
    avg_max_gain = sum(r.max_gain for r in results) / n
    avg_max_loss = sum(r.max_loss for r in results) / n
    
    # Profit factor (using 5d returns)
    wins = [r.return_5d for r in results if r.return_5d > 0]
    losses = [abs(r.return_5d) for r in results if r.return_5d < 0]
    profit_factor = sum(wins) / sum(losses) if losses else float('inf')
    
    # Best period
    periods = [
        ('1d', wr_1d, avg_1d),
        ('3d', wr_3d, avg_3d),
        ('5d', wr_5d, avg_5d),
        ('10d', wr_10d, avg_10d)
    ]
    best = max(periods, key=lambda x: x[1] * x[2] if x[2] > 0 else 0)
    
    stats = BacktestStats(
        signal_type=signal_type,
        total_signals=n,
        win_rate_1d=round(wr_1d, 1),
        win_rate_3d=round(wr_3d, 1),
        win_rate_5d=round(wr_5d, 1),
        win_rate_10d=round(wr_10d, 1),
        avg_return_1d=round(avg_1d, 2),
        avg_return_3d=round(avg_3d, 2),
        avg_return_5d=round(avg_5d, 2),
        avg_return_10d=round(avg_10d, 2),
        avg_max_gain=round(avg_max_gain, 2),
        avg_max_loss=round(avg_max_loss, 2),
        profit_factor=round(profit_factor, 2),
        best_period=best[0],
        best_win_rate=round(best[1], 1),
        best_avg_return=round(best[2], 2)
    )
    
    return results, stats

# ============================================================================
# FULL BACKTEST
# ============================================================================

def run_full_backtest():
    """Run backtest for all signal types"""
    
    print("\n" + "="*70)
    print("🐺 PRESSURE FRAMEWORK BACKTEST")
    print("="*70)
    print(f"\nTesting on {len(ALL_TICKERS)} tickers over 2 years")
    print("This proves whether our signals have a real edge.\n")
    
    all_results = {}
    all_stats = {}
    
    signal_types = ['SHORT_SQUEEZE', 'PANIC_RECOVERY', 'CAPITULATION', 'LAGGARD']
    
    for signal_type in signal_types:
        results, stats = run_backtest_for_signal(signal_type)
        all_results[signal_type] = results
        all_stats[signal_type] = stats
        
        if stats:
            print(f"\n✅ {signal_type}: {stats.total_signals} signals found")
    
    # Display results
    print("\n" + "="*70)
    print("📊 BACKTEST RESULTS")
    print("="*70)
    
    print("\n┌─────────────────┬────────┬─────────┬─────────┬─────────┬─────────┬─────────┐")
    print("│ Signal Type     │ Count  │ WR(1d)  │ WR(5d)  │ Avg(5d) │ MaxGain │ PF      │")
    print("├─────────────────┼────────┼─────────┼─────────┼─────────┼─────────┼─────────┤")
    
    for signal_type, stats in all_stats.items():
        if stats:
            print(f"│ {signal_type:15} │ {stats.total_signals:6} │ {stats.win_rate_1d:5.1f}%  │ {stats.win_rate_5d:5.1f}%  │ {stats.avg_return_5d:+5.2f}% │ {stats.avg_max_gain:+5.1f}%  │ {stats.profit_factor:5.2f}   │")
    
    print("└─────────────────┴────────┴─────────┴─────────┴─────────┴─────────┴─────────┘")
    
    print("\n📈 OPTIMAL HOLDING PERIODS")
    print("-"*50)
    for signal_type, stats in all_stats.items():
        if stats:
            print(f"   {signal_type}: {stats.best_period} (WR: {stats.best_win_rate}%, Avg: {stats.best_avg_return:+.2f}%)")
    
    # Save results
    Path('exports').mkdir(exist_ok=True)
    
    # Save detailed results
    all_results_flat = []
    for signal_type, results in all_results.items():
        for r in results:
            all_results_flat.append({
                'ticker': r.ticker,
                'date': r.signal_date,
                'type': r.signal_type,
                'entry': r.entry_price,
                'return_1d': r.return_1d,
                'return_5d': r.return_5d,
                'return_10d': r.return_10d,
                'max_gain': r.max_gain,
                'max_loss': r.max_loss
            })
    
    df = pd.DataFrame(all_results_flat)
    df.to_csv('exports/backtest_results.csv', index=False)
    print(f"\n📁 Detailed results saved: exports/backtest_results.csv")
    
    # Save summary
    summary = {
        'generated': datetime.now().isoformat(),
        'tickers_tested': len(ALL_TICKERS),
        'period': '2 years',
        'signal_stats': {k: vars(v) if v else None for k, v in all_stats.items()}
    }
    
    with open('exports/backtest_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"📁 Summary saved: exports/backtest_summary.json")
    
    # Print interpretation
    print("\n" + "="*70)
    print("🐺 INTERPRETATION")
    print("="*70)
    
    print("""
KEY FINDINGS:
- Win Rate > 55% = Signal has edge
- Profit Factor > 1.5 = Risk/reward favorable  
- Avg Return > 3% (5d) = Meaningful gains

TRADING IMPLICATIONS:
1. Use signals with WR > 55% for entries
2. Hold for the optimal period shown above
3. Size positions based on profit factor
4. Combine multiple signals for higher conviction

REMEMBER:
Past performance doesn't guarantee future results.
But it tells us what HAS worked in similar conditions.
    """)
    
    print("\n🐺 Backtest complete. The data speaks. AWOOOO!\n")
    
    return all_results, all_stats

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    run_full_backtest()
