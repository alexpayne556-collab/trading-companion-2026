"""
Thesis Validator Module for Trading Companion 2026
Implements thesis alignment scoring, conviction, catalyst progress, invalidation risk, and flag generation.
Production-ready, with all critical fixes and deep seek improvements applied.
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class ThesisDirection(Enum):
    LONG = "long"
    SHORT = "short"

@dataclass
class Position:
    ticker: str
    entry_price: float
    current_price: float
    entry_date: str  # ISO format: "2025-01-15"

@dataclass
class Thesis:
    target_price: float
    timeframe_months: float
    confidence_score: float  # 0-1
    invalidation_price: Optional[float] = None
    direction: ThesisDirection = ThesisDirection.LONG

@dataclass
class MarketData:
    sector_performance: Optional[float] = None  # % change
    volatility_percentile: Optional[float] = None  # 0-100

@dataclass
class ValidationResult:
    alignment_score: float      # 0-10 composite
    conviction_accuracy: int    # 0-100
    catalyst_progress: int      # 0-100
    invalidation_risk: int      # 0-100 (higher = more risk)
    flags: List[str]            # warnings/notes

class ThesisValidator:
    def __init__(self, today: Optional[str] = None):
        """Initialize with optional date override for testing."""
        self.today = (
            datetime.fromisoformat(today).date() if today else date.today()
        )

    def validate(
        self,
        position: Position,
        thesis: Thesis,
        market_data: MarketData
    ) -> ValidationResult:
        """Main entry point - returns complete validation."""
        conviction = self._calc_conviction_accuracy(position, thesis, market_data)
        progress = self._calc_catalyst_progress(position, thesis)
        risk = self._calc_invalidation_risk(position, thesis, market_data)
        alignment = self._composite_score(conviction, progress, risk, thesis.confidence_score)
        flags = self._generate_flags(position, thesis, conviction, progress, risk)
        return ValidationResult(
            alignment_score=round(alignment, 1),
            conviction_accuracy=conviction,
            catalyst_progress=progress,
            invalidation_risk=risk,
            flags=flags
        )

    def _calc_conviction_accuracy(self, position: Position, thesis: Thesis, market_data: MarketData) -> int:
        """
        How well is price tracking toward target? (0-100)
        Handles both LONG and SHORT directions, clamps output, and uses sector performance.
        """
        entry = position.entry_price
        current = position.current_price
        target = thesis.target_price
        direction = thesis.direction

        if direction == ThesisDirection.LONG:
            expected_move = max(target - entry, 0.001)
            actual_move = current - entry
        else:
            expected_move = max(entry - target, 0.001)
            actual_move = entry - current

        if expected_move < 0.001:
            return 50

        progress_ratio = min(abs(actual_move / expected_move), 2.0)

        # Direction check
        if actual_move * expected_move < 0:
            wrong_magnitude = min(abs(actual_move / expected_move), 1.0)
            score = 50 - (wrong_magnitude * 50)
        else:
            score = 50 + (progress_ratio / 2.0) * 50

        # Sector performance adjustment
        if market_data.sector_performance is not None:
            score += market_data.sector_performance * 0.5  # modest boost
        score = max(0, min(100, score))
        return int(score)

    def _calc_catalyst_progress(self, position: Position, thesis: Thesis) -> int:
        """
        Price progress vs time elapsed ratio. (0-100)
        Handles both LONG and SHORT directions, clamps output.
        """
        entry_date = datetime.fromisoformat(position.entry_date).date()
        days_elapsed = (self.today - entry_date).days
        total_days = thesis.timeframe_months * 30
        time_pct = max(days_elapsed / total_days, 0.01)

        direction = thesis.direction
        entry = position.entry_price
        current = position.current_price
        target = thesis.target_price

        if direction == ThesisDirection.LONG:
            expected_move = max(target - entry, 0.001)
            actual_move = current - entry
        else:
            expected_move = max(entry - target, 0.001)
            actual_move = entry - current

        if abs(expected_move) < 0.001:
            return 50

        price_pct = actual_move / expected_move
        trajectory = price_pct / time_pct

        if trajectory <= 0:
            score = 0
        elif trajectory >= 3.0:
            score = 100
        else:
            score = trajectory * 33.3 + 16.7
        score = max(0, min(100, score))
        return int(score)

    def _calc_invalidation_risk(self, position: Position, thesis: Thesis, market_data: MarketData) -> int:
        """
        Proximity to thesis-killing conditions. (0-100)
        Handles explicit invalidation price, implied risk, overtime, and volatility.
        """
        entry = position.entry_price
        current = position.current_price
        target = thesis.target_price
        direction = thesis.direction
        risk = 0

        if thesis.invalidation_price is not None:
            inv = thesis.invalidation_price
            original_buffer = abs(entry - inv)
            if original_buffer < 0.001:
                risk = 100
            else:
                current_buffer = abs(current - inv)
                risk_pct = 1 - (current_buffer / original_buffer)
                risk = max(0, min(100, risk_pct * 100))
                if (direction == ThesisDirection.LONG and current <= inv) or (direction == ThesisDirection.SHORT and current >= inv):
                    risk = 100
        else:
            expected_move = max(abs(target - entry), 0.001)
            wrong_move = (entry - current) if direction == ThesisDirection.LONG else (current - entry)
            if wrong_move <= 0:
                base_risk = 10
            else:
                risk_threshold = expected_move * 0.5
                base_risk = min(90, (wrong_move / risk_threshold) * 80 + 10)
            risk = base_risk

        entry_date = datetime.fromisoformat(position.entry_date).date()
        days_elapsed = (self.today - entry_date).days
        deadline_days = thesis.timeframe_months * 30
        if days_elapsed > deadline_days:
            overtime_pct = (days_elapsed - deadline_days) / deadline_days
            time_risk = min(20, overtime_pct * 40)
            risk = min(100, risk + time_risk)

        # Volatility adjustment
        if market_data.volatility_percentile is not None:
            if market_data.volatility_percentile > 75:
                risk = max(0, risk - 10)
            elif market_data.volatility_percentile < 25:
                risk = min(100, risk + 5)
        risk = max(0, min(100, risk))
        return int(risk)

    def _composite_score(self, conviction: int, progress: int, risk: int, confidence: float) -> float:
        """
        Weighted combination → 0-10 scale.
        """
        inverse_risk = 100 - risk
        raw = conviction * 0.40 + progress * 0.35 + inverse_risk * 0.25
        scaled = raw / 10
        confidence_factor = 0.8 + (confidence * 0.4)
        return max(0, min(10, scaled * confidence_factor))

    def _generate_flags(self, position: Position, thesis: Thesis, conviction: int, progress: int, risk: int) -> List[str]:
        """
        Generates human-readable warnings and notes based on scores and status.
        """
        flags = []
        if conviction < 30:
            flags.append("CONVICTION_DEGRADED")
        if progress < 25:
            flags.append("BEHIND_SCHEDULE")
        if risk > 70:
            flags.append("HIGH_INVALIDATION_RISK")
        if risk >= 100:
            flags.append("INVALIDATION_TRIGGERED")
        entry_date = datetime.fromisoformat(position.entry_date).date()
        deadline = entry_date + relativedelta(months=thesis.timeframe_months)
        if self.today > deadline:
            flags.append("OVERTIME")
        if thesis.direction == ThesisDirection.LONG:
            if position.current_price >= thesis.target_price:
                flags.append("TARGET_REACHED")
            elif abs(position.current_price - thesis.target_price) / max(thesis.target_price, 0.01) < 0.05:
                flags.append("NEAR_TARGET")
        else:
            if position.current_price <= thesis.target_price:
                flags.append("TARGET_REACHED")
            elif abs(position.current_price - thesis.target_price) / max(thesis.target_price, 0.01) < 0.05:
                flags.append("NEAR_TARGET")
        return flags


import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ThesisValidator:
    """
    Validates a position against its thesis definition.
    Scores alignment and flags thesis breaks.
    """
    
    # Thresholds for thesis invalidation
    DEEP_LOSS_THRESHOLD = -0.30  # -30% from entry = thesis may be broken
    MODERATE_LOSS_THRESHOLD = -0.15  # -15% = caution flag
    
    def __init__(self, position: Dict, thesis: Dict):
        """
        Initialize validator with a position and its thesis.
        """
        self.position = position
        self.thesis = thesis
        self.ticker = position.get("symbol")
        
        # Validate inputs
        if not self.ticker:
            raise ValueError("Position missing 'symbol' field")
        if not thesis or self.thesis.get("ticker") != self.ticker:
            raise ValueError(f"Thesis mismatch for {self.ticker}")
    
    def calculate_days_held(self) -> int:
        """
        Calculate how many days position has been held.
        PLACEHOLDER: In real implementation, would use position.entered_at timestamp.
        For now, assume all positions are very recent (1 day).
        """
        # TODO: Get actual entry timestamp from Alpaca position object
        return 1
    
    def calculate_price_progress(self) -> float:
        """
        Calculate progress from entry price toward target price.
        """
        target_price = self.thesis.get("target_price")
        
        # If no target defined, use unrealized P&L % as proxy
        if not target_price or target_price <= 0:
            return max(0.0, self.position.get("unrealized_plpc", 0.0))
        
        entry_price = self.position.get("avg_fill_price", 0.0)
        current_price = self.position.get("current_price", 0.0)
        
        if entry_price <= 0:
            return 0.0
        
        # Avoid division by zero
        if target_price == entry_price:
            return 1.0 if current_price >= entry_price else 0.0
        
        progress = (current_price - entry_price) / (target_price - entry_price)
        
        # Clamp to [0, infinity] to allow for overshoot, but show realistic progress
        return max(0.0, progress)
    
    def calculate_loss_ratio(self) -> float:
        """
        Calculate position P&L as a percentage of entry value.
        """
        qty = self.position.get("qty", 0)
        entry_price = self.position.get("avg_fill_price", 0)
        current_price = self.position.get("current_price", 0)
        unrealized_pnl = self.position.get("unrealized_pl", 0)
        
        if not qty or not entry_price:
            return 0.0
        
        entry_value = qty * entry_price
        
        if entry_value <= 0:
            return 0.0
        
        return unrealized_pnl / entry_value
    
    def calculate_alignment_score(self) -> int:
        """
        Score position alignment with thesis on scale of 0-10.
        """
        score = 5  # Start neutral
        
        # Add for price progress
        progress = self.calculate_price_progress()
        if progress > 0.0:
            score += 2
        elif progress < 0.0:
            score -= 1
        
        # Add for time remaining (assuming we have timeframe)
        timeframe_months = self.thesis.get("timeframe_months", 36)
        days_remaining = max(0, (timeframe_months * 30) - self.calculate_days_held())
        if days_remaining > 0:
            score += 1
        
        # Add for conviction level
        conviction = self.thesis.get("conviction", "MEDIUM")
        if conviction == "HIGH":
            score += 1
        elif conviction == "LOW":
            score -= 1
        
        # Add for positive P&L
        pnl = self.position.get("unrealized_pl", 0)
        if pnl > 0:
            score += 1
        
        # Subtract for losses
        loss_ratio = self.calculate_loss_ratio()
        if loss_ratio < self.DEEP_LOSS_THRESHOLD:  # < -30%
            score -= 3
        elif loss_ratio < self.MODERATE_LOSS_THRESHOLD:  # < -15%
            score -= 2
        
        # Clamp to 0-10
        return max(0, min(10, score))
    
    def is_thesis_intact(self) -> bool:
        """
        Check if thesis appears broken based on position P&L.
        """
        loss_ratio = self.calculate_loss_ratio()
        
        # Deep loss = thesis broke
        if loss_ratio < self.DEEP_LOSS_THRESHOLD:
            return False
        
        # TODO: Add checks for actual invalidation events
        # (e.g., "Did competitor win the contract?" "Was the funding cut?")
        
        return True
    
    def get_conviction_accuracy(self) -> str:
        """
        Assess if position performance matches conviction level.
        """
        conviction = self.thesis.get("conviction", "MEDIUM")
        pnl_pct = self.position.get("unrealized_plpc", 0.0)
        days_held = self.calculate_days_held()
        
        if conviction == "HIGH":
            # HIGH conviction should show positive P&L quickly
            if pnl_pct > 0.05:  # up 5%+
                return "ON_TRACK"
            elif pnl_pct < -0.15:  # down 15%+
                return "BROKEN"
            else:
                return "CAUTION"
        
        elif conviction == "MEDIUM":
            # MEDIUM conviction: give it more time
            if days_held < 30:
                # Within first month, allow some downside
                return "ON_TRACK" if pnl_pct > -0.10 else "CAUTION"
            else:
                # After 1 month, should be positive
                return "ON_TRACK" if pnl_pct > 0.0 else "CAUTION"
        
        else:  # LOW conviction
            # LOW conviction: speculative, more loss tolerance
            return "ON_TRACK" if pnl_pct > -0.20 else "CAUTION"
    
    def validate(self) -> Dict:
        """
        Run full validation and return comprehensive alignment report.
        """
        warnings = []
        
        # Calculate all metrics
        alignment_score = self.calculate_alignment_score()
        price_progress = self.calculate_price_progress()
        conviction_accuracy = self.get_conviction_accuracy()
        thesis_intact = self.is_thesis_intact()
        loss_ratio = self.calculate_loss_ratio()
        
        # Determine status
        if not thesis_intact or conviction_accuracy == "BROKEN":
            status = "BROKEN"
            warnings.append("Thesis appears broken: position down significantly")
        elif conviction_accuracy == "CAUTION" or alignment_score < 5:
            status = "CAUTION"
            warnings.append("Thesis misalignment or performance below conviction")
        else:
            status = "ALIGNED"
        
        # Add specific warnings
        if loss_ratio < self.DEEP_LOSS_THRESHOLD:
            warnings.append(f"Position down {loss_ratio*100:.1f}% from entry")
        elif loss_ratio < self.MODERATE_LOSS_THRESHOLD:
            warnings.append(f"Position down {loss_ratio*100:.1f}% - monitor closely")
        
        # Build report
        days_held = self.calculate_days_held()
        timeframe_months = self.thesis.get("timeframe_months", 36)
        days_remaining = max(0, (timeframe_months * 30) - days_held)
        
        report = {
            "ticker": self.ticker,
            "alignment_score": alignment_score,
            "price_progress": round(price_progress, 3),
            "conviction_accuracy": conviction_accuracy,
            "thesis_intact": thesis_intact,
            "days_held": days_held,
            "days_remaining": days_remaining,
            "entry_price": round(self.position.get("avg_fill_price", 0), 2),
            "current_price": round(self.position.get("current_price", 0), 2),
            "target_price": self.thesis.get("target_price"),
            "unrealized_pnl": round(self.position.get("unrealized_pl", 0), 2),
            "unrealized_pnl_pct": round(self.position.get("unrealized_plpc", 0), 4),
            "conviction": self.thesis.get("conviction"),
            "status": status,
            "warnings": warnings
        }
        
        logger.info(f"{self.ticker}: alignment_score={alignment_score}, status={status}")
        
        return report


if __name__ == "__main__":
    # Example usage (for testing)
    test_position = {
        "symbol": "MU",
        "qty": 10,
        "avg_fill_price": 130.00,
        "current_price": 132.50,
        "unrealized_pl": 25.00,
        "unrealized_plpc": 0.0192
    }
    
    test_thesis = {
        "ticker": "MU",
        "target_price": 150.00,
        "timeframe_months": 36,
        "conviction": "HIGH",
        "confidence_score": 9
    }
    
    validator = ThesisValidator(test_position, test_thesis)
    report = validator.validate()
    
    print(f"\n{test_position['symbol']} Thesis Validation Report:")
    print(f"  Alignment Score: {report['alignment_score']}/10")
    print(f"  Status: {report['status']}")
    print(f"  Price Progress: {report['price_progress']*100:.1f}% toward target")
    print(f"  P&L: ${report['unrealized_pnl']:.2f} ({report['unrealized_pnl_pct']*100:.2f}%)")
    if report['warnings']:
        print(f"  Warnings: {', '.join(report['warnings'])}")
