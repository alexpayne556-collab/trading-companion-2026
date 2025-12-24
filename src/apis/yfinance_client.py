"""
YFINANCE CLIENT: Pull real OHLCV data (free, no API key required)

PURPOSE:
--------
Fetch real price/volume data from Yahoo Finance for technical analysis.
No API key, no rate limits, reliable historical data.

DATA FLOW:
----------
YFinanceClient.get_bars(symbol="MU", period="6mo", interval="1d")
    → returns real OHLCV bars
    → TechnicalAnalyzer calculates indicators
    → indicators stored to JSONL

YFINANCE ADVANTAGES:
- Free (no API key needed)
- No rate limits
- Real data (Yahoo Finance backed)
- Historical data available (years back)
- Works for all US stocks

INPUT PARAMETERS:
-----------------
period: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
interval: "1m", "5m", "15m", "30m", "60m", "1d", "1wk", "1mo"

OUTPUT (converted to standard format):
--------------------------------------
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
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional

import yfinance as yf

logger = logging.getLogger(__name__)


class YFinanceClient:
    """
    Yahoo Finance API client for pulling real OHLCV bars.
    
    No API key needed. Real data, no rate limits.
    """
    
    def __init__(self):
        """Initialize YFinance client (no credentials needed)"""
        logger.info("YFinance client initialized")
    
    def get_bars(
        self,
        symbol: str,
        period: str = "6mo",
        interval: str = "1d"
    ) -> List[Dict]:
        """
        Fetch real OHLCV bars from Yahoo Finance.
        """
        try:
            # Download data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            # Check if we got data
            if df.empty:
                logger.warning(f"No data returned for {symbol} ({period}/{interval})")
                return []
            # Convert pandas DataFrame to list of dicts
            bars = []
            for date, row in df.iterrows():
                # Handle both datetime and date indices
                if hasattr(date, 'strftime'):
                    timestamp_str = date.strftime("%Y-%m-%d")
                else:
                    timestamp_str = str(date)
                bar = {
                    "timestamp": timestamp_str,
                    "open": round(float(row["Open"]), 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "close": round(float(row["Close"]), 2),
                    "volume": int(row["Volume"]) if "Volume" in row else 0
                }
                bars.append(bar)
            logger.info(f"Fetched {len(bars)} bars for {symbol} ({period}/{interval})")
            return bars
        except Exception as e:
            logger.error(f"Failed to fetch bars for {symbol}: {e}")
            return []
    def get_latest_bar(self, symbol: str) -> Optional[Dict]:
        """
        Fetch only the most recent bar.
        """
        bars = self.get_bars(symbol, period="5d", interval="1d")
        return bars[-1] if bars else None

def test_connection():
    """Test YFinance connection (run as: python -m src.apis.yfinance_client)"""
    try:
        client = YFinanceClient()
        # Fetch daily bars for MU (past 6 months)
        bars = client.get_bars("MU", period="6mo", interval="1d")
        if bars:
            print(f"✅ Connected to Yahoo Finance")
            print(f"Fetched {len(bars)} bars for MU (6 months daily)")
            latest = bars[-1]  # Most recent bar
            print(f"\nLatest bar (MU):")
            print(f"  Date: {latest['timestamp']}")
            print(f"  Close: ${latest['close']}")
            print(f"  High: ${latest['high']}")
            print(f"  Low: ${latest['low']}")
            print(f"  Volume: {latest['volume']:.0f}")
        else:
            print("❌ No bars returned")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
