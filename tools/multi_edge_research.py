"""
🐺 MULTI-EDGE RESEARCH FRAMEWORK
=================================

NOT a scanner. A TESTING framework.

Goal: Discover what signals predict big moves BEFORE committing to dashboard.

Approach:
1. Collect ALL available free data on known winners
2. Test MULTIPLE correlations
3. Validate which ones actually work
4. Counter our own findings
5. Build ONLY proven scanners

Tyr's insight: "How did others catch EVTV/ATON but we didn't?"
"""

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import json

class MultiEdgeResearcher:
    """
    Tests multiple data sources/correlations to find what ACTUALLY predicts moves.
    """
    
    def __init__(self):
        self.test_results = {}
        
    def research_ticker(self, ticker, days_back=30):
        """
        Collect EVERYTHING we can on a ticker.
        Test ALL possible correlations.
        """
        print(f"\n{'='*70}")
        print(f"🔬 RESEARCHING: {ticker}")
        print(f"{'='*70}")
        
        stock = yf.Ticker(ticker)
        
        # 1. BASIC PROFILE
        profile = self._test_profile(stock)
        
        # 2. PRICE ACTION (multiple timeframes)
        price_action = self._test_price_action(stock, days_back)
        
        # 3. VOLUME PATTERNS (not just ratio, but WHEN)
        volume_patterns = self._test_volume_patterns(stock)
        
        # 4. NEWS TIMING (before move or after?)
        news_timing = self._test_news_timing(stock)
        
        # 5. SHORT INTEREST (was it squeezable?)
        short_data = self._test_short_squeeze_potential(stock)
        
        # 6. SECTOR MOMENTUM (was sector hot?)
        sector_context = self._test_sector_momentum(stock)
        
        # 7. PRE-MARKET BEHAVIOR (free with yfinance)
        premarket = self._test_premarket_signal(stock)
        
        # 8. OPTIONS INTEREST (if available)
        options_data = self._test_options_signals(stock)
        
        return {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'profile': profile,
            'price_action': price_action,
            'volume_patterns': volume_patterns,
            'news_timing': news_timing,
            'short_data': short_data,
            'sector_context': sector_context,
            'premarket': premarket,
            'options': options_data
        }
    
    def _test_profile(self, stock):
        """Test: Does market cap, sector, industry predict move type?"""
        info = stock.info
        
        sector = info.get('sector', 'Unknown')
        industry = info.get('industry', 'Unknown')
        cap = info.get('marketCap', 0)
        
        # Categorize
        cap_type = 'NANO' if cap < 10e6 else 'MICRO' if cap < 100e6 else 'SMALL' if cap < 2e9 else 'MID' if cap < 10e9 else 'LARGE'
        
        # Test: Is biotech more consistent? Are nano-caps more explosive?
        return {
            'sector': sector,
            'industry': industry,
            'market_cap': cap,
            'cap_type': cap_type,
            'is_biotech': sector == 'Healthcare' and 'Biotech' in industry,
            'is_micro': cap < 100e6,
            'hypothesis': f"{cap_type} + {sector} = ?" 
        }
    
    def _test_price_action(self, stock, days_back):
        """Test: What price patterns preceded the move?"""
        hist = stock.history(period=f'{days_back}d', interval='1d')
        
        if len(hist) < 5:
            return {'error': 'Insufficient data'}
        
        # Calculate multiple timeframe moves
        moves = {}
        for days in [1, 2, 3, 5, 10, 20]:
            if len(hist) >= days:
                move = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-days-1]) - 1) * 100
                moves[f'{days}d'] = round(move, 2)
        
        # Test: Was there a pattern before explosion?
        # - Flat then spike (coiled spring)?
        # - Gradual build (momentum)?
        # - Sudden spike (news)?
        
        recent_volatility = hist['Close'].iloc[-5:].std() / hist['Close'].iloc[-5:].mean() * 100
        
        return {
            'moves': moves,
            'recent_volatility': round(recent_volatility, 2),
            'pattern_type': self._classify_price_pattern(hist),
            'hypothesis': 'Does flat->spike pattern predict AH explosion?'
        }
    
    def _classify_price_pattern(self, hist):
        """Classify the price pattern before move"""
        if len(hist) < 10:
            return 'INSUFFICIENT_DATA'
        
        recent_5d = hist['Close'].iloc[-5:]
        prior_5d = hist['Close'].iloc[-10:-5]
        
        recent_move = ((recent_5d.iloc[-1] / recent_5d.iloc[0]) - 1) * 100
        prior_move = ((prior_5d.iloc[-1] / prior_5d.iloc[0]) - 1) * 100
        
        if abs(prior_move) < 5 and recent_move > 20:
            return 'FLAT_THEN_SPIKE'
        elif recent_move > 20 and prior_move > 10:
            return 'MOMENTUM_BUILD'
        elif recent_move > 30:
            return 'SUDDEN_SPIKE'
        elif abs(recent_move) < 5:
            return 'FLAT'
        else:
            return 'GRADUAL'
    
    def _test_volume_patterns(self, stock):
        """Test: WHEN did volume hit? Morning spike? All day?"""
        # Get intraday if possible
        intraday = stock.history(period='1d', interval='1m')
        daily = stock.history(period='20d', interval='1d')
        
        if daily.empty:
            return {'error': 'No data'}
        
        # Daily volume analysis
        recent_vol = daily['Volume'].iloc[-1]
        avg_vol_20d = daily['Volume'].iloc[-20:].mean()
        vol_ratio = recent_vol / avg_vol_20d if avg_vol_20d > 0 else 0
        
        # Intraday timing (if available)
        timing = 'UNAVAILABLE'
        if not intraday.empty and len(intraday) > 50:
            intraday['hour'] = intraday.index.hour
            hourly_vol = intraday.groupby('hour')['Volume'].sum()
            
            # When was peak volume?
            peak_hour = hourly_vol.idxmax()
            
            if peak_hour < 11:
                timing = 'MORNING_SPIKE'
            elif peak_hour < 13:
                timing = 'MIDDAY'
            elif peak_hour >= 14:
                timing = 'AFTERNOON'
        
        return {
            'vol_ratio_20d': round(vol_ratio, 2),
            'intraday_timing': timing,
            'hypothesis': 'Morning volume spike = insiders know something?'
        }
    
    def _test_news_timing(self, stock):
        """Test: Did news come BEFORE move or AFTER?"""
        try:
            news = stock.news
            if not news:
                return {'count': 0, 'timing': 'NO_NEWS'}
            
            # Count news in last 24h
            now = datetime.now()
            recent_news = [n for n in news if datetime.fromtimestamp(n.get('providerPublishTime', 0)) > now - timedelta(hours=24)]
            
            return {
                'count_24h': len(recent_news),
                'total_count': len(news),
                'hypothesis': 'News before move = catalyst, news after = fomo'
            }
        except:
            return {'error': 'News unavailable'}
    
    def _test_short_squeeze_potential(self, stock):
        """Test: High short interest = squeeze setup?"""
        info = stock.info
        
        short_pct = info.get('shortPercentOfFloat', 0) * 100
        short_ratio = info.get('shortRatio', 0)
        
        # Test: Does >20% short interest predict squeezes?
        is_squeezable = short_pct > 20
        
        return {
            'short_pct_float': round(short_pct, 2),
            'short_ratio': short_ratio,
            'is_squeezable': is_squeezable,
            'hypothesis': 'High short % on micro-cap = squeeze setup?'
        }
    
    def _test_sector_momentum(self, stock):
        """Test: Was the whole sector moving?"""
        info = stock.info
        sector = info.get('sector', 'Unknown')
        
        # TODO: Check if other stocks in sector were moving
        # For now, just note the sector
        
        return {
            'sector': sector,
            'hypothesis': 'Sector rotation = predictive signal?'
        }
    
    def _test_premarket_signal(self, stock):
        """Test: Pre-market volume/move predicts day?"""
        # yfinance has pre-market data in extended hours
        try:
            premarket = stock.history(period='1d', interval='1m', prepost=True)
            
            if premarket.empty:
                return {'available': False}
            
            # Filter to pre-market hours (4am-9:30am)
            premarket_only = premarket[premarket.index.hour < 9.5]
            
            if len(premarket_only) == 0:
                return {'available': False}
            
            pm_vol = premarket_only['Volume'].sum()
            pm_move = ((premarket_only['Close'].iloc[-1] / premarket_only['Open'].iloc[0]) - 1) * 100 if len(premarket_only) > 0 else 0
            
            return {
                'available': True,
                'pm_volume': pm_vol,
                'pm_move_pct': round(pm_move, 2),
                'hypothesis': 'Pre-market spike = smart money positioning?'
            }
        except:
            return {'available': False}
    
    def _test_options_signals(self, stock):
        """Test: Unusual options activity?"""
        # Options data requires premium APIs, skip for now
        return {
            'available': False,
            'note': 'Options flow requires premium data'
        }
    
    def compare_multiple_tickers(self, tickers):
        """
        Research multiple tickers, find commonalities.
        Test MULTIPLE hypotheses.
        """
        results = []
        
        for ticker in tickers:
            try:
                result = self.research_ticker(ticker)
                results.append(result)
            except Exception as e:
                print(f"   Error on {ticker}: {e}")
        
        # Analyze commonalities
        self._analyze_commonalities(results)
        
        return results
    
    def _analyze_commonalities(self, results):
        """
        Find what the winners have in common.
        TEST multiple hypotheses.
        """
        print(f"\n{'='*70}")
        print("🧪 TESTING HYPOTHESES:")
        print(f"{'='*70}")
        
        # Hypothesis 1: Biotech is consistent
        biotech_count = sum(1 for r in results if r['profile'].get('is_biotech'))
        print(f"\n1. BIOTECH PATTERN:")
        print(f"   Count: {biotech_count}/{len(results)}")
        print(f"   Tyr says: '28% of moves'")
        print(f"   Test: Is biotech more predictable?")
        
        # Hypothesis 2: Micro-caps are explosive
        micro_count = sum(1 for r in results if r['profile'].get('is_micro'))
        print(f"\n2. MICRO-CAP PATTERN:")
        print(f"   Count: {micro_count}/{len(results)}")
        print(f"   Tyr says: 'The +100%+ monsters'")
        print(f"   Test: Are micro-caps less predictable but more explosive?")
        
        # Hypothesis 3: Morning volume spike
        morning_spike_count = sum(1 for r in results if r.get('volume_patterns', {}).get('intraday_timing') == 'MORNING_SPIKE')
        print(f"\n3. MORNING VOLUME SPIKE:")
        print(f"   Count: {morning_spike_count}/{len(results)}")
        print(f"   Test: Morning spike = insiders know?")
        
        # Hypothesis 4: Flat then spike (coiled spring)
        coiled_count = sum(1 for r in results if r.get('price_action', {}).get('pattern_type') == 'FLAT_THEN_SPIKE')
        print(f"\n4. COILED SPRING PATTERN:")
        print(f"   Count: {coiled_count}/{len(results)}")
        print(f"   Test: Flat then spike predicts continuation?")
        
        print(f"\n{'='*70}")
        print("💡 WHAT TO BUILD:")
        print(f"{'='*70}")
        print("\nBased on which hypotheses test TRUE, build scanners for:")
        print("   • High-probability patterns (consistent)")
        print("   • High-reward patterns (explosive)")
        print("   • Early warning signals (before move)")

def main():
    """
    Research framework - test before building
    """
    researcher = MultiEdgeResearcher()
    
    # Known winners
    winners = [
        'EVTV',   # Consumer, micro-cap, +336%
        'LVLU',   # Consumer, micro-cap, +115%
        'ALMS',   # Biotech, large-cap, +30%
        'RARE',   # Biotech, large-cap, +8%
        'NTLA',   # Biotech, mid-cap, +17%
        'OMH',    # Real estate, micro-cap, +50%
        'ATON',   # Financial, nano-cap, +113% AH
    ]
    
    print("🐺 MULTI-EDGE RESEARCH - TESTING BEFORE BUILDING")
    print("="*70)
    print("\nResearching known winners to find REAL patterns...")
    print("Testing MULTIPLE hypotheses, not fitting to one...")
    
    results = researcher.compare_multiple_tickers(winners)
    
    # Save results
    output_file = 'research/multi_edge_analysis.json'
    import os
    os.makedirs('research', exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Research saved to: {output_file}")
    print("\n🐺 Next: Analyze results, build ONLY validated scanners")

if __name__ == "__main__":
    main()
