#!/usr/bin/env python3
"""
🐺 WOLF CORRELATOR - Portfolio Risk Intelligence
================================================
Real portfolio thinking. Not just signal chasing.

TRACKS:
- Sector/theme exposure across positions
- Correlation between holdings
- Risk concentration warnings

WARNS:
- "You're 40% exposed to quantum"
- "QBTS correlates 0.85 with your existing positions"
- "Adding this increases drawdown risk by 15%"

SUGGESTS:
- Diversification opportunities
- Uncorrelated plays to balance portfolio
- Position sizing based on concentration

Run: python wolf_correlator.py portfolio
     python wolf_correlator.py check TICKER
     python wolf_correlator.py suggest

AWOOOO 🐺
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import yfinance as yf
import pandas as pd
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================

class CorrelatorConfig:
    """Correlator settings"""
    
    POSITIONS_FILE = "config/wolf_positions.json"
    CORRELATION_CACHE = "logs/correlation_cache.json"
    
    # Correlation thresholds
    HIGH_CORRELATION = 0.7      # Warn above this
    EXTREME_CORRELATION = 0.85  # Strong warning
    
    # Concentration thresholds
    MAX_SECTOR_PCT = 40         # Max % in one sector
    MAX_THEME_PCT = 50          # Max % in one theme
    
    # Lookback for correlation calculation
    CORRELATION_DAYS = 60


# ============================================================
# SECTOR & THEME MAPPINGS
# ============================================================

# Map tickers to sectors
TICKER_SECTORS = {
    # Quantum Computing
    "IONQ": "quantum", "RGTI": "quantum", "QBTS": "quantum", "QUBT": "quantum",
    
    # Nuclear Energy
    "NNE": "nuclear", "OKLO": "nuclear", "SMR": "nuclear", "LEU": "nuclear", 
    "CCJ": "nuclear", "UEC": "nuclear", "UUUU": "nuclear",
    
    # AI & Chips
    "NVDA": "ai_chips", "AMD": "ai_chips", "ARM": "ai_chips", "SMCI": "ai_chips",
    "TSM": "ai_chips", "INTC": "ai_chips", "AVGO": "ai_chips",
    
    # Voice AI
    "SOUN": "voice_ai", "AI": "voice_ai", "BBAI": "voice_ai",
    
    # Space
    "RKLB": "space", "LUNR": "space", "RDW": "space", "ASTS": "space",
    "SPCE": "space", "MNTS": "space",
    
    # Crypto/Blockchain
    "MARA": "crypto", "RIOT": "crypto", "CLSK": "crypto", "HUT": "crypto",
    "COIN": "crypto", "MSTR": "crypto",
    
    # EV
    "TSLA": "ev", "RIVN": "ev", "LCID": "ev", "NIO": "ev", "XPEV": "ev",
    "LI": "ev", "FSR": "ev",
    
    # Biotech / AI Drug Discovery
    "RXRX": "biotech_ai", "DNAY": "biotech_ai", "SDGR": "biotech_ai",
    "EXAI": "biotech_ai",
    
    # Traditional Tech
    "AAPL": "tech", "MSFT": "tech", "GOOGL": "tech", "META": "tech",
    "AMZN": "tech", "NFLX": "tech",
    
    # Financials
    "JPM": "financials", "BAC": "financials", "GS": "financials",
    "MS": "financials", "WFC": "financials",
    
    # Energy (Traditional)
    "XOM": "energy", "CVX": "energy", "OXY": "energy", "SLB": "energy"
}

# Map sectors to broader themes (for correlation grouping)
SECTOR_THEMES = {
    "quantum": "speculative_tech",
    "nuclear": "energy_transition",
    "ai_chips": "ai_ecosystem",
    "voice_ai": "ai_ecosystem",
    "space": "speculative_tech",
    "crypto": "speculative_tech",
    "ev": "energy_transition",
    "biotech_ai": "ai_ecosystem",
    "tech": "big_tech",
    "financials": "traditional",
    "energy": "traditional"
}

# Sector descriptions
SECTOR_INFO = {
    "quantum": {"name": "Quantum Computing", "risk": "extreme", "beta": 2.5},
    "nuclear": {"name": "Nuclear Energy", "risk": "high", "beta": 1.8},
    "ai_chips": {"name": "AI & Semiconductors", "risk": "high", "beta": 1.5},
    "voice_ai": {"name": "Voice AI", "risk": "high", "beta": 2.0},
    "space": {"name": "Space & Satellites", "risk": "extreme", "beta": 2.2},
    "crypto": {"name": "Crypto & Blockchain", "risk": "extreme", "beta": 2.8},
    "ev": {"name": "Electric Vehicles", "risk": "high", "beta": 1.6},
    "biotech_ai": {"name": "AI Drug Discovery", "risk": "extreme", "beta": 2.0},
    "tech": {"name": "Big Tech", "risk": "medium", "beta": 1.1},
    "financials": {"name": "Financials", "risk": "medium", "beta": 1.0},
    "energy": {"name": "Traditional Energy", "risk": "medium", "beta": 0.9}
}


# ============================================================
# POSITION TRACKING
# ============================================================

class PositionTracker:
    """Track current positions"""
    
    def __init__(self):
        self.positions_file = Path(CorrelatorConfig.POSITIONS_FILE)
        self.positions_file.parent.mkdir(exist_ok=True)
    
    def load_positions(self) -> Dict[str, dict]:
        """Load current positions"""
        if self.positions_file.exists():
            with open(self.positions_file) as f:
                return json.load(f)
        return {}
    
    def save_positions(self, positions: Dict[str, dict]):
        """Save positions"""
        with open(self.positions_file, "w") as f:
            json.dump(positions, f, indent=2)
    
    def add_position(self, ticker: str, shares: float, entry_price: float, 
                     sector: str = None, notes: str = ""):
        """Add a position"""
        positions = self.load_positions()
        
        # Auto-detect sector
        if not sector:
            sector = TICKER_SECTORS.get(ticker.upper(), "other")
        
        positions[ticker.upper()] = {
            "shares": shares,
            "entry_price": entry_price,
            "entry_date": datetime.now().isoformat(),
            "sector": sector,
            "notes": notes
        }
        
        self.save_positions(positions)
        print(f"✅ Added {ticker.upper()}: {shares} shares @ ${entry_price:.2f} ({sector})")
    
    def remove_position(self, ticker: str):
        """Remove a position"""
        positions = self.load_positions()
        
        if ticker.upper() in positions:
            del positions[ticker.upper()]
            self.save_positions(positions)
            print(f"✅ Removed {ticker.upper()}")
        else:
            print(f"Position not found: {ticker}")
    
    def update_position(self, ticker: str, shares: float = None, sector: str = None):
        """Update a position"""
        positions = self.load_positions()
        
        if ticker.upper() not in positions:
            print(f"Position not found: {ticker}")
            return
        
        if shares is not None:
            positions[ticker.upper()]["shares"] = shares
        if sector:
            positions[ticker.upper()]["sector"] = sector
        
        self.save_positions(positions)
        print(f"✅ Updated {ticker.upper()}")


# ============================================================
# CORRELATION CALCULATOR
# ============================================================

class CorrelationCalculator:
    """Calculate price correlations between tickers"""
    
    def __init__(self):
        self.cache_file = Path(CorrelatorConfig.CORRELATION_CACHE)
        self.cache = self._load_cache()
    
    def _load_cache(self) -> dict:
        """Load correlation cache"""
        if self.cache_file.exists():
            with open(self.cache_file) as f:
                cache = json.load(f)
                # Check if cache is fresh (less than 1 day old)
                cache_date = cache.get("date")
                if cache_date:
                    cache_dt = datetime.fromisoformat(cache_date)
                    if datetime.now() - cache_dt < timedelta(days=1):
                        return cache.get("correlations", {})
        return {}
    
    def _save_cache(self, correlations: dict):
        """Save correlation cache"""
        self.cache_file.parent.mkdir(exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump({
                "date": datetime.now().isoformat(),
                "correlations": correlations
            }, f, indent=2)
    
    def get_correlation(self, ticker1: str, ticker2: str) -> float:
        """Get correlation between two tickers"""
        # Check cache
        key = f"{min(ticker1, ticker2)}-{max(ticker1, ticker2)}"
        if key in self.cache:
            return self.cache[key]
        
        # Calculate
        corr = self._calculate_correlation(ticker1, ticker2)
        
        # Cache
        self.cache[key] = corr
        self._save_cache(self.cache)
        
        return corr
    
    def _calculate_correlation(self, ticker1: str, ticker2: str) -> float:
        """Calculate 60-day price correlation"""
        try:
            tickers = f"{ticker1} {ticker2}"
            data = yf.download(tickers, period=f"{CorrelatorConfig.CORRELATION_DAYS}d", 
                              interval="1d", progress=False, group_by='ticker')
            
            if data.empty:
                return 0.0
            
            # Handle multi-ticker data
            if isinstance(data.columns, pd.MultiIndex):
                returns1 = data[ticker1]["Close"].pct_change().dropna()
                returns2 = data[ticker2]["Close"].pct_change().dropna()
            else:
                # Single ticker edge case
                return 0.0
            
            # Align indices
            common_idx = returns1.index.intersection(returns2.index)
            if len(common_idx) < 10:
                return 0.0
            
            returns1 = returns1.loc[common_idx]
            returns2 = returns2.loc[common_idx]
            
            # Calculate correlation
            correlation = returns1.corr(returns2)
            
            return correlation if not np.isnan(correlation) else 0.0
            
        except Exception as e:
            print(f"  Correlation error {ticker1}/{ticker2}: {e}")
            return 0.0
    
    def get_portfolio_correlations(self, tickers: List[str]) -> pd.DataFrame:
        """Get correlation matrix for portfolio"""
        n = len(tickers)
        corr_matrix = np.eye(n)  # Start with identity
        
        for i in range(n):
            for j in range(i+1, n):
                corr = self.get_correlation(tickers[i], tickers[j])
                corr_matrix[i, j] = corr
                corr_matrix[j, i] = corr
        
        return pd.DataFrame(corr_matrix, index=tickers, columns=tickers)


# ============================================================
# WOLF CORRELATOR - MAIN ENGINE
# ============================================================

class WolfCorrelator:
    """Main correlation and risk engine"""
    
    def __init__(self):
        self.positions = PositionTracker()
        self.correlator = CorrelationCalculator()
    
    # ========================================
    # PORTFOLIO ANALYSIS
    # ========================================
    
    def analyze_portfolio(self) -> dict:
        """Full portfolio risk analysis"""
        positions = self.positions.load_positions()
        
        if not positions:
            return {"error": "No positions loaded. Use 'portfolio add' to add positions."}
        
        # Get current prices
        portfolio_value = 0
        position_values = {}
        
        for ticker, pos in positions.items():
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                current_price = info.get("regularMarketPrice") or info.get("currentPrice", pos["entry_price"])
                value = pos["shares"] * current_price
                position_values[ticker] = {
                    "shares": pos["shares"],
                    "entry_price": pos["entry_price"],
                    "current_price": current_price,
                    "value": value,
                    "pnl_pct": ((current_price - pos["entry_price"]) / pos["entry_price"]) * 100,
                    "sector": pos.get("sector", "other")
                }
                portfolio_value += value
            except Exception as e:
                print(f"  Warning: Could not fetch {ticker}: {e}")
        
        if portfolio_value == 0:
            return {"error": "Could not calculate portfolio value."}
        
        # Calculate exposures
        sector_exposure = defaultdict(float)
        theme_exposure = defaultdict(float)
        
        for ticker, data in position_values.items():
            pct = (data["value"] / portfolio_value) * 100
            data["portfolio_pct"] = pct
            
            sector = data["sector"]
            sector_exposure[sector] += pct
            
            theme = SECTOR_THEMES.get(sector, "other")
            theme_exposure[theme] += pct
        
        # Calculate portfolio beta
        weighted_beta = 0
        for ticker, data in position_values.items():
            sector = data["sector"]
            sector_beta = SECTOR_INFO.get(sector, {}).get("beta", 1.0)
            weighted_beta += sector_beta * (data["portfolio_pct"] / 100)
        
        # Generate warnings
        warnings = []
        
        # Sector concentration warnings
        for sector, pct in sector_exposure.items():
            if pct > CorrelatorConfig.MAX_SECTOR_PCT:
                sector_name = SECTOR_INFO.get(sector, {}).get("name", sector)
                warnings.append({
                    "type": "concentration",
                    "severity": "high",
                    "message": f"⚠️ HIGH {sector_name.upper()} CONCENTRATION: {pct:.1f}% (max: {CorrelatorConfig.MAX_SECTOR_PCT}%)"
                })
        
        # Theme concentration warnings
        for theme, pct in theme_exposure.items():
            if pct > CorrelatorConfig.MAX_THEME_PCT:
                warnings.append({
                    "type": "concentration",
                    "severity": "medium",
                    "message": f"⚠️ Theme '{theme}' at {pct:.1f}% - consider diversification"
                })
        
        # High beta warning
        if weighted_beta > 1.8:
            warnings.append({
                "type": "risk",
                "severity": "high",
                "message": f"⚠️ HIGH PORTFOLIO BETA: {weighted_beta:.2f} - expect 2x market moves"
            })
        
        # Calculate correlations
        tickers = list(position_values.keys())
        correlation_issues = []
        
        if len(tickers) >= 2:
            for i, t1 in enumerate(tickers):
                for t2 in tickers[i+1:]:
                    corr = self.correlator.get_correlation(t1, t2)
                    if corr >= CorrelatorConfig.EXTREME_CORRELATION:
                        correlation_issues.append({
                            "pair": f"{t1}/{t2}",
                            "correlation": corr,
                            "severity": "high"
                        })
                    elif corr >= CorrelatorConfig.HIGH_CORRELATION:
                        correlation_issues.append({
                            "pair": f"{t1}/{t2}",
                            "correlation": corr,
                            "severity": "medium"
                        })
        
        for issue in correlation_issues:
            warnings.append({
                "type": "correlation",
                "severity": issue["severity"],
                "message": f"⚠️ HIGH CORRELATION: {issue['pair']} = {issue['correlation']:.2f}"
            })
        
        return {
            "portfolio_value": portfolio_value,
            "positions": position_values,
            "sector_exposure": dict(sector_exposure),
            "theme_exposure": dict(theme_exposure),
            "portfolio_beta": weighted_beta,
            "warnings": warnings,
            "correlation_issues": correlation_issues,
            "recommendations": self._generate_recommendations(
                sector_exposure, theme_exposure, weighted_beta, warnings
            )
        }
    
    def _generate_recommendations(self, sector_exp, theme_exp, beta, warnings) -> List[str]:
        """Generate portfolio recommendations"""
        recs = []
        
        # Find underweight sectors
        all_sectors = set(SECTOR_INFO.keys())
        current_sectors = set(sector_exp.keys())
        missing_sectors = all_sectors - current_sectors
        
        # Recommend uncorrelated diversification
        if "speculative_tech" in theme_exp and theme_exp["speculative_tech"] > 30:
            if "traditional" not in theme_exp or theme_exp["traditional"] < 10:
                recs.append("💡 Consider adding traditional sectors (financials, energy) for diversification")
        
        if beta > 1.5:
            recs.append("💡 Portfolio is high-beta. Add lower-beta holdings to reduce volatility")
        
        # Sector-specific suggestions
        if "nuclear" in sector_exp and sector_exp["nuclear"] > 25:
            if "tech" not in sector_exp or sector_exp["tech"] < 10:
                recs.append("💡 Heavy nuclear exposure - consider big tech for stability")
        
        if "quantum" in sector_exp and sector_exp["quantum"] > 20:
            recs.append("💡 Quantum is highly correlated internally - treat as single position")
        
        if not warnings:
            recs.append("✅ Portfolio diversification looks reasonable")
        
        return recs
    
    # ========================================
    # NEW POSITION CHECK
    # ========================================
    
    def check_new_position(self, ticker: str, proposed_value: float = None) -> dict:
        """Check how adding a position would affect portfolio"""
        ticker = ticker.upper()
        positions = self.positions.load_positions()
        
        # Get ticker info
        sector = TICKER_SECTORS.get(ticker, "other")
        sector_info = SECTOR_INFO.get(sector, {"name": sector, "risk": "unknown", "beta": 1.0})
        
        result = {
            "ticker": ticker,
            "sector": sector,
            "sector_name": sector_info["name"],
            "sector_risk": sector_info["risk"],
            "sector_beta": sector_info["beta"],
            "warnings": [],
            "correlations": [],
            "recommendation": ""
        }
        
        if not positions:
            result["recommendation"] = "✅ First position - no correlation concerns"
            return result
        
        # Current portfolio analysis
        analysis = self.analyze_portfolio()
        current_sector_exp = analysis.get("sector_exposure", {})
        
        # Check sector concentration
        if sector in current_sector_exp:
            new_exposure = current_sector_exp[sector]
            if new_exposure >= CorrelatorConfig.MAX_SECTOR_PCT:
                result["warnings"].append({
                    "type": "concentration",
                    "message": f"⚠️ Already {new_exposure:.1f}% in {sector_info['name']} - adding more increases risk"
                })
        
        # Check correlations with existing positions
        high_corr_positions = []
        
        for existing_ticker in positions.keys():
            corr = self.correlator.get_correlation(ticker, existing_ticker)
            result["correlations"].append({
                "ticker": existing_ticker,
                "correlation": corr
            })
            
            if corr >= CorrelatorConfig.HIGH_CORRELATION:
                high_corr_positions.append({
                    "ticker": existing_ticker,
                    "correlation": corr
                })
        
        if high_corr_positions:
            for hc in high_corr_positions:
                if hc["correlation"] >= CorrelatorConfig.EXTREME_CORRELATION:
                    result["warnings"].append({
                        "type": "correlation",
                        "message": f"🚨 EXTREME correlation with {hc['ticker']}: {hc['correlation']:.2f} - essentially same position"
                    })
                else:
                    result["warnings"].append({
                        "type": "correlation",
                        "message": f"⚠️ High correlation with {hc['ticker']}: {hc['correlation']:.2f}"
                    })
        
        # Generate recommendation
        if any(w["type"] == "correlation" and "EXTREME" in w["message"] for w in result["warnings"]):
            result["recommendation"] = "🔴 AVOID: Essentially duplicates existing position"
        elif len(result["warnings"]) >= 2:
            result["recommendation"] = "🟡 CAUTION: Consider smaller position size"
        elif len(result["warnings"]) == 1:
            result["recommendation"] = "🟡 PROCEED WITH CAUTION: Be aware of concentration"
        else:
            result["recommendation"] = "🟢 GOOD: Adds diversification to portfolio"
        
        return result
    
    # ========================================
    # SUGGESTIONS
    # ========================================
    
    def suggest_diversification(self) -> dict:
        """Suggest tickers for diversification"""
        positions = self.positions.load_positions()
        
        if not positions:
            return {"error": "No positions to diversify from."}
        
        # Get current sectors
        current_sectors = set()
        for pos in positions.values():
            current_sectors.add(pos.get("sector", "other"))
        
        # Find underrepresented sectors
        all_sectors = set(SECTOR_INFO.keys())
        missing_sectors = all_sectors - current_sectors
        
        suggestions = []
        
        for sector in missing_sectors:
            sector_info = SECTOR_INFO.get(sector, {})
            
            # Find representative tickers
            sector_tickers = [t for t, s in TICKER_SECTORS.items() if s == sector][:3]
            
            suggestions.append({
                "sector": sector,
                "sector_name": sector_info.get("name", sector),
                "risk": sector_info.get("risk", "unknown"),
                "tickers": sector_tickers,
                "reason": f"No exposure to {sector_info.get('name', sector)}"
            })
        
        # Sort by risk (lower risk first for diversification)
        risk_order = {"low": 0, "medium": 1, "high": 2, "extreme": 3, "unknown": 4}
        suggestions.sort(key=lambda x: risk_order.get(x["risk"], 4))
        
        return {
            "current_sectors": list(current_sectors),
            "suggestions": suggestions[:5],
            "message": f"Consider adding exposure to uncorrelated sectors"
        }


# ============================================================
# CLI & DISPLAY
# ============================================================

def display_portfolio(analysis: dict):
    """Display portfolio analysis"""
    print("=" * 70)
    print("🐺 WOLF CORRELATOR - Portfolio Risk Analysis")
    print("=" * 70)
    
    if "error" in analysis:
        print(f"\n{analysis['error']}")
        return
    
    print(f"\n💰 PORTFOLIO VALUE: ${analysis['portfolio_value']:,.2f}")
    print(f"📊 PORTFOLIO BETA: {analysis['portfolio_beta']:.2f}")
    print()
    
    # Positions
    print("POSITIONS:")
    print("-" * 70)
    print(f"{'Ticker':<8} {'Shares':>10} {'Entry':>10} {'Current':>10} {'Value':>12} {'P&L':>8} {'Alloc':>7}")
    print("-" * 70)
    
    for ticker, data in analysis["positions"].items():
        print(f"{ticker:<8} {data['shares']:>10,.0f} ${data['entry_price']:>8.2f} ${data['current_price']:>8.2f} "
              f"${data['value']:>10,.0f} {data['pnl_pct']:>+7.1f}% {data['portfolio_pct']:>6.1f}%")
    
    # Sector exposure
    print(f"\n📈 SECTOR EXPOSURE:")
    print("-" * 40)
    
    for sector, pct in sorted(analysis["sector_exposure"].items(), key=lambda x: x[1], reverse=True):
        sector_name = SECTOR_INFO.get(sector, {}).get("name", sector)
        bar = "█" * int(pct / 2)
        print(f"  {sector_name:20s} {pct:5.1f}% {bar}")
    
    # Theme exposure
    print(f"\n🎯 THEME EXPOSURE:")
    print("-" * 40)
    
    for theme, pct in sorted(analysis["theme_exposure"].items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(pct / 2)
        print(f"  {theme:20s} {pct:5.1f}% {bar}")
    
    # Warnings
    if analysis["warnings"]:
        print(f"\n⚠️ WARNINGS:")
        print("-" * 40)
        for warning in analysis["warnings"]:
            print(f"  {warning['message']}")
    
    # Recommendations
    if analysis["recommendations"]:
        print(f"\n💡 RECOMMENDATIONS:")
        print("-" * 40)
        for rec in analysis["recommendations"]:
            print(f"  {rec}")
    
    print()
    print("=" * 70)


def display_position_check(check: dict):
    """Display new position check results"""
    print("=" * 60)
    print(f"🐺 POSITION CHECK: {check['ticker']}")
    print("=" * 60)
    
    print(f"\n📊 Sector: {check['sector_name']}")
    print(f"   Risk Level: {check['sector_risk']}")
    print(f"   Sector Beta: {check['sector_beta']}")
    
    if check["correlations"]:
        print(f"\n🔗 CORRELATIONS WITH CURRENT HOLDINGS:")
        print("-" * 40)
        for corr in sorted(check["correlations"], key=lambda x: x["correlation"], reverse=True):
            level = "🔴" if corr["correlation"] >= 0.85 else "🟡" if corr["correlation"] >= 0.7 else "🟢"
            print(f"  {level} {corr['ticker']:8s} {corr['correlation']:+.2f}")
    
    if check["warnings"]:
        print(f"\n⚠️ WARNINGS:")
        print("-" * 40)
        for warning in check["warnings"]:
            print(f"  {warning['message']}")
    
    print(f"\n📋 RECOMMENDATION: {check['recommendation']}")
    print()
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="🐺 Wolf Correlator - Portfolio risk intelligence"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Portfolio command
    portfolio_parser = subparsers.add_parser("portfolio", help="Manage/analyze portfolio")
    portfolio_parser.add_argument("--add", type=str, help="Add position: TICKER:SHARES:PRICE")
    portfolio_parser.add_argument("--remove", type=str, help="Remove position: TICKER")
    portfolio_parser.add_argument("--list", action="store_true", help="List positions")
    portfolio_parser.add_argument("--analyze", action="store_true", help="Full analysis")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check new position")
    check_parser.add_argument("ticker", type=str, help="Ticker to check")
    
    # Suggest command
    suggest_parser = subparsers.add_parser("suggest", help="Get diversification suggestions")
    
    # Correlation command
    corr_parser = subparsers.add_parser("correlation", help="Get correlation between tickers")
    corr_parser.add_argument("ticker1", type=str, help="First ticker")
    corr_parser.add_argument("ticker2", type=str, help="Second ticker")
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Load demo portfolio")
    
    args = parser.parse_args()
    
    correlator = WolfCorrelator()
    
    if args.command == "portfolio":
        if args.add:
            parts = args.add.upper().split(":")
            ticker = parts[0]
            shares = float(parts[1])
            price = float(parts[2])
            correlator.positions.add_position(ticker, shares, price)
        
        elif args.remove:
            correlator.positions.remove_position(args.remove.upper())
        
        elif args.list:
            positions = correlator.positions.load_positions()
            if positions:
                print("\n📋 Current Positions:")
                print("-" * 40)
                for ticker, data in positions.items():
                    print(f"  {ticker}: {data['shares']} shares @ ${data['entry_price']:.2f} ({data.get('sector', 'other')})")
            else:
                print("No positions loaded.")
        
        elif args.analyze:
            analysis = correlator.analyze_portfolio()
            display_portfolio(analysis)
        
        else:
            # Default: show analysis
            analysis = correlator.analyze_portfolio()
            display_portfolio(analysis)
    
    elif args.command == "check":
        check = correlator.check_new_position(args.ticker)
        display_position_check(check)
    
    elif args.command == "suggest":
        suggestions = correlator.suggest_diversification()
        
        if "error" in suggestions:
            print(suggestions["error"])
        else:
            print("\n🐺 DIVERSIFICATION SUGGESTIONS")
            print("=" * 50)
            print(f"\nCurrent sectors: {', '.join(suggestions['current_sectors'])}")
            print(f"\n{suggestions['message']}\n")
            
            for s in suggestions["suggestions"]:
                print(f"📊 {s['sector_name']} ({s['risk']} risk)")
                print(f"   Tickers: {', '.join(s['tickers'])}")
                print(f"   Reason: {s['reason']}")
                print()
    
    elif args.command == "correlation":
        calc = CorrelationCalculator()
        corr = calc.get_correlation(args.ticker1.upper(), args.ticker2.upper())
        
        level = "🔴 EXTREME" if corr >= 0.85 else "🟡 HIGH" if corr >= 0.7 else "🟢 MODERATE" if corr >= 0.5 else "⚪ LOW"
        print(f"\n🔗 Correlation: {args.ticker1.upper()} ↔ {args.ticker2.upper()}")
        print(f"   Correlation: {corr:+.3f}")
        print(f"   Level: {level}")
    
    elif args.command == "demo":
        # Load demo portfolio
        print("📥 Loading demo portfolio...")
        
        demo_positions = [
            ("IONQ", 500, 35.00, "quantum"),
            ("RGTI", 1000, 12.50, "quantum"),
            ("NNE", 200, 28.00, "nuclear"),
            ("OKLO", 300, 22.00, "nuclear"),
            ("SOUN", 800, 8.50, "voice_ai"),
            ("MARA", 400, 18.00, "crypto"),
            ("ARM", 100, 145.00, "ai_chips")
        ]
        
        for ticker, shares, price, sector in demo_positions:
            correlator.positions.add_position(ticker, shares, price, sector)
        
        print("\n✅ Demo portfolio loaded!")
        
        # Run analysis
        analysis = correlator.analyze_portfolio()
        display_portfolio(analysis)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
