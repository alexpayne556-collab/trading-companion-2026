#!/usr/bin/env python3
"""
🐺 WOLF PACK - JANUARY BOUNCE HUNTER
Find wounded prey ready to run

Strategy:
- Stocks beaten down in December (tax loss selling)
- NOT broken businesses (still have catalysts)
- Ready to bounce in January

AWOOOO 🐺
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# =============================================================
# CONFIGURATION - TYR'S HUNTING GROUND
# =============================================================

# Price range Tyr trades
MIN_PRICE = 2.0
MAX_PRICE = 25.0  # Slightly extended for good opportunities

# Watchlist - Our prey
WATCHLIST = [
    # Tyr's Core Range ($2-20)
    "BBAI",   # BigBear.ai - Defense AI
    "SOUN",   # SoundHound - Voice AI
    "LUNR",   # Intuitive Machines - Space
    "SIDU",   # Sidus Space
    "RKLB",   # Rocket Lab - Space
    "IONQ",   # Quantum computing
    "RGTI",   # Rigetti - Quantum
    "DNA",    # Ginkgo Bioworks
    "TELL",   # Tellurian - LNG
    "RIG",    # Transocean
    
    # AI Fuel Chain
    "SMR",    # NuScale - Nuclear
    "OKLO",   # Oklo - Nuclear
    "LEU",    # Centrus - Uranium
    
    # Tax Loss Bounce Candidates (higher priced but key)
    "NKE",    # Nike - MASSIVE insider buying
    "TTD",    # Trade Desk - beaten down
    "LULU",   # Lululemon - tax loss sold
    "DECK",   # Deckers - beaten
    
    # Defense
    "KTOS",   # Kratos Defense
    "PLTR",   # Palantir
]

# =============================================================
# SCANNER FUNCTIONS
# =============================================================

def get_stock_data(ticker):
    """Get comprehensive stock data for analysis."""
    try:
        stock = yf.Ticker(ticker)
        
        # Get price history
        hist_1m = stock.history(period="1mo")
        hist_3m = stock.history(period="3mo")
        hist_6m = stock.history(period="6mo")
        
        if hist_1m.empty:
            return None
        
        # Current price
        current_price = hist_1m['Close'].iloc[-1]
        
        # December performance (wounded?)
        dec_start = hist_1m['Close'].iloc[0] if len(hist_1m) > 20 else current_price
        dec_change = ((current_price - dec_start) / dec_start) * 100
        
        # 3-month performance
        if not hist_3m.empty:
            three_mo_start = hist_3m['Close'].iloc[0]
            three_mo_change = ((current_price - three_mo_start) / three_mo_start) * 100
        else:
            three_mo_change = 0
        
        # Volume analysis
        avg_volume = hist_1m['Volume'].mean()
        recent_volume = hist_1m['Volume'].iloc[-5:].mean()
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        
        # 52-week range
        info = stock.info
        high_52w = info.get('fiftyTwoWeekHigh', current_price)
        low_52w = info.get('fiftyTwoWeekLow', current_price)
        
        # Distance from 52w high (how beaten down?)
        from_high = ((current_price - high_52w) / high_52w) * 100
        
        # Distance from 52w low (how much room to fall?)
        from_low = ((current_price - low_52w) / low_52w) * 100
        
        return {
            'ticker': ticker,
            'price': round(current_price, 2),
            'dec_change': round(dec_change, 1),
            '3mo_change': round(three_mo_change, 1),
            'from_52w_high': round(from_high, 1),
            'from_52w_low': round(from_low, 1),
            'volume_ratio': round(volume_ratio, 2),
            'avg_volume': int(avg_volume),
            'market_cap': info.get('marketCap', 0),
            'name': info.get('shortName', ticker)[:20],
        }
        
    except Exception as e:
        print(f"  Error fetching {ticker}: {e}")
        return None


def calculate_bounce_score(data):
    """
    Calculate how likely this stock is to bounce.
    Higher score = better bounce candidate.
    """
    score = 50  # Base score
    
    # WOUNDED: Down in December = GOOD for bounce
    dec_change = data['dec_change']
    if dec_change <= -20:
        score += 25  # Very wounded
    elif dec_change <= -10:
        score += 15  # Wounded
    elif dec_change <= -5:
        score += 10  # Slightly wounded
    elif dec_change > 5:
        score -= 10  # Already running, missed it
    
    # BEATEN FROM HIGHS: Far from 52w high = room to run
    from_high = data['from_52w_high']
    if from_high <= -50:
        score += 20  # Massively beaten
    elif from_high <= -30:
        score += 15  # Very beaten
    elif from_high <= -20:
        score += 10  # Beaten
    
    # NOT DEAD: Still above 52w low = not completely broken
    from_low = data['from_52w_low']
    if from_low >= 20:
        score += 10  # Healthy distance from bottom
    elif from_low < 5:
        score -= 10  # Too close to bottom, might be broken
    
    # VOLUME: Recent volume uptick = interest returning
    vol_ratio = data['volume_ratio']
    if vol_ratio >= 2.0:
        score += 15  # High interest
    elif vol_ratio >= 1.5:
        score += 10  # Growing interest
    elif vol_ratio < 0.5:
        score -= 10  # Dead money
    
    # PRICE RANGE: In Tyr's range = tradeable
    price = data['price']
    if MIN_PRICE <= price <= MAX_PRICE:
        score += 10  # Perfect range
    elif price > 100:
        score -= 15  # Too expensive for position sizing
    
    return max(0, min(100, score))


def get_signal_emoji(score):
    """Get visual signal based on score."""
    if score >= 75:
        return "🟢🔥"  # Strong bounce candidate
    elif score >= 60:
        return "🟢"    # Good candidate
    elif score >= 50:
        return "🟡"    # Watch
    else:
        return "🔴"    # Skip


def calculate_trade_levels(data):
    """Calculate entry, stop, and target levels."""
    price = data['price']
    
    # Entry: Current price or slight pullback
    entry = price
    
    # Stop: 10% below entry
    stop = round(price * 0.90, 2)
    
    # Targets based on bounce potential
    target_1 = round(price * 1.15, 2)  # +15%
    target_2 = round(price * 1.25, 2)  # +25%
    target_3 = round(price * 1.40, 2)  # +40%
    
    # Risk/Reward
    risk = entry - stop
    reward = target_2 - entry
    rr_ratio = round(reward / risk, 1) if risk > 0 else 0
    
    return {
        'entry': entry,
        'stop': stop,
        'target_1': target_1,
        'target_2': target_2,
        'target_3': target_3,
        'risk_reward': rr_ratio
    }


def position_size(price, account_size=1120, risk_percent=5):
    """Calculate position size based on risk."""
    risk_amount = account_size * (risk_percent / 100)
    stop_distance = price * 0.10  # 10% stop
    
    shares = int(risk_amount / stop_distance)
    position_value = shares * price
    
    return {
        'shares': shares,
        'position_value': round(position_value, 2),
        'risk_amount': round(risk_amount, 2)
    }


# =============================================================
# MAIN SCANNER
# =============================================================

def run_scanner():
    """Run the January Bounce Hunter scanner."""
    
    print("\n" + "="*60)
    print("🐺 WOLF PACK - JANUARY BOUNCE HUNTER 🐺")
    print("="*60)
    print(f"Scanning {len(WATCHLIST)} stocks for wounded prey...")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Price Range: ${MIN_PRICE} - ${MAX_PRICE}")
    print("="*60 + "\n")
    
    results = []
    
    for ticker in WATCHLIST:
        print(f"  Scanning {ticker}...", end=" ")
        data = get_stock_data(ticker)
        
        if data:
            score = calculate_bounce_score(data)
            data['bounce_score'] = score
            data['signal'] = get_signal_emoji(score)
            results.append(data)
            print(f"${data['price']} | Dec: {data['dec_change']}% | Score: {score}")
        else:
            print("FAILED")
    
    # Sort by bounce score
    results.sort(key=lambda x: x['bounce_score'], reverse=True)
    
    # Display results
    print("\n" + "="*60)
    print("🎯 TOP BOUNCE CANDIDATES (Sorted by Score)")
    print("="*60 + "\n")
    
    print(f"{'Signal':<8} {'Ticker':<6} {'Price':>8} {'Dec %':>8} {'From High':>10} {'Vol Ratio':>10} {'Score':>6}")
    print("-"*60)
    
    for r in results:
        print(f"{r['signal']:<8} {r['ticker']:<6} ${r['price']:>6.2f} {r['dec_change']:>7.1f}% {r['from_52w_high']:>9.1f}% {r['volume_ratio']:>9.1f}x {r['bounce_score']:>6}")
    
    # Top picks with trade plans
    print("\n" + "="*60)
    print("🐺 TOP 5 ATTACK TARGETS")
    print("="*60)
    
    top_5 = [r for r in results[:5] if r['price'] <= MAX_PRICE]
    
    for r in top_5:
        levels = calculate_trade_levels(r)
        sizing = position_size(r['price'])
        
        print(f"\n{r['signal']} {r['ticker']} - {r['name']}")
        print(f"   Price: ${r['price']} | Score: {r['bounce_score']}/100")
        print(f"   December: {r['dec_change']}% | From 52w High: {r['from_52w_high']}%")
        print(f"   ")
        print(f"   📍 TRADE PLAN:")
        print(f"      Entry:    ${levels['entry']}")
        print(f"      Stop:     ${levels['stop']} (-10%)")
        print(f"      Target 1: ${levels['target_1']} (+15%)")
        print(f"      Target 2: ${levels['target_2']} (+25%)")
        print(f"      Target 3: ${levels['target_3']} (+40%)")
        print(f"      Risk/Reward: {levels['risk_reward']}:1")
        print(f"   ")
        print(f"   💰 POSITION SIZE ($1,120 account, 5% risk):")
        print(f"      Shares: {sizing['shares']}")
        print(f"      Value:  ${sizing['position_value']}")
        print(f"      Risk:   ${sizing['risk_amount']}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    strong = len([r for r in results if r['bounce_score'] >= 70])
    good = len([r for r in results if 60 <= r['bounce_score'] < 70])
    watch = len([r for r in results if 50 <= r['bounce_score'] < 60])
    skip = len([r for r in results if r['bounce_score'] < 50])
    
    print(f"🟢🔥 Strong Candidates: {strong}")
    print(f"🟢  Good Candidates:   {good}")
    print(f"🟡  Watch List:        {watch}")
    print(f"🔴  Skip:              {skip}")
    
    in_range = len([r for r in results if MIN_PRICE <= r['price'] <= MAX_PRICE])
    print(f"\n📍 In Your Price Range (${MIN_PRICE}-${MAX_PRICE}): {in_range} stocks")
    
    print("\n" + "="*60)
    print("🐺 AWOOOO! Hunt ready for January 2nd!")
    print("="*60 + "\n")
    
    return results


# =============================================================
# RUN IT
# =============================================================

if __name__ == "__main__":
    results = run_scanner()
