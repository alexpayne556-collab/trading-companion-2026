#!/usr/bin/env python3
"""
🐺 REAL-TIME PATTERN SCANNER - Live Pattern Detection

Scans for validated patterns in real-time
Combines: Insider clusters + Catalysts + Technical setups + ML predictions

Author: Brokkr (Brother Mode)
Date: January 2, 2026
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Optional
import sqlite3
import sys

# Import our weapons
sys.path.append(str(Path(__file__).parent.parent))
from research.wolf_intelligence import WolfIntelligence
from research.catalyst_tracker import CatalystTracker
from research.failed_breakout_detector import FailedBreakoutDetector
from research.sector_rotation import SectorRotationTracker


class RealtimePatternScanner:
    """
    Real-time pattern scanner
    Monitors watchlist for validated pattern setups
    """
    
    def __init__(self):
        self.data_dir = Path('data/patterns')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.alerts_dir = Path('logs/pattern_alerts')
        self.alerts_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize our weapons
        self.wolf_intelligence = WolfIntelligence()
        self.catalyst_tracker = CatalystTracker()
        self.breakout_detector = FailedBreakoutDetector()
        self.sector_rotation = SectorRotationTracker()
        
        # ML predictor (optional)
        self.ml_available = False
        try:
            from research.ml_predictor import MLPredictor
            self.ml_predictor = MLPredictor()
            
            # Load latest model if exists
            models = sorted(self.ml_predictor.models_dir.glob('ml_predictor_*.pkl'))
            if models:
                self.ml_predictor.load_model(models[-1])
                self.ml_available = True
                print("✅ ML Predictor loaded")
        except Exception:
            print("⚠️  ML Predictor not available (run training first)")
    
    def scan_for_patterns(self, tickers: List[str]) -> List[Dict]:
        """
        Scan tickers for ALL validated patterns
        Returns ranked list of setups
        """
        print(f"\n🔍 SCANNING {len(tickers)} TICKERS FOR PATTERNS")
        print("=" * 70)
        
        all_signals = []
        
        for ticker in tickers:
            try:
                signals = self._check_ticker_patterns(ticker)
                
                if signals['total_score'] >= 50:  # Threshold for alerting
                    all_signals.append(signals)
                    print(f"   ✅ {ticker}: {signals['total_score']}/100 - {len(signals['patterns'])} patterns")
                
            except Exception as e:
                # Silent fail - continue scanning
                continue
        
        # Sort by score
        all_signals.sort(key=lambda x: x['total_score'], reverse=True)
        
        return all_signals
    
    def _check_ticker_patterns(self, ticker: str) -> Dict:
        """
        Check single ticker against all patterns
        Returns dict with score and matched patterns
        """
        patterns_found = []
        total_score = 0
        
        # Get stock data
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1y')
        info = stock.info
        
        if hist.empty:
            return {'ticker': ticker, 'total_score': 0, 'patterns': []}
        
        current_price = hist['Close'].iloc[-1]
        
        # PATTERN 1: Insider Cluster Buying
        insider_score = self._check_insider_pattern(ticker)
        if insider_score > 0:
            patterns_found.append({
                'name': 'INSIDER_CLUSTER',
                'score': insider_score,
                'description': f'Multiple insiders buying ({insider_score} points)'
            })
            total_score += insider_score
        
        # PATTERN 2: Catalyst Timing
        catalyst_score = self._check_catalyst_pattern(ticker)
        if catalyst_score > 0:
            patterns_found.append({
                'name': 'CATALYST_TIMING',
                'score': catalyst_score,
                'description': f'Upcoming catalyst ({catalyst_score} points)'
            })
            total_score += catalyst_score
        
        # PATTERN 3: Failed Breakout Reset
        breakout_data = self.breakout_detector.detect_failed_breakout(ticker)
        if breakout_data:
            score = 15 + breakout_data.get('conviction_boost', 0)
            patterns_found.append({
                'name': 'FAILED_BREAKOUT_RESET',
                'score': score,
                'description': f'Reset from high with {breakout_data["pct_from_low"]:.1f}% recovery'
            })
            total_score += score
        
        # PATTERN 4: Wounded Prey (Technical)
        tech_score = self._check_technical_pattern(hist, info)
        if tech_score > 0:
            patterns_found.append({
                'name': 'WOUNDED_PREY',
                'score': tech_score,
                'description': f'Near 52w low with volume ({tech_score} points)'
            })
            total_score += tech_score
        
        # PATTERN 5: Sector Rotation
        sector_score = self._check_sector_pattern(ticker)
        if sector_score > 0:
            patterns_found.append({
                'name': 'SECTOR_MOMENTUM',
                'score': sector_score,
                'description': f'Hot sector ({sector_score} points)'
            })
            total_score += sector_score
        
        # PATTERN 6: Short Squeeze Potential
        squeeze_score = self._check_squeeze_pattern(info)
        if squeeze_score > 0:
            patterns_found.append({
                'name': 'SHORT_SQUEEZE_SETUP',
                'score': squeeze_score,
                'description': f'High short interest ({squeeze_score} points)'
            })
            total_score += squeeze_score
        
        # PATTERN 7: Tax Loss Bounce (if applicable)
        if datetime.now().month == 1:  # January
            bounce_score = self._check_tax_loss_bounce(hist)
            if bounce_score > 0:
                patterns_found.append({
                    'name': 'TAX_LOSS_BOUNCE',
                    'score': bounce_score,
                    'description': f'January bounce candidate ({bounce_score} points)'
                })
                total_score += bounce_score
        
        # ML PREDICTION (if available)
        ml_score = 0
        ml_probability = 0
        if self.ml_available:
            try:
                pred = self.ml_predictor.predict(ticker)
                if pred and pred['probability'] >= 0.6:
                    ml_score = int(pred['probability'] * 20)  # 60% = 12 points
                    ml_probability = pred['probability']
                    patterns_found.append({
                        'name': 'ML_PREDICTION',
                        'score': ml_score,
                        'description': f'ML predicts >10% move ({pred["probability"]:.0%} probability)'
                    })
                    total_score += ml_score
            except Exception:
                pass
        
        return {
            'ticker': ticker,
            'total_score': min(total_score, 100),  # Cap at 100
            'patterns': patterns_found,
            'current_price': current_price,
            'ml_probability': ml_probability,
            'timestamp': datetime.now().isoformat()
        }
    
    def _check_insider_pattern(self, ticker: str) -> int:
        """Check for insider buying clusters"""
        try:
            # Query our insider database
            db_path = Path('data/insider_transactions.db')
            if not db_path.exists():
                return 0
            
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            # Check for recent buys (14 days)
            cutoff = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
            
            c.execute('''
                SELECT COUNT(DISTINCT insider_name), SUM(shares * price)
                FROM insider_buys
                WHERE ticker = ? AND transaction_date >= ?
            ''', (ticker, cutoff))
            
            result = c.fetchone()
            conn.close()
            
            if result:
                insider_count, total_value = result
                
                if insider_count and insider_count >= 2:
                    # Base score
                    score = 15 if insider_count == 2 else 25
                    
                    # Bonus for large value
                    if total_value and total_value > 1_000_000:
                        score += 10
                    
                    return score
        
        except Exception:
            pass
        
        return 0
    
    def _check_catalyst_pattern(self, ticker: str) -> int:
        """Check for upcoming catalysts"""
        try:
            upcoming = self.catalyst_tracker.get_upcoming_catalysts(days=60)
            
            for catalyst in upcoming:
                if catalyst.get('ticker') == ticker:
                    days_until = catalyst.get('days_until', 999)
                    
                    if days_until <= 7:
                        return 15
                    elif days_until <= 14:
                        return 10
                    elif days_until <= 30:
                        return 5
                    elif days_until <= 60:
                        return 3
        
        except Exception:
            pass
        
        return 0
    
    def _check_technical_pattern(self, hist: pd.DataFrame, info: Dict) -> int:
        """Check for wounded prey technical setup"""
        try:
            current_price = hist['Close'].iloc[-1]
            low_52w = hist['Low'].rolling(252).min().iloc[-1]
            
            pct_from_low = ((current_price - low_52w) / low_52w) * 100
            
            # Volume check
            volume_ma = hist['Volume'].rolling(10).mean().iloc[-1]
            current_volume = hist['Volume'].iloc[-1]
            volume_ratio = current_volume / volume_ma if volume_ma > 0 else 0
            
            score = 0
            
            # Wounded prey scoring
            if pct_from_low < 15:
                score += 15
            elif pct_from_low < 25:
                score += 10
            elif pct_from_low < 40:
                score += 5
            
            # Volume surge bonus
            if volume_ratio > 2.0:
                score += 5
            
            return score
        
        except Exception:
            return 0
    
    def _check_sector_pattern(self, ticker: str) -> int:
        """Check if sector is hot"""
        try:
            # Map ticker to sector
            sector_map = {
                'SMR': 'NLR',    # Nuclear
                'OKLO': 'NLR',
                'LUNR': 'ROKT',  # Space (custom)
                'RKLB': 'ROKT',
                'IONQ': 'QTUM',  # Quantum
                'QBTS': 'QTUM',
                'RGTI': 'QTUM'
            }
            
            etf = sector_map.get(ticker)
            if not etf:
                return 0
            
            # Get sector performance
            performance = self.sector_rotation.get_sector_performance([5])
            
            for sector in performance:
                if sector.get('etf') == etf:
                    pct_5d = sector.get('5d', 0)
                    
                    if pct_5d > 5:
                        return 15
                    elif pct_5d > 3:
                        return 10
                    elif pct_5d > 0:
                        return 5
        
        except Exception:
            pass
        
        return 0
    
    def _check_squeeze_pattern(self, info: Dict) -> int:
        """Check for short squeeze setup"""
        try:
            short_pct = info.get('shortPercentOfFloat', 0) * 100
            
            if short_pct > 30:
                return 15
            elif short_pct > 20:
                return 10
            elif short_pct > 15:
                return 5
        
        except Exception:
            pass
        
        return 0
    
    def _check_tax_loss_bounce(self, hist: pd.DataFrame) -> int:
        """Check for tax loss bounce setup (January only)"""
        try:
            current_price = hist['Close'].iloc[-1]
            
            # Get December high
            dec_data = hist.loc['2025-12-01':'2025-12-31']
            if dec_data.empty:
                return 0
            
            dec_high = dec_data['High'].max()
            
            # Check if down significantly from December
            drawdown = (current_price - dec_high) / dec_high
            
            if drawdown < -0.30:
                return 15
            elif drawdown < -0.20:
                return 10
        
        except Exception:
            pass
        
        return 0
    
    def generate_alert(self, signals: List[Dict], min_score: int = 60):
        """
        Generate alert for high-score setups
        Saves to file and prints to console
        """
        high_score = [s for s in signals if s['total_score'] >= min_score]
        
        if not high_score:
            print(f"\n⚠️  No setups above {min_score} points found")
            return
        
        print(f"\n{'='*70}")
        print(f"🚨 HIGH CONVICTION SETUPS (≥{min_score} points)")
        print(f"{'='*70}")
        
        for signal in high_score:
            print(f"\n{signal['ticker']} - {signal['total_score']}/100")
            print(f"  Price: ${signal['current_price']:.2f}")
            print(f"  Patterns Matched: {len(signal['patterns'])}")
            
            for pattern in signal['patterns']:
                print(f"    • {pattern['name']}: +{pattern['score']} pts - {pattern['description']}")
            
            if signal.get('ml_probability', 0) > 0:
                print(f"  ML Probability: {signal['ml_probability']:.1%}")
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        alert_file = self.alerts_dir / f'pattern_alert_{timestamp}.json'
        
        with open(alert_file, 'w') as f:
            json.dump(high_score, f, indent=2)
        
        print(f"\n💾 Alert saved: {alert_file}")
    
    def run_morning_scan(self, tickers: List[str]):
        """
        Morning scan routine
        Run before market open to find today's setups
        """
        print("\n" + "=" * 70)
        print("🐺 WOLF PACK MORNING PATTERN SCAN")
        print(f"   {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}")
        print("=" * 70)
        
        # Scan for patterns
        signals = self.scan_for_patterns(tickers)
        
        # Generate alert for top setups
        self.generate_alert(signals, min_score=60)
        
        # Print summary
        print(f"\n{'='*70}")
        print(f"📊 SCAN SUMMARY")
        print(f"{'='*70}")
        print(f"Total tickers scanned: {len(tickers)}")
        print(f"Setups found (≥50 pts): {len(signals)}")
        print(f"High conviction (≥60 pts): {len([s for s in signals if s['total_score'] >= 60])}")
        print(f"Elite setups (≥75 pts): {len([s for s in signals if s['total_score'] >= 75])}")
        
        # Top 5
        print(f"\n🎯 TOP 5 SETUPS:")
        for i, signal in enumerate(signals[:5], 1):
            print(f"   {i}. {signal['ticker']:6s} {signal['total_score']}/100 - {len(signal['patterns'])} patterns")
        
        print(f"\n{'='*70}")
        print("🐺 SCAN COMPLETE")
        print(f"{'='*70}\n")
        
        return signals


def main():
    """CLI interface"""
    scanner = RealtimePatternScanner()
    
    # Load watchlist
    watchlist_file = Path('atp_watchlists/ATP_WOLF_PACK_MASTER.csv')
    
    if watchlist_file.exists():
        import csv
        with open(watchlist_file) as f:
            reader = csv.DictReader(f)
            tickers = [row['Symbol'] for row in reader]
    else:
        tickers = ['LUNR', 'IONQ', 'SMR', 'RKLB', 'GOGO', 'SOUN', 'BBAI', 'QBTS']
    
    # Run morning scan
    scanner.run_morning_scan(tickers)


if __name__ == '__main__':
    main()
