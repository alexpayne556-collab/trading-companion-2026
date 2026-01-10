#!/usr/bin/env python3
"""
GAP DIP RECOVERY VALIDATOR
Tests hypothesis: "Stocks gap up, dip intraday, then recover by close"

HYPOTHESIS:
When small caps gap up on news/momentum, they often dip in the first hour,
then recover to close near highs. If validated, this creates day-trading edge.

METHOD:
1. Load 60 days intraday data (5-min candles) for 21 tickers
2. Detect gap ups (>3% from prior close)
3. Measure dip timing (when does low occur?)
4. Measure dip depth (% from morning high)
5. Track recovery (does it close 2%+ above low?)

SUCCESS CRITERIA:
- >70% = VALIDATED EDGE (code as scanner)
- 50-70% = WEAK EDGE (refine or combine)
- <50% = DISPROVEN (discard, move to next)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys

# TICKER UNIVERSE (21 tickers across 4 sectors)
TICKERS = {
    'NUCLEAR': ['DNN', 'UEC', 'UUUU', 'SMR', 'OKLO', 'CCJ'],
    'AI_INFRA': ['CIFR', 'WULF', 'CLSK', 'APLD', 'IREN'],
    'SPACE': ['LUNR', 'RKLB', 'MNTS', 'SATL', 'PL'],
    'POWER': ['CEG', 'VST', 'PCG', 'D']
}

def load_intraday_data(ticker, days=60):
    """Load 5-minute intraday data for ticker"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        print(f"Loading {ticker}...", end=' ', flush=True)
        data = yf.download(ticker, start=start_date, end=end_date, interval='5m', progress=False)
        
        if data.empty:
            print("NO DATA")
            return None
        
        print(f"✓ {len(data)} candles")
        return data
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def detect_gaps(data, gap_threshold=0.03):
    """Find days where stock gapped up >3% from prior close"""
    if data is None or data.empty:
        return []
    
    gaps = []
    
    # Group by date
    data['Date'] = data.index.date
    grouped = data.groupby('Date')
    
    dates = sorted(data['Date'].unique())
    
    for i in range(1, len(dates)):
        today = dates[i]
        yesterday = dates[i-1]
        
        # Get data for both days
        yesterday_data = grouped.get_group(yesterday)
        today_data = grouped.get_group(today)
        
        if yesterday_data.empty or today_data.empty:
            continue
        
        # Prior close = yesterday's last close
        prior_close = float(yesterday_data['Close'].iloc[-1])
        
        # Today's open = first candle's open
        today_open = float(today_data['Open'].iloc[0])
        
        # Calculate gap %
        gap_pct = (today_open - prior_close) / prior_close
        
        if gap_pct >= gap_threshold:
            gaps.append({
                'date': today,
                'prior_close': prior_close,
                'open': today_open,
                'gap_pct': gap_pct * 100,
                'data': today_data
            })
    
    return gaps

def analyze_gap_day(gap_info):
    """Analyze a gap day: timing, depth, recovery"""
    data = gap_info['data']
    
    if len(data) < 10:  # Need at least 10 candles (50 minutes)
        return None
    
    # Morning high (first 30 minutes = 6 candles)
    morning_data = data.iloc[:6]
    morning_high = float(morning_data['High'].max())
    
    # Intraday low
    intraday_low = float(data['Low'].min())
    
    # Find when low occurred
    low_idx = data['Low'].idxmin()
    open_time = data.index[0]
    
    # Calculate minutes after open to reach low
    if hasattr(low_idx, 'total_seconds'):
        # datetime object
        minutes_to_low = (low_idx - open_time).total_seconds() / 60
    else:
        # Could be Series or other type - use iloc
        minutes_to_low = 0  # Default if can't calculate
    
    # Close
    close_price = float(data['Close'].iloc[-1])
    
    # Dip depth from morning high
    dip_depth = (morning_high - intraday_low) / morning_high * 100
    
    # Recovery: Did it close 2%+ above low?
    recovery = (close_price - intraday_low) / intraday_low * 100
    recovered = recovery >= 2.0
    
    return {
        'date': gap_info['date'],
        'gap_pct': gap_info['gap_pct'],
        'open': gap_info['open'],
        'morning_high': morning_high,
        'intraday_low': intraday_low,
        'close': close_price,
        'minutes_to_low': minutes_to_low,
        'dip_depth': dip_depth,
        'recovery_pct': recovery,
        'recovered': recovered
    }

def main():
    print("=" * 80)
    print("GAP DIP RECOVERY VALIDATOR")
    print("Hypothesis: Stocks gap up, dip intraday, then recover by close")
    print("=" * 80)
    print()
    
    all_results = []
    sector_results = {}
    
    # Test each sector
    for sector, tickers in TICKERS.items():
        print(f"\n{'='*80}")
        print(f"SECTOR: {sector}")
        print(f"{'='*80}")
        
        sector_gaps = []
        
        for ticker in tickers:
            # Load data
            data = load_intraday_data(ticker, days=60)
            if data is None:
                continue
            
            # Find gap days
            gaps = detect_gaps(data, gap_threshold=0.03)
            
            if not gaps:
                print(f"  {ticker}: No gaps found")
                continue
            
            print(f"  {ticker}: {len(gaps)} gap days found")
            
            # Analyze each gap day
            for gap in gaps:
                result = analyze_gap_day(gap)
                if result is not None:
                    result['ticker'] = ticker
                    result['sector'] = sector
                    all_results.append(result)
                    sector_gaps.append(result)
        
        # Calculate sector recovery rate
        if sector_gaps:
            recoveries = [r['recovered'] for r in sector_gaps]
            recovery_rate = sum(recoveries) / len(recoveries) * 100
            avg_dip = np.mean([r['dip_depth'] for r in sector_gaps])
            avg_time = np.mean([r['minutes_to_low'] for r in sector_gaps])
            
            sector_results[sector] = {
                'gap_days': len(sector_gaps),
                'recovery_rate': recovery_rate,
                'avg_dip_depth': avg_dip,
                'avg_minutes_to_low': avg_time
            }
            
            print(f"\n{sector} RESULTS:")
            print(f"  Gap days found: {len(sector_gaps)}")
            print(f"  Recovery rate: {recovery_rate:.1f}%")
            print(f"  Avg dip depth: {avg_dip:.2f}%")
            print(f"  Avg time to low: {avg_time:.0f} minutes")
    
    # OVERALL RESULTS
    print("\n" + "=" * 80)
    print("OVERALL RESULTS")
    print("=" * 80)
    
    if not all_results:
        print("NO DATA - Unable to test hypothesis")
        sys.exit(1)
    
    total_gaps = len(all_results)
    total_recoveries = sum([r['recovered'] for r in all_results])
    overall_recovery_rate = (total_recoveries / total_gaps * 100) if total_gaps > 0 else 0
    
    avg_dip_depth = np.mean([r['dip_depth'] for r in all_results])
    avg_minutes_to_low = np.mean([r['minutes_to_low'] for r in all_results])
    avg_recovery_pct = np.mean([r['recovery_pct'] for r in all_results])
    
    print(f"\nTotal gap days tested: {total_gaps}")
    print(f"Days that recovered (>2% from low): {total_recoveries}")
    print(f"RECOVERY RATE: {overall_recovery_rate:.1f}%")
    print(f"\nAverage dip depth: {avg_dip_depth:.2f}%")
    print(f"Average time to low: {avg_minutes_to_low:.0f} minutes after open")
    print(f"Average recovery: {avg_recovery_pct:.2f}%")
    
    # TOP PERFORMERS
    print("\n" + "=" * 80)
    print("TOP RECOVERY TICKERS (min 3 gap days)")
    print("=" * 80)
    
    ticker_stats = {}
    for result in all_results:
        ticker = result['ticker']
        if ticker not in ticker_stats:
            ticker_stats[ticker] = {'gaps': 0, 'recoveries': 0}
        ticker_stats[ticker]['gaps'] += 1
        if result['recovered']:
            ticker_stats[ticker]['recoveries'] += 1
    
    top_tickers = []
    for ticker, stats in ticker_stats.items():
        if stats['gaps'] >= 3:
            rate = stats['recoveries'] / stats['gaps'] * 100
            top_tickers.append((ticker, rate, stats['gaps'], stats['recoveries']))
    
    top_tickers.sort(key=lambda x: x[1], reverse=True)
    
    for ticker, rate, gaps, recoveries in top_tickers[:10]:
        print(f"  {ticker:6s}: {rate:5.1f}% ({recoveries}/{gaps} days)")
    
    # VERDICT
    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)
    
    if overall_recovery_rate >= 70:
        verdict = "✅ VALIDATED EDGE"
        recommendation = "Code as scanner. Define entry (on dip), exit (near close), stop (below low)."
    elif overall_recovery_rate >= 50:
        verdict = "⚠️  WEAK EDGE"
        recommendation = "Refine: Test specific sectors, tickers, or gap sizes. May work with filters."
    else:
        verdict = "❌ DISPROVEN"
        recommendation = "Discard this pattern. Move to next research project."
    
    print(f"\n{verdict}")
    print(f"Recovery rate: {overall_recovery_rate:.1f}% (threshold: >70% validated, >50% weak)")
    print(f"Sample size: {total_gaps} gap days")
    print(f"\nRECOMMENDATION: {recommendation}")
    
    # Save results
    df = pd.DataFrame(all_results)
    output_file = '/workspaces/trading-companion-2026/logs/gap_dip_recovery_results.csv'
    df.to_csv(output_file, index=False)
    print(f"\nResults saved to: {output_file}")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    if overall_recovery_rate >= 70:
        print("1. Build scanner to detect gap ups pre-market")
        print("2. Define entry: Wait for dip (avg ~{:.0f} min after open)".format(avg_minutes_to_low))
        print("3. Define exit: Near close (or target 2%+ from low)")
        print("4. Define stop: Below intraday low (-1%)")
        print("5. Paper trade 10 days to validate in real-time")
    elif overall_recovery_rate >= 50:
        print("1. Identify which sectors/tickers show >70% recovery")
        print("2. Test if larger gaps (>5%) have better recovery")
        print("3. Test if pre-market volume predicts recovery")
        print("4. Combine with other filters (volume, news, RSI)")
    else:
        print("1. Move to next research project: Leader/Laggard Lag Time")
        print("2. Test when CCJ moves 5%+, when do DNN/UEC/UUUU follow?")
        print("3. Build: leader_laggard_lag_validator.py")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
