#!/usr/bin/env python3
"""
🐺 CROSS-SIGNAL VALIDATOR - HIGH CONVICTION HUNTER
===================================================
Combine multiple signals for HIGH CONVICTION setups

SIGNALS:
- Wounded Prey (recovering from -30%+ decline)
- Insider Buying (Form 4 purchases, clusters)
- SEC 8-K Contracts (material contracts filed)
- Congress Trades (politicians buying)

When 3+ signals align → HIGH CONVICTION ENTRY

AWOOOO 🐺 LLHR
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import argparse
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
# WOUNDED PREY SIGNAL
# =============================================================================

def check_wounded_prey(ticker, days=90):
    """Check if ticker is wounded prey with bounce potential (0-30 points)"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1y', prepost=False)
        
        if len(hist) < 50:
            return 0, None
        
        current = hist['Close'].iloc[-1]
        high_52w = hist['High'].max()
        
        pct_from_high = ((current - high_52w) / high_52w) * 100
        
        # Not wounded
        if pct_from_high > -30:
            return 0, None
        
        # Price filter
        if current < 2 or current > 50:
            return 0, None
        
        # Recent recovery
        recent_5d = ((current - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100
        
        # Score wounded prey
        score = 0
        
        # Deeper wound
        if pct_from_high < -50:
            score += 15
        elif pct_from_high < -40:
            score += 10
        else:
            score += 5
        
        # Recovery started
        if recent_5d > 5:
            score += 15
        elif recent_5d > 0:
            score += 10
        else:
            score += 0
        
        details = {
            'status': 'WOUNDED',
            'pct_from_high': pct_from_high,
            'change_5d': recent_5d,
            'price': current
        }
        
        return score, details
        
    except Exception:
        return 0, None

# =============================================================================
# INSIDER BUYING SIGNAL
# =============================================================================

def check_insider_buying(ticker, days=90):
    """Check for insider buying activity (0-30 points)"""
    try:
        stock = yf.Ticker(ticker)
        
        # Get insider transactions
        insider_txns = stock.insider_transactions
        
        if insider_txns is None or len(insider_txns) == 0:
            return 0, None
        
        # Filter for purchases in date range
        cutoff = datetime.now() - timedelta(days=days)
        
        purchases = []
        for _, txn in insider_txns.iterrows():
            # Check if purchase
            txn_type = str(txn.get('Transaction', '')).lower()
            if 'purchase' not in txn_type and 'buy' not in txn_type:
                continue
            
            # Within timeframe
            txn_date = txn.get('Start Date')
            if txn_date and txn_date >= cutoff:
                purchases.append({
                    'date': txn_date,
                    'insider': txn.get('Insider', 'Unknown'),
                    'shares': txn.get('Shares', 0),
                    'value': txn.get('Value', 0)
                })
        
        if not purchases:
            return 0, None
        
        # Count unique buyers
        unique_buyers = len(set([p['insider'] for p in purchases]))
        total_value = sum([p['value'] if p['value'] else 0 for p in purchases])
        
        # Check for C-Suite
        c_suite_count = 0
        c_suite_keywords = ['ceo', 'cfo', 'coo', 'president', 'chairman', 'chief']
        for p in purchases:
            insider_lower = str(p['insider']).lower()
            if any(kw in insider_lower for kw in c_suite_keywords):
                c_suite_count += 1
        
        # Score insider buying
        score = 0
        
        # Multiple buyers (cluster)
        if unique_buyers >= 3:
            score += 15  # CLUSTER
        elif unique_buyers == 2:
            score += 10
        else:
            score += 5
        
        # C-Suite buying
        if c_suite_count >= 2:
            score += 10
        elif c_suite_count >= 1:
            score += 5
        
        # Recent activity (within 30 days)
        recent_purchases = [p for p in purchases if (datetime.now() - p['date']).days <= 30]
        if len(recent_purchases) >= 2:
            score += 5
        
        details = {
            'status': 'CLUSTER' if unique_buyers >= 3 else 'BUYING',
            'unique_buyers': unique_buyers,
            'total_purchases': len(purchases),
            'c_suite_count': c_suite_count,
            'total_value': total_value,
            'recent_count': len(recent_purchases)
        }
        
        return score, details
        
    except Exception:
        return 0, None

# =============================================================================
# SEC 8-K CONTRACT SIGNAL
# =============================================================================

def check_8k_contracts(ticker, days=30):
    """Check for recent 8-K contract filings (0-25 points)"""
    # NOTE: This is a placeholder. In production, integrate with sec_8k_contract_scanner.py
    # For now, we'll check recent news for contract keywords
    
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        if not news:
            return 0, None
        
        # Contract keywords
        contract_keywords = [
            'awarded', 'contract', 'dod', 'department of defense', 'nasa', 
            'doe', 'air force', 'navy', 'army', 'idiq', 'darpa',
            'government', 'federal', 'procurement'
        ]
        
        high_value_keywords = ['$', 'million', 'billion']
        
        # Check recent news
        cutoff = datetime.now() - timedelta(days=days)
        
        contract_hits = []
        for article in news[:20]:  # Check last 20 articles
            pub_time = datetime.fromtimestamp(article.get('providerPublishTime', 0))
            
            if pub_time < cutoff:
                continue
            
            title = str(article.get('title', '')).lower()
            
            # Check for contract keywords
            contract_match = any(kw in title for kw in contract_keywords)
            value_match = any(kw in title for kw in high_value_keywords)
            
            if contract_match:
                contract_hits.append({
                    'date': pub_time,
                    'title': article.get('title', ''),
                    'has_value': value_match
                })
        
        if not contract_hits:
            return 0, None
        
        # Score contracts
        score = 0
        
        # Recent contracts
        if len(contract_hits) >= 2:
            score += 15
        elif len(contract_hits) == 1:
            score += 10
        
        # High value contracts
        high_value_count = sum([1 for h in contract_hits if h['has_value']])
        if high_value_count >= 1:
            score += 10
        
        details = {
            'status': 'CONTRACTS',
            'contract_count': len(contract_hits),
            'high_value_count': high_value_count,
            'latest_date': max([h['date'] for h in contract_hits]) if contract_hits else None
        }
        
        return score, details
        
    except Exception:
        return 0, None

# =============================================================================
# THESIS ALIGNMENT SIGNAL
# =============================================================================

def check_thesis_alignment(ticker):
    """Check if ticker aligns with AI Fuel Chain thesis (0-15 points)"""
    
    score = 0
    
    # In thesis
    if ticker in sum(AI_FUEL_CHAIN.values(), []):
        score += 10
    
    # Priority ticker
    if ticker in PRIORITY_TICKERS:
        score += 5
    
    sector = get_sector_for_ticker(ticker)
    
    details = {
        'status': 'PRIORITY' if ticker in PRIORITY_TICKERS else 'THESIS' if score > 0 else 'OTHER',
        'sector': sector
    }
    
    return score, details

# =============================================================================
# CROSS-SIGNAL VALIDATION
# =============================================================================

def validate_ticker(ticker, wounded_days=90, insider_days=90, contract_days=30):
    """Validate ticker across all signals"""
    
    print(f"   Scanning {ticker}...", end="", flush=True)
    
    # Check all signals
    wounded_score, wounded_details = check_wounded_prey(ticker, wounded_days)
    insider_score, insider_details = check_insider_buying(ticker, insider_days)
    contract_score, contract_details = check_8k_contracts(ticker, contract_days)
    thesis_score, thesis_details = check_thesis_alignment(ticker)
    
    # Calculate total conviction score (0-100)
    total_score = wounded_score + insider_score + contract_score + thesis_score
    
    # Count active signals
    signals_active = sum([
        wounded_score > 0,
        insider_score > 0,
        contract_score > 0,
        thesis_score > 0
    ])
    
    print(f" {total_score}/100")
    
    result = {
        'ticker': ticker,
        'total_score': total_score,
        'signals_active': signals_active,
        'wounded': wounded_details,
        'wounded_score': wounded_score,
        'insider': insider_details,
        'insider_score': insider_score,
        'contract': contract_details,
        'contract_score': contract_score,
        'thesis': thesis_details,
        'thesis_score': thesis_score
    }
    
    return result

def scan_all_tickers(wounded_days=90, insider_days=90, contract_days=30, min_signals=2):
    """Scan all AI Fuel Chain tickers"""
    
    all_tickers = []
    for tickers in AI_FUEL_CHAIN.values():
        all_tickers.extend(tickers)
    
    print("\n" + "="*100)
    print(f"{Colors.CYAN}{Colors.BOLD}🎯 CROSS-SIGNAL VALIDATOR - HIGH CONVICTION HUNTER 🎯{Colors.END}")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print(f"   Scanning {len(all_tickers)} tickers across 4 signals")
    print("="*100)
    
    print(f"\n   {Colors.YELLOW}SIGNALS:{Colors.END}")
    print(f"      • Wounded Prey (0-30 pts): Recovering from -30%+ decline")
    print(f"      • Insider Buying (0-30 pts): Form 4 purchases, clusters")
    print(f"      • SEC 8-K Contracts (0-25 pts): Material contracts filed")
    print(f"      • Thesis Alignment (0-15 pts): AI Fuel Chain priority")
    print(f"      • CONVICTION: 70+ = HIGH | 50-69 = STRONG | 30-49 = MODERATE")
    print()
    
    results = []
    
    for ticker in all_tickers:
        result = validate_ticker(ticker, wounded_days, insider_days, contract_days)
        
        # Filter by minimum signals
        if result['signals_active'] >= min_signals:
            results.append(result)
    
    # Sort by total score
    results.sort(key=lambda x: x['total_score'], reverse=True)
    
    return results

def display_validation_report(results):
    """Display cross-signal validation report"""
    
    if not results:
        print(f"\n   {Colors.GREEN}No tickers with multiple signals found{Colors.END}")
        return
    
    # Tier by conviction score
    high_conviction = [r for r in results if r['total_score'] >= 70]
    strong_conviction = [r for r in results if 50 <= r['total_score'] < 70]
    moderate_conviction = [r for r in results if r['total_score'] < 50]
    
    # HIGH CONVICTION
    if high_conviction:
        print(f"\n{Colors.RED}{Colors.BOLD}{'='*100}")
        print(f"🔥 HIGH CONVICTION - READY TO HUNT")
        print(f"{'='*100}{Colors.END}")
        
        print(f"\n   {'TICKER':<8} | {'SECTOR':<12} | {'SIGNALS':>8} | {'WOUNDED':>8} | {'INSIDER':>8} | {'8-K':>8} | {'THESIS':>8} | {'SCORE':>7}")
        print(f"   {'─'*8}─┼─{'─'*12}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*7}")
        
        for r in high_conviction:
            priority = "⭐" if r['ticker'] in PRIORITY_TICKERS else ""
            
            wounded_status = "✓" if r['wounded_score'] > 0 else ""
            insider_status = "🔥" if r['insider'] and r['insider']['status'] == 'CLUSTER' else "✓" if r['insider_score'] > 0 else ""
            contract_status = "✓" if r['contract_score'] > 0 else ""
            thesis_status = "⭐" if r['thesis'] and r['thesis']['status'] == 'PRIORITY' else "✓" if r['thesis_score'] > 0 else ""
            
            print(f"   {r['ticker']:<6}{priority:<2} | {r['thesis']['sector']:<12} | {r['signals_active']:>8} | {r['wounded_score']:>7}{wounded_status} | {r['insider_score']:>7}{insider_status} | {r['contract_score']:>7}{contract_status} | {r['thesis_score']:>7}{thesis_status} | {Colors.BRIGHT_GREEN}{r['total_score']:>7}{Colors.END}")
        
        # Detailed breakdown
        print(f"\n{Colors.YELLOW}DETAILED BREAKDOWN:{Colors.END}")
        
        for r in high_conviction:
            print(f"\n   {Colors.BOLD}{r['ticker']}{Colors.END} [{r['thesis']['sector']}] — {Colors.BRIGHT_GREEN}CONVICTION: {r['total_score']}/100{Colors.END}")
            
            if r['wounded']:
                print(f"      🩸 WOUNDED: {r['wounded']['pct_from_high']:+.1f}% from high, {r['wounded']['change_5d']:+.1f}% 5d recovery")
            
            if r['insider']:
                cluster_txt = "🔥 CLUSTER" if r['insider']['status'] == 'CLUSTER' else "BUYING"
                print(f"      👔 INSIDER: {cluster_txt} — {r['insider']['unique_buyers']} buyers, {r['insider']['total_purchases']} txns, {r['insider']['c_suite_count']} C-Suite")
            
            if r['contract']:
                print(f"      📄 8-K: {r['contract']['contract_count']} contract(s), {r['contract']['high_value_count']} high-value")
            
            if r['thesis']:
                thesis_txt = "⭐ PRIORITY" if r['thesis']['status'] == 'PRIORITY' else "THESIS"
                print(f"      🎯 THESIS: {thesis_txt}")
    
    # STRONG CONVICTION
    if strong_conviction:
        print(f"\n{Colors.YELLOW}{'='*100}")
        print(f"💪 STRONG CONVICTION - WATCH CLOSELY")
        print(f"{'='*100}{Colors.END}")
        
        for r in strong_conviction[:10]:
            priority = "⭐" if r['ticker'] in PRIORITY_TICKERS else ""
            
            signals_str = []
            if r['wounded_score'] > 0:
                signals_str.append("WOUNDED")
            if r['insider_score'] > 0:
                signals_str.append("INSIDER" if r['insider']['status'] != 'CLUSTER' else "CLUSTER")
            if r['contract_score'] > 0:
                signals_str.append("8-K")
            if r['thesis_score'] > 0:
                signals_str.append("THESIS")
            
            print(f"   {r['ticker']:<6}{priority} [{r['thesis']['sector']:<12}] | Score: {r['total_score']:>3} | {' + '.join(signals_str)}")
    
    # MODERATE CONVICTION
    if moderate_conviction:
        print(f"\n{Colors.GREEN}{'='*100}")
        print(f"📊 MODERATE CONVICTION - EARLY WATCH")
        print(f"{'='*100}{Colors.END}")
        
        for r in moderate_conviction[:10]:
            priority = "⭐" if r['ticker'] in PRIORITY_TICKERS else ""
            print(f"   {r['ticker']:<6}{priority} [{r['thesis']['sector']:<12}] | Score: {r['total_score']:>3} | {r['signals_active']} signals")
    
    # Wolf's read
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*100}")
    print(f"🐺 WOLF'S CROSS-SIGNAL READ")
    print(f"{'='*100}{Colors.END}")
    
    if high_conviction:
        print(f"\n   🔥 HIGH CONVICTION SETUPS (70+):")
        for r in high_conviction[:3]:
            print(f"      → {r['ticker']}: {r['signals_active']} signals active, {r['total_score']}/100 conviction")
    
    print(f"\n   🎯 WHAT IT MEANS:")
    print(f"      • 1 signal = noise")
    print(f"      • 2 signals = pattern")
    print(f"      • 3+ signals = HIGH CONVICTION")
    print(f"      • Score 70+ = Ready to hunt")
    
    print(f"\n   ⚙️ HOW TO USE:")
    print(f"      1. Start with HIGH CONVICTION (70+)")
    print(f"      2. Verify in ATP Pro Level 2")
    print(f"      3. Check technical setup (support/resistance)")
    print(f"      4. Enter with position sizing")
    print(f"      5. Set stops (-8% to -10%)")
    
    print(f"\n   💰 EXAMPLE WORKFLOW:")
    print(f"      • Scanner flags: SIDU = 85/100 (wounded + insider cluster + 8-K contract + priority)")
    print(f"      • You verify: $4.20, bouncing off support, volume increasing")
    print(f"      • ATP Pro: Check Level 2, see tight spread, good liquidity")
    print(f"      • DECISION: Enter 2% position @ $4.20, stop @ $3.85, target $5.00")

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='🐺 Cross-Signal Validator')
    parser.add_argument('--ticker', type=str, help='Validate specific ticker')
    parser.add_argument('--wounded-days', type=int, default=90, help='Days lookback for wounded prey')
    parser.add_argument('--insider-days', type=int, default=90, help='Days lookback for insider buying')
    parser.add_argument('--contract-days', type=int, default=30, help='Days lookback for 8-K contracts')
    parser.add_argument('--min-signals', type=int, default=2, help='Minimum signals required')
    
    args = parser.parse_args()
    
    if args.ticker:
        # Validate single ticker
        result = validate_ticker(args.ticker, args.wounded_days, args.insider_days, args.contract_days)
        display_validation_report([result] if result['signals_active'] >= args.min_signals else [])
    else:
        # Scan all
        results = scan_all_tickers(args.wounded_days, args.insider_days, args.contract_days, args.min_signals)
        display_validation_report(results)
    
    print(f"\n{'='*100}")
    print(f"{Colors.CYAN}{Colors.BOLD}🐺 AWOOOO! HUNT WITH CONVICTION! LLHR! 🐺{Colors.END}")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    main()
