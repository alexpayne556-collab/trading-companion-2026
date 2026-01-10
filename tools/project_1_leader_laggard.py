#!/usr/bin/env python3
"""
🐺 RESEARCH PROJECT 1: LEADER/LAGGARD LAG TIME

Question: When a leader moves, how long until laggards follow?

Test Pairs:
- Nuclear: CCJ → DNN/UEC/UUUU
- AI: NVDA → APLD/IREN/MARA
- Space: RKLB → LUNR/ASTS

Success Criteria:
- 70%+ consistency (laggard follows leader direction)
- 50%+ magnitude follow-through (laggard moves at least 50% of leader's move)
- 15+ events in 6 months
- Lag window: 1-5 days

Tradeable Outcome:
If validated → "When {LEADER} moves {X}%, buy {LAGGARD} next day, expect {Y}% move within {Z} days"

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
    calculate_win_rate
)

# =============================================================================
# LEADER/LAGGARD PAIRS
# =============================================================================

LEADER_LAGGARD_PAIRS = {
    'nuclear': {
        'leader': 'CCJ',
        'laggards': ['DNN', 'UEC', 'UUUU', 'URG', 'SMR']
    },
    'ai_infra': {
        'leader': 'NVDA',
        'laggards': ['APLD', 'IREN', 'MARA', 'WULF', 'CIFR']
    },
    'space': {
        'leader': 'RKLB',
        'laggards': ['LUNR', 'ASTS', 'MNTS', 'PL']
    }
}

# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def find_leader_moves(df: pd.DataFrame, threshold: float = 5.0) -> pd.DataFrame:
    """
    Find significant moves in leader stock
    
    Args:
        df: Price dataframe with OHLCV
        threshold: Minimum percent move (default 5%)
    
    Returns:
        DataFrame with leader move dates and magnitudes
    """
    df = df.copy()
    df['Return'] = df['Close'].pct_change() * 100
    
    # Find days with significant moves
    big_moves = df[abs(df['Return']) >= threshold].copy()
    big_moves['Direction'] = np.where(big_moves['Return'] > 0, 'UP', 'DOWN')
    
    return big_moves[['Close', 'Return', 'Direction']]

def analyze_laggard_response(
    leader_moves: pd.DataFrame,
    laggard_df: pd.DataFrame,
    max_lag_days: int = 5
) -> pd.DataFrame:
    """
    Analyze how laggard responds to leader moves
    
    Args:
        leader_moves: DataFrame of leader moves (from find_leader_moves)
        laggard_df: Price dataframe for laggard
        max_lag_days: Maximum days to check for response
    
    Returns:
        DataFrame with lag analysis
    """
    results = []
    
    for date, row in leader_moves.iterrows():
        leader_return = row['Return']
        leader_direction = row['Direction']
        
        # Check laggard response in next N days
        future_dates = pd.date_range(
            start=date + timedelta(days=1),
            periods=max_lag_days,
            freq='D'
        )
        
        for lag_days in range(1, max_lag_days + 1):
            future_date = date + timedelta(days=lag_days)
            
            # Find next available trading day
            available_dates = laggard_df.index[laggard_df.index >= future_date]
            if len(available_dates) == 0:
                continue
            
            check_date = available_dates[0]
            
            # Calculate laggard return from leader move date to check date
            if date not in laggard_df.index or check_date not in laggard_df.index:
                continue
            
            laggard_start = laggard_df.loc[date, 'Close']
            laggard_end = laggard_df.loc[check_date, 'Close']
            laggard_return = ((laggard_end - laggard_start) / laggard_start) * 100
            
            # Check if direction matched
            direction_match = (
                (leader_direction == 'UP' and laggard_return > 0) or
                (leader_direction == 'DOWN' and laggard_return < 0)
            )
            
            # Check magnitude follow-through
            magnitude_ratio = abs(laggard_return) / abs(leader_return) if leader_return != 0 else 0
            
            results.append({
                'leader_date': date,
                'leader_return': leader_return,
                'leader_direction': leader_direction,
                'lag_days': lag_days,
                'check_date': check_date,
                'laggard_return': laggard_return,
                'direction_match': direction_match,
                'magnitude_ratio': magnitude_ratio,
                'followed_50pct': magnitude_ratio >= 0.5
            })
    
    return pd.DataFrame(results)

def analyze_pair(
    research: WolfPackResearch,
    leader: str,
    laggard: str,
    move_threshold: float = 5.0,
    max_lag: int = 5
) -> dict:
    """
    Analyze leader/laggard relationship
    
    Returns:
        Dictionary with analysis results
    """
    print(f"\n{'='*80}")
    print(f"🎯 ANALYZING: {leader} → {laggard}")
    print(f"{'='*80}")
    
    # Get data
    if leader not in research.data or laggard not in research.data:
        print(f"❌ Missing data for {leader} or {laggard}")
        return None
    
    leader_df = research.data[leader]
    laggard_df = research.data[laggard]
    
    # Find leader moves
    leader_moves = find_leader_moves(leader_df, threshold=move_threshold)
    print(f"\n📊 Found {len(leader_moves)} leader moves (>{move_threshold}%)")
    
    if len(leader_moves) == 0:
        print(f"⚠️  No significant moves found")
        return None
    
    # Analyze laggard response
    lag_analysis = analyze_laggard_response(leader_moves, laggard_df, max_lag_days=max_lag)
    
    if len(lag_analysis) == 0:
        print(f"⚠️  No laggard data available")
        return None
    
    # Calculate statistics by lag day
    print(f"\n📈 LAG ANALYSIS:")
    print(f"{'Lag Days':<12} {'Events':<10} {'Direction':<15} {'Magnitude':<15} {'Both':<15}")
    print("-" * 70)
    
    lag_stats = []
    for lag in range(1, max_lag + 1):
        lag_data = lag_analysis[lag_analysis['lag_days'] == lag]
        
        if len(lag_data) == 0:
            continue
        
        direction_accuracy = (lag_data['direction_match'].sum() / len(lag_data)) * 100
        magnitude_accuracy = (lag_data['followed_50pct'].sum() / len(lag_data)) * 100
        both_accuracy = ((lag_data['direction_match'] & lag_data['followed_50pct']).sum() / len(lag_data)) * 100
        
        lag_stats.append({
            'lag_days': lag,
            'events': len(lag_data),
            'direction_accuracy': direction_accuracy,
            'magnitude_accuracy': magnitude_accuracy,
            'both_accuracy': both_accuracy
        })
        
        print(f"{lag:<12} {len(lag_data):<10} {direction_accuracy:>6.1f}%        {magnitude_accuracy:>6.1f}%        {both_accuracy:>6.1f}%")
    
    # Best lag day
    if lag_stats:
        best_lag = max(lag_stats, key=lambda x: x['both_accuracy'])
        print(f"\n🎯 BEST LAG: {best_lag['lag_days']} days")
        print(f"   Direction accuracy: {best_lag['direction_accuracy']:.1f}%")
        print(f"   Magnitude accuracy: {best_lag['magnitude_accuracy']:.1f}%")
        print(f"   Both: {best_lag['both_accuracy']:.1f}%")
        print(f"   Sample size: {best_lag['events']} events")
        
        # Validation
        is_valid, message = ValidationCriteria.is_valid_edge(
            win_rate=best_lag['both_accuracy'],
            samples=best_lag['events'],
            risk_reward=1.0  # Simplified for directional accuracy
        )
        
        print(f"\n{'✅' if is_valid else '❌'} {message}")
        
        return {
            'leader': leader,
            'laggard': laggard,
            'total_events': len(leader_moves),
            'best_lag_days': best_lag['lag_days'],
            'direction_accuracy': best_lag['direction_accuracy'],
            'magnitude_accuracy': best_lag['magnitude_accuracy'],
            'both_accuracy': best_lag['both_accuracy'],
            'sample_size': best_lag['events'],
            'validated': is_valid,
            'validation_message': message,
            'lag_analysis': lag_analysis,
            'lag_stats': pd.DataFrame(lag_stats)
        }
    
    return None

# =============================================================================
# MAIN RESEARCH EXECUTION
# =============================================================================

def run_research(period='180d', move_threshold=5.0, max_lag=5):
    """
    Run complete leader/laggard research
    
    Args:
        period: Data lookback period
        move_threshold: Minimum % move to trigger (default 5%)
        max_lag: Maximum lag days to check (default 5)
    """
    print("="*80)
    print("🐺 RESEARCH PROJECT 1: LEADER/LAGGARD LAG TIME")
    print("="*80)
    print(f"\nParameters:")
    print(f"  Period: {period}")
    print(f"  Move threshold: {move_threshold}%")
    print(f"  Max lag: {max_lag} days")
    
    # Initialize research
    research = WolfPackResearch()
    
    # Load data
    research.load_data(period=period)
    
    # Run analysis for each sector
    all_results = []
    
    for sector, pairs in LEADER_LAGGARD_PAIRS.items():
        print(f"\n{'#'*80}")
        print(f"📊 SECTOR: {sector.upper()}")
        print(f"{'#'*80}")
        
        leader = pairs['leader']
        laggards = pairs['laggards']
        
        for laggard in laggards:
            result = analyze_pair(
                research,
                leader=leader,
                laggard=laggard,
                move_threshold=move_threshold,
                max_lag=max_lag
            )
            
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
                'Pair': f"{r['leader']} → {r['laggard']}",
                'Best Lag': f"{r['best_lag_days']} days",
                'Direction': f"{r['direction_accuracy']:.1f}%",
                'Magnitude': f"{r['magnitude_accuracy']:.1f}%",
                'Both': f"{r['both_accuracy']:.1f}%",
                'Samples': r['sample_size'],
                'Validated': '✅' if r['validated'] else '❌'
            })
        
        summary_df = pd.DataFrame(summary_data)
        print(summary_df.to_string(index=False))
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        research.save_results(summary_df, f'project_1_summary_{timestamp}.csv')
        
        # Detailed results
        for r in all_results:
            filename = f"project_1_detail_{r['leader']}_{r['laggard']}_{timestamp}.csv"
            research.save_results(r['lag_analysis'], filename)
        
        # Count validated edges
        validated_count = sum(1 for r in all_results if r['validated'])
        print(f"\n🎯 VALIDATED EDGES: {validated_count}/{len(all_results)}")
        
        if validated_count > 0:
            print(f"\n✅ TRADEABLE PATTERNS DISCOVERED:")
            for r in all_results:
                if r['validated']:
                    print(f"   • When {r['leader']} moves >{move_threshold}%, "
                          f"buy {r['laggard']} next day, expect {r['both_accuracy']:.0f}% follow-through "
                          f"within {r['best_lag_days']} days")
    
    print(f"\n🐺 LLHR. Project 1 complete.")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Research Project 1: Leader/Laggard Lag Time')
    parser.add_argument('--period', default='180d', help='Data period (default: 180d)')
    parser.add_argument('--threshold', type=float, default=5.0, help='Move threshold % (default: 5.0)')
    parser.add_argument('--max-lag', type=int, default=5, help='Max lag days (default: 5)')
    
    args = parser.parse_args()
    
    run_research(
        period=args.period,
        move_threshold=args.threshold,
        max_lag=args.max_lag
    )
