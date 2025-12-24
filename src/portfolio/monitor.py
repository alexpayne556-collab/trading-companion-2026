"""
Feature 1: Portfolio Monitor
- Pull live positions from Alpaca
- Compare against thesis definitions
- Flag concentration risk
- Generate alerts
- Log snapshots for ML training
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from src.apis.alpaca_client import AlpacaClient

logger = logging.getLogger(__name__)


class PortfolioMonitor:
    def __init__(self, theses_file: str = "src/theses/definitions.json", 
                 concentration_threshold: float = 0.20):
        """
        Initialize Portfolio Monitor
        
        Args:
            theses_file: Path to thesis definitions JSON
            concentration_threshold: Warn if position > X% of portfolio
        """
        self.alpaca = AlpacaClient()
        self.theses_file = theses_file
        self.concentration_threshold = concentration_threshold
        self.theses = self._load_theses()
        self.thesis_map = {t.get("ticker"): t for t in self.theses}
        
        logger.info(f"Portfolio Monitor initialized with {len(self.theses)} theses")
    
    def _load_theses(self) -> List[Dict]:
        """Load thesis definitions from JSON file"""
        try:
            if Path(self.theses_file).exists():
                with open(self.theses_file, 'r') as f:
                    theses = json.load(f)
                    logger.info(f"Loaded {len(theses)} theses from {self.theses_file}")
                    return theses if isinstance(theses, list) else []
            else:
                logger.warning(f"Theses file not found: {self.theses_file}")
                return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse theses JSON: {e}")
            return []
    
    def check_thesis_alignment(self, position: Dict) -> Dict:
        """
        Check if a position aligns with its thesis using ThesisValidator.
        
        This now returns detailed alignment metrics:
        - alignment_score (0-10)
        - price_progress toward target
        - conviction_accuracy (ON_TRACK, CAUTION, BROKEN)
        - thesis_intact (bool)
        - status (ALIGNED, CAUTION, BROKEN)
        - warnings (list of issues)
        
        Args:
            position: Dict from Alpaca with symbol, qty, avg_fill_price, current_price, unrealized_pl, etc.
        
        Returns:
            Dict with alignment report (or error if no thesis defined)
        """
        from src.portfolio.thesis_validator import ThesisValidator
        
        ticker = position.get("symbol")
        thesis = self.thesis_map.get(ticker)
        
        # If no thesis defined, return "not aligned" quickly
        if not thesis:
            return {
                "ticker": ticker,
                "aligned": False,
                "alignment_score": 0,
                "status": "NO_THESIS",
                "warnings": [f"No thesis defined for {ticker}"]
            }
        
        # Run validator
        try:
            validator = ThesisValidator(position, thesis)
            validation_report = validator.validate()
            
            # Reformat for portfolio monitor context
            return {
                "ticker": ticker,
                "aligned": True,
                "alignment_score": validation_report["alignment_score"],
                "status": validation_report["status"],
                "conviction": validation_report["conviction"],
                "price_progress": validation_report["price_progress"],
                "entry_price": validation_report["entry_price"],
                "current_price": validation_report["current_price"],
                "target_price": validation_report["target_price"],
                "unrealized_pnl": validation_report["unrealized_pnl"],
                "unrealized_pnl_pct": validation_report["unrealized_pnl_pct"],
                "days_held": validation_report["days_held"],
                "days_remaining": validation_report["days_remaining"],
                "warnings": validation_report["warnings"]
            }
        
        except Exception as e:
            logger.error(f"Failed to validate thesis for {ticker}: {e}")
            return {
                "ticker": ticker,
                "aligned": False,
                "alignment_score": 0,
                "status": "ERROR",
                "warnings": [f"Validation error: {str(e)}"]
            }
    
    def check_concentration_risk(self, portfolio_metrics: Dict) -> Dict:
        """
        Identify concentration risk (positions > threshold % of portfolio)
        
        Returns dict with:
        - at_risk: list of tickers exceeding threshold
        - portfolio_value: total portfolio value
        """
        concentration = portfolio_metrics.get("concentration", {})
        portfolio_value = portfolio_metrics.get("portfolio_value", 0)
        
        at_risk = [
            {
                "ticker": ticker,
                "percentage": data.get("percentage", 0),
                "value": data.get("value", 0)
            }
            for ticker, data in concentration.items()
            if data.get("percentage", 0) > (self.concentration_threshold * 100)
        ]
        
        return {
            "at_risk": at_risk,
            "threshold_percentage": self.concentration_threshold * 100,
            "portfolio_value": portfolio_value,
            "flag_raised": len(at_risk) > 0
        }
    
    def generate_monitoring_report(self) -> Dict:
        """
        Generate full portfolio monitoring report
        
        Returns:
        - timestamp
        - portfolio_metrics (value, P&L, positions count)
        - thesis_alignment (per position)
        - concentration_risk (flagged positions)
        - alerts (list of things that need attention)
        """
        # Fetch live data
        metrics = self.alpaca.calculate_portfolio_metrics()
        positions = metrics.get("positions", [])
        
        # Check each position
        alignment_report = [self.check_thesis_alignment(pos) for pos in positions]
        
        # Check concentration
        concentration = self.check_concentration_risk(metrics)
        
        # Build alerts
        alerts = []
        
        # Alert if concentration flag raised
        if concentration["flag_raised"]:
            for risk in concentration["at_risk"]:
                alerts.append({
                    "type": "concentration_risk",
                    "severity": "warning",
                    "message": f"{risk['ticker']} is {risk['percentage']:.1f}% of portfolio (threshold: {concentration['threshold_percentage']:.1f}%)"
                })
        
        # Alert if position has no thesis
        for alignment in alignment_report:
            if not alignment["aligned"]:
                alerts.append({
                    "type": "no_thesis",
                    "severity": "info",
                    "message": alignment["warnings"][0]
                })
            elif alignment["warnings"]:
                for warning in alignment["warnings"]:
                    alerts.append({
                        "type": "thesis_warning",
                        "severity": "warning",
                        "ticker": alignment["ticker"],
                        "message": warning
                    })
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "portfolio": {
                "value": metrics.get("portfolio_value", 0),
                "unrealized_pnl": metrics.get("total_unrealized_pnl", 0),
                "num_positions": metrics.get("num_positions", 0),
                "cash": metrics.get("cash", 0)
            },
            "thesis_alignment": alignment_report,
            "concentration_risk": concentration,
            "alerts": alerts,
            "raw_metrics": metrics
        }
        
        return report
    
    def log_report(self, report: Dict, filepath: str = "logs/portfolio_reports.jsonl"):
        """Log monitoring report to JSONL"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'a') as f:
            f.write(json.dumps(report) + '\n')
        
        logger.info(f"Monitoring report logged to {filepath}")
    
    def print_report(self, report: Dict):
        """Pretty-print monitoring report to console"""
        print("\n" + "="*80)
        print("PORTFOLIO MONITOR REPORT")
        print("="*80)
        print(f"Timestamp: {report['timestamp']}")
        print(f"\nPORTFOLIO:")
        print(f"  Value: ${report['portfolio']['value']:.2f}")
        print(f"  Unrealized P&L: ${report['portfolio']['unrealized_pnl']:.2f}")
        print(f"  Positions: {report['portfolio']['num_positions']}")
        print(f"  Cash: ${report['portfolio']['cash']:.2f}")
        
        print(f"\nTHESIS ALIGNMENT:")
        for alignment in report['thesis_alignment']:
            ticker = alignment['ticker']
            score = alignment.get('alignment_score', 0)
            status = alignment.get('status', 'UNKNOWN')
            conviction = alignment.get('conviction', 'N/A')
            price_progress = alignment.get('price_progress', 0)
            pnl = alignment.get('unrealized_pnl_pct', 0)
            
            status_icon = "✓" if status == "ALIGNED" else "⚠️ " if status == "CAUTION" else "✗"
            
            print(f"  {status_icon} {ticker:<6} Score: {score}/10  {conviction:<10} Progress: {price_progress*100:>5.1f}%  P&L: {pnl*100:>6.2f}%")
            
            if alignment.get('warnings'):
                for warning in alignment['warnings']:
                    print(f"      └─ {warning}")
        
        print(f"\nCONCENTRATION RISK:")
        if report['concentration_risk']['flag_raised']:
            for risk in report['concentration_risk']['at_risk']:
                print(f"  ⚠️  {risk['ticker']}: {risk['percentage']:.1f}% of portfolio")
        else:
            print(f"  ✓ All positions within threshold ({report['concentration_risk']['threshold_percentage']:.1f}%)")
        
        if report['alerts']:
            print(f"\nALERTS ({len(report['alerts'])}):")
            for alert in report['alerts']:
                severity_icon = "⚠️ " if alert['severity'] == 'warning' else "ℹ️ "
                print(f"  {severity_icon}{alert['type']}: {alert['message']}")
        else:
            print(f"\nNo alerts")
        
        print("="*80 + "\n")


def main():
    """CLI entry point for portfolio monitoring"""
    monitor = PortfolioMonitor()
    report = monitor.generate_monitoring_report()
    monitor.print_report(report)
    monitor.log_report(report)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
