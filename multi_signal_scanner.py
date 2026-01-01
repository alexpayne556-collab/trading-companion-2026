#!/usr/bin/env python3
"""
🐺 WOLF PACK MULTI-SIGNAL INTELLIGENCE SCANNER
"Insider buying is ONE signal. Here are ALL 10."

Scores stocks across 10 signals:
1. Insider Buying (Form 4)
2. Analyst Coverage (ratings, targets)
3. Government Contracts (8-K, press releases)
4. Big Tech Partnerships
5. Short Interest (squeeze potential)
6. Institutional Accumulation (13F)
7. Options Flow (unusual activity)
8. Earnings/Guidance (fundamentals)
9. Product Milestones (execution)
10. Momentum/Sentiment (technical)

Score ranges:
- 100+ = VERY HIGH CONVICTION
- 70-99 = HIGH CONVICTION
- 40-69 = MEDIUM CONVICTION
- <40 = LOW CONVICTION

Usage:
    python3 multi_signal_scanner.py --ticker AISP
    python3 multi_signal_scanner.py --watchlist
    python3 multi_signal_scanner.py --top 10
"""

import yfinance as yf
import argparse
import sys
from datetime import datetime, timedelta
from typing import Dict, List
import subprocess

# ============================================================
# CONFIGURATION
# ============================================================

# Priority watchlist
WATCHLIST = [
    'AISP', 'EFOI', 'SOUN', 'BBAI', 'SMR', 'IONQ', 'RGTI', 'QBTS',
    'LUNR', 'RKLB', 'ASTS', 'PATH', 'PLTR', 'UA', 'SIDU',
    'VRT', 'CCJ', 'OKLO', 'MU', 'AMD', 'NVDA',
]

# ============================================================
# SIGNAL SCORING FUNCTIONS
# ============================================================

def score_insider_buying(ticker: str) -> Dict:
    """
    Score insider buying from OpenInsider data
    
    Points:
    - No insider buying: 0
    - Single insider <$100K: +5
    - Single insider >$100K: +10
    - Multiple insiders (cluster): +15
    - C-Suite buying: +20
    - 10% owner: +15
    """
    try:
        # Call insider_cluster_hunter to get data
        result = subprocess.run(
            ['python3', 'insider_cluster_hunter.py', '--validate', ticker],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout
        
        # Parse output for insider buying
        if 'NO INSIDER BUYING FOUND' in output:
            return {'score': 0, 'note': 'No insider buying'}
        
        # Look for validation indicators
        if 'C-SUITE' in output:
            return {'score': 20, 'note': 'C-Suite buying detected'}
        elif '10% OWNER' in output:
            return {'score': 15, 'note': '10% owner buying'}
        elif 'CLUSTER' in output:
            return {'score': 15, 'note': 'Multiple insiders buying'}
        else:
            # Default to some insider buying
            return {'score': 10, 'note': 'Insider buying detected'}
            
    except Exception as e:
        return {'score': 0, 'note': f'Error checking: {e}'}

def score_analyst_coverage(ticker: str) -> Dict:
    """
    Score analyst coverage
    
    Points:
    - No coverage: 0
    - Hold: +5
    - Buy: +10
    - Strong Buy: +15
    - Price target raise: +10
    - New initiation: +15
    
    Note: This requires manual input or paid API
    For now, check Yahoo Finance data
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Check for analyst recommendations
        recommendation = info.get('recommendationKey', 'none')
        target_price = info.get('targetMeanPrice', 0)
        current_price = info.get('currentPrice', 0)
        
        score = 0
        notes = []
        
        if recommendation == 'strong_buy':
            score += 15
            notes.append('Strong Buy rating')
        elif recommendation == 'buy':
            score += 10
            notes.append('Buy rating')
        elif recommendation == 'hold':
            score += 5
            notes.append('Hold rating')
        
        # Check if target price is significantly above current
        if target_price and current_price:
            upside = ((target_price - current_price) / current_price) * 100
            if upside > 50:
                score += 15
                notes.append(f'{upside:.0f}% upside to target')
            elif upside > 20:
                score += 10
                notes.append(f'{upside:.0f}% upside to target')
        
        return {
            'score': min(score, 25),  # Cap at 25
            'note': ' | '.join(notes) if notes else 'Limited coverage'
        }
        
    except Exception as e:
        return {'score': 0, 'note': 'Unknown coverage'}

def score_short_interest(ticker: str) -> Dict:
    """
    Score short interest (squeeze potential)
    
    Points:
    - <10%: 0
    - 10-20%: +5
    - 20-30%: +10
    - >30%: +15
    - Days to cover >5: +5 bonus
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        short_ratio = info.get('shortRatio', 0)  # Days to cover
        short_percent = info.get('shortPercentOfFloat', 0)
        
        score = 0
        notes = []
        
        if short_percent > 30:
            score += 15
            notes.append(f'{short_percent:.1f}% short (EXTREME)')
        elif short_percent > 20:
            score += 10
            notes.append(f'{short_percent:.1f}% short (HIGH)')
        elif short_percent > 10:
            score += 5
            notes.append(f'{short_percent:.1f}% short (MODERATE)')
        
        if short_ratio > 5:
            score += 5
            notes.append(f'{short_ratio:.1f} days to cover')
        
        return {
            'score': score,
            'note': ' | '.join(notes) if notes else 'Low short interest'
        }
        
    except Exception as e:
        return {'score': 0, 'note': 'Unknown short data'}

def score_momentum(ticker: str) -> Dict:
    """
    Score momentum and sentiment
    
    Points:
    - Declining volume: -5
    - Normal: 0
    - Increasing volume 1.5x+: +5
    - High volume 3x+: +10
    - Recent price action positive: +5
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="60d")
        
        if len(hist) < 30:
            return {'score': 0, 'note': 'Insufficient data'}
        
        # Volume analysis
        volume_avg = hist['Volume'].iloc[:-30].mean()
        volume_recent = hist['Volume'].iloc[-30:].mean()
        volume_ratio = volume_recent / volume_avg if volume_avg > 0 else 1
        
        # Price action
        price_30d_ago = hist['Close'].iloc[-30]
        price_now = hist['Close'].iloc[-1]
        price_change = ((price_now - price_30d_ago) / price_30d_ago) * 100
        
        score = 0
        notes = []
        
        # Volume scoring
        if volume_ratio > 3:
            score += 10
            notes.append(f'Volume {volume_ratio:.1f}x (STRONG)')
        elif volume_ratio > 1.5:
            score += 5
            notes.append(f'Volume {volume_ratio:.1f}x')
        elif volume_ratio < 0.8:
            score -= 5
            notes.append('Volume declining')
        
        # Price action
        if price_change > 20:
            score += 10
            notes.append(f'Up {price_change:.1f}% (30d)')
        elif price_change > 0:
            score += 5
            notes.append(f'Up {price_change:.1f}% (30d)')
        elif price_change < -20:
            score -= 5
            notes.append(f'Down {price_change:.1f}% (30d)')
        
        return {
            'score': score,
            'note': ' | '.join(notes) if notes else 'Neutral momentum'
        }
        
    except Exception as e:
        return {'score': 0, 'note': f'Error: {e}'}

def score_earnings(ticker: str) -> Dict:
    """
    Score earnings and guidance
    
    Points:
    - Miss both: -10
    - Beat EPS or revenue: +5
    - Beat both: +15
    - Raised guidance: +15
    
    Note: Requires manual input or earnings calendar API
    For now, check profitability and growth
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Check profitability
        profit_margins = info.get('profitMargins', 0)
        revenue_growth = info.get('revenueGrowth', 0)
        earnings_growth = info.get('earningsGrowth', 0)
        
        score = 0
        notes = []
        
        # Profitability
        if profit_margins and profit_margins > 0.2:
            score += 10
            notes.append(f'{profit_margins*100:.1f}% profit margin')
        elif profit_margins and profit_margins > 0:
            score += 5
            notes.append('Profitable')
        elif profit_margins and profit_margins < -0.5:
            score -= 10
            notes.append('Burning cash heavily')
        
        # Growth
        if revenue_growth and revenue_growth > 0.3:
            score += 10
            notes.append(f'{revenue_growth*100:.0f}% revenue growth')
        elif revenue_growth and revenue_growth > 0.1:
            score += 5
            notes.append(f'{revenue_growth*100:.0f}% revenue growth')
        
        return {
            'score': min(score, 20),  # Cap at 20
            'note': ' | '.join(notes) if notes else 'Check latest earnings'
        }
        
    except Exception as e:
        return {'score': 0, 'note': 'Unknown earnings data'}

def score_partnerships(ticker: str) -> Dict:
    """
    Score partnerships and contracts
    
    Points:
    - No partnerships: 0
    - Small company: +5
    - Mid-cap: +10
    - Big Tech (AMZN, MSFT, GOOGL): +20
    
    Note: Requires manual research or news scraping
    For now, placeholder
    """
    # This would require news scraping or manual input
    # For MVP, return placeholder
    return {
        'score': 0,
        'note': 'Manual research required - check news'
    }

def score_contracts(ticker: str) -> Dict:
    """
    Score government contracts
    
    Points:
    - No contracts: 0
    - Small (<$10M): +5
    - Medium ($10-100M): +10
    - Large (>$100M): +20
    - DoD/NASA: +10 bonus
    
    Note: Requires 8-K monitoring or news scraping
    For now, placeholder
    """
    # This would require 8-K scraping or manual input
    # For MVP, return placeholder
    return {
        'score': 0,
        'note': 'Manual research required - check 8-Ks'
    }

# ============================================================
# COMPOSITE SCORING
# ============================================================

def calculate_multi_signal_score(ticker: str) -> Dict:
    """
    Calculate composite score across all signals
    
    Returns dict with:
    - total_score
    - breakdown by signal
    - conviction level
    """
    print(f"\n🔍 Analyzing {ticker}...")
    
    # Score each signal
    signals = {
        'insider_buying': score_insider_buying(ticker),
        'analyst_coverage': score_analyst_coverage(ticker),
        'short_interest': score_short_interest(ticker),
        'momentum': score_momentum(ticker),
        'earnings': score_earnings(ticker),
        'partnerships': score_partnerships(ticker),
        'contracts': score_contracts(ticker),
    }
    
    # Calculate total
    total_score = sum(s['score'] for s in signals.values())
    
    # Determine conviction level
    if total_score >= 100:
        conviction = 'VERY HIGH'
        emoji = '🔥🔥🔥'
    elif total_score >= 70:
        conviction = 'HIGH'
        emoji = '🔥🔥'
    elif total_score >= 40:
        conviction = 'MEDIUM'
        emoji = '🔥'
    else:
        conviction = 'LOW'
        emoji = '⚠️'
    
    return {
        'ticker': ticker,
        'total_score': total_score,
        'conviction': conviction,
        'emoji': emoji,
        'signals': signals,
    }

# ============================================================
# REPORTING
# ============================================================

def print_detailed_report(result: Dict):
    """Print detailed breakdown for single ticker"""
    
    print("\n" + "="*70)
    print(f"🐺 MULTI-SIGNAL ANALYSIS: {result['ticker']}")
    print("="*70)
    
    print(f"\n📊 TOTAL SCORE: {result['total_score']} / 150")
    print(f"🎯 CONVICTION: {result['emoji']} {result['conviction']}")
    
    print("\n" + "-"*70)
    print(f"{'SIGNAL':<25} {'SCORE':<10} {'NOTES'}")
    print("-"*70)
    
    signals = result['signals']
    
    print(f"{'1. Insider Buying':<25} {signals['insider_buying']['score']:>3}/20 {signals['insider_buying']['note']}")
    print(f"{'2. Analyst Coverage':<25} {signals['analyst_coverage']['score']:>3}/25 {signals['analyst_coverage']['note']}")
    print(f"{'3. Government Contracts':<25} {signals['contracts']['score']:>3}/30 {signals['contracts']['note']}")
    print(f"{'4. Partnerships':<25} {signals['partnerships']['score']:>3}/20 {signals['partnerships']['note']}")
    print(f"{'5. Short Interest':<25} {signals['short_interest']['score']:>3}/20 {signals['short_interest']['note']}")
    print(f"{'6. Momentum':<25} {signals['momentum']['score']:>3}/20 {signals['momentum']['note']}")
    print(f"{'7. Earnings':<25} {signals['earnings']['score']:>3}/20 {signals['earnings']['note']}")
    
    print("\n" + "="*70)
    
    # Trading recommendation
    print("\n💡 TRADING RECOMMENDATION:")
    
    if result['total_score'] >= 70:
        print("  ✅ HIGH CONVICTION - Consider for entry")
        print("  ✅ Multiple strong signals align")
        print("  Strategy: Size appropriately, set stops")
    elif result['total_score'] >= 40:
        print("  ⚠️ MEDIUM CONVICTION - Watch for more signals")
        print("  Strategy: Small position or wait for catalyst")
    else:
        print("  ❌ LOW CONVICTION - Avoid or paper trade only")
        print("  Strategy: Wait for stronger setup")

def print_watchlist_report(results: List[Dict]):
    """Print ranked watchlist"""
    
    # Sort by score
    results.sort(key=lambda x: x['total_score'], reverse=True)
    
    print("\n" + "="*70)
    print("🐺 WOLF PACK MULTI-SIGNAL RANKINGS")
    print("="*70)
    
    print(f"\n{'Rank':<6} {'Ticker':<8} {'Score':<8} {'Conviction':<15} {'Top Signals'}")
    print("-"*70)
    
    for i, result in enumerate(results, 1):
        ticker = result['ticker']
        score = result['total_score']
        conviction = f"{result['emoji']} {result['conviction']}"
        
        # Find top 2 signals
        signals = result['signals']
        top_signals = sorted(signals.items(), key=lambda x: x[1]['score'], reverse=True)[:2]
        top_names = [name.replace('_', ' ').title() for name, data in top_signals if data['score'] > 0]
        top_str = ', '.join(top_names[:2]) if top_names else 'Technical only'
        
        print(f"{i:<6} {ticker:<8} {score:<8} {conviction:<15} {top_str}")
    
    print("\n" + "="*70)
    print("\n📊 CONVICTION BREAKDOWN:")
    
    very_high = [r for r in results if r['total_score'] >= 100]
    high = [r for r in results if 70 <= r['total_score'] < 100]
    medium = [r for r in results if 40 <= r['total_score'] < 70]
    low = [r for r in results if r['total_score'] < 40]
    
    print(f"  🔥🔥🔥 VERY HIGH (100+): {len(very_high)} tickers")
    if very_high:
        print(f"      {', '.join([r['ticker'] for r in very_high])}")
    
    print(f"  🔥🔥 HIGH (70-99): {len(high)} tickers")
    if high:
        print(f"      {', '.join([r['ticker'] for r in high])}")
    
    print(f"  🔥 MEDIUM (40-69): {len(medium)} tickers")
    if medium:
        print(f"      {', '.join([r['ticker'] for r in medium])}")
    
    print(f"  ⚠️ LOW (<40): {len(low)} tickers")
    if low:
        print(f"      {', '.join([r['ticker'] for r in low])}")

# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='🐺 Wolf Pack Multi-Signal Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 multi_signal_scanner.py --ticker AISP
  python3 multi_signal_scanner.py --watchlist
  python3 multi_signal_scanner.py --top 10
  python3 multi_signal_scanner.py --compare AISP SOUN SMR
        """
    )
    
    parser.add_argument('--ticker', type=str,
                       help='Analyze single ticker')
    parser.add_argument('--watchlist', action='store_true',
                       help='Scan entire watchlist')
    parser.add_argument('--top', type=int,
                       help='Show top N ranked tickers')
    parser.add_argument('--compare', nargs='+',
                       help='Compare multiple tickers')
    
    args = parser.parse_args()
    
    # Single ticker
    if args.ticker:
        result = calculate_multi_signal_score(args.ticker.upper())
        print_detailed_report(result)
        return
    
    # Compare tickers
    if args.compare:
        results = []
        for ticker in args.compare:
            result = calculate_multi_signal_score(ticker.upper())
            results.append(result)
        print_watchlist_report(results)
        return
    
    # Watchlist scan
    if args.watchlist or args.top:
        print("\n🔍 Scanning watchlist...")
        results = []
        
        tickers = WATCHLIST[:args.top] if args.top else WATCHLIST
        
        for ticker in tickers:
            try:
                result = calculate_multi_signal_score(ticker)
                results.append(result)
            except Exception as e:
                print(f"  ⚠️ Error scanning {ticker}: {e}")
                continue
        
        print_watchlist_report(results)
        return
    
    # Default: show help
    parser.print_help()
    
    print("\n" + "="*70)
    print("🐺 AWOOOO - Multi-signal intelligence system online")
    print("="*70)
    print("\nTip: Start with --ticker AISP to see detailed breakdown")
    print("     Then run --watchlist to rank all opportunities")
    print("\n")

if __name__ == "__main__":
    main()
