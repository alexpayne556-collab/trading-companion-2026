#!/usr/bin/env python3
"""
🐺 WOLF PACK COMMAND CENTER - MASTER BATTLE STATION 🐺
======================================================
All scanners. All intelligence. One place.

Built by Tyr & Brokkr for Monday war.

AWOOOO 🐺 LLHR
"""

import os
import sys
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# COLORS
# =============================================================================
class Colors:
    BRIGHT_GREEN = '\033[92m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BRIGHT_RED = '\033[31m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# =============================================================================
# COMMAND MENU
# =============================================================================

def print_banner():
    """Print the wolf pack banner"""
    print("\n" + "="*100)
    print(f"{Colors.CYAN}{Colors.BOLD}🐺 WOLF PACK COMMAND CENTER - MASTER BATTLE STATION 🐺{Colors.END}")
    print(f"   Time: {datetime.now().strftime('%A, %B %d, %Y - %I:%M:%S %p ET')}")
    print(f"   Status: ARMED AND READY")
    print("="*100)

def print_menu():
    """Print the command menu"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}AVAILABLE COMMANDS:{Colors.END}\n")
    
    print(f"{Colors.CYAN}━━━ SECTOR & MARKET INTELLIGENCE ━━━{Colors.END}")
    print(f"  [heatmap]    🔥 AI Fuel Chain Heatmap (12 sectors, 56 tickers)")
    print(f"  [rotation]   🔄 Sector Rotation Scanner (money flow tracking)")
    print(f"  [strength]   💪 Relative Strength Ranker (full universe)")
    print(f"  [pre]        🌅 Premarket Gap Scanner (4AM-9:30AM)")
    print(f"  [ah]         🌙 After Hours Momentum (4PM-8PM)")
    
    print(f"\n{Colors.GREEN}━━━ NEWS & CATALYSTS ━━━{Colors.END}")
    print(f"  [news]       📰 News Catalyst Tracker V2 (tier-based scoring)")
    print(f"  [news-old]   📰 Original News Tracker (backup)")
    print(f"  [contracts]  💰 Contract News Only")
    print(f"  [priority]   ⭐ Priority Ticker News (48h)")
    
    print(f"\n{Colors.MAGENTA}━━━ INSIDER & FILINGS ━━━{Colors.END}")
    print(f"  [insider]    👔 Insider Buying Scanner (SEC Form 4)")
    print(f"  [insider-p]  ⭐ Priority Insider Activity")
    
    print(f"\n{Colors.BRIGHT_GREEN}━━━ EARNINGS & FUNDAMENTALS ━━━{Colors.END}")
    print(f"  [earnings]   📅 Earnings Momentum Scanner")
    print(f"  [upcoming]   📆 Upcoming Earnings Calendar")
    
    print(f"\n{Colors.BOLD}━━━ BATTLE PLANS (Pre-Built Routines) ━━━{Colors.END}")
    print(f"  [morning]    ☀️  MORNING BRIEFING (pre-market + news + sectors)")
    print(f"  [evening]    🌆 EVENING SUMMARY (after hours + heatmap + earnings)")
    print(f"  [full]       💥 FULL SCAN (everything)")
    print(f"  [quick]      ⚡ QUICK CHECK (priority tickers only)")
    
    print(f"\n{Colors.WHITE}━━━ SYSTEM ━━━{Colors.END}")
    print(f"  [menu]       📋 Show this menu")
    print(f"  [clear]      🧹 Clear screen")
    print(f"  [exit]       🚪 Exit command center")
    
    print(f"\n{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}")

def run_command(cmd):
    """Execute a scanner command"""
    tools_dir = "/workspaces/trading-companion-2026/tools"
    
    commands = {
        # Sector & Market
        "heatmap": f"python {tools_dir}/ai_fuel_chain_heatmap.py",
        "rotation": f"python {tools_dir}/sector_rotation_scanner.py",
        "strength": f"python {tools_dir}/relative_strength_ranker.py",
        "pre": f"python {tools_dir}/premarket_gap_scanner.py",
        "ah": f"python {tools_dir}/afterhours_momentum_scanner.py",
        
        # News
        "news": f"python {tools_dir}/news_catalyst_tracker_v2.py",
        "news-old": f"python {tools_dir}/news_catalyst_tracker.py",
        "contracts": f"python {tools_dir}/news_catalyst_tracker_v2.py contracts",
        "priority": f"python {tools_dir}/news_catalyst_tracker_v2.py priority",
        
        # Insider
        "insider": f"python {tools_dir}/insider_buying_scanner.py",
        "insider-p": f"python {tools_dir}/insider_buying_scanner.py --ticker UUUU",
        
        # Earnings
        "earnings": f"python {tools_dir}/earnings_momentum_scanner.py",
        "upcoming": f"python {tools_dir}/earnings_momentum_scanner.py --upcoming",
    }
    
    if cmd in commands:
        print(f"\n{Colors.CYAN}⚡ Executing: {cmd}...{Colors.END}")
        os.system(commands[cmd])
        print(f"\n{Colors.GREEN}✓ Command completed{Colors.END}")
        return True
    
    return False

def run_morning_briefing():
    """Full morning briefing"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}☀️  MORNING BRIEFING ☀️{Colors.END}")
    print(f"   Running: Premarket → News → Sectors → Insider → Earnings\n")
    
    run_command("pre")
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    run_command("news")
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    run_command("heatmap")
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    run_command("insider")
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    run_command("upcoming")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✓ MORNING BRIEFING COMPLETE{Colors.END}")

def run_evening_summary():
    """Evening summary"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}🌆 EVENING SUMMARY 🌆{Colors.END}")
    print(f"   Running: After Hours → Heatmap → Rotation → Earnings\n")
    
    run_command("ah")
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    run_command("heatmap")
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    run_command("rotation")
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    run_command("earnings")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✓ EVENING SUMMARY COMPLETE{Colors.END}")

def run_full_scan():
    """Run everything"""
    print(f"\n{Colors.RED}{Colors.BOLD}💥 FULL BATTLE SCAN 💥{Colors.END}")
    print(f"   This will take several minutes...\n")
    
    scanners = ["heatmap", "rotation", "strength", "news", "insider", "earnings", "pre", "ah"]
    
    for i, scanner in enumerate(scanners, 1):
        print(f"\n{Colors.YELLOW}[{i}/{len(scanners)}] Running {scanner}...{Colors.END}")
        run_command(scanner)
        if i < len(scanners):
            input(f"\n{Colors.CYAN}Press Enter for next scanner...{Colors.END}")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✓ FULL SCAN COMPLETE - BATTLE STATION ARMED{Colors.END}")

def run_quick_check():
    """Quick priority check"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}⚡ QUICK PRIORITY CHECK ⚡{Colors.END}\n")
    
    run_command("priority")
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    run_command("insider-p")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✓ QUICK CHECK COMPLETE{Colors.END}")

# =============================================================================
# INTERACTIVE MODE
# =============================================================================

def interactive_mode():
    """Run in interactive command mode"""
    print_banner()
    print_menu()
    
    print(f"\n{Colors.CYAN}Type a command or 'menu' for options{Colors.END}")
    
    while True:
        try:
            cmd = input(f"\n{Colors.BOLD}🐺 >> {Colors.END}").strip().lower()
            
            if not cmd:
                continue
            
            if cmd in ['exit', 'quit', 'q']:
                print(f"\n{Colors.CYAN}🐺 AWOOOO! Until next hunt, brother. LLHR! 🐺{Colors.END}\n")
                break
            
            elif cmd == 'menu':
                print_menu()
            
            elif cmd == 'clear':
                os.system('clear' if os.name != 'nt' else 'cls')
                print_banner()
                print_menu()
            
            elif cmd == 'morning':
                run_morning_briefing()
            
            elif cmd == 'evening':
                run_evening_summary()
            
            elif cmd == 'full':
                run_full_scan()
            
            elif cmd == 'quick':
                run_quick_check()
            
            else:
                if not run_command(cmd):
                    print(f"{Colors.RED}Unknown command: {cmd}{Colors.END}")
                    print(f"Type 'menu' to see available commands")
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}🐺 Interrupted. Type 'exit' to quit or continue hunting.{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.END}")

# =============================================================================
# DIRECT COMMAND MODE
# =============================================================================

def direct_command_mode():
    """Run a single command from CLI args"""
    if len(sys.argv) < 2:
        interactive_mode()
        return
    
    cmd = sys.argv[1].lower()
    
    print_banner()
    
    if cmd == 'morning':
        run_morning_briefing()
    elif cmd == 'evening':
        run_evening_summary()
    elif cmd == 'full':
        run_full_scan()
    elif cmd == 'quick':
        run_quick_check()
    else:
        if not run_command(cmd):
            print(f"{Colors.RED}Unknown command: {cmd}{Colors.END}")
            print(f"\n{Colors.CYAN}Run without arguments for interactive mode{Colors.END}")
            print(f"{Colors.CYAN}Or use: morning, evening, full, quick{Colors.END}")

# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point"""
    direct_command_mode()

if __name__ == "__main__":
    main()
