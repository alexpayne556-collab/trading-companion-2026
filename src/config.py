"""
Configuration settings for Trading Companion 2026.
Loads from environment variables with sensible defaults.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# =============================================================================
# PATHS
# =============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
THESES_DIR = DATA_DIR / "theses"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
THESES_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# ALPACA API
# =============================================================================
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

# Use paper trading by default (safer)
ALPACA_PAPER = os.getenv("ALPACA_PAPER", "true").lower() == "true"

# =============================================================================
# REFRESH & TIMING
# =============================================================================
CLI_REFRESH_INTERVAL = int(os.getenv("CLI_REFRESH_INTERVAL", "60"))  # seconds
PORTFOLIO_SYNC_INTERVAL = int(os.getenv("PORTFOLIO_SYNC_INTERVAL", "900"))  # 15 min
NEWS_SYNC_INTERVAL = int(os.getenv("NEWS_SYNC_INTERVAL", "3600"))  # 1 hour

# =============================================================================
# RISK THRESHOLDS
# =============================================================================
CONCENTRATION_THRESHOLD = float(os.getenv("CONCENTRATION_THRESHOLD", "0.20"))  # 20%
OVERNIGHT_MOVE_THRESHOLD = float(os.getenv("OVERNIGHT_MOVE_THRESHOLD", "0.05"))  # 5%
STALE_DATA_THRESHOLD = int(os.getenv("STALE_DATA_THRESHOLD", "300"))  # 5 min

# =============================================================================
# LOGGING
# =============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s"
LOG_FILE = LOGS_DIR / "trading_companion.log"

# Configure root logger
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, mode='a'),
    ]
)

# =============================================================================
# VALIDATION
# =============================================================================
def validate_config() -> dict:
    """Validate configuration and return status."""
    issues = []
    
    if not ALPACA_API_KEY:
        issues.append("ALPACA_API_KEY not set")
    if not ALPACA_SECRET_KEY:
        issues.append("ALPACA_SECRET_KEY not set")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "alpaca_configured": bool(ALPACA_API_KEY and ALPACA_SECRET_KEY),
        "paper_mode": ALPACA_PAPER,
        "theses_dir": str(THESES_DIR),
        "logs_dir": str(LOGS_DIR),
    }


if __name__ == "__main__":
    # Quick config check
    status = validate_config()
    print("Configuration Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
