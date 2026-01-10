#!/usr/bin/env python3
"""
🐺 MORNING PREP - 9 AM EXECUTION SCRIPT
========================================

Run this at 9:00 AM to prepare for market open.
Gets you ALL the data you need in 2 minutes.

Usage: python morning_prep.py
"""

import yfinance as yf
from datetime import datetime
import sys

print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║             🐺 WOLF PACK WAR ROOM - MORNING PREP 🐺          ║
║                                                              ║
║                  January 7, 2026 - CES DAY                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

print(f"⏰ Current Time: {datetime.now().strftime('%H:%M:%S')}")
print(f"🎯 Target: 5-6% portfolio gain today")
print(f"💰 Cash Available: $863 ($363 RH + $500 Fidelity)")

print("\n" + "="*70)
print("STEP 1: MARKET CHECK")
print("="*70)

try:
    # Check SPY/QQQ
    spy = yf.Ticker("SPY")
    spy_data = spy.history(period='1d', interval='1m')
    
    if len(spy_data) > 0:
        spy_price = spy_data['Close'].iloc[-1]
        spy_open = spy_data['Open'].iloc[0]
        spy_change = ((spy_price - spy_open) / spy_open) * 100
        
        if spy_change > 0:
            market_signal = "🟢 GREEN"
        elif spy_change < -0.5:
            market_signal = "🔴 RED"
        else:
            market_signal = "⚪ FLAT"
        
        print(f"\nSPY: ${spy_price:.2f} ({spy_change:+.2f}%) {market_signal}")
        
        if spy_change < -1:
            print("⚠️  WARNING: Market is down. Consider smaller position sizes.")
        elif spy_change > 1:
            print("✅ Market is strong. Good day for entries.")
    else:
        print("\n⏰ Pre-market - Waiting for 9:30 AM open")
        print("   Run this again at 9:30 to see market direction")

except Exception as e:
    print(f"\n⏰ Pre-market mode (market data after 9:30 AM)")

print("\n" + "="*70)
print("STEP 2: PRIMARY TARGETS - LIVE PRICES")
print("="*70)

targets = {
    'LUNR': {'conviction': 'HIGHEST', 'entry': '$16-17', 'size': '$400-500'},
    'QUBT': {'conviction': 'SWING', 'entry': 'Market', 'size': '$200-300'},
    'RDW': {'conviction': 'SWING', 'entry': 'Market', 'size': '$200-300'},
    'ASTS': {'conviction': 'BONUS', 'entry': 'Check price', 'size': '$100-200'},
}

print(f"\n{'Ticker':<8} {'Price':<10} {'PreMkt Chg':<12} {'Entry':<12} {'Size':<12} {'Action'}")
print("-" * 70)

for ticker, info in targets.items():
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='2d')
        
        if len(hist) >= 2:
            current = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            change_pct = ((current - prev_close) / prev_close) * 100
            
            if ticker == 'LUNR':
                if current < 16.5:
                    action = "🟢 BUY AT OPEN"
                elif current < 17.5:
                    action = "⏰ WAIT FOR 10AM DIP"
                else:
                    action = "⚠️  TOO HIGH - WAIT"
            elif ticker in ['QUBT', 'RDW']:
                if change_pct > 5:
                    action = "⚠️  ALREADY RAN - CAUTION"
                else:
                    action = "✅ WATCH FOR 2PM"
            else:  # ASTS
                action = "👀 MONITOR"
            
            print(f"{ticker:<8} ${current:>7.2f} {change_pct:>+9.2f}%  {info['entry']:<12} {info['size']:<12} {action}")
        else:
            print(f"{ticker:<8} {'N/A':<10} {'N/A':<12} {info['entry']:<12} {info['size']:<12} Waiting for data...")
    
    except Exception as e:
        print(f"{ticker:<8} ERROR     N/A          {info['entry']:<12} {info['size']:<12} Check manually")

print("\n" + "="*70)
print("STEP 3: 10 AM DIP WINDOW - LUNR ENTRY PLAN")
print("="*70)

print("""
⏰ 9:55 AM - Get Ready
   • Open Fidelity Active Trader Plus
   • Set limit order on LUNR: $16.50 (or 3% below current if higher)
   • Position size: $400-500
   • Set alert at $17.50

⏰ 10:00 AM - EXECUTE
   • Watch for dip (98% probability based on ML model)
   • If drops to $16-17 range → ENTER
   • If stays above $17.50 → WAIT

⏰ 10:15 AM - Confirm
   • Check if order filled
   • Set mental stop: -7% below entry
   • Target: +5-7% or hold for Jan 15

💡 IF LUNR GAPS UP ABOVE $18:
   → WAIT for pullback
   → Don't chase
   → IM-2 catalyst is Jan 15, you have time
""")

print("="*70)
print("STEP 4: CES PRESENTATIONS - 2 PM")
print("="*70)

print("""
📅 2:00 PM ET - QUBT Photonics Presentation
📅 2:00 PM ET - RDW Lunar Manufacturing Demo
📅 TBA - IONQ Quantum Demo

STRATEGY:
  If stocks RAN before 2 PM:
    → Take profits (3-5%)
    → "Buy rumor, sell news"
  
  If stocks FLAT before 2 PM:
    → Watch first 5 min of presentation
    → Enter on breakout if good reaction
    → SMALL size ($200)

  DO NOT:
    ❌ Hold through if already up 5%+
    ❌ FOMO into vertical moves
    ❌ Go all-in on news
""")

print("="*70)
print("STEP 5: POSITION SIZING CONFIRMATION")
print("="*70)

print("""
Total Cash: $863

RECOMMENDED ALLOCATION:
  🎯 $400-500 → LUNR (10 AM dip)
  🎲 $200-300 → CES swing (QUBT or RDW)
  💵 $100-200 → Reserve (ASTS or backup)

CONSERVATIVE ALLOCATION:
  🎯 $300 → LUNR (smaller size first)
  💵 $560 → Cash (add to LUNR if it works)

YOUR DECISION: ___________________
""")

print("="*70)
print("STEP 6: RISK MANAGEMENT REMINDERS")
print("="*70)

print("""
✅ FOLLOW THE STOPS:
   • LUNR: -7% max loss
   • CES swings: -5% max loss
   • If SPY dumps 2%: Close all positions

✅ TAKE PROFITS:
   • LUNR: +5% = sell half, let rest ride
   • CES: +3-5% = close same day
   • Don't be greedy on news plays

✅ DON'T FORCE IT:
   • If setups aren't clean, WAIT
   • If you miss entries, there's Jan 15
   • Protect capital > Make money today
""")

print("\n" + "="*70)
print("FINAL CHECKLIST")
print("="*70)

checklist = [
    ("Market direction checked (SPY/QQQ)", False),
    ("LUNR pre-market price noted", False),
    ("Fidelity Active Trader Plus ready", False),
    ("LUNR alerts set ($17.50, $16.50, $16.00)", False),
    ("Position sizes decided", False),
    ("Risk stops memorized (-7% LUNR, -5% CES)", False),
    ("CES presentation times noted (2 PM)", False),
    ("Phone charged for alerts", False),
]

for item, _ in checklist:
    print(f"  [ ] {item}")

print(f"\n\n{'='*70}")
print("🎯 THE ONE-SENTENCE PLAN")
print("="*70)
print("""
Enter LUNR at 10 AM dip ($16-17), $400-500 position,
hold for IM-2, swing CES if clean setups appear.
""")

print("="*70)
print("⚡ QUICK REFERENCE")
print("="*70)
print("""
9:30 AM  - Market opens, WATCH
10:00 AM - LUNR DIP ENTRY (primary target)
12:00 PM - Mid-day review
2:00 PM  - CES presentations (QUBT, RDW)
3:50 PM  - Close or hold decision
""")

print("\n" + "="*70)
print("🐺 GOOD HUNTING, TYR")
print("="*70)
print("""
You built the tools.
You found the setup.
You detected the convergence.
Now execute with discipline.

The pack hunts at dawn.
AWOOOO! 🐺
""")

print(f"\nTime now: {datetime.now().strftime('%H:%M:%S')}")
print("Next: Run this again at 9:30 AM for live data\n")
