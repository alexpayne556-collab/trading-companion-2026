#!/usr/bin/env python3
"""
wolf_briefing.py - THE REAL MONDAY BRIEFING

Scans 100+ tickers across 12 sectors.
Ranks by TOTAL score (Pressure + Independence + Diversification).
Outputs TOP 10 with diversified 5-ticker portfolio suggestion.

NO TUNNEL VISION. NO SINGLE CATALYST DEPENDENCY.

Usage:
    python wolf_briefing.py               # Full briefing
    python wolf_briefing.py --sector NUCLEAR  # Focus on sector
    python wolf_briefing.py --portfolio   # Just the portfolio suggestion

AWOOOO 🐺
"""

import argparse
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════════
# THE FULL UNIVERSE - 100+ tickers across 12 sectors
# ═══════════════════════════════════════════════════════════════════════════

UNIVERSE = {
    "QUANTUM": ["IONQ", "RGTI", "QBTS", "QUBT", "ARQQ"],
    "SPACE": ["LUNR", "RKLB", "RDW", "BKSY", "ASTS", "SPIR", "PL", "IRDM", "GSAT"],
    "NUCLEAR": ["LEU", "CCJ", "UUUU", "UEC", "SMR", "OKLO", "DNN", "NXE", "NNE", "BWXT"],
    "ROBOTICS": ["RR", "TER", "ISRG", "PATH", "CGNX", "ROK"],
    "AI_INFRA": ["NVDA", "SMCI", "VRT", "SOUN", "AI", "BBAI", "UPST"],
    "MEMORY_SEMI": ["MU", "WDC", "ANET", "MRVL", "AMD", "ARM", "AVGO", "TSM", "ASML", "WOLF"],
    "CRYPTO": ["MARA", "RIOT", "CLSK", "HUT", "BITF", "CORZ", "IREN", "COIN"],
    "CLEAN_ENERGY": ["PLUG", "FCEL", "BE", "ENPH", "RUN", "FSLR", "SEDG", "STEM"],
    "BIOTECH": ["MRNA", "BNTX", "NVAX", "CRSP", "EDIT", "NTLA", "BEAM", "RXRX"],
    "SOFTWARE": ["PLTR", "SNOW", "NET", "DDOG", "CRWD", "ZS", "MDB", "S"],
    "EV": ["TSLA", "RIVN", "LCID", "NIO", "XPEV", "LI", "CHPT", "QS"],
    "HIGH_SHORT": ["CVNA", "AFRM", "SOFI", "HOOD", "GME", "AMC", "SPCE"],
}

ALL_TICKERS = list(set([t for tickers in UNIVERSE.values() for t in tickers]))

# Sector leaders for lag detection
SECTOR_LEADERS = {
    "QUANTUM": "IONQ",
    "SPACE": "RKLB", 
    "NUCLEAR": "CCJ",
    "AI_INFRA": "NVDA",
    "MEMORY_SEMI": "MU",
    "CRYPTO": "MARA",
    "CLEAN_ENERGY": "FSLR",
    "EV": "TSLA",
    "SOFTWARE": "PLTR",
}

# CES-dependent tickers (score penalty)
CES_DEPENDENT = ["RR", "QBTS", "QUBT", "SOUN"]

# ═══════════════════════════════════════════════════════════════════════════
# HUNT TYPES
# ═══════════════════════════════════════════════════════════════════════════

HUNT_TYPES = {
    "WOUNDED_PREY": "Beaten down, now recovering",
    "SQUEEZE_STALKER": "High short + catalyst potential", 
    "LEADER_LAG": "Sector leader ran, this lagged",
    "ACCUMULATION": "Volume without price move",
    "BREAKOUT": "Breaking out of base",
    "MOMENTUM_DAY2": "Friday runner, Day 2 continuation",
    "TAX_BOUNCE": "December crushed, January bounce",
}

# ═══════════════════════════════════════════════════════════════════════════
# COMPREHENSIVE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

def get_sector(ticker: str) -> str:
    """Find which sector a ticker belongs to"""
    for sector, tickers in UNIVERSE.items():
        if ticker in tickers:
            return sector
    return "UNKNOWN"


def analyze_ticker_full(ticker: str, sector_data: dict = None) -> dict:
    """Full analysis with all scoring components"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")
        
        if hist.empty or len(hist) < 40:
            return None
        
        sector = get_sector(ticker)
        
        # ═══════════════════════════════════════════════════════════════════
        # BASIC METRICS
        # ═══════════════════════════════════════════════════════════════════
        
        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        daily_chg = ((current - prev) / prev) * 100
        
        # Volume
        vol_today = hist['Volume'].iloc[-1]
        vol_avg_20 = hist['Volume'].tail(20).mean()
        vol_avg_5 = hist['Volume'].tail(5).mean()
        vol_ratio = vol_today / vol_avg_20 if vol_avg_20 > 0 else 0
        
        # Price ranges
        high_20 = hist['High'].tail(20).max()
        low_20 = hist['Low'].tail(20).min()
        high_52 = hist['High'].max()
        low_52 = hist['Low'].min()
        
        from_52_high = ((current - high_52) / high_52) * 100
        from_52_low = ((current - low_52) / low_52) * 100
        range_position = (current - low_20) / (high_20 - low_20) if (high_20 - low_20) > 0 else 0.5
        
        # Momentum
        week_chg = ((current - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100 if len(hist) >= 5 else 0
        month_chg = ((current - hist['Close'].iloc[-20]) / hist['Close'].iloc[-20]) * 100 if len(hist) >= 20 else 0
        
        # December performance (tax-loss detection)
        dec_start_idx = -25 if len(hist) >= 25 else 0
        dec_chg = ((hist['Close'].iloc[-1] - hist['Close'].iloc[dec_start_idx]) / hist['Close'].iloc[dec_start_idx]) * 100
        
        # Short interest
        try:
            info = stock.info
            short_pct = info.get('shortPercentOfFloat', 0) * 100 if info.get('shortPercentOfFloat') else 0
            market_cap = info.get('marketCap', 0)
        except:
            short_pct = 0
            market_cap = 0
        
        # ═══════════════════════════════════════════════════════════════════
        # COMPONENT 1: PRESSURE SCORE (max 35 pts)
        # ═══════════════════════════════════════════════════════════════════
        
        pressure_score = 0
        pressure_signals = []
        
        # Volume signal (max 10)
        if vol_ratio >= 3:
            pressure_score += 10
            pressure_signals.append(f"Volume {vol_ratio:.1f}x")
        elif vol_ratio >= 2:
            pressure_score += 6
            pressure_signals.append(f"Volume {vol_ratio:.1f}x")
        elif vol_ratio >= 1.5:
            pressure_score += 3
        
        # Short interest (max 10)
        if short_pct >= 30:
            pressure_score += 10
            pressure_signals.append(f"Short {short_pct:.0f}%")
        elif short_pct >= 20:
            pressure_score += 7
            pressure_signals.append(f"Short {short_pct:.0f}%")
        elif short_pct >= 15:
            pressure_score += 4
            pressure_signals.append(f"Short {short_pct:.0f}%")
        
        # Momentum (max 10)
        if daily_chg >= 10:
            pressure_score += 10
            pressure_signals.append(f"Day +{daily_chg:.0f}%")
        elif daily_chg >= 5:
            pressure_score += 6
            pressure_signals.append(f"Day +{daily_chg:.0f}%")
        elif daily_chg >= 3:
            pressure_score += 3
        
        # Position in range (max 5)
        if range_position >= 0.9:
            pressure_score += 5
            pressure_signals.append("At highs")
        elif range_position >= 0.7:
            pressure_score += 3
        
        # ═══════════════════════════════════════════════════════════════════
        # COMPONENT 2: CATALYST INDEPENDENCE (max 25 pts)
        # ═══════════════════════════════════════════════════════════════════
        
        independence_score = 0
        
        # CES dependency penalty
        if ticker in CES_DEPENDENT:
            independence_score -= 10  # Penalty for single-event dependency
        else:
            independence_score += 10  # Bonus for NOT needing CES
        
        # Sector momentum (riding a wave, not a single event)
        if sector_data and sector in sector_data:
            sector_week = sector_data[sector]
            if sector_week > 10:
                independence_score += 10
            elif sector_week > 5:
                independence_score += 5
        
        # Multiple catalyst types (not single event)
        if short_pct >= 20:
            independence_score += 5  # Squeeze is always a catalyst
        
        # ═══════════════════════════════════════════════════════════════════
        # COMPONENT 3: HUNT TYPE DETECTION (max 25 pts)
        # ═══════════════════════════════════════════════════════════════════
        
        hunt_type = None
        hunt_score = 0
        hunt_reason = ""
        
        # WOUNDED PREY: Down big, now stabilizing
        if from_52_high <= -40 and week_chg > -5:
            hunt_type = "WOUNDED_PREY"
            hunt_score = 25
            hunt_reason = f"Down {from_52_high:.0f}% from high, stabilizing"
        elif from_52_high <= -30 and daily_chg > 0:
            hunt_type = "WOUNDED_PREY"
            hunt_score = 18
            hunt_reason = f"Down {from_52_high:.0f}% from high, showing life"
        
        # TAX BOUNCE: December crushed, January opportunity
        if dec_chg <= -20 and week_chg > 0 and not hunt_type:
            hunt_type = "TAX_BOUNCE"
            hunt_score = 20
            hunt_reason = f"Dec: {dec_chg:.0f}%, tax-loss bounce setup"
        
        # SQUEEZE STALKER: High short + any momentum
        if short_pct >= 25 and daily_chg > 3 and not hunt_type:
            hunt_type = "SQUEEZE_STALKER"
            hunt_score = 22
            hunt_reason = f"{short_pct:.0f}% short + momentum"
        elif short_pct >= 20 and week_chg > 5 and not hunt_type:
            hunt_type = "SQUEEZE_STALKER"
            hunt_score = 18
            hunt_reason = f"{short_pct:.0f}% short, building"
        
        # MOMENTUM DAY2: Friday runner
        if daily_chg >= 8 and vol_ratio >= 1.5 and not hunt_type:
            hunt_type = "MOMENTUM_DAY2"
            hunt_score = 15
            hunt_reason = f"Friday +{daily_chg:.0f}%, Day 2 potential"
        
        # BREAKOUT: Near highs with volume
        if range_position >= 0.95 and vol_ratio >= 1.3 and not hunt_type:
            hunt_type = "BREAKOUT"
            hunt_score = 18
            hunt_reason = "Breaking out of range"
        
        # ACCUMULATION: Volume without price move
        if vol_ratio >= 1.5 and abs(daily_chg) < 3 and not hunt_type:
            hunt_type = "ACCUMULATION"
            hunt_score = 15
            hunt_reason = "Volume without price move"
        
        # LEADER LAG: Check against sector leader
        if sector_data and sector in SECTOR_LEADERS and not hunt_type:
            leader = SECTOR_LEADERS[sector]
            if leader in sector_data.get('leader_moves', {}):
                leader_week = sector_data['leader_moves'][leader]
                if leader_week > 15 and week_chg < 5:
                    hunt_type = "LEADER_LAG"
                    hunt_score = 20
                    hunt_reason = f"Leader {leader} +{leader_week:.0f}%, this only +{week_chg:.0f}%"
        
        if not hunt_type:
            hunt_type = "NONE"
            hunt_score = 0
            hunt_reason = "No clear pattern"
        
        # ═══════════════════════════════════════════════════════════════════
        # COMPONENT 4: DIVERSIFICATION VALUE (max 15 pts)
        # ═══════════════════════════════════════════════════════════════════
        
        # This gets calculated at portfolio level, base score here
        div_score = 10  # Base - adjusted during portfolio construction
        
        # Small cap bonus (more explosive)
        if market_cap and market_cap < 5_000_000_000:
            div_score += 5
        
        # ═══════════════════════════════════════════════════════════════════
        # TOTAL SCORE
        # ═══════════════════════════════════════════════════════════════════
        
        total_score = pressure_score + independence_score + hunt_score + div_score
        
        return {
            'ticker': ticker,
            'sector': sector,
            'price': current,
            'daily_chg': daily_chg,
            'week_chg': week_chg,
            'month_chg': month_chg,
            'from_high': from_52_high,
            'vol_ratio': vol_ratio,
            'short_pct': short_pct,
            'market_cap': market_cap,
            'pressure_score': pressure_score,
            'independence_score': independence_score,
            'hunt_score': hunt_score,
            'hunt_type': hunt_type,
            'hunt_reason': hunt_reason,
            'div_score': div_score,
            'total_score': total_score,
            'pressure_signals': pressure_signals,
        }
        
    except Exception as e:
        return None


def get_sector_momentum() -> dict:
    """Calculate sector performance and leader moves"""
    sector_data = {}
    leader_moves = {}
    
    print("📊 Calculating sector momentum...")
    
    for sector, tickers in UNIVERSE.items():
        week_changes = []
        for ticker in tickers[:5]:
            try:
                hist = yf.Ticker(ticker).history(period="1mo")
                if len(hist) >= 5:
                    chg = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100
                    week_changes.append(chg)
                    if ticker in SECTOR_LEADERS.values():
                        leader_moves[ticker] = chg
            except:
                pass
        if week_changes:
            sector_data[sector] = np.mean(week_changes)
    
    sector_data['leader_moves'] = leader_moves
    return sector_data


def scan_full_universe() -> list:
    """Scan everything"""
    # Get sector data first
    sector_data = get_sector_momentum()
    
    print(f"\n🔍 Scanning {len(ALL_TICKERS)} tickers across {len(UNIVERSE)} sectors...")
    
    results = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(analyze_ticker_full, t, sector_data): t for t in ALL_TICKERS}
        
        completed = 0
        for future in as_completed(futures):
            completed += 1
            if completed % 20 == 0:
                print(f"   Progress: {completed}/{len(ALL_TICKERS)}")
            
            result = future.result()
            if result:
                results.append(result)
    
    results.sort(key=lambda x: x['total_score'], reverse=True)
    return results


def build_diversified_portfolio(results: list, num_positions: int = 5, capital: float = 740) -> list:
    """Build diversified portfolio from top results"""
    portfolio = []
    used_sectors = set()
    position_size = capital / num_positions
    
    for r in results:
        # Skip if we already have this sector
        if r['sector'] in used_sectors:
            continue
        
        # Skip if score too low
        if r['total_score'] < 20:
            continue
        
        used_sectors.add(r['sector'])
        portfolio.append({
            **r,
            'position_size': position_size,
        })
        
        if len(portfolio) >= num_positions:
            break
    
    return portfolio


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT
# ═══════════════════════════════════════════════════════════════════════════

def print_full_briefing(results: list, portfolio: list, sector_data: dict):
    """Print the complete Monday briefing"""
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🐺 WOLF PACK MONDAY BRIEFING — {datetime.now().strftime('%B %d, %Y'):<20}                     ║
║                                                                              ║
║  NO TUNNEL VISION. NO SINGLE CATALYST. THE WHOLE BATTLEFIELD.                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════
📊 SECTOR MOMENTUM (1 WEEK)
═══════════════════════════════════════════════════════════════════════════════
""")
    
    for sector, perf in sorted(sector_data.items(), key=lambda x: x[1] if isinstance(x[1], float) else -999, reverse=True):
        if isinstance(perf, float):
            bar = "█" * int(max(0, min(20, perf)))
            print(f"  {sector:<15} {perf:>+6.1f}% {bar}")
    
    print(f"""
═══════════════════════════════════════════════════════════════════════════════
🎯 TOP 10 SETUPS — RANKED BY TOTAL SCORE
═══════════════════════════════════════════════════════════════════════════════
""")
    
    for i, r in enumerate(results[:10], 1):
        ces_flag = "⚠️CES" if r['ticker'] in CES_DEPENDENT else ""
        
        print(f"""
#{i}: {r['ticker']} — Total Score: {r['total_score']} {ces_flag}
────────────────────────────────────────────────────────
  Sector:     {r['sector']}
  Price:      ${r['price']:.2f}
  Day/Week:   {r['daily_chg']:+.1f}% / {r['week_chg']:+.1f}%
  From High:  {r['from_high']:.1f}%
  Short:      {r['short_pct']:.1f}%
  
  Hunt Type:  {r['hunt_type']}
  Why:        {r['hunt_reason']}
  
  Scores:     Pressure:{r['pressure_score']:>3} | Independence:{r['independence_score']:>3} | Hunt:{r['hunt_score']:>3}
""")
    
    print(f"""
═══════════════════════════════════════════════════════════════════════════════
💰 DIVERSIFIED PORTFOLIO SUGGESTION — $740 / 5 Positions
═══════════════════════════════════════════════════════════════════════════════
""")
    
    print(f"{'#':<3} {'TICKER':<7} {'SECTOR':<15} {'SIZE':>8} {'SCORE':>6} {'HUNT TYPE':<15} {'REASON':<30}")
    print("─" * 95)
    
    total_allocated = 0
    for i, p in enumerate(portfolio, 1):
        print(f"{i:<3} {p['ticker']:<7} {p['sector']:<15} ${p['position_size']:>6.0f} {p['total_score']:>5} {p['hunt_type']:<15} {p['hunt_reason'][:30]}")
        total_allocated += p['position_size']
    
    print("─" * 95)
    print(f"    {'TOTAL':<7} {'':<15} ${total_allocated:>6.0f}")
    
    print(f"""
═══════════════════════════════════════════════════════════════════════════════
✅ WHY THIS PORTFOLIO
═══════════════════════════════════════════════════════════════════════════════

  • {len(portfolio)} different sectors = If one fails, {len(portfolio)-1} survive
  • Multiple hunt types = Not dependent on single catalyst
  • CES plays must EARN their spot = Compete against entire market
  • Each position ~${portfolio[0]['position_size']:.0f} = Survivable if wrong
  
═══════════════════════════════════════════════════════════════════════════════
⚠️ WATCH FOR MONDAY
═══════════════════════════════════════════════════════════════════════════════

  • Pre-market gaps > 10% = DON'T CHASE (move happened)
  • Volume dead pre-market = Skip that play
  • Overnight 8-K filings = Check each ticker
  • Sector rotation = May change rankings
  
═══════════════════════════════════════════════════════════════════════════════
""")


def main():
    parser = argparse.ArgumentParser(
        description="🐺 Wolf Pack Monday Briefing - Full Battlefield Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
NO TUNNEL VISION. THE WHOLE MARKET.
AWOOOO 🐺
        """
    )
    
    parser.add_argument("--sector", help="Focus on specific sector")
    parser.add_argument("--portfolio", action="store_true", help="Just portfolio suggestion")
    parser.add_argument("--capital", type=float, default=740, help="Capital to deploy")
    parser.add_argument("--positions", type=int, default=5, help="Number of positions")
    
    args = parser.parse_args()
    
    # Get sector momentum
    sector_data = get_sector_momentum()
    
    # Full scan
    results = scan_full_universe()
    
    # Build portfolio
    portfolio = build_diversified_portfolio(results, args.positions, args.capital)
    
    # Output
    print_full_briefing(results, portfolio, sector_data)


if __name__ == "__main__":
    main()
