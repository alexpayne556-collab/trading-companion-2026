#!/usr/bin/env python3
"""
🐺 WOLF GAMMA - The Squeeze Predictor
======================================
Read the options chain. See the squeeze BEFORE it happens.

THE MECHANICS:
When calls cluster at a strike, MMs sell those calls.
To hedge, MMs BUY shares.
More buying → price rises → more calls go ITM → more hedging → GAMMA SQUEEZE.

We can SEE this building:
- Heavy call open interest at specific strikes
- Call/put ratio skewing bullish
- Near-term expiry concentration (gamma highest)
- OI increasing (new positions, not closing)

This is not prediction. This is PHYSICS. MMs MUST hedge.

AWOOOO 🐺
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yfinance as yf
import pandas as pd
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================

class GammaConfig:
    """Gamma scanner settings"""
    
    OUTPUT_FILE = "logs/gamma_scan.json"
    
    # Squeeze thresholds
    CALL_PUT_RATIO_BULLISH = 2.0      # 2:1 calls to puts = bullish
    CALL_PUT_RATIO_EXTREME = 5.0      # 5:1 = squeeze potential
    
    OI_CONCENTRATION_THRESHOLD = 0.3   # 30% OI at one strike = pinning risk
    
    # Gamma exposure thresholds
    HIGH_GAMMA_THRESHOLD = 0.5         # Relative gamma score


# ============================================================
# GAMMA SCANNER
# ============================================================

class GammaScanner:
    """
    Scan options chains for gamma squeeze setups.
    
    What we look for:
    1. High call/put ratio (bullish positioning)
    2. Call OI clustering at specific strikes (pin/magnet)
    3. Near-term expiry concentration (max gamma)
    4. Price approaching high-OI strikes (trigger zone)
    5. Rising OI (new bets, not closing)
    """
    
    def __init__(self):
        self.results = []
    
    def scan_ticker(self, ticker: str) -> Optional[dict]:
        """Full gamma analysis for a single ticker"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get current price
            info = stock.info
            current_price = info.get("regularMarketPrice") or info.get("currentPrice", 0)
            
            if current_price == 0:
                hist = stock.history(period="1d")
                if not hist.empty:
                    if isinstance(hist.columns, pd.MultiIndex):
                        hist.columns = hist.columns.get_level_values(0)
                    current_price = hist["Close"].iloc[-1]
            
            if current_price == 0:
                return None
            
            # Get options expirations
            expirations = stock.options
            if not expirations:
                return None
            
            # Focus on near-term (highest gamma) - first 3 expirations
            near_term_exps = expirations[:3]
            
            all_calls = []
            all_puts = []
            
            for exp in near_term_exps:
                try:
                    opt = stock.option_chain(exp)
                    
                    calls = opt.calls.copy()
                    calls["expiration"] = exp
                    calls["days_to_exp"] = (datetime.strptime(exp, "%Y-%m-%d") - datetime.now()).days
                    
                    puts = opt.puts.copy()
                    puts["expiration"] = exp
                    puts["days_to_exp"] = (datetime.strptime(exp, "%Y-%m-%d") - datetime.now()).days
                    
                    all_calls.append(calls)
                    all_puts.append(puts)
                except Exception:
                    pass
            
            if not all_calls:
                return None
            
            calls_df = pd.concat(all_calls, ignore_index=True)
            puts_df = pd.concat(all_puts, ignore_index=True)
            
            # Calculate metrics
            analysis = self._analyze_chain(ticker, current_price, calls_df, puts_df)
            
            return analysis
            
        except Exception as e:
            return None
    
    def _analyze_chain(self, ticker: str, current_price: float, 
                       calls: pd.DataFrame, puts: pd.DataFrame) -> dict:
        """Analyze options chain for gamma squeeze potential"""
        
        # 1. Call/Put Ratio
        total_call_oi = calls["openInterest"].sum()
        total_put_oi = puts["openInterest"].sum()
        call_put_ratio = total_call_oi / total_put_oi if total_put_oi > 0 else 0
        
        # 2. Call/Put Volume Ratio (today's activity)
        total_call_vol = calls["volume"].sum()
        total_put_vol = puts["volume"].sum()
        vol_ratio = total_call_vol / total_put_vol if total_put_vol > 0 else 0
        
        # 3. Find high-OI strikes (gamma magnets)
        call_oi_by_strike = calls.groupby("strike")["openInterest"].sum()
        max_call_oi_strike = call_oi_by_strike.idxmax() if len(call_oi_by_strike) > 0 else 0
        max_call_oi = call_oi_by_strike.max() if len(call_oi_by_strike) > 0 else 0
        
        # OI concentration at max strike
        oi_concentration = max_call_oi / total_call_oi if total_call_oi > 0 else 0
        
        # 4. Find "gamma wall" - strikes with heavy OI near current price
        nearby_strikes = calls[
            (calls["strike"] >= current_price * 0.9) & 
            (calls["strike"] <= current_price * 1.2)
        ]
        
        gamma_wall_strike = None
        gamma_wall_oi = 0
        
        if len(nearby_strikes) > 0:
            strike_oi = nearby_strikes.groupby("strike")["openInterest"].sum()
            if len(strike_oi) > 0:
                gamma_wall_strike = strike_oi.idxmax()
                gamma_wall_oi = strike_oi.max()
        
        # 5. Distance to gamma wall
        distance_to_wall = 0
        if gamma_wall_strike and current_price > 0:
            distance_to_wall = (gamma_wall_strike - current_price) / current_price * 100
        
        # 6. Near-term gamma concentration
        nearest_exp_calls = calls[calls["days_to_exp"] <= 7]
        near_term_oi = nearest_exp_calls["openInterest"].sum()
        near_term_ratio = near_term_oi / total_call_oi if total_call_oi > 0 else 0
        
        # 7. ITM call ratio (already hedged)
        itm_calls = calls[calls["strike"] < current_price]
        itm_oi = itm_calls["openInterest"].sum()
        itm_ratio = itm_oi / total_call_oi if total_call_oi > 0 else 0
        
        # 8. OTM call concentration (potential fuel)
        otm_calls = calls[(calls["strike"] > current_price) & 
                          (calls["strike"] < current_price * 1.3)]
        otm_oi = otm_calls["openInterest"].sum()
        
        # SCORING
        gamma_score = 0
        signals = []
        
        # Call/put ratio scoring
        if call_put_ratio >= GammaConfig.CALL_PUT_RATIO_EXTREME:
            gamma_score += 30
            signals.append(f"🔥 EXTREME call/put ratio: {call_put_ratio:.1f}:1")
        elif call_put_ratio >= GammaConfig.CALL_PUT_RATIO_BULLISH:
            gamma_score += 15
            signals.append(f"📈 Bullish call/put ratio: {call_put_ratio:.1f}:1")
        
        # Volume ratio (today's action)
        if vol_ratio >= 3.0:
            gamma_score += 20
            signals.append(f"⚡ Heavy call buying today: {vol_ratio:.1f}:1 volume ratio")
        elif vol_ratio >= 2.0:
            gamma_score += 10
            signals.append(f"📊 Elevated call volume: {vol_ratio:.1f}:1")
        
        # Gamma wall proximity
        if gamma_wall_strike and 0 < distance_to_wall < 10:
            gamma_score += 25
            signals.append(f"🎯 Gamma wall at ${gamma_wall_strike:.2f} ({distance_to_wall:+.1f}% away)")
            signals.append(f"   Wall OI: {gamma_wall_oi:,} contracts")
        elif gamma_wall_strike and -5 < distance_to_wall <= 0:
            gamma_score += 15
            signals.append(f"📍 At gamma wall ${gamma_wall_strike:.2f}")
        
        # Near-term concentration (high gamma)
        if near_term_ratio > 0.4:
            gamma_score += 20
            signals.append(f"⏰ {near_term_ratio*100:.0f}% OI expires within 7 days (MAX GAMMA)")
        elif near_term_ratio > 0.25:
            gamma_score += 10
            signals.append(f"📅 {near_term_ratio*100:.0f}% near-term OI")
        
        # OTM fuel
        if otm_oi > total_call_oi * 0.5:
            gamma_score += 15
            signals.append(f"🚀 Heavy OTM call OI: {otm_oi:,} contracts (squeeze fuel)")
        
        # Determine squeeze potential
        squeeze_potential = "LOW"
        if gamma_score >= 70:
            squeeze_potential = "HIGH"
        elif gamma_score >= 50:
            squeeze_potential = "MEDIUM"
        elif gamma_score >= 30:
            squeeze_potential = "ELEVATED"
        
        # Build result
        result = {
            "ticker": ticker,
            "current_price": current_price,
            "gamma_score": gamma_score,
            "squeeze_potential": squeeze_potential,
            
            "metrics": {
                "call_put_ratio": round(call_put_ratio, 2),
                "volume_ratio": round(vol_ratio, 2),
                "total_call_oi": int(total_call_oi),
                "total_put_oi": int(total_put_oi),
                "gamma_wall_strike": gamma_wall_strike,
                "gamma_wall_oi": int(gamma_wall_oi) if gamma_wall_oi else 0,
                "distance_to_wall_pct": round(distance_to_wall, 2),
                "near_term_oi_pct": round(near_term_ratio * 100, 1),
                "otm_call_oi": int(otm_oi)
            },
            
            "signals": signals,
            
            "action": self._get_action(gamma_score, distance_to_wall, squeeze_potential),
            
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def _get_action(self, score: int, distance: float, potential: str) -> str:
        """Generate action recommendation"""
        if potential == "HIGH" and 0 < distance < 5:
            return "🚨 SQUEEZE IMMINENT - Price approaching gamma wall. Watch for acceleration."
        elif potential == "HIGH":
            return "👀 WATCH CLOSELY - High squeeze potential. Wait for price to approach wall."
        elif potential == "MEDIUM" and 0 < distance < 10:
            return "📊 BUILDING - Gamma setup forming. Add to watchlist."
        elif potential == "ELEVATED":
            return "📋 MONITOR - Some gamma buildup. Not actionable yet."
        else:
            return "⏸️ NO SETUP - Insufficient gamma concentration."
    
    def scan_universe(self, tickers: List[str]) -> List[dict]:
        """Scan multiple tickers for gamma setups"""
        print("=" * 70)
        print("🐺 WOLF GAMMA - Scanning for Squeeze Setups")
        print("=" * 70)
        print()
        
        results = []
        
        for i, ticker in enumerate(tickers):
            print(f"  [{i+1}/{len(tickers)}] Scanning {ticker}...", end=" ")
            
            try:
                analysis = self.scan_ticker(ticker)
                
                if analysis and analysis["gamma_score"] >= 30:
                    results.append(analysis)
                    print(f"🎯 Score: {analysis['gamma_score']} ({analysis['squeeze_potential']})")
                else:
                    print("No setup")
            except Exception as e:
                print(f"Error: {e}")
        
        # Sort by score
        results.sort(key=lambda x: x["gamma_score"], reverse=True)
        
        # Save results
        output = {
            "scan_time": datetime.now().isoformat(),
            "tickers_scanned": len(tickers),
            "setups_found": len(results),
            "results": results
        }
        
        output_file = Path(GammaConfig.OUTPUT_FILE)
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)
        
        return results


# ============================================================
# GAMMA MAP VISUALIZER
# ============================================================

def display_gamma_map(ticker: str):
    """Display detailed gamma map for a ticker"""
    scanner = GammaScanner()
    analysis = scanner.scan_ticker(ticker)
    
    if not analysis:
        print(f"Could not analyze {ticker}")
        return
    
    print()
    print("=" * 70)
    print(f"🐺 GAMMA MAP: {ticker}")
    print("=" * 70)
    print()
    
    print(f"📊 Current Price: ${analysis['current_price']:.2f}")
    print(f"🎯 Gamma Score: {analysis['gamma_score']}/100")
    print(f"💥 Squeeze Potential: {analysis['squeeze_potential']}")
    print()
    
    print("SIGNALS:")
    print("-" * 50)
    for signal in analysis["signals"]:
        print(f"  {signal}")
    print()
    
    print("METRICS:")
    print("-" * 50)
    metrics = analysis["metrics"]
    print(f"  Call/Put Ratio:     {metrics['call_put_ratio']:.1f}:1")
    print(f"  Volume Ratio:       {metrics['volume_ratio']:.1f}:1")
    print(f"  Total Call OI:      {metrics['total_call_oi']:,}")
    print(f"  Total Put OI:       {metrics['total_put_oi']:,}")
    print(f"  Gamma Wall:         ${metrics['gamma_wall_strike']:.2f} ({metrics['distance_to_wall_pct']:+.1f}%)")
    print(f"  Wall OI:            {metrics['gamma_wall_oi']:,}")
    print(f"  Near-term OI:       {metrics['near_term_oi_pct']:.0f}%")
    print(f"  OTM Call Fuel:      {metrics['otm_call_oi']:,}")
    print()
    
    print("ACTION:")
    print("-" * 50)
    print(f"  {analysis['action']}")
    print()
    print("=" * 70)
    
    return analysis


# ============================================================
# CLI
# ============================================================

def get_default_universe():
    """High-volatility universe for gamma scanning"""
    return [
        # Quantum (high gamma potential)
        "IONQ", "RGTI", "QBTS",
        # Nuclear  
        "NNE", "OKLO", "SMR",
        # Meme/Squeeze candidates
        "GME", "AMC", "BBBY",
        # High short interest
        "CVNA", "UPST", "AFRM",
        # Speculative tech
        "SOUN", "MARA", "RIOT",
        # EV
        "LCID", "RIVN",
        # Space
        "RKLB",
        # AI
        "ARM", "SMCI"
    ]


def main():
    parser = argparse.ArgumentParser(
        description="🐺 Wolf Gamma - Options chain squeeze detector"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan universe for gamma setups")
    scan_parser.add_argument("--tickers", type=str, help="Comma-separated tickers")
    
    # Map command (single ticker deep dive)
    map_parser = subparsers.add_parser("map", help="Detailed gamma map for single ticker")
    map_parser.add_argument("ticker", type=str, help="Ticker to analyze")
    
    # Top command (show top setups)
    top_parser = subparsers.add_parser("top", help="Show top gamma setups from last scan")
    top_parser.add_argument("--n", type=int, default=5, help="Number of results")
    
    args = parser.parse_args()
    
    if args.command == "scan":
        tickers = args.tickers.split(",") if args.tickers else get_default_universe()
        scanner = GammaScanner()
        results = scanner.scan_universe(tickers)
        
        print()
        print("=" * 70)
        print(f"📊 GAMMA SCAN COMPLETE - {len(results)} setups found")
        print("=" * 70)
        
        for r in results[:5]:
            potential_icon = "🔥" if r["squeeze_potential"] == "HIGH" else "⚡" if r["squeeze_potential"] == "MEDIUM" else "📊"
            print(f"\n{potential_icon} {r['ticker']} - Score: {r['gamma_score']} ({r['squeeze_potential']})")
            print(f"   Price: ${r['current_price']:.2f}")
            print(f"   C/P Ratio: {r['metrics']['call_put_ratio']:.1f}:1")
            if r['metrics']['gamma_wall_strike']:
                print(f"   Gamma Wall: ${r['metrics']['gamma_wall_strike']:.2f} ({r['metrics']['distance_to_wall_pct']:+.1f}%)")
            print(f"   {r['action']}")
    
    elif args.command == "map":
        display_gamma_map(args.ticker.upper())
    
    elif args.command == "top":
        output_file = Path(GammaConfig.OUTPUT_FILE)
        if output_file.exists():
            with open(output_file) as f:
                data = json.load(f)
            
            print(f"\n🐺 TOP {args.n} GAMMA SETUPS (from {data['scan_time'][:10]})")
            print("=" * 60)
            
            for r in data["results"][:args.n]:
                print(f"\n{r['ticker']} - Score: {r['gamma_score']} ({r['squeeze_potential']})")
                for sig in r["signals"][:2]:
                    print(f"  {sig}")
        else:
            print("No scan data. Run 'python wolf_gamma.py scan' first.")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
