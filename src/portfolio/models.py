"""
Portfolio data models.
Pydantic models for positions and portfolio snapshots.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, computed_field


class Position(BaseModel):
    """A single position in the portfolio."""
    
    ticker: str = Field(..., description="Stock ticker symbol")
    shares: float = Field(..., ge=0, description="Number of shares held")
    entry_price: float = Field(..., gt=0, description="Average entry price")
    current_price: float = Field(..., gt=0, description="Current market price")
    entry_date: Optional[date] = Field(None, description="Date position was opened")
    
    # Thesis linkage
    thesis_id: Optional[str] = Field(None, description="Linked thesis ID")
    conviction: int = Field(5, ge=1, le=10, description="Conviction score 1-10")
    
    @computed_field
    @property
    def current_value(self) -> float:
        """Current market value of position."""
        return self.shares * self.current_price
    
    @computed_field
    @property
    def cost_basis(self) -> float:
        """Total cost basis of position."""
        return self.shares * self.entry_price
    
    @computed_field
    @property
    def unrealized_pnl(self) -> float:
        """Unrealized profit/loss in dollars."""
        return self.current_value - self.cost_basis
    
    @computed_field
    @property
    def unrealized_pnl_pct(self) -> float:
        """Unrealized profit/loss as percentage."""
        if self.cost_basis == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_basis) * 100
    
    @computed_field
    @property
    def days_held(self) -> Optional[int]:
        """Days since position was opened."""
        if not self.entry_date:
            return None
        return (date.today() - self.entry_date).days


class PortfolioSnapshot(BaseModel):
    """Point-in-time snapshot of entire portfolio."""
    
    timestamp: datetime = Field(default_factory=datetime.now)
    positions: List[Position] = Field(default_factory=list)
    cash_balance: float = Field(0.0, ge=0)
    
    @computed_field
    @property
    def total_value(self) -> float:
        """Total portfolio value (positions + cash)."""
        positions_value = sum(p.current_value for p in self.positions)
        return positions_value + self.cash_balance
    
    @computed_field
    @property
    def total_cost(self) -> float:
        """Total cost basis of all positions."""
        return sum(p.cost_basis for p in self.positions)
    
    @computed_field
    @property
    def unrealized_pnl(self) -> float:
        """Total unrealized P&L."""
        return sum(p.unrealized_pnl for p in self.positions)
    
    @computed_field
    @property
    def unrealized_pnl_pct(self) -> float:
        """Total unrealized P&L as percentage."""
        if self.total_cost == 0:
            return 0.0
        return (self.unrealized_pnl / self.total_cost) * 100
    
    @computed_field
    @property
    def position_count(self) -> int:
        """Number of open positions."""
        return len(self.positions)
    
    def get_position(self, ticker: str) -> Optional[Position]:
        """Get position by ticker."""
        for pos in self.positions:
            if pos.ticker.upper() == ticker.upper():
                return pos
        return None
    
    def get_allocation(self, ticker: str) -> float:
        """Get position allocation as percentage of total value."""
        pos = self.get_position(ticker)
        if not pos or self.total_value == 0:
            return 0.0
        return (pos.current_value / self.total_value) * 100
    
    def to_display_dict(self) -> dict:
        """Convert to dictionary format for dashboard display."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "portfolio": {
                "total_value": self.total_value,
                "total_cost": self.total_cost,
                "unrealized_pnl": self.unrealized_pnl,
                "unrealized_pnl_pct": self.unrealized_pnl_pct,
                "cash_balance": self.cash_balance,
                "position_count": self.position_count,
            },
            "positions": [
                {
                    "ticker": p.ticker,
                    "shares": p.shares,
                    "entry_price": p.entry_price,
                    "current_price": p.current_price,
                    "current_value": p.current_value,
                    "unrealized_pnl": p.unrealized_pnl,
                    "unrealized_pnl_pct": p.unrealized_pnl_pct,
                    "allocation_pct": self.get_allocation(p.ticker),
                    "conviction": p.conviction,
                    "days_held": p.days_held,
                }
                for p in self.positions
            ]
        }
