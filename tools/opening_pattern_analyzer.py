#!/usr/bin/env python3
"""
🐺 OPENING PATTERN ANALYZER
Shows you EXACTLY when big money takes profits vs when retail gets trapped.

This tool analyzes the first hour of trading to identify:
- Opening gaps (9:30 AM)
- Profit-taking pullbacks (9:35-9:50 AM)
- Dead cat bounces (retail FOMO)
- Institutional re-entry (10:00-10:30 AM)

NO MORE GUESSING. LET'S SEE THE PATTERN.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import argparse
import json
from pathlib import Path

def analyze_opening_pattern(ticker, days_back=5):
    """
    Analyze opening hour patterns to see when profit-taking happens.
    
    Args:
        ticker: Stock symbol
        days_back: How many days to analyze
    
    Returns:
        dict with pattern analysis
    """
    print(f"\n🔍 ANALYZING OPENING PATTERN: {ticker}")
    print(f"   Looking back {days_back} days")
    print("=" * 60)
    
    try:
        # Get 1-minute intraday data for last N days
        stock = yf.Ticker(ticker)
        
        # Get data for analysis period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Use 1-minute intervals for precise timing
        hist = stock.history(start=start_date, end=end_date, interval='1m')
        
        if hist.empty:
            print(f"   ⚠️ No data available for {ticker}")
            return None
        
        results = {
            'ticker': ticker,
            'days_analyzed': days_back,
            'patterns': []
        }
        
        # Group by date
        hist['Date'] = hist.index.date
        
        for date in hist['Date'].unique():
            day_data = hist[hist['Date'] == date]
            
            if len(day_data) < 30:  # Need at least 30 minutes of data
                continue
            
            # Get key timeframes (market opens 9:30 AM)
            try:
                # 9:30 AM - Opening price
                open_930 = day_data.iloc[0]['Open']
                
                # 9:35 AM - 5 minutes in (check for pullback)
                data_935 = day_data.iloc[5:6] if len(day_data) > 5 else None
                price_935 = data_935['Close'].values[0] if data_935 is not None and not data_935.empty else None
                
                # 9:45 AM - 15 minutes in (early FOMO or consolidation)
                data_945 = day_data.iloc[15:16] if len(day_data) > 15 else None
                price_945 = data_945['Close'].values[0] if data_945 is not None and not data_945.empty else None
                
                # 10:00 AM - 30 minutes in (institutional re-entry?)
                data_1000 = day_data.iloc[30:31] if len(day_data) > 30 else None
                price_1000 = data_1000['Close'].values[0] if data_1000 is not None and not data_1000.empty else None
                
                # Get highs and lows for first hour
                high_first_hour = day_data.iloc[:60]['High'].max() if len(day_data) > 60 else day_data['High'].max()
                low_first_hour = day_data.iloc[:60]['Low'].min() if len(day_data) > 60 else day_data['Low'].min()
                
                # When did high occur?
                high_time_idx = day_data.iloc[:60]['High'].idxmax() if len(day_data) > 60 else day_data['High'].idxmax()
                high_time = high_time_idx.strftime('%H:%M') if hasattr(high_time_idx, 'strftime') else 'N/A'
                
                # Calculate moves
                move_935 = ((price_935 - open_930) / open_930 * 100) if price_935 else None
                move_945 = ((price_945 - open_930) / open_930 * 100) if price_945 else None
                move_1000 = ((price_1000 - open_930) / open_930 * 100) if price_1000 else None
                
                pattern = {
                    'date': str(date),
                    'open_930': round(open_930, 2),
                    'price_935': round(price_935, 2) if price_935 else None,
                    'price_945': round(price_945, 2) if price_945 else None,
                    'price_1000': round(price_1000, 2) if price_1000 else None,
                    'move_935': round(move_935, 2) if move_935 else None,
                    'move_945': round(move_945, 2) if move_945 else None,
                    'move_1000': round(move_1000, 2) if move_1000 else None,
                    'first_hour_high': round(high_first_hour, 2),
                    'first_hour_low': round(low_first_hour, 2),
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

def analyze_patterns(results):
    """Analyze the patterns to find profit-taking tendencies."""
    
    if not results or not results.get('patterns'):
        print("   ❌ No patterns to analyze")
        return
    
    patterns = results['patterns']
    ticker = results['ticker']
    
    print(f"\n📊 OPENING PATTERN ANALYSIS: {ticker}")
    print(f"   Days analyzed: {len(patterns)}")
    print("=" * 60)
    
    # Count how often price drops by 9:35 vs goes up
    drops_935 = sum(1 for p in patterns if p['move_935'] and p['move_935'] < 0)
    rises_935 = sum(1 for p in patterns if p['move_935'] and p['move_935'] > 0)
    
    # Average moves
    avg_935 = sum(p['move_935'] for p in patterns if p['move_935']) / len([p for p in patterns if p['move_935']])
    avg_945 = sum(p['move_945'] for p in patterns if p['move_945']) / len([p for p in patterns if p['move_945']])
    avg_1000 = sum(p['move_1000'] for p in patterns if p['move_1000']) / len([p for p in patterns if p['move_1000']])
    
    # When does high occur?
    high_at_open = sum(1 for p in patterns if p['high_time'].startswith('09:3'))
    high_before_10 = sum(1 for p in patterns if p['high_time'] < '10:00')
    
    print(f"\n🎯 THE TRUTH ABOUT TIMING:")
    print(f"\n   BY 9:35 AM (5 minutes):")
    print(f"   • Drops: {drops_935}/{len(patterns)} days ({drops_935/len(patterns)*100:.1f}%)")
    print(f"   • Rises: {rises_935}/{len(patterns)} days ({rises_935/len(patterns)*100:.1f}%)")
    print(f"   • Average move: {avg_935:+.2f}%")
    
    print(f"\n   BY 9:45 AM (15 minutes):")
    print(f"   • Average move: {avg_945:+.2f}%")
    
    print(f"\n   BY 10:00 AM (30 minutes):")
    print(f"   • Average move: {avg_1000:+.2f}%")
    
    print(f"\n   WHEN IS THE HIGH?")
    print(f"   • At open (9:30-9:35): {high_at_open}/{len(patterns)} days ({high_at_open/len(patterns)*100:.1f}%)")
    print(f"   • Before 10 AM: {high_before_10}/{len(patterns)} days ({high_before_10/len(patterns)*100:.1f}%)")
    
    print(f"\n🐺 WOLF'S READ:")
    if drops_935 > rises_935:
        print(f"   • {ticker} tends to PULLBACK in first 5 minutes ({drops_935/len(patterns)*100:.1f}% of days)")
        print(f"   • ✅ WAIT for 9:35-9:45 AM entry is VALIDATED")
    else:
        print(f"   • {ticker} tends to RUN at open ({rises_935/len(patterns)*100:.1f}% of days)")
        print(f"   • ⚠️ This stock you might need to buy AT THE OPEN")
    
    if high_at_open/len(patterns) > 0.6:
        print(f"   • ⚠️ HIGH happens at OPEN {high_at_open/len(patterns)*100:.1f}% of time")
        print(f"   • If you wait, you WILL miss the move")
    
    # Show day-by-day
    print(f"\n📅 DAY-BY-DAY BREAKDOWN:")
    print(f"{'DATE':<12} {'OPEN':<8} {'9:35':<8} {'9:45':<8} {'10:00':<8} {'HIGH TIME':<10}")
    print("-" * 60)
    
    for p in patterns[-10:]:  # Show last 10 days
        print(f"{p['date']:<12} ${p['open_930']:<7.2f} {p['move_935']:+.2f}% {p['move_945']:+.2f}% {p['move_1000']:+.2f}% {p['high_time']:<10}")
    
    return {
        'drops_935_pct': drops_935/len(patterns)*100,
        'avg_935': avg_935,
        'avg_945': avg_945,
        'high_at_open_pct': high_at_open/len(patterns)*100
    }

def main():
    parser = argparse.ArgumentParser(description='🐺 Opening Pattern Analyzer - See when big money takes profits')
    parser.add_argument('--ticker', type=str, default='QUBT', help='Ticker to analyze')
    parser.add_argument('--days', type=int, default=5, help='Days to look back')
    parser.add_argument('--compare', type=str, nargs='+', help='Compare multiple tickers')
    
    args = parser.parse_args()
    
    print(f"\n🐺 OPENING PATTERN ANALYZER")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    if args.compare:
        # Compare multiple tickers
        print(f"\n🔍 COMPARING OPENING PATTERNS")
        print(f"   Tickers: {', '.join(args.compare)}")
        print(f"   Days back: {args.days}")
        
        comparison = {}
        for ticker in args.compare:
            results = analyze_opening_pattern(ticker, args.days)
            if results:
                stats = analyze_patterns(results)
                if stats:
                    comparison[ticker] = stats
        
        # Summary comparison
        if comparison:
            print(f"\n📊 COMPARISON SUMMARY:")
            print(f"{'TICKER':<8} {'DROPS@9:35':<12} {'AVG@9:35':<12} {'AVG@9:45':<12} {'HIGH@OPEN':<12}")
            print("-" * 60)
            for ticker, stats in comparison.items():
                print(f"{ticker:<8} {stats['drops_935_pct']:.1f}% {stats['avg_935']:+.2f}% {stats['avg_945']:+.2f}% {stats['high_at_open_pct']:.1f}%")
    
    else:
        # Single ticker
        results = analyze_opening_pattern(args.ticker, args.days)
        if results:
            analyze_patterns(results)
            
            # Save results
            log_dir = Path(__file__).parent.parent / 'logs'
            log_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
            output_file = log_dir / f'opening_pattern_{args.ticker}_{timestamp}.json'
            
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n💾 Results saved to: {output_file}")
    
    print(f"\n🐺 AWOOOO! Pattern analysis complete.\n")

if __name__ == '__main__':
    main()
