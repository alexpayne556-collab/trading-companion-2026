#!/usr/bin/env python3
"""
🐺 TACTICAL SCANNERS - HUNT LIKE A WOLF
====================================

Not random patterns. SPECIFIC SITUATIONS that cause 10-20% moves.

Wolves don't attack randomly. They study the herd for:
- The Wounded (crushed, volume dying, capitulation over)
- The Divergent (moving different from the pack - hidden strength)
- The Exposed (small float, low liquidity, moves FAST)
- The Follower (lagging behind the leader - catches up)

WHAT CAUSES BIG MOVES:
1. Information Asymmetry - insiders accumulating before news
2. Forced Buying - shorts covering, gamma squeeze
3. Supply Exhaustion - float absorbed, catalyst = moon
4. Herd Stampede - narrative catches fire, FOMO

THE 5 TACTICAL HUNTS:
1. Leader-Follower Lag - When IONQ moves, RGTI follows (buy the lag)
2. Divergence Sniff - Sector down, one stock flat = accumulation
3. Squeeze Stalker - High short + low float + rising vol = powder keg
4. Second Day Momentum - Day 1 surprise, Day 2 predictable continuation
5. Wounded Prey Recovery - Volume spike after capitulation = bottom

From Brokkr, Tyr, and Fenrir - January 3, 2026
AWOOOO 🐺
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# UNIVERSE - All stocks we hunt
# ============================================================================

UNIVERSE = {
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ', 'LAES'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'BKSY', 'MNTS', 'ASTS', 'SPIR', 'PL', 'GSAT', 'SIDU', 'SATL', 'IRDM', 'VSAT'],
    'NUCLEAR': ['LEU', 'CCJ', 'UUUU', 'UEC', 'SMR', 'OKLO', 'DNN', 'NXE', 'LTBR', 'CEG', 'TLN', 'VST'],
    'BATTERY_METALS': ['MP', 'LAC', 'ALB', 'FCX', 'AG', 'HL', 'KGC'],
    'AI_INFRA': ['SMCI', 'DELL', 'HPE', 'NTAP', 'PSTG', 'WDC', 'STX', 'ANET'],
    'MEMORY': ['MU', 'WDC', 'STX', 'PSTG', 'NTAP', 'SMCI'],
    'SEMICONDUCTORS': ['NVDA', 'AMD', 'ARM', 'TSM', 'ASML', 'INTC', 'AVGO', 'QCOM', 'MRVL', 'AMAT', 'LRCX'],
    'SPATIAL': ['META', 'AAPL', 'GOOGL', 'MSFT', 'SNAP'],
    'ROBOTICS': ['TER', 'ZBRA', 'SYM', 'ROK', 'DE', 'ISRG'],
    'DEFENSE_AI': ['PLTR', 'ARLP', 'AVAV', 'LMT', 'NOC', 'GD', 'RTX'],
    'TAX_BOUNCE': ['IONQ', 'RGTI', 'QBTS', 'LUNR', 'RKLB', 'ASTS', 'SIDU', 'MNTS'],
    'CRYPTO': ['COIN', 'MARA', 'RIOT', 'CLSK', 'CIFR'],
    'FINTECH': ['SOFI', 'AFRM', 'UPST', 'SQ', 'PYPL', 'NU'],
    'BIOTECH': ['CRSP', 'EDIT', 'NTLA', 'BEAM', 'VERV', 'RXRX', 'SDGR'],
    'EV_HYDROGEN': ['TSLA', 'RIVN', 'LCID', 'PLUG', 'FCEL', 'BE', 'BLNK', 'CHPT']
}

SECTOR_LEADERS = {
    'QUANTUM': 'IONQ',
    'SPACE': 'RKLB',
    'NUCLEAR': 'CCJ',
    'AI_INFRA': 'NVDA',
    'CRYPTO': 'COIN'
}

# ============================================================================
# DATA FETCHING
# ============================================================================

def fetch_data(tickers: List[str], period: str = '6mo') -> Dict[str, pd.DataFrame]:
    """Fetch price data for multiple tickers"""
    data = {}
    
    for ticker in tickers:
        try:
            df = yf.download(ticker, period=period, progress=False)
            if not df.empty:
                # Handle multi-level columns from yfinance
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                data[ticker] = df
        except:
            continue
    
    return data

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add technical indicators to dataframe"""
    
    # Price changes
    df['pct_change_1d'] = df['Close'].pct_change() * 100
    df['pct_change_3d'] = df['Close'].pct_change(3) * 100
    df['pct_change_5d'] = df['Close'].pct_change(5) * 100
    df['pct_change_10d'] = df['Close'].pct_change(10) * 100
    
    # Volume relative to average
    df['avg_vol_20d'] = df['Volume'].rolling(20).mean()
    df['rel_vol'] = df['Volume'] / df['avg_vol_20d']
    df['vol_spike'] = df['rel_vol'] > 2.0
    
    # Distance from highs/lows
    df['high_10d'] = df['High'].rolling(10).max()
    df['low_10d'] = df['Low'].rolling(10).min()
    df['dist_from_high_10d'] = ((df['Close'] - df['high_10d']) / df['high_10d']) * 100
    df['dist_from_low_10d'] = ((df['Close'] - df['low_10d']) / df['low_10d']) * 100
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # CLV (Close Location Value)
    df['clv'] = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
    df['clv'] = df['clv'].fillna(0)
    df['clv_3d_avg'] = df['clv'].rolling(3).mean()
    
    return df

# ============================================================================
# HUNT #1: LEADER-FOLLOWER LAG
# ============================================================================

def hunt_leader_follower_lag(data: Dict[str, pd.DataFrame], lookback: int = 5) -> List[Dict]:
    """
    When the sector leader moves big, followers often lag 1-2 days before catching up.
    
    THE PLAY: When leader is up 5%+ and follower is flat/underperforming, buy the follower.
    """
    signals = []
    
    for sector, leader_ticker in SECTOR_LEADERS.items():
        if leader_ticker not in data:
            continue
        
        leader_df = data[leader_ticker]
        if len(leader_df) < lookback:
            continue
        
        # Check if leader had a big move in last 5 days
        recent_leader_move = leader_df['pct_change_1d'].iloc[-lookback:].max()
        
        if recent_leader_move > 5.0:  # Leader moved 5%+
            # Check followers in same sector
            sector_tickers = UNIVERSE.get(sector, [])
            
            for follower in sector_tickers:
                if follower == leader_ticker or follower not in data:
                    continue
                
                follower_df = data[follower]
                if len(follower_df) < lookback:
                    continue
                
                # Calculate lag: leader moved big, follower didn't
                follower_move = follower_df['pct_change_1d'].iloc[-lookback:].max()
                lag_amount = recent_leader_move - follower_move
                
                if lag_amount > 3.0:  # Follower is lagging by 3%+
                    signals.append({
                        'hunt': 'LEADER_FOLLOWER_LAG',
                        'ticker': follower,
                        'sector': sector,
                        'leader': leader_ticker,
                        'leader_move': round(recent_leader_move, 2),
                        'follower_move': round(follower_move, 2),
                        'lag_amount': round(lag_amount, 2),
                        'thesis': f"{leader_ticker} up {recent_leader_move:.1f}%, {follower} only {follower_move:.1f}% - should catch up",
                        'current_price': round(follower_df['Close'].iloc[-1], 2)
                    })
    
    return signals

# ============================================================================
# HUNT #2: DIVERGENCE SNIFF
# ============================================================================

def hunt_divergence(data: Dict[str, pd.DataFrame], lookback: int = 5) -> List[Dict]:
    """
    When sector is down but one stock is flat/up = someone is accumulating.
    
    THE PLAY: Buy the stock showing relative strength while sector bleeds.
    """
    signals = []
    
    for sector, tickers in UNIVERSE.items():
        # Calculate sector average performance
        sector_returns = []
        valid_tickers = []
        
        for ticker in tickers:
            if ticker in data and len(data[ticker]) >= lookback:
                recent_return = data[ticker]['pct_change_5d'].iloc[-1]
                if not np.isnan(recent_return):
                    sector_returns.append(recent_return)
                    valid_tickers.append(ticker)
        
        if len(sector_returns) < 3:  # Need at least 3 stocks for sector average
            continue
        
        sector_avg = np.mean(sector_returns)
        
        # Find divergent stocks
        if sector_avg < -3.0:  # Sector is down 3%+
            for i, ticker in enumerate(valid_tickers):
                ticker_return = sector_returns[i]
                divergence = ticker_return - sector_avg
                
                if divergence > 5.0:  # Stock is 5%+ stronger than sector
                    df = data[ticker]
                    
                    # Check if volume is rising (accumulation)
                    recent_vol = df['rel_vol'].iloc[-3:].mean()
                    
                    if recent_vol > 1.2:  # Volume above average
                        signals.append({
                            'hunt': 'DIVERGENCE_SNIFF',
                            'ticker': ticker,
                            'sector': sector,
                            'sector_avg': round(sector_avg, 2),
                            'ticker_return': round(ticker_return, 2),
                            'divergence': round(divergence, 2),
                            'rel_vol': round(recent_vol, 2),
                            'thesis': f"Sector down {sector_avg:.1f}%, {ticker} showing strength (+{divergence:.1f}% divergence)",
                            'current_price': round(df['Close'].iloc[-1], 2)
                        })
    
    return signals

# ============================================================================
# HUNT #3: SQUEEZE STALKER
# ============================================================================

def hunt_squeeze_candidates(data: Dict[str, pd.DataFrame]) -> List[Dict]:
    """
    High short interest + Low float + Rising volume = POWDER KEG
    
    We don't predict WHEN it explodes. We identify which CAN explode.
    THE PLAY: Build watchlist. Wait for volume spike. Pounce.
    """
    signals = []
    
    # Short interest data (would need real-time API in production)
    # For now, use volume acceleration as proxy for squeeze potential
    
    for ticker, df in data.items():
        if len(df) < 20:
            continue
        
        # Volume acceleration
        vol_recent = df['Volume'].iloc[-5:].mean()
        vol_baseline = df['Volume'].iloc[-20:-5].mean()
        
        if vol_baseline == 0:
            continue
        
        vol_acceleration = (vol_recent / vol_baseline)
        
        # Price compression near highs
        current_price = df['Close'].iloc[-1]
        high_20d = df['High'].rolling(20).max().iloc[-1]
        dist_from_high = ((current_price - high_20d) / high_20d) * 100
        
        # Squeeze indicators
        if vol_acceleration > 1.5 and dist_from_high > -10:  # Volume rising, near highs
            
            # Check for tightening range (coiling)
            range_recent = (df['High'].iloc[-5:] - df['Low'].iloc[-5:]).mean()
            range_avg = (df['High'].iloc[-25:-5] - df['Low'].iloc[-25:-5]).mean()
            range_compression = range_recent / range_avg if range_avg > 0 else 0
            
            if range_compression < 0.8:  # Tightening
                signals.append({
                    'hunt': 'SQUEEZE_STALKER',
                    'ticker': ticker,
                    'vol_acceleration': round(vol_acceleration, 2),
                    'dist_from_high': round(dist_from_high, 2),
                    'range_compression': round(range_compression, 2),
                    'thesis': f"Volume accelerating {vol_acceleration:.1f}x, range tightening - coiled spring",
                    'current_price': round(current_price, 2)
                })
    
    return signals

# ============================================================================
# HUNT #4: SECOND DAY MOMENTUM
# ============================================================================

def hunt_second_day_momentum(data: Dict[str, pd.DataFrame]) -> List[Dict]:
    """
    After a big Day 1 move with high volume, Day 2 often continues.
    
    THE PLAY: Don't chase Day 1. Position for Day 2 continuation.
    """
    signals = []
    
    for ticker, df in data.items():
        if len(df) < 10:
            continue
        
        # Check yesterday (Day 1)
        day1_return = df['pct_change_1d'].iloc[-2]  # Yesterday
        day1_vol = df['rel_vol'].iloc[-2]
        
        # Big move with volume = Day 1 breakout
        if day1_return > 5.0 and day1_vol > 2.0:
            
            # Check if today (Day 2) is gapping up or continuing
            today_return = df['pct_change_1d'].iloc[-1]
            
            if today_return > 0:  # Continuing
                signals.append({
                    'hunt': 'SECOND_DAY_MOMENTUM',
                    'ticker': ticker,
                    'day1_return': round(day1_return, 2),
                    'day1_vol': round(day1_vol, 2),
                    'day2_return': round(today_return, 2),
                    'thesis': f"Day 1: +{day1_return:.1f}% on {day1_vol:.1f}x vol. Day 2 continuing momentum.",
                    'current_price': round(df['Close'].iloc[-1], 2)
                })
            elif today_return > -2.0:  # Not fading much
                signals.append({
                    'hunt': 'SECOND_DAY_MOMENTUM',
                    'ticker': ticker,
                    'day1_return': round(day1_return, 2),
                    'day1_vol': round(day1_vol, 2),
                    'day2_return': round(today_return, 2),
                    'thesis': f"Day 1: +{day1_return:.1f}% on {day1_vol:.1f}x vol. Day 2 consolidating - watch for continuation.",
                    'current_price': round(df['Close'].iloc[-1], 2)
                })
    
    return signals

# ============================================================================
# HUNT #5: WOUNDED PREY RECOVERY
# ============================================================================

def hunt_wounded_recovery(data: Dict[str, pd.DataFrame]) -> List[Dict]:
    """
    Stock crushed 30-50% from highs. Volume DIES. Then volume SPIKES.
    
    THE PLAY: Volume spike after capitulation = smart money bottom fishing.
    """
    signals = []
    
    for ticker, df in data.items():
        if len(df) < 60:
            continue
        
        # Calculate drawdown from 52-week high
        high_52w = df['High'].rolling(252, min_periods=60).max().iloc[-1]
        current_price = df['Close'].iloc[-1]
        drawdown = ((current_price - high_52w) / high_52w) * 100
        
        # Wounded = down 25%+ from highs
        if drawdown < -25:
            
            # Check if volume died (sellers exhausted)
            vol_avg_60d = df['Volume'].iloc[-60:-5].mean()
            vol_avg_recent_pre = df['Volume'].iloc[-10:-3].mean()
            
            if vol_avg_60d > 0:
                vol_dried_up = (vol_avg_recent_pre / vol_avg_60d) < 0.7  # Volume dropped 30%
            else:
                vol_dried_up = False
            
            # Check for recent volume spike (recovery)
            vol_recent = df['Volume'].iloc[-3:].mean()
            vol_spike = (vol_recent / vol_avg_60d) > 1.8 if vol_avg_60d > 0 else False
            
            # Price starting to recover
            recent_return = df['pct_change_5d'].iloc[-1]
            
            if vol_dried_up and vol_spike and recent_return > -5:
                signals.append({
                    'hunt': 'WOUNDED_PREY_RECOVERY',
                    'ticker': ticker,
                    'drawdown': round(drawdown, 2),
                    'vol_spike_ratio': round(vol_recent / vol_avg_60d, 2) if vol_avg_60d > 0 else 0,
                    'recent_return': round(recent_return, 2),
                    'thesis': f"Down {abs(drawdown):.1f}% from highs, volume dried up, now spiking - potential bottom",
                    'current_price': round(current_price, 2)
                })
    
    return signals

# ============================================================================
# MAIN TACTICAL SCANNER
# ============================================================================

def run_all_hunts() -> Dict[str, List[Dict]]:
    """Run all 5 tactical hunts and return results"""
    
    print("\n" + "="*80)
    print("🐺 TACTICAL SCANNER - HUNTING THE HERD")
    print("="*80)
    print("Fetching market data...")
    
    # Get all unique tickers
    all_tickers = list(set([t for tickers in UNIVERSE.values() for t in tickers]))
    
    # Fetch data
    data = fetch_data(all_tickers, period='6mo')
    
    # Calculate indicators for each ticker
    for ticker in data:
        data[ticker] = calculate_technical_indicators(data[ticker])
    
    print(f"✓ Loaded {len(data)} tickers\n")
    
    # Run all hunts
    results = {
        'LEADER_FOLLOWER_LAG': hunt_leader_follower_lag(data),
        'DIVERGENCE_SNIFF': hunt_divergence(data),
        'SQUEEZE_STALKER': hunt_squeeze_candidates(data),
        'SECOND_DAY_MOMENTUM': hunt_second_day_momentum(data),
        'WOUNDED_PREY_RECOVERY': hunt_wounded_recovery(data)
    }
    
    return results

def display_results(results: Dict[str, List[Dict]]):
    """Display tactical scanner results"""
    
    print("\n" + "="*80)
    print("🎯 HUNT RESULTS")
    print("="*80)
    
    for hunt_name, signals in results.items():
        print(f"\n{'='*80}")
        print(f"🐺 {hunt_name}")
        print(f"{'='*80}")
        
        if not signals:
            print("No signals found.")
            continue
        
        print(f"Found {len(signals)} opportunities:\n")
        
        for signal in signals:
            print(f"  🎯 {signal['ticker']} @ ${signal['current_price']}")
            print(f"     {signal['thesis']}")
            
            # Print specific metrics
            for key, value in signal.items():
                if key not in ['hunt', 'ticker', 'thesis', 'current_price']:
                    print(f"     {key}: {value}")
            print()
    
    # Summary
    total_signals = sum(len(signals) for signals in results.values())
    print(f"\n{'='*80}")
    print(f"🐺 TOTAL OPPORTUNITIES: {total_signals}")
    print(f"{'='*80}\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    results = run_all_hunts()
    display_results(results)
    
    print("\n🐺 The wolf has finished scouting the herd.")
    print("AWOOOO\n")
