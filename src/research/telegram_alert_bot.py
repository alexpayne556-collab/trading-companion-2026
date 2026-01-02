#!/usr/bin/env python3
"""
🐺 TELEGRAM ALERT BOT

Sends instant mobile notifications for trading alerts
Better than email - instant, free, reliable, two-way commands

Setup Instructions:
1. Message @BotFather on Telegram
2. Create new bot: /newbot
3. Copy bot token
4. Create .env file: TELEGRAM_BOT_TOKEN=your_token_here
5. Get your chat ID: Run bot, send it a message, check logs
6. Update .env: TELEGRAM_CHAT_ID=your_chat_id

Author: Brokkr (Brother Mode)
Date: January 2, 2026
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests not available. Install with: pip install requests")


class TelegramAlertBot:
    """
    Telegram bot for instant trading alerts
    Free, fast, reliable, works worldwide
    """
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token:
            print("⚠️  TELEGRAM_BOT_TOKEN not set in environment")
            print("   Create .env file with: TELEGRAM_BOT_TOKEN=your_token_here")
            self.enabled = False
        elif not self.chat_id:
            print("⚠️  TELEGRAM_CHAT_ID not set in environment")
            print("   Run bot once to get your chat ID, then add to .env")
            self.enabled = False
        else:
            self.enabled = True
            self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        Send message to Telegram
        
        Args:
            message: Text to send (supports HTML formatting)
            parse_mode: 'HTML' or 'Markdown'
        
        Returns:
            True if sent successfully
        """
        if not self.enabled or not REQUESTS_AVAILABLE:
            print(f"📱 [TELEGRAM] {message}")
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"⚠️ Telegram API error: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"⚠️ Failed to send Telegram message: {e}")
            return False
    
    def send_premarket_gaps(self, gaps: List[Dict]):
        """Send pre-market gap alerts"""
        if not gaps:
            return
        
        message = "🌅 <b>PRE-MARKET GAPS DETECTED</b>\n\n"
        
        for gap in gaps[:5]:  # Top 5
            emoji = '🚀' if gap['gap_pct'] > 0 else '💀'
            message += f"{emoji} <b>{gap['ticker']}</b>: {gap['gap_pct']:+.2f}%\n"
            message += f"   ${gap['previous_close']:.2f} → ${gap['premarket_price']:.2f}\n"
            message += f"   Vol: {gap['premarket_volume']:,}\n\n"
        
        message += f"🕐 {datetime.now().strftime('%I:%M %p EST')}"
        
        self.send_message(message)
    
    def send_afterhours_moves(self, moves: List[Dict]):
        """Send after-hours movement alerts"""
        if not moves:
            return
        
        message = "🌙 <b>AFTER-HOURS MOVERS</b>\n\n"
        
        for move in moves[:5]:  # Top 5
            emoji = '📈' if move['move_pct'] > 0 else '📉'
            message += f"{emoji} <b>{move['ticker']}</b>: {move['move_pct']:+.2f}%\n"
            message += f"   ${move['regular_close']:.2f} → ${move['afterhours_price']:.2f}\n"
            message += f"   Vol: {move['afterhours_volume']:,}\n\n"
        
        message += f"🕐 {datetime.now().strftime('%I:%M %p EST')}"
        
        self.send_message(message)
    
    def send_position_alert(self, position: Dict):
        """Send position risk alert"""
        emoji = '🚨' if position.get('distance_to_stop_pct', 999) < 5 else '⚠️'
        
        message = f"{emoji} <b>POSITION ALERT: {position['ticker']}</b>\n\n"
        message += f"Session: {position['session']}\n"
        message += f"P&L: ${position['pnl_total']:+.2f} ({position['pnl_pct']:+.2f}%)\n"
        message += f"Price: ${position['current_price']:.2f}\n"
        
        if position.get('stop_loss', 0) > 0:
            message += f"Stop: ${position['stop_loss']:.2f} ({position['distance_to_stop_pct']:.1f}% away)\n"
        
        if position.get('alert_conditions'):
            message += f"\n⚠️ {', '.join(position['alert_conditions'])}"
        
        message += f"\n\n🕐 {datetime.now().strftime('%I:%M %p EST')}"
        
        self.send_message(message)
    
    def send_form4_cluster(self, cluster: Dict):
        """Send Form 4 cluster detection alert"""
        message = "🎯 <b>INSIDER CLUSTER DETECTED</b>\n\n"
        message += f"<b>{cluster['ticker']}</b>\n"
        message += f"Insiders: {cluster['insider_count']}\n"
        message += f"Total Value: ${cluster['total_value']:,.0f}\n"
        message += f"Timeframe: {cluster['days']} days\n\n"
        
        if 'insiders' in cluster:
            message += "Buyers:\n"
            for insider in cluster['insiders'][:3]:  # Top 3
                message += f"  • {insider['name']}: {insider['shares']:,} shares\n"
        
        message += f"\n🕐 {datetime.now().strftime('%I:%M %p EST')}"
        
        self.send_message(message)
    
    def send_sector_rotation_alert(self, sector: Dict):
        """Send hot sector alert"""
        message = "🔥 <b>SECTOR ROTATION ALERT</b>\n\n"
        message += f"<b>{sector['name']}</b> ({sector['etf']})\n"
        message += f"Move: {sector['performance']:+.2f}%\n\n"
        
        if 'tickers' in sector:
            message += "Watch:\n"
            for ticker in sector['tickers'][:5]:
                message += f"  • {ticker}\n"
        
        message += f"\n🕐 {datetime.now().strftime('%I:%M %p EST')}"
        
        self.send_message(message)
    
    def send_high_conviction_setup(self, signal: Dict):
        """Send high conviction trading setup"""
        message = "🐺 <b>HIGH CONVICTION SETUP</b>\n\n"
        message += f"<b>{signal['ticker']}</b> - {signal['total_score']}/100\n"
        message += f"Price: ${signal['current_price']:.2f}\n\n"
        
        message += "Patterns:\n"
        for pattern in signal['patterns'][:4]:
            message += f"  • {pattern['name']}: +{pattern['score']} pts\n"
        
        if signal.get('ml_probability', 0) > 0:
            message += f"\nML Probability: {signal['ml_probability']:.0%}\n"
        
        message += f"\n🕐 {datetime.now().strftime('%I:%M %p EST')}"
        
        self.send_message(message)
    
    def send_morning_report(self, report: Dict):
        """Send comprehensive morning report"""
        message = "🐺 <b>WOLF PACK MORNING REPORT</b>\n\n"
        message += f"📅 {datetime.now().strftime('%A, %B %d, %Y')}\n\n"
        
        # Portfolio
        if 'portfolio' in report:
            message += f"💰 Cash: ${report['portfolio']['cash']:,.0f}\n"
            message += f"📊 Positions: {report['portfolio']['positions']}\n\n"
        
        # Pre-market gaps
        if 'gaps' in report and report['gaps']:
            message += "🌅 <b>Pre-Market Gaps:</b>\n"
            for gap in report['gaps'][:3]:
                emoji = '🚀' if gap['gap_pct'] > 0 else '💀'
                message += f"  {emoji} {gap['ticker']}: {gap['gap_pct']:+.2f}%\n"
            message += "\n"
        
        # Top setups
        if 'setups' in report and report['setups']:
            message += "🎯 <b>Top Setups:</b>\n"
            for setup in report['setups'][:3]:
                message += f"  • {setup['ticker']} ({setup['score']}/100)\n"
            message += "\n"
        
        # Hot sectors
        if 'hot_sectors' in report and report['hot_sectors']:
            message += "🔥 <b>Hot Sectors:</b>\n"
            for sector in report['hot_sectors'][:2]:
                message += f"  • {sector['name']}: {sector['performance']:+.1f}%\n"
            message += "\n"
        
        message += "AWOOOO 🐺"
        
        self.send_message(message)
    
    def get_updates(self) -> List[Dict]:
        """Get messages sent to bot (for two-way communication)"""
        if not self.enabled or not REQUESTS_AVAILABLE:
            return []
        
        try:
            url = f"{self.base_url}/getUpdates"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('result', [])
            
            return []
        
        except Exception as e:
            print(f"⚠️ Failed to get Telegram updates: {e}")
            return []
    
    def get_chat_id_from_updates(self):
        """Helper: Get your chat ID from recent messages"""
        print("Checking for messages...")
        
        updates = self.get_updates()
        
        if updates:
            for update in updates:
                if 'message' in update:
                    chat_id = update['message']['chat']['id']
                    username = update['message']['chat'].get('username', 'Unknown')
                    text = update['message'].get('text', '')
                    
                    print(f"\n✅ Found message from @{username}")
                    print(f"   Chat ID: {chat_id}")
                    print(f"   Message: {text}")
                    print(f"\nAdd to your .env file:")
                    print(f"TELEGRAM_CHAT_ID={chat_id}")
                    
                    return chat_id
        else:
            print("No messages found. Send a message to your bot first.")
            return None
    
    def test_connection(self):
        """Test bot connection and send test message"""
        if not self.enabled:
            print("❌ Bot not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")
            return False
        
        message = "🐺 <b>Wolf Pack Alert System</b>\n\n"
        message += "✅ Connection successful!\n"
        message += f"🕐 {datetime.now().strftime('%I:%M %p EST')}\n\n"
        message += "Ready to receive trading alerts.\n\n"
        message += "AWOOOO 🐺"
        
        success = self.send_message(message)
        
        if success:
            print("✅ Test message sent successfully!")
        else:
            print("❌ Failed to send test message")
        
        return success


def main():
    """CLI interface"""
    import sys
    
    bot = TelegramAlertBot()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            # Test connection
            bot.test_connection()
        
        elif command == 'getchatid':
            # Get chat ID from messages
            if not bot.bot_token:
                print("Set TELEGRAM_BOT_TOKEN first")
            else:
                # Temporary bot to get updates
                temp_bot = TelegramAlertBot()
                temp_bot.enabled = True
                temp_bot.base_url = f"https://api.telegram.org/bot{bot.bot_token}"
                temp_bot.get_chat_id_from_updates()
        
        elif command == 'demo':
            # Send demo alerts
            print("Sending demo alerts...")
            
            # Demo gap alert
            bot.send_premarket_gaps([
                {'ticker': 'AISP', 'gap_pct': 5.2, 'previous_close': 3.13, 
                 'premarket_price': 3.29, 'premarket_volume': 125000}
            ])
            
            # Demo position alert
            bot.send_position_alert({
                'ticker': 'AISP',
                'session': 'AFTER-HOURS',
                'pnl_total': 12.45,
                'pnl_pct': 3.8,
                'current_price': 3.25,
                'stop_loss': 2.30,
                'distance_to_stop_pct': 29.2,
                'alert_conditions': []
            })
    
    else:
        print("Usage:")
        print("  python telegram_alert_bot.py test        # Test connection")
        print("  python telegram_alert_bot.py getchatid   # Get your chat ID")
        print("  python telegram_alert_bot.py demo        # Send demo alerts")
        print("\nSetup:")
        print("1. Message @BotFather on Telegram: /newbot")
        print("2. Copy bot token to .env: TELEGRAM_BOT_TOKEN=your_token")
        print("3. Run: python telegram_alert_bot.py getchatid")
        print("4. Send any message to your bot")
        print("5. Copy chat ID to .env: TELEGRAM_CHAT_ID=your_chat_id")
        print("6. Test: python telegram_alert_bot.py test")


if __name__ == '__main__':
    main()
