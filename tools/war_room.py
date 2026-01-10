#!/usr/bin/env python3
"""
🐺 WOLF PACK WAR ROOM - PREEMPTIVE STRIKE COMMAND CENTER
========================================================

The ULTIMATE dashboard that integrates ALL our tools.
This is how we stay AHEAD of smart money.

USAGE:
    python3 war_room.py              # Full war room scan
    python3 war_room.py --quick      # Quick 2-minute scan
    python3 war_room.py --ticker LUNR  # Deep dive on one ticker
    python3 war_room.py --hunt       # Find new opportunities

TOOLS INTEGRATED:
    ✓ whisper_scanner.py    - Detect setups before the move
    ✓ dip_predictor.py      - ML prediction for 10 AM dips
    ✓ sector_discovery.py   - Find laggards in hot sectors
    ✓ sector_hunter.py      - Find tickers for any sector
    ✓ catalyst_finder.py    - Track upcoming events
    ✓ squeeze_hunter.py     - Short squeeze detection
    ✓ max_pain_calculator.py - Options max pain
    ✓ laggard_hunter.py     - Find stocks that haven't run
    ✓ position_sizer.py     - Risk management
    ✓ options_flow_scanner.py - Smart money flow

THE PACK'S EDGE:
    We see the SETUP before the MOVE.
    We position EARLY at DISCOUNTED rates.
    We let smart money do the heavy lifting.

🐺 AWOOOO!
"""

import argparse
import subprocess
import sys
from datetime import datetime
import os

# Change to tools directory
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))

# Our core watchlist
WATCHLIST = [
    # Quantum + Photonics
    'QUBT', 'IONQ', 'QBTS', 'RGTI',
    # Space
    'RDW', 'RKLB', 'LUNR', 'SPCE', 'MNTS',
    # Nuclear
    'UUUU', 'SMR', 'OKLO', 'NNE', 'LEU',
    # Rare Earth
    'USAR', 'MP',
    # Photonics
    'LITE', 'AAOI', 'GFS', 'COHR',
    # Drones
    'AVAV', 'JOBY',
    # Our positions
    'AISP',
]


def run_tool(script: str, args: list = None, capture: bool = False):
    """Run a tool and optionally capture output"""
    cmd = ['python3', os.path.join(TOOLS_DIR, script)]
    if args:
        cmd.extend(args)
    
    if capture:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    else:
        subprocess.run(cmd)
        return None


def print_header(text: str, char: str = '='):
    """Print a formatted header"""
    print(f"\n{char*80}")
    print(f"🐺 {text}")
    print(f"{char*80}")


def war_room_full():
    """Full war room scan - comprehensive analysis"""
    print_header("WOLF PACK WAR ROOM - PREEMPTIVE STRIKE CENTER")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: FULL SCAN")
    
    # 1. WHISPER SCAN - What setups are forming?
    print_header("PHASE 1: WHISPER DETECTION", '-')
    print("Looking for setups before the move...\n")
    run_tool('whisper_scanner.py', ['--watchlist'])
    
    # 2. CATALYST CHECK - What's happening this week?
    print_header("PHASE 2: CATALYST CALENDAR", '-')
    print("What events are coming...\n")
    run_tool('catalyst_finder.py', ['--plan'])
    
    # 3. SECTOR COMPARISON - Where's the money flowing?
    print_header("PHASE 3: SECTOR HEAT MAP", '-')
    print("Finding hot sectors with laggards...\n")
    run_tool('sector_discovery.py', ['--compare', 'photonics', 'quantum', 'space', 'nuclear', 'rare_earth'])
    
    # 4. ML DIP PREDICTIONS - What's dipping tomorrow?
    print_header("PHASE 4: ML DIP PREDICTIONS", '-')
    print("Finding best 10 AM dip opportunities...\n")
    run_tool('dip_predictor.py', ['--find-patterns'])
    
    # 5. SQUEEZE SETUPS - What could explode?
    print_header("PHASE 5: SQUEEZE DETECTION", '-')
    print("Looking for short squeeze setups...\n")
    run_tool('squeeze_hunter.py')
    
    # 6. FINAL SUMMARY
    print_header("PHASE 6: BATTLE PLAN SUMMARY")
    print("""
🎯 DECISION TIME:

Based on all scans, ask yourself:

1. WHISPERS: What ticker has the highest whisper score?
   → Someone is accumulating. Follow the smart money.

2. CATALYST: What event is happening THIS WEEK?
   → Position BEFORE the news, not after.

3. LAGGARD: What hasn't run while its sector is hot?
   → Laggards catch up. Leaders exhaust.

4. ML DIP: What has 80%+ dip probability tomorrow?
   → Position today, add on the dip.

5. SQUEEZE: What has high short + volume?
   → Fuel for the fire.

🐺 THE PACK'S EDGE:
   We see the setup BEFORE the move.
   We position EARLY at DISCOUNTED rates.
   We let smart money do the heavy lifting.

AWOOOO! 🐺
""")


def war_room_quick():
    """Quick 2-minute scan - essentials only"""
    print_header("WOLF PACK WAR ROOM - QUICK SCAN")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: QUICK (2 minutes)")
    
    # 1. Whisper scan
    print_header("WHISPERS (What's being set up?)", '-')
    run_tool('whisper_scanner.py', ['--watchlist'])
    
    # 2. Catalysts this week
    print_header("CATALYSTS THIS WEEK", '-')
    run_tool('catalyst_finder.py', ['--week'])
    
    # 3. Top ML picks
    print_header("ML TOP PICKS", '-')
    run_tool('dip_predictor.py', ['--find-patterns'])


def war_room_ticker(ticker: str):
    """Deep dive on a single ticker"""
    print_header(f"DEEP DIVE: {ticker.upper()}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Whisper analysis
    print_header("WHISPER ANALYSIS", '-')
    run_tool('whisper_scanner.py', ['--ticker', ticker])
    
    # 2. ML dip prediction
    print_header("ML DIP PREDICTION", '-')
    run_tool('dip_predictor.py', ['--ticker', ticker])
    
    # 3. Max pain
    print_header("OPTIONS MAX PAIN", '-')
    run_tool('max_pain_calculator.py', ['--ticker', ticker])
    
    # 4. Catalyst check
    print_header("CATALYST CHECK", '-')
    run_tool('catalyst_finder.py', ['--ticker', ticker])
    
    # 5. Position sizing
    print_header("POSITION SIZING", '-')
    run_tool('position_sizer.py', ['--ticker', ticker])


def war_room_hunt():
    """Hunt for new opportunities"""
    print_header("WOLF PACK HUNT - FINDING NEW PREY")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Cross-sector laggards
    print_header("CROSS-SECTOR LAGGARDS", '-')
    run_tool('sector_hunter.py', ['--laggards'])
    
    # 2. Hot sectors
    print_header("HOT SECTORS TO EXPLORE", '-')
    run_tool('sector_hunter.py', ['--explore'])
    
    # 3. Squeeze candidates
    print_header("SQUEEZE CANDIDATES", '-')
    run_tool('squeeze_hunter.py')


def show_arsenal():
    """Show all available tools"""
    print_header("WOLF PACK ARSENAL - ALL TOOLS")
    print("""
🔥 CORE SCANNERS (Run these daily):
────────────────────────────────────────
whisper_scanner.py --watchlist     Detect setups before the move
dip_predictor.py --find-patterns   ML prediction for tomorrow's dips
sector_discovery.py --compare      Find laggards in hot sectors
catalyst_finder.py --plan          See this week's catalysts
squeeze_hunter.py                  Find short squeeze setups

📊 DEEP DIVE TOOLS:
────────────────────────────────────────
whisper_scanner.py --ticker X      Full whisper analysis
dip_predictor.py --ticker X        ML dip prediction
max_pain_calculator.py --ticker X  Options max pain
position_sizer.py --ticker X       Risk management

🔍 DISCOVERY TOOLS:
────────────────────────────────────────
sector_hunter.py "photonics"       Find all tickers in a sector
sector_hunter.py --laggards        Find laggards across ALL sectors
sector_hunter.py --explore         See all available sectors

📅 TIMING TOOLS:
────────────────────────────────────────
catalyst_finder.py --week          This week's catalysts
catalyst_finder.py --ticker X      Catalysts for specific ticker

🎯 POSITION MANAGEMENT:
────────────────────────────────────────
position_sizer.py --ticker X       Calculate position size
position_sizer.py --portfolio      View current positions

⚡ QUICK COMMANDS:
────────────────────────────────────────
war_room.py                        Full war room scan
war_room.py --quick                Quick 2-min scan
war_room.py --ticker LUNR          Deep dive on ticker
war_room.py --hunt                 Hunt for new opportunities
war_room.py --arsenal              Show this menu

🐺 SHELL SCRIPTS:
────────────────────────────────────────
./wolf_morning_routine.sh          6:30 AM full routine
./morning_hunt.sh                  Quick morning scan
""")


def main():
    parser = argparse.ArgumentParser(
        description='🐺 Wolf Pack War Room - Preemptive Strike Command Center',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 war_room.py              Full war room scan
  python3 war_room.py --quick      Quick 2-minute scan
  python3 war_room.py --ticker LUNR  Deep dive on ticker
  python3 war_room.py --hunt       Hunt for new opportunities
  python3 war_room.py --arsenal    Show all tools
        """
    )
    parser.add_argument('--quick', '-q', action='store_true', help='Quick 2-minute scan')
    parser.add_argument('--ticker', '-t', help='Deep dive on specific ticker')
    parser.add_argument('--hunt', action='store_true', help='Hunt for new opportunities')
    parser.add_argument('--arsenal', '-a', action='store_true', help='Show all available tools')
    
    args = parser.parse_args()
    
    if args.arsenal:
        show_arsenal()
    elif args.ticker:
        war_room_ticker(args.ticker)
    elif args.hunt:
        war_room_hunt()
    elif args.quick:
        war_room_quick()
    else:
        war_room_full()


if __name__ == '__main__':
    main()
