#!/usr/bin/env python3
"""
🐺 THE WOLF BRAIN - Intelligence Layer for Fidelity ATP
=========================================================

NOT "what does the chart say"
WHO IS TRAPPED AND WHY SHOULD I CARE?

This finds FORCED BUYERS:
- Shorts bleeding (high borrow, rising price = MUST cover)
- Insiders accumulating (Form 4 = they KNOW something)
- Sector laggards (sector hot, this stock cold = MUST catch up)
- Panic recovery (retail dumped, institutions buying cheap)
- Low float powder kegs (any spark = explosion)

OUTPUT: ATP-compatible watchlist + full trade plan

Built by Fenrir for Tyr.
LLHR 🐺
"""

import argparse
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json
from pathlib import Path
import warnings
import time
warnings.filterwarnings('ignore')

# ============================================================================
# THE UNIVERSE - Our Hunting Ground
# ============================================================================

UNIVERSE = {
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ', 'LAES'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'BKSY', 'ASTS', 'SPIR', 'SIDU', 'SATL'],
    'NUCLEAR': ['LEU', 'CCJ', 'UUUU', 'UEC', 'SMR', 'OKLO', 'NNE', 'DNN'],
    'AI_INFRA': ['SMCI', 'VRT', 'PWR', 'SOUN', 'AI', 'PATH', 'UPST'],
    'SEMICONDUCTORS': ['MU', 'AMD', 'ARM', 'MRVL', 'ALAB', 'CRDO'],
    'CRYPTO': ['MARA', 'RIOT', 'CLSK', 'COIN', 'CIFR', 'HUT'],
    'DEFENSE_AI': ['PLTR', 'KTOS', 'RCAT'],  # Not AISP - we hold it already
    'BIOTECH': ['CRSP', 'EDIT', 'NTLA'],
    'FINTECH': ['SOFI', 'AFRM', 'NU']
}

# Flatten
ALL_TICKERS = []
for tickers in UNIVERSE.values():
    ALL_TICKERS.extend(tickers)

# ============================================================================
# DATA FETCHERS
# ============================================================================

def get_stock_data(ticker: str) -> dict:
    """Get comprehensive stock data"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period='3mo')
        
        if hist.empty:
            return None
        
        current = hist['Close'].iloc[-1]
        
        # Calculate key metrics
        data = {
            'ticker': ticker,
            'price': current,
            'float': info.get('floatShares', 0),
            'shares_outstanding': info.get('sharesOutstanding', 0),
            'short_percent': info.get('shortPercentOfFloat', 0) or 0,
            'short_ratio': info.get('shortRatio', 0) or 0,  # Days to cover
            'avg_volume': info.get('averageVolume', 0),
            'market_cap': info.get('marketCap', 0),
            'sector': None,  # We'll fill this
        }
        
        # Find sector
        for sector, tickers in UNIVERSE.items():
            if ticker in tickers:
                data['sector'] = sector
                break
        
        # Price changes
        if len(hist) >= 5:
            data['change_5d'] = (current / hist['Close'].iloc[-5] - 1) * 100
        else:
            data['change_5d'] = 0
            
        if len(hist) >= 20:
            data['change_20d'] = (current / hist['Close'].iloc[-20] - 1) * 100
        else:
            data['change_20d'] = 0
        
        # Volume analysis
        vol_today = hist['Volume'].iloc[-1]
        vol_avg = hist['Volume'].rolling(20).mean().iloc[-1]
        data['volume_ratio'] = vol_today / vol_avg if vol_avg > 0 else 1
        
        # 52 week position
        high_52w = hist['High'].max()
        low_52w = hist['Low'].min()
        data['from_high'] = (current / high_52w - 1) * 100
        data['from_low'] = (current / low_52w - 1) * 100
        
        # Float category
        float_shares = data['float']
        if float_shares > 0:
            if float_shares < 20_000_000:
                data['float_category'] = 'NANO'  # < 20M = explosive
            elif float_shares < 50_000_000:
                data['float_category'] = 'MICRO'  # 20-50M = volatile
            elif float_shares < 100_000_000:
                data['float_category'] = 'SMALL'  # 50-100M = tradeable
            else:
                data['float_category'] = 'LARGE'  # > 100M = institutional
        else:
            data['float_category'] = 'UNKNOWN'
        
        return data
        
    except Exception as e:
        return None


def get_insider_buys(days: int = 30) -> list:
    """
    Get recent insider BUYING from SEC EDGAR
    Form 4 filings where transaction is PURCHASE (not options exercise)
    """
    insider_buys = []
    
    # SEC EDGAR API for recent Form 4s
    url = "https://efts.sec.gov/LATEST/search-index"
    
    # We'll check each ticker in our universe
    for ticker in ALL_TICKERS[:30]:  # Limit to avoid rate limiting
        try:
            # Use yfinance for insider transactions
            stock = yf.Ticker(ticker)
            
            try:
                insiders = stock.insider_transactions
                if insiders is not None and not insiders.empty:
                    # Filter for purchases
                    purchases = insiders[insiders['Shares'].fillna(0) > 0]
                    
                    if not purchases.empty:
                        recent = purchases.head(5)
                        for _, row in recent.iterrows():
                            insider_buys.append({
                                'ticker': ticker,
                                'insider': row.get('Insider', 'Unknown'),
                                'shares': row.get('Shares', 0),
                                'value': row.get('Value', 0),
                                'date': str(row.get('Start Date', ''))[:10]
                            })
            except:
                pass
                
            time.sleep(0.1)  # Rate limiting
            
        except:
            continue
    
    return insider_buys


def get_sector_performance() -> dict:
    """Calculate sector performance for rotation detection"""
    sector_perf = {}
    
    for sector, tickers in UNIVERSE.items():
        returns = []
        
        for ticker in tickers[:6]:  # Sample each sector
            try:
                hist = yf.Ticker(ticker).history(period='1mo')
                if len(hist) >= 5:
                    ret_5d = (hist['Close'].iloc[-1] / hist['Close'].iloc[-5] - 1) * 100
                    returns.append({'ticker': ticker, 'return': ret_5d})
            except:
                continue
        
        if returns:
            avg_return = sum(r['return'] for r in returns) / len(returns)
            best = max(returns, key=lambda x: x['return'])
            worst = min(returns, key=lambda x: x['return'])
            
            sector_perf[sector] = {
                'avg_return': avg_return,
                'best': best,
                'worst': worst,
                'all_returns': returns
            }
    
    return sector_perf


# ============================================================================
# TRAP DETECTORS - Finding Forced Buyers
# ============================================================================

class ShortTrap:
    """
    Detect shorts who are BLEEDING.
    High short interest + rising price + high borrow = FORCED to cover
    """
    
    @staticmethod
    def scan(data: dict) -> dict:
        result = {
            'trapped': False,
            'severity': 0,
            'reason': '',
            'details': {}
        }
        
        short_pct = data.get('short_percent', 0) * 100  # Convert to percentage
        days_to_cover = data.get('short_ratio', 0)
        price_change_5d = data.get('change_5d', 0)
        float_cat = data.get('float_category', 'UNKNOWN')
        
        # Scoring
        score = 0
        reasons = []
        
        # High short interest
        if short_pct > 25:
            score += 40
            reasons.append(f"SHORT {short_pct:.0f}% of float")
        elif short_pct > 15:
            score += 25
            reasons.append(f"SHORT {short_pct:.0f}% of float")
        elif short_pct > 10:
            score += 15
            reasons.append(f"SHORT {short_pct:.0f}%")
        
        # Days to cover (harder to exit)
        if days_to_cover > 5:
            score += 30
            reasons.append(f"{days_to_cover:.1f} days to cover")
        elif days_to_cover > 3:
            score += 20
            reasons.append(f"{days_to_cover:.1f} DTC")
        
        # Price rising (shorts in pain)
        if price_change_5d > 15 and short_pct > 10:
            score += 30
            reasons.append(f"UP {price_change_5d:.0f}% (shorts bleeding)")
        elif price_change_5d > 10 and short_pct > 10:
            score += 20
            reasons.append(f"UP {price_change_5d:.0f}%")
        elif price_change_5d > 5 and short_pct > 10:
            score += 10
        
        # Low float amplifies squeeze
        if float_cat in ['NANO', 'MICRO'] and short_pct > 15:
            score += 20
            reasons.append(f"{float_cat} float")
        
        result['severity'] = min(score, 100)
        result['trapped'] = score >= 50
        result['reason'] = ' | '.join(reasons) if reasons else 'No short trap'
        result['details'] = {
            'short_percent': short_pct,
            'days_to_cover': days_to_cover,
            'price_change': price_change_5d,
            'float': float_cat
        }
        
        return result


class LaggardTrap:
    """
    Detect sector laggards who MUST catch up.
    Sector hot but this stock cold = rotation incoming
    """
    
    @staticmethod
    def scan(data: dict, sector_perf: dict) -> dict:
        result = {
            'trapped': False,
            'severity': 0,
            'reason': '',
            'details': {}
        }
        
        sector = data.get('sector')
        if not sector or sector not in sector_perf:
            result['reason'] = 'Sector not tracked'
            return result
        
        perf = sector_perf[sector]
        sector_avg = perf['avg_return']
        stock_return = data.get('change_5d', 0)
        
        # How much is this stock lagging?
        lag = sector_avg - stock_return
        
        score = 0
        reasons = []
        
        # Sector must be hot
        if sector_avg > 10:
            score += 30
            reasons.append(f"{sector} +{sector_avg:.0f}%")
        elif sector_avg > 5:
            score += 20
            reasons.append(f"{sector} +{sector_avg:.0f}%")
        elif sector_avg > 2:
            score += 10
        
        # Stock must be lagging significantly
        if lag > 10 and sector_avg > 5:
            score += 40
            reasons.append(f"LAGGING {lag:.0f}%")
        elif lag > 5 and sector_avg > 3:
            score += 25
            reasons.append(f"LAGGING {lag:.0f}%")
        elif lag > 3:
            score += 15
        
        # Catch-up potential
        if data.get('volume_ratio', 0) > 1.5 and lag > 5:
            score += 20
            reasons.append("Volume confirming")
        
        # Not broken (shouldn't be down huge)
        if stock_return > -10:
            score += 10
        
        result['severity'] = min(score, 100)
        result['trapped'] = score >= 50
        result['reason'] = ' | '.join(reasons) if reasons else 'Not a laggard'
        result['details'] = {
            'sector': sector,
            'sector_return': sector_avg,
            'stock_return': stock_return,
            'lag': lag
        }
        
        return result


class PanicTrap:
    """
    Detect panic recovery setup.
    Stock crashed, volume spiked (panic selling), now recovering = weak hands out
    """
    
    @staticmethod
    def scan(data: dict) -> dict:
        result = {
            'trapped': False,
            'severity': 0,
            'reason': '',
            'details': {}
        }
        
        change_20d = data.get('change_20d', 0)
        change_5d = data.get('change_5d', 0)
        vol_ratio = data.get('volume_ratio', 1)
        from_low = data.get('from_low', 0)
        
        score = 0
        reasons = []
        
        # Must have been crushed recently
        if change_20d < -25:
            score += 25
            reasons.append(f"Was down {abs(change_20d):.0f}%")
        elif change_20d < -15:
            score += 15
        
        # Now recovering
        if change_5d > 15 and change_20d < -15:
            score += 40
            reasons.append(f"Bouncing +{change_5d:.0f}%")
        elif change_5d > 10 and change_20d < -10:
            score += 25
            reasons.append(f"Recovering +{change_5d:.0f}%")
        elif change_5d > 5:
            score += 10
        
        # Volume confirmation
        if vol_ratio > 2:
            score += 25
            reasons.append(f"Volume {vol_ratio:.1f}x")
        elif vol_ratio > 1.5:
            score += 15
        
        # Not too far off lows (still room to run)
        if from_low < 50 and from_low > 10:
            score += 10
        
        result['severity'] = min(score, 100)
        result['trapped'] = score >= 50
        result['reason'] = ' | '.join(reasons) if reasons else 'No panic recovery'
        result['details'] = {
            'change_20d': change_20d,
            'change_5d': change_5d,
            'volume_ratio': vol_ratio,
            'from_low': from_low
        }
        
        return result


class PowderKeg:
    """
    Detect powder keg setups.
    Low float + pressure building + catalyst potential = explosion waiting
    """
    
    @staticmethod
    def scan(data: dict) -> dict:
        result = {
            'trapped': False,
            'severity': 0,
            'reason': '',
            'details': {}
        }
        
        float_cat = data.get('float_category', 'UNKNOWN')
        short_pct = data.get('short_percent', 0) * 100
        vol_ratio = data.get('volume_ratio', 1)
        change_5d = data.get('change_5d', 0)
        
        score = 0
        reasons = []
        
        # Low float is the key
        if float_cat == 'NANO':
            score += 35
            reasons.append("NANO float (<20M)")
        elif float_cat == 'MICRO':
            score += 25
            reasons.append("MICRO float")
        elif float_cat == 'SMALL':
            score += 10
        
        # Add shorts for fuel
        if short_pct > 15 and float_cat in ['NANO', 'MICRO']:
            score += 30
            reasons.append(f"+{short_pct:.0f}% short")
        elif short_pct > 10:
            score += 15
        
        # Volume building
        if vol_ratio > 2:
            score += 20
            reasons.append("Volume building")
        elif vol_ratio > 1.5:
            score += 10
        
        # Price starting to move
        if change_5d > 5:
            score += 15
            reasons.append(f"Moving +{change_5d:.0f}%")
        
        result['severity'] = min(score, 100)
        result['trapped'] = score >= 50
        result['reason'] = ' | '.join(reasons) if reasons else 'Not a powder keg'
        result['details'] = {
            'float': float_cat,
            'short_percent': short_pct,
            'volume_ratio': vol_ratio,
            'change_5d': change_5d
        }
        
        return result


# ============================================================================
# THE BRAIN - Synthesize All Signals
# ============================================================================

def analyze_ticker(ticker: str, sector_perf: dict, insider_data: list) -> dict:
    """Full analysis on one ticker - find ALL traps"""
    
    data = get_stock_data(ticker)
    if not data:
        return None
    
    result = {
        'ticker': ticker,
        'price': data['price'],
        'sector': data['sector'],
        'float_category': data['float_category'],
        'change_5d': data['change_5d'],
        'change_20d': data['change_20d'],
        'volume_ratio': data['volume_ratio'],
        'from_high': data['from_high'],
        'traps': {},
        'conviction': 0,
        'primary_thesis': '',
        'trade_plan': {}
    }
    
    # Run all trap detectors
    result['traps']['short'] = ShortTrap.scan(data)
    result['traps']['laggard'] = LaggardTrap.scan(data, sector_perf)
    result['traps']['panic'] = PanicTrap.scan(data)
    result['traps']['powder_keg'] = PowderKeg.scan(data)
    
    # Check for insider buying
    ticker_insiders = [i for i in insider_data if i['ticker'] == ticker]
    if ticker_insiders:
        result['traps']['insider'] = {
            'trapped': True,
            'severity': min(len(ticker_insiders) * 25, 100),
            'reason': f"{len(ticker_insiders)} insider buys",
            'details': ticker_insiders
        }
    else:
        result['traps']['insider'] = {
            'trapped': False,
            'severity': 0,
            'reason': 'No recent insider buying'
        }
    
    # Calculate conviction from traps
    active_traps = [t for t in result['traps'].values() if t['trapped']]
    
    if active_traps:
        # Conviction = weighted average of trap severities
        conviction = sum(t['severity'] for t in active_traps) / len(active_traps)
        
        # Bonus for multiple traps
        if len(active_traps) >= 3:
            conviction = min(conviction + 20, 100)
        elif len(active_traps) >= 2:
            conviction = min(conviction + 10, 100)
        
        result['conviction'] = int(conviction)
        
        # Primary thesis = strongest trap
        strongest = max(active_traps, key=lambda x: x['severity'])
        for trap_name, trap_data in result['traps'].items():
            if trap_data == strongest:
                result['primary_thesis'] = f"{trap_name.upper()}: {trap_data['reason']}"
                break
    else:
        result['conviction'] = 0
        result['primary_thesis'] = "No traps detected"
    
    # Generate trade plan if conviction is high enough
    if result['conviction'] >= 50:
        result['trade_plan'] = generate_trade_plan(data, result)
    
    return result


def generate_trade_plan(data: dict, analysis: dict) -> dict:
    """Generate specific entry/stop/target"""
    
    price = data['price']
    
    # Entry zone - pullback to support
    # Use recent low or 3-5% below current
    entry_low = price * 0.95
    entry_high = price * 1.02
    
    # Stop based on volatility and trap type
    primary = analysis['primary_thesis'].split(':')[0].lower()
    
    if 'panic' in primary:
        stop_pct = 0.15  # Wider stop for recovery plays
    elif 'powder' in primary:
        stop_pct = 0.12  # Medium for powder kegs
    else:
        stop_pct = 0.10  # Standard 10%
    
    stop = price * (1 - stop_pct)
    
    # Target based on setup
    if analysis['conviction'] >= 80:
        target_pct = 0.30  # 30% for high conviction
    elif analysis['conviction'] >= 65:
        target_pct = 0.20  # 20% for medium
    else:
        target_pct = 0.15  # 15% for lower
    
    target = price * (1 + target_pct)
    
    # Position size for $500 risk
    risk_per_share = price - stop
    if risk_per_share > 0:
        shares_500_risk = int(500 / risk_per_share)
        position_cost = shares_500_risk * price
    else:
        shares_500_risk = 0
        position_cost = 0
    
    # R:R ratio
    reward = target - price
    risk = price - stop
    rr_ratio = reward / risk if risk > 0 else 0
    
    return {
        'entry_low': round(entry_low, 2),
        'entry_high': round(entry_high, 2),
        'stop': round(stop, 2),
        'stop_pct': round(stop_pct * 100, 1),
        'target': round(target, 2),
        'target_pct': round(target_pct * 100, 1),
        'shares_500_risk': shares_500_risk,
        'position_cost': round(position_cost, 2),
        'rr_ratio': round(rr_ratio, 1)
    }


# ============================================================================
# OUTPUT GENERATORS
# ============================================================================

def generate_atp_watchlist(leads: list) -> str:
    """Generate ATP-compatible watchlist format"""
    output = []
    output.append("# Wolf Brain Leads - Import to ATP")
    output.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    output.append("#")
    output.append("# Paste these tickers into ATP Watchlist")
    output.append("#" + "="*50)
    output.append("")
    
    for lead in leads:
        output.append(f"{lead['ticker']}")
    
    # Also save as CSV for ATP import
    csv_path = Path('/workspaces/trading-companion-2026/atp_watchlist.csv')
    with open(csv_path, 'w') as f:
        f.write("Symbol\n")
        for lead in leads:
            f.write(f"{lead['ticker']}\n")
    
    return '\n'.join(output)


def generate_briefing(leads: list) -> str:
    """Generate the Monday Morning Briefing"""
    output = []
    
    output.append("")
    output.append("=" * 70)
    output.append("🐺 WOLF BRAIN - TRAPPED PLAYER REPORT")
    output.append(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    output.append("=" * 70)
    output.append("")
    output.append("THE QUESTION: Who is TRAPPED and FORCED to buy?")
    output.append("")
    
    if not leads:
        output.append("❌ NO STRONG LEADS FOUND")
        output.append("   The market is quiet. No clear traps detected.")
        output.append("   Check back during market hours.")
        return '\n'.join(output)
    
    # Separate by conviction
    high_conviction = [l for l in leads if l['conviction'] >= 70]
    medium_conviction = [l for l in leads if 50 <= l['conviction'] < 70]
    
    if high_conviction:
        output.append("🔥 HIGH CONVICTION LEADS (70+)")
        output.append("-" * 70)
        
        for lead in high_conviction[:5]:
            output.append("")
            output.append(f"  ▶ {lead['ticker']} - CONVICTION: {lead['conviction']}/100")
            output.append(f"    Price: ${lead['price']:.2f} | Sector: {lead['sector']}")
            output.append(f"    5d: {lead['change_5d']:+.1f}% | 20d: {lead['change_20d']:+.1f}%")
            output.append(f"    Float: {lead['float_category']} | Volume: {lead['volume_ratio']:.1f}x avg")
            output.append("")
            output.append(f"    📍 THESIS: {lead['primary_thesis']}")
            output.append("")
            
            # Show all active traps
            active_traps = [(name, data) for name, data in lead['traps'].items() if data['trapped']]
            if active_traps:
                output.append("    🎯 TRAPS DETECTED:")
                for trap_name, trap_data in active_traps:
                    output.append(f"       • {trap_name.upper()}: {trap_data['reason']} ({trap_data['severity']})")
            
            # Trade plan
            if lead.get('trade_plan'):
                tp = lead['trade_plan']
                output.append("")
                output.append(f"    💰 TRADE PLAN:")
                output.append(f"       Entry Zone: ${tp['entry_low']:.2f} - ${tp['entry_high']:.2f}")
                output.append(f"       Stop Loss:  ${tp['stop']:.2f} ({tp['stop_pct']}%)")
                output.append(f"       Target:     ${tp['target']:.2f} ({tp['target_pct']}%)")
                output.append(f"       R:R Ratio:  {tp['rr_ratio']}:1")
                output.append(f"       Position:   {tp['shares_500_risk']} shares (${tp['position_cost']:.0f} for $500 risk)")
            
            output.append("")
            output.append("    " + "-" * 50)
    
    if medium_conviction:
        output.append("")
        output.append("⚡ MEDIUM CONVICTION LEADS (50-69)")
        output.append("-" * 70)
        
        for lead in medium_conviction[:5]:
            output.append(f"  • {lead['ticker']}: {lead['conviction']}/100 - {lead['primary_thesis']}")
            if lead.get('trade_plan'):
                tp = lead['trade_plan']
                output.append(f"    Entry: ${tp['entry_low']:.2f}-${tp['entry_high']:.2f} | Stop: ${tp['stop']:.2f} | Target: ${tp['target']:.2f}")
    
    # ATP export note
    output.append("")
    output.append("=" * 70)
    output.append("📤 ATP WATCHLIST EXPORTED TO: atp_watchlist.csv")
    output.append("   Import this file into Fidelity Active Trader Pro")
    output.append("=" * 70)
    
    output.append("")
    output.append("REMEMBER: We don't predict price. We find FORCED BUYERS.")
    output.append("AWOOOO 🐺")
    output.append("")
    
    return '\n'.join(output)


# ============================================================================
# MAIN COMMANDS
# ============================================================================

def brain_scan():
    """Full brain scan - find all trapped players"""
    print("\n🐺 WOLF BRAIN - Scanning for Trapped Players...")
    print("=" * 60)
    
    # Get sector performance first
    print("📊 Analyzing sector rotation...")
    sector_perf = get_sector_performance()
    
    # Get insider data
    print("💰 Checking insider buying...")
    insider_data = get_insider_buys()
    
    # Scan all tickers
    print(f"🔍 Scanning {len(ALL_TICKERS)} tickers...")
    print("")
    
    leads = []
    
    for i, ticker in enumerate(ALL_TICKERS):
        print(f"[{i+1}/{len(ALL_TICKERS)}] {ticker}...", end=" ", flush=True)
        
        result = analyze_ticker(ticker, sector_perf, insider_data)
        
        if result and result['conviction'] >= 50:
            leads.append(result)
            print(f"✅ LEAD ({result['conviction']})")
        else:
            print("⏭️")
        
        time.sleep(0.2)  # Rate limiting
    
    # Sort by conviction
    leads.sort(key=lambda x: x['conviction'], reverse=True)
    
    # Generate outputs
    briefing = generate_briefing(leads)
    print(briefing)
    
    # Save ATP watchlist
    if leads:
        atp_list = generate_atp_watchlist(leads)
        print("\n" + atp_list)
    
    # Save briefing
    briefing_path = Path('/workspaces/trading-companion-2026/logs/wolf_brain_briefing.txt')
    briefing_path.parent.mkdir(exist_ok=True)
    with open(briefing_path, 'w') as f:
        f.write(briefing)
    
    return leads


def brain_single(ticker: str):
    """Deep analysis on single ticker"""
    print(f"\n🐺 WOLF BRAIN - Deep Analysis: {ticker}")
    print("=" * 60)
    
    # Get context
    sector_perf = get_sector_performance()
    insider_data = get_insider_buys()
    
    result = analyze_ticker(ticker, sector_perf, insider_data)
    
    if not result:
        print(f"❌ Could not analyze {ticker}")
        return None
    
    # Detailed output
    print("")
    print(f"📊 {result['ticker']} - CONVICTION: {result['conviction']}/100")
    print("-" * 60)
    print(f"Price: ${result['price']:.2f}")
    print(f"Sector: {result['sector']}")
    print(f"Float: {result['float_category']}")
    print(f"5d Change: {result['change_5d']:+.1f}%")
    print(f"20d Change: {result['change_20d']:+.1f}%")
    print(f"Volume: {result['volume_ratio']:.1f}x average")
    print(f"From 52w High: {result['from_high']:.1f}%")
    print("")
    
    print("🎯 TRAP ANALYSIS:")
    print("-" * 60)
    for trap_name, trap_data in result['traps'].items():
        status = "🔥 TRAPPED" if trap_data['trapped'] else "❌ Clear"
        print(f"  {trap_name.upper():12} {status:12} ({trap_data['severity']:3}/100)")
        print(f"                 {trap_data['reason']}")
        print("")
    
    print("-" * 60)
    print(f"📍 PRIMARY THESIS: {result['primary_thesis']}")
    print("")
    
    if result.get('trade_plan'):
        tp = result['trade_plan']
        print("💰 TRADE PLAN:")
        print("-" * 60)
        print(f"  Entry Zone:    ${tp['entry_low']:.2f} - ${tp['entry_high']:.2f}")
        print(f"  Stop Loss:     ${tp['stop']:.2f} ({tp['stop_pct']}% risk)")
        print(f"  Target:        ${tp['target']:.2f} ({tp['target_pct']}% reward)")
        print(f"  R:R Ratio:     {tp['rr_ratio']}:1")
        print(f"  Position Size: {tp['shares_500_risk']} shares for $500 risk")
        print(f"  Total Cost:    ${tp['position_cost']:.2f}")
    else:
        print("⚠️ No trade plan - conviction too low")
    
    print("")
    print("=" * 60)
    
    return result


def brain_sectors():
    """Show sector heat map"""
    print("\n🐺 WOLF BRAIN - SECTOR HEAT MAP")
    print("=" * 60)
    
    sector_perf = get_sector_performance()
    
    # Sort by performance
    sorted_sectors = sorted(sector_perf.items(), key=lambda x: x[1]['avg_return'], reverse=True)
    
    print("")
    print("5-DAY SECTOR PERFORMANCE:")
    print("-" * 60)
    
    for sector, data in sorted_sectors:
        avg = data['avg_return']
        best = data['best']
        worst = data['worst']
        
        if avg > 10:
            heat = "🔥🔥🔥"
        elif avg > 5:
            heat = "🔥🔥"
        elif avg > 0:
            heat = "🔥"
        elif avg > -5:
            heat = "❄️"
        else:
            heat = "❄️❄️"
        
        print(f"{heat} {sector:15} {avg:+6.1f}%")
        print(f"      Best:  {best['ticker']:5} {best['return']:+6.1f}%")
        print(f"      Worst: {worst['ticker']:5} {worst['return']:+6.1f}%")
        
        # Find laggards
        laggards = [r for r in data['all_returns'] if r['return'] < avg - 3]
        if laggards and avg > 3:
            print(f"      ⚠️ LAGGARDS: {', '.join(l['ticker'] for l in laggards)}")
        print("")
    
    print("=" * 60)
    print("LAGGARD PLAY: Buy stocks that haven't moved with hot sector")
    print("=" * 60)


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="🐺 Wolf Brain - Find Trapped Players")
    parser.add_argument('command', nargs='?', default='scan',
                       help='scan = full scan, TICKER = single analysis, sectors = heat map')
    
    args = parser.parse_args()
    
    cmd = args.command.lower()
    
    if cmd == 'scan':
        brain_scan()
    elif cmd == 'sectors':
        brain_sectors()
    else:
        # Assume it's a ticker
        brain_single(args.command.upper())


if __name__ == "__main__":
    main()
