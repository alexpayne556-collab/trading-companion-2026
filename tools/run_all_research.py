#!/usr/bin/env python3
"""
🐺 WOLF PACK RESEARCH - MASTER RUNNER

Execute all 12 research projects systematically.
Run this to discover tradeable edge through rigorous testing.

Usage:
    python tools/run_all_research.py                    # Run all projects
    python tools/run_all_research.py --projects 1 2 4   # Run specific projects
    python tools/run_all_research.py --quick            # Quick mode (90 days)

Built by: BROKKR
Specification by: TYR + FENRIR
"""

import sys
import os
import subprocess
from datetime import datetime

# =============================================================================
# PROJECT REGISTRY
# =============================================================================

PROJECTS = {
    1: {
        'name': 'Leader/Laggard Lag Time',
        'file': 'project_1_leader_laggard.py',
        'description': 'When leader moves, how long until laggards follow?',
        'priority': 1,
        'status': 'READY'
    },
    2: {
        'name': 'Volume Divergence Prediction',
        'file': 'project_2_volume_divergence.py',
        'description': '3x volume + flat price = next day move?',
        'priority': 2,
        'status': 'READY'
    },
    3: {
        'name': 'Gap Behavior Study',
        'file': 'project_3_gap_study.py',
        'description': 'Do gaps fill or continue?',
        'priority': 3,
        'status': 'PENDING'
    },
    4: {
        'name': 'RSI Optimization',
        'file': 'rsi_bounce_validator.py',
        'description': 'What RSI level gives best bounce?',
        'priority': 1,
        'status': 'READY'
    },
    5: {
        'name': 'Catalyst Timing',
        'file': 'project_5_catalyst_timing.py',
        'description': 'When to enter before known events?',
        'priority': 2,
        'status': 'PENDING'
    },
    6: {
        'name': 'Time of Day Study',
        'file': 'project_6_time_of_day.py',
        'description': 'When do small caps make biggest moves?',
        'priority': 3,
        'status': 'PENDING'
    },
    7: {
        'name': 'Overnight Gap Prediction',
        'file': 'project_7_overnight_gap.py',
        'description': 'After-hours activity predicts gap?',
        'priority': 2,
        'status': 'PENDING'
    },
    8: {
        'name': 'Insider Buying Impact',
        'file': 'project_8_insider_buying.py',
        'description': 'Form 4 P-code = outperformance?',
        'priority': 2,
        'status': 'PENDING'
    },
    9: {
        'name': 'Sector Rotation Timing',
        'file': 'project_9_sector_rotation.py',
        'description': 'Nuclear → AI → Space pattern?',
        'priority': 1,
        'status': 'PENDING'
    },
    10: {
        'name': 'Earnings Momentum',
        'file': 'project_10_earnings_momentum.py',
        'description': 'How many days before earnings do runs start?',
        'priority': 2,
        'status': 'PENDING'
    },
    11: {
        'name': 'Short Interest Squeeze',
        'file': 'project_11_short_squeeze.py',
        'description': 'High SI + catalyst = outsized move?',
        'priority': 3,
        'status': 'PENDING'
    },
    12: {
        'name': 'Support/Resistance Accuracy',
        'file': 'project_12_support_resistance.py',
        'description': 'Do our stocks respect S/R?',
        'priority': 3,
        'status': 'PENDING'
    }
}

# =============================================================================
# RUNNER FUNCTIONS
# =============================================================================

def print_header():
    """Print header"""
    print("="*80)
    print("🐺 WOLF PACK RESEARCH - SYSTEMATIC EDGE DISCOVERY")
    print("="*80)
    print(f"\nPhilosophy:")
    print(f"  • Every pattern must be TESTED")
    print(f"  • Every edge must be VERIFIED")
    print(f"  • Every scanner must be EARNED")
    print(f"\nValidation Criteria:")
    print(f"  • Win rate > 60%")
    print(f"  • Sample size > 20")
    print(f"  • Risk/reward > 1.5:1")
    print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

def list_projects():
    """List all available projects"""
    print(f"\n{'='*80}")
    print(f"📋 AVAILABLE RESEARCH PROJECTS")
    print(f"{'='*80}\n")
    
    # Sort by priority
    sorted_projects = sorted(PROJECTS.items(), key=lambda x: x[1]['priority'])
    
    for proj_id, info in sorted_projects:
        status_icon = '✅' if info['status'] == 'READY' else '⏳'
        priority_label = f"P{info['priority']}"
        
        print(f"{status_icon} Project {proj_id:2d} [{priority_label}] - {info['name']}")
        print(f"   {info['description']}")
        print(f"   File: {info['file']}")
        print()

def run_project(proj_id: int, period: str = '180d', verbose: bool = True):
    """
    Run a single research project
    
    Args:
        proj_id: Project ID (1-12)
        period: Data period ('90d', '180d', '1y', etc.)
        verbose: Print full output
    
    Returns:
        True if successful, False otherwise
    """
    if proj_id not in PROJECTS:
        print(f"❌ Invalid project ID: {proj_id}")
        return False
    
    project = PROJECTS[proj_id]
    
    if project['status'] != 'READY':
        print(f"⏳ Project {proj_id} not yet implemented: {project['name']}")
        return False
    
    print(f"\n{'='*80}")
    print(f"🚀 RUNNING PROJECT {proj_id}: {project['name']}")
    print(f"{'='*80}\n")
    
    # Build command
    script_path = os.path.join('tools', project['file'])
    cmd = ['python', script_path, '--period', period]
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=not verbose,
            text=True
        )
        
        if not verbose:
            print(result.stdout)
        
        print(f"\n✅ Project {proj_id} complete\n")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Project {proj_id} failed:")
        if not verbose:
            print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"\n❌ Script not found: {script_path}")
        print(f"   Status: {project['status']}")
        return False

def run_all_projects(period: str = '180d', priority_only: bool = False):
    """
    Run all available projects
    
    Args:
        period: Data period
        priority_only: Only run priority 1 projects
    """
    print_header()
    list_projects()
    
    # Filter projects
    if priority_only:
        project_ids = [pid for pid, info in PROJECTS.items() 
                      if info['priority'] == 1 and info['status'] == 'READY']
        print(f"\n🎯 Running PRIORITY 1 projects only: {project_ids}")
    else:
        project_ids = [pid for pid, info in PROJECTS.items() 
                      if info['status'] == 'READY']
        print(f"\n🎯 Running ALL ready projects: {project_ids}")
    
    # Run projects
    results = {}
    for proj_id in project_ids:
        success = run_project(proj_id, period=period, verbose=True)
        results[proj_id] = success
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 EXECUTION SUMMARY")
    print(f"{'='*80}\n")
    
    successful = sum(1 for s in results.values() if s)
    failed = len(results) - successful
    
    print(f"Total projects: {len(results)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    
    if failed > 0:
        print(f"\nFailed projects:")
        for proj_id, success in results.items():
            if not success:
                print(f"  • Project {proj_id}: {PROJECTS[proj_id]['name']}")
    
    print(f"\n🐺 LLHR. All research complete.")
    print(f"📂 Results saved to: research_results/")

# =============================================================================
# MAIN
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Wolf Pack Research - Master Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/run_all_research.py                    # Run all ready projects
  python tools/run_all_research.py --projects 1 2 4   # Run specific projects
  python tools/run_all_research.py --priority         # Run priority 1 only
  python tools/run_all_research.py --quick            # Quick mode (90 days)
  python tools/run_all_research.py --list             # List all projects
        """
    )
    
    parser.add_argument('--projects', type=int, nargs='+', help='Specific project IDs to run')
    parser.add_argument('--priority', action='store_true', help='Run priority 1 projects only')
    parser.add_argument('--period', default='180d', help='Data period (default: 180d)')
    parser.add_argument('--quick', action='store_true', help='Quick mode (90 days)')
    parser.add_argument('--list', action='store_true', help='List available projects')
    
    args = parser.parse_args()
    
    # Quick mode
    if args.quick:
        args.period = '90d'
    
    # List projects
    if args.list:
        print_header()
        list_projects()
        return
    
    # Run specific projects
    if args.projects:
        print_header()
        results = {}
        for proj_id in args.projects:
            success = run_project(proj_id, period=args.period, verbose=True)
            results[proj_id] = success
        
        # Summary
        print(f"\n{'='*80}")
        print(f"📊 EXECUTION SUMMARY")
        print(f"{'='*80}\n")
        
        for proj_id, success in results.items():
            status = '✅' if success else '❌'
            print(f"{status} Project {proj_id}: {PROJECTS[proj_id]['name']}")
        
        print(f"\n🐺 LLHR. Research complete.")
        return
    
    # Run all or priority only
    run_all_projects(period=args.period, priority_only=args.priority)

if __name__ == '__main__':
    main()
