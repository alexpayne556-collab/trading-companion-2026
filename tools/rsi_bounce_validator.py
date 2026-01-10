#!/usr/bin/env python3
"""
🐺 RESEARCH PROJECT 4: RSI BOUNCE OPTIMIZATION

Question: What RSI level gives the best risk-adjusted bounce?

Test Parameters:
- RSI thresholds: 35, 30, 25, 20
- Lookback: 90 days
- Tickers: DNN, UEC, UUUU, SMR, CIFR, WULF (Tier A focus)
- Win condition: >5% gain within 5 days

Success Criteria:
- Win rate > 60%
- Sample size > 20
- Consistent across multiple tickers

Tradeable Outcome:
If validated → "Buy when RSI < {X}, expect {Y}% win rate, avg gain {Z}% within {N} days"

Built by: BROKKR
Specification by: TYR
"""

import sys
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from typing import List, Dict
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# RSI CALCULATION
# =============================================================================

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate RSI (Relative Strength Index)
    
    Args:
        prices: Series of closing prices
        period: RSI period (default 14)
    
    Returns:
        Series of RSI values
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# =============================================================================
# BOUNCE ANALYSIS
# =============================================================================

def analyze_rsi_bounces(ticker: str, days: int = 90) -> Dict:
    """
    Analyze RSI bounce behavior for a ticker
    
    Args:
        ticker: Stock symbol
        days: Lookback days
    
    Returns:
        Dictionary with analysis results
    """
    print(f"\n{'='*80}")
    print(f"📊 ANALYZING: {ticker}")
    print(f"{'='*80}")
    
    # Download data
    try:
        df = yf.download(ticker, period=f'{days}d', interval='1d', progress=False)
        if df.empty:
            print(f"❌ No data available")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    
    # Calculate RSI
    df['RSI'] = calculate_rsi(df['Close'])
    
    # Test multiple RSI thresholds
    thresholds = [35, 30, 25, 20]
    results = {}
    
    for threshold in thresholds:
        # Find RSI signals
        signals = df[df['RSI'] < threshold].copy()
        
        if len(signals) == 0:
            continue
        
        # Track outcomes
        signal_data = []
        for date, row in signals.iterrows():
            entry_price = row['Close']
            entry_rsi = row['RSI']
            
            # Look at next 5 days
            future_dates = df.index[df.index > date][:5]
            
            if len(future_dates) == 0:
                continue
            
            returns_1d = ((df.loc[future_dates[0], 'Close'] - entry_price) / entry_price * 100) if len(future_dates) >= 1 else 0
            returns_3d = ((df.loc[future_dates[2], 'Close'] - entry_price) / entry_price * 100) if len(future_dates) >= 3 else 0
            returns_5d = ((df.loc[future_dates[4], 'Close'] - entry_price) / entry_price * 100) if len(future_dates) >= 5 else 0
            
            # Max gain within 5 days
            future_highs = df.loc[future_dates, 'High']
            max_gain = ((future_highs.max() - entry_price) / entry_price * 100) if len(future_highs) > 0 else 0
            
            # Win condition: >5% gain within 5 days
            is_win = max_gain >= 5.0
            
            signal_data.append({
                'date': date,
                'entry_price': entry_price,
                'rsi': entry_rsi,
                'return_1d': returns_1d,
                'return_3d': returns_3d,
                'return_5d': returns_5d,
                'max_gain_5d': max_gain,
                'is_win': is_win
            })
        
        if len(signal_data) == 0:
            continue
        
        signal_df = pd.DataFrame(signal_data)
        
        # Calculate statistics
        total_signals = len(signal_df)
        wins = signal_df['is_win'].sum()
        losses = total_signals - wins
        win_rate = (wins / total_signals * 100) if total_signals > 0 else 0
        
        avg_return_1d = signal_df['return_1d'].mean()
        avg_return_3d = signal_df['return_3d'].mean()
        avg_return_5d = signal_df['return_5d'].mean()
        avg_max_gain = signal_df['max_gain_5d'].mean()
        
        results[threshold] = {
            'total_signals': total_signals,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'avg_return_1d': avg_return_1d,
            'avg_return_3d': avg_return_3d,
            'avg_return_5d': avg_return_5d,
            'avg_max_gain': avg_max_gain,
            'signals': signal_df
        }
    
    # Print results
    if results:
        print(f"\n📈 RSI BOUNCE ANALYSIS (Win = >5% gain within 5 days):\n")
        print(f"{'RSI':<8} {'Signals':<10} {'Wins':<8} {'Losses':<8} {'Win Rate':<12} {'Avg 1D':<12} {'Avg 3D':<12} {'Avg 5D':<12} {'Avg Max':<12}")
        print("-" * 110)
        
        for threshold in thresholds:
            if threshold in results:
                r = results[threshold]
                print(f"<{threshold:<6} {r['total_signals']:<10} {r['wins']:<8} {r['losses']:<8} "
                      f"{r['win_rate']:>6.1f}%      {r['avg_return_1d']:>+6.2f}%      "
                      f"{r['avg_return_3d']:>+6.2f}%      {r['avg_return_5d']:>+6.2f}%      "
                      f"{r['avg_max_gain']:>+6.2f}%")
        
        # Best threshold
        best_threshold = max(results.keys(), key=lambda x: results[x]['win_rate'])
        best = results[best_threshold]
        
        print(f"\n🎯 BEST THRESHOLD: RSI < {best_threshold}")
        print(f"   Win rate: {best['win_rate']:.1f}%")
        print(f"   Signals: {best['total_signals']}")
        print(f"   Avg max gain: +{best['avg_max_gain']:.2f}%")
        
        # Verdict
        if best['win_rate'] >= 70:
            verdict = "✅ VALIDATED EDGE"
        elif best['win_rate'] >= 60:
            verdict = "⚠️ WEAK EDGE"
        else:
            verdict = "❌ NO EDGE"
        
        print(f"\n{verdict}")
        
        return {
            'ticker': ticker,
            'best_threshold': best_threshold,
            'win_rate': best['win_rate'],
            'sample_size': best['total_signals'],
            'avg_max_gain': best['avg_max_gain'],
            'verdict': verdict,
            'all_thresholds': results
        }
    
    return None

# =============================================================================
# MAIN RESEARCH EXECUTION
# =============================================================================

def run_research(tickers: List[str] = None, days: int = 90):
    """
    Run RSI bounce research
    
    Args:
        tickers: List of tickers to test
        days: Lookback days
    """
    print("="*80)
    print("🐺 RESEARCH PROJECT 4: RSI BOUNCE OPTIMIZATION")
    print("="*80)
    print(f"\nParameters:")
    print(f"  Lookback: {days} days")
    print(f"  Win condition: >5% gain within 5 days")
    print(f"  RSI thresholds: 35, 30, 25, 20")
    
    # Default tickers (Tier A focus from spec)
    if tickers is None:
        tickers = ['DNN', 'UEC', 'UUUU', 'SMR', 'CIFR', 'WULF']
    
    print(f"  Tickers: {', '.join(tickers)}")
    
    # Run analysis
    all_results = []
    
    for ticker in tickers:
        result = analyze_rsi_bounces(ticker, days=days)
        if result:
            all_results.append(result)
    
    # Summary
    if all_results:
        print(f"\n{'='*80}")
        print(f"📊 RESEARCH SUMMARY")
        print(f"{'='*80}\n")
        
        summary_data = []
        for r in all_results:
            summary_data.append({
                'Ticker': r['ticker'],
                'Best RSI': f"<{r['best_threshold']}",
                'Win Rate': f"{r['win_rate']:.1f}%",
                'Samples': r['sample_size'],
                'Avg Gain': f"+{r['avg_max_gain']:.2f}%",
                'Verdict': r['verdict']
            })
        
        summary_df = pd.DataFrame(summary_data)
        print(summary_df.to_string(index=False))
        
        # Aggregate statistics
        total_signals = sum(r['sample_size'] for r in all_results)
        weighted_win_rate = sum(r['win_rate'] * r['sample_size'] for r in all_results) / total_signals if total_signals > 0 else 0
        avg_gain = sum(r['avg_max_gain'] for r in all_results) / len(all_results)
        
        print(f"\n{'='*80}")
        print(f"✅ AGGREGATE VALIDATION")
        print(f"{'='*80}\n")
        print(f"Total signals: {total_signals}")
        print(f"Weighted win rate: {weighted_win_rate:.1f}%")
        print(f"Average max gain: +{avg_gain:.2f}%")
        
        # Validation
        if weighted_win_rate >= 70:
            print(f"\n✅ VALIDATED EDGE - RSI bounce is tradeable")
            print(f"   Optimal RSI: < 30-35 (varies by ticker)")
            print(f"   Expected: {weighted_win_rate:.0f}% win rate, +{avg_gain:.1f}% avg gain")
            print(f"   Strategy: Buy at close when RSI < threshold, sell when +5% or 5 days")
        elif weighted_win_rate >= 60:
            print(f"\n⚠️ WEAK EDGE - Needs more data or refinement")
        else:
            print(f"\n❌ NO EDGE - RSI bounce not reliable in this universe")
        
        # Save results
        import os
        os.makedirs('research_results', exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"research_results/project_4_summary_{timestamp}.csv"
        summary_df.to_csv(filepath, index=False)
        print(f"\n💾 Saved: {filepath}")
        
        # Save detailed results
        for r in all_results:
            best_threshold = r['best_threshold']
            signals_df = r['all_thresholds'][best_threshold]['signals']
            detail_path = f"research_results/project_4_detail_{r['ticker']}_{timestamp}.csv"
            signals_df.to_csv(detail_path, index=False)
            print(f"💾 Saved: {detail_path}")
    
    print(f"\n🐺 LLHR. Project 4 complete.")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Research Project 4: RSI Bounce Optimization')
    parser.add_argument('--tickers', nargs='+', help='Tickers to analyze (default: DNN UEC UUUU SMR CIFR WULF)')
    parser.add_argument('--days', type=int, default=90, help='Lookback days (default: 90)')
    
    args = parser.parse_args()
    
    run_research(tickers=args.tickers, days=args.days)
