"""
Portfolio Manager.
Orchestrates data from Alpaca, theses, and risk rules.
"""

import logging
from datetime import datetime, date
from typing import Optional, Dict, List

from src.portfolio.models import Position, PortfolioSnapshot
from src.integrations.alpaca import AlpacaClient
from src.thesis import ThesisLoader, Thesis
from src.risk import RiskRuleEngine, Alert

logger = logging.getLogger(__name__)


class PortfolioManager:
    """
    Central orchestrator for portfolio data.
    Combines Alpaca positions with theses and risk rules.
    """
    
    def __init__(
        self,
        alpaca_client: Optional[AlpacaClient] = None,
        thesis_loader: Optional[ThesisLoader] = None,
        risk_engine: Optional[RiskRuleEngine] = None,
    ):
        """Initialize portfolio manager with dependencies."""
        self.alpaca = alpaca_client or AlpacaClient()
        self.thesis_loader = thesis_loader or ThesisLoader()
        self.risk_engine = risk_engine or RiskRuleEngine()
        
        self._snapshot: Optional[PortfolioSnapshot] = None
        self._theses: Dict[str, Thesis] = {}
        self._alerts: List[Alert] = []
        self._last_refresh: Optional[datetime] = None
        self._previous_prices: Dict[str, float] = {}
    
    @property
    def is_ready(self) -> bool:
        """Check if manager is ready (Alpaca configured)."""
        return self.alpaca.is_configured
    
    @property
    def snapshot(self) -> Optional[PortfolioSnapshot]:
        """Get current portfolio snapshot."""
        return self._snapshot
    
    @property
    def alerts(self) -> List[Alert]:
        """Get current alerts."""
        return self._alerts
    
    @property
    def last_refresh(self) -> Optional[datetime]:
        """Get timestamp of last refresh."""
        return self._last_refresh
    
    def refresh(self) -> bool:
        """
        Refresh portfolio data from Alpaca.
        Returns True if successful.
        """
        logger.info("Refreshing portfolio data...")
        
        # Store previous prices for overnight move detection
        if self._snapshot:
            for pos in self._snapshot.positions:
                self._previous_prices[pos.ticker] = pos.current_price
        
        # Get account info
        account = self.alpaca.get_account()
        if not account:
            logger.error(f"Failed to get account: {self.alpaca.last_error}")
            return False
        
        # Get positions
        alpaca_positions = self.alpaca.get_positions()
        
        # Load theses
        self._theses = self.thesis_loader.load_all()
        
        # Convert Alpaca positions to our Position model
        positions = []
        for ap in alpaca_positions:
            thesis = self._theses.get(ap.ticker.upper())
            
            pos = Position(
                ticker=ap.ticker,
                shares=ap.shares,
                entry_price=ap.avg_entry_price,
                current_price=ap.current_price,
                thesis_id=ap.ticker.upper() if thesis else None,
                conviction=thesis.confidence_score if thesis else 5,
            )
            positions.append(pos)
        
        # Build snapshot
        self._snapshot = PortfolioSnapshot(
            timestamp=datetime.now(),
            positions=positions,
            cash_balance=account.cash,
        )
        
        # Evaluate risk rules
        self._alerts = self.risk_engine.evaluate(
            self._snapshot,
            theses=self._theses,
            previous_prices=self._previous_prices,
        )
        
        self._last_refresh = datetime.now()
        logger.info(f"Refresh complete: {len(positions)} positions, {len(self._alerts)} alerts")
        
        return True
    
    def get_snapshot_dict(self) -> dict:
        """Get snapshot as dictionary for dashboard."""
        if not self._snapshot:
            return {
                "portfolio": {},
                "positions": [],
                "alerts": {"critical": [], "warning": [], "info": [], "total": 0},
                "last_refresh": None,
            }
        
        display = self._snapshot.to_display_dict()
        display["alerts"] = self.risk_engine.alerts_to_dict(self._alerts)
        display["last_refresh"] = self._last_refresh.isoformat() if self._last_refresh else None
        
        return display
    
    def get_thesis(self, ticker: str) -> Optional[Thesis]:
        """Get thesis for a ticker."""
        return self._theses.get(ticker.upper())
    
    def get_position(self, ticker: str) -> Optional[Position]:
        """Get position for a ticker."""
        if not self._snapshot:
            return None
        return self._snapshot.get_position(ticker)
    
    def get_critical_alerts(self) -> List[Alert]:
        """Get critical alerts only."""
        return self.risk_engine.get_alerts_by_severity(
            self._alerts, 
            self.risk_engine.__class__.__bases__[0]  # This is a hack, fix below
        )
    
    def test_connection(self) -> dict:
        """Test Alpaca connection."""
        return self.alpaca.test_connection()
