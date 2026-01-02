"""
🐺 SECTOR ROTATION TRACKER - Wolf Pack Research Module
Detect sector momentum before individual stocks break out
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path

class SectorRotationTracker:
    """Track sector ETF performance to catch rotation early"""
    
    # Key sector ETFs to monitor
    SECTOR_ETFS = {
        'XLK': 'Technology',
        'XLF': 'Financials',
        'XLE': 'Energy',
        'XLV': 'Healthcare',
        'XLI': 'Industrials',
        'XLB': 'Materials',
        'XLP': 'Consumer Staples',
        'XLY': 'Consumer Discretionary',
        'XLU': 'Utilities',
        'XLRE': 'Real Estate',
        'ITA': 'Defense/Aerospace',
        'NLR': 'Nuclear Energy',
        'ARKQ': 'Autonomous/Space',
        'BOTZ': 'Robotics/AI',
        'QCLN': 'Clean Energy',
        'XME': 'Metals/Mining'
    }
    
    def __init__(self):
        self.data_dir = Path('logs/sectors')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def get_sector_performance(self, periods=[5, 10, 20]):
        """
        Get performance for all sector ETFs over multiple periods
        
        Returns:
            DataFrame with sectors as rows, periods as columns
        """
        results = {}
        
        for etf, name in self.SECTOR_ETFS.items():
            try:
                ticker = yf.Ticker(etf)
                hist = ticker.history(period='3mo')
                
                if len(hist) < 20:
                    continue
                    
                current = hist['Close'].iloc[-1]
                
                perf = {'sector': name, 'etf': etf}
                
                for period in periods:
                    if len(hist) >= period:
                        past = hist['Close'].iloc[-period]
                        pct_change = ((current - past) / past) * 100
                        perf[f'{period}d'] = round(pct_change, 2)
                        
                results[etf] = perf
                
            except Exception as e:
                print(f"⚠️ {etf}: {e}")
                
        return pd.DataFrame.from_dict(results, orient='index')
    
    def rank_sectors(self, df):
        """
        Rank sectors by momentum
        
        Scoring:
        - 5d performance (40% weight)
        - 10d performance (30% weight)  
        - 20d performance (30% weight)
        - Acceleration (5d > 10d > 20d) = bonus
        """
        if df.empty:
            return df
            
        df = df.copy()
        
        # Calculate momentum score
        df['momentum_score'] = (
            df['5d'] * 0.4 +
            df['10d'] * 0.3 +
            df['20d'] * 0.3
        )
        
        # Acceleration bonus (getting stronger)
        df['accelerating'] = (df['5d'] > df['10d']) & (df['10d'] > df['20d'])
        df.loc[df['accelerating'], 'momentum_score'] += 10
        
        # Deceleration penalty
        df['decelerating'] = (df['5d'] < df['10d']) & (df['10d'] < df['20d'])
        df.loc[df['decelerating'], 'momentum_score'] -= 10
        
        # Sort by momentum score
        df = df.sort_values('momentum_score', ascending=False)
        
        return df
    
    def detect_rotation(self, current_df, previous_df=None):
        """
        Detect sector rotation by comparing current vs previous week
        
        Returns sectors that moved significantly in rankings
        """
        if previous_df is None or previous_df.empty:
            return None
            
        current_ranks = current_df.reset_index()[['etf', 'sector', 'momentum_score']]
        current_ranks['current_rank'] = range(1, len(current_ranks) + 1)
        
        previous_ranks = previous_df.reset_index()[['etf', 'momentum_score']]
        previous_ranks['previous_rank'] = range(1, len(previous_ranks) + 1)
        
        # Merge
        comparison = current_ranks.merge(previous_ranks, on='etf', suffixes=('_now', '_prev'))
        comparison['rank_change'] = comparison['previous_rank'] - comparison['current_rank']
        comparison['score_change'] = comparison['momentum_score_now'] - comparison['momentum_score_prev']
        
        # Flag significant movers
        comparison['significant'] = abs(comparison['rank_change']) >= 3
        
        return comparison.sort_values('rank_change', ascending=False)
    
    def map_sectors_to_tickers(self):
        """
        Map sector momentum to our watchlist tickers
        
        Returns dict: {sector: [tickers]}
        """
        sector_map = {
            'Technology': ['NVDA', 'AMD', 'AVGO', 'PLTR', 'IONQ', 'QBTS', 'RGTI'],
            'Defense/Aerospace': ['RTX', 'LMT', 'NOC', 'GD', 'KTOS', 'AVAV', 'RCAT'],
            'Nuclear Energy': ['SMR', 'OKLO', 'CCJ', 'LEU', 'NNE'],
            'Autonomous/Space': ['LUNR', 'RKLB', 'ASTS', 'BKSY', 'RDW'],
            'Energy': ['CHK', 'EQT', 'RRC', 'RIG', 'LNG'],
            'Financials': ['SOFI', 'HOOD', 'COIN'],
            'Consumer Discretionary': ['NKE', 'LULU', 'DECK', 'OPEN'],
            'Industrials': ['GEV', 'ETN'],
            'Materials': ['MP', 'LTBR']
        }
        
        return sector_map
    
    def generate_sector_alerts(self, df, threshold=5.0):
        """
        Generate alerts for sectors showing strong momentum
        
        Args:
            df: Sector performance DataFrame
            threshold: Alert if 5d performance > threshold
            
        Returns list of alerts with recommended tickers
        """
        alerts = []
        sector_map = self.map_sectors_to_tickers()
        
        # Hot sectors (5d > threshold)
        hot = df[df['5d'] > threshold].copy()
        
        for idx, row in hot.iterrows():
            sector_name = row['sector']
            tickers = sector_map.get(sector_name, [])
            
            if tickers:
                alerts.append({
                    'sector': sector_name,
                    'etf': row['etf'],
                    'performance_5d': row['5d'],
                    'performance_20d': row['20d'],
                    'momentum_score': row['momentum_score'],
                    'accelerating': row.get('accelerating', False),
                    'watchlist_tickers': tickers,
                    'alert_type': 'HOT_SECTOR',
                    'priority': 'HIGH' if row['5d'] > 10 else 'MEDIUM'
                })
                
        # Cold sectors (potential reversal)
        cold = df[df['5d'] < -threshold].copy()
        
        for idx, row in cold.iterrows():
            sector_name = row['sector']
            tickers = sector_map.get(sector_name, [])
            
            if tickers:
                alerts.append({
                    'sector': sector_name,
                    'etf': row['etf'],
                    'performance_5d': row['5d'],
                    'performance_20d': row['20d'],
                    'momentum_score': row['momentum_score'],
                    'watchlist_tickers': tickers,
                    'alert_type': 'COLD_SECTOR',
                    'priority': 'LOW'
                })
                
        return alerts
    
    def print_rotation_report(self):
        """Generate readable sector rotation report"""
        print("=" * 70)
        print("🐺 SECTOR ROTATION TRACKER")
        print("=" * 70)
        
        # Get current performance
        df = self.get_sector_performance([5, 10, 20])
        
        if df.empty:
            print("\n⚠️ No sector data available")
            return
            
        ranked = self.rank_sectors(df)
        
        # Print top movers
        print("\n🔥 HOTTEST SECTORS (5-Day Performance)")
        print("-" * 70)
        top5 = ranked.head(5)
        for idx, row in top5.iterrows():
            accel = "🚀" if row.get('accelerating', False) else ""
            print(f"{row['sector']:25} {row['etf']:6} {row['5d']:+6.2f}% {accel}")
            print(f"  10d: {row['10d']:+6.2f}%  |  20d: {row['20d']:+6.2f}%  |  Score: {row['momentum_score']:.1f}")
            
        print("\n❄️ COLDEST SECTORS")
        print("-" * 70)
        bottom5 = ranked.tail(5)
        for idx, row in bottom5.iterrows():
            decel = "📉" if row.get('decelerating', False) else ""
            print(f"{row['sector']:25} {row['etf']:6} {row['5d']:+6.2f}% {decel}")
            
        # Generate alerts
        alerts = self.generate_sector_alerts(ranked, threshold=3.0)
        
        if alerts:
            print("\n⚡ SECTOR ALERTS")
            print("-" * 70)
            for alert in alerts:
                if alert['alert_type'] == 'HOT_SECTOR':
                    print(f"\n🟢 {alert['sector']} ({alert['etf']}) +{alert['performance_5d']:.1f}%")
                    print(f"   Watchlist tickers: {', '.join(alert['watchlist_tickers'])}")
                    print(f"   Priority: {alert['priority']}")
                    
        print("\n" + "=" * 70)
        
        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        ranked.to_csv(self.data_dir / f'sector_rotation_{timestamp}.csv')
        print(f"📁 Saved: logs/sectors/sector_rotation_{timestamp}.csv")
        
        # Save alerts
        if alerts:
            with open(self.data_dir / f'sector_alerts_{timestamp}.json', 'w') as f:
                json.dump(alerts, f, indent=2)


# CLI Usage
if __name__ == "__main__":
    tracker = SectorRotationTracker()
    tracker.print_rotation_report()
