#!/usr/bin/env python3
"""
🐺 HERD SCANNER
Wide-net scanner that runs continuously
Catches unusual activity across many tickers
Run: python herd_scanner.py --continuous
"""

import os
import sys
import time
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from signals.wolf_signals import WolfSignals, HerdScanner


def color(text, code):
    colors = {
        'red': '\033[91m', 'green': '\033[92m', 'yellow': '\033[93m',
        'blue': '\033[94m', 'magenta': '\033[95m', 'cyan': '\033[96m',
        'white': '\033[97m', 'bold': '\033[1m', 'reset': '\033[0m'
    }
    return f"{colors.get(code, '')}{text}{colors['reset']}"


def fetch_batch(tickers: list) -> dict:
    """Fetch data for multiple tickers efficiently"""
    results = {}
    
    # Batch download
    data = yf.download(tickers, period='3mo', progress=False, group_by='ticker')
    
    for ticker in tickers:
        try:
            if len(tickers) == 1:
                df = data
            else:
                df = data[ticker]
            
            if len(df) < 25:
                continue
            
            if isinstance(df['Close'], pd.DataFrame):
                results[ticker] = {
                    'close': df['Close'].iloc[:, 0].values,
                    'high': df['High'].iloc[:, 0].values,
                    'low': df['Low'].iloc[:, 0].values,
                    'volume': df['Volume'].iloc[:, 0].values,
                    'dates': df.index.tolist()
                }
            else:
                results[ticker] = {
                    'close': df['Close'].values,
                    'high': df['High'].values,
                    'low': df['Low'].values,
                    'volume': df['Volume'].values,
                    'dates': df.index.tolist()
                }
        except:
            continue
    
    return results


def scan_herd(tickers: list):
    """Scan a herd of tickers for unusual activity"""
    
    print(color(f"\n🐺 HERD SCAN - {len(tickers)} tickers", 'yellow'))
    print(color(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'white'))
    print(color("=" * 60, 'cyan'))
    
    # Fetch all data
    print(color("  Fetching data...", 'white'))
    all_data = fetch_batch(tickers)
    
    print(color(f"  Loaded {len(all_data)} tickers", 'white'))
    print(color("  Scanning for signals...", 'white'))
    
    # Results
    alerts = {
        'wolf': [],
        'prerun': [],
        'capitulation': [],
        'volume_spike': [],
        'movers': []
    }
    
    for ticker, data in all_data.items():
        date_str = data['dates'][-1].strftime('%Y-%m-%d')
        
        # Get metrics
        metrics = WolfSignals.calculate_metrics(
            data['close'], data['high'], data['low'], data['volume']
        )
        
        if metrics is None:
            continue
        
        # Track big movers
        if abs(metrics['daily_chg']) > 5:
            alerts['movers'].append({
                'ticker': ticker,
                'price': metrics['price'],
                'change': metrics['daily_chg'],
                'volume': metrics['rel_vol']
            })
        
        # Get signals
        signals = WolfSignals.scan_ticker(
            data['close'], data['high'], data['low'], data['volume'],
            ticker, date_str
        )
        
        for signal in signals:
            if signal.signal_type == 'WOLF':
                alerts['wolf'].append(signal)
            elif signal.signal_type == 'PRE-RUN':
                alerts['prerun'].append(signal)
            elif signal.signal_type == 'CAPITULATION':
                alerts['capitulation'].append(signal)
            elif signal.signal_type == 'VOLUME' and metrics['rel_vol'] > 3:
                alerts['volume_spike'].append(signal)
    
    # Display Results
    print(color("\n" + "=" * 60, 'cyan'))
    
    # Wolf Signals
    if alerts['wolf']:
        print(color("\n🐺 WOLF SIGNALS:", 'green'))
        for s in alerts['wolf']:
            print(color(f"   {s.ticker:6} ${s.price:.2f} - {s.description}", 'green'))
    
    # Pre-Run
    if alerts['prerun']:
        print(color("\n📈 PRE-RUN SIGNALS:", 'yellow'))
        for s in alerts['prerun']:
            print(color(f"   {s.ticker:6} ${s.price:.2f} - {s.description}", 'yellow'))
    
    # Capitulation
    if alerts['capitulation']:
        print(color("\n💀 CAPITULATION:", 'magenta'))
        for s in alerts['capitulation']:
            print(color(f"   {s.ticker:6} ${s.price:.2f} - {s.description}", 'magenta'))
    
    # Volume Spikes (3x+)
    if alerts['volume_spike']:
        print(color("\n📊 VOLUME SPIKES (3x+):", 'cyan'))
        for s in sorted(alerts['volume_spike'], key=lambda x: x.metrics['rel_vol'], reverse=True)[:10]:
            print(color(f"   {s.ticker:6} ${s.price:.2f} - {s.metrics['rel_vol']:.1f}x volume", 'cyan'))
    
    # Big Movers
    if alerts['movers']:
        print(color("\n🚀 BIG MOVERS (5%+):", 'white'))
        sorted_movers = sorted(alerts['movers'], key=lambda x: abs(x['change']), reverse=True)
        for m in sorted_movers[:15]:
            arrow = "▲" if m['change'] > 0 else "▼"
            c = 'green' if m['change'] > 0 else 'red'
            print(color(f"   {m['ticker']:6} ${m['price']:.2f} {arrow} {m['change']:+.1f}% ({m['volume']:.1f}x vol)", c))
    
    # Summary
    total_alerts = (len(alerts['wolf']) + len(alerts['prerun']) + 
                   len(alerts['capitulation']) + len(alerts['volume_spike']))
    
    print(color("\n" + "=" * 60, 'cyan'))
    print(color(f"  TOTAL: {total_alerts} signals, {len(alerts['movers'])} big movers", 'yellow'))
    
    return alerts


def run_continuous(interval: int = 300):
    """Run scanner continuously"""
    
    print(color("""
    
    🐺🐺🐺 HERD SCANNER - CONTINUOUS MODE 🐺🐺🐺
    
    Scanning for:
    - Wolf Signals (p=0.023, +37.87% avg)
    - Pre-Run Predictor (p=0.0000, +17.27% avg)
    - Capitulation Hunter (p=0.004, +19.95% avg)
    - Volume Spikes (3x+ unusual activity)
    - Big Movers (5%+ daily change)
    
    """, 'yellow'))
    
    tickers = HerdScanner.get_all_tickers()
    print(color(f"  Watching {len(tickers)} tickers", 'cyan'))
    print(color(f"  Refresh every {interval} seconds", 'cyan'))
    print(color("  Press Ctrl+C to stop\n", 'white'))
    
    while True:
        try:
            alerts = scan_herd(tickers)
            
            # Sound alert if Wolf or strong Pre-Run signal found
            if alerts['wolf'] or any(s.strength == 'STRONG' for s in alerts['prerun']):
                print(color("\n  🔔 ALERT: High-confidence signal detected!", 'green'))
                # Could add sound/notification here
            
            print(color(f"\n  Next scan in {interval}s...", 'cyan'))
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print(color("\n\n  🐺 Scanner stopped. AWOOOO!", 'yellow'))
            break


def run_once():
    """Run scanner once"""
    tickers = HerdScanner.get_all_tickers()
    alerts = scan_herd(tickers)
    return alerts


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='🐺 Herd Scanner')
    parser.add_argument('--continuous', '-c', action='store_true', help='Run continuously')
    parser.add_argument('--interval', '-i', type=int, default=300, help='Scan interval (seconds)')
    
    args = parser.parse_args()
    
    if args.continuous:
        run_continuous(args.interval)
    else:
        run_once()
