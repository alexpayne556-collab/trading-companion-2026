#!/usr/bin/env python3
"""
🐺 MAX PAIN CALCULATOR - Where Options Expire Worthless
========================================================

FENRIR'S SECRET:
- Every Friday, stocks tend to close near "max pain"
- Max pain = price where most options expire worthless
- Market makers push price there to keep premium
- Check options pain calculators before Friday trades

THE EDGE:
- Know where the stock "wants" to close on Friday
- If price is far from max pain, expect movement toward it
- If you're holding through Friday, factor this in

USAGE:
    python max_pain_calculator.py --ticker USAR           # Calculate max pain
    python max_pain_calculator.py --ticker UUUU --expiry 2026-01-10
"""

import argparse
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd


def get_options_chain(ticker: str, expiry_date: str = None) -> dict:
    """
    Get options chain for a ticker.
    Returns calls and puts DataFrames.
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get available expiration dates
        expirations = stock.options
        
        if not expirations:
            print(f"  ⚠️  No options available for {ticker}")
            return None
        
        # Use provided expiry or nearest Friday
        if expiry_date:
            if expiry_date in expirations:
                target_expiry = expiry_date
            else:
                print(f"  ⚠️  Expiry {expiry_date} not available")
                print(f"  Available: {expirations[:5]}")
                target_expiry = expirations[0]
        else:
            target_expiry = expirations[0]  # Nearest expiry
        
        # Get the options chain
        opt = stock.option_chain(target_expiry)
        
        return {
            "ticker": ticker,
            "expiry": target_expiry,
            "calls": opt.calls,
            "puts": opt.puts,
            "current_price": stock.info.get('currentPrice') or stock.info.get('regularMarketPrice', 0),
        }
        
    except Exception as e:
        print(f"  ⚠️  Error fetching options for {ticker}: {e}")
        return None


def calculate_max_pain(options_data: dict) -> dict:
    """
    Calculate max pain - the price where most options expire worthless.
    
    Max pain is calculated by:
    1. For each strike price, calculate total value of ITM calls + puts
    2. The strike with minimum total ITM value = max pain
    
    This is where market makers lose the least / retail loses the most.
    """
    if not options_data:
        return None
    
    calls = options_data['calls']
    puts = options_data['puts']
    current_price = options_data['current_price']
    
    # Get all unique strikes
    call_strikes = set(calls['strike'].tolist())
    put_strikes = set(puts['strike'].tolist())
    all_strikes = sorted(call_strikes.union(put_strikes))
    
    if not all_strikes:
        return None
    
    # Calculate pain at each strike
    pain_data = []
    
    for strike in all_strikes:
        call_pain = 0
        put_pain = 0
        
        # Call pain: sum of (strike - current) * OI for all strikes BELOW current
        for _, row in calls.iterrows():
            if row['strike'] < strike:
                # This call is ITM if stock closes at 'strike'
                call_pain += (strike - row['strike']) * row['openInterest'] * 100
        
        # Put pain: sum of (current - strike) * OI for all strikes ABOVE current  
        for _, row in puts.iterrows():
            if row['strike'] > strike:
                # This put is ITM if stock closes at 'strike'
                put_pain += (row['strike'] - strike) * row['openInterest'] * 100
        
        total_pain = call_pain + put_pain
        pain_data.append({
            'strike': strike,
            'call_pain': call_pain,
            'put_pain': put_pain,
            'total_pain': total_pain,
        })
    
    # Find max pain (minimum total pain for MMs)
    pain_df = pd.DataFrame(pain_data)
    min_pain_idx = pain_df['total_pain'].idxmin()
    max_pain_strike = pain_df.loc[min_pain_idx, 'strike']
    
    # Calculate distance from current price
    distance = ((max_pain_strike - current_price) / current_price) * 100
    
    # Find highest OI strikes
    call_max_oi = calls.loc[calls['openInterest'].idxmax()] if not calls.empty else None
    put_max_oi = puts.loc[puts['openInterest'].idxmax()] if not puts.empty else None
    
    return {
        "ticker": options_data['ticker'],
        "expiry": options_data['expiry'],
        "current_price": current_price,
        "max_pain": max_pain_strike,
        "distance_pct": round(distance, 2),
        "call_max_oi_strike": call_max_oi['strike'] if call_max_oi is not None else None,
        "call_max_oi": int(call_max_oi['openInterest']) if call_max_oi is not None else 0,
        "put_max_oi_strike": put_max_oi['strike'] if put_max_oi is not None else None,
        "put_max_oi": int(put_max_oi['openInterest']) if put_max_oi is not None else 0,
        "pain_data": pain_df,
    }


def analyze_max_pain(ticker: str, expiry: str = None):
    """
    Full max pain analysis for a ticker.
    """
    print(f"\n{'='*60}")
    print(f"🎯 MAX PAIN ANALYSIS: {ticker}")
    print(f"{'='*60}")
    
    # Get options data
    options = get_options_chain(ticker, expiry)
    if not options:
        return None
    
    # Calculate max pain
    result = calculate_max_pain(options)
    if not result:
        print("  ⚠️  Could not calculate max pain")
        return None
    
    print(f"\nExpiration: {result['expiry']}")
    print(f"Current Price: ${result['current_price']:.2f}")
    print(f"\n{'─'*60}")
    print(f"📍 MAX PAIN: ${result['max_pain']:.2f}")
    print(f"{'─'*60}")
    
    # Direction analysis
    if result['distance_pct'] > 5:
        direction = "⬇️ BELOW max pain"
        expectation = "Price may drift UP toward max pain"
    elif result['distance_pct'] < -5:
        direction = "⬆️ ABOVE max pain"
        expectation = "Price may drift DOWN toward max pain"
    else:
        direction = "✅ NEAR max pain"
        expectation = "Price likely to stay range-bound"
    
    print(f"\nCurrent vs Max Pain: {result['distance_pct']:+.2f}%")
    print(f"Status: {direction}")
    print(f"Expectation: {expectation}")
    
    # Key strikes
    print(f"\n📊 KEY OPEN INTEREST:")
    print(f"   Highest Call OI: ${result['call_max_oi_strike']:.2f} ({result['call_max_oi']:,} contracts)")
    print(f"   Highest Put OI: ${result['put_max_oi_strike']:.2f} ({result['put_max_oi']:,} contracts)")
    
    # Call/Put ratio analysis
    total_call_oi = options['calls']['openInterest'].sum()
    total_put_oi = options['puts']['openInterest'].sum()
    pc_ratio = total_put_oi / total_call_oi if total_call_oi > 0 else 0
    
    print(f"\n📊 SENTIMENT:")
    print(f"   Total Call OI: {total_call_oi:,}")
    print(f"   Total Put OI: {total_put_oi:,}")
    print(f"   Put/Call Ratio: {pc_ratio:.2f}")
    
    if pc_ratio > 1.5:
        print(f"   🐻 BEARISH sentiment (high put OI)")
    elif pc_ratio < 0.7:
        print(f"   🐂 BULLISH sentiment (high call OI)")
    else:
        print(f"   ⚖️ NEUTRAL sentiment")
    
    # Friday trading recommendation
    print(f"\n{'─'*60}")
    print(f"📅 FRIDAY TRADING IMPLICATIONS:")
    print(f"{'─'*60}")
    
    if abs(result['distance_pct']) > 10:
        print(f"   ⚠️  Price is {abs(result['distance_pct']):.1f}% from max pain")
        print(f"   ⚠️  Expect volatility as price gravitates toward ${result['max_pain']:.2f}")
        print(f"   💡 Consider closing positions before Friday if holding")
    elif abs(result['distance_pct']) > 5:
        print(f"   👀 Price is {abs(result['distance_pct']):.1f}% from max pain")
        print(f"   📊 Some gravitational pull toward ${result['max_pain']:.2f}")
    else:
        print(f"   ✅ Price is near max pain")
        print(f"   📊 Likely to stay range-bound through expiration")
    
    return result


def main():
    parser = argparse.ArgumentParser(description="🐺 Max Pain Calculator")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker to analyze")
    parser.add_argument("--expiry", type=str, help="Expiration date (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    analyze_max_pain(args.ticker.upper(), args.expiry)
    
    print(f"\n{'🐺'*30}")
    print("      FENRIR'S MAX PAIN TRUTH")
    print(f"{'🐺'*30}")
    print("\n💡 Max pain works best:")
    print("   • On high-volume options stocks")
    print("   • During weekly expiration (Friday)")
    print("   • When there's no major catalyst")
    print("\n⚠️  Max pain can be overridden by:")
    print("   • Major news/catalyst")
    print("   • Extreme momentum")
    print("   • Low options volume")
    print("\n🐺 AWOOOO!")


if __name__ == "__main__":
    main()
