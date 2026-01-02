"""
🐺 CATALYST TRACKER - Wolf Pack Research Module
Track upcoming events that force price movement
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path

class CatalystTracker:
    """Track and score upcoming market catalysts"""
    
    def __init__(self):
        self.data_dir = Path('logs/catalysts')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def get_earnings_calendar(self, tickers, days_ahead=30):
        """
        Get earnings dates for watchlist tickers
        Returns dict with ticker: {date, days_until, last_surprise}
        """
        results = {}
        today = datetime.now()
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                
                # Get earnings date
                calendar = stock.calendar
                if calendar is not None and 'Earnings Date' in calendar:
                    earnings_date = calendar['Earnings Date'][0]
                    
                    if isinstance(earnings_date, str):
                        earnings_date = pd.to_datetime(earnings_date)
                    
                    days_until = (earnings_date - today).days
                    
                    if 0 <= days_until <= days_ahead:
                        # Get last earnings surprise
                        earnings_history = stock.earnings_history
                        last_surprise = 0
                        if earnings_history is not None and len(earnings_history) > 0:
                            last_surprise = earnings_history.iloc[0].get('surprisePercent', 0)
                        
                        results[ticker] = {
                            'date': earnings_date.strftime('%Y-%m-%d'),
                            'days_until': days_until,
                            'last_surprise_pct': last_surprise,
                            'catalyst_type': 'EARNINGS',
                            'impact': 'HIGH'
                        }
                        
            except Exception as e:
                print(f"⚠️ {ticker}: {e}")
                
        return results
    
    def add_manual_catalysts(self, ticker, event, date_str, catalyst_type, impact):
        """
        Add manual catalysts (product launches, FDA dates, etc)
        
        Args:
            ticker: Stock symbol
            event: Description of event
            date_str: Date string 'YYYY-MM-DD' or 'Q1 2026'
            catalyst_type: EARNINGS, FDA, PRODUCT_LAUNCH, CONTRACT, TECH_DEMO
            impact: LOW, MEDIUM, HIGH, EXTREME
        """
        catalyst_file = self.data_dir / 'manual_catalysts.json'
        
        # Load existing
        if catalyst_file.exists():
            with open(catalyst_file) as f:
                catalysts = json.load(f)
        else:
            catalysts = {}
            
        if ticker not in catalysts:
            catalysts[ticker] = []
            
        catalysts[ticker].append({
            'event': event,
            'date': date_str,
            'type': catalyst_type,
            'impact': impact,
            'added': datetime.now().strftime('%Y-%m-%d')
        })
        
        # Save
        with open(catalyst_file, 'w') as f:
            json.dump(catalysts, f, indent=2)
            
        print(f"✅ Added {ticker} catalyst: {event} ({date_str})")
        
    def get_all_catalysts(self, tickers, days_ahead=30):
        """
        Combine earnings calendar + manual catalysts
        Returns sorted by days_until
        """
        # Get earnings
        catalysts = self.get_earnings_calendar(tickers, days_ahead)
        
        # Add manual catalysts
        catalyst_file = self.data_dir / 'manual_catalysts.json'
        if catalyst_file.exists():
            with open(catalyst_file) as f:
                manual = json.load(f)
                
            today = datetime.now()
            
            for ticker, events in manual.items():
                if ticker not in tickers:
                    continue
                    
                for event in events:
                    date_str = event['date']
                    
                    # Try to parse date
                    try:
                        if 'Q' in date_str:
                            # Estimate quarter midpoint
                            year = int(date_str.split()[-1])
                            quarter = int(date_str[1])
                            month = quarter * 3 - 1  # Mid-quarter
                            event_date = datetime(year, month, 15)
                        else:
                            event_date = datetime.strptime(date_str, '%Y-%m-%d')
                            
                        days_until = (event_date - today).days
                        
                        if 0 <= days_until <= days_ahead:
                            key = f"{ticker}_{event['type']}"
                            catalysts[key] = {
                                'ticker': ticker,
                                'event': event['event'],
                                'date': date_str,
                                'days_until': days_until,
                                'catalyst_type': event['type'],
                                'impact': event['impact']
                            }
                    except:
                        pass
                        
        return catalysts
    
    def rank_catalysts(self, catalysts):
        """
        Score and rank catalysts by impact potential
        
        Scoring:
        - EXTREME impact + <7 days = 100
        - HIGH impact + <14 days = 80
        - MEDIUM impact + <21 days = 60
        - Negative earnings surprise last time = -20
        """
        ranked = []
        
        for key, data in catalysts.items():
            score = 0
            
            # Impact score
            impact_scores = {
                'EXTREME': 100,
                'HIGH': 80,
                'MEDIUM': 60,
                'LOW': 40
            }
            score += impact_scores.get(data['impact'], 50)
            
            # Urgency multiplier
            days = data['days_until']
            if days <= 3:
                score *= 1.5
            elif days <= 7:
                score *= 1.3
            elif days <= 14:
                score *= 1.1
                
            # Earnings surprise penalty
            if data.get('last_surprise_pct', 0) < -10:
                score -= 20
                
            ranked.append({
                **data,
                'score': int(score)
            })
            
        # Sort by score descending
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked
    
    def print_catalyst_report(self, tickers, days_ahead=30):
        """Generate readable catalyst report"""
        catalysts = self.get_all_catalysts(tickers, days_ahead)
        ranked = self.rank_catalysts(catalysts)
        
        print("=" * 70)
        print(f"🐺 CATALYST CALENDAR - Next {days_ahead} Days")
        print("=" * 70)
        
        if not ranked:
            print("\n⚠️ No catalysts found in next 30 days")
            return
            
        for cat in ranked:
            ticker = cat.get('ticker', cat.get('event', 'UNKNOWN')[:4])
            
            # Impact emoji
            impact_emoji = {
                'EXTREME': '🔥',
                'HIGH': '🟢',
                'MEDIUM': '🟡',
                'LOW': '🔵'
            }
            emoji = impact_emoji.get(cat['impact'], '⚪')
            
            print(f"\n{emoji} {ticker} - Score: {cat['score']}")
            print(f"   Event: {cat.get('event', 'Earnings Report')}")
            print(f"   Date: {cat['date']} ({cat['days_until']} days)")
            print(f"   Type: {cat['catalyst_type']}")
            print(f"   Impact: {cat['impact']}")
            
            if cat.get('last_surprise_pct'):
                surprise = cat['last_surprise_pct']
                print(f"   Last Earnings: {surprise:+.1f}% surprise")
                
        print("\n" + "=" * 70)
        
        # Save to file
        output_file = self.data_dir / f"catalyst_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w') as f:
            json.dump(ranked, f, indent=2)
        print(f"📁 Saved: {output_file}")


# CLI Usage
if __name__ == "__main__":
    import sys
    
    tracker = CatalystTracker()
    
    # Example: Add LUNR moon mission
    if len(sys.argv) > 1 and sys.argv[1] == 'add':
        # python catalyst_tracker.py add LUNR "IM-3 Moon Mission" "2026-02-15" PRODUCT_LAUNCH HIGH
        ticker = sys.argv[2]
        event = sys.argv[3]
        date = sys.argv[4]
        cat_type = sys.argv[5] if len(sys.argv) > 5 else 'PRODUCT_LAUNCH'
        impact = sys.argv[6] if len(sys.argv) > 6 else 'MEDIUM'
        
        tracker.add_manual_catalysts(ticker, event, date, cat_type, impact)
        
    else:
        # Load watchlist and scan
        import csv
        watchlist_file = Path('atp_watchlists/ATP_WOLF_PACK_MASTER.csv')
        
        if watchlist_file.exists():
            with open(watchlist_file) as f:
                reader = csv.DictReader(f)
                tickers = [row['Symbol'] for row in reader]
        else:
            tickers = ['AISP', 'GOGO', 'LUNR', 'IONQ', 'SMR', 'RKLB']
            
        tracker.print_catalyst_report(tickers, days_ahead=30)
