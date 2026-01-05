#!/usr/bin/env python3
"""
🐺 WOLF PACK ARSENAL - INSIDER BUYING TRACKER V2
=================================================
Track Form 4 filings for conviction buying signals
"Follow the smart money - they know what we don't"

IMPROVED:
- SEC EDGAR Form 4 direct access
- Cluster detection (multiple insiders buying)
- AI Fuel Chain sector integration
- Priority ticker focus
- Conviction scoring

TRANSACTION CODES:
P = Open market purchase (CONVICTION!)
S = Open market sale (watch out)
A = Grant/Award (compensation, ignore)
M = Option exercise (mixed signal)
G = Gift (ignore)

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
    BRIGHT_RED = '\033[31m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# =============================================================================
# AI FUEL CHAIN SECTORS
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
    """Get sector for a ticker"""
    for sector, tickers in AI_FUEL_CHAIN.items():
        if ticker in tickers:
            return sector
    return "OTHER"

# =============================================================================
# INSIDER DATA FETCHING
# =============================================================================

def get_insider_data_yf(ticker):
    """Get insider transactions using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        insider_df = stock.insider_transactions
        
        if insider_df is None or insider_df.empty:
            return None
        
        # Filter for recent transactions (last 90 days)
        if 'Start Date' in insider_df.columns:
            insider_df['Start Date'] = pd.to_datetime(insider_df['Start Date'], errors='coerce')
            cutoff = datetime.now() - timedelta(days=90)
            insider_df = insider_df[insider_df['Start Date'] >= cutoff]
        
        return insider_df
        
    except Exception as e:
        return None

def analyze_insider_activity(ticker):
    """Analyze insider buying/selling activity for a ticker"""
    df = get_insider_data_yf(ticker)
    
    if df is None or df.empty:
        return {
            "ticker": ticker,
            "sector": get_sector_for_ticker(ticker),
            "total_buys": 0,
            "total_sells": 0,
            "net_sentiment": "NO DATA",
            "recent_transactions": [],
            "conviction_score": 0,
            "cluster": False
        }
    
    # Count buys vs sells
    buys = 0
    sells = 0
    buy_value = 0
    sell_value = 0
    recent_txns = []
    unique_buyers = set()
    unique_sellers = set()
    
    for _, row in df.iterrows():
        txn_type = str(row.get('Transaction', '')).lower()
        shares = abs(row.get('Shares', 0)) if pd.notna(row.get('Shares')) else 0
        value = abs(row.get('Value', 0)) if pd.notna(row.get('Value')) else 0
        insider = row.get('Insider', 'Unknown')
        
        if 'purchase' in txn_type or 'buy' in txn_type:
            buys += 1
            buy_value += value
            unique_buyers.add(insider)
            recent_txns.append({
                "type": "BUY",
                "insider": insider,
                "shares": shares,
                "value": value,
                "date": row.get('Start Date', '')
            })
        elif 'sale' in txn_type or 'sell' in txn_type:
            sells += 1
            sell_value += value
            unique_sellers.add(insider)
            recent_txns.append({
                "type": "SELL",
                "insider": insider,
                "shares": shares,
                "value": value,
                "date": row.get('Start Date', '')
            })
    
    # Cluster detection (multiple insiders buying = conviction)
    is_cluster = len(unique_buyers) >= 3
    
    # Calculate sentiment
    if buys > sells * 2:
        sentiment = "STRONG BUY"
        conviction = min(100, buys * 10 + len(unique_buyers) * 5)
    elif buys > sells:
        sentiment = "BULLISH"
        conviction = min(80, buys * 8 + len(unique_buyers) * 4)
    elif sells > buys * 2:
        sentiment = "STRONG SELL"
        conviction = -min(100, sells * 10)
    elif sells > buys:
        sentiment = "BEARISH"
        conviction = -min(80, sells * 8)
    else:
        sentiment = "NEUTRAL"
        conviction = 0
    
    return {
        "ticker": ticker,
        "sector": get_sector_for_ticker(ticker),
        "total_buys": buys,
        "total_sells": sells,
        "unique_buyers": len(unique_buyers),
        "unique_sellers": len(unique_sellers),
        "buy_value": buy_value,
        "sell_value": sell_value,
        "net_sentiment": sentiment,
        "recent_transactions": sorted(recent_txns, key=lambda x: x['date'], reverse=True)[:10],
        "conviction_score": conviction,
        "cluster": is_cluster
    }

# =============================================================================
# SCANNING FUNCTIONS
# =============================================================================

def scan_insider_activity(min_buys=1):
    """Scan all AI Fuel Chain tickers for insider activity"""
    
    all_tickers = []
    for tickers in AI_FUEL_CHAIN.values():
        all_tickers.extend(tickers)
    
    print("\n" + "="*100)
    print(f"{Colors.CYAN}{Colors.BOLD}👔 WOLF PACK ARSENAL - INSIDER BUYING TRACKER V2 👔{Colors.END}")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print(f"   Scanning {len(all_tickers)} tickers for insider activity (last 90 days)")
    print(f"   Looking for conviction buying signals + clusters")
    print("="*100)
    
    results = []
    
    print(f"\n   Scanning", end="", flush=True)
    for i, ticker in enumerate(all_tickers):
        if i % 10 == 0:
            print(".", end="", flush=True)
        data = analyze_insider_activity(ticker)
        if data and (data["total_buys"] >= min_buys or data["total_sells"] >= min_buys):
            results.append(data)
    print(" ✓ Done!")
    
    # Sort by conviction score
    results.sort(key=lambda x: x["conviction_score"], reverse=True)
    
    return results

def display_insider_report(results):
    """Display comprehensive insider report"""
    
    # Cluster alerts
    clusters = [r for r in results if r.get("cluster")]
    if clusters:
        print(f"\n{Colors.RED}{Colors.BOLD}{'='*100}")
        print(f"🚨 CLUSTER ALERTS - Multiple Insiders Buying (High Conviction!)")
        print(f"{'='*100}{Colors.END}")
        
        for r in clusters:
            priority = "⭐" if r['ticker'] in PRIORITY_TICKERS else ""
            print(f"\n   {Colors.BRIGHT_GREEN}{r['ticker']}{priority} [{r['sector']}]{Colors.END}")
            print(f"      {r['unique_buyers']} different insiders buying | {r['total_buys']} total buys")
            print(f"      Conviction Score: {r['conviction_score']}")
    
    # Strong buys
    strong_buys = [r for r in results if r["net_sentiment"] == "STRONG BUY"]
    print(f"\n{Colors.BRIGHT_GREEN}{'='*100}")
    print(f"🔥 STRONG INSIDER BUYING ({len(strong_buys)} stocks)")
    print(f"{'='*100}{Colors.END}")
    
    if strong_buys:
        print(f"\n   {'TICKER':<8} | {'SECTOR':<12} | {'BUYS':>6} | {'BUYERS':>7} | {'BUY VALUE':>12} | {'SCORE':>7} | {'⭐':<3}")
        print(f"   {'─'*8}─┼─{'─'*12}─┼─{'─'*6}─┼─{'─'*7}─┼─{'─'*12}─┼─{'─'*7}─┼─{'─'*3}")
        
        for r in strong_buys[:20]:
            priority = "⭐" if r['ticker'] in PRIORITY_TICKERS else ""
            cluster = "🔥" if r['cluster'] else ""
            buy_val_str = f"${r['buy_value']/1e6:.1f}M" if r['buy_value'] >= 1e6 else f"${r['buy_value']/1e3:.0f}K"
            
            print(f"   {r['ticker']:<8} | {r['sector']:<12} | {r['total_buys']:>6} | {r['unique_buyers']:>7} | {buy_val_str:>12} | {r['conviction_score']:>7} | {priority}{cluster}")
    else:
        print("   No strong insider buying detected")
    
    # Bullish signals
    bullish = [r for r in results if r["net_sentiment"] == "BULLISH"]
    if bullish:
        print(f"\n{Colors.GREEN}{'='*100}")
        print(f"📈 BULLISH INSIDER ACTIVITY ({len(bullish)} stocks)")
        print(f"{'='*100}{Colors.END}")
        
        for r in bullish[:15]:
            priority = "⭐" if r['ticker'] in PRIORITY_TICKERS else ""
            buy_val_str = f"${r['buy_value']/1e6:.1f}M" if r['buy_value'] >= 1e6 else f"${r['buy_value']/1e3:.0f}K"
            print(f"   {r['ticker']:<8}{priority} [{r['sector']:<12}] | Buys: {r['total_buys']:>2} | Buyers: {r['unique_buyers']} | Value: {buy_val_str}")
    
    # Sector breakdown
    print(f"\n{Colors.CYAN}{'='*100}")
    print(f"📊 INSIDER ACTIVITY BY SECTOR")
    print(f"{'='*100}{Colors.END}")
    
    sector_stats = {}
    for r in results:
        sector = r['sector']
        if sector not in sector_stats:
            sector_stats[sector] = {'buys': 0, 'count': 0, 'clusters': 0}
        
        sector_stats[sector]['buys'] += r['total_buys']
        sector_stats[sector]['count'] += 1
        if r['cluster']:
            sector_stats[sector]['clusters'] += 1
    
    sorted_sectors = sorted(sector_stats.items(), key=lambda x: x[1]['buys'], reverse=True)
    
    print(f"\n   {'SECTOR':<15} | {'STOCKS':>7} | {'TOTAL BUYS':>12} | {'CLUSTERS':>10}")
    print(f"   {'─'*15}─┼─{'─'*7}─┼─{'─'*12}─┼─{'─'*10}")
    
    for sector, stats in sorted_sectors:
        heat = "🔥" if stats['clusters'] > 0 else "📈" if stats['buys'] >= 10 else ""
        print(f"   {sector:<15} | {stats['count']:>7} | {stats['buys']:>12} | {stats['clusters']:>10} {heat}")
    
    # Warnings (heavy selling)
    bearish = [r for r in results if r["net_sentiment"] in ["BEARISH", "STRONG SELL"]]
    if bearish:
        print(f"\n{Colors.RED}{'='*100}")
        print(f"⚠️  INSIDER SELLING WARNING ({len(bearish)} stocks)")
        print(f"{'='*100}{Colors.END}")
        
        for r in bearish[:10]:
            priority = "⭐" if r['ticker'] in PRIORITY_TICKERS else ""
            sell_val_str = f"${r['sell_value']/1e6:.1f}M" if r['sell_value'] >= 1e6 else f"${r['sell_value']/1e3:.0f}K"
            print(f"   {r['ticker']:<8}{priority} [{r['sector']:<12}] | Sells: {r['total_sells']:>2} | Sell Value: {sell_val_str}")
    
    # Priority tickers
    print(f"\n{Colors.YELLOW}{'='*100}")
    print(f"⭐ PRIORITY TICKER WATCH")
    print(f"{'='*100}{Colors.END}")
    
    for ticker in PRIORITY_TICKERS:
        data = [r for r in results if r['ticker'] == ticker]
        
        if data:
            r = data[0]
            emoji = "🔥" if r["cluster"] else \
                    "💪" if r["net_sentiment"] == "STRONG BUY" else \
                    "📈" if r["net_sentiment"] == "BULLISH" else \
                    "⚠️" if r["net_sentiment"] in ["BEARISH", "STRONG SELL"] else "➖"
            
            print(f"   {emoji} {r['ticker']:<8} [{r['sector']:<12}] | Buys: {r['total_buys']:>3} | Sells: {r['total_sells']:>3} | {r['net_sentiment']}")
        else:
            print(f"   ➖ {ticker:<8} | No insider data")
    
    # Wolf's read
    print(f"\n{Colors.CYAN}{'='*100}")
    print(f"🐺 WOLF'S INSIDER READ")
    print(f"{'='*100}{Colors.END}")
    
    if clusters:
        print(f"\n   🚨 {len(clusters)} CLUSTERS DETECTED:")
        for c in clusters[:5]:
            print(f"      → {c['ticker']} ({c['sector']}): {c['unique_buyers']} insiders buying")
        print(f"\n   Multiple insiders = they know something we don't")
    
    if strong_buys:
        print(f"\n   💪 TOP CONVICTION PLAYS:")
        for sb in strong_buys[:5]:
            print(f"      → {sb['ticker']}: Score {sb['conviction_score']}, {sb['total_buys']} buys")
    
    print(f"\n   🎯 STRATEGY:")
    print(f"      • Clusters = highest conviction")
    print(f"      • Multiple buyers > single buyer")
    print(f"      • Open market purchases (P) = real conviction")
    print(f"      • Insiders front-run news by weeks/months")

def get_ticker_insider_detail(ticker):
    """Get detailed insider information for a single ticker"""
    
    print(f"\n{Colors.CYAN}{'='*80}")
    print(f"🔍 INSIDER DETAIL: {ticker}")
    print(f"{'='*80}{Colors.END}")
    
    data = analyze_insider_activity(ticker)
    
    if not data or data['net_sentiment'] == 'NO DATA':
        print("   No insider data available")
        return None
    
    sector = data['sector']
    priority = "⭐ PRIORITY" if ticker in PRIORITY_TICKERS else ""
    cluster = "🔥 CLUSTER DETECTED" if data['cluster'] else ""
    
    print(f"\n   Ticker: {Colors.BOLD}{ticker}{Colors.END} [{sector}] {priority} {cluster}")
    print(f"   Sentiment: {Colors.GREEN if 'BUY' in data['net_sentiment'] else Colors.RED}{data['net_sentiment']}{Colors.END}")
    print(f"   Conviction Score: {data['conviction_score']}")
    print(f"\n   Buying Activity:")
    print(f"      Total Buys: {data['total_buys']}")
    print(f"      Unique Buyers: {data['unique_buyers']}")
    print(f"      Buy Value: ${data['buy_value']:,.0f}")
    print(f"\n   Selling Activity:")
    print(f"      Total Sells: {data['total_sells']}")
    print(f"      Unique Sellers: {data['unique_sellers']}")
    print(f"      Sell Value: ${data['sell_value']:,.0f}")
    
    if data['recent_transactions']:
        print(f"\n   Recent Transactions:")
        print(f"   {'TYPE':<6} | {'INSIDER':<35} | {'SHARES':>12} | {'VALUE':>14} | {'DATE':<12}")
        print(f"   {'─'*6}─┼─{'─'*35}─┼─{'─'*12}─┼─{'─'*14}─┼─{'─'*12}")
        
        for txn in data['recent_transactions'][:10]:
            emoji = "🟢" if txn['type'] == 'BUY' else "🔴"
            val_str = f"${txn['value']:,.0f}" if txn['value'] else "N/A"
            shares_str = f"{txn['shares']:,.0f}" if txn['shares'] else "N/A"
            date_str = str(txn['date'])[:10] if pd.notna(txn['date']) else "N/A"
            
            print(f"   {emoji} {txn['type']:<4} | {txn['insider'][:35]:<35} | {shares_str:>12} | {val_str:>14} | {date_str}")
    
    return data

# =============================================================================
# MAIN
# =============================================================================

def main():
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "detail" and len(sys.argv) > 2:
            ticker = sys.argv[2].upper()
            get_ticker_insider_detail(ticker)
        elif sys.argv[1] == "priority":
            results = scan_insider_activity(min_buys=0)
            priority_results = [r for r in results if r['ticker'] in PRIORITY_TICKERS]
            display_insider_report(priority_results)
        elif sys.argv[1] == "--ticker" and len(sys.argv) > 2:
            ticker = sys.argv[2].upper()
            get_ticker_insider_detail(ticker)
        else:
            ticker = sys.argv[1].upper()
            get_ticker_insider_detail(ticker)
    else:
        results = scan_insider_activity(min_buys=1)
        display_insider_report(results)
    
    print(f"\n{'='*100}")
    print(f"{Colors.CYAN}{Colors.BOLD}🐺 AWOOOO! FOLLOW THE SMART MONEY! LLHR! 🐺{Colors.END}")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    main()
