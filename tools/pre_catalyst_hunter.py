#!/usr/bin/env python3
"""
🐺 PRE-CATALYST HUNTER
Find plays 1-3 days BEFORE they run - position before the wave forms

Tyr's strategy: "Let the wave pick us up, not we catch it"

This tool finds:
1. Upcoming catalysts (CES, earnings, FDA, contracts)
2. Current unusual activity (options flow, insider buying, 8-K filings)
3. Stocks with BOTH = high-conviction early positioning

The goal: Buy BEFORE the herd arrives, sell into THEIR buying.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import argparse
import json
from pathlib import Path
import requests

def get_upcoming_catalysts(days_ahead=7):
    """
    Find catalysts happening in next 1-7 days
    
    Returns:
        dict: {ticker: catalyst_info}
    """
    print(f"\n🔍 HUNTING CATALYSTS {days_ahead} DAYS AHEAD")
    print("=" * 60)
    
    catalysts = {}
    
    # CES 2026: Jan 6-9 (this week)
    ces_dates = {
        'QBTS': {'event': 'CES Quantum Demo', 'date': '2026-01-07', 'time': '1:00 PM PT', 'days_away': 1},
        'RGTI': {'event': 'CES Quantum Tech', 'date': '2026-01-08', 'time': 'TBD', 'days_away': 2},
        'LUNR': {'event': 'CES Lunar Demo', 'date': '2026-01-08', 'time': 'TBD', 'days_away': 2},
    }
    
    # Known upcoming events (manually curated - Fenrir's job to update)
    upcoming = {
        # Add more as Fenrir finds them
    }
    
    catalysts.update(ces_dates)
    catalysts.update(upcoming)
    
    # Filter to days_ahead window
    today = datetime.now().date()
    filtered = {}
    
    for ticker, info in catalysts.items():
        try:
            event_date = datetime.strptime(info['date'], '%Y-%m-%d').date()
            days_until = (event_date - today).days
            
            if 1 <= days_until <= days_ahead:
                info['days_until'] = days_until
                filtered[ticker] = info
        except:
            continue
    
    return filtered

def check_unusual_activity(ticker):
    """
    Check if ticker has unusual activity (pre-run signals)
    
    Returns:
        dict: {
            'options_signal': bool,
            'volume_signal': bool,
            'price_signal': bool,
            'strength_score': 0-10
        }
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get recent data
        hist = stock.history(period='5d', interval='1d')
        
        if len(hist) < 2:
            return None
        
        # Volume analysis
        avg_volume = hist['Volume'].mean()
        recent_volume = hist['Volume'].iloc[-1]
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 0
        volume_signal = volume_ratio > 1.5  # 50% above average
        
        # Price momentum (quiet accumulation)
        price_change_5d = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100)
        
        # We want EARLY plays: slight up (1-5%) or flat, NOT already run 10%+
        price_signal = -2 < price_change_5d < 8  # Not dumping, not already ran
        
        # Options (if available)
        options_signal = False
        try:
            options = stock.options
            if options:
                # Has options = more liquid, better for small accounts
                options_signal = True
        except:
            pass
        
        # Strength score (0-10)
        score = 0
        if volume_signal:
            score += 3
        if price_signal:
            score += 3
        if options_signal:
            score += 2
        if volume_ratio > 2.0:  # 2x volume
            score += 1
        if 2 < price_change_5d < 5:  # Sweet spot: quiet accumulation
            score += 1
        
        return {
            'volume_ratio': round(volume_ratio, 2),
            'volume_signal': volume_signal,
            'price_change_5d': round(price_change_5d, 2),
            'price_signal': price_signal,
            'options_available': options_signal,
            'strength_score': min(score, 10),
            'current_price': round(hist['Close'].iloc[-1], 2)
        }
        
    except Exception as e:
        print(f"   ⚠️ Error checking {ticker}: {e}")
        return None

def find_pre_catalyst_plays(days_ahead=7, min_score=5):
    """
    Find plays with upcoming catalyst + current unusual activity
    
    Args:
        days_ahead: How many days to look ahead for catalysts
        min_score: Minimum strength score (0-10)
    
    Returns:
        list: [{ticker, catalyst, activity, conviction}]
    """
    print(f"\n🐺 PRE-CATALYST HUNTER")
    print(f"   Looking for plays {days_ahead} days ahead")
    print(f"   Minimum strength score: {min_score}/10")
    print("=" * 60)
    
    # Get upcoming catalysts
    catalysts = get_upcoming_catalysts(days_ahead)
    
    if not catalysts:
        print("   ⚠️ No catalysts found in next 7 days")
        print("   💡 Fenrir needs to update catalyst calendar")
        return []
    
    print(f"\n📅 FOUND {len(catalysts)} UPCOMING CATALYSTS:")
    for ticker, info in catalysts.items():
        print(f"   {ticker}: {info['event']} on {info['date']} ({info['days_until']} days)")
    
    # Check each ticker for unusual activity
    print(f"\n🔍 CHECKING FOR UNUSUAL ACTIVITY:")
    
    plays = []
    
    for ticker, catalyst_info in catalysts.items():
        print(f"\n   Analyzing {ticker}...")
        
        activity = check_unusual_activity(ticker)
        
        if not activity:
            print(f"      ❌ No data available")
            continue
        
        score = activity['strength_score']
        print(f"      Strength Score: {score}/10")
        print(f"      Volume Ratio: {activity['volume_ratio']}x")
        print(f"      5-Day Change: {activity['price_change_5d']:+.2f}%")
        print(f"      Current Price: ${activity['current_price']}")
        
        # Determine conviction
        if score >= 7:
            conviction = "HIGH"
        elif score >= 5:
            conviction = "MEDIUM"
        else:
            conviction = "LOW"
        
        if score >= min_score:
            plays.append({
                'ticker': ticker,
                'conviction': conviction,
                'catalyst': catalyst_info,
                'activity': activity,
                'days_until_catalyst': catalyst_info['days_until']
            })
            print(f"      ✅ CONVICTION: {conviction}")
        else:
            print(f"      ⚠️ Score too low ({score} < {min_score})")
    
    return plays

def display_results(plays):
    """Display pre-catalyst plays in actionable format"""
    
    if not plays:
        print(f"\n❌ NO HIGH-CONVICTION PRE-CATALYST PLAYS FOUND")
        print(f"\n💡 THIS MEANS:")
        print(f"   • Either nothing good happening next week")
        print(f"   • OR smart money hasn't positioned yet")
        print(f"   • OR Fenrir needs to update catalyst calendar")
        return
    
    print(f"\n🎯 PRE-CATALYST PLAYS (BEFORE THE RUN)")
    print("=" * 60)
    
    # Sort by conviction and days until
    plays_sorted = sorted(plays, key=lambda x: (
        {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}[x['conviction']],
        -x['days_until_catalyst']  # Negative so earlier dates sort higher
    ), reverse=True)
    
    for i, play in enumerate(plays_sorted, 1):
        ticker = play['ticker']
        conviction = play['conviction']
        catalyst = play['catalyst']
        activity = play['activity']
        days_until = play['days_until_catalyst']
        
        print(f"\n#{i} {ticker} - {conviction} CONVICTION")
        print(f"   Current Price: ${activity['current_price']}")
        print(f"   Catalyst: {catalyst['event']}")
        print(f"   Date: {catalyst['date']} ({days_until} days away)")
        print(f"   Strength Score: {activity['strength_score']}/10")
        print(f"   5-Day Move: {activity['price_change_5d']:+.2f}% (not pumped yet)")
        print(f"   Volume: {activity['volume_ratio']}x average")
        
        # Strategy
        if days_until >= 2:
            timing = "Buy TODAY or tomorrow (2+ days early)"
        elif days_until == 1:
            timing = "Buy TODAY (1 day early - still early enough)"
        else:
            timing = "SKIP - catalyst too soon (day of)"
        
        print(f"   🐺 Strategy: {timing}")
        
        # Risk/Reward
        if conviction == "HIGH":
            target_pct = 20
            risk_pct = 7
        elif conviction == "MEDIUM":
            target_pct = 15
            risk_pct = 8
        else:
            target_pct = 10
            risk_pct = 10
        
        target_price = activity['current_price'] * (1 + target_pct/100)
        stop_price = activity['current_price'] * (1 - risk_pct/100)
        
        print(f"   Target: ${target_price:.2f} (+{target_pct}%)")
        print(f"   Stop: ${stop_price:.2f} (-{risk_pct}%)")
        print(f"   Risk/Reward: 1:{target_pct/risk_pct:.1f}")
    
    # Final recommendation
    print(f"\n🐺 WOLF'S RECOMMENDATION:")
    
    high_conviction = [p for p in plays_sorted if p['conviction'] == 'HIGH']
    
    if high_conviction:
        top_play = high_conviction[0]
        print(f"   TOP PLAY: {top_play['ticker']}")
        print(f"   Why: {top_play['catalyst']['event']} in {top_play['days_until_catalyst']} days")
        print(f"   Current: ${top_play['activity']['current_price']}")
        print(f"   Position: Buy $150-200 TODAY (before herd arrives)")
        print(f"   Exit: Sell into strength when catalyst hits")
    else:
        medium_conviction = [p for p in plays_sorted if p['conviction'] == 'MEDIUM']
        if medium_conviction:
            print(f"   Consider: {medium_conviction[0]['ticker']} (medium conviction)")
            print(f"   Or WAIT for tonight's scanners to find better plays")
        else:
            print(f"   WAIT - No high-conviction early plays right now")
            print(f"   Run scanners tonight to find next week's opportunities")

def main():
    parser = argparse.ArgumentParser(description='🐺 Pre-Catalyst Hunter - Position before the wave')
    parser.add_argument('--days', type=int, default=7, help='Days ahead to search for catalysts')
    parser.add_argument('--min-score', type=int, default=5, help='Minimum strength score (0-10)')
    
    args = parser.parse_args()
    
    print(f"\n🐺 PRE-CATALYST HUNTER")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Strategy: Position BEFORE the wave")
    print("=" * 60)
    
    # Find plays
    plays = find_pre_catalyst_plays(args.days, args.min_score)
    
    # Display
    display_results(plays)
    
    # Save
    if plays:
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        output_file = log_dir / f'pre_catalyst_plays_{timestamp}.json'
        
        with open(output_file, 'w') as f:
            json.dump(plays, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
    
    print(f"\n🐺 POSITION BEFORE CHAOS. SELL INTO STRENGTH.")
    print(f"   AWOOOO!\n")

if __name__ == '__main__':
    main()
