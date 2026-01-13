"""
🐺 CATALYST SCANNER - Based on Real Research
Patterns discovered from 2 weeks of tracking actual moves
"""

import feedparser
import re
from datetime import datetime
import yfinance as yf
from collections import defaultdict
import sqlite3
import logging

logger = logging.getLogger(__name__)

# Your discovered catalyst keywords by pattern type
CATALYST_PATTERNS = {
    'GPU_AI_CONTRACT': [
        'nvidia', 'gpu', 'b300', 'b200', 'blackwell', 'ai contract',
        'enterprise ai', 'gpu contract', 'government contract ai'
    ],
    'CLINICAL_TRIAL': [
        'phase 3', 'phase 2', 'phase 1', 'trial results', 'clinical trial',
        'endpoints met', 'fda', 'approval', 'onward', 'clinical data'
    ],
    'GOVERNMENT_CONTRACT': [
        'government contract', 'defense contract', 'mda shield',
        'department of defense', 'dod', 'navy', 'air force', 'army'
    ],
    'OPERATIONAL_MILESTONE': [
        'operational', 'facility', 'launch', 'opening', 'begins operations',
        'commenced', 'lounge operational', 'product launch'
    ],
    'MERGER_ACQUISITION': [
        'merger', 'acquisition', 'merger agreement', 'framework', 'per share',
        'to acquire', 'to merge', 'combination'
    ]
}

# News sources from your research
NEWS_FEEDS = [
    'https://www.globenewswire.com/en/RssFeed/subjectcode/60-AI/feedTitle/GlobeNewswire%20-%20AI%20News',
    'https://www.prnewswire.com/rss/healthcare-latest-news/healthcare-and-pharmaceuticals-latest-news.rss',
    'https://www.prnewswire.com/rss/technology-latest-news/technology-latest-news.rss'
]

# Tickers from your research
CATALYST_WATCHLIST = {
    'GPU_AI': ['EVTV', 'ATON', 'VCIG', 'DGXX'],
    'BIOTECH': ['ALMS', 'BEAM', 'RARE', 'NTLA', 'XBIO', 'SRPT', 'ARWR'],
    'DEFENSE_SPACE': ['MNTS', 'KTOS', 'RCAT', 'SATL'],
    'EV': ['BLNK'],
    'CRYPTO': ['BKKT']
}


class CatalystScanner:
    """Scans for catalysts based on your discovered patterns"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize catalyst tracking database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS catalysts (
                id INTEGER PRIMARY KEY,
                detected_at TIMESTAMP,
                symbol TEXT,
                catalyst_type TEXT,
                headline TEXT,
                url TEXT,
                keywords TEXT,
                move_pct REAL,
                pattern TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def scan_news(self):
        """Scan news feeds for catalyst keywords"""
        catalysts_found = []
        
        for feed_url in NEWS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:20]:  # Latest 20
                    title = entry.title.lower()
                    summary = entry.get('summary', '').lower()
                    text = f"{title} {summary}"
                    
                    # Check each catalyst pattern
                    for catalyst_type, keywords in CATALYST_PATTERNS.items():
                        matches = [kw for kw in keywords if kw in text]
                        
                        if matches:
                            # Extract ticker symbols
                            symbols = self.extract_tickers(entry.title, entry.get('summary', ''))
                            
                            catalyst = {
                                'catalyst_type': catalyst_type,
                                'headline': entry.title,
                                'url': entry.link,
                                'keywords': ', '.join(matches),
                                'symbols': symbols,
                                'published': entry.get('published', ''),
                                'detected_at': datetime.now().isoformat()
                            }
                            
                            catalysts_found.append(catalyst)
                            logger.info(f"🎯 CATALYST: {catalyst_type} - {entry.title}")
            
            except Exception as e:
                logger.error(f"Error parsing feed {feed_url}: {e}")
        
        return catalysts_found
    
    def extract_tickers(self, title, summary):
        """Extract ticker symbols from news text"""
        text = f"{title} {summary}"
        
        # Look for ticker pattern: $TICKER or (NASDAQ: TICKER)
        ticker_pattern = r'\$([A-Z]{2,5})|(?:NASDAQ|NYSE|OTCQB):\s*([A-Z]{2,5})'
        matches = re.findall(ticker_pattern, text.upper())
        
        tickers = [m[0] or m[1] for m in matches if m[0] or m[1]]
        
        # Also check if watchlist tickers are mentioned
        for category, symbols in CATALYST_WATCHLIST.items():
            for symbol in symbols:
                if symbol.lower() in text.lower():
                    tickers.append(symbol)
        
        return list(set(tickers))
    
    def detect_sector_heat(self, movements):
        """Detect if multiple stocks in same sector are moving"""
        sector_counts = defaultdict(list)
        
        for movement in movements:
            symbol = movement['symbol']
            
            # Categorize by sector
            for sector, tickers in CATALYST_WATCHLIST.items():
                if symbol in tickers:
                    sector_counts[sector].append(movement)
        
        hot_sectors = {}
        for sector, moves in sector_counts.items():
            if len(moves) >= 2:  # 2+ stocks moving = hot sector
                hot_sectors[sector] = {
                    'count': len(moves),
                    'symbols': [m['symbol'] for m in moves],
                    'avg_move': sum(m['movement_pct'] for m in moves) / len(moves)
                }
                logger.info(f"🔥 HOT SECTOR: {sector} - {len(moves)} stocks moving")
        
        return hot_sectors
    
    def check_pattern_match(self, symbol, movement_pct, catalyst_type):
        """Match movement to your discovered patterns"""
        
        # Pattern 1: Binary Events (Clinical Trials)
        if catalyst_type == 'CLINICAL_TRIAL':
            if movement_pct > 50:
                return 'BINARY_EVENT_GAP'  # ALMS pattern
        
        # Pattern 2: GPU/AI Contracts
        elif catalyst_type == 'GPU_AI_CONTRACT':
            if movement_pct > 100:
                return 'GPU_WHALE'  # EVTV pattern
            elif movement_pct > 20:
                return 'GPU_FISH'  # ATON/VCIG pattern
        
        # Pattern 3: Government/Defense Contracts
        elif catalyst_type == 'GOVERNMENT_CONTRACT':
            if movement_pct > 30:
                return 'MULTIDAY_RUNNER'  # MNTS pattern
        
        # Pattern 4: Operational Milestones
        elif catalyst_type == 'OPERATIONAL_MILESTONE':
            if movement_pct > 20:
                return 'INTRADAY_BUILD'  # VCIG operational pattern
        
        return 'UNKNOWN_PATTERN'
    
    def log_catalyst(self, catalyst, movement=None):
        """Log detected catalyst to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            for symbol in catalyst['symbols']:
                pattern = None
                move_pct = None
                
                if movement:
                    move_pct = movement.get('movement_pct')
                    pattern = self.check_pattern_match(
                        symbol, move_pct, catalyst['catalyst_type']
                    )
                
                conn.execute('''
                    INSERT INTO catalysts (
                        detected_at, symbol, catalyst_type, headline,
                        url, keywords, move_pct, pattern
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now(),
                    symbol,
                    catalyst['catalyst_type'],
                    catalyst['headline'],
                    catalyst['url'],
                    catalyst['keywords'],
                    move_pct,
                    pattern
                ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error logging catalyst: {e}")
    
    def get_today_catalysts(self):
        """Get catalysts detected today"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute('''
                SELECT symbol, catalyst_type, headline, keywords, move_pct, pattern
                FROM catalysts
                WHERE DATE(detected_at) = DATE("now")
                ORDER BY detected_at DESC
            ''')
            
            catalysts = []
            for row in cursor:
                catalysts.append({
                    'symbol': row[0],
                    'catalyst_type': row[1],
                    'headline': row[2],
                    'keywords': row[3],
                    'move_pct': row[4],
                    'pattern': row[5]
                })
            
            conn.close()
            return catalysts
        except:
            return []
    
    def get_pattern_stats(self):
        """Get statistics on which patterns are working"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute('''
                SELECT 
                    pattern,
                    COUNT(*) as count,
                    AVG(move_pct) as avg_move,
                    MAX(move_pct) as max_move
                FROM catalysts
                WHERE pattern IS NOT NULL
                GROUP BY pattern
                ORDER BY avg_move DESC
            ''')
            
            stats = {}
            for row in cursor:
                stats[row[0]] = {
                    'count': row[1],
                    'avg_move': round(row[2], 1) if row[2] else 0,
                    'max_move': round(row[3], 1) if row[3] else 0
                }
            
            conn.close()
            return stats
        except:
            return {}
