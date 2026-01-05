#!/usr/bin/env python3
"""
🐺 MONDAY BATTLE STATION
========================
EVERYTHING YOU NEED FOR MONDAY IN ONE DASHBOARD

Run this Monday morning and it gives you:
1. Pre-market gaps on your watchlist
2. Sector heat check
3. Position sizing calculator
4. Entry/Stop/Target levels
5. News headlines
6. Decision framework

Usage:
    python monday_battle_station.py           # Full dashboard
    python monday_battle_station.py --live    # Auto-refresh mode
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time
import argparse
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION - YOUR WATCHLIST
# ============================================================

ACCOUNT_SIZE = 10650  # Your account size
RISK_PER_TRADE = 0.02  # 2% risk per trade
MAX_POSITIONS = 5     # Maximum concurrent positions

# Priority watchlist - your top picks
PRIORITY_WATCHLIST = [
    'UUUU', 'RDW', 'LUNR', 'SIDU', 'SMR',  # Top momentum plays
    'CCJ', 'DNN', 'NXE', 'RKLB', 'ASTS'    # Secondary
]

# Full universe by sector
SECTORS = {
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'BKSY', 'ASTS', 'SPIR', 'PL', 'SIDU'],
    'NUCLEAR': ['LEU', 'CCJ', 'UUUU', 'UEC', 'SMR', 'OKLO', 'DNN', 'NXE', 'NNE'],
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ', 'LAES'],
    'AI_INFRA': ['CORZ', 'VRT', 'SOUN', 'PATH', 'UPST', 'AI', 'IREN'],
    'MEMORY': ['MU', 'WDC', 'SMCI', 'ANET', 'CRDO', 'COHR'],
    'CRYPTO': ['MARA', 'RIOT', 'CLSK', 'HUT', 'BITF'],
}

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_eastern_time():
    eastern = pytz.timezone('US/Eastern')
    return datetime.now(eastern)

def clear_screen():
    print("\033[2J\033[H", end="")

def print_header(title):
    print("\n" + "=" * 70)
    print(f"🐺 {title}")
    print("=" * 70)

# ============================================================
# DATA FETCHING
# ============================================================

def get_stock_data(ticker):
    """Get comprehensive data for a single ticker"""
    try:
        stock = yf.Ticker(ticker)
        
        # Historical data
        hist = stock.history(period='1mo', prepost=False)
        hist_prepost = stock.history(period='2d', prepost=True, interval='1m')
        
        if len(hist) < 5:
            return None
        
        # Current/last prices
        reg_close = hist['Close'].iloc[-1]
        
        # Pre-market/after-hours price if available
        if len(hist_prepost) > 0:
            current_price = hist_prepost['Close'].iloc[-1]
        else:
            current_price = reg_close
        
        # Calculate metrics
        high_20 = hist.tail(20)['High'].max() if len(hist) >= 20 else hist['High'].max()
        low_20 = hist.tail(20)['Low'].min() if len(hist) >= 20 else hist['Low'].min()
        
        # 5-day change
        if len(hist) >= 5:
            price_5d = hist.iloc[-5]['Close']
            change_5d = ((reg_close - price_5d) / price_5d) * 100
        else:
            change_5d = 0
        
        # Friday change
        if len(hist) >= 2:
            prev_close = hist.iloc[-2]['Close']
            friday_change = ((reg_close - prev_close) / prev_close) * 100
        else:
            friday_change = 0
        
        # Gap from after hours
        gap_pct = ((current_price - reg_close) / reg_close) * 100
        
        # Average volume
        avg_vol = hist['Volume'].tail(20).mean()
        friday_vol = hist['Volume'].iloc[-1]
        vol_ratio = friday_vol / avg_vol if avg_vol > 0 else 1
        
        # Distance from 20-day high/low
        pct_from_high = ((reg_close - high_20) / high_20) * 100
        pct_from_low = ((reg_close - low_20) / low_20) * 100
        
        return {
            'ticker': ticker,
            'price': current_price,
            'reg_close': reg_close,
            'gap_pct': gap_pct,
            'friday_change': friday_change,
            'change_5d': change_5d,
            'high_20': high_20,
            'low_20': low_20,
            'pct_from_high': pct_from_high,
            'pct_from_low': pct_from_low,
            'vol_ratio': vol_ratio,
            'avg_vol': avg_vol
        }
    except Exception as e:
        return None

# ============================================================
# POSITION SIZING CALCULATOR
# ============================================================

def calculate_position(entry, stop, account=ACCOUNT_SIZE, risk_pct=RISK_PER_TRADE):
    """Calculate position size based on entry and stop"""
    risk_amount = account * risk_pct
    risk_per_share = abs(entry - stop)
    
    if risk_per_share == 0:
        return None
    
    shares = int(risk_amount / risk_per_share)
    position_value = shares * entry
    
    # Calculate targets (1:2 and 1:3 R:R)
    direction = 1 if entry > stop else -1
    target_1 = entry + (risk_per_share * 2 * direction)
    target_2 = entry + (risk_per_share * 3 * direction)
    
    return {
        'shares': shares,
        'position_value': position_value,
        'risk_amount': risk_amount,
        'risk_per_share': risk_per_share,
        'target_1': target_1,  # 2R
        'target_2': target_2,  # 3R
        'pct_of_account': (position_value / account) * 100
    }

def suggest_levels(data):
    """Suggest entry, stop, and target levels based on data"""
    price = data['price']
    high_20 = data['high_20']
    low_20 = data['low_20']
    
    # Entry: current price or slight pullback
    entry = price
    
    # Stop: 6-8% below entry or below recent low
    stop_pct = price * 0.94  # 6% stop
    stop_support = low_20 * 0.98  # Just below 20-day low
    stop = max(stop_pct, stop_support)  # Use higher (tighter) stop
    
    # If near highs, use breakout setup
    if data['pct_from_high'] > -5:
        entry = high_20 * 1.01  # Entry on breakout
        stop = price * 0.94     # Stop at current level
    
    return entry, stop

# ============================================================
# MAIN DASHBOARD SECTIONS
# ============================================================

def section_premarket_gaps(priority_list):
    """Section 1: Pre-market gaps on priority watchlist"""
    print_header("PRE-MARKET GAP CHECK")
    
    results = []
    for ticker in priority_list:
        data = get_stock_data(ticker)
        if data:
            results.append(data)
    
    if not results:
        print("  No data available")
        return results
    
    # Sort by gap
    results = sorted(results, key=lambda x: abs(x['gap_pct']), reverse=True)
    
    print(f"\n  {'TICKER':<8} {'PRICE':>9} {'GAP':>8} {'FRI CHG':>9} {'5D CHG':>9} {'FROM HIGH':>10}")
    print("  " + "-" * 60)
    
    for r in results:
        gap_emoji = "🟢" if r['gap_pct'] > 1 else "🔴" if r['gap_pct'] < -1 else "⚪"
        print(f"  {gap_emoji} {r['ticker']:<6} ${r['price']:>7.2f} {r['gap_pct']:>+7.1f}% {r['friday_change']:>+8.1f}% {r['change_5d']:>+8.1f}% {r['pct_from_high']:>+9.1f}%")
    
    return results

def section_sector_heat():
    """Section 2: Sector heat map"""
    print_header("SECTOR HEAT CHECK")
    
    sector_data = {}
    
    for sector, tickers in SECTORS.items():
        changes = []
        for ticker in tickers[:5]:  # Sample 5 from each sector
            data = get_stock_data(ticker)
            if data:
                changes.append(data['change_5d'])
        
        if changes:
            sector_data[sector] = sum(changes) / len(changes)
    
    # Sort by performance
    sorted_sectors = sorted(sector_data.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n  {'SECTOR':<12} {'5-DAY AVG':>12} {'STATUS':>15}")
    print("  " + "-" * 42)
    
    for sector, avg in sorted_sectors:
        if avg > 15:
            status = "🔥🔥🔥 ON FIRE"
        elif avg > 8:
            status = "🔥🔥 HOT"
        elif avg > 3:
            status = "🔥 WARM"
        elif avg > 0:
            status = "➖ FLAT"
        else:
            status = "❄️ COLD"
        print(f"  {sector:<12} {avg:>+11.1f}% {status:>15}")
    
    return sorted_sectors

def section_position_calculator(results):
    """Section 3: Position sizing for top picks"""
    print_header("POSITION SIZING CALCULATOR")
    
    print(f"\n  Account: ${ACCOUNT_SIZE:,.0f} | Risk/Trade: {RISK_PER_TRADE*100:.0f}% = ${ACCOUNT_SIZE * RISK_PER_TRADE:.0f}")
    print(f"  Max Positions: {MAX_POSITIONS}")
    
    print(f"\n  {'TICKER':<8} {'ENTRY':>9} {'STOP':>9} {'SHARES':>8} {'SIZE':>10} {'T1 (2R)':>9} {'T2 (3R)':>9}")
    print("  " + "-" * 70)
    
    for r in results[:MAX_POSITIONS]:
        entry, stop = suggest_levels(r)
        pos = calculate_position(entry, stop)
        
        if pos:
            print(f"  {r['ticker']:<8} ${entry:>7.2f} ${stop:>7.2f} {pos['shares']:>8} ${pos['position_value']:>8,.0f} ${pos['target_1']:>7.2f} ${pos['target_2']:>7.2f}")

def section_decision_framework():
    """Section 4: Decision framework"""
    print_header("DECISION FRAMEWORK")
    
    print("""
  ┌────────────────────────────────────────────────────────────────────┐
  │  THE WOLF HUNTS STRENGTH — NOT WEAKNESS                            │
  ├────────────────────────────────────────────────────────────────────┤
  │                                                                    │
  │  ✅ TAKE THE TRADE IF:                                             │
  │     • Stock gapping UP in premarket with volume                    │
  │     • Sector is HOT (top 3 in heat map)                            │
  │     • Near 20-day high (breakout setup)                            │
  │     • 5-day momentum positive                                      │
  │     • Risk/reward at least 1:2                                     │
  │                                                                    │
  │  ❌ SKIP THE TRADE IF:                                             │
  │     • Gapping into resistance                                      │
  │     • Sector is cold/money flowing out                             │
  │     • Extended (>50% from 20-day low)                              │
  │     • No clear stop level                                          │
  │     • "Hope" is the thesis                                         │
  │                                                                    │
  │  ⏰ TIMING:                                                        │
  │     • 9:30-9:45: Watch, don't trade                                │
  │     • 9:45-10:30: First entries on confirmed direction             │
  │     • 10:30-12:00: Add to winners or cut losers                    │
  │     • 12:00-2:00: Lunch chop, stay patient                         │
  │     • 2:00-4:00: Final push, take profits or hold overnight        │
  │                                                                    │
  └────────────────────────────────────────────────────────────────────┘
""")

def section_checklist():
    """Section 5: Morning checklist"""
    print_header("MORNING CHECKLIST")
    
    print("""
  ┌────────────────────────────────────────────────────────────────────┐
  │  PRE-MARKET (6:00 AM - 9:30 AM ET)                                 │
  ├────────────────────────────────────────────────────────────────────┤
  │  [ ] Check futures (SPY, QQQ direction)                            │
  │  [ ] Run this scanner for premarket gaps                           │
  │  [ ] Check news on top gappers (finviz.com)                        │
  │  [ ] Identify #1 and #2 plays                                      │
  │  [ ] Set alerts at entry levels                                    │
  │  [ ] Size positions BEFORE market open                             │
  │  [ ] Know your stops BEFORE you enter                              │
  ├────────────────────────────────────────────────────────────────────┤
  │  AT THE OPEN (9:30 AM)                                             │
  ├────────────────────────────────────────────────────────────────────┤
  │  [ ] WATCH first 15 minutes - don't chase                          │
  │  [ ] Note opening range (high/low of first 15 min)                 │
  │  [ ] Wait for pullback to entry OR breakout of opening range       │
  │  [ ] Execute with LIMIT orders, not market                         │
  │  [ ] Set stop loss IMMEDIATELY after fill                          │
  ├────────────────────────────────────────────────────────────────────┤
  │  DURING THE DAY                                                    │
  ├────────────────────────────────────────────────────────────────────┤
  │  [ ] Check positions every 30 min                                  │
  │  [ ] Move stops to breakeven once +5%                              │
  │  [ ] Take partial profits at T1 (2R)                               │
  │  [ ] Let runners run to T2 (3R)                                    │
  │  [ ] Cut losers FAST if stop hit                                   │
  └────────────────────────────────────────────────────────────────────┘
""")

def section_quick_stats():
    """Quick account/risk stats"""
    print_header("ACCOUNT STATUS")
    
    risk_per_trade = ACCOUNT_SIZE * RISK_PER_TRADE
    max_risk_total = risk_per_trade * MAX_POSITIONS
    
    print(f"""
  Account Size:     ${ACCOUNT_SIZE:,.0f}
  Risk Per Trade:   ${risk_per_trade:,.0f} ({RISK_PER_TRADE*100:.0f}%)
  Max Positions:    {MAX_POSITIONS}
  Max Total Risk:   ${max_risk_total:,.0f} ({(max_risk_total/ACCOUNT_SIZE)*100:.0f}% of account)
  
  GOLDEN RULES:
  • Never risk more than 2% on a single trade
  • Never have more than 5 positions open
  • If down 5% on the day, STOP TRADING
  • Protect capital first, profits second
""")

# ============================================================
# MAIN DASHBOARD
# ============================================================

def run_dashboard():
    """Run the full Monday battle station dashboard"""
    et_now = get_eastern_time()
    
    clear_screen()
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  🐺 MONDAY BATTLE STATION".center(68) + "█")
    print("█" + f"  {et_now.strftime('%A, %B %d, %Y — %I:%M %p ET')}".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    # Section 1: Pre-market gaps
    print("\n⚡ Scanning priority watchlist...")
    results = section_premarket_gaps(PRIORITY_WATCHLIST)
    
    # Section 2: Sector heat
    print("\n⚡ Checking sector heat...")
    section_sector_heat()
    
    # Section 3: Position calculator
    if results:
        section_position_calculator(results)
    
    # Section 4: Quick stats
    section_quick_stats()
    
    # Section 5: Decision framework
    section_decision_framework()
    
    # Section 6: Checklist
    section_checklist()
    
    print("\n" + "=" * 70)
    print("🐺 THE WOLF IS READY. HUNT STRENGTH. PROTECT CAPITAL.")
    print("=" * 70)

def run_live(refresh=60):
    """Run in live mode with auto-refresh"""
    print("\n🐺 MONDAY BATTLE STATION — LIVE MODE")
    print(f"   Refreshing every {refresh} seconds. Ctrl+C to stop.\n")
    
    try:
        while True:
            run_dashboard()
            print(f"\n   Next refresh in {refresh}s...")
            time.sleep(refresh)
    except KeyboardInterrupt:
        print("\n\n🐺 Battle station closed. Good hunting!")

def main():
    parser = argparse.ArgumentParser(description='Monday Battle Station')
    parser.add_argument('--live', action='store_true', help='Auto-refresh mode')
    parser.add_argument('--refresh', type=int, default=60, help='Refresh interval (default: 60s)')
    
    args = parser.parse_args()
    
    if args.live:
        run_live(args.refresh)
    else:
        run_dashboard()

if __name__ == "__main__":
    main()
