#!/usr/bin/env python3
"""
🐺 WOLF DEN COMMAND CENTER 🐺

THE CORE SYSTEM - Everything in one place.

Based on Fenrir's doctrine:
- WOUNDED WOLF: Track distance from 10-day high
- SECTOR HEAT: Which sectors are HOT right now
- MOMENTUM IGNITION: Volume spike detection
- DECISION MATRIX: Combine signals into BUY/WAIT/SKIP

This is the ONE screen you check every morning.

Author: Brokkr (following Fenrir's blueprint)
Date: January 3, 2026
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class WolfDenCommand:
    """
    The Command Center - all signals in one view
    """
    
    # ═══════════════════════════════════════════════════════════════════
    # TIER SYSTEM (from Fenrir's doctrine)
    # ═══════════════════════════════════════════════════════════════════
    
    TIER_1_MONSTERS = {
        # 5+ moves in 30 days - CORE POSITIONS
        'SIDU': {'sector': 'Space/Bio', 'moves': 9, 'notes': 'The undisputed king'},
        'RCAT': {'sector': 'Defense', 'moves': 5, 'notes': 'Consistent 10-15% pops'},
        'LUNR': {'sector': 'Space', 'moves': 5, 'notes': 'IM-3 catalyst Feb'},
        'ASTS': {'sector': 'Space', 'moves': 4, 'notes': 'Satellite constellation'},
        'RDW': {'sector': 'Space', 'moves': 4, 'notes': 'Defense/space crossover'},
        'CLSK': {'sector': 'Crypto', 'moves': 4, 'notes': 'Bitcoin proxy'},
    }
    
    TIER_2_SYMPATHY = {
        # 3-4 moves - Move WITH sector
        'IONQ': {'sector': 'Quantum', 'moves': 3, 'notes': 'Leads quantum moves'},
        'RGTI': {'sector': 'Quantum', 'moves': 3, 'notes': 'Follows IONQ usually'},
        'QBTS': {'sector': 'Quantum', 'moves': 4, 'notes': 'Higher beta'},
        'QUBT': {'sector': 'Quantum', 'moves': 3, 'notes': 'Smallest, wildest'},
        'RKLB': {'sector': 'Space', 'moves': 4, 'notes': 'Space sympathy'},
        'BKSY': {'sector': 'Space', 'moves': 3, 'notes': 'Usually lags space'},
        'SMR': {'sector': 'Nuclear', 'moves': 2, 'notes': 'Policy-driven'},
        'NNE': {'sector': 'Nuclear', 'moves': 2, 'notes': 'Nuclear sympathy'},
        'OKLO': {'sector': 'Nuclear', 'moves': 2, 'notes': 'AI datacenter angle'},
        'LEU': {'sector': 'Nuclear', 'moves': 2, 'notes': 'Uranium supply'},
    }
    
    TIER_3_CATALYST = {
        # 1-2 moves - Need specific news
        'AISP': {'sector': 'Defense', 'moves': 1, 'notes': 'Your current position'},
        'MARA': {'sector': 'Crypto', 'moves': 2, 'notes': 'Bitcoin miner'},
        'RIOT': {'sector': 'Crypto', 'moves': 2, 'notes': 'Bitcoin miner'},
        'AFRM': {'sector': 'Fintech', 'moves': 2, 'notes': 'BNPL leader'},
        'RIVN': {'sector': 'EV', 'moves': 3, 'notes': 'EV production ramp'},
        'LCID': {'sector': 'EV', 'moves': 2, 'notes': 'Luxury EV'},
        'SPCE': {'sector': 'Space', 'moves': 2, 'notes': 'Needs catalyst'},
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # SECTOR CLUSTERS (for sympathy plays)
    # ═══════════════════════════════════════════════════════════════════
    
    SECTORS = {
        'Space': ['LUNR', 'RKLB', 'ASTS', 'RDW', 'BKSY', 'SPCE', 'SIDU'],
        'Quantum': ['IONQ', 'RGTI', 'QBTS', 'QUBT'],
        'Nuclear': ['SMR', 'NNE', 'OKLO', 'LEU', 'CCJ'],
        'Defense': ['RCAT', 'AISP', 'PLTR', 'RTX'],
        'Crypto': ['CLSK', 'MARA', 'RIOT', 'COIN'],
        'EV': ['RIVN', 'LCID', 'TSLA', 'NIO'],
    }
    
    # Sector ETFs for heat check
    SECTOR_ETFS = {
        'Space': 'ARKX',
        'Defense': 'ITA', 
        'Semis': 'SMH',
        'Nuclear': 'NLR',
        'Crypto': 'BITO',
        'EV': 'DRIV',
    }
    
    def __init__(self):
        self.all_tickers = {
            **self.TIER_1_MONSTERS,
            **self.TIER_2_SYMPATHY,
            **self.TIER_3_CATALYST
        }
        self.data_dir = Path('logs/wolf_den')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    # ═══════════════════════════════════════════════════════════════════
    # WOUNDED WOLF SCAN
    # ═══════════════════════════════════════════════════════════════════
    
    def wounded_wolf_scan(self) -> Dict:
        """
        Calculate distance from 10-day high for all tickers
        
        Categories:
        - WOUNDED: Down 5-15% from high (BUY ZONE)
        - BLEEDING: Down >15% (CAUTION)
        - NEUTRAL: Within 5% of high
        - EXTENDED: At/near highs (DON'T CHASE)
        """
        results = {
            'wounded': [],      # -5% to -15% = BUY ZONE
            'bleeding': [],     # Below -15% = CAUTION
            'neutral': [],      # -5% to 0%
            'extended': [],     # At highs
        }
        
        for ticker, info in self.all_tickers.items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1mo')
                
                if len(hist) < 10:
                    continue
                
                current = hist['Close'].iloc[-1]
                high_10d = hist['High'].tail(10).max()
                low_10d = hist['Low'].tail(10).min()
                
                # Distance from 10-day high (negative = below high)
                dist_from_high = ((current - high_10d) / high_10d) * 100
                
                # Volume analysis
                avg_vol = hist['Volume'].tail(20).mean()
                today_vol = hist['Volume'].iloc[-1]
                vol_ratio = today_vol / avg_vol if avg_vol > 0 else 1
                
                tier = self._get_tier(ticker)
                
                data = {
                    'ticker': ticker,
                    'tier': tier,
                    'sector': info['sector'],
                    'notes': info['notes'],
                    'price': round(current, 2),
                    'high_10d': round(high_10d, 2),
                    'dist_from_high': round(dist_from_high, 1),
                    'vol_ratio': round(vol_ratio, 2),
                }
                
                # Categorize
                if dist_from_high <= -15:
                    results['bleeding'].append(data)
                elif dist_from_high <= -5:
                    results['wounded'].append(data)
                elif dist_from_high >= -2:
                    results['extended'].append(data)
                else:
                    results['neutral'].append(data)
                    
            except Exception as e:
                continue
        
        # Sort each category by tier
        for cat in results:
            results[cat].sort(key=lambda x: x['tier'])
        
        return results
    
    # ═══════════════════════════════════════════════════════════════════
    # SECTOR HEAT CHECK
    # ═══════════════════════════════════════════════════════════════════
    
    def sector_heat_check(self) -> Dict:
        """
        Check which sectors are HOT today
        Uses both ETFs and individual stock performance
        """
        sector_heat = {}
        
        # Check ETFs
        for sector, etf in self.SECTOR_ETFS.items():
            try:
                stock = yf.Ticker(etf)
                hist = stock.history(period='5d')
                
                if len(hist) >= 2:
                    today_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                    week_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                    
                    sector_heat[sector] = {
                        'etf': etf,
                        'today': round(today_change, 2),
                        'week': round(week_change, 2),
                        'stocks': [],
                        'hot_stocks': 0,
                    }
            except:
                continue
        
        # Check individual stocks by sector
        for sector, tickers in self.SECTORS.items():
            if sector not in sector_heat:
                sector_heat[sector] = {
                    'etf': 'N/A',
                    'today': 0,
                    'week': 0,
                    'stocks': [],
                    'hot_stocks': 0,
                }
            
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period='5d')
                    
                    if len(hist) >= 2:
                        today_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                        
                        sector_heat[sector]['stocks'].append({
                            'ticker': ticker,
                            'change': round(today_change, 2)
                        })
                        
                        if today_change >= 3:  # Stock is hot if up 3%+
                            sector_heat[sector]['hot_stocks'] += 1
                except:
                    continue
            
            # Sort stocks by performance
            sector_heat[sector]['stocks'].sort(key=lambda x: x['change'], reverse=True)
        
        return sector_heat
    
    # ═══════════════════════════════════════════════════════════════════
    # MOMENTUM IGNITION SCAN
    # ═══════════════════════════════════════════════════════════════════
    
    def momentum_ignition_scan(self) -> List[Dict]:
        """
        Find stocks with unusual volume (2x+ average)
        These are potential momentum ignition plays
        """
        ignitions = []
        
        for ticker, info in self.all_tickers.items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1mo')
                
                if len(hist) < 5:
                    continue
                
                current = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                today_change = ((current - prev_close) / prev_close) * 100
                
                avg_vol = hist['Volume'].tail(20).mean()
                today_vol = hist['Volume'].iloc[-1]
                vol_ratio = today_vol / avg_vol if avg_vol > 0 else 1
                
                if vol_ratio >= 1.5:  # 1.5x+ volume = something happening
                    ignitions.append({
                        'ticker': ticker,
                        'tier': self._get_tier(ticker),
                        'sector': info['sector'],
                        'price': round(current, 2),
                        'change': round(today_change, 2),
                        'vol_ratio': round(vol_ratio, 2),
                        'signal_strength': 'STRONG' if vol_ratio >= 2.0 else 'MODERATE'
                    })
            except:
                continue
        
        # Sort by volume ratio
        ignitions.sort(key=lambda x: x['vol_ratio'], reverse=True)
        return ignitions
    
    # ═══════════════════════════════════════════════════════════════════
    # SECTOR LAGGARD FINDER
    # ═══════════════════════════════════════════════════════════════════
    
    def find_sector_laggards(self, sector_heat: Dict) -> List[Dict]:
        """
        When a sector is hot, find the laggards that haven't moved yet
        These are sympathy play opportunities
        """
        laggards = []
        
        for sector, data in sector_heat.items():
            # Sector is "hot" if ETF up 2%+ or 2+ stocks up 3%+
            is_hot = data['today'] >= 2 or data['hot_stocks'] >= 2
            
            if is_hot and data['stocks']:
                # Find stocks that are lagging (up less than sector average)
                avg_change = sum(s['change'] for s in data['stocks']) / len(data['stocks'])
                
                for stock in data['stocks']:
                    if stock['change'] < avg_change - 1:  # Lagging by 1%+
                        ticker_info = self.all_tickers.get(stock['ticker'], {})
                        laggards.append({
                            'ticker': stock['ticker'],
                            'sector': sector,
                            'sector_heat': round(data['today'], 2),
                            'stock_change': stock['change'],
                            'sector_avg': round(avg_change, 2),
                            'lag': round(avg_change - stock['change'], 2),
                            'tier': self._get_tier(stock['ticker']),
                            'notes': ticker_info.get('notes', '')
                        })
        
        # Sort by lag amount
        laggards.sort(key=lambda x: x['lag'], reverse=True)
        return laggards
    
    # ═══════════════════════════════════════════════════════════════════
    # DECISION MATRIX
    # ═══════════════════════════════════════════════════════════════════
    
    def decision_matrix(self, wounded: Dict, sector_heat: Dict, ignitions: List) -> List[Dict]:
        """
        THE DECISION ENGINE
        
        Combine all signals into actionable decisions:
        - Wounded + Hot Sector + Volume = STRONG BUY
        - Wounded + Hot Sector = BUY (wait for volume)
        - Wounded + Volume = CONSIDER
        - Hot Sector + Volume = MOMENTUM (can chase small)
        - None = SKIP
        """
        decisions = []
        
        # Get hot sectors
        hot_sectors = [s for s, d in sector_heat.items() if d['today'] >= 2 or d['hot_stocks'] >= 2]
        
        # Get volume spike tickers
        vol_tickers = {i['ticker']: i['vol_ratio'] for i in ignitions}
        
        # Analyze wounded stocks
        for stock in wounded['wounded']:
            ticker = stock['ticker']
            stock_sector = stock['sector'].split('/')[0]  # Handle 'Space/Bio' -> 'Space'
            
            is_hot_sector = any(hs.lower() in stock_sector.lower() for hs in hot_sectors)
            has_volume = ticker in vol_tickers
            vol_ratio = vol_tickers.get(ticker, 1.0)
            
            # Score the setup
            score = 0
            signals = []
            
            if stock['tier'] == 1:
                score += 2
                signals.append("TIER 1 RUNNER")
            elif stock['tier'] == 2:
                score += 1
                signals.append("TIER 2")
            
            if is_hot_sector:
                score += 2
                signals.append(f"HOT SECTOR ({stock_sector})")
            
            if has_volume:
                score += 2 if vol_ratio >= 2.0 else 1
                signals.append(f"VOLUME {vol_ratio}x")
            
            # Wounded is already true (that's why it's in this list)
            score += 1
            signals.append(f"WOUNDED ({stock['dist_from_high']}%)")
            
            # Decision
            if score >= 5:
                action = "🔥 STRONG BUY"
            elif score >= 4:
                action = "✅ BUY"
            elif score >= 3:
                action = "👀 CONSIDER"
            else:
                action = "⏳ WATCH"
            
            decisions.append({
                'ticker': ticker,
                'action': action,
                'score': score,
                'signals': signals,
                'price': stock['price'],
                'tier': stock['tier'],
                'sector': stock['sector'],
            })
        
        # Also check momentum ignition stocks that aren't wounded
        wounded_tickers = [s['ticker'] for s in wounded['wounded']]
        
        for ign in ignitions:
            if ign['ticker'] not in wounded_tickers:
                stock_sector = ign['sector'].split('/')[0]
                is_hot_sector = any(hs.lower() in stock_sector.lower() for hs in hot_sectors)
                
                score = 0
                signals = []
                
                if ign['tier'] == 1:
                    score += 2
                    signals.append("TIER 1 RUNNER")
                elif ign['tier'] == 2:
                    score += 1
                    signals.append("TIER 2")
                
                if is_hot_sector:
                    score += 2
                    signals.append(f"HOT SECTOR ({stock_sector})")
                
                score += 2 if ign['vol_ratio'] >= 2.0 else 1
                signals.append(f"VOLUME {ign['vol_ratio']}x")
                
                if score >= 4:
                    action = "🚀 MOMENTUM"
                else:
                    action = "👀 WATCH"
                
                decisions.append({
                    'ticker': ign['ticker'],
                    'action': action,
                    'score': score,
                    'signals': signals,
                    'price': ign['price'],
                    'tier': ign['tier'],
                    'sector': ign['sector'],
                })
        
        # Sort by score
        decisions.sort(key=lambda x: x['score'], reverse=True)
        return decisions
    
    # ═══════════════════════════════════════════════════════════════════
    # MAIN COMMAND CENTER
    # ═══════════════════════════════════════════════════════════════════
    
    def run_full_scan(self):
        """
        THE MORNING RITUAL
        
        Run this every morning at 6 AM to know your game plan
        """
        print("\n" + "🐺" * 40)
        print("       W O L F   D E N   C O M M A N D   C E N T E R")
        print("       " + datetime.now().strftime('%A, %B %d, %Y - %I:%M %p'))
        print("🐺" * 40)
        
        # 1. WOUNDED WOLF SCAN
        print("\n\n" + "═" * 80)
        print("📍 PHASE 1: WOUNDED WOLF SCAN")
        print("   Finding repeat runners in the BUY ZONE")
        print("═" * 80)
        
        wounded = self.wounded_wolf_scan()
        self._print_wounded_results(wounded)
        
        # 2. SECTOR HEAT CHECK
        print("\n\n" + "═" * 80)
        print("🔥 PHASE 2: SECTOR HEAT CHECK")
        print("   Which sectors are HOT today?")
        print("═" * 80)
        
        sector_heat = self.sector_heat_check()
        self._print_sector_heat(sector_heat)
        
        # 3. MOMENTUM IGNITION
        print("\n\n" + "═" * 80)
        print("🚀 PHASE 3: MOMENTUM IGNITION SCAN")
        print("   Unusual volume = something happening")
        print("═" * 80)
        
        ignitions = self.momentum_ignition_scan()
        self._print_ignitions(ignitions)
        
        # 4. SECTOR LAGGARDS
        print("\n\n" + "═" * 80)
        print("🎯 PHASE 4: SECTOR LAGGARD OPPORTUNITIES")
        print("   Hot sector + lagging stock = sympathy play")
        print("═" * 80)
        
        laggards = self.find_sector_laggards(sector_heat)
        self._print_laggards(laggards)
        
        # 5. DECISION MATRIX
        print("\n\n" + "═" * 80)
        print("⚡ PHASE 5: DECISION MATRIX")
        print("   Your action plan for today")
        print("═" * 80)
        
        decisions = self.decision_matrix(wounded, sector_heat, ignitions)
        self._print_decisions(decisions)
        
        # Save results
        self._save_results(wounded, sector_heat, ignitions, laggards, decisions)
        
        print("\n\n" + "🐺" * 40)
        print("       SCAN COMPLETE - GO HUNT")
        print("🐺" * 40 + "\n")
        
        return {
            'wounded': wounded,
            'sector_heat': sector_heat,
            'ignitions': ignitions,
            'laggards': laggards,
            'decisions': decisions
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # HELPER FUNCTIONS
    # ═══════════════════════════════════════════════════════════════════
    
    def _get_tier(self, ticker):
        if ticker in self.TIER_1_MONSTERS:
            return 1
        elif ticker in self.TIER_2_SYMPATHY:
            return 2
        return 3
    
    def _print_wounded_results(self, wounded):
        # Wounded (BUY ZONE)
        print("\n🎯 WOUNDED (Down 5-15% from 10d high) - BUY ZONE:")
        if wounded['wounded']:
            for s in wounded['wounded']:
                tier_stars = "⭐" * (4 - s['tier'])
                print(f"   {tier_stars} {s['ticker']:6} | ${s['price']:7.2f} | {s['dist_from_high']:+6.1f}% from high | Vol: {s['vol_ratio']}x")
                print(f"            Sector: {s['sector']} | {s['notes']}")
        else:
            print("   No wounded wolves today - wait for pullbacks")
        
        # Bleeding (CAUTION)
        print("\n⚠️ BLEEDING (Down >15%) - CAUTION:")
        if wounded['bleeding']:
            for s in wounded['bleeding']:
                print(f"   {s['ticker']:6} | ${s['price']:7.2f} | {s['dist_from_high']:+6.1f}% from high")
        else:
            print("   None")
        
        # Extended (DON'T CHASE)
        print("\n🚫 EXTENDED (At highs) - DON'T CHASE:")
        if wounded['extended']:
            for s in wounded['extended'][:5]:  # Show top 5
                tier_stars = "⭐" * (4 - s['tier'])
                print(f"   {tier_stars} {s['ticker']:6} | ${s['price']:7.2f} | {s['dist_from_high']:+6.1f}% from high")
        else:
            print("   None at highs")
    
    def _print_sector_heat(self, sector_heat):
        # Sort by today's performance
        sorted_sectors = sorted(sector_heat.items(), key=lambda x: x[1]['today'], reverse=True)
        
        print("\n   SECTOR        ETF     TODAY    WEEK    HOT STOCKS")
        print("   " + "-" * 55)
        
        for sector, data in sorted_sectors:
            heat_emoji = "🔥" if data['today'] >= 2 else "  "
            print(f"   {heat_emoji} {sector:12} {data['etf']:6} {data['today']:+6.1f}%  {data['week']:+6.1f}%   {data['hot_stocks']} stocks hot")
            
            # Show top movers in hot sectors
            if data['today'] >= 2 and data['stocks']:
                for stock in data['stocks'][:3]:
                    print(f"      └─ {stock['ticker']:6} {stock['change']:+.1f}%")
    
    def _print_ignitions(self, ignitions):
        if not ignitions:
            print("\n   No momentum ignitions detected")
            return
        
        print("\n   TICKER   TIER   SECTOR         CHANGE    VOLUME    SIGNAL")
        print("   " + "-" * 65)
        
        for ign in ignitions[:10]:  # Top 10
            tier_stars = "⭐" * (4 - ign['tier'])
            print(f"   {ign['ticker']:7} {tier_stars:6} {ign['sector']:14} {ign['change']:+6.1f}%   {ign['vol_ratio']:5.1f}x   {ign['signal_strength']}")
    
    def _print_laggards(self, laggards):
        if not laggards:
            print("\n   No laggard opportunities (sectors not hot enough)")
            return
        
        print("\n   When sector is HOT but stock is lagging = catch-up potential")
        print("\n   TICKER   SECTOR    STOCK CHG   SECTOR AVG   LAG")
        print("   " + "-" * 55)
        
        for lag in laggards[:5]:  # Top 5
            print(f"   {lag['ticker']:7} {lag['sector']:10} {lag['stock_change']:+6.1f}%     {lag['sector_avg']:+6.1f}%    {lag['lag']:+.1f}%")
            if lag['notes']:
                print(f"           └─ {lag['notes']}")
    
    def _print_decisions(self, decisions):
        if not decisions:
            print("\n   No actionable setups today")
            return
        
        # Group by action
        strong_buys = [d for d in decisions if 'STRONG BUY' in d['action']]
        buys = [d for d in decisions if d['action'] == '✅ BUY']
        momentum = [d for d in decisions if 'MOMENTUM' in d['action']]
        consider = [d for d in decisions if 'CONSIDER' in d['action']]
        
        if strong_buys:
            print("\n🔥 STRONG BUY (Score 5+):")
            for d in strong_buys:
                print(f"   {d['ticker']:6} @ ${d['price']} | Score: {d['score']}")
                print(f"           Signals: {', '.join(d['signals'])}")
        
        if buys:
            print("\n✅ BUY (Score 4):")
            for d in buys:
                print(f"   {d['ticker']:6} @ ${d['price']} | Score: {d['score']}")
                print(f"           Signals: {', '.join(d['signals'])}")
        
        if momentum:
            print("\n🚀 MOMENTUM PLAYS (Already moving, can chase small):")
            for d in momentum:
                print(f"   {d['ticker']:6} @ ${d['price']} | Score: {d['score']}")
                print(f"           Signals: {', '.join(d['signals'])}")
        
        if consider:
            print("\n👀 CONSIDER (Need more confirmation):")
            for d in consider[:5]:  # Top 5
                print(f"   {d['ticker']:6} @ ${d['price']} | {', '.join(d['signals'])}")
        
        # Summary
        print("\n" + "─" * 60)
        print(f"   SUMMARY: {len(strong_buys)} STRONG BUY | {len(buys)} BUY | {len(momentum)} MOMENTUM | {len(consider)} WATCH")
    
    def _save_results(self, wounded, sector_heat, ignitions, laggards, decisions):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Convert decisions for JSON (clean up)
        clean_decisions = [{
            'ticker': d['ticker'],
            'action': d['action'],
            'score': d['score'],
            'signals': d['signals'],
            'price': d['price']
        } for d in decisions]
        
        data = {
            'scan_time': timestamp,
            'wounded_wolves': wounded,
            'sector_heat': {k: {**v, 'stocks': v['stocks'][:5]} for k, v in sector_heat.items()},  # Top 5 per sector
            'momentum_ignitions': ignitions[:10],
            'laggard_opportunities': laggards[:5],
            'decisions': clean_decisions[:20]
        }
        
        filename = self.data_dir / f'command_scan_{timestamp}.json'
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Saved: {filename}")


def main():
    command = WolfDenCommand()
    command.run_full_scan()


if __name__ == '__main__':
    main()
