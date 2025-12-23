"""
Alpaca API Client Wrapper
Handles live portfolio data, P&L tracking, and transaction logging
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
import requests
import json

load_dotenv()

logger = logging.getLogger(__name__)

class AlpacaClient:
    def __init__(self):
        """Initialize Alpaca API client with credentials from .env"""
        self.api_key_id = os.getenv("ALPACA_API_KEY_ID")
        self.api_secret_key = os.getenv("ALPACA_API_SECRET_KEY")
        self.base_url = os.getenv("ALPACA_BASE_URL", "https://api.alpaca.markets")
        
        if not self.api_key_id or not self.api_secret_key:
            raise ValueError("ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY not found in .env")
        
        self.headers = {
            "APCA-API-KEY-ID": self.api_key_id,
            "APCA-API-SECRET-KEY": self.api_secret_key,
            "Content-Type": "application/json"
        }
        
        logger.info("Alpaca client initialized")
    
    def get_account(self) -> Dict:
        """Fetch account information (balance, buying power, etc.)"""
        try:
            response = requests.get(
                f"{self.base_url}/v2/account",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch account: {e}")
            return {}
    
    def get_positions(self) -> List[Dict]:
        """Fetch all open positions with current P&L"""
        try:
            response = requests.get(
                f"{self.base_url}/v2/positions",
                headers=self.headers
            )
            response.raise_for_status()
            positions = response.json()
            logger.info(f"Fetched {len(positions)} positions")
            return positions
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch positions: {e}")
            return []
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Fetch a specific position by symbol"""
        try:
            response = requests.get(
                f"{self.base_url}/v2/positions/{symbol}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch position {symbol}: {e}")
            return None
    
    def get_orders(self, status: str = "all", limit: int = 100) -> List[Dict]:
        """Fetch order history"""
        try:
            params = {
                "status": status,
                "limit": limit,
                "nested": True
            }
            response = requests.get(
                f"{self.base_url}/v2/orders",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            orders = response.json()
            logger.info(f"Fetched {len(orders)} orders")
            return orders
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch orders: {e}")
            return []
    
    def calculate_portfolio_metrics(self) -> Dict:
        """
        Calculate key portfolio metrics:
        - Total P&L
        - Concentration risk (% per position)
        - Account balance
        """
        try:
            account = self.get_account()
            positions = self.get_positions()
            
            portfolio_value = float(account.get("portfolio_value", 0))
            cash = float(account.get("cash", 0))
            buying_power = float(account.get("buying_power", 0))
            
            # Calculate unrealized P&L
            total_unrealized_pnl = sum(
                float(p.get("unrealized_pl", 0)) for p in positions
            )
            
            # Calculate concentration risk
            concentration = {}
            for pos in positions:
                symbol = pos.get("symbol")
                market_value = float(pos.get("market_value", 0))
                pct = (market_value / portfolio_value * 100) if portfolio_value > 0 else 0
                concentration[symbol] = {
                    "value": market_value,
                    "percentage": round(pct, 2),
                    "shares": float(pos.get("qty", 0)),
                    "avg_entry_price": float(pos.get("avg_fill_price", 0)),
                    "current_price": float(pos.get("current_price", 0)),
                    "unrealized_pl": float(pos.get("unrealized_pl", 0)),
                    "unrealized_plpc": float(pos.get("unrealized_plpc", 0))
                }
            
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "portfolio_value": round(portfolio_value, 2),
                "cash": round(cash, 2),
                "buying_power": round(buying_power, 2),
                "total_unrealized_pnl": round(total_unrealized_pnl, 2),
                "num_positions": len(positions),
                "concentration": concentration,
                "positions": positions
            }
            
            logger.info(f"Portfolio metrics: ${portfolio_value:.2f} with {len(positions)} positions")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate portfolio metrics: {e}")
            return {}
    
    def log_portfolio_snapshot(self, filepath: str = "logs/portfolio_snapshots.jsonl"):
        """
        Log current portfolio state to JSONL file (one JSON object per line)
        Used for data collection and future Spark analysis
        """
        try:
            metrics = self.calculate_portfolio_metrics()
            
            # Ensure logs directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Append to JSONL file
            with open(filepath, 'a') as f:
                f.write(json.dumps(metrics) + '\n')
            
            logger.info(f"Portfolio snapshot logged to {filepath}")
        except Exception as e:
            logger.error(f"Failed to log portfolio snapshot: {e}")


def test_connection():
    """Test Alpaca connection (run as: python -m src.apis.alpaca_client)"""
    try:
        client = AlpacaClient()
        account = client.get_account()
        print(f"✅ Connected to Alpaca")
        print(f"Account Balance: ${float(account.get('portfolio_value', 0)):.2f}")
        
        metrics = client.calculate_portfolio_metrics()
        print(f"Positions: {metrics.get('num_positions', 0)}")
        print(f"Unrealized P&L: ${metrics.get('total_unrealized_pnl', 0):.2f}")
        
        # Log snapshot
        client.log_portfolio_snapshot()
        print("✅ Portfolio snapshot logged")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")


if __name__ == "__main__":
    test_connection()
