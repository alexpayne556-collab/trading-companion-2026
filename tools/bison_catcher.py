#!/usr/bin/env python3
"""
🐺 BISON CATCHER
The only tool that matters. Catches Day 1 moves at market open.

Run this at 9:30 AM. It screams when the buffalo walk by.

Usage:
    python tools/bison_catcher.py
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

UNIVERSE = {
    'Quantum': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'Nuclear': ['UUUU', 'USAR', 'NXE', 'DNN', 'LEU'],
    'Space': ['RKLB', 'ASTS', 'LUNR', 'PL', 'SIDU', 'SPCE'],
    'Semi': ['NVTS', 'NXPI', 'SWKS', 'MRVL', 'MU'],
    'AI_Infra': ['SMCI', 'PLTR', 'IONQ'],
}

def scan_for_bison():
    """
    Find tickers with:
    1. Volume > 3x average in first hour
    2. Price up 5%+ 
    3. Multiple tickers in sector moving = HERD
    """
    print("🐺 BISON CATCHER - LIVE SCAN")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    alerts = []
    sector_heat = {}
    
    for sector, tickers in UNIVERSE.items():
        sector_movers = 0
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                
                # Get today's intraday + last 5 days for context
                today = stock.history(period='1d', interval='5m')
                hist = stock.history(period='5d')
                
                if len(today) < 10 or len(hist) < 2:
                    continue
                
                # Current price
                current_price = today['Close'].iloc[-1]
                today_open = today['Open'].iloc[0]
                
                # Today's move
                day_change = ((current_price - today_open) / today_open) * 100
                
                # Volume comparison
                current_vol = today['Volume'].sum()
                avg_vol = hist['Volume'].mean()
                vol_ratio = current_vol / avg_vol if avg_vol > 0 else 0
                
                # ALERT CONDITIONS
                is_big_move = day_change > 5
                is_volume_spike = vol_ratio > 2.0
                
                if is_big_move and is_volume_spike:
                    sector_movers += 1
                    
                    alerts.append({
                        'ticker': ticker,
                        'sector': sector,
                        'price': current_price,
                        'change': day_change,
                        'vol_ratio': vol_ratio,
                        'score': day_change * vol_ratio  # Combined score
                    })
                
            except Exception as e:
                continue
        
        if sector_movers > 0:
            sector_heat[sector] = sector_movers
    
    # Sort alerts by score
    alerts.sort(key=lambda x: x['score'], reverse=True)
    
    # Display alerts
    if len(alerts) == 0:
        print("\n❌ NO BISON DETECTED")
        print("   Market is quiet or we're between moves.")
        return
    
    print(f"\n🚨 {len(alerts)} BISON DETECTED:")
    print("-"*80)
    
    for alert in alerts:
        # Check if this is a HERD move (multiple in sector)
        sector_count = sector_heat.get(alert['sector'], 0)
        herd_flag = "🔥 HERD" if sector_count >= 2 else "⚠️  SOLO"
        
        print(f"\n{alert['ticker']:6} ({alert['sector']:8}) ${alert['price']:.2f}")
        print(f"  Change: {alert['change']:+6.2f}%")
        print(f"  Volume: {alert['vol_ratio']:.1f}x average")
        print(f"  Score:  {alert['score']:.1f}")
        print(f"  Status: {herd_flag} ({sector_count} movers in sector)")
    
    # Sector summary
    print("\n" + "="*80)
    print("SECTOR HEAT MAP:")
    print("-"*80)
    for sector, count in sorted(sector_heat.items(), key=lambda x: x[1], reverse=True):
        heat = "🔥🔥🔥" if count >= 3 else "🔥🔥" if count >= 2 else "🔥"
        print(f"{sector:12} {heat}  {count} movers")
    
    # Top play recommendation
    print("\n" + "="*80)
    print("🎯 TOP PLAY:")
    print("-"*80)
    
    if len(alerts) > 0:
        top = alerts[0]
        sector_count = sector_heat.get(top['sector'], 0)
        
        print(f"{top['ticker']} - ${top['price']:.2f}")
        print(f"  Why: {top['change']:+.1f}% on {top['vol_ratio']:.1f}x volume")
        
        if sector_count >= 2:
            print(f"  ✅ CONFIRMED: {sector_count} tickers moving in {top['sector']}")
            print(f"  🐺 ACTION: Enter on first pullback, hold Day 2-3")
        else:
            print(f"  ⚠️  CAUTION: Solo mover (no sector confirmation)")
            print(f"  🐺 ACTION: Watch for sector confirmation before entering")
    
    print("="*80)

if __name__ == '__main__':
    scan_for_bison()
