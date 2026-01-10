#!/usr/bin/env python3
"""
🐺 COMPLETE FENRIR EDGE VERIFICATION
Test all 12 claimed edges with real data
No bullshit. Just numbers.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_rsi(series, period=14):
    """Calculate RSI indicator"""
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def load_ticker(ticker, period='2y'):
    """Load and prepare ticker data"""
    df = yf.download(ticker, period=period, progress=False)
    if df.empty:
        return None
    
    # Handle multi-index columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Calculate indicators
    df['Return'] = df['Close'].pct_change() * 100
    df['RSI'] = calculate_rsi(df['Close'])
    df['Vol_Avg'] = df['Volume'].rolling(20).mean()
    df['Vol_Ratio'] = df['Volume'] / df['Vol_Avg']
    df['Gap'] = ((df['Open'] - df['Close'].shift(1)) / df['Close'].shift(1)) * 100
    df['Ret_5d'] = df['Close'].pct_change(5) * 100
    df['Next_Return'] = df['Return'].shift(-1)
    df['Prev_Close'] = df['Close'].shift(1)
    df['Overnight'] = (df['Open'] - df['Prev_Close']) / df['Prev_Close'] * 100
    df['Intraday'] = (df['Close'] - df['Open']) / df['Open'] * 100
    df['DayOfWeek'] = df.index.dayofweek
    
    return df

def print_verdict(edge_name, win_rate, events, claimed_rate=None):
    """Print verdict for an edge"""
    print(f"\n{'='*70}")
    print(f"EDGE: {edge_name}")
    print(f"{'='*70}")
    print(f"Events: {events}")
    print(f"Win Rate: {win_rate:.1f}%")
    if claimed_rate:
        print(f"Claimed: {claimed_rate}%")
    
    if events < 10:
        print(f"⚠️  SMALL SAMPLE - Not enough data")
        return "INSUFFICIENT"
    elif win_rate >= 60:
        if claimed_rate and abs(win_rate - claimed_rate) > 10:
            print(f"✅ EDGE EXISTS but claimed rate off by {abs(win_rate-claimed_rate):.0f}%")
            return "EDGE (RATE WRONG)"
        else:
            print(f"✅ VERIFIED EDGE")
            return "VERIFIED"
    else:
        print(f"❌ NOT AN EDGE - Below 60%")
        return "FAILED"

# ============================================================================
# EDGE 1: OVERNIGHT > INTRADAY
# ============================================================================

def test_overnight_edge():
    """Test if overnight beats intraday"""
    print("\n" + "="*70)
    print("EDGE #1: OVERNIGHT > INTRADAY")
    print("="*70)
    
    results = []
    
    for ticker in ['WULF', 'SMR', 'DNN', 'NVDA', 'AMD']:
        df = load_ticker(ticker, period='2y')
        if df is None:
            continue
        
        overnight = df['Overnight'].sum()
        intraday = df['Intraday'].sum()
        
        results.append({
            'Ticker': ticker,
            'Overnight': f"{overnight:+.1f}%",
            'Intraday': f"{intraday:+.1f}%",
            'Winner': 'Overnight' if overnight > intraday else 'Intraday'
        })
    
    df_results = pd.DataFrame(results)
    print("\n" + df_results.to_string(index=False))
    
    overnight_wins = sum(1 for r in results if r['Winner'] == 'Overnight')
    print(f"\nOvernight wins: {overnight_wins}/{len(results)} tickers")
    
    if overnight_wins >= 4:
        print("✅ VERIFIED: Overnight dominates")
        return "VERIFIED"
    else:
        print("❌ NOT VERIFIED")
        return "FAILED"

# ============================================================================
# EDGE 2: DNN RELATIVE STRENGTH (Claimed 86%)
# ============================================================================

def test_dnn_relative_strength():
    """Test DNN up when SPY down"""
    dnn = load_ticker('DNN', period='1y')
    spy = load_ticker('SPY', period='1y')
    
    if dnn is None or spy is None:
        return "NO DATA"
    
    merged = dnn[['Return', 'Next_Return', 'RSI']].join(spy[['Return']].rename(columns={'Return': 'SPY_Return'}), how='inner')
    
    # Condition: DNN up >1%, SPY down >0.5%
    condition = (merged['Return'] > 1) & (merged['SPY_Return'] < -0.5)
    events = merged[condition].dropna(subset=['Next_Return'])
    
    wins = (events['Next_Return'] > 0).sum()
    total = len(events)
    win_rate = (wins / total * 100) if total > 0 else 0
    
    return print_verdict("DNN Relative Strength", win_rate, total, 86)

# ============================================================================
# EDGE 3: BTC LEADS AI INFRA (Claimed 80%)
# ============================================================================

def test_btc_leads_ai():
    """Test if BTC up 5%+ predicts AI infra"""
    btc = load_ticker('BTC-USD', period='1y')
    
    if btc is None:
        return "NO DATA"
    
    # BTC up 5%+ days
    big_days = btc[btc['Return'] >= 5.0].index
    
    results = []
    for ticker in ['WULF', 'CLSK', 'CIFR', 'BTBT']:
        df = load_ticker(ticker, period='1y')
        if df is None:
            continue
        
        wins = 0
        total = 0
        
        for date in big_days:
            if date not in df.index:
                continue
            
            same_day = df.loc[date, 'Return']
            if same_day > 0:
                wins += 1
            total += 1
        
        if total > 0:
            results.append({'Ticker': ticker, 'Wins': wins, 'Total': total, 'Rate': f"{wins/total*100:.0f}%"})
    
    if not results:
        return "NO DATA"
    
    total_wins = sum(r['Wins'] for r in results)
    total_events = sum(r['Total'] for r in results)
    win_rate = (total_wins / total_events * 100) if total_events > 0 else 0
    
    print(f"\nBTC big days: {len(big_days)}")
    print(pd.DataFrame(results).to_string(index=False))
    
    return print_verdict("BTC Leads AI Infra", win_rate, total_events, 80)

# ============================================================================
# EDGE 4: WULF WEAK CLOSE BOUNCE (Claimed 78%)
# ============================================================================

def test_wulf_weak_close():
    """Test WULF bounce after closing in bottom 25% of range"""
    wulf = load_ticker('WULF', period='1y')
    
    if wulf is None:
        return "NO DATA"
    
    # Close in bottom 25% of day's range
    wulf['Range'] = wulf['High'] - wulf['Low']
    wulf['Close_Position'] = (wulf['Close'] - wulf['Low']) / wulf['Range']
    
    weak_closes = wulf[wulf['Close_Position'] < 0.25].dropna(subset=['Next_Return'])
    
    wins = (weak_closes['Next_Return'] > 0).sum()
    total = len(weak_closes)
    win_rate = (wins / total * 100) if total > 0 else 0
    
    return print_verdict("WULF Weak Close Bounce", win_rate, total, 78)

# ============================================================================
# EDGE 5: WULF 5-DAY CRASH BOUNCE (Claimed 76%)
# ============================================================================

def test_wulf_crash_bounce():
    """Test WULF bounce after 15%+ 5-day drop"""
    wulf = load_ticker('WULF', period='2y')
    
    if wulf is None:
        return "NO DATA"
    
    crashes = wulf[wulf['Ret_5d'] <= -15].dropna(subset=['Next_Return'])
    
    wins = (crashes['Next_Return'] > 0).sum()
    total = len(crashes)
    win_rate = (wins / total * 100) if total > 0 else 0
    
    return print_verdict("WULF 5-Day Crash Bounce", win_rate, total, 76)

# ============================================================================
# EDGE 6: UEC RELATIVE STRENGTH (Claimed 74%)
# ============================================================================

def test_uec_relative_strength():
    """Test UEC up when SPY down"""
    uec = load_ticker('UEC', period='1y')
    spy = load_ticker('SPY', period='1y')
    
    if uec is None or spy is None:
        return "NO DATA"
    
    merged = uec[['Return', 'Next_Return']].join(spy[['Return']].rename(columns={'Return': 'SPY_Return'}), how='inner')
    
    condition = (merged['Return'] > 1) & (merged['SPY_Return'] < -0.5)
    events = merged[condition].dropna(subset=['Next_Return'])
    
    wins = (events['Next_Return'] > 0).sum()
    total = len(events)
    win_rate = (wins / total * 100) if total > 0 else 0
    
    return print_verdict("UEC Relative Strength", win_rate, total, 74)

# ============================================================================
# EDGE 7: UEC COMBO (RSI<40 + VOL + DOWN) (Claimed 67%)
# ============================================================================

def test_uec_combo():
    """Test UEC combo signal"""
    uec = load_ticker('UEC', period='1y')
    
    if uec is None:
        return "NO DATA"
    
    # Combo: RSI < 40, Volume 2x+, Down day
    condition = (uec['RSI'] < 40) & (uec['Vol_Ratio'] > 2) & (uec['Return'] < 0)
    events = uec[condition].dropna(subset=['Next_Return'])
    
    wins = (events['Next_Return'] > 0).sum()
    total = len(events)
    win_rate = (wins / total * 100) if total > 0 else 0
    
    return print_verdict("UEC Combo Signal", win_rate, total, 67)

# ============================================================================
# EDGE 8: CIFR RELATIVE STRENGTH (Claimed 67%)
# ============================================================================

def test_cifr_relative_strength():
    """Test CIFR up when SPY down"""
    cifr = load_ticker('CIFR', period='1y')
    spy = load_ticker('SPY', period='1y')
    
    if cifr is None or spy is None:
        return "NO DATA"
    
    merged = cifr[['Return', 'Next_Return']].join(spy[['Return']].rename(columns={'Return': 'SPY_Return'}), how='inner')
    
    condition = (merged['Return'] > 1) & (merged['SPY_Return'] < -0.5)
    events = merged[condition].dropna(subset=['Next_Return'])
    
    wins = (events['Next_Return'] > 0).sum()
    total = len(events)
    win_rate = (wins / total * 100) if total > 0 else 0
    
    return print_verdict("CIFR Relative Strength", win_rate, total, 67)

# ============================================================================
# EDGE 9: SMR FADE AFTER 5-DAY RUN (Claimed 69%)
# ============================================================================

def test_smr_fade():
    """Test fading SMR after big run"""
    smr = load_ticker('SMR', period='1y')
    
    if smr is None:
        return "NO DATA"
    
    # After 15%+ 5-day gain, next day tends to reverse
    big_runs = smr[smr['Ret_5d'] >= 15].dropna(subset=['Next_Return'])
    
    # Fade = bet on down day
    wins = (big_runs['Next_Return'] < 0).sum()
    total = len(big_runs)
    win_rate = (wins / total * 100) if total > 0 else 0
    
    return print_verdict("SMR Fade After Run", win_rate, total, 69)

# ============================================================================
# EDGE 10: CIFR FADE WIDE UP DAY (Claimed 83%)
# ============================================================================

def test_cifr_fade_wide():
    """Test fading CIFR after wide up day"""
    cifr = load_ticker('CIFR', period='1y')
    
    if cifr is None:
        return "NO DATA"
    
    # Wide up day: Up 10%+ with wide range
    cifr['Range_Pct'] = (cifr['High'] - cifr['Low']) / cifr['Close'] * 100
    
    condition = (cifr['Return'] >= 10) & (cifr['Range_Pct'] > 15)
    events = cifr[condition].dropna(subset=['Next_Return'])
    
    # Fade = bet on down
    wins = (events['Next_Return'] < 0).sum()
    total = len(events)
    win_rate = (wins / total * 100) if total > 0 else 0
    
    return print_verdict("CIFR Fade Wide Up", win_rate, total, 83)

# ============================================================================
# EDGE 11: URA LEADS DNN BY 1 DAY (Claimed 64%)
# ============================================================================

def test_ura_leads_dnn():
    """Test if URA predicts DNN next day"""
    ura = load_ticker('URA', period='1y')
    dnn = load_ticker('DNN', period='1y')
    
    if ura is None or dnn is None:
        return "NO DATA"
    
    # URA up 3%+, predict DNN next day
    big_days = ura[ura['Return'] >= 3].index
    
    wins = 0
    total = 0
    
    for date in big_days:
        try:
            ura_loc = ura.index.get_loc(date)
            if ura_loc + 1 >= len(ura):
                continue
            next_date = ura.index[ura_loc + 1]
            
            if next_date in dnn.index:
                dnn_next = dnn.loc[next_date, 'Return']
                if dnn_next > 0:
                    wins += 1
                total += 1
        except:
            continue
    
    win_rate = (wins / total * 100) if total > 0 else 0
    
    return print_verdict("URA Leads DNN (1 day)", win_rate, total, 64)

# ============================================================================
# EDGE 12: SMR TUESDAY OVERNIGHT (Claimed 63%)
# ============================================================================

def test_smr_tuesday():
    """Test SMR Tuesday overnight edge"""
    smr = load_ticker('SMR', period='1y')
    
    if smr is None:
        return "NO DATA"
    
    # Buy Monday close, sell Tuesday open
    # DayOfWeek: 0=Mon, 1=Tue
    tuesdays = smr[smr['DayOfWeek'] == 1].copy()
    
    wins = (tuesdays['Overnight'] > 0).sum()
    total = len(tuesdays)
    win_rate = (wins / total * 100) if total > 0 else 0
    
    return print_verdict("SMR Tuesday Overnight", win_rate, total, 63)

# ============================================================================
# EDGE 13: WEDNESDAY BEST DAY (Claimed 55%)
# ============================================================================

def test_wednesday_edge():
    """Test if Wednesday is best day"""
    tickers = ['DNN', 'UEC', 'WULF', 'SMR', 'CIFR', 'CLSK']
    
    day_results = {day: {'wins': 0, 'total': 0} for day in range(5)}
    
    for ticker in tickers:
        df = load_ticker(ticker, period='1y')
        if df is None:
            continue
        
        for day in range(5):
            day_data = df[df['DayOfWeek'] == day]
            day_results[day]['wins'] += (day_data['Return'] > 0).sum()
            day_results[day]['total'] += len(day_data)
    
    print(f"\n{'='*70}")
    print("EDGE #13: WEDNESDAY BEST DAY")
    print(f"{'='*70}")
    
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    best_rate = 0
    best_day = None
    
    for day in range(5):
        wins = day_results[day]['wins']
        total = day_results[day]['total']
        rate = (wins / total * 100) if total > 0 else 0
        
        print(f"{day_names[day]:10}: {wins}/{total} = {rate:.1f}%")
        
        if rate > best_rate:
            best_rate = rate
            best_day = day_names[day]
    
    print(f"\nBest day: {best_day} ({best_rate:.1f}%)")
    print(f"Claimed: Wednesday (55%)")
    
    if best_day == 'Wednesday' and best_rate >= 55:
        print("✅ VERIFIED")
        return "VERIFIED"
    else:
        print(f"❌ WRONG - {best_day} is best, not Wednesday")
        return "FAILED"

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*70)
    print("🐺 FENRIR EDGE VERIFICATION LAB")
    print("Testing all 12 claimed edges")
    print("="*70)
    
    results = {}
    
    print("\n" + "⏳ Running tests...")
    
    results['Overnight > Intraday'] = test_overnight_edge()
    results['DNN Relative Strength'] = test_dnn_relative_strength()
    results['BTC Leads AI Infra'] = test_btc_leads_ai()
    results['WULF Weak Close'] = test_wulf_weak_close()
    results['WULF 5-Day Crash'] = test_wulf_crash_bounce()
    results['UEC Relative Strength'] = test_uec_relative_strength()
    results['UEC Combo Signal'] = test_uec_combo()
    results['CIFR Relative Strength'] = test_cifr_relative_strength()
    results['SMR Fade Run'] = test_smr_fade()
    results['CIFR Fade Wide'] = test_cifr_fade_wide()
    results['URA Leads DNN'] = test_ura_leads_dnn()
    results['SMR Tuesday'] = test_smr_tuesday()
    results['Wednesday Best'] = test_wednesday_edge()
    
    # Final summary
    print("\n" + "="*70)
    print("🐺 FINAL VERDICT")
    print("="*70)
    
    verified = sum(1 for v in results.values() if v == "VERIFIED")
    failed = sum(1 for v in results.values() if v == "FAILED")
    insufficient = sum(1 for v in results.values() if v == "INSUFFICIENT")
    
    for edge, result in results.items():
        symbol = "✅" if result == "VERIFIED" else "❌" if result == "FAILED" else "⚠️"
        print(f"{symbol} {edge:30} {result}")
    
    print(f"\n{'='*70}")
    print(f"VERIFIED: {verified}/{len(results)}")
    print(f"FAILED: {failed}/{len(results)}")
    print(f"INSUFFICIENT DATA: {insufficient}/{len(results)}")
    print(f"{'='*70}")
    
    accuracy = (verified / len(results) * 100) if len(results) > 0 else 0
    print(f"\nFENRIR ACCURACY: {accuracy:.0f}%")
    
    if accuracy >= 70:
        print("✅ FENRIR'S RESEARCH IS LEGIT")
    elif accuracy >= 50:
        print("⚠️ MIXED RESULTS - Some edges work, some don't")
    else:
        print("❌ MOST CLAIMS DON'T HOLD UP")
    
    print("\n🐺 LLHR. DATA > CLAIMS. AWOOOO.")

if __name__ == "__main__":
    main()
