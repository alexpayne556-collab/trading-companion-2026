#!/usr/bin/env python3
"""
🐺 LIVE TRADING COMPANION - Data-Validated Patterns Only
Uses ONLY the 3 validated strategies from pattern_validation.ipynb

Usage: python live_trading_companion.py
Run this every morning and throughout the day for real-time signals
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import argparse

# Color codes for terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

# Current positions (update these manually or connect to broker)
CURRENT_POSITIONS = {
    'LUNR': {'shares': 0, 'avg_cost': 0},  # Update with real data
    'IONQ': {'shares': 0, 'avg_cost': 0},
    'UUUU': {'shares': 0, 'avg_cost': 0},
    'MU': {'shares': 0, 'avg_cost': 0},
    'ASTS': {'shares': 0, 'avg_cost': 0},
    'USAR': {'shares': 0, 'avg_cost': 0}
}

# Validated tickers for 10 AM dip (60% win rate)
DIP_TICKERS = ['UUUU', 'IONQ', 'MU', 'WDC']

# Sector ETFs for rotation tracking
SECTOR_ETFS = {
    'Tech': 'XLK',
    'Industrials': 'XLI',
    'Materials': 'XLB',
    'Financials': 'XLF',
    'Energy': 'XLE'
}

# Watchlist for momentum scanning
MOMENTUM_WATCHLIST = [
    'NVDA', 'AMD', 'AVGO', 'MU', 'WDC', 'STX', 'KLAC', 'LRCX',  # AI Chips
    'LUNR', 'RKLB', 'ASTS', 'RDW',  # Space
    'IONQ', 'RGTI', 'QUBT', 'QBTS',  # Quantum
    'UUUU', 'SMR', 'OKLO', 'CCJ',  # Nuclear
    'USAR', 'MP', 'REE'  # Rare Earth
]


def count_consecutive_green_days(ticker, days=10):
    """
    Count consecutive green days for a ticker.
    VALIDATED: 4+ days = 75-100% reversal rate
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=f'{days}d')
        
        if len(hist) < 2:
            return 0, None
        
        # Count from most recent backwards
        green_streak = 0
        for i in range(len(hist) - 1, 0, -1):
            change = ((hist['Close'].iloc[i] / hist['Close'].iloc[i-1]) - 1) * 100
            if change > 0:
                green_streak += 1
            else:
                break
        
        current_price = hist['Close'].iloc[-1]
        return green_streak, current_price
        
    except Exception as e:
        print(f"Error counting green days for {ticker}: {e}")
        return 0, None


def check_sector_rotation():
    """
    Check which sectors are accelerating/decelerating.
    VALIDATED: 160 instances confirm inverse relationships
    """
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}🔄 SECTOR ROTATION ANALYSIS{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")
    
    sector_data = {}
    
    for name, ticker in SECTOR_ETFS.items():
        try:
            etf = yf.Ticker(ticker)
            hist = etf.history(period='15d')
            
            if len(hist) < 10:
                continue
            
            # Calculate 5-day and 10-day returns
            returns_5d = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-6]) - 1) * 100
            returns_10d = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-11]) - 1) * 100
            
            accelerating = returns_5d > returns_10d
            
            sector_data[name] = {
                'ticker': ticker,
                'returns_5d': returns_5d,
                'returns_10d': returns_10d,
                'accelerating': accelerating,
                'current': hist['Close'].iloc[-1]
            }
            
        except Exception as e:
            print(f"Error fetching {name}: {e}")
    
    # Print results
    print(f"{'SECTOR':<15} {'5D RETURN':<12} {'10D RETURN':<12} {'STATUS':<15}")
    print("-" * 60)
    
    for name, data in sector_data.items():
        status = f"{GREEN}ACCELERATING{RESET}" if data['accelerating'] else f"{RED}DECELERATING{RESET}"
        print(f"{name:<15} {data['returns_5d']:>+10.2f}%  {data['returns_10d']:>+10.2f}%  {status}")
    
    # Show inverse pairs
    print(f"\n{YELLOW}🎯 VALIDATED INVERSE PAIRS (when one UP, other DOWN):{RESET}")
    print("   • Tech ↔ Financials")
    print("   • Tech ↔ Materials")
    print("   • Materials ↔ Industrials")
    print()
    
    # Find accelerating sectors
    accelerating_sectors = [name for name, data in sector_data.items() if data['accelerating']]
    decelerating_sectors = [name for name, data in sector_data.items() if not data['accelerating']]
    
    if accelerating_sectors:
        print(f"{GREEN}✅ BUY STOCKS IN: {', '.join(accelerating_sectors)}{RESET}")
    if decelerating_sectors:
        print(f"{RED}❌ AVOID/SELL IN: {', '.join(decelerating_sectors)}{RESET}")
    
    return sector_data


def check_positions_green_days():
    """
    Check all positions for consecutive green days.
    SELL SIGNAL: 4+ days = 75% reversal rate
    """
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}📊 POSITION ANALYSIS - GREEN DAY COUNT{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")
    
    print(f"{'TICKER':<10} {'PRICE':<10} {'GREEN DAYS':<12} {'ACTION':<30}")
    print("-" * 80)
    
    sell_signals = []
    
    for ticker in CURRENT_POSITIONS.keys():
        green_days, current_price = count_consecutive_green_days(ticker, days=10)
        
        if current_price is None:
            continue
        
        # Determine action based on validated pattern
        if green_days >= 5:
            action = f"{RED}{BOLD}🚨 SELL ALL - 100% reversal rate{RESET}"
            sell_signals.append({'ticker': ticker, 'urgency': 'CRITICAL', 'days': green_days})
        elif green_days == 4:
            action = f"{YELLOW}{BOLD}⚠️ SELL 50% - 75% reversal rate{RESET}"
            sell_signals.append({'ticker': ticker, 'urgency': 'HIGH', 'days': green_days})
        elif green_days == 3:
            action = f"{YELLOW}⚠️ WATCH - 14% reversal (keep riding){RESET}"
        else:
            action = f"{GREEN}✅ HOLD - No reversal signal{RESET}"
        
        print(f"{ticker:<10} ${current_price:<9.2f} {green_days:<12} {action}")
    
    if sell_signals:
        print(f"\n{RED}{BOLD}🚨 IMMEDIATE ACTION REQUIRED:{RESET}")
        for signal in sell_signals:
            print(f"   {signal['ticker']}: {signal['days']} green days - {signal['urgency']} PRIORITY")
    else:
        print(f"\n{GREEN}✅ All positions safe - no reversal signals{RESET}")
    
    return sell_signals


def find_momentum_opportunities():
    """
    Find stocks with momentum (validated 75% continuation rate).
    CHASE BIG RUNNERS - they keep running!
    """
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}🚀 MOMENTUM CHASE OPPORTUNITIES (75% Win Rate){RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")
    
    print(f"{'TICKER':<10} {'TODAY CHG':<12} {'VOLUME':<15} {'ACTION':<30}")
    print("-" * 80)
    
    opportunities = []
    
    for ticker in MOMENTUM_WATCHLIST:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='2d')
            
            if len(hist) < 2:
                continue
            
            # Today's change
            today_change = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-2]) - 1) * 100
            
            # Volume check
            avg_volume = hist['Volume'].iloc[:-1].mean()
            today_volume = hist['Volume'].iloc[-1]
            volume_ratio = today_volume / avg_volume if avg_volume > 0 else 0
            
            # VALIDATED PATTERN: Big runners (+5%+) with volume keep running 75%
            if today_change > 5 and volume_ratio > 1.5:
                action = f"{GREEN}{BOLD}🎯 CHASE - 75% continuation{RESET}"
                opportunities.append({
                    'ticker': ticker,
                    'change': today_change,
                    'volume_ratio': volume_ratio
                })
                
                print(f"{ticker:<10} {today_change:>+10.2f}%  {volume_ratio:>12.2f}x  {action}")
                
        except Exception as e:
            pass
    
    if not opportunities:
        print(f"{YELLOW}No momentum opportunities right now{RESET}")
    
    return opportunities


def check_10am_dip_setups():
    """
    Check for 10 AM dip opportunities on VALIDATED tickers only.
    ONLY UUUU, IONQ, MU, WDC have 60% dip rate.
    """
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}⏰ 10 AM DIP SETUPS (60% Win Rate - Selective Tickers){RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")
    
    now = datetime.now()
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    dip_window_start = now.replace(hour=10, minute=0, second=0, microsecond=0)
    dip_window_end = now.replace(hour=10, minute=30, second=0, microsecond=0)
    
    if now < market_open:
        print(f"{YELLOW}Market not open yet. Check back at 9:30 AM{RESET}")
        return []
    
    if now < dip_window_start:
        print(f"{BLUE}Wait until 10:00 AM for dip setups{RESET}")
        print(f"{BLUE}Preparing tickers: {', '.join(DIP_TICKERS)}{RESET}")
        return []
    
    if now > dip_window_end:
        print(f"{YELLOW}10 AM window closed. No more dip plays today.{RESET}")
        return []
    
    print(f"{GREEN}🎯 10 AM DIP WINDOW ACTIVE{RESET}")
    print(f"{'TICKER':<10} {'CURRENT':<10} {'OPEN':<10} {'DIP %':<10} {'ACTION':<30}")
    print("-" * 80)
    
    dip_setups = []
    
    for ticker in DIP_TICKERS:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1d', interval='1m')
            
            if len(hist) < 2:
                continue
            
            open_price = hist['Open'].iloc[0]
            current_price = hist['Close'].iloc[-1]
            dip_pct = ((current_price / open_price) - 1) * 100
            
            # Check if it gapped up and is dipping
            if open_price > hist['Close'].iloc[0] and dip_pct < 0:
                action = f"{GREEN}🎯 BUY DIP - Set limit at ${current_price:.2f}{RESET}"
                dip_setups.append({
                    'ticker': ticker,
                    'current': current_price,
                    'open': open_price,
                    'dip_pct': dip_pct
                })
                
                print(f"{ticker:<10} ${current_price:<9.2f} ${open_price:<9.2f} {dip_pct:>+9.2f}%  {action}")
            
        except Exception as e:
            pass
    
    if not dip_setups:
        print(f"{YELLOW}No dip setups right now{RESET}")
    
    print(f"\n{RED}⚠️ DO NOT USE FOR: LUNR, USAR (only 40% dip rate - chase instead){RESET}")
    
    return dip_setups


def main():
    parser = argparse.ArgumentParser(description='Live Trading Companion - Data-Validated Patterns')
    parser.add_argument('--positions', action='store_true', help='Check position green days')
    parser.add_argument('--sectors', action='store_true', help='Check sector rotation')
    parser.add_argument('--momentum', action='store_true', help='Find momentum opportunities')
    parser.add_argument('--dips', action='store_true', help='Check 10 AM dip setups')
    parser.add_argument('--all', action='store_true', help='Run all checks')
    
    args = parser.parse_args()
    
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}🐺 WOLF PACK TRADING COMPANION - DATA-VALIDATED PATTERNS ONLY{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}Based on pattern_validation.ipynb - 60-90 days backtested{RESET}")
    print(f"{BLUE}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    
    if args.all or (not args.positions and not args.sectors and not args.momentum and not args.dips):
        # Run everything if no specific flags
        check_positions_green_days()
        check_sector_rotation()
        find_momentum_opportunities()
        check_10am_dip_setups()
    else:
        if args.positions:
            check_positions_green_days()
        if args.sectors:
            check_sector_rotation()
        if args.momentum:
            find_momentum_opportunities()
        if args.dips:
            check_10am_dip_setups()
    
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}🐺 RULES:{RESET}")
    print(f"{BLUE}✅ Chase momentum (75% continuation){RESET}")
    print(f"{BLUE}✅ Sell after 4 green days (75% reversal){RESET}")
    print(f"{BLUE}✅ Rotate with accelerating sectors (160 instances validated){RESET}")
    print(f"{BLUE}⚠️ 10 AM dip ONLY for UUUU/IONQ/MU/WDC (60% win rate){RESET}")
    print(f"{BLUE}❌ Don't wait for dips on runners - they keep running!{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")


if __name__ == "__main__":
    main()
