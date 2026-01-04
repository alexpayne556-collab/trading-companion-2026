#!/usr/bin/env python3
"""
🐺 THE PRESSURE FRAMEWORK - WHO IS TRAPPED, WHO WILL BE FORCED TO ACT
=====================================================================

Forget patterns. Forget charts. Every stock has PLAYERS.
Each player has CONSTRAINTS. The edge is knowing who's trapped
and who will be FORCED to act.

THE PLAYERS:
┌─────────────────┬───────────────────────────────────────────────────────┐
│ Player          │ Constraint                                            │
├─────────────────┼───────────────────────────────────────────────────────┤
│ SHORTS          │ Pay borrow rate DAILY. Must cover eventually.         │
│ MARKET MAKERS   │ Must stay delta neutral. Mechanical hedging.          │
│ RETAIL          │ Emotional. Small accounts. FOMO and panic.            │
│ INSTITUTIONS    │ Need to fill large orders quietly. Leave footprints.  │
│ INSIDERS        │ Know the truth. Can't hide (Form 4). FOLLOW THEM.     │
└─────────────────┴───────────────────────────────────────────────────────┘

THE INSIGHT:
We don't predict price. We predict WHO WILL BE FORCED TO BUY.

- Short squeeze = shorts FORCED to buy
- Gamma squeeze = market makers FORCED to buy  
- Sector sympathy = institutions rotating, FORCED to chase
- Panic recovery = retail sold, institutions buying their shares cheap

Built by Brokkr & Fenrir for the Wolf Pack
AWOOOO 🐺
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# THE PLAYERS AND THEIR CONSTRAINTS
# ============================================================================

class Player(Enum):
    SHORTS = "shorts"
    MARKET_MAKERS = "market_makers"
    RETAIL = "retail"
    INSTITUTIONS = "institutions"
    INSIDERS = "insiders"

class PressureType(Enum):
    SHORT_SQUEEZE = "short_squeeze"          # Shorts forced to cover
    GAMMA_SQUEEZE = "gamma_squeeze"          # MMs forced to hedge
    SECTOR_SYMPATHY = "sector_sympathy"      # Institutions forced to chase
    PANIC_RECOVERY = "panic_recovery"        # Retail sold, smart money buys
    INSIDER_SIGNAL = "insider_signal"        # Insiders know something
    LAGGARD_CATCHUP = "laggard_catchup"      # Underperformer must catch up
    CAPITULATION_BOTTOM = "capitulation"     # Sellers exhausted

@dataclass
class PressureSignal:
    """A detected pressure situation"""
    ticker: str
    pressure_type: PressureType
    trapped_player: Player
    pressure_score: float  # 0-100
    thesis: str
    entry_zone: str
    target: str
    stop: str
    timing: str
    data: Dict

# ============================================================================
# UNIVERSE
# ============================================================================

UNIVERSE = {
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ', 'LAES'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'BKSY', 'MNTS', 'ASTS', 'SPIR', 'PL', 
              'GSAT', 'SIDU', 'SATL', 'IRDM', 'VSAT'],
    'EVTOL': ['JOBY', 'ACHR', 'LILM', 'EVTL'],
    'NUCLEAR': ['LEU', 'CCJ', 'UUUU', 'UEC', 'SMR', 'OKLO', 'DNN', 'NXE', 
                'LTBR', 'CEG', 'TLN', 'VST', 'NNE'],
    'AI_INFRA': ['SMCI', 'DELL', 'HPE', 'ANET', 'VRT', 'PWR', 'SOUN', 'AI'],
    'SEMICONDUCTORS': ['NVDA', 'AMD', 'ARM', 'TSM', 'ASML', 'MU', 'MRVL', 'AVGO'],
    'CRYPTO': ['MARA', 'RIOT', 'CLSK', 'COIN', 'CIFR', 'HUT', 'BITF'],
    'BIOTECH': ['CRSP', 'EDIT', 'NTLA', 'BEAM', 'RXRX'],
    'FINTECH': ['SOFI', 'AFRM', 'UPST', 'NU'],
    'EV_CLEAN': ['TSLA', 'RIVN', 'LCID', 'PLUG', 'FCEL', 'BE']
}

SECTOR_LEADERS = {
    'QUANTUM': 'IONQ',
    'SPACE': 'RKLB', 
    'NUCLEAR': 'CCJ',
    'AI_INFRA': 'NVDA',
    'SEMICONDUCTORS': 'NVDA',
    'CRYPTO': 'COIN',
    'BIOTECH': 'CRSP',
    'FINTECH': 'SOFI',
    'EV_CLEAN': 'TSLA'
}

# ============================================================================
# THE TIMING TRUTH
# ============================================================================

TIMING_WINDOWS = """
┌────────────────────┬──────────────────────────────────────────────────────┐
│ Time               │ What's Actually Happening                            │
├────────────────────┼──────────────────────────────────────────────────────┤
│ 9:30-10:00 AM      │ Retail emotional orders. Often WRONG. This is trap.  │
│ 10:00-11:00 AM     │ Institutions show hand. REAL direction emerges.      │
│ 11:00 AM-3:00 PM   │ Algorithms chop each other. NO EDGE. Stay out.       │
│ 3:00-4:00 PM       │ Power hour. Institutions finish positioning.         │
└────────────────────┴──────────────────────────────────────────────────────┘

THE PLAY: Don't chase the open. Wait for 10 AM. Let retail panic or 
euphoria exhaust. Then see what institutions actually do.
"""

# ============================================================================
# THE SMALL CAP EDGE
# ============================================================================

SMALL_CAP_EDGE = """
WHY DO WE HAVE EDGE IN $2-20 STOCKS?

1. INSTITUTIONS CAN'T PLAY
   - They can't move $50M in a stock with $2M daily volume
   - Too small. They IGNORE our space.

2. FLOAT IS TIGHT  
   - 20M shares outstanding means 10,000 buyers can move price 5%
   - In AAPL that's nothing. In RGTI it's everything.

3. INFORMATION ASYMMETRY
   - No analysts covering. No CNBC talking about it.
   - The edge goes to those who DIG.

4. SHORTS GET LAZY
   - They short small caps expecting them to die
   - When they don't die, shorts get TRAPPED
   - Borrow rates spike. They bleed.

5. RETAIL IS ALONE
   - No one telling them what to do
   - They panic. They FOMO. They're WRONG at the extremes.

WE'RE SMALL ENOUGH TO GET IN AND OUT.
WE'RE DEDICATED ENOUGH TO WATCH.
WE'RE PATIENT ENOUGH TO WAIT FOR FORCED BUYERS.
"""

# ============================================================================
# DATA FETCHING
# ============================================================================

def fetch_stock_data(ticker: str, period: str = '3mo') -> Optional[pd.DataFrame]:
    """Fetch price/volume data for a ticker"""
    try:
        df = yf.download(ticker, period=period, progress=False)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return None

def get_stock_info(ticker: str) -> Dict:
    """Get stock info including short interest"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'short_percent': info.get('shortPercentOfFloat', 0) or 0,
            'short_ratio': info.get('shortRatio', 0) or 0,
            'float_shares': info.get('floatShares', 0) or 0,
            'market_cap': info.get('marketCap', 0) or 0,
            'avg_volume': info.get('averageVolume', 0) or 0,
            'price': info.get('currentPrice', 0) or info.get('regularMarketPrice', 0) or 0,
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0) or 0,
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0) or 0,
        }
    except:
        return {}

# ============================================================================
# PRESSURE DETECTION: SHORT SQUEEZE POTENTIAL
# ============================================================================

def detect_short_squeeze_pressure(ticker: str, df: pd.DataFrame, info: Dict) -> Optional[PressureSignal]:
    """
    Detect short squeeze potential.
    
    SHORTS ARE TRAPPED WHEN:
    - High short interest (>20% of float)
    - Stock is rising (not dying like they bet)
    - Volume increasing (covering starting)
    - Near 52-week highs (maximum pain)
    """
    if not info or df is None or len(df) < 20:
        return None
    
    short_pct = info.get('short_percent', 0) * 100  # Convert to percentage
    short_ratio = info.get('short_ratio', 0)
    current_price = df['Close'].iloc[-1]
    high_52w = info.get('fifty_two_week_high', 0)
    
    # Calculate metrics
    price_from_high = ((current_price - high_52w) / high_52w * 100) if high_52w > 0 else -100
    
    # Volume trend
    vol_recent = df['Volume'].iloc[-5:].mean()
    vol_baseline = df['Volume'].iloc[-20:-5].mean()
    vol_ratio = vol_recent / vol_baseline if vol_baseline > 0 else 0
    
    # Price trend
    price_change_5d = ((current_price - df['Close'].iloc[-6]) / df['Close'].iloc[-6] * 100) if len(df) >= 6 else 0
    price_change_20d = ((current_price - df['Close'].iloc[-21]) / df['Close'].iloc[-21] * 100) if len(df) >= 21 else 0
    
    # PRESSURE SCORE
    pressure_score = 0
    
    # Short interest component (0-40 points)
    if short_pct >= 30:
        pressure_score += 40
    elif short_pct >= 20:
        pressure_score += 30
    elif short_pct >= 15:
        pressure_score += 20
    elif short_pct >= 10:
        pressure_score += 10
    
    # Short ratio / days to cover (0-20 points)
    if short_ratio >= 10:
        pressure_score += 20
    elif short_ratio >= 5:
        pressure_score += 15
    elif short_ratio >= 3:
        pressure_score += 10
    
    # Price rising against shorts (0-20 points)
    if price_change_5d > 10:
        pressure_score += 20
    elif price_change_5d > 5:
        pressure_score += 15
    elif price_change_5d > 0:
        pressure_score += 10
    
    # Near highs = max pain (0-10 points)
    if price_from_high > -10:
        pressure_score += 10
    elif price_from_high > -20:
        pressure_score += 5
    
    # Volume increasing (0-10 points)
    if vol_ratio > 2:
        pressure_score += 10
    elif vol_ratio > 1.5:
        pressure_score += 5
    
    if pressure_score < 30:
        return None
    
    return PressureSignal(
        ticker=ticker,
        pressure_type=PressureType.SHORT_SQUEEZE,
        trapped_player=Player.SHORTS,
        pressure_score=pressure_score,
        thesis=f"Short interest {short_pct:.1f}%, {short_ratio:.1f} days to cover. Price up {price_change_5d:.1f}% in 5 days. Shorts bleeding.",
        entry_zone=f"Current ${current_price:.2f} or pullback to ${current_price * 0.95:.2f}",
        target=f"${current_price * 1.20:.2f} (+20%) on squeeze",
        stop=f"${current_price * 0.90:.2f} (-10%)",
        timing="Wait for volume spike >2x average to confirm covering started",
        data={
            'short_percent': short_pct,
            'short_ratio': short_ratio,
            'price_change_5d': price_change_5d,
            'vol_ratio': vol_ratio,
            'price_from_high': price_from_high
        }
    )

# ============================================================================
# PRESSURE DETECTION: SECTOR LAGGARD CATCHUP
# ============================================================================

def detect_laggard_pressure(ticker: str, df: pd.DataFrame, sector: str, 
                            sector_data: Dict[str, pd.DataFrame]) -> Optional[PressureSignal]:
    """
    Detect laggard catch-up potential.
    
    INSTITUTIONS ARE FORCED TO CHASE WHEN:
    - Sector leader ripped
    - This stock didn't follow
    - They need "sector exposure"
    - They'll buy the laggard to catch up
    """
    if df is None or len(df) < 10:
        return None
    
    leader = SECTOR_LEADERS.get(sector)
    if not leader or leader not in sector_data:
        return None
    
    leader_df = sector_data[leader]
    if leader_df is None or len(leader_df) < 10:
        return None
    
    # Calculate returns
    ticker_return_5d = ((df['Close'].iloc[-1] - df['Close'].iloc[-6]) / df['Close'].iloc[-6] * 100) if len(df) >= 6 else 0
    leader_return_5d = ((leader_df['Close'].iloc[-1] - leader_df['Close'].iloc[-6]) / leader_df['Close'].iloc[-6] * 100) if len(leader_df) >= 6 else 0
    
    # The LAG
    lag = leader_return_5d - ticker_return_5d
    
    # Only trigger if leader moved significantly and laggard didn't
    if leader_return_5d < 5 or lag < 5:
        return None
    
    current_price = df['Close'].iloc[-1]
    
    # PRESSURE SCORE
    pressure_score = min(lag * 5, 50)  # Up to 50 points from lag
    
    # Bonus if leader move was huge
    if leader_return_5d > 15:
        pressure_score += 25
    elif leader_return_5d > 10:
        pressure_score += 15
    
    # Bonus if volume is picking up (institutions entering)
    vol_recent = df['Volume'].iloc[-3:].mean()
    vol_baseline = df['Volume'].iloc[-15:-3].mean()
    if vol_baseline > 0 and vol_recent / vol_baseline > 1.3:
        pressure_score += 15
    
    if pressure_score < 40:
        return None
    
    return PressureSignal(
        ticker=ticker,
        pressure_type=PressureType.LAGGARD_CATCHUP,
        trapped_player=Player.INSTITUTIONS,
        pressure_score=pressure_score,
        thesis=f"Leader {leader} up {leader_return_5d:.1f}%, {ticker} only {ticker_return_5d:.1f}%. Lag of {lag:.1f}%. Institutions need exposure, will chase.",
        entry_zone=f"Current ${current_price:.2f}",
        target=f"${current_price * (1 + lag/100):.2f} (catch-up to leader)",
        stop=f"${current_price * 0.92:.2f} (-8%)",
        timing="Enter now. Catch-up happens fast once it starts.",
        data={
            'leader': leader,
            'leader_return': leader_return_5d,
            'ticker_return': ticker_return_5d,
            'lag': lag
        }
    )

# ============================================================================
# PRESSURE DETECTION: PANIC RECOVERY
# ============================================================================

def detect_panic_recovery(ticker: str, df: pd.DataFrame) -> Optional[PressureSignal]:
    """
    Detect panic selling exhaustion.
    
    RETAIL IS TRAPPED WHEN:
    - Big gap down scared them
    - They panic sold at the bottom
    - Smart money (institutions) is buying the fear
    - Volume spikes but price stabilizes = accumulation
    """
    if df is None or len(df) < 20:
        return None
    
    # Look for recent gap down or crash
    low_5d = df['Low'].iloc[-5:].min()
    high_20d = df['High'].iloc[-20:-5].max()
    
    drawdown = ((low_5d - high_20d) / high_20d * 100) if high_20d > 0 else 0
    
    if drawdown > -10:  # Need at least 10% drawdown
        return None
    
    current_price = df['Close'].iloc[-1]
    
    # Recovery from low
    recovery = ((current_price - low_5d) / low_5d * 100) if low_5d > 0 else 0
    
    # Volume on recovery (institutional buying)
    vol_recent = df['Volume'].iloc[-3:].mean()
    vol_baseline = df['Volume'].iloc[-20:-5].mean()
    vol_ratio = vol_recent / vol_baseline if vol_baseline > 0 else 0
    
    # Price stabilizing (not making new lows)
    price_stable = df['Close'].iloc[-1] > df['Low'].iloc[-5:].min()
    
    # PRESSURE SCORE
    pressure_score = 0
    
    # Deeper drawdown = more panic (0-30)
    if drawdown < -30:
        pressure_score += 30
    elif drawdown < -20:
        pressure_score += 20
    elif drawdown < -10:
        pressure_score += 10
    
    # Recovery starting (0-30)
    if recovery > 10:
        pressure_score += 30
    elif recovery > 5:
        pressure_score += 20
    elif recovery > 0:
        pressure_score += 10
    
    # Volume spike on recovery (0-20)
    if vol_ratio > 2:
        pressure_score += 20
    elif vol_ratio > 1.5:
        pressure_score += 10
    
    # Price stabilizing (0-20)
    if price_stable:
        pressure_score += 20
    
    if pressure_score < 50:
        return None
    
    return PressureSignal(
        ticker=ticker,
        pressure_type=PressureType.PANIC_RECOVERY,
        trapped_player=Player.RETAIL,
        pressure_score=pressure_score,
        thesis=f"Crashed {drawdown:.1f}% from recent high. Recovering {recovery:.1f}% on {vol_ratio:.1f}x volume. Retail panic sold, institutions buying.",
        entry_zone=f"Current ${current_price:.2f} or pullback to ${low_5d:.2f}",
        target=f"${high_20d * 0.9:.2f} (90% of prior high)",
        stop=f"${low_5d * 0.95:.2f} (below recent low)",
        timing="Wait for 10 AM to confirm morning panic is over",
        data={
            'drawdown': drawdown,
            'recovery': recovery,
            'vol_ratio': vol_ratio,
            'recent_low': low_5d,
            'prior_high': high_20d
        }
    )

# ============================================================================
# PRESSURE DETECTION: CAPITULATION BOTTOM
# ============================================================================

def detect_capitulation(ticker: str, df: pd.DataFrame, info: Dict) -> Optional[PressureSignal]:
    """
    Detect capitulation / seller exhaustion.
    
    ALL WEAK HANDS ARE OUT WHEN:
    - Stock crushed 40%+ from highs
    - Volume died (no sellers left)
    - Then volume SPIKES (smart money entering)
    - The bottom is in
    """
    if df is None or len(df) < 60 or not info:
        return None
    
    current_price = df['Close'].iloc[-1]
    high_52w = info.get('fifty_two_week_high', 0)
    
    if high_52w == 0:
        return None
    
    # Drawdown from 52-week high
    drawdown = ((current_price - high_52w) / high_52w * 100)
    
    if drawdown > -30:  # Need at least 30% drawdown
        return None
    
    # Volume pattern: died then spiked
    vol_30_60 = df['Volume'].iloc[-60:-30].mean()  # Older period
    vol_10_30 = df['Volume'].iloc[-30:-10].mean()  # Volume died period
    vol_recent = df['Volume'].iloc[-10:].mean()     # Recent spike
    
    if vol_30_60 == 0:
        return None
    
    vol_died = vol_10_30 / vol_30_60 if vol_30_60 > 0 else 1
    vol_spiked = vol_recent / vol_10_30 if vol_10_30 > 0 else 1
    
    # Price stabilizing near lows
    low_60d = df['Low'].iloc[-60:].min()
    dist_from_low = ((current_price - low_60d) / low_60d * 100) if low_60d > 0 else 100
    
    # PRESSURE SCORE
    pressure_score = 0
    
    # Deep drawdown (0-30)
    if drawdown < -50:
        pressure_score += 30
    elif drawdown < -40:
        pressure_score += 20
    elif drawdown < -30:
        pressure_score += 10
    
    # Volume died then spiked (0-40)
    if vol_died < 0.7 and vol_spiked > 1.5:
        pressure_score += 40
    elif vol_died < 0.8 and vol_spiked > 1.3:
        pressure_score += 25
    elif vol_spiked > 1.5:
        pressure_score += 15
    
    # Near bottom but recovering (0-30)
    if 0 < dist_from_low < 15:
        pressure_score += 30
    elif dist_from_low < 25:
        pressure_score += 15
    
    if pressure_score < 50:
        return None
    
    return PressureSignal(
        ticker=ticker,
        pressure_type=PressureType.CAPITULATION_BOTTOM,
        trapped_player=Player.RETAIL,
        pressure_score=pressure_score,
        thesis=f"Down {drawdown:.1f}% from 52w high. Volume died (to {vol_died:.1f}x), now spiking ({vol_spiked:.1f}x). Sellers exhausted, smart money entering.",
        entry_zone=f"Current ${current_price:.2f}",
        target=f"${current_price * 1.50:.2f} (+50% recovery)",
        stop=f"${low_60d * 0.95:.2f} (below 60d low)",
        timing="Enter on any pullback. The bottom is likely in.",
        data={
            'drawdown': drawdown,
            'vol_died': vol_died,
            'vol_spiked': vol_spiked,
            'dist_from_low': dist_from_low,
            'low_60d': low_60d
        }
    )

# ============================================================================
# MAIN PRESSURE SCANNER
# ============================================================================

def scan_all_pressure() -> List[PressureSignal]:
    """
    Scan entire universe for pressure situations.
    
    Returns list of all detected pressure signals.
    """
    print("\n" + "="*80)
    print("🐺 PRESSURE FRAMEWORK - WHO IS TRAPPED?")
    print("="*80)
    print(TIMING_WINDOWS)
    print()
    
    all_signals = []
    sector_data = {}  # Cache for laggard detection
    
    # Flatten universe
    all_tickers = []
    ticker_to_sector = {}
    for sector, tickers in UNIVERSE.items():
        for ticker in tickers:
            all_tickers.append(ticker)
            ticker_to_sector[ticker] = sector
    
    print(f"Scanning {len(all_tickers)} tickers for trapped players...\n")
    
    # Fetch all data first
    print("Fetching price data...")
    stock_data = {}
    stock_info = {}
    
    for i, ticker in enumerate(all_tickers):
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{len(all_tickers)}...")
        
        df = fetch_stock_data(ticker)
        if df is not None:
            stock_data[ticker] = df
            sector = ticker_to_sector[ticker]
            if sector not in sector_data:
                sector_data[sector] = {}
            sector_data[sector][ticker] = df
        
        info = get_stock_info(ticker)
        if info:
            stock_info[ticker] = info
    
    print(f"\nLoaded {len(stock_data)} tickers. Detecting pressure...\n")
    
    # Run all detectors
    for ticker in all_tickers:
        df = stock_data.get(ticker)
        info = stock_info.get(ticker, {})
        sector = ticker_to_sector[ticker]
        
        # Short squeeze
        signal = detect_short_squeeze_pressure(ticker, df, info)
        if signal:
            all_signals.append(signal)
        
        # Laggard catch-up
        signal = detect_laggard_pressure(ticker, df, sector, sector_data.get(sector, {}))
        if signal:
            all_signals.append(signal)
        
        # Panic recovery
        signal = detect_panic_recovery(ticker, df)
        if signal:
            all_signals.append(signal)
        
        # Capitulation bottom
        signal = detect_capitulation(ticker, df, info)
        if signal:
            all_signals.append(signal)
    
    # Sort by pressure score
    all_signals.sort(key=lambda x: x.pressure_score, reverse=True)
    
    return all_signals

def display_pressure_signals(signals: List[PressureSignal]):
    """Display pressure signals in a clean format"""
    
    if not signals:
        print("\n" + "="*80)
        print("No pressure situations detected.")
        print("="*80)
        print("\nThis is actually valuable information:")
        print("- No one is trapped = no forced buying coming")
        print("- Wait for setups to develop")
        print("- Cash is a position too")
        return
    
    # Group by pressure type
    by_type = {}
    for signal in signals:
        ptype = signal.pressure_type.value
        if ptype not in by_type:
            by_type[ptype] = []
        by_type[ptype].append(signal)
    
    print("\n" + "="*80)
    print(f"🎯 FOUND {len(signals)} PRESSURE SITUATIONS")
    print("="*80)
    
    for ptype, type_signals in by_type.items():
        print(f"\n{'='*80}")
        print(f"🔥 {ptype.upper().replace('_', ' ')} ({len(type_signals)} signals)")
        print(f"{'='*80}")
        
        for signal in type_signals[:5]:  # Top 5 per type
            print(f"\n  🐺 {signal.ticker} | Score: {signal.pressure_score:.0f}/100")
            print(f"     WHO'S TRAPPED: {signal.trapped_player.value.upper()}")
            print(f"     THESIS: {signal.thesis}")
            print(f"     ENTRY: {signal.entry_zone}")
            print(f"     TARGET: {signal.target}")
            print(f"     STOP: {signal.stop}")
            print(f"     TIMING: {signal.timing}")
    
    # Top 10 overall
    print("\n" + "="*80)
    print("🏆 TOP 10 PRESSURE SITUATIONS (HIGHEST CONVICTION)")
    print("="*80)
    
    for i, signal in enumerate(signals[:10], 1):
        print(f"\n  #{i} {signal.ticker} ({signal.pressure_type.value})")
        print(f"      Score: {signal.pressure_score:.0f} | Trapped: {signal.trapped_player.value}")
        print(f"      {signal.thesis[:80]}...")

def print_framework():
    """Print the complete framework explanation"""
    
    print("\n" + "="*80)
    print("🐺 THE PRESSURE FRAMEWORK")
    print("="*80)
    
    print("""
THE QUESTION WE ANSWER:
"Who is trapped, who will be forced to act, and when?"

THE PLAYERS AND THEIR CONSTRAINTS:
┌─────────────────┬────────────────────────────────────────────────────────────┐
│ Player          │ When They're TRAPPED                                       │
├─────────────────┼────────────────────────────────────────────────────────────┤
│ SHORTS          │ Price rising + high borrow rate = bleeding money daily     │
│ MARKET MAKERS   │ Heavy call buying = FORCED to buy shares to hedge          │
│ RETAIL          │ Gap down = panic sell at bottom. Gap up = FOMO at top      │
│ INSTITUTIONS    │ Sector hot but they missed it = FORCED to chase            │
│ INSIDERS        │ Never trapped - they KNOW. FOLLOW THEM.                    │
└─────────────────┴────────────────────────────────────────────────────────────┘

THE SETUPS WE HUNT:
┌─────────────────────────┬───────────────────┬────────────────────────────────┐
│ Setup                   │ Who's Trapped     │ The Play                       │
├─────────────────────────┼───────────────────┼────────────────────────────────┤
│ High SI + catalyst      │ SHORTS            │ Buy before spark, sell squeeze │
│ Insider buying          │ Nobody            │ Follow smart money             │
│ Leader rips + laggard   │ INSTITUTIONS      │ Buy laggard, it catches up     │
│ Gap down + vol spike    │ RETAIL            │ Buy fear, institutions are     │
│ Crushed + vol spike     │ RETAIL (was)      │ Capitulation bottom            │
│ Heavy call buying       │ MARKET MAKERS     │ Gamma squeeze potential        │
└─────────────────────────┴───────────────────┴────────────────────────────────┘
""")
    
    print(SMALL_CAP_EDGE)

# ============================================================================
# MAIN
# ============================================================================

def save_results_to_json(signals: List[PressureSignal]):
    """Save results to JSON for dashboard consumption"""
    import json
    from pathlib import Path
    
    # Ensure logs directory exists
    logs_dir = Path('/workspaces/trading-companion-2026/logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Convert signals to dict format
    signals_data = []
    for s in signals:
        signals_data.append({
            'ticker': s.ticker,
            'type': s.pressure_type.value,
            'trapped_player': s.trapped_player.value,
            'score': s.pressure_score,
            'thesis': s.thesis,
            'entry_zone': s.entry_zone,
            'target': s.target,
            'stop': s.stop,
            'timing': s.timing,
            'data': s.data
        })
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'total_signals': len(signals),
        'signals': signals_data
    }
    
    # Save to file
    output_path = logs_dir / 'pressure_scan_latest.json'
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n📁 Results saved to {output_path}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Pressure Framework Scanner')
    parser.add_argument('--explain', action='store_true', help='Print framework explanation')
    
    args = parser.parse_args()
    
    if args.explain:
        print_framework()
    else:
        signals = scan_all_pressure()
        display_pressure_signals(signals)
        
        # Save to JSON for dashboard
        save_results_to_json(signals)
        
        print("\n" + "="*80)
        print("🐺 THE WOLF SEES WHO'S TRAPPED")
        print("="*80)
        print("\nThe question isn't 'what does the chart say'")
        print("The question is 'who will be FORCED to buy?'")
        print("\nAWOOOO 🐺\n")
