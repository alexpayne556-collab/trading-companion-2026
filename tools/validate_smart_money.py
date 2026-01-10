#!/usr/bin/env python3
"""
🐺 SMART MONEY 10 AM DIP VALIDATION
Testing Tyr's Hypothesis - Direct Python, No Jupyter
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print('\n' + '='*70)
print('🐺 BROKKR SMART MONEY VALIDATOR')
print('='*70)
print('Testing: Peak at 9:45-9:50, Dip at 10-11 AM')
print('='*70 + '\n')

# WATCHLIST
TICKERS = ['IONQ', 'RGTI', 'QBTS', 'RKLB', 'ASTS', 'LUNR', 
           'CCJ', 'UEC', 'UUUU', 'MRNA', 'BNTX', 
           'CRWD', 'S', 'ZS', 'NVDA', 'AMD', 'AI',
           'NVVE', 'APLD']

print(f'Testing {len(TICKERS)} tickers...\n')

def analyze_10am_dip(ticker, days=30):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=f'{days}d', interval='5m')
        
        if len(df) < 50:
            return None
        
        df['date'] = df.index.date
        results = []
        
        for date in df['date'].unique():
            day = df[df['date'] == date].copy()
            if len(day) < 20:
                continue
            
            # Morning peak: 9:30-10:00 AM
            morning = day[(day.index.hour == 9) | ((day.index.hour == 10) & (day.index.minute == 0))]
            if len(morning) == 0:
                continue
            
            morning_high = morning['High'].max()
            morning_high_time = morning['High'].idxmax()
            open_price = day['Open'].iloc[0]
            
            # Dip: 10:00-11:00 AM
            dip_window = day[(day.index.hour == 10) | ((day.index.hour == 11) & (day.index.minute == 0))]
            if len(dip_window) == 0:
                continue
            
            dip_low = dip_window['Low'].min()
            
            # Rest of day
            close = day['Close'].iloc[-1]
            
            # Metrics
            peak_gain = ((morning_high - open_price) / open_price) * 100
            dip_from_peak = ((dip_low - morning_high) / morning_high) * 100
            close_from_dip = ((close - dip_low) / dip_low) * 100
            
            strategy_return = peak_gain + close_from_dip
            buy_hold = ((close - open_price) / open_price) * 100
            edge = strategy_return - buy_hold
            
            pattern_worked = (morning_high > dip_low) and (dip_from_peak < -1)
            
            results.append({
                'date': date,
                'peak_time': morning_high_time.strftime('%H:%M'),
                'peak_gain': peak_gain,
                'dip_from_peak': dip_from_peak,
                'edge': edge,
                'pattern_worked': pattern_worked
            })
        
        if len(results) == 0:
            return None
        
        return pd.DataFrame(results)
        
    except Exception as e:
        return None

# RUN ANALYSIS
summary = []

for ticker in TICKERS:
    print(f'  {ticker}...', end=' ')
    df = analyze_10am_dip(ticker, days=30)
    
    if df is not None and len(df) > 0:
        win_rate = df['pattern_worked'].mean() * 100
        avg_edge = df['edge'].mean()
        avg_dip = df['dip_from_peak'].mean()
        peak_time = df['peak_time'].mode()[0] if len(df) > 0 else 'N/A'
        
        print(f'✅ {win_rate:.0f}% win, {avg_edge:+.2f}% edge')
        
        summary.append({
            'ticker': ticker,
            'days': len(df),
            'win_rate': win_rate,
            'avg_edge': avg_edge,
            'avg_dip': avg_dip,
            'peak_time': peak_time
        })
    else:
        print('❌')

# RESULTS
print('\n' + '='*70)
print('🎯 TYR\'S HYPOTHESIS VALIDATION')
print('='*70)

if len(summary) > 0:
    summary_df = pd.DataFrame(summary)
    
    avg_win = summary_df['win_rate'].mean()
    avg_edge = summary_df['avg_edge'].mean()
    avg_dip = summary_df['avg_dip'].mean()
    
    print(f'\n�� OVERALL:')
    print(f'   Tickers: {len(summary_df)}')
    print(f'   Avg win rate: {avg_win:.1f}%')
    print(f'   Avg edge: {avg_edge:+.2f}%')
    print(f'   Avg dip from peak: {avg_dip:.2f}%')
    
    print(f'\n🎯 VERDICT:')
    if avg_win > 70:
        print(f'   ✅ TYR IS RIGHT!')
        print(f'   → Pattern works {avg_win:.0f}% of time')
        print(f'   → {avg_edge:+.2f}% daily edge')
    elif avg_win > 50:
        print(f'   🟡 PATTERN EXISTS ({avg_win:.0f}%)')
    else:
        print(f'   ❌ Pattern weak ({avg_win:.0f}%)')
    
    print(f'\n🏆 BEST TICKERS:')
    best = summary_df.sort_values('avg_edge', ascending=False).head(5)
    for _, row in best.iterrows():
        print(f'   {row["ticker"]}: {row["win_rate"]:.0f}% win, {row["avg_edge"]:+.2f}% edge, peak {row["peak_time"]}')
    
    # Save
    summary_df.to_csv('tools/smart_money_results.csv', index=False)
    print(f'\n✅ Saved: tools/smart_money_results.csv')

print('\n' + '='*70)
print('🐺 AWOOOO')
print('='*70 + '\n')
