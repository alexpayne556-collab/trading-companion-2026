#!/usr/bin/env python3
"""
wolf_master.py - The Unified Wolf Pack Command Center

Runs all scanners, compiles intelligence, outputs battle-ready report.
One command to rule them all.

Usage:
    python wolf_master.py scan          # Full scan - all tools
    python wolf_master.py quick         # Quick scan - pressure + gamma only
    python wolf_master.py monday        # Monday prep - everything for Monday
    python wolf_master.py status        # Current positions + watchlist
    python wolf_master.py premarket     # Pre-market check (run 4-9 AM)

AWOOOO 🐺
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Our primary targets
WATCHLIST = ["QBTS", "RR", "SOUN", "OKLO", "RKLB", "QUBT", "IONQ", "RGTI", "LEU", "SMR"]

# CES 2026 plays
CES_PLAYS = ["RR", "QBTS", "QUBT", "SOUN"]

# Tools and their commands
TOOLS = {
    "pressure": {"cmd": "python wolf_pressure.py scan", "desc": "Pressure rankings"},
    "gamma": {"cmd": "python wolf_gamma.py map {symbol}", "desc": "Gamma squeeze analysis"},
    "monday": {"cmd": "python wolf_monday.py plan", "desc": "Monday battle plan"},
    "sunday": {"cmd": "python wolf_sunday.py plan", "desc": "Sunday prep"},
    "alpha": {"cmd": "python wolf_alpha.py scan", "desc": "Unified alpha signals"},
    "waves": {"cmd": "python wolf_waves.py {symbol}", "desc": "Wave phase detection"},
    "stalker": {"cmd": "python wolf_stalker.py scan", "desc": "Accumulation detection"},
    "spring": {"cmd": "python wolf_spring.py scan", "desc": "Coiled springs"},
    "journal": {"cmd": "python wolf_journal.py review", "desc": "Trade journal"},
    "stats": {"cmd": "python wolf_journal.py stats", "desc": "Win rate stats"},
}


# ═══════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def run_tool(cmd: str, show_output: bool = True) -> str:
    """Run a tool and return output"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=120,
            cwd=Path(__file__).parent
        )
        output = result.stdout + result.stderr
        if show_output:
            print(output)
        return output
    except subprocess.TimeoutExpired:
        print(f"⏱️  Tool timed out: {cmd}")
        return ""
    except Exception as e:
        print(f"❌ Error running {cmd}: {e}")
        return ""


def print_header(title: str):
    """Print a section header"""
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  🐺 {title:<60} ║
╚══════════════════════════════════════════════════════════════════╝
""")


def print_separator():
    """Print a separator line"""
    print("─" * 70)


# ═══════════════════════════════════════════════════════════════════════════
# SCAN MODES
# ═══════════════════════════════════════════════════════════════════════════

def full_scan():
    """Run all scanners - comprehensive analysis"""
    print_header("WOLF PACK FULL SCAN")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Watchlist: {', '.join(WATCHLIST)}")
    print_separator()
    
    # 0. WIDE HUNT - Find front-runners across ALL sectors
    print_header("WIDE HUNT - ALL SECTORS")
    run_tool("python wolf_hunt_wide.py scan 2>&1")
    
    # 1. Pressure Rankings
    print_header("PRESSURE RANKINGS (Watchlist)")
    run_tool("python wolf_pressure.py scan 2>&1")
    
    # 2. Monday Plan
    print_header("MONDAY BATTLE PLAN")
    run_tool("python wolf_monday.py plan 2>&1")
    
    # 3. Gamma on top targets
    print_header("GAMMA ANALYSIS - TOP TARGETS")
    for symbol in CES_PLAYS[:3]:
        print(f"\n--- {symbol} ---")
        run_tool(f"python wolf_gamma.py map {symbol} 2>&1")
    
    # 4. Alpha signals
    print_header("ALPHA SIGNALS")
    run_tool("python wolf_alpha.py scan 2>&1")
    
    # 5. Wave phases
    print_header("WAVE PHASES")
    run_tool("python wolf_waves.py scan 2>&1")
    
    # 6. Accumulation
    print_header("ACCUMULATION DETECTION")
    run_tool("python wolf_stalker.py scan 2>&1")
    
    # 7. Coiled springs
    print_header("COILED SPRINGS")
    run_tool("python wolf_spring.py scan 2>&1")
    
    # 8. Journal stats
    print_header("TRADE STATS")
    run_tool("python wolf_journal.py stats 2>&1")
    
    print_header("SCAN COMPLETE")
    print("""
NEXT STEPS:
1. Review pressure rankings for top targets
2. Check gamma scores on #1 and #2 picks
3. Note any red flags (insider selling, dilution risk)
4. Update MONDAY_EXECUTION_PLAN.md if needed
5. Rest. Hunt Monday.

AWOOOO 🐺
""")


def quick_scan():
    """Quick scan - just pressure and gamma on top picks"""
    print_header("WOLF PACK QUICK SCAN")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator()
    
    # 1. Pressure Rankings
    print_header("PRESSURE RANKINGS")
    run_tool("python wolf_pressure.py scan 2>&1")
    
    # 2. Gamma on RR and QBTS
    print_header("GAMMA - RR")
    run_tool("python wolf_gamma.py map RR 2>&1")
    
    print_header("GAMMA - QBTS")
    run_tool("python wolf_gamma.py map QBTS 2>&1")
    
    print_header("QUICK SCAN COMPLETE")


def monday_prep():
    """Full Monday preparation - everything needed for Monday open"""
    print_header("MONDAY BATTLE PREP")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("""
╔══════════════════════════════════════════════════════════════════╗
║  📋 MONDAY PREP CHECKLIST                                         ║
╠══════════════════════════════════════════════════════════════════╣
║  [ ] Review pressure rankings                                    ║
║  [ ] Check gamma on top picks                                    ║
║  [ ] Verify entry/stop/target prices                             ║
║  [ ] Check for overnight SEC filings                             ║
║  [ ] Note any red flags                                          ║
║  [ ] Set exact position sizes                                    ║
╚══════════════════════════════════════════════════════════════════╝
""")
    print_separator()
    
    # 1. Sunday prep
    print_header("SUNDAY ANALYSIS")
    run_tool("python wolf_sunday.py plan 2>&1")
    
    # 2. Monday plan
    print_header("MONDAY BATTLE PLAN")
    run_tool("python wolf_monday.py plan 2>&1")
    
    # 3. Pressure
    print_header("PRESSURE RANKINGS")
    run_tool("python wolf_pressure.py scan 2>&1")
    
    # 4. Gamma on CES plays
    for symbol in CES_PLAYS[:2]:
        print_header(f"GAMMA - {symbol}")
        run_tool(f"python wolf_gamma.py map {symbol} 2>&1")
    
    # 5. Execution plan reminder
    print_header("EXECUTION REMINDERS")
    print("""
╔══════════════════════════════════════════════════════════════════╗
║  🎯 RR (Richtech Robotics)                                        ║
╠══════════════════════════════════════════════════════════════════╣
║  Entry:    $3.35 - $3.50                                         ║
║  Stop:     $3.00 (14% risk)                                      ║
║  Target 1: $4.00 (+14%) - Take 50%                               ║
║  Target 2: $4.50 (+29%) - Trail rest                             ║
║  Position: $650 (185 shares @ $3.50)                             ║
╚══════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════╗
║  🎯 QBTS (D-Wave Quantum)                                         ║
╠══════════════════════════════════════════════════════════════════╣
║  Entry:    $26 - $28                                             ║
║  Stop:     $24 (14% risk)                                        ║
║  Target 1: $32 (+14%) - Take 50%                                 ║
║  Target 2: $38 (+35%) - Trail rest                               ║
║  Position: $650 (23 shares @ $28)                                ║
╚══════════════════════════════════════════════════════════════════╝

⚠️  RED FLAGS - DO NOT ENTER:
• Gap UP >10% pre-market (move already happened)
• 8-K filing mentioning ATM offering
• Jensen keynote ignores quantum/robotics
• Put volume > Call volume

✅ GREEN FLAGS - FULL SIZE:
• Gap flat or slightly down
• Pre-market volume 2x+ normal
• Jensen mentions GR00T/humanoid/quantum
• Call sweeps detected

📅 EXIT EVERYTHING BEFORE JAN 7 DEMOS
""")


def premarket_check():
    """Pre-market check - run 4-9 AM"""
    print_header("PRE-MARKET CHECK")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("""
⚠️  RUN THIS BETWEEN 4 AM - 9:30 AM ET

This checks:
1. Current pressure rankings (may differ from Friday)
2. Gamma levels on top picks
3. Quick wave phase check

NOTE: Pre-market prices not available via yfinance.
Check your broker for actual pre-market gaps.
""")
    print_separator()
    
    # Quick pressure check
    print_header("CURRENT PRESSURE")
    run_tool("python wolf_pressure.py scan 2>&1")
    
    # Gamma check
    print_header("GAMMA - RR")
    run_tool("python wolf_gamma.py map RR 2>&1")
    
    print_header("GAMMA - QBTS")
    run_tool("python wolf_gamma.py map QBTS 2>&1")
    
    print_header("PRE-MARKET COMPLETE")
    print("""
BEFORE 9:30 AM:
1. Check broker for actual pre-market prices
2. If gap >10% UP - DO NOT CHASE
3. If gap flat/down - Prepare entry orders
4. Set stop orders immediately after fill

AWOOOO 🐺
""")


def status_check():
    """Check current status - positions, watchlist, stats"""
    print_header("WOLF PACK STATUS")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator()
    
    # Trade journal
    print_header("TRADE JOURNAL")
    run_tool("python wolf_journal.py review 2>&1")
    
    # Stats
    print_header("PERFORMANCE STATS")
    run_tool("python wolf_journal.py stats 2>&1")
    
    # Current pressure
    print_header("CURRENT WATCHLIST PRESSURE")
    run_tool("python wolf_pressure.py scan 2>&1")
    
    print_header("STATUS COMPLETE")


def show_tools():
    """List all available tools"""
    print_header("WOLF PACK ARSENAL")
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║  MASTER COMMANDS                                                  ║
╠═══════════════════════════════════════════════════════════════════╣
║  python wolf_master.py scan       Full scan - all tools           ║
║  python wolf_master.py quick      Quick scan - pressure + gamma   ║
║  python wolf_master.py monday     Monday prep - battle plan       ║
║  python wolf_master.py premarket  Pre-market check (4-9 AM)       ║
║  python wolf_master.py status     Positions + stats               ║
║  python wolf_master.py tools      List all tools                  ║
╠═══════════════════════════════════════════════════════════════════╣
║  WIDE HUNT (182 tickers across 13 sectors)                        ║
╠═══════════════════════════════════════════════════════════════════╣
║  python wolf_hunt_wide.py scan           Full market scan         ║
║  python wolf_hunt_wide.py sector QUANTUM Scan one sector          ║
║  python wolf_hunt_wide.py sector NUCLEAR Uranium/nuclear          ║
║  python wolf_hunt_wide.py sector SPACE   Space stocks             ║
║  python wolf_hunt_wide.py sector BIOTECH Biotech                  ║
║  python wolf_hunt_wide.py top 20         Top 20 movers            ║
╠═══════════════════════════════════════════════════════════════════╣
║  INDIVIDUAL TOOLS                                                 ║
╠═══════════════════════════════════════════════════════════════════╣
║  python wolf_pressure.py scan     Pressure convergence ranking    ║
║  python wolf_gamma.py map QBTS    Gamma squeeze analysis          ║
║  python wolf_monday.py plan       CES 2026 battle plan            ║
║  python wolf_sunday.py plan       Sunday Monday prep              ║
║  python wolf_alpha.py scan        Unified alpha signals           ║
║  python wolf_waves.py scan        Wave phase detection            ║
║  python wolf_stalker.py scan      Smart money accumulation        ║
║  python wolf_spring.py scan       Coiled spring detector          ║
╠═══════════════════════════════════════════════════════════════════╣
║  JOURNAL                                                          ║
╠═══════════════════════════════════════════════════════════════════╣
║  python wolf_journal.py log RR 3.45 3.00 4.50 "thesis"            ║
║  python wolf_journal.py close RR 4.25 "notes"                     ║
║  python wolf_journal.py review    Review all trades               ║
║  python wolf_journal.py stats     Win rate statistics             ║
║  python wolf_journal.py lesson "Don't chase gaps"                 ║
╠═══════════════════════════════════════════════════════════════════╣
║  DASHBOARD                                                        ║
╠═══════════════════════════════════════════════════════════════════╣
║  streamlit run wolf_den_war_room.py --server.port 8501            ║
╚═══════════════════════════════════════════════════════════════════╝
""")


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="🐺 Wolf Pack Master Command Center",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python wolf_master.py scan        # Full scan - all tools
  python wolf_master.py quick       # Quick pressure + gamma
  python wolf_master.py monday      # Monday battle prep
  python wolf_master.py premarket   # Pre-market check
  python wolf_master.py status      # Journal + stats
  python wolf_master.py tools       # List all tools

AWOOOO 🐺
        """
    )
    
    parser.add_argument(
        "command",
        choices=["scan", "quick", "monday", "premarket", "status", "tools"],
        nargs="?",
        default="tools",
        help="Command to run"
    )
    
    args = parser.parse_args()
    
    if args.command == "scan":
        full_scan()
    elif args.command == "quick":
        quick_scan()
    elif args.command == "monday":
        monday_prep()
    elif args.command == "premarket":
        premarket_check()
    elif args.command == "status":
        status_check()
    elif args.command == "tools":
        show_tools()
    else:
        show_tools()


if __name__ == "__main__":
    main()
