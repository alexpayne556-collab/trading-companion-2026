#!/usr/bin/env python3
"""
🐺 CONGRESS TRACKER - FOLLOW THE MONEY
========================================
Track congressional stock trades in AI Fuel Chain sectors

Politicians know what's coming before we do.
When they buy → We pay attention.
When they sell → We watch carefully.

Data source: Capitol Trades website scraping (free, public data)

AWOOOO 🐺 LLHR
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
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
    BLUE = '\033[94m'
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

# Important committees
IMPORTANT_COMMITTEES = [
    'armed services',
    'energy and commerce',
    'science, space, and technology',
    'appropriations',
    'intelligence',
    'homeland security'
]

def get_sector_for_ticker(ticker):
    for sector, tickers in AI_FUEL_CHAIN.items():
        if ticker in tickers:
            return sector
    return "OTHER"

# =============================================================================
# CONGRESS TRADE SCRAPING
# =============================================================================

def scrape_recent_trades(days=30):
    """
    Scrape recent congressional trades
    
    NOTE: This is a MOCK implementation for demonstration.
    In production, you would:
    1. Use Capitol Trades API (if available) OR
    2. Scrape their public website OR
    3. Use House/Senate financial disclosure filings
    
    For now, returns mock data structure for testing.
    """
    
    print(f"\n   {Colors.YELLOW}⚠️ MOCK DATA MODE{Colors.END}")
    print(f"      In production, this would scrape Capitol Trades or House/Senate disclosures")
    print(f"      For now, returning mock trades for demonstration...\n")
    
    # Mock congressional trades
    mock_trades = [
        {
            'date': datetime.now() - timedelta(days=5),
            'politician': 'Rep. Jane Smith',
            'party': 'D',
            'state': 'CA',
            'ticker': 'UUUU',
            'transaction': 'Purchase',
            'amount_min': 15000,
            'amount_max': 50000,
            'committee': 'Energy and Commerce'
        },
        {
            'date': datetime.now() - timedelta(days=12),
            'politician': 'Sen. John Doe',
            'party': 'R',
            'state': 'TX',
            'ticker': 'MU',
            'transaction': 'Purchase',
            'amount_min': 50000,
            'amount_max': 100000,
            'committee': 'Armed Services'
        },
        {
            'date': datetime.now() - timedelta(days=18),
            'politician': 'Rep. Bob Johnson',
            'party': 'R',
            'state': 'FL',
            'ticker': 'SIDU',
            'transaction': 'Purchase',
            'amount_min': 1000,
            'amount_max': 15000,
            'committee': 'Science, Space, and Technology'
        },
        {
            'date': datetime.now() - timedelta(days=25),
            'politician': 'Sen. Mary Williams',
            'party': 'D',
            'state': 'NY',
            'ticker': 'LITE',
            'transaction': 'Purchase',
            'amount_min': 15000,
            'amount_max': 50000,
            'committee': 'Appropriations'
        },
        {
            'date': datetime.now() - timedelta(days=28),
            'politician': 'Rep. Tom Davis',
            'party': 'R',
            'state': 'OH',
            'ticker': 'SMR',
            'transaction': 'Sale',
            'amount_min': 15000,
            'amount_max': 50000,
            'committee': 'Energy and Commerce'
        }
    ]
    
    return mock_trades

def analyze_congress_trades(trades):
    """Analyze congressional trades for patterns"""
    
    results = {}
    
    for trade in trades:
        ticker = trade['ticker']
        
        # Only track AI Fuel Chain tickers
        if ticker not in sum(AI_FUEL_CHAIN.values(), []):
            continue
        
        if ticker not in results:
            results[ticker] = {
                'ticker': ticker,
                'sector': get_sector_for_ticker(ticker),
                'purchases': [],
                'sales': [],
                'total_purchase_min': 0,
                'total_purchase_max': 0,
                'total_sale_min': 0,
                'total_sale_max': 0,
                'unique_buyers': set(),
                'unique_sellers': set(),
                'committee_buyers': set()
            }
        
        politician = trade['politician']
        committee = trade.get('committee', 'Unknown')
        
        if trade['transaction'] == 'Purchase':
            results[ticker]['purchases'].append(trade)
            results[ticker]['total_purchase_min'] += trade['amount_min']
            results[ticker]['total_purchase_max'] += trade['amount_max']
            results[ticker]['unique_buyers'].add(politician)
            
            # Track important committee members
            if any(comm in committee.lower() for comm in IMPORTANT_COMMITTEES):
                results[ticker]['committee_buyers'].add(f"{politician} ({committee})")
        
        else:  # Sale
            results[ticker]['sales'].append(trade)
            results[ticker]['total_sale_min'] += trade['amount_min']
            results[ticker]['total_sale_max'] += trade['amount_max']
            results[ticker]['unique_sellers'].add(politician)
    
    # Convert sets to counts
    for ticker in results:
        results[ticker]['unique_buyer_count'] = len(results[ticker]['unique_buyers'])
        results[ticker]['unique_seller_count'] = len(results[ticker]['unique_sellers'])
        results[ticker]['committee_buyer_count'] = len(results[ticker]['committee_buyers'])
        
        # Calculate signal strength
        buy_signal = results[ticker]['unique_buyer_count'] * 10
        sell_signal = results[ticker]['unique_seller_count'] * -10
        committee_boost = results[ticker]['committee_buyer_count'] * 20
        
        results[ticker]['signal_strength'] = buy_signal + sell_signal + committee_boost
    
    return list(results.values())

def scan_congress_trades(days=30):
    """Scan congressional trades"""
    
    print("\n" + "="*100)
    print(f"{Colors.CYAN}{Colors.BOLD}🏛️ CONGRESS TRACKER - FOLLOW THE MONEY 🏛️{Colors.END}")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print(f"   Tracking congressional trades in AI Fuel Chain sectors")
    print("="*100)
    
    print(f"\n   {Colors.YELLOW}📊 DATA SOURCE:{Colors.END}")
    print(f"      • House/Senate financial disclosures (public record)")
    print(f"      • 45-day filing deadline (trades may be delayed)")
    print(f"      • Amounts reported in ranges ($1K-$15K, $15K-$50K, etc.)")
    print()
    
    # Scrape trades
    trades = scrape_recent_trades(days)
    
    print(f"   Found {len(trades)} trades in last {days} days")
    print(f"   Analyzing for AI Fuel Chain tickers...\n")
    
    # Analyze
    results = analyze_congress_trades(trades)
    
    # Sort by signal strength
    results.sort(key=lambda x: x['signal_strength'], reverse=True)
    
    return results, trades

def display_congress_report(results, all_trades):
    """Display congressional trading report"""
    
    if not results:
        print(f"\n   {Colors.GREEN}No congressional trades in AI Fuel Chain tickers found{Colors.END}")
        return
    
    # Buying activity
    buying_activity = [r for r in results if r['unique_buyer_count'] > 0]
    selling_activity = [r for r in results if r['unique_seller_count'] > 0]
    
    if buying_activity:
        print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*100}")
        print(f"💰 CONGRESSIONAL BUYING ACTIVITY")
        print(f"{'='*100}{Colors.END}")
        
        print(f"\n   {'TICKER':<8} | {'SECTOR':<12} | {'BUYERS':>8} | {'PURCHASES':>10} | {'AMOUNT':>15} | {'SIGNAL':>8}")
        print(f"   {'─'*8}─┼─{'─'*12}─┼─{'─'*8}─┼─{'─'*10}─┼─{'─'*15}─┼─{'─'*8}")
        
        for r in buying_activity:
            priority = "⭐" if r['ticker'] in PRIORITY_TICKERS else ""
            committee = "🏛️" if r['committee_buyer_count'] > 0 else ""
            
            amount_str = f"${r['total_purchase_min']/1000:.0f}K-${r['total_purchase_max']/1000:.0f}K"
            signal_str = f"+{r['signal_strength']}" if r['signal_strength'] > 0 else str(r['signal_strength'])
            
            print(f"   {r['ticker']:<6}{priority:<2} | {r['sector']:<12} | {r['unique_buyer_count']:>8} | {len(r['purchases']):>10} | {amount_str:>15} | {signal_str:>8} {committee}")
        
        # Detailed breakdown
        print(f"\n{Colors.YELLOW}DETAILED PURCHASE BREAKDOWN:{Colors.END}")
        
        for r in buying_activity[:5]:  # Top 5
            print(f"\n   {Colors.BOLD}{r['ticker']}{Colors.END} [{r['sector']}]")
            
            for purchase in r['purchases']:
                party_color = Colors.BLUE if purchase['party'] == 'D' else Colors.RED if purchase['party'] == 'R' else Colors.WHITE
                amount_str = f"${purchase['amount_min']/1000:.0f}K-${purchase['amount_max']/1000:.0f}K"
                days_ago = (datetime.now() - purchase['date']).days
                
                committee_str = f" [{purchase.get('committee', 'Unknown')}]" if purchase.get('committee') else ""
                
                print(f"      • {purchase['politician']} ({purchase['party']}-{purchase['state']}){committee_str}")
                print(f"        {amount_str} | {days_ago} days ago")
            
            if r['committee_buyer_count'] > 0:
                print(f"      {Colors.YELLOW}⚠️ {r['committee_buyer_count']} important committee member(s) buying{Colors.END}")
    
    if selling_activity:
        print(f"\n{Colors.RED}{Colors.BOLD}{'='*100}")
        print(f"⚠️ CONGRESSIONAL SELLING ACTIVITY")
        print(f"{'='*100}{Colors.END}")
        
        for r in selling_activity:
            if r['unique_seller_count'] == 0:
                continue
            
            priority = "⭐" if r['ticker'] in PRIORITY_TICKERS else ""
            amount_str = f"${r['total_sale_min']/1000:.0f}K-${r['total_sale_max']/1000:.0f}K"
            
            print(f"\n   {r['ticker']:<6}{priority} [{r['sector']:<12}] | {r['unique_seller_count']} sellers | {len(r['sales'])} sales | {amount_str}")
            
            for sale in r['sales'][:3]:
                party_color = Colors.BLUE if sale['party'] == 'D' else Colors.RED if sale['party'] == 'R' else Colors.WHITE
                amount_str = f"${sale['amount_min']/1000:.0f}K-${sale['amount_max']/1000:.0f}K"
                days_ago = (datetime.now() - sale['date']).days
                
                print(f"      • {sale['politician']} ({sale['party']}-{sale['state']}) | {amount_str} | {days_ago} days ago")
    
    # Party breakdown
    print(f"\n{Colors.CYAN}{'='*100}")
    print(f"🏛️ PARTY BREAKDOWN")
    print(f"{'='*100}{Colors.END}")
    
    dem_purchases = [t for t in all_trades if t['transaction'] == 'Purchase' and t['party'] == 'D']
    rep_purchases = [t for t in all_trades if t['transaction'] == 'Purchase' and t['party'] == 'R']
    
    print(f"\n   Democrats: {len(dem_purchases)} purchases")
    print(f"   Republicans: {len(rep_purchases)} purchases")
    
    # Most active politicians
    politician_activity = {}
    for trade in all_trades:
        pol = trade['politician']
        if pol not in politician_activity:
            politician_activity[pol] = {'purchases': 0, 'sales': 0, 'party': trade['party'], 'state': trade['state']}
        
        if trade['transaction'] == 'Purchase':
            politician_activity[pol]['purchases'] += 1
        else:
            politician_activity[pol]['sales'] += 1
    
    most_active = sorted(politician_activity.items(), key=lambda x: x[1]['purchases'] + x[1]['sales'], reverse=True)
    
    if most_active:
        print(f"\n{Colors.YELLOW}MOST ACTIVE TRADERS:{Colors.END}")
        for pol, activity in most_active[:5]:
            print(f"   • {pol} ({activity['party']}-{activity['state']}): {activity['purchases']} buys, {activity['sales']} sales")
    
    # Wolf's read
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*100}")
    print(f"🐺 WOLF'S CONGRESSIONAL READ")
    print(f"{'='*100}{Colors.END}")
    
    if buying_activity:
        print(f"\n   🎯 STRONG BUYING SIGNALS:")
        for r in buying_activity[:3]:
            print(f"      → {r['ticker']}: {r['unique_buyer_count']} politicians buying")
            if r['committee_buyer_count'] > 0:
                print(f"        ⚠️ Including {r['committee_buyer_count']} important committee member(s)")
    
    print(f"\n   🏛️ WHAT IT MEANS:")
    print(f"      • Politicians file 45 days AFTER trade (delayed data)")
    print(f"      • Committee members = special insight into policy/contracts")
    print(f"      • Multiple politicians buying = broad consensus")
    print(f"      • Cross-party buying = VERY bullish")
    
    print(f"\n   ⚙️ HOW TO USE:")
    print(f"      1. Check which committees they're on")
    print(f"      2. Armed Services + Defense stocks = contracts coming")
    print(f"      3. Energy + Uranium stocks = policy support")
    print(f"      4. Multiple politicians = pattern, not luck")
    print(f"      5. Cross-reference with our other signals (8-K, insider, wounded prey)")
    
    print(f"\n   ⚠️ IMPORTANT:")
    print(f"      • This is DELAYED data (45-day filing)")
    print(f"      • Don't chase — use as confirmation")
    print(f"      • Best signal: Committee member buying in their sector")

# =============================================================================
# MAIN
# =============================================================================

def main():
    results, all_trades = scan_congress_trades(days=90)
    display_congress_report(results, all_trades)
    
    print(f"\n{'='*100}")
    print(f"{Colors.CYAN}{Colors.BOLD}🐺 AWOOOO! FOLLOW THE MONEY! LLHR! 🐺{Colors.END}")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    main()

# =============================================================================
# PRODUCTION NOTES
# =============================================================================
"""
To make this production-ready:

1. DATA SOURCE OPTIONS:
   
   A. Capitol Trades Website (https://www.capitoltrades.com)
      - Public data, no API
      - Would need to scrape HTML
      - Rate limit to be respectful
   
   B. House/Senate Financial Disclosures
      - https://disclosures-clerk.house.gov/PublicDisclosure/FinancialDisclosure
      - Official source
      - PDF/XML parsing required
   
   C. Quiver Quantitative API (paid)
      - Clean API access
      - $10-50/month
      - https://www.quiverquant.com/congresstrading/

2. SCRAPING IMPLEMENTATION:

   def scrape_capitol_trades():
       url = "https://www.capitoltrades.com/trades"
       headers = {'User-Agent': 'Mozilla/5.0...'}
       
       response = requests.get(url, headers=headers)
       soup = BeautifulSoup(response.content, 'html.parser')
       
       # Parse table rows
       trades = []
       for row in soup.find_all('tr', class_='trade-row'):
           trade = {
               'date': parse_date(row.find('td', class_='date').text),
               'politician': row.find('td', class_='politician').text,
               'ticker': row.find('td', class_='ticker').text,
               # ... etc
           }
           trades.append(trade)
       
       return trades

3. RATE LIMITING:
   - Add time.sleep(1) between requests
   - Cache results (don't re-scrape same data)
   - Respect robots.txt

4. DATA STORAGE:
   - Cache trades in JSON file
   - Only fetch new trades since last run
   - Keep historical data for pattern analysis

5. COMMITTEE DETECTION:
   - Scrape politician pages for committee assignments
   - Match committees to sectors (Armed Services → Defense, etc.)
"""
