"""
Trading Companion 2026 - Main Entry Point
Phase 1: Portfolio Monitor + Thesis Alignment
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def main():
    print("Trading Companion 2026 initialized")
    print(f"Alpaca API Key loaded: {bool(os.getenv('ALPACA_API_KEY'))}")

if __name__ == "__main__":
    main()
