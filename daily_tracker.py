#!/usr/bin/env python3
"""
🐺 DAILY TRACKER - The Memory Loop

Every day:
1. Log what moved TODAY (ATON, EVTV, everything)
2. Check yesterday's signals - what worked, what failed
3. Learn from it - update scoring
4. Prepare for tomorrow

This is how humans learn. This is how we build the edge.

NOT statistical bullshit. REAL money-making moves.
"""

import yfinance as yf
import json
import sqlite3
from datetime import datetime, timedelta
import os
from pathlib import Path

DB_PATH = "intelligence.db"
DAILY_LOG_DIR = "logs/daily"

# =============================================================================
# DATABASE SETUP
# =============================================================================

def init_database():
    """Initialize or update database schema"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Daily movers table - EVERYTHING that moves
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_movers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            logged_time TEXT NOT NULL,
            
            -- What we saw
            move_pct REAL,
            close_price REAL,
            volume INTEGER,
            volume_ratio REAL,
            float_size INTEGER,
            market_cap INTEGER,
            
            -- Our analysis
            legs_score INTEGER,
            verdict TEXT,
            signals TEXT,
            
            -- Forward tracking (filled next day)
            day1_return REAL,
            day2_return REAL,
            day3_return REAL,
            day5_return REAL,
            peak_return REAL,
            peak_day INTEGER,
            outcome TEXT,
            
            -- Learning
            was_right INTEGER,  -- 1 if we were right, 0 if wrong, NULL if unknown
            notes TEXT,
            
            UNIQUE(ticker, date)
        )
    """)
    
    # Predictions table - what we think will happen
    c.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            prediction_date TEXT NOT NULL,
            prediction_time TEXT NOT NULL,
            
            -- What we predict
            expected_outcome TEXT,  -- 'CONTINUE', 'REVERSE', 'FLAT'
            confidence INTEGER,  -- 1-10
            reason TEXT,
            
            -- Validation (filled later)
            actual_outcome TEXT,
            was_correct INTEGER,
            day3_return REAL,
            
            UNIQUE(ticker, prediction_date)
        )
    """)
    
    # Learning table - what patterns work
    c.execute("""
        CREATE TABLE IF NOT EXISTS pattern_learnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_name TEXT NOT NULL,
            last_updated TEXT NOT NULL,
            
            -- Stats
            total_signals INTEGER DEFAULT 0,
            correct_signals INTEGER DEFAULT 0,
            win_rate REAL DEFAULT 0,
            avg_return REAL DEFAULT 0,
            
            -- Pattern definition
            criteria TEXT,
            
            UNIQUE(pattern_name)
        )
    """)
    
    conn.commit()
    conn.close()
    
    # Create log directory
    Path(DAILY_LOG_DIR).mkdir(parents=True, exist_ok=True)

# =============================================================================
# END OF DAY - LOG EVERYTHING THAT MOVED
# =============================================================================

def log_todays_movers():
    """
    Run this at market close (4:00 PM).
    Logs EVERYTHING that moved today.
    """
    from market_mover_finder import discover_movers, check_legs
    
    print("=" * 70)
    print("🐺 END OF DAY - LOGGING TODAY'S MOVERS")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Discover all movers
    print("\n📊 Discovering today's movers...")
    movers = discover_movers(verbose=False)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    logged_count = 0
    
    for mover in movers:
        try:
            # Insert or replace
            c.execute("""
                INSERT OR REPLACE INTO daily_movers 
                (ticker, date, logged_time, move_pct, close_price, volume, 
                 volume_ratio, float_size, market_cap, legs_score, verdict, signals)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mover['ticker'],
                today,
                datetime.now().isoformat(),
                mover.get('move_today', 0),
                mover.get('price', 0),
                0,  # volume not in mover dict
                mover.get('volume_ratio', 0),
                mover.get('float', 0),
                mover.get('market_cap', 0),
                mover.get('legs_score', 0),
                mover.get('verdict', ''),
                json.dumps(mover.get('signals', []))
            ))
            
            logged_count += 1
            
            if logged_count <= 10:
                print(f"   ✅ {mover['ticker']}: {mover.get('verdict', 'Unknown')}")
        
        except Exception as e:
            print(f"   ❌ {mover['ticker']}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Logged {logged_count} movers for {today}")
    
    # Save to JSON file
    json_file = f"{DAILY_LOG_DIR}/movers_{today}.json"
    with open(json_file, 'w') as f:
        json.dump(movers, f, indent=2, default=str)
    
    print(f"💾 Saved to {json_file}")
    
    return logged_count

# =============================================================================
# NEXT MORNING - VALIDATE YESTERDAY'S PREDICTIONS
# =============================================================================

def validate_yesterday():
    """
    Run this next morning at 9:31 AM.
    Check: Did yesterday's signals work? Update the database.
    """
    print("=" * 70)
    print("🔍 VALIDATING YESTERDAY'S SIGNALS")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get yesterday's movers that need validation
    c.execute("""
        SELECT ticker, legs_score, verdict 
        FROM daily_movers 
        WHERE date = ? AND day1_return IS NULL
    """, (yesterday,))
    
    yesterday_movers = c.fetchall()
    
    if not yesterday_movers:
        print(f"\n❌ No movers found for {yesterday}")
        conn.close()
        return
    
    print(f"\n📊 Found {len(yesterday_movers)} movers from {yesterday}")
    print("\nValidating each...")
    
    validated = 0
    winners = 0
    losers = 0
    
    for ticker, legs_score, verdict in yesterday_movers:
        try:
            # Get today's price vs yesterday
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            
            if len(hist) < 2:
                continue
            
            yesterday_close = hist['Close'].iloc[-2]
            today_close = hist['Close'].iloc[-1]
            
            day1_return = ((today_close - yesterday_close) / yesterday_close) * 100
            
            # Determine if we were right
            predicted_up = legs_score >= 2  # Predicted continuation
            actually_up = day1_return > 2
            was_right = (predicted_up == actually_up)
            
            # Determine outcome
            if day1_return >= 5:
                outcome = "WINNER"
                winners += 1
            elif day1_return <= -5:
                outcome = "LOSER"
                losers += 1
            else:
                outcome = "FLAT"
            
            # Update database
            c.execute("""
                UPDATE daily_movers 
                SET day1_return = ?, outcome = ?, was_right = ?
                WHERE ticker = ? AND date = ?
            """, (day1_return, outcome, 1 if was_right else 0, ticker, yesterday))
            
            validated += 1
            
            status = "✅" if was_right else "❌"
            print(f"   {status} {ticker}: Day 1 = {day1_return:+.1f}% ({outcome})")
        
        except Exception as e:
            print(f"   ⚠️ {ticker}: Error - {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Validated {validated} signals")
    print(f"   Winners: {winners} | Losers: {losers} | Flat: {validated - winners - losers}")
    
    if validated > 0:
        win_rate = (winners / validated) * 100
        print(f"   Win Rate: {win_rate:.1f}%")
    
    return validated

# =============================================================================
# LEARNING - UPDATE PATTERN WIN RATES
# =============================================================================

def update_learnings():
    """
    Analyze all validated signals.
    Update pattern win rates.
    """
    print("\n" + "=" * 70)
    print("🧠 UPDATING PATTERN LEARNINGS")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Analyze: Does "STRONG LEGS" actually work?
    c.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN outcome = 'WINNER' THEN 1 ELSE 0 END) as winners,
            AVG(day1_return) as avg_return
        FROM daily_movers
        WHERE verdict LIKE '%STRONG LEGS%' AND day1_return IS NOT NULL
    """)
    
    strong_legs = c.fetchone()
    
    if strong_legs and strong_legs[0] > 0:
        total, winners, avg_return = strong_legs
        win_rate = (winners / total) * 100
        
        print(f"\n🚀 STRONG LEGS Pattern:")
        print(f"   Total signals: {total}")
        print(f"   Winners: {winners}")
        print(f"   Win rate: {win_rate:.1f}%")
        print(f"   Avg return: {avg_return:.1f}%")
        
        # Update pattern_learnings table
        c.execute("""
            INSERT OR REPLACE INTO pattern_learnings 
            (pattern_name, last_updated, total_signals, correct_signals, win_rate, avg_return, criteria)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'STRONG_LEGS',
            datetime.now().isoformat(),
            total,
            winners,
            win_rate,
            avg_return,
            'legs_score >= 4'
        ))
    
    # Analyze: Does "MICRO FLOAT" work?
    c.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN outcome = 'WINNER' THEN 1 ELSE 0 END) as winners,
            AVG(day1_return) as avg_return
        FROM daily_movers
        WHERE float_size < 5000000 AND day1_return IS NOT NULL
    """)
    
    micro_float = c.fetchone()
    
    if micro_float and micro_float[0] > 0:
        total, winners, avg_return = micro_float
        win_rate = (winners / total) * 100
        
        print(f"\n🔬 MICRO FLOAT (<5M) Pattern:")
        print(f"   Total signals: {total}")
        print(f"   Winners: {winners}")
        print(f"   Win rate: {win_rate:.1f}%")
        print(f"   Avg return: {avg_return:.1f}%")
        
        c.execute("""
            INSERT OR REPLACE INTO pattern_learnings 
            (pattern_name, last_updated, total_signals, correct_signals, win_rate, avg_return, criteria)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'MICRO_FLOAT',
            datetime.now().isoformat(),
            total,
            winners,
            win_rate,
            avg_return,
            'float_size < 5000000'
        ))
    
    conn.commit()
    conn.close()
    
    print("\n✅ Pattern learnings updated")

# =============================================================================
# REPORTING
# =============================================================================

def daily_report():
    """Generate daily performance report"""
    print("\n" + "=" * 70)
    print("📊 DAILY PERFORMANCE REPORT")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Last 7 days win rate
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    c.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN outcome = 'WINNER' THEN 1 ELSE 0 END) as winners,
            AVG(day1_return) as avg_return
        FROM daily_movers
        WHERE date >= ? AND day1_return IS NOT NULL
    """, (week_ago,))
    
    last_week = c.fetchone()
    
    if last_week and last_week[0] > 0:
        total, winners, avg_return = last_week
        win_rate = (winners / total) * 100
        
        print(f"\n📈 Last 7 Days:")
        print(f"   Total signals: {total}")
        print(f"   Winners: {winners}")
        print(f"   Win rate: {win_rate:.1f}%")
        print(f"   Avg Day 1 return: {avg_return:+.1f}%")
    
    # Best patterns
    print(f"\n🏆 Best Performing Patterns:")
    
    c.execute("""
        SELECT pattern_name, total_signals, win_rate, avg_return
        FROM pattern_learnings
        WHERE total_signals >= 3
        ORDER BY win_rate DESC
        LIMIT 5
    """)
    
    for pattern_name, total, win_rate, avg_return in c.fetchall():
        print(f"   {pattern_name}: {win_rate:.1f}% win rate ({total} signals, avg {avg_return:+.1f}%)")
    
    conn.close()

# =============================================================================
# MAIN WORKFLOW
# =============================================================================

def end_of_day_workflow():
    """Run this at market close (4:00 PM)"""
    init_database()
    log_todays_movers()
    daily_report()

def morning_workflow():
    """Run this at market open (9:31 AM)"""
    init_database()
    validate_yesterday()
    update_learnings()
    daily_report()

def full_workflow():
    """Run both - useful for backfill"""
    init_database()
    validate_yesterday()
    update_learnings()
    log_todays_movers()
    daily_report()

# =============================================================================
# MANUAL QUERIES
# =============================================================================

def show_ticker_history(ticker):
    """Show all history for a ticker"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        SELECT date, move_pct, legs_score, verdict, day1_return, outcome
        FROM daily_movers
        WHERE ticker = ?
        ORDER BY date DESC
    """, (ticker,))
    
    print(f"\n📊 {ticker} History:")
    print("-" * 70)
    
    for row in c.fetchall():
        date, move_pct, legs_score, verdict, day1_return, outcome = row
        print(f"{date}: {move_pct:+.1f}% | Score: {legs_score} | {verdict}")
        if day1_return:
            print(f"         → Day 1: {day1_return:+.1f}% ({outcome})")
    
    conn.close()

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
🐺 DAILY TRACKER - The Memory Loop
===================================

Commands:
  python daily_tracker.py end      # 4:00 PM - Log today's movers
  python daily_tracker.py morning  # 9:31 AM - Validate yesterday
  python daily_tracker.py full     # Run both (backfill mode)
  python daily_tracker.py report   # Show performance report
  python daily_tracker.py ticker ATON  # Show ticker history

The Workflow:
  Every day at close: Log everything that moved
  Next morning: Validate - were we right?
  System learns: Update pattern win rates
  Repeat: Every day, we get smarter

NOT statistical bullshit. REAL money-making edges.
        """)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'end':
        end_of_day_workflow()
    elif cmd == 'morning':
        morning_workflow()
    elif cmd == 'full':
        full_workflow()
    elif cmd == 'report':
        init_database()
        daily_report()
    elif cmd == 'ticker' and len(sys.argv) > 2:
        ticker = sys.argv[2].upper()
        show_ticker_history(ticker)
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
