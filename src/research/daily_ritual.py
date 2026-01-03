#!/usr/bin/env python3
"""
🐺 WOLF DEN DAILY RITUAL 🐺

THE MORNING RITUAL - Run this EVERY trading day at 6:00 AM

This script runs ALL your scanners in sequence:
1. Wolf Den Command Center (wounded wolves + sector heat + decisions)
2. Sector Sympathy Scanner (leader moves + laggard opportunities)
3. Position Grid Check (if you have positions)

One command. Full market awareness.

Usage:
    python daily_ritual.py          # Full scan
    python daily_ritual.py quick    # Quick summary only

Author: Brokkr (following Fenrir's doctrine)
Date: January 3, 2026
"""

import sys
from datetime import datetime
from pathlib import Path

# Import our scanners
from wolf_den_command import WolfDenCommand
from sector_sympathy import SectorSympatyTracker
from position_grid import PositionGrid


def print_header():
    """Print the ritual header"""
    print("\n")
    print("🐺" * 50)
    print()
    print("    ██╗    ██╗ ██████╗ ██╗     ███████╗    ██████╗ ███████╗███╗   ██╗")
    print("    ██║    ██║██╔═══██╗██║     ██╔════╝    ██╔══██╗██╔════╝████╗  ██║")
    print("    ██║ █╗ ██║██║   ██║██║     █████╗      ██║  ██║█████╗  ██╔██╗ ██║")
    print("    ██║███╗██║██║   ██║██║     ██╔══╝      ██║  ██║██╔══╝  ██║╚██╗██║")
    print("    ╚███╔███╔╝╚██████╔╝███████╗██║         ██████╔╝███████╗██║ ╚████║")
    print("     ╚══╝╚══╝  ╚═════╝ ╚══════╝╚═╝         ╚═════╝ ╚══════╝╚═╝  ╚═══╝")
    print()
    print("                    D A I L Y   R I T U A L")
    print()
    print(f"                 {datetime.now().strftime('%A, %B %d, %Y')}")
    print(f"                       {datetime.now().strftime('%I:%M %p')}")
    print()
    print("🐺" * 50)


def print_divider(title: str):
    """Print a section divider"""
    print("\n\n")
    print("▓" * 80)
    print(f"▓▓▓  {title}")
    print("▓" * 80)


def run_full_ritual():
    """Run the complete daily ritual"""
    print_header()
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 1: WOLF DEN COMMAND CENTER
    # ═══════════════════════════════════════════════════════════════════
    print_divider("PHASE 1: WOLF DEN COMMAND CENTER")
    
    command = WolfDenCommand()
    results = command.run_full_scan()
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 2: SECTOR SYMPATHY SCANNER
    # ═══════════════════════════════════════════════════════════════════
    print_divider("PHASE 2: SECTOR SYMPATHY OPPORTUNITIES")
    
    sympathy = SectorSympatyTracker()
    sympathy.check_leader_moves()
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 3: POSITION GRID CHECK (if exists)
    # ═══════════════════════════════════════════════════════════════════
    print_divider("PHASE 3: POSITION GRID STATUS")
    
    grid = PositionGrid()
    if grid.positions.get('positions'):
        grid.check_rebalance_signals()
    else:
        print("\n   📊 No position grid initialized")
        print("   To create one: python position_grid.py init <capital>")
        print("\n   Simulation for $1,000:")
        grid.simulate_grid(1000)
    
    # ═══════════════════════════════════════════════════════════════════
    # FINAL SUMMARY
    # ═══════════════════════════════════════════════════════════════════
    print_divider("🎯 TODAY'S ACTION SUMMARY")
    
    # Count decisions
    strong_buys = [d for d in results['decisions'] if 'STRONG BUY' in d['action']]
    buys = [d for d in results['decisions'] if d['action'] == '✅ BUY']
    momentum = [d for d in results['decisions'] if 'MOMENTUM' in d['action']]
    
    print(f"""
    ┌─────────────────────────────────────────────────────────────────┐
    │                     TODAY'S HUNTING GROUNDS                      │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                  │
    │   🔥 STRONG BUY SIGNALS:  {len(strong_buys):<3}                               │
    │   ✅ BUY SIGNALS:         {len(buys):<3}                               │
    │   🚀 MOMENTUM PLAYS:      {len(momentum):<3}                               │
    │                                                                  │
    │   WOUNDED WOLVES:         {len(results['wounded']['wounded']):<3} (in buy zone)              │
    │   VOLUME IGNITIONS:       {len(results['ignitions']):<3}                               │
    │   LAGGARD OPPS:           {len(results['laggards']):<3}                               │
    │                                                                  │
    └─────────────────────────────────────────────────────────────────┘
""")
    
    # Top picks
    if strong_buys:
        print("    🔥 TOP STRONG BUY PICKS:")
        for d in strong_buys[:3]:
            print(f"       • {d['ticker']:6} @ ${d['price']:<8} - {', '.join(d['signals'][:2])}")
    
    if momentum:
        print("\n    🚀 MOMENTUM PLAYS (already running):")
        for d in momentum[:3]:
            print(f"       • {d['ticker']:6} @ ${d['price']:<8}")
    
    print("\n")
    print("🐺" * 50)
    print("                   THE HUNT BEGINS")
    print("🐺" * 50)
    print()


def run_quick_scan():
    """Run a quick summary scan"""
    print("\n🐺 QUICK WOLF DEN SCAN")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-" * 40)
    
    command = WolfDenCommand()
    
    # Just run wounded scan and decisions
    wounded = command.wounded_wolf_scan()
    sector_heat = command.sector_heat_check()
    ignitions = command.momentum_ignition_scan()
    decisions = command.decision_matrix(wounded, sector_heat, ignitions)
    
    # Quick summary
    strong_buys = [d for d in decisions if 'STRONG BUY' in d['action']]
    
    print(f"\n   Wounded Wolves: {len(wounded['wounded'])}")
    print(f"   Volume Ignitions: {len(ignitions)}")
    print(f"   Strong Buy Signals: {len(strong_buys)}")
    
    if strong_buys:
        print("\n   TOP PICKS:")
        for d in strong_buys[:3]:
            print(f"   • {d['ticker']} @ ${d['price']}")
    
    print()


def main():
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'quick':
        run_quick_scan()
    else:
        run_full_ritual()


if __name__ == '__main__':
    main()
