"""
Integration tests for Trading Companion 2026.
Tests the full system without hitting live APIs.
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch

# Test imports work
def test_imports():
    """Test that all core modules can be imported."""
    from src.config import CLI_REFRESH_INTERVAL, THESES_DIR
    from src.portfolio.models import Position, PortfolioSnapshot
    from src.thesis.models import Thesis, Catalyst
    from src.thesis.loader import ThesisLoader
    from src.integrations.alpaca.client import AlpacaClient
    from src.risk.rules import RiskRuleEngine, Alert, AlertSeverity
    from src.portfolio.manager import PortfolioManager
    from src.services.portfolio_service import PortfolioService
    
    assert CLI_REFRESH_INTERVAL > 0
    assert THESES_DIR is not None


def test_position_model():
    """Test Position model calculations."""
    from src.portfolio.models import Position
    
    pos = Position(
        ticker="AAPL",
        shares=10,
        entry_price=150.0,
        current_price=175.0,
    )
    
    assert pos.current_value == 1750.0
    assert pos.cost_basis == 1500.0
    assert pos.unrealized_pnl == 250.0
    assert abs(pos.unrealized_pnl_pct - 16.67) < 0.1


def test_portfolio_snapshot():
    """Test PortfolioSnapshot aggregations."""
    from src.portfolio.models import Position, PortfolioSnapshot
    
    positions = [
        Position(ticker="AAPL", shares=10, entry_price=150, current_price=175),
        Position(ticker="MSFT", shares=5, entry_price=300, current_price=350),
    ]
    
    snapshot = PortfolioSnapshot(
        positions=positions,
        cash_balance=1000.0,
    )
    
    # AAPL: 10 * 175 = 1750
    # MSFT: 5 * 350 = 1750
    # Total positions: 3500
    # Total + cash: 4500
    assert snapshot.total_value == 4500.0
    assert snapshot.position_count == 2
    assert snapshot.get_position("AAPL") is not None
    assert snapshot.get_allocation("AAPL") == pytest.approx(38.89, rel=0.01)


def test_thesis_model():
    """Test Thesis model."""
    from src.thesis.models import Thesis, Catalyst
    from datetime import date, timedelta
    
    future_date = date.today() + timedelta(days=30)
    
    thesis = Thesis(
        ticker="LUNR",
        name="Lunar Logistics",
        thesis="Space industry inflection",
        conviction="HIGH",
        confidence_score=8,
        target_price=15.0,
        catalysts=[
            Catalyst(
                event="Lunar landing",
                event_date=future_date,
                probability=0.8,
            )
        ],
    )
    
    assert thesis.conviction_score == 9
    assert len(thesis.active_catalysts) == 1
    assert thesis.next_catalyst is not None
    assert thesis.upside_pct(10.0) == 50.0


def test_risk_rules_concentration():
    """Test concentration risk detection."""
    from src.portfolio.models import Position, PortfolioSnapshot
    from src.risk.rules import RiskRuleEngine, AlertSeverity
    
    # Position is 80% of portfolio - should trigger alert
    positions = [
        Position(ticker="AAPL", shares=100, entry_price=100, current_price=100),
    ]
    snapshot = PortfolioSnapshot(
        positions=positions,
        cash_balance=2500.0,  # 10000 + 2500 = 12500 total, AAPL is 80%
    )
    
    engine = RiskRuleEngine(concentration_threshold=0.20)
    alerts = engine.evaluate(snapshot)
    
    concentration_alerts = [a for a in alerts if a.rule == "concentration"]
    assert len(concentration_alerts) == 1
    assert concentration_alerts[0].ticker == "AAPL"


def test_risk_rules_missing_thesis():
    """Test missing thesis detection."""
    from src.portfolio.models import Position, PortfolioSnapshot
    from src.risk.rules import RiskRuleEngine
    
    positions = [
        Position(ticker="AAPL", shares=10, entry_price=100, current_price=100),
    ]
    snapshot = PortfolioSnapshot(positions=positions, cash_balance=5000)
    
    engine = RiskRuleEngine()
    alerts = engine.evaluate(snapshot, theses={})  # No theses defined
    
    missing_alerts = [a for a in alerts if a.rule == "missing_thesis"]
    assert len(missing_alerts) == 1


def test_alpaca_client_not_configured():
    """Test AlpacaClient reports not configured without keys."""
    from src.integrations.alpaca.client import AlpacaClient
    
    client = AlpacaClient(api_key="", secret_key="")
    assert not client.is_configured
    
    status = client.test_connection()
    assert not status["connected"]
    assert "not configured" in status["error"].lower()


def test_portfolio_service():
    """Test PortfolioService with mocked manager."""
    from src.services.portfolio_service import PortfolioService
    from src.portfolio.manager import PortfolioManager
    
    service = PortfolioService()
    status = service.get_status()
    
    assert "alpaca_connected" in status
    assert "has_snapshot" in status


def test_thesis_loader(tmp_path):
    """Test ThesisLoader with temporary directory."""
    from src.thesis.loader import ThesisLoader
    from src.thesis.models import Thesis
    import yaml
    
    # Create a test thesis file
    thesis_data = {
        "ticker": "TEST",
        "name": "Test Company",
        "thesis": "Test thesis statement",
        "conviction": "HIGH",
        "confidence_score": 7,
    }
    
    thesis_file = tmp_path / "TEST.yaml"
    with open(thesis_file, 'w') as f:
        yaml.dump(thesis_data, f)
    
    loader = ThesisLoader(theses_dir=tmp_path)
    theses = loader.load_all()
    
    assert "TEST" in theses
    assert theses["TEST"].ticker == "TEST"
    assert theses["TEST"].conviction == "HIGH"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
