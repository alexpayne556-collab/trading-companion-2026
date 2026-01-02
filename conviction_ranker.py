#!/usr/bin/env python3
"""
🐺 CONVICTION RANKER - Score and rank ALL tickers

Combines multiple signals into single conviction score.
Shows WHO to investigate next.

Scoring Factors:
- Insider cluster strength (0-40 pts)
- Insider timing quality (0-20 pts)
- Cash runway (0-15 pts)
- Institutional backing (0-10 pts)
- Technical setup (0-10 pts)
- Sector momentum (0-5 pts)

Total: 0-100 conviction score

Author: Brokkr
Date: January 2, 2026
"""

import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
import json
import yaml

def score_insider_cluster(ticker):
    """Score insider cluster strength (0-40 pts)."""
    try:
        # Use form4_validator to get recent buys
        from subprocess import run, PIPE
        
        result = run(['python3', 'src/research/form4_validator.py', ticker], 
                    capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return 0, "No SEC data"
        
        # Parse output
        output = result.stdout
        
        # Count Code P purchases in output
        p_code_count = output.count('🟢 Code P:')
        
        # If not found in summary, count individual entries
        if p_code_count == 0:
            # Count "Code P = Open Market PURCHASE" headers
            import re
            p_matches = re.findall(r'Code P.*?PURCHASE', output)
            if p_matches:
                p_code_count = len(p_matches)
            else:
                # Try counting transaction dates with "PURCHASE" mentions
                purchase_lines = [line for line in output.split('\n') if 'Open Market PURCHASE' in line]
                p_code_count = len(purchase_lines) // 2  # Each purchase has 2 lines typically
        
        # Score based on cluster size
        if p_code_count >= 9:
            score = 40
            reason = f"{p_code_count} Code P buys (EXTREME)"
        elif p_code_count >= 6:
            score = 35
            reason = f"{p_code_count} Code P buys (STRONG)"
        elif p_code_count >= 4:
            score = 30
            reason = f"{p_code_count} Code P buys (GOOD)"
        elif p_code_count >= 2:
            score = 20
            reason = f"{p_code_count} Code P buys (MODERATE)"
        elif p_code_count >= 1:
            score = 10
            reason = f"{p_code_count} Code P buy (WEAK)"
        else:
            score = 0
            reason = "No recent buys"
        
        return score, reason
        
    except Exception as e:
        return 0, f"Error: {str(e)[:30]}"

def score_insider_timing(ticker):
    """Score insider timing quality using Paul Allen methodology (0-20 pts)."""
    try:
        # Use insider_track_record from src/research
        from subprocess import run, PIPE
        
        result = run(['python3', 'src/research/insider_track_record.py', ticker], 
                    capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return 10, "Assumed average (no data)"
        
        output = result.stdout
        
        # Look for timing score in output
        if 'timing score:' in output.lower() or 'buy timing:' in output.lower():
            # Extract score (rough parsing)
            import re
            match = re.search(r'(\d+\.?\d*)/100', output)
            if match:
                timing = float(match.group(1))
                
                if timing >= 95:
                    score = 20
                    reason = f"{timing:.1f}/100 (EXCELLENT)"
                elif timing >= 85:
                    score = 15
                    reason = f"{timing:.1f}/100 (GOOD)"
                elif timing >= 70:
                    score = 10
                    reason = f"{timing:.1f}/100 (FAIR)"
                else:
                    score = 5
                    reason = f"{timing:.1f}/100 (POOR)"
                
                return score, reason
        
        # Check if output mentions "EXCELLENT" or similar
        if 'EXCELLENT' in output.upper():
            return 20, "Excellent timing"
        elif 'GOOD' in output.upper():
            return 15, "Good timing"
        
        return 10, "Assumed average timing"
        
    except Exception as e:
        return 10, "Assumed average timing"

def score_cash_runway(ticker):
    """Score cash runway (0-15 pts)."""
    try:
        stock = yf.Ticker(ticker)
        balance_sheet = stock.balance_sheet
        
        if balance_sheet is None or balance_sheet.empty:
            return 0, "No financial data"
        
        # Get cash and quarterly burn
        cash = balance_sheet.loc['Cash And Cash Equivalents'].iloc[0] if 'Cash And Cash Equivalents' in balance_sheet.index else 0
        
        # Estimate quarterly burn (rough)
        income = stock.income_stmt
        if income is not None and not income.empty:
            net_income = income.loc['Net Income'].iloc[0] if 'Net Income' in income.index else 0
            quarterly_burn = abs(net_income) / 4 if net_income < 0 else 0
        else:
            quarterly_burn = 1  # Assume some burn
        
        if quarterly_burn > 0:
            quarters_runway = cash / quarterly_burn
        else:
            quarters_runway = 100  # Assume long runway if profitable
        
        # Score
        if quarters_runway >= 20:
            score = 15
            reason = f"{quarters_runway:.0f}+ months (SAFE)"
        elif quarters_runway >= 12:
            score = 12
            reason = f"{quarters_runway:.0f} months (GOOD)"
        elif quarters_runway >= 6:
            score = 8
            reason = f"{quarters_runway:.0f} months (FAIR)"
        else:
            score = 3
            reason = f"{quarters_runway:.0f} months (RISKY)"
        
        return score, reason
        
    except Exception as e:
        return 5, "Assumed moderate"

def score_institutional_backing(ticker):
    """Score institutional backing (0-10 pts)."""
    try:
        stock = yf.Ticker(ticker)
        holders = stock.institutional_holders
        
        if holders is None or holders.empty:
            return 0, "No institutional data"
        
        # Get total institutional ownership
        total_pct = holders['% Out'].sum()
        
        if total_pct >= 50:
            score = 10
            reason = f"{total_pct:.0f}% institutional (HIGH)"
        elif total_pct >= 30:
            score = 7
            reason = f"{total_pct:.0f}% institutional (GOOD)"
        elif total_pct >= 15:
            score = 5
            reason = f"{total_pct:.0f}% institutional (MODERATE)"
        else:
            score = 2
            reason = f"{total_pct:.0f}% institutional (LOW)"
        
        return score, reason
        
    except Exception as e:
        return 3, "Assumed low"

def score_technical_setup(ticker):
    """Score technical setup - price vs 52w high/low (0-10 pts)."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1y')
        
        if hist.empty:
            return 5, "No price data"
        
        current = hist['Close'].iloc[-1]
        high_52w = hist['High'].max()
        low_52w = hist['Low'].min()
        
        # Calculate position in range
        range_size = high_52w - low_52w
        position = (current - low_52w) / range_size if range_size > 0 else 0.5
        
        # Score - prefer wounded prey (low in range)
        if position <= 0.15:
            score = 10
            reason = f"Near 52w low (WOUNDED PREY)"
        elif position <= 0.30:
            score = 8
            reason = f"Low in range (GOOD)"
        elif position <= 0.50:
            score = 5
            reason = f"Mid-range (NEUTRAL)"
        elif position <= 0.80:
            score = 3
            reason = f"High in range (CAUTION)"
        else:
            score = 1
            reason = f"Near 52w high (AVOID)"
        
        return score, reason
        
    except Exception as e:
        return 5, "Neutral"

def score_sector_momentum(ticker):
    """Score sector momentum (0-5 pts)."""
    # Simplified - would need sector mapping
    # For now, check if price is trending up
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1mo')
        
        if hist.empty or len(hist) < 10:
            return 3, "Neutral"
        
        # Check if trending up
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        change_pct = ((end_price - start_price) / start_price) * 100
        
        if change_pct > 10:
            score = 5
            reason = f"+{change_pct:.1f}% momentum (STRONG)"
        elif change_pct > 5:
            score = 4
            reason = f"+{change_pct:.1f}% momentum (GOOD)"
        elif change_pct > 0:
            score = 3
            reason = f"+{change_pct:.1f}% momentum (FLAT)"
        elif change_pct > -10:
            score = 2
            reason = f"{change_pct:.1f}% momentum (WEAK)"
        else:
            score = 1
            reason = f"{change_pct:.1f}% momentum (FALLING)"
        
        return score, reason
        
    except Exception as e:
        return 3, "Neutral"

def calculate_conviction_score(ticker):
    """Calculate total conviction score for ticker."""
    print(f"\n🔍 Analyzing {ticker}...")
    
    scores = {}
    
    # Insider cluster (0-40)
    score, reason = score_insider_cluster(ticker)
    scores['insider_cluster'] = {'score': score, 'reason': reason}
    print(f"   Insider cluster: {score}/40 - {reason}")
    
    # Insider timing (0-20)
    score, reason = score_insider_timing(ticker)
    scores['insider_timing'] = {'score': score, 'reason': reason}
    print(f"   Insider timing: {score}/20 - {reason}")
    
    # Cash runway (0-15)
    score, reason = score_cash_runway(ticker)
    scores['cash_runway'] = {'score': score, 'reason': reason}
    print(f"   Cash runway: {score}/15 - {reason}")
    
    # Institutional (0-10)
    score, reason = score_institutional_backing(ticker)
    scores['institutional'] = {'score': score, 'reason': reason}
    print(f"   Institutional: {score}/10 - {reason}")
    
    # Technical (0-10)
    score, reason = score_technical_setup(ticker)
    scores['technical'] = {'score': score, 'reason': reason}
    print(f"   Technical: {score}/10 - {reason}")
    
    # Sector (0-5)
    score, reason = score_sector_momentum(ticker)
    scores['sector'] = {'score': score, 'reason': reason}
    print(f"   Sector: {score}/5 - {reason}")
    
    # Total
    total = sum([s['score'] for s in scores.values()])
    
    # Conviction level
    if total >= 80:
        conviction = "🟢 EXTREME"
    elif total >= 65:
        conviction = "🟢 HIGH"
    elif total >= 50:
        conviction = "🟡 MODERATE"
    elif total >= 35:
        conviction = "🟡 LOW"
    else:
        conviction = "🔴 AVOID"
    
    print(f"   TOTAL: {total}/100 - {conviction}")
    
    return {
        'ticker': ticker,
        'total_score': total,
        'conviction': conviction,
        'breakdown': scores
    }

def rank_watchlist(watchlist):
    """Rank entire watchlist by conviction."""
    print("🐺 CONVICTION RANKER")
    print("=" * 70)
    print(f"\nAnalyzing {len(watchlist)} tickers...\n")
    
    results = []
    
    for ticker in watchlist:
        try:
            result = calculate_conviction_score(ticker)
            results.append(result)
        except Exception as e:
            print(f"   ❌ Failed to analyze {ticker}: {e}")
            results.append({
                'ticker': ticker,
                'total_score': 0,
                'conviction': '🔴 ERROR',
                'breakdown': {}
            })
    
    # Sort by score
    results.sort(key=lambda x: x['total_score'], reverse=True)
    
    # Display ranking
    print("\n" + "=" * 70)
    print("📊 CONVICTION RANKING")
    print("=" * 70)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['ticker']}: {result['total_score']}/100 - {result['conviction']}")
    
    return results

def main():
    """Main execution."""
    # Load watchlist from config
    try:
        with open('wolf_den_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        watchlist = [config['watchlist']['primary']] + config['watchlist']['backup'] + config['watchlist']['positions']
    except:
        # Fallback watchlist
        watchlist = ['AISP', 'SOUN', 'LUNR', 'BBAI', 'SMR']
    
    # Add some extras for Friday investigation
    extended_watchlist = watchlist + ['IONQ', 'PLUG', 'HIMS', 'KVUE']
    
    results = rank_watchlist(extended_watchlist)
    
    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'watchlist': extended_watchlist,
        'rankings': results
    }
    
    with open('logs/conviction_rankings_latest.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Rankings saved to logs/conviction_rankings_latest.json")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
