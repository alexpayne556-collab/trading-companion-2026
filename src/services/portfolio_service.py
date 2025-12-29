"""
Portfolio Service.
High-level API for portfolio operations.
Used by CLI dashboard and future web dashboard.
"""

import logging
from typing import Optional

from src.portfolio import PortfolioManager, PortfolioSnapshot
from src.thesis import Thesis

logger = logging.getLogger(__name__)


class PortfolioService:
    """
    High-level service for portfolio operations.
    Wraps PortfolioManager for easy use by dashboards.
    """
    
    def __init__(self, manager: Optional[PortfolioManager] = None):
        """Initialize service."""
        self._manager = manager or PortfolioManager()
    
    @property
    def is_ready(self) -> bool:
        """Check if service is ready."""
        return self._manager.is_ready
    
    def refresh(self) -> bool:
        """Refresh portfolio data."""
        return self._manager.refresh()
    
    def get_snapshot(self) -> dict:
        """
        Get portfolio snapshot as dictionary.
        This is the main method used by dashboards.
        """
        return self._manager.get_snapshot_dict()
    
    def get_position(self, ticker: str) -> Optional[dict]:
        """Get single position details."""
        pos = self._manager.get_position(ticker)
        if not pos:
            return None
        
        snapshot = self._manager.snapshot
        thesis = self._manager.get_thesis(ticker)
        
        return {
            "ticker": pos.ticker,
            "shares": pos.shares,
            "entry_price": pos.entry_price,
            "current_price": pos.current_price,
            "current_value": pos.current_value,
            "cost_basis": pos.cost_basis,
            "unrealized_pnl": pos.unrealized_pnl,
            "unrealized_pnl_pct": pos.unrealized_pnl_pct,
            "days_held": pos.days_held,
            "conviction": pos.conviction,
            "allocation_pct": snapshot.get_allocation(ticker) if snapshot else 0,
            "thesis": thesis.thesis if thesis else None,
            "target_price": thesis.target_price if thesis else None,
        }
    
    def get_thesis(self, ticker: str) -> Optional[dict]:
        """Get thesis for a ticker."""
        thesis = self._manager.get_thesis(ticker)
        if not thesis:
            return None
        
        return {
            "ticker": thesis.ticker,
            "name": thesis.name,
            "thesis": thesis.thesis,
            "conviction": thesis.conviction,
            "confidence_score": thesis.confidence_score,
            "target_price": thesis.target_price,
            "timeframe_months": thesis.timeframe_months,
            "catalysts": [
                {
                    "event": c.event,
                    "probability": c.probability,
                    "days_until": c.days_until,
                }
                for c in thesis.active_catalysts
            ],
            "invalidation": thesis.invalidation,
        }
    
    def test_connection(self) -> dict:
        """Test API connection."""
        return self._manager.test_connection()
    
    def get_status(self) -> dict:
        """Get overall service status."""
        conn = self.test_connection()
        snapshot = self._manager.snapshot
        
        return {
            "alpaca_connected": conn.get("connected", False),
            "alpaca_error": conn.get("error"),
            "has_snapshot": snapshot is not None,
            "position_count": snapshot.position_count if snapshot else 0,
            "last_refresh": self._manager.last_refresh.isoformat() if self._manager.last_refresh else None,
            "alert_count": len(self._manager.alerts),
        }
