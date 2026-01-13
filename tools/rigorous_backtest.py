#!/usr/bin/env python3
"""
🐺 RIGOROUS BACKTESTING FRAMEWORK
==================================
Tyr's requirement: Test EVERYTHING on MANY tickers before claiming it works.

Not testing on winners only. Testing on EVERYONE:
- Winners AND losers
- Stocks that had the pattern and moved
- Stocks that had the pattern and did NOTHING

Only after passing THIS test do we add to dashboard.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("🐺 RIGOROUS BACKTESTING - No Bullshit, Just Facts")
print("="*80)
print("Testing our claimed 'edges' on MANY tickers, not just winners")
print("="*80)

# =============================================================================
# THE UNIVERSE - Not just winners, EVERYONE
# =============================================================================

# Winners we know about
KNOWN_WINNERS = [
    'EVTV', 'ATON', 'LVLU', 'PASW', 'ALMS', 'BEAM', 'MNTS', 
    'VCIG', 'OMH', 'RARE', 'NTLA', 'MU', 'ARDX', 'SATL'
]

# Micro-caps that DIDN'T explode (to test false positives)
MICRO_CAPS_QUIET = [
    'XBIO', 'KOSS', 'SKLZ', 'BBIG', 'ATXI', 'RCAT', 'DGXX',
    'GEVO', 'WKHS', 'GOEV', 'AEHR', 'ACHR', 'JOBY', 'LILM',
    'SOFI', 'WISH', 'CLOV', 'RIDE', 'NKLA', 'SPCE'
]

# Biotechs that didn't move
BIOTECH_QUIET = [
    'CRSP', 'EDIT', 'VERV', 'BLUE', 'SRPT', 'ARWR', 'IONS',
    'NBIX', 'EXAS', 'VRTX', 'REGN', 'BIIB'
]

ALL_TEST_TICKERS = KNOWN_WINNERS + MICRO_CAPS_QUIET + BIOTECH_QUIET

print(f"\nTest Universe:")
print(f"  Known Winners: {len(KNOWN_WINNERS)}")
print(f"  Micro-caps (no move): {len(MICRO_CAPS_QUIET)}")
print(f"  Biotechs (no move): {len(BIOTECH_QUIET)}")
print(f"  TOTAL: {len(ALL_TEST_TICKERS)} tickers")

# =============================================================================
# EDGE 1: MICRO-CAP EXPLOSIVE PATTERN
# =============================================================================
print("\n" + "="*80)
print("EDGE 1: MICRO-CAP EXPLOSIVE PATTERN")
print("="*80)
print("CLAIM: Micro-cap (<$100M) + Tiny float (<10M) + Volume spike = Explosion")
print("TEST: Does this pattern predict moves, or just describe winners?")

def test_microcap_explosive(symbols, lookback_days=30):
    """
    Test the micro-cap explosive pattern on all tickers.
    
    TRUE POSITIVE: Pattern present AND stock moved big
    FALSE POSITIVE: Pattern present BUT stock did nothing
    TRUE NEGATIVE: No pattern AND stock did nothing
    FALSE NEGATIVE: No pattern BUT stock moved anyway
    """
    results = []
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period=f"{lookback_days}d")
            
            if len(hist) < 10:
                continue
            
            # Get characteristics
            market_cap = info.get('marketCap', 0)
            float_shares = info.get('floatShares', 0)
            
            # Calculate volume ratio
            today_vol = hist['Volume'].iloc[-1]
            avg_vol = hist['Volume'].iloc[:-1].mean() if len(hist) > 1 else today_vol
            vol_ratio = today_vol / avg_vol if avg_vol > 0 else 1
            
            # Calculate max move in period
            returns = hist['Close'].pct_change() * 100
            max_daily_move = returns.max()
            
            # Did stock move big? (>20% in any day)
            did_move_big = max_daily_move > 20
            
            # Does it match pattern?
            matches_pattern = (
                market_cap < 100_000_000 and  # Micro-cap
                float_shares < 10_000_000 and  # Tiny float
                vol_ratio > 2.0  # Volume spike
            )
            
            # Classify
            if matches_pattern and did_move_big:
                result = "TRUE_POSITIVE"
            elif matches_pattern and not did_move_big:
                result = "FALSE_POSITIVE"
            elif not matches_pattern and not did_move_big:
                result = "TRUE_NEGATIVE"
            else:
                result = "FALSE_NEGATIVE"
            
            results.append({
                'symbol': symbol,
                'market_cap_m': market_cap / 1e6 if market_cap else 0,
                'float_m': float_shares / 1e6 if float_shares else 0,
                'vol_ratio': vol_ratio,
                'max_move': max_daily_move,
                'matches_pattern': matches_pattern,
                'did_move': did_move_big,
                'result': result
            })
            
        except Exception as e:
            continue
    
    return pd.DataFrame(results)

print("\nRunning test on full universe...")
microcap_results = test_microcap_explosive(ALL_TEST_TICKERS, lookback_days=30)

if len(microcap_results) > 0:
    # Calculate accuracy metrics
    true_pos = len(microcap_results[microcap_results['result'] == 'TRUE_POSITIVE'])
    false_pos = len(microcap_results[microcap_results['result'] == 'FALSE_POSITIVE'])
    true_neg = len(microcap_results[microcap_results['result'] == 'TRUE_NEGATIVE'])
    false_neg = len(microcap_results[microcap_results['result'] == 'FALSE_NEGATIVE'])
    
    precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0
    recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0
    accuracy = (true_pos + true_neg) / len(microcap_results)
    
    print(f"\n📊 RESULTS:")
    print(f"   True Positives: {true_pos} (Pattern + Move)")
    print(f"   False Positives: {false_pos} (Pattern but NO move) ⚠️")
    print(f"   True Negatives: {true_neg} (No pattern, no move)")
    print(f"   False Negatives: {false_neg} (No pattern but moved anyway)")
    print(f"\n   Precision: {precision*100:.1f}% (When pattern shows, how often does it work?)")
    print(f"   Recall: {recall*100:.1f}% (Of all big moves, how many did we catch?)")
    print(f"   Accuracy: {accuracy*100:.1f}%")
    
    print(f"\n🔴 FALSE POSITIVES (Pattern but didn't move):")
    false_pos_df = microcap_results[microcap_results['result'] == 'FALSE_POSITIVE']
    for _, row in false_pos_df.head(10).iterrows():
        print(f"   {row['symbol']:6} | MCap: ${row['market_cap_m']:.0f}M | Float: {row['float_m']:.1f}M | Vol: {row['vol_ratio']:.1f}x | Max move: {row['max_move']:.1f}%")
    
    microcap_results.to_csv('backtest_microcap_explosive.csv', index=False)
    print(f"\n✓ Saved detailed results to backtest_microcap_explosive.csv")

# =============================================================================
# EDGE 2: COILED SPRING PATTERN
# =============================================================================
print("\n" + "="*80)
print("EDGE 2: COILED SPRING PATTERN")
print("="*80)
print("CLAIM: Intraday spike + fade predicts after-hours explosion")
print("TEST: Does this actually predict AH moves?")

def test_coiled_spring(symbols):
    """
    Test if coiled spring pattern predicts after-hours moves.
    
    Need to check:
    1. Did stock spike intraday?
    2. Did it fade from high?
    3. Did it explode after-hours?
    """
    results = []
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            
            # Get last 5 days
            hist = ticker.history(period='5d')
            
            if len(hist) < 2:
                continue
            
            # For each day, check if coiled spring appeared
            for i in range(len(hist)-1):
                date = hist.index[i]
                
                # Today's data
                open_price = hist['Open'].iloc[i]
                high = hist['High'].iloc[i]
                close = hist['Close'].iloc[i]
                
                # Next day's data (to see if it continued)
                next_open = hist['Open'].iloc[i+1]
                next_high = hist['High'].iloc[i+1]
                
                # Spike magnitude
                spike = (high - open_price) / open_price * 100 if open_price > 0 else 0
                
                # Fade from high
                fade = (close - high) / high * 100 if high > 0 else 0
                
                # Next day move
                next_move = (next_high - close) / close * 100 if close > 0 else 0
                
                # Coiled spring pattern?
                is_coiled = spike > 10 and fade < -5
                
                # Did it continue next day?
                did_continue = next_move > 5
                
                if is_coiled:
                    result = "TRUE_POSITIVE" if did_continue else "FALSE_POSITIVE"
                    
                    results.append({
                        'symbol': symbol,
                        'date': date.strftime('%Y-%m-%d'),
                        'spike_pct': spike,
                        'fade_pct': fade,
                        'next_move_pct': next_move,
                        'is_coiled': is_coiled,
                        'did_continue': did_continue,
                        'result': result
                    })
            
        except Exception as e:
            continue
    
    return pd.DataFrame(results)

print("\nRunning test on full universe...")
coiled_results = test_coiled_spring(ALL_TEST_TICKERS)

if len(coiled_results) > 0:
    true_pos = len(coiled_results[coiled_results['result'] == 'TRUE_POSITIVE'])
    false_pos = len(coiled_results[coiled_results['result'] == 'FALSE_POSITIVE'])
    
    precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0
    
    print(f"\n📊 RESULTS:")
    print(f"   Coiled springs found: {len(coiled_results)}")
    print(f"   Continued next day: {true_pos}")
    print(f"   Did NOT continue: {false_pos}")
    print(f"   Success Rate: {precision*100:.1f}%")
    
    print(f"\n🔴 FALSE POSITIVES (Coiled but didn't continue):")
    false_pos_df = coiled_results[coiled_results['result'] == 'FALSE_POSITIVE']
    for _, row in false_pos_df.head(10).iterrows():
        print(f"   {row['symbol']:6} {row['date']} | Spike: +{row['spike_pct']:.1f}% | Fade: {row['fade_pct']:.1f}% | Next: {row['next_move_pct']:+.1f}%")
    
    coiled_results.to_csv('backtest_coiled_spring.csv', index=False)
    print(f"\n✓ Saved detailed results to backtest_coiled_spring.csv")

# =============================================================================
# EDGE 3: BIOTECH CATALYST PATTERN
# =============================================================================
print("\n" + "="*80)
print("EDGE 3: BIOTECH CATALYST PATTERN")
print("="*80)
print("CLAIM: Biotech + News/SEC filing = Consistent gains")
print("TEST: Do biotechs with news actually move consistently?")

def test_biotech_catalyst(symbols):
    """
    Test if biotech stocks move on news.
    
    Problem: We can't easily detect "news" with free data.
    So we'll use volume spike as proxy for "something happened".
    """
    results = []
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period='30d')
            
            if len(hist) < 10:
                continue
            
            # Is it a biotech?
            sector = info.get('sector', '')
            industry = info.get('industry', '')
            is_biotech = 'health' in sector.lower() or 'biotech' in industry.lower()
            
            if not is_biotech:
                continue
            
            # Find days with volume spikes (proxy for news)
            hist['vol_ratio'] = hist['Volume'] / hist['Volume'].rolling(20).mean()
            hist['return'] = hist['Close'].pct_change() * 100
            
            # Days with volume spike (>2x)
            news_days = hist[hist['vol_ratio'] > 2.0]
            
            if len(news_days) == 0:
                continue
            
            # Of those days, how many moved up?
            positive_moves = len(news_days[news_days['return'] > 0])
            total_news_days = len(news_days)
            
            avg_move = news_days['return'].mean()
            
            results.append({
                'symbol': symbol,
                'sector': sector,
                'industry': industry,
                'news_days': total_news_days,
                'positive_moves': positive_moves,
                'win_rate': positive_moves / total_news_days if total_news_days > 0 else 0,
                'avg_move': avg_move
            })
            
        except Exception as e:
            continue
    
    return pd.DataFrame(results)

print("\nRunning test on biotech universe...")
biotech_results = test_biotech_catalyst(ALL_TEST_TICKERS)

if len(biotech_results) > 0:
    avg_win_rate = biotech_results['win_rate'].mean()
    avg_move = biotech_results['avg_move'].mean()
    
    print(f"\n📊 RESULTS:")
    print(f"   Biotechs tested: {len(biotech_results)}")
    print(f"   Average win rate on news: {avg_win_rate*100:.1f}%")
    print(f"   Average move on news: {avg_move:+.1f}%")
    
    print(f"\n📋 TOP PERFORMERS:")
    top = biotech_results.sort_values('win_rate', ascending=False).head(10)
    for _, row in top.iterrows():
        print(f"   {row['symbol']:6} | Win rate: {row['win_rate']*100:.0f}% | Avg move: {row['avg_move']:+.1f}% | News days: {row['news_days']}")
    
    biotech_results.to_csv('backtest_biotech_catalyst.csv', index=False)
    print(f"\n✓ Saved detailed results to backtest_biotech_catalyst.csv")

# =============================================================================
# FINAL VERDICT
# =============================================================================
print("\n" + "="*80)
print("🎯 FINAL VERDICT - What Actually Works?")
print("="*80)

print("""
Based on rigorous testing across MANY tickers (winners AND losers):

1. MICRO-CAP EXPLOSIVE PATTERN
   - Tested on: {} tickers
   - Precision: {}%
   - VERDICT: {}

2. COILED SPRING PATTERN
   - Tested on: {} instances
   - Success rate: {}%
   - VERDICT: {}

3. BIOTECH CATALYST PATTERN
   - Tested on: {} biotechs
   - Average win rate: {}%
   - VERDICT: {}

🐺 BROKKR'S HONEST ASSESSMENT:
Only patterns with >60% success rate go into dashboard.
The rest need more work or get discarded.

This is how we build confidence - test EVERYTHING before claiming it works.
""".format(
    len(microcap_results) if len(microcap_results) > 0 else 0,
    f"{precision*100:.1f}" if len(microcap_results) > 0 else "N/A",
    "✅ ADD TO DASHBOARD" if len(microcap_results) > 0 and precision > 0.6 else "❌ NEEDS WORK",
    len(coiled_results) if len(coiled_results) > 0 else 0,
    f"{precision*100:.1f}" if len(coiled_results) > 0 else "N/A",
    "✅ ADD TO DASHBOARD" if len(coiled_results) > 0 and precision > 0.6 else "❌ NEEDS WORK",
    len(biotech_results) if len(biotech_results) > 0 else 0,
    f"{avg_win_rate*100:.1f}" if len(biotech_results) > 0 else "N/A",
    "✅ ADD TO DASHBOARD" if len(biotech_results) > 0 and avg_win_rate > 0.6 else "❌ NEEDS WORK"
))

print("\n🐺 AWOOOO - Truth over comfort. Always.")
