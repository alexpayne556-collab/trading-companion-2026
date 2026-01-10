#!/usr/bin/env python3
"""
🐺 WAR ROOM MASTER - 24/7 Trading Intelligence
Runs all 7 pattern scanners and ranks opportunities
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import sys

# Our hunting ground
SECTORS = {
    'AI Chips': ['NVDA', 'AMD', 'AVGO', 'MU', 'WDC', 'STX', 'KLAC', 'LRCX'],
    'Space': ['LUNR', 'RKLB', 'RDW', 'ASTS', 'SPCE', 'MNTS'],
    'Quantum': ['IONQ', 'RGTI', 'QUBT', 'QBTS', 'ARQQ'],
    'Nuclear': ['UUUU', 'SMR', 'OKLO', 'CCJ', 'LEU', 'NNE', 'DNN', 'UEC'],
    'Rare Earth': ['USAR', 'MP', 'REE'],
    'Photonics': ['LITE', 'COHR', 'AAOI', 'LSCC'],
    'Satellite': ['ASTS', 'GSAT', 'SATS'],
    'Defense AI': ['AISP', 'PLTR', 'AVAV'],
    'Robotics': ['JOBY', 'BLDE', 'PATH'],
}

SECTOR_ETFS = {
    'Tech': 'XLK',
    'Discretionary': 'XLY', 
    'Industrials': 'XLI',
    'Materials': 'XLB',
    'Energy': 'XLE',
    'Financials': 'XLF',
    'Healthcare': 'XLV',
}


class OpportunityScorer:
    """Ranks opportunities across all patterns"""
    
    @staticmethod
    def score_opportunity(pattern, confidence, win_rate, timeframe_days):
        """
        Score = (confidence * win_rate * 100) / timeframe_days
        Higher score = better opportunity
        """
        return (confidence * win_rate * 100) / timeframe_days


def pattern_1_red_in_green():
    """RED stocks in GREEN sectors - Classic laggard play"""
    print("\n" + "="*80)
    print("PATTERN 1: RED IN GREEN (Sector Laggards)")
    print("="*80)
    
    opportunities = []
    
    for sector, tickers in SECTORS.items():
        sector_data = []
        
        for ticker_sym in tickers:
            try:
                ticker = yf.Ticker(ticker_sym)
                hist = ticker.history(period='5d')
                if len(hist) >= 2:
                    today_change = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-2]) - 1) * 100
                    week_change = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
                    price = hist['Close'].iloc[-1]
                    volume_ratio = hist['Volume'].iloc[-1] / hist['Volume'].mean() if hist['Volume'].mean() > 0 else 0
                    
                    sector_data.append({
                        'ticker': ticker_sym,
                        'today': today_change,
                        'week': week_change,
                        'price': price,
                        'volume_ratio': volume_ratio
                    })
            except:
                continue
        
        if sector_data:
            avg_today = sum([d['today'] for d in sector_data]) / len(sector_data)
            
            # Hot sector (avg +2% or more)
            if avg_today > 2:
                for data in sector_data:
                    # Red today, but sector is hot
                    if data['today'] < -1:
                        confidence = 0.7
                        score = OpportunityScorer.score_opportunity(
                            pattern=1,
                            confidence=confidence,
                            win_rate=0.70,
                            timeframe_days=3
                        )
                        
                        opportunities.append({
                            'pattern': 'RED IN GREEN',
                            'ticker': data['ticker'],
                            'sector': sector,
                            'score': score,
                            'entry': data['price'],
                            'today_change': data['today'],
                            'week_change': data['week'],
                            'reasoning': f"Sector hot +{avg_today:.1f}%, {data['ticker']} lagging {data['today']:.1f}%",
                            'timeframe': '1-3 days'
                        })
    
    return opportunities


def pattern_2_green_to_red():
    """Stocks that ran BIG will dip tomorrow"""
    print("\n" + "="*80)
    print("PATTERN 2: GREEN → RED (Buy Tomorrow's Dip)")
    print("="*80)
    
    opportunities = []
    
    for sector, tickers in SECTORS.items():
        for ticker_sym in tickers:
            try:
                ticker = yf.Ticker(ticker_sym)
                hist = ticker.history(period='5d')
                if len(hist) >= 2:
                    today_change = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-2]) - 1) * 100
                    price = hist['Close'].iloc[-1]
                    
                    # Big runner today (7%+)
                    if today_change > 7:
                        dip_target = price * 0.97  # Expect -3% dip
                        confidence = 0.65
                        score = OpportunityScorer.score_opportunity(
                            pattern=2,
                            confidence=confidence,
                            win_rate=0.65,
                            timeframe_days=1  # Next day entry
                        )
                        
                        opportunities.append({
                            'pattern': 'GREEN → RED',
                            'ticker': ticker_sym,
                            'sector': sector,
                            'score': score,
                            'entry': dip_target,
                            'today_change': today_change,
                            'reasoning': f"Ran +{today_change:.1f}% today, expect dip to ${dip_target:.2f} tomorrow",
                            'timeframe': 'Tomorrow entry, 2-5 day hold'
                        })
            except:
                continue
    
    return opportunities


def pattern_3_oversold_bounce():
    """Stocks down big this week, due for bounce"""
    print("\n" + "="*80)
    print("PATTERN 3: OVERSOLD BOUNCE (Rubber Band)")
    print("="*80)
    
    opportunities = []
    
    for sector, tickers in SECTORS.items():
        for ticker_sym in tickers:
            try:
                ticker = yf.Ticker(ticker_sym)
                hist = ticker.history(period='1mo')
                if len(hist) >= 5:
                    week_change = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-5]) - 1) * 100
                    month_change = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
                    price = hist['Close'].iloc[-1]
                    
                    # Down -10%+ this week but up for the month
                    if week_change < -10 and month_change > 0:
                        bounce_target = price * 1.05
                        confidence = 0.60
                        score = OpportunityScorer.score_opportunity(
                            pattern=3,
                            confidence=confidence,
                            win_rate=0.60,
                            timeframe_days=3
                        )
                        
                        opportunities.append({
                            'pattern': 'OVERSOLD BOUNCE',
                            'ticker': ticker_sym,
                            'sector': sector,
                            'score': score,
                            'entry': price,
                            'week_change': week_change,
                            'month_change': month_change,
                            'reasoning': f"Down {week_change:.1f}% this week, still +{month_change:.1f}% monthly",
                            'timeframe': '1-3 days'
                        })
            except:
                continue
    
    return opportunities


def pattern_7_sector_rotation():
    """Find sectors ACCELERATING while others DECELERATE"""
    print("\n" + "="*80)
    print("PATTERN 7: SECTOR ROTATION (Follow the Money)")
    print("="*80)
    
    opportunities = []
    
    rotation_data = []
    for name, ticker_sym in SECTOR_ETFS.items():
        try:
            ticker = yf.Ticker(ticker_sym)
            hist = ticker.history(period='2mo')
            if len(hist) >= 20:
                d5 = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-5]) - 1) * 100
                d10 = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-10]) - 1) * 100
                
                momentum = 'ACCEL' if d5 > d10 else 'DECEL'
                
                rotation_data.append({
                    'sector': name,
                    'ticker': ticker_sym,
                    'd5': d5,
                    'd10': d10,
                    'momentum': momentum
                })
        except:
            continue
    
    # Find accelerating sectors
    for data in rotation_data:
        if data['momentum'] == 'ACCEL' and data['d5'] > 1:
            confidence = 0.70
            score = OpportunityScorer.score_opportunity(
                pattern=7,
                confidence=confidence,
                win_rate=0.70,
                timeframe_days=7
            )
            
            opportunities.append({
                'pattern': 'SECTOR ROTATION',
                'ticker': data['ticker'],
                'sector': data['sector'],
                'score': score,
                'entry': 'ETF or top stocks',
                'd5_change': data['d5'],
                'd10_change': data['d10'],
                'reasoning': f"{data['sector']} accelerating: 5d +{data['d5']:.1f}%, 10d +{data['d10']:.1f}%",
                'timeframe': '1-2 weeks'
            })
    
    return opportunities


def display_opportunities(opportunities):
    """Display all opportunities ranked by score"""
    if not opportunities:
        print("\n❌ No opportunities found at this time")
        return
    
    print("\n" + "="*80)
    print("🎯 RANKED OPPORTUNITIES (Best to Worst)")
    print("="*80)
    
    sorted_opps = sorted(opportunities, key=lambda x: x['score'], reverse=True)
    
    for i, opp in enumerate(sorted_opps[:15], 1):  # Top 15
        print(f"\n#{i} | Score: {opp['score']:.1f} | {opp['pattern']}")
        print(f"   🎯 {opp['ticker']} ({opp['sector']})")
        print(f"   📊 Entry: ${opp['entry']:.2f}" if isinstance(opp['entry'], float) else f"   📊 Entry: {opp['entry']}")
        print(f"   💡 {opp['reasoning']}")
        print(f"   ⏰ Timeframe: {opp['timeframe']}")


def main():
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "🐺 WAR ROOM MASTER 🐺" + " "*36 + "║")
    print("║" + " "*23 + "24/7 Trading Intelligence" + " "*30 + "║")
    print("╚" + "="*78 + "╝")
    print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_opportunities = []
    
    # Run all pattern scanners
    print("\n🔍 Scanning Pattern 1: Red in Green...")
    all_opportunities.extend(pattern_1_red_in_green())
    
    print("\n🔍 Scanning Pattern 2: Green → Red...")
    all_opportunities.extend(pattern_2_green_to_red())
    
    print("\n🔍 Scanning Pattern 3: Oversold Bounces...")
    all_opportunities.extend(pattern_3_oversold_bounce())
    
    print("\n🔍 Scanning Pattern 7: Sector Rotation...")
    all_opportunities.extend(pattern_7_sector_rotation())
    
    # Display ranked results
    display_opportunities(all_opportunities)
    
    print("\n" + "="*80)
    print("🐺 AWOOOO! Hunt with intelligence.")
    print("="*80)


if __name__ == "__main__":
    main()
