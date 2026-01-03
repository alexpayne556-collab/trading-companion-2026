#!/usr/bin/env python3
"""
🐺 REPEAT RUNNER SCANNER - Daily Watchlist Generator

Based on our analysis:
- 77 moves of 10%+ in 30 days
- Same stocks repeat (SIDU 9x, RCAT 5x, LUNR 5x)
- 39% are reversals (down then pop)
- 32% are momentum (already running)

This scanner:
1. Identifies repeat runners that are DOWN (reversal setup)
2. Identifies repeat runners that are UP (momentum play)
3. Alerts on unusual volume on any repeat runner

Run this EVERY MORNING at 6 AM

Author: Brokkr (Brother Mode)
Date: January 3, 2026
"""

import yfinance as yf
from datetime import datetime
from pathlib import Path
import json


class RepeatRunnerScanner:
    """
    Scan for setups on stocks that repeatedly make 10%+ moves
    """
    
    # Repeat runners by category (from our analysis)
    TIER_1_RUNNERS = {
        # 5+ big moves - HIGHEST PRIORITY
        'SIDU': {'moves': 9, 'sector': 'Biotech', 'avg_gain': 32},
        'RCAT': {'moves': 5, 'sector': 'Defense/AI', 'avg_gain': 13},
        'LUNR': {'moves': 5, 'sector': 'Space', 'avg_gain': 16},
        'ASTS': {'moves': 4, 'sector': 'Space', 'avg_gain': 15},
        'RDW': {'moves': 4, 'sector': 'Space', 'avg_gain': 14},
        'CLSK': {'moves': 4, 'sector': 'Crypto/Mining', 'avg_gain': 14},
    }
    
    TIER_2_RUNNERS = {
        # 3-4 big moves - HIGH PRIORITY
        'QBTS': {'moves': 4, 'sector': 'Quantum', 'avg_gain': 15},
        'RKLB': {'moves': 4, 'sector': 'Space', 'avg_gain': 12},
        'BKSY': {'moves': 3, 'sector': 'Space', 'avg_gain': 12},
        'IONQ': {'moves': 3, 'sector': 'Quantum', 'avg_gain': 12},
        'RGTI': {'moves': 3, 'sector': 'Quantum', 'avg_gain': 14},
        'QUBT': {'moves': 3, 'sector': 'Quantum', 'avg_gain': 13},
        'RIVN': {'moves': 3, 'sector': 'EV', 'avg_gain': 13},
    }
    
    TIER_3_RUNNERS = {
        # 2 big moves - WATCH LIST
        'SMR': {'moves': 2, 'sector': 'Nuclear', 'avg_gain': 14},
        'LEU': {'moves': 2, 'sector': 'Nuclear', 'avg_gain': 13},
        'MARA': {'moves': 2, 'sector': 'Crypto/Mining', 'avg_gain': 11},
        'AFRM': {'moves': 2, 'sector': 'Fintech', 'avg_gain': 12},
        'SPCE': {'moves': 2, 'sector': 'Space', 'avg_gain': 11},
        'NNE': {'moves': 2, 'sector': 'Nuclear', 'avg_gain': 13},
        'OKLO': {'moves': 2, 'sector': 'Nuclear', 'avg_gain': 12},
        'AISP': {'moves': 1, 'sector': 'Defense/AI', 'avg_gain': 15},  # Your position!
    }
    
    def __init__(self):
        self.all_runners = {**self.TIER_1_RUNNERS, **self.TIER_2_RUNNERS, **self.TIER_3_RUNNERS}
        self.data_dir = Path('logs/daily_scans')
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def scan_all_runners(self):
        """
        Generate daily scan of all repeat runners
        Categorize by setup type
        """
        print("\n" + "🐺" * 35)
        print("   REPEAT RUNNER DAILY SCAN")
        print("   " + datetime.now().strftime('%A, %B %d, %Y - %I:%M %p'))
        print("🐺" * 35)
        
        reversal_setups = []    # Down 5%+ from recent high
        momentum_setups = []    # Up and running
        volume_alerts = []      # Unusual volume today
        neutral = []            # No clear setup
        
        for ticker, info in self.all_runners.items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1mo')
                
                if len(hist) < 5:
                    continue
                
                # Current price
                current = hist['Close'].iloc[-1]
                
                # 5-day high/low
                high_5d = hist['High'].tail(5).max()
                low_5d = hist['Low'].tail(5).min()
                
                # Distance from 5d high
                dist_from_high = ((current - high_5d) / high_5d) * 100
                
                # 5-day change
                price_5d_ago = hist['Close'].iloc[-5] if len(hist) >= 5 else current
                change_5d = ((current - price_5d_ago) / price_5d_ago) * 100
                
                # Volume analysis
                avg_vol = hist['Volume'].tail(20).mean()
                today_vol = hist['Volume'].iloc[-1]
                vol_ratio = today_vol / avg_vol if avg_vol > 0 else 1
                
                # RSI (simple calculation)
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs.iloc[-1])) if loss.iloc[-1] != 0 else 50
                
                setup = {
                    'ticker': ticker,
                    'sector': info['sector'],
                    'tier': self._get_tier(ticker),
                    'historical_moves': info['moves'],
                    'avg_gain': info['avg_gain'],
                    'current_price': round(current, 2),
                    'change_5d': round(change_5d, 2),
                    'dist_from_high': round(dist_from_high, 2),
                    'vol_ratio': round(vol_ratio, 2),
                    'rsi': round(rsi, 1) if not pd.isna(rsi) else 50
                }
                
                # Categorize setup
                if vol_ratio >= 2.0:
                    volume_alerts.append(setup)
                
                if dist_from_high <= -10:
                    # Down 10%+ from 5d high = REVERSAL SETUP
                    reversal_setups.append(setup)
                elif change_5d >= 10:
                    # Up 10%+ in 5 days = MOMENTUM PLAY
                    momentum_setups.append(setup)
                else:
                    neutral.append(setup)
                    
            except Exception as e:
                continue
        
        # Print results
        self._print_reversal_setups(reversal_setups)
        self._print_momentum_setups(momentum_setups)
        self._print_volume_alerts(volume_alerts)
        self._print_watchlist(neutral)
        
        # Save daily scan
        self._save_scan(reversal_setups, momentum_setups, volume_alerts, neutral)
        
        return {
            'reversal': reversal_setups,
            'momentum': momentum_setups,
            'volume': volume_alerts,
            'neutral': neutral
        }
    
    def _get_tier(self, ticker):
        if ticker in self.TIER_1_RUNNERS:
            return 1
        elif ticker in self.TIER_2_RUNNERS:
            return 2
        return 3
    
    def _print_reversal_setups(self, setups):
        print("\n" + "=" * 70)
        print("🔻 REVERSAL SETUPS (Down 10%+, Ready to Bounce)")
        print("   These stocks REPEAT big moves after pullbacks")
        print("=" * 70)
        
        if not setups:
            print("   No reversal setups today")
            return
        
        # Sort by tier then by distance from high
        setups.sort(key=lambda x: (x['tier'], x['dist_from_high']))
        
        for s in setups:
            tier_emoji = "⭐⭐⭐" if s['tier'] == 1 else "⭐⭐" if s['tier'] == 2 else "⭐"
            print(f"\n{tier_emoji} {s['ticker']} ({s['sector']})")
            print(f"   Price: ${s['current_price']} | {s['dist_from_high']:+.1f}% from 5d high")
            print(f"   Historical: {s['historical_moves']} big moves, avg +{s['avg_gain']}%")
            print(f"   Volume: {s['vol_ratio']}x avg | RSI: {s['rsi']}")
            if s['rsi'] < 30:
                print(f"   🎯 OVERSOLD - High probability reversal")
    
    def _print_momentum_setups(self, setups):
        print("\n" + "=" * 70)
        print("🚀 MOMENTUM PLAYS (Already Running)")
        print("   These are hot - consider adding on dips")
        print("=" * 70)
        
        if not setups:
            print("   No momentum plays today")
            return
        
        # Sort by 5d change
        setups.sort(key=lambda x: x['change_5d'], reverse=True)
        
        for s in setups:
            tier_emoji = "⭐⭐⭐" if s['tier'] == 1 else "⭐⭐" if s['tier'] == 2 else "⭐"
            print(f"\n{tier_emoji} {s['ticker']} ({s['sector']})")
            print(f"   Price: ${s['current_price']} | 5d: {s['change_5d']:+.1f}%")
            print(f"   Historical: {s['historical_moves']} big moves, avg +{s['avg_gain']}%")
            print(f"   Volume: {s['vol_ratio']}x avg | RSI: {s['rsi']}")
            if s['rsi'] > 70:
                print(f"   ⚠️ OVERBOUGHT - Wait for pullback")
    
    def _print_volume_alerts(self, setups):
        print("\n" + "=" * 70)
        print("📢 VOLUME ALERTS (2x+ Average Volume)")
        print("   Something is happening - investigate!")
        print("=" * 70)
        
        if not setups:
            print("   No unusual volume alerts")
            return
        
        # Sort by volume ratio
        setups.sort(key=lambda x: x['vol_ratio'], reverse=True)
        
        for s in setups:
            print(f"\n🔊 {s['ticker']} ({s['sector']})")
            print(f"   Volume: {s['vol_ratio']}x AVERAGE")
            print(f"   Price: ${s['current_price']} | 5d: {s['change_5d']:+.1f}%")
    
    def _print_watchlist(self, setups):
        print("\n" + "=" * 70)
        print("👀 NEUTRAL - ON WATCHLIST")
        print("   No clear setup, but track for next move")
        print("=" * 70)
        
        # Sort by tier
        setups.sort(key=lambda x: x['tier'])
        
        for s in setups:
            tier_emoji = "⭐⭐⭐" if s['tier'] == 1 else "⭐⭐" if s['tier'] == 2 else "⭐"
            print(f"   {tier_emoji} {s['ticker']}: ${s['current_price']} | 5d: {s['change_5d']:+.1f}% | Vol: {s['vol_ratio']}x")
    
    def _save_scan(self, reversal, momentum, volume, neutral):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        data = {
            'scan_time': timestamp,
            'reversal_setups': reversal,
            'momentum_plays': momentum,
            'volume_alerts': volume,
            'neutral': neutral
        }
        
        filename = self.data_dir / f'daily_scan_{timestamp}.json'
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Saved: {filename}")


# Need pandas for RSI
import pandas as pd


def main():
    scanner = RepeatRunnerScanner()
    scanner.scan_all_runners()


if __name__ == '__main__':
    main()
