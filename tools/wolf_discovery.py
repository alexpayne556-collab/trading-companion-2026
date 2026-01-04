#!/usr/bin/env python3
"""
🐺 WOLF DISCOVERY - Find Trapped Players ANYWHERE
==================================================

Don't start with our list.
Start with FILTERS that find trapped players.

WHAT TRAPS PLAYERS:
1. HIGH SHORT INTEREST (>15%) - They MUST cover
2. LOW FLOAT (<50M shares) - Small door, big crowd  
3. PRICE RISING + HIGH SI - Shorts bleeding NOW
4. UNUSUAL VOLUME - Something is happening
5. SECTOR HOT - Institutions rotating in

We scan EVERYTHING and filter down to trapped players.

Built by Fenrir for Tyr.
$1,316 to deploy. Make it count.
AWOOOO 🐺
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import time
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# EXPANDED UNIVERSE - Cast a Wide Net
# ============================================================================

# Our core sectors (what we know)
CORE_UNIVERSE = {
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ', 'LAES'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'BKSY', 'ASTS', 'SPIR', 'SIDU', 'SATL', 'MNTS', 'PL'],
    'NUCLEAR': ['LEU', 'CCJ', 'UUUU', 'UEC', 'SMR', 'OKLO', 'NNE', 'DNN', 'NXE', 'LTBR'],
    'AI_INFRA': ['SMCI', 'VRT', 'PWR', 'SOUN', 'AI', 'PATH', 'UPST', 'BBAI', 'BIGC'],
    'SEMICONDUCTORS': ['MU', 'AMD', 'ARM', 'MRVL', 'ALAB', 'CRDO', 'WOLF', 'ACLS'],
    # CRYPTO removed - user preference: "dying breed"
    'DEFENSE_AI': ['PLTR', 'KTOS', 'RCAT', 'AVAV', 'NNOX'],
    'BIOTECH': ['CRSP', 'EDIT', 'NTLA', 'BEAM', 'VERV', 'RXRX'],
    'FINTECH': ['SOFI', 'AFRM', 'NU', 'UPST', 'LC'],
    'EV_CLEAN': ['RIVN', 'LCID', 'PLUG', 'FCEL', 'BE', 'CHPT', 'QS'],
}

# KNOWN HIGH SHORT INTEREST NAMES (expand our hunting ground)
HIGH_SHORT_WATCHLIST = [
    # Meme/Squeeze history
    'GME', 'AMC', 'BBBY', 'KOSS', 'EXPR', 'BB',
    # NO CRYPTO - user says "dying breed"
    # EV (shorts love these)
    'RIVN', 'LCID', 'FSR', 'NKLA', 'GOEV', 'FFIE', 'MULN',
    # Biotech (binary events)
    'SAVA', 'SRPT', 'NVAX', 'MRNA',
    # Tech fallen angels
    'CVNA', 'UPST', 'AFRM', 'HOOD', 'PATH', 'DOCS',
    # Small cap tech
    'BIGC', 'NNOX', 'VIEW', 'ARRY', 'RUN',
    # Defense/Space small caps
    'RCAT', 'LUNR', 'ASTS', 'SPIR', 'RDW',
    # Random high short
    'BYND', 'FUBO', 'CLOV', 'WISH', 'SDC', 'OPEN',
]

# RECENT IPOs and SPACs (often heavily shorted)
RECENT_PLAYS = [
    'RDDT', 'ARM', 'BIRK', 'CART', 'KVYO', 'TOST',
]

# Combine everything
ALL_DISCOVERY = list(set(
    [t for tickers in CORE_UNIVERSE.values() for t in tickers] +
    HIGH_SHORT_WATCHLIST +
    RECENT_PLAYS
))

print(f"🐺 Discovery Universe: {len(ALL_DISCOVERY)} tickers")

# ============================================================================
# DATA COLLECTION
# ============================================================================

def get_stock_metrics(ticker: str) -> dict:
    """Get all metrics we need to identify trapped players"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period='1mo')
        
        if hist.empty or len(hist) < 5:
            return None
        
        current = hist['Close'].iloc[-1]
        
        # Core metrics
        data = {
            'ticker': ticker,
            'price': current,
            'market_cap': info.get('marketCap', 0) or 0,
            
            # Float and shares
            'float': info.get('floatShares', 0) or 0,
            'shares_out': info.get('sharesOutstanding', 0) or 0,
            
            # SHORT DATA - THE KEY
            'short_percent': (info.get('shortPercentOfFloat', 0) or 0) * 100,
            'short_ratio': info.get('shortRatio', 0) or 0,  # Days to cover
            
            # Volume
            'avg_volume': info.get('averageVolume', 0) or 0,
            'volume_today': hist['Volume'].iloc[-1] if not hist.empty else 0,
            
            # Price action
            'change_1d': 0,
            'change_5d': 0,
            'change_20d': 0,
        }
        
        # Calculate returns
        if len(hist) >= 2:
            data['change_1d'] = (current / hist['Close'].iloc[-2] - 1) * 100
        if len(hist) >= 5:
            data['change_5d'] = (current / hist['Close'].iloc[-5] - 1) * 100
        if len(hist) >= 20:
            data['change_20d'] = (current / hist['Close'].iloc[-20] - 1) * 100
        
        # Volume ratio
        if data['avg_volume'] > 0:
            data['volume_ratio'] = data['volume_today'] / data['avg_volume']
        else:
            data['volume_ratio'] = 1
        
        # Float category
        float_shares = data['float']
        if float_shares > 0:
            if float_shares < 10_000_000:
                data['float_cat'] = 'TINY'
            elif float_shares < 30_000_000:
                data['float_cat'] = 'NANO'
            elif float_shares < 50_000_000:
                data['float_cat'] = 'MICRO'
            elif float_shares < 100_000_000:
                data['float_cat'] = 'SMALL'
            else:
                data['float_cat'] = 'NORMAL'
        else:
            data['float_cat'] = 'UNKNOWN'
        
        # Price category (we want $2-50 range for position sizing)
        if data['price'] < 2:
            data['price_cat'] = 'PENNY'
        elif data['price'] < 10:
            data['price_cat'] = 'LOW'
        elif data['price'] < 30:
            data['price_cat'] = 'MID'
        elif data['price'] < 100:
            data['price_cat'] = 'HIGH'
        else:
            data['price_cat'] = 'EXPENSIVE'
        
        return data
        
    except Exception as e:
        return None


# ============================================================================
# TRAP SCORING
# ============================================================================

def score_short_trap(data: dict) -> dict:
    """Score short squeeze potential"""
    score = 0
    reasons = []
    
    si = data['short_percent']
    dtc = data['short_ratio']
    change_5d = data['change_5d']
    float_cat = data['float_cat']
    
    # Short interest scoring
    if si >= 30:
        score += 40
        reasons.append(f"🔥 SI={si:.0f}%")
    elif si >= 20:
        score += 30
        reasons.append(f"SI={si:.0f}%")
    elif si >= 15:
        score += 20
        reasons.append(f"SI={si:.0f}%")
    elif si >= 10:
        score += 10
    
    # Days to cover
    if dtc >= 5:
        score += 25
        reasons.append(f"DTC={dtc:.1f}")
    elif dtc >= 3:
        score += 15
        reasons.append(f"DTC={dtc:.1f}")
    elif dtc >= 2:
        score += 10
    
    # Shorts in pain (price rising with high SI)
    if change_5d > 10 and si > 15:
        score += 25
        reasons.append(f"+{change_5d:.0f}% BLEEDING")
    elif change_5d > 5 and si > 15:
        score += 15
        reasons.append(f"+{change_5d:.0f}%")
    elif change_5d > 0 and si > 20:
        score += 10
    
    # Low float amplifier
    if float_cat in ['TINY', 'NANO'] and si > 15:
        score += 20
        reasons.append(f"{float_cat} float")
    elif float_cat == 'MICRO' and si > 15:
        score += 10
    
    return {
        'score': min(score, 100),
        'reasons': reasons,
        'trapped': score >= 50
    }


def score_momentum_trap(data: dict) -> dict:
    """Score momentum/laggard potential"""
    score = 0
    reasons = []
    
    change_5d = data['change_5d']
    change_20d = data['change_20d']
    vol_ratio = data['volume_ratio']
    
    # Strong momentum
    if change_5d > 20:
        score += 35
        reasons.append(f"🚀 +{change_5d:.0f}% 5d")
    elif change_5d > 10:
        score += 25
        reasons.append(f"+{change_5d:.0f}% 5d")
    elif change_5d > 5:
        score += 15
    
    # Trend
    if change_20d > 30:
        score += 25
        reasons.append(f"+{change_20d:.0f}% 20d")
    elif change_20d > 15:
        score += 15
    elif change_20d > 0:
        score += 5
    
    # Volume confirmation
    if vol_ratio > 3:
        score += 25
        reasons.append(f"VOL {vol_ratio:.1f}x")
    elif vol_ratio > 2:
        score += 15
        reasons.append(f"VOL {vol_ratio:.1f}x")
    elif vol_ratio > 1.5:
        score += 10
    
    # Bounce from lows (recovery play)
    if change_20d < -20 and change_5d > 10:
        score += 15
        reasons.append("BOUNCE")
    
    return {
        'score': min(score, 100),
        'reasons': reasons,
        'trapped': score >= 50
    }


def score_powder_keg(data: dict) -> dict:
    """Score explosive potential (low float + pressure)"""
    score = 0
    reasons = []
    
    float_cat = data['float_cat']
    si = data['short_percent']
    vol_ratio = data['volume_ratio']
    price = data['price']
    
    # Low float is key
    if float_cat == 'TINY':
        score += 35
        reasons.append("TINY float")
    elif float_cat == 'NANO':
        score += 25
        reasons.append("NANO float")
    elif float_cat == 'MICRO':
        score += 15
        reasons.append("MICRO float")
    
    # Add shorts for fuel
    if si > 20 and float_cat in ['TINY', 'NANO', 'MICRO']:
        score += 30
        reasons.append(f"+{si:.0f}% SI")
    elif si > 10:
        score += 15
    
    # Volume building
    if vol_ratio > 2:
        score += 20
        reasons.append("VOL building")
    elif vol_ratio > 1.5:
        score += 10
    
    # Price range (tradeable)
    if 3 < price < 30:
        score += 15
        reasons.append(f"${price:.2f}")
    elif 1 < price < 50:
        score += 10
    
    return {
        'score': min(score, 100),
        'reasons': reasons,
        'trapped': score >= 50
    }


def calculate_conviction(data: dict) -> dict:
    """Calculate overall conviction score"""
    
    short_trap = score_short_trap(data)
    momentum = score_momentum_trap(data)
    powder_keg = score_powder_keg(data)
    
    # Combined score - weight short squeeze highest
    combined = (
        short_trap['score'] * 0.5 +
        momentum['score'] * 0.3 +
        powder_keg['score'] * 0.2
    )
    
    # Bonus for multiple traps
    traps_active = sum([
        short_trap['trapped'],
        momentum['trapped'],
        powder_keg['trapped']
    ])
    
    if traps_active >= 2:
        combined = min(combined + 15, 100)
    
    # Collect all reasons
    all_reasons = (
        short_trap['reasons'] +
        momentum['reasons'] +
        powder_keg['reasons']
    )
    
    # Determine primary thesis
    if short_trap['score'] >= momentum['score'] and short_trap['score'] >= powder_keg['score']:
        thesis = "SHORT SQUEEZE"
    elif momentum['score'] >= powder_keg['score']:
        thesis = "MOMENTUM"
    else:
        thesis = "POWDER KEG"
    
    return {
        'conviction': int(combined),
        'thesis': thesis,
        'reasons': all_reasons,
        'short_score': short_trap['score'],
        'momentum_score': momentum['score'],
        'powder_score': powder_keg['score'],
        'traps_active': traps_active
    }


# ============================================================================
# TRADE PLAN
# ============================================================================

def generate_trade_plan(data: dict, conviction: dict, risk_dollars: float = 200) -> dict:
    """Generate specific trade plan"""
    
    price = data['price']
    si = data['short_percent']
    
    # Stop based on setup type
    if conviction['thesis'] == 'SHORT SQUEEZE':
        stop_pct = 0.12  # 12% for squeeze plays (volatile)
        target_pct = 0.25  # 25% target
    elif conviction['thesis'] == 'MOMENTUM':
        stop_pct = 0.10  # 10% standard
        target_pct = 0.20
    else:  # POWDER KEG
        stop_pct = 0.15  # 15% for explosive plays
        target_pct = 0.30
    
    # If very high conviction, tighter stop, higher target
    if conviction['conviction'] >= 80:
        target_pct += 0.10
    
    stop = price * (1 - stop_pct)
    target = price * (1 + target_pct)
    
    # Position sizing
    risk_per_share = price - stop
    if risk_per_share > 0:
        shares = int(risk_dollars / risk_per_share)
        cost = shares * price
    else:
        shares = 0
        cost = 0
    
    # R:R
    reward = target - price
    rr = reward / risk_per_share if risk_per_share > 0 else 0
    
    return {
        'entry': round(price, 2),
        'stop': round(stop, 2),
        'stop_pct': round(stop_pct * 100, 1),
        'target': round(target, 2),
        'target_pct': round(target_pct * 100, 1),
        'shares': shares,
        'cost': round(cost, 2),
        'risk': risk_dollars,
        'rr': round(rr, 1)
    }


# ============================================================================
# DISCOVERY SCAN
# ============================================================================

def discover_trapped_players(min_conviction: int = 50, min_short: float = 10):
    """Scan entire universe for trapped players"""
    
    print("\n" + "=" * 70)
    print("🐺 WOLF DISCOVERY - Finding Trapped Players")
    print("=" * 70)
    print(f"Scanning {len(ALL_DISCOVERY)} tickers...")
    print(f"Filters: Conviction >= {min_conviction}, Short >= {min_short}%")
    print("")
    
    leads = []
    
    for i, ticker in enumerate(ALL_DISCOVERY):
        try:
            # Progress
            if (i + 1) % 10 == 0:
                print(f"[{i+1}/{len(ALL_DISCOVERY)}] Scanning...", flush=True)
            
            # Get data
            data = get_stock_metrics(ticker)
            if not data:
                continue
            
            # Skip if price too extreme
            if data['price'] < 1 or data['price'] > 500:
                continue
            
            # Skip if no short data and we're looking for shorts
            if min_short > 0 and data['short_percent'] < min_short:
                continue
            
            # Calculate conviction
            conv = calculate_conviction(data)
            
            if conv['conviction'] >= min_conviction:
                # Generate trade plan
                plan = generate_trade_plan(data, conv)
                
                leads.append({
                    **data,
                    **conv,
                    'trade_plan': plan
                })
            
            time.sleep(0.1)  # Rate limiting
            
        except Exception as e:
            continue
    
    # Sort by conviction
    leads.sort(key=lambda x: x['conviction'], reverse=True)
    
    return leads


def print_discovery_report(leads: list, capital: float = 1316):
    """Print the discovery report"""
    
    print("\n" + "=" * 70)
    print("🐺 WOLF DISCOVERY REPORT")
    print(f"   Capital Available: ${capital:,.0f}")
    print(f"   Leads Found: {len(leads)}")
    print("=" * 70)
    
    if not leads:
        print("\n❌ No strong leads found with current filters")
        print("   Try lowering min_conviction or min_short")
        return
    
    # Categorize leads
    squeeze_plays = [l for l in leads if l['thesis'] == 'SHORT SQUEEZE']
    momentum_plays = [l for l in leads if l['thesis'] == 'MOMENTUM']
    powder_kegs = [l for l in leads if l['thesis'] == 'POWDER KEG']
    
    # Print squeeze plays
    if squeeze_plays:
        print("\n🔴 SHORT SQUEEZE PLAYS (Shorts TRAPPED)")
        print("-" * 70)
        
        for lead in squeeze_plays[:10]:
            tp = lead['trade_plan']
            print(f"\n  {lead['ticker']:6} | Conv: {lead['conviction']:3} | SI: {lead['short_percent']:5.1f}% | DTC: {lead['short_ratio']:4.1f}")
            print(f"         Price: ${lead['price']:7.2f} | Float: {lead['float_cat']:6}")
            print(f"         5d: {lead['change_5d']:+6.1f}% | 20d: {lead['change_20d']:+6.1f}% | Vol: {lead['volume_ratio']:.1f}x")
            print(f"         🎯 {' '.join(lead['reasons'][:4])}")
            print(f"         📍 Entry: ${tp['entry']:.2f} | Stop: ${tp['stop']:.2f} | Target: ${tp['target']:.2f} ({tp['rr']}:1)")
    
    # Print momentum plays
    if momentum_plays:
        print("\n🟡 MOMENTUM PLAYS (Runners)")
        print("-" * 70)
        
        for lead in momentum_plays[:5]:
            tp = lead['trade_plan']
            print(f"\n  {lead['ticker']:6} | Conv: {lead['conviction']:3} | 5d: {lead['change_5d']:+.1f}%")
            print(f"         Price: ${lead['price']:.2f} | Vol: {lead['volume_ratio']:.1f}x")
            print(f"         🎯 {' '.join(lead['reasons'][:3])}")
    
    # Print powder kegs
    if powder_kegs:
        print("\n🟠 POWDER KEGS (Low Float Explosives)")
        print("-" * 70)
        
        for lead in powder_kegs[:5]:
            tp = lead['trade_plan']
            print(f"\n  {lead['ticker']:6} | Conv: {lead['conviction']:3} | Float: {lead['float_cat']}")
            print(f"         Price: ${lead['price']:.2f} | SI: {lead['short_percent']:.1f}%")
            print(f"         🎯 {' '.join(lead['reasons'][:3])}")
    
    # DEPLOYMENT PLAN
    print("\n" + "=" * 70)
    print(f"💰 DEPLOYMENT PLAN (${capital:,.0f})")
    print("=" * 70)
    
    # Top picks
    top_picks = leads[:5]
    per_position = capital / len(top_picks) if top_picks else 0
    
    print(f"\nSplit ${capital:.0f} across {len(top_picks)} positions (${per_position:.0f} each):\n")
    
    for i, lead in enumerate(top_picks, 1):
        shares = int(per_position / lead['price'])
        cost = shares * lead['price']
        print(f"  {i}. {lead['ticker']:6} - ${cost:.0f} ({shares} shares @ ${lead['price']:.2f})")
        print(f"     WHY: {lead['thesis']} - {' '.join(lead['reasons'][:2])}")
        print(f"     STOP: ${lead['trade_plan']['stop']:.2f} | TARGET: ${lead['trade_plan']['target']:.2f}")
        print("")
    
    # Save to file
    print("-" * 70)
    print("📤 Saving to discovery_leads.csv...")
    
    df = pd.DataFrame([{
        'ticker': l['ticker'],
        'conviction': l['conviction'],
        'thesis': l['thesis'],
        'price': l['price'],
        'short_pct': l['short_percent'],
        'dtc': l['short_ratio'],
        'float': l['float_cat'],
        'change_5d': l['change_5d'],
        'volume_ratio': l['volume_ratio'],
        'entry': l['trade_plan']['entry'],
        'stop': l['trade_plan']['stop'],
        'target': l['trade_plan']['target'],
        'reasons': ' | '.join(l['reasons'][:3])
    } for l in leads])
    
    df.to_csv('/workspaces/trading-companion-2026/discovery_leads.csv', index=False)
    
    # ATP watchlist
    with open('/workspaces/trading-companion-2026/atp_discovery.csv', 'w') as f:
        f.write("Symbol\n")
        for lead in leads[:20]:
            f.write(f"{lead['ticker']}\n")
    
    print("📤 ATP watchlist: atp_discovery.csv")
    print("")
    print("=" * 70)
    print("REMEMBER: Short squeeze = Shorts MUST cover")
    print("         Powder keg = Any spark explodes")
    print("         We position AHEAD of forced buying")
    print("=" * 70)
    print("\nAWOOOO 🐺")


# ============================================================================
# MAIN
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="🐺 Wolf Discovery")
    parser.add_argument('--min-conviction', type=int, default=50,
                       help='Minimum conviction score (default: 50)')
    parser.add_argument('--min-short', type=float, default=10,
                       help='Minimum short interest % (default: 10)')
    parser.add_argument('--capital', type=float, default=1316,
                       help='Capital to deploy (default: 1316)')
    parser.add_argument('--all', action='store_true',
                       help='Include all stocks, not just high short')
    
    args = parser.parse_args()
    
    # If --all, set min_short to 0
    min_short = 0 if args.all else args.min_short
    
    leads = discover_trapped_players(
        min_conviction=args.min_conviction,
        min_short=min_short
    )
    
    print_discovery_report(leads, capital=args.capital)


if __name__ == "__main__":
    main()
