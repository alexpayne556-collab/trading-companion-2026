#!/usr/bin/env python3
"""
🐺 LAGGARD HUNTER - Find Tomorrow's Winners Before the Crowd
============================================================

FENRIR'S FRAMEWORK (now weaponized):
- Leaders prove the thesis
- Laggards capture the overflow
- Position BEFORE the crowd discovers them

THE EDGE:
When NVDA runs 180%, the crowd buys NVDA.
Smart money buys what powers NVDA (nuclear, cooling, infrastructure).
THE PACK buys the laggard in that supply chain.

USAGE:
    python laggard_hunter.py                    # Full scan all sectors
    python laggard_hunter.py --sector nuclear   # Scan specific sector
    python laggard_hunter.py --watchlist        # Show watchlist only
"""

import argparse
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
import json

# Comprehensive sector mappings with ALL stocks
SECTOR_STOCKS = {
    "nuclear": {
        "tickers": ["SMR", "OKLO", "UUUU", "CCJ", "DNN", "NNE", "LEU", "UEC", "URG", "URNM"],
        "thesis": "AI power demand → Nuclear renaissance",
        "leader_threshold": 100,  # % gain to be considered "leader"
    },
    "rare_earth": {
        "tickers": ["MP", "USAR", "AREC", "UUUU"],  # UUUU plays both
        "thesis": "Defense + EVs + AI all need rare earths",
        "leader_threshold": 100,
    },
    "quantum": {
        "tickers": ["IONQ", "QBTS", "QUBT", "RGTI", "ARQQ"],
        "thesis": "Quantum computing hype cycle + CES catalyst",
        "leader_threshold": 50,
    },
    "space": {
        "tickers": ["RKLB", "RDW", "ASTS", "LUNR", "BKSY", "SPCE", "ASTR"],
        "thesis": "Space economy boom + government contracts",
        "leader_threshold": 50,
    },
    "defense": {
        "tickers": ["LMT", "RTX", "NOC", "GD", "AISP", "KTOS", "PLTR", "AVAV"],
        "thesis": "Geopolitical tension → Defense spending",
        "leader_threshold": 30,  # Big caps move slower
    },
    "drones": {
        "tickers": ["AVAV", "UAVS", "KTOS", "JOBY", "ACHR", "AISP"],
        "thesis": "Ukraine war proved drone dominance",
        "leader_threshold": 50,
    },
    "ai_infrastructure": {
        "tickers": ["NVDA", "AMD", "VRT", "ET", "AA", "SMCI", "DELL", "CEG", "VST"],
        "thesis": "AI needs: chips, cooling, power, aluminum",
        "leader_threshold": 80,
    },
    "crypto_fintech": {
        "tickers": ["COIN", "MSTR", "RIOT", "MARA", "CLSK", "HUT", "BITF", "SQ", "HOOD"],
        "thesis": "Crypto cycle + fintech disruption",
        "leader_threshold": 80,
    },
}


def get_stock_performance(ticker: str, days: int = 90) -> dict:
    """Get stock performance metrics."""
    try:
        stock = yf.Ticker(ticker)
        
        # Get price history
        end = datetime.now()
        start = end - timedelta(days=days + 10)  # Extra buffer
        hist = stock.history(start=start, end=end)
        
        if hist.empty or len(hist) < 5:
            return None
        
        current = hist['Close'].iloc[-1]
        
        # Calculate returns for different periods
        returns = {}
        for period_name, period_days in [("1w", 5), ("1m", 21), ("3m", 63), ("ytd", days)]:
            if len(hist) >= period_days:
                past_price = hist['Close'].iloc[-period_days]
                returns[period_name] = ((current - past_price) / past_price) * 100
            else:
                returns[period_name] = 0
        
        # Get recent volume vs average
        recent_vol = hist['Volume'].iloc[-5:].mean()
        avg_vol = hist['Volume'].mean()
        vol_ratio = recent_vol / avg_vol if avg_vol > 0 else 1
        
        # Get market cap
        info = stock.info
        market_cap = info.get('marketCap', 0)
        market_cap_str = f"${market_cap/1e9:.1f}B" if market_cap > 1e9 else f"${market_cap/1e6:.0f}M"
        
        return {
            "ticker": ticker,
            "price": round(current, 2),
            "market_cap": market_cap,
            "market_cap_str": market_cap_str,
            "return_1w": round(returns.get("1w", 0), 2),
            "return_1m": round(returns.get("1m", 0), 2),
            "return_3m": round(returns.get("3m", 0), 2),
            "return_ytd": round(returns.get("ytd", 0), 2),
            "vol_ratio": round(vol_ratio, 2),
        }
    except Exception as e:
        print(f"  ⚠️  Error fetching {ticker}: {e}")
        return None


def classify_stock(perf: dict, leader_threshold: float) -> str:
    """Classify stock as LEADER, MID, or LAGGARD."""
    ytd_return = perf.get("return_3m", 0)  # Using 3-month as proxy
    
    if ytd_return >= leader_threshold:
        return "🔴 LEADER"
    elif ytd_return >= leader_threshold * 0.5:
        return "🟡 MID"
    else:
        return "🟢 LAGGARD"


def calculate_laggard_score(perf: dict, sector_avg: float, leader_return: float) -> float:
    """
    Calculate laggard opportunity score (0-100).
    Higher = better laggard opportunity.
    
    Factors:
    - Gap from leader (bigger gap = more room to run)
    - Recent momentum (starting to move = good)
    - Volume increase (attention building)
    - Price accessibility (under $20 = bonus for small accounts)
    """
    score = 0
    
    # Gap from leader (40 points max)
    if leader_return > 0:
        gap = leader_return - perf["return_3m"]
        gap_score = min(40, (gap / leader_return) * 40)
        score += gap_score
    
    # Recent momentum - 1 week (20 points max)
    # Positive but not crazy = good (starting to move)
    if 0 < perf["return_1w"] < 15:
        score += 20
    elif perf["return_1w"] >= 15:
        score += 10  # Already moving, less upside
    elif -5 < perf["return_1w"] < 0:
        score += 15  # Slight dip = entry opportunity
    
    # Volume ratio (20 points max)
    if perf["vol_ratio"] > 2:
        score += 20  # Attention building
    elif perf["vol_ratio"] > 1.5:
        score += 15
    elif perf["vol_ratio"] > 1:
        score += 10
    
    # Price accessibility (20 points max)
    if perf["price"] < 10:
        score += 20  # Very accessible for small accounts
    elif perf["price"] < 20:
        score += 15
    elif perf["price"] < 50:
        score += 10
    elif perf["price"] < 100:
        score += 5
    
    return round(score, 1)


def analyze_sector(sector_name: str) -> dict:
    """Analyze a sector and find laggard opportunities."""
    if sector_name not in SECTOR_STOCKS:
        print(f"❌ Unknown sector: {sector_name}")
        return None
    
    sector = SECTOR_STOCKS[sector_name]
    print(f"\n{'='*60}")
    print(f"🔍 ANALYZING: {sector_name.upper()}")
    print(f"📊 Thesis: {sector['thesis']}")
    print(f"{'='*60}")
    
    stocks = []
    for ticker in sector["tickers"]:
        perf = get_stock_performance(ticker)
        if perf:
            perf["status"] = classify_stock(perf, sector["leader_threshold"])
            stocks.append(perf)
    
    if not stocks:
        print("  ❌ No data available")
        return None
    
    # Sort by 3-month return to identify leader
    stocks.sort(key=lambda x: x["return_3m"], reverse=True)
    leader = stocks[0]
    leader_return = leader["return_3m"]
    
    # Calculate sector average
    sector_avg = sum(s["return_3m"] for s in stocks) / len(stocks)
    
    # Calculate laggard scores
    for stock in stocks:
        stock["laggard_score"] = calculate_laggard_score(stock, sector_avg, leader_return)
    
    # Sort by laggard score for final output
    laggards = [s for s in stocks if "LAGGARD" in s["status"]]
    laggards.sort(key=lambda x: x["laggard_score"], reverse=True)
    
    # Print results
    print(f"\n🏆 LEADER: {leader['ticker']} (+{leader['return_3m']:.1f}% in 3mo)")
    print(f"📈 Sector Avg: +{sector_avg:.1f}%")
    print(f"\n{'─'*60}")
    print(f"{'TICKER':<8} {'PRICE':>8} {'3MO':>8} {'1WK':>8} {'VOL':>6} {'STATUS':<12} {'SCORE':>6}")
    print(f"{'─'*60}")
    
    for stock in stocks:
        print(f"{stock['ticker']:<8} ${stock['price']:>7.2f} {stock['return_3m']:>+7.1f}% {stock['return_1w']:>+7.1f}% {stock['vol_ratio']:>5.1f}x {stock['status']:<12} {stock['laggard_score']:>5.0f}")
    
    # Top laggard opportunities
    if laggards:
        print(f"\n{'='*60}")
        print("🎯 TOP LAGGARD OPPORTUNITIES:")
        print(f"{'='*60}")
        
        for i, lag in enumerate(laggards[:3], 1):
            gap_from_leader = leader_return - lag["return_3m"]
            print(f"\n#{i} {lag['ticker']} (Score: {lag['laggard_score']})")
            print(f"   Price: ${lag['price']:.2f} | MCap: {lag['market_cap_str']}")
            print(f"   Gap from leader: +{gap_from_leader:.1f}% room to run")
            print(f"   1-week momentum: {lag['return_1w']:+.1f}%")
            print(f"   Volume: {lag['vol_ratio']:.1f}x normal")
            
            # Entry suggestion
            if lag['return_1w'] > 10:
                print(f"   ⚠️  WAIT: Already moving, look for pullback")
            elif lag['return_1w'] < -5:
                print(f"   🟢 ACCUMULATE: Weakness in hot sector = opportunity")
            else:
                print(f"   🟢 POSITION: Good entry window")
    
    return {
        "sector": sector_name,
        "thesis": sector["thesis"],
        "leader": leader,
        "sector_avg": sector_avg,
        "stocks": stocks,
        "laggards": laggards,
    }


def full_scan():
    """Scan all sectors for laggard opportunities."""
    print("\n" + "🐺"*30)
    print("      LAGGARD HUNTER - FULL SECTOR SCAN")
    print("🐺"*30)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_laggards = []
    
    for sector_name in SECTOR_STOCKS.keys():
        result = analyze_sector(sector_name)
        if result and result.get("laggards"):
            for lag in result["laggards"]:
                lag["sector"] = sector_name
                lag["sector_thesis"] = result["thesis"]
                lag["leader"] = result["leader"]["ticker"]
                lag["leader_return"] = result["leader"]["return_3m"]
                all_laggards.append(lag)
    
    # Sort all laggards by score
    all_laggards.sort(key=lambda x: x["laggard_score"], reverse=True)
    
    # Final rankings
    print("\n" + "="*70)
    print("🏆 TOP 10 LAGGARD OPPORTUNITIES ACROSS ALL SECTORS")
    print("="*70)
    print(f"\n{'RANK':<5} {'TICKER':<8} {'SECTOR':<15} {'PRICE':>8} {'GAP':>8} {'SCORE':>6}")
    print("-"*70)
    
    for i, lag in enumerate(all_laggards[:10], 1):
        gap = lag["leader_return"] - lag["return_3m"]
        print(f"#{i:<4} {lag['ticker']:<8} {lag['sector']:<15} ${lag['price']:>7.2f} {gap:>+7.1f}% {lag['laggard_score']:>5.0f}")
    
    # Generate actionable output
    print("\n" + "="*70)
    print("🎯 ACTIONABLE PLAYS FOR TYR ($1,327 TOTAL)")
    print("="*70)
    
    # Filter for affordable opportunities (under $50)
    affordable = [l for l in all_laggards if l["price"] < 50][:5]
    
    for i, play in enumerate(affordable[:3], 1):
        gap = play["leader_return"] - play["return_3m"]
        
        # Calculate position size suggestion
        if play["laggard_score"] > 70:
            position_pct = 15  # High conviction
        elif play["laggard_score"] > 50:
            position_pct = 10  # Medium conviction
        else:
            position_pct = 5   # Speculative
        
        position_size = round(1327 * position_pct / 100)
        shares = int(position_size / play["price"])
        
        print(f"\n#{i} {play['ticker']} - {play['sector'].upper()}")
        print(f"   Thesis: {play['sector_thesis']}")
        print(f"   Leader: {play['leader']} (+{play['leader_return']:.0f}%)")
        print(f"   Gap to close: +{gap:.0f}%")
        print(f"   Entry: ${play['price']:.2f}")
        print(f"   Position: ${position_size} ({shares} shares) = {position_pct}% of portfolio")
        print(f"   Score: {play['laggard_score']}/100")
        
        # Status check
        if play['return_1w'] > 10:
            print(f"   ⚠️  Status: MOVING - wait for pullback or scale in")
        elif play['return_1w'] < -3:
            print(f"   🟢 Status: DIP - good accumulation zone")
        else:
            print(f"   🟢 Status: QUIET - ideal positioning window")
    
    # Check if Tyr already owns any top laggards
    tyr_positions = ["AISP", "UUUU", "USAR"]
    owned = [l for l in all_laggards[:10] if l["ticker"] in tyr_positions]
    
    if owned:
        print("\n" + "="*70)
        print("✅ TYR'S POSITIONS IN TOP LAGGARDS:")
        print("="*70)
        for pos in owned:
            gap = pos["leader_return"] - pos["return_3m"]
            print(f"   {pos['ticker']} - {pos['sector']} - Gap: +{gap:.0f}% - Score: {pos['laggard_score']}")
        print("\n   🐺 You're already positioned in laggards. HOLD and let them catch up.")
    
    return all_laggards


def show_watchlist():
    """Show Tyr's current watchlist based on laggard analysis."""
    print("\n" + "🐺"*30)
    print("      TYR'S LAGGARD WATCHLIST")
    print("🐺"*30)
    
    # Watchlist from Fenrir's framework
    watchlist = {
        "ET": {"sector": "AI Infrastructure", "thesis": "Data center natural gas demand", "entry_zone": "$17-18"},
        "AA": {"sector": "AI Infrastructure", "thesis": "Aluminum for data centers", "entry_zone": "$35-38"},
        "DNN": {"sector": "Nuclear/Uranium", "thesis": "Uranium supply crunch", "entry_zone": "Sector pullback"},
        "AREC": {"sector": "Rare Earth", "thesis": "Earlier stage USAR play", "entry_zone": "DoD news"},
        "MP": {"sector": "Rare Earth", "thesis": "Level 4 bottleneck (multiple sectors)", "entry_zone": "Current"},
        "CAT": {"sector": "Mining Equipment", "thesis": "Level 4 bottleneck (AI + Nuclear)", "entry_zone": "Current"},
    }
    
    print(f"\n{'TICKER':<8} {'SECTOR':<20} {'PRICE':>8} {'1WK':>8} {'STATUS':<15}")
    print("-"*70)
    
    for ticker, info in watchlist.items():
        perf = get_stock_performance(ticker)
        if perf:
            if perf["return_1w"] > 10:
                status = "⚠️ WAIT (running)"
            elif perf["return_1w"] < -3:
                status = "🟢 BUY ZONE"
            else:
                status = "🟡 WATCH"
            
            print(f"{ticker:<8} {info['sector']:<20} ${perf['price']:>7.2f} {perf['return_1w']:>+7.1f}% {status:<15}")
            print(f"         Thesis: {info['thesis']}")
            print(f"         Entry zone: {info['entry_zone']}")
            print()


def main():
    parser = argparse.ArgumentParser(description="🐺 Laggard Hunter - Find laggards in hot sectors")
    parser.add_argument("--sector", type=str, help="Analyze specific sector")
    parser.add_argument("--watchlist", action="store_true", help="Show watchlist only")
    parser.add_argument("--quick", action="store_true", help="Quick scan (fewer tickers)")
    
    args = parser.parse_args()
    
    if args.watchlist:
        show_watchlist()
    elif args.sector:
        analyze_sector(args.sector.lower())
    else:
        full_scan()
    
    print("\n" + "🐺"*30)
    print("      THE PACK HUNTS LAGGARDS")
    print("🐺"*30)
    print("\n🐺 AWOOOO!")


if __name__ == "__main__":
    main()
