"""
CLI Dashboard for Trading Companion 2026.
Text-based portfolio monitor with auto-refresh.
"""

import os
import time
import logging
from datetime import datetime

from src.services import PortfolioService
from src.config import CLI_REFRESH_INTERVAL

logger = logging.getLogger(__name__)


class CLIDashboard:
    """Text-based portfolio dashboard."""
    
    BOX_WIDTH = 78
    
    def __init__(self, service: PortfolioService = None):
        """Initialize CLI dashboard."""
        self.service = service or PortfolioService()
        self.snapshot = None
        self.refresh_interval = CLI_REFRESH_INTERVAL
        self.last_error = None
    
    def clear_screen(self) -> None:
        """Clear terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def refresh(self) -> None:
        """Refresh portfolio data."""
        try:
            logger.info("Refreshing portfolio...")
            success = self.service.refresh()
            if success:
                self.snapshot = self.service.get_snapshot()
                self.last_error = None
            else:
                self.last_error = "Failed to refresh - check API connection"
            logger.info("Refresh complete")
        except Exception as e:
            logger.error(f"Error refreshing: {e}")
            self.last_error = str(e)
    
    def format_currency(self, value) -> str:
        """Format value as currency."""
        if value is None:
            return "$-.--"
        return f"${value:,.2f}"
    
    def format_percent(self, value) -> str:
        """Format value as percentage."""
        if value is None:
            return "-.--%"
        sign = "+" if value >= 0 else ""
        return f"{sign}{value:.1f}%"
    
    def safe_get(self, data: dict, *keys, default=None):
        """Safely get nested dictionary values."""
        for key in keys:
            if not isinstance(data, dict):
                return default
            data = data.get(key, default)
            if data is None:
                return default
        return data
    
    def display_header(self) -> None:
        """Display dashboard header."""
        w = self.BOX_WIDTH
        print("+" + "=" * w + "+")
        print("|" + "TRADING COMPANION 2026 - PORTFOLIO MONITOR".center(w) + "|")
        timestamp = f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        print("|" + timestamp.center(w) + "|")
        print("+" + "=" * w + "+")
        print()
    
    def display_portfolio_summary(self) -> None:
        """Display portfolio summary."""
        if not self.snapshot:
            if self.last_error:
                print(f"ERROR: {self.last_error}")
            else:
                print("No portfolio data. Run refresh first.")
            return
        
        portfolio = self.safe_get(self.snapshot, 'portfolio', default={})
        w = self.BOX_WIDTH
        
        print("+" + "-" * w + "+")
        print("|" + " PORTFOLIO SUMMARY".ljust(w) + "|")
        print("+" + "-" * w + "+")
        
        rows = [
            ("Total Value:", self.format_currency(portfolio.get('total_value'))),
            ("Total Cost:", self.format_currency(portfolio.get('total_cost'))),
            ("Unrealized P&L:", self.format_currency(portfolio.get('unrealized_pnl'))),
            ("P&L %:", self.format_percent(portfolio.get('unrealized_pnl_pct'))),
            ("Cash:", self.format_currency(portfolio.get('cash_balance'))),
            ("Positions:", str(portfolio.get('position_count', 0))),
        ]
        
        for label, value in rows:
            content = f"  {label:<18} {value:>20}"
            print("|" + content.ljust(w) + "|")
        
        print("+" + "-" * w + "+")
        print()
    
    def display_positions(self) -> None:
        """Display all positions."""
        positions = self.safe_get(self.snapshot, 'positions', default=[])
        if not positions:
            return
        
        w = self.BOX_WIDTH
        
        print("+" + "-" * w + "+")
        print("|" + " POSITIONS".ljust(w) + "|")
        print("+" + "-" * w + "+")
        
        # Header
        header = f"| {'Ticker':<8} | {'Shares':>8} | {'Price':>10} | {'Value':>12} | {'P&L %':>8} | {'Alloc':>6} |"
        print(header)
        print("|" + "-" * w + "|")
        
        # Rows
        for pos in positions:
            ticker = str(pos.get('ticker', '???'))[:8]
            shares = f"{pos.get('shares', 0):.0f}"
            price = self.format_currency(pos.get('current_price'))
            value = self.format_currency(pos.get('current_value'))
            pnl = self.format_percent(pos.get('unrealized_pnl_pct'))
            alloc = f"{pos.get('allocation_pct', 0):.1f}%"
            
            row = f"| {ticker:<8} | {shares:>8} | {price:>10} | {value:>12} | {pnl:>8} | {alloc:>6} |"
            print(row)
        
        print("+" + "-" * w + "+")
        print()
    
    def display_alerts(self) -> None:
        """Display alerts if any."""
        alerts = self.safe_get(self.snapshot, 'alerts', default={})
        critical = alerts.get('critical', [])
        warning = alerts.get('warning', [])
        
        w = self.BOX_WIDTH
        
        if critical:
            print("+" + "-" * w + "+")
            print("|" + " [!] CRITICAL ALERTS".ljust(w) + "|")
            print("+" + "-" * w + "+")
            for alert in critical[:5]:
                text = str(alert)[:w-4]
                print("|  " + text.ljust(w-2) + "|")
            print("+" + "-" * w + "+")
            print()
        
        if warning:
            print("+" + "-" * w + "+")
            print("|" + " [?] WARNINGS".ljust(w) + "|")
            print("+" + "-" * w + "+")
            for alert in warning[:5]:
                text = str(alert)[:w-4]
                print("|  " + text.ljust(w-2) + "|")
            print("+" + "-" * w + "+")
            print()
    
    def display_footer(self) -> None:
        """Display footer."""
        print(f"Refresh: {self.refresh_interval}s | Ctrl+C to exit")
    
    def display_connection_status(self) -> None:
        """Display connection status."""
        status = self.service.get_status()
        w = self.BOX_WIDTH
        
        if status.get('alpaca_connected'):
            print("|" + f" [OK] Alpaca connected".ljust(w) + "|")
        else:
            error = status.get('alpaca_error', 'Unknown error')
            print("|" + f" [X] Alpaca: {error}"[:w].ljust(w) + "|")
    
    def render(self) -> None:
        """Render complete dashboard."""
        self.clear_screen()
        self.display_header()
        self.display_portfolio_summary()
        self.display_positions()
        self.display_alerts()
        self.display_footer()
    
    def run(self) -> None:
        """Run dashboard in loop."""
        logger.info("Starting CLI Dashboard...")
        
        # Check connection first
        status = self.service.test_connection()
        if not status.get('connected'):
            print("=" * 80)
            print("ALPACA CONNECTION FAILED")
            print("=" * 80)
            print(f"Error: {status.get('error', 'Unknown')}")
            print()
            print("To fix this:")
            print("1. Create a .env file in the project root")
            print("2. Add your Alpaca API keys:")
            print("   ALPACA_API_KEY=your_key_here")
            print("   ALPACA_SECRET_KEY=your_secret_here")
            print("3. Get keys from: https://app.alpaca.markets/paper/dashboard/overview")
            print()
            return
        
        try:
            while True:
                self.refresh()
                self.render()
                time.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            print("\n\nDashboard stopped.")
            logger.info("Dashboard stopped by user")


def main():
    """Entry point."""
    dashboard = CLIDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
