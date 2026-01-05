#!/usr/bin/env python3
"""
🐺 EARNINGS MOMENTUM SCANNER
=============================
Tracks upcoming earnings and post-earnings momentum
Identifies setups before/after earnings announcements

Usage:
    python earnings_momentum_scanner.py                # Full scan
    python earnings_momentum_scanner.py --upcoming     # Next 2 weeks only
    python earnings_momentum_scanner.py --recent       # Last 2 weeks only
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import argparse
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# UNIVERSE FOR EARNINGS TRACKING
# ============================================================

EARNINGS_UNIVERSE = {
    'NUCLEAR': ['UUUU', 'SMR', 'LEU', 'OKLO', 'CCJ', 'DNN', 'UEC', 'NXE', 'NNE'],
    'UTILITIES': ['NEE', 'VST', 'CEG', 'WMB'],
    'COOLING': ['VRT', 'MOD', 'NVT'],
    'PHOTONICS': ['LITE', 'AAOI', 'COHR'],
    'NETWORKING': ['ANET', 'CRDO', 'FN', 'CIEN'],
    'STORAGE': ['MU', 'WDC', 'STX'],
    'CHIPS': ['AMD', 'MRVL', 'AVGO', 'INTC', 'AMKR'],
    'DC_BUILDERS': ['SMCI', 'EME', 'CLS', 'FIX'],
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'ASTS', 'SIDU', 'BKSY'],
    'AI_SOFTWARE': ['PLTR', 'AI', 'SOUN', 'PATH', 'UPST']
}

# ============================================================
# EARNINGS ANALYSIS
# ============================================================

def get_earnings_data(ticker, sector):
    """Get earnings information for a ticker"""
    try:
        stock = yf.Ticker(ticker)
        
        # Get calendar (next earnings)
        try:
            calendar = stock.calendar
            if calendar is not None and not calendar.empty:
                # Handle different formats
                if isinstance(calendar, pd.DataFrame):
                    next_earnings = calendar.get('Earnings Date', [None])[0]
                else:
                    next_earnings = calendar.get('Earnings Date')
            else:
                next_earnings = None
        except:
            next_earnings = None
        
        # Get earnings history
        try:
            earnings_dates = stock.earnings_dates
            if earnings_dates is not None and not earnings_dates.empty:
                # Filter for dates with actual/estimate data
                recent_earnings = earnings_dates.head(4)  # Last 4 quarters
            else:
                recent_earnings = None
        except:
            recent_earnings = None
        
        # Get current price and momentum
        hist = stock.history(period='1mo', prepost=True)
        if len(hist) < 5:
            return None
        
        current = hist['Close'].iloc[-1]
        change_5d = ((current - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100
        change_20d = ((current - hist['Close'].iloc[-20]) / hist['Close'].iloc[-20]) * 100 if len(hist) >= 20 else 0
        
        # Calculate days to next earnings
        days_to_earnings = None
        if next_earnings:
            try:
                if isinstance(next_earnings, str):
                    next_date = datetime.strptime(next_earnings[:10], '%Y-%m-%d')
                else:
                    next_date = next_earnings
                    if hasattr(next_date, 'date'):
                        next_date = datetime.combine(next_date.date(), datetime.min.time())
                
                days_to_earnings = (next_date - datetime.now()).days
            except:
                pass
        
        # Analyze surprise history
        surprise_history = []
        if recent_earnings is not None:
            try:
                for idx, row in recent_earnings.iterrows():
                    eps_est = row.get('EPS Estimate', None)
                    eps_act = row.get('Reported EPS', None)
                    if eps_est and eps_act and pd.notna(eps_est) and pd.notna(eps_act):
                        surprise = ((eps_act - eps_est) / abs(eps_est)) * 100 if eps_est != 0 else 0
                        surprise_history.append({
                            'date': idx,
                            'estimate': eps_est,
                            'actual': eps_act,
                            'surprise': surprise
                        })
            except:
                pass
        
        # Beat rate
        beats = len([s for s in surprise_history if s['surprise'] > 0])
        beat_rate = (beats / len(surprise_history)) * 100 if surprise_history else None
        
        return {
            'ticker': ticker,
            'sector': sector,
            'price': current,
            '5d_change': change_5d,
            '20d_change': change_20d,
            'next_earnings': str(next_earnings)[:10] if next_earnings else None,
            'days_to_earnings': days_to_earnings,
            'beat_rate': beat_rate,
            'surprise_history': surprise_history[:4],
            'avg_surprise': sum(s['surprise'] for s in surprise_history) / len(surprise_history) if surprise_history else None
        }
        
    except Exception as e:
        return None

def scan_earnings(mode='all'):
    """Scan all tickers for earnings data"""
    print(f"\n⚡ SCANNING EARNINGS DATA...")
    
    results = []
    total = sum(len(t) for t in EARNINGS_UNIVERSE.values())
    count = 0
    
    for sector, tickers in EARNINGS_UNIVERSE.items():
        for ticker in tickers:
            count += 1
            print(f"   Scanning: {ticker} ({count}/{total})       ", end='\r')
            
            data = get_earnings_data(ticker, sector)
            if data:
                results.append(data)
    
    print(f"\n   ✓ Scanned {len(results)} tickers")
    
    return results

def get_eastern_time():
    eastern = pytz.timezone('US/Eastern')
    return datetime.now(eastern)

def display_earnings_report(results, mode='all'):
    """Display earnings report"""
    et_now = get_eastern_time()
    
    print("\n" + "=" * 110)
    print(f"🐺 EARNINGS MOMENTUM SCANNER — {et_now.strftime('%I:%M %p ET')}")
    print("=" * 110)
    
    # Upcoming earnings
    upcoming = [r for r in results if r.get('days_to_earnings') and 0 < r['days_to_earnings'] <= 30]
    upcoming_sorted = sorted(upcoming, key=lambda x: x['days_to_earnings'])
    
    print(f"\n📅 UPCOMING EARNINGS (Next 30 days)\n")
    print(f"{'TICKER':<8} | {'SECTOR':<12} | {'EARNINGS DATE':<15} | {'DAYS':>6} | {'5D CHG':>8} | {'20D CHG':>8} | {'BEAT RATE':>10} | {'SETUP'}")
    print("-" * 110)
    
    for r in upcoming_sorted[:15]:
        # Setup quality
        setup = ""
        if r['5d_change'] > 5 and (r['beat_rate'] or 0) > 70:
            setup = "🔥 STRONG"
        elif r['5d_change'] > 0:
            setup = "📈 OK"
        elif r['5d_change'] < -5:
            setup = "⚠️ WEAK"
        else:
            setup = "➖ FLAT"
        
        beat_str = f"{r['beat_rate']:.0f}%" if r['beat_rate'] else "—"
        
        print(f"{r['ticker']:<8} | {r['sector']:<12} | {r['next_earnings'] or '—':<15} | {r['days_to_earnings']:>6} | {r['5d_change']:>+7.1f}% | {r['20d_change']:>+7.1f}% | {beat_str:>10} | {setup}")
    
    if not upcoming_sorted:
        print("   No upcoming earnings in next 30 days")
    
    # This week's earnings
    this_week = [r for r in upcoming if r['days_to_earnings'] <= 7]
    if this_week:
        print("\n🎯 THIS WEEK'S EARNINGS:")
        for r in sorted(this_week, key=lambda x: x['days_to_earnings']):
            print(f"   {r['ticker']} ({r['sector']}) — {r['next_earnings']} — {r['days_to_earnings']} days away")
    
    # Beat rate leaders
    print("\n" + "=" * 110)
    print("📊 EARNINGS BEAT RATE LEADERS")
    print("=" * 110)
    
    with_beat_rate = [r for r in results if r.get('beat_rate') is not None]
    beat_sorted = sorted(with_beat_rate, key=lambda x: x['beat_rate'], reverse=True)
    
    print(f"\n{'TICKER':<8} | {'SECTOR':<12} | {'BEAT RATE':>10} | {'AVG SURPRISE':>12} | {'RECENT TREND':>12}")
    print("-" * 65)
    
    for r in beat_sorted[:10]:
        avg_surp = f"{r['avg_surprise']:+.1f}%" if r['avg_surprise'] else "—"
        trend = "🔥 CRUSHER" if r['beat_rate'] >= 75 else "📈 BEATS" if r['beat_rate'] >= 50 else "⚠️ MIXED"
        print(f"{r['ticker']:<8} | {r['sector']:<12} | {r['beat_rate']:>9.0f}% | {avg_surp:>12} | {trend}")
    
    # Post-earnings momentum plays
    print("\n" + "=" * 110)
    print("🚀 POST-EARNINGS MOMENTUM (Strong move + upcoming earnings)")
    print("=" * 110)
    
    momentum_plays = [r for r in results if r['5d_change'] > 5 and r.get('days_to_earnings') and r['days_to_earnings'] > 0 and r['days_to_earnings'] <= 30]
    momentum_sorted = sorted(momentum_plays, key=lambda x: x['5d_change'], reverse=True)
    
    for r in momentum_sorted[:5]:
        print(f"\n   {r['ticker']} ({r['sector']})")
        print(f"      5-day: {r['5d_change']:+.1f}% | 20-day: {r['20d_change']:+.1f}%")
        print(f"      Earnings: {r['next_earnings']} ({r['days_to_earnings']} days)")
        if r['beat_rate']:
            print(f"      Beat rate: {r['beat_rate']:.0f}%")
    
    # Pre-earnings setups
    print("\n" + "=" * 110)
    print("🐺 WOLF'S EARNINGS PLAYS")
    print("=" * 110)
    
    # Strong beat history + momentum + upcoming earnings
    best_setups = [
        r for r in results 
        if r.get('beat_rate') and r['beat_rate'] >= 50
        and r['5d_change'] > 0
        and r.get('days_to_earnings') and 0 < r['days_to_earnings'] <= 14
    ]
    
    if best_setups:
        print("\n🎯 PRE-EARNINGS MOMENTUM PLAYS:")
        print("   (Strong beat history + positive momentum + earnings within 2 weeks)")
        for r in sorted(best_setups, key=lambda x: x['beat_rate'], reverse=True):
            print(f"   → {r['ticker']}: {r['beat_rate']:.0f}% beat rate, {r['5d_change']:+.1f}% momentum, earnings {r['next_earnings']}")
    
    # Earnings surprise history
    print("\n📈 RECENT SURPRISE STREAKS:")
    streak_tickers = []
    for r in results:
        if r.get('surprise_history') and len(r['surprise_history']) >= 2:
            recent = r['surprise_history'][:2]
            if all(s['surprise'] > 0 for s in recent):
                streak_tickers.append((r['ticker'], len([s for s in r['surprise_history'] if s['surprise'] > 0])))
    
    for ticker, streak in sorted(streak_tickers, key=lambda x: x[1], reverse=True)[:5]:
        print(f"   {ticker}: {streak} consecutive beats")

def main():
    parser = argparse.ArgumentParser(description='Earnings Momentum Scanner')
    parser.add_argument('--upcoming', action='store_true', help='Show upcoming only')
    parser.add_argument('--recent', action='store_true', help='Show recent only')
    
    args = parser.parse_args()
    
    mode = 'all'
    if args.upcoming:
        mode = 'upcoming'
    elif args.recent:
        mode = 'recent'
    
    results = scan_earnings(mode)
    display_earnings_report(results, mode)

if __name__ == "__main__":
    main()
