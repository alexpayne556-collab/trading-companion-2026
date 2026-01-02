#!/usr/bin/env python3
"""
🐺 FAST CONVICTION SCANNER - Uses cached SEC data

Pre-loaded conviction scores for watchlist.
Updates daily via background scan.

Author: Brokkr
Date: January 2, 2026
"""

import json
from datetime import datetime
import yfinance as yf

# HARD-CODED CONVICTION SCORES (From our research)
# Update these after running full SEC scans

CONVICTION_DATA = {
    'AISP': {
        'insider_cluster': 40,  # 10 Code P buys
        'insider_timing': 20,    # Paul Allen 98.2/100
        'insider_reason_cluster': '10 Code P buys (EXTREME)',
        'insider_reason_timing': '98.2/100 (EXCELLENT)',
        'cash_runway_months': 15,  # $15.5M, moderate burn
        'notes': '9 insider cluster, CEO $192K, Paul Allen $274K Dec 29'
    },
    'SOUN': {
        'insider_cluster': 0,
        'insider_timing': 10,
        'insider_reason_cluster': 'No recent buys',
        'insider_reason_timing': 'Assumed average',
        'cash_runway_months': 18,
        'notes': 'Wounded prey, no insider signal'
    },
    'LUNR': {
        'insider_cluster': 20,  # 2 Code P buys
        'insider_timing': 15,
        'insider_reason_cluster': '2 Code P buys (MODERATE)',
        'insider_reason_timing': 'Good timing',
        'cash_runway_months': 12,
        'notes': 'IM-3 catalyst, moderate insider support'
    },
    'BBAI': {
        'insider_cluster': 0,
        'insider_timing': 10,
        'insider_reason_cluster': 'No recent buys',
        'insider_reason_timing': 'Assumed average',
        'cash_runway_months': 8,
        'notes': 'Defense AI, no insider signal'
    },
    'SMR': {
        'insider_cluster': 0,
        'insider_timing': 10,
        'insider_reason_cluster': 'No recent buys',
        'insider_reason_timing': 'Assumed average',
        'cash_runway_months': 24,
        'notes': 'Nuclear sector, wounded prey'
    },
    'IONQ': {
        'insider_cluster': 10,
        'insider_timing': 10,
        'insider_reason_cluster': '1 Code P buy (WEAK)',
        'insider_reason_timing': 'Assumed average',
        'cash_runway_months': 18,
        'notes': 'Quantum sector, moderate insider'
    },
    'PLUG': {
        'insider_cluster': 10,
        'insider_timing': 10,
        'insider_reason_cluster': '1 Code P buy (WEAK)',
        'insider_reason_timing': 'Assumed average',
        'cash_runway_months': 6,
        'notes': 'Hydrogen sector, $87K Dec 15 buy'
    },
    'HIMS': {
        'insider_cluster': 0,
        'insider_timing': 10,
        'insider_reason_cluster': 'No recent buys',
        'insider_reason_timing': 'Assumed average',
        'cash_runway_months': 36,
        'notes': 'Healthcare, no insider signal'
    },
    'KVUE': {
        'insider_cluster': 35,  # $111M institutional conviction
        'insider_timing': 15,
        'insider_reason_cluster': 'Massive institutional buying',
        'insider_reason_timing': 'Good timing',
        'cash_runway_months': 60,
        'notes': 'Consumer health, too expensive for us'
    }
}

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
        
        range_size = high_52w - low_52w
        position = (current - low_52w) / range_size if range_size > 0 else 0.5
        
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
    except:
        return 5, "Neutral"

def score_sector_momentum(ticker):
    """Score sector momentum (0-5 pts)."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1mo')
        
        if hist.empty or len(hist) < 10:
            return 3, "Neutral"
        
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
    except:
        return 3, "Neutral"

def score_institutional_backing(ticker):
    """Score institutional backing (0-10 pts)."""
    try:
        stock = yf.Ticker(ticker)
        holders = stock.institutional_holders
        
        if holders is None or holders.empty:
            return 3, "No institutional data"
        
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
            score = 3
            reason = f"{total_pct:.0f}% institutional (LOW)"
        
        return score, reason
    except:
        return 3, "Assumed low"

def score_cash_runway(cash_months):
    """Score cash runway from pre-loaded data (0-15 pts)."""
    if cash_months >= 24:
        return 15, f"{cash_months}+ months (SAFE)"
    elif cash_months >= 15:
        return 12, f"{cash_months} months (GOOD)"
    elif cash_months >= 10:
        return 8, f"{cash_months} months (FAIR)"
    else:
        return 3, f"{cash_months} months (RISKY)"

def calculate_fast_conviction(ticker):
    """Calculate conviction using pre-loaded insider data."""
    print(f"\n🔍 Analyzing {ticker}...")
    
    # Get pre-loaded insider data
    ticker_data = CONVICTION_DATA.get(ticker, {
        'insider_cluster': 0,
        'insider_timing': 10,
        'insider_reason_cluster': 'No data',
        'insider_reason_timing': 'Assumed average',
        'cash_runway_months': 12,
        'notes': 'No pre-loaded data'
    })
    
    scores = {}
    
    # Insider cluster (pre-loaded)
    scores['insider_cluster'] = {
        'score': ticker_data['insider_cluster'],
        'reason': ticker_data['insider_reason_cluster']
    }
    print(f"   Insider cluster: {ticker_data['insider_cluster']}/40 - {ticker_data['insider_reason_cluster']}")
    
    # Insider timing (pre-loaded)
    scores['insider_timing'] = {
        'score': ticker_data['insider_timing'],
        'reason': ticker_data['insider_reason_timing']
    }
    print(f"   Insider timing: {ticker_data['insider_timing']}/20 - {ticker_data['insider_reason_timing']}")
    
    # Cash runway (pre-loaded)
    score, reason = score_cash_runway(ticker_data['cash_runway_months'])
    scores['cash_runway'] = {'score': score, 'reason': reason}
    print(f"   Cash runway: {score}/15 - {reason}")
    
    # Institutional (live)
    score, reason = score_institutional_backing(ticker)
    scores['institutional'] = {'score': score, 'reason': reason}
    print(f"   Institutional: {score}/10 - {reason}")
    
    # Technical (live)
    score, reason = score_technical_setup(ticker)
    scores['technical'] = {'score': score, 'reason': reason}
    print(f"   Technical: {score}/10 - {reason}")
    
    # Sector (live)
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
    print(f"   📝 Notes: {ticker_data['notes']}")
    
    return {
        'ticker': ticker,
        'total_score': total,
        'conviction': conviction,
        'breakdown': scores,
        'notes': ticker_data['notes']
    }

def main():
    """Main execution."""
    import yaml
    
    # Load watchlist
    try:
        with open('wolf_den_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        watchlist = [config['watchlist']['primary']] + config['watchlist']['backup'] + config['watchlist']['positions']
    except:
        watchlist = ['AISP', 'SOUN', 'LUNR', 'BBAI', 'SMR']
    
    # Add extras
    extended_watchlist = watchlist + ['IONQ', 'PLUG', 'HIMS', 'KVUE']
    
    print("🐺 FAST CONVICTION SCANNER")
    print("=" * 70)
    print(f"\nAnalyzing {len(extended_watchlist)} tickers...\n")
    
    results = []
    for ticker in extended_watchlist:
        try:
            result = calculate_fast_conviction(ticker)
            results.append(result)
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append({
                'ticker': ticker,
                'total_score': 0,
                'conviction': '🔴 ERROR',
                'breakdown': {},
                'notes': str(e)
            })
    
    # Sort
    results.sort(key=lambda x: x['total_score'], reverse=True)
    
    # Display
    print("\n" + "=" * 70)
    print("📊 CONVICTION RANKING")
    print("=" * 70)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['ticker']}: {result['total_score']}/100 - {result['conviction']}")
        if result.get('notes'):
            print(f"   💡 {result['notes']}")
    
    # Save
    output = {
        'timestamp': datetime.now().isoformat(),
        'watchlist': extended_watchlist,
        'rankings': results,
        'data_source': 'Pre-loaded from SEC research + live yfinance'
    }
    
    with open('logs/conviction_rankings_latest.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Rankings saved to logs/conviction_rankings_latest.json")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
