"""
Thesis data models.
Investment thesis and catalyst tracking.
"""

from datetime import date
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class Catalyst(BaseModel):
    """An event that could validate or invalidate a thesis."""
    
    event: str = Field(..., description="Description of the catalyst event")
    event_date: Optional[date] = Field(None, description="Expected date of catalyst")
    probability: float = Field(0.5, ge=0, le=1, description="Probability of occurring")
    timeline: str = Field("unknown", description="Timeline description (immediate, 30-60 days, etc.)")
    impact: str = Field("", description="Expected impact on thesis")
    triggered: bool = Field(False, description="Has this catalyst occurred?")
    
    @property
    def days_until(self) -> Optional[int]:
        """Days until catalyst event."""
        if not self.event_date:
            return None
        return (self.event_date - date.today()).days


class Thesis(BaseModel):
    """Investment thesis for a position."""
    
    # Identity
    ticker: str = Field(..., description="Stock ticker symbol")
    name: str = Field("", description="Company name")
    sector: str = Field("", description="Sector classification")
    
    # Core thesis
    thesis: str = Field(..., description="Core thesis in 1 sentence")
    reasoning: str = Field("", description="Detailed reasoning")
    
    # Catalysts
    catalysts: List[Catalyst] = Field(default_factory=list)
    invalidation: List[str] = Field(default_factory=list, description="What would break this thesis")
    
    # Targets
    target_price: Optional[float] = Field(None, gt=0)
    timeframe_months: int = Field(12, ge=1, le=60)
    
    # Conviction
    conviction: Literal["LOW", "MEDIUM", "HIGH"] = Field("MEDIUM")
    confidence_score: int = Field(5, ge=1, le=10)
    
    # Portfolio context
    portfolio_weight: float = Field(0.0, ge=0, le=1, description="Target allocation (0-1)")
    entry_price: Optional[float] = Field(None, gt=0)
    entry_date: Optional[date] = Field(None)
    
    # Related
    related_tickers: List[str] = Field(default_factory=list)
    red_team_notes: str = Field("", description="Devil's advocate notes")
    
    @property
    def conviction_score(self) -> int:
        """Convert conviction to numeric score."""
        mapping = {"LOW": 3, "MEDIUM": 6, "HIGH": 9}
        return mapping.get(self.conviction, 5)
    
    @property
    def active_catalysts(self) -> List[Catalyst]:
        """Get catalysts that haven't triggered yet."""
        return [c for c in self.catalysts if not c.triggered]
    
    @property
    def upcoming_catalysts(self) -> List[Catalyst]:
        """Get catalysts with dates in the future, sorted by date."""
        upcoming = [c for c in self.active_catalysts if c.event_date and c.days_until and c.days_until > 0]
        return sorted(upcoming, key=lambda c: c.event_date)
    
    @property
    def next_catalyst(self) -> Optional[Catalyst]:
        """Get the next upcoming catalyst."""
        upcoming = self.upcoming_catalysts
        return upcoming[0] if upcoming else None
    
    def upside_pct(self, current_price: float) -> Optional[float]:
        """Calculate upside percentage to target."""
        if not self.target_price or current_price <= 0:
            return None
        return ((self.target_price - current_price) / current_price) * 100
    
    def is_valid(self) -> bool:
        """Basic validation check."""
        return bool(self.ticker and self.thesis)
    
    def to_summary(self) -> str:
        """One-line summary for display."""
        catalyst_info = ""
        if self.next_catalyst:
            catalyst_info = f" | Next: {self.next_catalyst.event[:30]}..."
        return f"{self.ticker} ({self.conviction}): {self.thesis[:50]}...{catalyst_info}"
