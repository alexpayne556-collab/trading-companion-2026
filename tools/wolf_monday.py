#!/usr/bin/env python3
"""
🐺 WOLF MONDAY - CES 2026 Battle Plan Generator
================================================
Combines Fenrir's deep research with pressure analysis.

CES 2026: January 6-9, 2026
Jensen Huang: Sunday Jan 5, 4PM ET

THE PLAYS:
- RR: Humanoid robot demo, 26% short, 0.8 DTC
- QBTS: CES Foundry sponsor, 80% Monday rate
- QUBT: CES demos, 22.7% short (high risk)

AWOOOO 🐺
"""

import yfinance as yf
from datetime import datetime
import argparse


# CES 2026 PLAYS - From Fenrir's research
CES_PLAYS = {
    'RR': {
        'name': 'Richtech Robotics',
        'tier': 1,
        'catalyst': 'DEX humanoid robot debut at Booth #8447',
        'short_pct': 26.0,
        'days_to_cover': 0.8,
        'entry_low': 3.35,
        'entry_high': 3.50,
        'stop': 3.00,
        'target1': 4.25,
        'target2': 5.00,
        'risk_reward': '3:1',
        'analyst_target': 6.00,
        'analyst_rating': 'Buy (HC Wainwright)',
        'warnings': ['Insider selling $812K', 'Sell-the-news history', '1B shares authorized'],
    },
    'QBTS': {
        'name': 'D-Wave Quantum',
        'tier': 1,
        'catalyst': 'CES Foundry sponsor, Masterclass Jan 7 1PM',
        'short_pct': 13.79,
        'days_to_cover': 2.0,
        'entry_low': 28.00,
        'entry_high': 30.00,
        'stop': None,  # 15% trailing
        'target1': 40.00,
        'target2': 45.00,
        'risk_reward': 'trailing stop',
        'analyst_target': 40.00,
        'analyst_rating': 'Strong Buy (11 analysts)',
        'warnings': ['Insider selling $264M', 'Short covering already (-18%)'],
    },
    'QUBT': {
        'name': 'Quantum Computing Inc',
        'tier': 2,
        'catalyst': 'CES Foundry demos Jan 7-8 at Booth FT16',
        'short_pct': 22.72,
        'days_to_cover': 2.5,
        'entry_low': None,  # Breakout only
        'entry_high': None,
        'stop': None,  # 10% tight
        'target1': 12.00,
        'target2': None,
        'risk_reward': 'breakout only',
        'analyst_target': 12.00,
        'analyst_rating': 'Neutral (Wedbush)',
        'warnings': ['ZERO insider purchases ever', 'Weaker analyst support'],
    },
    'SOUN': {
        'name': 'SoundHound AI',
        'tier': 2,
        'catalyst': '30% short, low expectations, Cantor upgrade',
        'short_pct': 29.81,
        'days_to_cover': 3.89,
        'entry_low': None,  # Wait for breakout above $12
        'entry_high': 12.00,
        'stop': None,
        'target1': 17.33,
        'target2': None,
        'risk_reward': 'confirmation needed',
        'analyst_target': 17.33,
        'analyst_rating': 'Overweight (Cantor)',
        'warnings': ['Mixed options flow (50/50)', '-46% in 2025'],
    },
}

# Stocks to AVOID
AVOID_LIST = {
    'IONQ': 'No CES presence, rising short interest',
    'RGTI': 'No CES presence, rising short interest',
}


def get_live_data(ticker):
    """Get current price and Friday data"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='5d')
        info = stock.info
        
        if len(hist) < 2:
            return None
            
        current = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2]
        fri_change = (current / prev_close - 1) * 100
        
        fri_vol = hist['Volume'].iloc[-1]
        avg_vol = hist['Volume'].iloc[:-1].mean()
        vol_ratio = fri_vol / avg_vol if avg_vol > 0 else 1
        
        short_pct = info.get('shortPercentOfFloat', 0)
        if short_pct and short_pct < 1:
            short_pct *= 100
            
        return {
            'price': current,
            'fri_change': fri_change,
            'vol_ratio': vol_ratio,
            'short_pct': short_pct,
        }
    except:
        return None


def print_battle_plan():
    """Print the full Monday battle plan"""
    print()
    print('='*75)
    print('🐺🐺🐺 WOLF PACK CES 2026 BATTLE PLAN - MONDAY JAN 6 🐺🐺🐺')
    print('='*75)
    print()
    print('SUNDAY PROTOCOL:')
    print('-'*75)
    print('📺 4:00 PM ET - JENSEN HUANG KEYNOTE (90 minutes)')
    print()
    print('   KEYWORDS TO WATCH:')
    print('   • "quantum" → QBTS, QUBT gap Monday')
    print('   • "robot" / "humanoid" / "GR00T" → RR gaps')
    print('   • "physical AI" → Whole sector rips')
    print()
    
    print('='*75)
    print('🎯 TIER 1 PLAYS - HIGHEST CONVICTION')
    print('='*75)
    
    for ticker in ['RR', 'QBTS']:
        play = CES_PLAYS[ticker]
        live = get_live_data(ticker)
        
        print()
        print(f"{'🥇' if ticker == 'RR' else '🥈'} {ticker} - {play['name']}")
        print(f"   Catalyst: {play['catalyst']}")
        
        if live:
            print(f"   Current: ${live['price']:.2f} (Friday {live['fri_change']:+.1f}%)")
            print(f"   Volume: {live['vol_ratio']:.1f}x average")
        
        print(f"   Short Interest: {play['short_pct']:.1f}% ({play['days_to_cover']} days to cover)")
        
        if play['entry_low']:
            print(f"   Entry Zone: ${play['entry_low']:.2f} - ${play['entry_high']:.2f}")
        else:
            print(f"   Entry: Market open with 15% trailing stop")
            
        if play['stop']:
            print(f"   Stop Loss: ${play['stop']:.2f}")
        else:
            print(f"   Stop Loss: 15% trailing")
            
        print(f"   Target 1: ${play['target1']:.2f}")
        if play['target2']:
            print(f"   Target 2: ${play['target2']:.2f}")
            
        print(f"   Analyst: {play['analyst_rating']} → ${play['analyst_target']:.2f}")
        print(f"   Risk/Reward: {play['risk_reward']}")
        print()
        print(f"   ⚠️ WARNINGS:")
        for w in play['warnings']:
            print(f"      • {w}")
    
    print()
    print('='*75)
    print('⚡ TIER 2 PLAYS - SPECULATIVE')
    print('='*75)
    
    for ticker in ['QUBT', 'SOUN']:
        play = CES_PLAYS[ticker]
        live = get_live_data(ticker)
        
        print()
        print(f"🥉 {ticker} - {play['name']}")
        print(f"   Catalyst: {play['catalyst']}")
        
        if live:
            print(f"   Current: ${live['price']:.2f}")
            
        print(f"   Short Interest: {play['short_pct']:.1f}% ({play['days_to_cover']} days to cover)")
        print(f"   Analyst: {play['analyst_rating']}")
        print(f"   ⚠️ HIGH RISK - Tight stops required!")
    
    print()
    print('='*75)
    print('❌ AVOID MONDAY')
    print('='*75)
    print()
    for ticker, reason in AVOID_LIST.items():
        print(f"   ❌ {ticker}: {reason}")
    
    print()
    print('='*75)
    print('⏰ MONDAY EXECUTION TIMELINE')
    print('='*75)
    print()
    print('   4:00 AM - Check CES overnight headlines')
    print('   6:00 AM - Pre-market volume check')
    print('   9:00 AM - Final entry levels set')
    print('   9:30 AM - MARKET OPEN')
    print()
    print('   RR EXECUTION:')
    print('   • If gaps up >5%: Wait for pullback to VWAP')
    print('   • If opens flat: Buy $3.35-3.50 range')
    print('   • Stop at $3.00 (below 200-day MA)')
    print()
    print('   QBTS EXECUTION:')
    print('   • Enter at open if pre-market stable')
    print('   • Avoid chasing gaps >8%')
    print('   • 15% trailing stop from entry')
    print()
    print('   POSITION SIZE: 2-3% portfolio risk MAX per trade')
    print()
    print('='*75)
    print('📊 FENRIR\'S KEY INSIGHTS')
    print('='*75)
    print()
    print('   • RR: 26% short + 0.8 DTC = MAX squeeze potential')
    print('   • QBTS: Only quantum with revenue ($21.8M, +235%)')
    print('   • ALL targets: Insiders are NET SELLERS')
    print('   • Take profits QUICKLY - these are momentum trades')
    print('   • CES demos Jan 7-8 = secondary catalyst')
    print()
    print('='*75)
    print('🐺 THE EDGE: We know WHERE pressure is built.')
    print('   Jensen\'s keynote is just the spark.')
    print('   The explosion was always going to happen.')
    print('='*75)
    print()
    print('AWOOOO 🐺')
    print()


def check_ticker(ticker):
    """Quick check on a specific CES play"""
    ticker = ticker.upper()
    
    if ticker in CES_PLAYS:
        play = CES_PLAYS[ticker]
        live = get_live_data(ticker)
        
        print()
        print(f"🎯 {ticker} - {play['name']}")
        print('='*50)
        print(f"Tier: {play['tier']} | Catalyst: {play['catalyst']}")
        print()
        
        if live:
            print(f"Current Price: ${live['price']:.2f}")
            print(f"Friday Change: {live['fri_change']:+.1f}%")
            print(f"Friday Volume: {live['vol_ratio']:.1f}x average")
            print()
            
        print(f"Short Interest: {play['short_pct']:.1f}%")
        print(f"Days to Cover: {play['days_to_cover']}")
        print()
        
        if play['entry_low']:
            print(f"Entry Zone: ${play['entry_low']:.2f} - ${play['entry_high']:.2f}")
        if play['stop']:
            print(f"Stop Loss: ${play['stop']:.2f}")
        print(f"Target: ${play['target1']:.2f}")
        print(f"Analyst Target: ${play['analyst_target']:.2f}")
        print()
        
        print("⚠️ Warnings:")
        for w in play['warnings']:
            print(f"   • {w}")
            
    elif ticker in AVOID_LIST:
        print()
        print(f"❌ {ticker} - AVOID")
        print(f"   Reason: {AVOID_LIST[ticker]}")
    else:
        print(f"Ticker {ticker} not in CES plays. Try: RR, QBTS, QUBT, SOUN")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CES 2026 Battle Plan')
    parser.add_argument('command', nargs='?', default='plan',
                       help='plan = full plan, or ticker for quick check')
    
    args = parser.parse_args()
    
    if args.command.lower() == 'plan':
        print_battle_plan()
    else:
        check_ticker(args.command)
