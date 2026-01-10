#!/usr/bin/env python3
"""
🐺 WHISPER SCANNER - Detect the SETUP Before the Move

"They can't hide everything. We watch the cracks."

Data Sources We CAN Pull:
1. SEC FTD Data - Fail-to-Deliver reports (bi-weekly, ~2 week delay)
2. Options OI Buildup - Multi-day accumulation patterns
3. Bid/Ask Spread Tightening - Market maker positioning
4. Unusual Volume Patterns - Pre-breakout accumulation
5. Short Interest Changes - Squeeze setups

Data We COULD Add (with more work):
- Dark pool prints (chartexchange.com - would need scraping)
- Conference schedules (ICR, CES, JPM Healthcare)
- Patent filings (USPTO API)
- Job postings (LinkedIn - would need scraping)

Usage:
    python3 whisper_scanner.py --ticker QUBT
    python3 whisper_scanner.py --watchlist
    python3 whisper_scanner.py --ftd  # Check FTD data
"""

import argparse
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json

# Our watchlist
WATCHLIST = [
    'QUBT', 'IONQ', 'QBTS', 'RGTI',  # Quantum
    'RDW', 'RKLB', 'LUNR', 'SPCE', 'MNTS',  # Space
    'UUUU', 'SMR', 'OKLO', 'NNE', 'LEU',  # Nuclear
    'USAR', 'MP',  # Rare Earth
    'LITE', 'AAOI', 'GFS', 'COHR',  # Photonics
    'AVAV', 'JOBY',  # Drones
]


def analyze_options_buildup(ticker: str, days: int = 10) -> dict:
    """
    Look for OPTIONS OI building over multiple days
    This is the QUIET accumulation - not single day spikes
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get all expiration dates
        expirations = stock.options
        if not expirations:
            return {'signal': False, 'reason': 'No options data'}
        
        # Look at nearest expiration
        nearest_exp = expirations[0]
        
        # Get options chain
        opt = stock.option_chain(nearest_exp)
        calls = opt.calls
        puts = opt.puts
        
        if len(calls) == 0:
            return {'signal': False, 'reason': 'No calls data'}
        
        # Calculate metrics
        total_call_oi = calls['openInterest'].sum()
        total_put_oi = puts['openInterest'].sum()
        total_call_volume = calls['volume'].sum()
        
        # Call/Put ratio
        cp_ratio = total_call_oi / max(total_put_oi, 1)
        
        # Volume to OI ratio (high = new positions being opened)
        vol_oi_ratio = total_call_volume / max(total_call_oi, 1)
        
        # Find the strike with highest OI (this is where smart money is betting)
        max_oi_strike = calls.loc[calls['openInterest'].idxmax()]
        
        # Get current price
        info = stock.info
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        
        # Calculate implied move
        if current_price > 0:
            target_strike = max_oi_strike['strike']
            implied_move = ((target_strike - current_price) / current_price) * 100
        else:
            implied_move = 0
        
        # SIGNAL: Bullish setup
        bullish_signals = []
        
        if cp_ratio > 2:
            bullish_signals.append(f"Call/Put ratio: {cp_ratio:.1f}x (bullish)")
        
        if vol_oi_ratio > 0.3:
            bullish_signals.append(f"Volume/OI: {vol_oi_ratio:.1f} (new positions opening)")
        
        if implied_move > 10:
            bullish_signals.append(f"Smart money targeting: ${target_strike} ({implied_move:+.1f}%)")
        
        return {
            'signal': len(bullish_signals) >= 2,
            'call_oi': total_call_oi,
            'put_oi': total_put_oi,
            'cp_ratio': cp_ratio,
            'vol_oi_ratio': vol_oi_ratio,
            'max_strike': max_oi_strike['strike'],
            'max_oi': max_oi_strike['openInterest'],
            'implied_move': implied_move,
            'expiration': nearest_exp,
            'signals': bullish_signals
        }
    except Exception as e:
        return {'signal': False, 'reason': str(e)}


def analyze_spread_tightening(ticker: str) -> dict:
    """
    When market makers KNOW something is coming, spreads tighten
    They want to capture the flow, not get run over
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        bid = info.get('bid', 0)
        ask = info.get('ask', 0)
        price = info.get('currentPrice') or info.get('regularMarketPrice', 1)
        
        if bid > 0 and ask > 0:
            spread = ask - bid
            spread_pct = (spread / price) * 100
            
            # Tight spread = something's up
            if spread_pct < 0.5:
                return {
                    'signal': True,
                    'spread': spread,
                    'spread_pct': spread_pct,
                    'interpretation': 'TIGHT spread - market makers confident, expecting flow'
                }
            elif spread_pct < 1.0:
                return {
                    'signal': False,
                    'spread': spread,
                    'spread_pct': spread_pct,
                    'interpretation': 'Normal spread'
                }
            else:
                return {
                    'signal': False,
                    'spread': spread,
                    'spread_pct': spread_pct,
                    'interpretation': 'WIDE spread - low confidence or illiquid'
                }
        return {'signal': False, 'reason': 'No bid/ask data'}
    except Exception as e:
        return {'signal': False, 'reason': str(e)}


def analyze_volume_pattern(ticker: str, lookback: int = 20) -> dict:
    """
    Look for QUIET accumulation patterns
    Not single day spikes - steady building over days
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='3mo')
        
        if len(hist) < lookback:
            return {'signal': False, 'reason': 'Not enough history'}
        
        # Recent volume vs average
        recent_vol = hist['Volume'].tail(5).mean()
        avg_vol = hist['Volume'].tail(lookback).mean()
        old_vol = hist['Volume'].head(lookback).mean()
        
        vol_trend = ((recent_vol - old_vol) / old_vol) * 100 if old_vol > 0 else 0
        vol_ratio = recent_vol / avg_vol if avg_vol > 0 else 0
        
        # Price trend (is price following volume?)
        recent_price = hist['Close'].tail(5).mean()
        old_price = hist['Close'].head(5).mean()
        price_change = ((recent_price - old_price) / old_price) * 100 if old_price > 0 else 0
        
        # SIGNAL: Volume building without price explosion (accumulation)
        signals = []
        
        if vol_trend > 50:
            signals.append(f"Volume trending UP {vol_trend:.0f}% over {lookback} days")
        
        if vol_ratio > 1.5 and abs(price_change) < 20:
            signals.append(f"Volume {vol_ratio:.1f}x average, price stable (ACCUMULATION)")
        
        # Check for consecutive up-volume days
        hist['up_volume'] = (hist['Close'] > hist['Open']) & (hist['Volume'] > avg_vol)
        recent_up_days = hist['up_volume'].tail(10).sum()
        
        if recent_up_days >= 6:
            signals.append(f"{recent_up_days}/10 recent days: up on above-average volume")
        
        return {
            'signal': len(signals) >= 1,
            'vol_trend': vol_trend,
            'vol_ratio': vol_ratio,
            'price_change': price_change,
            'up_volume_days': recent_up_days,
            'signals': signals
        }
    except Exception as e:
        return {'signal': False, 'reason': str(e)}


def analyze_short_interest(ticker: str) -> dict:
    """
    Look for squeeze setups - high short interest + volume
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        short_pct = info.get('shortPercentOfFloat', 0)
        short_ratio = info.get('shortRatio', 0)  # Days to cover
        
        signals = []
        
        if short_pct and short_pct > 0.15:  # >15% short
            signals.append(f"Short interest: {short_pct*100:.1f}% of float")
        
        if short_ratio and short_ratio > 5:  # >5 days to cover
            signals.append(f"Days to cover: {short_ratio:.1f} (squeeze potential)")
        
        return {
            'signal': len(signals) >= 1,
            'short_pct': short_pct,
            'short_ratio': short_ratio,
            'signals': signals
        }
    except Exception as e:
        return {'signal': False, 'reason': str(e)}


def get_ftd_info():
    """
    Info about SEC FTD data
    The SEC publishes Fail-to-Deliver data bi-weekly
    High FTDs = shorts struggling to find shares = squeeze setup
    """
    print("""
🐺 SEC FAIL-TO-DELIVER (FTD) DATA
{'='*60}

WHAT IT IS:
When someone sells short but can't locate shares to borrow,
it becomes a "Fail-to-Deliver." The SEC FORCES disclosure.

WHERE TO GET IT:
https://www.sec.gov/data/foiadocsfailsdatahtm

HOW TO READ IT:
- High FTD + Rising Price = Shorts are TRAPPED
- High FTD + Flat Price = Accumulation happening
- FTD Spike then Drop = They found shares (squeeze might be over)

DELAY:
Data is ~2 weeks old (T+2 settlement + reporting delay)
But it shows PATTERNS over time.

MANUAL CHECK:
1. Go to SEC site above
2. Download latest CNS file
3. Search for your ticker
4. Look for FTD spikes

AUTOMATION:
We could scrape this but it's semi-structured text files.
For now, manual check is more reliable.
""")


def scan_ticker_whispers(ticker: str):
    """
    Full whisper analysis for a single ticker
    Looking for the SETUP, not the SIGNAL
    """
    print(f"\n{'='*80}")
    print(f"🐺 WHISPER SCAN: {ticker}")
    print(f"{'='*80}")
    
    # Get basic info
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        name = info.get('shortName', ticker)
        print(f"\n{name}")
        print(f"Price: ${price:.2f}")
    except:
        print(f"\n{ticker}")
        price = 0
    
    whisper_score = 0
    all_signals = []
    
    # 1. Options Buildup
    print(f"\n📊 OPTIONS ANALYSIS:")
    print("-" * 40)
    opts = analyze_options_buildup(ticker)
    if opts.get('signal'):
        whisper_score += 25
        for s in opts.get('signals', []):
            print(f"   ✓ {s}")
            all_signals.append(s)
        print(f"   Max OI Strike: ${opts.get('max_strike', 0)} ({opts.get('implied_move', 0):+.1f}% from current)")
    else:
        print(f"   ○ No unusual options activity")
    
    # 2. Spread Analysis
    print(f"\n📊 SPREAD ANALYSIS:")
    print("-" * 40)
    spread = analyze_spread_tightening(ticker)
    if spread.get('signal'):
        whisper_score += 15
        print(f"   ✓ {spread.get('interpretation')}")
        print(f"   Spread: {spread.get('spread_pct', 0):.2f}%")
        all_signals.append(spread.get('interpretation'))
    else:
        print(f"   ○ {spread.get('interpretation', 'Normal spread')}")
    
    # 3. Volume Pattern
    print(f"\n📊 VOLUME PATTERN:")
    print("-" * 40)
    vol = analyze_volume_pattern(ticker)
    if vol.get('signal'):
        whisper_score += 25
        for s in vol.get('signals', []):
            print(f"   ✓ {s}")
            all_signals.append(s)
    else:
        print(f"   ○ No unusual volume pattern")
    
    # 4. Short Interest
    print(f"\n📊 SHORT INTEREST:")
    print("-" * 40)
    shorts = analyze_short_interest(ticker)
    if shorts.get('signal'):
        whisper_score += 20
        for s in shorts.get('signals', []):
            print(f"   ✓ {s}")
            all_signals.append(s)
    else:
        short_pct = shorts.get('short_pct', 0)
        if short_pct:
            print(f"   ○ Short interest: {short_pct*100:.1f}% (not elevated)")
        else:
            print(f"   ○ No short data available")
    
    # Summary
    print(f"\n{'='*80}")
    print(f"🐺 WHISPER SCORE: {whisper_score}/85")
    print(f"{'='*80}")
    
    if whisper_score >= 50:
        print(f"\n🔥 HIGH WHISPER ACTIVITY - Something is being SET UP")
        print(f"\nSignals detected:")
        for s in all_signals:
            print(f"   • {s}")
    elif whisper_score >= 25:
        print(f"\n⚡ MODERATE WHISPER ACTIVITY - Watch closely")
    else:
        print(f"\n○ LOW WHISPER ACTIVITY - No clear setup detected")
    
    return {
        'ticker': ticker,
        'score': whisper_score,
        'signals': all_signals,
        'options': opts,
        'volume': vol,
        'shorts': shorts
    }


def scan_watchlist():
    """Scan entire watchlist for whispers"""
    print(f"\n{'='*80}")
    print(f"🐺 WHISPER SCAN - FULL WATCHLIST")
    print(f"{'='*80}")
    print(f"\nScanning {len(WATCHLIST)} tickers for setup signals...\n")
    
    results = []
    
    for ticker in WATCHLIST:
        print(f"   Scanning {ticker}...", end='\r')
        
        whisper_score = 0
        signals = []
        
        # Quick analysis
        opts = analyze_options_buildup(ticker)
        if opts.get('signal'):
            whisper_score += 25
            signals.extend(opts.get('signals', []))
        
        vol = analyze_volume_pattern(ticker)
        if vol.get('signal'):
            whisper_score += 25
            signals.extend(vol.get('signals', []))
        
        shorts = analyze_short_interest(ticker)
        if shorts.get('signal'):
            whisper_score += 20
            signals.extend(shorts.get('signals', []))
        
        # Get price
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        except:
            price = 0
        
        results.append({
            'ticker': ticker,
            'price': price,
            'score': whisper_score,
            'signals': len(signals)
        })
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Display
    print(f"\n{'TICKER':<8} {'PRICE':>10} {'WHISPER':>10} {'SIGNALS':>10}")
    print("-" * 45)
    
    for r in results:
        indicator = "🔥" if r['score'] >= 50 else "⚡" if r['score'] >= 25 else "  "
        print(f"{r['ticker']:<8} ${r['price']:>8.2f} {r['score']:>9}/85 {r['signals']:>9} {indicator}")
    
    # Top picks
    hot_ones = [r for r in results if r['score'] >= 40]
    if hot_ones:
        print(f"\n{'='*80}")
        print(f"🔥 SOMETHING'S BEING SET UP:")
        print(f"{'='*80}")
        for r in hot_ones:
            print(f"\n   {r['ticker']} - Whisper Score {r['score']}/85")
            print(f"   Run: python3 whisper_scanner.py --ticker {r['ticker']}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description='🐺 Detect setups before the move')
    parser.add_argument('--ticker', '-t', help='Scan specific ticker')
    parser.add_argument('--watchlist', '-w', action='store_true', help='Scan full watchlist')
    parser.add_argument('--ftd', action='store_true', help='Show FTD data info')
    
    args = parser.parse_args()
    
    if args.ftd:
        get_ftd_info()
    elif args.ticker:
        scan_ticker_whispers(args.ticker.upper())
    elif args.watchlist:
        scan_watchlist()
    else:
        # Default: scan watchlist
        scan_watchlist()


if __name__ == '__main__':
    main()
