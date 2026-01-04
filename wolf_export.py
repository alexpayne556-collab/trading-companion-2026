#!/usr/bin/env python3
"""
🐺 WOLF EXPORT - ATP/ROBINHOOD WATCHLIST GENERATOR
===================================================

One button. Top targets. Ready to import.

This isn't just a CSV - it's a PRIORITIZED BATTLE PLAN.
Every ticker comes with:
- WHY it's there (the thesis)
- WHO is trapped
- WHAT scanner found it
- WHERE to enter/exit
- CONFIDENCE level

Exports to:
- Fidelity ATP (.csv with notes)
- Robinhood (.csv simple format)
- TradingView (.txt watchlist)
- Full Report (.md for reading)

The wolf brain providing targets for the broker body.

Built by Brokkr & Fenrir
AWOOOO 🐺
"""

import json
import csv
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# TARGET DATA STRUCTURE
# ============================================================================

class SignalSource(Enum):
    PRESSURE_SHORT_SQUEEZE = "🔴 Short Squeeze"
    PRESSURE_PANIC_RECOVERY = "🟡 Panic Recovery"
    PRESSURE_CAPITULATION = "🟣 Capitulation"
    PRESSURE_LAGGARD = "🟠 Laggard Catch-up"
    TACTICAL_LEADER_LAG = "📊 Leader-Lag"
    TACTICAL_MOMENTUM = "🚀 Day 2 Momentum"
    TACTICAL_WOUNDED = "🩸 Wounded Recovery"
    SMART_MONEY = "💰 Insider Buying"
    CONVICTION = "⭐ High Conviction"

@dataclass
class WolfTarget:
    """A fully-qualified trading target"""
    rank: int
    ticker: str
    company: str
    current_price: float
    signal_source: str
    confidence: int  # 0-100
    trapped_player: str
    thesis: str
    entry_zone: str
    target_price: str
    stop_loss: str
    risk_reward: str
    timing: str
    sector: str
    short_interest: Optional[float] = None
    insider_buying: Optional[str] = None
    volume_ratio: Optional[float] = None
    notes: str = ""

# ============================================================================
# DATA AGGREGATION - Pull from all our scanners
# ============================================================================

def load_pressure_signals() -> List[Dict]:
    """Load signals from pressure framework"""
    try:
        with open('logs/pressure_scan_latest.json', 'r') as f:
            data = json.load(f)
            return data.get('signals', [])
    except FileNotFoundError:
        return []

def load_tactical_signals() -> Dict[str, List[Dict]]:
    """Load signals from tactical scanners"""
    try:
        with open('logs/tactical_scan_latest.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_smart_money() -> List[Dict]:
    """Load insider buying data"""
    try:
        with open('logs/smart_money_latest.json', 'r') as f:
            data = json.load(f)
            return data.get('purchases', [])
    except FileNotFoundError:
        return []

def load_conviction_rankings() -> List[Dict]:
    """Load conviction rankings"""
    try:
        with open('logs/conviction_rankings_latest.json', 'r') as f:
            data = json.load(f)
            return data.get('rankings', [])
    except FileNotFoundError:
        return []

def get_stock_info(ticker: str) -> Dict:
    """Get current price and company info"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='5d')
        
        # Handle multi-level columns
        if isinstance(hist.columns, pd.MultiIndex):
            hist.columns = hist.columns.get_level_values(0)
        
        current_price = hist['Close'].iloc[-1] if not hist.empty else 0
        
        try:
            info = stock.info
            company = info.get('shortName', info.get('longName', ticker))
            sector = info.get('sector', 'Unknown')
            short_pct = info.get('shortPercentOfFloat', 0)
        except:
            company = ticker
            sector = 'Unknown'
            short_pct = 0
        
        return {
            'price': round(float(current_price), 2),
            'company': company or ticker,
            'sector': sector or 'Unknown',
            'short_pct': short_pct or 0
        }
    except Exception as e:
        return {'price': 0, 'company': ticker, 'sector': 'Unknown', 'short_pct': 0}

# ============================================================================
# SECTOR MAPPING
# ============================================================================

SECTOR_MAP = {
    'IONQ': 'Quantum', 'RGTI': 'Quantum', 'QBTS': 'Quantum', 'QUBT': 'Quantum', 'ARQQ': 'Quantum', 'LAES': 'Quantum',
    'LUNR': 'Space', 'RKLB': 'Space', 'RDW': 'Space', 'BKSY': 'Space', 'MNTS': 'Space', 'ASTS': 'Space',
    'SPIR': 'Space', 'PL': 'Space', 'GSAT': 'Space', 'SIDU': 'Space', 'SATL': 'Space',
    'JOBY': 'eVTOL', 'ACHR': 'eVTOL', 'LILM': 'eVTOL', 'EVTL': 'eVTOL',
    'LEU': 'Nuclear', 'CCJ': 'Nuclear', 'UUUU': 'Nuclear', 'UEC': 'Nuclear', 'SMR': 'Nuclear',
    'OKLO': 'Nuclear', 'DNN': 'Nuclear', 'NXE': 'Nuclear', 'NNE': 'Nuclear', 'CEG': 'Nuclear',
    'NVDA': 'AI/Semis', 'AMD': 'AI/Semis', 'SMCI': 'AI/Semis', 'ARM': 'AI/Semis', 'TSM': 'AI/Semis',
    'MRVL': 'AI/Semis', 'AVGO': 'AI/Semis', 'MU': 'AI/Semis', 'SOUN': 'AI/Semis', 'AI': 'AI/Semis',
    'MARA': 'Crypto', 'RIOT': 'Crypto', 'CLSK': 'Crypto', 'COIN': 'Crypto', 'CIFR': 'Crypto',
    'CRSP': 'Biotech', 'EDIT': 'Biotech', 'NTLA': 'Biotech', 'BEAM': 'Biotech', 'RXRX': 'Biotech',
    'TSLA': 'EV/Clean', 'RIVN': 'EV/Clean', 'LCID': 'EV/Clean', 'PLUG': 'EV/Clean', 'FCEL': 'EV/Clean',
    'SOFI': 'Fintech', 'AFRM': 'Fintech', 'UPST': 'Fintech', 'NU': 'Fintech',
}

# ============================================================================
# TARGET AGGREGATION - Combine all signals into ranked targets
# ============================================================================

def aggregate_targets(max_targets: int = 20) -> List[WolfTarget]:
    """
    Aggregate signals from ALL scanners into a unified, ranked target list.
    
    Scoring:
    - Pressure signal score (0-100) × 1.0
    - Insider buying bonus: +20
    - Multiple scanner hits bonus: +15 per additional scanner
    - High short interest (>20%) bonus: +10
    """
    
    print("🐺 AGGREGATING WOLF TARGETS...")
    print("="*60)
    
    # Track scores and signals for each ticker
    ticker_data = {}
    
    # 1. Load pressure signals (primary source)
    pressure_signals = load_pressure_signals()
    print(f"📊 Loaded {len(pressure_signals)} pressure signals")
    
    for sig in pressure_signals:
        ticker = sig.get('ticker', '')
        if not ticker:
            continue
            
        if ticker not in ticker_data:
            ticker_data[ticker] = {
                'signals': [],
                'score': 0,
                'thesis': '',
                'trapped': '',
                'entry': '',
                'target': '',
                'stop': '',
                'timing': ''
            }
        
        # Add pressure score
        score = sig.get('score', 0)
        ticker_data[ticker]['score'] += score
        ticker_data[ticker]['signals'].append(sig.get('type', 'pressure'))
        
        # Keep best thesis
        if not ticker_data[ticker]['thesis'] or score > 50:
            ticker_data[ticker]['thesis'] = sig.get('thesis', '')
            ticker_data[ticker]['trapped'] = sig.get('trapped_player', '')
            ticker_data[ticker]['entry'] = sig.get('entry_zone', '')
            ticker_data[ticker]['target'] = sig.get('target', '')
            ticker_data[ticker]['stop'] = sig.get('stop', '')
            ticker_data[ticker]['timing'] = sig.get('timing', '')
    
    # 2. Load tactical signals
    tactical = load_tactical_signals()
    tactical_count = sum(len(v) for k, v in tactical.items() if k not in ['timestamp', 'total_signals'])
    print(f"🔫 Loaded {tactical_count} tactical signals")
    
    for scanner_name, signals in tactical.items():
        if scanner_name in ['timestamp', 'total_signals']:
            continue
        if not isinstance(signals, list):
            continue
            
        for sig in signals:
            ticker = sig.get('ticker', '')
            if not ticker:
                continue
                
            if ticker not in ticker_data:
                ticker_data[ticker] = {
                    'signals': [],
                    'score': 0,
                    'thesis': sig.get('thesis', ''),
                    'trapped': 'retail',
                    'entry': f"Current: ${sig.get('current_price', 'N/A')}",
                    'target': '+10-15%',
                    'stop': '-5%',
                    'timing': 'Day trade or swing'
                }
            
            # Tactical signal = +30 base score
            ticker_data[ticker]['score'] += 30
            ticker_data[ticker]['signals'].append(scanner_name)
            
            # Update thesis if better
            if sig.get('thesis') and not ticker_data[ticker]['thesis']:
                ticker_data[ticker]['thesis'] = sig.get('thesis', '')
    
    # 3. Load insider buying
    insider_buys = load_smart_money()
    print(f"💰 Loaded {len(insider_buys)} insider purchases")
    
    insider_tickers = set()
    for purchase in insider_buys:
        ticker = purchase.get('ticker', '')
        if not ticker:
            continue
        insider_tickers.add(ticker)
        
        if ticker not in ticker_data:
            ticker_data[ticker] = {
                'signals': [],
                'score': 0,
                'thesis': f"Insider buying: ${purchase.get('total_value', 0):,.0f} by {purchase.get('owner', 'insider')[:30]}",
                'trapped': 'none (follow smart money)',
                'entry': f"Current price",
                'target': '+15-25%',
                'stop': '-7%',
                'timing': 'Swing trade (weeks)'
            }
        
        # Insider buying = +25 bonus
        ticker_data[ticker]['score'] += 25
        ticker_data[ticker]['signals'].append('insider_buying')
    
    # 4. Multiple signal bonus
    for ticker, data in ticker_data.items():
        unique_signals = len(set(data['signals']))
        if unique_signals > 1:
            data['score'] += (unique_signals - 1) * 15  # +15 per additional signal
    
    # 5. Convert to WolfTarget objects with live data
    targets = []
    
    # Sort by score and take top N
    sorted_tickers = sorted(ticker_data.items(), key=lambda x: x[1]['score'], reverse=True)[:max_targets * 2]
    
    print(f"\n🎯 Fetching data for top {len(sorted_tickers)} candidates...")
    
    for rank, (ticker, data) in enumerate(sorted_tickers, 1):
        if len(targets) >= max_targets:
            break
            
        try:
            info = get_stock_info(ticker)
            
            if info['price'] <= 0:
                print(f"  ⚠️ {ticker}: price is 0, skipping")
                continue
            
            # Determine primary signal source
            signals = data['signals']
            if 'short_squeeze' in signals:
                source = SignalSource.PRESSURE_SHORT_SQUEEZE.value
            elif 'panic_recovery' in signals:
                source = SignalSource.PRESSURE_PANIC_RECOVERY.value
            elif 'capitulation' in signals:
                source = SignalSource.PRESSURE_CAPITULATION.value
            elif 'laggard_catchup' in signals:
                source = SignalSource.PRESSURE_LAGGARD.value
            elif 'SECOND_DAY_MOMENTUM' in signals:
                source = SignalSource.TACTICAL_MOMENTUM.value
            elif 'LEADER_FOLLOWER_LAG' in signals:
                source = SignalSource.TACTICAL_LEADER_LAG.value
            elif 'insider_buying' in signals:
                source = SignalSource.SMART_MONEY.value
            else:
                source = SignalSource.CONVICTION.value
            
            # Calculate confidence (normalized score)
            confidence = min(100, int(data['score']))
            
            # Build target
            target = WolfTarget(
                rank=len(targets) + 1,
                ticker=ticker,
                company=info['company'][:40] if info['company'] else ticker,
                current_price=info['price'],
                signal_source=source,
                confidence=confidence,
                trapped_player=data['trapped'] or 'Unknown',
                thesis=data['thesis'][:200] if data['thesis'] else 'Multiple signals converging',
                entry_zone=data['entry'] or f"${info['price']:.2f}",
                target_price=data['target'] or '+10-15%',
                stop_loss=data['stop'] or '-5-7%',
                risk_reward='2:1+',
                timing=data['timing'] or 'Day/Swing',
                sector=SECTOR_MAP.get(ticker, info.get('sector', 'Unknown')[:20] if info.get('sector') else 'Unknown'),
                short_interest=info.get('short_pct', 0),
                insider_buying='Yes' if ticker in insider_tickers else 'No',
                volume_ratio=1.0,
                notes=f"Signals: {', '.join(list(set(signals))[:3])}"
            )
            
            targets.append(target)
            print(f"  #{target.rank} {ticker}: {confidence}/100 - {source}")
            
        except Exception as e:
            print(f"  ❌ {ticker}: Error - {e}")
            continue
    
    print(f"\n✅ Generated {len(targets)} targets")
    return targets

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_atp_csv(targets: List[WolfTarget], filepath: str = 'exports/wolf_atp_watchlist.csv'):
    """
    Export to Fidelity ATP format.
    ATP can import CSV with Symbol column.
    We add our own columns for reference.
    """
    Path('exports').mkdir(exist_ok=True)
    
    rows = []
    for t in targets:
        rows.append({
            'Symbol': t.ticker,
            'Rank': t.rank,
            'Confidence': f"{t.confidence}/100",
            'Signal': t.signal_source,
            'Sector': t.sector,
            'Price': f"${t.current_price:.2f}",
            'Entry': t.entry_zone,
            'Target': t.target_price,
            'Stop': t.stop_loss,
            'Thesis': t.thesis[:100],
            'Trapped': t.trapped_player,
            'Timing': t.timing,
            'Notes': t.notes
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(filepath, index=False)
    print(f"📁 ATP CSV saved: {filepath}")
    return filepath

def export_robinhood_csv(targets: List[WolfTarget], filepath: str = 'exports/wolf_robinhood.csv'):
    """
    Export simple CSV for Robinhood import.
    Robinhood only needs Symbol column.
    """
    Path('exports').mkdir(exist_ok=True)
    
    # Robinhood format - just symbols
    rows = [{'Symbol': t.ticker} for t in targets]
    
    df = pd.DataFrame(rows)
    df.to_csv(filepath, index=False)
    print(f"📁 Robinhood CSV saved: {filepath}")
    return filepath

def export_tradingview_txt(targets: List[WolfTarget], filepath: str = 'exports/wolf_tradingview.txt'):
    """Export TradingView watchlist format (comma-separated tickers)"""
    Path('exports').mkdir(exist_ok=True)
    
    symbols = [t.ticker for t in targets]
    
    with open(filepath, 'w') as f:
        f.write(','.join(symbols))
    
    print(f"📁 TradingView TXT saved: {filepath}")
    return filepath

def export_full_report(targets: List[WolfTarget], filepath: str = 'exports/wolf_targets_report.md'):
    """Export detailed markdown report for reading"""
    Path('exports').mkdir(exist_ok=True)
    
    lines = [
        "# 🐺 WOLF PACK TARGET LIST",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "> **The question isn't 'what does the chart say'. It's 'who will be FORCED to buy?'**",
        "",
        "---",
        "",
        "## 🎯 TOP TARGETS",
        "",
        "| Rank | Ticker | Confidence | Signal | Sector | Price | Entry | Target |",
        "|------|--------|------------|--------|--------|-------|-------|--------|"
    ]
    
    for t in targets[:10]:
        lines.append(f"| {t.rank} | **{t.ticker}** | {t.confidence}/100 | {t.signal_source} | {t.sector} | ${t.current_price:.2f} | {t.entry_zone} | {t.target_price} |")
    
    lines.extend([
        "",
        "---",
        "",
        "## 📋 DETAILED ANALYSIS",
        ""
    ])
    
    for t in targets:
        lines.extend([
            f"### #{t.rank} {t.ticker} - {t.company}",
            "",
            f"**Signal:** {t.signal_source}  ",
            f"**Confidence:** {t.confidence}/100  ",
            f"**Sector:** {t.sector}  ",
            "",
            f"**Current Price:** ${t.current_price:.2f}  ",
            f"**Entry Zone:** {t.entry_zone}  ",
            f"**Target:** {t.target_price}  ",
            f"**Stop Loss:** {t.stop_loss}  ",
            "",
            f"**Who's Trapped:** {t.trapped_player}  ",
            f"**Timing:** {t.timing}  ",
            "",
            f"**Thesis:** {t.thesis}",
            "",
            f"**Notes:** {t.notes}",
            "",
            "---",
            ""
        ])
    
    lines.extend([
        "",
        "## 🐺 REMEMBER",
        "",
        "- We don't predict price. We predict WHO WILL BE FORCED TO BUY.",
        "- 9:30-10:00 AM = The trap. Wait for real direction.",
        "- Position size: Never more than 10% per trade.",
        "- If the thesis breaks, the trade breaks. Exit.",
        "",
        "AWOOOO! 🐺"
    ])
    
    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"📁 Full report saved: {filepath}")
    return filepath

def export_json(targets: List[WolfTarget], filepath: str = 'exports/wolf_targets.json'):
    """Export as JSON for programmatic use"""
    Path('exports').mkdir(exist_ok=True)
    
    data = {
        'generated': datetime.now().isoformat(),
        'count': len(targets),
        'targets': [asdict(t) for t in targets]
    }
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"📁 JSON saved: {filepath}")
    return filepath

# ============================================================================
# MAIN
# ============================================================================

def run_export(max_targets: int = 20):
    """Run full export pipeline"""
    
    print("\n" + "="*70)
    print("🐺 WOLF EXPORT - GENERATING BATTLE PLAN")
    print("="*70)
    
    # Aggregate all signals into targets
    targets = aggregate_targets(max_targets=max_targets)
    
    if not targets:
        print("\n❌ No targets generated. Run scanners first:")
        print("   python hunt/pressure_framework.py")
        print("   python hunt/tactical_scanners.py")
        print("   python hunt/smart_money_hunter.py")
        return
    
    # Export to all formats
    print("\n" + "="*70)
    print("📤 EXPORTING TO ALL FORMATS")
    print("="*70)
    
    export_atp_csv(targets)
    export_robinhood_csv(targets)
    export_tradingview_txt(targets)
    export_full_report(targets)
    export_json(targets)
    
    # Print summary
    print("\n" + "="*70)
    print("🐺 EXPORT COMPLETE")
    print("="*70)
    
    print("\n📁 FILES READY:")
    print("   • exports/wolf_atp_watchlist.csv    → Import to Fidelity ATP")
    print("   • exports/wolf_robinhood.csv        → Import to Robinhood")
    print("   • exports/wolf_tradingview.txt      → Import to TradingView")
    print("   • exports/wolf_targets_report.md    → Read the full analysis")
    print("   • exports/wolf_targets.json         → Programmatic access")
    
    print("\n🎯 TOP 5 TARGETS:")
    for t in targets[:5]:
        print(f"   #{t.rank} {t.ticker:6} | {t.confidence:3}/100 | {t.signal_source:20} | {t.trapped_player[:15]}")
    
    print("\n" + "="*70)
    print("The wolf brain is ready. Import to ATP and hunt.")
    print("AWOOOO 🐺")
    print("="*70 + "\n")
    
    return targets

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Wolf Export - Generate watchlists for ATP/Robinhood')
    parser.add_argument('--targets', type=int, default=20, help='Number of targets (default: 20)')
    
    args = parser.parse_args()
    run_export(max_targets=args.targets)
