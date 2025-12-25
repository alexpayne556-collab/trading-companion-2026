"""Thesis validation logic for trading companion."""
from market_data import *
from datetime import datetime

class ThesisValidator:
    def __init__(self, today: str = None):
        self.today = (
            datetime.fromisoformat(today).date() if today else datetime.today().date()
        )
    def validate(self, position: Position, thesis: Thesis, market_data: MarketData) -> ValidationResult:
        conviction = self._calc_conviction_accuracy(position, thesis, market_data)
        progress = self._calc_catalyst_progress(position, thesis, market_data)
        risk = self._calc_invalidation_risk(position, thesis, market_data)
        alignment = self._composite_score(conviction, progress, risk, thesis.confidence_score)
        flags = self._generate_flags(position, thesis, conviction, progress, risk, market_data)
        return ValidationResult(
            alignment_score=alignment,
            conviction_accuracy=conviction,
            catalyst_progress=progress,
            invalidation_risk=risk,
            flags=flags
        )
    def _calc_conviction_accuracy(self, position: Position, thesis: Thesis, market_data: MarketData) -> int:
        conviction = self._base_conviction(position, thesis)
        if market_data.market.volatility_regime == VolatilityRegime.HIGH:
            conviction = max(0, conviction - 10)
        elif market_data.market.volatility_regime == VolatilityRegime.ELEVATED:
            conviction = max(0, conviction - 5)
        elif market_data.market.volatility_regime == VolatilityRegime.LOW:
            conviction = min(100, conviction + 5)
        if market_data.sector.stock_vs_sector_trend == "lagging":
            conviction = max(0, conviction - 8)
        elif market_data.sector.stock_vs_sector_trend == "outperforming":
            conviction = min(100, conviction + 8)
        if market_data.market.breadth_above_20ma < 0.30:
            conviction = max(0, conviction - 5)
        elif market_data.market.breadth_above_20ma > 0.70:
            conviction = min(100, conviction + 3)
        if market_data.sector.correlation_to_sector_60day < 0.3:
            conviction = min(100, conviction + 5)
        elif market_data.sector.correlation_to_sector_60day > 0.8:
            conviction = max(0, conviction - 3)
        return max(0, min(100, conviction))
    def _base_conviction(self, position: Position, thesis: Thesis) -> int:
        if thesis.direction == ThesisDirection.LONG:
            expected = thesis.target_price - position.entry_price
            actual = position.current_price - position.entry_price
        else:
            expected = position.entry_price - thesis.target_price
            actual = position.entry_price - position.current_price
        if expected <= 0:
            return 50
        ratio = actual / expected if expected != 0 else 0
        if ratio < 0:
            conviction = 50 - (abs(ratio) * 50)
        elif ratio >= 2.0:
            conviction = 100
        else:
            conviction = 50 + (ratio / 2.0 * 50)
        return int(conviction)
    def _calc_catalyst_progress(self, position: Position, thesis: Thesis, market_data: MarketData) -> int:
        progress = self._base_progress(position, thesis)
        vol_ratio = market_data.volatility.volatility_ratio()
        if vol_ratio > 1.5:
            progress = min(100, progress + 10)
        elif vol_ratio < 0.7:
            progress = max(0, progress - 5)
        if market_data.market.sp500_trend == TrendDirection.UP:
            if thesis.direction == ThesisDirection.LONG:
                progress = min(100, progress + 8)
            else:
                progress = max(0, progress - 8)
        elif market_data.market.sp500_trend == TrendDirection.DOWN:
            if thesis.direction == ThesisDirection.LONG:
                progress = max(0, progress - 8)
            else:
                progress = min(100, progress + 8)
        if market_data.sector.sector_trend == TrendDirection.UP:
            if thesis.direction == ThesisDirection.LONG:
                progress = min(100, progress + 5)
        elif market_data.sector.sector_trend == TrendDirection.DOWN:
            if thesis.direction == ThesisDirection.LONG:
                progress = max(0, progress - 5)
        if market_data.volatility.beta_60day > 1.5 and progress > 50:
            progress = min(100, progress + 5)
        return max(0, min(100, progress))
    def _base_progress(self, position: Position, thesis: Thesis) -> int:
        entry_date = datetime.fromisoformat(position.entry_date).date()
        days_elapsed = (self.today - entry_date).days
        days_total = thesis.timeframe_months * 30
        if days_total <= 0:
            return 50
        time_pct = min(1.0, days_elapsed / days_total)
        if thesis.direction == ThesisDirection.LONG:
            expected = thesis.target_price - position.entry_price
            actual = position.current_price - position.entry_price
        else:
            expected = position.entry_price - thesis.target_price
            actual = position.entry_price - position.current_price
        if expected <= 0 or time_pct == 0:
            return 50
        price_pct = actual / expected
        trajectory = price_pct / time_pct
        if trajectory <= 0:
            progress = 0
        elif trajectory >= 3.0:
            progress = 100
        else:
            progress = int(trajectory * 33.3 + 16.7)
        return max(0, min(100, progress))
    def _calc_invalidation_risk(self, position: Position, thesis: Thesis, market_data: MarketData) -> int:
        risk = self._base_invalidation_risk(position, thesis)
        vol_ratio = market_data.volatility.volatility_ratio()
        if vol_ratio > 1.5:
            risk = max(0, risk - 15)
        elif vol_ratio < 0.7:
            risk = min(100, risk + 5)
        if market_data.volatility.beta_60day > 1.5:
            risk = max(0, risk - 10)
        elif market_data.volatility.beta_60day < 0.5:
            risk = min(100, risk + 8)
        if market_data.market.volatility_regime == VolatilityRegime.HIGH:
            risk = min(100, risk + 15)
        elif market_data.market.volatility_regime == VolatilityRegime.ELEVATED:
            risk = min(100, risk + 8)
        elif market_data.market.volatility_regime == VolatilityRegime.LOW:
            risk = max(0, risk - 5)
        if market_data.sector.correlation_to_sector_60day > 0.85:
            risk = min(100, risk + 8)
        return max(0, min(100, risk))
    def _base_invalidation_risk(self, position: Position, thesis: Thesis) -> int:
        if thesis.is_invalidated(position.current_price):
            return 100
        if thesis.invalidation_price is not None:
            if thesis.direction == ThesisDirection.LONG:
                distance = position.current_price - thesis.invalidation_price
                total_range = thesis.target_price - thesis.invalidation_price
            else:
                distance = thesis.invalidation_price - position.current_price
                total_range = thesis.invalidation_price - thesis.target_price
            if total_range <= 0:
                return 50
            pct_to_invalidation = distance / total_range
            risk = int((1 - pct_to_invalidation) * 100)
        else:
            risk = 30
        entry_date = datetime.fromisoformat(position.entry_date).date()
        days_elapsed = (self.today - entry_date).days
        days_total = thesis.timeframe_months * 30
        if days_elapsed > days_total:
            risk = min(100, risk + 20)
        return risk
    def _composite_score(self, conviction: int, progress: int, risk: int, confidence: float) -> float:
        inverse_risk = 100 - risk
        raw_score = (
            conviction * 0.40 +
            progress * 0.35 +
            inverse_risk * 0.25
        )
        scaled = raw_score / 10.0
        confidence_factor = 0.8 + (confidence * 0.4)
        final = scaled * confidence_factor
        return round(max(0, min(10, final)), 2)
    def _generate_flags(self, position: Position, thesis: Thesis, conviction: int, progress: int, risk: int, market_data: MarketData) -> list:
        flags = []
        if conviction < 30:
            flags.append("CONVICTION_DEGRADED: Price moving against thesis")
        if conviction < 20:
            flags.append("SEVERE_CONVICTION_LOSS: Consider exiting")
        if progress < 25:
            flags.append("BEHIND_SCHEDULE: Catalyst not materializing on pace")
        elif progress > 90:
            flags.append("AHEAD_OF_SCHEDULE: Thesis executing faster than expected")
        if risk >= 100:
            flags.append("INVALIDATION_TRIGGERED: Thesis is invalidated")
        elif risk > 70:
            flags.append("HIGH_INVALIDATION_RISK: Close to thesis break, reduce size")
        entry_date = datetime.fromisoformat(position.entry_date).date()
        days_elapsed = (self.today - entry_date).days
        days_total = thesis.timeframe_months * 30
        if days_elapsed > days_total:
            months_over = (days_elapsed - days_total) / 30
            flags.append(f"OVERTIME: {months_over:.1f}mo past original timeframe")
        if thesis.is_target_hit(position.current_price):
            flags.append("TARGET_REACHED: Thesis fulfilled, consider taking profits")
        if market_data.market.volatility_regime == VolatilityRegime.HIGH:
            flags.append("CRISIS_MODE_ACTIVE: VIX high, thesis execution harder")
        elif market_data.market.volatility_regime == VolatilityRegime.ELEVATED:
            flags.append("ELEVATED_VOLATILITY: Market stressed, wider swings expected")
        elif market_data.market.volatility_regime == VolatilityRegime.LOW:
            flags.append("LOW_VOLATILITY: Calm market, thesis might work smoother")
        if market_data.sector.stock_vs_sector_trend == "lagging":
            diff_pct = market_data.sector.relative_strength_vs_sector_5d * 100
            flags.append(f"LAGGING_SECTOR: Stock {diff_pct:.1f}% behind sector in 5d")
        elif market_data.sector.stock_vs_sector_trend == "outperforming":
            diff_pct = market_data.sector.relative_strength_vs_sector_5d * 100
            flags.append(f"OUTPERFORMING: Stock ahead of sector by {diff_pct:.1f}% in 5d")
        breadth_pct = market_data.market.breadth_above_20ma * 100
        if breadth_pct < 30:
            flags.append(f"WEAK_BREADTH: Only {breadth_pct:.0f}% of stocks above 20MA, structural weakness")
        elif breadth_pct > 70:
            flags.append(f"STRONG_BREADTH: {breadth_pct:.0f}% of stocks in uptrend, tailwind for longs")
        if market_data.market.sp500_trend == TrendDirection.DOWN:
            if thesis.direction == ThesisDirection.LONG:
                flags.append("HEADWIND: Broad market in downtrend, thesis harder to execute")
        elif market_data.market.sp500_trend == TrendDirection.UP:
            if thesis.direction == ThesisDirection.LONG:
                flags.append("TAILWIND: Broad market in uptrend, favorable backdrop")
        vol_ratio = market_data.volatility.volatility_ratio()
        if vol_ratio > 1.8:
            vol_pct = (vol_ratio - 1) * 100
            flags.append(f"VOLATILITY_SPIKE: Vol up {vol_pct:.0f}% vs baseline, expect wider swings")
        elif vol_ratio < 0.6:
            flags.append("EXTREME_CALM: Vol unusually low, mean reversion risk")
        return flags
