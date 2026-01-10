#!/usr/bin/env python3
"""
🐺 LIVE ACTION PLAN
====================

Gets real-time prices and tells you EXACTLY what to do.
Run at: 9:00 AM, 9:30 AM, 10:00 AM tomorrow
"""

import yfinance as yf
from datetime import datetime

print("""
╔══════════════════════════════════════════════════════════════╗
║         🐺 LIVE DATA + ACTIONS - WHAT TO DO NOW 🐺           ║
╚══════════════════════════════════════════════════════════════╝
""")

current_time = datetime.now()
print(f"⏰ {current_time.strftime('%I:%M %p')} - January 7, 2026\n")

# Get live data
print("📊 GETTING LIVE PRICES...\n")

tickers = {
    'LUNR': 'PRIMARY TARGET',
    'QUBT': 'CES 2PM',
    'RDW': 'CES 2PM',
    'ASTS': 'BONUS',
    'SPY': 'MARKET'
}

data = {}
for ticker, label in tickers.items():
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='2d', interval='1m')
        if len(hist) >= 2:
            current = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            change = ((current - prev_close) / prev_close) * 100
            data[ticker] = {
                'price': current,
                'change': change,
                'label': label
            }
        else:
            # Pre-market or no data yet
            hist = stock.history(period='5d')
            if len(hist) >= 1:
                current = hist['Close'].iloc[-1]
                data[ticker] = {
                    'price': current,
                    'change': 0,
                    'label': label
                }
    except Exception as e:
        print(f"⚠️  {ticker}: Can't get data (market not open yet?)")
        data[ticker] = {'price': 0, 'change': 0, 'label': label}

# Display live prices
print("="*70)
print("💰 LIVE PRICES")
print("="*70)
for ticker, info in data.items():
    if info['price'] > 0:
        change_icon = "🟢" if info['change'] >= 0 else "🔴"
        print(f"{ticker:<6} ${info['price']:>8.2f}  {info['change']:>+6.2f}%  {change_icon}  {info['label']}")
    else:
        print(f"{ticker:<6} Waiting for market data...")

print("\n" + "="*70)
print("🎯 ACTIONS BY ACCOUNT")
print("="*70)

lunr = data.get('LUNR', {}).get('price', 18.36)
spy_change = data.get('SPY', {}).get('change', 0)

# Check market condition
market_ok = spy_change > -1.0  # Market not dumping

print(f"\n📱 ROBINHOOD ACCOUNT ($363 cash)")
print("-" * 70)

if lunr < 17.0 and market_ok:
    print(f"✅ DO THIS:")
    print(f"   1. Buy LUNR at market")
    print(f"   2. Shares: {int(300/lunr)} shares (~$300)")
    print(f"   3. Set stop loss: ${lunr * 0.93:.2f} (-7%)")
    print(f"   4. Keep $63 cash as buffer")
elif lunr >= 17.0 and lunr < 18.0 and market_ok:
    print(f"⏰ DO THIS:")
    print(f"   1. Set limit order: $17.00")
    print(f"   2. Shares: {int(300/17)} shares (~$300)")
    print(f"   3. Good for day order")
    print(f"   4. If not filled by 10:30 AM → cancel and reassess")
elif lunr >= 18.0 or not market_ok:
    print(f"🛑 DO THIS:")
    print(f"   1. DO NOT buy LUNR today (too high or market bad)")
    print(f"   2. Keep $363 cash")
    print(f"   3. Wait for pullback later this week")
    print(f"   4. IM-2 catalyst is Jan 15 - you have time")

print(f"\n💼 FIDELITY ACCOUNT ($500 cash)")
print("-" * 70)

if lunr < 17.0 and market_ok:
    print(f"✅ DO THIS:")
    print(f"   1. Buy LUNR at market")
    print(f"   2. Shares: {int(400/lunr)} shares (~$400)")
    print(f"   3. Set stop loss: ${lunr * 0.93:.2f} (-7%)")
    print(f"   4. Keep $100 cash for CES trades")
elif lunr >= 17.0 and lunr < 18.0 and market_ok:
    print(f"⏰ DO THIS:")
    print(f"   1. Set limit order: $17.00")
    print(f"   2. Shares: {int(400/17)} shares (~$400)")
    print(f"   3. If filled before 10:30 AM → good")
    print(f"   4. If not filled → keep cash, maybe CES swing $200")
elif lunr >= 18.0 or not market_ok:
    print(f"🛑 DO THIS:")
    print(f"   1. DO NOT buy LUNR (too high or market bad)")
    print(f"   2. Option: CES swing trade $200-300")
    print(f"   3. Keep rest in cash")
    print(f"   4. Wait for better LUNR entry")

print("\n" + "="*70)
print("🎲 CES SWING TRADES (2 PM Presentations)")
print("="*70)

qubt = data.get('QUBT', {}).get('price', 11.96)
rdw = data.get('RDW', {}).get('price', 10.26)
qubt_change = data.get('QUBT', {}).get('change', 0)
rdw_change = data.get('RDW', {}).get('change', 0)

print(f"\nQUBT: ${qubt:.2f} ({qubt_change:+.2f}%)")
print(f"RDW:  ${rdw:.2f} ({rdw_change:+.2f}%)")

if qubt_change > 8 or rdw_change > 8:
    print(f"\n⚠️  ALREADY RAN OVERNIGHT:")
    print(f"   1. These jumped on CES hype")
    print(f"   2. If you trade: MAX $100-200")
    print(f"   3. Exit BEFORE 2 PM presentations")
    print(f"   4. High risk of 'sell the news'")
else:
    print(f"\n✅ CLEAN ENTRY:")
    print(f"   1. Can swing trade $200-300")
    print(f"   2. Pick one: QUBT or RDW (don't do both)")
    print(f"   3. Enter at market open")
    print(f"   4. Exit at +3-5% or before 2 PM")

print("\n" + "="*70)
print("⏰ TIME-BASED ACTIONS")
print("="*70)

hour = current_time.hour

if hour < 9 or (hour == 9 and current_time.minute < 30):
    print(f"\n🌅 PRE-MARKET (Before 9:30 AM):")
    print(f"   ✅ Open Fidelity Active Trader Plus")
    print(f"   ✅ Check LUNR pre-market price")
    print(f"   ✅ Set alerts: $17.50, $17.00, $16.50")
    print(f"   ✅ Read any overnight LUNR news")
    print(f"   ✅ Run this script again at 9:30 AM")

elif hour == 9 or (hour == 10 and current_time.minute < 15):
    print(f"\n🔔 MARKET OPEN (9:30-10:15 AM):")
    if lunr < 17.0:
        print(f"   ✅ BUY LUNR NOW at ${lunr:.2f}")
        print(f"   ✅ Robinhood: ~$300")
        print(f"   ✅ Fidelity: ~$400")
        print(f"   ✅ Total position: ~$700")
    elif lunr < 18.0:
        print(f"   ⏰ WAIT for 10 AM dip to $17")
        print(f"   ⏰ Set limit order at $17.00")
        print(f"   ⏰ Run this script again at 10:00 AM")
    else:
        print(f"   🛑 SKIP LUNR today")
        print(f"   🛑 Focus on CES swings instead")

elif hour >= 10 and hour < 14:
    print(f"\n📊 MID-DAY (10:15 AM - 2:00 PM):")
    print(f"   ✅ Check if LUNR filled")
    print(f"   ✅ If in profit: Move stop to breakeven")
    print(f"   ✅ Prepare for CES at 2 PM")
    print(f"   ✅ If in CES swings: Plan exit strategy")

elif hour >= 14 and hour < 16:
    print(f"\n🎤 CES PRESENTATIONS (2:00-4:00 PM):")
    print(f"   ✅ Exit CES swings at +3-5%")
    print(f"   ✅ Or exit before presentations start")
    print(f"   ✅ LUNR: Hold if green")
    print(f"   ✅ Lock in any profits by 3:50 PM")

else:
    print(f"\n💤 AFTER HOURS:")
    print(f"   ✅ Review today's trades")
    print(f"   ✅ Plan for tomorrow")
    print(f"   ✅ Check IM-2 catalyst timeline")

print("\n" + "="*70)
print("📝 QUICK SUMMARY")
print("="*70)

print(f"""
LUNR @ ${lunr:.2f}:
  • If <$17: BUY $700 total (RH $300 + Fidelity $400)
  • If $17-18: LIMIT ORDER $17, wait for dip
  • If >$18: SKIP today, wait for pullback

CES SWINGS:
  • Already ran? Small size $100-200 max
  • Clean entry? $200-300 one ticker
  • Exit before 2 PM or at +3-5%

TOTAL RISK:
  • Max loss if wrong: $50-70 (~5-6% of portfolio)
  • Max gain if right: $70-100 (7-8% of portfolio)
  • Stop losses: -7% LUNR, -5% CES

DISCIPLINE:
  • Don't chase if price runs
  • Take profits at targets
  • IM-2 is Jan 15 - you have time
""")

print("="*70)
print("🐺 EXECUTE THE PLAN")
print("="*70)
print("""
Trust the system.
Trust the data.
Trust yourself.

AWOOOO! 🐺
""")

print(f"Current time: {current_time.strftime('%I:%M %p')}")
print("Run this script at 9:30 AM and 10:00 AM for updates.\n")
