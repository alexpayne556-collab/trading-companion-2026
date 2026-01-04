#!/usr/bin/env python3
"""
🐺 WOLF PACK COMMAND CENTER
Real-time trading dashboard
Run: python dashboard.py
"""

import os
import sys
import time
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from signals.wolf_signals import WolfSignals, HerdScanner, Signal

# ============================================================================
# DISPLAY HELPERS
# ============================================================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def color(text, code):
    """ANSI color codes"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bold': '\033[1m',
        'reset': '\033[0m'
    }
    return f"{colors.get(code, '')}{text}{colors['reset']}"

def print_header():
    """Print dashboard header"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(color("=" * 80, 'cyan'))
    print(color(f"  🐺 WOLF PACK COMMAND CENTER", 'bold'))
    print(color(f"  Last Update: {now}", 'white'))
    print(color("=" * 80, 'cyan'))

def print_section(title, emoji=""):
    """Print section header"""
    print(f"\n{color(f'{emoji} {title}', 'yellow')}")
    print(color("-" * 60, 'white'))

# ============================================================================
# DATA FETCHING
# ============================================================================

def fetch_ticker_data(ticker: str, period: str = '3mo') -> dict:
    """Fetch and process ticker data"""
    try:
        df = yf.download(ticker, period=period, progress=False)
        
        if len(df) < 25:
            return None
        
        if isinstance(df['Close'], pd.DataFrame):
            return {
                'close': df['Close'].iloc[:, 0].values,
                'high': df['High'].iloc[:, 0].values,
                'low': df['Low'].iloc[:, 0].values,
                'volume': df['Volume'].iloc[:, 0].values,
                'dates': df.index.tolist()
            }
        else:
            return {
                'close': df['Close'].values,
                'high': df['High'].values,
                'low': df['Low'].values,
                'volume': df['Volume'].values,
                'dates': df.index.tolist()
            }
    except Exception as e:
        return None

# ============================================================================
# SIGNAL SCANNING
# ============================================================================

def scan_signals(tickers: list) -> dict:
    """Scan all tickers for signals"""
    results = {
        'wolf': [],
        'prerun': [],
        'capitulation': [],
        'volume': [],
        'status': []
    }
    
    for ticker in tickers:
        data = fetch_ticker_data(ticker)
        if data is None:
            continue
        
        date_str = data['dates'][-1].strftime('%Y-%m-%d')
        
        # Get all signals
        signals = WolfSignals.scan_ticker(
            data['close'], data['high'], data['low'], data['volume'],
            ticker, date_str
        )
        
        # Categorize signals
        for signal in signals:
            if signal.signal_type == 'WOLF':
                results['wolf'].append(signal)
            elif signal.signal_type == 'PRE-RUN':
                results['prerun'].append(signal)
            elif signal.signal_type == 'CAPITULATION':
                results['capitulation'].append(signal)
            elif signal.signal_type == 'VOLUME':
                results['volume'].append(signal)
        
        # Calculate status for all tickers
        metrics = WolfSignals.calculate_metrics(
            data['close'], data['high'], data['low'], data['volume']
        )
        if metrics:
            results['status'].append({
                'ticker': ticker,
                'price': metrics['price'],
                'daily_chg': metrics['daily_chg'],
                'pct_from_high': metrics['pct_from_high'],
                'rel_vol': metrics['rel_vol'],
                'sector': HerdScanner.get_sector(ticker)
            })
    
    return results

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_signals(results: dict):
    """Display all signals"""
    
    # === WOLF SIGNALS ===
    print_section("WOLF SIGNALS", "🐺")
    print(color("  Volume spike + flat day + healthy trend | p=0.023, +37.87% avg, 78% WR", 'white'))
    
    if results['wolf']:
        for s in results['wolf']:
            strength_color = 'green' if s.strength == 'STRONG' else 'yellow' if s.strength == 'MODERATE' else 'white'
            print(f"  {color(s.ticker, 'bold'):8} ${s.price:.2f}  [{color(s.strength, strength_color)}]")
            print(f"           {s.description}")
    else:
        print(color("  No Wolf Signals", 'white'))
    
    # === PRE-RUN PREDICTOR ===
    print_section("PRE-RUN PREDICTOR", "📈")
    print(color("  5 signatures before explosions | p=0.0000, +17.27% avg, 58% WR", 'white'))
    
    if results['prerun']:
        for s in results['prerun']:
            score = s.metrics.get('score', 0)
            strength_color = 'green' if score == 5 else 'yellow'
            print(f"  {color(s.ticker, 'bold'):8} ${s.price:.2f}  [Score {color(f'{score}/5', strength_color)}]")
            print(f"           {s.description}")
    else:
        print(color("  No Pre-Run signals (score >= 4)", 'white'))
    
    # === CAPITULATION HUNTER ===
    print_section("CAPITULATION HUNTER", "💀")
    print(color("  Red spike when wounded | p=0.004, +19.95% avg, 58% WR", 'white'))
    
    if results['capitulation']:
        for s in results['capitulation']:
            strength_color = 'green' if s.strength == 'STRONG' else 'yellow' if s.strength == 'MODERATE' else 'white'
            print(f"  {color(s.ticker, 'bold'):8} ${s.price:.2f}  [{color(s.strength, strength_color)}]")
            print(f"           {s.description}")
    else:
        print(color("  No Capitulation signals", 'white'))
    
    # === VOLUME ALERTS (WIDE NET) ===
    print_section("VOLUME ALERTS", "📊")
    print(color("  Unusual volume activity (wide net scanner)", 'white'))
    
    # Filter to only show non-signal volume alerts
    vol_only = [s for s in results['volume'] 
                if s.ticker not in [w.ticker for w in results['wolf']]
                and s.ticker not in [p.ticker for p in results['prerun']]
                and s.ticker not in [c.ticker for c in results['capitulation']]]
    
    if vol_only:
        for s in vol_only[:10]:  # Top 10
            direction = color("▲", 'green') if s.metrics['daily_chg'] > 0 else color("▼", 'red')
            print(f"  {s.ticker:8} ${s.price:.2f}  {direction} {abs(s.metrics['daily_chg']):+.1f}%  {s.metrics['rel_vol']:.1f}x vol")
    else:
        print(color("  No unusual volume", 'white'))

def display_market_status(results: dict):
    """Display market status overview"""
    
    print_section("MARKET STATUS", "📍")
    
    if not results['status']:
        print(color("  No data", 'white'))
        return
    
    # Sort by daily change
    sorted_status = sorted(results['status'], key=lambda x: x['daily_chg'], reverse=True)
    
    # Header
    print(f"  {'TICKER':<8} {'PRICE':>10} {'DAY':>8} {'FROM HIGH':>12} {'VOL':>8} {'STATUS':<15}")
    print(f"  {'-' * 65}")
    
    for s in sorted_status:
        # Color the daily change
        if s['daily_chg'] > 5:
            day_color = 'green'
            day_str = f"+{s['daily_chg']:.1f}%"
        elif s['daily_chg'] > 0:
            day_color = 'green'
            day_str = f"+{s['daily_chg']:.1f}%"
        elif s['daily_chg'] > -5:
            day_color = 'red'
            day_str = f"{s['daily_chg']:.1f}%"
        else:
            day_color = 'red'
            day_str = f"{s['daily_chg']:.1f}%"
        
        # Status indicator
        if s['pct_from_high'] > -5:
            status = color("🟢 Near High", 'green')
        elif s['pct_from_high'] > -15:
            status = color("🟡 Pullback", 'yellow')
        elif s['pct_from_high'] > -30:
            status = color("🟠 Wounded", 'yellow')
        else:
            status = color("🔴 Deep Wound", 'red')
        
        # Volume indicator
        vol_str = f"{s['rel_vol']:.1f}x"
        if s['rel_vol'] > 2:
            vol_str = color(vol_str, 'cyan')
        
        print(f"  {s['ticker']:<8} ${s['price']:>9.2f} {color(day_str, day_color):>8} "
              f"{s['pct_from_high']:>+10.1f}%  {vol_str:>8}  {status}")

def display_sector_heat(results: dict):
    """Display sector heat map"""
    
    print_section("SECTOR HEAT", "🔥")
    
    if not results['status']:
        return
    
    # Group by sector
    sectors = {}
    for s in results['status']:
        sector = s['sector']
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(s)
    
    # Calculate sector averages
    sector_heat = []
    for sector, stocks in sectors.items():
        avg_chg = np.mean([s['daily_chg'] for s in stocks])
        avg_vol = np.mean([s['rel_vol'] for s in stocks])
        sector_heat.append({
            'sector': sector,
            'avg_chg': avg_chg,
            'avg_vol': avg_vol,
            'count': len(stocks)
        })
    
    # Sort by change
    sector_heat = sorted(sector_heat, key=lambda x: x['avg_chg'], reverse=True)
    
    for s in sector_heat:
        bar_len = int(abs(s['avg_chg']) * 2)
        if s['avg_chg'] > 0:
            bar = color("█" * min(bar_len, 20), 'green')
            chg_str = color(f"+{s['avg_chg']:.1f}%", 'green')
        else:
            bar = color("█" * min(bar_len, 20), 'red')
            chg_str = color(f"{s['avg_chg']:.1f}%", 'red')
        
        vol_indicator = "🔥" if s['avg_vol'] > 1.5 else "  "
        print(f"  {s['sector']:<10} {chg_str:>8} {bar} {vol_indicator}")

def display_quick_actions():
    """Display quick action reminders"""
    
    print_section("QUICK REFERENCE", "📋")
    
    print(color("  WOLF SIGNAL:      Volume spike + flat + healthy trend → BUY continuation", 'white'))
    print(color("  PRE-RUN 5/5:      All 5 signatures → Strong entry", 'white'))
    print(color("  CAPITULATION:     Red spike when wounded → BUY the capitulation", 'white'))
    print()
    print(color("  Commands:", 'cyan'))
    print(color("  [R] Refresh   [W] Wide scan   [Q] Quit", 'white'))

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def run_dashboard(auto_refresh: bool = False, refresh_interval: int = 60):
    """Run the main dashboard"""
    
    # Core tickers to always watch
    core_tickers = HerdScanner.REPEAT_RUNNERS
    
    while True:
        clear_screen()
        print_header()
        
        print(color("\n  Scanning...", 'cyan'))
        
        # Scan core tickers
        results = scan_signals(core_tickers)
        
        clear_screen()
        print_header()
        
        # Display all sections
        display_signals(results)
        display_market_status(results)
        display_sector_heat(results)
        display_quick_actions()
        
        print(color(f"\n  Watching: {', '.join(core_tickers)}", 'white'))
        
        if auto_refresh:
            print(color(f"\n  Auto-refresh in {refresh_interval}s... (Ctrl+C to stop)", 'cyan'))
            time.sleep(refresh_interval)
        else:
            print()
            cmd = input(color("  Command [R/W/Q]: ", 'cyan')).strip().upper()
            
            if cmd == 'Q':
                print(color("\n  🐺 Pack out. AWOOOO!", 'yellow'))
                break
            elif cmd == 'W':
                # Wide scan
                print(color("\n  Running wide scan...", 'cyan'))
                all_tickers = HerdScanner.get_all_tickers()
                results = scan_signals(all_tickers)
                
                clear_screen()
                print_header()
                print(color(f"\n  WIDE SCAN - {len(all_tickers)} tickers", 'yellow'))
                
                display_signals(results)
                display_market_status(results)
                
                input(color("\n  Press Enter to continue...", 'cyan'))

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='🐺 Wolf Pack Command Center')
    parser.add_argument('--auto', '-a', action='store_true', help='Auto-refresh mode')
    parser.add_argument('--interval', '-i', type=int, default=60, help='Refresh interval (seconds)')
    parser.add_argument('--wide', '-w', action='store_true', help='Start with wide scan')
    
    args = parser.parse_args()
    
    print(color("""
    
    🐺🐺🐺 WOLF PACK COMMAND CENTER 🐺🐺🐺
    
    """, 'yellow'))
    
    if args.wide:
        print(color("  Starting wide scan mode...", 'cyan'))
        time.sleep(1)
    
    try:
        run_dashboard(auto_refresh=args.auto, refresh_interval=args.interval)
    except KeyboardInterrupt:
        print(color("\n\n  🐺 Pack out. AWOOOO!", 'yellow'))
