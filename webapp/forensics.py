#!/usr/bin/env python3
"""
FORENSIC ANALYSIS - Work backwards from moves to find ALL signals

Don't fit patterns. DISCOVER patterns.
Look at what ACTUALLY moved and catalog EVERYTHING that preceded it.
"""

import yfinance as yf
from datetime import datetime, timedelta
import sqlite3
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

DB_PATH = '/workspaces/trading-companion-2026/research/forensics.db'

def init_forensics_db():
    """Create forensics database"""
    conn = sqlite3.connect(DB_PATH)
    
    # Every mover we analyze
    conn.execute('''
        CREATE TABLE IF NOT EXISTS analyzed_moves (
            id INTEGER PRIMARY KEY,
            ticker TEXT,
            move_date TEXT,
            peak_price REAL,
            peak_change_pct REAL,
            peak_volume INTEGER,
            days_to_peak INTEGER,
            analyzed_at TEXT,
            UNIQUE(ticker, move_date)
        )
    ''')
    
    # All signals found before each move
    conn.execute('''
        CREATE TABLE IF NOT EXISTS signals_found (
            id INTEGER PRIMARY KEY,
            move_id INTEGER,
            ticker TEXT,
            signal_type TEXT,
            days_before_move INTEGER,
            signal_data TEXT,
            confidence TEXT,
            notes TEXT,
            FOREIGN KEY(move_id) REFERENCES analyzed_moves(id)
        )
    ''')
    
    # Price/volume patterns before moves
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pre_move_patterns (
            id INTEGER PRIMARY KEY,
            move_id INTEGER,
            ticker TEXT,
            pattern_name TEXT,
            days_before TEXT,
            pattern_data TEXT,
            FOREIGN KEY(move_id) REFERENCES analyzed_moves(id)
        )
    ''')
    
    # Correlations with other tickers
    conn.execute('''
        CREATE TABLE IF NOT EXISTS correlations (
            id INTEGER PRIMARY KEY,
            move_id INTEGER,
            ticker TEXT,
            correlated_ticker TEXT,
            correlation_strength REAL,
            lag_days INTEGER,
            notes TEXT,
            FOREIGN KEY(move_id) REFERENCES analyzed_moves(id)
        )
    ''')
    
    conn.commit()
    conn.close()


def analyze_move(ticker, move_date_str):
    """
    Deep forensic analysis of a move
    Look at EVERYTHING that happened before it
    """
    ticker = ticker.upper()
    move_date = datetime.strptime(move_date_str, '%Y-%m-%d')
    
    print(f"\n{'='*80}")
    print(f"🔍 FORENSIC ANALYSIS: {ticker} on {move_date_str}")
    print(f"{'='*80}\n")
    
    # Get price data (30 days before to 5 days after)
    start_date = move_date - timedelta(days=30)
    end_date = move_date + timedelta(days=5)
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            print(f"❌ No data for {ticker}")
            return None
        
        # Find the actual move
        move_idx = None
        for i, (date, row) in enumerate(hist.iterrows()):
            if date.date() == move_date.date():
                move_idx = i
                break
        
        if move_idx is None:
            print(f"❌ Move date not found in data")
            return None
        
        move_price = hist.iloc[move_idx]['Close']
        move_open = hist.iloc[move_idx]['Open']
        move_change = ((move_price - move_open) / move_open) * 100
        move_volume = hist.iloc[move_idx]['Volume']
        
        print(f"📊 MOVE DETAILS:")
        print(f"   Price: ${move_open:.2f} → ${move_price:.2f} (+{move_change:.1f}%)")
        print(f"   Volume: {move_volume:,}")
        
        # Find peak (next 5 days)
        peak_price = move_price
        peak_change = move_change
        days_to_peak = 0
        
        for i in range(move_idx, min(move_idx + 6, len(hist))):
            if hist.iloc[i]['Close'] > peak_price:
                peak_price = hist.iloc[i]['Close']
                peak_change = ((peak_price - move_open) / move_open) * 100
                days_to_peak = i - move_idx
        
        print(f"   Peak: ${peak_price:.2f} (+{peak_change:.1f}%) on Day {days_to_peak}")
        
        # SIGNAL DETECTION - Look at everything before the move
        signals = []
        
        print(f"\n🔎 ANALYZING SIGNALS BEFORE MOVE:\n")
        
        # 1. VOLUME ANALYSIS - Look for volume spikes/buildup
        if move_idx >= 5:
            avg_volume_5d = hist.iloc[move_idx-5:move_idx]['Volume'].mean()
            avg_volume_20d = hist.iloc[max(0,move_idx-20):move_idx]['Volume'].mean()
            
            print(f"   📈 VOLUME PATTERNS:")
            for lookback in [1, 2, 3, 5, 7, 10]:
                if move_idx >= lookback:
                    prev_vol = hist.iloc[move_idx-lookback]['Volume']
                    vol_change = ((prev_vol - avg_volume_20d) / avg_volume_20d) * 100
                    
                    if abs(vol_change) > 20:
                        signal = {
                            'type': 'VOLUME_SPIKE',
                            'days_before': lookback,
                            'data': f"Volume {vol_change:+.0f}% vs 20d avg",
                            'confidence': 'HIGH' if abs(vol_change) > 100 else 'MEDIUM'
                        }
                        signals.append(signal)
                        print(f"      • D-{lookback}: Volume {vol_change:+.0f}% vs avg")
        
        # 2. PRICE ACTION - Look for base building, accumulation
        print(f"\n   📊 PRICE PATTERNS:")
        if move_idx >= 10:
            # Look for consolidation (low volatility before breakout)
            volatility_10d = hist.iloc[move_idx-10:move_idx]['Close'].pct_change().std()
            volatility_20d = hist.iloc[max(0,move_idx-20):move_idx]['Close'].pct_change().std()
            
            if volatility_10d < volatility_20d * 0.7:
                signals.append({
                    'type': 'CONSOLIDATION',
                    'days_before': 10,
                    'data': f"Low volatility base building",
                    'confidence': 'MEDIUM'
                })
                print(f"      • Base building: 10d vol {volatility_10d:.4f} vs 20d {volatility_20d:.4f}")
            
            # Look for higher lows (accumulation)
            lows = hist.iloc[move_idx-10:move_idx]['Low']
            if len(lows) >= 3:
                if lows.iloc[-3] < lows.iloc[-2] < lows.iloc[-1]:
                    signals.append({
                        'type': 'HIGHER_LOWS',
                        'days_before': 3,
                        'data': 'Ascending lows pattern',
                        'confidence': 'MEDIUM'
                    })
                    print(f"      • Higher lows pattern (accumulation)")
        
        # 3. GAP ANALYSIS - Morning gaps
        if move_idx > 0:
            prev_close = hist.iloc[move_idx-1]['Close']
            gap_pct = ((move_open - prev_close) / prev_close) * 100
            
            if abs(gap_pct) > 5:
                signals.append({
                    'type': 'GAP',
                    'days_before': 0,
                    'data': f"Gap {gap_pct:+.1f}% at open",
                    'confidence': 'HIGH'
                })
                print(f"\n   🚀 GAP AT OPEN: {gap_pct:+.1f}%")
        
        # 4. SECTOR ROTATION - Check if sector moved first
        print(f"\n   🔄 SECTOR/CORRELATION ANALYSIS:")
        print(f"      (Need to implement sector peer comparison)")
        
        # 5. NEWS/CATALYST WINDOW
        print(f"\n   📰 CATALYST WINDOW:")
        print(f"      Checking news/filings 1-7 days before move...")
        # This will pull from catalysts database
        
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO analyzed_moves 
            (ticker, move_date, peak_price, peak_change_pct, peak_volume, days_to_peak, analyzed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ticker, move_date_str, peak_price, peak_change, move_volume, days_to_peak, datetime.now().isoformat()))
        
        move_id = cursor.lastrowid
        
        # Save all signals
        for signal in signals:
            cursor.execute('''
                INSERT INTO signals_found (move_id, ticker, signal_type, days_before_move, signal_data, confidence, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (move_id, ticker, signal['type'], signal['days_before'], signal['data'], signal['confidence'], ''))
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Analysis complete: {len(signals)} signals cataloged")
        
        return {
            'ticker': ticker,
            'move_date': move_date_str,
            'peak_change': peak_change,
            'days_to_peak': days_to_peak,
            'signals': signals
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def analyze_recent_movers():
    """Analyze all recent movers to find patterns"""
    
    # Monday Jan 12 movers
    movers = [
        ('OCGN', '2026-01-12'),  # +14.8% - JPM presentation Thursday
        ('BEAM', '2026-01-12'),  # Biotech
        ('NTLA', '2026-01-12'),  # Biotech - JPM Wed
        ('RARE', '2026-01-12'),  # Biotech
        ('ALMS', '2026-01-12'),  # Biotech
        ('RIOT', '2026-01-12'),  # Crypto
        ('WULF', '2026-01-12'),  # Crypto
        ('WDC', '2026-01-12'),   # Storage
        ('STX', '2026-01-12'),   # Storage
    ]
    
    results = []
    for ticker, date in movers:
        result = analyze_move(ticker, date)
        if result:
            results.append(result)
        print()
    
    return results


def find_common_signals():
    """Find which signals appear most often before big moves"""
    conn = sqlite3.connect(DB_PATH)
    
    # Signal frequency
    cursor = conn.execute('''
        SELECT signal_type, COUNT(*) as frequency, AVG(CAST(move.peak_change_pct AS REAL)) as avg_peak
        FROM signals_found sig
        JOIN analyzed_moves move ON sig.move_id = move.id
        GROUP BY signal_type
        ORDER BY frequency DESC
    ''')
    
    print(f"\n{'='*80}")
    print(f"📊 COMMON SIGNALS ACROSS ALL MOVES:")
    print(f"{'='*80}\n")
    
    for row in cursor:
        signal_type, freq, avg_peak = row
        print(f"   {signal_type}: {freq} occurrences, avg peak +{avg_peak:.1f}%")
    
    conn.close()


if __name__ == '__main__':
    init_forensics_db()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'analyze':
            ticker = sys.argv[2]
            date = sys.argv[3] if len(sys.argv) > 3 else datetime.now().strftime('%Y-%m-%d')
            analyze_move(ticker, date)
        elif sys.argv[1] == 'recent':
            analyze_recent_movers()
            find_common_signals()
    else:
        print("Usage: python forensics.py analyze TICKER YYYY-MM-DD")
        print("       python forensics.py recent")
