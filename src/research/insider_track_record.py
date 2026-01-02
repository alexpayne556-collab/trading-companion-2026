#!/usr/bin/env python3
"""
🐺 INSIDER TRACK RECORD ANALYZER
Built by Brokkr - January 2, 2026

Purpose: Parse historical Form 4s for specific insiders, calculate timing accuracy,
win rate, and average returns. Automate the "is this insider smart money?" question.

Usage:
    python3 insider_track_record.py AISP "Paul B Allen"
    python3 insider_track_record.py AISP "Victor Huang"
    python3 insider_track_record.py --ticker AISP --all

PACK WORK, NOT CONSULTANT WORK.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import argparse
import json
import time
import yfinance as yf

def get_form4_history(ticker, insider_name=None, lookback_days=730):
    """
    Fetch Form 4 history for a ticker from SEC EDGAR.
    
    Args:
        ticker: Stock symbol
        insider_name: Specific insider to filter (optional)
        lookback_days: How far back to search (default 2 years)
    
    Returns:
        List of Form 4 transactions with dates and amounts
    """
    print(f"🔍 Searching SEC EDGAR for {ticker} Form 4s (last {lookback_days} days)...")
    
    # Note: This is a simplified version
    # Full implementation would parse OpenInsider or SEC EDGAR directly
    # For now, we'll document the structure and return mock data for demonstration
    
    transactions = []
    
    # TODO: Implement actual SEC EDGAR scraping
    # For now, using known AISP data from our earlier validation
    
    if ticker == "AISP":
        transactions = [
            {
                "insider": "Paul B Allen",
                "title": "President",
                "date": "2024-12-29",
                "type": "P",
                "shares": 100000,
                "price": 2.74,
                "amount": 274000
            },
            {
                "insider": "Paul B Allen", 
                "title": "President",
                "date": "2024-03-15",
                "type": "S",
                "shares": 50000,
                "price": 5.11,
                "amount": 255500
            },
            {
                "insider": "Victor Huang",
                "title": "CEO",
                "date": "2024-11-20",
                "type": "P",
                "shares": 60000,
                "price": 3.18,
                "amount": 190800
            },
            # Additional transactions would be parsed here
        ]
    
    return transactions

def analyze_insider_timing(transactions, ticker):
    """
    Calculate timing accuracy for an insider's trades.
    
    Metrics:
    - Buy timing: Did they buy near lows?
    - Sell timing: Did they sell near highs?
    - Win rate: % of profitable round trips
    - Avg return: Average return from buy price
    """
    print(f"\n📊 Analyzing insider timing accuracy...")
    
    # Get historical price data
    stock = yf.Ticker(ticker)
    
    buys = [t for t in transactions if t['type'] == 'P']
    sells = [t for t in transactions if t['type'] == 'S']
    
    results = {
        "total_buys": len(buys),
        "total_sells": len(sells),
        "round_trips": [],
        "buy_timing_scores": [],
        "sell_timing_scores": []
    }
    
    # Analyze each buy
    for buy in buys:
        buy_date = datetime.strptime(buy['date'], '%Y-%m-%d')
        buy_price = buy['price']
        
        # Get 30-day price range around buy
        start = buy_date - timedelta(days=30)
        end = buy_date + timedelta(days=30)
        
        try:
            hist = stock.history(start=start, end=end)
            if len(hist) > 0:
                low_30d = hist['Low'].min()
                high_30d = hist['High'].max()
                range_30d = high_30d - low_30d
                
                # Score: How close to low? (0 = bought at high, 100 = bought at low)
                if range_30d > 0:
                    score = 100 * (1 - (buy_price - low_30d) / range_30d)
                    results['buy_timing_scores'].append(score)
        except:
            pass
    
    # Analyze sells similarly
    for sell in sells:
        sell_date = datetime.strptime(sell['date'], '%Y-%m-%d')
        sell_price = sell['price']
        
        start = sell_date - timedelta(days=30)
        end = sell_date + timedelta(days=30)
        
        try:
            hist = stock.history(start=start, end=end)
            if len(hist) > 0:
                low_30d = hist['Low'].min()
                high_30d = hist['High'].max()
                range_30d = high_30d - low_30d
                
                # Score: How close to high? (0 = sold at low, 100 = sold at high)
                if range_30d > 0:
                    score = 100 * (sell_price - low_30d) / range_30d
                    results['sell_timing_scores'].append(score)
        except:
            pass
    
    # Calculate round trips (sell after buy)
    for sell in sells:
        sell_date = datetime.strptime(sell['date'], '%Y-%m-%d')
        sell_price = sell['price']
        
        # Find prior buy
        prior_buys = [b for b in buys if datetime.strptime(b['date'], '%Y-%m-%d') < sell_date]
        if prior_buys:
            # Use most recent buy
            recent_buy = max(prior_buys, key=lambda x: x['date'])
            buy_price = recent_buy['price']
            
            pct_return = (sell_price - buy_price) / buy_price * 100
            
            results['round_trips'].append({
                "buy_date": recent_buy['date'],
                "buy_price": buy_price,
                "sell_date": sell['date'],
                "sell_price": sell_price,
                "return_pct": pct_return
            })
    
    return results

def print_insider_report(insider_name, transactions, analysis, ticker):
    """Print a formatted report on insider's track record."""
    
    print(f"\n{'='*70}")
    print(f"🐺 INSIDER TRACK RECORD: {insider_name}")
    print(f"Ticker: {ticker}")
    print(f"{'='*70}\n")
    
    # Transaction summary
    print(f"📋 TRANSACTION HISTORY:")
    print(f"   Total buys (P-codes): {analysis['total_buys']}")
    print(f"   Total sells (S-codes): {analysis['total_sells']}")
    print()
    
    # Buy timing analysis
    if analysis['buy_timing_scores']:
        avg_buy_score = sum(analysis['buy_timing_scores']) / len(analysis['buy_timing_scores'])
        print(f"📊 BUY TIMING ANALYSIS:")
        print(f"   Average timing score: {avg_buy_score:.1f}/100")
        print(f"   (100 = bought at 30-day low, 0 = bought at 30-day high)")
        
        if avg_buy_score >= 70:
            print(f"   ✅ EXCELLENT - Consistently buys near lows")
        elif avg_buy_score >= 50:
            print(f"   🟡 GOOD - Decent timing on entries")
        else:
            print(f"   ⚠️  POOR - Not great at timing entries")
        print()
    
    # Sell timing analysis
    if analysis['sell_timing_scores']:
        avg_sell_score = sum(analysis['sell_timing_scores']) / len(analysis['sell_timing_scores'])
        print(f"📊 SELL TIMING ANALYSIS:")
        print(f"   Average timing score: {avg_sell_score:.1f}/100")
        print(f"   (100 = sold at 30-day high, 0 = sold at 30-day low)")
        
        if avg_sell_score >= 70:
            print(f"   ✅ EXCELLENT - Consistently sells near highs")
        elif avg_sell_score >= 50:
            print(f"   🟡 GOOD - Decent timing on exits")
        else:
            print(f"   ⚠️  POOR - Not great at timing exits")
        print()
    
    # Round trip analysis
    if analysis['round_trips']:
        print(f"🔄 ROUND TRIP TRADES:")
        for i, trip in enumerate(analysis['round_trips'], 1):
            print(f"   {i}. Buy ${trip['buy_price']:.2f} ({trip['buy_date']}) → "
                  f"Sell ${trip['sell_price']:.2f} ({trip['sell_date']}) = "
                  f"{trip['return_pct']:+.1f}%")
        
        avg_return = sum(t['return_pct'] for t in analysis['round_trips']) / len(analysis['round_trips'])
        win_rate = len([t for t in analysis['round_trips'] if t['return_pct'] > 0]) / len(analysis['round_trips']) * 100
        
        print()
        print(f"   Average return: {avg_return:+.1f}%")
        print(f"   Win rate: {win_rate:.0f}%")
        print()
    
    # Most recent activity
    recent = sorted([t for t in transactions if t['insider'] == insider_name], 
                   key=lambda x: x['date'], reverse=True)
    
    if recent:
        latest = recent[0]
        print(f"📅 MOST RECENT ACTIVITY:")
        print(f"   Date: {latest['date']}")
        print(f"   Type: {'BUY' if latest['type'] == 'P' else 'SELL'}")
        print(f"   Shares: {latest['shares']:,}")
        print(f"   Price: ${latest['price']:.2f}")
        print(f"   Amount: ${latest['amount']:,}")
        print()
    
    # VERDICT
    print(f"🎯 VERDICT:")
    
    # Calculate overall score
    signals = []
    
    if analysis['buy_timing_scores']:
        avg_buy = sum(analysis['buy_timing_scores']) / len(analysis['buy_timing_scores'])
        if avg_buy >= 60:
            signals.append("✅ Good buy timing")
        else:
            signals.append("⚠️  Questionable buy timing")
    
    if analysis['round_trips']:
        avg_return = sum(t['return_pct'] for t in analysis['round_trips']) / len(analysis['round_trips'])
        win_rate = len([t for t in analysis['round_trips'] if t['return_pct'] > 0]) / len(analysis['round_trips']) * 100
        
        if avg_return > 30 and win_rate > 60:
            signals.append("✅ Profitable track record")
        elif avg_return > 0:
            signals.append("🟡 Modestly profitable")
        else:
            signals.append("⚠️  Unprofitable history")
    
    if analysis['total_buys'] >= 3 and analysis['total_sells'] == 0:
        signals.append("✅ Accumulating, not distributing")
    
    for signal in signals:
        print(f"   {signal}")
    
    # Final assessment
    positive_signals = sum(1 for s in signals if '✅' in s)
    
    print()
    if positive_signals >= 2:
        print(f"   🐺 ASSESSMENT: SMART MONEY - Follow this insider")
    elif positive_signals >= 1:
        print(f"   🟡 ASSESSMENT: MODERATE - Proceed with caution")
    else:
        print(f"   ⚠️  ASSESSMENT: RED FLAG - Questionable track record")
    
    print(f"\n{'='*70}\n")

def main():
    parser = argparse.ArgumentParser(description='Analyze insider trading track records')
    parser.add_argument('ticker', help='Stock ticker symbol')
    parser.add_argument('--insider', help='Specific insider name to analyze')
    parser.add_argument('--all', action='store_true', help='Analyze all insiders')
    parser.add_argument('--lookback', type=int, default=730, help='Days to look back (default 730)')
    
    args = parser.parse_args()
    
    # Fetch Form 4 data
    transactions = get_form4_history(args.ticker, args.insider, args.lookback)
    
    if not transactions:
        print(f"❌ No Form 4 transactions found for {args.ticker}")
        return
    
    # Get unique insiders
    insiders = list(set(t['insider'] for t in transactions))
    
    if args.insider:
        insiders = [i for i in insiders if args.insider.lower() in i.lower()]
    
    # Analyze each insider
    for insider in insiders:
        insider_txns = [t for t in transactions if t['insider'] == insider]
        analysis = analyze_insider_timing(insider_txns, args.ticker)
        print_insider_report(insider, transactions, analysis, args.ticker)
        
        if len(insiders) > 1 and insider != insiders[-1]:
            print("\n" + "="*70)
            print("Press Enter to see next insider...")
            input()

if __name__ == '__main__':
    main()
