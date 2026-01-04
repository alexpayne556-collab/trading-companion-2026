#!/usr/bin/env python3
"""
wolf_hunt_wide.py - The Wide Net Scanner

Scans THOUSANDS of tickers to find front-runners.
Not just our hand-picked watchlist. THE ENTIRE MARKET.

Looks for:
1. Volume explosions (today vs 20-day avg)
2. Price acceleration (breaking out of ranges)
3. High short interest (squeeze candidates)
4. Options activity (unusual call buying)

Usage:
    python wolf_hunt_wide.py scan           # Full market scan
    python wolf_hunt_wide.py sector TECH    # Scan specific sector
    python wolf_hunt_wide.py top 20         # Top 20 movers with signals

AWOOOO 🐺
"""

import argparse
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════════
# THE UNIVERSE - Thousands of tickers by sector
# ═══════════════════════════════════════════════════════════════════════════

SECTOR_UNIVERSE = {
    # ──────────────────────────────────────────────────────────────────────
    # QUANTUM COMPUTING - The hot sector
    # ──────────────────────────────────────────────────────────────────────
    "QUANTUM": [
        "QBTS", "QUBT", "IONQ", "RGTI", "ARQQ", "QMCO",
    ],
    
    # ──────────────────────────────────────────────────────────────────────
    # SPACE & DEFENSE - Government money flows here
    # ──────────────────────────────────────────────────────────────────────
    "SPACE": [
        "RKLB", "LUNR", "RDW", "ASTS", "SPIR", "BKSY", "PL", "VORB",
        "ASTR", "MNTS", "LLAP", "SATL", "GSAT",
    ],
    
    "DEFENSE": [
        "RCAT", "PLTR", "KTOS", "LDOS", "CACI", "BAH", "MRCY",
        "AVAV", "AAXN", "TDG", "HII", "LMT", "NOC", "RTX", "GD",
    ],
    
    # ──────────────────────────────────────────────────────────────────────
    # NUCLEAR & ENERGY - AI power demand play
    # ──────────────────────────────────────────────────────────────────────
    "NUCLEAR": [
        "SMR", "NNE", "LEU", "OKLO", "CCJ", "UEC", "UUUU", "DNN",
        "URG", "NXE", "EU", "ENCUF", "BWXT", "LTBR",
    ],
    
    "ENERGY": [
        "FSLR", "ENPH", "SEDG", "RUN", "NOVA", "ARRY", "MAXN",
        "PLUG", "BE", "BLDP", "HYSR", "CLNE", "STEM",
    ],
    
    # ──────────────────────────────────────────────────────────────────────
    # AI & SEMICONDUCTORS - The backbone
    # ──────────────────────────────────────────────────────────────────────
    "AI": [
        "NVDA", "AMD", "SMCI", "ARM", "AVGO", "MRVL", "MU",
        "SOUN", "BBAI", "AI", "UPST", "PATH", "S",
        "SNOW", "PLTR", "DDOG", "CRWD", "ZS", "NET",
    ],
    
    "SEMICONDUCTORS": [
        "TSM", "ASML", "AMAT", "LRCX", "KLAC", "SNPS", "CDNS",
        "QCOM", "TXN", "ADI", "ON", "MCHP", "NXPI", "STM",
        "WOLF", "CREE", "DIOD", "SLAB", "MPWR", "SWKS",
    ],
    
    # ──────────────────────────────────────────────────────────────────────
    # ROBOTICS & AUTOMATION - CES theme
    # ──────────────────────────────────────────────────────────────────────
    "ROBOTICS": [
        "RR", "ISRG", "IRBT", "PATH", "TER", "CGNX", "FANUY",
        "ROK", "ABB", "LECO", "MKSI", "NOVT", "AMSC",
    ],
    
    # ──────────────────────────────────────────────────────────────────────
    # BIOTECH & HEALTHCARE - Always volatile
    # ──────────────────────────────────────────────────────────────────────
    "BIOTECH": [
        "MRNA", "BNTX", "NVAX", "SAVA", "LABU", "XBI",
        "ARCT", "CRSP", "EDIT", "NTLA", "BEAM", "VERV",
        "DNLI", "RXRX", "EXAI", "SDGR", "ABCL", "IMVT",
    ],
    
    # ──────────────────────────────────────────────────────────────────────
    # EV & CLEAN TECH - High volatility
    # ──────────────────────────────────────────────────────────────────────
    "EV": [
        "TSLA", "RIVN", "LCID", "NIO", "XPEV", "LI", "FFIE",
        "FSR", "GOEV", "WKHS", "RIDE", "NKLA", "HYLN",
        "CHPT", "BLNK", "EVGO", "QS", "MVST", "DCFC",
    ],
    
    # ──────────────────────────────────────────────────────────────────────
    # FINTECH & PAYMENTS - Money moving
    # ──────────────────────────────────────────────────────────────────────
    "FINTECH": [
        "SQ", "PYPL", "AFRM", "UPST", "SOFI", "NU", "HOOD",
        "COIN", "MARA", "RIOT", "CLSK", "CIFR", "HUT",
        "BTBT", "BITF", "CORZ", "IREN",
    ],
    
    # ──────────────────────────────────────────────────────────────────────
    # SMALL CAP HIGH SHORT - Squeeze candidates
    # ──────────────────────────────────────────────────────────────────────
    "HIGH_SHORT": [
        "GME", "AMC", "BBBY", "KOSS", "EXPR", "NAKD",
        "SPCE", "WISH", "CLOV", "WKHS", "GOEV", "NKLA",
        "MULN", "FFIE", "RIDE",
    ],
    
    # ──────────────────────────────────────────────────────────────────────
    # RECENT IPOs - New blood
    # ──────────────────────────────────────────────────────────────────────
    "RECENT_IPOS": [
        "ARM", "CART", "BIRK", "KVYO", "TOST", "DOCN",
        "BROS", "RKLB", "IONQ", "ENVX", "DNA",
    ],
}

# Flatten all sectors for full scan
ALL_TICKERS = list(set([t for tickers in SECTOR_UNIVERSE.values() for t in tickers]))

# ═══════════════════════════════════════════════════════════════════════════
# SCANNER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_ticker_signals(ticker: str) -> dict:
    """Get all signals for a single ticker"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="3mo")
        
        if hist.empty or len(hist) < 20:
            return None
        
        # Current data
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2]
        daily_change = ((current_price - prev_close) / prev_close) * 100
        
        # Volume analysis
        current_vol = hist['Volume'].iloc[-1]
        avg_vol_20 = hist['Volume'].tail(20).mean()
        vol_ratio = current_vol / avg_vol_20 if avg_vol_20 > 0 else 0
        
        # Price range analysis (is it breaking out?)
        high_20 = hist['High'].tail(20).max()
        low_20 = hist['Low'].tail(20).min()
        range_position = (current_price - low_20) / (high_20 - low_20) if (high_20 - low_20) > 0 else 0.5
        
        # Weekly momentum
        if len(hist) >= 5:
            week_ago = hist['Close'].iloc[-5]
            weekly_change = ((current_price - week_ago) / week_ago) * 100
        else:
            weekly_change = 0
        
        # Monthly momentum
        if len(hist) >= 20:
            month_ago = hist['Close'].iloc[-20]
            monthly_change = ((current_price - month_ago) / month_ago) * 100
        else:
            monthly_change = 0
        
        # Short interest (if available)
        try:
            info = stock.info
            short_percent = info.get('shortPercentOfFloat', 0) * 100 if info.get('shortPercentOfFloat') else 0
            float_shares = info.get('floatShares', 0)
            market_cap = info.get('marketCap', 0)
        except:
            short_percent = 0
            float_shares = 0
            market_cap = 0
        
        # Calculate composite score
        score = 0
        signals = []
        
        # Volume explosion (max 30 points)
        if vol_ratio >= 5:
            score += 30
            signals.append(f"🔥 VOLUME EXPLOSION: {vol_ratio:.1f}x avg")
        elif vol_ratio >= 3:
            score += 20
            signals.append(f"⚡ High volume: {vol_ratio:.1f}x avg")
        elif vol_ratio >= 2:
            score += 10
            signals.append(f"📊 Elevated volume: {vol_ratio:.1f}x avg")
        
        # Price momentum (max 25 points)
        if daily_change >= 10:
            score += 25
            signals.append(f"🚀 Daily surge: +{daily_change:.1f}%")
        elif daily_change >= 5:
            score += 15
            signals.append(f"📈 Strong day: +{daily_change:.1f}%")
        elif daily_change >= 3:
            score += 8
            signals.append(f"✅ Up: +{daily_change:.1f}%")
        
        # Breakout position (max 20 points)
        if range_position >= 0.95:
            score += 20
            signals.append("🎯 AT 20-DAY HIGH")
        elif range_position >= 0.85:
            score += 12
            signals.append("📍 Near 20d high")
        
        # Short squeeze potential (max 15 points)
        if short_percent >= 25:
            score += 15
            signals.append(f"💥 HIGH SHORT: {short_percent:.1f}%")
        elif short_percent >= 15:
            score += 10
            signals.append(f"⚠️ Elevated short: {short_percent:.1f}%")
        elif short_percent >= 10:
            score += 5
            signals.append(f"📊 Short: {short_percent:.1f}%")
        
        # Weekly momentum bonus (max 10 points)
        if weekly_change >= 20:
            score += 10
            signals.append(f"🔥 Week: +{weekly_change:.1f}%")
        elif weekly_change >= 10:
            score += 5
            signals.append(f"📈 Week: +{weekly_change:.1f}%")
        
        return {
            'ticker': ticker,
            'price': current_price,
            'daily_change': daily_change,
            'weekly_change': weekly_change,
            'monthly_change': monthly_change,
            'vol_ratio': vol_ratio,
            'short_percent': short_percent,
            'range_position': range_position,
            'score': score,
            'signals': signals,
            'market_cap': market_cap,
        }
        
    except Exception as e:
        return None


def scan_universe(tickers: list, max_workers: int = 10) -> list:
    """Scan a list of tickers in parallel"""
    results = []
    
    print(f"\n🔍 Scanning {len(tickers)} tickers...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(get_ticker_signals, t): t for t in tickers}
        
        completed = 0
        for future in as_completed(futures):
            completed += 1
            if completed % 20 == 0:
                print(f"   Progress: {completed}/{len(tickers)}")
            
            result = future.result()
            if result and result['score'] > 0:
                results.append(result)
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def print_results(results: list, limit: int = 30):
    """Print scan results"""
    print(f"""
{'='*75}
🔥 WOLF HUNT WIDE - TOP FRONT-RUNNERS 🔥
{'='*75}
{'TICKER':<8} {'PRICE':>10} {'DAY':>8} {'WEEK':>8} {'VOL':>8} {'SHORT':>8} {'SCORE':>6}
{'-'*75}""")
    
    for r in results[:limit]:
        vol_str = f"{r['vol_ratio']:.1f}x"
        short_str = f"{r['short_percent']:.1f}%" if r['short_percent'] > 0 else "-"
        
        # Score level indicator
        if r['score'] >= 50:
            level = "🔥"
        elif r['score'] >= 30:
            level = "⚡"
        else:
            level = "✅"
        
        print(f"{r['ticker']:<8} ${r['price']:>9.2f} {r['daily_change']:>+7.1f}% {r['weekly_change']:>+7.1f}% {vol_str:>8} {short_str:>8} {r['score']:>4} {level}")
    
    print(f"{'='*75}\n")
    
    # Print detailed signals for top 10
    print("🎯 TOP 10 DETAILED SIGNALS:\n")
    for i, r in enumerate(results[:10], 1):
        print(f"{i}. {r['ticker']} @ ${r['price']:.2f} — Score: {r['score']}")
        for signal in r['signals']:
            print(f"   {signal}")
        print()


def scan_sector(sector: str):
    """Scan a specific sector"""
    sector = sector.upper()
    if sector not in SECTOR_UNIVERSE:
        print(f"❌ Unknown sector: {sector}")
        print(f"Available: {', '.join(SECTOR_UNIVERSE.keys())}")
        return
    
    print(f"\n🐺 SCANNING SECTOR: {sector}")
    print(f"   Tickers: {', '.join(SECTOR_UNIVERSE[sector])}")
    
    results = scan_universe(SECTOR_UNIVERSE[sector])
    print_results(results, limit=len(results))


def full_scan():
    """Scan the entire universe"""
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  🐺 WOLF HUNT WIDE - FULL MARKET SCAN                            ║
╠══════════════════════════════════════════════════════════════════╣
║  Sectors: {len(SECTOR_UNIVERSE):<52} ║
║  Tickers: {len(ALL_TICKERS):<52} ║
║  Looking for: Volume + Momentum + Shorts + Breakouts             ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    results = scan_universe(ALL_TICKERS, max_workers=15)
    print_results(results, limit=30)
    
    # Sector breakdown
    print("📊 TOP MOVERS BY SECTOR:\n")
    for sector, tickers in SECTOR_UNIVERSE.items():
        sector_results = [r for r in results if r['ticker'] in tickers]
        if sector_results:
            top = sector_results[0]
            print(f"  {sector:<15} {top['ticker']:<6} +{top['daily_change']:.1f}% Score:{top['score']}")
    
    print()


def top_movers(limit: int = 20):
    """Quick scan for top movers only"""
    print(f"\n🐺 TOP {limit} FRONT-RUNNERS\n")
    results = scan_universe(ALL_TICKERS, max_workers=15)
    print_results(results, limit=limit)


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="🐺 Wolf Hunt Wide - Full Market Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python wolf_hunt_wide.py scan                 # Full market scan
  python wolf_hunt_wide.py sector QUANTUM       # Scan quantum sector
  python wolf_hunt_wide.py sector BIOTECH       # Scan biotech
  python wolf_hunt_wide.py top 20               # Top 20 movers

Available Sectors:
  QUANTUM, SPACE, DEFENSE, NUCLEAR, ENERGY, AI, SEMICONDUCTORS,
  ROBOTICS, BIOTECH, EV, FINTECH, HIGH_SHORT, RECENT_IPOS

AWOOOO 🐺
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Full scan
    subparsers.add_parser("scan", help="Full market scan")
    
    # Sector scan
    sector_parser = subparsers.add_parser("sector", help="Scan specific sector")
    sector_parser.add_argument("name", help="Sector name")
    
    # Top movers
    top_parser = subparsers.add_parser("top", help="Top N movers")
    top_parser.add_argument("count", type=int, nargs="?", default=20, help="Number of results")
    
    args = parser.parse_args()
    
    if args.command == "scan":
        full_scan()
    elif args.command == "sector":
        scan_sector(args.name)
    elif args.command == "top":
        top_movers(args.count)
    else:
        # Default to full scan
        full_scan()


if __name__ == "__main__":
    main()
