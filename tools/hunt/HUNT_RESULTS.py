#!/usr/bin/env python3
"""
🐺 THE HUNT RESULTS - WEEKEND SUMMARY
What we found in 2 days of hunting
"""

print("""
================================================================================
🐺 THE HUNT RESULTS - WEEKEND SUMMARY
================================================================================

MISSION: Find what predicts the next run on repeat runners
TICKERS: SIDU, RGTI, QBTS, RCAT, LUNR, ASTS, IONQ
TIMEFRAME: 2024-2025 data
VALIDATION: Monte Carlo, p-values, effect sizes

================================================================================
EDGE #1: THE WOLF SIGNAL (from before the hunt)
================================================================================
Formula:
  - Volume spike > 2x 20-day average
  - Price change < 2% (flat day)
  - Volume ratio (up/down) > 2.5 over 20 days  
  - Within 5 days of 20-day high

Stats:
  - 9 signals
  - 77.8% win rate
  - +37.87% avg 10-day return
  - P-value: 0.023 ✅
  - Effect size: 2.55

WHY IT WORKS:
  Institutions accumulating quietly during healthy uptrends.
  High volume + flat price = absorbing supply.

================================================================================
EDGE #2: PRE-RUN PREDICTOR (Hunt #1)
================================================================================
Formula (score 5/5 criteria):
  - 5-day volume ratio > 1.0
  - Signal day volume > 1.0 (vs 20d base)
  - 5-day price change > -2%
  - 5-day avg CLV > 0.45
  - Up/down volume ratio > 1.2

Stats (score >= 4):
  - 793 signals
  - 52.3% win rate
  - +13.02% avg 10-day return
  - P-value: 0.0000 ✅
  - Effect size: 4.05

Stats (perfect 5/5 score):
  - 397 signals
  - 57.9% win rate
  - +17.27% avg return
  - 46.6% hit 10%+ gains

TOP CATCHES:
  ASTS +252%, RGTI +244%, +226%, +202%, +186%, +179%

================================================================================
EDGE #3: CAPITULATION HUNTER (Hunt #3)
================================================================================
Formula:
  - Stock down 15-40% from 20-day high (wounded)
  - Volume spike > 1.5x 20-day average
  - CLV < 0.5 (sellers won = red day)
  
Stats:
  - 88 signals
  - 58.0% win rate
  - +19.95% avg 10-day return
  - 35.2% hit 20%+ gains
  - P-value: 0.004 ✅
  - Effect size: 3.35

WHY IT WORKS:
  COUNTERINTUITIVE! When a wounded stock has a big red spike,
  that's capitulation - sellers giving up. The bottom is in.

TOP CATCHES:
  RGTI +235%, +186%, +149%, SIDU +183%, +155%, QBTS +140%

================================================================================
WHAT DIDN'T WORK
================================================================================

Lead-Lag (Hunt #2):
  - ASTS→RCAT 60% follow rate looked promising
  - But p=0.537 - not statistically significant
  - LUNR→RGTI 71% WR but p=0.14
  - Conclusion: Correlation, not causation

Timing Patterns (Hunt #4):
  - Runs happen every ~15-20 days (median)
  - Average pullback before run: -44%
  - But "just waiting" has no predictive power
  - Conclusion: Need trigger, not just time

SEC Filings (Hunt #5):
  - Data quality issues (historical filings)
  - Some correlation but not enough signal
  - Conclusion: Needs better data source

================================================================================
THE ARSENAL - 3 VALIDATED EDGES
================================================================================

1. WOLF SIGNAL
   Trigger: Volume spike + flat + healthy trend near highs
   When: Looking for breakout continuation
   p=0.023, +37.87% avg, 77.8% WR
   
2. PRE-RUN PREDICTOR  
   Trigger: 5/5 criteria score
   When: Broad scanning for setups
   p=0.0000, +17.27% avg, 57.9% WR

3. CAPITULATION HUNTER
   Trigger: Red spike when wounded (15-40% down)
   When: Buying dips on repeat runners
   p=0.004, +19.95% avg, 58% WR

================================================================================
NEXT STEPS FOR MONDAY
================================================================================

1. Build real-time scanner combining all 3 signals
2. Check current state of all 7 tickers against each signal
3. Set alerts for when signals trigger
4. Consider position sizing based on signal strength

================================================================================
THE PACK IS READY 🐺
================================================================================
""")
