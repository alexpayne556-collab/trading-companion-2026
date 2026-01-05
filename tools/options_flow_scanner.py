#!/usr/bin/env python3
"""
OPTIONS FLOW SCANNER - PRODUCTION VERSION

Catches unusual options activity signaling smart money positioning.
Uses Yahoo Finance for FREE real-time options chains (no Barchart scraping).

SUCCESS CRITERIA: 30%+ hit rate on 10%+ moves within 3 days.

Scoring (0-100):
• Volume/OI ratio (max 40): ≥10x = 40pts, ≥5x = 30pts, ≥2x = 20pts
• Days to expiry (max 20): ≤7 days = 20pts, ≤14 days = 15pts
• OTM strikes (max 20): ≥20% OTM = 20pts, ≥10% = 15pts
• Volume threshold (max 20): ≥1000 = 20pts, ≥500 = 15pts, ≥100 = 10pts

Usage:
    python3 options_flow_scanner.py
    python3 options_flow_scanner.py --score 60  # Higher threshold
"""

import yfinance as yf
from datetime import datetime, timedelta
import json
from pathlib import Path
import argparse
import time
import pandas as pd

# Tyr's watchlist
WATCHLIST = [
    'UUUU', 'USAR', 'AISP',
    'UEC', 'CCJ', 'SMR', 'LEU', 'DNN', 'NXE',
    'RR', 'QBTS', 'QUBT', 'RGTI', 'IONQ',
    'SMCI', 'CRDO', 'VRT',
    'RDW', 'RKLB', 'LUNR', 'ASTS',
]

class OptionsFlowScanner:
    def __init__(self, min_score=50):
        self.min_score = min_score
    
    def get_unusual_options(self, ticker):
        """Get unusual options from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get current price
            info = stock.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            if not current_price:
                return []
            
            # Get all expiration dates
            expirations = stock.options
            if not expirations:
                return []
            
            unusual_options = []
            
            # Check near-term expirations only (≤14 days)
            now = datetime.now()
            for exp_date_str in expirations[:4]:  # First 4 expirations
                try:
                    exp_date = datetime.strptime(exp_date_str, '%Y-%m-%d')
                    days_to_expiry = (exp_date - now).days
                    
                    if days_to_expiry > 14:
                        continue  # Too far out
                    
                    # Get options chain
                    options_chain = stock.option_chain(exp_date_str)
                    
                    # Check calls
                    calls = options_chain.calls
                    for _, row in calls.iterrows():
                        volume = row.get('volume', 0)
                        oi = row.get('openInterest', 0)
                        strike = row.get('strike', 0)
                        
                        if volume == 0 or oi == 0 or strike == 0:
                            continue
                        
                        # Calculate metrics
                        vol_oi_ratio = volume / oi if oi > 0 else 0
                        strike_vs_price_pct = ((strike - current_price) / current_price) * 100
                        
                        # Score this option
                        score, reasons = self.score_option(
                            volume, oi, vol_oi_ratio, days_to_expiry,
                            strike_vs_price_pct, 'CALL'
                        )
                        
                        if score >= self.min_score:
                            unusual_options.append({
                                'ticker': ticker,
                                'type': 'CALL',
                                'strike': strike,
                                'expiry': exp_date_str,
                                'days_to_expiry': days_to_expiry,
                                'volume': volume,
                                'open_interest': oi,
                                'vol_oi_ratio': vol_oi_ratio,
                                'current_price': current_price,
                                'strike_vs_price_pct': strike_vs_price_pct,
                                'score': score,
                                'reasons': reasons,
                                'block_trade': self.check_block_trade(volume)
                            })
                    
                    # Check puts
                    puts = options_chain.puts
                    for _, row in puts.iterrows():
                        volume = row.get('volume', 0)
                        oi = row.get('openInterest', 0)
                        strike = row.get('strike', 0)
                        
                        if volume == 0 or oi == 0 or strike == 0:
                            continue
                        
                        # Calculate metrics
                        vol_oi_ratio = volume / oi if oi > 0 else 0
                        strike_vs_price_pct = ((current_price - strike) / current_price) * 100  # For puts, OTM is below
                        
                        # Score this option
                        score, reasons = self.score_option(
                            volume, oi, vol_oi_ratio, days_to_expiry,
                            strike_vs_price_pct, 'PUT'
                        )
                        
                        if score >= self.min_score:
                            unusual_options.append({
                                'ticker': ticker,
                                'type': 'PUT',
                                'strike': strike,
                                'expiry': exp_date_str,
                                'days_to_expiry': days_to_expiry,
                                'volume': volume,
                                'open_interest': oi,
                                'vol_oi_ratio': vol_oi_ratio,
                                'current_price': current_price,
                                'strike_vs_price_pct': strike_vs_price_pct,
                                'score': score,
                                'reasons': reasons,
                                'block_trade': self.check_block_trade(volume)
                            })
                
                except Exception as e:
                    continue
            
            return unusual_options
            
        except Exception as e:
            return []
    
    def score_option(self, volume, oi, vol_oi_ratio, days_to_expiry, otm_pct, option_type):
        """Score 0-100 based on conviction signals"""
        score = 0
        reasons = []
        
        # Volume/OI ratio (max 40 pts)
        if vol_oi_ratio >= 10:
            score += 40
            reasons.append(f"Vol/OI {vol_oi_ratio:.1f}x (EXTREME unusual activity)")
        elif vol_oi_ratio >= 5:
            score += 30
            reasons.append(f"Vol/OI {vol_oi_ratio:.1f}x (Very unusual)")
        elif vol_oi_ratio >= 2:
            score += 20
            reasons.append(f"Vol/OI {vol_oi_ratio:.1f}x (Unusual)")
        
        # Days to expiry (max 20 pts) - Near-term = higher conviction
        if days_to_expiry <= 7:
            score += 20
            reasons.append(f"{days_to_expiry} days to expiry (URGENT positioning)")
        elif days_to_expiry <= 14:
            score += 15
            reasons.append(f"{days_to_expiry} days to expiry (Near-term)")
        
        # OTM percentage (max 20 pts) - OTM = directional bet
        if otm_pct >= 20:
            score += 20
            reasons.append(f"{otm_pct:.0f}% OTM (Aggressive bet)")
        elif otm_pct >= 10:
            score += 15
            reasons.append(f"{otm_pct:.0f}% OTM (Directional)")
        elif otm_pct >= 5:
            score += 10
            reasons.append(f"{otm_pct:.0f}% OTM")
        
        # Volume threshold (max 20 pts) - Size matters
        if volume >= 1000:
            score += 20
            reasons.append(f"{volume:,} contracts (Institutional size)")
        elif volume >= 500:
            score += 15
            reasons.append(f"{volume:,} contracts (Large size)")
        elif volume >= 100:
            score += 10
            reasons.append(f"{volume:,} contracts (Medium size)")
        
        return score, reasons
    
    def check_block_trade(self, volume):
        """Categorize block trade size"""
        if volume >= 1000:
            return "LARGE INSTITUTIONAL (1000+)"
        elif volume >= 500:
            return "INSTITUTIONAL (500+)"
        elif volume >= 100:
            return "SIGNIFICANT (100+)"
        else:
            return "RETAIL (<100)"
    
    def scan(self):
        """Scan watchlist for unusual options"""
        print(f"\n🔍 OPTIONS FLOW SCANNER - PRODUCTION VERSION")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"   Scanning {len(WATCHLIST)} tickers")
        print(f"   Data source: Yahoo Finance (real-time)")
        print(f"   Min score: {self.min_score}/100")
        print("=" * 80)
        
        print("\n   Scanning options chains...")
        all_unusual = []
        
        for ticker in WATCHLIST:
            print(f"      {ticker}...", end=' ', flush=True)
            
            unusual = self.get_unusual_options(ticker)
            if unusual:
                all_unusual.extend(unusual)
                print(f"✓ Found {len(unusual)}")
            else:
                print("✓")
            
            time.sleep(0.5)  # Rate limiting
        
        return all_unusual
    
    def display_results(self, results):
        """Display results"""
        if not results:
            print("\n📊 No unusual options activity detected on watchlist.")
            print("\n🐺 This could mean:")
            print("   • No smart money positioning today")
            print("   • Activity happened earlier (check historical data)")
            print("   • Our tickers aren't hot right now")
            print("   • Try lowering --score threshold")
            return
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Separate calls and puts
        calls = [r for r in results if r['type'] == 'CALL']
        puts = [r for r in results if r['type'] == 'PUT']
        
        print("\n" + "=" * 80)
        print("🔥 UNUSUAL OPTIONS ACTIVITY DETECTED")
        print("=" * 80)
        
        if calls:
            print(f"\n📈 BULLISH BETS ({len(calls)} unusual calls):")
            print("=" * 80)
            
            for i, opt in enumerate(calls[:10], 1):  # Top 10
                print(f"\n{i}. {opt['ticker']} ${opt['strike']} CALL | Exp: {opt['expiry']} ({opt['days_to_expiry']}d)")
                print(f"   Score: {opt['score']}/100 | Current: ${opt['current_price']:.2f}")
                print(f"   Volume: {opt['volume']:,} | OI: {opt['open_interest']:,} | Vol/OI: {opt['vol_oi_ratio']:.1f}x")
                print(f"   Block Size: {opt['block_trade']}")
                print(f"   Why:")
                for reason in opt['reasons']:
                    print(f"      • {reason}")
        
        if puts:
            print(f"\n📉 BEARISH BETS ({len(puts)} unusual puts):")
            print("=" * 80)
            
            for i, opt in enumerate(puts[:10], 1):  # Top 10
                print(f"\n{i}. {opt['ticker']} ${opt['strike']} PUT | Exp: {opt['expiry']} ({opt['days_to_expiry']}d)")
                print(f"   Score: {opt['score']}/100 | Current: ${opt['current_price']:.2f}")
                print(f"   Volume: {opt['volume']:,} | OI: {opt['open_interest']:,} | Vol/OI: {opt['vol_oi_ratio']:.1f}x")
                print(f"   Block Size: {opt['block_trade']}")
                print(f"   Why:")
                for reason in opt['reasons']:
                    print(f"      • {reason}")
        
        print("\n" + "=" * 80)
        print("🐺 WOLF'S READ")
        print("=" * 80)
        
        # Top tickers by count
        ticker_counts = {}
        for opt in results:
            ticker = opt['ticker']
            ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1
        
        top_tickers = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)
        
        if top_tickers:
            print(f"\n   🎯 HOT TICKERS (most unusual activity):")
            for ticker, count in top_tickers[:5]:
                ticker_opts = [o for o in results if o['ticker'] == ticker]
                calls_count = len([o for o in ticker_opts if o['type'] == 'CALL'])
                puts_count = len([o for o in ticker_opts if o['type'] == 'PUT'])
                
                if calls_count > puts_count:
                    direction = f"{calls_count} calls vs {puts_count} puts = BULLISH"
                elif puts_count > calls_count:
                    direction = f"{puts_count} puts vs {calls_count} calls = BEARISH"
                else:
                    direction = f"{calls_count} calls, {puts_count} puts = MIXED"
                
                print(f"      • {ticker} - {count} unusual options | {direction}")
        
        # Score 80+ = HIGHEST conviction
        high_conviction = [r for r in results if r['score'] >= 80]
        if high_conviction:
            print(f"\n   🔥 HIGHEST CONVICTION (score 80+):")
            for opt in high_conviction[:5]:
                direction = "🚀 BULLISH" if opt['type'] == 'CALL' else "🔻 BEARISH"
                print(f"      • {opt['ticker']} ${opt['strike']} {opt['type']} | {direction} | Score: {opt['score']}")
        
        print("\n   🎯 WHAT THIS MEANS:")
        print("      • Vol/OI >5x = Someone knows something")
        print("      • <7 days expiry = URGENT positioning (event expected)")
        print("      • OTM strikes = Directional bet, need big move to profit")
        print("      • 1000+ contracts = Institutional money, not retail")
        print("      • Unusual activity 24-48h BEFORE 10%+ moves (our thesis)")
    
    def save_results(self, results):
        """Save to JSON"""
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        output_file = log_dir / f"options_flow_{datetime.now().strftime('%Y-%m-%d_%H%M')}.json"
        
        with open(output_file, 'w') as f:
            json.dump({
                'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'min_score': self.min_score,
                'results': results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Options Flow Scanner - Production Version')
    parser.add_argument('--score', type=int, default=50, help='Minimum score threshold (default: 50)')
    
    args = parser.parse_args()
    
    scanner = OptionsFlowScanner(args.score)
    results = scanner.scan()
    scanner.display_results(results)
    
    if results:
        scanner.save_results(results)
    
    print("\n🐺 AWOOOO! Options flow scan complete.\n")

if __name__ == '__main__':
    main()
