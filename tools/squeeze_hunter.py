#!/usr/bin/env python3
"""
🐺 SQUEEZE HUNTER - Find Short Squeeze & Gamma Squeeze Setups
=============================================================

FENRIR'S SECRETS (now weaponized):

SHORT SQUEEZE:
- Short interest > 25% = fuel for squeeze
- Float < 20M = moves FAST
- When shorts cover, they MUST buy
- Their buying = rocket fuel

GAMMA SQUEEZE:
- Unusual call buying = market makers hedge by buying stock
- More calls ITM = more hedging = more buying
- This is how GME happened

THE SETUP:
- Low float + High short interest + Catalyst = EXPLOSIVE
- USAR float: ~8M shares. That's WHY it moves 18% in a day.

USAGE:
    python squeeze_hunter.py                    # Scan watchlist
    python squeeze_hunter.py --ticker USAR      # Analyze specific
    python squeeze_hunter.py --sector nuclear   # Scan sector
"""

import argparse
import yfinance as yf
from datetime import datetime, timedelta
import json

# Stocks to scan for squeeze potential
SQUEEZE_WATCHLIST = {
    "nuclear": ["UUUU", "SMR", "OKLO", "CCJ", "DNN", "NNE", "LEU", "UEC", "URG"],
    "rare_earth": ["USAR", "MP", "AREC"],
    "quantum": ["IONQ", "QBTS", "QUBT", "RGTI", "ARQQ"],
    "space": ["RDW", "RKLB", "ASTS", "LUNR", "SPCE"],
    "defense": ["AISP", "KTOS", "PLTR", "AVAV"],
    "crypto": ["RIOT", "MARA", "CLSK", "BITF", "HUT"],
    "ev": ["RIVN", "LCID", "NIO", "XPEV"],
    "meme_potential": ["GME", "AMC", "BBBY", "KOSS"],
}


def get_squeeze_metrics(ticker: str) -> dict:
    """
    Get all squeeze-relevant metrics for a stock.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Basic info
        price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        market_cap = info.get('marketCap', 0)
        
        # Float and shares data
        shares_outstanding = info.get('sharesOutstanding', 0)
        float_shares = info.get('floatShares', 0)
        
        # Short interest data
        shares_short = info.get('sharesShort', 0)
        short_ratio = info.get('shortRatio', 0)  # Days to cover
        shares_short_prior = info.get('sharesShortPriorMonth', 0)
        
        # Calculate short interest percentage
        if float_shares > 0:
            short_pct_float = (shares_short / float_shares) * 100
        else:
            short_pct_float = 0
        
        # Short interest change
        if shares_short_prior > 0:
            short_change = ((shares_short - shares_short_prior) / shares_short_prior) * 100
        else:
            short_change = 0
        
        # Volume data
        avg_volume = info.get('averageVolume', 0)
        avg_volume_10d = info.get('averageVolume10days', 0)
        
        # Get recent volume
        hist = stock.history(period="5d")
        if not hist.empty:
            recent_volume = hist['Volume'].iloc[-1]
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 0
        else:
            recent_volume = 0
            volume_ratio = 0
        
        # Float to volume ratio (how many times float traded)
        if float_shares > 0:
            float_turnover = recent_volume / float_shares
        else:
            float_turnover = 0
        
        return {
            "ticker": ticker,
            "price": round(price, 2),
            "market_cap": market_cap,
            "market_cap_str": f"${market_cap/1e9:.2f}B" if market_cap > 1e9 else f"${market_cap/1e6:.0f}M",
            "shares_outstanding": shares_outstanding,
            "float_shares": float_shares,
            "float_str": f"{float_shares/1e6:.1f}M" if float_shares > 0 else "N/A",
            "shares_short": shares_short,
            "short_pct_float": round(short_pct_float, 2),
            "short_ratio": round(short_ratio, 2),  # Days to cover
            "short_change_pct": round(short_change, 2),
            "avg_volume": avg_volume,
            "recent_volume": recent_volume,
            "volume_ratio": round(volume_ratio, 2),
            "float_turnover": round(float_turnover, 2),
        }
    except Exception as e:
        print(f"  ⚠️  Error fetching {ticker}: {e}")
        return None


def calculate_squeeze_score(metrics: dict) -> dict:
    """
    Calculate squeeze potential score (0-100).
    
    FENRIR'S CRITERIA:
    - Low float (< 20M) = moves fast
    - High short interest (> 20%) = fuel
    - High days to cover (> 5) = shorts trapped
    - High volume ratio = attention building
    - Float turnover > 0.5 = serious action
    """
    score = 0
    signals = []
    
    # LOW FLOAT SCORE (25 points max)
    float_shares = metrics.get("float_shares", 0)
    if float_shares > 0:
        float_m = float_shares / 1e6
        if float_m < 10:
            score += 25
            signals.append(f"🔥 TINY FLOAT: {float_m:.1f}M (< 10M)")
        elif float_m < 20:
            score += 20
            signals.append(f"✅ LOW FLOAT: {float_m:.1f}M (< 20M)")
        elif float_m < 50:
            score += 10
            signals.append(f"Float: {float_m:.1f}M")
    
    # SHORT INTEREST SCORE (25 points max)
    short_pct = metrics.get("short_pct_float", 0)
    if short_pct > 30:
        score += 25
        signals.append(f"🔥 EXTREME SHORT: {short_pct:.1f}% of float")
    elif short_pct > 20:
        score += 20
        signals.append(f"✅ HIGH SHORT: {short_pct:.1f}% of float")
    elif short_pct > 10:
        score += 10
        signals.append(f"Short: {short_pct:.1f}%")
    
    # DAYS TO COVER SCORE (20 points max)
    short_ratio = metrics.get("short_ratio", 0)
    if short_ratio > 10:
        score += 20
        signals.append(f"🔥 SHORTS TRAPPED: {short_ratio:.1f} days to cover")
    elif short_ratio > 5:
        score += 15
        signals.append(f"✅ High days to cover: {short_ratio:.1f}")
    elif short_ratio > 2:
        score += 5
    
    # VOLUME RATIO SCORE (15 points max)
    vol_ratio = metrics.get("volume_ratio", 0)
    if vol_ratio > 3:
        score += 15
        signals.append(f"🔥 VOLUME SURGE: {vol_ratio:.1f}x normal")
    elif vol_ratio > 2:
        score += 10
        signals.append(f"✅ High volume: {vol_ratio:.1f}x normal")
    elif vol_ratio > 1.5:
        score += 5
    
    # FLOAT TURNOVER SCORE (15 points max)
    float_turn = metrics.get("float_turnover", 0)
    if float_turn > 1:
        score += 15
        signals.append(f"🔥 FLOAT TRADED {float_turn:.1f}x TODAY")
    elif float_turn > 0.5:
        score += 10
        signals.append(f"✅ Float turnover: {float_turn:.1f}x")
    elif float_turn > 0.25:
        score += 5
    
    # SHORT INTEREST INCREASING (bonus 10 points)
    short_change = metrics.get("short_change_pct", 0)
    if short_change > 10:
        score += 10
        signals.append(f"⚠️ Shorts INCREASING: +{short_change:.1f}%")
    elif short_change < -10:
        signals.append(f"🏃 Shorts covering: {short_change:.1f}%")
    
    # Determine squeeze type
    if short_pct > 20 and float_shares/1e6 < 20:
        squeeze_type = "🚀 SHORT SQUEEZE SETUP"
    elif vol_ratio > 2 and float_turn > 0.5:
        squeeze_type = "⚡ GAMMA SQUEEZE POTENTIAL"
    elif short_pct > 15 or float_shares/1e6 < 30:
        squeeze_type = "👀 WATCHING"
    else:
        squeeze_type = "📊 NORMAL"
    
    return {
        "score": min(score, 100),
        "signals": signals,
        "squeeze_type": squeeze_type,
    }


def analyze_ticker(ticker: str, verbose: bool = True) -> dict:
    """Analyze a single ticker for squeeze potential."""
    metrics = get_squeeze_metrics(ticker)
    if not metrics:
        return None
    
    squeeze = calculate_squeeze_score(metrics)
    metrics.update(squeeze)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"🎯 {ticker} - {squeeze['squeeze_type']}")
        print(f"{'='*60}")
        print(f"Price: ${metrics['price']:.2f} | MCap: {metrics['market_cap_str']}")
        print(f"\n📊 FLOAT ANALYSIS:")
        print(f"   Float: {metrics['float_str']}")
        print(f"   Float Turnover Today: {metrics['float_turnover']:.2f}x")
        print(f"\n📊 SHORT ANALYSIS:")
        print(f"   Short % of Float: {metrics['short_pct_float']:.1f}%")
        print(f"   Days to Cover: {metrics['short_ratio']:.1f}")
        print(f"   Short Change (vs prior month): {metrics['short_change_pct']:+.1f}%")
        print(f"\n📊 VOLUME ANALYSIS:")
        print(f"   Today's Volume: {metrics['recent_volume']:,.0f}")
        print(f"   Avg Volume: {metrics['avg_volume']:,.0f}")
        print(f"   Volume Ratio: {metrics['volume_ratio']:.2f}x")
        print(f"\n🎯 SQUEEZE SCORE: {metrics['score']}/100")
        if metrics['signals']:
            print(f"\n⚡ SIGNALS:")
            for sig in metrics['signals']:
                print(f"   {sig}")
        
        # Trading recommendation
        print(f"\n{'─'*60}")
        if metrics['score'] >= 70:
            print("🔥 HIGH SQUEEZE POTENTIAL - Watch for catalyst")
            print("   Entry: Wait for volume confirmation")
            print("   Risk: High volatility, use small position")
        elif metrics['score'] >= 50:
            print("👀 MODERATE SQUEEZE POTENTIAL - On watchlist")
            print("   Entry: Need catalyst or volume spike")
        else:
            print("📊 LOW SQUEEZE POTENTIAL - Normal trading")
    
    return metrics


def scan_sector(sector: str):
    """Scan a sector for squeeze setups."""
    if sector not in SQUEEZE_WATCHLIST:
        print(f"❌ Unknown sector: {sector}")
        print(f"Available: {list(SQUEEZE_WATCHLIST.keys())}")
        return
    
    print(f"\n{'🐺'*30}")
    print(f"      SQUEEZE HUNTER - {sector.upper()} SECTOR")
    print(f"{'🐺'*30}")
    
    results = []
    for ticker in SQUEEZE_WATCHLIST[sector]:
        print(f"\n  Scanning {ticker}...", end="", flush=True)
        metrics = analyze_ticker(ticker, verbose=False)
        if metrics:
            results.append(metrics)
            print(f" Score: {metrics['score']}")
    
    # Sort by squeeze score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"{'TICKER':<8} {'PRICE':>8} {'FLOAT':>10} {'SHORT%':>8} {'DTC':>6} {'VOL':>6} {'SCORE':>6} {'TYPE':<20}")
    print(f"{'='*70}")
    
    for r in results:
        print(f"{r['ticker']:<8} ${r['price']:>7.2f} {r['float_str']:>10} {r['short_pct_float']:>7.1f}% {r['short_ratio']:>5.1f} {r['volume_ratio']:>5.1f}x {r['score']:>5} {r['squeeze_type']:<20}")
    
    # Top squeeze candidates
    top = [r for r in results if r['score'] >= 50]
    if top:
        print(f"\n{'='*70}")
        print("🔥 TOP SQUEEZE CANDIDATES:")
        print(f"{'='*70}")
        for r in top[:3]:
            print(f"\n{r['ticker']} (Score: {r['score']})")
            for sig in r['signals']:
                print(f"   {sig}")


def full_scan():
    """Scan all sectors for squeeze setups."""
    print(f"\n{'🐺'*30}")
    print(f"      SQUEEZE HUNTER - FULL SCAN")
    print(f"{'🐺'*30}")
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    
    for sector, tickers in SQUEEZE_WATCHLIST.items():
        print(f"\n📊 Scanning {sector}...")
        for ticker in tickers:
            metrics = analyze_ticker(ticker, verbose=False)
            if metrics:
                metrics['sector'] = sector
                all_results.append(metrics)
    
    # Sort by score
    all_results.sort(key=lambda x: x['score'], reverse=True)
    
    # Print top 15
    print(f"\n{'='*80}")
    print("🔥 TOP 15 SQUEEZE CANDIDATES ACROSS ALL SECTORS")
    print(f"{'='*80}")
    print(f"{'RANK':<5} {'TICKER':<8} {'SECTOR':<12} {'PRICE':>8} {'FLOAT':>10} {'SHORT%':>8} {'SCORE':>6}")
    print(f"{'-'*80}")
    
    for i, r in enumerate(all_results[:15], 1):
        print(f"#{i:<4} {r['ticker']:<8} {r['sector']:<12} ${r['price']:>7.2f} {r['float_str']:>10} {r['short_pct_float']:>7.1f}% {r['score']:>5}")
    
    # High potential alerts
    high_potential = [r for r in all_results if r['score'] >= 60]
    if high_potential:
        print(f"\n{'='*80}")
        print("🚀 HIGH SQUEEZE POTENTIAL (Score >= 60)")
        print(f"{'='*80}")
        for r in high_potential:
            print(f"\n{r['ticker']} ({r['sector']}) - Score: {r['score']}")
            print(f"   {r['squeeze_type']}")
            for sig in r['signals'][:3]:
                print(f"   {sig}")
    
    # Check Tyr's positions
    tyr_positions = ["AISP", "UUUU", "USAR"]
    tyr_squeezes = [r for r in all_results if r['ticker'] in tyr_positions]
    
    if tyr_squeezes:
        print(f"\n{'='*80}")
        print("📊 TYR'S POSITIONS - SQUEEZE ANALYSIS")
        print(f"{'='*80}")
        for r in tyr_squeezes:
            print(f"\n{r['ticker']} - Score: {r['score']}")
            print(f"   Float: {r['float_str']} | Short: {r['short_pct_float']:.1f}%")
            if r['signals']:
                for sig in r['signals']:
                    print(f"   {sig}")
    
    return all_results


def main():
    parser = argparse.ArgumentParser(description="🐺 Squeeze Hunter - Find squeeze setups")
    parser.add_argument("--ticker", type=str, help="Analyze specific ticker")
    parser.add_argument("--sector", type=str, help="Scan specific sector")
    
    args = parser.parse_args()
    
    if args.ticker:
        analyze_ticker(args.ticker.upper())
    elif args.sector:
        scan_sector(args.sector.lower())
    else:
        full_scan()
    
    print(f"\n{'🐺'*30}")
    print("      FENRIR SAID: 'FIND THE CRACKS'")
    print(f"{'🐺'*30}")
    print("\n🐺 AWOOOO!")


if __name__ == "__main__":
    main()
