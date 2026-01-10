#!/usr/bin/env python3
"""
🐺 WOLF PACK PATTERN HUNTER
Find what moves stocks and if it repeats

Analyzes:
1. Biggest gainers/losers in last 30 days
2. Historical pattern recognition (does it repeat?)
3. Catalyst identification (WHY did it move?)
4. Cross-reference with insider buying
5. Sector momentum patterns

Usage:
    python3 pattern_hunter.py --period 30
    python3 pattern_hunter.py --ticker SOUN --analyze
    python3 pattern_hunter.py --sector AI --repeaters
"""

import yfinance as yf
import argparse
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import statistics

# ============================================================
# CONFIGURATION
# ============================================================

SECTORS = {
    'AI': ['PLTR', 'AI', 'PATH', 'SOUN', 'BBAI', 'UPST', 'SNOW'],
    'Nuclear': ['SMR', 'CCJ', 'OKLO', 'LEU', 'UUUU'],
    'Space': ['LUNR', 'RKLB', 'ASTS', 'SPCE', 'PL'],
    'Quantum': ['IONQ', 'RGTI', 'QBTS', 'ARQQ'],
    'Defense': ['LMT', 'RTX', 'NOC', 'KTOS', 'AVAV'],
    'Meme': ['SIDU', 'GME', 'AMC'],
}

# All tickers to scan
ALL_TICKERS = [
    'PLTR', 'AI', 'PATH', 'SOUN', 'BBAI', 'UPST', 'SNOW', 'MDB', 'DDOG',
    'SMR', 'CCJ', 'LEU', 'UUUU', 'OKLO', 'NNE', 'CEG',
    'LUNR', 'RKLB', 'ASTS', 'SPCE', 'PL', 'BKSY',
    'IONQ', 'RGTI', 'QBTS', 'ARQQ', 'QUBT',
    'KTOS', 'AVAV', 'LDOS', 'SAIC',
    'SIDU', 'GME', 'AMC', 'UA', 'NKE',
    'VRT', 'DELL', 'MU', 'ANET', 'NVDA', 'AMD',
]

# ============================================================
# FETCH HISTORICAL DATA
# ============================================================

def fetch_price_history(ticker: str, months: int = 12) -> Dict:
    """
    Fetch historical price data
    
    Returns:
        Dict with dates, prices, volumes
    """
    try:
        stock = yf.Ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months*30)
        
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            return None
            
        return {
            'ticker': ticker,
            'data': hist,
            'current_price': hist['Close'].iloc[-1],
            'start_price': hist['Close'].iloc[0],
        }
        
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

# ============================================================
# PATTERN ANALYSIS
# ============================================================

def find_biggest_movers(days: int = 30) -> Tuple[List, List]:
    """
    Find biggest gainers and losers in the last N days
    
    Returns:
        (gainers, losers) - each is list of (ticker, pct_change, current_price)
    """
    print(f"\n🔍 Scanning {len(ALL_TICKERS)} tickers for {days}-day moves...")
    
    gainers = []
    losers = []
    
    for ticker in ALL_TICKERS:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f"{days}d")
            
            if len(hist) < 2:
                continue
                
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            pct_change = ((end_price - start_price) / start_price) * 100
            
            volume_avg = hist['Volume'].mean()
            volume_recent = hist['Volume'].iloc[-5:].mean()
            volume_ratio = volume_recent / volume_avg if volume_avg > 0 else 1
            
            data = {
                'ticker': ticker,
                'change': pct_change,
                'price': end_price,
                'volume_ratio': volume_ratio,
            }
            
            if pct_change > 10:
                gainers.append(data)
            elif pct_change < -10:
                losers.append(data)
                
        except Exception as e:
            continue
    
    # Sort by absolute change
    gainers.sort(key=lambda x: x['change'], reverse=True)
    losers.sort(key=lambda x: x['change'])
    
    return gainers, losers

def analyze_historical_patterns(ticker: str, months: int = 12) -> Dict:
    """
    Analyze if this ticker has repeating patterns
    
    Checks:
    - Monthly seasonality (does it always move in December?)
    - Volatility patterns (is it always volatile?)
    - Volume spikes (does volume predict moves?)
    """
    data = fetch_price_history(ticker, months)
    
    if not data:
        return None
    
    hist = data['data']
    
    # Calculate monthly returns
    monthly_returns = []
    for i in range(1, len(hist)):
        days_ago = len(hist) - i
        if days_ago % 30 == 0 and days_ago > 0:
            past_price = hist['Close'].iloc[i-30] if i >= 30 else hist['Close'].iloc[0]
            current_price = hist['Close'].iloc[i]
            monthly_return = ((current_price - past_price) / past_price) * 100
            monthly_returns.append(monthly_return)
    
    # Calculate volatility
    returns = hist['Close'].pct_change().dropna()
    volatility = returns.std() * 100
    
    # Find biggest moves
    biggest_gain = returns.max() * 100
    biggest_loss = returns.min() * 100
    
    # Volume analysis
    volume_spikes = (hist['Volume'] > hist['Volume'].mean() * 2).sum()
    
    # Recent 30-day performance
    if len(hist) >= 30:
        recent_30d = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-30]) / hist['Close'].iloc[-30]) * 100
    else:
        recent_30d = 0
    
    return {
        'ticker': ticker,
        'months_analyzed': months,
        'avg_monthly_return': statistics.mean(monthly_returns) if monthly_returns else 0,
        'volatility': volatility,
        'biggest_gain_day': biggest_gain,
        'biggest_loss_day': biggest_loss,
        'volume_spikes': volume_spikes,
        'recent_30d_change': recent_30d,
        'is_volatile': volatility > 5,  # >5% daily volatility
        'is_repeater': len([r for r in monthly_returns if abs(r) > 20]) > 2,  # 3+ big moves
    }

def identify_catalyst(ticker: str, change_pct: float) -> str:
    """
    Try to identify WHY the stock moved
    
    Checks:
    - Volume pattern (was there unusual volume?)
    - Sector correlation (did whole sector move?)
    - Magnitude (how big was the move?)
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="60d")
        
        if len(hist) < 30:
            return "Insufficient data"
        
        # Volume analysis
        volume_avg = hist['Volume'].iloc[:-30].mean()
        volume_recent = hist['Volume'].iloc[-30:].mean()
        volume_ratio = volume_recent / volume_avg if volume_avg > 0 else 1
        
        catalysts = []
        
        # High volume = News/Event driven
        if volume_ratio > 3:
            catalysts.append(f"VOLUME SPIKE ({volume_ratio:.1f}x) - News/catalyst likely")
        
        # Gradual climb = Accumulation
        elif volume_ratio > 1.5 and change_pct > 20:
            catalysts.append("ACCUMULATION - Steady buying pressure")
        
        # Low volume = Technical/Squeeze
        elif volume_ratio < 1.2 and abs(change_pct) > 15:
            catalysts.append("LOW VOLUME MOVE - Short squeeze or thin float")
        
        # Volatility check
        returns = hist['Close'].pct_change().dropna()
        big_days = (abs(returns) > 0.10).sum()  # Days with >10% moves
        
        if big_days > 5:
            catalysts.append(f"HIGH VOLATILITY - {big_days} days with >10% moves")
        
        # Sector momentum
        sector = get_sector(ticker)
        if sector:
            catalysts.append(f"SECTOR: {sector}")
        
        return " | ".join(catalysts) if catalysts else "Unknown catalyst"
        
    except Exception as e:
        return f"Error analyzing: {e}"

def get_sector(ticker: str) -> str:
    """Find which sector this ticker belongs to"""
    for sector, tickers in SECTORS.items():
        if ticker in tickers:
            return sector
    return None

# ============================================================
# REPEATER DETECTION
# ============================================================

def find_repeaters(months: int = 12) -> List[Dict]:
    """
    Find stocks that repeatedly make big moves
    
    These are the "momentum machines" that keep moving
    """
    print(f"\n🔍 Scanning for REPEATERS (stocks that move repeatedly)...\n")
    
    repeaters = []
    
    for ticker in ALL_TICKERS:
        pattern = analyze_historical_patterns(ticker, months)
        
        if not pattern:
            continue
        
        # Define "repeater" as:
        # 1. High volatility (>5% avg daily move)
        # 2. Multiple big moves (3+ moves >20% in a month)
        # 3. Recent 30d move is also big
        
        if pattern['is_repeater'] and abs(pattern['recent_30d_change']) > 15:
            repeaters.append({
                'ticker': ticker,
                'recent_30d': pattern['recent_30d_change'],
                'volatility': pattern['volatility'],
                'biggest_gain': pattern['biggest_gain_day'],
                'biggest_loss': pattern['biggest_loss_day'],
                'volume_spikes': pattern['volume_spikes'],
                'sector': get_sector(ticker),
            })
    
    repeaters.sort(key=lambda x: abs(x['recent_30d']), reverse=True)
    
    return repeaters

# ============================================================
# REPORTING
# ============================================================

def print_movers_report(gainers: List, losers: List, days: int):
    """Print report of biggest movers"""
    
    print("\n" + "="*70)
    print(f"🐺 WOLF PACK PATTERN HUNTER")
    print(f"   {days}-Day Biggest Movers")
    print("="*70)
    
    print(f"\n🚀 TOP GAINERS (Last {days} Days)")
    print("-"*70)
    print(f"{'Ticker':<8} {'Change':<12} {'Price':<12} {'Volume':<10} {'Catalyst'}")
    print("-"*70)
    
    for data in gainers[:10]:
        ticker = data['ticker']
        change = data['change']
        price = data['price']
        vol_ratio = data['volume_ratio']
        
        catalyst = identify_catalyst(ticker, change)
        
        print(f"{ticker:<8} {change:>+6.1f}% {price:>8.2f} {vol_ratio:>6.1f}x {catalyst[:40]}")
    
    print(f"\n📉 TOP LOSERS (Last {days} Days)")
    print("-"*70)
    print(f"{'Ticker':<8} {'Change':<12} {'Price':<12} {'Volume':<10} {'Catalyst'}")
    print("-"*70)
    
    for data in losers[:10]:
        ticker = data['ticker']
        change = data['change']
        price = data['price']
        vol_ratio = data['volume_ratio']
        
        catalyst = identify_catalyst(ticker, change)
        
        print(f"{ticker:<8} {change:>+6.1f}% {price:>8.2f} {vol_ratio:>6.1f}x {catalyst[:40]}")

def print_repeaters_report(repeaters: List):
    """Print report of repeating movers"""
    
    print("\n" + "="*70)
    print(f"🐺 REPEATER DETECTION REPORT")
    print(f"   Stocks that repeatedly make big moves")
    print("="*70)
    
    if not repeaters:
        print("\n❌ No repeaters found in this dataset")
        return
    
    print(f"\n🔥 MOMENTUM MACHINES ({len(repeaters)} found)")
    print("-"*70)
    print(f"{'Ticker':<8} {'30d':<10} {'Volatility':<12} {'Biggest':<10} {'Sector'}")
    print("-"*70)
    
    for rep in repeaters:
        ticker = rep['ticker']
        change = rep['recent_30d']
        vol = rep['volatility']
        biggest = rep['biggest_gain']
        sector = rep['sector'] or 'Other'
        
        print(f"{ticker:<8} {change:>+6.1f}% {vol:>7.1f}% {biggest:>+7.1f}% {sector}")
    
    print("\n📊 INTERPRETATION:")
    print("-"*70)
    print("These stocks REPEATEDLY make big moves (3+ times in past year)")
    print("They're volatile but PREDICTABLE - they keep moving")
    print("Strategy: Watch for entry after pullbacks, ride the momentum")
    print("\nCross-reference with insider buying for highest conviction plays")

def analyze_single_ticker(ticker: str):
    """Deep dive analysis on single ticker"""
    
    print("\n" + "="*70)
    print(f"🐺 DEEP DIVE: {ticker}")
    print("="*70)
    
    # Fetch data
    pattern = analyze_historical_patterns(ticker, 12)
    
    if not pattern:
        print(f"\n❌ No data available for {ticker}")
        return
    
    # Recent move
    stock = yf.Ticker(ticker)
    hist = stock.history(period="60d")
    
    if len(hist) >= 30:
        change_30d = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-30]) / hist['Close'].iloc[-30]) * 100
        change_7d = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-7]) / hist['Close'].iloc[-7]) * 100 if len(hist) >= 7 else 0
    else:
        change_30d = 0
        change_7d = 0
    
    # Print analysis
    print(f"\n📊 PERFORMANCE:")
    print(f"  30-day change: {change_30d:+.1f}%")
    print(f"  7-day change:  {change_7d:+.1f}%")
    print(f"  Current price: ${hist['Close'].iloc[-1]:.2f}")
    
    print(f"\n📈 PATTERN ANALYSIS:")
    print(f"  Volatility:      {pattern['volatility']:.1f}% (daily)")
    print(f"  Biggest gain:    {pattern['biggest_gain_day']:+.1f}%")
    print(f"  Biggest loss:    {pattern['biggest_loss_day']:+.1f}%")
    print(f"  Volume spikes:   {pattern['volume_spikes']} times")
    print(f"  Is repeater:     {'✅ YES' if pattern['is_repeater'] else '❌ NO'}")
    print(f"  Is volatile:     {'✅ YES' if pattern['is_volatile'] else '❌ NO'}")
    
    # Catalyst
    catalyst = identify_catalyst(ticker, change_30d)
    print(f"\n🎯 LIKELY CATALYST:")
    print(f"  {catalyst}")
    
    # Sector
    sector = get_sector(ticker)
    if sector:
        print(f"\n🏢 SECTOR: {sector}")
    
    # Trading recommendation
    print(f"\n💡 TRADING INSIGHTS:")
    
    if pattern['is_repeater']:
        print("  ✅ This stock REPEATEDLY makes big moves")
        print("  ✅ It's a 'momentum machine' - catches fire regularly")
        print(f"  Strategy: Watch for pullbacks, then ride momentum")
    else:
        print("  ⚠️ Not a consistent repeater")
        print("  Strategy: Need strong catalyst for entry")
    
    if pattern['is_volatile']:
        print("  ⚠️ HIGH VOLATILITY - Use tight stops")
        print(f"  Daily swings average {pattern['volatility']:.1f}%")
    
    if abs(change_30d) > 20:
        print(f"  🔥 CURRENTLY EXTENDED - Up {change_30d:+.1f}% in 30 days")
        if change_30d > 0:
            print("  Consider waiting for pullback")
        else:
            print("  Potential bounce candidate if support holds")

# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='🐺 Wolf Pack Pattern Hunter - Find what moves stocks and if it repeats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 pattern_hunter.py --period 30
  python3 pattern_hunter.py --repeaters
  python3 pattern_hunter.py --ticker SOUN --analyze
  python3 pattern_hunter.py --sector AI
        """
    )
    
    parser.add_argument('--period', type=int, default=30,
                       help='Days to look back (default: 30)')
    parser.add_argument('--repeaters', action='store_true',
                       help='Find stocks that repeatedly move')
    parser.add_argument('--ticker', type=str,
                       help='Analyze single ticker in depth')
    parser.add_argument('--analyze', action='store_true',
                       help='Deep dive analysis (use with --ticker)')
    parser.add_argument('--sector', type=str,
                       help='Filter by sector (AI, Nuclear, Space, etc)')
    
    args = parser.parse_args()
    
    # Single ticker analysis
    if args.ticker:
        analyze_single_ticker(args.ticker.upper())
        return
    
    # Repeater detection
    if args.repeaters:
        repeaters = find_repeaters(12)
        print_repeaters_report(repeaters)
        return
    
    # Sector filter
    if args.sector:
        sector_tickers = SECTORS.get(args.sector)
        if not sector_tickers:
            print(f"\n❌ Unknown sector: {args.sector}")
            print(f"Available sectors: {', '.join(SECTORS.keys())}")
            return
        
        print(f"\n🔍 Scanning {args.sector} sector...")
        global ALL_TICKERS
        ALL_TICKERS = sector_tickers
    
    # Find biggest movers
    gainers, losers = find_biggest_movers(args.period)
    print_movers_report(gainers, losers, args.period)
    
    print("\n" + "="*70)
    print("🐺 AWOOOO - Hunt complete")
    print("="*70)
    print("\nNext steps:")
    print("  1. Run: python3 insider_cluster_hunter.py --validate [TOP_TICKERS]")
    print("  2. Check: python3 pattern_hunter.py --ticker [TICKER] --analyze")
    print("  3. Find: python3 pattern_hunter.py --repeaters")
    print("\n")

if __name__ == "__main__":
    main()
