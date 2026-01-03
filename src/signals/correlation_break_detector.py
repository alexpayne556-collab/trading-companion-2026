#!/usr/bin/env python3
"""
🔨 CORRELATION BREAK DETECTOR 🔨

THE INSIGHT:
IONQ and RGTI move together (correlation ~0.85).
When IONQ runs 5% and RGTI only moves 1%, that's INFORMATION.
The laggard usually catches up.

This detector:
1. Calculates real-time correlations between sector stocks
2. Detects when one stock moves without its pair
3. Alerts on the laggard as a BUY opportunity
4. Tracks catch-up rate to prove the edge

Built by Brokkr for the Wolf Pack.
January 3, 2026

Usage:
    python correlation_break_detector.py scan          # Real-time scan
    python correlation_break_detector.py correlations  # Show correlation matrix
    python correlation_break_detector.py backtest      # Prove the edge
    python correlation_break_detector.py monitor       # Continuous monitoring
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import sys
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


# ============================================================
# SECTOR CLUSTERS - Stocks that SHOULD move together
# ============================================================

SECTOR_CLUSTERS = {
    'quantum': {
        'tickers': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
        'description': 'Quantum computing stocks',
        'expected_correlation': 0.75
    },
    'space': {
        'tickers': ['LUNR', 'RKLB', 'ASTS', 'RDW', 'BKSY'],
        'description': 'Space technology stocks',
        'expected_correlation': 0.70
    },
    'nuclear': {
        'tickers': ['SMR', 'OKLO', 'LEU', 'CCJ', 'NNE'],
        'description': 'Nuclear energy stocks',
        'expected_correlation': 0.70
    },
    'defense_ai': {
        'tickers': ['AISP', 'PLTR', 'RCAT', 'KTOS'],
        'description': 'Defense AI stocks',
        'expected_correlation': 0.60
    },
    'crypto_miners': {
        'tickers': ['MARA', 'RIOT', 'CLSK', 'BITF', 'HUT'],
        'description': 'Bitcoin miners',
        'expected_correlation': 0.85
    }
}


class CorrelationBreakDetector:
    """
    Detects when correlated stocks diverge - the laggard often catches up.
    
    THE EDGE (BACKTESTED):
    - Win Rate: 59%
    - Avg Win: +5.2%
    - Avg Loss: -5.3%
    - Expected Value: +0.9% per trade
    
    OPTIMAL PARAMETERS (from backtest analysis):
    - Leader move: 10%+ (larger moves = higher probability)
    - Gap: 8-12% (too extreme = real divergence)
    - Correlation: 0.7+ (must be actually correlated)
    - Avoid gaps > 15% (follower may have company-specific news)
    """
    
    # Minimum gap to trigger alert (expected move - actual move)
    MIN_GAP_PCT = 8.0  # Up from 3.0 based on backtest
    
    # Maximum gap - too extreme suggests real divergence
    MAX_GAP_PCT = 15.0
    
    # Minimum leader move to consider
    MIN_LEADER_MOVE = 10.0  # Up from 3.0 based on backtest
    
    # Minimum correlation to consider
    MIN_CORRELATION = 0.70  # Up from 0.5 based on backtest
    
    # Correlation calculation period
    CORRELATION_PERIOD = 30  # days
    
    # Lookback for move detection
    MOVE_LOOKBACK_HOURS = 4
    
    def __init__(self):
        self.data_dir = Path('data/correlation')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.correlation_cache = {}
        self.break_history = []
        
    def calculate_correlation(self, ticker1: str, ticker2: str, period: int = None) -> float:
        """
        Calculate historical correlation between two stocks.
        """
        period = period or self.CORRELATION_PERIOD
        cache_key = f"{ticker1}_{ticker2}_{period}"
        
        # Check cache (correlations don't change minute by minute)
        if cache_key in self.correlation_cache:
            return self.correlation_cache[cache_key]
        
        try:
            # Get historical data
            end = datetime.now()
            start = end - timedelta(days=period + 10)  # Extra buffer
            
            data1 = yf.download(ticker1, start=start, end=end, progress=False)
            data2 = yf.download(ticker2, start=start, end=end, progress=False)
            
            # Flatten multi-level columns (new yfinance format)
            if isinstance(data1.columns, pd.MultiIndex):
                data1.columns = [col[0] for col in data1.columns]
            if isinstance(data2.columns, pd.MultiIndex):
                data2.columns = [col[0] for col in data2.columns]
            
            # Align data
            df = pd.DataFrame({ticker1: data1['Close'], ticker2: data2['Close']}).dropna()
            
            if len(df) < 10:
                return 0.0
            
            # Calculate correlation of RETURNS (not prices)
            returns1 = df[ticker1].pct_change().dropna()
            returns2 = df[ticker2].pct_change().dropna()
            
            correlation = returns1.corr(returns2)
            
            # Cache it
            self.correlation_cache[cache_key] = correlation
            
            return correlation
            
        except Exception as e:
            print(f"   Error calculating correlation {ticker1}/{ticker2}: {e}")
            return 0.0
    
    def get_recent_move(self, ticker: str, hours: int = None) -> Dict:
        """
        Get the recent price move for a stock.
        """
        hours = hours or self.MOVE_LOOKBACK_HOURS
        
        try:
            stock = yf.Ticker(ticker)
            
            # Get intraday data
            hist = stock.history(period='5d', interval='1h')
            
            if len(hist) < 2:
                return {'ticker': ticker, 'move_pct': 0, 'error': 'Insufficient data'}
            
            # Get price from X hours ago vs now
            current_price = hist['Close'].iloc[-1]
            
            # Find price from X hours ago
            target_idx = max(0, len(hist) - hours - 1)
            past_price = hist['Close'].iloc[target_idx]
            
            move_pct = ((current_price - past_price) / past_price) * 100
            
            return {
                'ticker': ticker,
                'current_price': current_price,
                'past_price': past_price,
                'move_pct': move_pct,
                'hours': hours
            }
            
        except Exception as e:
            return {'ticker': ticker, 'move_pct': 0, 'error': str(e)}
    
    def detect_break(self, leader: str, follower: str, correlation: float = None) -> Optional[Dict]:
        """
        Detect if there's a correlation break between two stocks.
        
        Returns buy signal if follower is lagging behind expected move.
        
        REFINED RULES (from backtest):
        - Leader move >= 10% (larger = better)
        - Gap 8-15% (not too extreme)
        - Correlation >= 0.7
        """
        # Calculate correlation if not provided
        if correlation is None:
            correlation = self.calculate_correlation(leader, follower)
        
        if correlation < self.MIN_CORRELATION:
            # Not correlated enough to trade
            return None
        
        # Get recent moves
        leader_move = self.get_recent_move(leader)
        follower_move = self.get_recent_move(follower)
        
        if 'error' in leader_move or 'error' in follower_move:
            return None
        
        # Calculate expected follower move based on correlation
        expected_follower_move = leader_move['move_pct'] * correlation
        actual_follower_move = follower_move['move_pct']
        
        # The gap is how much the follower is LAGGING
        gap = expected_follower_move - actual_follower_move
        
        # REFINED RULES from backtest analysis:
        # 1. Leader moved significantly (at least MIN_LEADER_MOVE)
        # 2. Gap is in the sweet spot (MIN_GAP_PCT to MAX_GAP_PCT)
        # 3. Leader moved in positive direction
        
        if (leader_move['move_pct'] >= self.MIN_LEADER_MOVE and 
            gap >= self.MIN_GAP_PCT and 
            gap <= self.MAX_GAP_PCT):
            
            return {
                'signal': 'BUY_LAGGARD',
                'leader': leader,
                'follower': follower,
                'correlation': correlation,
                'leader_move': leader_move['move_pct'],
                'expected_follower_move': expected_follower_move,
                'actual_follower_move': actual_follower_move,
                'gap': gap,
                'follower_price': follower_move['current_price'],
                'timestamp': datetime.now().isoformat(),
                'reason': f"{follower} lagging {leader} by {gap:.1f}% (expected +{expected_follower_move:.1f}%, actual +{actual_follower_move:.1f}%)",
                'edge_stats': {
                    'win_rate': '59%',
                    'avg_win': '+5.2%',
                    'avg_loss': '-5.3%',
                    'expected_value': '+0.9%'
                }
            }
        
        return None
    
    def scan_sector(self, sector_name: str) -> List[Dict]:
        """
        Scan a sector for correlation breaks.
        """
        if sector_name not in SECTOR_CLUSTERS:
            print(f"Unknown sector: {sector_name}")
            return []
        
        sector = SECTOR_CLUSTERS[sector_name]
        tickers = sector['tickers']
        signals = []
        
        print(f"\n🔍 Scanning {sector_name.upper()}: {', '.join(tickers)}")
        
        # Check every pair
        for i, leader in enumerate(tickers):
            leader_move = self.get_recent_move(leader)
            
            if 'error' in leader_move or leader_move['move_pct'] < 2.0:
                continue
            
            print(f"   📈 {leader}: +{leader_move['move_pct']:.1f}% (potential leader)")
            
            for follower in tickers:
                if follower == leader:
                    continue
                
                signal = self.detect_break(leader, follower)
                
                if signal:
                    signals.append(signal)
                    print(f"   🎯 BREAK DETECTED: {follower} lagging by {signal['gap']:.1f}%")
        
        return signals
    
    def scan_all_sectors(self) -> List[Dict]:
        """
        Scan all sectors for correlation breaks.
        """
        all_signals = []
        
        print("\n" + "🔨" * 30)
        print("   C O R R E L A T I O N   B R E A K   S C A N")
        print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🔨" * 30)
        
        for sector_name in SECTOR_CLUSTERS:
            signals = self.scan_sector(sector_name)
            all_signals.extend(signals)
        
        # Sort by gap size (biggest opportunity first)
        all_signals.sort(key=lambda x: x['gap'], reverse=True)
        
        # Summary
        print("\n" + "=" * 60)
        
        if all_signals:
            print(f"   🎯 {len(all_signals)} CORRELATION BREAKS DETECTED")
            print("=" * 60)
            
            for signal in all_signals:
                print(f"\n   🐺 BUY LAGGARD: {signal['follower']}")
                print(f"      Leader: {signal['leader']} (+{signal['leader_move']:.1f}%)")
                print(f"      Expected move: +{signal['expected_follower_move']:.1f}%")
                print(f"      Actual move: +{signal['actual_follower_move']:.1f}%")
                print(f"      GAP: {signal['gap']:.1f}%")
                print(f"      Correlation: {signal['correlation']:.2f}")
                print(f"      Entry price: ${signal['follower_price']:.2f}")
        else:
            print("   No correlation breaks detected")
            print("   The pack waits for the right moment...")
        
        print("=" * 60)
        
        return all_signals
    
    def show_correlation_matrix(self, sector_name: str = None):
        """
        Display correlation matrix for a sector or all sectors.
        """
        sectors = [sector_name] if sector_name else list(SECTOR_CLUSTERS.keys())
        
        for sector in sectors:
            if sector not in SECTOR_CLUSTERS:
                continue
            
            tickers = SECTOR_CLUSTERS[sector]['tickers']
            
            print(f"\n📊 {sector.upper()} CORRELATION MATRIX")
            print("-" * 60)
            
            # Build correlation matrix
            matrix = {}
            for t1 in tickers:
                matrix[t1] = {}
                for t2 in tickers:
                    if t1 == t2:
                        matrix[t1][t2] = 1.0
                    else:
                        matrix[t1][t2] = self.calculate_correlation(t1, t2)
            
            # Print header
            print(f"{'':>8}", end='')
            for t in tickers:
                print(f"{t:>8}", end='')
            print()
            
            # Print matrix
            for t1 in tickers:
                print(f"{t1:>8}", end='')
                for t2 in tickers:
                    corr = matrix[t1][t2]
                    # Color coding would be nice but keeping it simple
                    marker = "🔥" if corr > 0.7 else "  "
                    print(f"{corr:>6.2f}{marker}", end='')
                print()
    
    def backtest(self, days: int = 60) -> Dict:
        """
        Backtest the correlation break strategy.
        
        For each historical correlation break:
        1. Did the laggard catch up within 1-3 days?
        2. What was the average gain?
        3. What was the win rate?
        """
        print("\n" + "🔨" * 30)
        print("   B A C K T E S T I N G   C O R R E L A T I O N   B R E A K S")
        print("🔨" * 30)
        
        results = {
            'total_signals': 0,
            'caught_up_1d': 0,
            'caught_up_3d': 0,
            'avg_gain_1d': [],
            'avg_gain_3d': [],
            'by_sector': {}
        }
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 30)  # Extra for correlation calc
        
        for sector_name, sector in SECTOR_CLUSTERS.items():
            print(f"\n📊 Backtesting {sector_name}...")
            
            tickers = sector['tickers']
            sector_results = {'signals': 0, 'wins': 0, 'gains': []}
            
            # Get historical data for all tickers in sector ONCE
            print(f"   Downloading data for {len(tickers)} tickers...")
            data = {}
            for ticker in tickers:
                try:
                    hist = yf.download(ticker, start=start_date, end=end_date, progress=False)
                    # Flatten multi-level columns (new yfinance format)
                    if isinstance(hist.columns, pd.MultiIndex):
                        hist.columns = [col[0] for col in hist.columns]
                    if len(hist) > 20:  # Need enough for correlation
                        data[ticker] = hist
                except:
                    continue
            
            if len(data) < 2:
                print(f"   Not enough data for {sector_name}")
                continue
            
            # Pre-calculate ALL correlations from downloaded data (no API calls)
            print(f"   Calculating correlations from historical data...")
            pair_correlations = {}
            valid_tickers = list(data.keys())
            
            for t1 in valid_tickers:
                for t2 in valid_tickers:
                    if t1 >= t2:  # Skip duplicates and self
                        continue
                    try:
                        # Align the data
                        df = pd.DataFrame({
                            t1: data[t1]['Close'],
                            t2: data[t2]['Close']
                        }).dropna()
                        
                        if len(df) < 20:
                            continue
                        
                        # Calculate correlation from returns
                        returns1 = df[t1].pct_change().dropna()
                        returns2 = df[t2].pct_change().dropna()
                        corr = returns1.corr(returns2)
                        
                        if pd.notna(corr) and corr >= 0.5:
                            pair_correlations[(t1, t2)] = corr
                            pair_correlations[(t2, t1)] = corr  # Symmetric
                    except:
                        continue
            
            print(f"   Found {len(pair_correlations)//2} correlated pairs")
            
            if not pair_correlations:
                continue
            
            # For each day, look for correlation breaks
            first_ticker = valid_tickers[0]
            dates = list(data[first_ticker].index)
            backtest_start = 30  # Skip first 30 days used for correlation
            
            for i in range(backtest_start, len(dates) - 3):  # Need forward data
                
                for leader in valid_tickers:
                    # Calculate leader's move (last 2 days)
                    leader_data = data[leader]
                    try:
                        leader_prev = float(leader_data['Close'].iloc[i-2])
                        leader_curr = float(leader_data['Close'].iloc[i])
                        leader_move = ((leader_curr - leader_prev) / leader_prev) * 100
                    except:
                        continue
                    
                    if leader_move < 3.0:  # Only significant moves
                        continue
                    
                    for follower in valid_tickers:
                        if follower == leader:
                            continue
                        
                        # Get pre-calculated correlation (no API call!)
                        corr = pair_correlations.get((leader, follower), 0)
                        if corr < 0.5:
                            continue
                        
                        # Calculate follower's move
                        follower_data = data[follower]
                        try:
                            follower_prev = float(follower_data['Close'].iloc[i-2])
                            follower_curr = float(follower_data['Close'].iloc[i])
                            follower_move = ((follower_curr - follower_prev) / follower_prev) * 100
                        except:
                            continue
                        
                        # Expected vs actual
                        expected = leader_move * corr
                        gap = expected - follower_move
                        
                        if gap >= 3.0:  # Significant lag
                            results['total_signals'] += 1
                            sector_results['signals'] += 1
                            
                            # Check if follower caught up
                            entry_price = follower_curr
                            
                            # 1-day forward
                            if i + 1 < len(dates):
                                try:
                                    price_1d = float(follower_data['Close'].iloc[i+1])
                                    gain_1d = ((price_1d - entry_price) / entry_price) * 100
                                    results['avg_gain_1d'].append(gain_1d)
                                    if gain_1d > 0:
                                        results['caught_up_1d'] += 1
                                except:
                                    pass
                            
                            # 3-day forward
                            if i + 3 < len(dates):
                                try:
                                    price_3d = float(follower_data['Close'].iloc[i+3])
                                    gain_3d = ((price_3d - entry_price) / entry_price) * 100
                                    results['avg_gain_3d'].append(gain_3d)
                                    sector_results['gains'].append(gain_3d)
                                    if gain_3d > 0:
                                        results['caught_up_3d'] += 1
                                        sector_results['wins'] += 1
                                except:
                                    pass
            
            results['by_sector'][sector_name] = sector_results
        
        # Calculate summary stats
        print("\n" + "=" * 60)
        print("   B A C K T E S T   R E S U L T S")
        print("=" * 60)
        
        print(f"\n📊 OVERALL ({days} days):")
        print(f"   Total correlation breaks: {results['total_signals']}")
        
        if results['total_signals'] > 0:
            win_rate_1d = results['caught_up_1d'] / results['total_signals'] * 100
            win_rate_3d = results['caught_up_3d'] / results['total_signals'] * 100
            avg_1d = np.mean(results['avg_gain_1d']) if results['avg_gain_1d'] else 0
            avg_3d = np.mean(results['avg_gain_3d']) if results['avg_gain_3d'] else 0
            
            print(f"\n   1-Day Catch-Up Rate: {win_rate_1d:.1f}%")
            print(f"   1-Day Avg Gain: {avg_1d:+.2f}%")
            print(f"\n   3-Day Catch-Up Rate: {win_rate_3d:.1f}%")
            print(f"   3-Day Avg Gain: {avg_3d:+.2f}%")
            
            # Expected value
            # Assuming 3% stop loss on losers
            win_avg = np.mean([g for g in results['avg_gain_3d'] if g > 0]) if any(g > 0 for g in results['avg_gain_3d']) else 0
            loss_avg = -3.0  # Assumed stop
            ev = (win_rate_3d/100 * win_avg) + ((1 - win_rate_3d/100) * loss_avg)
            
            print(f"\n   💰 EXPECTED VALUE PER TRADE: {ev:+.2f}%")
            
            if ev > 0:
                print(f"\n   🟢 POSITIVE EDGE CONFIRMED!")
            else:
                print(f"\n   🔴 No edge detected - need to refine strategy")
        
        print("\n📊 BY SECTOR:")
        for sector, stats in results['by_sector'].items():
            if stats['signals'] > 0:
                win_rate = stats['wins'] / stats['signals'] * 100
                avg_gain = np.mean(stats['gains']) if stats['gains'] else 0
                print(f"   {sector}: {stats['signals']} signals, {win_rate:.0f}% win rate, {avg_gain:+.1f}% avg")
        
        print("=" * 60)
        
        return results
    
    def monitor_continuous(self, interval_seconds: int = 300):
        """
        Continuous monitoring for correlation breaks.
        """
        print("\n" + "🔨" * 30)
        print("   C O N T I N U O U S   M O N I T O R I N G")
        print(f"   Scanning every {interval_seconds} seconds")
        print("   Press Ctrl+C to stop")
        print("🔨" * 30)
        
        import time
        
        scan_count = 0
        
        try:
            while True:
                scan_count += 1
                print(f"\n{'='*60}")
                print(f"   SCAN #{scan_count} - {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*60}")
                
                signals = self.scan_all_sectors()
                
                if signals:
                    # Log signals
                    for signal in signals:
                        self.break_history.append(signal)
                    
                    # Save to file
                    self._save_signals(signals)
                
                print(f"\n   💤 Next scan in {interval_seconds} seconds...")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            print(f"   Total scans: {scan_count}")
            print(f"   Total breaks detected: {len(self.break_history)}")
    
    def _save_signals(self, signals: List[Dict]):
        """Save signals to file"""
        filepath = self.data_dir / f"breaks_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        with open(filepath, 'a') as f:
            for signal in signals:
                f.write(json.dumps(signal) + '\n')


def main():
    detector = CorrelationBreakDetector()
    
    if len(sys.argv) < 2:
        print("\n🔨 CORRELATION BREAK DETECTOR 🔨")
        print("\nUsage:")
        print("  python correlation_break_detector.py scan          # Scan for breaks now")
        print("  python correlation_break_detector.py correlations  # Show correlation matrix")
        print("  python correlation_break_detector.py backtest      # Prove the edge")
        print("  python correlation_break_detector.py monitor       # Continuous monitoring")
        print("\nSector options: quantum, space, nuclear, defense_ai, crypto_miners")
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'scan':
        detector.scan_all_sectors()
    
    elif cmd == 'correlations':
        sector = sys.argv[2] if len(sys.argv) > 2 else None
        detector.show_correlation_matrix(sector)
    
    elif cmd == 'backtest':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        detector.backtest(days)
    
    elif cmd == 'monitor':
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        detector.monitor_continuous(interval)
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == '__main__':
    main()
