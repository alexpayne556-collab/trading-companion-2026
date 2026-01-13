#!/usr/bin/env python3
"""
🐺 BACKTEST BLIND - The Ultimate Test

Turn back time 5 days. NO HINTS. NO HARDCODED TICKERS.

Can we find what actually moved using ONLY:
- Volume patterns
- Price action
- Market-wide scanning

If YES = System works
If NO = Back to drawing board

This is the proof.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import argparse


def get_test_universe():
    """
    Get test universe: S&P 500 + NASDAQ 100 + liquid small caps
    Same as market_discovery.py
    """
    
    # S&P 500
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        sp500 = tables[0]['Symbol'].str.replace('.', '-').tolist()
    except:
        sp500 = []
    
    # NASDAQ 100
    try:
        url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
        tables = pd.read_html(url)
        nasdaq = tables[4]['Ticker'].str.replace('.', '-').tolist()
    except:
        nasdaq = []
    
    # Liquid small caps (where most explosive moves happen)
    small_caps = [
        'SOUN', 'AISP', 'PTON', 'PLUG', 'CLOV', 'SOFI', 'HOOD', 'LCID', 
        'RIVN', 'XOS', 'MULN', 'NKLA', 'BYND', 'OPEN', 'WISH', 
        'COIN', 'MARA', 'RIOT', 'WULF', 'CLSK', 'BTBT', 'CIFR', 'IREN',
        'ATOS', 'GNUS', 'TRKA', 'CPOP', 'CREX', 'APLD', 'ATON', 'CORZ',
        'NVAX', 'MRNA', 'BNTX', 'SAVA', 'BMRN', 'RARE', 'BEAM', 'NTLA',
        'CRSP', 'EDIT', 'VRTX', 'IONS', 'SRPT', 'EXAS', 'PACB', 'ILMN'
    ]
    
    all_tickers = list(set(sp500 + nasdaq + small_caps))
    
    return all_tickers


def scan_historical_day(tickers, target_date):
    """
    Scan for movers on a specific historical date
    Returns tickers with unusual activity (volume + price)
    
    This simulates: "What if we ran market_discovery.py on this day?"
    """
    
    print(f"\n📅 Scanning {target_date.strftime('%Y-%m-%d')}...")
    
    # Get data for target day + previous 20 days for baseline
    start_date = target_date - timedelta(days=30)
    end_date = target_date + timedelta(days=1)
    
    signals = []
    count = 0
    
    for ticker in tickers:
        count += 1
        if count % 100 == 0:
            print(f"   Progress: {count}/{len(tickers)}...")
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date, interval='1d')
            
            if len(hist) < 10:
                continue
            
            # Find target day in history
            target_idx = None
            for i, idx in enumerate(hist.index):
                if idx.date() == target_date.date():
                    target_idx = i
                    break
            
            if target_idx is None or target_idx < 5:
                continue
            
            # Get target day data
            today = hist.iloc[target_idx]
            yesterday = hist.iloc[target_idx - 1]
            
            # Calculate metrics
            price_change = ((today['Close'] - yesterday['Close']) / yesterday['Close']) * 100
            
            # Volume spike vs 20-day average
            baseline_vol = hist.iloc[max(0, target_idx-20):target_idx]['Volume'].mean()
            if baseline_vol > 0:
                volume_spike = ((today['Volume'] - baseline_vol) / baseline_vol) * 100
            else:
                volume_spike = 0
            
            # Signal criteria (same as volume_detector.py)
            has_volume_signal = volume_spike >= 50  # 50%+ volume spike
            has_price_signal = abs(price_change) >= 5  # 5%+ price move
            
            if has_volume_signal or has_price_signal:
                signals.append({
                    'ticker': ticker,
                    'date': target_date.strftime('%Y-%m-%d'),
                    'price_change': price_change,
                    'volume_spike': volume_spike,
                    'price': today['Close'],
                    'volume': today['Volume']
                })
            
            time.sleep(0.05)  # Rate limiting
            
        except Exception as e:
            continue
    
    # Sort by combined signal strength
    signals.sort(key=lambda x: abs(x['price_change']) + (x['volume_spike'] / 10), reverse=True)
    
    return signals


def get_forward_returns(ticker, entry_date, days=[1, 2, 3, 5]):
    """
    Get forward returns from entry date
    This tells us: Did we catch a mover BEFORE it ran?
    """
    
    try:
        stock = yf.Ticker(ticker)
        start = entry_date
        end = entry_date + timedelta(days=10)
        hist = stock.history(start=start, end=end, interval='1d')
        
        if len(hist) < 2:
            return None
        
        entry_price = hist.iloc[0]['Close']
        
        returns = {'entry_price': entry_price}
        
        for day in days:
            if day < len(hist):
                future_price = hist.iloc[day]['Close']
                ret = ((future_price - entry_price) / entry_price) * 100
                returns[f'day_{day}'] = ret
            else:
                returns[f'day_{day}'] = None
        
        # Peak gain in next 5 days
        if len(hist) >= 2:
            peak = hist.iloc[:min(6, len(hist))]['High'].max()
            peak_gain = ((peak - entry_price) / entry_price) * 100
            returns['peak_gain'] = peak_gain
        else:
            returns['peak_gain'] = None
        
        return returns
        
    except:
        return None


def backtest_period(start_date_str, end_date_str):
    """
    Run blind backtest over a date range
    
    For each day:
    1. Scan for volume + price signals (NO HINTS)
    2. Check forward returns
    3. Calculate: Did we find movers BEFORE they moved?
    """
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    
    print("🐺 BACKTEST BLIND - Can We Find Movers Without Hardcoded Tickers?")
    print("="*70)
    print(f"Test Period: {start_date_str} to {end_date_str}")
    print("="*70)
    
    # Get universe
    universe = get_test_universe()
    print(f"\nUniverse: {len(universe)} tickers")
    
    # Run backtest day by day
    current_date = start_date
    all_results = []
    
    while current_date <= end_date:
        # Skip weekends
        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue
        
        # Scan this day for signals
        signals = scan_historical_day(universe, current_date)
        
        print(f"\n✅ Found {len(signals)} signals on {current_date.strftime('%Y-%m-%d')}")
        
        # Get forward returns for top signals
        print(f"   Checking forward returns for top 20 signals...")
        
        for signal in signals[:20]:
            returns = get_forward_returns(signal['ticker'], current_date)
            
            if returns:
                signal.update(returns)
                all_results.append(signal)
                
                # Print interesting results (signal that led to move)
                if returns.get('peak_gain', 0) >= 10:
                    print(f"   🎯 {signal['ticker']:6s} - Signal: Vol +{signal['volume_spike']:.0f}% / "
                          f"Price {signal['price_change']:+.1f}% → Peak: {returns['peak_gain']:+.1f}%")
        
        current_date += timedelta(days=1)
        time.sleep(1)  # Rate limiting between days
    
    return all_results


def analyze_results(results):
    """Analyze backtest results - Did we catch movers early?"""
    
    print("\n" + "="*70)
    print("📊 BACKTEST RESULTS")
    print("="*70)
    
    if not results:
        print("No results to analyze")
        return
    
    # Filter for signals that had forward returns data
    valid = [r for r in results if r.get('peak_gain') is not None]
    
    print(f"\nTotal signals tested: {len(valid)}")
    
    # Winners (peak gain >= 10%)
    winners = [r for r in valid if r.get('peak_gain', 0) >= 10]
    print(f"Big winners (peak ≥10%): {len(winners)} ({len(winners)/len(valid)*100:.1f}%)")
    
    # Sort winners by peak gain
    winners.sort(key=lambda x: x.get('peak_gain', 0), reverse=True)
    
    print(f"\n🏆 TOP 20 CATCHES (Signal → Actual Move)")
    print("-" * 70)
    
    for i, w in enumerate(winners[:20], 1):
        day5 = w.get('day_5')
        day5_str = f"{day5:+6.1f}%" if day5 is not None else "N/A   "
        print(f"{i:2d}. {w['date']} {w['ticker']:6s} - "
              f"Signal: Vol +{w['volume_spike']:5.0f}% / Price {w['price_change']:+6.1f}% → "
              f"Peak: {w['peak_gain']:+6.1f}% (Day 5: {day5_str})")
    
    # Statistics
    if winners:
        avg_peak = sum(w.get('peak_gain', 0) for w in winners) / len(winners)
        
        winners_with_day5 = [w for w in winners if w.get('day_5') is not None]
        if winners_with_day5:
            avg_day5 = sum(w.get('day_5') for w in winners_with_day5) / len(winners_with_day5)
            day5_str = f"{avg_day5:.1f}%"
        else:
            day5_str = "N/A"
        
        print(f"\n📈 Winner Statistics:")
        print(f"   Average peak gain: {avg_peak:.1f}%")
        print(f"   Average Day 5 gain: {day5_str}")
    
    # Signal characteristics
    print(f"\n🔍 Signal Characteristics (Winners):")
    avg_vol_spike = sum(w['volume_spike'] for w in winners) / len(winners)
    avg_price_signal = sum(abs(w['price_change']) for w in winners) / len(winners)
    
    print(f"   Average volume spike: {avg_vol_spike:.0f}%")
    print(f"   Average price signal: {avg_price_signal:.1f}%")
    
    print("\n" + "="*70)
    print("🎯 CONCLUSION:")
    
    if len(winners) / len(valid) >= 0.15:
        print("   ✅ SYSTEM WORKS - Found movers BEFORE they ran")
        print("   Volume + price signals successfully identified future movers")
    elif len(winners) / len(valid) >= 0.08:
        print("   ⚠️  SYSTEM SHOWS PROMISE - Some predictive value")
        print("   Needs refinement but core approach valid")
    else:
        print("   ❌ SYSTEM NEEDS WORK - Low hit rate")
        print("   Signals not reliably predicting future moves")
    
    print("="*70)


def main():
    parser = argparse.ArgumentParser(description='Blind backtest - Find movers without hardcoded tickers')
    parser.add_argument('--start', default='2026-01-06', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', default='2026-01-10', help='End date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # Run backtest
    results = backtest_period(args.start, args.end)
    
    # Analyze results
    analyze_results(results)
    
    # Save results
    df = pd.DataFrame(results)
    output_file = f'backtest_results_{args.start}_to_{args.end}.csv'
    df.to_csv(output_file, index=False)
    print(f"\n💾 Results saved to {output_file}")


if __name__ == "__main__":
    main()
