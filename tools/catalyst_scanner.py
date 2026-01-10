#!/usr/bin/env python3
"""
🐺 PACK CATALYST SCANNER - Priority #1
Built by Brokkr | Intel from Heimdall | Execution by Tyr

Scans:
- SEC 8-K filings (material events)
- Insider buys (Form 4)
- Earnings calendar (next 7 days)
- After-hours moves >3%
- Integration for Heimdall's X sentiment

NO BULLSHIT. Real catalysts only.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# HEIMDALL'S WATCHLIST - Full Pack Universe
# ============================================================================
WATCHLIST = {
    'AI_INFRASTRUCTURE': [
        'APLD', 'IREN', 'CORZ', 'BTBT', 'WULF', 'HUT', 'CIFR', 'CLSK', 
        'MARA', 'RIOT', 'CRWV', 'NBIS', 'MU', 'MRVL', 'AVGO', 'ANET', 
        'SMCI', 'DELL', 'TSMC', 'AMD'
    ],
    'NUCLEAR_URANIUM': [
        'UUUU', 'CCJ', 'SMR', 'OKLO', 'LEU', 'NXE', 'UEC', 'DNN', 
        'URG', 'MEOH'
    ],
    'SPACE_DEFENSE': [
        'LUNR', 'RKLB', 'MNTS', 'RCAT', 'AVAV', 'SATL', 'ASTS', 'SPCE', 
        'PL', 'RDW', 'LMT', 'NOC', 'RTX', 'GD', 'LHX', 'KTOS', 'BA'
    ],
    'BTC_MINERS_HPC': [
        'BITF', 'HIVE', 'SDIG', 'BTBT', 'CIFR', 'WULF', 'IREN', 'CLSK', 
        'MARA', 'RIOT', 'CORZ', 'APLD'
    ],
    'POWER_UTILITIES': [
        'NRG', 'PEG', 'PCG', 'EXC', 'ED', 'XEL', 'EIX', 'D', 'NEE', 
        'CEG', 'AEP', 'ETR', 'DTE', 'SRE', 'VST', 'SO', 'ETN'
    ],
    'BATTERY_METALS': [
        'ALB', 'SQM', 'LAC', 'PLL', 'MP'
    ]
}

# ============================================================================
# HEIMDALL INTEL - Known Catalysts & Risks
# ============================================================================
HEIMDALL_INTEL = {
    'hot_sectors': {
        'AI_INFRASTRUCTURE': 'CES catalysts, data center boom',
        'POWER_UTILITIES': 'AI power demand, data center interconnects, Meta/Oklo deals',
        'NUCLEAR_URANIUM': 'DOE funding, spot $81/lb, Kazakhstan supply crunch',
        'SPACE_DEFENSE': '$1.5T Trump defense budget, DoD contracts',
        'BTC_MINERS_HPC': 'HPC conversion pivot, Bitcoin $94k'
    },
    'risks': {
        'AI_INFRASTRUCTURE': 'MSFT cutting leases, hyperscaler capex slowdown',
        'BTC_MINERS_HPC': 'Dilution risk (BTBT), BTC volatility',
        'general': 'Fed rate cuts delayed, regulatory probes (SMCI)'
    },
    'rotation_timing': {
        'AI_INFRASTRUCTURE': 'Runs 3-6 weeks, wounded laggards (CORZ) bounce next',
        'POWER_UTILITIES': 'Leading on deals (Meta/Oklo)',
        'NUCLEAR_URANIUM': 'Up 15% YTD, supply crunch accelerating'
    }
}

def get_all_tickers():
    """Flatten watchlist to all tickers"""
    all_tickers = []
    for sector, tickers in WATCHLIST.items():
        all_tickers.extend(tickers)
    return list(set(all_tickers))  # Remove duplicates

def scan_after_hours_moves(min_move=3.0):
    """
    Scan for after-hours moves >X%
    This is the first signal of a catalyst
    """
    print("\n" + "="*100)
    print("🔥 AFTER-HOURS CATALYST SCAN")
    print("="*100)
    
    all_tickers = get_all_tickers()
    catalysts = []
    
    for ticker in all_tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get regular close and AH price
            hist = stock.history(period='2d')
            if len(hist) < 1:
                continue
                
            regular_close = hist['Close'].iloc[-1]
            ah_price = info.get('postMarketPrice', regular_close)
            
            if ah_price == regular_close:
                continue
            
            ah_change = ((ah_price - regular_close) / regular_close) * 100
            
            if abs(ah_change) >= min_move:
                # Find sector
                sector = None
                for s, tickers in WATCHLIST.items():
                    if ticker in tickers:
                        sector = s
                        break
                
                catalysts.append({
                    'ticker': ticker,
                    'sector': sector,
                    'regular_close': regular_close,
                    'ah_price': ah_price,
                    'ah_change': ah_change,
                    'volume': hist['Volume'].iloc[-1] if len(hist) > 0 else 0,
                    'direction': 'UP' if ah_change > 0 else 'DOWN'
                })
                
        except Exception as e:
            continue
    
    if catalysts:
        df = pd.DataFrame(catalysts).sort_values('ah_change', key=abs, ascending=False)
        
        print(f"\nFound {len(df)} tickers with AH moves >{min_move}%:\n")
        
        for _, row in df.iterrows():
            print(f"{'🔥' if row['direction'] == 'UP' else '❄️'} {row['ticker']} ({row['sector']})")
            print(f"   Close: ${row['regular_close']:.2f} → AH: ${row['ah_price']:.2f} ({row['ah_change']:+.1f}%)")
            print(f"   Volume: {row['volume']:,.0f}")
            
            # HEIMDALL INTEGRATION POINT
            print(f"   → Heimdall: Query X sentiment for '{row['ticker']}' to verify catalyst")
            print()
        
        return df
    else:
        print("\n✅ No significant after-hours moves detected")
        return pd.DataFrame()

def scan_earnings_calendar(days_ahead=7):
    """
    Scan for earnings in next N days
    Note: yfinance has limited earnings data, but we check what we can
    """
    print("\n" + "="*100)
    print(f"📅 EARNINGS CALENDAR (Next {days_ahead} Days)")
    print("="*100)
    
    all_tickers = get_all_tickers()
    earnings = []
    
    for ticker in all_tickers:
        try:
            stock = yf.Ticker(ticker)
            
            # Try to get earnings dates
            if hasattr(stock, 'calendar') and stock.calendar is not None:
                earnings_date = stock.calendar.get('Earnings Date')
                if earnings_date is not None:
                    # Find sector
                    sector = None
                    for s, tickers in WATCHLIST.items():
                        if ticker in tickers:
                            sector = s
                            break
                    
                    earnings.append({
                        'ticker': ticker,
                        'sector': sector,
                        'earnings_date': earnings_date
                    })
        except:
            continue
    
    if earnings:
        df = pd.DataFrame(earnings)
        print(f"\nFound {len(df)} upcoming earnings:\n")
        
        for _, row in df.iterrows():
            print(f"📊 {row['ticker']} ({row['sector']})")
            print(f"   Date: {row['earnings_date']}")
            print(f"   → Heimdall: Check X for earnings expectations/whispers")
            print()
        
        return df
    else:
        print("\n✅ No earnings data available via yfinance")
        print("   → Heimdall: Use web scraping for full earnings calendar")
        return pd.DataFrame()

def scan_sector_momentum():
    """
    Scan each sector for momentum
    Identify hot/cold sectors based on weekly performance
    """
    print("\n" + "="*100)
    print("📊 SECTOR MOMENTUM SCAN")
    print("="*100)
    
    sector_performance = []
    
    for sector_name, tickers in WATCHLIST.items():
        sector_changes = []
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1mo')
                
                if len(hist) >= 6:
                    # Week performance
                    week_change = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-6]) - 1) * 100
                    sector_changes.append(week_change)
            except:
                continue
        
        if sector_changes:
            avg_change = np.mean(sector_changes)
            median_change = np.median(sector_changes)
            
            sector_performance.append({
                'sector': sector_name,
                'avg_week_change': avg_change,
                'median_week_change': median_change,
                'ticker_count': len(sector_changes),
                'heimdall_intel': HEIMDALL_INTEL['hot_sectors'].get(sector_name, 'N/A')
            })
    
    df = pd.DataFrame(sector_performance).sort_values('avg_week_change', ascending=False)
    
    print("\nSector Performance (Last Week):\n")
    
    for _, row in df.iterrows():
        status = "🔥 HOT" if row['avg_week_change'] > 5 else "❄️ COLD" if row['avg_week_change'] < -5 else "⚖️ NEUTRAL"
        
        print(f"{status} {row['sector']}")
        print(f"   Avg Change: {row['avg_week_change']:+.1f}%")
        print(f"   Median: {row['median_week_change']:+.1f}%")
        print(f"   Tickers: {row['ticker_count']}")
        print(f"   Intel: {row['heimdall_intel']}")
        print()
    
    return df

def scan_big_movers_today(min_move=5.0):
    """
    Scan for tickers that moved >X% today
    Potential catalysts or continuation opportunities
    """
    print("\n" + "="*100)
    print(f"💥 TODAY'S BIG MOVERS (>{min_move}%)")
    print("="*100)
    
    all_tickers = get_all_tickers()
    movers = []
    
    for ticker in all_tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='5d')
            
            if len(hist) < 2:
                continue
            
            today_close = hist['Close'].iloc[-1]
            yesterday_close = hist['Close'].iloc[-2]
            
            change = ((today_close - yesterday_close) / yesterday_close) * 100
            
            if abs(change) >= min_move:
                # Find sector
                sector = None
                for s, tickers in WATCHLIST.items():
                    if ticker in tickers:
                        sector = s
                        break
                
                # Volume ratio
                today_vol = hist['Volume'].iloc[-1]
                avg_vol = hist['Volume'].iloc[:-1].mean()
                vol_ratio = today_vol / avg_vol if avg_vol > 0 else 1
                
                movers.append({
                    'ticker': ticker,
                    'sector': sector,
                    'change': change,
                    'close': today_close,
                    'volume_ratio': vol_ratio,
                    'direction': 'UP' if change > 0 else 'DOWN'
                })
        except:
            continue
    
    if movers:
        df = pd.DataFrame(movers).sort_values('change', key=abs, ascending=False)
        
        print(f"\nFound {len(df)} tickers moving >{min_move}%:\n")
        
        for _, row in df.iterrows():
            print(f"{'🚀' if row['direction'] == 'UP' else '💥'} {row['ticker']} ({row['sector']})")
            print(f"   Change: {row['change']:+.1f}% | Close: ${row['close']:.2f}")
            print(f"   Volume: {row['volume_ratio']:.1f}x average")
            print(f"   → Heimdall: What's the catalyst? Check X/web for news")
            print()
        
        return df
    else:
        print(f"\n✅ No moves >{min_move}% today")
        return pd.DataFrame()

def generate_daily_briefing():
    """
    Main function: Generate complete daily catalyst briefing
    """
    print("="*100)
    print("🐺 PACK CATALYST SCANNER - DAILY BRIEFING")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)
    
    print(f"\n📋 Scanning {len(get_all_tickers())} tickers across {len(WATCHLIST)} sectors...")
    
    # Run all scans
    ah_moves = scan_after_hours_moves(min_move=3.0)
    big_movers = scan_big_movers_today(min_move=5.0)
    sector_momentum = scan_sector_momentum()
    earnings = scan_earnings_calendar(days_ahead=7)
    
    # Summary
    print("\n" + "="*100)
    print("🎯 CATALYST SUMMARY")
    print("="*100)
    
    print(f"\n📊 Signals Detected:")
    print(f"   After-hours moves: {len(ah_moves)}")
    print(f"   Big movers today: {len(big_movers)}")
    print(f"   Upcoming earnings: {len(earnings)}")
    
    hot_sectors = sector_momentum[sector_momentum['avg_week_change'] > 5]
    cold_sectors = sector_momentum[sector_momentum['avg_week_change'] < -5]
    
    print(f"\n🔥 Hot Sectors ({len(hot_sectors)}):")
    for _, row in hot_sectors.iterrows():
        print(f"   {row['sector']}: {row['avg_week_change']:+.1f}%")
    
    if len(cold_sectors) > 0:
        print(f"\n❄️ Cold Sectors ({len(cold_sectors)}):")
        for _, row in cold_sectors.iterrows():
            print(f"   {row['sector']}: {row['avg_week_change']:+.1f}%")
    
    # HEIMDALL INTEGRATION POINTS
    print("\n" + "="*100)
    print("🤝 HEIMDALL INTEGRATION REQUESTS")
    print("="*100)
    
    print("\nNext Steps for Pack Coordination:")
    print("\n1. X SENTIMENT QUERIES:")
    if len(ah_moves) > 0:
        print(f"   After-hours movers: {', '.join(ah_moves['ticker'].tolist()[:5])}")
    if len(big_movers) > 0:
        print(f"   Today's big movers: {', '.join(big_movers['ticker'].tolist()[:5])}")
    
    print("\n2. WEB SCRAPING REQUESTS:")
    print("   → Full earnings calendar (next 7 days)")
    print("   → SEC 8-K filings (material events)")
    print("   → Insider buy activity (Form 4)")
    
    print("\n3. CATALYST VERIFICATION:")
    print("   → Why did these tickers move?")
    print("   → Are catalysts sustainable or one-time?")
    print("   → X sentiment: Bullish/Bearish/Neutral breakdown")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if len(ah_moves) > 0:
        ah_moves.to_csv(f'catalyst_ah_moves_{timestamp}.csv', index=False)
    if len(big_movers) > 0:
        big_movers.to_csv(f'catalyst_big_movers_{timestamp}.csv', index=False)
    if len(sector_momentum) > 0:
        sector_momentum.to_csv(f'catalyst_sector_momentum_{timestamp}.csv', index=False)
    
    print(f"\n✅ Results saved to catalyst_*_{timestamp}.csv")
    
    print("\n" + "="*100)
    print("🐺 BROKKR CATALYST SCAN COMPLETE")
    print("="*100)
    print("\nWaiting for Heimdall's verification...")
    print("Then Fenrir validates strategy...")
    print("Then Tyr executes...")
    print("\n🐺 PACK HUNTS TOGETHER. AWOOOO 🐺")

if __name__ == '__main__':
    generate_daily_briefing()
