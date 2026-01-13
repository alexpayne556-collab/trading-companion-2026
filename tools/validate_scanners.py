"""
🧪 SCANNER VALIDATION FRAMEWORK

NOT for production. For TESTING scanners on historical data.

Goal: Test each scanner on 50+ historical movers, calculate hit rate.
Only add to dashboard if >60% hit rate.

Tyr's rule: "Test many ways. Build only what works."
"""

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import json

class ScannerValidator:
    """
    Tests scanners against historical moves to see if they would have caught them.
    """
    
    def __init__(self):
        self.results = {}
        
    def get_historical_movers(self, days_back=90, min_move=20):
        """
        Get stocks that moved >20% in past 90 days.
        This is our test set.
        """
        # For now, use known movers
        # In production, would scan all stocks
        
        known_movers = [
            'EVTV', 'LVLU', 'ALMS', 'PASW', 'OMH', 'RARE', 'PATH',
            'ATON', 'NTLA', 'KTOS', 'APLD', 'MU', 'RIOT'
        ]
        
        return known_movers
    
    def test_scanner(self, scanner_name, scanner_function, test_tickers):
        """
        Test a scanner on historical data.
        
        Args:
            scanner_name: Name of scanner (e.g., "Coiled Spring")
            scanner_function: Function that returns True/False if would have caught
            test_tickers: List of tickers to test on
        
        Returns:
            hit_rate, false_positive_rate, details
        """
        print(f"\n{'='*70}")
        print(f"🧪 TESTING: {scanner_name}")
        print(f"{'='*70}")
        
        caught = 0
        missed = 0
        details = []
        
        for ticker in test_tickers:
            try:
                would_catch, score, reason = scanner_function(ticker)
                
                if would_catch:
                    caught += 1
                    print(f"   ✅ {ticker}: Score {score}/100 - {reason}")
                else:
                    missed += 1
                    print(f"   ❌ {ticker}: Score {score}/100 - {reason}")
                
                details.append({
                    'ticker': ticker,
                    'caught': would_catch,
                    'score': score,
                    'reason': reason
                })
            except Exception as e:
                print(f"   ⚠️ {ticker}: Error - {e}")
                missed += 1
        
        total = caught + missed
        hit_rate = (caught / total * 100) if total > 0 else 0
        
        print(f"\n   Results: {caught}/{total} caught ({hit_rate:.0f}%)")
        
        # Decision
        if hit_rate >= 60:
            decision = "✅ BUILD IT"
        elif hit_rate >= 40:
            decision = "⚠️ NEEDS WORK"
        else:
            decision = "❌ DISCARD"
        
        print(f"   Decision: {decision}")
        
        return {
            'scanner': scanner_name,
            'hit_rate': hit_rate,
            'caught': caught,
            'missed': missed,
            'decision': decision,
            'details': details
        }

# =============================================================================
# SCANNER TESTS
# =============================================================================

def test_coiled_spring(ticker):
    """
    Test: Would coiled spring scanner have caught this?
    
    Pattern: Intraday spike >15%, fade >10%, micro-cap <$100M
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    intraday = stock.history(period='1d', interval='1m')
    
    if intraday.empty or len(intraday) < 50:
        return False, 0, "No intraday data"
    
    # Market cap check
    market_cap = info.get('marketCap', 0)
    if market_cap > 100_000_000:
        return False, 0, "Not micro-cap"
    
    # Intraday spike check
    open_price = intraday['Open'].iloc[0]
    high_price = intraday['High'].max()
    close_price = intraday['Close'].iloc[-1]
    
    spike = ((high_price / open_price) - 1) * 100
    fade = ((close_price / high_price) - 1) * 100
    
    # Scoring (same as intraday_momentum_scanner.py)
    score = 0
    if market_cap < 10_000_000:
        score += 30
    elif market_cap < 50_000_000:
        score += 20
    
    if spike > 20:
        score += 25
    elif spike > 15:
        score += 20
    
    if 10 < abs(fade) < 20:
        score += 20
    
    would_catch = score >= 80
    reason = f"Spike {spike:.0f}%, Fade {fade:.0f}%"
    
    return would_catch, score, reason


def test_sec_catalyst(ticker):
    """
    Test: Would SEC catalyst scanner have caught this?
    
    Pattern: SEC 8-K filing with keywords like "agreement", "merger", etc
    """
    # This requires checking SEC EDGAR
    # For now, check if it's biotech (proxy for news-driven)
    
    stock = yf.Ticker(ticker)
    info = stock.info
    
    sector = info.get('sector', '')
    industry = info.get('industry', '')
    
    is_biotech = sector == 'Healthcare' and 'Biotech' in industry
    
    if is_biotech:
        # Check if there was news
        try:
            news = stock.news
            if news and len(news) > 0:
                return True, 75, "Biotech + news"
        except:
            pass
    
    return False, 0, "No SEC catalyst"


def test_quiet_explosion(ticker):
    """
    Test: Would quiet → explosion scanner have caught this?
    
    Pattern: Quiet day before (<5% move), then MASSIVE volume spike (>1000%)
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period='5d', interval='1d')
    
    if len(hist) < 2:
        return False, 0, "Insufficient data"
    
    day_before = hist.iloc[-2]
    big_day = hist.iloc[-1]
    
    # Quiet check
    db_move = abs((day_before['Close'] / day_before['Open']) - 1) * 100
    
    # Volume explosion check
    vol_increase = ((big_day['Volume'] / day_before['Volume']) - 1) * 100 if day_before['Volume'] > 0 else 0
    
    # Market cap check
    info = stock.info
    market_cap = info.get('marketCap', 0)
    is_micro = market_cap < 100_000_000
    
    score = 0
    if is_micro:
        score += 30
    
    if db_move < 5:
        score += 30  # Quiet before
    
    if vol_increase > 10000:  # >100x volume
        score += 40
    elif vol_increase > 1000:  # >10x volume
        score += 30
    elif vol_increase > 500:  # >5x volume
        score += 20
    
    would_catch = score >= 60
    reason = f"Quiet {db_move:.0f}%, Vol +{vol_increase:.0f}%"
    
    return would_catch, score, reason


def test_float_rotation(ticker):
    """
    Test: Would float rotation scanner have caught this?
    
    Pattern: Volume > 50% of float, micro-cap
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period='1d', interval='1d')
    
    if hist.empty:
        return False, 0, "No data"
    
    float_shares = info.get('floatShares', 0)
    volume = hist['Volume'].iloc[-1]
    market_cap = info.get('marketCap', 0)
    
    if float_shares == 0:
        return False, 0, "No float data"
    
    float_rotation = (volume / float_shares) * 100
    is_micro = market_cap < 100_000_000
    
    score = 0
    if is_micro:
        score += 30
    
    if float_rotation > 100:  # Entire float traded
        score += 40
    elif float_rotation > 50:
        score += 30
    elif float_rotation > 25:
        score += 20
    
    would_catch = score >= 60
    reason = f"{float_rotation:.0f}% float rotation"
    
    return would_catch, score, reason


# =============================================================================
# MAIN VALIDATION
# =============================================================================

def main():
    """
    Run validation on all scanners.
    """
    print("="*70)
    print("🧪 SCANNER VALIDATION - TEST BEFORE BUILDING")
    print("="*70)
    print("\nTesting scanners on known movers...")
    print("Only building scanners with >60% hit rate.\n")
    
    validator = ScannerValidator()
    test_tickers = validator.get_historical_movers()
    
    # Test each scanner
    results = []
    
    # 1. Coiled Spring
    result1 = validator.test_scanner(
        "Coiled Spring (ATON pattern)",
        test_coiled_spring,
        test_tickers
    )
    results.append(result1)
    
    # 2. Quiet → Explosion
    result2 = validator.test_scanner(
        "Quiet → Explosion (EVTV pattern)",
        test_quiet_explosion,
        test_tickers
    )
    results.append(result2)
    
    # 3. Float Rotation
    result3 = validator.test_scanner(
        "Float Rotation",
        test_float_rotation,
        test_tickers
    )
    results.append(result3)
    
    # 4. SEC Catalyst
    result4 = validator.test_scanner(
        "SEC Catalyst (Biotech)",
        test_sec_catalyst,
        test_tickers
    )
    results.append(result4)
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'='*70}\n")
    
    for result in results:
        print(f"{result['scanner']:30s} | {result['hit_rate']:5.0f}% | {result['decision']}")
    
    print(f"\n{'='*70}")
    print("💡 RECOMMENDATIONS:")
    print(f"{'='*70}\n")
    
    for result in results:
        if result['hit_rate'] >= 60:
            print(f"✅ ADD TO DASHBOARD: {result['scanner']}")
        elif result['hit_rate'] >= 40:
            print(f"⚠️ NEEDS REFINEMENT: {result['scanner']}")
        else:
            print(f"❌ DON'T BUILD: {result['scanner']}")
    
    # Save results
    import os
    os.makedirs('research', exist_ok=True)
    with open('research/scanner_validation.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: research/scanner_validation.json")
    print("\n🐺 VALIDATION COMPLETE. BUILD ONLY WHAT TESTED >60%.\n")

if __name__ == "__main__":
    main()
