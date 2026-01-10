#!/usr/bin/env python3
"""
🐺 WOLF PACK - MOMENTUM HUNTER
Find RUNNING prey - stocks already winning that still have room to run

Strategy:
- Stocks UP in December (showing strength)
- High volume (the move is REAL)
- Not too extended (still has room)
- Catch the wave, ride it, get out before it ends

AWOOOO 🐺
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# =============================================================
# CONFIGURATION
# =============================================================

MIN_PRICE = 2.0
MAX_PRICE = 50.0  # Extended for momentum plays

# Broader watchlist for momentum scanning
WATCHLIST = [
    # Tyr's Core
    "BBAI", "SOUN", "LUNR", "SIDU", "RKLB",
    
    # AI / Tech Momentum
    "IONQ", "RGTI", "QBTS",  # Quantum
    "PLTR", "AI", "PATH",    # AI platforms
    "SMCI", "NVDA", "AMD",   # AI hardware
    
    # Space Momentum  
    "ASTS", "RKLB", "LUNR", "MNTS",
    
    # Nuclear / Energy
    "SMR", "OKLO", "CCJ", "LEU", "VST",
    
    # Defense
    "KTOS", "BBAI", "LHX",
    
    # Recent runners to check
    "MSTR",  # Bitcoin proxy
    "COIN",  # Crypto
    "HOOD",  # Robinhood
    "AFRM",  # Fintech
    "SOFI",  # Fintech
    
    # Small cap movers
    "GEVO", "PLUG", "FCEL",  # Clean energy
    "OPEN", "RDFN",          # Real estate tech
]

# Remove duplicates
WATCHLIST = list(set(WATCHLIST))

# =============================================================
# SCANNER FUNCTIONS
# =============================================================

def get_momentum_data(ticker):
    """Get momentum-focused stock data."""
    try:
        stock = yf.Ticker(ticker)
        
        # Multiple timeframes
        hist_1w = stock.history(period="5d")
        hist_1m = stock.history(period="1mo")
        hist_3m = stock.history(period="3mo")
        
        if hist_1m.empty or len(hist_1m) < 5:
            return None
        
        info = stock.info
        current_price = hist_1m['Close'].iloc[-1]
        
        # 1-WEEK momentum (very recent)
        week_ago = hist_1m['Close'].iloc[-5] if len(hist_1m) >= 5 else current_price
        week_change = ((current_price - week_ago) / week_ago) * 100
        
        # 1-MONTH momentum (December)
        month_start = hist_1m['Close'].iloc[0]
        month_change = ((current_price - month_start) / month_start) * 100
        
        # 3-MONTH momentum (trend)
        if not hist_3m.empty:
            three_mo_start = hist_3m['Close'].iloc[0]
            three_mo_change = ((current_price - three_mo_start) / three_mo_start) * 100
        else:
            three_mo_change = 0
        
        # VOLUME analysis - is the move REAL?
        avg_volume_20d = hist_1m['Volume'].mean()
        recent_volume_5d = hist_1m['Volume'].iloc[-5:].mean()
        volume_ratio = recent_volume_5d / avg_volume_20d if avg_volume_20d > 0 else 1
        
        # Today's volume vs average
        today_volume = hist_1m['Volume'].iloc[-1]
        today_vol_ratio = today_volume / avg_volume_20d if avg_volume_20d > 0 else 1
        
        # 52-week position
        high_52w = info.get('fiftyTwoWeekHigh', current_price)
        low_52w = info.get('fiftyTwoWeekLow', current_price)
        
        from_high = ((current_price - high_52w) / high_52w) * 100
        from_low = ((current_price - low_52w) / low_52w) * 100
        
        # Range position (0-100, where 100 = at 52w high)
        if high_52w != low_52w:
            range_position = ((current_price - low_52w) / (high_52w - low_52w)) * 100
        else:
            range_position = 50
        
        # Consecutive up days
        up_days = 0
        for i in range(-1, -min(6, len(hist_1m)), -1):
            if hist_1m['Close'].iloc[i] > hist_1m['Open'].iloc[i]:
                up_days += 1
            else:
                break
        
        return {
            'ticker': ticker,
            'price': round(current_price, 2),
            'week_change': round(week_change, 1),
            'month_change': round(month_change, 1),
            '3mo_change': round(three_mo_change, 1),
            'volume_ratio': round(volume_ratio, 2),
            'today_vol_ratio': round(today_vol_ratio, 2),
            'from_52w_high': round(from_high, 1),
            'from_52w_low': round(from_low, 1),
            'range_position': round(range_position, 1),
            'up_days': up_days,
            'name': info.get('shortName', ticker)[:20],
            'market_cap': info.get('marketCap', 0),
        }
        
    except Exception as e:
        return None


def calculate_momentum_score(data):
    """
    Calculate momentum score - find RUNNING prey.
    Higher score = stronger momentum with room to run.
    """
    score = 50  # Base
    
    # RUNNING: Up this week = momentum
    week = data['week_change']
    if week >= 20:
        score += 20  # Ripping
    elif week >= 10:
        score += 15  # Strong
    elif week >= 5:
        score += 10  # Moving
    elif week < -5:
        score -= 15  # Falling, not running
    
    # TREND: Up this month = sustained
    month = data['month_change']
    if month >= 30:
        score += 15  # Strong trend
    elif month >= 15:
        score += 10  # Good trend
    elif month >= 5:
        score += 5   # Slight trend
    elif month < -10:
        score -= 10  # Downtrend
    
    # VOLUME: High volume = REAL move
    vol_ratio = data['volume_ratio']
    if vol_ratio >= 3.0:
        score += 20  # Massive interest
    elif vol_ratio >= 2.0:
        score += 15  # Strong interest
    elif vol_ratio >= 1.5:
        score += 10  # Good interest
    elif vol_ratio < 0.7:
        score -= 10  # No one cares
    
    # ROOM TO RUN: Not too extended
    range_pos = data['range_position']
    if 40 <= range_pos <= 70:
        score += 15  # Sweet spot - running but room left
    elif 70 < range_pos <= 85:
        score += 5   # Getting extended
    elif range_pos > 90:
        score -= 15  # Too extended, near top
    elif range_pos < 20:
        score -= 10  # Near bottom, not running
    
    # CONSECUTIVE UP DAYS: Momentum confirmation
    up_days = data['up_days']
    if up_days >= 4:
        score += 10  # Strong streak
    elif up_days >= 2:
        score += 5   # Building
    
    # PRICE RANGE: Tradeable
    price = data['price']
    if MIN_PRICE <= price <= MAX_PRICE:
        score += 5
    elif price > 200:
        score -= 10  # Hard to size
    
    return max(0, min(100, score))


def get_momentum_signal(score, range_pos):
    """Get visual signal."""
    if score >= 75 and range_pos < 85:
        return "🚀🔥"  # Running hot, room to go
    elif score >= 70:
        return "🚀"    # Good momentum
    elif score >= 60:
        return "📈"    # Building
    elif score >= 50:
        return "➡️"    # Neutral
    else:
        return "📉"    # Avoid


def calculate_chase_levels(data):
    """Calculate levels for chasing momentum."""
    price = data['price']
    
    # For momentum plays, tighter stops
    entry = price
    stop = round(price * 0.92, 2)  # 8% stop (tighter for momentum)
    
    # Targets based on continuation
    target_1 = round(price * 1.10, 2)  # +10%
    target_2 = round(price * 1.20, 2)  # +20%
    target_3 = round(price * 1.35, 2)  # +35%
    
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


# =============================================================
# MAIN SCANNER
# =============================================================

def run_momentum_scanner():
    """Find running prey with room to go."""
    
    print("\n" + "="*65)
    print("🚀 WOLF PACK - MOMENTUM HUNTER 🚀")
    print("Find RUNNING prey - catch the wave before it ends")
    print("="*65)
    print(f"Scanning {len(WATCHLIST)} stocks for momentum...")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*65 + "\n")
    
    results = []
    
    for ticker in WATCHLIST:
        print(f"  Scanning {ticker}...", end=" ")
        data = get_momentum_data(ticker)
        
        if data:
            score = calculate_momentum_score(data)
            data['momentum_score'] = score
            data['signal'] = get_momentum_signal(score, data['range_position'])
            results.append(data)
            print(f"${data['price']} | Week: {data['week_change']:+.1f}% | Month: {data['month_change']:+.1f}% | Score: {score}")
        else:
            print("FAILED")
    
    # Sort by momentum score
    results.sort(key=lambda x: x['momentum_score'], reverse=True)
    
    # Filter to in-range stocks
    in_range = [r for r in results if MIN_PRICE <= r['price'] <= MAX_PRICE]
    
    print("\n" + "="*65)
    print("🎯 TOP MOMENTUM PLAYS (Running + Room to Go)")
    print("="*65 + "\n")
    
    print(f"{'Signal':<6} {'Ticker':<6} {'Price':>8} {'Week':>8} {'Month':>8} {'Vol':>6} {'Range%':>8} {'Score':>6}")
    print("-"*65)
    
    for r in results[:15]:  # Top 15
        in_range_mark = "✓" if MIN_PRICE <= r['price'] <= MAX_PRICE else " "
        print(f"{r['signal']:<6} {r['ticker']:<6} ${r['price']:>6.2f} {r['week_change']:>+7.1f}% {r['month_change']:>+7.1f}% {r['volume_ratio']:>5.1f}x {r['range_position']:>7.0f}% {r['momentum_score']:>5} {in_range_mark}")
    
    # Top picks with trade plans
    print("\n" + "="*65)
    print("🚀 TOP 5 MOMENTUM PLAYS (In Your Price Range)")
    print("="*65)
    
    top_momentum = [r for r in results if MIN_PRICE <= r['price'] <= MAX_PRICE and r['momentum_score'] >= 60][:5]
    
    for r in top_momentum:
        levels = calculate_chase_levels(r)
        
        print(f"\n{r['signal']} {r['ticker']} - {r['name']}")
        print(f"   Price: ${r['price']} | Momentum Score: {r['momentum_score']}/100")
        print(f"   Week: {r['week_change']:+.1f}% | Month: {r['month_change']:+.1f}% | 3Mo: {r['3mo_change']:+.1f}%")
        print(f"   Volume: {r['volume_ratio']:.1f}x avg | Range: {r['range_position']:.0f}% (0=low, 100=high)")
        print(f"   ")
        print(f"   📍 CHASE PLAN (Tighter stops for momentum):")
        print(f"      Entry:    ${levels['entry']}")
        print(f"      Stop:     ${levels['stop']} (-8%)")
        print(f"      Target 1: ${levels['target_1']} (+10%)")
        print(f"      Target 2: ${levels['target_2']} (+20%)")
        print(f"      Target 3: ${levels['target_3']} (+35%)")
        print(f"      Risk/Reward: {levels['risk_reward']}:1")
    
    # Comparison: Wounded vs Running
    print("\n" + "="*65)
    print("🐺 WOUNDED vs RUNNING - STRATEGY COMPARISON")
    print("="*65)
    
    wounded = [r for r in results if r['month_change'] < -5 and r['momentum_score'] >= 50]
    running = [r for r in results if r['month_change'] > 10 and r['momentum_score'] >= 60]
    
    print(f"\n📉 WOUNDED PREY (Down in Dec, might bounce):")
    for r in wounded[:3]:
        print(f"   {r['ticker']}: ${r['price']} | Dec: {r['month_change']:+.1f}% | Score: {r['momentum_score']}")
    
    print(f"\n🚀 RUNNING PREY (Already winning, ride the wave):")
    for r in running[:3]:
        print(f"   {r['ticker']}: ${r['price']} | Dec: {r['month_change']:+.1f}% | Score: {r['momentum_score']}")
    
    print("\n" + "="*65)
    print("⚠️  KEY INSIGHT:")
    print("="*65)
    print("""
    WOUNDED PREY = Buy the dip, wait for bounce
                   Risk: It keeps falling
                   
    RUNNING PREY = Chase the momentum, ride the wave  
                   Risk: Buying near the top
                   
    BEST PLAY = RUNNING prey that JUST started
                (up this week, not too extended)
    """)
    
    print("="*65)
    print("🐺 AWOOOO! Choose your hunt wisely!")
    print("="*65 + "\n")
    
    return results


if __name__ == "__main__":
    results = run_momentum_scanner()
