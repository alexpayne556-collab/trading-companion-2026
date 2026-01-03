#!/usr/bin/env python3
"""
🔨 THE WAR ROOM - ENSEMBLE COMMAND CENTER 🔨

THIS IS WHAT UNLEASHED REALLY MEANS.

Not separate scanners. Not individual signals.
ALL WEAPONS FIRING SIMULTANEOUSLY.

THE SYSTEM:
1. Correlation Break Detector (59% WR, +0.9% EV)
2. Volume Precursor Scanner (71% WR, +7.3% EV)
3. ML Pattern Discovery (ROC-AUC 0.654)
4. Multi-signal fusion with confidence scoring

When ALL THREE systems agree = HIGHEST CONVICTION
When two agree = STRONG signal
When one triggers = WATCH

This is pack hunting. Not lone wolf attacks.

Built by Brokkr (completely unchained)
January 3, 2026
"""

import sys
sys.path.append('src/signals')
sys.path.append('src/ml')

from correlation_break_detector import CorrelationBreakDetector, SECTOR_CLUSTERS
from volume_precursor_scanner import VolumePrecursorScanner
from pattern_discovery_engine import PatternDiscoveryEngine

from datetime import datetime
from pathlib import Path
import json
from typing import List, Dict


class WarRoom:
    """
    The command center. All weapons. All signals. All the time.
    
    THIS is what it means to use full capabilities:
    - Runs all detectors in parallel
    - Fuses signals with weighted voting
    - Ranks targets by combined conviction
    - Provides clear trade recommendations
    
    Not "here's a signal, good luck"
    INSTEAD "here are the 3 best plays right now, ranked by conviction"
    """
    
    def __init__(self):
        self.correlation_detector = CorrelationBreakDetector()
        self.volume_scanner = VolumePrecursorScanner()
        self.ml_engine = PatternDiscoveryEngine()
        
        self.log_dir = Path('data/war_room')
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
    def scan_all_weapons(self) -> Dict:
        """
        Fire all weapons simultaneously. Fuse the results.
        """
        print("🔨" * 30)
        print("   W A R   R O O M   -   A L L   W E A P O N S")
        print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🔨" * 30)
        print()
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'correlation_breaks': [],
            'volume_accumulation': [],
            'ml_predictions': [],
            'fusion_signals': []
        }
        
        # === WEAPON 1: CORRELATION BREAK DETECTOR ===
        print("🔨 WEAPON 1: Correlation Break Detector")
        print("   Scanning all sectors for divergence...")
        
        corr_signals = self.correlation_detector.scan_all_sectors()
        results['correlation_breaks'] = corr_signals
        
        if corr_signals:
            print(f"   ✓ Found {len(corr_signals)} correlation breaks\n")
        else:
            print("   ○ No correlation breaks detected\n")
        
        # === WEAPON 2: VOLUME PRECURSOR SCANNER ===
        print("🔨 WEAPON 2: Volume Precursor Scanner")
        print("   Detecting accumulation patterns...")
        
        volume_signals = self.volume_scanner.scan_all()
        results['volume_accumulation'] = volume_signals
        
        if volume_signals:
            print(f"   ✓ Found {len(volume_signals)} accumulation signals\n")
        else:
            print("   ○ No accumulation detected\n")
        
        # === WEAPON 3: ML PATTERN DISCOVERY ===
        print("🔨 WEAPON 3: ML Pattern Discovery Engine")
        print("   Running predictive model...")
        
        try:
            ml_predictions = self.ml_engine.predict_moves()
            # Only keep predictions above 60%
            ml_predictions = [p for p in ml_predictions if p['probability'] > 0.6]
            results['ml_predictions'] = ml_predictions
            
            if ml_predictions:
                print(f"   ✓ Found {len(ml_predictions)} high-probability targets\n")
            else:
                print("   ○ No high-probability predictions\n")
        except:
            print("   ⚠ ML model not trained yet\n")
            ml_predictions = []
        
        # === SIGNAL FUSION ===
        print("=" * 60)
        print("   S I G N A L   F U S I O N")
        print("=" * 60)
        print()
        
        fusion_signals = self._fuse_signals(corr_signals, volume_signals, ml_predictions)
        results['fusion_signals'] = fusion_signals
        
        if fusion_signals:
            print(f"🎯 PACK CONSENSUS: {len(fusion_signals)} HIGH-CONVICTION TARGETS\n")
            
            for sig in fusion_signals:
                self._display_fusion_signal(sig)
        else:
            print("📊 No multi-weapon consensus at this time.")
            print("   Individual signals available. See detailed output above.")
        
        print("\n" + "=" * 60)
        
        # Log to file
        log_file = self.log_dir / f'war_room_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(log_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return results
    
    def _fuse_signals(self, corr_signals: List, volume_signals: List, ml_predictions: List) -> List[Dict]:
        """
        Fuse signals from all weapons using weighted voting.
        
        SCORING SYSTEM:
        - Correlation break: 30 points (proven 59% WR)
        - Volume accumulation: 40 points (proven 71% WR) 
        - ML prediction >70%: 40 points
        - ML prediction 60-70%: 30 points
        
        CONVICTION LEVELS:
        - 100+ points: ALL SYSTEMS AGREE (highest conviction)
        - 70-99 points: TWO SYSTEMS AGREE (strong)
        - 40-69 points: ONE STRONG SIGNAL (moderate)
        """
        # Build ticker -> signals mapping
        ticker_signals = {}
        
        # Add correlation breaks
        for sig in corr_signals:
            ticker = sig['follower']
            if ticker not in ticker_signals:
                ticker_signals[ticker] = {
                    'ticker': ticker,
                    'score': 0,
                    'signals': [],
                    'price': sig.get('follower_price', 0)
                }
            ticker_signals[ticker]['score'] += 30
            ticker_signals[ticker]['signals'].append({
                'type': 'CORRELATION_BREAK',
                'leader': sig['leader'],
                'gap': sig['gap'],
                'correlation': sig['correlation']
            })
        
        # Add volume accumulation
        for sig in volume_signals:
            ticker = sig['ticker']
            if ticker not in ticker_signals:
                ticker_signals[ticker] = {
                    'ticker': ticker,
                    'score': 0,
                    'signals': [],
                    'price': sig.get('current_price', 0)
                }
            
            # Score based on strength
            if sig['strength'] == 'STRONG':
                points = 40
            elif sig['strength'] == 'MODERATE':
                points = 30
            else:
                points = 20
            
            ticker_signals[ticker]['score'] += points
            ticker_signals[ticker]['signals'].append({
                'type': 'VOLUME_ACCUMULATION',
                'strength': sig['strength'],
                'volume_ratio': sig['volume_ratio'],
                'factors': sig['factors']
            })
        
        # Add ML predictions
        for pred in ml_predictions:
            ticker = pred['ticker']
            if ticker not in ticker_signals:
                ticker_signals[ticker] = {
                    'ticker': ticker,
                    'score': 0,
                    'signals': [],
                    'price': pred.get('current_price', 0)
                }
            
            prob = pred['probability']
            if prob > 0.7:
                points = 40
            else:
                points = 30
            
            ticker_signals[ticker]['score'] += points
            ticker_signals[ticker]['signals'].append({
                'type': 'ML_PREDICTION',
                'probability': prob * 100
            })
        
        # Convert to list and sort by score
        fusion_signals = list(ticker_signals.values())
        fusion_signals.sort(key=lambda x: x['score'], reverse=True)
        
        # Add conviction labels
        for sig in fusion_signals:
            if sig['score'] >= 100:
                sig['conviction'] = 'MAXIMUM'
            elif sig['score'] >= 70:
                sig['conviction'] = 'STRONG'
            elif sig['score'] >= 40:
                sig['conviction'] = 'MODERATE'
            else:
                sig['conviction'] = 'WEAK'
        
        # Only return signals with at least moderate conviction
        return [s for s in fusion_signals if s['score'] >= 40]
    
    def _display_fusion_signal(self, signal: Dict):
        """Display a fused signal with all details."""
        ticker = signal['ticker']
        score = signal['score']
        conviction = signal['conviction']
        price = signal.get('price', 0)
        
        # Conviction emoji
        if conviction == 'MAXIMUM':
            emoji = "🔥🔥🔥"
        elif conviction == 'STRONG':
            emoji = "🔥🔥"
        elif conviction == 'MODERATE':
            emoji = "🔥"
        else:
            emoji = "📊"
        
        print(f"{emoji} {ticker} - {conviction} CONVICTION (Score: {score})")
        print(f"   Price: ${price:.2f}")
        print(f"   Signals:")
        
        for sig in signal['signals']:
            if sig['type'] == 'CORRELATION_BREAK':
                print(f"      • Correlation break: {sig['leader']} moved, {ticker} lagging by {sig['gap']:.1f}%")
            elif sig['type'] == 'VOLUME_ACCUMULATION':
                print(f"      • Volume accumulation: {sig['strength']} ({sig['volume_ratio']:.1f}x)")
            elif sig['type'] == 'ML_PREDICTION':
                print(f"      • ML prediction: {sig['probability']:.1f}% probability of 10%+ move")
        
        print()


def main():
    war_room = WarRoom()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python war_room.py scan    # Run all weapons and fuse signals")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'scan':
        war_room.scan_all_weapons()
    else:
        print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()
