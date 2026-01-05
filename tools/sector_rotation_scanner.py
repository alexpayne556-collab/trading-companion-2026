#!/usr/bin/env python3
"""
🐺 SECTOR ROTATION SCANNER
==========================
Tracks money flow between AI infrastructure layers
Identifies which sector is LEADING and which is LAGGING

Usage:
    python sector_rotation_scanner.py              # Run once
    python sector_rotation_scanner.py --live       # Auto-refresh
    python sector_rotation_scanner.py --alert 5    # Alert on 5%+ moves
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time
import argparse
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# SECTOR DEFINITIONS — ROTATION TRACKING
# ============================================================

ROTATION_SECTORS = {
    'NUCLEAR': {
        'tickers': ['UUUU', 'SMR', 'LEU', 'OKLO', 'CCJ', 'DNN', 'UEC', 'NXE', 'NNE'],
        'leader': 'CCJ',  # Uranium giant as benchmark
        'thesis': 'AI power demand'
    },
    'COOLING': {
        'tickers': ['VRT', 'MOD', 'NVT'],
        'leader': 'VRT',
        'thesis': 'Rack density explosion'
    },
    'PHOTONICS': {
        'tickers': ['LITE', 'AAOI', 'COHR', 'GFS'],
        'leader': 'LITE',
        'thesis': 'Copper wall forcing light'
    },
    'NETWORKING': {
        'tickers': ['ANET', 'CRDO', 'FN', 'CIEN'],
        'leader': 'ANET',
        'thesis': 'Data center interconnects'
    },
    'STORAGE': {
        'tickers': ['MU', 'WDC', 'STX'],
        'leader': 'MU',
        'thesis': 'HBM for AI training'
    },
    'CHIPS_ALT': {
        'tickers': ['AMD', 'MRVL', 'AVGO', 'AMKR'],
        'leader': 'AMD',
        'thesis': 'NVIDIA alternatives rising'
    },
    'QUANTUM': {
        'tickers': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
        'leader': 'IONQ',
        'thesis': 'Speculative/next frontier'
    },
    'SPACE': {
        'tickers': ['LUNR', 'RKLB', 'RDW', 'ASTS', 'SIDU', 'BKSY'],
        'leader': 'RKLB',
        'thesis': 'Defense/satellite buildout'
    },
    'AI_SOFTWARE': {
        'tickers': ['PLTR', 'AI', 'SOUN', 'PATH', 'UPST'],
        'leader': 'PLTR',
        'thesis': 'Enterprise AI adoption'
    },
    'DC_BUILDERS': {
        'tickers': ['SMCI', 'EME', 'CLS', 'FIX'],
        'leader': 'SMCI',
        'thesis': 'Physical buildout'
    }
}

# ============================================================
# ROTATION ANALYSIS FUNCTIONS
# ============================================================

def get_eastern_time():
    eastern = pytz.timezone('US/Eastern')
    return datetime.now(eastern)

def get_sector_momentum(sector_name, tickers):
    """Calculate sector momentum across multiple timeframes"""
    results = []
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1mo', prepost=True)
            
            if len(hist) < 5:
                continue
            
            current = hist['Close'].iloc[-1]
            
            # Multiple timeframes
            changes = {}
            for period, days in [('1d', 1), ('2d', 2), ('5d', 5), ('10d', 10), ('20d', 20)]:
                if len(hist) >= days:
                    prev = hist['Close'].iloc[-days]
                    changes[period] = ((current - prev) / prev) * 100
                else:
                    changes[period] = 0
            
            results.append({
                'ticker': ticker,
                'price': current,
                **changes
            })
            
        except:
            pass
    
    if not results:
        return None
    
    # Aggregate
    df = pd.DataFrame(results)
    return {
        'sector': sector_name,
        'count': len(df),
        '1d': df['1d'].mean(),
        '2d': df['2d'].mean(),
        '5d': df['5d'].mean(),
        '10d': df['10d'].mean(),
        '20d': df['20d'].mean(),
        'momentum_score': df['5d'].mean() * 0.5 + df['2d'].mean() * 0.3 + df['1d'].mean() * 0.2,
        'acceleration': df['2d'].mean() - df['5d'].mean() / 2,  # Is momentum accelerating?
        'tickers': results
    }

def detect_rotation_pattern(sector_data):
    """Detect rotation patterns between sectors"""
    patterns = []
    
    sorted_by_5d = sorted(sector_data, key=lambda x: x['5d'], reverse=True)
    sorted_by_1d = sorted(sector_data, key=lambda x: x['1d'], reverse=True)
    sorted_by_accel = sorted(sector_data, key=lambda x: x['acceleration'], reverse=True)
    
    # Leading sectors (strong 5d, strong 1d)
    leaders = [s for s in sector_data if s['5d'] > 5 and s['1d'] > 0]
    
    # Accelerating sectors (positive acceleration)
    accelerating = [s for s in sector_data if s['acceleration'] > 2]
    
    # Fading sectors (strong 5d but weak 1d)
    fading = [s for s in sector_data if s['5d'] > 5 and s['1d'] < 0]
    
    # Emerging sectors (weak 5d but strong 1d/2d)
    emerging = [s for s in sector_data if s['5d'] < 5 and s['2d'] > 3]
    
    # Lagging (everything negative)
    lagging = [s for s in sector_data if s['5d'] < 0 and s['1d'] < 0]
    
    return {
        'leaders': leaders,
        'accelerating': accelerating,
        'fading': fading,
        'emerging': emerging,
        'lagging': lagging,
        'sorted_momentum': sorted_by_5d,
        'sorted_acceleration': sorted_by_accel
    }

def scan_rotation():
    """Full rotation scan"""
    print("\n⚡ SCANNING SECTOR ROTATION...")
    
    sector_data = []
    
    for sector_name, info in ROTATION_SECTORS.items():
        data = get_sector_momentum(sector_name, info['tickers'])
        if data:
            data['thesis'] = info['thesis']
            sector_data.append(data)
            print(f"   ✓ {sector_name}: {data['5d']:+.1f}% (5d)", end='\r')
    
    print(f"\n   ✓ Scanned {len(sector_data)} sectors")
    
    patterns = detect_rotation_pattern(sector_data)
    
    return sector_data, patterns

def display_rotation(sector_data, patterns, alert_threshold=None):
    """Display rotation analysis"""
    et_now = get_eastern_time()
    
    print("\n" + "=" * 90)
    print(f"🐺 SECTOR ROTATION SCANNER — {et_now.strftime('%I:%M %p ET')}")
    print("=" * 90)
    
    # Momentum ranking
    print("\n📊 SECTOR MOMENTUM RANKING\n")
    print(f"{'Rank':<5} | {'SECTOR':<15} | {'1-DAY':>8} | {'2-DAY':>8} | {'5-DAY':>8} | {'10-DAY':>8} | {'ACCEL':>8} | {'FLOW':<12}")
    print("-" * 90)
    
    for i, s in enumerate(patterns['sorted_momentum'], 1):
        # Flow indicator
        if s['acceleration'] > 3:
            flow = "🚀 SURGING"
        elif s['acceleration'] > 1:
            flow = "📈 INFLOW"
        elif s['acceleration'] > -1:
            flow = "➖ STEADY"
        elif s['acceleration'] > -3:
            flow = "📉 OUTFLOW"
        else:
            flow = "🔴 DUMPING"
        
        print(f"{i:<5} | {s['sector']:<15} | {s['1d']:>+7.1f}% | {s['2d']:>+7.1f}% | {s['5d']:>+7.1f}% | {s['10d']:>+7.1f}% | {s['acceleration']:>+7.1f} | {flow}")
    
    # Rotation patterns
    print("\n" + "=" * 90)
    print("🔄 ROTATION PATTERNS DETECTED")
    print("=" * 90)
    
    if patterns['leaders']:
        print("\n🔥 LEADING SECTORS (Strong 5d + Strong 1d = Money flowing IN)")
        for s in patterns['leaders']:
            print(f"   → {s['sector']}: {s['5d']:+.1f}% (5d), {s['1d']:+.1f}% (1d)")
            print(f"      Thesis: {s['thesis']}")
    
    if patterns['accelerating']:
        print("\n🚀 ACCELERATING (Momentum increasing)")
        for s in patterns['accelerating']:
            print(f"   → {s['sector']}: Acceleration {s['acceleration']:+.1f}")
    
    if patterns['emerging']:
        print("\n🌱 EMERGING (Weak 5d but strong recent = NEW rotation target)")
        for s in patterns['emerging']:
            print(f"   → {s['sector']}: {s['2d']:+.1f}% (2d) vs {s['5d']:+.1f}% (5d)")
    
    if patterns['fading']:
        print("\n⚠️ FADING (Strong 5d but weak 1d = Money leaving)")
        for s in patterns['fading']:
            print(f"   → {s['sector']}: {s['5d']:+.1f}% (5d) but {s['1d']:+.1f}% (1d)")
    
    if patterns['lagging']:
        print("\n❄️ LAGGING (Avoid)")
        for s in patterns['lagging']:
            print(f"   → {s['sector']}: {s['5d']:+.1f}%")
    
    # Top individual tickers
    print("\n" + "=" * 90)
    print("🎯 TOP INDIVIDUAL PLAYS BY SECTOR")
    print("=" * 90)
    
    for s in patterns['sorted_momentum'][:5]:  # Top 5 sectors
        print(f"\n{s['sector']} ({s['5d']:+.1f}% avg):")
        ticker_sorted = sorted(s['tickers'], key=lambda x: x['5d'], reverse=True)
        for t in ticker_sorted[:3]:
            print(f"   {t['ticker']:<6} ${t['price']:>8.2f} | 1d: {t['1d']:>+6.1f}% | 5d: {t['5d']:>+6.1f}%")
    
    # Alerts
    if alert_threshold:
        big_moves = []
        for s in sector_data:
            if abs(s['1d']) >= alert_threshold:
                big_moves.append(s)
        
        if big_moves:
            print("\n" + "🔔" * 20)
            print(f"🚨 SECTOR ALERTS (>{alert_threshold}% 1-day move)")
            for s in big_moves:
                direction = "🟢 UP" if s['1d'] > 0 else "🔴 DOWN"
                print(f"   {s['sector']}: {s['1d']:+.1f}% {direction}")
            print("🔔" * 20)
    
    # Wolf's read
    print("\n" + "=" * 90)
    print("🐺 WOLF'S ROTATION READ")
    print("=" * 90)
    
    leader = patterns['sorted_momentum'][0] if patterns['sorted_momentum'] else None
    laggard = patterns['sorted_momentum'][-1] if patterns['sorted_momentum'] else None
    
    if leader and laggard:
        print(f"""
    MONEY IS ROTATING:
    
    INTO → {leader['sector']} ({leader['5d']:+.1f}%)
           "{leader['thesis']}"
    
    OUT OF → {laggard['sector']} ({laggard['5d']:+.1f}%)
    
    STRATEGY:
    → FOLLOW the leaders, not fight them
    → Watch "emerging" sectors for NEXT rotation
    → Avoid "fading" sectors even if they look strong
    """)

def run_live_scanner(alert_threshold=5, refresh_interval=180):
    """Run in live mode"""
    print("\n🐺 SECTOR ROTATION SCANNER — LIVE MODE")
    print(f"   Alert threshold: {alert_threshold}%")
    print(f"   Refreshing every {refresh_interval} seconds")
    print("   Press Ctrl+C to stop\n")
    
    try:
        while True:
            print("\033[2J\033[H", end="")
            sector_data, patterns = scan_rotation()
            display_rotation(sector_data, patterns, alert_threshold)
            print(f"\n   Next refresh in {refresh_interval} seconds... (Ctrl+C to stop)")
            time.sleep(refresh_interval)
    except KeyboardInterrupt:
        print("\n\n🐺 Scanner stopped.")

def main():
    parser = argparse.ArgumentParser(description='Sector Rotation Scanner')
    parser.add_argument('--live', action='store_true', help='Run in live mode')
    parser.add_argument('--alert', type=float, default=5, help='Alert threshold %%')
    parser.add_argument('--refresh', type=int, default=180, help='Refresh interval')
    
    args = parser.parse_args()
    
    if args.live:
        run_live_scanner(alert_threshold=args.alert, refresh_interval=args.refresh)
    else:
        sector_data, patterns = scan_rotation()
        display_rotation(sector_data, patterns, args.alert)

if __name__ == "__main__":
    main()
