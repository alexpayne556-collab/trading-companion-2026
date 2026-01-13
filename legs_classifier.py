#!/usr/bin/env python3
"""
🐺 LEGS CLASSIFIER - Does This Move Have Staying Power?

For each discovered mover, classify:
- STRONG LEGS: Small float + increasing volume + catalyst + hot sector
- WEAK LEGS: Large float + declining volume + no catalyst + pump
- FADING: Already exhausted, late to the party

Like ATON - you jumped on after +40% but it had LEGS, went another +39%.
vs pump-and-dumps that gap 100% then bleed all day.

This tells you: CHASE or WAIT?
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add webapp to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'webapp'))

try:
    from intelligence_db import log_alert
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


def get_float_size(ticker):
    """
    Get float size - critical for determining if move has room
    Small float (<50M) = can run hard
    Large float (>500M) = harder to move
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        shares_float = info.get('floatShares', info.get('sharesOutstanding', 0))
        
        if shares_float == 0:
            return None, "UNKNOWN"
        
        # Classify
        if shares_float < 20_000_000:
            size = "MICRO"  # Can 5-10x on volume
        elif shares_float < 50_000_000:
            size = "SMALL"  # Can 2-5x on volume
        elif shares_float < 200_000_000:
            size = "MEDIUM"  # Can move 50-100%
        elif shares_float < 500_000_000:
            size = "LARGE"  # Hard to move >50%
        else:
            size = "MEGA"  # Moves slowly
        
        return shares_float, size
        
    except:
        return None, "UNKNOWN"


def check_volume_trend(ticker):
    """
    Is volume INCREASING (bullish) or DECREASING (bearish)?
    Compare last 3 days vs previous 10 days
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1mo', interval='1d')
        
        if len(hist) < 13:
            return None, "INSUFFICIENT_DATA"
        
        # Last 3 days avg volume
        recent_vol = hist['Volume'].tail(3).mean()
        
        # Previous 10 days avg volume
        baseline_vol = hist['Volume'].iloc[-13:-3].mean()
        
        if baseline_vol == 0:
            return None, "NO_BASELINE"
        
        change = ((recent_vol - baseline_vol) / baseline_vol) * 100
        
        # Classify trend
        if change >= 100:
            trend = "SURGING"  # 2x+ volume = strong interest
        elif change >= 50:
            trend = "RISING"  # Building momentum
        elif change >= 0:
            trend = "STEADY"  # Holding interest
        elif change >= -30:
            trend = "FADING"  # Losing interest
        else:
            trend = "COLLAPSING"  # Interest dying
        
        return change, trend
        
    except:
        return None, "ERROR"


def check_price_action(ticker, days=5):
    """
    Check if price is building a base (bullish) or just spiking (risky)
    - Higher lows = accumulation = LEGS
    - Spike-and-fade = exhaustion = NO LEGS
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1mo', interval='1d')
        
        if len(hist) < days:
            return "INSUFFICIENT_DATA"
        
        recent = hist.tail(days)
        lows = recent['Low'].values
        highs = recent['High'].values
        
        # Check for higher lows (accumulation pattern)
        higher_lows = all(lows[i] >= lows[i-1] * 0.95 for i in range(1, len(lows)))
        
        # Check for consolidation (range tightening)
        recent_range = highs[-1] - lows[-1]
        prev_range = highs[0] - lows[0]
        consolidating = recent_range < prev_range * 1.2
        
        # Check for parabolic move (unsustainable)
        price_5d_ago = hist.iloc[-6]['Close'] if len(hist) >= 6 else hist.iloc[0]['Close']
        price_now = hist.iloc[-1]['Close']
        pct_move_5d = ((price_now - price_5d_ago) / price_5d_ago) * 100
        
        if pct_move_5d > 100:
            return "PARABOLIC"  # Too fast, likely to fade
        elif higher_lows and consolidating:
            return "ACCUMULATION"  # Building base = LEGS
        elif higher_lows:
            return "BUILDING"  # Uptrend forming
        elif pct_move_5d > 50:
            return "SPIKE"  # Sharp move, watch for fade
        else:
            return "CHOPPY"  # No clear pattern
        
    except:
        return "ERROR"


def has_recent_catalyst(ticker):
    """
    Check if there's a recent catalyst (news in last 7 days)
    Real catalysts = LEGS
    No catalyst = Likely pump
    """
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        if not news:
            return False, "NO_NEWS"
        
        # Check for recent news (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_news = [n for n in news if datetime.fromtimestamp(n.get('providerPublishTime', 0)) > week_ago]
        
        if len(recent_news) >= 2:
            return True, f"{len(recent_news)}_ITEMS"
        elif len(recent_news) == 1:
            return True, "1_ITEM"
        else:
            return False, "STALE_NEWS"
        
    except:
        return False, "ERROR"


def classify_legs(ticker):
    """
    Main classification: Does this ticker have LEGS or is it FADING?
    
    Returns:
    - legs_score: 0-10 (10 = strongest legs)
    - classification: STRONG_LEGS, MODERATE_LEGS, WEAK_LEGS, FADING
    - reasons: Why it has/doesn't have legs
    """
    
    print(f"\n🔍 Analyzing {ticker}...")
    
    reasons = []
    score = 5  # Start neutral
    
    # 1. Float size
    float_shares, float_size = get_float_size(ticker)
    if float_size == "MICRO":
        score += 2
        reasons.append(f"MICRO float ({float_shares:,}) - Can run HARD")
    elif float_size == "SMALL":
        score += 1
        reasons.append(f"SMALL float ({float_shares:,}) - Room to move")
    elif float_size == "LARGE":
        score -= 1
        reasons.append(f"LARGE float ({float_shares:,}) - Harder to move")
    elif float_size == "MEGA":
        score -= 2
        reasons.append(f"MEGA float ({float_shares:,}) - Moves slowly")
    
    # 2. Volume trend
    vol_change, vol_trend = check_volume_trend(ticker)
    if vol_trend == "SURGING":
        score += 2
        reasons.append(f"Volume SURGING (+{vol_change:.0f}%) - Strong interest")
    elif vol_trend == "RISING":
        score += 1
        reasons.append(f"Volume RISING (+{vol_change:.0f}%) - Building momentum")
    elif vol_trend == "FADING":
        score -= 1
        reasons.append(f"Volume FADING ({vol_change:.0f}%) - Losing interest")
    elif vol_trend == "COLLAPSING":
        score -= 2
        reasons.append(f"Volume COLLAPSING ({vol_change:.0f}%) - Interest dying")
    
    # 3. Price action
    price_pattern = check_price_action(ticker)
    if price_pattern == "ACCUMULATION":
        score += 2
        reasons.append("ACCUMULATION pattern - Building base")
    elif price_pattern == "BUILDING":
        score += 1
        reasons.append("BUILDING uptrend - Momentum forming")
    elif price_pattern == "PARABOLIC":
        score -= 2
        reasons.append("PARABOLIC move - Likely to fade")
    elif price_pattern == "SPIKE":
        score -= 1
        reasons.append("SPIKE pattern - Watch for fade")
    
    # 4. Catalyst presence
    has_catalyst, catalyst_info = has_recent_catalyst(ticker)
    if has_catalyst:
        score += 1
        reasons.append(f"Recent catalyst ({catalyst_info})")
    else:
        score -= 1
        reasons.append(f"No recent catalyst - Possible pump")
    
    # Cap score at 0-10
    score = max(0, min(10, score))
    
    # Classify
    if score >= 8:
        classification = "STRONG_LEGS"
    elif score >= 6:
        classification = "MODERATE_LEGS"
    elif score >= 4:
        classification = "WEAK_LEGS"
    else:
        classification = "FADING"
    
    return {
        'ticker': ticker,
        'score': score,
        'classification': classification,
        'reasons': reasons,
        'float': float_shares,
        'float_size': float_size,
        'volume_trend': vol_trend,
        'price_pattern': price_pattern,
        'has_catalyst': has_catalyst
    }


def print_classification(result):
    """Print formatted classification report"""
    
    emojis = {
        'STRONG_LEGS': '🚀',
        'MODERATE_LEGS': '📈',
        'WEAK_LEGS': '⚠️',
        'FADING': '📉'
    }
    
    emoji = emojis.get(result['classification'], '❓')
    
    print(f"\n{emoji} {result['ticker']} - {result['classification']} (Score: {result['score']}/10)")
    print("-" * 70)
    
    for reason in result['reasons']:
        print(f"  • {reason}")
    
    print()


def analyze_watchlist(watchlist_file='dynamic_watchlist.txt'):
    """
    Analyze all tickers from dynamic watchlist
    Return classification for each
    """
    
    print("🐺 LEGS CLASSIFIER - Analyzing Discovered Movers\n")
    
    # Read watchlist
    with open(watchlist_file, 'r') as f:
        tickers = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"📋 Analyzing {len(tickers)} tickers from {watchlist_file}...\n")
    
    results = []
    
    for ticker in tickers:
        try:
            result = classify_legs(ticker)
            results.append(result)
            print_classification(result)
            
            # Log strong legs to database
            if DB_AVAILABLE and result['score'] >= 7:
                log_alert('STRONG_LEGS', ticker,
                         f"Strong Legs: {ticker} (Score {result['score']}/10)",
                         result)
            
        except Exception as e:
            print(f"❌ Error analyzing {ticker}: {e}")
            continue
    
    # Summary
    print("\n" + "="*70)
    print("📊 CLASSIFICATION SUMMARY")
    print("="*70)
    
    strong = [r for r in results if r['classification'] == 'STRONG_LEGS']
    moderate = [r for r in results if r['classification'] == 'MODERATE_LEGS']
    weak = [r for r in results if r['classification'] == 'WEAK_LEGS']
    fading = [r for r in results if r['classification'] == 'FADING']
    
    print(f"\n🚀 STRONG LEGS ({len(strong)}):")
    for r in sorted(strong, key=lambda x: x['score'], reverse=True):
        print(f"   {r['ticker']:6s} - Score {r['score']}/10")
    
    print(f"\n📈 MODERATE LEGS ({len(moderate)}):")
    for r in sorted(moderate, key=lambda x: x['score'], reverse=True):
        print(f"   {r['ticker']:6s} - Score {r['score']}/10")
    
    print(f"\n⚠️  WEAK LEGS ({len(weak)}):")
    for r in sorted(weak, key=lambda x: x['score'], reverse=True):
        print(f"   {r['ticker']:6s} - Score {r['score']}/10")
    
    print(f"\n📉 FADING ({len(fading)}):")
    for r in sorted(fading, key=lambda x: x['score'], reverse=True):
        print(f"   {r['ticker']:6s} - Score {r['score']}/10")
    
    print("\n" + "="*70)
    
    return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Classify if movers have legs or are fading')
    parser.add_argument('ticker', nargs='?', help='Single ticker to analyze')
    parser.add_argument('--watchlist', default='dynamic_watchlist.txt', 
                       help='Watchlist file to analyze (default: dynamic_watchlist.txt)')
    
    args = parser.parse_args()
    
    if args.ticker:
        # Analyze single ticker
        result = classify_legs(args.ticker)
        print_classification(result)
    else:
        # Analyze entire watchlist
        analyze_watchlist(args.watchlist)


if __name__ == "__main__":
    main()
