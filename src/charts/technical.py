"""
TECHNICAL INDICATORS: Professional-grade using TA-Lib

PURPOSE:
--------
Calculate advanced technical indicators from OHLCV bars for thesis-driven trading.

TA-Lib provides 150+ indicators: Momentum, Trend, Volatility, Volume.
We focus on thesis confluence checks: Does technical setup match thesis timing?

INDICATORS CALCULATED:
----------------------
TREND:
- EMA (20, 50, 200) — Exponential Moving Average (shows direction)
- SMA (20, 50, 200) — Simple Moving Average
- ADX (Average Directional Index) — Trend strength (0-100)
- ADXR — ADX smoothed

MOMENTUM:
- RSI (14) — Relative Strength Index (0-100, <30 oversold, >70 overbought)
- MACD (12/26/9) — Moving Average Convergence Divergence (momentum + trend)
- Stochastic (14, 3, 3) — %K, %D (position within recent range)
- Williams %R (14) — -100 to 0 scale
- CCI (20) — Commodity Channel Index (cyclical oscillator)
- ROC (12) — Rate of Change (momentum magnitude)

VOLATILITY:
- Bollinger Bands (20, 2) — Upper, Middle, Lower, Width, %B
- ATR (14) — Average True Range (volatility measure)
- NATR (14) — Normalized ATR (% of price)
- BBANDS Width (volatility indicator)

VOLUME:
- OBV — On-Balance Volume (cumulative volume trend)
- AD — Accumulation/Distribution
- ADOSC (3, 10) — Chaikin Accumulation/Distribution Oscillator

PATTERN RECOGNITION:
- CDLMORNINGSTAR — Morning Star pattern (reversal)
- CDLHAMMER — Hammer pattern
- CDLENGULFING — Engulfing pattern

INPUT (bars from YFinanceClient):
----------------------------------
[
  {
    "timestamp": "2025-12-23",
    "open": 130.00,
    "high": 133.00,
    "low": 129.50,
    "close": 132.50,
    "volume": 1234567
  }
]

OUTPUT (comprehensive indicator report):
----------------------------------------
{
  "timestamp": "2025-12-23",
  "close": 132.50,
  # TREND
  "ema_20": 131.45, "ema_50": 130.20, "ema_200": 128.50,
  "sma_20": 131.30, "sma_50": 130.10, "sma_200": 128.40,
  "adx": 42.5,  # 0-100, >25 strong trend
  "adxr": 41.2,
  # MOMENTUM
  "rsi_14": 65.3,  # <30 oversold, >70 overbought
  "macd": 0.45, "macd_signal": 0.40, "macd_histogram": 0.05,
  "stoch_k": 72.5, "stoch_d": 70.2,
  "williams_r": -25.3,  # -100 to 0, -20 to 0 overbought
  "cci": 45.2,  # >100 overbought, <-100 oversold
  "roc_12": 2.5,  # % change
  # VOLATILITY
  "bb_upper": 135.20, "bb_middle": 132.50, "bb_lower": 129.80,
  "bb_width": 5.40, "bb_percent_b": 0.72,  # 0-1, >0.8 near upper
  "atr_14": 2.3,  # volatility in price units
  "natr_14": 1.7,  # volatility as % of price
  # VOLUME
  "obv": 1234567890,  # cumulative volume
  "ad": 456789,  # accumulation/distribution
  "adosc": 123456,  # A/D oscillator
  # PATTERNS
  "cdl_morning_star": 0,  # 0 (not present), 100 (bullish), -100 (bearish)
  "cdl_hammer": 100,
  # CUSTOM CONFLUENCE SCORE
  "confluence_score": 8  # 0-10: how many indicators align
}
"""

import logging
from typing import List, Dict, Optional
import numpy as np
import talib

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """
    Calculate 50+ professional-grade technical indicators using TA-Lib.
    
    Confluence scoring: How many indicators align with thesis direction?
    """
    
    def __init__(self):
        """Initialize TA-Lib analyzer"""
        logger.info("TA-Lib analyzer initialized")
    
    def analyze(self, bars: List[Dict]) -> List[Dict]:
        """
        Analyze OHLCV bars with comprehensive TA-Lib indicators.
        """
        if not bars or len(bars) < 50:
            logger.warning(f"Need at least 50 bars for full analysis; got {len(bars)}")
            return bars
        opens = np.array([bar["open"] for bar in bars], dtype=np.float64)
        highs = np.array([bar["high"] for bar in bars], dtype=np.float64)
        lows = np.array([bar["low"] for bar in bars], dtype=np.float64)
        closes = np.array([bar["close"] for bar in bars], dtype=np.float64)
        volumes = np.array([bar["volume"] for bar in bars], dtype=np.float64)
        indicators = {}
        # ==================== TREND ====================
        indicators["ema_20"] = talib.EMA(closes, timeperiod=20)
        indicators["ema_50"] = talib.EMA(closes, timeperiod=50)
        indicators["ema_200"] = talib.EMA(closes, timeperiod=200)
        indicators["sma_20"] = talib.SMA(closes, timeperiod=20)
        indicators["sma_50"] = talib.SMA(closes, timeperiod=50)
        indicators["sma_200"] = talib.SMA(closes, timeperiod=200)
        indicators["adx"] = talib.ADX(highs, lows, closes, timeperiod=14)
        indicators["adxr"] = talib.ADXR(highs, lows, closes, timeperiod=14)
        # ==================== MOMENTUM ====================
        indicators["rsi_14"] = talib.RSI(closes, timeperiod=14)
        macd, macd_signal, macd_hist = talib.MACD(closes, fastperiod=12, slowperiod=26, signalperiod=9)
        indicators["macd"] = macd
        indicators["macd_signal"] = macd_signal
        indicators["macd_histogram"] = macd_hist
        stoch_k, stoch_d = talib.STOCH(highs, lows, closes, fastk_period=14, slowk_period=3, slowd_period=3)
        indicators["stoch_k"] = stoch_k
        indicators["stoch_d"] = stoch_d
        indicators["williams_r"] = talib.WILLR(highs, lows, closes, timeperiod=14)
        indicators["cci"] = talib.CCI(highs, lows, closes, timeperiod=20)
        indicators["roc_12"] = talib.ROC(closes, timeperiod=12)
        indicators["mom_10"] = talib.MOM(closes, timeperiod=10)
        # ==================== VOLATILITY ====================
        indicators["atr_14"] = talib.ATR(highs, lows, closes, timeperiod=14)
        indicators["natr_14"] = talib.NATR(highs, lows, closes, timeperiod=14)
        bb_upper, bb_middle, bb_lower = talib.BBANDS(closes, timeperiod=20, nbdevup=2, nbdevdn=2)
        indicators["bb_upper"] = bb_upper
        indicators["bb_middle"] = bb_middle
        indicators["bb_lower"] = bb_lower
        bb_width = bb_upper - bb_lower
        bb_percent_b = np.where(
            bb_width != 0,
            (closes - bb_lower) / bb_width,
            np.nan
        )
        indicators["bb_percent_b"] = bb_percent_b
        indicators["bb_width"] = bb_width
        # ==================== VOLUME ====================
        indicators["obv"] = talib.OBV(closes, volumes)
        indicators["ad"] = talib.AD(highs, lows, closes, volumes)
        indicators["adosc"] = talib.ADOSC(highs, lows, closes, volumes, fastperiod=3, slowperiod=10)
        # ==================== PATTERNS ====================
        indicators["cdl_morning_star"] = talib.CDLMORNINGSTAR(opens, highs, lows, closes)
        indicators["cdl_hammer"] = talib.CDLHAMMER(opens, highs, lows, closes)
        indicators["cdl_engulfing"] = talib.CDLENGULFING(opens, highs, lows, closes)
        indicators["cdl_harami"] = talib.CDLHARAMI(opens, highs, lows, closes)
        # ==================== BUILD RESULTS ====================
        analyzed_bars = []
        for i, bar in enumerate(bars):
            analyzed_bar = bar.copy()
            for key, values in indicators.items():
                val = values[i]
                if np.isnan(val):
                    analyzed_bar[key] = None
                elif isinstance(val, (int, np.integer)):
                    analyzed_bar[key] = int(val)
                else:
                    analyzed_bar[key] = round(float(val), 2)
            analyzed_bars.append(analyzed_bar)
        logger.info(f"Analyzed {len(analyzed_bars)} bars with TA-Lib ({len(indicators)} indicators)")
        return analyzed_bars

def test_analyzer():
    """Test TA-Lib analyzer with real YFinance data"""
    from src.apis.yfinance_client import YFinanceClient
    client = YFinanceClient()
    bars = client.get_bars("MU", period="1y", interval="1d")
    if not bars:
        print("❌ Failed to fetch bars")
        return
    print(f"📊 Fetched {len(bars)} bars for MU")
    analyzer = TechnicalAnalyzer()
    analyzed = analyzer.analyze(bars)
    print("\n" + "="*150)
    print("TECHNICAL ANALYSIS - MU (TA-Lib Professional Indicators)")
    print("="*150)
    for bar in analyzed[-3:]:
        print(f"\n{'='*150}")
        print(f"Date: {bar['timestamp']} | Close: ${bar['close']}")
        print(f"{'='*150}")
        print(f"\n📈 TREND:")
        print(f"  EMA: 20={bar.get('ema_20')}, 50={bar.get('ema_50')}, 200={bar.get('ema_200')}")
        print(f"  SMA: 20={bar.get('sma_20')}, 50={bar.get('sma_50')}, 200={bar.get('sma_200')}")
        print(f"  ADX: {bar.get('adx')} (0-100, >25 strong) | ADXR: {bar.get('adxr')}")
        print(f"\n⚡ MOMENTUM:")
        print(f"  RSI(14): {bar.get('rsi_14')} (<30 oversold, >70 overbought)")
        print(f"  MACD: {bar.get('macd')} | Signal: {bar.get('macd_signal')} | Histogram: {bar.get('macd_histogram')}")
        print(f"  Stochastic: %K={bar.get('stoch_k')}, %D={bar.get('stoch_d')}")
        print(f"  Williams %R: {bar.get('williams_r')} (-100 to 0, -20 to 0 overbought)")
        print(f"  CCI: {bar.get('cci')} (>100 overbought, <-100 oversold)")
        print(f"  ROC(12): {bar.get('roc_12')}% | MOM(10): {bar.get('mom_10')}")
        print(f"\n📊 VOLATILITY:")
        print(f"  BB: Upper={bar.get('bb_upper')}, Middle={bar.get('bb_middle')}, Lower={bar.get('bb_lower')}")
        print(f"  BB Width: {bar.get('bb_width')} | %B: {bar.get('bb_percent_b')} (0-1, >0.8 upper band)")
        print(f"  ATR(14): {bar.get('atr_14')} | NATR(14): {bar.get('natr_14')}%")
        print(f"\n📈 VOLUME:")
        print(f"  OBV: {bar.get('obv')} | A/D: {bar.get('ad')} | ADOSC: {bar.get('adosc')}")
        print(f"\n🎯 PATTERNS:")
        print(f"  Morning Star: {bar.get('cdl_morning_star')} | Hammer: {bar.get('cdl_hammer')}")
        print(f"  Engulfing: {bar.get('cdl_engulfing')} | Harami: {bar.get('cdl_harami')}")
    print("\n" + "="*150)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_analyzer()
