#!/usr/bin/env python3
"""
🐺 GAP DIP RECOVERY ANALYZER
Shows you EXACTLY when stocks gap down then recover - so you can buy the dip.

Tyr's observation: "Reality is they gap down then back up and I wish I bought the dip"
Let's validate this pattern and find the OPTIMAL entry point.

This tool analyzes:
1. Opening gap direction (up or down)
2. If gap down: When is the LOW? (best entry)
3. If gap up: When is the first pullback? (best entry)
4. Recovery timing (when does it come back?)
5. Success rate (% that recover after gap down)
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import argparse
import json
from pathlib import Path

def analyze_gap_dip_recovery(ticker, days_back=10):
    """
    Analyze gap-down-then-recovery pattern to find optimal entry.
    
    Args:
        ticker: Stock symbol
        days_back: How many days to analyze
    
    Returns:
        dict with pattern analysis
    """
    print(f"\n🔍 GAP DIP RECOVERY ANALYZER: {ticker}")
    print(f"   Looking back {days_back} days")
    print("=" * 60)
    
    try:
        stock = yf.Ticker(ticker)
        
        # Get daily data for gap analysis
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back + 5)
        
        daily = stock.history(start=start_date, end=end_date, interval='1d')
        
        if len(daily) < 2:
            print(f"   ⚠️ Not enough data for {ticker}")
            return None
        
        # Get 1-minute data for intraday analysis
        hist = stock.history(start=end_date - timedelta(days=days_back), end=end_date, interval='1m')
        
        if hist.empty:
            print(f"   ⚠️ No intraday data for {ticker}")
            return None
        
        results = {
            'ticker': ticker,
            'days_analyzed': days_back,
            'patterns': []
        }
        
        # Analyze each day
        hist['Date'] = hist.index.date
        
        for i, date in enumerate(hist['Date'].unique()):
            if i == 0:
                continue  # Need previous day for gap calculation
            
            day_data = hist[hist['Date'] == date]
            
            if len(day_data) < 30:  # Need at least 30 minutes
                continue
            
            # Get previous day's close
            prev_date = hist['Date'].unique()[i-1]
            prev_day = hist[hist['Date'] == prev_date]
            prev_close = prev_day.iloc[-1]['Close'] if not prev_day.empty else None
            
            if prev_close is None:
                continue
            
            try:
                # Current day analysis
                open_price = day_data.iloc[0]['Open']
                high_day = day_data['High'].max()
                low_day = day_data['Low'].min()
                close_price = day_data.iloc[-1]['Close']
                
                # Gap calculation
                gap_pct = ((open_price - prev_close) / prev_close * 100)
                
                # Find when low/high occurred
                low_idx = day_data['Low'].idxmin()
                high_idx = day_data['High'].idxmax()
                
                low_time = low_idx.strftime('%H:%M') if hasattr(low_idx, 'strftime') else 'N/A'
                high_time = high_idx.strftime('%H:%M') if hasattr(high_idx, 'strftime') else 'N/A'
                
                # Get first 30 min low (the "dip")
                first_30min = day_data.iloc[:30]
                dip_price = first_30min['Low'].min() if not first_30min.empty else low_day
                dip_pct_from_open = ((dip_price - open_price) / open_price * 100)
                
                # Did it recover?
                recovery_from_dip = ((close_price - dip_price) / dip_price * 100)
                recovery_from_open = ((close_price - open_price) / open_price * 100)
                
                # Pattern classification
                if gap_pct < -1:
                    pattern_type = "GAP_DOWN"
                elif gap_pct > 1:
                    pattern_type = "GAP_UP"
                else:
                    pattern_type = "FLAT"
                
                # Did dip offer better entry than open?
                dip_advantage = (dip_pct_from_open < -0.5)  # At least 0.5% dip
                
                pattern = {
                    'date': str(date),
                    'pattern_type': pattern_type,
                    'prev_close': round(prev_close, 2),
                    'open': round(open_price, 2),
                    'gap_pct': round(gap_pct, 2),
                    'dip_price': round(dip_price, 2),
                    'dip_time': low_time,
                    'dip_from_open_pct': round(dip_pct_from_open, 2),
                    'close': round(close_price, 2),
                    'recovery_from_dip_pct': round(recovery_from_dip, 2),
                    'recovery_from_open_pct': round(recovery_from_open, 2),
                    'dip_advantage': dip_advantage,
                    'high_time': high_time
                }
                
                results['patterns'].append(pattern)
                
            except Exception as e:
                print(f"   ⚠️ Error processing {date}: {e}")
                continue
        
        return results
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def analyze_results(results):
    """Analyze patterns to answer Tyr's question: Should I wait for the dip?"""
    
    if not results or not results.get('patterns'):
        print("   ❌ No patterns to analyze")
        return
    
    patterns = results['patterns']
    ticker = results['ticker']
    
    print(f"\n📊 GAP DIP RECOVERY ANALYSIS: {ticker}")
    print(f"   Days analyzed: {len(patterns)}")
    print("=" * 60)
    
    # Separate by pattern type
    gap_downs = [p for p in patterns if p['pattern_type'] == 'GAP_DOWN']
    gap_ups = [p for p in patterns if p['pattern_type'] == 'GAP_UP']
    flats = [p for p in patterns if p['pattern_type'] == 'FLAT']
    
    print(f"\n📈 PATTERN BREAKDOWN:")
    print(f"   Gap Down: {len(gap_downs)} days ({len(gap_downs)/len(patterns)*100:.1f}%)")
    print(f"   Gap Up: {len(gap_ups)} days ({len(gap_ups)/len(patterns)*100:.1f}%)")
    print(f"   Flat: {len(flats)} days ({len(flats)/len(patterns)*100:.1f}%)")
    
    # Analyze gap downs (Tyr's pattern)
    if gap_downs:
        print(f"\n🔻 GAP DOWN PATTERN (TYR'S QUESTION):")
        print(f"   Total gap downs: {len(gap_downs)}")
        
        # How many recovered?
        recovered = [p for p in gap_downs if p['recovery_from_dip_pct'] > 0]
        print(f"   Recovered from dip: {len(recovered)}/{len(gap_downs)} ({len(recovered)/len(gap_downs)*100:.1f}%)")
        
        # Average dip from open
        avg_dip = sum(p['dip_from_open_pct'] for p in gap_downs) / len(gap_downs)
        print(f"   Average dip from open: {avg_dip:.2f}%")
        
        # Average recovery
        avg_recovery = sum(p['recovery_from_dip_pct'] for p in recovered) / len(recovered) if recovered else 0
        print(f"   Average recovery from dip: {avg_recovery:.2f}%")
        
        # When is the dip?
        dip_times = [p['dip_time'] for p in gap_downs if p['dip_time'] != 'N/A']
        early_dips = sum(1 for t in dip_times if t < '10:00')
        print(f"   Dip before 10 AM: {early_dips}/{len(dip_times)} ({early_dips/len(dip_times)*100:.1f}%)")
        
        # Dip advantage
        dip_advantage_count = sum(1 for p in gap_downs if p['dip_advantage'])
        print(f"   Dip offered better entry: {dip_advantage_count}/{len(gap_downs)} ({dip_advantage_count/len(gap_downs)*100:.1f}%)")
    
    # Analyze gap ups (for pullback entry)
    if gap_ups:
        print(f"\n🔺 GAP UP PATTERN:")
        print(f"   Total gap ups: {len(gap_ups)}")
        
        # How many had pullback opportunity?
        pullbacks = [p for p in gap_ups if p['dip_from_open_pct'] < -0.5]
        print(f"   Had pullback >0.5%: {len(pullbacks)}/{len(gap_ups)} ({len(pullbacks)/len(gap_ups)*100:.1f}%)")
        
        if pullbacks:
            avg_pullback = sum(p['dip_from_open_pct'] for p in pullbacks) / len(pullbacks)
            print(f"   Average pullback: {avg_pullback:.2f}%")
    
    # The VERDICT
    print(f"\n🐺 WOLF'S VERDICT FOR {ticker}:")
    
    if gap_downs:
        recovery_rate = len(recovered)/len(gap_downs)*100
        
        if recovery_rate > 70 and avg_dip < -1:
            print(f"   ✅ TYR IS RIGHT - Wait for dip on gap downs")
            print(f"   • {recovery_rate:.0f}% of gap downs RECOVER")
            print(f"   • Average dip: {avg_dip:.2f}% from open")
            print(f"   • Strategy: If gaps down, WAIT for dip then BUY")
        elif gap_downs and not recovered:
            print(f"   ⚠️ WARNING - Gap downs DON'T recover")
            print(f"   • Only {recovery_rate:.0f}% recover")
            print(f"   • Strategy: AVOID on gap downs OR buy at EOD")
        else:
            print(f"   🤔 MIXED - Gap downs sometimes recover")
            print(f"   • {recovery_rate:.0f}% recovery rate")
            print(f"   • Strategy: Use scanner confirmation")
    
    # Show recent examples
    print(f"\n📅 RECENT EXAMPLES:")
    print(f"{'DATE':<12} {'PATTERN':<10} {'GAP%':<8} {'DIP%':<8} {'RECOVERY%':<10} {'DIP TIME':<10}")
    print("-" * 70)
    
    for p in patterns[-10:]:
        print(f"{p['date']:<12} {p['pattern_type']:<10} {p['gap_pct']:>6.2f}% {p['dip_from_open_pct']:>6.2f}% {p['recovery_from_dip_pct']:>8.2f}% {p['dip_time']:<10}")
    
    return {
        'gap_down_recovery_rate': len(recovered)/len(gap_downs)*100 if gap_downs else 0,
        'avg_dip_pct': avg_dip if gap_downs else 0,
        'dip_advantage_rate': dip_advantage_count/len(gap_downs)*100 if gap_downs else 0
    }

def main():
    parser = argparse.ArgumentParser(description='🐺 Gap Dip Recovery Analyzer - Find optimal entry timing')
    parser.add_argument('--ticker', type=str, default='QUBT', help='Ticker to analyze')
    parser.add_argument('--days', type=int, default=10, help='Days to look back')
    parser.add_argument('--compare', type=str, nargs='+', help='Compare multiple tickers')
    
    args = parser.parse_args()
    
    print(f"\n🐺 GAP DIP RECOVERY ANALYZER")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Question: Should I wait for the dip?")
    print("=" * 60)
    
    if args.compare:
        # Compare multiple tickers
        print(f"\n🔍 COMPARING GAP PATTERNS")
        print(f"   Tickers: {', '.join(args.compare)}")
        
        comparison = {}
        for ticker in args.compare:
            results = analyze_gap_dip_recovery(ticker, args.days)
            if results:
                stats = analyze_results(results)
                if stats:
                    comparison[ticker] = stats
        
        # Summary
        if comparison:
            print(f"\n📊 COMPARISON SUMMARY:")
            print(f"{'TICKER':<8} {'RECOVERY%':<12} {'AVG DIP%':<12} {'DIP ADVANTAGE%':<15}")
            print("-" * 50)
            for ticker, stats in comparison.items():
                print(f"{ticker:<8} {stats['gap_down_recovery_rate']:>9.1f}% {stats['avg_dip_pct']:>9.2f}% {stats['dip_advantage_rate']:>12.1f}%")
    
    else:
        # Single ticker
        results = analyze_gap_dip_recovery(args.ticker, args.days)
        if results:
            analyze_results(results)
            
            # Save
            log_dir = Path(__file__).parent.parent / 'logs'
            log_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
            output_file = log_dir / f'gap_dip_recovery_{args.ticker}_{timestamp}.json'
            
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n💾 Results saved to: {output_file}")
    
    print(f"\n🐺 AWOOOO! Analysis complete.\n")

if __name__ == '__main__':
    main()
