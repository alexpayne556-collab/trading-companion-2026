#!/usr/bin/env python3
"""
🐺 CATALYST FINDER
Find upcoming events that move stocks

The Pack's Edge:
- CES demos
- Earnings dates  
- Conference presentations
- Product launches
- Contract announcements

Usage:
    python3 catalyst_finder.py --ticker QUBT
    python3 catalyst_finder.py --week  # All catalysts this week
    python3 catalyst_finder.py --sector photonics
"""

import argparse
import yfinance as yf
from datetime import datetime, timedelta
import json

# 🐺 KNOWN CATALYSTS (manually tracked)
# These are events we've discovered through research
UPCOMING_CATALYSTS = {
    # CES 2026 - January 7-10, 2026
    'RDW': {
        'date': '2026-01-07',
        'event': 'CES 2026 - Lunar Manufacturing Demo',
        'time': '2:00 PM ET',
        'source': 'CBS 60 Minutes mention',
        'impact': 'HIGH',
    },
    'QUBT': {
        'date': '2026-01-07',
        'event': 'CES 2026 - Photonics Chip Presentation',
        'time': '2:00 PM ET',
        'source': 'Company website',
        'impact': 'HIGH',
    },
    'IONQ': {
        'date': '2026-01-07',
        'event': 'CES 2026 - Quantum Computing Demo',
        'time': 'TBA',
        'source': 'CES schedule',
        'impact': 'MEDIUM',
    },
    
    # Earnings season starts mid-January
    'NVDA': {
        'date': '2026-02-26',
        'event': 'Q4 2025 Earnings',
        'time': 'After Market',
        'source': 'Yahoo Finance',
        'impact': 'HIGH',
    },
    
    # Space events
    'LUNR': {
        'date': '2026-01-15',
        'event': 'IM-2 Mission Update',
        'time': 'TBA',
        'source': 'NASA schedule',
        'impact': 'HIGH',
    },
    'RKLB': {
        'date': '2026-01-10',
        'event': 'Electron Launch Window',
        'time': 'TBA',
        'source': 'Launch schedule',
        'impact': 'MEDIUM',
    },
    
    # Nuclear
    'SMR': {
        'date': '2026-01-15',
        'event': 'NRC Update Expected',
        'time': 'TBA',
        'source': 'Company filings',
        'impact': 'HIGH',
    },
    'OKLO': {
        'date': '2026-01-20',
        'event': 'DOE Permit Decision Window',
        'time': 'TBA',
        'source': 'Regulatory calendar',
        'impact': 'HIGH',
    },
    
    # Rare Earth
    'USAR': {
        'date': '2026-01-31',
        'event': 'Venezuela Refinery Update',
        'time': 'TBA',
        'source': 'Company PR',
        'impact': 'MEDIUM',
    },
}

# Weekly catalyst patterns
WEEKLY_PATTERNS = {
    'Monday': 'Pre-market gaps from weekend news',
    'Tuesday': 'CES demos continue (this week)',
    'Wednesday': 'Mid-week consolidation typical',
    'Thursday': 'Options positioning for Friday expiry',
    'Friday': 'Max pain gravity + weekly options expiry',
}


def get_earnings_date(ticker: str) -> dict:
    """Get next earnings date from Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        calendar = stock.calendar
        
        if calendar is not None and 'Earnings Date' in calendar:
            earnings_date = calendar['Earnings Date']
            if isinstance(earnings_date, list) and len(earnings_date) > 0:
                return {
                    'date': str(earnings_date[0].date()),
                    'event': 'Earnings Report',
                    'source': 'Yahoo Finance',
                    'impact': 'HIGH'
                }
        return None
    except:
        return None


def find_catalyst(ticker: str) -> dict:
    """Find all known catalysts for a ticker"""
    catalysts = []
    
    # Check our known catalysts
    if ticker in UPCOMING_CATALYSTS:
        catalysts.append(UPCOMING_CATALYSTS[ticker])
    
    # Check Yahoo Finance for earnings
    earnings = get_earnings_date(ticker)
    if earnings:
        catalysts.append(earnings)
    
    return catalysts


def catalysts_this_week():
    """Show all catalysts happening this week"""
    today = datetime.now()
    week_end = today + timedelta(days=7)
    
    print(f"\n{'='*80}")
    print(f"🐺 CATALYSTS THIS WEEK ({today.strftime('%b %d')} - {week_end.strftime('%b %d')})")
    print(f"{'='*80}")
    
    upcoming = []
    
    for ticker, catalyst in UPCOMING_CATALYSTS.items():
        try:
            cat_date = datetime.strptime(catalyst['date'], '%Y-%m-%d')
            if today <= cat_date <= week_end:
                upcoming.append({
                    'ticker': ticker,
                    **catalyst,
                    'date_obj': cat_date
                })
        except:
            pass
    
    # Sort by date
    upcoming.sort(key=lambda x: x['date_obj'])
    
    if not upcoming:
        print("\n📭 No known catalysts this week (in our database)")
        print("   Tip: Check CES schedule, earnings calendar, SEC filings")
        return
    
    # Group by day
    current_day = None
    for cat in upcoming:
        day = cat['date_obj'].strftime('%A, %B %d')
        if day != current_day:
            current_day = day
            print(f"\n📅 {day}")
            print("-" * 60)
        
        impact_emoji = "🔥" if cat['impact'] == 'HIGH' else "⚡"
        print(f"   {impact_emoji} {cat['ticker']}: {cat['event']}")
        if 'time' in cat:
            print(f"      Time: {cat['time']}")
        if 'source' in cat:
            print(f"      Source: {cat['source']}")


def analyze_ticker_catalysts(ticker: str):
    """Full catalyst analysis for a ticker"""
    print(f"\n{'='*80}")
    print(f"🐺 CATALYST ANALYSIS: {ticker}")
    print(f"{'='*80}")
    
    catalysts = find_catalyst(ticker)
    
    # Get current price
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        print(f"\nCurrent Price: ${price:.2f}")
    except:
        price = 0
    
    if not catalysts:
        print("\n📭 No known upcoming catalysts in our database")
        print("\nSuggested research:")
        print(f"   • Search: \"{ticker} January 2026 news\"")
        print(f"   • Check: Company investor relations page")
        print(f"   • Check: SEC EDGAR for 8-K filings")
        return
    
    print(f"\n📅 UPCOMING CATALYSTS:")
    print("-" * 60)
    
    for cat in catalysts:
        try:
            cat_date = datetime.strptime(cat['date'], '%Y-%m-%d')
            days_away = (cat_date - datetime.now()).days
            
            impact_emoji = "🔥" if cat['impact'] == 'HIGH' else "⚡"
            print(f"\n{impact_emoji} {cat['event']}")
            print(f"   Date: {cat['date']} ({days_away} days away)")
            if 'time' in cat:
                print(f"   Time: {cat['time']}")
            if 'source' in cat:
                print(f"   Source: {cat['source']}")
                
            # Pre-catalyst positioning advice
            if days_away <= 3:
                print(f"   ⚠️  IMMINENT - Position NOW if you're going to")
            elif days_away <= 7:
                print(f"   📌 This week - Watch for pre-catalyst run")
        except:
            print(f"\n{cat['event']}")
            print(f"   Date: {cat['date']}")


def show_this_weeks_plan():
    """Show the week's trading plan"""
    today = datetime.now()
    day_name = today.strftime('%A')
    
    print(f"\n{'='*80}")
    print(f"🐺 THIS WEEK'S PLAYBOOK")
    print(f"{'='*80}")
    
    print(f"\n📅 TODAY IS {day_name.upper()}")
    print(f"   Pattern: {WEEKLY_PATTERNS.get(day_name, 'Normal trading day')}")
    
    print(f"\n🎯 KEY EVENTS THIS WEEK:")
    print("-" * 60)
    print("   • CES 2026: Jan 7-10 (TOMORROW STARTS)")
    print("   • Weekly options expiry: Friday Jan 10")
    print("   • Pre-market tells: Watch 6-9:30 AM gaps")
    
    catalysts_this_week()
    
    print(f"\n{'='*80}")
    print("🐺 STRATEGY FOR THE WEEK:")
    print(f"{'='*80}")
    print("""
   MONDAY (Today):
   • Position in CES plays BEFORE demos tomorrow
   • Watch pre-market for weekend news gaps
   • QUBT, RDW, IONQ all have CES events
   
   TUESDAY-WEDNESDAY:
   • CES demos happening - watch for press releases
   • Trade the NEWS not the anticipation
   • Be ready to take profits on pops
   
   THURSDAY:
   • Options positioning begins for Friday
   • Watch max pain levels
   • Gamma squeeze setups emerge
   
   FRIDAY:
   • Weekly expiry - max pain gravity
   • Take profits before 3 PM
   • Don't hold through weekend unless confident
""")


def main():
    parser = argparse.ArgumentParser(description='🐺 Find stock catalysts')
    parser.add_argument('--ticker', '-t', help='Analyze specific ticker')
    parser.add_argument('--week', '-w', action='store_true', help='Show this week\'s catalysts')
    parser.add_argument('--plan', '-p', action='store_true', help='Show weekly trading plan')
    
    args = parser.parse_args()
    
    if args.ticker:
        analyze_ticker_catalysts(args.ticker.upper())
    elif args.week:
        catalysts_this_week()
    elif args.plan:
        show_this_weeks_plan()
    else:
        # Default: show plan
        show_this_weeks_plan()


if __name__ == '__main__':
    main()
