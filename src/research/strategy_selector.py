#!/usr/bin/env python3
"""
🐺 MULTI-STRATEGY SELECTOR 🐺

THE 10 STRATEGIES (from Fenrir's Amended Blueprint):

1. Insider Cluster Thesis    - 3+ insider P-code buys
2. Wounded Wolf Reversal     - Tier 1 runner down 5-15%
3. Momentum Ignition Scalp   - 2x volume breakout
4. Sector Sympathy Laggard   - Hot sector, buy the laggard
5. After-Hours Momentum      - AH move with volume (SIDU taught us)
6. Gap-and-Go                - 5%+ morning gap, ride continuation
7. Mean Reversion Oversold   - Quality stock down 20%+, RSI < 30
8. Short Squeeze Setup       - High SI + catalyst
9. Earnings Momentum         - Run into earnings, sell before
10. Technical Breakout       - Pattern completion with volume

"No strategy is permanent. No trade is forbidden - only poorly-sized trades."
"The market rewards ADAPTATION."

Author: Brokkr (implementing Fenrir's doctrine)
Date: January 3, 2026
"""

import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Tuple


class StrategySelector:
    """
    Analyze a stock and identify which strategies apply
    Multiple strategies can (and should) combine
    """
    
    # Strategy definitions with conditions
    STRATEGIES = {
        1: {
            'name': 'Insider Cluster Thesis',
            'trigger': '3+ insider P-code buys in 30 days',
            'timeframe': 'Swing (1-4 weeks)',
            'sizing': 'Full position',
            'edge': 'Smart money accumulation',
        },
        2: {
            'name': 'Wounded Wolf Reversal',
            'trigger': 'Tier 1 runner down 5-15% from 10d high',
            'timeframe': 'Swing (days to weeks)',
            'sizing': 'Standard position',
            'edge': 'Proven runners bounce',
        },
        3: {
            'name': 'Momentum Ignition Scalp',
            'trigger': '2x+ average volume in first 30 min',
            'timeframe': 'Intraday to 2-3 days',
            'sizing': 'Smaller, quick profit',
            'edge': 'Volume precedes price',
        },
        4: {
            'name': 'Sector Sympathy Laggard',
            'trigger': 'Sector hot, stock lagging 5%+ behind peers',
            'timeframe': 'Intraday to next day',
            'sizing': 'Standard position',
            'edge': 'Money flows to entire sector',
        },
        5: {
            'name': 'After-Hours Momentum',
            'trigger': 'AH move 5%+ with volume, continues into next day',
            'timeframe': 'Next day open',
            'sizing': 'House money if already in, else small',
            'edge': 'AH moves often continue (SIDU taught us)',
        },
        6: {
            'name': 'Gap-and-Go',
            'trigger': '5%+ gap up at open, holds first 5 min',
            'timeframe': 'Intraday',
            'sizing': 'Small, quick scalp',
            'edge': 'Momentum continuation',
        },
        7: {
            'name': 'Mean Reversion Oversold',
            'trigger': 'Quality stock down 20%+, RSI < 30',
            'timeframe': 'Swing (1-2 weeks)',
            'sizing': 'Standard, add on confirmation',
            'edge': 'Oversold bounces',
        },
        8: {
            'name': 'Short Squeeze Setup',
            'trigger': 'High short interest + catalyst',
            'timeframe': 'Days',
            'sizing': 'Small, high risk/reward',
            'edge': 'Forced covering',
        },
        9: {
            'name': 'Earnings Momentum',
            'trigger': 'Run into earnings, sell before',
            'timeframe': '1-2 weeks before earnings',
            'sizing': 'Standard, exit before report',
            'edge': 'Anticipation > reality',
        },
        10: {
            'name': 'Technical Breakout',
            'trigger': 'Pattern completion with volume confirmation',
            'timeframe': 'Swing',
            'sizing': 'Standard',
            'edge': 'Chart patterns work on liquid names',
        },
    }
    
    # Tier 1 runners (for Strategy 2)
    TIER_1_RUNNERS = ['SIDU', 'RCAT', 'LUNR', 'ASTS', 'RDW', 'CLSK', 'IONQ', 'QBTS']
    
    # Sector mappings
    SECTORS = {
        'Space': ['LUNR', 'RKLB', 'ASTS', 'RDW', 'BKSY', 'SPCE', 'SIDU'],
        'Quantum': ['IONQ', 'RGTI', 'QBTS', 'QUBT'],
        'Nuclear': ['SMR', 'NNE', 'OKLO', 'LEU', 'CCJ'],
        'Defense': ['RCAT', 'AISP', 'PLTR'],
        'Crypto': ['CLSK', 'MARA', 'RIOT', 'COIN'],
    }
    
    def __init__(self):
        self.data_dir = Path('logs/strategies')
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_stock(self, ticker: str, verbose: bool = True) -> Dict:
        """
        Analyze a stock and identify all applicable strategies
        
        Returns dict with:
        - applicable_strategies: list of strategy numbers
        - strategy_details: full analysis for each
        - combined_score: overall opportunity score
        - recommended_action: what to do
        """
        if verbose:
            print(f"\n🐺 MULTI-STRATEGY ANALYSIS: {ticker}")
            print("=" * 60)
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1mo')
            info = stock.info
            
            if len(hist) < 5:
                return {'error': 'Insufficient data'}
            
        except Exception as e:
            return {'error': str(e)}
        
        current = hist['Close'].iloc[-1]
        
        applicable = []
        details = {}
        
        # ═══════════════════════════════════════════════════════════════
        # STRATEGY 2: Wounded Wolf Reversal
        # ═══════════════════════════════════════════════════════════════
        high_10d = hist['High'].tail(10).max()
        dist_from_high = ((current - high_10d) / high_10d) * 100
        
        is_tier1 = ticker in self.TIER_1_RUNNERS
        is_wounded = -15 <= dist_from_high <= -5
        
        if is_tier1 and is_wounded:
            applicable.append(2)
            details[2] = {
                'name': 'Wounded Wolf Reversal',
                'signal_strength': 'STRONG' if dist_from_high <= -10 else 'MODERATE',
                'data': {
                    'distance_from_high': round(dist_from_high, 1),
                    'high_10d': round(high_10d, 2),
                    'is_tier1': True,
                }
            }
        
        # ═══════════════════════════════════════════════════════════════
        # STRATEGY 3: Momentum Ignition Scalp
        # ═══════════════════════════════════════════════════════════════
        avg_vol = hist['Volume'].tail(20).mean()
        today_vol = hist['Volume'].iloc[-1]
        vol_ratio = today_vol / avg_vol if avg_vol > 0 else 1
        
        if vol_ratio >= 2.0:
            applicable.append(3)
            details[3] = {
                'name': 'Momentum Ignition Scalp',
                'signal_strength': 'STRONG' if vol_ratio >= 3.0 else 'MODERATE',
                'data': {
                    'volume_ratio': round(vol_ratio, 2),
                    'today_volume': int(today_vol),
                    'avg_volume': int(avg_vol),
                }
            }
        
        # ═══════════════════════════════════════════════════════════════
        # STRATEGY 4: Sector Sympathy Laggard
        # ═══════════════════════════════════════════════════════════════
        stock_sector = None
        for sector, tickers in self.SECTORS.items():
            if ticker in tickers:
                stock_sector = sector
                break
        
        if stock_sector:
            # Calculate sector average
            sector_changes = []
            for peer in self.SECTORS[stock_sector]:
                try:
                    peer_stock = yf.Ticker(peer)
                    peer_hist = peer_stock.history(period='5d')
                    if len(peer_hist) >= 2:
                        peer_change = ((peer_hist['Close'].iloc[-1] - peer_hist['Close'].iloc[-2]) 
                                      / peer_hist['Close'].iloc[-2]) * 100
                        sector_changes.append(peer_change)
                except:
                    continue
            
            if sector_changes:
                sector_avg = sum(sector_changes) / len(sector_changes)
                stock_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) 
                               / hist['Close'].iloc[-2]) * 100
                lag = sector_avg - stock_change
                
                # Sector is "hot" if avg up 3%+, and stock is lagging 5%+
                if sector_avg >= 3 and lag >= 5:
                    applicable.append(4)
                    details[4] = {
                        'name': 'Sector Sympathy Laggard',
                        'signal_strength': 'STRONG' if lag >= 10 else 'MODERATE',
                        'data': {
                            'sector': stock_sector,
                            'sector_avg': round(sector_avg, 2),
                            'stock_change': round(stock_change, 2),
                            'lag': round(lag, 2),
                        }
                    }
        
        # ═══════════════════════════════════════════════════════════════
        # STRATEGY 6: Gap-and-Go (check previous day's gap)
        # ═══════════════════════════════════════════════════════════════
        if len(hist) >= 2:
            prev_close = hist['Close'].iloc[-2]
            open_price = hist['Open'].iloc[-1]
            gap_pct = ((open_price - prev_close) / prev_close) * 100
            
            if gap_pct >= 5:
                applicable.append(6)
                details[6] = {
                    'name': 'Gap-and-Go',
                    'signal_strength': 'STRONG' if gap_pct >= 10 else 'MODERATE',
                    'data': {
                        'gap_percent': round(gap_pct, 2),
                        'prev_close': round(prev_close, 2),
                        'open': round(open_price, 2),
                    }
                }
        
        # ═══════════════════════════════════════════════════════════════
        # STRATEGY 7: Mean Reversion Oversold
        # ═══════════════════════════════════════════════════════════════
        # Calculate RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1])) if loss.iloc[-1] != 0 else 50
        
        # Check if down 20%+ from 30-day high
        high_30d = hist['High'].max()
        dist_30d = ((current - high_30d) / high_30d) * 100
        
        if dist_30d <= -20 and rsi < 30:
            applicable.append(7)
            details[7] = {
                'name': 'Mean Reversion Oversold',
                'signal_strength': 'STRONG' if rsi < 25 else 'MODERATE',
                'data': {
                    'rsi': round(rsi, 1),
                    'distance_from_30d_high': round(dist_30d, 1),
                }
            }
        
        # ═══════════════════════════════════════════════════════════════
        # STRATEGY 10: Technical Breakout (simple version)
        # ═══════════════════════════════════════════════════════════════
        # Check if breaking out of 10-day range with volume
        high_10d_range = hist['High'].tail(10).max()
        low_10d_range = hist['Low'].tail(10).min()
        range_size = high_10d_range - low_10d_range
        
        # If current > high and volume is up
        if current > high_10d_range * 0.99 and vol_ratio >= 1.5:
            applicable.append(10)
            details[10] = {
                'name': 'Technical Breakout',
                'signal_strength': 'STRONG' if vol_ratio >= 2.0 else 'MODERATE',
                'data': {
                    'breakout_level': round(high_10d_range, 2),
                    'current': round(current, 2),
                    'volume_ratio': round(vol_ratio, 2),
                }
            }
        
        # ═══════════════════════════════════════════════════════════════
        # COMBINED ANALYSIS
        # ═══════════════════════════════════════════════════════════════
        
        # Score based on number and strength of strategies
        combined_score = 0
        for strat_num in applicable:
            if details[strat_num]['signal_strength'] == 'STRONG':
                combined_score += 2
            else:
                combined_score += 1
        
        # Determine action
        if combined_score >= 4:
            action = "🔥 STRONG BUY - Multiple strategies aligned"
        elif combined_score >= 2:
            action = "✅ BUY - Good setup"
        elif combined_score >= 1:
            action = "👀 WATCH - Single strategy, wait for confirmation"
        else:
            action = "⏳ NO SETUP - Wait for better entry"
        
        result = {
            'ticker': ticker,
            'current_price': round(current, 2),
            'applicable_strategies': applicable,
            'strategy_details': details,
            'combined_score': combined_score,
            'recommended_action': action,
            'analysis_time': datetime.now().isoformat(),
        }
        
        if verbose:
            self._print_analysis(result)
        
        return result
    
    def _print_analysis(self, result: Dict):
        """Print formatted analysis"""
        print(f"\n   Price: ${result['current_price']}")
        print(f"   Combined Score: {result['combined_score']}")
        print(f"\n   {result['recommended_action']}")
        
        if result['applicable_strategies']:
            print(f"\n   APPLICABLE STRATEGIES:")
            print("   " + "-" * 50)
            
            for strat_num in result['applicable_strategies']:
                detail = result['strategy_details'][strat_num]
                strength = "🔥" if detail['signal_strength'] == 'STRONG' else "👀"
                print(f"\n   {strength} Strategy #{strat_num}: {detail['name']}")
                print(f"      Signal: {detail['signal_strength']}")
                for key, val in detail['data'].items():
                    print(f"      {key}: {val}")
        else:
            print("\n   No strategies currently applicable")
            print("   Wait for better setup")
    
    def scan_watchlist(self, tickers: List[str]) -> List[Dict]:
        """Scan multiple tickers and rank by combined score"""
        print("\n🐺 MULTI-STRATEGY WATCHLIST SCAN")
        print("=" * 70)
        
        results = []
        
        for ticker in tickers:
            result = self.analyze_stock(ticker, verbose=False)
            if 'error' not in result:
                results.append(result)
        
        # Sort by combined score
        results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # Print summary
        print(f"\n{'TICKER':<8} {'PRICE':>8} {'SCORE':>6} {'STRATEGIES':>30} {'ACTION':<20}")
        print("-" * 80)
        
        for r in results:
            strats = ', '.join([f"#{s}" for s in r['applicable_strategies']]) or 'None'
            action = r['recommended_action'].split(' - ')[0]  # Just the emoji part
            print(f"{r['ticker']:<8} ${r['current_price']:>6.2f} {r['combined_score']:>6} {strats:>30} {action:<20}")
        
        # Save results
        self._save_scan(results)
        
        return results
    
    def _save_scan(self, results: List[Dict]):
        """Save scan results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.data_dir / f'strategy_scan_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Saved: {filename}")
    
    def print_strategy_guide(self):
        """Print all strategies as reference"""
        print("\n🐺 THE 10 STRATEGIES - QUICK REFERENCE")
        print("=" * 70)
        
        for num, strat in self.STRATEGIES.items():
            print(f"\n#{num}: {strat['name']}")
            print(f"   Trigger: {strat['trigger']}")
            print(f"   Timeframe: {strat['timeframe']}")
            print(f"   Sizing: {strat['sizing']}")
            print(f"   Edge: {strat['edge']}")
        
        print("\n" + "=" * 70)
        print("\"No strategy is permanent. The market rewards ADAPTATION.\"")
        print("=" * 70)


def main():
    import sys
    
    selector = StrategySelector()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'guide':
            selector.print_strategy_guide()
        
        elif command == 'scan':
            # Scan default watchlist
            watchlist = ['SIDU', 'RCAT', 'LUNR', 'ASTS', 'RDW', 'CLSK', 
                        'IONQ', 'QBTS', 'AISP', 'SMR', 'OKLO']
            selector.scan_watchlist(watchlist)
        
        else:
            # Assume it's a ticker
            selector.analyze_stock(command.upper())
    else:
        # Default: show guide and scan
        selector.print_strategy_guide()
        print("\n")
        watchlist = ['SIDU', 'RCAT', 'LUNR', 'ASTS', 'RDW', 'AISP']
        selector.scan_watchlist(watchlist)


if __name__ == '__main__':
    main()
