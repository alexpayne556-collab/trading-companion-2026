#!/usr/bin/env python3
"""
🐺 RESEARCH PROJECT 2: VOLUME DIVERGENCE PREDICTION

Question: When volume spikes 3x+ but price barely moves, what happens next day?

Hypothesis: Accumulation/distribution without price movement = coiled spring

Test Parameters:
- Volume: 3x+ above 20-day average
- Price: < 2% change on the volume spike day
- Outcome: Next-day move >3%

Success Criteria:
- 65%+ lead to 3%+ move next day
- 60%+ directional accuracy (if we can predict direction)
- 30+ events in 6 months

Tradeable Outcome:
If validated → "When {TICKER} has 3x volume but flat price, buy at close, expect {X}% move next day"

Built by: BROKKR
Specification by: TYR + FENRIR
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from wolf_pack_research import (
    WolfPackResearch,
    ValidationCriteria,
    format_percent,
    calculate_win_rate,
    NUCLEAR, AI_INFRA, SPACE_DEFENSE
)

# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def find_volume_divergences(
    df: pd.DataFrame,
    volume_multiplier: float = 3.0,
    price_threshold: float = 2.0,
    avg_window: int = 20
) -> pd.DataFrame:
    """
    Find days with volume divergence (high volume, low price change)
    
    Args:
        df: Price dataframe with OHLCV
        volume_multiplier: Volume must be X times average (default 3.0)
        price_threshold: Price change must be < X% (default 2.0)
        avg_window: Rolling window for average volume (default 20)
    
    Returns:
        DataFrame with divergence dates and characteristics
    """
    df = df.copy()
    
    # Calculate metrics
    df['Volume_Avg'] = df['Volume'].rolling(window=avg_window).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_Avg']
    df['Price_Change'] = df['Close'].pct_change() * 100
    df['Next_Day_Change'] = df['Price_Change'].shift(-1)
    df['Next_Day_High'] = ((df['High'].shift(-1) - df['Close']) / df['Close']) * 100
    df['Next_Day_Low'] = ((df['Low'].shift(-1) - df['Close']) / df['Close']) * 100
    df['Next_Day_MaxMove'] = df[['Next_Day_High', 'Next_Day_Low']].abs().max(axis=1)
    
    # Find divergences
    divergences = df[
        (df['Volume_Ratio'] >= volume_multiplier) &
        (abs(df['Price_Change']) < price_threshold)
    ].copy()
    
    # Classify next-day outcome
    divergences['Big_Move'] = divergences['Next_Day_MaxMove'] >= 3.0
    divergences['Direction'] = np.where(
        divergences['Next_Day_Change'] > 0, 'UP',
        np.where(divergences['Next_Day_Change'] < 0, 'DOWN', 'FLAT')
    )
    
    # Try to predict direction from volume character
    divergences['Close_Location'] = (
        (df.loc[divergences.index, 'Close'] - df.loc[divergences.index, 'Low']) /
        (df.loc[divergences.index, 'High'] - df.loc[divergences.index, 'Low'])
    )
    divergences['Predicted_Direction'] = np.where(
        divergences['Close_Location'] > 0.6, 'UP',  # Closed in upper 40%
        np.where(divergences['Close_Location'] < 0.4, 'DOWN', 'UNCERTAIN')  # Closed in lower 40%
    )
    divergences['Prediction_Correct'] = divergences['Predicted_Direction'] == divergences['Direction']
    
    return divergences[[
        'Close', 'Volume', 'Volume_Avg', 'Volume_Ratio', 'Price_Change',
        'Next_Day_Change', 'Next_Day_MaxMove', 'Big_Move', 'Direction',
        'Close_Location', 'Predicted_Direction', 'Prediction_Correct'
    ]]

def analyze_ticker(
    research: WolfPackResearch,
    ticker: str,
    volume_multiplier: float = 3.0,
    price_threshold: float = 2.0
) -> dict:
    """
    Analyze volume divergence pattern for a single ticker
    
    Returns:
        Dictionary with analysis results
    """
    if ticker not in research.data:
        return None
    
    df = research.data[ticker]
    divergences = find_volume_divergences(df, volume_multiplier, price_threshold)
    
    if len(divergences) == 0:
        return None
    
    # Calculate statistics
    total_events = len(divergences)
    big_move_rate = (divergences['Big_Move'].sum() / total_events) * 100
    
    # Direction accuracy (only for predictions that weren't UNCERTAIN)
    predictable = divergences[divergences['Predicted_Direction'] != 'UNCERTAIN']
    if len(predictable) > 0:
        direction_accuracy = (predictable['Prediction_Correct'].sum() / len(predictable)) * 100
        predictable_pct = (len(predictable) / total_events) * 100
    else:
        direction_accuracy = 0
        predictable_pct = 0
    
    # Average moves
    avg_next_day = divergences['Next_Day_Change'].mean()
    avg_max_move = divergences['Next_Day_MaxMove'].mean()
    
    # Direction breakdown
    up_count = (divergences['Direction'] == 'UP').sum()
    down_count = (divergences['Direction'] == 'DOWN').sum()
    flat_count = (divergences['Direction'] == 'FLAT').sum()
    
    return {
        'ticker': ticker,
        'total_events': total_events,
        'big_move_rate': big_move_rate,
        'direction_accuracy': direction_accuracy,
        'predictable_pct': predictable_pct,
        'avg_next_day_change': avg_next_day,
        'avg_max_move': avg_max_move,
        'up_count': up_count,
        'down_count': down_count,
        'flat_count': flat_count,
        'divergences': divergences
    }

# =============================================================================
# MAIN RESEARCH EXECUTION
# =============================================================================

def run_research(period='180d', volume_multiplier=3.0, price_threshold=2.0):
    """
    Run complete volume divergence research
    
    Args:
        period: Data lookback period
        volume_multiplier: Volume spike threshold (default 3.0x)
        price_threshold: Max price change % (default 2.0%)
    """
    print("="*80)
    print("🐺 RESEARCH PROJECT 2: VOLUME DIVERGENCE PREDICTION")
    print("="*80)
    print(f"\nParameters:")
    print(f"  Period: {period}")
    print(f"  Volume multiplier: {volume_multiplier}x average")
    print(f"  Price threshold: < {price_threshold}%")
    
    # Focus on Tier A stocks (under $25, most volatile)
    tier_a_tickers = [
        # Nuclear Tier A
        'DNN', 'URG', 'UEC', 'UUUU', 'SMR',
        # AI Infra Tier A
        'CIFR', 'WULF', 'BTBT', 'HUT', 'CLSK', 'CORZ',
        # Space Tier A
        'MNTS', 'SPCE', 'SATL', 'PL', 'RCAT', 'LUNR', 'KTOS'
    ]
    
    # Initialize research
    research = WolfPackResearch(tier_a_tickers)
    research.load_data(period=period)
    
    # Run analysis
    all_results = []
    
    print(f"\n{'='*80}")
    print(f"📊 ANALYZING TICKERS")
    print(f"{'='*80}\n")
    
    for ticker in tier_a_tickers:
        result = analyze_ticker(research, ticker, volume_multiplier, price_threshold)
        
        if result:
            all_results.append(result)
            print(f"✓ {ticker:<6} | Events: {result['total_events']:>3} | "
                  f"Big Move: {result['big_move_rate']:>5.1f}% | "
                  f"Direction: {result['direction_accuracy']:>5.1f}% | "
                  f"Avg: {format_percent(result['avg_next_day_change'])}")
    
    # Summary
    if all_results:
        print(f"\n{'='*80}")
        print(f"📊 RESEARCH SUMMARY")
        print(f"{'='*80}\n")
        
        # Aggregate statistics
        total_events = sum(r['total_events'] for r in all_results)
        total_big_moves = sum((r['big_move_rate'] / 100) * r['total_events'] for r in all_results)
        big_move_rate = (total_big_moves / total_events) * 100 if total_events > 0 else 0
        
        # Direction accuracy (weighted by predictable events)
        total_predictable = sum((r['predictable_pct'] / 100) * r['total_events'] for r in all_results)
        weighted_direction_acc = sum(
            (r['direction_accuracy'] * (r['predictable_pct'] / 100) * r['total_events']) 
            for r in all_results
        ) / total_predictable if total_predictable > 0 else 0
        
        print(f"Total events found: {total_events}")
        print(f"Big move rate (>3%): {big_move_rate:.1f}%")
        print(f"Direction accuracy: {weighted_direction_acc:.1f}%")
        print(f"Predictable events: {(total_predictable/total_events)*100:.1f}%")
        
        # Validation
        print(f"\n{'='*80}")
        print(f"✅ VALIDATION")
        print(f"{'='*80}\n")
        
        is_valid, message = ValidationCriteria.is_valid_edge(
            win_rate=big_move_rate,
            samples=total_events,
            risk_reward=1.0  # Simplified
        )
        
        print(f"Big move rate: {big_move_rate:.1f}% {'✅' if big_move_rate >= 65 else '❌'} (target: 65%)")
        print(f"Direction accuracy: {weighted_direction_acc:.1f}% {'✅' if weighted_direction_acc >= 60 else '❌'} (target: 60%)")
        print(f"Sample size: {total_events} {'✅' if total_events >= 30 else '❌'} (target: 30)")
        print(f"\n{' ✅' if is_valid else '❌'} {message}")
        
        # Top performers
        print(f"\n{'='*80}")
        print(f"🏆 TOP PERFORMERS (Best Big Move Rate)")
        print(f"{'='*80}\n")
        
        top_performers = sorted(all_results, key=lambda x: x['big_move_rate'], reverse=True)[:10]
        for i, r in enumerate(top_performers, 1):
            print(f"{i:2d}. {r['ticker']:<6} | {r['big_move_rate']:>5.1f}% big moves | "
                  f"{r['direction_accuracy']:>5.1f}% direction | {r['total_events']:>3} events")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        summary_data = []
        for r in all_results:
            summary_data.append({
                'Ticker': r['ticker'],
                'Events': r['total_events'],
                'Big_Move_Rate': f"{r['big_move_rate']:.1f}%",
                'Direction_Acc': f"{r['direction_accuracy']:.1f}%",
                'Predictable_Pct': f"{r['predictable_pct']:.1f}%",
                'Avg_Next_Day': format_percent(r['avg_next_day_change']),
                'Avg_Max_Move': format_percent(r['avg_max_move']),
                'Up': r['up_count'],
                'Down': r['down_count'],
                'Flat': r['flat_count']
            })
        
        summary_df = pd.DataFrame(summary_data)
        research.save_results(summary_df, f'project_2_summary_{timestamp}.csv')
        
        # Detailed results for top performers
        for r in top_performers[:5]:
            filename = f"project_2_detail_{r['ticker']}_{timestamp}.csv"
            research.save_results(r['divergences'].reset_index(), filename)
        
        # Tradeable pattern
        if is_valid and weighted_direction_acc >= 60:
            print(f"\n{'='*80}")
            print(f"💰 TRADEABLE PATTERN DISCOVERED")
            print(f"{'='*80}\n")
            print(f"When stock has {volume_multiplier}x volume but < {price_threshold}% price change:")
            print(f"  • {big_move_rate:.0f}% chance of >3% move next day")
            print(f"  • {weighted_direction_acc:.0f}% direction accuracy (when predictable)")
            print(f"  • Check close location: >0.6 = bullish, <0.4 = bearish")
            print(f"  • Entry: At close on divergence day")
            print(f"  • Target: +3% next day")
            print(f"  • Stop: -2%")
    
    print(f"\n🐺 LLHR. Project 2 complete.")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Research Project 2: Volume Divergence Prediction')
    parser.add_argument('--period', default='180d', help='Data period (default: 180d)')
    parser.add_argument('--volume', type=float, default=3.0, help='Volume multiplier (default: 3.0)')
    parser.add_argument('--price', type=float, default=2.0, help='Price threshold % (default: 2.0)')
    
    args = parser.parse_args()
    
    run_research(
        period=args.period,
        volume_multiplier=args.volume,
        price_threshold=args.price
    )
