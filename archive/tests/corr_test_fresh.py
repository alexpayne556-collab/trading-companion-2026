import yfinance as yf
import numpy as np
import pandas as pd
from scipy import stats
from datetime import datetime, timedelta

def test_correlation_breaks():
    print("Testing IONQ/RGTI Correlation Breaks")
    print("=" * 60)
    
    # Download data - get only Close prices
    ionq_data = yf.download('IONQ', start='2024-06-01', end='2026-01-03', progress=False)['Close']
    rgti_data = yf.download('RGTI', start='2024-06-01', end='2026-01-03', progress=False)['Close']
    
    print(f"IONQ data points: {len(ionq_data)}")
    print(f"RGTI data points: {len(rgti_data)}")
    
    if len(ionq_data) == 0 or len(rgti_data) == 0:
        print("Failed to download data")
        return
    
    # Calculate daily returns
    ionq_ret = ionq_data.pct_change()
    rgti_ret = rgti_data.pct_change()
    
    print(f"IONQ returns: {ionq_ret.dropna().shape}")
    print(f"RGTI returns: {rgti_ret.dropna().shape}")
    
    # Rolling correlation
    window = 20
    corr = ionq_ret.rolling(window).corr(rgti_ret)
    
    print(f"Corr type: {type(corr)}, len: {len(corr) if hasattr(corr, '__len__') else 'N/A'}")
    
    # Print correlation stats
    valid_corr = corr.dropna()
    if len(valid_corr) > 0:
        print(f"Correlation stats: min={valid_corr.min():.2f}, max={valid_corr.max():.2f}, median={valid_corr.median():.2f}")
    else:
        print("No valid correlation values")
    
    # Find signals
    returns_list = []
    debug_count = 0
    high_corr_count = 0
    
    for i in range(window, len(ionq_data)-5):
        corr_val = corr.iloc[i]
        if isinstance(corr_val, (int, float)) and not pd.isna(corr_val):
            if corr_val > 0.7:
                high_corr_count += 1
                ionq_chg = ionq_ret.iloc[i] * 100
                rgti_chg = rgti_ret.iloc[i] * 100
                
                if debug_count < 5:
                    print(f"Day {i}: IONQ={ionq_chg:.2f}%, RGTI={rgti_chg:.2f}%, corr={corr_val:.2f}")
                    debug_count += 1
            
                if pd.notna(ionq_chg) and pd.notna(rgti_chg):
                    gap = abs(ionq_chg - rgti_chg)
                    
                    if gap > 8:
                        # Buy the laggard
                        if ionq_chg > rgti_chg:
                            entry = rgti_data.iloc[i]
                            exit_idx = min(i+5, len(rgti_data)-1)
                            exit_price = rgti_data.iloc[exit_idx]
                            ret = ((exit_price - entry) / entry) * 100
                            returns_list.append(ret)
    
    print(f"Days with high correlation (>0.7): {high_corr_count}")
    print(f"Signals found: {len(returns_list)}")
    
    if len(returns_list) == 0:
        print("No signals")
        return
    
    returns_arr = np.array(returns_list)
    
    # Basic stats
    wr = (returns_arr > 0).mean() * 100
    avg_ret = returns_arr.mean()
    
    print(f"\nWin Rate: {wr:.1f}%")
    print(f"Avg Return: {avg_ret:.2f}%")
    
    # Monte Carlo
    print("\nMonte Carlo test...")
    
    all_random_returns = []
    for i in range(len(rgti_data)-5):
        entry = rgti_data.iloc[i]
        exit_price = rgti_data.iloc[i+5]
        ret = ((exit_price - entry) / entry) * 100
        all_random_returns.append(ret)
    
    mc_results = []
    for _ in range(1000):
        sample = np.random.choice(all_random_returns, size=len(returns_arr))
        mc_results.append(np.mean(sample))
    
    mc_mean = np.mean(mc_results)
    mc_std = np.std(mc_results)
    
    pval = np.mean(np.array(mc_results) >= avg_ret)
    effect = (avg_ret - mc_mean) / mc_std if mc_std > 0 else 0
    
    print(f"Random baseline: {mc_mean:.2f}%")
    print(f"P-value: {pval:.4f}")
    print(f"Effect size: {effect:.2f}")
    print(f"Std devs: {effect:.1f}")
    
    print("\n" + "=" * 60)
    if pval < 0.05 and abs(effect) > 2:
        print("VERDICT: REAL EDGE")
    elif pval < 0.10:
        print("VERDICT: MARGINAL")
    else:
        print("VERDICT: NO EDGE")

if __name__ == '__main__':
    test_correlation_breaks()
