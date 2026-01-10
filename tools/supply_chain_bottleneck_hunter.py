#!/usr/bin/env python3
"""
🐺 SUPPLY CHAIN BOTTLENECK HUNTER
Finds Level 3 plays by tracing the supply chain BACKWARD

Fenrir's framework:
Level 1: The narrative (AI is hot)
Level 2: What it needs (nuclear power)
Level 3: What that needs (uranium, equipment)
Level 4: The bottleneck (who supplies Level 3?)

This tool:
1. Takes a hot ticker (like UUUU)
2. Traces supply chain backward
3. Finds bottlenecks (limited suppliers)
4. Predicts what gets squeezed next

The META-GAME: Find what will be scarce BEFORE it's scarce.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path

class SupplyChainHunter:
    """
    Trace supply chains to find Level 3+ opportunities
    
    The logic:
    - When sector gets hot → demand spikes
    - Suppliers get squeezed → prices rise
    - Supplier's suppliers get REALLY squeezed → biggest gains
    
    Example:
    AI hot → Data centers need power → Nuclear plants need uranium →
    Uranium miners need equipment → EQUIPMENT SUPPLIERS = bottleneck
    """
    
    def __init__(self):
        self.supply_chains = self.build_supply_chain_map()
        self.data_dir = Path(__file__).parent.parent / 'logs' / 'supply_chain'
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def build_supply_chain_map(self):
        """
        Map of supply chains (manually curated by Fenrir's research)
        
        Format:
        {
            'sector': {
                'level_1': [obvious plays],
                'level_2': [what they need],
                'level_3': [what level 2 needs],
                'bottlenecks': [limited suppliers]
            }
        }
        """
        return {
            'AI': {
                'narrative': 'AI needs massive compute power',
                'level_1': ['NVDA', 'AMD', 'MSFT'],  # Obvious
                'level_2': ['SMR', 'OKLO', 'UUUU'],  # Power supply
                'level_3': ['CCJ', 'DNN', 'UUUU'],   # Uranium
                'level_4': ['CAT', 'DE', 'FLR'],     # Mining equipment
                'bottleneck': 'Mining equipment + processing chemicals',
                'bottleneck_tickers': ['CAT', 'DE', 'FLR', 'DOW']
            },
            
            'Nuclear': {
                'narrative': 'Nuclear energy revival for AI + climate',
                'level_1': ['SMR', 'OKLO', 'NuScale'],  # Small modular reactors
                'level_2': ['UUUU', 'CCJ', 'DNN'],      # Uranium miners
                'level_3': ['UUUU', 'MP', 'USAR'],      # Rare earths (for mining equipment)
                'level_4': ['CAT', 'ALB', 'SQM'],       # Equipment + lithium (batteries for equipment)
                'bottleneck': 'Rare earth magnets + heavy equipment',
                'bottleneck_tickers': ['CAT', 'MP', 'ALB']
            },
            
            'Defense': {
                'narrative': 'Geopolitical tensions + Ukraine/Taiwan',
                'level_1': ['LMT', 'RTX', 'NOC'],       # Big primes
                'level_2': ['AISP', 'AVAV', 'KTOS'],    # Small cap contractors
                'level_3': ['TDY', 'HII', 'LDOS'],      # Specialized components
                'level_4': ['MP', 'USAR', 'UUUU'],      # Rare earths (missiles need magnets)
                'bottleneck': 'Rare earth permanent magnets',
                'bottleneck_tickers': ['MP', 'USAR']
            },
            
            'EVs': {
                'narrative': 'Electric vehicle transition',
                'level_1': ['TSLA', 'RIVN', 'LCID'],   # Car makers
                'level_2': ['ALB', 'SQM', 'LTHM'],     # Lithium
                'level_3': ['MP', 'UUUU', 'USAR'],     # Rare earths (motors)
                'level_4': ['CAT', 'RIO', 'BHP'],      # Mining equipment
                'bottleneck': 'Rare earth processing (China controls 90%)',
                'bottleneck_tickers': ['MP', 'USAR']
            },
            
            'Quantum': {
                'narrative': 'Quantum computing breakthrough',
                'level_1': ['QUBT', 'QBTS', 'IONQ'],   # Quantum computers
                'level_2': ['ASML', 'AMAT', 'LRCX'],   # Fabrication equipment
                'level_3': ['USAR', 'UUUU', 'MP'],     # Rare earths (quantum sensors)
                'level_4': ['???'],                     # Unknown (too early)
                'bottleneck': 'Helium-3 + rare earth isotopes',
                'bottleneck_tickers': ['???']  # Opportunity - no public plays yet
            }
        }
    
    def find_bottlenecks(self, hot_ticker):
        """
        Given a hot ticker, trace back to find the bottleneck
        
        Args:
            hot_ticker: str - The ticker that's running (e.g., 'UUUU')
        
        Returns:
            dict: Bottleneck analysis with Level 3+ plays
        """
        print(f"\n🔍 BOTTLENECK HUNTER: Tracing {hot_ticker}")
        print("=" * 60)
        
        # Find which sectors this ticker is in
        sectors_found = []
        ticker_level = None
        
        for sector, chain in self.supply_chains.items():
            for level in ['level_1', 'level_2', 'level_3', 'level_4']:
                if hot_ticker in chain.get(level, []):
                    sectors_found.append(sector)
                    ticker_level = level
                    break
        
        if not sectors_found:
            print(f"   ⚠️ {hot_ticker} not found in supply chain maps")
            print(f"   💡 Add it to supply_chain_map manually")
            return None
        
        sector = sectors_found[0]
        chain = self.supply_chains[sector]
        
        print(f"\n📊 SECTOR: {sector}")
        print(f"   Narrative: {chain['narrative']}")
        print(f"   Your position: {hot_ticker} (at {ticker_level})")
        print(f"\n🔗 SUPPLY CHAIN:")
        
        # Show the chain
        for i, level in enumerate(['level_1', 'level_2', 'level_3', 'level_4'], 1):
            tickers = chain.get(level, [])
            marker = "👈 YOU ARE HERE" if level == ticker_level else ""
            print(f"   Level {i}: {', '.join(tickers)} {marker}")
        
        print(f"\n⚠️ BOTTLENECK: {chain['bottleneck']}")
        print(f"   Bottleneck tickers: {', '.join(chain['bottleneck_tickers'])}")
        
        # Analyze bottleneck tickers
        bottleneck_analysis = []
        
        for ticker in chain['bottleneck_tickers']:
            if ticker == '???':
                print(f"\n   {ticker}: Opportunity not yet public")
                continue
            
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1mo')
                
                if len(hist) < 5:
                    continue
                
                current_price = hist['Close'].iloc[-1]
                change_5d = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5] * 100) if len(hist) >= 5 else 0
                change_1mo = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100)
                
                # Volume analysis
                avg_volume = hist['Volume'].mean()
                recent_volume = hist['Volume'].iloc[-1]
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
                
                # Get market cap
                info = stock.info
                market_cap = info.get('marketCap', 0)
                market_cap_b = market_cap / 1e9 if market_cap else 0
                
                status = self._categorize_play(change_1mo, change_5d, volume_ratio)
                
                bottleneck_analysis.append({
                    'ticker': ticker,
                    'price': current_price,
                    'change_5d': change_5d,
                    'change_1mo': change_1mo,
                    'volume_ratio': volume_ratio,
                    'market_cap_b': market_cap_b,
                    'status': status
                })
                
                print(f"\n   {ticker}: ${current_price:.2f}")
                print(f"      5-Day: {change_5d:+.2f}%")
                print(f"      1-Month: {change_1mo:+.2f}%")
                print(f"      Volume: {volume_ratio:.2f}x")
                print(f"      Market Cap: ${market_cap_b:.1f}B")
                print(f"      Status: {status}")
                
            except Exception as e:
                print(f"\n   {ticker}: Error - {e}")
                continue
        
        # Find the BEST bottleneck play
        if bottleneck_analysis:
            # Sort by status priority
            priority = {'🟢 EARLY': 3, '🟡 MOVING': 2, '🔴 LATE': 1}
            bottleneck_analysis.sort(key=lambda x: (priority.get(x['status'], 0), x['change_1mo']), reverse=True)
            
            best = bottleneck_analysis[0]
            
            print(f"\n🎯 BEST BOTTLENECK PLAY:")
            print(f"   {best['ticker']} - {best['status']}")
            print(f"   Current: ${best['price']:.2f}")
            print(f"   1-Month: {best['change_1mo']:+.2f}%")
            print(f"   Logic: When {hot_ticker} needs more capacity, {best['ticker']} gets squeezed")
        
        result = {
            'sector': sector,
            'narrative': chain['narrative'],
            'your_position': hot_ticker,
            'your_level': ticker_level,
            'bottleneck': chain['bottleneck'],
            'bottleneck_plays': bottleneck_analysis,
            'best_play': best if bottleneck_analysis else None
        }
        
        return result
    
    def _categorize_play(self, change_1mo, change_5d, volume_ratio):
        """Categorize if play is early, moving, or late"""
        if change_1mo < 5 and volume_ratio < 1.5:
            return "🟢 EARLY (not discovered yet)"
        elif change_1mo < 15 and volume_ratio > 1.2:
            return "🟡 MOVING (early positioning)"
        else:
            return "🔴 LATE (already ran)"
    
    def find_common_bottlenecks(self, tickers):
        """
        Given multiple hot tickers, find what they ALL need
        
        This finds Level 4+ plays by identifying common suppliers
        
        Args:
            tickers: list of hot tickers
        
        Returns:
            dict: Common bottlenecks across multiple sectors
        """
        print(f"\n🔍 COMMON BOTTLENECK HUNTER")
        print(f"   Analyzing: {', '.join(tickers)}")
        print("=" * 60)
        
        # Find bottlenecks for each ticker
        all_bottlenecks = {}
        
        for ticker in tickers:
            result = self.find_bottlenecks(ticker)
            if result and result['bottleneck_plays']:
                sector = result['sector']
                for play in result['bottleneck_plays']:
                    bt = play['ticker']
                    if bt not in all_bottlenecks:
                        all_bottlenecks[bt] = {
                            'ticker': bt,
                            'sectors': [],
                            'play_data': play
                        }
                    all_bottlenecks[bt]['sectors'].append(sector)
        
        # Find tickers that appear in multiple bottlenecks
        multi_sector_bottlenecks = {
            k: v for k, v in all_bottlenecks.items() 
            if len(v['sectors']) >= 2
        }
        
        if multi_sector_bottlenecks:
            print(f"\n🎯 MULTI-SECTOR BOTTLENECKS (HIGHEST CONVICTION):")
            for ticker, data in multi_sector_bottlenecks.items():
                print(f"\n   {ticker}:")
                print(f"      Bottleneck for: {', '.join(data['sectors'])}")
                print(f"      Price: ${data['play_data']['price']:.2f}")
                print(f"      1-Month: {data['play_data']['change_1mo']:+.2f}%")
                print(f"      Status: {data['play_data']['status']}")
                print(f"      💡 THESIS: When {len(data['sectors'])} sectors boom, {ticker} gets squeezed from ALL sides")
        else:
            print(f"\n   ℹ️ No common bottlenecks found")
            print(f"   Each sector has different supply chain")
        
        return multi_sector_bottlenecks
    
    def predict_next_bottleneck(self, sector):
        """
        Predict what will be scarce NEXT based on current trends
        
        This is Level 5 thinking: What problem don't they know they have yet?
        """
        print(f"\n🔮 PREDICTING NEXT BOTTLENECK: {sector}")
        print("=" * 60)
        
        chain = self.supply_chains.get(sector)
        if not chain:
            print(f"   ⚠️ Sector not mapped")
            return None
        
        print(f"\n📊 CURRENT STATE:")
        print(f"   Level 1 (hot): {', '.join(chain['level_1'])}")
        print(f"   Level 2 (getting hot): {', '.join(chain['level_2'])}")
        print(f"   Level 3 (early): {', '.join(chain['level_3'])}")
        print(f"   Level 4 (undiscovered): {', '.join(chain['level_4'])}")
        
        print(f"\n🔮 THE PREDICTION:")
        print(f"   When Level 2 doubles production capacity...")
        print(f"   They will need 2x more from Level 3...")
        print(f"   Which will squeeze Level 4...")
        print(f"   Current bottleneck: {chain['bottleneck']}")
        
        # Check if Level 4 has unknowns
        if '???' in chain['level_4']:
            print(f"\n   🎯 RESEARCH OPPORTUNITY:")
            print(f"   Level 4 is not yet public")
            print(f"   Whoever finds it FIRST wins")
            print(f"   Fenrir's job: Research what {chain['level_3'][0]} needs to scale")
        else:
            print(f"\n   🎯 NEXT PLAY:")
            print(f"   Buy {chain['level_4'][0]} BEFORE Level 3 scales")

def main():
    """Demo the bottleneck hunter"""
    print("🐺 SUPPLY CHAIN BOTTLENECK HUNTER")
    print("=" * 60)
    print("Finds Level 3+ plays by tracing supply chains")
    print("=" * 60)
    
    hunter = SupplyChainHunter()
    
    # Example 1: Find bottleneck for UUUU (Tyr's position)
    print("\n\n📍 EXAMPLE 1: Your UUUU position")
    hunter.find_bottlenecks('UUUU')
    
    # Example 2: Find bottleneck for USAR
    print("\n\n📍 EXAMPLE 2: Your USAR position")
    hunter.find_bottlenecks('USAR')
    
    # Example 3: Find COMMON bottlenecks
    print("\n\n📍 EXAMPLE 3: Common bottlenecks across YOUR positions")
    hunter.find_common_bottlenecks(['UUUU', 'USAR', 'AISP'])
    
    # Example 4: Predict next bottleneck
    print("\n\n📍 EXAMPLE 4: Predict next bottleneck in AI sector")
    hunter.predict_next_bottleneck('AI')
    
    print(f"\n\n🐺 LEVEL 3 THINKING:")
    print(f"   Everyone buys UUUU (nuclear)")
    print(f"   Smart money buys what UUUU needs (rare earths)")
    print(f"   Wolf buys what rare earth miners need (CAT, MP equipment)")
    print(f"\n   AWOOOO! 🐺\n")

if __name__ == '__main__':
    main()
