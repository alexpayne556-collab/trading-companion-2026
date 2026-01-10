#!/usr/bin/env python3
"""
🐺 WOLF PACK RESEARCH FRAMEWORK
Master class for discovering trading edge through systematic testing.

All patterns must be verified before becoming scanners.
No assumptions. No hope. DATA ONLY.

Built by: BROKKR (GitHub Copilot)
Specification by: TYR + FENRIR
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import os
from typing import Dict, List, Optional, Tuple
warnings.filterwarnings('ignore')

# =============================================================================
# TICKER UNIVERSE (FROM TYR + FENRIR SPEC)
# =============================================================================

WATCHLIST = {
    'nuclear_tier_a': ['DNN', 'URG', 'UEC', 'UUUU', 'SMR'],
    'nuclear_tier_b': ['CCJ', 'OKLO', 'LEU', 'NXE'],
    'nuclear_tier_c': ['URNM', 'URA', 'UROY'],
    'nuclear_tier_d': ['BWXT', 'NNE', 'ASPI', 'PDN', 'BOE', 'ISO'],
    
    'ai_infra_tier_a': ['CIFR', 'WULF', 'BTBT', 'HUT', 'CLSK', 'CORZ'],
    'ai_infra_tier_b': ['APLD', 'IREN', 'MARA', 'RIOT', 'VRT', 'MU'],
    'ai_infra_tier_c': ['MRVL', 'AVGO', 'ANET', 'SMCI', 'DELL', 'CRWV', 'NBIS'],
    
    'space_defense_tier_a': ['MNTS', 'SPCE', 'SATL', 'PL', 'RCAT', 'LUNR', 'KTOS'],
    'space_defense_tier_b': ['RKLB', 'AVAV', 'ASTS'],
    'space_defense_tier_c': ['LMT', 'NOC', 'RTX', 'GD', 'BA'],
    'space_defense_tier_d': ['RDW', 'IRDM', 'VSAT', 'LHX', 'HII', 'TXT'],
    
    'power_tier_a': ['PCG', 'EXC', 'XEL', 'D'],
    'power_tier_b': ['CEG', 'VST', 'NEE', 'NRG', 'SO', 'ETN'],
    
    'rare_earth_tier_a': ['LAC', 'PLL', 'MP'],
    'rare_earth_tier_b': ['ALB', 'SQM']
}

# Flatten into sector lists
NUCLEAR = (WATCHLIST['nuclear_tier_a'] + WATCHLIST['nuclear_tier_b'] + 
           WATCHLIST['nuclear_tier_c'] + WATCHLIST['nuclear_tier_d'])
AI_INFRA = (WATCHLIST['ai_infra_tier_a'] + WATCHLIST['ai_infra_tier_b'] + 
            WATCHLIST['ai_infra_tier_c'])
SPACE_DEFENSE = (WATCHLIST['space_defense_tier_a'] + WATCHLIST['space_defense_tier_b'] + 
                 WATCHLIST['space_defense_tier_c'] + WATCHLIST['space_defense_tier_d'])
POWER = WATCHLIST['power_tier_a'] + WATCHLIST['power_tier_b']
RARE_EARTH = WATCHLIST['rare_earth_tier_a'] + WATCHLIST['rare_earth_tier_b']

ALL_TICKERS = list(set(NUCLEAR + AI_INFRA + SPACE_DEFENSE + POWER + RARE_EARTH))

# =============================================================================
# CORE FRAMEWORK
# =============================================================================

class WolfPackResearch:
    """
    Master research class for discovering trading edge.
    
    Philosophy:
    - Test everything
    - Trust nothing until verified
    - Minimum 20 samples for validation
    - Win rate > 60% to be tradeable
    - Risk/reward > 1.5:1
    """
    
    def __init__(self, tickers: Optional[List[str]] = None):
        """Initialize with ticker list or use default watchlist"""
        self.tickers = tickers if tickers else ALL_TICKERS
        self.data = {}
        self.results_dir = 'research_results'
        
        # Create results directory
        os.makedirs(self.results_dir, exist_ok=True)
        
        print(f"🐺 WOLF PACK RESEARCH INITIALIZED")
        print(f"   Tickers: {len(self.tickers)}")
        print(f"   Results: {self.results_dir}/")
        
    def load_data(self, period='180d', interval='1d'):
        """
        Load price data for all tickers
        
        Args:
            period: '180d', '1y', '2y', etc.
            interval: '1d', '1h', '5m', etc.
        """
        print(f"\n📊 LOADING DATA")
        print(f"   Period: {period}")
        print(f"   Interval: {interval}\n")
        
        failed = []
        for i, ticker in enumerate(self.tickers, 1):
            try:
                df = yf.download(ticker, period=period, interval=interval, progress=False)
                if not df.empty:
                    self.data[ticker] = df
                    print(f"  [{i}/{len(self.tickers)}] ✓ {ticker:<6} {len(df)} bars")
                else:
                    failed.append(ticker)
                    print(f"  [{i}/{len(self.tickers)}] ✗ {ticker:<6} No data")
            except Exception as e:
                failed.append(ticker)
                print(f"  [{i}/{len(self.tickers)}] ✗ {ticker:<6} {str(e)[:50]}")
        
        print(f"\n✅ Loaded: {len(self.data)}/{len(self.tickers)} tickers")
        if failed:
            print(f"❌ Failed: {', '.join(failed)}")
        
        return len(self.data)
    
    def calculate_rsi(self, ticker: str, period: int = 14) -> pd.DataFrame:
        """Calculate RSI for a ticker"""
        if ticker not in self.data:
            return None
            
        df = self.data[ticker].copy()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        return df
    
    def save_results(self, data: pd.DataFrame, filename: str):
        """Save results to CSV"""
        filepath = os.path.join(self.results_dir, filename)
        data.to_csv(filepath, index=False)
        print(f"💾 Saved: {filepath}")
        return filepath
    
    def get_sector_tickers(self, sector: str) -> List[str]:
        """Get tickers by sector"""
        sector_map = {
            'nuclear': NUCLEAR,
            'ai_infra': AI_INFRA,
            'ai': AI_INFRA,
            'space': SPACE_DEFENSE,
            'defense': SPACE_DEFENSE,
            'power': POWER,
            'utilities': POWER,
            'rare_earth': RARE_EARTH
        }
        return sector_map.get(sector.lower(), [])

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_win_rate(series: pd.Series, threshold: float = 0.0) -> float:
    """Calculate win rate (% > threshold)"""
    if len(series) == 0:
        return 0.0
    return (series > threshold).sum() / len(series) * 100

def calculate_risk_reward(gains: pd.Series, losses: pd.Series) -> float:
    """Calculate average gain / average loss ratio"""
    avg_gain = gains[gains > 0].mean() if len(gains[gains > 0]) > 0 else 0
    avg_loss = abs(losses[losses < 0].mean()) if len(losses[losses < 0]) > 0 else 1
    return avg_gain / avg_loss if avg_loss != 0 else 0

def format_percent(value: float) -> str:
    """Format as percentage"""
    return f"{value:+.2f}%"

def format_money(value: float) -> str:
    """Format as money"""
    return f"${value:,.2f}"

# =============================================================================
# VALIDATION CRITERIA
# =============================================================================

class ValidationCriteria:
    """
    Pattern validation thresholds from TYR spec
    """
    MIN_WIN_RATE = 60.0  # Minimum 60% win rate
    MIN_SAMPLES = 20      # Minimum 20 occurrences
    MIN_RISK_REWARD = 1.5 # Minimum 1.5:1 R/R
    
    @staticmethod
    def is_valid_edge(win_rate: float, samples: int, risk_reward: float) -> Tuple[bool, str]:
        """Check if pattern meets validation criteria"""
        if samples < ValidationCriteria.MIN_SAMPLES:
            return False, f"Insufficient samples ({samples} < {ValidationCriteria.MIN_SAMPLES})"
        
        if win_rate < ValidationCriteria.MIN_WIN_RATE:
            return False, f"Low win rate ({win_rate:.1f}% < {ValidationCriteria.MIN_WIN_RATE}%)"
        
        if risk_reward < ValidationCriteria.MIN_RISK_REWARD:
            return False, f"Poor risk/reward ({risk_reward:.2f} < {ValidationCriteria.MIN_RISK_REWARD})"
        
        return True, "VALIDATED EDGE"

# =============================================================================
# RESEARCH PROJECTS (Modules imported separately)
# =============================================================================

"""
Research modules (to be built):
- project_1_leader_laggard.py
- project_2_volume_divergence.py
- project_3_gap_study.py
- project_4_rsi_optimization.py
- project_5_catalyst_timing.py
- project_6_time_of_day.py
- project_7_overnight_gap.py
- project_8_insider_buying.py
- project_9_sector_rotation.py
- project_10_earnings_momentum.py
- project_11_short_squeeze.py
- project_12_support_resistance.py
"""

if __name__ == '__main__':
    print("="*80)
    print("🐺 WOLF PACK RESEARCH FRAMEWORK")
    print("="*80)
    print("\nFramework loaded. Import and use in research projects.")
    print("\nExample:")
    print("  from wolf_pack_research import WolfPackResearch, NUCLEAR, AI_INFRA")
    print("  research = WolfPackResearch(NUCLEAR)")
    print("  research.load_data(period='180d')")
    print("\n🐺 LLHR. AWOOOO.")
