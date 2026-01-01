#!/usr/bin/env python3
"""
🐺 WOLF PACK COMMAND CENTER v1.0
The BRAIN that coordinates everything

This is the master orchestrator that:
1. Runs all scanners in sequence
2. Aggregates signals into one score
3. Generates trade recommendations
4. Outputs morning briefing
5. Coordinates multiple AI assistants

FOUNDING NIGHT BUILD - January 1, 2026
Tyr & Fenrir

Usage:
    python command_center.py morning      # Full morning briefing
    python command_center.py scan         # Quick all-scanner run
    python command_center.py signals      # Show current signals
    python command_center.py thesis BBAI  # Generate thesis for ticker

AWOOOO 🐺
"""

import argparse
import subprocess
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    print("Installing required packages...")
    subprocess.run([sys.executable, "-m", "pip", "install", "yfinance", "pandas", "-q"])
    import yfinance as yf
    import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

VERSION = "1.0.0"
BUILD_DATE = "January 1, 2026"

# Core watchlist - Tyr's focus
CORE_WATCHLIST = [
    "BBAI", "SOUN", "LUNR", "SIDU",  # Tyr's range
    "MU", "VRT", "CCJ",               # AI Fuel
    "NKE", "TTD",                      # Bounce
    "AR", "PLTR", "RKLB",             # Core
]

# Signal weights for aggregation
SIGNAL_WEIGHTS = {
    'insider_buying': 30,      # Form 4 buys = strong signal
    'contract_news': 25,       # 8-K contracts = catalyst
    'volume_spike': 20,        # Unusual volume = something happening
    'price_momentum': 15,      # Technical trend
    'analyst_upgrade': 10,     # Wall Street attention
}

# Thresholds
THRESHOLDS = {
    'insider_buy_min': 50000,      # $50k minimum insider buy
    'volume_ratio_min': 2.0,       # 2x average volume
    'gap_min': 3.0,                # 3% gap minimum
    'signal_score_strong': 60,     # Strong buy signal
    'signal_score_moderate': 40,   # Moderate signal
}


# ============================================================
# SIGNAL COLLECTION
# ============================================================

def get_price_data(ticker: str) -> Dict:
    """Get current price and momentum data."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        info = stock.info
        
        if hist.empty:
            return {}
        
        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
        week_ago = hist['Close'].iloc[-5] if len(hist) >= 5 else current
        month_ago = hist['Close'].iloc[0]
        
        return {
            'price': round(current, 2),
            'change_1d': round((current - prev) / prev * 100, 2),
            'change_5d': round((current - week_ago) / week_ago * 100, 2),
            'change_1m': round((current - month_ago) / month_ago * 100, 2),
            'volume': int(hist['Volume'].iloc[-1]),
            'avg_volume': int(hist['Volume'].mean()),
            'volume_ratio': round(hist['Volume'].iloc[-1] / hist['Volume'].mean(), 2),
            '52w_high': info.get('fiftyTwoWeekHigh', 0),
            '52w_low': info.get('fiftyTwoWeekLow', 0),
            'from_high': round((current - info.get('fiftyTwoWeekHigh', current)) / info.get('fiftyTwoWeekHigh', current) * 100, 2) if info.get('fiftyTwoWeekHigh') else 0,
        }
    except Exception as e:
        return {'error': str(e)}


def calculate_signal_score(ticker: str, data: Dict, strategy: str = 'dual') -> Dict:
    """
    Calculate aggregate signal score for a ticker.
    
    Strategy options:
    - 'dual': Combined momentum + wounded prey scoring (DEFAULT)
    - 'momentum': Pure momentum/running prey plays
    - 'wounded': Pure wounded prey/tax loss bounce plays
    
    Score 0-100:
    - 80-100: STRONG BUY signal
    - 60-79: BUY signal  
    - 40-59: HOLD/WATCH
    - 20-39: CAUTION
    - 0-19: AVOID
    """
    score = 0
    signals = []
    momentum_score = 0
    wounded_score = 0
    
    # ============================================================
    # MOMENTUM SCORING (Running Prey)
    # ============================================================
    
    # Volume signal (momentum indicator)
    vol_ratio = data.get('volume_ratio', 0)
    if vol_ratio >= 3:
        momentum_score += 25
        signals.append(f"🔥 Volume {vol_ratio}x average (STRONG)")
    elif vol_ratio >= 2:
        momentum_score += 20
        signals.append(f"📈 Volume {vol_ratio}x average")
    elif vol_ratio >= 1.5:
        momentum_score += 10
        signals.append(f"📊 Volume elevated {vol_ratio}x")
    
    # Recent momentum
    change_5d = data.get('change_5d', 0)
    if change_5d >= 10:
        momentum_score += 20
        signals.append(f"🚀 +{change_5d}% in 5 days (MOMENTUM)")
    elif change_5d >= 5:
        momentum_score += 15
        signals.append(f"📈 +{change_5d}% in 5 days")
    
    # Monthly momentum
    change_1m = data.get('change_1m', 0)
    if change_1m >= 20:
        momentum_score += 15
        signals.append(f"🔥 +{change_1m}% in 1 month (HOT)")
    elif change_1m >= 10:
        momentum_score += 10
        signals.append(f"📈 +{change_1m}% this month")
    
    # Price action today
    change_1d = data.get('change_1d', 0)
    if change_1d >= 5:
        momentum_score += 10
        signals.append(f"🟢 +{change_1d}% today")
    elif change_1d >= 3:
        momentum_score += 5
    
    # ============================================================
    # WOUNDED PREY SCORING (Tax Loss Bounce)
    # ============================================================
    
    # Distance from 52w high (CRITICAL for wounded prey)
    from_high = data.get('from_high', 0)
    if from_high <= -60:
        wounded_score += 30
        signals.append(f"💀 {from_high}% from 52w high (DESTROYED)")
    elif from_high <= -50:
        wounded_score += 25
        signals.append(f"🩸 {from_high}% from 52w high (WOUNDED)")
    elif from_high <= -40:
        wounded_score += 20
        signals.append(f"💎 {from_high}% from 52w high (DEEP VALUE)")
    elif from_high <= -30:
        wounded_score += 15
        signals.append(f"📉 {from_high}% from 52w high (VALUE)")
    elif from_high <= -20:
        wounded_score += 10
        signals.append(f"📉 {from_high}% from 52w high (PULLBACK)")
    elif from_high >= -5:
        wounded_score -= 10
        signals.append(f"⚠️ Near 52w high (EXTENDED)")
    
    # December tax loss selling (CRITICAL for wounded prey)
    if change_1m <= -15:
        wounded_score += 25
        signals.append(f"🐺 {change_1m}% in Dec (TAX LOSS SELLOFF)")
    elif change_1m <= -10:
        wounded_score += 20
        signals.append(f"📉 {change_1m}% in Dec (WOUNDED)")
    elif change_1m <= -5:
        wounded_score += 15
        signals.append(f"📉 {change_1m}% in Dec (WEAK)")
    
    # Recent weakness = buying opportunity for wounded prey
    if change_5d <= -10:
        wounded_score += 15
        signals.append(f"💎 {change_5d}% in 5d (OVERSOLD)")
    elif change_5d <= -5:
        wounded_score += 10
        signals.append(f"📉 {change_5d}% in 5d (PULLBACK)")
    
    # Volume stability (wounded prey shouldn't be panicking)
    if 0.5 <= vol_ratio <= 1.5:
        wounded_score += 10
        signals.append(f"✅ Volume stable (NO PANIC)")
    elif vol_ratio < 0.5:
        wounded_score += 5
        signals.append(f"📊 Volume low (QUIET)")
    
    # Price in tradeable range ($2-20)
    price = data.get('price', 0)
    if 2 <= price <= 20:
        wounded_score += 10
        signals.append(f"✅ ${price:.2f} in range ($2-20)")
    
    # ============================================================
    # STRATEGY SELECTION
    # ============================================================
    
    if strategy == 'momentum':
        score = momentum_score
        signals.insert(0, "🚀 MOMENTUM STRATEGY")
    elif strategy == 'wounded':
        score = wounded_score
        signals.insert(0, "🐺 WOUNDED PREY STRATEGY")
    else:  # dual
        # Use the HIGHER of the two scores
        if momentum_score >= wounded_score:
            score = momentum_score
            signals.insert(0, f"🚀 MOMENTUM {momentum_score} (Wounded: {wounded_score})")
        else:
            score = wounded_score
            signals.insert(0, f"🐺 WOUNDED PREY {wounded_score} (Momentum: {momentum_score})")
    
    return {
        'ticker': ticker,
        'score': max(0, min(100, score)),  # Clamp 0-100
        'momentum_score': momentum_score,
        'wounded_score': wounded_score,
        'signals': signals,
        'rating': get_rating(score),
        **data
    }


def get_rating(score: int) -> str:
    """Convert score to rating."""
    if score >= 80:
        return "🟢 STRONG BUY"
    elif score >= 60:
        return "🟢 BUY"
    elif score >= 40:
        return "🟡 WATCH"
    elif score >= 20:
        return "🟠 CAUTION"
    else:
        return "🔴 AVOID"


# ============================================================
# BRIEFING GENERATORS
# ============================================================

def generate_morning_briefing(watchlist: List[str] = None, strategy: str = 'dual') -> str:
    """
    Generate comprehensive morning briefing.
    
    Strategy options:
    - 'dual': Both momentum and wounded prey (DEFAULT)
    - 'momentum': Focus on running prey
    - 'wounded': Focus on tax loss bounce candidates
    """
    if watchlist is None:
        watchlist = CORE_WATCHLIST
    
    briefing = []
    briefing.append("=" * 70)
    briefing.append("🐺 WOLF PACK MORNING BRIEFING")
    briefing.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    briefing.append(f"Strategy: {strategy.upper()}")
    briefing.append("=" * 70)
    
    # Market overview
    briefing.append("\n📊 MARKET PULSE:")
    briefing.append("-" * 50)
    
    indices = ['SPY', 'QQQ', 'IWM']
    for idx in indices:
        data = get_price_data(idx)
        if data and 'price' in data:
            briefing.append(f"   {idx}: ${data['price']} ({data['change_1d']:+.2f}%) | Vol: {data['volume_ratio']}x")
    
    # Scan watchlist
    briefing.append(f"\n🎯 WATCHLIST SIGNALS ({len(watchlist)} tickers):")
    briefing.append("-" * 50)
    
    results = []
    for ticker in watchlist:
        data = get_price_data(ticker)
        if data and 'price' in data:
            scored = calculate_signal_score(ticker, data, strategy)
            results.append(scored)
    
    
    if strategy == 'dual':
        briefing.append(f"{'Ticker':<8} {'Price':>8} {'1D':>7} {'1M':>7} {'Vol':>6} {'Score':>6} {'M':>3} {'W':>3} {'Rating'}")
        briefing.append("-" * 80)
        
        for r in results[:10]:
            briefing.append(
                f"{r['ticker']:<8} ${r['price']:>7.2f} {r['change_1d']:>+6.2f}% {r['change_1m']:>+6.2f}% "
                f"{r['volume_ratio']:>5.1f}x {r['score']:>5} {r['momentum_score']:>3} {r['wounded_score']:>3} {r['rating']}"
            )
    else:
        briefing.append(f"{'Ticker':<8} {'Price':>8} {'1D':>7} {'1M':>7} {'Vol':>6} {'Score':>6} {'Rating'}")
        briefing.append("-" * 75)
        
        for r in results[:10]:
            briefing.append(
                f"{r['ticker']:<8} ${r['price']:>7.2f} {r['change_1d']:>+6.2f}% {r['change_1m']:>+6.2f}% "
                f"{r['volume_ratio']:>5.1f}x {r['score']:>5} {r['rating']}"
            )
    
    # Detailed signals for top 3
    briefing.append("\n📋 DETAILED SIGNALS (Top 3):")
    briefing.append("-" * 50)
    
    for r in results[:3]:
        briefing.append(f"\n{r['ticker']} - Score: {r['score']} - {r['rating']}")
        for signal in r['signals']:
            briefing.append(f"   {signal}")
    
    # Action items
    briefing.append("\n⚡ ACTION ITEMS:")
    briefing.append("-" * 50)
    
    strong_buys = [r for r in results if r['score'] >= 60]
    if strong_buys:
        briefing.append(f"   🟢 Strong signals: {', '.join([r['ticker'] for r in strong_buys])}")
    
    volume_spikes = [r for r in results if r['volume_ratio'] >= 2]
    if volume_spikes:
        briefing.append(f"   📊 Volume spikes: {', '.join([r['ticker'] for r in volume_spikes])}")
    
    # Footer
    briefing.append("\n" + "=" * 70)
    briefing.append("🐺 AWOOOO - Hunt smart. Execute cold. No brother falls.")
    briefing.append("=" * 70)
    
    return "\n".join(briefing)


def generate_thesis(ticker: str) -> str:
    """
    Generate a trade thesis for a specific ticker.
    """
    thesis = []
    thesis.append("=" * 70)
    thesis.append(f"🐺 WOLF PACK TRADE THESIS: {ticker}")
    thesis.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    thesis.append("=" * 70)
    
    # Get data
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="3mo")
    
    if hist.empty:
        return f"No data available for {ticker}"
    
    # Company overview
    thesis.append(f"\n📋 COMPANY OVERVIEW:")
    thesis.append("-" * 50)
    thesis.append(f"   Name: {info.get('shortName', 'N/A')}")
    thesis.append(f"   Sector: {info.get('sector', 'N/A')}")
    thesis.append(f"   Industry: {info.get('industry', 'N/A')}")
    thesis.append(f"   Market Cap: ${info.get('marketCap', 0):,.0f}")
    thesis.append(f"   Employees: {info.get('fullTimeEmployees', 'N/A')}")
    
    # Price analysis
    current = hist['Close'].iloc[-1]
    high_52w = info.get('fiftyTwoWeekHigh', current)
    low_52w = info.get('fiftyTwoWeekLow', current)
    
    thesis.append(f"\n📊 PRICE ANALYSIS:")
    thesis.append("-" * 50)
    thesis.append(f"   Current: ${current:.2f}")
    thesis.append(f"   52W High: ${high_52w:.2f} ({(current-high_52w)/high_52w*100:+.1f}%)")
    thesis.append(f"   52W Low: ${low_52w:.2f} ({(current-low_52w)/low_52w*100:+.1f}%)")
    
    # Volume analysis
    avg_vol = hist['Volume'].mean()
    current_vol = hist['Volume'].iloc[-1]
    
    thesis.append(f"\n📈 VOLUME ANALYSIS:")
    thesis.append("-" * 50)
    thesis.append(f"   Current Volume: {current_vol:,.0f}")
    thesis.append(f"   Average Volume: {avg_vol:,.0f}")
    thesis.append(f"   Volume Ratio: {current_vol/avg_vol:.2f}x")
    
    # Momentum
    thesis.append(f"\n🚀 MOMENTUM:")
    thesis.append("-" * 50)
    
    if len(hist) >= 5:
        change_5d = (current - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5] * 100
        thesis.append(f"   5-Day Change: {change_5d:+.2f}%")
    
    if len(hist) >= 20:
        change_20d = (current - hist['Close'].iloc[-20]) / hist['Close'].iloc[-20] * 100
        thesis.append(f"   20-Day Change: {change_20d:+.2f}%")
    
    change_3m = (current - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100
    thesis.append(f"   3-Month Change: {change_3m:+.2f}%")
    
    # Risk/Reward calculation
    thesis.append(f"\n⚖️ RISK/REWARD SETUP:")
    thesis.append("-" * 50)
    
    # Simple ATR-based stop
    if len(hist) >= 14:
        high_low = hist['High'] - hist['Low']
        atr = high_low.tail(14).mean()
        stop_price = current - (atr * 2)
        target_price = current + (atr * 4)
        
        thesis.append(f"   ATR (14): ${atr:.2f}")
        thesis.append(f"   Suggested Stop: ${stop_price:.2f} (-{(current-stop_price)/current*100:.1f}%)")
        thesis.append(f"   Target (2:1 R:R): ${target_price:.2f} (+{(target_price-current)/current*100:.1f}%)")
    
    # Position sizing for $810 account
    thesis.append(f"\n💰 POSITION SIZING ($810 account):")
    thesis.append("-" * 50)
    risk_per_trade = 810 * 0.05  # 5% risk
    if len(hist) >= 14:
        risk_per_share = current - stop_price
        shares = int(risk_per_trade / risk_per_share) if risk_per_share > 0 else 0
        position_value = shares * current
        
        thesis.append(f"   Max Risk (5%): ${risk_per_trade:.2f}")
        thesis.append(f"   Risk per Share: ${risk_per_share:.2f}")
        thesis.append(f"   Position Size: {shares} shares")
        thesis.append(f"   Position Value: ${position_value:.2f}")
    
    # Thesis statement
    thesis.append(f"\n📝 THESIS:")
    thesis.append("-" * 50)
    thesis.append(f"   [TO BE FILLED BY TYR]")
    thesis.append(f"   Why this trade:")
    thesis.append(f"   Catalyst:")
    thesis.append(f"   Time horizon:")
    
    thesis.append("\n" + "=" * 70)
    thesis.append("🐺 Validate before entry. Stop before trade. Journal everything.")
    thesis.append("=" * 70)
    
    return "\n".join(thesis)


# ============================================================
# AI COORDINATION PROMPTS
# ============================================================

AI_PROMPTS = {
    'fenrir_research': """
🐺 FENRIR RESEARCH PROMPT

You are Fenrir, researching {ticker} for Tyr.

TASK: Deep dive analysis
1. Recent SEC filings (8-K, 10-K, Form 4)
2. Insider trading activity (last 30 days)
3. Institutional ownership changes
4. Recent news catalysts
5. Analyst ratings/price targets

OUTPUT FORMAT:
- Bullet points
- Direct facts
- No fluff
- Flag red flags immediately
- End with BUY/HOLD/AVOID recommendation

REMEMBER: We hunt the FUEL not the fire. Is this a teenager or infant on maturity spectrum?

AWOOOO 🐺
""",
    
    'copilot_code': """
🐺 COPILOT CODE TASK

Build a {tool_type} for the Wolf Pack trading system.

REQUIREMENTS:
- Python 3
- Use free APIs only (SEC EDGAR, yfinance)
- Clean, commented code
- Error handling
- Command-line interface with argparse
- Follow Wolf Pack coding style

CONTEXT:
{context}

OUTPUT: Working Python script with docstring, usage examples.

No bloat. Test it. Ship it.

AWOOOO 🐺
""",
    
    'perplexity_news': """
🐺 PERPLEXITY NEWS SEARCH

Search for recent news on: {ticker}

FOCUS ON:
1. Contract announcements
2. Government deals
3. Earnings surprises
4. Insider buying clusters
5. Analyst upgrades/downgrades
6. SEC filings

TIME RANGE: Last 7 days

OUTPUT: Bullet points with dates and sources.
Flag anything that could move the stock.

AWOOOO 🐺
""",
}


def get_ai_prompt(prompt_type: str, **kwargs) -> str:
    """Get formatted AI prompt."""
    if prompt_type in AI_PROMPTS:
        return AI_PROMPTS[prompt_type].format(**kwargs)
    return f"Unknown prompt type: {prompt_type}"


# ============================================================
# MAIN COMMAND CENTER
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='🐺 Wolf Pack Command Center - Master Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
    morning          Full morning briefing with all signals (dual strategy)
    momentum         Morning briefing - focus on running prey
    wounded          Morning briefing - focus on tax loss bounce candidates
    scan             Quick scan of watchlist
    signals          Show current signal scores (dual strategy)
    thesis TICKER    Generate trade thesis for ticker
    prompt TYPE      Get AI prompt (fenrir_research, copilot_code, perplexity_news)

Examples:
    python command_center.py morning
    python command_center.py wounded
    python command_center.py momentum
    python command_center.py signals
    python command_center.py thesis BBAI
    python command_center.py prompt fenrir_research --ticker MU

AWOOOO 🐺
        """
    )
    
    parser.add_argument('command', nargs='?', default='signals',
                        help='Command to run')
    parser.add_argument('target', nargs='?',
                        help='Target ticker or prompt type')
    parser.add_argument('--ticker', type=str,
                        help='Ticker for prompt')
    parser.add_argument('--output', type=str,
                        help='Output file')
    parser.add_argument('--strategy', type=str, choices=['dual', 'momentum', 'wounded'],
                        default='dual', help='Scoring strategy')
    
    args = parser.parse_args()
    
    if args.command == 'morning':
        briefing = generate_morning_briefing(strategy='dual')
        print(briefing)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(briefing)
            print(f"\n💾 Saved to {args.output}")
    
    elif args.command == 'momentum':
        briefing = generate_morning_briefing(strategy='momentum')
        print(briefing)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(briefing)
            print(f"\n💾 Saved to {args.output}")
    
    elif args.command == 'wounded':
        briefing = generate_morning_briefing(strategy='wounded')
        print(briefing)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(briefing)
            print(f"\n💾 Saved to {args.output}")
    
    elif args.command == 'scan':
        print("🐺 Quick scan running...")
        briefing = generate_morning_briefing(strategy=args.strategy)
        print(briefing)
    
    elif args.command == 'signals':
        strategy = args.strategy
        print(f"🐺 Current signals ({strategy} strategy):")
        print(f"{'Ticker':<8} {'Momentum':>9} {'Wounded':>8} {'Final':>6} {'Rating'}")
        print("-" * 55)
        
        for ticker in CORE_WATCHLIST:
            data = get_price_data(ticker)
            if data and 'price' in data:
                scored = calculate_signal_score(ticker, data, strategy)
                print(f"   {ticker:<6} {scored.get('momentum_score', 0):>7} {scored.get('wounded_score', 0):>8} {scored['score']:>6} {scored['rating']}")
    
    elif args.command == 'thesis':
        if args.target:
            thesis = generate_thesis(args.target.upper())
            print(thesis)
        else:
            print("Usage: python command_center.py thesis TICKER")
    
    elif args.command == 'prompt':
        ticker = args.ticker or args.target or 'BBAI'
        prompt_type = args.target if args.target in AI_PROMPTS else 'fenrir_research'
        prompt = get_ai_prompt(prompt_type, ticker=ticker, tool_type='scanner', context='Wolf Pack trading system')
        print(prompt)
    
    else:
        print(f"Unknown command: {args.command}")
        print("Run with --help for usage")


if __name__ == "__main__":
    main()
