#!/usr/bin/env python3
"""
🐺 SECTOR SYMPATHY TRACKER 🐺

Fenrir's CORRELATION DELAY concept:
When one stock in a sector runs, others follow - but not simultaneously.
Often IONQ moves first, then RGTI 15-30 minutes later, then QBTS.

This tracker:
1. Identifies sector LEADERS (first to move)
2. Tracks FOLLOWERS and their typical delay
3. Alerts when leader moves so you can front-run the sympathy plays

EXAMPLE: LUNR runs 10%
→ Check RKLB, ASTS, RDW, BKSY
→ Find which one moved LEAST
→ That's your entry (catch-up potential)

Author: Brokkr (following Fenrir's doctrine)
Date: January 3, 2026
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json
from collections import defaultdict


class SectorSympatyTracker:
    """
    Track sector correlations and identify sympathy play opportunities
    """
    
    # Sector clusters with leader identification
    SECTORS = {
        'Space': {
            'leader': 'LUNR',  # Usually moves first
            'followers': ['RKLB', 'ASTS', 'RDW', 'BKSY', 'SPCE', 'SIDU'],
            'etf': 'ARKX',
            'correlation': 0.75,  # Historical correlation strength
        },
        'Quantum': {
            'leader': 'IONQ',  # The bellwether
            'followers': ['RGTI', 'QBTS', 'QUBT'],
            'etf': None,
            'correlation': 0.85,  # Highest correlation - they move together
        },
        'Nuclear': {
            'leader': 'SMR',  # Most liquid
            'followers': ['NNE', 'OKLO', 'LEU', 'CCJ'],
            'etf': 'NLR',
            'correlation': 0.70,
        },
        'Defense': {
            'leader': 'RCAT',  # Most volatile, moves first
            'followers': ['AISP', 'PLTR'],
            'etf': 'ITA',
            'correlation': 0.60,  # Lower correlation
        },
        'Crypto': {
            'leader': 'CLSK',  # Most volatile miner
            'followers': ['MARA', 'RIOT', 'COIN'],
            'etf': 'BITO',
            'correlation': 0.80,  # High correlation with BTC
        },
        'EV': {
            'leader': 'RIVN',  # Most retail attention
            'followers': ['LCID', 'NIO'],
            'etf': 'DRIV',
            'correlation': 0.65,
        },
    }
    
    # Threshold for "leader moving"
    LEADER_MOVE_THRESHOLD = 5.0  # 5% move triggers sympathy watch
    
    def __init__(self):
        self.data_dir = Path('logs/sympathy')
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def check_leader_moves(self) -> dict:
        """
        Check if any sector leaders are making significant moves today
        Returns sectors where sympathy plays might develop
        """
        print("\n" + "🐺" * 30)
        print("   SECTOR SYMPATHY SCANNER")
        print("   " + datetime.now().strftime('%A, %B %d, %Y - %I:%M %p'))
        print("🐺" * 30)
        
        sympathy_alerts = []
        
        for sector, data in self.SECTORS.items():
            leader = data['leader']
            
            try:
                stock = yf.Ticker(leader)
                hist = stock.history(period='5d')
                
                if len(hist) < 2:
                    continue
                
                # Today's move
                current = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                today_change = ((current - prev_close) / prev_close) * 100
                
                # 5-day move
                first_close = hist['Close'].iloc[0]
                five_day_change = ((current - first_close) / first_close) * 100
                
                if abs(today_change) >= self.LEADER_MOVE_THRESHOLD:
                    # Leader is moving! Check followers
                    print(f"\n🔥 {sector} LEADER MOVING!")
                    print(f"   {leader}: {today_change:+.1f}% today | {five_day_change:+.1f}% 5-day")
                    
                    follower_data = self._analyze_followers(sector, data['followers'], today_change)
                    
                    sympathy_alerts.append({
                        'sector': sector,
                        'leader': leader,
                        'leader_move': round(today_change, 2),
                        'leader_5d': round(five_day_change, 2),
                        'followers': follower_data,
                        'correlation': data['correlation'],
                    })
                else:
                    print(f"\n   {sector}: {leader} {today_change:+.1f}% (below threshold)")
                    
            except Exception as e:
                print(f"\n   {sector}: ERROR - {e}")
                continue
        
        if sympathy_alerts:
            self._print_sympathy_opportunities(sympathy_alerts)
        else:
            print("\n\n📊 No major sector leader moves today")
            print("   Threshold: ±5% daily move to trigger sympathy watch")
        
        return sympathy_alerts
    
    def _analyze_followers(self, sector: str, followers: list, leader_move: float) -> list:
        """
        Analyze follower stocks when leader is moving
        Identify the laggards for sympathy plays
        """
        follower_data = []
        
        for ticker in followers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='5d')
                
                if len(hist) < 2:
                    continue
                
                current = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                today_change = ((current - prev_close) / prev_close) * 100
                
                # Calculate lag (how much behind the leader)
                lag = leader_move - today_change
                
                # Volume analysis
                avg_vol = hist['Volume'].tail(20).mean() if len(hist) >= 20 else hist['Volume'].mean()
                today_vol = hist['Volume'].iloc[-1]
                vol_ratio = today_vol / avg_vol if avg_vol > 0 else 1
                
                follower_data.append({
                    'ticker': ticker,
                    'price': round(current, 2),
                    'change': round(today_change, 2),
                    'lag': round(lag, 2),
                    'vol_ratio': round(vol_ratio, 2),
                    'catch_up_potential': round(lag, 2) if lag > 0 else 0,
                })
                
            except Exception as e:
                continue
        
        # Sort by lag (biggest laggards first)
        follower_data.sort(key=lambda x: x['lag'], reverse=True)
        
        return follower_data
    
    def _print_sympathy_opportunities(self, alerts: list):
        """Print actionable sympathy play opportunities"""
        print("\n\n" + "=" * 70)
        print("🎯 SYMPATHY PLAY OPPORTUNITIES")
        print("   When the leader runs, laggards catch up")
        print("=" * 70)
        
        for alert in alerts:
            print(f"\n🔥 {alert['sector'].upper()}")
            print(f"   Leader: {alert['leader']} → {alert['leader_move']:+.1f}% today")
            print(f"   Correlation: {alert['correlation']*100:.0f}%")
            print(f"\n   FOLLOWERS (sorted by catch-up potential):")
            print(f"   {'TICKER':<8} {'PRICE':>8} {'CHANGE':>8} {'LAG':>8} {'VOLUME':>8} {'SIGNAL':>12}")
            print("   " + "-" * 55)
            
            for f in alert['followers']:
                if f['lag'] > 2:  # Only show if lagging by 2%+
                    signal = "🎯 BUY" if f['lag'] > 5 else "👀 WATCH"
                    print(f"   {f['ticker']:<8} ${f['price']:>6.2f} {f['change']:>+7.1f}% {f['lag']:>+7.1f}% {f['vol_ratio']:>6.1f}x {signal:>12}")
                else:
                    print(f"   {f['ticker']:<8} ${f['price']:>6.2f} {f['change']:>+7.1f}% {f['lag']:>+7.1f}% {f['vol_ratio']:>6.1f}x {'—':>12}")
    
    def find_all_laggards(self) -> list:
        """
        Scan ALL sectors for laggard opportunities
        Find stocks that should be moving more based on sector performance
        """
        print("\n" + "🐺" * 30)
        print("   ALL-SECTOR LAGGARD SCAN")
        print("   " + datetime.now().strftime('%Y-%m-%d %H:%M'))
        print("🐺" * 30)
        
        all_laggards = []
        
        for sector, data in self.SECTORS.items():
            # Get all tickers in sector
            all_tickers = [data['leader']] + data['followers']
            
            changes = {}
            for ticker in all_tickers:
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period='5d')
                    
                    if len(hist) < 2:
                        continue
                    
                    current = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    today_change = ((current - prev_close) / prev_close) * 100
                    
                    changes[ticker] = {
                        'change': today_change,
                        'price': current,
                    }
                except:
                    continue
            
            if len(changes) < 2:
                continue
            
            # Calculate sector average
            avg_change = sum(c['change'] for c in changes.values()) / len(changes)
            
            # Find laggards (below average by 2%+)
            for ticker, data_item in changes.items():
                lag = avg_change - data_item['change']
                if lag > 2:  # Lagging by 2%+
                    all_laggards.append({
                        'ticker': ticker,
                        'sector': sector,
                        'price': round(data_item['price'], 2),
                        'change': round(data_item['change'], 2),
                        'sector_avg': round(avg_change, 2),
                        'lag': round(lag, 2),
                    })
        
        # Sort by lag
        all_laggards.sort(key=lambda x: x['lag'], reverse=True)
        
        if all_laggards:
            print("\n   LAGGARDS (Stock lagging sector average by 2%+)")
            print(f"\n   {'TICKER':<8} {'SECTOR':<10} {'PRICE':>8} {'CHANGE':>8} {'SECT AVG':>10} {'LAG':>8}")
            print("   " + "-" * 60)
            
            for lag in all_laggards[:10]:  # Top 10
                print(f"   {lag['ticker']:<8} {lag['sector']:<10} ${lag['price']:>6.2f} {lag['change']:>+7.1f}% {lag['sector_avg']:>+9.1f}% {lag['lag']:>+7.1f}%")
        else:
            print("\n   No significant laggards found")
        
        return all_laggards
    
    def track_correlation_history(self, days: int = 30):
        """
        Build historical correlation data between leaders and followers
        This helps identify which followers respond fastest
        """
        print(f"\n📊 BUILDING CORRELATION HISTORY ({days} days)")
        
        correlations = {}
        
        for sector, data in self.SECTORS.items():
            leader = data['leader']
            followers = data['followers']
            
            try:
                # Get leader history
                leader_stock = yf.Ticker(leader)
                leader_hist = leader_stock.history(period=f'{days}d')['Close'].pct_change()
                
                sector_corr = {'leader': leader, 'followers': {}}
                
                for follower in followers:
                    try:
                        follower_stock = yf.Ticker(follower)
                        follower_hist = follower_stock.history(period=f'{days}d')['Close'].pct_change()
                        
                        # Calculate correlation
                        corr = leader_hist.corr(follower_hist)
                        sector_corr['followers'][follower] = round(corr, 3)
                        
                    except:
                        continue
                
                correlations[sector] = sector_corr
                
            except Exception as e:
                continue
        
        # Print results
        print("\n   SECTOR          LEADER    FOLLOWERS (correlation)")
        print("   " + "-" * 60)
        
        for sector, corr_data in correlations.items():
            followers_str = ", ".join([f"{t}({c:.2f})" for t, c in corr_data['followers'].items()])
            print(f"   {sector:<14} {corr_data['leader']:<8} {followers_str}")
        
        return correlations


def main():
    import sys
    
    tracker = SectorSympatyTracker()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'leaders':
            tracker.check_leader_moves()
        elif command == 'laggards':
            tracker.find_all_laggards()
        elif command == 'correlations':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            tracker.track_correlation_history(days)
        else:
            print("Usage:")
            print("  python sector_sympathy.py leaders      - Check if leaders are moving")
            print("  python sector_sympathy.py laggards     - Find all laggard opportunities")
            print("  python sector_sympathy.py correlations - Show historical correlations")
    else:
        # Default: check leaders and find laggards
        tracker.check_leader_moves()
        tracker.find_all_laggards()


if __name__ == '__main__':
    main()
