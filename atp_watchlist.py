#!/usr/bin/env python3
"""
🐺 WOLF PACK ATP PRO WATCHLIST GENERATOR v1.0
Generates watchlists formatted for Fidelity Active Trader Pro

Creates multiple watchlist files organized by:
- Sector/Theme
- Price range
- Signal strength
- Custom criteria

Output formats:
- CSV (ATP Pro import)
- TXT (simple list)
- JSON (full data)

Usage:
    python atp_watchlist.py                    # Generate all watchlists
    python atp_watchlist.py --sector defense   # Defense only
    python atp_watchlist.py --price-max 20     # Under $20 only

AWOOOO 🐺
"""

import argparse
import csv
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

try:
    import yfinance as yf
except ImportError:
    print("❌ yfinance not installed!")
    print("Run: pip install yfinance --break-system-packages")
    yf = None


# ============================================================
# WATCHLIST DEFINITIONS
# ============================================================

WATCHLISTS = {
    # === TYR'S PRICE RANGE ($2-20) ===
    'tyrs_range': {
        'name': "Tyr's Range ($2-20)",
        'description': 'Stocks in Tyrs trading range for small account',
        'tickers': [
            'BBAI',   # BigBear AI ~$5
            'SOUN',   # SoundHound ~$10
            'LUNR',   # Intuitive Machines ~$16
            'SIDU',   # Sidus Space ~$3
            'RIG',    # Transocean ~$4
            'TELL',   # Tellurian ~$1
            'GSAT',   # Globalstar ~$2
            'DNA',    # Ginkgo Bioworks ~$8
            'OPEN',   # Opendoor ~$2
            'SOFI',   # SoFi ~$15
        ]
    },
    
    # === AI INFRASTRUCTURE (THE FUEL) ===
    'ai_fuel': {
        'name': 'AI Fuel Chain',
        'description': 'AI infrastructure - memory, cooling, power',
        'tickers': [
            # Memory
            'MU',     # Micron - HBM king
            'WDC',    # Western Digital
            'STX',    # Seagate
            # Cooling
            'VRT',    # Vertiv - #1 AI cooling
            'TT',     # Trane Technologies
            'ETN',    # Eaton
            # Networking
            'AVGO',   # Broadcom
            'MRVL',   # Marvell
            'ANET',   # Arista Networks
        ]
    },
    
    # === DEFENSE ===
    'defense': {
        'name': 'Defense & Aerospace',
        'description': '$924.7B budget, global rearmament',
        'tickers': [
            'NOC',    # Northrop - MS #1 pick
            'RTX',    # RTX - $251B backlog
            'LHX',    # L3Harris
            'GD',     # General Dynamics
            'LMT',    # Lockheed
            'KTOS',   # Kratos - drones
            'PLTR',   # Palantir - AI defense
            'BBAI',   # BigBear AI
        ]
    },
    
    # === SPACE ===
    'space': {
        'name': 'Space & Satellites',
        'description': 'Launch, lunar, satellites',
        'tickers': [
            'RKLB',   # Rocket Lab
            'LUNR',   # Intuitive Machines
            'ASTS',   # AST SpaceMobile
            'SPCE',   # Virgin Galactic
            'RDW',    # Redwire
            'BKSY',   # BlackSky
        ]
    },
    
    # === NUCLEAR/ENERGY ===
    'nuclear': {
        'name': 'Nuclear & Power',
        'description': 'AI power demand play',
        'tickers': [
            'CCJ',    # Cameco - uranium
            'LEU',    # Centrus - HALEU
            'OKLO',   # Oklo - SMR
            'SMR',    # NuScale
            'VST',    # Vistra
            'CEG',    # Constellation
            'GEV',    # GE Vernova
        ]
    },
    
    # === NATURAL GAS ===
    'natgas': {
        'name': 'Natural Gas',
        'description': 'LNG export boom',
        'tickers': [
            'AR',     # Antero Resources
            'EQT',    # EQT Corp
            'RRC',    # Range Resources
            'SWN',    # Southwestern
            'CHK',    # Chesapeake
            'LNG',    # Cheniere
        ]
    },
    
    # === TAX LOSS BOUNCE ===
    'bounce': {
        'name': 'Tax Loss Bounce Plays',
        'description': 'Oversold Q4, wash sale ends Jan 24',
        'tickers': [
            'TTD',    # Trade Desk -68%
            'NKE',    # Nike + insider buying
            'CMG',    # Chipotle -48%
            'DECK',   # Deckers -50%
            'LULU',   # Lululemon -45%
        ]
    },
    
    # === QUANTUM (CAUTION) ===
    'quantum': {
        'name': 'Quantum (EXTREME CAUTION)',
        'description': 'Bubble territory - lottery only',
        'tickers': [
            'IONQ',   # IonQ
            'RGTI',   # Rigetti
            'QBTS',   # D-Wave
        ]
    },
    
    # === MARKET PULSE (INDICES) ===
    'pulse': {
        'name': 'Market Pulse',
        'description': 'Index tracking',
        'tickers': [
            'SPY',    # S&P 500
            'QQQ',    # Nasdaq 100
            'IWM',    # Russell 2000
            'DIA',    # Dow Jones
            'VIX',    # Volatility
        ]
    },
}


# ============================================================
# PRICE DATA FETCHER
# ============================================================

def get_ticker_data(ticker: str) -> Optional[Dict]:
    """
    Get current data for a ticker.
    """
    if yf is None:
        return {'ticker': ticker, 'price': 0, 'change': 0}
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        prev_close = info.get('previousClose', price)
        change = ((price - prev_close) / prev_close * 100) if prev_close else 0
        
        return {
            'ticker': ticker,
            'name': info.get('shortName', ticker)[:30],
            'price': round(price, 2) if price else 0,
            'change': round(change, 2),
            'volume': info.get('regularMarketVolume', 0),
            'avg_volume': info.get('averageVolume', 0),
            'market_cap': info.get('marketCap', 0),
            '52w_high': info.get('fiftyTwoWeekHigh', 0),
            '52w_low': info.get('fiftyTwoWeekLow', 0),
        }
    except Exception as e:
        return {'ticker': ticker, 'price': 0, 'change': 0, 'error': str(e)}


# ============================================================
# EXPORT FUNCTIONS
# ============================================================

def export_to_csv(watchlist_name: str, tickers: List[str], output_dir: str = '.'):
    """
    Export watchlist to CSV format for ATP Pro import.
    
    ATP Pro CSV format: Symbol (one per line or comma-separated)
    """
    filename = os.path.join(output_dir, f"ATP_{watchlist_name}.csv")
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Symbol'])  # Header
        for ticker in tickers:
            writer.writerow([ticker])
    
    print(f"   ✅ {filename}")
    return filename


def export_to_txt(watchlist_name: str, tickers: List[str], output_dir: str = '.'):
    """
    Export watchlist to TXT format (simple list).
    """
    filename = os.path.join(output_dir, f"ATP_{watchlist_name}.txt")
    
    with open(filename, 'w') as f:
        for ticker in tickers:
            f.write(f"{ticker}\n")
    
    print(f"   ✅ {filename}")
    return filename


def export_to_json(watchlist_name: str, data: Dict, output_dir: str = '.'):
    """
    Export watchlist with full data to JSON.
    """
    filename = os.path.join(output_dir, f"ATP_{watchlist_name}.json")
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"   ✅ {filename}")
    return filename


def export_combined_csv(all_tickers: List[str], output_dir: str = '.'):
    """
    Export all unique tickers to one master CSV.
    """
    unique = sorted(list(set(all_tickers)))
    filename = os.path.join(output_dir, "ATP_WOLF_PACK_MASTER.csv")
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Symbol'])
        for ticker in unique:
            writer.writerow([ticker])
    
    print(f"   ✅ {filename} ({len(unique)} unique tickers)")
    return filename


# ============================================================
# DISPLAY FUNCTIONS
# ============================================================

def display_watchlist(name: str, data: Dict, with_prices: bool = False):
    """
    Display a watchlist with optional price data.
    """
    print(f"\n{'='*60}")
    print(f"📋 {data['name']}")
    print(f"{'='*60}")
    print(f"Description: {data['description']}")
    print(f"Tickers: {len(data['tickers'])}")
    print("-" * 60)
    
    if with_prices and yf:
        print(f"{'Ticker':<8} {'Price':>10} {'Change':>8} {'Name':<25}")
        print("-" * 60)
        for ticker in data['tickers']:
            info = get_ticker_data(ticker)
            if info:
                change_str = f"{info.get('change', 0):+.2f}%"
                print(f"{ticker:<8} ${info.get('price', 0):>9.2f} {change_str:>8} {info.get('name', '')[:25]:<25}")
    else:
        # Simple list
        for i, ticker in enumerate(data['tickers'], 1):
            print(f"   {i:2}. {ticker}")
    
    print()


# ============================================================
# MAIN GENERATOR
# ============================================================

def generate_all_watchlists(output_dir: str = '.', with_prices: bool = False):
    """
    Generate all watchlist files.
    """
    print(f"\n🐺 WOLF PACK ATP PRO WATCHLIST GENERATOR")
    print(f"=" * 60)
    print(f"Output directory: {output_dir}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"=" * 60)
    
    # Create output directory if needed
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    all_tickers = []
    
    for key, data in WATCHLISTS.items():
        print(f"\n📋 Generating: {data['name']}")
        
        # Display
        if with_prices:
            display_watchlist(key, data, with_prices=True)
        
        # Export CSV for ATP Pro
        export_to_csv(key, data['tickers'], output_dir)
        
        # Export TXT
        export_to_txt(key, data['tickers'], output_dir)
        
        # Collect all tickers
        all_tickers.extend(data['tickers'])
    
    # Master list
    print(f"\n📋 Generating: Master List")
    export_combined_csv(all_tickers, output_dir)
    
    # Summary
    unique_count = len(set(all_tickers))
    print(f"\n{'='*60}")
    print(f"✅ GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"Watchlists created: {len(WATCHLISTS)}")
    print(f"Total tickers: {len(all_tickers)}")
    print(f"Unique tickers: {unique_count}")
    print(f"\nFiles saved to: {output_dir}/")
    
    # ATP Import instructions
    print(f"\n📖 HOW TO IMPORT INTO ATP PRO:")
    print(f"-" * 60)
    print(f"1. Open Active Trader Pro")
    print(f"2. Go to Trade & Orders > Directed Trade")
    print(f"3. Click 'Watch Lists' in top menu")
    print(f"4. Click '+' to create new watchlist")
    print(f"5. Name it (e.g., 'Wolf Pack - Defense')")
    print(f"6. Click 'Import' button")
    print(f"7. Select the CSV file (e.g., ATP_defense.csv)")
    print(f"8. Tickers are now loaded!")
    print(f"\nRepeat for each sector watchlist.")
    
    print(f"\n🐺 AWOOOO - Watchlists ready for the hunt!")


def generate_filtered_watchlist(
    price_min: float = 0,
    price_max: float = float('inf'),
    sectors: List[str] = None,
    output_dir: str = '.'
):
    """
    Generate a filtered watchlist based on criteria.
    """
    print(f"\n🐺 GENERATING FILTERED WATCHLIST")
    print(f"=" * 60)
    print(f"Price range: ${price_min} - ${price_max}")
    
    filtered_tickers = []
    
    # Collect tickers from selected sectors
    if sectors:
        for sector in sectors:
            if sector in WATCHLISTS:
                filtered_tickers.extend(WATCHLISTS[sector]['tickers'])
    else:
        # All sectors
        for data in WATCHLISTS.values():
            filtered_tickers.extend(data['tickers'])
    
    # Remove duplicates
    filtered_tickers = list(set(filtered_tickers))
    
    # Filter by price if yfinance available
    if yf and (price_min > 0 or price_max < float('inf')):
        print(f"\nFiltering by price...")
        final_tickers = []
        
        for ticker in filtered_tickers:
            data = get_ticker_data(ticker)
            price = data.get('price', 0)
            
            if price_min <= price <= price_max:
                final_tickers.append(ticker)
                print(f"   ✅ {ticker}: ${price}")
            else:
                print(f"   ❌ {ticker}: ${price} (outside range)")
        
        filtered_tickers = final_tickers
    
    # Export
    if filtered_tickers:
        filename = f"ATP_filtered_{price_min}-{price_max}"
        export_to_csv(filename, filtered_tickers, output_dir)
        print(f"\n✅ Generated filtered watchlist: {len(filtered_tickers)} tickers")
    else:
        print(f"\n❌ No tickers match the criteria")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='🐺 Wolf Pack ATP Pro Watchlist Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available sectors:
  tyrs_range  - Stocks in $2-20 range
  ai_fuel     - AI infrastructure (MU, VRT, etc.)
  defense     - Defense & aerospace
  space       - Space & satellites
  nuclear     - Nuclear & power
  natgas      - Natural gas
  bounce      - Tax loss bounce plays
  quantum     - Quantum (CAUTION)
  pulse       - Market indices

Examples:
    python atp_watchlist.py                      # Generate all
    python atp_watchlist.py --sector defense     # Defense only
    python atp_watchlist.py --price-max 20       # Under $20
    python atp_watchlist.py --prices             # Show current prices
    python atp_watchlist.py --output ./lists     # Custom output dir

AWOOOO 🐺
        """
    )
    
    parser.add_argument('--sector', type=str, nargs='+',
                        help='Specific sector(s) to generate')
    parser.add_argument('--price-min', type=float, default=0,
                        help='Minimum price filter')
    parser.add_argument('--price-max', type=float, default=float('inf'),
                        help='Maximum price filter')
    parser.add_argument('--output', type=str, default='.',
                        help='Output directory (default: current)')
    parser.add_argument('--prices', action='store_true',
                        help='Fetch and display current prices')
    parser.add_argument('--list-sectors', action='store_true',
                        help='List available sectors')
    
    args = parser.parse_args()
    
    # List sectors
    if args.list_sectors:
        print("\n📋 Available Sectors:")
        for key, data in WATCHLISTS.items():
            print(f"   {key:<15} - {data['name']} ({len(data['tickers'])} tickers)")
        return
    
    # Filtered generation
    if args.sector or args.price_min > 0 or args.price_max < float('inf'):
        generate_filtered_watchlist(
            price_min=args.price_min,
            price_max=args.price_max,
            sectors=args.sector,
            output_dir=args.output
        )
    else:
        # Full generation
        generate_all_watchlists(
            output_dir=args.output,
            with_prices=args.prices
        )


if __name__ == "__main__":
    main()
