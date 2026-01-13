#!/usr/bin/env python3
"""
🐺 CPI DAY MORNING WORKFLOW
Run this sequence for maximum edge on CPI release days.

CPI drops 8:30 AM ET.
This script runs the full pre/post analysis.

Usage:
  python cpi_morning.py premarket   # Run at 7:30-8:00 AM
  python cpi_morning.py open        # Run at 9:31 AM
  python cpi_morning.py full        # Run both in sequence
"""

import subprocess
import sys
from datetime import datetime
import json
import os

def run_command(cmd, description):
    """Run a command and capture output"""
    print(f"\n{'='*70}")
    print(f"🐺 {description}")
    print(f"   {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*70}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    
    return result.returncode == 0

def premarket_workflow():
    """
    Run at 7:30-8:00 AM before CPI release.
    Establishes baseline of what's hot BEFORE the news.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    print("\n" + "🌅" * 35)
    print("   PREMARKET WORKFLOW - Pre-CPI Baseline")
    print("🌅" * 35)
    
    # 1. Market discovery baseline
    run_command(
        f"python market_discovery.py > logs/pre_cpi_{timestamp}.txt 2>&1",
        "Running market discovery (baseline)"
    )
    print("   ✅ Saved to logs/pre_cpi_{timestamp}.txt")
    
    # 2. Legs classification
    run_command(
        f"python market_mover_finder.py discover --quiet",
        "Finding movers with legs"
    )
    
    # 3. Check our positions
    run_command(
        "python legs_classifier.py ATON NTLA BEAM",
        "Checking current positions"
    )
    
    # 4. Catalyst scan
    run_command(
        "python catalyst_detector.py scan",
        "Scanning for catalysts"
    )
    
    print("\n" + "=" * 70)
    print("✅ PREMARKET COMPLETE")
    print("   Now wait for CPI at 8:30 AM")
    print("   Run 'python cpi_morning.py open' at 9:31 AM")
    print("=" * 70)

def market_open_workflow():
    """
    Run at 9:31 AM after market opens.
    Catches the reaction to CPI.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    print("\n" + "🔔" * 35)
    print("   MARKET OPEN WORKFLOW - Post-CPI Analysis")
    print("🔔" * 35)
    
    # 1. Full market discovery
    run_command(
        f"python market_discovery.py > logs/post_cpi_{timestamp}.txt 2>&1",
        "Running market discovery (post-CPI)"
    )
    
    # 2. Market mover finder with watchlist
    run_command(
        "python market_mover_finder.py open",
        "Finding movers with legs + generating watchlist"
    )
    
    # 3. Legs classifier on top movers
    run_command(
        "python legs_classifier.py --scan",
        "Classifying legs on discovered movers"
    )
    
    # 4. Catalyst check
    run_command(
        "python catalyst_detector.py scan",
        "Checking for material catalysts"
    )
    
    # 5. Intraday scanner
    run_command(
        "python intraday_scanner.py --scan-once",
        "Running intraday momentum scan"
    )
    
    print("\n" + "=" * 70)
    print("✅ MARKET OPEN ANALYSIS COMPLETE")
    print("   Check watchlist_*.csv for Fidelity ATP import")
    print("   Top opportunities listed above")
    print("=" * 70)

def full_workflow():
    """Run both premarket and open workflows"""
    premarket_workflow()
    
    print("\n" + "⏰" * 35)
    print("   WAITING FOR MARKET OPEN...")
    print("   CPI at 8:30 AM | Market at 9:30 AM")
    print("   Will continue at 9:31 AM")
    print("⏰" * 35)
    
    # In real use, you'd schedule this
    # For now, just run both
    input("\nPress ENTER when market opens to continue...")
    
    market_open_workflow()

def quick_scan():
    """Quick scan for immediate use"""
    print("\n🐺 QUICK SCAN - What's moving NOW?")
    print("=" * 70)
    
    run_command("python market_mover_finder.py discover --top 10", "Top 10 movers")
    run_command("python catalyst_detector.py scan", "Catalyst check")

def main():
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    if len(sys.argv) < 2:
        print("""
🐺 CPI MORNING WORKFLOW
=======================

Commands:
  python cpi_morning.py premarket   # 7:30-8:00 AM - Pre-CPI baseline
  python cpi_morning.py open        # 9:31 AM - Post-CPI analysis
  python cpi_morning.py full        # Both in sequence
  python cpi_morning.py quick       # Quick scan anytime

CPI Schedule:
  8:30 AM ET - CPI Release
  8:30-9:30 - Futures react, premarket moves
  9:30 AM - Market opens
  9:31 AM - Run 'open' workflow

The edge: Know what's moving BEFORE and AFTER.
Compare the two to see CPI impact.
        """)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'premarket':
        premarket_workflow()
    elif cmd == 'open':
        market_open_workflow()
    elif cmd == 'full':
        full_workflow()
    elif cmd == 'quick':
        quick_scan()
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
