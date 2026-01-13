#!/usr/bin/env python3
"""
🐺 TRADING COMPANION 2026 - PRODUCTION SYSTEM
Real foundation. Real data. Real functionality.
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import sqlite3
import yfinance as yf
from datetime import datetime
import threading
import time
import os
import sys
import logging

# Add parent to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import catalyst scanner
from catalyst_scanner import CatalystScanner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'brokkr-2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Paths
BASE_DIR = '/workspaces/trading-companion-2026'
DB_PATH = f'{BASE_DIR}/research/movements.db'
CATALYST_DB_PATH = f'{BASE_DIR}/research/catalysts.db'
WATCHLIST_PATH = f'{BASE_DIR}/watchlist.txt'

# State
sonar_active = False
scanner = None
catalyst_scanner = CatalystScanner(CATALYST_DB_PATH)


def init_database():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detected_at TIMESTAMP,
            symbol TEXT,
            movement_pct REAL,
            tier TEXT,
            baseline_price REAL,
            current_price REAL,
            alert_level TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("✅ Database ready")


def load_watchlist():
    """Load watchlist"""
    if os.path.exists(WATCHLIST_PATH):
        with open(WATCHLIST_PATH, 'r') as f:
            tickers = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return tickers
    return ['ATON', 'EVTV', 'LVLU', 'PASW', 'ALMS', 'BEAM']


class SonarScanner:
    """Movement scanner"""
    
    def __init__(self, tickers):
        self.tickers = tickers
        self.baseline = {}
        logger.info(f"Scanner: {len(tickers)} tickers")
    
    def set_baseline(self):
        """Set baseline prices"""
        for ticker in self.tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1d')
                if not hist.empty:
                    self.baseline[ticker] = float(hist['Close'].iloc[-1])
            except:
                pass
        logger.info(f"Baseline: {len(self.baseline)} tickers")
    
    def scan(self):
        """Scan for movements"""
        movements = []
        logger.info(f"Scanning {len(self.baseline)} tickers...")
        
        for ticker, baseline in self.baseline.items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1d', interval='5m')
                
                if hist.empty:
                    continue
                
                current = float(hist['Close'].iloc[-1])
                change_pct = ((current - baseline) / baseline) * 100
                
                # Log all movements for debugging
                logger.info(f"{ticker}: ${baseline:.2f} -> ${current:.2f} ({change_pct:+.1f}%)")
                
                if abs(change_pct) >= 5:
                    if abs(change_pct) >= 100:
                        tier, alert = 'WHALE', 'CRITICAL'
                    elif abs(change_pct) >= 20:
                        tier, alert = 'FISH', 'HIGH'
                    elif abs(change_pct) >= 10:
                        tier, alert = 'BASS', 'MEDIUM'
                    else:
                        tier, alert = 'NIBBLE', 'LOW'
                    
                    movement = {
                        'symbol': ticker,
                        'movement_pct': round(change_pct, 2),
                        'tier': tier,
                        'alert_level': alert,
                        'baseline_price': round(baseline, 2),
                        'current_price': round(current, 2),
                        'detected_at': datetime.now().isoformat()
                    }
                    
                    movements.append(movement)
                    self.log_db(movement)
                    logger.info(f"🎯 DETECTED: {tier} {ticker} {change_pct:+.1f}%")
            except Exception as e:
                logger.error(f"Error scanning {ticker}: {e}")
        
        logger.info(f"Scan complete: {len(movements)} movements detected")
        return movements
    
    def log_db(self, m):
        """Log to database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute('''
                INSERT INTO movements (detected_at, symbol, movement_pct, tier, baseline_price, current_price, alert_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (datetime.now(), m['symbol'], m['movement_pct'], m['tier'], m['baseline_price'], m['current_price'], m['alert_level']))
            conn.commit()
            conn.close()
        except:
            pass


def sonar_loop():
    """Background scanner with catalyst detection"""
    global sonar_active, scanner, catalyst_scanner
    
    while sonar_active:
        try:
            # Scan for price movements
            movements = scanner.scan()
            
            # Scan for news catalysts
            catalysts = catalyst_scanner.scan_news()
            
            # Detect sector heat
            hot_sectors = catalyst_scanner.detect_sector_heat(movements)
            
            # Emit to frontend
            socketio.emit('sonar_ping', {
                'movements': movements,
                'catalysts': catalysts,
                'hot_sectors': hot_sectors,
                'timestamp': datetime.now().isoformat(),
                'count': len(movements)
            })
            
            logger.info(f"Ping: {len(movements)} movements, {len(catalysts)} catalysts, {len(hot_sectors)} hot sectors")
            time.sleep(300)  # 5 minutes
        except Exception as e:
            logger.error(f"Loop error: {e}")
            time.sleep(60)


@app.route('/')
def index():
    return render_template('dashboard.html')


@app.route('/api/sonar/start', methods=['POST'])
def start_sonar():
    global sonar_active, scanner
    
    if sonar_active:
        return jsonify({'status': 'running'})
    
    tickers = load_watchlist()
    scanner = SonarScanner(tickers)
    scanner.set_baseline()
    
    sonar_active = True
    threading.Thread(target=sonar_loop, daemon=True).start()
    
    return jsonify({'status': 'started', 'tickers': len(tickers)})


@app.route('/api/sonar/stop', methods=['POST'])
def stop_sonar():
    global sonar_active
    sonar_active = False
    return jsonify({'status': 'stopped'})


@app.route('/api/movements/today')
def get_movements():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute('''
            SELECT symbol, movement_pct, tier, detected_at, current_price
            FROM movements
            WHERE DATE(detected_at) = DATE("now")
            ORDER BY ABS(movement_pct) DESC
            LIMIT 50
        ''')
        
        movements = [{'symbol': r[0], 'movement_pct': r[1], 'tier': r[2], 'detected_at': r[3], 'current_price': r[4]} for r in cursor]
        conn.close()
        
        return jsonify(movements)
    except Exception as e:
        logger.error(f"Movements error: {e}")
        return jsonify([])


@app.route('/api/movements/stats')
def get_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute('''
            SELECT tier, COUNT(*) FROM movements
            WHERE DATE(detected_at) = DATE("now")
            GROUP BY tier
        ''')
        
        stats = {}
        for row in cursor:
            stats[row[0]] = row[1]
        
        conn.close()
        
        return jsonify({
            'total': sum(stats.values()),
            'whales': stats.get('WHALE', 0),
            'fish': stats.get('FISH', 0),
            'bass': stats.get('BASS', 0),
            'nibbles': stats.get('NIBBLE', 0)
        })
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'total': 0, 'whales': 0, 'fish': 0, 'bass': 0, 'nibbles': 0})


@app.route('/api/catalysts/today')
def get_catalysts():
    """Get today's detected catalysts"""
    try:
        catalysts = catalyst_scanner.get_today_catalysts()
        return jsonify(catalysts)
    except Exception as e:
        logger.error(f"Catalysts error: {e}")
        return jsonify([])


@app.route('/api/catalysts/patterns')
def get_catalyst_patterns():
    """Get pattern statistics from your research"""
    try:
        stats = catalyst_scanner.get_pattern_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Pattern stats error: {e}")
        return jsonify({})


if __name__ == '__main__':
    print("🐺 TRADING COMPANION 2026")
    print("=" * 60)
    init_database()
    print("Starting on http://localhost:8080")
    print("=" * 60)
    socketio.run(app, host='0.0.0.0', port=8080, debug=False, allow_unsafe_werkzeug=True)
