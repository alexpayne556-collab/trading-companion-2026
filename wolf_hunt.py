#!/usr/bin/env python3
"""
🐺 WOLF HUNT - THE UNIFIED DECISION ENGINE
============================================

One command. Everything checked. Clear verdict.

python wolf_hunt.py TICKER        # Full analysis on one ticker
python wolf_hunt.py scan          # Find best opportunities NOW
python wolf_hunt.py today         # What should I hunt TODAY?

THE QUESTION: Should I put $500 on this for a big gain?

VERDICT:
🟢 HUNT   - Multiple signals, clear setup, GO
🟡 STALK  - Interesting but wait for better entry
🔴 PASS   - Not enough edge, skip

Built by the Wolf Pack. This is where it all comes together.
AWOOOO! 🐺
"""

import argparse
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

UNIVERSE = {
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'BKSY', 'ASTS'],
    'NUCLEAR': ['LEU', 'CCJ', 'UUUU', 'SMR', 'OKLO', 'NNE'],
    'AI_INFRA': ['SMCI', 'DELL', 'ANET', 'VRT', 'SOUN', 'AI'],
    'SEMICONDUCTORS': ['NVDA', 'AMD', 'ARM', 'MU', 'MRVL'],
    'CRYPTO': ['MARA', 'RIOT', 'CLSK', 'COIN', 'CIFR'],
    'MEME_GAMMA': ['GME', 'AMC', 'BBBY'],
    'BIOTECH': ['CRSP', 'EDIT', 'NTLA'],
    'FINTECH': ['SOFI', 'AFRM', 'UPST']
}

# Flatten for scanning
ALL_TICKERS = []
for sector, tickers in UNIVERSE.items():
    ALL_TICKERS.extend(tickers)

# ============================================================================
# SIGNAL CHECKERS - Each returns score 0-100 and details
# ============================================================================

class SignalChecker:
    """Base class for signal checks"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        self._price_data = None
        self._info = None
    
    @property
    def price_data(self):
        if self._price_data is None:
            self._price_data = self.stock.history(period='3mo')
        return self._price_data
    
    @property
    def info(self):
        if self._info is None:
            try:
                self._info = self.stock.info
            except:
                self._info = {}
        return self._info
    
    @property
    def current_price(self):
        if not self.price_data.empty:
            return self.price_data['Close'].iloc[-1]
        return 0


class GammaChecker(SignalChecker):
    """Check options chain for gamma squeeze setup"""
    
    def check(self) -> dict:
        result = {
            'name': 'GAMMA SQUEEZE',
            'score': 0,
            'signal': False,
            'details': '',
            'data': {}
        }
        
        try:
            # Get options chain
            expirations = self.stock.options
            if not expirations:
                result['details'] = 'No options available'
                return result
            
            # Focus on near-term (max gamma)
            near_exp = expirations[0]
            chain = self.stock.option_chain(near_exp)
            calls = chain.calls
            puts = chain.puts
            
            if calls.empty or puts.empty:
                result['details'] = 'Empty options chain'
                return result
            
            # Calculate metrics
            total_call_oi = calls['openInterest'].sum()
            total_put_oi = puts['openInterest'].sum()
            
            if total_put_oi > 0:
                cp_ratio = total_call_oi / total_put_oi
            else:
                cp_ratio = 0
            
            # Call volume ratio
            total_call_vol = calls['volume'].sum() if 'volume' in calls else 0
            total_put_vol = puts['volume'].sum() if 'volume' in puts else 0
            
            if total_put_vol > 0:
                vol_ratio = total_call_vol / total_put_vol
            else:
                vol_ratio = total_call_vol if total_call_vol > 0 else 0
            
            # Find gamma wall (highest OI strike near current price)
            current = self.current_price
            calls_near = calls[abs(calls['strike'] - current) / current < 0.15]
            
            gamma_wall = None
            gamma_wall_oi = 0
            if not calls_near.empty:
                max_oi_idx = calls_near['openInterest'].idxmax()
                gamma_wall = calls_near.loc[max_oi_idx, 'strike']
                gamma_wall_oi = calls_near.loc[max_oi_idx, 'openInterest']
            
            # Calculate OTM call fuel
            if current > 0:
                otm_calls = calls[calls['strike'] > current * 1.05]
                otm_fuel = otm_calls['openInterest'].sum()
            else:
                otm_fuel = 0
            
            # Score it
            score = 0
            
            # Call/Put ratio scoring
            if cp_ratio >= 5:
                score += 35
            elif cp_ratio >= 3:
                score += 25
            elif cp_ratio >= 2:
                score += 15
            elif cp_ratio >= 1.5:
                score += 10
            
            # Volume ratio (today's action)
            if vol_ratio >= 3:
                score += 20
            elif vol_ratio >= 2:
                score += 15
            elif vol_ratio >= 1.5:
                score += 10
            
            # Gamma wall proximity
            if gamma_wall and current > 0:
                wall_dist = (gamma_wall - current) / current
                if 0 < wall_dist < 0.05:  # Within 5% above
                    score += 25
                elif 0 < wall_dist < 0.10:  # Within 10%
                    score += 15
                elif wall_dist <= 0:  # At or above wall
                    score += 10
            
            # OTM fuel
            if otm_fuel > total_call_oi * 0.3:
                score += 20
            elif otm_fuel > total_call_oi * 0.2:
                score += 10
            
            result['score'] = min(score, 100)
            result['signal'] = score >= 50
            result['data'] = {
                'cp_ratio': round(cp_ratio, 1),
                'vol_ratio': round(vol_ratio, 1),
                'gamma_wall': gamma_wall,
                'gamma_wall_oi': gamma_wall_oi,
                'otm_fuel': otm_fuel,
                'expiry': near_exp
            }
            
            if gamma_wall and current > 0:
                wall_pct = ((gamma_wall - current) / current) * 100
                result['details'] = f"C/P: {cp_ratio:.1f}:1, Wall: ${gamma_wall:.0f} ({wall_pct:+.1f}%)"
            else:
                result['details'] = f"C/P: {cp_ratio:.1f}:1"
            
        except Exception as e:
            result['details'] = f'Error: {str(e)[:50]}'
        
        return result


class MomentumChecker(SignalChecker):
    """Check price momentum and trend"""
    
    def check(self) -> dict:
        result = {
            'name': 'MOMENTUM',
            'score': 0,
            'signal': False,
            'details': '',
            'data': {}
        }
        
        try:
            df = self.price_data
            if len(df) < 20:
                result['details'] = 'Insufficient data'
                return result
            
            current = df['Close'].iloc[-1]
            
            # Calculate returns
            ret_5d = (current / df['Close'].iloc[-5] - 1) * 100 if len(df) >= 5 else 0
            ret_20d = (current / df['Close'].iloc[-20] - 1) * 100 if len(df) >= 20 else 0
            
            # Moving averages
            ma_10 = df['Close'].rolling(10).mean().iloc[-1]
            ma_20 = df['Close'].rolling(20).mean().iloc[-1]
            ma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else ma_20
            
            # Volume trend
            vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
            vol_recent = df['Volume'].iloc[-5:].mean()
            vol_ratio = vol_recent / vol_avg if vol_avg > 0 else 1
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Score it
            score = 0
            
            # Trend alignment
            if current > ma_10 > ma_20:
                score += 20
            elif current > ma_20:
                score += 10
            
            # 5-day momentum
            if ret_5d > 10:
                score += 25
            elif ret_5d > 5:
                score += 15
            elif ret_5d > 0:
                score += 5
            
            # 20-day momentum  
            if ret_20d > 20:
                score += 20
            elif ret_20d > 10:
                score += 15
            elif ret_20d > 0:
                score += 5
            
            # Volume confirmation
            if vol_ratio > 1.5 and ret_5d > 0:
                score += 15
            elif vol_ratio > 1.2 and ret_5d > 0:
                score += 10
            
            # RSI - want momentum but not overbought
            if 50 < current_rsi < 70:
                score += 20  # Ideal - bullish but room to run
            elif 40 < current_rsi <= 50:
                score += 10  # Neutral
            elif current_rsi >= 70:
                score += 5   # Overbought risk
            
            result['score'] = min(score, 100)
            result['signal'] = score >= 50
            result['data'] = {
                'ret_5d': round(ret_5d, 1),
                'ret_20d': round(ret_20d, 1),
                'rsi': round(current_rsi, 0),
                'vol_ratio': round(vol_ratio, 2),
                'above_ma20': current > ma_20
            }
            result['details'] = f"5d: {ret_5d:+.1f}%, 20d: {ret_20d:+.1f}%, RSI: {current_rsi:.0f}"
            
        except Exception as e:
            result['details'] = f'Error: {str(e)[:50]}'
        
        return result


class VolumeChecker(SignalChecker):
    """Check for unusual volume patterns"""
    
    def check(self) -> dict:
        result = {
            'name': 'VOLUME',
            'score': 0,
            'signal': False,
            'details': '',
            'data': {}
        }
        
        try:
            df = self.price_data
            if len(df) < 20:
                result['details'] = 'Insufficient data'
                return result
            
            # Calculate volume metrics
            vol_avg_20 = df['Volume'].rolling(20).mean().iloc[-1]
            vol_today = df['Volume'].iloc[-1]
            vol_ratio = vol_today / vol_avg_20 if vol_avg_20 > 0 else 1
            
            # Volume trend over last 5 days
            vol_5d_avg = df['Volume'].iloc[-5:].mean()
            vol_prev_5d = df['Volume'].iloc[-10:-5].mean()
            vol_trend = vol_5d_avg / vol_prev_5d if vol_prev_5d > 0 else 1
            
            # Up volume vs down volume
            df['up_vol'] = df['Volume'].where(df['Close'] > df['Open'], 0)
            df['down_vol'] = df['Volume'].where(df['Close'] <= df['Open'], 0)
            
            up_vol_5d = df['up_vol'].iloc[-5:].sum()
            down_vol_5d = df['down_vol'].iloc[-5:].sum()
            
            if down_vol_5d > 0:
                up_down_ratio = up_vol_5d / down_vol_5d
            else:
                up_down_ratio = 5 if up_vol_5d > 0 else 1
            
            # Score it
            score = 0
            
            # Today's volume
            if vol_ratio > 3:
                score += 30
            elif vol_ratio > 2:
                score += 20
            elif vol_ratio > 1.5:
                score += 10
            
            # Volume trend
            if vol_trend > 1.5:
                score += 25
            elif vol_trend > 1.2:
                score += 15
            
            # Up vs down volume
            if up_down_ratio > 2:
                score += 30
            elif up_down_ratio > 1.5:
                score += 20
            elif up_down_ratio > 1:
                score += 10
            
            # Accumulation pattern (rising price on rising volume)
            price_up = df['Close'].iloc[-1] > df['Close'].iloc[-5]
            vol_up = vol_5d_avg > vol_prev_5d
            if price_up and vol_up:
                score += 15
            
            result['score'] = min(score, 100)
            result['signal'] = score >= 50
            result['data'] = {
                'vol_ratio': round(vol_ratio, 2),
                'vol_trend': round(vol_trend, 2),
                'up_down_ratio': round(up_down_ratio, 2)
            }
            result['details'] = f"Today: {vol_ratio:.1f}x avg, Up/Down: {up_down_ratio:.1f}:1"
            
        except Exception as e:
            result['details'] = f'Error: {str(e)[:50]}'
        
        return result


class ShortSqueezeChecker(SignalChecker):
    """Check for short squeeze potential"""
    
    def check(self) -> dict:
        result = {
            'name': 'SHORT SQUEEZE',
            'score': 0,
            'signal': False,
            'details': '',
            'data': {}
        }
        
        try:
            info = self.info
            
            # Get short data
            short_pct = info.get('shortPercentOfFloat', 0) or 0
            short_ratio = info.get('shortRatio', 0) or 0  # Days to cover
            
            # Check price action (shorts getting squeezed?)
            df = self.price_data
            if len(df) >= 5:
                ret_5d = (df['Close'].iloc[-1] / df['Close'].iloc[-5] - 1) * 100
            else:
                ret_5d = 0
            
            # Score it
            score = 0
            
            # Short interest level
            if short_pct > 30:
                score += 35
            elif short_pct > 20:
                score += 25
            elif short_pct > 15:
                score += 15
            elif short_pct > 10:
                score += 10
            
            # Days to cover
            if short_ratio > 5:
                score += 25
            elif short_ratio > 3:
                score += 15
            elif short_ratio > 2:
                score += 10
            
            # Are shorts in pain? (price rising)
            if ret_5d > 15 and short_pct > 15:
                score += 25  # Shorts bleeding badly
            elif ret_5d > 10 and short_pct > 10:
                score += 15
            elif ret_5d > 5 and short_pct > 10:
                score += 10
            
            # Squeeze potential combo
            if short_pct > 20 and short_ratio > 3 and ret_5d > 0:
                score += 15  # Perfect storm building
            
            result['score'] = min(score, 100)
            result['signal'] = score >= 50
            result['data'] = {
                'short_pct': round(short_pct, 1),
                'days_to_cover': round(short_ratio, 1),
                'ret_5d': round(ret_5d, 1)
            }
            
            if short_pct > 0:
                result['details'] = f"SI: {short_pct:.0f}%, DTC: {short_ratio:.1f}, 5d: {ret_5d:+.1f}%"
            else:
                result['details'] = "No short data available"
            
        except Exception as e:
            result['details'] = f'Error: {str(e)[:50]}'
        
        return result


class TechnicalSetupChecker(SignalChecker):
    """Check for clean technical setup"""
    
    def check(self) -> dict:
        result = {
            'name': 'TECHNICAL SETUP',
            'score': 0,
            'signal': False,
            'details': '',
            'data': {}
        }
        
        try:
            df = self.price_data
            if len(df) < 50:
                result['details'] = 'Insufficient data'
                return result
            
            current = df['Close'].iloc[-1]
            high_52w = df['High'].max()
            low_52w = df['Low'].min()
            
            # Position in range
            range_pct = (current - low_52w) / (high_52w - low_52w) if high_52w > low_52w else 0.5
            
            # Distance from 52w high
            from_high = (current / high_52w - 1) * 100
            
            # Support/Resistance levels
            ma_20 = df['Close'].rolling(20).mean().iloc[-1]
            ma_50 = df['Close'].rolling(50).mean().iloc[-1]
            
            # Recent consolidation (tight range)
            recent_high = df['High'].iloc[-10:].max()
            recent_low = df['Low'].iloc[-10:].min()
            consolidation = (recent_high - recent_low) / current * 100
            
            # Breakout check
            prev_high = df['High'].iloc[-20:-1].max()
            breakout = current > prev_high
            
            # Score it
            score = 0
            
            # Not at extreme - room to run
            if 0.3 < range_pct < 0.7:
                score += 15
            elif range_pct < 0.3:
                score += 20  # Near lows - bounce potential
            
            # Distance from high
            if -15 < from_high < 0:
                score += 20  # Near highs - strength
            elif -30 < from_high <= -15:
                score += 10
            
            # Above key MAs
            if current > ma_20 > ma_50:
                score += 25
            elif current > ma_20:
                score += 15
            elif current > ma_50:
                score += 10
            
            # Tight consolidation (coiled spring)
            if consolidation < 10:
                score += 20
            elif consolidation < 15:
                score += 10
            
            # Breakout
            if breakout:
                score += 20
            
            result['score'] = min(score, 100)
            result['signal'] = score >= 50
            result['data'] = {
                'range_pct': round(range_pct * 100, 0),
                'from_high': round(from_high, 1),
                'consolidation': round(consolidation, 1),
                'above_ma20': current > ma_20,
                'breakout': breakout
            }
            
            setup_type = "BREAKOUT" if breakout else ("COILED" if consolidation < 10 else "TRENDING")
            result['details'] = f"{setup_type}, {from_high:+.0f}% from high, {consolidation:.0f}% range"
            
        except Exception as e:
            result['details'] = f'Error: {str(e)[:50]}'
        
        return result


class RegimeChecker:
    """Check market regime - not ticker specific"""
    
    def check(self) -> dict:
        result = {
            'name': 'MARKET REGIME',
            'score': 0,
            'signal': False,
            'details': '',
            'data': {}
        }
        
        try:
            # Get market data
            spy = yf.Ticker("SPY").history(period='1mo')
            qqq = yf.Ticker("QQQ").history(period='1mo')
            vix = yf.Ticker("^VIX").history(period='1mo')
            
            if spy.empty:
                result['details'] = 'No market data'
                return result
            
            # SPY metrics
            spy_ret_5d = (spy['Close'].iloc[-1] / spy['Close'].iloc[-5] - 1) * 100
            spy_ret_20d = (spy['Close'].iloc[-1] / spy['Close'].iloc[-20] - 1) * 100
            
            # QQQ metrics
            qqq_ret_5d = (qqq['Close'].iloc[-1] / qqq['Close'].iloc[-5] - 1) * 100
            
            # VIX
            vix_level = vix['Close'].iloc[-1]
            vix_prev = vix['Close'].iloc[-5]
            vix_direction = "rising" if vix_level > vix_prev else "falling"
            
            # Determine regime
            score = 50  # Start neutral
            
            # VIX level
            if vix_level < 15:
                score += 20
                regime = "RISK-ON"
            elif vix_level < 20:
                score += 10
                regime = "NEUTRAL"
            elif vix_level < 25:
                score -= 10
                regime = "CAUTIOUS"
            else:
                score -= 20
                regime = "RISK-OFF"
            
            # Trend
            if spy_ret_5d > 2 and spy_ret_20d > 0:
                score += 20
                regime = "RISK-ON"
            elif spy_ret_5d < -2:
                score -= 15
                if regime != "RISK-OFF":
                    regime = "PULLBACK"
            
            # VIX direction
            if vix_direction == "falling":
                score += 10
            else:
                score -= 5
            
            result['score'] = max(0, min(score, 100))
            result['signal'] = score >= 60
            result['data'] = {
                'regime': regime,
                'vix': round(vix_level, 1),
                'vix_direction': vix_direction,
                'spy_5d': round(spy_ret_5d, 1),
                'qqq_5d': round(qqq_ret_5d, 1)
            }
            result['details'] = f"{regime} | VIX: {vix_level:.0f} ({vix_direction}), SPY: {spy_ret_5d:+.1f}%"
            
        except Exception as e:
            result['details'] = f'Error: {str(e)[:50]}'
        
        return result


class SectorChecker:
    """Check sector momentum"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker
    
    def check(self) -> dict:
        result = {
            'name': 'SECTOR MOMENTUM',
            'score': 0,
            'signal': False,
            'details': '',
            'data': {}
        }
        
        try:
            # Find which sector
            sector = None
            for s, tickers in UNIVERSE.items():
                if self.ticker in tickers:
                    sector = s
                    break
            
            if not sector:
                result['details'] = 'Not in tracked sectors'
                return result
            
            # Get sector peers
            peers = UNIVERSE[sector]
            
            # Calculate sector performance
            returns = []
            for peer in peers[:8]:  # Limit to avoid too many API calls
                try:
                    hist = yf.Ticker(peer).history(period='1mo')
                    if len(hist) >= 5:
                        ret = (hist['Close'].iloc[-1] / hist['Close'].iloc[-5] - 1) * 100
                        returns.append((peer, ret))
                except:
                    continue
            
            if not returns:
                result['details'] = 'Could not get sector data'
                return result
            
            # Sector average
            avg_ret = sum(r[1] for r in returns) / len(returns)
            
            # Our ticker's return
            our_ret = None
            for peer, ret in returns:
                if peer == self.ticker:
                    our_ret = ret
                    break
            
            # Score it
            score = 0
            
            # Sector momentum
            if avg_ret > 10:
                score += 35
            elif avg_ret > 5:
                score += 25
            elif avg_ret > 2:
                score += 15
            elif avg_ret > 0:
                score += 10
            
            # Leader or laggard
            if our_ret is not None:
                relative = our_ret - avg_ret
                if relative > 5:
                    score += 25  # Sector leader
                elif relative > 0:
                    score += 15
                elif relative > -5:
                    score += 10  # Laggard catch-up potential
                else:
                    score += 5
            
            # Multiple stocks in sector moving
            strong_movers = sum(1 for _, r in returns if r > 5)
            if strong_movers >= 3:
                score += 20
            elif strong_movers >= 2:
                score += 10
            
            result['score'] = min(score, 100)
            result['signal'] = score >= 50
            result['data'] = {
                'sector': sector,
                'sector_ret': round(avg_ret, 1),
                'our_ret': round(our_ret, 1) if our_ret else 0,
                'strong_movers': strong_movers
            }
            result['details'] = f"{sector}: {avg_ret:+.1f}%, {strong_movers} hot peers"
            
        except Exception as e:
            result['details'] = f'Error: {str(e)[:50]}'
        
        return result


# ============================================================================
# LEVEL CALCULATOR
# ============================================================================

def calculate_levels(ticker: str) -> dict:
    """Calculate support, resistance, stop, targets"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period='3mo')
        
        if len(df) < 20:
            return None
        
        current = df['Close'].iloc[-1]
        
        # Moving averages as support/resistance
        ma_10 = df['Close'].rolling(10).mean().iloc[-1]
        ma_20 = df['Close'].rolling(20).mean().iloc[-1]
        ma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else ma_20
        
        # Recent high/low
        recent_high = df['High'].iloc[-20:].max()
        recent_low = df['Low'].iloc[-20:].min()
        
        # ATR for stop calculation
        df['tr'] = pd.concat([
            df['High'] - df['Low'],
            abs(df['High'] - df['Close'].shift(1)),
            abs(df['Low'] - df['Close'].shift(1))
        ], axis=1).max(axis=1)
        atr = df['tr'].rolling(14).mean().iloc[-1]
        
        # Support = nearest MA below or recent low
        supports = [ma_10, ma_20, ma_50, recent_low]
        support = max([s for s in supports if s < current], default=recent_low)
        
        # Resistance = nearest MA above or recent high
        resistances = [ma_10, ma_20, recent_high]
        resistance = min([r for r in resistances if r > current], default=recent_high)
        
        # Stop = 2 ATR below current or below support
        stop_atr = current - (2 * atr)
        stop_support = support * 0.98  # 2% below support
        stop = max(stop_atr, stop_support)
        
        # Targets
        risk = current - stop
        target_1 = current + (risk * 1.5)  # 1.5:1 R:R
        target_2 = current + (risk * 3)    # 3:1 R:R
        
        # If near resistance, adjust target to resistance
        if target_1 > resistance * 0.98:
            target_1 = resistance
        
        return {
            'current': round(current, 2),
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'stop': round(stop, 2),
            'target_1': round(target_1, 2),
            'target_2': round(target_2, 2),
            'atr': round(atr, 2),
            'stop_pct': round((stop / current - 1) * 100, 1),
            'target_1_pct': round((target_1 / current - 1) * 100, 1),
            'target_2_pct': round((target_2 / current - 1) * 100, 1),
            'risk_per_share': round(current - stop, 2)
        }
        
    except Exception as e:
        return None


# ============================================================================
# THE HUNT - Main Analysis
# ============================================================================

def hunt_ticker(ticker: str, risk_amount: float = 500) -> dict:
    """
    Full analysis on one ticker.
    Returns verdict, signals, levels, position sizing.
    """
    print(f"\n🐺 WOLF HUNT: {ticker}")
    print("=" * 60)
    
    # Initialize checkers
    gamma = GammaChecker(ticker)
    momentum = MomentumChecker(ticker)
    volume = VolumeChecker(ticker)
    short = ShortSqueezeChecker(ticker)
    technical = TechnicalSetupChecker(ticker)
    regime = RegimeChecker()
    sector = SectorChecker(ticker)
    
    # Run all checks
    print("\n📊 Checking signals...")
    
    signals = {
        'gamma': gamma.check(),
        'momentum': momentum.check(),
        'volume': volume.check(),
        'short': short.check(),
        'technical': technical.check(),
        'regime': regime.check(),
        'sector': sector.check()
    }
    
    # Calculate overall conviction
    weights = {
        'gamma': 1.5,      # Gamma is powerful
        'momentum': 1.2,
        'volume': 1.0,
        'short': 1.3,
        'technical': 1.0,
        'regime': 1.2,     # Regime matters
        'sector': 1.0
    }
    
    total_weight = sum(weights.values())
    weighted_score = sum(signals[s]['score'] * weights[s] for s in signals)
    conviction = int(weighted_score / total_weight)
    
    # Count firing signals
    firing = sum(1 for s in signals.values() if s['signal'])
    
    # Determine verdict
    if conviction >= 70 and firing >= 4:
        verdict = "🟢 HUNT"
        verdict_text = "STRONG SETUP - Multiple signals aligned"
    elif conviction >= 55 and firing >= 3:
        verdict = "🟢 HUNT"
        verdict_text = "GOOD SETUP - Enough edge to trade"
    elif conviction >= 45 and firing >= 2:
        verdict = "🟡 STALK"
        verdict_text = "WATCH - Wait for better entry or more signals"
    else:
        verdict = "🔴 PASS"
        verdict_text = "NOT ENOUGH EDGE - Skip this one"
    
    # Get levels
    levels = calculate_levels(ticker)
    
    # Display results
    print(f"\n{'=' * 60}")
    print(f"📊 VERDICT: {verdict}")
    print(f"   Conviction: {conviction}/100")
    print(f"   {verdict_text}")
    print(f"{'=' * 60}")
    
    # Signal stack
    print(f"\n📡 SIGNAL STACK ({firing}/7 firing):")
    print("-" * 60)
    
    for name, data in signals.items():
        status = "✅" if data['signal'] else "❌"
        print(f"{status} {data['name']}: {data['score']}/100 - {data['details']}")
    
    # Levels
    if levels:
        print(f"\n📍 LEVELS:")
        print("-" * 60)
        print(f"   Current:    ${levels['current']:.2f}")
        print(f"   Support:    ${levels['support']:.2f}")
        print(f"   Resistance: ${levels['resistance']:.2f}")
        print(f"   Stop Loss:  ${levels['stop']:.2f} ({levels['stop_pct']:+.1f}%)")
        print(f"   Target 1:   ${levels['target_1']:.2f} ({levels['target_1_pct']:+.1f}%)")
        print(f"   Target 2:   ${levels['target_2']:.2f} ({levels['target_2_pct']:+.1f}%)")
        
        # Position sizing
        print(f"\n💰 POSITION SIZING (${risk_amount} risk):")
        print("-" * 60)
        
        risk_per_share = levels['risk_per_share']
        if risk_per_share > 0:
            shares = int(risk_amount / risk_per_share)
            position_cost = shares * levels['current']
            max_loss = shares * risk_per_share
            profit_t1 = shares * (levels['target_1'] - levels['current'])
            profit_t2 = shares * (levels['target_2'] - levels['current'])
            
            print(f"   Risk per share: ${risk_per_share:.2f}")
            print(f"   Position size:  {shares} shares")
            print(f"   Total cost:     ${position_cost:,.2f}")
            print(f"   Max loss:       ${max_loss:.2f}")
            print(f"   Profit @ T1:    ${profit_t1:.2f} ({profit_t1/max_loss:.1f}:1 R:R)")
            print(f"   Profit @ T2:    ${profit_t2:.2f} ({profit_t2/max_loss:.1f}:1 R:R)")
    
    # The Three Wolves
    print(f"\n🐺 THE THREE WOLVES:")
    print("-" * 60)
    
    # Brokkr - Technical validity
    brokkr_says = "Signal stack valid" if firing >= 3 else "Weak signal stack"
    print(f"   🔧 Brokkr: \"{brokkr_says}\"")
    
    # Fenrir - Setup quality
    if levels:
        rr = (levels['target_1'] - levels['current']) / (levels['current'] - levels['stop']) if levels['current'] > levels['stop'] else 0
        fenrir_says = f"R:R is {rr:.1f}:1 - {'Good' if rr >= 1.5 else 'Weak'}"
    else:
        fenrir_says = "Cannot calculate R:R"
    print(f"   🐺 Fenrir: \"{fenrir_says}\"")
    
    # Tyr - Final decision
    if verdict == "🟢 HUNT":
        tyr_says = f"Enter on pullback to ${levels['support']:.2f}" if levels else "Enter at market"
    elif verdict == "🟡 STALK":
        tyr_says = "Add to watchlist, wait for setup"
    else:
        tyr_says = "Skip - not our hunt"
    print(f"   👑 Tyr: \"{tyr_says}\"")
    
    print(f"\n{'=' * 60}")
    
    return {
        'ticker': ticker,
        'verdict': verdict,
        'conviction': conviction,
        'signals': signals,
        'levels': levels,
        'firing': firing
    }


def scan_universe(risk_amount: float = 500) -> list:
    """Scan entire universe and rank by conviction"""
    print("\n🐺 WOLF PACK HUNT - SCANNING ALL TARGETS")
    print("=" * 60)
    print(f"Scanning {len(ALL_TICKERS)} tickers...\n")
    
    results = []
    
    for i, ticker in enumerate(ALL_TICKERS):
        try:
            print(f"[{i+1}/{len(ALL_TICKERS)}] {ticker}...", end=" ")
            
            # Quick check - don't need full analysis for scan
            gamma = GammaChecker(ticker)
            momentum = MomentumChecker(ticker)
            
            g = gamma.check()
            m = momentum.check()
            
            # Quick conviction
            quick_score = (g['score'] + m['score']) / 2
            
            if quick_score >= 40:  # Worth deeper look
                result = hunt_ticker(ticker, risk_amount)
                results.append(result)
                print(f"✅ {result['verdict']} ({result['conviction']})")
            else:
                print(f"⏭️ Skip ({quick_score:.0f})")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:30]}")
            continue
    
    # Sort by conviction
    results.sort(key=lambda x: x['conviction'], reverse=True)
    
    # Display top picks
    print("\n" + "=" * 60)
    print("🏆 TOP HUNTS - RANKED BY CONVICTION")
    print("=" * 60)
    
    hunts = [r for r in results if "HUNT" in r['verdict']]
    stalks = [r for r in results if "STALK" in r['verdict']]
    
    if hunts:
        print(f"\n🟢 HUNT ({len(hunts)} setups):")
        for r in hunts[:5]:
            print(f"   {r['ticker']:6} - {r['conviction']}/100 - {r['firing']}/7 signals")
    else:
        print("\n⚠️ No strong HUNT setups right now")
    
    if stalks:
        print(f"\n🟡 STALK ({len(stalks)} on watch):")
        for r in stalks[:5]:
            print(f"   {r['ticker']:6} - {r['conviction']}/100 - {r['firing']}/7 signals")
    
    return results


def hunt_today(risk_amount: float = 500):
    """What should I hunt TODAY? Quick answer."""
    print("\n🐺 WHAT TO HUNT TODAY")
    print("=" * 60)
    print(f"Risk budget: ${risk_amount}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # Check regime first
    regime = RegimeChecker().check()
    print(f"\n🌡️ MARKET: {regime['details']}")
    
    if regime['score'] < 40:
        print("\n⚠️  CAUTION: Market regime unfavorable")
        print("   Consider smaller positions or sitting out")
    
    # Quick scan of high-probability targets
    hot_list = ['GME', 'IONQ', 'RGTI', 'MARA', 'SMCI', 'LUNR', 'LEU', 'ARM']
    
    print(f"\n🔍 Quick scanning {len(hot_list)} high-probability targets...")
    
    candidates = []
    
    for ticker in hot_list:
        try:
            result = hunt_ticker(ticker, risk_amount)
            if "HUNT" in result['verdict']:
                candidates.append(result)
        except:
            continue
    
    print("\n" + "=" * 60)
    print("📋 TODAY'S HUNT LIST")
    print("=" * 60)
    
    if candidates:
        # Best candidate
        best = candidates[0]
        print(f"\n🥇 TOP PICK: {best['ticker']}")
        print(f"   Conviction: {best['conviction']}/100")
        print(f"   Signals: {best['firing']}/7 firing")
        if best['levels']:
            print(f"   Entry: ${best['levels']['current']:.2f}")
            print(f"   Stop: ${best['levels']['stop']:.2f}")
            print(f"   Target: ${best['levels']['target_1']:.2f}")
        
        if len(candidates) > 1:
            print(f"\n🥈 ALSO GOOD:")
            for c in candidates[1:3]:
                print(f"   {c['ticker']} - {c['conviction']}/100")
    else:
        print("\n❌ No strong setups found in hot list")
        print("   Run 'wolf_hunt.py scan' for full universe scan")
    
    return candidates


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="🐺 Wolf Hunt - Unified Decision Engine")
    parser.add_argument('command', nargs='?', default='today',
                       help='TICKER for single analysis, "scan" for universe, "today" for quick picks')
    parser.add_argument('--risk', type=float, default=500,
                       help='Risk amount in dollars (default: 500)')
    
    args = parser.parse_args()
    
    if args.command.lower() == 'scan':
        scan_universe(args.risk)
    elif args.command.lower() == 'today':
        hunt_today(args.risk)
    else:
        # Single ticker
        hunt_ticker(args.command.upper(), args.risk)


if __name__ == "__main__":
    main()
