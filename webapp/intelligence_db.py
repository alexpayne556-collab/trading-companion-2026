"""
Learning Database - Track everything, learn patterns in real-time
"""

import sqlite3
from datetime import datetime
import json

DB_PATH = '/workspaces/trading-companion-2026/research/intelligence.db'

def init_intelligence_db():
    """Initialize the learning database"""
    conn = sqlite3.connect(DB_PATH)
    
    # Scans: Every time we check prices
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_time TIMESTAMP,
            ticker TEXT,
            price REAL,
            volume INTEGER,
            change_pct REAL,
            tier TEXT
        )
    ''')
    
    # Catalysts: News events we detect
    conn.execute('''
        CREATE TABLE IF NOT EXISTS catalysts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detected_at TIMESTAMP,
            ticker TEXT,
            catalyst_type TEXT,
            headline TEXT,
            url TEXT,
            keywords TEXT,
            initial_move_pct REAL
        )
    ''')
    
    # Patterns: Track outcomes to learn what works
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pattern_outcomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            pattern_type TEXT,
            entry_date TIMESTAMP,
            entry_price REAL,
            catalyst TEXT,
            day1_close REAL,
            day2_close REAL,
            day3_close REAL,
            day5_close REAL,
            peak_price REAL,
            peak_day INTEGER,
            final_outcome TEXT,
            notes TEXT
        )
    ''')
    
    # Positions: Track what we're holding
    conn.execute('''
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            entry_date TIMESTAMP,
            entry_price REAL,
            pattern_type TEXT,
            catalyst TEXT,
            exit_date TIMESTAMP,
            exit_price REAL,
            exit_reason TEXT,
            gain_loss_pct REAL,
            days_held INTEGER,
            status TEXT
        )
    ''')
    
    # Alerts: Log every alert we generate
    conn.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_time TIMESTAMP,
            alert_type TEXT,
            ticker TEXT,
            message TEXT,
            data TEXT
        )
    ''')
    
    # Market events: CPI, FOMC, etc - track what happened
    conn.execute('''
        CREATE TABLE IF NOT EXISTS market_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_date DATE,
            event_type TEXT,
            expected_value TEXT,
            actual_value TEXT,
            market_reaction TEXT,
            top_gainers TEXT,
            top_losers TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def log_scan(ticker, price, volume, change_pct, tier=None):
    """Log a price scan"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        INSERT INTO scans (scan_time, ticker, price, volume, change_pct, tier)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.now(), ticker, price, volume, change_pct, tier))
    conn.commit()
    conn.close()

def log_catalyst(ticker, catalyst_type, headline, url, keywords, initial_move_pct):
    """Log a detected catalyst"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        INSERT INTO catalysts (detected_at, ticker, catalyst_type, headline, url, keywords, initial_move_pct)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.now(), ticker, catalyst_type, headline, url, keywords, initial_move_pct))
    conn.commit()
    conn.close()

def log_pattern_outcome(ticker, pattern_type, entry_date, entry_price, catalyst, 
                        day1_close, day2_close=None, day3_close=None, day5_close=None,
                        peak_price=None, peak_day=None, final_outcome=None, notes=None):
    """Track how a pattern played out"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        INSERT INTO pattern_outcomes 
        (ticker, pattern_type, entry_date, entry_price, catalyst,
         day1_close, day2_close, day3_close, day5_close,
         peak_price, peak_day, final_outcome, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (ticker, pattern_type, entry_date, entry_price, catalyst,
          day1_close, day2_close, day3_close, day5_close,
          peak_price, peak_day, final_outcome, notes))
    conn.commit()
    conn.close()

def log_alert(alert_type, ticker, message, data=None):
    """Log an alert"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        INSERT INTO alerts (alert_time, alert_type, ticker, message, data)
        VALUES (?, ?, ?, ?, ?)
    ''', (datetime.now(), alert_type, ticker, message, json.dumps(data) if data else None))
    conn.commit()
    conn.close()

def get_pattern_stats(pattern_type):
    """Learn: What's the success rate of this pattern?"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute('''
        SELECT 
            COUNT(*) as total,
            AVG(CASE WHEN final_outcome = 'WIN' THEN 1 ELSE 0 END) as win_rate,
            AVG(peak_price - entry_price) / AVG(entry_price) * 100 as avg_peak_gain,
            AVG(peak_day) as avg_peak_day
        FROM pattern_outcomes
        WHERE pattern_type = ?
    ''', (pattern_type,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] > 0:
        return {
            'total': result[0],
            'win_rate': result[1] * 100 if result[1] else 0,
            'avg_peak_gain': result[2] if result[2] else 0,
            'avg_peak_day': result[3] if result[3] else 0
        }
    return None

def get_ticker_history(ticker, days=30):
    """Get scan history for a ticker"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute('''
        SELECT scan_time, price, volume, change_pct
        FROM scans
        WHERE ticker = ?
        AND scan_time > datetime('now', '-' || ? || ' days')
        ORDER BY scan_time DESC
    ''', (ticker, days))
    
    results = []
    for row in cursor:
        results.append({
            'time': row[0],
            'price': row[1],
            'volume': row[2],
            'change_pct': row[3]
        })
    
    conn.close()
    return results

def get_recent_catalysts(hours=24):
    """Get catalysts detected in last N hours"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute('''
        SELECT detected_at, ticker, catalyst_type, headline, url, initial_move_pct
        FROM catalysts
        WHERE detected_at > datetime('now', '-' || ? || ' hours')
        ORDER BY detected_at DESC
    ''', (hours,))
    
    results = []
    for row in cursor:
        results.append({
            'time': row[0],
            'ticker': row[1],
            'type': row[2],
            'headline': row[3],
            'url': row[4],
            'move': row[5]
        })
    
    conn.close()
    return results

def get_active_positions():
    """Get current open positions"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute('''
        SELECT ticker, entry_date, entry_price, pattern_type, catalyst,
               (julianday('now') - julianday(entry_date)) as days_held
        FROM positions
        WHERE status = 'OPEN'
        ORDER BY entry_date DESC
    ''')
    
    results = []
    for row in cursor:
        results.append({
            'ticker': row[0],
            'entry_date': row[1],
            'entry_price': row[2],
            'pattern': row[3],
            'catalyst': row[4],
            'days_held': int(row[5])
        })
    
    conn.close()
    return results

def get_recent_alerts(count=50):
    """Get recent alerts"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute('''
        SELECT alert_time, alert_type, ticker, message
        FROM alerts
        ORDER BY alert_time DESC
        LIMIT ?
    ''', (count,))
    
    results = []
    for row in cursor:
        results.append({
            'time': row[0],
            'type': row[1],
            'ticker': row[2],
            'message': row[3]
        })
    
    conn.close()
    return results

if __name__ == '__main__':
    init_intelligence_db()
    print("✅ Intelligence database initialized")
