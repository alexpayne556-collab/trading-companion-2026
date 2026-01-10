#!/usr/bin/env python3
"""
🐺 WOLF INTELLIGENCE - DAILY HUNT WITH ML
Combines scanners + machine learning for ultimate edge
"""

import sys
sys.path.append('/workspaces/trading-companion-2026/tools')

from wolf_intelligence_engine import WolfIntelligence
import json

def daily_ml_hunt():
    """Run this every morning with scanner results"""
    
    print("🐺 WOLF INTELLIGENCE - DAILY ML HUNT")
    print("=" * 60)
    
    engine = WolfIntelligence()
    
    # Step 1: Analyze your sectors
    print("\n📊 ANALYZING YOUR SECTORS...")
    
    sectors = {
        'Nuclear': ['UUUU', 'CCJ', 'DNN', 'URG', 'URNM'],
        'Rare Earth': ['USAR', 'MP', 'UUUU', 'REES'],
        'Quantum': ['QUBT', 'QBTS', 'RGTI', 'IONQ'],
        'Space': ['RDW', 'LUNR', 'RKLB', 'ASTS'],
        'Defense': ['AISP', 'LMT', 'RTX', 'NOC']
    }
    
    results = {}
    
    for sector_name, tickers in sectors.items():
        print(f"\n🔍 {sector_name.upper()} SECTOR:")
        result = engine.analyze_sector_leader_laggard(tickers)
        if result:
            results[sector_name] = result
            
            # Trading recommendations
            if result['laggards']:
                laggard = result['laggards'][0]
                leader = result['leader']
                lag_hours = result['timing_lag_hours']
                
                print(f"\n   💡 TRADE SETUP:")
                print(f"      Watch {leader} (leader)")
                print(f"      If it breaks out → Buy {laggard} within {lag_hours:.0f}h")
                print(f"      {laggard} should follow the move")
    
    # Step 2: Predict win probability for current positions
    print(f"\n\n🎲 YOUR POSITIONS - ML ANALYSIS:")
    
    positions = {
        'USAR': {
            'sector_rank': 5,
            'options_vol_oi_ratio': 0,
            'volume_ratio': 1.5,
            'form4_buying': False,
            'has_8k': False,
            'change_1d': 0,
            'change_5d': 12,
            'change_20d': 18,
            'volatility': 0.05,
            'days_to_catalyst': 7  # Venezuela ongoing
        },
        'UUUU': {
            'sector_rank': 2,
            'options_vol_oi_ratio': 104.8,
            'volume_ratio': 2.0,
            'form4_buying': False,
            'has_8k': False,
            'change_1d': 3.2,
            'change_5d': 22.5,
            'change_20d': 19.2,
            'volatility': 0.045,
            'days_to_catalyst': 999  # No specific catalyst
        },
        'AISP': {
            'sector_rank': 8,
            'options_vol_oi_ratio': 0,
            'volume_ratio': 1.2,
            'form4_buying': False,
            'has_8k': False,
            'change_1d': 1.5,
            'change_5d': 8,
            'change_20d': 15,
            'volatility': 0.04,
            'days_to_catalyst': 999
        }
    }
    
    for ticker, data in positions.items():
        win_prob = engine.predict_win_probability(data)
        
        print(f"\n   {ticker}:")
        print(f"      Win Probability: {win_prob:.1%}")
        
        if win_prob > 0.65:
            print(f"      🟢 HIGH CONVICTION - Hold or add")
        elif win_prob > 0.50:
            print(f"      🟡 MEDIUM - Hold position")
        else:
            print(f"      🔴 RISKY - Consider exit")
    
    # Step 3: Save results
    output = {
        'date': '2026-01-06',
        'sectors_analyzed': results,
        'positions_analyzed': {k: {'win_prob': engine.predict_win_probability(v)} for k, v in positions.items()}
    }
    
    with open('/workspaces/trading-companion-2026/logs/wolf_intelligence/daily_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n\n🐺 ML ANALYSIS COMPLETE")
    print(f"   Results saved to: logs/wolf_intelligence/daily_analysis.json")
    print(f"   Use these insights + scanner data for positioning")
    print(f"\n   AWOOOO! 🐺\n")

if __name__ == '__main__':
    daily_ml_hunt()
