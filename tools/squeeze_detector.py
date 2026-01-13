#!/usr/bin/env python3
"""
🐺 SQUEEZE DETECTOR
Finds micro-cap short squeezes and gamma squeezes

These are NOT technical plays. Different rules apply.

SQUEEZE SIGNALS:
1. Micro-cap (<$100M market cap)
2. Penny stock (<$5) OR micro float
3. EXPLOSIVE volume (10x+)
4. Multi-day momentum building
5. Near or AT new highs

When these line up = SHORT SQUEEZE potential
Can run 100-500%+ over multiple days
"""

import yfinance as yf
from datetime import datetime
import sys
sys.path.insert(0, '/workspaces/trading-companion-2026')


class SqueezeDetector:
    """Detects micro-cap squeeze setups"""
    
    def detect_squeeze_signals(self, ticker):
        """
        Check if ticker shows squeeze characteristics
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period='3mo')
            
            if len(hist) < 30:
                return None
            
            signals = {}
            score = 0
            
            # 1. Market cap check
            market_cap = info.get('marketCap', 0)
            if market_cap == 0:
                market_cap = info.get('sharesOutstanding', 0) * hist['Close'].iloc[-1]
            
            signals['market_cap'] = market_cap
            
            if market_cap < 100_000_000:  # <$100M = micro-cap
                score += 30
                signals['is_micro_cap'] = True
            else:
                signals['is_micro_cap'] = False
                return None  # Not a squeeze candidate
            
            # 2. Price check (penny stocks squeeze more)
            price = hist['Close'].iloc[-1]
            signals['price'] = round(price, 2)
            
            if price < 5:
                score += 20
                signals['is_penny'] = True
            else:
                signals['is_penny'] = False
            
            # 3. EXPLOSIVE volume
            vol_today = hist['Volume'].iloc[-1]
            vol_avg = hist['Volume'].iloc[-30:-1].mean()
            vol_ratio = vol_today / vol_avg if vol_avg > 0 else 1
            
            signals['vol_ratio'] = round(vol_ratio, 1)
            
            if vol_ratio >= 50:
                score += 50  # MASSIVE
                signals['vol_status'] = 'EXPLOSIVE'
            elif vol_ratio >= 20:
                score += 40
                signals['vol_status'] = 'MASSIVE'
            elif vol_ratio >= 10:
                score += 30
                signals['vol_status'] = 'HIGH'
            elif vol_ratio >= 5:
                score += 15
                signals['vol_status'] = 'ELEVATED'
            else:
                signals['vol_status'] = 'NORMAL'
            
            # 4. Multi-day momentum
            week_move = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-6]) - 1) * 100 if len(hist) >= 6 else 0
            day_move = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-2]) - 1) * 100 if len(hist) >= 2 else 0
            
            signals['day_move'] = round(day_move, 1)
            signals['week_move'] = round(week_move, 1)
            
            if week_move > 100:
                score += 30
                signals['momentum'] = 'PARABOLIC'
            elif week_move > 50:
                score += 20
                signals['momentum'] = 'STRONG'
            elif week_move > 20:
                score += 10
                signals['momentum'] = 'BUILDING'
            
            # 5. Near highs (squeeze plays make new highs)
            month_high = hist['High'].iloc[-20:].max()
            from_high = ((price / month_high) - 1) * 100
            
            signals['from_high'] = round(from_high, 1)
            
            if from_high >= -5:
                score += 25
                signals['high_status'] = 'AT_HIGHS'
            elif from_high >= -10:
                score += 15
                signals['high_status'] = 'NEAR_HIGHS'
            else:
                signals['high_status'] = 'OFF_HIGHS'
            
            # 6. Green days (consecutive buying)
            green_days = sum(hist['Close'].tail(5) > hist['Open'].tail(5))
            signals['green_days'] = green_days
            
            if green_days >= 4:
                score += 15
            elif green_days >= 3:
                score += 10
            
            signals['squeeze_score'] = score
            
            return signals
            
        except Exception as e:
            return None
    
    def scan_for_squeezes(self):
        """Scan for active squeezes"""
        from discovery_engine.free_data_sources import build_confirmed_universe
        
        print("=" * 70)
        print("🎰 SQUEEZE DETECTOR")
        print("   Micro-cap short squeeze and gamma squeeze finder")
        print("=" * 70)
        
        # Get universe
        universe = build_confirmed_universe()
        tickers = [u['ticker'] for u in universe]
        
        # Add known squeeze candidates
        penny_stocks = ['EVTV', 'LVLU', 'PASW', 'BDSX', 'OMH', 'JAGX', 'HYMC']
        tickers.extend(penny_stocks)
        tickers = list(set(tickers))
        
        print(f"\n🔍 Scanning {len(tickers)} tickers for squeeze setups...")
        
        squeezes = []
        
        for ticker in tickers:
            signals = self.detect_squeeze_signals(ticker)
            
            if signals and signals['squeeze_score'] >= 70:
                squeezes.append({
                    'ticker': ticker,
                    **signals
                })
        
        # Sort by score
        squeezes.sort(key=lambda x: x['squeeze_score'], reverse=True)
        
        print(f"\n✅ Found {len(squeezes)} active squeezes\n")
        
        if len(squeezes) == 0:
            print("   No active squeezes detected")
            print("   → Check again during market hours\n")
            return []
        
        print("=" * 70)
        print("🔥 ACTIVE SQUEEZES")
        print("=" * 70)
        print(f"\n{'TICKER':<7} {'SCORE':>5} {'CAP':>6} {'VOL':>7} {'WEEK':>7} {'HIGH':>7} STATUS")
        print("-" * 70)
        
        for s in squeezes:
            cap_str = f"${s['market_cap']/1_000_000:.0f}M"
            vol_str = f"{s['vol_ratio']:.0f}x"
            week_str = f"{s['week_move']:.0f}%"
            high_str = f"{s['from_high']:.0f}%"
            
            # Status indicators
            indicators = []
            if s['is_micro_cap']:
                indicators.append('🎰MICRO')
            if s['is_penny']:
                indicators.append('💰PENNY')
            if s['vol_status'] in ['EXPLOSIVE', 'MASSIVE']:
                indicators.append('🔥VOL')
            if s['momentum'] in ['PARABOLIC', 'STRONG']:
                indicators.append('🚀MOM')
            if s['high_status'] == 'AT_HIGHS':
                indicators.append('🎯HIGH')
            
            status = ' '.join(indicators)
            
            print(f"{s['ticker']:<7} {s['squeeze_score']:>5} {cap_str:>6} {vol_str:>7} {week_str:>7} {high_str:>7} {status}")
        
        print("\n" + "=" * 70)
        print("⚠️  SQUEEZE PLAY RULES")
        print("=" * 70)
        print("1. These are HIGH RISK / HIGH REWARD")
        print("2. Can run 100-500%+ over multiple days")
        print("3. Use SMALL position sizes ($50-100)")
        print("4. Set TIGHT stops (20-30%)")
        print("5. Take profits on the way up (50%, 100%, 200%)")
        print("6. Don't hold overnight if momentum breaks")
        print("\n7. 🎰 This is SPECULATION, not investing")
        print("=" * 70)
        
        return squeezes


def main():
    detector = SqueezeDetector()
    return detector.scan_for_squeezes()


if __name__ == "__main__":
    main()
