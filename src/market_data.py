"""Market data structures for thesis validation."""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class ThesisDirection(Enum):
    LONG = "long"
    SHORT = "short"

class VolatilityRegime(Enum):
    LOW = "low"
    NORMAL = "normal"
    ELEVATED = "elevated"
    HIGH = "high"

class TrendDirection(Enum):
    DOWN = "down"
    SIDEWAYS = "sideways"
    UP = "up"

@dataclass
class Position:
    ticker: str
    entry_price: float
    current_price: float
    entry_date: str
    shares: float = 1.0
    def price_change_pct(self) -> float:
        if self.entry_price == 0:
            return 0.0
        return (self.current_price - self.entry_price) / self.entry_price
    def dollars_per_percent(self) -> float:
        return (self.entry_price * self.shares) / 100

@dataclass
class Thesis:
    target_price: float
    timeframe_months: float
    confidence_score: float
    invalidation_price: Optional[float] = None
    direction: ThesisDirection = ThesisDirection.LONG
    def is_target_hit(self, current_price: float) -> bool:
        if self.direction == ThesisDirection.LONG:
            return current_price >= self.target_price
        else:
            return current_price <= self.target_price
    def is_invalidated(self, current_price: float) -> bool:
        if self.invalidation_price is None:
            return False
        if self.direction == ThesisDirection.LONG:
            return current_price <= self.invalidation_price
        else:
            return current_price >= self.invalidation_price

@dataclass
class VolatilityMetrics:
    volatility_20day: float
    volatility_60day: float
    volatility_252day: float
    iv_20day: Optional[float] = None
    iv_60day: Optional[float] = None
    beta_60day: float = 1.0
    vol_of_vol: float = 0.2
    garch_persistence: float = 0.95
    def volatility_ratio(self) -> float:
        if self.volatility_252day == 0:
            return 1.0
        return self.volatility_20day / self.volatility_252day

@dataclass
class SectorMetrics:
    sector_return_1d: float
    sector_return_5d: float
    sector_return_20d: float
    relative_strength_vs_sector_5d: float
    relative_strength_vs_sector_20d: float
    relative_strength_vs_market_5d: float
    sector_trend: TrendDirection
    stock_vs_sector_trend: str
    correlation_to_sector_60day: float
    sector_volatility_20day: float

@dataclass
class MarketBreadth:
    vix_level: float
    volatility_regime: VolatilityRegime
    sp500_5day_return: float
    sp500_20day_return: float
    sp500_trend: TrendDirection
    breadth_above_20ma: float

@dataclass
class MarketData:
    timestamp: str
    stock_symbol: str
    volatility: VolatilityMetrics
    sector: SectorMetrics
    market: MarketBreadth
    earnings_days_until: Optional[int] = None

@dataclass
class ValidationResult:
    alignment_score: float
    conviction_accuracy: int
    catalyst_progress: int
    invalidation_risk: int
    flags: List[str] = field(default_factory=list)
