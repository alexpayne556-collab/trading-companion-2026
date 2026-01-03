#!/usr/bin/env python3
"""
🐺 WOLF PACK DASHBOARD v2.0
Designed to run alongside Fidelity ATP
Compact, scannable, real-time signals
"""

import os
import sys
import time
from datetime import datetime
import yfinance as yf
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# =============================================================================
# CONFIGURATION
# =============================================================================

# Core tickers (original pack)
CORE_PACK = ['SIDU', 'RGTI', 'QBTS', 'RCAT', 'LUNR', 'ASTS', 'IONQ']

# Full universe by sector
UNIVERSE = {
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'SPACE': ['LUNR', 'RKLB', 'SIDU', 'ASTS', 'RDW', 'BKSY', 'MNTS'],
    'NUCLEAR': ['SMR', 'OKLO', 'LEU', 'CCJ', 'UUUU', 'NNE'],
    'DEFENSE_AI': ['PLTR', 'RCAT', 'KTOS', 'BBAI', 'AVAV'],
    'AI_INFRA': ['SOUN', 'VRT', 'CORZ', 'PATH', 'UPST'],
    'CRYPTO': ['MARA', 'RIOT', 'CLSK', 'HUT'],
}

# =============================================================================
# COLORS
# =============================================================================

class C:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

def color(text, c):
    return f"{c}{text}{C.RESET}"

# =============================================================================
# SIGNAL DETECTION
# =============================================================================

def get_signals(close, high, low, volume, ticker):
    """Check all 4 validated signals"""
    signals = []
    i = len(close) - 1
    
    if i < 55:
        return signals, {}
    
    # Base metrics
    base_vol = np.mean(volume[max(0, i-20):i])
    rel_vol = volume[i] / base_vol if base_vol > 0 else 1
    
    prev_close = close[i-1]
    daily_chg = ((close[i] - prev_close) / prev_close) * 100
    
    high_20 = max(high[max(0, i-20):i])
    pct_from_high = ((close[i] - high_20) / high_20) * 100
    
    # Up/down volume ratio
    up_vol = sum(volume[j] for j in range(max(0, i-20), i) if close[j] > close[j-1])
    down_vol = sum(volume[j] for j in range(max(0, i-20), i) if close[j] < close[j-1])
    vol_ratio = up_vol / down_vol if down_vol > 0 else 1
    
    # 5-day metrics
    price_5d = ((close[i] - close[max(0, i-5)]) / close[max(0, i-5)]) * 100
    vol_5d = np.mean(volume[max(0, i-5):i])
    vol_ratio_5d = vol_5d / base_vol if base_vol > 0 else 1
    
    # CLV
    clvs = []
    for k in range(max(0, i-5), i):
        day_range = high[k] - low[k]
        if day_range > 0:
            clvs.append((close[k] - low[k]) / day_range)
    avg_clv = np.mean(clvs) if clvs else 0.5
    
    day_range = high[i] - low[i]
    clv_today = (close[i] - low[i]) / day_range if day_range > 0 else 0.5
    
    # 50-day MA
    ma50 = np.mean(close[i-50:i])
    above_ma50 = close[i] > ma50
    
    # 10-day high for pocket pivot
    high_10 = max(high[max(0, i-10):i])
    pct_from_high_10 = ((close[i] - high_10) / high_10) * 100
    
    metrics = {
        'price': float(close[i]),
        'daily_chg': float(daily_chg),
        'pct_from_high': float(pct_from_high),
        'rel_vol': float(rel_vol),
        'vol_ratio': float(vol_ratio),
        'avg_clv': float(avg_clv),
        'clv_today': float(clv_today),
        'above_ma50': above_ma50,
        'pct_from_high_10': float(pct_from_high_10),
    }
    
    # ─────────────────────────────────────────────────────────────────────────
    # SIGNAL 1: WOLF SIGNAL
    # Volume spike + flat + near highs + healthy trend
    # ─────────────────────────────────────────────────────────────────────────
    wolf_vol = rel_vol > 2
    wolf_flat = abs(daily_chg) < 2
    wolf_trend = vol_ratio > 2.5
    wolf_near = pct_from_high > -5
    
    if wolf_vol and wolf_flat and wolf_trend and wolf_near:
        signals.append(('🐺 WOLF', 'STRONG', '+37.87% avg'))
    
    # ─────────────────────────────────────────────────────────────────────────
    # SIGNAL 2: PRE-RUN PREDICTOR
    # 5 criteria score
    # ─────────────────────────────────────────────────────────────────────────
    prerun_score = 0
    if vol_ratio_5d > 1.0: prerun_score += 1
    if rel_vol > 1.0: prerun_score += 1
    if price_5d > -2: prerun_score += 1
    if avg_clv > 0.45: prerun_score += 1
    if vol_ratio > 1.2: prerun_score += 1
    
    if prerun_score == 5:
        signals.append(('📈 PRERUN', 'STRONG', f'5/5 +17.27%'))
    elif prerun_score == 4:
        signals.append(('📈 PRERUN', 'MODERATE', f'4/5'))
    
    metrics['prerun_score'] = prerun_score
    
    # ─────────────────────────────────────────────────────────────────────────
    # SIGNAL 3: CAPITULATION HUNTER
    # Wounded + volume spike + red
    # ─────────────────────────────────────────────────────────────────────────
    cap_wounded = -40 < pct_from_high < -15
    cap_vol = rel_vol > 1.5
    cap_red = clv_today < 0.5
    
    if cap_wounded and cap_vol and cap_red:
        signals.append(('💀 CAPITUL', 'STRONG', '+19.95% avg'))
    elif cap_wounded and (cap_vol or cap_red):
        signals.append(('💀 CAPITUL', 'WATCH', 'wounded'))
    
    # ─────────────────────────────────────────────────────────────────────────
    # SIGNAL 4: POCKET PIVOT (NEW!)
    # Above 50MA + pullback + up day + volume
    # ─────────────────────────────────────────────────────────────────────────
    pp_above = above_ma50
    pp_pullback = -10 < pct_from_high_10 < -3
    pp_up = daily_chg > 0
    
    # Volume > any down day in last 10
    down_vols = [volume[j] for j in range(max(0, i-10), i) if close[j] < close[j-1]]
    max_down_vol = max(down_vols) if down_vols else 0
    pp_vol = volume[i] > max_down_vol
    
    if pp_above and pp_pullback and pp_up and pp_vol:
        signals.append(('🎯 POCKET', 'STRONG', '+9.61% avg'))
    elif pp_above and pp_pullback:
        signals.append(('🎯 POCKET', 'SETUP', 'pullback'))
    
    return signals, metrics


def fetch_data(tickers):
    """Fetch data efficiently"""
    data = {}
    df = yf.download(tickers, period='3mo', progress=False, group_by='ticker')
    
    for ticker in tickers:
        try:
            if len(tickers) == 1:
                ticker_df = df
            else:
                ticker_df = df[ticker]
            
            ticker_df = ticker_df.dropna()
            if len(ticker_df) >= 55:
                data[ticker] = ticker_df
        except:
            continue
    
    return data


def get_sector(ticker):
    """Get sector for a ticker"""
    for sector, tickers in UNIVERSE.items():
        if ticker in tickers:
            return sector
    return 'OTHER'


# =============================================================================
# DISPLAY
# =============================================================================

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')


def display_dashboard(data, mode='core'):
    """Main dashboard display"""
    
    clear_screen()
    
    now = datetime.now().strftime('%H:%M:%S')
    
    print(color("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     🐺 WOLF PACK SIGNAL DASHBOARD                            ║
╚══════════════════════════════════════════════════════════════════════════════╝""", C.CYAN))
    print(color(f"  Last Scan: {now}  |  Mode: {mode.upper()}  |  [R]efresh [W]ide [C]ore [Q]uit", C.DIM))
    
    # Collect all results
    results = []
    all_signals = []
    
    for ticker, df in data.items():
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        volume = df['Volume'].values
        
        signals, metrics = get_signals(close, high, low, volume, ticker)
        
        results.append({
            'ticker': ticker,
            'sector': get_sector(ticker),
            'signals': signals,
            'metrics': metrics
        })
        
        for sig in signals:
            all_signals.append((ticker, sig, metrics))
    
    # Sort by daily change
    results.sort(key=lambda x: x['metrics'].get('daily_chg', 0), reverse=True)
    
    # ─────────────────────────────────────────────────────────────────────────
    # ACTIVE SIGNALS BOX
    # ─────────────────────────────────────────────────────────────────────────
    
    strong_signals = [s for s in all_signals if s[1][1] == 'STRONG']
    watch_signals = [s for s in all_signals if s[1][1] in ['MODERATE', 'SETUP', 'WATCH']]
    
    print(color("\n┌─────────────────────────── ACTIVE SIGNALS ───────────────────────────┐", C.GREEN))
    
    if strong_signals:
        for ticker, (sig_type, strength, note), metrics in strong_signals:
            price = metrics['price']
            chg = metrics['daily_chg']
            arrow = color("▲", C.GREEN) if chg > 0 else color("▼", C.RED)
            print(color(f"│ ⭐ {sig_type:10} {ticker:6} ${price:>8.2f} {arrow}{abs(chg):>5.1f}%  {note:<15} │", C.GREEN))
    else:
        print(color("│  No strong signals right now                                         │", C.DIM))
    
    if watch_signals:
        print(color("│" + "─"*72 + "│", C.DIM))
        for ticker, (sig_type, strength, note), metrics in watch_signals[:5]:
            price = metrics['price']
            chg = metrics['daily_chg']
            arrow = "▲" if chg > 0 else "▼"
            print(color(f"│  ○ {sig_type:10} {ticker:6} ${price:>8.2f} {arrow}{abs(chg):>5.1f}%  {strength}: {note:<10} │", C.DIM))
    
    print(color("└──────────────────────────────────────────────────────────────────────┘", C.GREEN))
    
    # ─────────────────────────────────────────────────────────────────────────
    # MARKET TABLE
    # ─────────────────────────────────────────────────────────────────────────
    
    print(color("\n┌────────────────────────── MARKET STATUS ─────────────────────────────┐", C.CYAN))
    print(color("│  TICKER   PRICE    DAY%   HIGH%   VOL   PRE  STATUS                  │", C.WHITE))
    print(color("│" + "─"*72 + "│", C.DIM))
    
    for r in results[:20]:
        ticker = r['ticker']
        m = r['metrics']
        signals = r['signals']
        
        price = m['price']
        chg = m['daily_chg']
        from_hi = m['pct_from_high']
        vol = m['rel_vol']
        prerun = m.get('prerun_score', 0)
        
        # Color based on change
        if chg > 5:
            row_color = C.GREEN
        elif chg < -5:
            row_color = C.RED
        else:
            row_color = C.WHITE
        
        # Status
        status = ""
        if signals:
            status = signals[0][0]
        elif from_hi > -5:
            status = "🟢 Near High"
        elif from_hi > -15:
            status = "🟡 Pullback"
        elif from_hi > -30:
            status = "🟠 Wounded"
        else:
            status = "🔴 Crushed"
        
        # Volume indicator
        vol_ind = "🔥" if vol > 2 else "📊" if vol > 1.5 else "  "
        
        arrow = "▲" if chg > 0 else "▼"
        print(color(f"│  {ticker:<6} ${price:>7.2f}  {arrow}{abs(chg):>5.1f}%  {from_hi:>5.1f}%  {vol:>4.1f}x {prerun}/5  {status:<12} │", row_color))
    
    print(color("└──────────────────────────────────────────────────────────────────────┘", C.CYAN))
    
    # ─────────────────────────────────────────────────────────────────────────
    # SECTOR HEAT
    # ─────────────────────────────────────────────────────────────────────────
    
    print(color("\n┌─────────────────────────── SECTOR HEAT ──────────────────────────────┐", C.YELLOW))
    
    for sector, tickers in UNIVERSE.items():
        sector_results = [r for r in results if r['sector'] == sector]
        if sector_results:
            avg_chg = np.mean([r['metrics']['daily_chg'] for r in sector_results])
            bar_len = min(20, max(0, int(abs(avg_chg))))
            bar = "█" * bar_len
            
            if avg_chg > 3:
                sc = C.GREEN
                emoji = "🔥"
            elif avg_chg > 0:
                sc = C.GREEN
                emoji = "📈"
            elif avg_chg > -3:
                sc = C.RED
                emoji = "📉"
            else:
                sc = C.RED
                emoji = "💀"
            
            print(color(f"│  {sector:<12} {avg_chg:>+6.1f}% {bar:<20} {emoji}                    │", sc))
    
    print(color("└──────────────────────────────────────────────────────────────────────┘", C.YELLOW))
    
    # ─────────────────────────────────────────────────────────────────────────
    # SIGNAL REFERENCE
    # ─────────────────────────────────────────────────────────────────────────
    
    print(color("""
┌─────────────────────────── SIGNAL GUIDE ─────────────────────────────┐
│  🐺 WOLF    = Vol spike + flat + near highs     p=0.023  +37.87%     │
│  📈 PRERUN  = 5 criteria score before runs      p=0.000  +17.27%     │
│  💀 CAPITUL = Red spike when wounded            p=0.004  +19.95%     │
│  🎯 POCKET  = Buy dip in uptrend + volume       p=0.000  +9.61%      │
└──────────────────────────────────────────────────────────────────────┘""", C.DIM))
    
    print(color("\n  🐺 AWOOOO!", C.YELLOW))


# =============================================================================
# MAIN
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='🐺 Wolf Pack Dashboard')
    parser.add_argument('--auto', '-a', action='store_true', help='Auto-refresh mode')
    parser.add_argument('--wide', '-w', action='store_true', help='Wide mode (all tickers)')
    parser.add_argument('--interval', '-i', type=int, default=60, help='Refresh interval')
    
    args = parser.parse_args()
    
    # Determine tickers
    if args.wide:
        tickers = []
        for sector_tickers in UNIVERSE.values():
            tickers.extend(sector_tickers)
        tickers = list(set(tickers))
        mode = 'wide'
    else:
        tickers = CORE_PACK
        mode = 'core'
    
    print(f"  Loading {len(tickers)} tickers...")
    data = fetch_data(tickers)
    
    if args.auto:
        while True:
            try:
                display_dashboard(data, mode)
                print(f"\n  Auto-refresh in {args.interval}s... (Ctrl+C to stop)")
                time.sleep(args.interval)
                data = fetch_data(tickers)
            except KeyboardInterrupt:
                print("\n\n  🐺 Dashboard stopped. AWOOOO!")
                break
    else:
        while True:
            display_dashboard(data, mode)
            
            try:
                cmd = input("\n  Command: ").strip().upper()
                
                if cmd == 'Q':
                    print("\n  🐺 AWOOOO!")
                    break
                elif cmd == 'R':
                    print("  Refreshing...")
                    data = fetch_data(tickers)
                elif cmd == 'W':
                    tickers = []
                    for sector_tickers in UNIVERSE.values():
                        tickers.extend(sector_tickers)
                    tickers = list(set(tickers))
                    mode = 'wide'
                    print(f"  Loading {len(tickers)} tickers...")
                    data = fetch_data(tickers)
                elif cmd == 'C':
                    tickers = CORE_PACK
                    mode = 'core'
                    print(f"  Loading {len(tickers)} tickers...")
                    data = fetch_data(tickers)
                    
            except KeyboardInterrupt:
                print("\n\n  🐺 AWOOOO!")
                break


if __name__ == '__main__':
    main()
