#!/usr/bin/env python3
"""
🐺 PATTERN ENGINE - Backtest & Validate Trading Patterns

Tests repeatable patterns against historical data to find quantifiable edges.
No guessing. Only validation.

Author: Brokkr (Brother Mode)
Date: January 2, 2026
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Tuple, Optional
import sqlite3
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class PatternResult:
    """Results of a pattern backtest"""
    pattern_name: str
    total_signals: int
    winners: int
    losers: int
    win_rate: float
    avg_winner: float
    avg_loser: float
    expected_value: float
    max_winner: float
    max_loser: float
    avg_hold_days: float
    sharpe_ratio: float
    confidence_level: str
    
    def to_dict(self):
        return asdict(self)


class PatternEngine:
    """
    Backtest trading patterns against historical data
    Validates assumptions with statistics, not hope
    """
    
    def __init__(self):
        self.data_dir = Path('data/patterns')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir = Path('logs/backtests')
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Database for pattern signals
        self.db_path = self.data_dir / 'pattern_signals.db'
        self._init_database()
    
    def _init_database(self):
        """Initialize pattern tracking database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Insider cluster signals
        c.execute('''CREATE TABLE IF NOT EXISTS insider_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            signal_date TEXT,
            insider_count INTEGER,
            total_value REAL,
            days_held INTEGER,
            entry_price REAL,
            exit_price REAL,
            return_pct REAL,
            outcome TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Catalyst signals (earnings, FDA, contracts)
        c.execute('''CREATE TABLE IF NOT EXISTS catalyst_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            catalyst_type TEXT,
            catalyst_date TEXT,
            pre_move_pct REAL,
            post_move_pct REAL,
            days_after INTEGER,
            outcome TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Short squeeze signals
        c.execute('''CREATE TABLE IF NOT EXISTS squeeze_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            signal_date TEXT,
            short_interest_pct REAL,
            days_to_cover REAL,
            catalyst_present BOOLEAN,
            max_move_pct REAL,
            days_to_peak INTEGER,
            outcome TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        conn.commit()
        conn.close()
    
    def backtest_insider_cluster(self, 
                                  tickers: List[str], 
                                  lookback_years: int = 3,
                                  min_insiders: int = 2,
                                  hold_days: int = 60) -> PatternResult:
        """
        Backtest Pattern: Insider Cluster Buying
        
        Logic:
        - Find instances of 2+ insiders buying within 14 days
        - Enter at close of last insider buy
        - Exit after hold_days or at 20% gain (whichever first)
        - Stop loss at -15%
        """
        print(f"\n🔍 BACKTESTING: Insider Cluster Pattern")
        print(f"   Tickers: {len(tickers)}")
        print(f"   Lookback: {lookback_years} years")
        print(f"   Min Insiders: {min_insiders}")
        print("=" * 70)
        
        signals = []
        
        for ticker in tickers:
            try:
                # Get historical price data
                stock = yf.Ticker(ticker)
                hist = stock.history(period=f'{lookback_years}y')
                
                if hist.empty:
                    continue
                
                # TODO: Need actual insider transaction history
                # For now, simulate with simple logic
                # In production: Query OpenInsider historical data or SEC EDGAR
                
                # Placeholder: Generate synthetic insider signals for testing
                signals_found = self._find_synthetic_insider_clusters(
                    ticker, hist, min_insiders
                )
                
                for signal in signals_found:
                    result = self._evaluate_trade(
                        hist, 
                        signal['entry_date'], 
                        hold_days,
                        profit_target=0.20,
                        stop_loss=-0.15
                    )
                    
                    if result:
                        signals.append({
                            'ticker': ticker,
                            'entry_date': signal['entry_date'],
                            'insider_count': signal['insider_count'],
                            **result
                        })
                        
            except Exception as e:
                print(f"⚠️ {ticker}: {e}")
                continue
        
        return self._calculate_pattern_result("INSIDER_CLUSTER", signals)
    
    def backtest_earnings_surprise(self,
                                    tickers: List[str],
                                    lookback_years: int = 3,
                                    hold_days: int = 60) -> PatternResult:
        """
        Backtest Pattern: Earnings Beat + Post-Earnings Drift
        
        Logic:
        - Identify earnings beats (actual > estimate)
        - Enter at open day after earnings
        - Exit after hold_days
        - Track post-earnings drift phenomenon
        """
        print(f"\n🔍 BACKTESTING: Earnings Surprise Pattern")
        print("=" * 70)
        
        signals = []
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period=f'{lookback_years}y')
                
                if hist.empty:
                    continue
                
                # Get earnings history
                earnings = stock.earnings_dates
                
                if earnings is None or earnings.empty:
                    continue
                
                # Filter for reported earnings (not estimates)
                reported = earnings[earnings['Reported EPS'].notna()]
                
                for date, row in reported.iterrows():
                    actual = row.get('Reported EPS')
                    estimate = row.get('EPS Estimate')
                    
                    if pd.isna(actual) or pd.isna(estimate):
                        continue
                    
                    # Check if beat
                    surprise = (actual - estimate) / abs(estimate) if estimate != 0 else 0
                    
                    if surprise > 0.05:  # Beat by 5%+
                        # Enter day after earnings
                        entry_date = date + timedelta(days=1)
                        
                        result = self._evaluate_trade(
                            hist,
                            entry_date,
                            hold_days,
                            profit_target=0.15,
                            stop_loss=-0.10
                        )
                        
                        if result:
                            signals.append({
                                'ticker': ticker,
                                'entry_date': entry_date,
                                'surprise_pct': surprise * 100,
                                **result
                            })
                            
            except Exception as e:
                print(f"⚠️ {ticker}: {e}")
                continue
        
        return self._calculate_pattern_result("EARNINGS_SURPRISE", signals)
    
    def backtest_tax_loss_bounce(self,
                                  tickers: List[str],
                                  lookback_years: int = 5) -> PatternResult:
        """
        Backtest Pattern: Tax Loss Selling Bounce (January Effect)
        
        Logic:
        - Find stocks down 20%+ from 52w high in late December
        - Enter Dec 28-31
        - Exit mid-January (15 trading days)
        - Validate our existing 68.8% win rate
        """
        print(f"\n🔍 BACKTESTING: Tax Loss Bounce Pattern")
        print("=" * 70)
        
        signals = []
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period=f'{lookback_years}y')
                
                if hist.empty:
                    continue
                
                # For each year, check December conditions
                for year in range(datetime.now().year - lookback_years, datetime.now().year):
                    # Get Dec 28 price
                    try:
                        dec_window = hist.loc[f'{year}-12-20':f'{year}-12-31']
                        
                        if dec_window.empty:
                            continue
                        
                        entry_date = dec_window.index[-1]  # Last trading day of year
                        entry_price = dec_window['Close'].iloc[-1]
                        
                        # Check if down 20%+ from 52w high
                        year_high = hist.loc[f'{year-1}-01-01':entry_date]['High'].max()
                        
                        drawdown = (entry_price - year_high) / year_high
                        
                        if drawdown < -0.20:  # Down 20%+
                            # Enter here, exit mid-January
                            exit_date = entry_date + timedelta(days=21)  # ~15 trading days
                            
                            result = self._evaluate_trade(
                                hist,
                                entry_date,
                                21,  # Hold ~3 weeks
                                profit_target=0.30,
                                stop_loss=-0.15
                            )
                            
                            if result:
                                signals.append({
                                    'ticker': ticker,
                                    'entry_date': entry_date,
                                    'drawdown_pct': drawdown * 100,
                                    **result
                                })
                                
                    except Exception:
                        continue
                        
            except Exception as e:
                print(f"⚠️ {ticker}: {e}")
                continue
        
        return self._calculate_pattern_result("TAX_LOSS_BOUNCE", signals)
    
    def backtest_short_squeeze_potential(self,
                                         tickers: List[str],
                                         lookback_years: int = 2) -> PatternResult:
        """
        Backtest Pattern: Short Squeeze
        
        Logic:
        - High short interest (>20%) + positive catalyst
        - Track max move in 5 days after catalyst
        - Calculate squeeze frequency and magnitude
        
        NOTE: Short interest data limited in free sources
        """
        print(f"\n🔍 BACKTESTING: Short Squeeze Pattern")
        print("=" * 70)
        
        signals = []
        
        # This requires historical short interest data
        # yfinance doesn't provide historical short interest
        # Would need: FINRA data, Ortex API, or web scraping
        
        print("⚠️  Historical short interest data not available via free API")
        print("   Alternative: Use current short interest + forward test")
        print("   Or: Subscribe to Ortex/S3 Partners for historical data")
        
        # Placeholder for when we have data
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Current short interest
                short_pct = info.get('shortPercentOfFloat', 0) * 100
                
                if short_pct > 20:
                    print(f"   🎯 {ticker}: {short_pct:.1f}% short - HIGH SQUEEZE POTENTIAL")
                    
            except Exception:
                continue
        
        return PatternResult(
            pattern_name="SHORT_SQUEEZE",
            total_signals=0,
            winners=0,
            losers=0,
            win_rate=0.0,
            avg_winner=0.0,
            avg_loser=0.0,
            expected_value=0.0,
            max_winner=0.0,
            max_loser=0.0,
            avg_hold_days=0.0,
            sharpe_ratio=0.0,
            confidence_level="INSUFFICIENT_DATA"
        )
    
    def _find_synthetic_insider_clusters(self, 
                                         ticker: str, 
                                         hist: pd.DataFrame,
                                         min_insiders: int) -> List[Dict]:
        """
        Placeholder: Generate synthetic insider signals for backtesting
        
        In production: Query actual Form 4 historical data
        For now: Use price action as proxy (unusual volume + price drop)
        """
        signals = []
        
        # Simple heuristic: Volume spike + price near low = potential insider signal
        hist['volume_ma'] = hist['Volume'].rolling(20).mean()
        hist['volume_ratio'] = hist['Volume'] / hist['volume_ma']
        hist['low_20d'] = hist['Low'].rolling(20).min()
        hist['near_low'] = (hist['Close'] - hist['low_20d']) / hist['low_20d'] < 0.10
        
        # Find volume spikes near lows
        candidates = hist[
            (hist['volume_ratio'] > 2.0) & 
            (hist['near_low'] == True)
        ]
        
        for idx, row in candidates.iterrows():
            signals.append({
                'entry_date': idx,
                'insider_count': min_insiders,  # Synthetic
                'entry_price': row['Close']
            })
        
        return signals[:10]  # Limit for testing
    
    def _evaluate_trade(self,
                       hist: pd.DataFrame,
                       entry_date: pd.Timestamp,
                       hold_days: int,
                       profit_target: float = 0.20,
                       stop_loss: float = -0.15) -> Optional[Dict]:
        """
        Evaluate a single trade from entry to exit
        
        Returns:
        - entry_price, exit_price, return_pct, days_held, outcome
        """
        try:
            # Find entry price
            entry_idx = hist.index.searchsorted(entry_date)
            
            if entry_idx >= len(hist):
                return None
            
            entry_price = hist.iloc[entry_idx]['Close']
            
            # Track from entry forward
            future = hist.iloc[entry_idx:entry_idx + hold_days]
            
            if len(future) < 2:
                return None
            
            # Check for profit target or stop loss hit
            for i, (idx, row) in enumerate(future.iterrows()):
                if i == 0:
                    continue  # Skip entry day
                
                current_return = (row['Close'] - entry_price) / entry_price
                
                # Hit profit target
                if current_return >= profit_target:
                    return {
                        'entry_price': entry_price,
                        'exit_price': row['Close'],
                        'return_pct': current_return * 100,
                        'days_held': i,
                        'outcome': 'WINNER_TARGET'
                    }
                
                # Hit stop loss
                if current_return <= stop_loss:
                    return {
                        'entry_price': entry_price,
                        'exit_price': row['Close'],
                        'return_pct': current_return * 100,
                        'days_held': i,
                        'outcome': 'LOSER_STOP'
                    }
            
            # Held full period
            exit_price = future.iloc[-1]['Close']
            return_pct = (exit_price - entry_price) / entry_price
            
            return {
                'entry_price': entry_price,
                'exit_price': exit_price,
                'return_pct': return_pct * 100,
                'days_held': len(future) - 1,
                'outcome': 'WINNER_HOLD' if return_pct > 0 else 'LOSER_HOLD'
            }
            
        except Exception as e:
            return None
    
    def _calculate_pattern_result(self, 
                                  pattern_name: str, 
                                  signals: List[Dict]) -> PatternResult:
        """Calculate aggregate statistics for a pattern"""
        
        if not signals:
            return PatternResult(
                pattern_name=pattern_name,
                total_signals=0,
                winners=0,
                losers=0,
                win_rate=0.0,
                avg_winner=0.0,
                avg_loser=0.0,
                expected_value=0.0,
                max_winner=0.0,
                max_loser=0.0,
                avg_hold_days=0.0,
                sharpe_ratio=0.0,
                confidence_level="NO_DATA"
            )
        
        returns = [s['return_pct'] for s in signals]
        winners = [r for r in returns if r > 0]
        losers = [r for r in returns if r <= 0]
        hold_days = [s['days_held'] for s in signals]
        
        win_rate = len(winners) / len(returns) if returns else 0
        avg_winner = np.mean(winners) if winners else 0
        avg_loser = np.mean(losers) if losers else 0
        expected_value = np.mean(returns) if returns else 0
        
        # Sharpe ratio (annualized)
        if len(returns) > 1:
            returns_std = np.std(returns)
            sharpe = (expected_value / returns_std) * np.sqrt(252 / np.mean(hold_days)) if returns_std > 0 else 0
        else:
            sharpe = 0
        
        # Statistical confidence
        n = len(signals)
        if n < 10:
            confidence = "LOW_SAMPLE"
        elif n < 30:
            confidence = "MEDIUM"
        elif n < 100:
            confidence = "GOOD"
        else:
            confidence = "HIGH"
        
        return PatternResult(
            pattern_name=pattern_name,
            total_signals=len(signals),
            winners=len(winners),
            losers=len(losers),
            win_rate=win_rate,
            avg_winner=avg_winner,
            avg_loser=avg_loser,
            expected_value=expected_value,
            max_winner=max(returns) if returns else 0,
            max_loser=min(returns) if returns else 0,
            avg_hold_days=np.mean(hold_days) if hold_days else 0,
            sharpe_ratio=sharpe,
            confidence_level=confidence
        )
    
    def run_full_backtest_suite(self, tickers: List[str]) -> Dict[str, PatternResult]:
        """
        Run all pattern backtests
        Returns comprehensive results
        """
        print("\n" + "=" * 70)
        print("🐺 WOLF PACK PATTERN ENGINE - FULL BACKTEST SUITE")
        print("=" * 70)
        print(f"\nTesting {len(tickers)} tickers across multiple patterns...")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {}
        
        # Pattern 1: Insider Clusters
        results['insider_cluster'] = self.backtest_insider_cluster(tickers)
        
        # Pattern 2: Earnings Surprise
        results['earnings_surprise'] = self.backtest_earnings_surprise(tickers)
        
        # Pattern 3: Tax Loss Bounce
        results['tax_loss_bounce'] = self.backtest_tax_loss_bounce(tickers)
        
        # Pattern 4: Short Squeeze (limited data)
        results['short_squeeze'] = self.backtest_short_squeeze_potential(tickers)
        
        # Save results
        self._save_results(results)
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _save_results(self, results: Dict[str, PatternResult]):
        """Save backtest results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.results_dir / f'backtest_results_{timestamp}.json'
        
        results_dict = {
            'timestamp': datetime.now().isoformat(),
            'patterns': {k: v.to_dict() for k, v in results.items()}
        }
        
        with open(output_file, 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        print(f"\n💾 Results saved: {output_file}")
    
    def _print_summary(self, results: Dict[str, PatternResult]):
        """Print backtest summary"""
        print("\n" + "=" * 70)
        print("📊 BACKTEST RESULTS SUMMARY")
        print("=" * 70)
        
        for pattern_name, result in results.items():
            print(f"\n{pattern_name.upper().replace('_', ' ')}:")
            print(f"  Total Signals: {result.total_signals}")
            print(f"  Win Rate: {result.win_rate * 100:.1f}%")
            print(f"  Expected Value: {result.expected_value:+.2f}%")
            print(f"  Avg Winner: +{result.avg_winner:.2f}%")
            print(f"  Avg Loser: {result.avg_loser:.2f}%")
            print(f"  Max Winner: +{result.max_winner:.2f}%")
            print(f"  Max Loser: {result.max_loser:.2f}%")
            print(f"  Avg Hold: {result.avg_hold_days:.1f} days")
            print(f"  Sharpe Ratio: {result.sharpe_ratio:.2f}")
            print(f"  Confidence: {result.confidence_level}")
            
            # Verdict
            if result.expected_value > 10 and result.win_rate > 0.6:
                print(f"  ✅ VERDICT: STRONG EDGE")
            elif result.expected_value > 5 and result.win_rate > 0.5:
                print(f"  👍 VERDICT: POSITIVE EDGE")
            elif result.total_signals < 10:
                print(f"  ⚠️  VERDICT: INSUFFICIENT DATA")
            else:
                print(f"  ❌ VERDICT: NO EDGE DETECTED")
        
        print("\n" + "=" * 70)


def main():
    """CLI interface"""
    import sys
    
    engine = PatternEngine()
    
    # Load watchlist
    watchlist_file = Path('atp_watchlists/ATP_WOLF_PACK_MASTER.csv')
    
    if watchlist_file.exists():
        import csv
        with open(watchlist_file) as f:
            reader = csv.DictReader(f)
            tickers = [row['Symbol'] for row in reader]
    else:
        # Default test set
        tickers = ['LUNR', 'IONQ', 'SMR', 'RKLB', 'GOGO', 'SOUN', 'BBAI', 'QBTS']
    
    print(f"Loaded {len(tickers)} tickers for backtesting")
    
    if len(sys.argv) > 1:
        pattern = sys.argv[1].lower()
        
        if pattern == 'insider':
            result = engine.backtest_insider_cluster(tickers)
            print(result)
        elif pattern == 'earnings':
            result = engine.backtest_earnings_surprise(tickers)
            print(result)
        elif pattern == 'tax':
            result = engine.backtest_tax_loss_bounce(tickers)
            print(result)
        elif pattern == 'squeeze':
            result = engine.backtest_short_squeeze_potential(tickers)
            print(result)
        else:
            print(f"Unknown pattern: {pattern}")
            print("Options: insider, earnings, tax, squeeze, all")
    else:
        # Run full suite
        engine.run_full_backtest_suite(tickers)


if __name__ == '__main__':
    main()
