#!/usr/bin/env python3
"""
🐺 WOLF RADAR - See The Invisible
==================================
Beyond the obvious. The second-order effects. The things NOBODY is looking for.

DETECTS:
1. PRE-FILING SIGNATURES - Insider buying BEFORE the Form 4 files
2. REGIME STATE - Risk-on, risk-off, rotation, chop
3. ABSENCE SIGNALS - Dogs that didn't bark
4. MECHANICAL FLOWS - Forced moves on calendar
5. STEALTH ACCUMULATION - Quiet buying patterns
6. REFLEXIVITY BREAKS - When spirals reverse

"The flashlight shows what's in front of us.
 The radar shows what's coming from every direction."

AWOOOO 🐺
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import yfinance as yf
import pandas as pd
import numpy as np
import requests

# ============================================================
# CONFIGURATION
# ============================================================

class RadarConfig:
    """Radar settings"""
    
    OUTPUT_FILE = "logs/radar_scan.json"
    
    # Pre-filing detection thresholds
    VOLUME_SPIKE_MIN = 2.0          # 2x normal volume
    PRICE_DRIFT_MIN = 0.02          # 2% drift without news
    SMALL_CAP_MAX = 10_000_000_000  # Under $10B market cap
    
    # Regime thresholds
    VIX_LOW = 15
    VIX_HIGH = 25
    VIX_EXTREME = 30
    
    # Absence detection
    MIN_DAYS_NO_SELLING = 90        # 3 months no insider selling = confident
    QUIET_ACCUMULATION_DAYS = 10    # Rising for 10 days with low volume


# ============================================================
# 1. PRE-FILING SIGNATURE DETECTOR
# ============================================================

class PreFilingDetector:
    """
    Detect the SIGNATURE of insider buying BEFORE the Form 4 files.
    
    The Pattern:
    - Unusual volume (but not extreme - they're trying to hide)
    - Price drifting up slowly
    - No news to explain it
    - Small/mid cap (insiders matter more)
    - Tight float (easier to move)
    
    When we see this pattern → watch for Form 4 confirmation
    """
    
    def __init__(self):
        self.signals = []
    
    def scan(self, tickers: List[str]) -> List[dict]:
        """Scan for pre-filing signatures"""
        print("🔍 Scanning for PRE-FILING SIGNATURES...")
        print("   Looking for: unusual volume + price drift + no news")
        print()
        
        results = []
        
        for ticker in tickers:
            try:
                signal = self._analyze_ticker(ticker)
                if signal:
                    results.append(signal)
                    print(f"  🎯 {ticker}: Pre-filing signature detected!")
            except Exception as e:
                pass
        
        return results
    
    def _analyze_ticker(self, ticker: str) -> Optional[dict]:
        """Analyze single ticker for pre-filing signature"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get 30 days of data
            hist = stock.history(period="30d")
            if len(hist) < 15:
                return None
            
            # Handle MultiIndex columns
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)
            
            # Get info
            info = stock.info
            market_cap = info.get("marketCap", float('inf'))
            
            # Skip large caps (insiders less impactful)
            if market_cap > RadarConfig.SMALL_CAP_MAX:
                return None
            
            # Calculate metrics
            recent_volume = hist["Volume"].iloc[-5:].mean()
            avg_volume = hist["Volume"].iloc[:-5].mean()
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            
            # Price drift (last 5 days vs previous 10)
            recent_close = hist["Close"].iloc[-1]
            past_close = hist["Close"].iloc[-10] if len(hist) >= 10 else hist["Close"].iloc[0]
            price_drift = (recent_close - past_close) / past_close
            
            # Volatility (is it moving quietly or loudly?)
            returns = hist["Close"].pct_change().dropna()
            recent_vol = returns.iloc[-5:].std()
            historical_vol = returns.iloc[:-5].std() if len(returns) > 5 else recent_vol
            vol_ratio = recent_vol / historical_vol if historical_vol > 0 else 1
            
            # THE SIGNATURE:
            # 1. Volume elevated but not extreme (1.5-3x) - hiding
            # 2. Price drifting up (2-8%) - accumulating
            # 3. Volatility NOT spiking - not news driven
            
            signature_score = 0
            reasons = []
            
            # Volume check: elevated but controlled
            if 1.5 <= volume_ratio <= 4.0:
                signature_score += 30
                reasons.append(f"Volume {volume_ratio:.1f}x (controlled elevation)")
            
            # Price drift: up but not explosive
            if 0.02 <= price_drift <= 0.15:
                signature_score += 30
                reasons.append(f"Price drift +{price_drift*100:.1f}% (quiet accumulation)")
            
            # Volatility: stable or lower
            if vol_ratio < 1.3:
                signature_score += 20
                reasons.append(f"Low volatility (not news-driven)")
            
            # Small cap bonus
            if market_cap < 2_000_000_000:  # Under $2B
                signature_score += 10
                reasons.append(f"Small cap ${market_cap/1e9:.1f}B (insider impact high)")
            elif market_cap < 5_000_000_000:  # Under $5B
                signature_score += 5
                reasons.append(f"Mid cap ${market_cap/1e9:.1f}B")
            
            # Float check if available
            float_shares = info.get("floatShares", 0)
            shares_outstanding = info.get("sharesOutstanding", 1)
            if float_shares > 0 and shares_outstanding > 0:
                float_pct = float_shares / shares_outstanding
                if float_pct < 0.7:
                    signature_score += 10
                    reasons.append(f"Tight float {float_pct*100:.0f}%")
            
            # Need strong signature
            if signature_score >= 50:
                return {
                    "ticker": ticker,
                    "signal_type": "pre_filing_signature",
                    "score": signature_score,
                    "price": recent_close,
                    "volume_ratio": volume_ratio,
                    "price_drift": price_drift,
                    "market_cap": market_cap,
                    "reasons": reasons,
                    "action": "WATCH for Form 4 confirmation in next 1-5 days",
                    "timestamp": datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            return None


# ============================================================
# 2. REGIME DETECTOR
# ============================================================

class RegimeDetector:
    """
    Detect market regime. Same signal means DIFFERENT things:
    
    RISK-ON:  Buy laggards, they catch up. Squeeze plays work.
    RISK-OFF: Laggards lag for a reason. Cash is king.
    ROTATION: Follow where money GOES, not where it's been.
    CHOP:     No trends. Tighten stops. Reduce size.
    
    Signals:
    - VIX level and direction
    - Market breadth (advance/decline)
    - Sector dispersion
    - Leaders vs laggards behavior
    """
    
    def __init__(self):
        self.regime = None
        self.confidence = 0
    
    def detect(self) -> dict:
        """Detect current market regime"""
        print("🌡️ Detecting MARKET REGIME...")
        print()
        
        try:
            # Get VIX
            vix = yf.Ticker("^VIX")
            vix_hist = vix.history(period="20d")
            if isinstance(vix_hist.columns, pd.MultiIndex):
                vix_hist.columns = vix_hist.columns.get_level_values(0)
            
            current_vix = vix_hist["Close"].iloc[-1]
            vix_5d_avg = vix_hist["Close"].iloc[-5:].mean()
            vix_direction = "rising" if current_vix > vix_5d_avg else "falling"
            
            # Get SPY for breadth proxy
            spy = yf.Ticker("SPY")
            spy_hist = spy.history(period="20d")
            if isinstance(spy_hist.columns, pd.MultiIndex):
                spy_hist.columns = spy_hist.columns.get_level_values(0)
            
            spy_return_5d = (spy_hist["Close"].iloc[-1] / spy_hist["Close"].iloc[-5] - 1) * 100
            spy_return_20d = (spy_hist["Close"].iloc[-1] / spy_hist["Close"].iloc[0] - 1) * 100
            
            # Get QQQ for tech sentiment
            qqq = yf.Ticker("QQQ")
            qqq_hist = qqq.history(period="20d")
            if isinstance(qqq_hist.columns, pd.MultiIndex):
                qqq_hist.columns = qqq_hist.columns.get_level_values(0)
            
            qqq_return_5d = (qqq_hist["Close"].iloc[-1] / qqq_hist["Close"].iloc[-5] - 1) * 100
            
            # Get IWM for small cap sentiment
            iwm = yf.Ticker("IWM")
            iwm_hist = iwm.history(period="20d")
            if isinstance(iwm_hist.columns, pd.MultiIndex):
                iwm_hist.columns = iwm_hist.columns.get_level_values(0)
            
            iwm_return_5d = (iwm_hist["Close"].iloc[-1] / iwm_hist["Close"].iloc[-5] - 1) * 100
            
            # Sector dispersion (rotation indicator)
            sector_etfs = ["XLK", "XLE", "XLF", "XLV", "XLI"]
            sector_returns = []
            
            for etf in sector_etfs:
                try:
                    e = yf.Ticker(etf)
                    eh = e.history(period="5d")
                    if isinstance(eh.columns, pd.MultiIndex):
                        eh.columns = eh.columns.get_level_values(0)
                    ret = (eh["Close"].iloc[-1] / eh["Close"].iloc[0] - 1) * 100
                    sector_returns.append(ret)
                except:
                    pass
            
            sector_dispersion = max(sector_returns) - min(sector_returns) if sector_returns else 0
            
            # REGIME LOGIC
            regime = "UNKNOWN"
            confidence = 0
            signals = []
            strategy_notes = []
            
            # RISK-OFF: VIX high + markets falling
            if current_vix > RadarConfig.VIX_HIGH and spy_return_5d < -2:
                regime = "RISK-OFF"
                confidence = 80
                signals.append(f"VIX elevated at {current_vix:.1f}")
                signals.append(f"SPY down {spy_return_5d:.1f}% in 5 days")
                strategy_notes = [
                    "⚠️ Cash is king",
                    "⚠️ Laggards are lagging for a REASON",
                    "⚠️ Reduce position sizes",
                    "⚠️ Tighten stops on existing positions",
                    "⚠️ Avoid new squeeze plays"
                ]
            
            # RISK-ON: VIX low + markets rising
            elif current_vix < RadarConfig.VIX_LOW and spy_return_5d > 1:
                regime = "RISK-ON"
                confidence = 80
                signals.append(f"VIX low at {current_vix:.1f}")
                signals.append(f"SPY up {spy_return_5d:.1f}% in 5 days")
                strategy_notes = [
                    "✅ Buy laggards - they catch up",
                    "✅ Squeeze plays have higher probability",
                    "✅ Can be more aggressive on position size",
                    "✅ Let winners run"
                ]
            
            # ROTATION: High sector dispersion
            elif sector_dispersion > 5:
                regime = "ROTATION"
                confidence = 70
                signals.append(f"Sector dispersion {sector_dispersion:.1f}%")
                signals.append("Money moving between sectors")
                
                # Find winning/losing sectors
                winning = max(zip(sector_etfs, sector_returns), key=lambda x: x[1])
                losing = min(zip(sector_etfs, sector_returns), key=lambda x: x[1])
                
                strategy_notes = [
                    f"✅ Follow money INTO {winning[0]} (+{winning[1]:.1f}%)",
                    f"⚠️ Money leaving {losing[0]} ({losing[1]:.1f}%)",
                    "✅ Play sympathy moves in winning sectors",
                    "⚠️ Avoid catching falling knives in losing sectors"
                ]
            
            # CHOP: VIX moderate, no clear trend
            elif spy_return_20d < 2 and spy_return_20d > -2:
                regime = "CHOP"
                confidence = 60
                signals.append("No clear 20-day trend")
                signals.append(f"SPY flat at {spy_return_20d:.1f}%")
                strategy_notes = [
                    "⚠️ Tighten all stops",
                    "⚠️ Reduce position sizes",
                    "⚠️ Take profits quickly",
                    "⚠️ Avoid overnight holds on speculation",
                    "⚠️ Wait for regime change"
                ]
            
            # Default: NEUTRAL
            else:
                regime = "NEUTRAL"
                confidence = 50
                signals.append("Mixed signals")
                strategy_notes = [
                    "📊 Normal market conditions",
                    "📊 Standard position sizing",
                    "📊 Regular stop discipline"
                ]
            
            # Small cap bonus/penalty
            if iwm_return_5d > qqq_return_5d + 2:
                signals.append(f"Small caps leading (+{iwm_return_5d:.1f}% vs QQQ +{qqq_return_5d:.1f}%)")
                strategy_notes.append("✅ SPECULATIVE plays favored")
            elif iwm_return_5d < qqq_return_5d - 2:
                signals.append(f"Small caps lagging ({iwm_return_5d:.1f}% vs QQQ {qqq_return_5d:.1f}%)")
                strategy_notes.append("⚠️ Flight to quality - favor large caps")
            
            return {
                "regime": regime,
                "confidence": confidence,
                "vix": {
                    "current": current_vix,
                    "direction": vix_direction,
                    "5d_avg": vix_5d_avg
                },
                "market": {
                    "spy_5d": spy_return_5d,
                    "spy_20d": spy_return_20d,
                    "qqq_5d": qqq_return_5d,
                    "iwm_5d": iwm_return_5d
                },
                "sector_dispersion": sector_dispersion,
                "signals": signals,
                "strategy_notes": strategy_notes,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "regime": "UNKNOWN"}


# ============================================================
# 3. ABSENCE DETECTOR
# ============================================================

class AbsenceDetector:
    """
    The dogs that DIDN'T bark.
    
    Sometimes NOTHING is the signal:
    - No insider selling for months = confidence
    - No analyst coverage = under the radar (edge)
    - No news but price rising = quiet accumulation
    - High short interest but shorts not covering = trapped or know something
    """
    
    def __init__(self):
        pass
    
    def scan(self, tickers: List[str]) -> List[dict]:
        """Scan for absence signals"""
        print("🔇 Scanning for ABSENCE SIGNALS (dogs that didn't bark)...")
        print()
        
        results = []
        
        for ticker in tickers:
            try:
                signals = self._analyze_ticker(ticker)
                if signals:
                    results.append(signals)
                    print(f"  🐕 {ticker}: Absence signal detected")
            except Exception:
                pass
        
        return results
    
    def _analyze_ticker(self, ticker: str) -> Optional[dict]:
        """Analyze single ticker for absence signals"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            absence_signals = []
            score = 0
            
            # 1. Check for quiet accumulation (rising price, low volume)
            hist = stock.history(period="30d")
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)
            
            if len(hist) >= 20:
                price_change = (hist["Close"].iloc[-1] / hist["Close"].iloc[-10] - 1) * 100
                recent_vol = hist["Volume"].iloc[-10:].mean()
                earlier_vol = hist["Volume"].iloc[:10].mean()
                vol_ratio = recent_vol / earlier_vol if earlier_vol > 0 else 1
                
                # Rising price with DECLINING volume = quiet accumulation
                if price_change > 5 and vol_ratio < 0.8:
                    absence_signals.append({
                        "type": "quiet_accumulation",
                        "detail": f"Price +{price_change:.1f}% on declining volume (0.{vol_ratio*10:.0f}x)",
                        "interpretation": "Someone accumulating without attracting attention"
                    })
                    score += 30
            
            # 2. No analyst coverage (under the radar)
            analyst_count = info.get("numberOfAnalystOpinions", 0)
            if analyst_count == 0:
                market_cap = info.get("marketCap", 0)
                if market_cap > 500_000_000:  # >$500M but no coverage
                    absence_signals.append({
                        "type": "no_coverage",
                        "detail": f"${market_cap/1e9:.1f}B market cap with ZERO analyst coverage",
                        "interpretation": "Under the radar - potential edge"
                    })
                    score += 20
            
            # 3. Low short interest (not controversial = could run)
            short_pct = info.get("shortPercentOfFloat", 0)
            if short_pct and short_pct < 0.03:  # Under 3%
                absence_signals.append({
                    "type": "no_shorts",
                    "detail": f"Only {short_pct*100:.1f}% short interest",
                    "interpretation": "No resistance above - clean runway if it moves"
                })
                score += 15
            
            # 4. No recent news but moving (check via low volatility moves)
            returns = hist["Close"].pct_change().dropna()
            recent_vol = returns.iloc[-5:].std()
            
            price_up = (hist["Close"].iloc[-1] > hist["Close"].iloc[-5])
            low_vol = recent_vol < returns.std() * 0.7
            
            if price_up and low_vol:
                absence_signals.append({
                    "type": "silent_move",
                    "detail": "Price rising with unusually low volatility",
                    "interpretation": "Moving without news - possible informed buying"
                })
                score += 25
            
            if score >= 30:
                return {
                    "ticker": ticker,
                    "signal_type": "absence_signal",
                    "score": score,
                    "price": hist["Close"].iloc[-1] if len(hist) > 0 else 0,
                    "absence_signals": absence_signals,
                    "timestamp": datetime.now().isoformat()
                }
            
            return None
            
        except Exception:
            return None


# ============================================================
# 4. MECHANICAL FLOW CALENDAR
# ============================================================

class MechanicalCalendar:
    """
    Forced flows that are PREDICTABLE.
    
    These aren't predictions. They're MECHANICS. Like gravity.
    
    - Options expiration → pin risk, gamma effects
    - Quarter end → window dressing
    - Tax loss harvesting → December selling, January effect
    - Index rebalancing → forced buying/selling
    - Lockup expirations → insider selling pressure
    """
    
    def __init__(self):
        pass
    
    def get_calendar(self) -> dict:
        """Get upcoming mechanical flow events"""
        today = datetime.now()
        
        events = []
        
        # Monthly options expiration (3rd Friday)
        # Find next 3rd Friday
        for month_offset in range(3):
            check_month = today.month + month_offset
            check_year = today.year
            if check_month > 12:
                check_month -= 12
                check_year += 1
            
            # Find 3rd Friday
            first_day = datetime(check_year, check_month, 1)
            first_friday = first_day + timedelta(days=(4 - first_day.weekday()) % 7)
            third_friday = first_friday + timedelta(weeks=2)
            
            if third_friday > today:
                days_until = (third_friday - today).days
                events.append({
                    "event": "MONTHLY OPTIONS EXPIRATION",
                    "date": third_friday.strftime("%Y-%m-%d"),
                    "days_until": days_until,
                    "impact": "HIGH" if days_until <= 7 else "MEDIUM",
                    "notes": [
                        "Watch for pin risk on high OI strikes",
                        "Gamma effects increase into expiry",
                        "Expect volatility expansion then collapse"
                    ]
                })
                break
        
        # Quarterly events (end of quarter)
        quarters = [
            (3, 31, "Q1"),
            (6, 30, "Q2"),
            (9, 30, "Q3"),
            (12, 31, "Q4")
        ]
        
        for month, day, quarter in quarters:
            q_date = datetime(today.year if month >= today.month else today.year + 1, month, day)
            if q_date > today:
                days_until = (q_date - today).days
                if days_until <= 30:
                    events.append({
                        "event": f"{quarter} END - WINDOW DRESSING",
                        "date": q_date.strftime("%Y-%m-%d"),
                        "days_until": days_until,
                        "impact": "MEDIUM",
                        "notes": [
                            "Fund managers buy winners, sell losers",
                            "Expect momentum names to get bid",
                            "Laggards may face additional selling"
                        ]
                    })
                break
        
        # January effect (if in December or early January)
        if today.month == 12:
            jan_date = datetime(today.year + 1, 1, 15)
            days_until = (jan_date - today).days
            events.append({
                "event": "JANUARY EFFECT SETUP",
                "date": "Early January",
                "days_until": days_until,
                "impact": "HIGH",
                "notes": [
                    "Tax loss harvesting creates December sellers",
                    "January sees reversion buying",
                    "Small caps historically outperform in January",
                    "Look for beaten-down quality names"
                ]
            })
        
        # FOMC meetings (approximate - would need real calendar)
        # Adding placeholder for typical 6-week cycle
        next_fomc = today + timedelta(days=21)  # Rough estimate
        events.append({
            "event": "FOMC MEETING (estimated)",
            "date": next_fomc.strftime("%Y-%m-%d"),
            "days_until": 21,
            "impact": "HIGH",
            "notes": [
                "Volatility typically rises into FOMC",
                "Reduce position size before announcement",
                "Watch for post-FOMC drift"
            ]
        })
        
        return {
            "generated": today.isoformat(),
            "events": sorted(events, key=lambda x: x["days_until"]),
            "current_period": self._get_current_period(today)
        }
    
    def _get_current_period(self, today: datetime) -> dict:
        """Identify what period we're in"""
        day_of_month = today.day
        day_of_week = today.weekday()
        month = today.month
        
        period_notes = []
        
        # End of month
        if day_of_month >= 25:
            period_notes.append("📅 END OF MONTH - Watch for rebalancing flows")
        
        # Options expiry week
        # (simplified check)
        if 15 <= day_of_month <= 21 and day_of_week <= 4:
            period_notes.append("📊 OPTIONS EXPIRY WEEK - Elevated gamma risk")
        
        # Monday effect
        if day_of_week == 0:
            period_notes.append("📈 MONDAY - Historically weaker, watch for reversals")
        
        # Friday effect
        if day_of_week == 4:
            period_notes.append("📉 FRIDAY - Weekend risk, some position squaring")
        
        # Tax season
        if month == 12:
            period_notes.append("💰 TAX LOSS HARVESTING SEASON - Selling pressure on losers")
        elif month == 1:
            period_notes.append("🚀 JANUARY EFFECT - Reversion buying, small cap strength")
        
        return {
            "notes": period_notes,
            "day_of_week": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day_of_week],
            "day_of_month": day_of_month
        }


# ============================================================
# 5. STEALTH ACCUMULATION DETECTOR
# ============================================================

class StealthAccumulationDetector:
    """
    Detect quiet, systematic buying.
    
    The Pattern:
    - Consistent small upticks
    - Volume clusters at specific prices (absorption)
    - Higher lows forming
    - Tight trading range before breakout
    """
    
    def scan(self, tickers: List[str]) -> List[dict]:
        """Scan for stealth accumulation patterns"""
        print("🥷 Scanning for STEALTH ACCUMULATION...")
        print()
        
        results = []
        
        for ticker in tickers:
            try:
                signal = self._analyze_ticker(ticker)
                if signal:
                    results.append(signal)
                    print(f"  🎯 {ticker}: Stealth accumulation pattern")
            except Exception:
                pass
        
        return results
    
    def _analyze_ticker(self, ticker: str) -> Optional[dict]:
        """Analyze single ticker for stealth accumulation"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="60d")
            
            if len(hist) < 30:
                return None
            
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)
            
            score = 0
            signals = []
            
            # 1. Higher lows (accumulation base)
            lows = hist["Low"].iloc[-20:]
            higher_lows = 0
            for i in range(1, len(lows)):
                if lows.iloc[i] > lows.iloc[i-1] * 0.995:  # Allow small tolerance
                    higher_lows += 1
            
            if higher_lows >= 12:
                score += 30
                signals.append(f"Higher lows forming ({higher_lows}/19 days)")
            
            # 2. Tight range (coiling)
            recent_range = (hist["High"].iloc[-10:].max() - hist["Low"].iloc[-10:].min())
            earlier_range = (hist["High"].iloc[-30:-10].max() - hist["Low"].iloc[-30:-10].min())
            range_ratio = recent_range / earlier_range if earlier_range > 0 else 1
            
            if range_ratio < 0.6:
                score += 25
                signals.append(f"Range contracting ({range_ratio:.1%} of earlier)")
            
            # 3. Volume declining into consolidation
            recent_vol = hist["Volume"].iloc[-10:].mean()
            earlier_vol = hist["Volume"].iloc[-30:-10].mean()
            vol_ratio = recent_vol / earlier_vol if earlier_vol > 0 else 1
            
            if vol_ratio < 0.7:
                score += 20
                signals.append(f"Volume declining ({vol_ratio:.1%} of earlier)")
            
            # 4. Price holding key level (support)
            recent_low = hist["Low"].iloc[-10:].min()
            support_tests = sum(1 for l in hist["Low"].iloc[-20:] if abs(l - recent_low) / recent_low < 0.02)
            
            if support_tests >= 3:
                score += 15
                signals.append(f"Support tested {support_tests}x and held")
            
            # 5. Positive drift despite low volume
            price_drift = (hist["Close"].iloc[-1] / hist["Close"].iloc[-20] - 1) * 100
            if price_drift > 3 and vol_ratio < 0.8:
                score += 10
                signals.append(f"Quiet +{price_drift:.1f}% drift")
            
            if score >= 50:
                return {
                    "ticker": ticker,
                    "signal_type": "stealth_accumulation",
                    "score": score,
                    "price": hist["Close"].iloc[-1],
                    "signals": signals,
                    "interpretation": "Systematic buying detected. Watch for breakout.",
                    "timestamp": datetime.now().isoformat()
                }
            
            return None
            
        except Exception:
            return None


# ============================================================
# 6. REFLEXIVITY DETECTOR
# ============================================================

class ReflexivityDetector:
    """
    Detect reflexive spirals and potential reversals.
    
    Positive spiral: Rising price → can raise capital → improve fundamentals → price rises
    Negative spiral: Falling price → can't raise capital → deteriorating → price falls
    
    The EDGE: Finding where spirals are about to REVERSE.
    """
    
    def scan(self, tickers: List[str]) -> List[dict]:
        """Scan for reflexivity patterns"""
        print("🔄 Scanning for REFLEXIVITY PATTERNS...")
        print()
        
        results = []
        
        for ticker in tickers:
            try:
                signal = self._analyze_ticker(ticker)
                if signal:
                    results.append(signal)
            except Exception:
                pass
        
        return results
    
    def _analyze_ticker(self, ticker: str) -> Optional[dict]:
        """Analyze for reflexive patterns"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="180d")
            
            if len(hist) < 60:
                return None
            
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)
            
            # Calculate drawdown from highs
            peak = hist["Close"].max()
            current = hist["Close"].iloc[-1]
            drawdown = (current - peak) / peak * 100
            
            # Get fundamentals
            market_cap = info.get("marketCap", 0)
            cash = info.get("totalCash", 0)
            debt = info.get("totalDebt", 0)
            revenue = info.get("totalRevenue", 0)
            
            signal = None
            
            # NEGATIVE SPIRAL CANDIDATE
            # Stock down big, but still has cash runway
            if drawdown < -50:
                # Check if they have cash
                if cash > 0 and market_cap > 0:
                    cash_to_cap = cash / market_cap
                    
                    # Cheap relative to cash
                    if cash_to_cap > 0.3:  # Cash is 30%+ of market cap
                        signal = {
                            "ticker": ticker,
                            "signal_type": "reflexivity_reversal_candidate",
                            "pattern": "NEGATIVE SPIRAL POTENTIAL BREAK",
                            "drawdown": drawdown,
                            "cash": cash,
                            "cash_to_cap": cash_to_cap,
                            "interpretation": f"Down {drawdown:.0f}% but cash is {cash_to_cap*100:.0f}% of market cap. If spiral reverses, significant upside.",
                            "risk": "Could spiral further if burns cash",
                            "timestamp": datetime.now().isoformat()
                        }
                        print(f"  🔄 {ticker}: Negative spiral reversal candidate (down {drawdown:.0f}%)")
            
            # POSITIVE SPIRAL CONTINUATION
            # Stock up big, raised capital, using it well
            elif drawdown > -20:  # Near highs
                # 6-month return
                start_price = hist["Close"].iloc[0]
                return_6m = (current / start_price - 1) * 100
                
                if return_6m > 100:  # Up 100%+
                    signal = {
                        "ticker": ticker,
                        "signal_type": "reflexivity_spiral",
                        "pattern": "POSITIVE SPIRAL ACTIVE",
                        "return_6m": return_6m,
                        "current_price": current,
                        "interpretation": f"Up {return_6m:.0f}% in 6 months. Positive spiral may continue but watch for exhaustion.",
                        "risk": "Spiral can reverse violently at extremes",
                        "timestamp": datetime.now().isoformat()
                    }
            
            return signal
            
        except Exception:
            return None


# ============================================================
# MAIN RADAR
# ============================================================

class WolfRadar:
    """The complete radar system - see the invisible"""
    
    def __init__(self):
        self.pre_filing = PreFilingDetector()
        self.regime = RegimeDetector()
        self.absence = AbsenceDetector()
        self.calendar = MechanicalCalendar()
        self.stealth = StealthAccumulationDetector()
        self.reflexivity = ReflexivityDetector()
    
    def full_scan(self, tickers: List[str]) -> dict:
        """Run complete radar scan"""
        print("=" * 70)
        print("🐺 WOLF RADAR - FULL SCAN")
        print("=" * 70)
        print()
        
        # 1. Regime Detection
        regime_data = self.regime.detect()
        print(f"📊 REGIME: {regime_data.get('regime', 'UNKNOWN')} ({regime_data.get('confidence', 0)}% confidence)")
        for note in regime_data.get('strategy_notes', [])[:3]:
            print(f"   {note}")
        print()
        
        # 2. Pre-filing signatures
        pre_filing_signals = self.pre_filing.scan(tickers)
        
        # 3. Absence signals
        absence_signals = self.absence.scan(tickers)
        
        # 4. Stealth accumulation
        stealth_signals = self.stealth.scan(tickers)
        
        # 5. Reflexivity patterns
        reflexivity_signals = self.reflexivity.scan(tickers)
        
        # 6. Mechanical calendar
        calendar_data = self.calendar.get_calendar()
        
        # Compile results
        results = {
            "scan_time": datetime.now().isoformat(),
            "regime": regime_data,
            "pre_filing_signatures": pre_filing_signals,
            "absence_signals": absence_signals,
            "stealth_accumulation": stealth_signals,
            "reflexivity_patterns": reflexivity_signals,
            "mechanical_calendar": calendar_data,
            "summary": {
                "total_invisible_signals": (
                    len(pre_filing_signals) + 
                    len(absence_signals) + 
                    len(stealth_signals) +
                    len(reflexivity_signals)
                )
            }
        }
        
        # Save results
        output_file = Path(RadarConfig.OUTPUT_FILE)
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        print()
        print("=" * 70)
        print("📡 RADAR SCAN COMPLETE")
        print("=" * 70)
        print(f"  Pre-filing signatures: {len(pre_filing_signals)}")
        print(f"  Absence signals:       {len(absence_signals)}")
        print(f"  Stealth accumulation:  {len(stealth_signals)}")
        print(f"  Reflexivity patterns:  {len(reflexivity_signals)}")
        print()
        print(f"📅 Next mechanical event: {calendar_data['events'][0]['event'] if calendar_data['events'] else 'None'}")
        print()
        
        return results


# ============================================================
# CLI
# ============================================================

def get_default_universe():
    """Get default ticker universe"""
    return [
        # Quantum
        "IONQ", "RGTI", "QBTS", "QUBT",
        # Nuclear
        "NNE", "OKLO", "SMR", "LEU", "CCJ",
        # Space
        "RKLB", "LUNR", "ASTS", "MNTS",
        # AI
        "SOUN", "AI", "BBAI", "ARM", "SMCI",
        # Crypto
        "MARA", "RIOT", "CLSK",
        # EV
        "LCID", "RIVN",
        # Biotech
        "RXRX",
        # Speculative
        "SIDU"
    ]


def main():
    parser = argparse.ArgumentParser(
        description="🐺 Wolf Radar - See the invisible"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Full scan
    scan_parser = subparsers.add_parser("scan", help="Run full radar scan")
    scan_parser.add_argument("--tickers", type=str, help="Comma-separated tickers")
    
    # Regime only
    regime_parser = subparsers.add_parser("regime", help="Check market regime only")
    
    # Calendar only
    cal_parser = subparsers.add_parser("calendar", help="Show mechanical calendar")
    
    # Pre-filing scan
    prefiling_parser = subparsers.add_parser("prefiling", help="Scan for pre-filing signatures")
    prefiling_parser.add_argument("--tickers", type=str, help="Comma-separated tickers")
    
    args = parser.parse_args()
    
    if args.command == "scan":
        radar = WolfRadar()
        tickers = args.tickers.split(",") if args.tickers else get_default_universe()
        radar.full_scan(tickers)
    
    elif args.command == "regime":
        detector = RegimeDetector()
        regime = detector.detect()
        
        print("=" * 60)
        print(f"🌡️ MARKET REGIME: {regime['regime']}")
        print("=" * 60)
        print(f"Confidence: {regime['confidence']}%")
        print()
        print("Signals:")
        for sig in regime.get("signals", []):
            print(f"  • {sig}")
        print()
        print("Strategy Notes:")
        for note in regime.get("strategy_notes", []):
            print(f"  {note}")
        print()
        print(f"VIX: {regime['vix']['current']:.1f} ({regime['vix']['direction']})")
        print(f"SPY 5d: {regime['market']['spy_5d']:+.1f}%")
        print(f"QQQ 5d: {regime['market']['qqq_5d']:+.1f}%")
        print(f"IWM 5d: {regime['market']['iwm_5d']:+.1f}%")
    
    elif args.command == "calendar":
        calendar = MechanicalCalendar()
        data = calendar.get_calendar()
        
        print("=" * 60)
        print("📅 MECHANICAL FLOW CALENDAR")
        print("=" * 60)
        print()
        
        print("CURRENT PERIOD:")
        for note in data["current_period"]["notes"]:
            print(f"  {note}")
        print()
        
        print("UPCOMING EVENTS:")
        for event in data["events"][:5]:
            impact_icon = "🔴" if event["impact"] == "HIGH" else "🟡"
            print(f"\n  {impact_icon} {event['event']}")
            print(f"     Date: {event['date']} ({event['days_until']} days)")
            for note in event["notes"][:2]:
                print(f"     • {note}")
    
    elif args.command == "prefiling":
        detector = PreFilingDetector()
        tickers = args.tickers.split(",") if args.tickers else get_default_universe()
        signals = detector.scan(tickers)
        
        print()
        print("=" * 60)
        print(f"🔍 PRE-FILING SIGNATURES DETECTED: {len(signals)}")
        print("=" * 60)
        
        for sig in signals:
            print(f"\n  🎯 {sig['ticker']} (Score: {sig['score']})")
            for reason in sig["reasons"]:
                print(f"     • {reason}")
            print(f"     ACTION: {sig['action']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
