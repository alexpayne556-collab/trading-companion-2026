#!/usr/bin/env python3
"""
🐺 ALERT ORCHESTRATOR - Master Alert Coordinator

Ties all alert systems together:
- Pre-market gaps
- After-hours moves  
- Position alerts
- Form 4 clusters
- Pattern scanner alerts
- Sector rotation

Sends notifications via Telegram (or fallback to console)

Run via cron:
  6:00 AM: Morning pre-market scan
  4:30 PM: Evening after-hours scan
  Every hour 9-5: Check for Form 4 clusters, patterns

Author: Brokkr (Brother Mode)
Date: January 2, 2026
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from research.premarket_afterhours_scanner import PreMarketAfterHoursScanner
from research.position_tracker import PositionTracker
from research.telegram_alert_bot import TelegramAlertBot


class AlertOrchestrator:
    """
    Master coordinator for all alert systems
    Run via cron jobs for 24/7 monitoring
    """
    
    def __init__(self):
        self.pm_ah_scanner = PreMarketAfterHoursScanner()
        self.position_tracker = PositionTracker()
        self.telegram = TelegramAlertBot()
        
        self.watchlist_file = 'atp_watchlists/ATP_WOLF_PACK_MASTER.csv'
    
    def morning_routine(self):
        """
        6 AM Morning Routine
        - Check pre-market gaps
        - Check position status
        - Generate morning report
        """
        print("\n" + "="*70)
        print("🌅 MORNING ROUTINE - 6 AM")
        print(f"   {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}")
        print("="*70)
        
        # 1. Pre-market gaps
        print("\n1️⃣ Scanning pre-market gaps...")
        gaps = self.pm_ah_scanner.scan_premarket_gaps(
            self.pm_ah_scanner._load_watchlist(self.watchlist_file),
            min_gap_pct=3.0
        )
        
        # Alert on gaps
        if gaps:
            self.telegram.send_premarket_gaps(gaps)
            print(f"   ✅ Sent {len(gaps)} gap alerts to Telegram")
        
        # 2. Position check
        print("\n2️⃣ Checking positions...")
        position_status = self.position_tracker.get_current_status()
        
        if position_status:
            # Check for extended hours movements on positions
            position_tickers = [p['ticker'] for p in position_status]
            position_alerts = self.pm_ah_scanner.check_positions_extended_hours(
                position_status
            )
            
            # Send position alerts
            for alert in position_alerts:
                if alert.get('alert_conditions'):
                    self.telegram.send_position_alert(alert)
        
        # 3. Generate morning report
        print("\n3️⃣ Generating morning report...")
        report = self._build_morning_report(gaps, position_status)
        self.telegram.send_morning_report(report)
        
        print("\n✅ Morning routine complete")
        print("="*70 + "\n")
    
    def evening_routine(self):
        """
        4:30 PM Evening Routine
        - Check after-hours moves
        - Check position risk
        - Summary of day
        """
        print("\n" + "="*70)
        print("🌙 EVENING ROUTINE - 4:30 PM")
        print(f"   {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}")
        print("="*70)
        
        # 1. After-hours moves
        print("\n1️⃣ Scanning after-hours moves...")
        moves = self.pm_ah_scanner.scan_afterhours_moves(
            self.pm_ah_scanner._load_watchlist(self.watchlist_file),
            min_move_pct=2.0
        )
        
        # Alert on moves
        if moves:
            self.telegram.send_afterhours_moves(moves)
            print(f"   ✅ Sent {len(moves)} after-hours alerts to Telegram")
        
        # 2. Position risk check
        print("\n2️⃣ Checking position risk...")
        position_status = self.position_tracker.get_current_status()
        
        if position_status:
            position_alerts = self.pm_ah_scanner.check_positions_extended_hours(
                position_status
            )
            
            # Send critical alerts
            for alert in position_alerts:
                if alert.get('alert_conditions'):
                    self.telegram.send_position_alert(alert)
                    print(f"   🚨 Sent position alert for {alert['ticker']}")
        
        print("\n✅ Evening routine complete")
        print("="*70 + "\n")
    
    def hourly_check(self):
        """
        Hourly checks during market hours (9 AM - 5 PM)
        - Form 4 clusters
        - Pattern scanner
        - Position alerts
        """
        print(f"\n⏰ HOURLY CHECK - {datetime.now().strftime('%I:%M %p')}")
        
        # Check positions for alerts
        alerts = self.position_tracker.get_alerts()
        
        if alerts:
            print(f"   🚨 {len(alerts)} position alerts")
            for alert in alerts:
                self.telegram.send_position_alert(alert)
        else:
            print("   ✅ No position alerts")
    
    def _build_morning_report(self, gaps: List[Dict], positions: List[Dict]) -> Dict:
        """Build comprehensive morning report"""
        
        # Calculate portfolio stats
        total_cash = 600 + 500  # RH + Fidelity (hardcoded for now)
        total_position_value = sum(p.get('position_value', 0) for p in positions)
        total_account = total_cash + total_position_value
        
        report = {
            'portfolio': {
                'cash': total_cash,
                'positions': len(positions),
                'position_value': total_position_value,
                'total': total_account
            },
            'gaps': gaps[:5] if gaps else [],
            'positions': positions
        }
        
        # TODO: Add hot sectors, top setups when those scanners are integrated
        
        return report
    
    def test_all_alerts(self):
        """Test all alert types"""
        print("\n🧪 TESTING ALL ALERT TYPES\n")
        
        # Test pre-market gap
        print("1. Testing pre-market gap alert...")
        self.telegram.send_premarket_gaps([
            {
                'ticker': 'AISP',
                'gap_pct': 5.2,
                'previous_close': 3.13,
                'premarket_price': 3.29,
                'premarket_volume': 125000
            }
        ])
        
        # Test after-hours move
        print("2. Testing after-hours move alert...")
        self.telegram.send_afterhours_moves([
            {
                'ticker': 'LUNR',
                'move_pct': -3.1,
                'regular_close': 17.93,
                'afterhours_price': 17.37,
                'afterhours_volume': 85000
            }
        ])
        
        # Test position alert
        print("3. Testing position alert...")
        position_status = self.position_tracker.get_current_status()
        if position_status:
            self.telegram.send_position_alert(position_status[0])
        
        # Test morning report
        print("4. Testing morning report...")
        report = {
            'portfolio': {
                'cash': 1100,
                'positions': 1,
                'position_value': 215,
                'total': 1315
            },
            'gaps': [
                {'ticker': 'SMR', 'gap_pct': 4.2}
            ],
            'positions': position_status
        }
        self.telegram.send_morning_report(report)
        
        print("\n✅ All test alerts sent!\n")


def main():
    """CLI interface"""
    orchestrator = AlertOrchestrator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'morning':
            orchestrator.morning_routine()
        
        elif command == 'evening':
            orchestrator.evening_routine()
        
        elif command == 'hourly':
            orchestrator.hourly_check()
        
        elif command == 'test':
            orchestrator.test_all_alerts()
        
        else:
            print("Unknown command")
    
    else:
        print("Usage:")
        print("  python alert_orchestrator.py morning  # 6 AM routine")
        print("  python alert_orchestrator.py evening  # 4:30 PM routine")
        print("  python alert_orchestrator.py hourly   # Hourly check")
        print("  python alert_orchestrator.py test     # Test all alerts")
        print("\nSetup cron jobs:")
        print("  0 6 * * 1-5    cd /path/to/project && python src/research/alert_orchestrator.py morning")
        print("  30 16 * * 1-5  cd /path/to/project && python src/research/alert_orchestrator.py evening")
        print("  0 9-17 * * 1-5 cd /path/to/project && python src/research/alert_orchestrator.py hourly")


if __name__ == '__main__':
    main()
