#!/usr/bin/env python3
"""
🐺 WOLF PRESSURE - Find Where The Explosion Will Happen
========================================================
This isn't prediction. This is PRESSURE IDENTIFICATION.

WHO IS FORCED TO BUY?
- Market makers MUST hedge when calls go ITM
- Shorts MUST cover when price spikes
- Institutions MUST get exposure when themes pop

We find WHERE the pressure is built.
The catalyst is just the SPARK.
The EXPLOSION was always going to happen.

AWOOOO 🐺
"""

import argparse
import yfinance as yf
from datetime import datetime
from typing import List, Dict, Optional


# Universe to scan
PRESSURE_UNIVERSE = [
    # Quantum (CES)
    'QBTS', 'QUBT', 'IONQ', 'RGTI',
    # Space/Defense  
    'RKLB', 'LUNR', 'RDW', 'RCAT',
    # Nuclear/Energy
    'SMR', 'NNE', 'LEU', 'OKLO',
    # AI/Tech
    'PLTR', 'WOLF', 'NVDA',
    # CES 2026 Plays
    'RR', 'SOUN',
]

# Historical Monday win rates after big Fridays
MONDAY_RATES = {
    'RKLB': 100,  # 5/5 Mondays up after big Friday
    'QBTS': 80,   # 4/5
    'OKLO': 80,   # 4/5
    'RR': 70,     # CES catalyst play
    'RCAT': 67,   # 4/6
    'LUNR': 67,   # 2/3
    'RDW': 67,    # 2/3
    'RGTI': 67,   # 2/3
    'IONQ': 60,   # 3/5
    'SOUN': 55,   # High short, low expectations
    'WOLF': 50,   # estimate
    'QUBT': 29,   # 2/7
    'NNE': 17,    # 1/6
    'LEU': 17,    # 1/6
    'SMR': 0,     # 0/4
    'PLTR': 50,   # estimate
    'NVDA': 55,   # estimate
}


def get_pressure_data(ticker: str) -> Optional[Dict]:
    """
    Get comprehensive pressure data for a ticker.
    Combines: gamma, short interest, Monday probability, accumulation signals
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='10d')
        info = stock.info
        
        if len(hist) < 5:
            return None
            
        current_price = hist['Close'].iloc[-1]
        
        # === FRIDAY DATA ===
        fri_close = hist['Close'].iloc[-1]
        fri_open = hist['Open'].iloc[-1]
        fri_vol = hist['Volume'].iloc[-1]
        fri_high = hist['High'].iloc[-1]
        fri_low = hist['Low'].iloc[-1]
        
        # Friday change
        if len(hist) >= 2:
            fri_change = (fri_close / hist['Close'].iloc[-2] - 1) * 100
        else:
            fri_change = 0
            
        # Average volume
        avg_vol = hist['Volume'].iloc[:-1].mean() if len(hist) > 1 else fri_vol
        vol_ratio = fri_vol / avg_vol if avg_vol > 0 else 1
        
        # Close position in range (accumulation signal)
        if fri_high != fri_low:
            close_position = ((fri_close - fri_low) / (fri_high - fri_low)) * 100
        else:
            close_position = 50
            
        # === SHORT INTEREST ===
        short_pct = info.get('shortPercentOfFloat', 0)
        if short_pct and short_pct < 1:
            short_pct = short_pct * 100
            
        # === OPTIONS GAMMA ===
        gamma_score = 0
        trigger_strike = 0
        distance_to_trigger = 0
        call_oi = 0
        
        try:
            exp_dates = stock.options
            if exp_dates:
                nearest_exp = exp_dates[0]
                chain = stock.option_chain(nearest_exp)
                calls = chain.calls
                
                # Find biggest call OI above price
                calls_above = calls[calls['strike'] > current_price]
                if len(calls_above) > 0:
                    biggest = calls_above.loc[calls_above['openInterest'].idxmax()]
                    trigger_strike = biggest['strike']
                    call_oi = int(biggest['openInterest'])
                    distance_to_trigger = ((trigger_strike - current_price) / current_price) * 100
                    
                    # Gamma score
                    proximity = max(0, 20 - distance_to_trigger) * 3
                    oi_factor = min(40, call_oi / 500)
                    short_factor = min(30, short_pct)
                    gamma_score = proximity + oi_factor + short_factor
        except:
            pass
            
        # === MONDAY PROBABILITY ===
        monday_rate = MONDAY_RATES.get(ticker, 50)
        
        # === MASTER PRESSURE SCORE ===
        # Weight: Monday (30) + Gamma (25) + Short (15) + Accumulation (15) + Volume (15)
        
        # Normalize components
        monday_component = (monday_rate / 100) * 30
        gamma_component = (gamma_score / 100) * 25
        short_component = (min(short_pct, 30) / 30) * 15
        accum_component = (close_position / 100) * 15 if fri_change < 10 else 5
        vol_component = min(15, (vol_ratio - 1) * 10) if vol_ratio > 1 else 0
        
        pressure_score = monday_component + gamma_component + short_component + accum_component + vol_component
        
        # Determine pressure level
        if pressure_score >= 70:
            pressure_level = "🔥 EXTREME"
        elif pressure_score >= 55:
            pressure_level = "⚡ HIGH"
        elif pressure_score >= 40:
            pressure_level = "✅ MODERATE"
        else:
            pressure_level = "⚪ LOW"
            
        return {
            'ticker': ticker,
            'price': current_price,
            'friday_change': fri_change,
            'vol_ratio': vol_ratio,
            'close_position': close_position,
            'short_pct': short_pct,
            'gamma_score': gamma_score,
            'trigger_strike': trigger_strike,
            'distance_to_trigger': distance_to_trigger,
            'call_oi': call_oi,
            'monday_rate': monday_rate,
            'pressure_score': pressure_score,
            'pressure_level': pressure_level,
            'components': {
                'monday': monday_component,
                'gamma': gamma_component,
                'short': short_component,
                'accumulation': accum_component,
                'volume': vol_component,
            }
        }
        
    except Exception as e:
        return None


def scan_pressure() -> List[Dict]:
    """Scan all tickers for pressure buildup"""
    print()
    print('='*70)
    print('🔥 WOLF PRESSURE - Where Will The Explosion Happen? 🔥')
    print('='*70)
    print()
    
    results = []
    
    for ticker in PRESSURE_UNIVERSE:
        data = get_pressure_data(ticker)
        if data:
            results.append(data)
            
    # Sort by pressure score
    results.sort(key=lambda x: x['pressure_score'], reverse=True)
    
    print(f"{'TICKER':<8} {'PRICE':<10} {'FRI':<8} {'MON%':<8} {'GAMMA':<8} {'SHORT':<8} {'SCORE':<10} {'LEVEL'}")
    print('-'*80)
    
    for r in results:
        print(f"{r['ticker']:<8} ${r['price']:<8.2f} {r['friday_change']:+.1f}%   "
              f"{r['monday_rate']:<8}% {r['gamma_score']:<8.0f} {r['short_pct']:<8.1f}% "
              f"{r['pressure_score']:<10.0f} {r['pressure_level']}")
    
    print()
    print('='*70)
    
    # Show top pressure plays
    high_pressure = [r for r in results if r['pressure_score'] >= 55]
    if high_pressure:
        print()
        print('🎯 HIGH PRESSURE PLAYS:')
        print()
        for r in high_pressure:
            print(f"  {r['pressure_level']} {r['ticker']} at ${r['price']:.2f}")
            print(f"      Monday Win Rate: {r['monday_rate']}%")
            if r['trigger_strike'] > 0:
                print(f"      Gamma Trigger: ${r['trigger_strike']:.2f} ({r['distance_to_trigger']:+.1f}% away)")
                print(f"      Call OI at Strike: {r['call_oi']:,} contracts")
            print(f"      Short Interest: {r['short_pct']:.1f}%")
            print(f"      Friday: {r['friday_change']:+.1f}% on {r['vol_ratio']:.1f}x volume")
            print()
    
    return results


def check_ticker(ticker: str) -> Optional[Dict]:
    """Get pressure data for specific ticker"""
    print()
    print(f'🔬 PRESSURE ANALYSIS: {ticker}')
    print('='*70)
    
    data = get_pressure_data(ticker.upper())
    
    if not data:
        print(f"No data for {ticker}")
        return None
        
    print()
    print(f"{data['pressure_level']} PRESSURE SCORE: {data['pressure_score']:.0f}/100")
    print()
    print(f"Price: ${data['price']:.2f}")
    print(f"Friday Change: {data['friday_change']:+.1f}%")
    print(f"Friday Volume: {data['vol_ratio']:.1f}x average")
    print(f"Close Position: {data['close_position']:.0f}% of range")
    print()
    print('PRESSURE COMPONENTS:')
    print(f"  Monday Probability: {data['monday_rate']}% ({data['components']['monday']:.1f} pts)")
    print(f"  Gamma Score: {data['gamma_score']:.0f} ({data['components']['gamma']:.1f} pts)")
    print(f"  Short Interest: {data['short_pct']:.1f}% ({data['components']['short']:.1f} pts)")
    print(f"  Accumulation Signal: {data['close_position']:.0f}% ({data['components']['accumulation']:.1f} pts)")
    print(f"  Volume Surge: {data['vol_ratio']:.1f}x ({data['components']['volume']:.1f} pts)")
    print()
    
    if data['trigger_strike'] > 0:
        print('OPTIONS GAMMA:')
        print(f"  Trigger Strike: ${data['trigger_strike']:.2f}")
        print(f"  Distance: {data['distance_to_trigger']:+.1f}%")
        print(f"  Call OI: {data['call_oi']:,} contracts")
        print(f"  Shares to Hedge: {data['call_oi'] * 100:,}")
        print()
    
    return data


def get_pressure_for_dashboard() -> List[Dict]:
    """Return pressure data for dashboard integration"""
    results = []
    
    for ticker in PRESSURE_UNIVERSE:
        data = get_pressure_data(ticker)
        if data:
            results.append(data)
            
    results.sort(key=lambda x: x['pressure_score'], reverse=True)
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Wolf Pressure - Pressure Point Scanner')
    parser.add_argument('command', nargs='?', default='scan',
                       help='scan = full scan, or ticker symbol for single check')
    
    args = parser.parse_args()
    
    if args.command.lower() == 'scan':
        scan_pressure()
    else:
        check_ticker(args.command)
