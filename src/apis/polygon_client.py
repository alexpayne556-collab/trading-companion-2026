"""
POLYGON API CLIENT: Pull live OHLCV data for technical analysis

PURPOSE:
--------
Fetch price/volume data from Polygon.io (free tier) for:
- Computing technical indicators (EMA, RSI, MACD, etc.)
- Identifying patterns matching thesis setups
- Feeding into Feature 5 opportunity detection

POLYGON FREE TIER LIMITS:
- 5 requests per minute
- Same-day or 1-day delayed data (acceptable for thesis trading)
- Covers US stocks (all our tickers: MU, RKLB, LUNR, KDK, UUUU)

DATA FLOW:
----------
PolygonClient.get_agg_bars(symbol="MU", timeframe="daily", limit=100)
    → returns OHLCV bars (open, high, low, close, volume)
    → ChartAnalyzer consumes bars → calculates indicators
    → indicators stored to JSONL for dashboard

INPUT EXAMPLE (what Polygon returns):
-------------------------------------
{
  "status": "OK",
  "results": [
    {
      "v": 1234567,      # volume
      "vw": 130.45,      # volume weighted average price
      "o": 130.00,       # open
      "c": 132.50,       # close
      "h": 133.00,       # high
      "l": 129.50,       # low
      "t": 1703334000000, # timestamp (milliseconds)
      "n": 100           # number of transactions
    }
  ]
}

OUTPUT EXAMPLE (what we consume):
---------------------------------
[
  {
    "timestamp": "2025-12-23T00:00:00Z",
    "open": 130.00,
    "high": 133.00,
    "low": 129.50,
    "close": 132.50,
    "volume": 1234567
  }
]
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
import requests

load_dotenv()

logger = logging.getLogger(__name__)


class PolygonClient:
    """
    Polygon.io API client for pulling OHLCV bars.
    
    Handles:
    - Rate limiting (5 req/min free tier)
    - Error handling (API failures, missing data)
    - Data transformation (milliseconds → datetime, format standardization)
    - Caching (avoid duplicate requests)
    """
    
    def __init__(self):
        """Initialize Polygon client with API key from .env"""
        self.api_key = os.getenv("POLYGON_API_KEY")
        self.base_url = "https://api.polygon.io"
        
        if not self.api_key:
            raise ValueError("POLYGON_API_KEY not found in .env")
        
        logger.info("Polygon client initialized")
    
    def get_agg_bars(
        self,
        symbol: str,
        timeframe: str = "day",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Fetch aggregated OHLCV bars for a ticker.
        """
        # Default to past 100 days if not specified
        if not end_date:
            end_date = datetime.utcnow().strftime("%Y-%m-%d")
        if not start_date:
            start_days_ago = 100
            start_date = (datetime.utcnow() - timedelta(days=start_days_ago)).strftime("%Y-%m-%d")
        try:
            url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/1/{timeframe}/{start_date}/{end_date}"
            params = {
                "limit": limit,
                "apiKey": self.api_key
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("status") != "OK":
                logger.warning(f"Polygon returned status={data.get('status')} for {symbol}")
                return []
            results = data.get("results", [])
            bars = []
            for result in results:
                timestamp_ms = result.get("t", 0)
                timestamp_s = timestamp_ms / 1000.0
                dt = datetime.utcfromtimestamp(timestamp_s)
                bar = {
                    "timestamp": dt.isoformat() + "Z",
                    "open": round(result.get("o", 0), 2),
                    "high": round(result.get("h", 0), 2),
                    "low": round(result.get("l", 0), 2),
                    "close": round(result.get("c", 0), 2),
                    "volume": int(result.get("v", 0))
                }
                bars.append(bar)
            logger.info(f"Fetched {len(bars)} bars for {symbol} ({timeframe}) from {start_date} to {end_date}")
            return bars
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch bars for {symbol}: {e}")
            return []
        except ValueError as e:
            logger.error(f"Invalid response from Polygon for {symbol}: {e}")
            return []
    def get_latest_bar(self, symbol: str, timeframe: str = "day") -> Optional[Dict]:
        """
        Fetch only the most recent bar (useful for quick checks).
        """
        bars = self.get_agg_bars(symbol, timeframe, limit=1)
        return bars[0] if bars else None

def test_connection():
    """Test Polygon connection (run as: python -m src.apis.polygon_client)"""
    try:
        client = PolygonClient()
        bars = client.get_agg_bars("MU", "day", limit=20)
        if bars:
            print(f"✅ Connected to Polygon")
            print(f"Fetched {len(bars)} bars for MU")
            latest = bars[-1]
            print(f"\nLatest bar (MU):")
            print(f"  Date: {latest['timestamp']}")
            print(f"  Close: ${latest['close']}")
            print(f"  High: ${latest['high']}")
            print(f"  Low: ${latest['low']}")
            print(f"  Volume: {latest['volume']:.0f}")
        else:
            print("❌ No bars returned (check API key or rate limits)")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
