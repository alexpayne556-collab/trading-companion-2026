"""
Risk Rule Engine.
Evaluates portfolio against risk rules and generates alerts.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass, field

from src.config import CONCENTRATION_THRESHOLD, OVERNIGHT_MOVE_THRESHOLD
from src.portfolio.models import PortfolioSnapshot, Position
from src.thesis.models import Thesis

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """A risk alert."""
    severity: AlertSeverity
    rule: str
    ticker: Optional[str]
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        ticker_str = f"[{self.ticker}] " if self.ticker else ""
        return f"{ticker_str}{self.message}"


class RiskRuleEngine:
    """Evaluates portfolio against risk rules."""
    
    def __init__(
        self,
        concentration_threshold: float = None,
        overnight_threshold: float = None,
    ):
        """Initialize risk engine."""
        self.concentration_threshold = concentration_threshold or CONCENTRATION_THRESHOLD
        self.overnight_threshold = overnight_threshold or OVERNIGHT_MOVE_THRESHOLD
    
    def evaluate(
        self,
        snapshot: PortfolioSnapshot,
        theses: dict = None,
        previous_prices: dict = None,
    ) -> List[Alert]:
        """
        Evaluate all risk rules against portfolio.
        
        Args:
            snapshot: Current portfolio snapshot
            theses: Dict of ticker -> Thesis for thesis alignment checks
            previous_prices: Dict of ticker -> previous close for overnight moves
        
        Returns:
            List of Alert objects
        """
        alerts = []
        theses = theses or {}
        previous_prices = previous_prices or {}
        
        # Rule 1: Concentration risk
        alerts.extend(self._check_concentration(snapshot))
        
        # Rule 2: Overnight moves
        alerts.extend(self._check_overnight_moves(snapshot, previous_prices))
        
        # Rule 3: Thesis alignment
        alerts.extend(self._check_thesis_alignment(snapshot, theses))
        
        # Rule 4: Missing thesis
        alerts.extend(self._check_missing_thesis(snapshot, theses))
        
        # Sort by severity (critical first)
        severity_order = {AlertSeverity.CRITICAL: 0, AlertSeverity.WARNING: 1, AlertSeverity.INFO: 2}
        alerts.sort(key=lambda a: severity_order.get(a.severity, 99))
        
        return alerts
    
    def _check_concentration(self, snapshot: PortfolioSnapshot) -> List[Alert]:
        """Check for position concentration risk."""
        alerts = []
        
        for pos in snapshot.positions:
            allocation = snapshot.get_allocation(pos.ticker) / 100  # Convert to decimal
            
            if allocation > self.concentration_threshold:
                pct = allocation * 100
                threshold_pct = self.concentration_threshold * 100
                alerts.append(Alert(
                    severity=AlertSeverity.WARNING,
                    rule="concentration",
                    ticker=pos.ticker,
                    message=f"Position is {pct:.1f}% of portfolio (threshold: {threshold_pct:.0f}%)",
                ))
        
        return alerts
    
    def _check_overnight_moves(
        self,
        snapshot: PortfolioSnapshot,
        previous_prices: dict,
    ) -> List[Alert]:
        """Check for significant overnight price moves."""
        alerts = []
        
        for pos in snapshot.positions:
            prev_price = previous_prices.get(pos.ticker)
            if not prev_price or prev_price <= 0:
                continue
            
            move = (pos.current_price - prev_price) / prev_price
            
            if abs(move) > self.overnight_threshold:
                direction = "up" if move > 0 else "down"
                alerts.append(Alert(
                    severity=AlertSeverity.CRITICAL if abs(move) > 0.10 else AlertSeverity.WARNING,
                    rule="overnight_move",
                    ticker=pos.ticker,
                    message=f"Moved {move*100:+.1f}% {direction} overnight",
                ))
        
        return alerts
    
    def _check_thesis_alignment(
        self,
        snapshot: PortfolioSnapshot,
        theses: dict,
    ) -> List[Alert]:
        """Check if positions align with thesis targets."""
        alerts = []
        
        for pos in snapshot.positions:
            thesis = theses.get(pos.ticker.upper())
            if not thesis:
                continue
            
            # Check if price exceeded target
            if thesis.target_price and pos.current_price > thesis.target_price:
                alerts.append(Alert(
                    severity=AlertSeverity.INFO,
                    rule="thesis_alignment",
                    ticker=pos.ticker,
                    message=f"Price ${pos.current_price:.2f} exceeded target ${thesis.target_price:.2f}",
                ))
            
            # Check conviction vs allocation mismatch
            target_weight = thesis.portfolio_weight
            actual_weight = snapshot.get_allocation(pos.ticker) / 100
            
            if target_weight > 0 and actual_weight > target_weight * 1.5:
                alerts.append(Alert(
                    severity=AlertSeverity.WARNING,
                    rule="thesis_alignment",
                    ticker=pos.ticker,
                    message=f"Allocation {actual_weight*100:.1f}% exceeds thesis target {target_weight*100:.1f}%",
                ))
        
        return alerts
    
    def _check_missing_thesis(
        self,
        snapshot: PortfolioSnapshot,
        theses: dict,
    ) -> List[Alert]:
        """Check for positions without defined thesis."""
        alerts = []
        
        for pos in snapshot.positions:
            if pos.ticker.upper() not in theses:
                alerts.append(Alert(
                    severity=AlertSeverity.INFO,
                    rule="missing_thesis",
                    ticker=pos.ticker,
                    message="No thesis defined - consider documenting your reasoning",
                ))
        
        return alerts
    
    def get_alerts_by_severity(
        self,
        alerts: List[Alert],
        severity: AlertSeverity,
    ) -> List[Alert]:
        """Filter alerts by severity level."""
        return [a for a in alerts if a.severity == severity]
    
    def alerts_to_dict(self, alerts: List[Alert]) -> dict:
        """Convert alerts to dictionary format for dashboard."""
        return {
            "critical": [str(a) for a in alerts if a.severity == AlertSeverity.CRITICAL],
            "warning": [str(a) for a in alerts if a.severity == AlertSeverity.WARNING],
            "info": [str(a) for a in alerts if a.severity == AlertSeverity.INFO],
            "total": len(alerts),
        }
