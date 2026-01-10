#!/usr/bin/env python3
"""
🐺 SECTOR DISCOVERY ENGINE
Find emerging sector tickers BEFORE they run

The Pack's Edge:
- Track ETF holdings for emerging sectors
- Find ALL public tickers in a theme
- Identify laggards in hot sectors
- Get in EARLY at discounted rates

Usage:
    python3 sector_discovery.py --sector "photonics"
    python3 sector_discovery.py --sector "quantum computing"
    python3 sector_discovery.py --sector "space"
    python3 sector_discovery.py --etf ARKQ  # What's ARK buying?
    python3 sector_discovery.py --keywords "lithium niobate,optical chips"
"""

import argparse
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json

# 🐺 SECTOR KEYWORD MAPPINGS
# These are the terms that identify stocks in each emerging sector
SECTOR_KEYWORDS = {
    'photonics': [
        'photonics', 'optical', 'silicon photonics', 'laser', 'optoelectronics',
        'lithium niobate', 'optical interconnect', 'photonic chip', 'optical computing'
    ],
    'quantum': [
        'quantum computing', 'quantum', 'qubit', 'quantum processor',
        'quantum machine', 'quantum algorithm', 'quantum cryptography'
    ],
    'space': [
        'space', 'satellite', 'rocket', 'lunar', 'orbital', 'spacecraft',
        'space station', 'space debris', 'launch vehicle'
    ],
    'rare_earth': [
        'rare earth', 'lithium', 'cobalt', 'critical minerals', 'mining',
        'mineral processing', 'battery materials'
    ],
    'nuclear': [
        'nuclear', 'uranium', 'SMR', 'small modular reactor', 'nuclear fuel',
        'enrichment', 'nuclear power'
    ],
    'robotics': [
        'robotics', 'humanoid', 'robot', 'automation', 'industrial robot',
        'autonomous', 'AGV', 'cobot'
    ],
    'drones': [
        'drone', 'UAV', 'unmanned', 'aerial vehicle', 'eVTOL', 'air taxi'
    ],
    'ai_chips': [
        'AI chip', 'GPU', 'TPU', 'neural processor', 'inference chip',
        'AI accelerator', 'machine learning chip'
    ]
}

# 🐺 KNOWN SECTOR TICKERS
# Manually curated lists of tickers we KNOW are in each sector
SECTOR_TICKERS = {
    'photonics': {
        'LITE': 'Lumentum - Lasers for high-speed optical modules',
        'AAOI': 'Applied Optoelectronics - Microsoft contract ramping',
        'GFS': 'GlobalFoundries - Largest silicon photonics foundry (owns AMF)',
        'COHR': 'Coherent Corp - Silicon photonics transceivers',
        'QUBT': 'Quantum Computing Inc - Integrated PHOTONICS company!',
        'MACOM': 'MACOM Technology - Silicon photonics',
        'MRVL': 'Marvell - Optical interconnects for AI',
        'II-VI': 'II-VI Incorporated - Optical components (now Coherent)',
        'IIVI': 'II-VI (alt ticker)',
        'LUNA': 'Luna Innovations - Fiber optic sensing',
        'IPGP': 'IPG Photonics - High-power fiber lasers',
        'CIEN': 'Ciena - Optical networking equipment',
        'INFN': 'Infinera - Optical transport systems',
    },
    'quantum': {
        'IONQ': 'IonQ - Trapped ion quantum computing',
        'QUBT': 'Quantum Computing Inc - Photonics + quantum',
        'QBTS': 'D-Wave Quantum - Quantum annealing',
        'RGTI': 'Rigetti Computing - Superconducting quantum',
        'ARQQ': 'Arqit Quantum - Quantum encryption',
    },
    'space': {
        'RKLB': 'Rocket Lab - Launch + spacecraft',
        'RDW': 'Redwire - Space infrastructure',
        'LUNR': 'Intuitive Machines - Lunar landers',
        'ASTS': 'AST SpaceMobile - Space-based cellular',
        'SPCE': 'Virgin Galactic - Space tourism',
        'MNTS': 'Momentus - In-space transportation',
        'BKSY': 'BlackSky - Earth observation',
        'PL': 'Planet Labs - Earth imaging',
        'LLAP': 'Terran Orbital - Small satellites',
        'ASTR': 'Astra Space - Launch services',
    },
    'rare_earth': {
        'USAR': 'USA Rare Earth - Venezuela processing',
        'MP': 'MP Materials - Mountain Pass mine',
        'UUUU': 'Energy Fuels - Rare earth + uranium',
        'LAC': 'Lithium Americas - Lithium mining',
        'LTHM': 'Livent - Lithium production',
        'ALB': 'Albemarle - Lithium giant',
        'SQM': 'Sociedad Quimica - Chilean lithium',
    },
    'nuclear': {
        'UUUU': 'Energy Fuels - Uranium producer',
        'UEC': 'Uranium Energy Corp - US uranium',
        'DNN': 'Denison Mines - Canadian uranium',
        'CCJ': 'Cameco - Uranium giant',
        'LEU': 'Centrus Energy - HALEU enrichment',
        'SMR': 'NuScale Power - Small modular reactors',
        'OKLO': 'Oklo - Advanced fission',
        'NNE': 'Nano Nuclear Energy - Micro reactors',
    },
    'robotics': {
        'ISRG': 'Intuitive Surgical - Surgical robots',
        'IRBT': 'iRobot - Consumer robots',
        'FANUY': 'Fanuc - Industrial robots',
        'ABB': 'ABB - Industrial automation',
        'ROK': 'Rockwell - Industrial automation',
        'AGTI': 'Agiliti - Healthcare equipment (robots)',
        'PATH': 'UiPath - Software robots (RPA)',
        'BTAI': 'BioXcel Therapeutics - Medical robots',
    },
    'drones': {
        'UAVS': 'AgEagle Aerial - Drone systems',
        'AVAV': 'AeroVironment - Military drones',
        'JOBY': 'Joby Aviation - Air taxi',
        'LILM': 'Lilium - eVTOL',
        'ACHR': 'Archer Aviation - Urban air mobility',
        'EVTL': 'Vertical Aerospace - eVTOL',
    },
    'ai_chips': {
        'NVDA': 'NVIDIA - GPU leader',
        'AMD': 'AMD - GPU competitor',
        'INTC': 'Intel - Trying to compete',
        'AVGO': 'Broadcom - AI networking chips',
        'MRVL': 'Marvell - Custom AI chips',
        'QCOM': 'Qualcomm - Mobile AI',
        'ASML': 'ASML - Makes the machines that make chips',
    }
}

# 🐺 THEMATIC ETFS
# ETFs that track emerging sectors - their holdings reveal opportunities
THEMATIC_ETFS = {
    'ARKQ': 'ARK Autonomous Tech & Robotics',
    'ARKK': 'ARK Innovation',
    'ARKX': 'ARK Space Exploration',
    'UFO': 'Procure Space ETF',
    'ROBO': 'ROBO Global Robotics',
    'BOTZ': 'Global X Robotics & AI',
    'QTUM': 'Defiance Quantum ETF',
    'QQQJ': 'Invesco NASDAQ Next Gen 100',
    'SMH': 'VanEck Semiconductor ETF',
    'SOXX': 'iShares Semiconductor ETF',
    'URNM': 'Sprott Uranium Miners ETF',
    'URA': 'Global X Uranium ETF',
    'REMX': 'VanEck Rare Earth ETF',
    'LIT': 'Global X Lithium & Battery Tech',
}


def get_sector_tickers(sector: str) -> dict:
    """Get all known tickers for a sector"""
    sector_lower = sector.lower().replace(' ', '_')
    
    # Try exact match first
    if sector_lower in SECTOR_TICKERS:
        return SECTOR_TICKERS[sector_lower]
    
    # Try partial match
    for key in SECTOR_TICKERS:
        if sector_lower in key or key in sector_lower:
            return SECTOR_TICKERS[key]
    
    return {}


def analyze_ticker(ticker: str) -> dict:
    """Get key metrics for a ticker"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get price data
        hist = stock.history(period='1mo')
        if len(hist) == 0:
            return None
            
        current_price = hist['Close'].iloc[-1]
        month_ago_price = hist['Close'].iloc[0]
        month_return = ((current_price - month_ago_price) / month_ago_price) * 100
        
        # Get week return
        week_hist = stock.history(period='5d')
        if len(week_hist) >= 2:
            week_return = ((week_hist['Close'].iloc[-1] - week_hist['Close'].iloc[0]) / week_hist['Close'].iloc[0]) * 100
        else:
            week_return = 0
            
        # Volume analysis
        avg_volume = info.get('averageVolume', 0)
        today_volume = hist['Volume'].iloc[-1] if len(hist) > 0 else 0
        volume_ratio = today_volume / avg_volume if avg_volume > 0 else 0
        
        return {
            'price': current_price,
            'market_cap': info.get('marketCap', 0),
            'week_return': week_return,
            'month_return': month_return,
            'volume_ratio': volume_ratio,
            'avg_volume': avg_volume,
            'short_percent': info.get('shortPercentOfFloat', 0),
        }
    except Exception as e:
        return None


def find_laggards(sector: str) -> list:
    """Find laggards in a sector - stocks that haven't run yet"""
    tickers = get_sector_tickers(sector)
    if not tickers:
        print(f"❌ Unknown sector: {sector}")
        print(f"Available sectors: {', '.join(SECTOR_TICKERS.keys())}")
        return []
    
    results = []
    
    print(f"\n🔍 Analyzing {len(tickers)} tickers in {sector.upper()} sector...")
    print("-" * 80)
    
    for ticker, description in tickers.items():
        metrics = analyze_ticker(ticker)
        if metrics:
            results.append({
                'ticker': ticker,
                'description': description,
                **metrics
            })
    
    # Sort by month return (lowest = most laggard)
    results.sort(key=lambda x: x['month_return'])
    
    return results


def score_opportunity(ticker_data: dict, sector_avg_return: float) -> float:
    """
    Score a ticker as an opportunity
    Higher score = better opportunity
    
    Factors:
    - Laggard status (hasn't run with sector)
    - Volume increasing (accumulation)
    - Not too heavily shorted
    - Reasonable price
    """
    score = 50  # Base score
    
    # Laggard bonus (up to +30)
    # If sector avg is +10% and this stock is +2%, that's laggard = good
    laggard_gap = sector_avg_return - ticker_data['month_return']
    if laggard_gap > 0:
        score += min(laggard_gap * 3, 30)  # Up to 30 points for being laggard
    
    # Volume accumulation bonus (up to +15)
    if ticker_data['volume_ratio'] > 1.5:
        score += 15
    elif ticker_data['volume_ratio'] > 1.0:
        score += 10
    
    # Price range bonus - prefer $5-$50 range (up to +10)
    price = ticker_data['price']
    if 5 <= price <= 50:
        score += 10
    elif price < 5:
        score += 5  # Penny stocks riskier
    
    # Short interest (can be squeeze potential)
    short_pct = ticker_data.get('short_percent', 0) or 0
    if short_pct > 0.2:  # >20% short
        score += 5  # Squeeze potential
    
    return min(score, 100)


def discover_sector(sector: str):
    """Main function to discover opportunities in a sector"""
    print(f"\n{'='*80}")
    print(f"🐺 SECTOR DISCOVERY: {sector.upper()}")
    print(f"{'='*80}")
    
    tickers = get_sector_tickers(sector)
    if not tickers:
        print(f"❌ Unknown sector: {sector}")
        print(f"\n📋 Available sectors:")
        for s in SECTOR_TICKERS.keys():
            print(f"   • {s}")
        return
    
    print(f"\n📊 Found {len(tickers)} tickers in {sector} sector")
    print("-" * 80)
    
    # Analyze all tickers
    results = []
    for ticker, description in tickers.items():
        print(f"   Analyzing {ticker}...", end='\r')
        metrics = analyze_ticker(ticker)
        if metrics:
            results.append({
                'ticker': ticker,
                'description': description,
                **metrics
            })
    
    if not results:
        print("❌ Could not analyze any tickers")
        return
    
    # Calculate sector average return
    sector_avg = sum(r['month_return'] for r in results) / len(results)
    
    # Score each opportunity
    for r in results:
        r['score'] = score_opportunity(r, sector_avg)
    
    # Sort by score (highest = best opportunity)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Display results
    print(f"\n{'='*80}")
    print(f"📈 SECTOR AVERAGE: {sector_avg:+.1f}% (1 month)")
    print(f"{'='*80}")
    
    print(f"\n{'TICKER':<8} {'PRICE':>10} {'1W':>8} {'1M':>8} {'VOL':>8} {'SCORE':>8}")
    print("-" * 80)
    
    for r in results:
        vol_indicator = "🔥" if r['volume_ratio'] > 1.5 else "  "
        lag_indicator = "⬇️" if r['month_return'] < sector_avg else "  "
        print(f"{r['ticker']:<8} ${r['price']:>8.2f} {r['week_return']:>+7.1f}% {r['month_return']:>+7.1f}% {r['volume_ratio']:>7.1f}x {r['score']:>7.0f} {vol_indicator}{lag_indicator}")
    
    # Top 3 opportunities
    print(f"\n{'='*80}")
    print("🎯 TOP 3 OPPORTUNITIES (Laggards with Volume)")
    print(f"{'='*80}")
    
    for i, r in enumerate(results[:3], 1):
        lag_status = "LAGGARD" if r['month_return'] < sector_avg else "LEADER"
        print(f"\n#{i} {r['ticker']} - {r['description']}")
        print(f"   Price: ${r['price']:.2f}")
        print(f"   1-Month: {r['month_return']:+.1f}% ({lag_status} vs sector avg {sector_avg:+.1f}%)")
        print(f"   Volume: {r['volume_ratio']:.1f}x average")
        print(f"   Score: {r['score']:.0f}/100")
        
        # Calculate potential
        if r['month_return'] < sector_avg:
            catch_up = sector_avg - r['month_return']
            target = r['price'] * (1 + catch_up/100)
            print(f"   🎯 If catches sector avg: ${target:.2f} ({catch_up:+.1f}%)")
    
    return results


def compare_sectors(*sectors):
    """Compare multiple sectors to find best opportunities"""
    print(f"\n{'='*80}")
    print("🐺 CROSS-SECTOR COMPARISON")
    print(f"{'='*80}")
    
    all_opportunities = []
    
    for sector in sectors:
        tickers = get_sector_tickers(sector)
        if not tickers:
            continue
            
        results = []
        for ticker, description in tickers.items():
            metrics = analyze_ticker(ticker)
            if metrics:
                results.append({
                    'ticker': ticker,
                    'description': description,
                    'sector': sector,
                    **metrics
                })
        
        if results:
            sector_avg = sum(r['month_return'] for r in results) / len(results)
            for r in results:
                r['score'] = score_opportunity(r, sector_avg)
                r['sector_avg'] = sector_avg
            all_opportunities.extend(results)
    
    # Sort all by score
    all_opportunities.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n{'TICKER':<8} {'SECTOR':<12} {'PRICE':>10} {'1M':>8} {'SCORE':>8}")
    print("-" * 80)
    
    for r in all_opportunities[:10]:
        print(f"{r['ticker']:<8} {r['sector']:<12} ${r['price']:>8.2f} {r['month_return']:>+7.1f}% {r['score']:>7.0f}")
    
    return all_opportunities[:10]


def list_all_sectors():
    """List all available sectors and their tickers"""
    print(f"\n{'='*80}")
    print("🐺 ALL AVAILABLE SECTORS")
    print(f"{'='*80}")
    
    for sector, tickers in SECTOR_TICKERS.items():
        print(f"\n📊 {sector.upper()} ({len(tickers)} tickers)")
        print("-" * 40)
        for ticker, desc in tickers.items():
            print(f"   {ticker}: {desc}")


def add_ticker_to_sector(sector: str, ticker: str, description: str):
    """Add a new ticker to a sector (in memory only - would need to save to file)"""
    sector_lower = sector.lower().replace(' ', '_')
    if sector_lower in SECTOR_TICKERS:
        SECTOR_TICKERS[sector_lower][ticker] = description
        print(f"✅ Added {ticker} to {sector}")
    else:
        print(f"❌ Unknown sector: {sector}")
        

def main():
    parser = argparse.ArgumentParser(description='🐺 Discover opportunities in emerging sectors')
    parser.add_argument('--sector', '-s', help='Sector to analyze (e.g., photonics, quantum, space)')
    parser.add_argument('--compare', '-c', nargs='+', help='Compare multiple sectors')
    parser.add_argument('--list', '-l', action='store_true', help='List all available sectors')
    parser.add_argument('--add', nargs=3, metavar=('SECTOR', 'TICKER', 'DESC'), 
                       help='Add ticker to sector')
    
    args = parser.parse_args()
    
    if args.list:
        list_all_sectors()
    elif args.compare:
        compare_sectors(*args.compare)
    elif args.add:
        add_ticker_to_sector(args.add[0], args.add[1], args.add[2])
    elif args.sector:
        discover_sector(args.sector)
    else:
        # Default: compare hot sectors
        print("🐺 BROKKR'S SECTOR DISCOVERY ENGINE")
        print("Find laggards in hot sectors BEFORE they run")
        print()
        print("Usage:")
        print("  python3 sector_discovery.py --sector photonics")
        print("  python3 sector_discovery.py --sector quantum")
        print("  python3 sector_discovery.py --compare photonics quantum space")
        print("  python3 sector_discovery.py --list")
        print()
        
        # Quick comparison of current hot sectors
        compare_sectors('photonics', 'quantum', 'space', 'nuclear')


if __name__ == '__main__':
    main()
