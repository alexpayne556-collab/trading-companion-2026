#!/usr/bin/env python3
"""
🐺 MISSED GAINS ANALYZER - Find What We're Missing

This tool analyzes:
1. Which watchlist stocks made big moves (10%+) recently
2. What happened BEFORE the move (volume, price action)
3. Which sectors/themes are hot RIGHT NOW
4. Repeat runners (stocks that move 10%+ multiple times)

The goal: Find the PATTERN so we can catch the NEXT one

Author: Brokkr (Brother Mode)
Date: January 3, 2026
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json
from collections import defaultdict


class MissedGainsAnalyzer:
    """
    Analyze what big moves we missed and find the pattern
    """
    
    # Our full watchlist (from various lists)
    MASTER_WATCHLIST = [
        # Defense/AI
        'AISP', 'PLTR', 'KTOS', 'RCAT', 'AVAV', 'LMT', 'RTX', 'NOC', 'GD',
        # Space
        'LUNR', 'RKLB', 'ASTS', 'RDW', 'BKSY', 'SPCE',
        # Nuclear
        'SMR', 'OKLO', 'NNE', 'CCJ', 'LEU', 'LTBR',
        # Quantum Computing
        'IONQ', 'QBTS', 'RGTI', 'QUBT',
        # AI/Tech
        'NVDA', 'AMD', 'AVGO', 'SMCI', 'MRVL', 'TSM',
        # EV/Energy
        'TSLA', 'RIVN', 'LCID', 'NIO', 'XPEV',
        # Biotech
        'MRNA', 'BNTX', 'CRSP', 'EDIT', 'NTLA',
        # Fintech
        'SOFI', 'HOOD', 'COIN', 'AFRM', 'UPST',
        # Social/Consumer
        'RDDT', 'SNAP', 'PINS', 'RBLX',
        # Other momentum
        'GME', 'AMC', 'MSTR', 'CLSK', 'MARA', 'RIOT',
        # Recent adds
        'GEV', 'VST', 'CEG', 'SIDU', 'DRUG'
    ]
    
    # Sector mapping
    SECTORS = {
        'Defense/AI': ['AISP', 'PLTR', 'KTOS', 'RCAT', 'AVAV', 'LMT', 'RTX', 'NOC', 'GD'],
        'Space': ['LUNR', 'RKLB', 'ASTS', 'RDW', 'BKSY', 'SPCE'],
        'Nuclear': ['SMR', 'OKLO', 'NNE', 'CCJ', 'LEU', 'LTBR'],
        'Quantum': ['IONQ', 'QBTS', 'RGTI', 'QUBT'],
        'AI/Semis': ['NVDA', 'AMD', 'AVGO', 'SMCI', 'MRVL', 'TSM'],
        'EV': ['TSLA', 'RIVN', 'LCID', 'NIO', 'XPEV'],
        'Biotech': ['MRNA', 'BNTX', 'CRSP', 'EDIT', 'NTLA'],
        'Fintech': ['SOFI', 'HOOD', 'COIN', 'AFRM', 'UPST'],
        'Meme/Momentum': ['GME', 'AMC', 'MSTR', 'CLSK', 'MARA', 'RIOT'],
        'Power/Grid': ['GEV', 'VST', 'CEG']
    }
    
    def __init__(self):
        self.data_dir = Path('logs/analysis')
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def find_big_moves(self, days_back=30, min_gain=10.0):
        """
        Find all stocks that made 10%+ single-day gains in last N days
        Returns list of moves with date, ticker, gain%, and what happened before
        """
        print(f"\n🔍 SCANNING {len(self.MASTER_WATCHLIST)} STOCKS FOR {min_gain}%+ MOVES")
        print(f"   Looking back {days_back} days...")
        print("=" * 70)
        
        big_moves = []
        
        for ticker in self.MASTER_WATCHLIST:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period=f'{days_back + 10}d')
                
                if len(hist) < 5:
                    continue
                
                # Calculate daily returns
                hist['Daily_Return'] = hist['Close'].pct_change() * 100
                
                # Find days with 10%+ gains
                for i in range(1, len(hist)):
                    daily_return = hist['Daily_Return'].iloc[i]
                    
                    if daily_return >= min_gain:
                        date = hist.index[i]
                        
                        # Get context: what happened 5 days before?
                        start_idx = max(0, i - 5)
                        pre_move_data = hist.iloc[start_idx:i]
                        
                        # Volume analysis
                        avg_vol_before = pre_move_data['Volume'].mean()
                        move_day_vol = hist['Volume'].iloc[i]
                        vol_ratio = move_day_vol / avg_vol_before if avg_vol_before > 0 else 1
                        
                        # Price action before
                        price_5d_before = hist['Close'].iloc[start_idx]
                        price_before_move = hist['Close'].iloc[i-1]
                        pre_move_change = ((price_before_move - price_5d_before) / price_5d_before) * 100
                        
                        # Was there unusual volume in days before?
                        unusual_vol_days = sum(1 for v in pre_move_data['Volume'] if v > avg_vol_before * 1.5)
                        
                        move_data = {
                            'ticker': ticker,
                            'date': date.strftime('%Y-%m-%d'),
                            'gain_pct': round(daily_return, 2),
                            'close_price': round(hist['Close'].iloc[i], 2),
                            'volume': int(move_day_vol),
                            'vol_ratio': round(vol_ratio, 1),
                            'pre_move_5d_change': round(pre_move_change, 2),
                            'unusual_vol_days_before': unusual_vol_days,
                            'sector': self._get_sector(ticker)
                        }
                        
                        big_moves.append(move_data)
                        
            except Exception as e:
                continue
        
        # Sort by date (most recent first)
        big_moves.sort(key=lambda x: x['date'], reverse=True)
        
        return big_moves
    
    def analyze_repeat_runners(self, moves):
        """
        Find stocks that made multiple big moves (momentum names)
        These are the ones to watch most closely
        """
        print("\n🔄 REPEAT RUNNERS (Multiple 10%+ Days)")
        print("=" * 70)
        
        # Count moves per ticker
        move_counts = defaultdict(list)
        for move in moves:
            move_counts[move['ticker']].append(move)
        
        # Filter for repeat runners (2+ moves)
        repeat_runners = {k: v for k, v in move_counts.items() if len(v) >= 2}
        
        # Sort by number of moves
        sorted_runners = sorted(repeat_runners.items(), key=lambda x: len(x[1]), reverse=True)
        
        for ticker, ticker_moves in sorted_runners:
            print(f"\n🔥 {ticker} - {len(ticker_moves)} BIG MOVES")
            print(f"   Sector: {self._get_sector(ticker)}")
            for m in ticker_moves:
                print(f"   {m['date']}: +{m['gain_pct']}% (Vol: {m['vol_ratio']}x avg)")
        
        return sorted_runners
    
    def analyze_sector_rotation(self, moves):
        """
        Which sectors are hot? Where are the moves clustering?
        """
        print("\n📊 SECTOR ROTATION ANALYSIS")
        print("=" * 70)
        
        sector_moves = defaultdict(list)
        
        for move in moves:
            sector = move['sector']
            sector_moves[sector].append(move)
        
        # Sort sectors by number of moves
        sorted_sectors = sorted(sector_moves.items(), key=lambda x: len(x[1]), reverse=True)
        
        for sector, sector_move_list in sorted_sectors:
            total_moves = len(sector_move_list)
            avg_gain = sum(m['gain_pct'] for m in sector_move_list) / total_moves
            recent_moves = [m for m in sector_move_list if (datetime.now() - datetime.strptime(m['date'], '%Y-%m-%d')).days <= 7]
            
            print(f"\n{'🔥' if len(recent_moves) > 0 else '📈'} {sector}: {total_moves} big moves")
            print(f"   Average gain: +{avg_gain:.1f}%")
            print(f"   Recent (7d): {len(recent_moves)} moves")
            
            if recent_moves:
                print(f"   HOT NOW:")
                for m in recent_moves[:3]:
                    print(f"      {m['ticker']}: +{m['gain_pct']}% on {m['date']}")
        
        return sorted_sectors
    
    def find_pre_move_patterns(self, moves):
        """
        What happens BEFORE big moves? Find the setup pattern.
        """
        print("\n🎯 PRE-MOVE PATTERN ANALYSIS")
        print("=" * 70)
        
        # Categorize moves by what happened before
        patterns = {
            'volume_accumulation': [],  # Unusual volume 1-3 days before
            'quiet_breakout': [],       # Low volume, then explosion
            'momentum_continuation': [], # Already up, continued higher
            'reversal': []              # Was down, then reversed
        }
        
        for move in moves:
            if move['unusual_vol_days_before'] >= 2:
                patterns['volume_accumulation'].append(move)
            elif move['unusual_vol_days_before'] == 0 and move['vol_ratio'] > 3:
                patterns['quiet_breakout'].append(move)
            elif move['pre_move_5d_change'] > 5:
                patterns['momentum_continuation'].append(move)
            elif move['pre_move_5d_change'] < -5:
                patterns['reversal'].append(move)
        
        print("\n📌 PATTERN BREAKDOWN:")
        print(f"\n1. VOLUME ACCUMULATION (unusual volume before move): {len(patterns['volume_accumulation'])}")
        print("   These give you WARNING - volume spikes 1-3 days before")
        for m in patterns['volume_accumulation'][:5]:
            print(f"   • {m['ticker']}: +{m['gain_pct']}% on {m['date']} ({m['unusual_vol_days_before']} unusual vol days before)")
        
        print(f"\n2. QUIET BREAKOUTS (low volume, then explosion): {len(patterns['quiet_breakout'])}")
        print("   These are HARD to catch - need catalyst monitoring")
        for m in patterns['quiet_breakout'][:5]:
            print(f"   • {m['ticker']}: +{m['gain_pct']}% on {m['date']} (Vol {m['vol_ratio']}x vs quiet before)")
        
        print(f"\n3. MOMENTUM CONTINUATION (already running): {len(patterns['momentum_continuation'])}")
        print("   These you catch by STAYING IN winners")
        for m in patterns['momentum_continuation'][:5]:
            print(f"   • {m['ticker']}: +{m['gain_pct']}% on {m['date']} (was already +{m['pre_move_5d_change']:.1f}% 5d prior)")
        
        print(f"\n4. REVERSALS (was down, then popped): {len(patterns['reversal'])}")
        print("   These need CATALYST - often news-driven")
        for m in patterns['reversal'][:5]:
            print(f"   • {m['ticker']}: +{m['gain_pct']}% on {m['date']} (was {m['pre_move_5d_change']:.1f}% 5d prior)")
        
        return patterns
    
    def generate_action_plan(self, moves, repeat_runners, sector_data, patterns):
        """
        Based on analysis, what should we DO?
        """
        print("\n" + "=" * 70)
        print("🎯 ACTION PLAN - HOW TO CATCH THE NEXT ONE")
        print("=" * 70)
        
        # 1. Repeat runners to watch
        print("\n📌 1. REPEAT RUNNERS - ADD TO DAILY WATCH")
        print("   These stocks move BIG repeatedly - prioritize them:")
        for ticker, ticker_moves in repeat_runners[:5]:
            print(f"   ⭐ {ticker} ({len(ticker_moves)} moves) - {self._get_sector(ticker)}")
        
        # 2. Hot sectors right now
        print("\n📌 2. HOT SECTORS - WHERE MONEY IS FLOWING")
        recent_sectors = []
        for sector, sector_moves in sector_data[:3]:
            recent = [m for m in sector_moves if (datetime.now() - datetime.strptime(m['date'], '%Y-%m-%d')).days <= 7]
            if recent:
                recent_sectors.append((sector, recent))
                print(f"   🔥 {sector}: {len(recent)} moves this week")
        
        # 3. Pre-move signals to watch
        print("\n📌 3. SIGNALS THAT PREDICT MOVES")
        vol_accum_pct = len(patterns['volume_accumulation']) / len(moves) * 100 if moves else 0
        print(f"   • {vol_accum_pct:.0f}% of moves had unusual volume 1-3 days BEFORE")
        print("   → SCAN FOR: Volume > 1.5x average on watchlist stocks")
        
        # 4. Specific tickers to watch NOW
        print("\n📌 4. SPECIFIC TICKERS FOR MONDAY")
        
        # Recent movers that might continue
        last_7d = [m for m in moves if (datetime.now() - datetime.strptime(m['date'], '%Y-%m-%d')).days <= 7]
        if last_7d:
            print("   Recent movers (momentum continuation plays):")
            for m in last_7d[:5]:
                print(f"   → {m['ticker']}: +{m['gain_pct']}% on {m['date']}")
        
        # Repeat runners that haven't moved recently
        print("\n   Repeat runners due for next move:")
        for ticker, ticker_moves in repeat_runners[:10]:
            last_move = ticker_moves[0]
            days_since = (datetime.now() - datetime.strptime(last_move['date'], '%Y-%m-%d')).days
            if days_since > 7:
                print(f"   → {ticker}: Last move {days_since}d ago (+{last_move['gain_pct']}%)")
    
    def _get_sector(self, ticker):
        """Get sector for a ticker"""
        for sector, tickers in self.SECTORS.items():
            if ticker in tickers:
                return sector
        return 'Other'
    
    def run_full_analysis(self, days_back=30):
        """Run complete analysis"""
        print("\n" + "🐺" * 35)
        print("   WOLF PACK - MISSED GAINS ANALYSIS")
        print("🐺" * 35)
        
        # 1. Find big moves
        moves = self.find_big_moves(days_back=days_back, min_gain=10.0)
        
        if not moves:
            print("\n⚠️ No big moves found in the period")
            return
        
        print(f"\n📊 Found {len(moves)} moves of 10%+ in last {days_back} days")
        
        # Show recent moves
        print("\n📈 MOST RECENT BIG MOVES:")
        for m in moves[:10]:
            print(f"   {m['date']}: {m['ticker']} +{m['gain_pct']}% (Vol: {m['vol_ratio']}x)")
        
        # 2. Find repeat runners
        repeat_runners = self.analyze_repeat_runners(moves)
        
        # 3. Sector rotation
        sector_data = self.analyze_sector_rotation(moves)
        
        # 4. Pre-move patterns
        patterns = self.find_pre_move_patterns(moves)
        
        # 5. Action plan
        self.generate_action_plan(moves, repeat_runners, sector_data, patterns)
        
        # Save analysis
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(self.data_dir / f'missed_gains_{timestamp}.json', 'w') as f:
            json.dump({
                'moves': moves,
                'repeat_runners': [(k, len(v)) for k, v in repeat_runners],
                'analysis_date': timestamp
            }, f, indent=2)
        
        print(f"\n💾 Saved: logs/analysis/missed_gains_{timestamp}.json")
        
        return moves, repeat_runners, sector_data, patterns


def main():
    import sys
    
    analyzer = MissedGainsAnalyzer()
    
    days = 30
    if len(sys.argv) > 1:
        days = int(sys.argv[1])
    
    analyzer.run_full_analysis(days_back=days)


if __name__ == '__main__':
    main()
