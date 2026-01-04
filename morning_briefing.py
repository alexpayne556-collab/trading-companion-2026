#!/usr/bin/env python3
"""
🐺 MORNING BRIEFING - THE DAILY BATTLE PLAN
============================================

Every morning, BEFORE market open, you need ONE document.
Not 50 tabs. Not 10 scanners. ONE PLAN.

This generates:
1. MARKET ENVIRONMENT - What's the field look like?
2. WHO'S TRAPPED TODAY - The pressure map
3. TOP 5 PLAYS - Full thesis for each
4. TIMING ZONES - When to act
5. RISK RULES - Position sizing for today
6. WATCHLIST - What else to monitor

The wolf wakes up. The wolf has a plan. The wolf executes.

Built by Brokkr & Fenrir
AWOOOO 🐺
"""

import json
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# MARKET ENVIRONMENT
# ============================================================================

def get_market_environment() -> Dict:
    """Assess the overall market environment"""
    
    env = {
        'spy': {'price': 0, 'change': 0, 'trend': 'Unknown'},
        'qqq': {'price': 0, 'change': 0, 'trend': 'Unknown'},
        'vix': {'price': 0, 'level': 'Unknown'},
        'sector_rotation': [],
        'risk_level': 'NORMAL',
        'bias': 'NEUTRAL'
    }
    
    # SPY
    try:
        spy = yf.Ticker('SPY')
        hist = spy.history(period='5d')
        if not hist.empty:
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
            change = ((current - prev) / prev) * 100
            
            # 5-day trend
            first = hist['Close'].iloc[0]
            trend = 'BULLISH' if current > first * 1.01 else ('BEARISH' if current < first * 0.99 else 'SIDEWAYS')
            
            env['spy'] = {'price': round(current, 2), 'change': round(change, 2), 'trend': trend}
    except:
        pass
    
    # QQQ
    try:
        qqq = yf.Ticker('QQQ')
        hist = qqq.history(period='5d')
        if not hist.empty:
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
            change = ((current - prev) / prev) * 100
            
            first = hist['Close'].iloc[0]
            trend = 'BULLISH' if current > first * 1.01 else ('BEARISH' if current < first * 0.99 else 'SIDEWAYS')
            
            env['qqq'] = {'price': round(current, 2), 'change': round(change, 2), 'trend': trend}
    except:
        pass
    
    # VIX
    try:
        vix = yf.Ticker('^VIX')
        hist = vix.history(period='1d')
        if not hist.empty:
            current = hist['Close'].iloc[-1]
            
            if current < 15:
                level = 'LOW (complacent)'
            elif current < 20:
                level = 'NORMAL'
            elif current < 25:
                level = 'ELEVATED'
            elif current < 30:
                level = 'HIGH (fear)'
            else:
                level = 'EXTREME (panic)'
            
            env['vix'] = {'price': round(current, 2), 'level': level}
    except:
        pass
    
    # Determine overall risk level
    vix_price = env['vix']['price']
    if vix_price > 25:
        env['risk_level'] = 'HIGH'
        env['bias'] = 'DEFENSIVE'
    elif vix_price > 20:
        env['risk_level'] = 'ELEVATED'
        env['bias'] = 'CAUTIOUS'
    elif env['spy']['trend'] == 'BULLISH' and env['qqq']['trend'] == 'BULLISH':
        env['risk_level'] = 'LOW'
        env['bias'] = 'RISK-ON'
    else:
        env['risk_level'] = 'NORMAL'
        env['bias'] = 'NEUTRAL'
    
    return env

def get_sector_movers() -> List[Dict]:
    """Check which sectors are moving"""
    
    sector_etfs = {
        'XLK': 'Technology',
        'XLF': 'Financials',
        'XLE': 'Energy',
        'XLV': 'Healthcare',
        'XLI': 'Industrials',
        'XLY': 'Consumer Disc',
        'XLP': 'Consumer Staples',
        'XLU': 'Utilities',
        'XLB': 'Materials',
        'XLRE': 'Real Estate'
    }
    
    movers = []
    
    for ticker, name in sector_etfs.items():
        try:
            etf = yf.Ticker(ticker)
            hist = etf.history(period='5d')
            if not hist.empty and len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = ((current - prev) / prev) * 100
                
                movers.append({
                    'sector': name,
                    'ticker': ticker,
                    'change': round(change, 2)
                })
        except:
            continue
    
    return sorted(movers, key=lambda x: x['change'], reverse=True)

# ============================================================================
# PRESSURE MAP
# ============================================================================

def load_pressure_signals() -> List[Dict]:
    """Load latest pressure framework signals"""
    try:
        with open('logs/pressure_scan_latest.json', 'r') as f:
            data = json.load(f)
            return data.get('signals', [])
    except FileNotFoundError:
        return []

def load_tactical_signals() -> Dict:
    """Load latest tactical scanner signals"""
    try:
        with open('logs/tactical_scan_latest.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_smart_money() -> List[Dict]:
    """Load latest smart money signals"""
    try:
        with open('logs/smart_money_latest.json', 'r') as f:
            data = json.load(f)
            return data.get('purchases', [])
    except FileNotFoundError:
        return []

def summarize_pressure() -> Dict:
    """Summarize who's trapped today"""
    
    signals = load_pressure_signals()
    
    summary = {
        'total_signals': len(signals),
        'short_squeeze': [],
        'panic_recovery': [],
        'capitulation': [],
        'laggard': [],
        'top_trapped': []
    }
    
    for sig in signals:
        sig_type = sig.get('type', '')
        ticker = sig.get('ticker', '')
        score = sig.get('score', 0)
        
        if sig_type == 'short_squeeze':
            summary['short_squeeze'].append({'ticker': ticker, 'score': score})
        elif sig_type == 'panic_recovery':
            summary['panic_recovery'].append({'ticker': ticker, 'score': score})
        elif sig_type == 'capitulation':
            summary['capitulation'].append({'ticker': ticker, 'score': score})
        elif sig_type == 'laggard_catchup':
            summary['laggard'].append({'ticker': ticker, 'score': score})
    
    # Top 5 overall
    summary['top_trapped'] = sorted(signals, key=lambda x: x.get('score', 0), reverse=True)[:5]
    
    return summary

# ============================================================================
# TOP PLAYS
# ============================================================================

def generate_top_plays(num_plays: int = 5) -> List[Dict]:
    """Generate top plays with full thesis"""
    
    plays = []
    
    # Get all signals
    pressure = load_pressure_signals()
    tactical = load_tactical_signals()
    insider = load_smart_money()
    
    # Score and rank
    ticker_scores = {}
    
    for sig in pressure:
        ticker = sig.get('ticker', '')
        score = sig.get('score', 0)
        if ticker:
            if ticker not in ticker_scores:
                ticker_scores[ticker] = {
                    'score': 0, 
                    'signals': [], 
                    'thesis': sig.get('thesis', ''),
                    'trapped': sig.get('trapped_player', ''),
                    'entry': sig.get('entry_zone', ''),
                    'target': sig.get('target', ''),
                    'stop': sig.get('stop', ''),
                    'timing': sig.get('timing', '')
                }
            ticker_scores[ticker]['score'] += score
            ticker_scores[ticker]['signals'].append(sig.get('type', 'pressure'))
    
    for scanner, signals in tactical.items():
        if scanner in ['timestamp', 'total_signals']:
            continue
        if not isinstance(signals, list):
            continue
        for sig in signals:
            ticker = sig.get('ticker', '')
            if ticker:
                if ticker not in ticker_scores:
                    ticker_scores[ticker] = {
                        'score': 0, 
                        'signals': [], 
                        'thesis': sig.get('thesis', ''),
                        'trapped': 'retail',
                        'entry': f"${sig.get('current_price', 0):.2f}",
                        'target': '+10-15%',
                        'stop': '-5%',
                        'timing': 'Day trade'
                    }
                ticker_scores[ticker]['score'] += 25
                ticker_scores[ticker]['signals'].append(scanner)
    
    insider_tickers = set()
    for purchase in insider:
        ticker = purchase.get('ticker', '')
        if ticker:
            insider_tickers.add(ticker)
            if ticker in ticker_scores:
                ticker_scores[ticker]['score'] += 20
                ticker_scores[ticker]['signals'].append('insider_buying')
    
    # Sort and take top plays
    sorted_tickers = sorted(ticker_scores.items(), key=lambda x: x[1]['score'], reverse=True)
    
    for ticker, data in sorted_tickers[:num_plays]:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1d')
            price = hist['Close'].iloc[-1] if not hist.empty else 0
            info = stock.info
            company = info.get('shortName', ticker)[:40]
        except:
            price = 0
            company = ticker
        
        plays.append({
            'ticker': ticker,
            'company': company,
            'price': round(price, 2),
            'confidence': min(100, data['score']),
            'signals': list(set(data['signals']))[:3],
            'thesis': data['thesis'] or 'Multiple signals converging',
            'trapped': data['trapped'] or 'Unknown',
            'entry': data['entry'] or f"${price:.2f}",
            'target': data['target'] or '+10-15%',
            'stop': data['stop'] or '-5%',
            'timing': data['timing'] or 'Day/Swing',
            'insider_buying': ticker in insider_tickers
        })
    
    return plays

# ============================================================================
# BRIEFING GENERATOR
# ============================================================================

def generate_briefing() -> str:
    """Generate the complete morning briefing"""
    
    now = datetime.now()
    lines = []
    
    # Header
    lines.extend([
        "# 🐺 WOLF PACK MORNING BRIEFING",
        f"**Date:** {now.strftime('%A, %B %d, %Y')}",
        f"**Generated:** {now.strftime('%H:%M')}",
        "",
        "> *\"We don't predict price. We predict WHO WILL BE FORCED TO BUY.\"*",
        "",
        "---",
        ""
    ])
    
    # Market Environment
    env = get_market_environment()
    
    lines.extend([
        "## 📊 MARKET ENVIRONMENT",
        "",
        "| Index | Price | Change | Trend |",
        "|-------|-------|--------|-------|",
        f"| **SPY** | ${env['spy']['price']} | {env['spy']['change']:+.2f}% | {env['spy']['trend']} |",
        f"| **QQQ** | ${env['qqq']['price']} | {env['qqq']['change']:+.2f}% | {env['qqq']['trend']} |",
        f"| **VIX** | {env['vix']['price']} | - | {env['vix']['level']} |",
        "",
        f"**Risk Level:** {env['risk_level']}  ",
        f"**Market Bias:** {env['bias']}  ",
        "",
    ])
    
    # Sector rotation
    sectors = get_sector_movers()
    if sectors:
        lines.extend([
            "### Sector Rotation",
            "",
            "| Sector | Change |",
            "|--------|--------|"
        ])
        for s in sectors[:5]:
            emoji = "🟢" if s['change'] > 0 else "🔴"
            lines.append(f"| {emoji} {s['sector']} | {s['change']:+.2f}% |")
        lines.append("")
    
    lines.append("---\n")
    
    # Pressure Map
    pressure = summarize_pressure()
    
    lines.extend([
        "## 🎯 WHO'S TRAPPED TODAY",
        "",
        f"**Total Pressure Signals:** {pressure['total_signals']}",
        "",
        "| Pressure Type | Count | Top Ticker |",
        "|---------------|-------|------------|",
        f"| 🔴 Short Squeeze | {len(pressure['short_squeeze'])} | {pressure['short_squeeze'][0]['ticker'] if pressure['short_squeeze'] else 'None'} |",
        f"| 🟡 Panic Recovery | {len(pressure['panic_recovery'])} | {pressure['panic_recovery'][0]['ticker'] if pressure['panic_recovery'] else 'None'} |",
        f"| 🟣 Capitulation | {len(pressure['capitulation'])} | {pressure['capitulation'][0]['ticker'] if pressure['capitulation'] else 'None'} |",
        f"| 🟠 Laggard Catch-up | {len(pressure['laggard'])} | {pressure['laggard'][0]['ticker'] if pressure['laggard'] else 'None'} |",
        "",
    ])
    
    lines.append("---\n")
    
    # Top 5 Plays
    plays = generate_top_plays(5)
    
    lines.extend([
        "## 🎯 TODAY'S TOP 5 PLAYS",
        ""
    ])
    
    for i, play in enumerate(plays, 1):
        insider_badge = "💰" if play['insider_buying'] else ""
        lines.extend([
            f"### #{i} {play['ticker']} - {play['company']} {insider_badge}",
            "",
            f"**Current Price:** ${play['price']:.2f}  ",
            f"**Confidence:** {play['confidence']}/100  ",
            f"**Signals:** {', '.join(play['signals'])}  ",
            "",
            f"**WHO'S TRAPPED:** {play['trapped']}  ",
            "",
            f"**THESIS:** {play['thesis']}",
            "",
            f"| Entry | Target | Stop | Timing |",
            f"|-------|--------|------|--------|",
            f"| {play['entry']} | {play['target']} | {play['stop']} | {play['timing']} |",
            "",
        ])
    
    lines.append("---\n")
    
    # Timing Zones
    lines.extend([
        "## ⏰ TIMING ZONES",
        "",
        "| Time | What's Happening | Action |",
        "|------|------------------|--------|",
        "| **9:30-10:00** | The Trap | ⚠️ DO NOT CHASE. Watch for direction. |",
        "| **10:00-11:00** | Real Direction | ✅ EXECUTE if thesis confirms. |",
        "| **11:00-3:00** | Chop Zone | ❌ NO EDGE. Manage existing. |",
        "| **3:00-4:00** | Power Hour | ✅ Institutions positioning. Watch. |",
        "",
    ])
    
    lines.append("---\n")
    
    # Risk Rules
    lines.extend([
        "## 🛡️ TODAY'S RISK RULES",
        "",
    ])
    
    if env['risk_level'] == 'HIGH':
        lines.extend([
            "**⚠️ HIGH RISK ENVIRONMENT**",
            "",
            "- Max position size: **5%** per trade",
            "- Max portfolio exposure: **30%**",
            "- Tighter stops: **-3%**",
            "- Consider sitting on hands",
            ""
        ])
    elif env['risk_level'] == 'ELEVATED':
        lines.extend([
            "**⚡ ELEVATED RISK**",
            "",
            "- Max position size: **7%** per trade",
            "- Max portfolio exposure: **50%**",
            "- Normal stops: **-5%**",
            "- Be selective",
            ""
        ])
    else:
        lines.extend([
            "**✅ NORMAL CONDITIONS**",
            "",
            "- Max position size: **10%** per trade",
            "- Max portfolio exposure: **70%**",
            "- Standard stops: **-5-7%**",
            "- Execute with confidence",
            ""
        ])
    
    lines.append("---\n")
    
    # Watchlist
    lines.extend([
        "## 👀 ADDITIONAL WATCHLIST",
        "",
        "Keep these on your radar:",
        ""
    ])
    
    # Get additional signals
    pressure_signals = load_pressure_signals()
    watchlist = []
    seen_tickers = set([p['ticker'] for p in plays])
    
    for sig in sorted(pressure_signals, key=lambda x: x.get('score', 0), reverse=True)[:15]:
        ticker = sig.get('ticker', '')
        if ticker and ticker not in seen_tickers:
            watchlist.append({
                'ticker': ticker,
                'type': sig.get('type', 'pressure'),
                'score': sig.get('score', 0)
            })
            seen_tickers.add(ticker)
    
    for w in watchlist[:10]:
        lines.append(f"- **{w['ticker']}** - {w['type'].replace('_', ' ').title()} (Score: {w['score']})")
    
    lines.extend([
        "",
        "---",
        "",
        "## 🐺 REMEMBER",
        "",
        "1. **The thesis is everything.** If it breaks, the trade breaks.",
        "2. **WHO is trapped?** That's the edge, not the chart.",
        "3. **Wait for 10:00 AM.** The first 30 minutes are a trap.",
        "4. **Position size is survival.** Never risk more than 10% per trade.",
        "5. **Cut losers fast.** Let winners run.",
        "",
        "---",
        "",
        f"*Briefing generated by Wolf Pack Command Center at {now.strftime('%H:%M')}*",
        "",
        "**AWOOOO! 🐺**"
    ])
    
    return '\n'.join(lines)

# ============================================================================
# MAIN
# ============================================================================

def run_briefing():
    """Generate and save morning briefing"""
    
    print("\n" + "="*60)
    print("🐺 GENERATING MORNING BRIEFING")
    print("="*60)
    
    # Generate briefing
    briefing = generate_briefing()
    
    # Save to file
    Path('exports').mkdir(exist_ok=True)
    
    date_str = datetime.now().strftime('%Y%m%d')
    filepath = f'exports/morning_briefing_{date_str}.md'
    
    with open(filepath, 'w') as f:
        f.write(briefing)
    
    # Also save as latest
    with open('exports/morning_briefing_latest.md', 'w') as f:
        f.write(briefing)
    
    print(f"\n📁 Briefing saved: {filepath}")
    print(f"📁 Also saved as: exports/morning_briefing_latest.md")
    
    # Print preview
    print("\n" + "="*60)
    print("📋 BRIEFING PREVIEW")
    print("="*60)
    
    # Print first ~50 lines
    lines = briefing.split('\n')
    for line in lines[:50]:
        print(line)
    
    print("\n... (see full briefing in exports/)")
    print("\n🐺 Briefing ready. The wolf has a plan. AWOOOO!\n")
    
    return briefing

if __name__ == "__main__":
    run_briefing()
