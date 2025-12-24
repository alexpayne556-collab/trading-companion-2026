"""
THESIS VALIDATOR: Score portfolio position alignment against thesis definitions

PURPOSE:
--------
For each position in the portfolio, compare it against its defined thesis to score:
1. How close is current price to target price?
2. How long has the position been held vs. planned timeframe?
3. Is the conviction level still appropriate?
4. Has the thesis been invalidated by market events?

INPUT (Example):
----------------
position = {
    "symbol": "MU",
    "qty": 10,
    "avg_fill_price": 130.00,
    "current_price": 132.50,
    "unrealized_pl": 25.00,
    "unrealized_plpc": 0.0192
}

thesis = {
    "ticker": "MU",
    "target_price": 150.00,
    "timeframe_months": 36,
    "conviction": "HIGH",
    "confidence_score": 9
}

OUTPUT (Example):
-----------------
{
    "ticker": "MU",
    "alignment_score": 7,  # out of 10
    "price_progress": 0.48,  # how close to target (current_price - entry) / (target - entry)
    "conviction_accuracy": "ON_TRACK",  # HIGH conviction, reasonable entry
    "thesis_intact": True,  # no invalidation signs
    "days_held": 1,
    "days_remaining": 1079,  # target timeframe - days held
    "status": "ALIGNED",  # ALIGNED, CAUTION, BROKEN
    "warnings": []
}

CALCULATION LOGIC:
------------------
1. PRICE_PROGRESS:
   - If no target price: assume thesis is long-term, measure by unrealized P&L %
   - If target price exists: measure progress from entry to target
   - formula: (current_price - entry_price) / (target_price - entry_price)
   - capped at 0.0 to 1.0 (overshoot counts as full progress)

2. ALIGNMENT_SCORE (0-10):
   - Start at 5 (neutral)
   - Add points: if price progressing toward target (+2)
   - Add points: if time remaining and thesis not broken (+1)
   - Add points: if conviction is HIGH (+1)
   - Add points: if P&L is positive (+1)
   - Subtract points: if thesis shows invalidation signs (-3)
   - Subtract points: if deeply underwater (-2)
   - Result is clamped to 0-10

3. THESIS_INTACT:
   - Check unrealized P&L % against "invalidation threshold" (typically -30%)
   - If position is down >30% from entry, thesis may be broken
   - Return False if any invalidation conditions met
   - Otherwise True

4. CONVICTION_ACCURACY:
   - HIGH conviction should show positive P&L or recent entry
   - MEDIUM conviction should be breakeven or better after 1 month+
   - LOW conviction should be treated as speculative (higher loss tolerance)
"""

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
