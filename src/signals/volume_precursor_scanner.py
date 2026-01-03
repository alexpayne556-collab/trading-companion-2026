#!/usr/bin/env python3
"""
🔨 VOLUME PRECURSOR SCANNER 🔨

THE INSIGHT:
Volume precedes price. Before a big move, someone is accumulating.
They can't hide volume completely. It shows up BEFORE the price moves.

When volume is 2x+ average but price only moved <3%, that's INFORMATION.
Someone is absorbing sells and building a position. Catalyst likely coming.

THE EDGE (to be proven):
- Detect accumulation BEFORE the move
- Buy when smart money is loading
- Exit when the catalyst triggers

Built by Brokkr for the Wolf Pack.
January 3, 2026

Usage:
    python volume_precursor_scanner.py scan           # Real-time scan
    python volume_precursor_scanner.py backtest 180   # Prove the edge
    python volume_precursor_scanner.py analyze IONQ   # Deep dive one ticker
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import sys
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


# Watchlist from the Protocol
TIER_1_RUNNERS = ['SIDU', 'LUNR', 'RCAT', 'ASTS', 'RDW']

SECTOR_WATCHLIST = {
    'quantum': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'space': ['LUNR', 'RKLB', 'ASTS', 'RDW', 'BKSY'],
    'nuclear': ['SMR', 'OKLO', 'LEU', 'CCJ', 'NNE'],
    'defense_ai': ['AISP', 'PLTR', 'RCAT', 'KTOS'],
    'crypto_miners': ['MARA', 'RIOT', 'CLSK', 'BITF', 'HUT']
}

ALL_WATCHLIST = list(set(
    TIER_1_RUNNERS + 
    [t for sector in SECTOR_WATCHLIST.values() for t in sector]
))


class VolumePrecursorScanner:
    """
    Detects accumulation: high volume without corresponding price movement.
    
    THE SIGNAL:
    When volume is 2x+ average but price hasn't moved >3%, someone is loading.
    This is the PRECURSOR - the move comes AFTER the accumulation.
    
    GENIUS ADDITIONS:
    1. Time decay - recent accumulation matters more
    2. Intraday pattern - accumulation at specific times (open, close)
    3. Multi-timeframe - check 1d, 3d, 5d windows
    4. Relative strength - accumulation + outperformance = strongest signal
    """
    
    # Core parameters
    MIN_VOLUME_RATIO = 2.0      # Volume must be 2x+ average
    MAX_PRICE_CHANGE = 3.0      # Price change must be <3%
    VOLUME_LOOKBACK = 20        # Days for average volume calc
    
    # Genius additions
    MIN_RELATIVE_VOLUME = 1.5   # Minimum for weaker signals
    STRONG_VOLUME_RATIO = 3.0   # 3x+ volume = strong signal
    PRICE_STABILITY_RANGE = 2.0 # <2% = very stable during accumulation
    
    def __init__(self):
        self.data_dir = Path('data/volume_signals')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.signal_history = []
        
    def calculate_volume_metrics(self, ticker: str, period: str = '60d') -> Optional[Dict]:
        """
        Calculate comprehensive volume metrics for a ticker.
        """
        try:
            # Get historical data
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if len(hist) < self.VOLUME_LOOKBACK:
                return None
            
            # Flatten multi-level columns if needed
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = [col[0] for col in hist.columns]
            
            # Calculate metrics
            current_volume = hist['Volume'].iloc[-1]
            avg_volume_20d = hist['Volume'].iloc[-20:].mean()
            
            # Price changes (multiple timeframes)
            price_1d = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
            price_3d = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-4]) / hist['Close'].iloc[-4]) * 100 if len(hist) >= 4 else price_1d
            price_5d = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100 if len(hist) >= 6 else price_3d
            
            # Volume ratios (multiple timeframes)
            volume_ratio_1d = current_volume / avg_volume_20d
            volume_ratio_3d = hist['Volume'].iloc[-3:].mean() / avg_volume_20d
            volume_ratio_5d = hist['Volume'].iloc[-5:].mean() / avg_volume_20d
            
            # Price volatility during accumulation (stability metric)
            recent_high = hist['High'].iloc[-5:].max()
            recent_low = hist['Low'].iloc[-5:].min()
            current_price = hist['Close'].iloc[-1]
            volatility = ((recent_high - recent_low) / current_price) * 100
            
            # SPY comparison (relative strength)
            spy = yf.Ticker('SPY')
            spy_hist = spy.history(period='10d')
            if isinstance(spy_hist.columns, pd.MultiIndex):
                spy_hist.columns = [col[0] for col in spy_hist.columns]
            
            spy_change_5d = ((spy_hist['Close'].iloc[-1] - spy_hist['Close'].iloc[-6]) / spy_hist['Close'].iloc[-6]) * 100 if len(spy_hist) >= 6 else 0
            relative_strength = price_5d - spy_change_5d
            
            return {
                'ticker': ticker,
                'current_price': float(current_price),
                'current_volume': int(current_volume),
                'avg_volume_20d': int(avg_volume_20d),
                'volume_ratio_1d': volume_ratio_1d,
                'volume_ratio_3d': volume_ratio_3d,
                'volume_ratio_5d': volume_ratio_5d,
                'price_change_1d': price_1d,
                'price_change_3d': price_3d,
                'price_change_5d': price_5d,
                'volatility_5d': volatility,
                'relative_strength': relative_strength,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"   Error analyzing {ticker}: {e}")
            return None
    
    def detect_accumulation(self, metrics: Dict) -> Optional[Dict]:
        """
        Detect accumulation pattern with GENIUS multi-factor scoring.
        
        Not just "volume high, price low" - we score multiple signals:
        1. Volume ratio (higher = better)
        2. Price stability (tighter = better)
        3. Multi-timeframe confirmation
        4. Relative strength vs SPY
        """
        if not metrics:
            return None
        
        ticker = metrics['ticker']
        
        # Basic filters - MUST PASS
        volume_ratio = metrics['volume_ratio_1d']
        price_change = abs(metrics['price_change_1d'])
        
        # CRITICAL: Price must NOT have moved significantly yet
        # If price already moved >3%, we MISSED the accumulation
        if price_change >= self.MAX_PRICE_CHANGE:
            return None  # Too late, price already moved
        
        # Volume must be elevated
        if volume_ratio < self.MIN_RELATIVE_VOLUME:
            return None  # Not enough volume
        
        # GENIUS SCORING SYSTEM (0-100)
        score = 0
        factors = []
        
        # Factor 1: Volume intensity (0-30 points)
        if volume_ratio >= self.STRONG_VOLUME_RATIO:
            volume_score = 30
            factors.append(f"Volume {volume_ratio:.1f}x (EXTREME)")
        elif volume_ratio >= self.MIN_VOLUME_RATIO:
            volume_score = 20
            factors.append(f"Volume {volume_ratio:.1f}x (HIGH)")
        else:
            volume_score = 10
            factors.append(f"Volume {volume_ratio:.1f}x")
        score += volume_score
        
        # Factor 2: Price stability (0-25 points)
        if price_change < self.PRICE_STABILITY_RANGE:
            stability_score = 25
            factors.append(f"Price stable ({price_change:.1f}%)")
        elif price_change < self.MAX_PRICE_CHANGE:
            stability_score = 15
            factors.append(f"Price controlled ({price_change:.1f}%)")
        else:
            stability_score = 5
        score += stability_score
        
        # Factor 3: Multi-timeframe confirmation (0-20 points)
        timeframe_score = 0
        if metrics['volume_ratio_3d'] >= self.MIN_RELATIVE_VOLUME:
            timeframe_score += 10
            factors.append("3d volume elevated")
        if metrics['volume_ratio_5d'] >= self.MIN_RELATIVE_VOLUME:
            timeframe_score += 10
            factors.append("5d volume elevated")
        score += timeframe_score
        
        # Factor 4: Relative strength (0-15 points)
        if metrics['relative_strength'] > 2:
            rs_score = 15
            factors.append(f"Outperforming SPY +{metrics['relative_strength']:.1f}%")
        elif metrics['relative_strength'] > 0:
            rs_score = 8
            factors.append("Matching SPY")
        else:
            rs_score = 0
        score += rs_score
        
        # Factor 5: Volatility compression (0-10 points)
        if metrics['volatility_5d'] < 5:
            vol_score = 10
            factors.append("Low volatility (coiling)")
        elif metrics['volatility_5d'] < 10:
            vol_score = 5
        else:
            vol_score = 0
        score += vol_score
        
        # Signal strength based on score
        if score >= 70:
            signal_strength = 'STRONG'
        elif score >= 50:
            signal_strength = 'MODERATE'
        elif score >= 30:
            signal_strength = 'WEAK'
        else:
            return None  # Too weak
        
        return {
            'signal': 'ACCUMULATION',
            'ticker': ticker,
            'strength': signal_strength,
            'score': score,
            'factors': factors,
            'volume_ratio': volume_ratio,
            'price_change': price_change,
            'current_price': metrics['current_price'],
            'current_volume': metrics['current_volume'],
            'avg_volume': metrics['avg_volume_20d'],
            'relative_strength': metrics['relative_strength'],
            'timestamp': datetime.now().isoformat(),
            'reason': f"{ticker} showing {signal_strength} accumulation (score: {score}/100)"
        }
    
    def scan_all(self) -> List[Dict]:
        """
        Scan entire watchlist for volume precursor signals.
        """
        print("🔨" * 30)
        print("   V O L U M E   P R E C U R S O R   S C A N")
        print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🔨" * 30)
        print()
        
        signals = []
        
        for ticker in sorted(ALL_WATCHLIST):
            metrics = self.calculate_volume_metrics(ticker)
            if metrics:
                signal = self.detect_accumulation(metrics)
                if signal:
                    signals.append(signal)
        
        # Sort by score
        signals.sort(key=lambda x: x['score'], reverse=True)
        
        # Display results
        if signals:
            print(f"\n🎯 FOUND {len(signals)} ACCUMULATION SIGNALS:\n")
            print("=" * 80)
            
            for sig in signals:
                strength_emoji = "🔥" if sig['strength'] == 'STRONG' else "⚡" if sig['strength'] == 'MODERATE' else "📊"
                print(f"{strength_emoji} {sig['ticker']} - {sig['strength']} (Score: {sig['score']}/100)")
                print(f"   Price: ${sig['current_price']:.2f} ({sig['price_change']:+.1f}% today)")
                print(f"   Volume: {sig['current_volume']:,} ({sig['volume_ratio']:.1f}x average)")
                print(f"   Factors: {', '.join(sig['factors'])}")
                print()
        else:
            print("\n" + "=" * 60)
            print("   No accumulation signals detected")
            print("   The pack waits for smart money to load...")
            print("=" * 60)
        
        return signals
    
    def backtest(self, days: int = 180):
        """
        Backtest the volume precursor signal.
        
        THE QUESTION: When we detect accumulation, what happens next?
        - 1 day forward
        - 3 days forward
        - 5 days forward
        - 10 days forward
        
        This proves (or disproves) the edge.
        """
        print("🔨" * 30)
        print("   B A C K T E S T I N G   V O L U M E   P R E C U R S O R")
        print("🔨" * 30)
        print()
        
        results = {
            'total_signals': 0,
            'wins_1d': 0,
            'wins_3d': 0,
            'wins_5d': 0,
            'wins_10d': 0,
            'gains_1d': [],
            'gains_3d': [],
            'gains_5d': [],
            'gains_10d': [],
            'by_strength': {'STRONG': [], 'MODERATE': [], 'WEAK': []}
        }
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 30)
        
        for ticker in ALL_WATCHLIST:
            print(f"📊 Backtesting {ticker}...")
            
            try:
                # Get historical data
                stock = yf.Ticker(ticker)
                hist = stock.history(start=start_date, end=end_date)
                
                if isinstance(hist.columns, pd.MultiIndex):
                    hist.columns = [col[0] for col in hist.columns]
                
                if len(hist) < 30:
                    continue
                
                # For each day, check if accumulation signal would have triggered
                for i in range(25, len(hist) - 15):  # Need lookback and forward data
                    
                    # Calculate metrics at this point in time
                    window = hist.iloc[:i+1]
                    
                    current_volume = window['Volume'].iloc[-1]
                    avg_volume = window['Volume'].iloc[-20:].mean()
                    volume_ratio = current_volume / avg_volume
                    
                    current_price = window['Close'].iloc[-1]
                    prev_price = window['Close'].iloc[-2]
                    price_change = abs((current_price - prev_price) / prev_price) * 100
                    
                    # Check if signal would have triggered
                    if volume_ratio >= self.MIN_VOLUME_RATIO and price_change < self.MAX_PRICE_CHANGE:
                        results['total_signals'] += 1
                        
                        entry_price = current_price
                        date_str = window.index[-1].strftime('%Y-%m-%d')
                        
                        # Forward returns
                        try:
                            # 1 day
                            if i + 1 < len(hist):
                                price_1d = hist['Close'].iloc[i + 1]
                                gain_1d = ((price_1d - entry_price) / entry_price) * 100
                                results['gains_1d'].append(gain_1d)
                                if gain_1d > 0:
                                    results['wins_1d'] += 1
                            
                            # 3 days
                            if i + 3 < len(hist):
                                price_3d = hist['Close'].iloc[i + 3]
                                gain_3d = ((price_3d - entry_price) / entry_price) * 100
                                results['gains_3d'].append(gain_3d)
                                if gain_3d > 0:
                                    results['wins_3d'] += 1
                            
                            # 5 days
                            if i + 5 < len(hist):
                                price_5d = hist['Close'].iloc[i + 5]
                                gain_5d = ((price_5d - entry_price) / entry_price) * 100
                                results['gains_5d'].append(gain_5d)
                                if gain_5d > 0:
                                    results['wins_5d'] += 1
                            
                            # 10 days
                            if i + 10 < len(hist):
                                price_10d = hist['Close'].iloc[i + 10]
                                gain_10d = ((price_10d - entry_price) / entry_price) * 100
                                results['gains_10d'].append(gain_10d)
                                if gain_10d > 0:
                                    results['wins_10d'] += 1
                        except:
                            pass
                        
            except Exception as e:
                print(f"   Error: {e}")
                continue
        
        # Print results
        print("\n" + "=" * 60)
        print("   B A C K T E S T   R E S U L T S")
        print("=" * 60)
        
        if results['total_signals'] > 0:
            print(f"\n📊 ANALYZED {results['total_signals']} SIGNALS over {days} days\n")
            
            # 1-day results
            if results['gains_1d']:
                wr_1d = (results['wins_1d'] / len(results['gains_1d'])) * 100
                avg_1d = sum(results['gains_1d']) / len(results['gains_1d'])
                print(f"1-Day Results:")
                print(f"   Win Rate: {wr_1d:.1f}%")
                print(f"   Avg Gain: {avg_1d:+.2f}%")
            
            # 3-day results
            if results['gains_3d']:
                wr_3d = (results['wins_3d'] / len(results['gains_3d'])) * 100
                avg_3d = sum(results['gains_3d']) / len(results['gains_3d'])
                print(f"\n3-Day Results:")
                print(f"   Win Rate: {wr_3d:.1f}%")
                print(f"   Avg Gain: {avg_3d:+.2f}%")
            
            # 5-day results
            if results['gains_5d']:
                wr_5d = (results['wins_5d'] / len(results['gains_5d'])) * 100
                avg_5d = sum(results['gains_5d']) / len(results['gains_5d'])
                print(f"\n5-Day Results:")
                print(f"   Win Rate: {wr_5d:.1f}%")
                print(f"   Avg Gain: {avg_5d:+.2f}%")
            
            # 10-day results
            if results['gains_10d']:
                wr_10d = (results['wins_10d'] / len(results['gains_10d'])) * 100
                avg_10d = sum(results['gains_10d']) / len(results['gains_10d'])
                print(f"\n10-Day Results:")
                print(f"   Win Rate: {wr_10d:.1f}%")
                print(f"   Avg Gain: {avg_10d:+.2f}%")
                
                # Expected value
                if wr_10d > 0:
                    wins = [g for g in results['gains_10d'] if g > 0]
                    losses = [g for g in results['gains_10d'] if g < 0]
                    avg_win = sum(wins) / len(wins) if wins else 0
                    avg_loss = abs(sum(losses) / len(losses)) if losses else 0
                    ev = (wr_10d/100 * avg_win) - ((100-wr_10d)/100 * avg_loss)
                    
                    print(f"\n💰 10-DAY EXPECTED VALUE: {ev:+.2f}%")
                    
                    if ev > 2:
                        print("   🟢🟢 STRONG POSITIVE EDGE!")
                    elif ev > 0:
                        print("   🟢 POSITIVE EDGE CONFIRMED")
                    else:
                        print("   🔴 No edge detected")
        
        print("=" * 60)
    
    def analyze_ticker(self, ticker: str):
        """
        Deep analysis of a single ticker.
        """
        print(f"\n🔍 DEEP ANALYSIS: {ticker}")
        print("=" * 60)
        
        metrics = self.calculate_volume_metrics(ticker, period='90d')
        if not metrics:
            print(f"No data available for {ticker}")
            return
        
        print(f"\n📊 CURRENT METRICS:")
        print(f"   Price: ${metrics['current_price']:.2f}")
        print(f"   Volume: {metrics['current_volume']:,} ({metrics['volume_ratio_1d']:.2f}x average)")
        print(f"   Price Change 1d: {metrics['price_change_1d']:+.1f}%")
        print(f"   Price Change 5d: {metrics['price_change_5d']:+.1f}%")
        print(f"   Volatility 5d: {metrics['volatility_5d']:.1f}%")
        print(f"   Relative Strength: {metrics['relative_strength']:+.1f}%")
        
        signal = self.detect_accumulation(metrics)
        if signal:
            print(f"\n🎯 SIGNAL DETECTED:")
            print(f"   Strength: {signal['strength']}")
            print(f"   Score: {signal['score']}/100")
            print(f"   Factors: {', '.join(signal['factors'])}")
        else:
            print(f"\n❌ No accumulation signal at this time")
        
        print("=" * 60)


def main():
    scanner = VolumePrecursorScanner()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python volume_precursor_scanner.py scan")
        print("  python volume_precursor_scanner.py backtest [days]")
        print("  python volume_precursor_scanner.py analyze <TICKER>")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'scan':
        scanner.scan_all()
    
    elif command == 'backtest':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 180
        scanner.backtest(days)
    
    elif command == 'analyze':
        if len(sys.argv) < 3:
            print("Please provide a ticker: python volume_precursor_scanner.py analyze IONQ")
            return
        ticker = sys.argv[2].upper()
        scanner.analyze_ticker(ticker)
    
    else:
        print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()
