#!/usr/bin/env python3
"""
Trading Intelligence Daemon - Runs continuously, remembers everything

This replaces manual scanning. Let it run 24/7.
"""

import time
import sys
import os
from datetime import datetime
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'webapp'))

def is_market_hours():
    """Check if market is open (9:30 AM - 4 PM ET, Mon-Fri)"""
    now = datetime.now()
    
    # Skip weekends
    if now.weekday() >= 5:
        return False
    
    # Market hours: 9:30 AM - 4:00 PM ET
    # (Simplified - not checking holidays)
    hour = now.hour
    minute = now.minute
    
    if hour < 9 or (hour == 9 and minute < 30):
        return False
    if hour >= 16:
        return False
    
    return True


def run_scanner():
    """Run scanner, which now logs to database"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running scanner...")
    try:
        result = subprocess.run(
            ['python', 'scanner.py', 'scan'],
            cwd='/workspaces/trading-companion-2026',
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Count movers from output
        movers = result.stdout.count('MOVERS DETECTED')
        if movers:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'MOVERS DETECTED' in line:
                    print(f"   ✅ {line.strip()}")
        else:
            print(f"   📊 No significant moves")
            
    except Exception as e:
        print(f"   ❌ Scanner error: {e}")


def run_volume_detector():
    """Check for volume spikes"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking volume spikes...")
    try:
        result = subprocess.run(
            ['python', 'volume_detector.py', '0.3'],
            cwd='/workspaces/trading-companion-2026',
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Parse results
        if 'volume spikes detected' in result.stdout:
            for line in result.stdout.split('\n'):
                if 'SUMMARY:' in line:
                    print(f"   {line.strip()}")
                    
    except Exception as e:
        print(f"   ❌ Volume detector error: {e}")


def run_news_scraper():
    """Scrape news for catalysts"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scraping news...")
    try:
        result = subprocess.run(
            ['python', 'hunt.py', 'scan'],
            cwd='/workspaces/trading-companion-2026',
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Parse results
        if 'Total articles:' in result.stdout:
            for line in result.stdout.split('\n'):
                if 'Total articles:' in line or 'Hot catalysts:' in line:
                    print(f"   {line.strip()}")
                    
    except Exception as e:
        print(f"   ❌ News scraper error: {e}")


def main():
    """Main daemon loop"""
    print("\n" + "="*80)
    print("🐺 TRADING INTELLIGENCE DAEMON")
    print("="*80)
    print(f"Started: {datetime.now()}")
    print("Running continuously. Press Ctrl+C to stop.\n")
    print("Operations:")
    print("  - Scanner: Every 5 minutes during market hours")
    print("  - Volume detector: Every 10 minutes")
    print("  - News scraper: Every 30 minutes")
    print("  - All data logged to intelligence.db")
    print("="*80 + "\n")
    
    scanner_counter = 0
    news_counter = 0
    
    try:
        while True:
            scanner_counter += 1
            news_counter += 1
            
            # Always run scanner (even after hours for AH trading)
            run_scanner()
            
            # Volume detector every 2 scanner runs
            if scanner_counter % 2 == 0:
                run_volume_detector()
            
            # News every 6 scanner runs (30 minutes)
            if news_counter % 6 == 0:
                run_news_scraper()
                news_counter = 0
            
            # Adjust sleep based on market hours
            if is_market_hours():
                sleep_time = 300  # 5 minutes during market
                print(f"\n💤 Next scan in 5 minutes...\n")
            else:
                sleep_time = 900  # 15 minutes after hours
                print(f"\n💤 After hours - next scan in 15 minutes...\n")
            
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("🐺 Daemon stopped")
        print(f"Stopped: {datetime.now()}")
        print("="*80 + "\n")


if __name__ == '__main__':
    main()
