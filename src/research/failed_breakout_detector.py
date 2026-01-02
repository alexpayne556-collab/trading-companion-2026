"""
🐺 FAILED BREAKOUT DETECTOR - Wolf Pack Research Module
Find stocks that hyped, failed, and are resetting with insider support
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path

class FailedBreakoutDetector:
    """Detect stocks that ran hard then failed - ripe for reversal"""
    
    def __init__(self):
        self.data_dir = Path('logs/breakouts')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def detect_failed_breakout(self, ticker, lookback_days=60):
        """
        Detect if stock had a failed breakout attempt
        
        Pattern:
        1. Stock ran +30%+ in short period
        2. Gave most/all of it back
        3. Now consolidating near lows
        
        Returns dict with breakout analysis
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='6mo')
            
            if len(hist) < lookback_days:
                return None
                
            # Find highest high in lookback period
            recent = hist.tail(lookback_days)
            high = recent['High'].max()
            high_date = recent['High'].idxmax()
            
            # Current price
            current = hist['Close'].iloc[-1]
            
            # Low after the high
            after_high = hist[hist.index > high_date]
            if len(after_high) > 0:
                low_after = after_high['Low'].min()
                low_date = after_high['Low'].idxmin()
            else:
                return None
                
            # Calculate moves
            price_at_high_date = hist.loc[high_date]['Close']
            lookback_low = hist.tail(lookback_days * 2)['Low'].min()
            
            run_pct = ((high - lookback_low) / lookback_low) * 100
            retracement_pct = ((high - low_after) / high) * 100
            current_from_low = ((current - low_after) / low_after) * 100
            
            # Failed breakout criteria
            is_failed = (
                run_pct >= 30 and  # Ran at least 30%
                retracement_pct >= 50 and  # Gave back at least 50%
                current_from_low < 15  # Still near lows
            )
            
            if is_failed:
                return {
                    'ticker': ticker,
                    'high': round(high, 2),
                    'high_date': high_date.strftime('%Y-%m-%d'),
                    'low_after': round(low_after, 2),
                    'low_date': low_date.strftime('%Y-%m-%d'),
                    'current': round(current, 2),
                    'run_pct': round(run_pct, 1),
                    'retracement_pct': round(retracement_pct, 1),
                    'current_from_low_pct': round(current_from_low, 1),
                    'days_since_high': (datetime.now() - high_date).days,
                    'pattern': 'FAILED_BREAKOUT',
                    'status': 'RESETTING'
                }
            
            return None
            
        except Exception as e:
            print(f"⚠️ {ticker}: {e}")
            return None
    
    def scan_watchlist(self, tickers):
        """Scan entire watchlist for failed breakouts"""
        results = []
        
        print(f"🔍 Scanning {len(tickers)} tickers for failed breakouts...")
        
        for ticker in tickers:
            result = self.detect_failed_breakout(ticker)
            if result:
                results.append(result)
                
        return results
    
    def score_reversal_potential(self, breakout_data, has_insider_buying=False):
        """
        Score reversal potential
        
        Factors:
        - How big was the run (bigger = more attention)
        - How much retraced (more = capitulation)
        - Time elapsed (2-8 weeks ideal)
        - Insider buying (huge bonus)
        """
        score = 0
        
        # Run size (max 30 points)
        run = breakout_data['run_pct']
        if run >= 100:
            score += 30
        elif run >= 50:
            score += 25
        elif run >= 30:
            score += 20
            
        # Retracement (max 30 points)
        retrace = breakout_data['retracement_pct']
        if retrace >= 80:
            score += 30
        elif retrace >= 60:
            score += 25
        elif retrace >= 50:
            score += 20
            
        # Time window (max 20 points)
        days = breakout_data['days_since_high']
        if 14 <= days <= 60:
            score += 20
        elif 7 <= days <= 90:
            score += 15
        else:
            score += 5
            
        # Insider buying (max 20 points)
        if has_insider_buying:
            score += 20
            
        return score
    
    def print_breakout_report(self, tickers):
        """Generate readable failed breakout report"""
        print("=" * 70)
        print("🐺 FAILED BREAKOUT DETECTOR")
        print("=" * 70)
        
        results = self.scan_watchlist(tickers)
        
        if not results:
            print("\n⚠️ No failed breakouts found")
            return
            
        # Sort by reversal potential
        for result in results:
            result['score'] = self.score_reversal_potential(result)
            
        results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n🎯 Found {len(results)} Failed Breakouts\n")
        
        for i, fb in enumerate(results, 1):
            print(f"{i}. {fb['ticker']} - Score: {fb['score']}/100")
            print(f"   Run: ${fb['low_after']:.2f} → ${fb['high']:.2f} (+{fb['run_pct']:.1f}%)")
            print(f"   Retrace: ${fb['high']:.2f} → ${fb['low_after']:.2f} (-{fb['retracement_pct']:.1f}%)")
            print(f"   Now: ${fb['current']:.2f} (+{fb['current_from_low_pct']:.1f}% from low)")
            print(f"   Days since high: {fb['days_since_high']}")
            print()
            
        # Save
        timestamp = datetime.now().strftime('%Y%m%d')
        output_file = self.data_dir / f'failed_breakouts_{timestamp}.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"📁 Saved: {output_file}")
        print("=" * 70)
        
        return results


# CLI Usage
if __name__ == "__main__":
    import csv
    
    detector = FailedBreakoutDetector()
    
    # Load watchlist
    watchlist_file = Path('atp_watchlists/ATP_WOLF_PACK_MASTER.csv')
    
    if watchlist_file.exists():
        with open(watchlist_file) as f:
            reader = csv.DictReader(f)
            tickers = [row['Symbol'] for row in reader]
    else:
        tickers = ['IONQ', 'LUNR', 'SOUN', 'BBAI', 'SMR', 'RKLB']
        
    detector.print_breakout_report(tickers)
