"""
Alpaca API response models.
Clean data structures for Alpaca API responses.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AlpacaAccount:
    """Alpaca account information."""
    account_id: str
    cash: float
    portfolio_value: float
    buying_power: float
    equity: float
    status: str


@dataclass
class AlpacaPosition:
    """A position returned from Alpaca API."""
    ticker: str
    shares: float
    avg_entry_price: float
    current_price: float
    market_value: float
    unrealized_pl: float
    unrealized_plpc: float  # percentage
    side: str = "long"
    
    @property
    def is_long(self) -> bool:
        return self.side == "long"
    
    @property
    def cost_basis(self) -> float:
        return self.shares * self.avg_entry_price


@dataclass
class AlpacaOrder:
    """An order from Alpaca API."""
    order_id: str
    ticker: str
    side: str  # buy, sell
    order_type: str  # market, limit, stop, stop_limit
    qty: float
    filled_qty: float
    status: str
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    filled_avg_price: Optional[float] = None
