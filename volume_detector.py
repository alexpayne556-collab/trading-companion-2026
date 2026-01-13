#!/usr/bin/env python3
"""
Volume Spike Detector - Find accumulation BEFORE price moves

This is the edge: Volume increases 2-3 days before price breakout
"""

import sqlite3
import yfinance as yf
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'webapp'))
from intelligence_db import log_alert

DB_PATH = '/workspaces/trading-companion-2026/research/intelligence.db'

def get_volume_baseline(ticker, days=20):
    """Get 20-day average volume from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute('''
        SELECT AVG(volume) 
        FROM scans 
        WHERE ticker = ? 
        AND scan_time > datetime('now', '-' || ? || ' days')
        AND volume > 0
    ''', (ticker, days))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result[0] else None


def detect_volume_spikes(threshold=0.3):
    """
    Detect volume spikes across all tickers
    
    threshold: 0.3 = 30% above 20d average
    """
    print(f"\n{'='*80}")
    print(f"🔍 VOLUME SPIKE DETECTOR")
    print(f"{'='*80}\n")
    print(f"Threshold: {threshold*100:.0f}% above 20-day average\n")
    
    # Get unique tickers from database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute('SELECT DISTINCT ticker FROM scans ORDER BY ticker')
    tickers = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    spikes = []
    
    for ticker in tickers:
        # Get baseline
        avg_volume = get_volume_baseline(ticker, days=20)
        
        if not avg_volume or avg_volume == 0:
            continue
        
        # Get current volume (latest scan)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute('''
            SELECT volume, change_pct, scan_time 
            FROM scans 
            WHERE ticker = ? 
            AND volume > 0
            ORDER BY scan_time DESC 
            LIMIT 1
        ''', (ticker,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            continue
        
        current_volume, current_change, scan_time = result
        
        # Calculate spike
        volume_change = ((current_volume - avg_volume) / avg_volume)
        
        if volume_change >= threshold:
            # VOLUME SPIKE DETECTED
            spike_info = {
                'ticker': ticker,
                'current_volume': int(current_volume),
                'avg_volume': int(avg_volume),
                'volume_increase': volume_change,
                'price_change': current_change,
                'scan_time': scan_time
            }
            
            spikes.append(spike_info)
            
            # Determine significance
            if volume_change >= 1.0:  # 100%+ increase
                significance = 'CRITICAL'
            elif volume_change >= 0.5:  # 50-100%
                significance = 'HIGH'
            else:  # 30-50%
                significance = 'MEDIUM'
            
            print(f"🚨 {significance}: {ticker}")
            print(f"   Volume: {current_volume:,} (avg: {avg_volume:,})")
            print(f"   Increase: +{volume_change*100:.0f}%")
            print(f"   Price: {current_change:+.1f}%")
            
            # Log alert
            log_alert(
                'VOLUME_SPIKE',
                ticker,
                f"Volume +{volume_change*100:.0f}% vs 20d avg (price {current_change:+.1f}%)",
                {
                    'current_volume': current_volume,
                    'avg_volume': avg_volume,
                    'volume_increase_pct': volume_change * 100,
                    'price_change_pct': current_change,
                    'significance': significance
                }
            )
            
            print()
    
    # Summary
    print(f"{'='*80}")
    print(f"📊 SUMMARY: {len(spikes)} volume spikes detected")
    
    if spikes:
        print(f"\n🎯 TOP OPPORTUNITIES (volume building before price moves):\n")
        
        # Sort by volume increase, but prioritize those with minimal price change
        # (These are early signals - volume moved but price hasn't yet)
        early_signals = [s for s in spikes if abs(s['price_change']) < 5]
        late_signals = [s for s in spikes if abs(s['price_change']) >= 5]
        
        if early_signals:
            print("   ⚠️  EARLY (Price hasn't moved much yet):")
            for spike in sorted(early_signals, key=lambda x: x['volume_increase'], reverse=True)[:5]:
                print(f"      {spike['ticker']}: Volume +{spike['volume_increase']*100:.0f}%, Price {spike['price_change']:+.1f}%")
        
        if late_signals:
            print("\n   📈 LATE (Already moving):")
            for spike in sorted(late_signals, key=lambda x: x['volume_increase'], reverse=True)[:5]:
                print(f"      {spike['ticker']}: Volume +{spike['volume_increase']*100:.0f}%, Price {spike['price_change']:+.1f}%")
    
    print(f"{'='*80}\n")
    
    return spikes


if __name__ == '__main__':
    threshold = 0.3  # 30% default
    
    if len(sys.argv) > 1:
        try:
            threshold = float(sys.argv[1])
        except:
            print("Usage: python volume_detector.py [threshold]")
            print("Example: python volume_detector.py 0.5  (50% threshold)")
            sys.exit(1)
    
    spikes = detect_volume_spikes(threshold)
    
    print(f"\n💡 TIP: Look for volume spikes with <5% price change")
    print(f"   These are EARLY signals - accumulation before breakout\n")
