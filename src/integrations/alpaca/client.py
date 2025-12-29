"""
Alpaca API client.
Handles authentication and API calls to Alpaca.
"""

import logging
from datetime import date
from typing import List, Optional, Dict, Any
import requests

from src.config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL
from .responses import AlpacaPosition, AlpacaAccount

logger = logging.getLogger(__name__)


class AlpacaClient:
    """Client for Alpaca Trading API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize Alpaca client."""
        self.api_key = api_key or ALPACA_API_KEY
        self.secret_key = secret_key or ALPACA_SECRET_KEY
        self.base_url = (base_url or ALPACA_BASE_URL).rstrip('/')
        
        self._session = requests.Session()
        self._session.headers.update({
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret_key,
            "Content-Type": "application/json",
        })
        
        self._last_error: Optional[str] = None
    
    @property
    def is_configured(self) -> bool:
        """Check if API keys are configured."""
        return bool(self.api_key and self.secret_key)
    
    @property
    def last_error(self) -> Optional[str]:
        """Get last error message."""
        return self._last_error
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make API request with error handling."""
        url = f"{self.base_url}{endpoint}"
        self._last_error = None
        
        try:
            response = self._session.request(method, url, timeout=10, **kwargs)
            
            if response.status_code == 401:
                self._last_error = "Authentication failed - check API keys"
                logger.error(self._last_error)
                return None
            
            if response.status_code == 429:
                self._last_error = "Rate limited - too many requests"
                logger.warning(self._last_error)
                return None
            
            if response.status_code >= 400:
                self._last_error = f"API error: {response.status_code} - {response.text}"
                logger.error(self._last_error)
                return None
            
            return response.json()
            
        except requests.exceptions.Timeout:
            self._last_error = "Request timed out"
            logger.error(self._last_error)
            return None
        except requests.exceptions.ConnectionError:
            self._last_error = "Connection error - check network"
            logger.error(self._last_error)
            return None
        except Exception as e:
            self._last_error = f"Unexpected error: {str(e)}"
            logger.error(self._last_error)
            return None
    
    def get_account(self) -> Optional[AlpacaAccount]:
        """Get account information."""
        data = self._request("GET", "/v2/account")
        if not data:
            return None
        
        try:
            return AlpacaAccount(
                account_id=data.get("id", ""),
                cash=float(data.get("cash", 0)),
                portfolio_value=float(data.get("portfolio_value", 0)),
                buying_power=float(data.get("buying_power", 0)),
                equity=float(data.get("equity", 0)),
                status=data.get("status", "unknown"),
            )
        except Exception as e:
            logger.error(f"Error parsing account data: {e}")
            return None
    
    def get_positions(self) -> List[AlpacaPosition]:
        """Get all open positions."""
        data = self._request("GET", "/v2/positions")
        if not data:
            return []
        
        positions = []
        for item in data:
            try:
                pos = AlpacaPosition(
                    ticker=item.get("symbol", ""),
                    shares=float(item.get("qty", 0)),
                    avg_entry_price=float(item.get("avg_entry_price", 0)),
                    current_price=float(item.get("current_price", 0)),
                    market_value=float(item.get("market_value", 0)),
                    unrealized_pl=float(item.get("unrealized_pl", 0)),
                    unrealized_plpc=float(item.get("unrealized_plpc", 0)),
                    side=item.get("side", "long"),
                )
                positions.append(pos)
            except Exception as e:
                ticker = item.get("symbol", "unknown")
                logger.error(f"Error parsing position {ticker}: {e}")
        
        return positions
    
    def get_position(self, ticker: str) -> Optional[AlpacaPosition]:
        """Get a specific position by ticker."""
        data = self._request("GET", f"/v2/positions/{ticker.upper()}")
        if not data:
            return None
        
        try:
            return AlpacaPosition(
                ticker=data.get("symbol", ""),
                shares=float(data.get("qty", 0)),
                avg_entry_price=float(data.get("avg_entry_price", 0)),
                current_price=float(data.get("current_price", 0)),
                market_value=float(data.get("market_value", 0)),
                unrealized_pl=float(data.get("unrealized_pl", 0)),
                unrealized_plpc=float(data.get("unrealized_plpc", 0)),
                side=data.get("side", "long"),
            )
        except Exception as e:
            logger.error(f"Error parsing position {ticker}: {e}")
            return None
    
    def test_connection(self) -> Dict[str, Any]:
        """Test API connection and return status."""
        if not self.is_configured:
            return {
                "connected": False,
                "error": "API keys not configured",
            }
        
        account = self.get_account()
        if account:
            return {
                "connected": True,
                "account_id": account.account_id,
                "status": account.status,
                "portfolio_value": account.portfolio_value,
            }
        else:
            return {
                "connected": False,
                "error": self._last_error or "Unknown error",
            }
