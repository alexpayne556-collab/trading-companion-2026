#!/usr/bin/env python3
"""
🐺 CLUSTER BUY SCANNER - MULTIPLE INSIDERS = CONVICTION
========================================================
Aggregate Form 4 filings to detect cluster buying
3+ insiders buying = they know something

OpenInsider aggregation + our insider data combined

AWOOOO 🐺 LLHR
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
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
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# =============================================================================
# AI FUEL CHAIN
# =============================================================================

AI_FUEL_CHAIN = {
    'NUCLEAR': ['UUUU', 'SMR', 'LEU', 'OKLO', 'CCJ', 'DNN', 'UEC', 'NXE', 'NNE'],
    'UTILITIES': ['NEE', 'VST', 'CEG', 'WMB'],
    'COOLING': ['VRT', 'MOD', 'NVT'],
    'PHOTONICS': ['LITE', 'AAOI', 'COHR', 'GFS'],
    'NETWORKING': ['ANET', 'CRDO', 'FN', 'CIEN'],
    'STORAGE': ['MU', 'WDC', 'STX'],
    'CHIPS': ['AMD', 'MRVL', 'AVGO', 'INTC', 'AMKR'],
    'DC_BUILDERS': ['SMCI', 'EME', 'CLS', 'FIX'],
    'DC_REITS': ['EQIX', 'DLR'],
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'ASTS', 'SIDU', 'BKSY', 'PL'],
    'AI_SOFTWARE': ['PLTR', 'AI', 'SOUN', 'PATH', 'UPST']
}

PRIORITY_TICKERS = ['UUUU', 'SIDU', 'LUNR', 'MU', 'LITE', 'VRT', 'SMR', 'LEU', 'RDW', 'OKLO']

def get_sector_for_ticker(ticker):
    for sector, tickers in AI_FUEL_CHAIN.items():
        if ticker in tickers:
            return sector
    return "OTHER"

# =============================================================================
# CLUSTER DETECTION
# =============================================================================

def detect_clusters(ticker, days=30):
    """Detect cluster buying for a ticker"""
    try:
        stock = yf.Ticker(ticker)
        insider_df = stock.insider_transactions
        
        if insider_df is None or insider_df.empty:
            return None
        
        # Filter for recent purchases
        if 'Start Date' in insider_df.columns:
            insider_df['Start Date'] = pd.to_datetime(insider_df['Start Date'], errors='coerce')
            cutoff = datetime.now() - timedelta(days=days)
            recent = insider_df[insider_df['Start Date'] >= cutoff]
        else:
            recent = insider_df
        
        # Count buyers
        buyers = []
        buy_dates = []
        total_value = 0
        c_suite_buyers = []
        
        for _, row in recent.iterrows():
            txn = str(row.get('Transaction', '')).lower()
            
            if 'purchase' in txn or 'buy' in txn:
                insider = row.get('Insider', 'Unknown')
                value = row.get('Value', 0)
                date = row.get('Start Date')
                title = str(row.get('Text', '')).lower()
                
                buyers.append(insider)
                buy_dates.append(date)
                
                if pd.notna(value):
                    total_value += abs(value)
                
                # Check for C-Suite
                if any(x in title for x in ['ceo', 'cfo', 'coo', 'president', 'chairman']):
                    c_suite_buyers.append(insider)
        
        unique_buyers = list(set(buyers))
        
        if len(unique_buyers) < 2:
            return None
        
        # Cluster classification
        is_cluster = len(unique_buyers) >= 3
        has_c_suite = len(c_suite_buyers) > 0
        
        # Time concentration (all within 7 days = tight cluster)
        if buy_dates:
            valid_dates = [d for d in buy_dates if pd.notna(d)]
            if valid_dates:
                date_range = (max(valid_dates) - min(valid_dates)).days
                tight_cluster = date_range <= 7 and len(unique_buyers) >= 3
            else:
                tight_cluster = False
        else:
            tight_cluster = False
        
        return {
            'ticker': ticker,
            'sector': get_sector_for_ticker(ticker),
            'unique_buyers': len(unique_buyers),
            'total_buys': len(buyers),
            'c_suite_buyers': len(set(c_suite_buyers)),
            'total_value': total_value,
            'is_cluster': is_cluster,
            'tight_cluster': tight_cluster,
            'has_c_suite': has_c_suite,
            'buyer_names': unique_buyers[:5],
            'recent_date': max(buy_dates) if buy_dates else None
        }
        
    except Exception as e:
        return None

def scan_all_clusters(days=30):
    """Scan all AI Fuel Chain for clusters"""
    
    all_tickers = []
    for tickers in AI_FUEL_CHAIN.values():
        all_tickers.extend(tickers)
    
    print("\n" + "="*100)
    print(f"{Colors.CYAN}{Colors.BOLD}🔍 CLUSTER BUY SCANNER - MULTIPLE INSIDERS = CONVICTION 🔍{Colors.END}")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print(f"   Scanning {len(all_tickers)} tickers for cluster buying (last {days} days)")
    print(f"   Cluster = 3+ different insiders buying")
    print("="*100)
    
    results = []
    
    print(f"\n   Scanning", end="", flush=True)
    for i, ticker in enumerate(all_tickers):
        if i % 10 == 0:
            print(".", end="", flush=True)
        
        cluster = detect_clusters(ticker, days)
        if cluster and cluster['unique_buyers'] >= 2:
            results.append(cluster)
    
    print(" ✓ Done!")
    
    # Sort by cluster strength
    results.sort(key=lambda x: (x['is_cluster'], x['tight_cluster'], x['unique_buyers'], x['total_value']), reverse=True)
    
    return results

def display_cluster_report(results):
    """Display cluster buying report"""
    
    # Filter categories
    tier_1_clusters = [r for r in results if r['is_cluster'] and r['tight_cluster']]
    tier_2_clusters = [r for r in results if r['is_cluster'] and not r['tight_cluster']]
    potential_clusters = [r for r in results if not r['is_cluster'] and r['unique_buyers'] >= 2]
    
    # Tier 1: Tight clusters
    if tier_1_clusters:
        print(f"\n{Colors.RED}{Colors.BOLD}{'='*100}")
        print(f"🔥 TIER 1 CLUSTERS - TIGHT TIMING (3+ insiders within 7 days)")
        print(f"{'='*100}{Colors.END}")
        
        for r in tier_1_clusters:
            priority = "⭐" if r['ticker'] in PRIORITY_TICKERS else ""
            c_suite = "👔" if r['has_c_suite'] else ""
            
            val_str = f"${r['total_value']/1e6:.1f}M" if r['total_value'] >= 1e6 else f"${r['total_value']/1e3:.0f}K"
            
            print(f"\n   {Colors.BRIGHT_GREEN}{r['ticker']}{priority}{c_suite} [{r['sector']}]{Colors.END}")
            print(f"      Buyers: {r['unique_buyers']} | Total Buys: {r['total_buys']} | Value: {val_str}")
            print(f"      C-Suite: {r['c_suite_buyers']} | Recent: {str(r['recent_date'])[:10] if r['recent_date'] else 'N/A'}")
            print(f"      {Colors.YELLOW}🚨 HIGH CONVICTION - Multiple insiders buying within days{Colors.END}")
    
    # Tier 2: Regular clusters
    if tier_2_clusters:
        print(f"\n{Colors.BRIGHT_GREEN}{'='*100}")
        print(f"💪 TIER 2 CLUSTERS - EXTENDED BUYING (3+ insiders over weeks)")
        print(f"{'='*100}{Colors.END}")
        
        for r in tier_2_clusters:
            priority = "⭐" if r['ticker'] in PRIORITY_TICKERS else ""
            c_suite = "👔" if r['has_c_suite'] else ""
            
            val_str = f"${r['total_value']/1e6:.1f}M" if r['total_value'] >= 1e6 else f"${r['total_value']/1e3:.0f}K"
            
            print(f"   {r['ticker']}{priority}{c_suite} [{r['sector']:<12}] | Buyers: {r['unique_buyers']} | Buys: {r['total_buys']} | Value: {val_str}")
    
    # Potential clusters
    if potential_clusters:
        print(f"\n{Colors.GREEN}{'='*100}")
        print(f"📈 POTENTIAL CLUSTERS - WATCH (2 insiders buying)")
        print(f"{'='*100}{Colors.END}")
        
        for r in potential_clusters[:10]:
            priority = "⭐" if r['ticker'] in PRIORITY_TICKERS else ""
            print(f"   {r['ticker']}{priority} [{r['sector']:<12}] | Buyers: {r['unique_buyers']} | Buys: {r['total_buys']}")
    
    # Sector breakdown
    print(f"\n{Colors.CYAN}{'='*100}")
    print(f"📊 CLUSTER ACTIVITY BY SECTOR")
    print(f"{'='*100}{Colors.END}")
    
    sector_stats = {}
    for r in results:
        sector = r['sector']
        if sector not in sector_stats:
            sector_stats[sector] = {'count': 0, 'tight': 0, 'total_buyers': 0}
        
        sector_stats[sector]['count'] += 1
        sector_stats[sector]['total_buyers'] += r['unique_buyers']
        if r['tight_cluster']:
            sector_stats[sector]['tight'] += 1
    
    sorted_sectors = sorted(sector_stats.items(), key=lambda x: (x[1]['tight'], x[1]['total_buyers']), reverse=True)
    
    print(f"\n   {'SECTOR':<15} | {'STOCKS':>7} | {'TIGHT CLUSTERS':>16} | {'TOTAL BUYERS':>13}")
    print(f"   {'─'*15}─┼─{'─'*7}─┼─{'─'*16}─┼─{'─'*13}")
    
    for sector, stats in sorted_sectors:
        heat = "🔥" if stats['tight'] > 0 else "📈" if stats['count'] >= 3 else ""
        print(f"   {sector:<15} | {stats['count']:>7} | {stats['tight']:>16} | {stats['total_buyers']:>13} {heat}")
    
    # Priority tickers
    priority_clusters = [r for r in results if r['ticker'] in PRIORITY_TICKERS]
    
    if priority_clusters:
        print(f"\n{Colors.YELLOW}{'='*100}")
        print(f"⭐ PRIORITY TICKER CLUSTERS")
        print(f"{'='*100}{Colors.END}")
        
        for r in priority_clusters:
            c_suite = "👔 C-SUITE" if r['has_c_suite'] else ""
            tight = "🔥 TIGHT" if r['tight_cluster'] else ""
            
            print(f"\n   {Colors.BOLD}{r['ticker']}{Colors.END} [{r['sector']}] {tight} {c_suite}")
            print(f"      {r['unique_buyers']} insiders | {r['total_buys']} total buys")
            print(f"      Buyers: {', '.join(r['buyer_names'][:3])}")
    
    # Wolf's read
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*100}")
    print(f"🐺 WOLF'S CLUSTER READ")
    print(f"{'='*100}{Colors.END}")
    
    if tier_1_clusters:
        print(f"\n   🚨 {len(tier_1_clusters)} TIGHT CLUSTERS DETECTED:")
        for c in tier_1_clusters[:3]:
            print(f"      → {c['ticker']}: {c['unique_buyers']} insiders buying within days")
        print(f"\n   Tight clusters = coordinated buying = they know something")
    
    if tier_2_clusters:
        print(f"\n   💪 {len(tier_2_clusters)} EXTENDED CLUSTERS:")
        for c in tier_2_clusters[:3]:
            print(f"      → {c['ticker']}: {c['unique_buyers']} insiders over weeks")
    
    print(f"\n   🎯 STRATEGY:")
    print(f"      • Tight clusters (within 7 days) = HIGHEST conviction")
    print(f"      • 3+ buyers > 2 buyers > 1 buyer")
    print(f"      • C-Suite buying = insider confidence")
    print(f"      • Insiders buy weeks/months before catalysts")

# =============================================================================
# MAIN
# =============================================================================

def main():
    import sys
    
    days = 30
    if len(sys.argv) > 1:
        days = int(sys.argv[1])
    
    results = scan_all_clusters(days)
    display_cluster_report(results)
    
    print(f"\n{'='*100}")
    print(f"{Colors.CYAN}{Colors.BOLD}🐺 AWOOOO! FOLLOW THE SMART MONEY! LLHR! 🐺{Colors.END}")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    main()
