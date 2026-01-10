#!/usr/bin/env python3
"""
🐺 SECTOR HUNTER - Find Tickers for ANY Sector You Can Imagine

The Pack's Philosophy:
"Every sector has public tickers. We just need to know where to look."

Data Sources:
1. ETF Holdings - Thematic ETFs reveal sector plays
2. SIC Codes - SEC industry classifications
3. Yahoo Finance - Industry screeners
4. Manual curation - Pack knowledge

Usage:
    python3 sector_hunter.py "photonics"
    python3 sector_hunter.py "humanoid robots"
    python3 sector_hunter.py "solid state batteries"
    python3 sector_hunter.py --explore  # What sectors exist?
"""

import argparse
import yfinance as yf
from datetime import datetime, timedelta
import re

# 🐺 THE PACK'S SECTOR KNOWLEDGE BASE
# This grows as we discover more sectors

SECTOR_DATABASE = {
    # ===== ENERGY =====
    'nuclear': {
        'keywords': ['nuclear', 'uranium', 'SMR', 'reactor', 'enrichment', 'fission'],
        'etfs': ['URA', 'URNM', 'NLR'],
        'tickers': {
            'CCJ': 'Cameco - Uranium giant',
            'UEC': 'Uranium Energy Corp',
            'UUUU': 'Energy Fuels - Uranium + rare earth',
            'DNN': 'Denison Mines',
            'LEU': 'Centrus - HALEU enrichment',
            'SMR': 'NuScale Power - Small modular reactors',
            'OKLO': 'Oklo - Advanced fission',
            'NNE': 'Nano Nuclear - Micro reactors',
        }
    },
    
    'solar': {
        'keywords': ['solar', 'photovoltaic', 'PV', 'renewable'],
        'etfs': ['TAN', 'ICLN'],
        'tickers': {
            'ENPH': 'Enphase Energy',
            'SEDG': 'SolarEdge',
            'FSLR': 'First Solar',
            'RUN': 'Sunrun',
            'NOVA': 'Sunnova Energy',
            'ARRY': 'Array Technologies',
        }
    },
    
    # ===== SPACE =====
    'space': {
        'keywords': ['space', 'satellite', 'rocket', 'orbital', 'lunar', 'mars'],
        'etfs': ['ARKX', 'UFO', 'ROKT'],
        'tickers': {
            'RKLB': 'Rocket Lab - Launch + spacecraft',
            'RDW': 'Redwire - Space infrastructure',
            'LUNR': 'Intuitive Machines - Lunar landers',
            'ASTS': 'AST SpaceMobile - Space cellular',
            'SPCE': 'Virgin Galactic - Space tourism',
            'MNTS': 'Momentus - In-space transport',
            'BKSY': 'BlackSky - Earth observation',
            'PL': 'Planet Labs - Earth imaging',
        }
    },
    
    # ===== COMPUTING =====
    'quantum': {
        'keywords': ['quantum', 'qubit', 'quantum computing', 'quantum processor'],
        'etfs': ['QTUM'],
        'tickers': {
            'IONQ': 'IonQ - Trapped ion quantum',
            'QUBT': 'Quantum Computing Inc - Photonics + quantum',
            'QBTS': 'D-Wave - Quantum annealing',
            'RGTI': 'Rigetti - Superconducting quantum',
            'ARQQ': 'Arqit - Quantum encryption',
        }
    },
    
    'photonics': {
        'keywords': ['photonics', 'optical', 'silicon photonics', 'laser', 'optoelectronics', 'lithium niobate'],
        'etfs': [],  # No pure-play ETF yet
        'tickers': {
            'LITE': 'Lumentum - Lasers for optical modules',
            'AAOI': 'Applied Optoelectronics - Microsoft contract',
            'GFS': 'GlobalFoundries - Silicon photonics foundry',
            'COHR': 'Coherent - Silicon photonics transceivers',
            'QUBT': 'Quantum Computing - Lithium niobate photonics!',
            'MRVL': 'Marvell - Optical interconnects',
            'IPGP': 'IPG Photonics - High-power fiber lasers',
            'CIEN': 'Ciena - Optical networking',
            'LUNA': 'Luna Innovations - Fiber optic sensing',
        }
    },
    
    'ai_chips': {
        'keywords': ['AI chip', 'GPU', 'neural', 'inference', 'accelerator', 'TPU'],
        'etfs': ['SMH', 'SOXX', 'PSI'],
        'tickers': {
            'NVDA': 'NVIDIA - GPU leader (expensive)',
            'AMD': 'AMD - GPU challenger',
            'INTC': 'Intel - Trying to compete',
            'AVGO': 'Broadcom - AI networking',
            'MRVL': 'Marvell - Custom AI chips',
            'QCOM': 'Qualcomm - Mobile AI',
            'ASML': 'ASML - Makes chip machines',
            'TSM': 'TSMC - Makes all the chips',
        }
    },
    
    # ===== ROBOTICS =====
    'robotics': {
        'keywords': ['robot', 'robotics', 'automation', 'cobot', 'industrial robot'],
        'etfs': ['ROBO', 'BOTZ', 'ARKQ'],
        'tickers': {
            'ISRG': 'Intuitive Surgical - Surgery robots',
            'ROK': 'Rockwell Automation',
            'ABB': 'ABB - Industrial robots',
            'PATH': 'UiPath - Software robots (RPA)',
            'IRBT': 'iRobot - Consumer robots',
        }
    },
    
    'humanoid_robots': {
        'keywords': ['humanoid', 'bipedal', 'android', 'atlas', 'optimus'],
        'etfs': ['BOTZ', 'ROBO'],
        'tickers': {
            'TSLA': 'Tesla - Optimus robot',
            'HYND': 'Hyundai - Boston Dynamics owner (Korean)',
            # Most humanoid robot companies are PRIVATE:
            # - Boston Dynamics (Hyundai subsidiary)
            # - Figure AI (private)
            # - Agility Robotics (private)
            # - 1X Technologies (private)
            # - Apptronik (private)
        },
        'notes': 'Most humanoid robot plays are PRIVATE. Tesla is the main public play via Optimus.'
    },
    
    # ===== DRONES =====
    'drones': {
        'keywords': ['drone', 'UAV', 'unmanned', 'UAS', 'quadcopter'],
        'etfs': ['ARKQ'],
        'tickers': {
            'AVAV': 'AeroVironment - Military drones',
            'UAVS': 'AgEagle - Drone systems',
            'JOBY': 'Joby Aviation - Air taxi',
            'LILM': 'Lilium - eVTOL',
            'ACHR': 'Archer Aviation - Urban air',
            'EVTL': 'Vertical Aerospace - eVTOL',
        }
    },
    
    # ===== MATERIALS =====
    'rare_earth': {
        'keywords': ['rare earth', 'critical minerals', 'REE', 'neodymium', 'dysprosium'],
        'etfs': ['REMX'],
        'tickers': {
            'MP': 'MP Materials - Mountain Pass mine',
            'USAR': 'USA Rare Earth - Venezuela processing',
            'UUUU': 'Energy Fuels - Rare earth + uranium',
        }
    },
    
    'lithium': {
        'keywords': ['lithium', 'battery', 'EV battery', 'lithium ion'],
        'etfs': ['LIT', 'BATT'],
        'tickers': {
            'ALB': 'Albemarle - Lithium giant',
            'SQM': 'Sociedad Quimica - Chilean lithium',
            'LAC': 'Lithium Americas',
            'LICY': 'Li-Cycle - Battery recycling',
            'QS': 'QuantumScape - Solid state battery',
        }
    },
    
    'solid_state_batteries': {
        'keywords': ['solid state battery', 'SSB', 'solid electrolyte'],
        'etfs': [],
        'tickers': {
            'QS': 'QuantumScape - Solid state leader',
            'SLDP': 'Solid Power',
            'MVST': 'Microvast',
        },
        'notes': 'Emerging sector - Toyota/Samsung doing R&D but most pure-plays are small caps'
    },
    
    # ===== BIOTECH =====
    'longevity': {
        'keywords': ['longevity', 'anti-aging', 'life extension', 'senolytics'],
        'etfs': [],
        'tickers': {
            'UNITY': 'Unity Biotechnology - Senolytics',
            'LIFE': 'aTyr Pharma',
            # Most longevity plays are private:
            # - Altos Labs (private, backed by Bezos)
            # - Calico (Alphabet subsidiary)
        },
        'notes': 'Very early sector. Most serious players are private.'
    },
    
    'crispr': {
        'keywords': ['CRISPR', 'gene editing', 'gene therapy', 'CAR-T'],
        'etfs': ['ARKG', 'XBI'],
        'tickers': {
            'CRSP': 'CRISPR Therapeutics',
            'EDIT': 'Editas Medicine',
            'NTLA': 'Intellia Therapeutics',
            'BEAM': 'Beam Therapeutics - Base editing',
            'VERV': 'Verve Therapeutics - Gene editing for heart',
        }
    },
    
    # ===== FINTECH =====
    'crypto_stocks': {
        'keywords': ['bitcoin', 'crypto', 'blockchain', 'BTC'],
        'etfs': ['BITO', 'GBTC'],
        'tickers': {
            'MSTR': 'MicroStrategy - Bitcoin treasury',
            'COIN': 'Coinbase - Crypto exchange',
            'MARA': 'Marathon Digital - BTC mining',
            'RIOT': 'Riot Platforms - BTC mining',
            'CLSK': 'CleanSpark - BTC mining',
            'HUT': 'Hut 8 - BTC mining',
        }
    },
    
    # ===== DEFENSE =====
    'defense_ai': {
        'keywords': ['defense AI', 'military AI', 'autonomous weapons', 'JADC2'],
        'etfs': ['ITA', 'XAR'],
        'tickers': {
            'PLTR': 'Palantir - Defense AI',
            'RTX': 'Raytheon - Defense giant',
            'LMT': 'Lockheed Martin',
            'NOC': 'Northrop Grumman',
            'LDOS': 'Leidos - Defense tech',
            'KTOS': 'Kratos Defense - Drones',
        }
    },
    
    'cybersecurity': {
        'keywords': ['cybersecurity', 'infosec', 'zero trust', 'endpoint'],
        'etfs': ['HACK', 'CIBR', 'BUG'],
        'tickers': {
            'CRWD': 'CrowdStrike',
            'PANW': 'Palo Alto Networks',
            'ZS': 'Zscaler',
            'FTNT': 'Fortinet',
            'S': 'SentinelOne',
            'OKTA': 'Okta - Identity',
        }
    },
}

# 🐺 SECTOR ALIASES - different ways people might say the same thing
SECTOR_ALIASES = {
    'robots': 'robotics',
    'robot': 'robotics',
    'humanoid': 'humanoid_robots',
    'atlas': 'humanoid_robots',
    'optimus': 'humanoid_robots',
    'uranium': 'nuclear',
    'smr': 'nuclear',
    'battery': 'lithium',
    'batteries': 'lithium',
    'ev': 'lithium',
    'space stocks': 'space',
    'satellites': 'space',
    'rockets': 'space',
    'gene editing': 'crispr',
    'gene therapy': 'crispr',
    'quantum computing': 'quantum',
    'qc': 'quantum',
    'optical': 'photonics',
    'light computing': 'photonics',
    'bitcoin': 'crypto_stocks',
    'btc': 'crypto_stocks',
    'crypto': 'crypto_stocks',
    'cyber': 'cybersecurity',
    'security': 'cybersecurity',
    'military': 'defense_ai',
    'defense': 'defense_ai',
    'rare earths': 'rare_earth',
    'ree': 'rare_earth',
    'critical minerals': 'rare_earth',
    'drones': 'drones',
    'uav': 'drones',
    'evtol': 'drones',
    'air taxi': 'drones',
    'solar power': 'solar',
    'solar energy': 'solar',
    'ai': 'ai_chips',
    'gpu': 'ai_chips',
    'chips': 'ai_chips',
    'semiconductors': 'ai_chips',
    'aging': 'longevity',
    'anti-aging': 'longevity',
    'ssb': 'solid_state_batteries',
    'solid state': 'solid_state_batteries',
}


def normalize_sector(query: str) -> str:
    """Convert user query to sector key"""
    query = query.lower().strip().replace('-', '_').replace(' ', '_')
    
    # Check aliases first
    if query in SECTOR_ALIASES:
        return SECTOR_ALIASES[query]
    
    # Check if it's already a valid sector
    if query in SECTOR_DATABASE:
        return query
    
    # Fuzzy match - check if query is contained in any sector name
    for sector in SECTOR_DATABASE.keys():
        if query in sector or sector in query:
            return sector
    
    # Check if query matches any keywords
    for sector, data in SECTOR_DATABASE.items():
        for keyword in data.get('keywords', []):
            if query in keyword.lower() or keyword.lower() in query:
                return sector
    
    return None


def search_sector(query: str):
    """Search for a sector and return its tickers"""
    sector = normalize_sector(query)
    
    if not sector:
        print(f"\n❌ Unknown sector: '{query}'")
        print("\n💡 Try one of these:")
        for s in sorted(SECTOR_DATABASE.keys()):
            print(f"   • {s.replace('_', ' ')}")
        print("\n🐺 TIP: Ask Fenrir to research new sectors!")
        return None
    
    data = SECTOR_DATABASE[sector]
    
    print(f"\n{'='*80}")
    print(f"🐺 SECTOR: {sector.upper().replace('_', ' ')}")
    print(f"{'='*80}")
    
    # Show keywords
    if data.get('keywords'):
        print(f"\n🔑 Keywords: {', '.join(data['keywords'][:5])}")
    
    # Show ETFs
    if data.get('etfs'):
        print(f"\n📦 Tracking ETFs: {', '.join(data['etfs'])}")
    
    # Show notes if any
    if data.get('notes'):
        print(f"\n⚠️  Note: {data['notes']}")
    
    # Show tickers
    print(f"\n📊 PUBLIC TICKERS ({len(data['tickers'])}):")
    print("-" * 60)
    
    tickers_data = []
    for ticker, desc in data['tickers'].items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='5d')
            if len(hist) >= 2:
                price = hist['Close'].iloc[-1]
                week_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                tickers_data.append({
                    'ticker': ticker,
                    'desc': desc,
                    'price': price,
                    'week': week_change
                })
        except:
            tickers_data.append({
                'ticker': ticker,
                'desc': desc,
                'price': 0,
                'week': 0
            })
    
    # Sort by week performance to find laggards
    tickers_data.sort(key=lambda x: x['week'])
    
    for t in tickers_data:
        lag = "⬇️ LAGGARD" if t['week'] < 0 else ""
        hot = "🔥 HOT" if t['week'] > 10 else ""
        print(f"   {t['ticker']:<6} ${t['price']:>8.2f}  {t['week']:>+6.1f}%  {t['desc'][:35]} {lag}{hot}")
    
    return data


def explore_all_sectors():
    """Show all available sectors"""
    print(f"\n{'='*80}")
    print("🐺 ALL SECTORS IN THE PACK'S KNOWLEDGE BASE")
    print(f"{'='*80}")
    
    # Group by category
    categories = {
        'ENERGY': ['nuclear', 'solar'],
        'SPACE': ['space'],
        'COMPUTING': ['quantum', 'photonics', 'ai_chips'],
        'ROBOTICS': ['robotics', 'humanoid_robots', 'drones'],
        'MATERIALS': ['rare_earth', 'lithium', 'solid_state_batteries'],
        'BIOTECH': ['longevity', 'crispr'],
        'FINTECH': ['crypto_stocks'],
        'DEFENSE': ['defense_ai', 'cybersecurity'],
    }
    
    for category, sectors in categories.items():
        print(f"\n📁 {category}")
        print("-" * 40)
        for sector in sectors:
            if sector in SECTOR_DATABASE:
                data = SECTOR_DATABASE[sector]
                ticker_count = len(data.get('tickers', {}))
                etf_count = len(data.get('etfs', []))
                print(f"   • {sector.replace('_', ' '):<25} {ticker_count} tickers, {etf_count} ETFs")


def add_sector_interactive():
    """Guide user to add a new sector"""
    print(f"\n{'='*80}")
    print("🐺 ADD NEW SECTOR TO DATABASE")
    print(f"{'='*80}")
    print("""
To add a new sector, you need:
1. Sector name (e.g., "photonics")
2. Keywords (terms that identify stocks in this sector)
3. ETFs that track this sector (if any)
4. Tickers and descriptions

Here's the format to add to sector_hunter.py:

    'your_sector': {
        'keywords': ['keyword1', 'keyword2'],
        'etfs': ['ETF1', 'ETF2'],
        'tickers': {
            'TICK1': 'Description of company 1',
            'TICK2': 'Description of company 2',
        }
    },

🐺 WHERE TO FIND TICKERS FOR A NEW SECTOR:

1. ETF Holdings:
   - Go to etf.com and search for thematic ETFs
   - Look at top 10 holdings
   
2. Yahoo Finance Screener:
   - finance.yahoo.com/screener
   - Filter by industry
   
3. SEC EDGAR:
   - Search by SIC code (industry classification)
   
4. Google:
   - "[sector name] stocks publicly traded 2026"
   - "[sector name] ETF holdings"
   
5. Ask Fenrir:
   - "Search for [sector] companies stocks"
""")


def find_laggards_across_sectors():
    """Find the biggest laggards across all sectors"""
    print(f"\n{'='*80}")
    print("🐺 CROSS-SECTOR LAGGARD HUNT")
    print(f"{'='*80}")
    print("\nFinding stocks that HAVEN'T run yet across all sectors...\n")
    
    all_laggards = []
    
    for sector, data in SECTOR_DATABASE.items():
        for ticker, desc in data.get('tickers', {}).items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1mo')
                if len(hist) >= 5:
                    price = hist['Close'].iloc[-1]
                    month_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                    
                    # Only include laggards (down or flat)
                    if month_change < 5:
                        all_laggards.append({
                            'ticker': ticker,
                            'sector': sector,
                            'price': price,
                            'month': month_change,
                            'desc': desc[:30]
                        })
            except:
                pass
    
    # Sort by month change (most laggard first)
    all_laggards.sort(key=lambda x: x['month'])
    
    print(f"{'TICKER':<8} {'SECTOR':<18} {'PRICE':>10} {'1-MONTH':>10}")
    print("-" * 60)
    
    for lag in all_laggards[:15]:
        print(f"{lag['ticker']:<8} {lag['sector']:<18} ${lag['price']:>8.2f} {lag['month']:>+9.1f}%")
    
    print(f"\n🎯 These are stocks that HAVEN'T moved while their sectors heat up.")
    print("   They're either:\n   a) About to catch up (BUY) or\n   b) Broken for a reason (AVOID)")


def main():
    parser = argparse.ArgumentParser(
        description='🐺 Find tickers for ANY sector',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 sector_hunter.py "photonics"
  python3 sector_hunter.py "humanoid robots"  
  python3 sector_hunter.py "solid state batteries"
  python3 sector_hunter.py --explore
  python3 sector_hunter.py --laggards
        """
    )
    parser.add_argument('sector', nargs='?', help='Sector to search for')
    parser.add_argument('--explore', '-e', action='store_true', help='Show all available sectors')
    parser.add_argument('--add', '-a', action='store_true', help='Guide to add new sector')
    parser.add_argument('--laggards', '-l', action='store_true', help='Find laggards across all sectors')
    
    args = parser.parse_args()
    
    if args.explore:
        explore_all_sectors()
    elif args.add:
        add_sector_interactive()
    elif args.laggards:
        find_laggards_across_sectors()
    elif args.sector:
        search_sector(args.sector)
    else:
        print("🐺 SECTOR HUNTER - Find tickers for ANY sector")
        print()
        print("Usage:")
        print("  python3 sector_hunter.py 'photonics'")
        print("  python3 sector_hunter.py 'quantum'")
        print("  python3 sector_hunter.py --explore   # see all sectors")
        print("  python3 sector_hunter.py --laggards  # find laggards")
        print()
        explore_all_sectors()


if __name__ == '__main__':
    main()
