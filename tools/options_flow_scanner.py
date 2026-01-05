#!/usr/bin/env python3
"""
OPTIONS FLOW SCANNER - PRODUCTION VERSION

Catches unusual options activity signaling smart money positioning.
Scrapes Barchart for free data (15-30 min delay acceptable for overnight holds).

SUCCESS CRITERIA: Flag unusual activity 24-48h BEFORE 10%+ moves, 30%+ hit rate

Usage:
    python3 options_flow_scanner.py              # Daily scan
    python3 options_flow_scanner.py --sunday     # Sunday scan for Monday
"""

import requests
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime, timedelta
import json
from pathlib import Path
import argparse
import time
import re

# Tyr's watchlist
WATCHLIST = [
    # Current positions
    'UUUU', 'USAR', 'AISP',
    # Nuclear
    'UEC', 'CCJ', 'SMR', 'LEU', 'DNN', 'NXE',
    # Quantum/Robotics/CES
    'RR', 'QBTS', 'QUBT', 'RGTI', 'IONQ',
    # AI Infrastructure
    'SMCI', 'CRDO', 'VRT',
    # Space
    'RDW', 'RKLB', 'LUNR', 'ASTS',
]

class OptionsFlowScanner:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    def scrape_barchart_unusual_options(self):
        """Scrape Barchart unusual options page"""
        try:
            url = "https://www.barchart.com/options/unusual-activity/stocks"
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                print(f"   ⚠️  Barchart returned {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the data table
            table = soup.find('table', class_='bc-table')
            if not table:
                print("   ⚠️  Could not find Barchart data table")
                return []
            
            unusual_options = []
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) < 10:
                    continue
                
                try:
                    ticker = cells[0].text.strip()
                    
                    # Only process watchlist tickers
                    if ticker not in WATCHLIST:
                        continue
                    
                    option_type = cells[1].text.strip()  # Call or Put
                    strike = cells[2].text.strip()
                    expiry = cells[3].text.strip()
                    volume = int(cells[5].text.strip().replace(',', ''))
                    open_interest = int(cells[6].text.strip().replace(',', ''))
                    vol_oi_ratio = volume / open_interest if open_interest > 0 else 0
                    
                    unusual_options.append({
                        'ticker': ticker,
                        'type': option_type,
                        'strike': strike,
                        'expiry': expiry,
                        'volume': volume,
                        'open_interest': open_interest,
                        'vol_oi_ratio': vol_oi_ratio
                    })
                    
                except (ValueError, AttributeError, IndexError) as e:
                    continue
            
            return unusual_options
            
        except Exception as e:
            print(f"   ⚠️  Error scraping Barchart: {str(e)}")
            return []
    
    def get_option_details(self, ticker, strike, expiry, option_type):
        """Get additional details about an option"""
        try:
            stock = yf.Ticker(ticker)
            current_price = stock.info.get('currentPrice') or stock.info.get('regularMarketPrice')
            
            if not current_price:
                return None
            
            # Parse strike price
            strike_price = float(re.sub(r'[^\d.]', '', strike))
            
            # Calculate strike vs price
            if option_type.upper() == 'CALL':
                strike_vs_price = ((strike_price - current_price) / current_price) * 100
                otm = strike_price > current_price
            else:  # PUT
                strike_vs_price = ((current_price - strike_price) / current_price) * 100
                otm = strike_price < current_price
            
            # Parse expiry to get days
            try:
                expiry_date = datetime.strptime(expiry, '%m/%d/%y')
                days_to_expiry = (expiry_date - datetime.now()).days
            except:
                days_to_expiry = 0
            
            return {
                'current_price': current_price,
                'strike_price': strike_price,
                'strike_vs_price_pct': strike_vs_price,
                'otm': otm,
                'days_to_expiry': days_to_expiry
            }
            
        except Exception as e:
            return None
    
    def check_block_trades(self, volume):
        """Detect large block trades (institutional)"""
        if volume >= 1000:
            return "Large institutional (1000+ contracts)"
        elif volume >= 500:
            return "Medium institutional (500+ contracts)"
        elif volume >= 100:
            return "Small institutional (100+ contracts)"
        else:
            return "Retail volume"
    
    def score_unusual_activity(self, option_data, details):
        """Score the unusual activity 0-100"""
        score = 0
        reasons = []
        
        # Volume vs OI ratio (max 40 points)
        if option_data['vol_oi_ratio'] >= 10:
            score += 40
            reasons.append("Volume 10x+ open interest (NEW positions)")
        elif option_data['vol_oi_ratio'] >= 5:
            score += 30
            reasons.append("Volume 5x+ open interest")
        elif option_data['vol_oi_ratio'] >= 2:
            score += 20
            reasons.append("Volume 2x+ open interest")
        
        if not details:
            return score, reasons
        
        # Days to expiry (max 20 points)
        if details['days_to_expiry'] <= 7:
            score += 20
            reasons.append("Expires in <7 days (imminent move expected)")
        elif details['days_to_expiry'] <= 14:
            score += 15
            reasons.append("Expires in <14 days")
        
        # OTM strikes (max 20 points)
        if details['otm']:
            if abs(details['strike_vs_price_pct']) >= 20:
                score += 20
                reasons.append(f"{abs(details['strike_vs_price_pct']):.1f}% OTM (leveraged bet)")
            elif abs(details['strike_vs_price_pct']) >= 10:
                score += 15
                reasons.append(f"{abs(details['strike_vs_price_pct']):.1f}% OTM")
        
        # Volume threshold (max 20 points)
        if option_data['volume'] >= 1000:
            score += 20
            reasons.append("1000+ contracts (institutional)")
        elif option_data['volume'] >= 500:
            score += 15
            reasons.append("500+ contracts")
        elif option_data['volume'] >= 100:
            score += 10
            reasons.append("100+ contracts")
        
        return score, reasons
    
    def scan(self):
        """Run the scan"""
        print(f"\n📊 OPTIONS FLOW SCANNER - PRODUCTION VERSION")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"   Scanning unusual options activity on {len(WATCHLIST)} watchlist tickers")
        print(f"   Data source: Barchart (15-30 min delay)")
        print("=" * 80)
        
        print("\n   Scraping Barchart unusual options...", end=' ', flush=True)
        unusual_options = self.scrape_barchart_unusual_options()
        print(f"✓ Found {len(unusual_options)} unusual options on watchlist")
        
        if not unusual_options:
            return []
        
        # Enrich with details and scoring
        print("   Analyzing activity...", end='', flush=True)
        scored_options = []
        
        for option in unusual_options:
            details = self.get_option_details(
                option['ticker'],
                option['strike'],
                option['expiry'],
                option['type']
            )
            
            score, reasons = self.score_unusual_activity(option, details)
            
            if score >= 50:  # Only alert on significant activity
                option['score'] = score
                option['reasons'] = reasons
                option['details'] = details
                option['block_trade_size'] = self.check_block_trades(option['volume'])
                scored_options.append(option)
            
            time.sleep(0.2)
        
        print(f" ✓ Found {len(scored_options)} high-conviction signals")
        
        return scored_options
    
    def display_results(self, scored_options):
        """Display results"""
        if not scored_options:
            print("\n📊 No unusual options activity detected on watchlist.")
            print("\n🐺 This could mean:")
            print("   • No smart money positioning on our tickers right now")
            print("   • Activity happened earlier (check Barchart manually)")
            print("   • Our tickers aren't hot this week")
            return
        
        # Sort by score
        scored_options.sort(key=lambda x: x['score'], reverse=True)
        
        # Separate calls and puts
        calls = [o for o in scored_options if o['type'].upper() == 'CALL']
        puts = [o for o in scored_options if o['type'].upper() == 'PUT']
        
        print("\n" + "=" * 80)
        print("🚨 UNUSUAL OPTIONS ACTIVITY DETECTED")
        print("=" * 80)
        
        if calls:
            print("\n🟢 BULLISH SIGNALS (CALLS):")
            print("=" * 80)
            
            for i, option in enumerate(calls, 1):
                details = option.get('details')
                print(f"\n{i}. {option['ticker']} — Score: {option['score']}/100")
                print(f"   Strike: ${option['strike']} | Expiry: {option['expiry']} ({details['days_to_expiry']} days)")
                print(f"   Volume: {option['volume']:,} | OI: {option['open_interest']:,} | Vol/OI: {option['vol_oi_ratio']:.1f}x")
                if details:
                    print(f"   Current: ${details['current_price']:.2f} | Strike vs Price: {details['strike_vs_price_pct']:+.1f}%")
                print(f"   Block Trade: {option['block_trade_size']}")
                print(f"\n   WHY THIS MATTERS:")
                for reason in option['reasons']:
                    print(f"      • {reason}")
                
                # Interpretation
                if option['score'] >= 80:
                    print(f"\n   🔥 INTERPRETATION: STRONG bullish signal. Smart money expecting significant upside.")
                elif option['score'] >= 70:
                    print(f"\n   ⚡ INTERPRETATION: GOOD bullish signal. Watch for confirmation.")
                else:
                    print(f"\n   ⚠️  INTERPRETATION: MODERATE bullish signal. Needs validation.")
        
        if puts:
            print("\n🔴 BEARISH SIGNALS (PUTS):")
            print("=" * 80)
            
            for i, option in enumerate(puts, 1):
                details = option.get('details')
                print(f"\n{i}. {option['ticker']} — Score: {option['score']}/100")
                print(f"   Strike: ${option['strike']} | Expiry: {option['expiry']} ({details['days_to_expiry']} days)")
                print(f"   Volume: {option['volume']:,} | OI: {option['open_interest']:,} | Vol/OI: {option['vol_oi_ratio']:.1f}x")
                if details:
                    print(f"   Current: ${details['current_price']:.2f} | Strike vs Price: {details['strike_vs_price_pct']:+.1f}%")
                print(f"   Block Trade: {option['block_trade_size']}")
                print(f"\n   WHY THIS MATTERS:")
                for reason in option['reasons']:
                    print(f"      • {reason}")
                
                # Interpretation
                if option['score'] >= 80:
                    print(f"\n   🔥 INTERPRETATION: STRONG bearish signal or hedging.")
                elif option['score'] >= 70:
                    print(f"\n   ⚡ INTERPRETATION: GOOD bearish signal. Watch for confirmation.")
                else:
                    print(f"\n   ⚠️  INTERPRETATION: MODERATE - could be hedging, not pure bearish.")
        
        print("\n" + "=" * 80)
        print("🐺 WOLF'S READ")
        print("=" * 80)
        
        if calls and not puts:
            print("\n   🟢 BULLISH FLOW ONLY - Smart money betting on upside")
        elif puts and not calls:
            print("\n   🔴 BEARISH FLOW ONLY - Either bearish or heavy hedging")
        elif calls and puts:
            print("\n   ⚪ MIXED SIGNALS - Could be complex positioning or uncertainty")
        
        print("\n   🎯 WHAT TO DO:")
        print("      • Score 80+ = STRONG signal, worth investigating")
        print("      • Score 70-79 = GOOD signal, watch for confirmation")
        print("      • Score 50-69 = MODERATE, needs validation")
        print("      • Check ATP for price action confirmation")
        print("      • Look for catalyst (earnings, CES, contracts)")
        
        print("\n   ⏰ TIMING:")
        print("      • Data is 15-30 min delayed (acceptable for overnight holds)")
        print("      • Options flow leads price action 24-48 hours often")
        print("      • Best used for swing trade setups, not day trades")
    
    def save_results(self, scored_options):
        """Save results"""
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        output_file = log_dir / f"options_flow_{datetime.now().strftime('%Y-%m-%d_%H%M')}.json"
        
        # Convert for JSON serialization
        for option in scored_options:
            if option.get('details'):
                option['details'] = {k: float(v) if isinstance(v, (int, float)) else v 
                                   for k, v in option['details'].items()}
        
        with open(output_file, 'w') as f:
            json.dump({
                'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'results': scored_options
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Options Flow Scanner - Production Version')
    parser.add_argument('--sunday', action='store_true', help='Sunday scan for Monday positioning')
    
    args = parser.parse_args()
    
    if args.sunday:
        print("\n📅 SUNDAY SCAN MODE - Analyzing Thursday/Friday options activity for Monday setups")
    
    scanner = OptionsFlowScanner()
    scored_options = scanner.scan()
    scanner.display_results(scored_options)
    
    if scored_options:
        scanner.save_results(scored_options)
    
    print("\n🐺 AWOOOO! Options flow scan complete.\n")

if __name__ == '__main__':
    main()
