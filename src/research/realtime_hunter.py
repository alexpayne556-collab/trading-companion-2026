#!/usr/bin/env python3
"""
🐺 REAL-TIME REPEAT RUNNER HUNTER 🐺

THE PROBLEM: We know SIDU runs 9 times a month. We know LUNR hits 5 times.
But we're not CATCHING them because we're not watching at the right moment.

THE SOLUTION: Real-time monitoring that ALERTS you the moment a repeat runner:
1. Gaps up pre-market (5%+)
2. Shows volume spike (2x+ average)
3. Breaks intraday high
4. Shows momentum ignition in first 30 minutes

Run this during market hours. It watches. It alerts. You execute.

Usage:
    python realtime_hunter.py              # Run continuous monitor
    python realtime_hunter.py --premarket  # Pre-market gaps only
    python realtime_hunter.py --test       # Test mode (one scan)

Author: Brokkr (hunting mode engaged)
Date: January 3, 2026
"""

import yfinance as yf
import time
from datetime import datetime, timedelta
from pathlib import Path
import json
import sys
import os

# Try to import for sound alerts (optional)
try:
    import subprocess
    SOUND_AVAILABLE = True
except:
    SOUND_AVAILABLE = False


class RealtimeHunter:
    """
    Watch repeat runners in real-time and alert on opportunities
    """
    
    # THE PREY - Stocks that REPEAT huge gains
    TIER_1_HUNTERS = {
        # MUST WATCH - These hit 10%+ multiple times per month
        'SIDU': {'moves': 9, 'sector': 'Space/Bio', 'avg_gain': 32},
        'RCAT': {'moves': 5, 'sector': 'Defense', 'avg_gain': 13},
        'LUNR': {'moves': 5, 'sector': 'Space', 'avg_gain': 16},
        'ASTS': {'moves': 4, 'sector': 'Space', 'avg_gain': 15},
        'RDW': {'moves': 4, 'sector': 'Space', 'avg_gain': 14},
        'CLSK': {'moves': 4, 'sector': 'Crypto', 'avg_gain': 14},
    }
    
    TIER_2_HUNTERS = {
        # HIGH PRIORITY - Move with sectors
        'IONQ': {'moves': 3, 'sector': 'Quantum', 'avg_gain': 12},
        'RGTI': {'moves': 3, 'sector': 'Quantum', 'avg_gain': 14},
        'QBTS': {'moves': 4, 'sector': 'Quantum', 'avg_gain': 15},
        'QUBT': {'moves': 3, 'sector': 'Quantum', 'avg_gain': 13},
        'SMR': {'moves': 2, 'sector': 'Nuclear', 'avg_gain': 14},
        'OKLO': {'moves': 2, 'sector': 'Nuclear', 'avg_gain': 12},
        'RKLB': {'moves': 4, 'sector': 'Space', 'avg_gain': 12},
        'BKSY': {'moves': 3, 'sector': 'Space', 'avg_gain': 12},
    }
    
    # Alert thresholds
    GAP_THRESHOLD = 5.0         # 5%+ gap = alert
    VOLUME_THRESHOLD = 2.0      # 2x average volume = alert
    INTRADAY_MOVE_THRESHOLD = 3.0  # 3%+ move from open = alert
    
    def __init__(self):
        self.all_targets = {**self.TIER_1_HUNTERS, **self.TIER_2_HUNTERS}
        self.alerts_today = []
        self.last_prices = {}
        self.data_dir = Path('logs/hunts')
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def play_alert_sound(self):
        """Play alert sound if available"""
        if SOUND_AVAILABLE:
            try:
                # Try different methods
                if sys.platform == 'darwin':  # Mac
                    subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'], capture_output=True)
                else:  # Linux
                    subprocess.run(['echo', '-e', '\a'], capture_output=True)
            except:
                pass
    
    def print_alert(self, ticker: str, alert_type: str, data: dict):
        """Print formatted alert"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        print("\n" + "🚨" * 30)
        print(f"   🐺 HUNTER ALERT - {alert_type.upper()}")
        print(f"   Time: {timestamp}")
        print("🚨" * 30)
        
        tier = "⭐⭐⭐ TIER 1" if ticker in self.TIER_1_HUNTERS else "⭐⭐ TIER 2"
        info = self.all_targets[ticker]
        
        print(f"\n   {tier}: {ticker} ({info['sector']})")
        print(f"   Historical: {info['moves']} big moves, avg +{info['avg_gain']}%")
        print(f"\n   CURRENT DATA:")
        
        for key, val in data.items():
            print(f"   • {key}: {val}")
        
        print(f"\n   🎯 ACTION: Check {ticker} NOW!")
        print("🚨" * 30 + "\n")
        
        self.play_alert_sound()
        
        # Log alert
        self.alerts_today.append({
            'time': timestamp,
            'ticker': ticker,
            'type': alert_type,
            'data': data
        })
    
    def check_premarket_gaps(self) -> list:
        """
        Check for pre-market gaps on all targets
        A gap of 5%+ on a repeat runner = HIGH PROBABILITY continuation
        """
        alerts = []
        
        print(f"\n🔍 Scanning pre-market gaps... ({datetime.now().strftime('%H:%M:%S')})")
        
        for ticker in self.all_targets:
            try:
                stock = yf.Ticker(ticker)
                
                # Get previous close and current pre-market price
                info = stock.info
                prev_close = info.get('previousClose', 0)
                premarket = info.get('preMarketPrice')
                
                if not premarket or not prev_close:
                    continue
                
                gap_pct = ((premarket - prev_close) / prev_close) * 100
                
                if gap_pct >= self.GAP_THRESHOLD:
                    alert_data = {
                        'Previous Close': f'${prev_close:.2f}',
                        'Pre-Market': f'${premarket:.2f}',
                        'Gap': f'+{gap_pct:.1f}%',
                    }
                    
                    self.print_alert(ticker, 'PRE-MARKET GAP', alert_data)
                    alerts.append({
                        'ticker': ticker,
                        'type': 'gap',
                        'gap_pct': gap_pct,
                        'premarket': premarket
                    })
                
                elif gap_pct >= 3.0:
                    # Smaller gap but worth noting
                    print(f"   👀 {ticker}: +{gap_pct:.1f}% gap (watching)")
                
            except Exception as e:
                continue
        
        if not alerts:
            print("   No significant gaps detected")
        
        return alerts
    
    def check_volume_spikes(self) -> list:
        """
        Check for unusual volume on all targets
        2x+ average volume = something is happening
        """
        alerts = []
        
        print(f"\n🔍 Scanning volume spikes... ({datetime.now().strftime('%H:%M:%S')})")
        
        for ticker in self.all_targets:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='5d', interval='1d')
                
                if len(hist) < 2:
                    continue
                
                # Today's volume vs average
                today_vol = hist['Volume'].iloc[-1]
                avg_vol = hist['Volume'].iloc[:-1].mean()
                
                if avg_vol == 0:
                    continue
                
                vol_ratio = today_vol / avg_vol
                
                # Price change
                current = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                change_pct = ((current - prev_close) / prev_close) * 100
                
                if vol_ratio >= self.VOLUME_THRESHOLD:
                    alert_data = {
                        'Price': f'${current:.2f}',
                        'Change': f'{change_pct:+.1f}%',
                        'Volume': f'{vol_ratio:.1f}x AVERAGE',
                        'Today Vol': f'{int(today_vol):,}',
                        'Avg Vol': f'{int(avg_vol):,}'
                    }
                    
                    self.print_alert(ticker, 'VOLUME SPIKE', alert_data)
                    alerts.append({
                        'ticker': ticker,
                        'type': 'volume',
                        'vol_ratio': vol_ratio,
                        'change_pct': change_pct
                    })
                
                elif vol_ratio >= 1.5:
                    print(f"   👀 {ticker}: {vol_ratio:.1f}x volume ({change_pct:+.1f}%)")
                
            except Exception as e:
                continue
        
        if not alerts:
            print("   No significant volume spikes")
        
        return alerts
    
    def check_intraday_momentum(self) -> list:
        """
        Check for intraday momentum moves
        3%+ move from open = momentum ignition
        """
        alerts = []
        
        print(f"\n🔍 Scanning intraday momentum... ({datetime.now().strftime('%H:%M:%S')})")
        
        for ticker in self.all_targets:
            try:
                stock = yf.Ticker(ticker)
                
                # Get intraday data
                hist = stock.history(period='1d', interval='5m')
                
                if len(hist) < 3:
                    continue
                
                open_price = hist['Open'].iloc[0]
                current = hist['Close'].iloc[-1]
                high = hist['High'].max()
                
                move_from_open = ((current - open_price) / open_price) * 100
                high_from_open = ((high - open_price) / open_price) * 100
                
                # Check if making new intraday high
                is_at_high = current >= high * 0.99
                
                if move_from_open >= self.INTRADAY_MOVE_THRESHOLD:
                    alert_data = {
                        'Open': f'${open_price:.2f}',
                        'Current': f'${current:.2f}',
                        'Move': f'+{move_from_open:.1f}% from open',
                        'Intraday High': f'${high:.2f} (+{high_from_open:.1f}%)',
                        'At High': '✅ YES' if is_at_high else 'No'
                    }
                    
                    self.print_alert(ticker, 'INTRADAY MOMENTUM', alert_data)
                    alerts.append({
                        'ticker': ticker,
                        'type': 'momentum',
                        'move_pct': move_from_open,
                        'at_high': is_at_high
                    })
                
            except Exception as e:
                continue
        
        if not alerts:
            print("   No significant intraday moves")
        
        return alerts
    
    def check_breakouts(self) -> list:
        """
        Check for breakouts above recent resistance
        Breaking above 5-day high = potential runner
        """
        alerts = []
        
        print(f"\n🔍 Scanning for breakouts... ({datetime.now().strftime('%H:%M:%S')})")
        
        for ticker in self.all_targets:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='10d')
                
                if len(hist) < 6:
                    continue
                
                current = hist['Close'].iloc[-1]
                high_5d = hist['High'].iloc[-6:-1].max()  # 5-day high excluding today
                
                # Breaking out above 5-day high
                if current > high_5d * 1.01:  # 1% above to confirm breakout
                    breakout_pct = ((current - high_5d) / high_5d) * 100
                    
                    # Check volume
                    avg_vol = hist['Volume'].tail(20).mean()
                    today_vol = hist['Volume'].iloc[-1]
                    vol_ratio = today_vol / avg_vol if avg_vol > 0 else 1
                    
                    alert_data = {
                        'Price': f'${current:.2f}',
                        '5-Day High': f'${high_5d:.2f}',
                        'Breakout': f'+{breakout_pct:.1f}% above resistance',
                        'Volume': f'{vol_ratio:.1f}x average'
                    }
                    
                    self.print_alert(ticker, 'BREAKOUT', alert_data)
                    alerts.append({
                        'ticker': ticker,
                        'type': 'breakout',
                        'breakout_pct': breakout_pct,
                        'vol_ratio': vol_ratio
                    })
                
            except Exception as e:
                continue
        
        if not alerts:
            print("   No breakouts detected")
        
        return alerts
    
    def run_full_scan(self) -> dict:
        """Run all scans once"""
        print("\n" + "🐺" * 40)
        print("   R E A L T I M E   H U N T E R")
        print(f"   {datetime.now().strftime('%A %B %d, %Y - %I:%M:%S %p')}")
        print("🐺" * 40)
        
        results = {
            'gaps': self.check_premarket_gaps(),
            'volume': self.check_volume_spikes(),
            'momentum': self.check_intraday_momentum(),
            'breakouts': self.check_breakouts(),
        }
        
        # Summary
        total_alerts = sum(len(v) for v in results.values())
        
        print("\n" + "=" * 60)
        print(f"   SCAN COMPLETE - {total_alerts} ALERTS")
        
        if total_alerts > 0:
            print("\n   🎯 OPPORTUNITIES DETECTED:")
            for alert in self.alerts_today[-total_alerts:]:
                print(f"      • {alert['ticker']}: {alert['type'].upper()}")
        else:
            print("   No immediate opportunities. The wolves wait...")
        
        print("=" * 60)
        
        return results
    
    def run_continuous(self, interval_seconds: int = 60):
        """
        Run continuous monitoring
        Scans every X seconds during market hours
        """
        print("\n" + "🐺" * 40)
        print("   C O N T I N U O U S   H U N T I N G   M O D E")
        print(f"   Scanning every {interval_seconds} seconds")
        print("   Press Ctrl+C to stop")
        print("🐺" * 40)
        
        scan_count = 0
        
        try:
            while True:
                scan_count += 1
                print(f"\n{'='*60}")
                print(f"   SCAN #{scan_count} - {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*60}")
                
                # Run all checks
                self.check_volume_spikes()
                self.check_intraday_momentum()
                self.check_breakouts()
                
                # Only check gaps before market open
                hour = datetime.now().hour
                if hour < 9 or (hour == 9 and datetime.now().minute < 30):
                    self.check_premarket_gaps()
                
                print(f"\n   💤 Sleeping {interval_seconds}s until next scan...")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Hunting stopped by user")
            self._save_session()
    
    def _save_session(self):
        """Save today's alerts to file"""
        if not self.alerts_today:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.data_dir / f'hunt_session_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump({
                'session_end': timestamp,
                'total_alerts': len(self.alerts_today),
                'alerts': self.alerts_today
            }, f, indent=2)
        
        print(f"\n💾 Session saved: {filename}")
        print(f"   Total alerts this session: {len(self.alerts_today)}")


def main():
    hunter = RealtimeHunter()
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == '--premarket':
            hunter.check_premarket_gaps()
        
        elif arg == '--test':
            hunter.run_full_scan()
        
        elif arg == '--continuous' or arg == '-c':
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            hunter.run_continuous(interval)
        
        else:
            print("Usage:")
            print("  python realtime_hunter.py              # Full scan once")
            print("  python realtime_hunter.py --premarket  # Pre-market gaps")
            print("  python realtime_hunter.py --test       # Test scan")
            print("  python realtime_hunter.py -c [secs]    # Continuous (default 60s)")
    else:
        # Default: run full scan
        hunter.run_full_scan()


if __name__ == '__main__':
    main()
