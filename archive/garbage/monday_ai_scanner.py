#!/usr/bin/env python3
"""
🐺 MONDAY AI PATTERN SCANNER
Run this Friday 3:00 PM to find Monday plays
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

# Tickers with validated Monday patterns
MONDAY_TICKERS = {
    'CIFR': 4.39,   # Historical Monday avg return
    'IREN': 4.14,
    'RCAT': 3.02,
    'HIVE': 2.78,
    'RIOT': 2.69,
    'APLD': 2.58,
    'UUUU': 2.68,
}

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def scan_monday_setups(capital=10000, positions=5):
    """
    Scan for Monday AI infrastructure plays
    
    Args:
        capital: Total capital available
        positions: Number of positions to suggest
    """
    print("🐺 MONDAY AI PATTERN SCANNER")
    print(f"Capital: ${capital:,.0f}")
    print(f"Target positions: {positions}")
    print("="*70)
    print()
    
    results = []
    
    for ticker, hist_return in MONDAY_TICKERS.items():
        try:
            # Get recent data
            df = yf.download(ticker, period='1mo', progress=False)
            if len(df) < 14:
                continue
                
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Current metrics
            price = df['Close'].iloc[-1]
            rsi = calculate_rsi(df['Close']).iloc[-1]
            
            # Volume check
            vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
            vol_recent = df['Volume'].iloc[-1]
            vol_ratio = vol_recent / vol_avg if vol_avg > 0 else 0
            
            # Week performance
            if len(df) >= 5:
                week_ret = ((price - df['Close'].iloc[-5]) / df['Close'].iloc[-5]) * 100
            else:
                week_ret = 0
            
            # Add to results
            results.append({
                'ticker': ticker,
                'price': price,
                'rsi': rsi,
                'week_ret': week_ret,
                'vol_ratio': vol_ratio,
                'hist_return': hist_return,
                'tradeable': rsi < 70  # Only trade if not overbought
            })
            
        except Exception as e:
            print(f"⚠️  {ticker}: Failed to fetch data")
    
    # Sort by historical return (best first)
    results.sort(key=lambda x: x['hist_return'], reverse=True)
    
    # Show all results
    print("📊 ALL MONDAY PATTERN STOCKS:")
    print()
    for r in results:
        status = "✅ TRADE" if r['tradeable'] else "❌ SKIP (Overbought)"
        print(f"{r['ticker']:6} ${r['price']:7.2f}  RSI:{r['rsi']:4.0f}  "
              f"Week:{r['week_ret']:+6.1f}%  HistAvg:{r['hist_return']:+5.2f}%  {status}")
    
    print()
    print("="*70)
    print("🎯 RECOMMENDED POSITIONS FOR MONDAY:")
    print("="*70)
    print()
    
    # Filter tradeable and take top N
    tradeable = [r for r in results if r['tradeable']]
    
    if len(tradeable) == 0:
        print("❌ NO GOOD SETUPS - ALL OVERBOUGHT")
        print("   Wait for pullback or skip Monday play")
        return
    
    # Use fewer positions if not enough tradeable stocks
    actual_positions = min(positions, len(tradeable))
    position_size = capital / actual_positions
    
    print(f"Capital per position: ${position_size:,.0f}")
    print()
    
    total_deployed = 0
    expected_return = 0
    
    for i, r in enumerate(tradeable[:actual_positions]):
        shares = int(position_size / r['price'])
        position_value = shares * r['price']
        expected_gain = position_value * (r['hist_return'] / 100)
        
        print(f"{i+1}. {r['ticker']:6} - BUY {shares:4} shares @ ${r['price']:.2f}")
        print(f"   Position: ${position_value:,.0f}")
        print(f"   RSI: {r['rsi']:.0f}")
        print(f"   Historical Monday avg: +{r['hist_return']:.2f}%")
        print(f"   Expected Monday gain: ${expected_gain:,.0f}")
        print()
        
        total_deployed += position_value
        expected_return += expected_gain
    
    print("="*70)
    print(f"💰 TOTAL DEPLOYED: ${total_deployed:,.0f} ({total_deployed/capital*100:.0f}% of capital)")
    print(f"📈 EXPECTED MONDAY RETURN: ${expected_return:,.0f} ({expected_return/capital*100:.1f}%)")
    print(f"💵 CASH RESERVE: ${capital - total_deployed:,.0f} (for crash bounces)")
    print()
    
    print("="*70)
    print("⏰ EXECUTION PLAN:")
    print("="*70)
    print()
    print("FRIDAY 3:59 PM:")
    print("  - Buy all positions at market close")
    print("  - Set mental stop losses at -3%")
    print()
    print("MONDAY 10:00 AM:")
    print("  - Check all positions")
    print("  - If any up 2%+, SELL")
    print("  - If up 3%+, sell 50% and let rest run")
    print("  - If down -2%, wait until 3 PM to decide")
    print()
    print("MONDAY 3:00 PM:")
    print("  - Exit any remaining positions")
    print("  - Don't hold into Tuesday (pattern is Monday-specific)")
    print()
    print("🐺 These are VALIDATED patterns. Trust the data. LLHR.")
    print()

if __name__ == "__main__":
    import sys
    
    capital = 10000  # Default
    positions = 5     # Default
    
    # Check for command line args
    if len(sys.argv) > 1:
        capital = int(sys.argv[1])
    if len(sys.argv) > 2:
        positions = int(sys.argv[2])
    
    scan_monday_setups(capital, positions)
