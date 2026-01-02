"""
🐺 INSIDER PROFILER - Wolf Pack Research Module
Analyze WHO is buying and their historical track record
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path
import yfinance as yf

class InsiderProfiler:
    """Profile insiders and score their conviction/track record"""
    
    # Insider role scoring
    ROLE_SCORES = {
        'CEO': 100,
        'President': 100,
        'Founder': 100,
        'Chairman': 90,
        'Executive Chairman': 90,
        'CFO': 60,  # Often scheduled buys
        'COO': 80,
        'CTO': 85,
        'Director': 70,
        '10% Owner': 95,  # Large shareholder
        'Other': 50
    }
    
    def __init__(self):
        self.data_dir = Path('logs/insiders')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def parse_form4_for_details(self, ticker):
        """
        Parse recent Form 4s for a ticker to get insider details
        
        Returns list of transactions with:
        - Name, title, amount, price, date
        - Whether it was open market or 10b5-1
        """
        url = f"https://www.sec.gov/cgi-bin/browse-edgar"
        params = {
            'action': 'getcompany',
            'CIK': ticker,
            'type': '4',
            'dateb': '',
            'owner': 'include',
            'count': 100
        }
        
        # Note: This is simplified - real implementation needs proper SEC parsing
        # For now, return structure we want
        return []
    
    def score_insider_buy(self, role, amount, is_10b51=False, timing_score=None):
        """
        Score an insider buy based on multiple factors
        
        Args:
            role: Executive title
            amount: Dollar value of purchase
            is_10b51: Whether it was a scheduled buy
            timing_score: Optional timing score (how close to low)
            
        Returns:
            conviction_score: 0-100
        """
        score = 0
        
        # Role weight (40 points max)
        role_weight = self.ROLE_SCORES.get(role, 50) * 0.4
        score += role_weight
        
        # Amount weight (30 points max)
        if amount >= 1_000_000:
            amount_weight = 30
        elif amount >= 500_000:
            amount_weight = 25
        elif amount >= 250_000:
            amount_weight = 20
        elif amount >= 100_000:
            amount_weight = 15
        elif amount >= 50_000:
            amount_weight = 10
        else:
            amount_weight = 5
        score += amount_weight
        
        # 10b5-1 penalty (scheduled buys less meaningful)
        if is_10b51:
            score -= 20
            
        # Timing bonus (20 points max)
        if timing_score:
            score += timing_score * 0.2
            
        return min(100, max(0, score))
    
    def analyze_insider_cluster(self, ticker, days=30):
        """
        Analyze all insider buys for a ticker in recent period
        
        Returns:
            - Total conviction (sum of amounts)
            - Number of insiders
            - Average price
            - Highest role
            - Pattern (one-time, wave, sustained)
        """
        # This would parse actual Form 4 data
        # For now, return structure
        
        analysis = {
            'ticker': ticker,
            'period_days': days,
            'total_insiders': 0,
            'total_amount': 0,
            'transactions': [],
            'pattern': 'UNKNOWN',
            'conviction_score': 0
        }
        
        return analysis
    
    def check_insider_track_record(self, insider_name, ticker):
        """
        Look up historical performance of an insider's buys
        
        For a given insider:
        - When did they last buy?
        - What was the price then vs now?
        - Success rate of their buys
        
        This requires building a database over time
        """
        # Placeholder for future database
        track_record = {
            'insider': insider_name,
            'ticker': ticker,
            'previous_buys': [],
            'success_rate': None,
            'avg_return': None
        }
        
        return track_record
    
    def detect_insider_pattern(self, transactions):
        """
        Detect pattern in insider buying
        
        Patterns:
        - ONE_TIME: Single isolated buy
        - WAVE: Multiple insiders buying same week
        - SUSTAINED: Same insider buying multiple times
        - ACCUMULATION: Regular buys over months
        """
        if len(transactions) == 0:
            return 'NONE'
        elif len(transactions) == 1:
            return 'ONE_TIME'
        elif len(transactions) >= 3:
            # Check if same week
            dates = [t['date'] for t in transactions]
            date_range = max(dates) - min(dates)
            
            if date_range.days <= 7:
                return 'WAVE'
            elif date_range.days <= 30:
                return 'SUSTAINED'
            else:
                return 'ACCUMULATION'
        else:
            return 'MODERATE'
    
    def generate_insider_report(self, ticker):
        """Generate full insider profile report"""
        print(f"\n{'=' * 70}")
        print(f"🐺 INSIDER PROFILE - {ticker}")
        print(f"{'=' * 70}")
        
        # Get stock price context
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1y')
            current = hist['Close'].iloc[-1]
            low_52w = hist['Low'].min()
            pct_from_low = ((current - low_52w) / low_52w) * 100
            
            print(f"\n📊 CURRENT CONTEXT")
            print(f"Price: ${current:.2f}")
            print(f"52W Low: ${low_52w:.2f} (+{pct_from_low:.1f}%)")
        except:
            pass
        
        # Analyze insiders
        analysis = self.analyze_insider_cluster(ticker, days=60)
        
        print(f"\n👔 INSIDER ACTIVITY (60 days)")
        print(f"Total Insiders: {analysis['total_insiders']}")
        print(f"Total Conviction: ${analysis['total_amount']:,.0f}")
        print(f"Pattern: {analysis['pattern']}")
        print(f"Conviction Score: {analysis['conviction_score']}/100")
        
        if analysis['transactions']:
            print(f"\n📋 TRANSACTIONS")
            for txn in analysis['transactions'][:10]:
                role_emoji = "👑" if txn['role'] in ['CEO', 'President'] else "💼"
                scheduled = " [10b5-1]" if txn.get('is_10b51') else ""
                print(f"{role_emoji} {txn['name']} ({txn['role']})")
                print(f"   ${txn['amount']:,.0f} @ ${txn['price']:.2f} - {txn['date']}{scheduled}")
        
        # Save
        timestamp = datetime.now().strftime('%Y%m%d')
        with open(self.data_dir / f'{ticker}_profile_{timestamp}.json', 'w') as f:
            json.dump(analysis, f, indent=2)
            
        print(f"\n📁 Saved: logs/insiders/{ticker}_profile_{timestamp}.json")
        print("=" * 70)


# CLI Usage
if __name__ == "__main__":
    import sys
    
    profiler = InsiderProfiler()
    
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
        profiler.generate_insider_report(ticker)
    else:
        print("Usage: python insider_profiler.py TICKER")
        print("Example: python insider_profiler.py AISP")
