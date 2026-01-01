#!/usr/bin/env python3
"""
🐺 WOLF PACK MASTER TICKER LIST
For Insider Cluster Hunter validation
Give this to Sonnet in VS Code
Last Updated: January 2, 2026
"""

# ==============================================================
# FULL WATCHLIST - ALL SECTORS
# ==============================================================

WOLF_PACK_WATCHLIST = [
    # ============================================
    # AI / MACHINE LEARNING (Our Core Thesis)
    # ============================================
    "PLTR",   # Palantir - AI defense
    "AI",     # C3.ai
    "PATH",   # UiPath - AI automation
    "SOUN",   # SoundHound - AI voice
    "BBAI",   # BigBear.ai - Defense AI
    "UPST",   # Upstart - AI lending
    "SNOW",   # Snowflake - AI data
    "MDB",    # MongoDB - AI databases
    "DDOG",   # Datadog - AI monitoring
    "CRWD",   # CrowdStrike - AI security
    "S",      # SentinelOne - AI security
    "AISP",   # Airship AI - Border security AI 🔥 INSIDER BUYING
    "GFAI",   # Guardforce AI
    "BTAI",   # BioXcel Therapeutics
    "VCNX",   # Vaccinex
    "AEHR",   # Aehr Test Systems
    
    # ============================================
    # NUCLEAR / SMR (AI Power Demand Thesis)
    # ============================================
    "SMR",    # NuScale Power - SMR leader
    "CCJ",    # Cameco - Uranium major
    "LEU",    # Centrus Energy - Enrichment
    "UUUU",   # Energy Fuels - Uranium
    "DNN",    # Denison Mines
    "NNE",    # Nano Nuclear Energy
    "OKLO",   # Oklo - Advanced reactors
    "UEC",    # Uranium Energy Corp
    "URG",    # Ur-Energy
    "NXE",    # NexGen Energy
    "BWXT",   # BWX Technologies
    "CEG",    # Constellation Energy
    "VST",    # Vistra Corp
    "NRG",    # NRG Energy
    
    # ============================================
    # SPACE (Lunar Economy Thesis)
    # ============================================
    "LUNR",   # Intuitive Machines - Current position
    "RKLB",   # Rocket Lab
    "ASTS",   # AST SpaceMobile
    "RDW",    # Redwire
    "LLAP",   # Terran Orbital
    "MNTS",   # Momentus
    "SPCE",   # Virgin Galactic
    "PL",     # Planet Labs
    "BKSY",   # BlackSky
    "IRDM",   # Iridium
    "GSAT",   # Globalstar
    "SATL",   # Satellogic
    "ASTR",   # Astra Space
    
    # ============================================
    # QUANTUM COMPUTING
    # ============================================
    "IONQ",   # IonQ - Trapped ion
    "RGTI",   # Rigetti - Superconducting
    "QBTS",   # D-Wave - Annealing
    "ARQQ",   # Arqit Quantum
    "QUBT",   # Quantum Computing Inc
    
    # ============================================
    # DEFENSE / GOVERNMENT CONTRACTORS
    # ============================================
    "LMT",    # Lockheed Martin
    "RTX",    # Raytheon
    "NOC",    # Northrop Grumman
    "GD",     # General Dynamics
    "BA",     # Boeing
    "LHX",    # L3Harris
    "KTOS",   # Kratos Defense
    "LDOS",   # Leidos
    "SAIC",   # Science Applications
    "PSN",    # Parsons Corp
    "CACI",   # CACI International
    "BAH",    # Booz Allen
    "MRCY",   # Mercury Systems
    "AVAV",   # AeroVironment - Drones
    
    # ============================================
    # NATURAL GAS (Winter Thesis)
    # ============================================
    "AR",     # Antero Resources
    "EQT",    # EQT Corporation
    "RRC",    # Range Resources
    "SWN",    # Southwestern Energy
    "CHK",    # Chesapeake Energy
    "CNX",    # CNX Resources
    "CTRA",   # Coterra Energy
    "DVN",    # Devon Energy
    "FANG",   # Diamondback Energy
    "EOG",    # EOG Resources
    
    # ============================================
    # AI INFRASTRUCTURE (Cooling, Power, Memory)
    # ============================================
    "VRT",    # Vertiv - Data center cooling
    "DELL",   # Dell - AI servers
    "SMCI",   # Super Micro - AI servers
    "MU",     # Micron - Memory
    "ANET",   # Arista Networks - Data center networking
    "CRDO",   # Credo Technology
    "RMBS",   # Rambus - Memory interface
    "ONTO",   # Onto Innovation
    "KLAC",   # KLA Corp
    "LRCX",   # Lam Research
    "AMAT",   # Applied Materials
    "ASML",   # ASML Holding
    "NVDA",   # NVIDIA
    "AMD",    # AMD
    "INTC",   # Intel
    "MRVL",   # Marvell
    "AVGO",   # Broadcom
    "QCOM",   # Qualcomm
    "ARM",    # Arm Holdings
    
    # ============================================
    # FINTECH / SPECULATIVE GROWTH
    # ============================================
    "SOFI",   # SoFi
    "HOOD",   # Robinhood
    "AFRM",   # Affirm
    "NU",     # Nu Holdings
    "COIN",   # Coinbase
    
    # ============================================
    # BIOTECH (High Risk/Reward)
    # ============================================
    "DNA",    # Ginkgo Bioworks
    "CRSP",   # CRISPR Therapeutics
    "EDIT",   # Editas Medicine
    "NTLA",   # Intellia Therapeutics
    "BEAM",   # Beam Therapeutics
    
    # ============================================
    # INSIDER BUYING DETECTED (From Tonight's Scan)
    # ============================================
    "AISP",   # Airship AI - $433K insider buying 🔥
    "EFOI",   # Energy Focus - $1.7M+ CEO buying 🔥
    "TPVG",   # TriplePoint Venture - $2.1M C-Suite
    "BOC",    # Boston Omaha - $1.3M 3 insiders
    "ANDG",   # Andersen Group - $7.9M 4 insiders
    "BNTC",   # Benitec Biopharma - $2.4M
    "CLPR",   # Clipper Realty - $216K
    "DMLP",   # Dorchester Minerals - $779K
    "EPD",    # Enterprise Products - $481K
    "EPSN",   # Epsilon Energy - $131K
    "SLGL",   # Sol-Gel Technologies - $2.9M
    "AVO",    # Mission Produce - $2.3M
    
    # ============================================
    # MEME / MOMENTUM PLAYS (Watch Only)
    # ============================================
    "SIDU",   # Sidus Space - +395% monthly
    "GME",    # GameStop
    "AMC",    # AMC Entertainment
    
    # ============================================
    # VALUE / TURNAROUND
    # ============================================
    "UA",     # Under Armour - Prem Watsa accumulation
    "PARA",   # Paramount
    "WBD",    # Warner Bros Discovery
]

# ==============================================================
# PRIORITY TICKERS (Our Core Focus - $2-20 Range)
# ==============================================================

PRIORITY_WATCHLIST = [
    # Wounded Prey Candidates
    "SMR",    # -21.6% December
    "SOUN",   # -13.5% December  
    "BBAI",   # -10.7% December
    "RGTI",   # -5.5% December
    "DNA",    # -3.9% December
    
    # Current Positions
    "LUNR",   # 10 shares @ $16.85
    "UA",     # Small position
    
    # Insider Validated (NEW!)
    "AISP",   # $2.74 - $433K insider buying 🔥
    "EFOI",   # $2.29 - $1.7M CEO buying 🔥
    
    # High Momentum
    "SIDU",   # +395% monthly (CAUTION)
    "QBTS",   # Quantum hype
    "IONQ",   # Quantum leader
    
    # AI Fuel Chain
    "VRT",    # Vertiv cooling
    "CCJ",    # Cameco uranium
    "AR",     # Antero nat gas
]

# ==============================================================
# QUICK COPY - COMMA SEPARATED
# ==============================================================

COMMA_SEPARATED = "PLTR,AI,PATH,SOUN,BBAI,UPST,SNOW,MDB,DDOG,CRWD,S,AISP,GFAI,BTAI,VCNX,AEHR,SMR,CCJ,LEU,UUUU,DNN,NNE,OKLO,UEC,URG,NXE,BWXT,CEG,VST,NRG,LUNR,RKLB,ASTS,RDW,LLAP,MNTS,SPCE,PL,BKSY,IRDM,GSAT,SATL,ASTR,IONQ,RGTI,QBTS,ARQQ,QUBT,LMT,RTX,NOC,GD,BA,LHX,KTOS,LDOS,SAIC,PSN,CACI,BAH,MRCY,AVAV,AR,EQT,RRC,SWN,CHK,CNX,CTRA,DVN,FANG,EOG,VRT,DELL,SMCI,MU,ANET,CRDO,RMBS,ONTO,KLAC,LRCX,AMAT,ASML,NVDA,AMD,INTC,MRVL,AVGO,QCOM,ARM,SOFI,HOOD,AFRM,NU,COIN,DNA,CRSP,EDIT,NTLA,BEAM,AISP,EFOI,TPVG,BOC,ANDG,BNTC,CLPR,DMLP,EPD,EPSN,SLGL,AVO,SIDU,GME,AMC,UA,PARA,WBD"

# ==============================================================
# USAGE EXAMPLES
# ==============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🐺 WOLF PACK TICKER LIST")
    print("=" * 70)
    print(f"\nTotal tickers: {len(WOLF_PACK_WATCHLIST)}")
    print(f"Priority tickers: {len(PRIORITY_WATCHLIST)}")
    
    print("\n" + "-" * 70)
    print("USAGE EXAMPLES:")
    print("-" * 70)
    
    print("\n1. Validate priority tickers:")
    print("   python3 insider_cluster_hunter.py --validate " + " ".join(PRIORITY_WATCHLIST[:5]))
    
    print("\n2. Validate wounded prey specifically:")
    print("   python3 insider_cluster_hunter.py --validate SMR SOUN BBAI RGTI DNA")
    
    print("\n3. Full cluster scan:")
    print("   python3 insider_cluster_hunter.py --scan")
    
    print("\n4. Validate with wounded prey cross-reference:")
    print("   python3 insider_cluster_hunter.py --validate SMR SOUN --wounded-prey SMR SOUN BBAI")
    
    print("\n" + "-" * 70)
    print("PRIORITY TICKERS TO VALIDATE:")
    print("-" * 70)
    for ticker in PRIORITY_WATCHLIST:
        print(f"  {ticker}")
    
    print("\n" + "=" * 70)
    print("Copy the comma-separated list for batch processing:")
    print("=" * 70)
    print(COMMA_SEPARATED)
