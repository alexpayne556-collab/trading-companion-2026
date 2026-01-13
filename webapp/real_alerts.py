"""
Real alert system - Discord, Terminal, Log file
No API costs, just direct notifications
"""

import requests
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class AlertSystem:
    """Multi-channel alert system"""
    
    def __init__(self):
        self.alert_log = '/workspaces/trading-companion-2026/logs/alerts.log'
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')  # Optional
        
        # Create alerts log
        os.makedirs(os.path.dirname(self.alert_log), exist_ok=True)
    
    def alert(self, message, level='INFO', data=None):
        """Send alert through all channels"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_message = f"[{timestamp}] [{level}] {message}"
        
        # 1. Log to file
        with open(self.alert_log, 'a') as f:
            f.write(full_message + '\n')
            if data:
                f.write(f"   Data: {data}\n")
        
        # 2. Terminal output
        if level in ['WHALE', 'FISH', 'URGENT']:
            print("\n" + "="*80)
            print(f"🚨 {level} ALERT 🚨")
            print(full_message)
            if data:
                for k, v in data.items():
                    print(f"   {k}: {v}")
            print("="*80 + "\n")
        
        # 3. Discord webhook (if configured)
        if self.discord_webhook and level in ['WHALE', 'FISH']:
            try:
                payload = {
                    'content': f"**{level} ALERT**\n{message}",
                    'username': 'Trading Companion'
                }
                requests.post(self.discord_webhook, json=payload, timeout=5)
            except:
                pass
        
        # 4. Logger
        logger.info(full_message)
    
    def whale_alert(self, symbol, movement_pct, price, catalyst=None):
        """WHALE movement detected"""
        msg = f"🐋 WHALE: {symbol} +{movement_pct:.1f}% @ ${price:.2f}"
        
        data = {
            'Symbol': symbol,
            'Movement': f"{movement_pct:+.1f}%",
            'Price': f"${price:.2f}",
            'Catalyst': catalyst or 'Unknown',
            'Timestamp': datetime.now().isoformat()
        }
        
        self.alert(msg, level='WHALE', data=data)
    
    def fish_alert(self, symbol, movement_pct, price, catalyst=None):
        """FISH movement detected"""
        msg = f"🐟 FISH: {symbol} +{movement_pct:.1f}% @ ${price:.2f}"
        
        data = {
            'Symbol': symbol,
            'Movement': f"{movement_pct:+.1f}%",
            'Price': f"${price:.2f}",
            'Catalyst': catalyst or 'Unknown'
        }
        
        self.alert(msg, level='FISH', data=data)
    
    def news_alert(self, headline, tickers, url):
        """Hot news detected"""
        msg = f"📰 NEWS: {headline}"
        
        data = {
            'Headline': headline,
            'Tickers': ', '.join(tickers) if tickers else 'None',
            'URL': url
        }
        
        self.alert(msg, level='URGENT', data=data)
    
    def sector_heat_alert(self, sector, count, symbols):
        """Sector heating up"""
        msg = f"🔥 HOT SECTOR: {sector} - {count} stocks moving"
        
        data = {
            'Sector': sector,
            'Count': count,
            'Symbols': ', '.join(symbols)
        }
        
        self.alert(msg, level='INFO', data=data)
    
    def get_recent_alerts(self, count=20):
        """Read recent alerts from log"""
        try:
            with open(self.alert_log, 'r') as f:
                lines = f.readlines()
                return lines[-count:]
        except:
            return []
