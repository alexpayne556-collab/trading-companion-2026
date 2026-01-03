"""
Simplified Rigorous Backtesting - Clean Version
Test correlation break detector with statistical rigor
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy import stats
import yfinance as yf
from src.signals.correlation_break_detector import CorrelationBreakDetector


def backtest_correlation_breaks():
    """Test correlation breaks with Monte Carlo simulation"""
    
    print('=' * 70)
    print('RIGOROUS TEST: CORRELATION BREAK DETECTOR')
    print('=' * 70)
    
    # Get signals
    detector = CorrelationBreakDetector()
    signals = detector.scan_quantum_stocks()
    
    if not signals:
        print('\nNo signals found.')
        return
    
    print(f'\nFound {len(signals)} signals to test')
    
    # Backtest each signal
    returns = []
    
    for signal in signals:
        ticker = signal['ticker']
        signal_date = signal['date']
        
        # Get price data
        end_date = signal_date + timedelta(days=10)
        data = yf.download(ticker, start=signal_date, end=end_date, progress=False)
        
        if len(data) < 2:
            continue
        
        entry_price = data['Close'].iloc[0]
        exit_price = data['Close'].iloc[-1]
        ret = ((exit_price - entry_price) / entry_price) * 100
        returns.append(ret)
    
    if not returns:
        print('No valid trades.')
        return
    
    returns = np.array(returns)
    
    # Calculate metrics
    win_rate = (returns > 0).mean() * 100
    avg_return = returns.mean()
    
    print(f'\nBASIC METRICS:')
    print(f'  Win Rate: {win_rate:.1f}%')
    print(f'  Avg Return: {avg_return:+.2f}%')
    print(f'  Total Trades: {len(returns)}')
    
    # Monte Carlo simulation
    print(f'\nRunning Monte Carlo simulation...')
    
    # Get historical data for random sampling
    tickers = ['IONQ', 'RGTI', 'QBTS', 'SIDU']
    all_returns = []
    
    for ticker in tickers:
        data = yf.download(ticker, start='2024-01-01', end='2025-12-31', progress=False)
        if len(data) > 10:
            for i in range(len(data) - 5):
                entry = data['Close'].iloc[i]
                exit_val = data['Close'].iloc[min(i+5, len(data)-1)]
                ret = ((exit_val - entry) / entry) * 100
                all_returns.append(ret)
    
    all_returns = np.array(all_returns)
    
    # Run Monte Carlo
    mc_returns = []
    for _ in range(1000):
        random_sample = np.random.choice(all_returns, size=len(returns), replace=True)
        mc_returns.append(random_sample.mean())
    
    mc_returns = np.array(mc_returns)
    mc_mean = mc_returns.mean()
    mc_std = mc_returns.std()
    
    # Calculate p-value
    p_value = (mc_returns >= avg_return).mean()
    
    # Calculate effect size (Cohen's d)
    cohens_d = (avg_return - mc_mean) / mc_std if mc_std > 0 else 0
    
    # Std devs above random
    std_devs = (avg_return - mc_mean) / mc_std if mc_std > 0 else 0
    
    print(f'\nMONTE CARLO RESULTS:')
    print(f'  Strategy Return: {avg_return:+.2f}%')
    print(f'  Random Baseline: {mc_mean:+.2f}%')
    print(f'  Random Std Dev: {mc_std:.2f}%')
    print(f'  P-value: {p_value:.4f}')
    print(f'  Effect Size (Cohen\'s d): {cohens_d:.2f}')
    print(f'  Std Devs Above Random: {std_devs:.1f}')
    
    # VERDICT
    print('\n' + '=' * 70)
    print('VERDICT:')
    print('=' * 70)
    
    if p_value < 0.05 and std_devs > 2.0 and abs(cohens_d) > 0.5:
        print('\n✅ REAL EDGE DETECTED')
        print('   - Statistically significant (p < 0.05)')
        print('   - More than 2 std devs above random')
        print('   - Large effect size (|d| > 0.5)')
    elif p_value < 0.10:
        print('\n⚠️  MARGINAL EDGE')
        print('   - Close to significant but needs refinement')
    else:
        print('\n❌ NO STATISTICAL EDGE')
        print('   - This is probably random luck')
        print('   - Not tradeable')
    
    print('=' * 70)


if __name__ == '__main__':
    backtest_correlation_breaks()
