"""
🐺 WOLF PACK SIGNALS MODULE
All validated trading signals in one place
Import this to use the signals anywhere
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class Signal:
    """A trading signal"""
    ticker: str
    signal_type: str
    strength: str  # 'STRONG', 'MODERATE', 'WEAK'
    price: float
    date: str
    metrics: Dict
    description: str


class WolfSignals:
    """
    The 3 validated edges:
    1. Wolf Signal (p=0.023, +37.87% avg, 78% WR)
    2. Pre-Run Predictor (p=0.0000, +17.27% avg, 58% WR)
    3. Capitulation Hunter (p=0.004, +19.95% avg, 58% WR)
    """
    
    @staticmethod
    def calculate_metrics(close: np.ndarray, high: np.ndarray, 
                         low: np.ndarray, volume: np.ndarray) -> Dict:
        """Calculate all metrics needed for signals"""
        i = len(close) - 1
        
        if i < 25:
            return None
        
        # Base volume (20-day avg excluding last 5)
        base_vol = np.mean(volume[max(0, i-20):i])
        
        # Relative volume today
        rel_vol = volume[i] / base_vol if base_vol > 0 else 1
        
        # Daily change
        prev_close = close[i-1] if i > 0 else close[i]
        daily_chg = ((close[i] - prev_close) / prev_close) * 100
        
        # Up/down volume ratio (20 days)
        up_vol = sum(volume[j] for j in range(max(0, i-20), i) if close[j] > close[j-1])
        down_vol = sum(volume[j] for j in range(max(0, i-20), i) if close[j] < close[j-1])
        vol_ratio = up_vol / down_vol if down_vol > 0 else 1
        
        # Distance from 20-day high
        high_20 = max(high[max(0, i-20):i]) if i > 0 else high[i]
        pct_from_high = ((close[i] - high_20) / high_20) * 100
        
        # Days since high
        days_from_high = 0
        for j in range(min(20, i)):
            if high[i-j-1] == high_20:
                days_from_high = j
                break
        
        # 5-day price change
        price_5d = ((close[i] - close[max(0, i-5)]) / close[max(0, i-5)]) * 100 if i >= 5 else 0
        
        # 5-day volume ratio
        prerun_vol = np.mean(volume[max(0, i-5):i])
        vol_ratio_prerun = prerun_vol / base_vol if base_vol > 0 else 1
        
        # CLV calculations
        clvs = []
        for k in range(max(0, i-5), i):
            day_range = high[k] - low[k]
            if day_range > 0:
                clvs.append((close[k] - low[k]) / day_range)
            else:
                clvs.append(0.5)
        avg_clv = np.mean(clvs) if clvs else 0.5
        
        # Today's CLV
        day_range = high[i] - low[i]
        clv_today = (close[i] - low[i]) / day_range if day_range > 0 else 0.5
        
        return {
            'price': float(close[i]),
            'rel_vol': float(rel_vol),
            'daily_chg': float(daily_chg),
            'vol_ratio': float(vol_ratio),
            'pct_from_high': float(pct_from_high),
            'days_from_high': int(days_from_high),
            'price_5d': float(price_5d),
            'vol_ratio_prerun': float(vol_ratio_prerun),
            'avg_clv': float(avg_clv),
            'clv_today': float(clv_today),
            'base_vol': base_vol
        }
    
    @staticmethod
    def check_wolf_signal(metrics: Dict) -> Optional[Signal]:
        """
        WOLF SIGNAL: Institutions accumulating during healthy uptrend
        - Volume spike > 2x
        - Flat price (< 2%)
        - Volume ratio > 2.5
        - Near highs (< 5 days)
        
        Stats: p=0.023, +37.87% avg, 77.8% WR
        """
        if metrics is None:
            return None
        
        conditions = [
            metrics['rel_vol'] > 2.0,
            abs(metrics['daily_chg']) < 2,
            metrics['vol_ratio'] > 2.5,
            metrics['days_from_high'] < 5
        ]
        
        if all(conditions):
            # Determine strength
            if metrics['vol_ratio'] > 4.0 and metrics['rel_vol'] > 3.0:
                strength = 'STRONG'
            elif metrics['vol_ratio'] > 3.0:
                strength = 'MODERATE'
            else:
                strength = 'WEAK'
            
            return Signal(
                ticker='',
                signal_type='WOLF',
                strength=strength,
                price=metrics['price'],
                date='',
                metrics=metrics,
                description=f"Volume spike {metrics['rel_vol']:.1f}x on flat day, "
                           f"vol ratio {metrics['vol_ratio']:.1f}, near highs"
            )
        return None
    
    @staticmethod
    def check_prerun_predictor(metrics: Dict) -> Optional[Signal]:
        """
        PRE-RUN PREDICTOR: 5 signatures before explosions
        - 5d volume ratio > 1.0
        - Signal day volume > 1.0
        - 5d price > -2%
        - 5d CLV > 0.45
        - Up/down ratio > 1.2
        
        Stats: p=0.0000, +17.27% avg (5/5), 57.9% WR
        """
        if metrics is None:
            return None
        
        score = 0
        if metrics['vol_ratio_prerun'] > 1.0:
            score += 1
        if metrics['rel_vol'] > 1.0:
            score += 1
        if metrics['price_5d'] > -2:
            score += 1
        if metrics['avg_clv'] > 0.45:
            score += 1
        if metrics['vol_ratio'] > 1.2:
            score += 1
        
        if score >= 4:
            if score == 5:
                strength = 'STRONG'
            else:
                strength = 'MODERATE'
            
            return Signal(
                ticker='',
                signal_type='PRE-RUN',
                strength=strength,
                price=metrics['price'],
                date='',
                metrics={**metrics, 'score': score},
                description=f"Pre-run score {score}/5, "
                           f"5d vol {metrics['vol_ratio_prerun']:.1f}x, CLV {metrics['avg_clv']:.2f}"
            )
        return None
    
    @staticmethod
    def check_capitulation(metrics: Dict) -> Optional[Signal]:
        """
        CAPITULATION HUNTER: Buy red spikes when wounded
        - Down 15-40% from 20d high
        - Volume spike > 1.5x
        - CLV < 0.5 (red day)
        
        Stats: p=0.004, +19.95% avg, 58% WR
        """
        if metrics is None:
            return None
        
        conditions = [
            -40 <= metrics['pct_from_high'] <= -15,
            metrics['rel_vol'] > 1.5,
            metrics['clv_today'] < 0.5
        ]
        
        if all(conditions):
            # Stronger if more red and more volume
            if metrics['clv_today'] < 0.2 and metrics['rel_vol'] > 2.5:
                strength = 'STRONG'
            elif metrics['clv_today'] < 0.3 or metrics['rel_vol'] > 2.0:
                strength = 'MODERATE'
            else:
                strength = 'WEAK'
            
            return Signal(
                ticker='',
                signal_type='CAPITULATION',
                strength=strength,
                price=metrics['price'],
                date='',
                metrics=metrics,
                description=f"Wounded {metrics['pct_from_high']:.0f}% from high, "
                           f"red spike {metrics['rel_vol']:.1f}x vol, CLV {metrics['clv_today']:.2f}"
            )
        return None
    
    @staticmethod
    def check_volume_alert(metrics: Dict) -> Optional[Signal]:
        """
        VOLUME ALERT: Catch any unusual volume (wide net)
        - Volume > 2x average
        """
        if metrics is None:
            return None
        
        if metrics['rel_vol'] > 2.0:
            if metrics['rel_vol'] > 5.0:
                strength = 'STRONG'
            elif metrics['rel_vol'] > 3.0:
                strength = 'MODERATE'
            else:
                strength = 'WEAK'
            
            direction = "UP" if metrics['daily_chg'] > 0 else "DOWN"
            
            return Signal(
                ticker='',
                signal_type='VOLUME',
                strength=strength,
                price=metrics['price'],
                date='',
                metrics=metrics,
                description=f"Volume spike {metrics['rel_vol']:.1f}x, "
                           f"price {direction} {abs(metrics['daily_chg']):.1f}%"
            )
        return None
    
    @classmethod
    def scan_ticker(cls, close: np.ndarray, high: np.ndarray,
                   low: np.ndarray, volume: np.ndarray,
                   ticker: str, date: str) -> List[Signal]:
        """Scan a ticker for all signals"""
        signals = []
        
        metrics = cls.calculate_metrics(close, high, low, volume)
        if metrics is None:
            return signals
        
        # Check each signal type
        wolf = cls.check_wolf_signal(metrics)
        if wolf:
            wolf.ticker = ticker
            wolf.date = date
            signals.append(wolf)
        
        prerun = cls.check_prerun_predictor(metrics)
        if prerun:
            prerun.ticker = ticker
            prerun.date = date
            signals.append(prerun)
        
        cap = cls.check_capitulation(metrics)
        if cap:
            cap.ticker = ticker
            cap.date = date
            signals.append(cap)
        
        vol = cls.check_volume_alert(metrics)
        if vol:
            vol.ticker = ticker
            vol.date = date
            signals.append(vol)
        
        return signals


class HerdScanner:
    """
    Wide-net scanner for catching big moves
    Scans a larger universe for unusual activity
    """
    
    QUANTUM = ['IONQ', 'RGTI', 'QBTS', 'ARQQ', 'QUBT']
    SPACE = ['LUNR', 'RCAT', 'ASTS', 'RDW', 'MNTS', 'BKSY']
    AI_TECH = ['SOUN', 'BBAI', 'AI', 'PLTR', 'PATH']
    BIOTECH = ['MDGL', 'MRNA', 'NVAX', 'BNTX']
    MEME = ['GME', 'AMC', 'BBBY', 'KOSS']
    REPEAT_RUNNERS = ['SIDU', 'RGTI', 'QBTS', 'RCAT', 'LUNR', 'ASTS', 'IONQ']
    
    @classmethod
    def get_all_tickers(cls) -> List[str]:
        """Get all tickers to scan"""
        all_tickers = set()
        all_tickers.update(cls.QUANTUM)
        all_tickers.update(cls.SPACE)
        all_tickers.update(cls.AI_TECH)
        all_tickers.update(cls.BIOTECH)
        all_tickers.update(cls.MEME)
        all_tickers.update(cls.REPEAT_RUNNERS)
        return list(all_tickers)
    
    @classmethod
    def get_sector(cls, ticker: str) -> str:
        """Get sector for a ticker"""
        if ticker in cls.QUANTUM:
            return 'QUANTUM'
        elif ticker in cls.SPACE:
            return 'SPACE'
        elif ticker in cls.AI_TECH:
            return 'AI/TECH'
        elif ticker in cls.BIOTECH:
            return 'BIOTECH'
        elif ticker in cls.MEME:
            return 'MEME'
        return 'OTHER'
