#!/usr/bin/env python3
"""
🐺 BROKKR VERIFICATION ENGINE
Testing Fenrir's research claims with ACTUAL DATA
January 10, 2026
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 200)

print("="*70)
print("🐺 BROKKR VERIFICATION ENGINE")
print("Testing Fenrir's Claims with Real Data")
print("="*70)

# =============================================================================
# LOAD DATA
# =============================================================================

TICKERS = {
    'nuclear': ['DNN', 'UEC', 'UUUU', 'SMR', 'CCJ', 'URG'],
    'ai_infra': ['CIFR', 'WULF', 'CLSK', 'BTBT', 'APLD', 'IREN'],
}

ALL_TICKERS = [t for sector in TICKERS.values() for t in sector]

print(f"\n📊 Loading data for {len(ALL_TICKERS)} tickers...")

data = {}
for ticker in ALL_TICKERS:
    try:
        df = yf.download(ticker, period='180d', interval='1d', progress=False)
        if not df.empty:
            # Flatten multi-index columns if needed
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Calculate RSI
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Calculate returns
            df['Return'] = df['Close'].pct_change() * 100
            df['Return_5d'] = ((df['Close'] / df['Close'].shift(5)) - 1) * 100
            
            # Volume ratio
            vol_avg = df['Volume'].rolling(20).mean()
            df['Vol_Ratio'] = df['Volume'] / vol_avg
            
            # Gap
            df['Gap'] = ((df['Open'] - df['Close'].shift(1)) / df['Close'].shift(1)) * 100
            
            # Day of week
            df['DayOfWeek'] = df.index.dayofweek
            
            # Consecutive days
            df['Green'] = df['Return'] > 0
            df['Consec_Green'] = df['Green'].groupby((~df['Green']).cumsum()).cumsum()
            
            data[ticker] = df
            print(f"  ✓ {ticker}: {len(df)} days, current ${df['Close'].iloc[-1]:.2f}")
    except Exception as e:
        print(f"  ✗ {ticker}: {e}")

print(f"\n✅ Loaded {len(data)} tickers\n")

# =============================================================================
# TEST 1: Current RSI Status
# =============================================================================

print("="*70)
print("🔬 TEST 1: Current RSI Status")
print("Fenrir claimed: Nuclear RSI 73-91 (overbought), AI Infra 53-60 (neutral)")
print("="*70)

current_status = []
for ticker, df in data.items():
    current_rsi = df['RSI'].iloc[-1]
    current_price = df['Close'].iloc[-1]
    ret_5d = df['Return_5d'].iloc[-1]
    
    if current_rsi > 70:
        status = '🔴 OVERBOUGHT'
    elif current_rsi < 30:
        status = '🟢 OVERSOLD'
    elif current_rsi < 40:
        status = '🟡 LOW'
    else:
        status = '⚪ NEUTRAL'
    
    sector = 'Nuclear' if ticker in TICKERS['nuclear'] else 'AI Infra'
    
    current_status.append({
        'Ticker': ticker,
        'Sector': sector,
        'Price': current_price,
        'RSI': current_rsi,
        'Status': status,
        '5D%': ret_5d
    })

status_df = pd.DataFrame(current_status).sort_values('RSI', ascending=False)
print(f"\n{status_df.to_string(index=False)}\n")

# Verdict
nuclear_rsis = [x['RSI'] for x in current_status if x['Sector'] == 'Nuclear']
ai_rsis = [x['RSI'] for x in current_status if x['Sector'] == 'AI Infra']

print(f"📊 VERDICT:")
print(f"   Nuclear avg RSI: {np.mean(nuclear_rsis):.1f}")
print(f"   AI Infra avg RSI: {np.mean(ai_rsis):.1f}")

if np.mean(nuclear_rsis) > 70:
    print(f"   ✅ FENRIR CORRECT: Nuclear is overbought\n")
else:
    print(f"   ❌ FENRIR WRONG: Nuclear not overbought\n")

# =============================================================================
# TEST 2: RSI < 30 Bounce
# =============================================================================

print("="*70)
print("🔬 TEST 2: RSI < 30 Bounce Pattern")
print("Fenrir claimed: ~51% win rate (NO EDGE)")
print("="*70)

rsi_results = []

for ticker, df in data.items():
    signals = df[df['RSI'] < 30].copy()
    
    if len(signals) == 0:
        continue
    
    wins = 0
    total = 0
    returns = []
    
    for idx in signals.index:
        try:
            loc = df.index.get_loc(idx)
            if loc + 5 < len(df):
                future_ret = ((df['Close'].iloc[loc + 5] - df['Close'].iloc[loc]) / df['Close'].iloc[loc]) * 100
                returns.append(future_ret)
                if future_ret > 5:
                    wins += 1
                total += 1
        except:
            pass
    
    if total > 0:
        win_rate = (wins / total) * 100
        avg_return = np.mean(returns)
        
        rsi_results.append({
            'Ticker': ticker,
            'Events': total,
            'Wins': wins,
            'Win_Rate': win_rate,
            'Avg_Return': avg_return
        })

if rsi_results:
    rsi_df = pd.DataFrame(rsi_results)
    print(f"\n{rsi_df.to_string(index=False)}\n")
    
    total_events = rsi_df['Events'].sum()
    total_wins = rsi_df['Wins'].sum()
    agg_win_rate = (total_wins / total_events) * 100 if total_events > 0 else 0
    
    print(f"📊 AGGREGATE:")
    print(f"   Total events: {total_events}")
    print(f"   Total wins: {total_wins}")
    print(f"   Win rate: {agg_win_rate:.1f}%")
    
    if agg_win_rate < 60:
        print(f"   ✅ FENRIR CORRECT: RSI < 30 is NOT an edge ({agg_win_rate:.0f}% < 60%)\n")
    else:
        print(f"   ❌ FENRIR WRONG: RSI < 30 IS an edge ({agg_win_rate:.0f}% > 60%)\n")

# =============================================================================
# TEST 3: WULF Drop Bounce
# =============================================================================

print("="*70)
print("🔬 TEST 3: WULF Drop Bounce Pattern")
print("Fenrir claimed: 64% win rate after -5% drop")
print("="*70)

if 'WULF' in data:
    wulf = data['WULF']
    big_drops = wulf[wulf['Return'] <= -5.0].copy()
    
    wins = 0
    total = 0
    returns = []
    
    for idx in big_drops.index:
        try:
            loc = wulf.index.get_loc(idx)
            if loc + 1 < len(wulf):
                next_ret = wulf['Return'].iloc[loc + 1]
                returns.append(next_ret)
                if next_ret > 0:
                    wins += 1
                total += 1
        except:
            pass
    
    if total > 0:
        win_rate = (wins / total) * 100
        avg_return = np.mean(returns)
        
        print(f"\nEvents (WULF -5%+ drops): {total}")
        print(f"Next day green: {wins}/{total}")
        print(f"Win rate: {win_rate:.1f}%")
        print(f"Avg next day: {avg_return:+.2f}%")
        
        if 60 <= win_rate <= 70:
            print(f"\n✅ FENRIR CORRECT: WULF bounces ~{win_rate:.0f}%\n")
        else:
            print(f"\n⚠️ VERIFICATION: Claimed 64%, actual {win_rate:.0f}%\n")

# =============================================================================
# TEST 4: DNN Gap Continuation
# =============================================================================

print("="*70)
print("🔬 TEST 4: DNN Gap Continuation Pattern")
print("Fenrir claimed: 67% continuation rate on 3%+ gaps")
print("="*70)

if 'DNN' in data:
    dnn = data['DNN']
    gap_ups = dnn[dnn['Gap'] >= 3.0].copy()
    
    continued = 0
    filled = 0
    total = 0
    
    for idx in gap_ups.index:
        try:
            close_price = dnn.loc[idx, 'Close']
            open_price = dnn.loc[idx, 'Open']
            
            if close_price > open_price:
                continued += 1
            else:
                filled += 1
            total += 1
        except:
            pass
    
    if total > 0:
        continue_rate = (continued / total) * 100
        fill_rate = (filled / total) * 100
        
        print(f"\nGap up 3%+ events: {total}")
        print(f"Continued (close > open): {continued}/{total} = {continue_rate:.0f}%")
        print(f"Filled (close < open): {filled}/{total} = {fill_rate:.0f}%")
        
        if 60 <= continue_rate <= 75:
            print(f"\n✅ FENRIR CORRECT: DNN gaps continue ~{continue_rate:.0f}%\n")
        else:
            print(f"\n⚠️ VERIFICATION: Claimed 67%, actual {continue_rate:.0f}%\n")
    else:
        print("\nNo gap up events in 180-day period\n")

# =============================================================================
# TEST 5: Day of Week
# =============================================================================

print("="*70)
print("🔬 TEST 5: Day of Week Performance")
print("Fenrir claimed: Wednesday best day (55% win rate, +1.09% avg)")
print("="*70)

dow_results = []

for day in range(5):
    day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][day]
    
    all_returns = []
    wins = 0
    total = 0
    
    for ticker, df in data.items():
        day_data = df[df['DayOfWeek'] == day]['Return'].dropna()
        all_returns.extend(day_data.tolist())
        wins += (day_data > 0).sum()
        total += len(day_data)
    
    if total > 0:
        avg_return = np.mean(all_returns)
        win_rate = (wins / total) * 100
        
        dow_results.append({
            'Day': day_name,
            'Count': total,
            'Wins': wins,
            'Win_Rate': win_rate,
            'Avg_Return': avg_return
        })

if dow_results:
    dow_df = pd.DataFrame(dow_results)
    print(f"\n{dow_df.to_string(index=False)}\n")
    
    best_day_idx = dow_df['Avg_Return'].argmax()
    best_day = dow_df.iloc[best_day_idx]
    print(f"📊 Best day: {best_day['Day']} ({best_day['Win_Rate']:.1f}% win rate, {best_day['Avg_Return']:+.2f}% avg)")
    
    if 'Wednesday' in best_day['Day']:
        print(f"✅ FENRIR CORRECT: Wednesday is best day\n")
    else:
        print(f"⚠️ VERIFICATION: Best day is {best_day['Day']}, not Wednesday\n")

# =============================================================================
# TEST 6: Leader/Laggard Correlation
# =============================================================================

print("="*70)
print("🔬 TEST 6: CCJ Leader → DNN/UEC Laggard")
print("Fenrir claimed: Same day correlation ~96%, next day ~50% (no edge)")
print("="*70)

if 'CCJ' in data and 'DNN' in data and 'UEC' in data:
    ccj = data['CCJ']
    ccj_big_days = ccj[ccj['Return'] >= 3.0].index
    
    print(f"\nCCJ big up days (3%+): {len(ccj_big_days)}")
    
    for laggard_name in ['DNN', 'UEC']:
        laggard = data[laggard_name]
        
        same_day_green = 0
        next_day_green = 0
        count = 0
        
        for date in ccj_big_days:
            if date not in laggard.index:
                continue
            
            same_ret = laggard.loc[date, 'Return']
            if same_ret > 0:
                same_day_green += 1
            
            try:
                loc = laggard.index.get_loc(date)
                if loc + 1 < len(laggard):
                    next_ret = laggard['Return'].iloc[loc + 1]
                    if next_ret > 0:
                        next_day_green += 1
            except:
                pass
            
            count += 1
        
        if count > 0:
            same_pct = (same_day_green / count) * 100
            next_pct = (next_day_green / count) * 100
            
            print(f"\n{laggard_name}:")
            print(f"  Same day green: {same_day_green}/{count} = {same_pct:.0f}%")
            print(f"  Next day green: {next_day_green}/{count} = {next_pct:.0f}%")
            
            if same_pct > 90 and 45 <= next_pct <= 55:
                print(f"  ✅ FENRIR CORRECT: Same day correlation, next day random")
            else:
                print(f"  ⚠️ Same {same_pct:.0f}%, Next {next_pct:.0f}%")
    
    print()

# =============================================================================
# FINAL VERDICT
# =============================================================================

print("="*70)
print("🐺 BROKKR'S FINAL VERDICT")
print("="*70)
print("\nVerification complete. Check results above.")
print("\nKey findings:")
print("  • Nuclear stocks: Check current RSI status")
print("  • RSI < 30 edge: Validated or debunked")
print("  • WULF bounce: Validated or debunked")
print("  • DNN gaps: Validated or debunked")
print("  • Wednesday edge: Validated or debunked")
print("  • Leader/laggard: Validated or debunked")
print("\nNext steps:")
print("  1. Code VALIDATED patterns into scanners")
print("  2. Discard DEBUNKED patterns")
print("  3. Paper trade 2 weeks before live money")
print("\n🐺 DATA > CLAIMS. LLHR. AWOOOO.")
