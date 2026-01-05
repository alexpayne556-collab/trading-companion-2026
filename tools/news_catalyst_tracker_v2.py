#!/usr/bin/env python3
"""
🐺 WOLF PACK ARSENAL - NEWS CATALYST TRACKER V2
================================================
Track news and catalysts across the AI Fuel Chain
"Information is the wolf's greatest weapon"

IMPROVED:
- Sector-level news aggregation
- Contract/Government catalyst detection
- News momentum tracking
- AI Fuel Chain specific keywords
- Better catalyst scoring

AWOOOO 🐺 LLHR
"""

import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# COLORS
# =============================================================================
class Colors:
    BRIGHT_GREEN = '\033[92m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BRIGHT_RED = '\033[31m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# =============================================================================
# AI FUEL CHAIN SECTORS + TICKERS
# =============================================================================

AI_FUEL_CHAIN = {
    'NUCLEAR': ['UUUU', 'SMR', 'LEU', 'OKLO', 'CCJ', 'DNN', 'UEC', 'NXE', 'NNE'],
    'UTILITIES': ['NEE', 'VST', 'CEG', 'WMB'],
    'COOLING': ['VRT', 'MOD', 'NVT'],
    'PHOTONICS': ['LITE', 'AAOI', 'COHR', 'GFS'],
    'NETWORKING': ['ANET', 'CRDO', 'FN', 'CIEN'],
    'STORAGE': ['MU', 'WDC', 'STX'],
    'CHIPS': ['AMD', 'MRVL', 'AVGO', 'INTC', 'AMKR'],
    'DC_BUILDERS': ['SMCI', 'EME', 'CLS', 'FIX'],
    'DC_REITS': ['EQIX', 'DLR'],
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'ASTS', 'SIDU', 'BKSY', 'PL'],
    'AI_SOFTWARE': ['PLTR', 'AI', 'SOUN', 'PATH', 'UPST']
}

PRIORITY_TICKERS = ['UUUU', 'SIDU', 'LUNR', 'MU', 'LITE', 'VRT', 'SMR', 'LEU', 'RDW', 'OKLO']

# =============================================================================
# CATALYST KEYWORDS - AI FUEL CHAIN SPECIFIC
# =============================================================================

# High-value catalysts (worth 3 points each)
TIER_1_CATALYSTS = [
    "DOE contract", "DOD contract", "NASA contract", "government contract",
    "hyperscaler", "Microsoft", "Google", "Amazon", "Meta", "NVIDIA contract",
    "data center order", "nuclear contract", "acquisition", "merger",
    "breakthrough", "FDA approval", "first commercial"
]

# Medium catalysts (worth 2 points)
TIER_2_CATALYSTS = [
    "contract awarded", "partnership", "deal signed", "agreement",
    "expansion", "new facility", "capacity increase", "record order",
    "price target raised", "upgrade", "buy rating", "insider buying",
    "revenue beat", "earnings beat", "guidance raised"
]

# Standard bullish (worth 1 point)
TIER_3_BULLISH = [
    "growth", "increase", "positive", "exceeds", "strong demand",
    "new customer", "patent", "license", "dividend", "buyback"
]

# Bearish signals (negative points)
BEARISH_CATALYSTS = [
    "downgrade", "sell rating", "price target cut", "miss", "decline",
    "loss", "lawsuit", "investigation", "recall", "offering", "dilution",
    "layoff", "restructuring", "warning", "guidance cut", "debt concern"
]

# AI Infrastructure Keywords
AI_INFRASTRUCTURE = {
    'NUCLEAR': ["uranium", "nuclear power", "SMR", "small modular reactor", "NRC", "nuclear fuel", "enrichment"],
    'POWER': ["data center power", "power grid", "electricity", "gigawatt", "energy supply"],
    'COOLING': ["liquid cooling", "immersion cooling", "thermal management", "rack density", "heat dissipation"],
    'PHOTONICS': ["silicon photonics", "optical interconnect", "800G", "1.6T", "transceiver", "copper wall"],
    'NETWORKING': ["InfiniBand", "Ethernet fabric", "AI cluster", "network fabric", "data center switching"],
    'STORAGE': ["HBM", "high bandwidth memory", "HBM3", "HBM4", "AI memory", "GPU memory"],
    'CHIPS': ["AI chip", "GPU", "AI accelerator", "custom silicon", "inference chip", "training chip"],
    'DATACENTER': ["hyperscale", "colocation", "AI infrastructure", "compute capacity", "GPU cluster"],
    'QUANTUM': ["quantum computing", "qubit", "quantum advantage", "quantum supremacy", "quantum error correction"],
    'SPACE': ["satellite", "lunar", "space infrastructure", "launch contract", "defense contract"]
}

# =============================================================================
# NEWS SCORING ENGINE
# =============================================================================

def score_news_item(title, description=""):
    """Score a news item based on catalyst keywords"""
    text = (title + " " + description).lower()
    
    score = 0
    catalysts = []
    
    # Tier 1 catalysts (3 points each)
    for kw in TIER_1_CATALYSTS:
        if kw.lower() in text:
            score += 3
            catalysts.append(f"⭐⭐⭐ {kw}")
    
    # Tier 2 catalysts (2 points each)
    for kw in TIER_2_CATALYSTS:
        if kw.lower() in text:
            score += 2
            catalysts.append(f"⭐⭐ {kw}")
    
    # Tier 3 bullish (1 point)
    for kw in TIER_3_BULLISH:
        if kw.lower() in text:
            score += 1
            catalysts.append(f"⭐ {kw}")
    
    # Bearish (subtract points)
    for kw in BEARISH_CATALYSTS:
        if kw.lower() in text:
            score -= 2
            catalysts.append(f"🔴 {kw}")
    
    # AI Infrastructure relevance
    ai_themes = []
    for theme, keywords in AI_INFRASTRUCTURE.items():
        for kw in keywords:
            if kw.lower() in text:
                ai_themes.append(theme)
                break
    
    return score, list(set(catalysts))[:5], list(set(ai_themes))

def classify_sentiment(score):
    """Classify sentiment based on score"""
    if score >= 5:
        return "🔥 MONSTER CATALYST"
    elif score >= 3:
        return "🚀 STRONG BULLISH"
    elif score >= 1:
        return "📈 BULLISH"
    elif score == 0:
        return "➖ NEUTRAL"
    elif score >= -2:
        return "⚠️ BEARISH"
    else:
        return "🔴 VERY BEARISH"

# =============================================================================
# NEWS FETCHING
# =============================================================================

def get_ticker_news(ticker, max_items=10):
    """Get news for a specific ticker"""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        if not news:
            return []
        
        results = []
        for item in news[:max_items]:
            title = item.get('title', '')
            
            # Score the news
            score, catalysts, ai_themes = score_news_item(title)
            
            results.append({
                "ticker": ticker,
                "title": title,
                "publisher": item.get('publisher', 'Unknown'),
                "link": item.get('link', ''),
                "published": datetime.fromtimestamp(item.get('providerPublishTime', 0)),
                "score": score,
                "catalysts": catalysts,
                "ai_themes": ai_themes,
                "sentiment": classify_sentiment(score)
            })
        
        return results
        
    except Exception as e:
        return []

def get_sector_for_ticker(ticker):
    """Get sector for a ticker"""
    for sector, tickers in AI_FUEL_CHAIN.items():
        if ticker in tickers:
            return sector
    return "UNKNOWN"

def scan_all_news(hours_back=24):
    """Scan news for entire AI Fuel Chain"""
    
    cutoff = datetime.now() - timedelta(hours=hours_back)
    
    print("\n" + "="*100)
    print(f"{Colors.CYAN}{Colors.BOLD}🐺 WOLF PACK NEWS CATALYST TRACKER V2 🐺{Colors.END}")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print(f"   Scanning AI Fuel Chain news from last {hours_back} hours")
    print(f"   Universe: 56 tickers across 12 sectors")
    print("="*100)
    
    all_news = []
    ticker_count = {}
    
    all_tickers = []
    for tickers in AI_FUEL_CHAIN.values():
        all_tickers.extend(tickers)
    
    print(f"\n   Scanning {len(all_tickers)} tickers", end="", flush=True)
    for i, ticker in enumerate(all_tickers):
        if i % 10 == 0:
            print(".", end="", flush=True)
        
        news = get_ticker_news(ticker, max_items=5)
        
        # Filter by time
        recent_news = [n for n in news if n['published'] >= cutoff]
        
        for n in recent_news:
            n['sector'] = get_sector_for_ticker(ticker)
        
        all_news.extend(recent_news)
        
        # Track news volume per ticker
        if recent_news:
            ticker_count[ticker] = len(recent_news)
    
    print(" ✓ Done!")
    
    # Sort by score
    all_news.sort(key=lambda x: (x['score'], x['published']), reverse=True)
    
    return all_news, ticker_count

# =============================================================================
# DISPLAY FUNCTIONS
# =============================================================================

def display_top_catalysts(all_news, n=10):
    """Display top catalysts"""
    print(f"\n{Colors.BRIGHT_GREEN}{'='*100}")
    print(f"🔥 TOP {n} CATALYSTS BY SCORE")
    print(f"{'='*100}{Colors.END}")
    
    top = [n for n in all_news if n['score'] > 0][:n]
    
    if not top:
        print("   No significant catalysts found")
        return
    
    for i, n in enumerate(top, 1):
        priority = "⭐" if n['ticker'] in PRIORITY_TICKERS else ""
        time_str = n['published'].strftime('%m/%d %H:%M')
        
        print(f"\n{i}. {n['ticker']:<6}{priority} [{n['sector']}] — Score: {n['score']} — {n['sentiment']}")
        print(f"   {Colors.BRIGHT_GREEN}{n['title'][:85]}{Colors.END}")
        print(f"   {time_str} | {n['publisher']}")
        
        if n['catalysts']:
            print(f"   Catalysts: {', '.join(n['catalysts'][:3])}")
        
        if n['ai_themes']:
            print(f"   Themes: {', '.join(n['ai_themes'])}")

def display_sector_summary(all_news):
    """Display sector-level news summary"""
    print(f"\n{Colors.CYAN}{'='*100}")
    print(f"📊 SECTOR NEWS SUMMARY")
    print(f"{'='*100}{Colors.END}")
    
    sector_stats = {}
    
    for n in all_news:
        sector = n['sector']
        if sector not in sector_stats:
            sector_stats[sector] = {
                'count': 0,
                'total_score': 0,
                'bullish': 0,
                'bearish': 0,
                'monster': 0
            }
        
        sector_stats[sector]['count'] += 1
        sector_stats[sector]['total_score'] += n['score']
        
        if n['score'] >= 5:
            sector_stats[sector]['monster'] += 1
        elif n['score'] >= 1:
            sector_stats[sector]['bullish'] += 1
        elif n['score'] < 0:
            sector_stats[sector]['bearish'] += 1
    
    # Sort by total score
    sorted_sectors = sorted(sector_stats.items(), key=lambda x: x[1]['total_score'], reverse=True)
    
    print(f"\n   {'SECTOR':<15} | {'NEWS':>6} | {'SCORE':>7} | {'🔥':>4} | {'📈':>4} | {'⚠️':>4}")
    print(f"   {'─'*15}─┼─{'─'*6}─┼─{'─'*7}─┼─{'─'*4}─┼─{'─'*4}─┼─{'─'*4}")
    
    for sector, stats in sorted_sectors:
        heat = "🔥" if stats['total_score'] >= 10 else "📈" if stats['total_score'] >= 5 else "➖"
        print(f"   {sector:<15} | {stats['count']:>6} | {stats['total_score']:>+7} | {stats['monster']:>4} | {stats['bullish']:>4} | {stats['bearish']:>4} {heat}")

def display_news_momentum(ticker_count):
    """Display tickers with most news coverage"""
    print(f"\n{Colors.MAGENTA}{'='*100}")
    print(f"📰 NEWS MOMENTUM - Most Coverage")
    print(f"{'='*100}{Colors.END}")
    
    if not ticker_count:
        print("   No news momentum detected")
        return
    
    sorted_tickers = sorted(ticker_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print(f"\n   {'TICKER':<8} | {'SECTOR':<15} | {'NEWS COUNT':>12} | {'⭐':<3}")
    print(f"   {'─'*8}─┼─{'─'*15}─┼─{'─'*12}─┼─{'─'*3}")
    
    for ticker, count in sorted_tickers:
        sector = get_sector_for_ticker(ticker)
        priority = "⭐" if ticker in PRIORITY_TICKERS else ""
        heat = "🔥🔥" if count >= 5 else "🔥" if count >= 3 else ""
        print(f"   {ticker:<8} | {sector:<15} | {count:>12} {heat} | {priority}")

def display_priority_watch(all_news):
    """Display news for priority tickers"""
    print(f"\n{Colors.YELLOW}{'='*100}")
    print(f"⭐ PRIORITY TICKER WATCH")
    print(f"{'='*100}{Colors.END}")
    
    for ticker in PRIORITY_TICKERS:
        ticker_news = [n for n in all_news if n['ticker'] == ticker]
        
        if ticker_news:
            sector = get_sector_for_ticker(ticker)
            print(f"\n   {Colors.BOLD}{ticker}{Colors.END} [{sector}]:")
            
            for n in ticker_news[:3]:
                time_str = n['published'].strftime('%m/%d %H:%M')
                score_color = Colors.GREEN if n['score'] >= 1 else Colors.RED if n['score'] < 0 else Colors.WHITE
                
                print(f"      {score_color}[{n['score']:+2}] {n['sentiment']}{Colors.END}")
                print(f"      {n['title'][:75]}")
                print(f"      {time_str}")
        else:
            print(f"\n   {ticker}: No recent news")

def display_contract_news(all_news):
    """Display contract/government news"""
    print(f"\n{Colors.BRIGHT_GREEN}{'='*100}")
    print(f"💰 CONTRACT & GOVERNMENT NEWS")
    print(f"{'='*100}{Colors.END}")
    
    contract_keywords = ["contract", "awarded", "DOE", "DOD", "NASA", "government", "hyperscaler"]
    
    contract_news = []
    for n in all_news:
        if any(kw.lower() in n['title'].lower() for kw in contract_keywords):
            contract_news.append(n)
    
    if contract_news:
        for n in contract_news[:10]:
            priority = "⭐" if n['ticker'] in PRIORITY_TICKERS else ""
            time_str = n['published'].strftime('%m/%d %H:%M')
            
            print(f"\n   {n['ticker']:<6}{priority} [{n['sector']}] — {n['sentiment']}")
            print(f"   {Colors.BRIGHT_GREEN}{n['title'][:85]}{Colors.END}")
            print(f"   {time_str}")
    else:
        print("   No contract news found")

def display_warnings(all_news):
    """Display bearish warnings"""
    print(f"\n{Colors.RED}{'='*100}")
    print(f"⚠️  BEARISH WARNINGS")
    print(f"{'='*100}{Colors.END}")
    
    warnings = [n for n in all_news if n['score'] < 0]
    
    if warnings:
        for n in warnings[:10]:
            priority = "⭐" if n['ticker'] in PRIORITY_TICKERS else ""
            time_str = n['published'].strftime('%m/%d %H:%M')
            
            print(f"\n   {n['ticker']:<6}{priority} [{n['sector']}]")
            print(f"   {Colors.RED}{n['title'][:85]}{Colors.END}")
            print(f"   {time_str}")
    else:
        print(f"   {Colors.GREEN}✓ No bearish news detected{Colors.END}")

# =============================================================================
# EARNINGS CALENDAR
# =============================================================================

def get_earnings_calendar():
    """Get upcoming earnings"""
    print(f"\n{Colors.YELLOW}{'='*100}")
    print(f"📅 UPCOMING EARNINGS CALENDAR")
    print(f"{'='*100}{Colors.END}")
    
    upcoming = []
    
    all_tickers = []
    for tickers in AI_FUEL_CHAIN.values():
        all_tickers.extend(tickers)
    
    print(f"\n   Checking earnings dates", end="", flush=True)
    
    for i, ticker in enumerate(all_tickers):
        if i % 15 == 0:
            print(".", end="", flush=True)
        
        try:
            stock = yf.Ticker(ticker)
            calendar = stock.calendar
            
            if calendar is not None and not calendar.empty:
                if 'Earnings Date' in calendar.index:
                    earnings_date = calendar.loc['Earnings Date'].iloc[0]
                    
                    if pd.notna(earnings_date):
                        if isinstance(earnings_date, str):
                            earnings_dt = datetime.strptime(earnings_date[:10], '%Y-%m-%d')
                        else:
                            earnings_dt = earnings_date
                        
                        if earnings_dt >= datetime.now():
                            upcoming.append({
                                "ticker": ticker,
                                "sector": get_sector_for_ticker(ticker),
                                "date": earnings_dt,
                                "days_away": (earnings_dt - datetime.now()).days
                            })
        except:
            pass
    
    print(" ✓")
    
    # Sort by date
    upcoming.sort(key=lambda x: x['date'])
    
    if upcoming:
        print(f"\n   {'TICKER':<8} | {'SECTOR':<15} | {'DATE':<12} | {'DAYS':>6} | {'⭐':<3} | {'ALERT'}")
        print(f"   {'─'*8}─┼─{'─'*15}─┼─{'─'*12}─┼─{'─'*6}─┼─{'─'*3}─┼─{'─'*10}")
        
        for e in upcoming[:20]:
            priority = "⭐" if e['ticker'] in PRIORITY_TICKERS else ""
            date_str = e['date'].strftime('%Y-%m-%d')
            
            if e['days_away'] <= 3:
                alert = "🔴 THIS WEEK!"
            elif e['days_away'] <= 7:
                alert = "⚠️ NEXT WEEK"
            else:
                alert = ""
            
            print(f"   {e['ticker']:<8} | {e['sector']:<15} | {date_str:<12} | {e['days_away']:>6} | {priority:<3} | {alert}")
    else:
        print("   No upcoming earnings found")

# =============================================================================
# MAIN
# =============================================================================

def main():
    import sys
    import pandas as pd
    
    # Parse args
    hours_back = 24
    mode = "full"
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "earnings":
            mode = "earnings"
        elif sys.argv[1] == "priority":
            mode = "priority"
            hours_back = 48
        elif sys.argv[1].isdigit():
            hours_back = int(sys.argv[1])
    
    # Scan news
    all_news, ticker_count = scan_all_news(hours_back)
    
    # Display results
    display_top_catalysts(all_news, n=15)
    display_contract_news(all_news)
    display_sector_summary(all_news)
    display_news_momentum(ticker_count)
    display_priority_watch(all_news)
    display_warnings(all_news)
    
    # Earnings calendar
    print("\n")
    get_earnings_calendar()
    
    # Footer
    print(f"\n{'='*100}")
    print(f"{Colors.CYAN}{Colors.BOLD}🐺 AWOOOO! INFORMATION IS THE WOLF'S GREATEST WEAPON! LLHR! 🐺{Colors.END}")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    main()
