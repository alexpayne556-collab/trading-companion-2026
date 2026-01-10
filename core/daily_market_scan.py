#!/usr/bin/env python3
"""
🐺 DAILY MARKET SCANNER
Run this every morning to find TODAY's setups
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

WATCHLIST = [
    'APLD', 'WULF', 'CLSK', 'CIFR', 'IREN', 'BTBT', 'CORZ', 'HIVE', 'MARA', 'RIOT',
    'IONQ', 'RGTI', 'QBTS', 'QUBT', 
    'RKLB', 'LUNR', 'ASTS', 'SPIR',
    'SMR', 'OKLO', 'DNN', 'UEC', 'UUUU', 'CCJ',
    'PLTR', 'KTOS', 'RCAT', 'AVAV',
    'SOUN', 'BBAI', 'AI', 'GFAI',
    'FSLR', 'ENPH', 'SEDG', 'RUN',
]

def calculate_rsi(prices, period=14):
    """Calculate RSI"""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def daily_scan():
    """Run comprehensive daily scan"""
    print("🐺 DAILY MARKET SCANNER")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %A')}")
    print("="*70)
    print()
    
    crash_bounces = []
    overbought = []
    momentum = []
    neutral = []
    
    for ticker in WATCHLIST:
        try:
            df = yf.download(ticker, period='1mo', progress=False)
            if len(df) < 20:
                continue
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            price = df['Close'].iloc[-1]
            today_change = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
            
            if len(df) >= 5:
                week_ret = ((price - df['Close'].iloc[-5]) / df['Close'].iloc[-5]) * 100
            else:
                week_ret = 0
            
            rsi = calculate_rsi(df['Close']).iloc[-1]
            
            vol_avg = df['Volume'].rolling(20).mean().iloc[-2]
            vol_today = df['Volume'].iloc[-1]
            vol_ratio = vol_today / vol_avg if vol_avg > 0 else 0
            
            # Categorize
            if week_ret <= -10 and rsi < 45:
                crash_bounces.append({
                    'ticker': ticker, 'price': price, 'week': week_ret, 
                    'rsi': rsi, 'vol': vol_ratio
                })
            elif rsi > 75:
                overbought.append({
                    'ticker': ticker, 'price': price, 'week': week_ret, 
                    'rsi': rsi
                })
            elif 5 <= week_ret <= 15 and 45 <= rsi <= 65 and vol_ratio > 1.0:
                momentum.append({
                    'ticker': ticker, 'price': price, 'week': week_ret, 
                    'rsi': rsi, 'vol': vol_ratio
                })
            else:
                neutral.append({
                    'ticker': ticker, 'price': price, 'week': week_ret, 
                    'rsi': rsi
                })
        except:
            pass
    
    # Print results
    print("🎯 CRASH BOUNCES (69% Edge - BUY):")
    if crash_bounces:
        for s in crash_bounces:
            print(f"  ✅ {s['ticker']:6} ${s['price']:7.2f}  Week:{s['week']:+6.1f}%  RSI:{s['rsi']:4.0f}  Vol:{s['vol']:.1f}x")
    else:
        print("  None found")
    print()
    
    print("⚠️  OVERBOUGHT (64% Edge - AVOID/SHORT):")
    if overbought:
        for s in sorted(overbought, key=lambda x: x['rsi'], reverse=True):
            print(f"  ❌ {s['ticker']:6} ${s['price']:7.2f}  Week:{s['week']:+6.1f}%  RSI:{s['rsi']:4.0f}")
    else:
        print("  None found")
    print()
    
    print("🚀 MOMENTUM (58.8% Monday Edge - BUY if Monday):")
    day_of_week = datetime.now().weekday()  # 0=Monday
    if day_of_week == 0:
        if momentum:
            for s in momentum:
                print(f"  ✅ {s['ticker']:6} ${s['price']:7.2f}  Week:{s['week']:+6.1f}%  RSI:{s['rsi']:4.0f}  Vol:{s['vol']:.1f}x")
        else:
            print("  None found")
    else:
        print(f"  ⏸️  Not Monday (today is {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][day_of_week]}) - skip momentum plays")
    print()
    
    print("➡️  NEUTRAL (No clear edge - WAIT):")
    print(f"  {len(neutral)} stocks in neutral zone")
    print()
    
    print("="*70)
    print("💡 TODAY'S RECOMMENDATION:")
    print("="*70)
    
    if day_of_week == 0 and momentum:  # Monday with momentum
        print("✅ TRADE: Monday momentum setups available")
        print(f"   Buy: {', '.join([s['ticker'] for s in momentum[:3]])}")
    elif crash_bounces:
        print("✅ TRADE: Crash bounce setups available")
        print(f"   Buy: {', '.join([s['ticker'] for s in crash_bounces[:2]])}")
    else:
        print("❌ WAIT: No clear setups matching validated edges")
        print("   Come back tomorrow or wait for market to set up")
    
    print()
    print("🐺 Only trade when the setup matches the playbook. LLHR.")
    print()

if __name__ == "__main__":
    daily_scan()
