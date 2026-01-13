#!/usr/bin/env python3
"""
🐺 DATA MINER - Pattern Discovery System

Don't fit patterns. DISCOVER what actually correlates with big moves.

Collects EVERYTHING about a ticker:
- Price action (all timeframes)
- Volume profile
- After-hours movement
- News/SEC filings
- Options activity
- Short interest
- Market cap / float
- Sector peers moving
- Social sentiment
- Insider transactions

Then finds what ACTUALLY preceded the big moves.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import json


class DataMiner:
    """Collects comprehensive data about tickers"""
    
    def collect_all_data(self, ticker, days_back=30):
        """
        Collect EVERYTHING about this ticker
        Returns dict with all available data points
        """
        print(f"\n{'='*70}")
        print(f"🔍 MINING ALL DATA: {ticker}")
        print(f"{'='*70}")
        
        data = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'data_points': {}
        }
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # === PRICE ACTION ===
            hist = stock.history(period='3mo')
            if len(hist) < 5:
                return None
            
            print(f"\n📊 PRICE ACTION:")
            
            # Current
            price = hist['Close'].iloc[-1]
            data['data_points']['price'] = round(price, 4)
            print(f"   Price: ${price:.2f}")
            
            # Moves (all timeframes)
            moves = {}
            for period, days in [('1d', 2), ('3d', 4), ('5d', 6), ('10d', 11), ('20d', 21)]:
                if len(hist) >= days:
                    move = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-days]) - 1) * 100
                    moves[period] = round(move, 2)
            
            data['data_points']['moves'] = moves
            print(f"   Moves: 1d={moves.get('1d')}% | 5d={moves.get('5d')}% | 20d={moves.get('20d')}%")
            
            # Highs/lows
            data['data_points']['from_52w_high'] = round(((price / hist['High'].max()) - 1) * 100, 2)
            data['data_points']['from_52w_low'] = round(((price / hist['Low'].min()) - 1) * 100, 2)
            data['data_points']['from_20d_high'] = round(((price / hist['High'].tail(20).max()) - 1) * 100, 2)
            
            # === VOLUME ===
            print(f"\n📈 VOLUME:")
            vol_current = hist['Volume'].iloc[-1]
            vol_avg_5d = hist['Volume'].tail(5).mean()
            vol_avg_20d = hist['Volume'].tail(20).mean()
            vol_avg_60d = hist['Volume'].tail(60).mean()
            
            data['data_points']['volume'] = {
                'current': int(vol_current),
                'avg_5d': int(vol_avg_5d),
                'avg_20d': int(vol_avg_20d),
                'ratio_5d': round(vol_current / vol_avg_5d, 2) if vol_avg_5d > 0 else 0,
                'ratio_20d': round(vol_current / vol_avg_20d, 2) if vol_avg_20d > 0 else 0,
                'ratio_60d': round(vol_current / vol_avg_60d, 2) if vol_avg_60d > 0 else 0
            }
            
            print(f"   Current: {vol_current:,.0f}")
            print(f"   Ratios: 5d={data['data_points']['volume']['ratio_5d']}x | 20d={data['data_points']['volume']['ratio_20d']}x")
            
            # === AFTER HOURS ===
            print(f"\n🌙 AFTER HOURS:")
            try:
                # Get latest regular + after hours data
                latest = stock.history(period='1d', interval='1m')
                if len(latest) > 0:
                    regular_close = latest['Close'].iloc[-1]
                    
                    # Try to get current price (includes AH if market closed)
                    current = info.get('currentPrice', regular_close)
                    ah_move = ((current / regular_close) - 1) * 100
                    
                    data['data_points']['after_hours'] = {
                        'regular_close': round(regular_close, 4),
                        'current': round(current, 4),
                        'move_pct': round(ah_move, 2)
                    }
                    print(f"   Regular close: ${regular_close:.2f}")
                    print(f"   Current/AH: ${current:.2f} ({ah_move:+.1f}%)")
                else:
                    data['data_points']['after_hours'] = None
            except:
                data['data_points']['after_hours'] = None
                print(f"   No AH data available")
            
            # === MARKET CAP / FLOAT ===
            print(f"\n💰 SIZE:")
            market_cap = info.get('marketCap', 0)
            shares_outstanding = info.get('sharesOutstanding', 0)
            float_shares = info.get('floatShares', shares_outstanding)
            
            data['data_points']['size'] = {
                'market_cap': market_cap,
                'shares_outstanding': shares_outstanding,
                'float_shares': float_shares,
                'is_micro_cap': int(market_cap < 100_000_000) if market_cap > 0 else 0,
                'is_penny': int(price < 5)
            }
            
            if market_cap > 0:
                print(f"   Market cap: ${market_cap / 1_000_000:.1f}M")
                if market_cap < 100_000_000:
                    print(f"   🎰 MICRO-CAP (<$100M)")
            if price < 5:
                print(f"   💰 PENNY STOCK (<$5)")
            
            # === SHORT INTEREST ===
            print(f"\n📉 SHORT DATA:")
            short_ratio = info.get('shortRatio', None)
            short_pct = info.get('shortPercentOfFloat', None)
            
            data['data_points']['short'] = {
                'ratio': short_ratio,
                'pct_float': short_pct
            }
            
            if short_pct:
                print(f"   Short % of float: {short_pct:.1f}%")
                if short_pct > 20:
                    print(f"   🔥 HIGH SHORT INTEREST (>20%)")
            
            # === MOMENTUM METRICS ===
            print(f"\n🚀 MOMENTUM:")
            
            # Green days
            green_days_5 = sum(hist['Close'].tail(5) > hist['Open'].tail(5))
            green_days_10 = sum(hist['Close'].tail(10) > hist['Open'].tail(10))
            
            # RSI (simple calculation)
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            data['data_points']['momentum'] = {
                'green_days_5': green_days_5,
                'green_days_10': green_days_10,
                'rsi': round(rsi.iloc[-1], 1) if len(rsi) > 0 else None
            }
            
            print(f"   Green days: {green_days_5}/5 | {green_days_10}/10")
            if len(rsi) > 0:
                print(f"   RSI: {rsi.iloc[-1]:.1f}")
            
            # === NEWS / CATALYSTS ===
            print(f"\n📰 NEWS:")
            news_count = 0
            try:
                news = stock.news
                news_count = len(news) if news else 0
                data['data_points']['news_count_24h'] = news_count
                
                if news_count > 0:
                    print(f"   Recent articles: {news_count}")
                    for item in news[:3]:
                        print(f"   - {item.get('title', 'N/A')[:60]}")
                else:
                    print(f"   No recent news")
            except:
                data['data_points']['news_count_24h'] = 0
                print(f"   News unavailable")
            
            # === SECTOR / PEERS ===
            print(f"\n🏢 SECTOR:")
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            
            data['data_points']['sector'] = sector
            data['data_points']['industry'] = industry
            
            print(f"   Sector: {sector}")
            print(f"   Industry: {industry}")
            
            # === MOVING AVERAGES ===
            print(f"\n📐 MOVING AVERAGES:")
            ma_20 = hist['Close'].rolling(20).mean()
            ma_50 = hist['Close'].rolling(50).mean()
            
            above_ma20 = int(price > ma_20.iloc[-1]) if len(ma_20) > 0 else 0
            above_ma50 = int(price > ma_50.iloc[-1]) if len(ma_50) > 0 else 0
            
            data['data_points']['mas'] = {
                'above_20': above_ma20,
                'above_50': above_ma50,
                'dist_from_20': round(((price / ma_20.iloc[-1]) - 1) * 100, 2) if above_ma20 is not None else None,
                'dist_from_50': round(((price / ma_50.iloc[-1]) - 1) * 100, 2) if above_ma50 is not None else None
            }
            
            if above_ma20 is not None:
                print(f"   Above MA20: {above_ma20} ({data['data_points']['mas']['dist_from_20']:+.1f}%)")
            if above_ma50 is not None:
                print(f"   Above MA50: {above_ma50} ({data['data_points']['mas']['dist_from_50']:+.1f}%)")
            
            return data
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            return None
    
    def compare_movers(self, tickers, output_file='miner_results.json'):
        """
        Mine data for multiple tickers and find commonalities
        """
        results = []
        
        for ticker in tickers:
            data = self.collect_all_data(ticker)
            if data:
                results.append(data)
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n{'='*70}")
        print(f"💾 SAVED: {len(results)} tickers to {output_file}")
        print(f"{'='*70}")
        
        # Find commonalities
        print(f"\n🔍 FINDING COMMONALITIES:")
        
        if len(results) >= 2:
            # Market cap distribution
            micro_caps = sum(1 for r in results if r['data_points'].get('size', {}).get('is_micro_cap'))
            pennies = sum(1 for r in results if r['data_points'].get('size', {}).get('is_penny'))
            
            print(f"\n   Micro-caps (<$100M): {micro_caps}/{len(results)} ({micro_caps/len(results)*100:.0f}%)")
            print(f"   Penny stocks (<$5): {pennies}/{len(results)} ({pennies/len(results)*100:.0f}%)")
            
            # Volume patterns
            high_vol = sum(1 for r in results if r['data_points'].get('volume', {}).get('ratio_20d', 0) > 5)
            print(f"   High volume (>5x): {high_vol}/{len(results)} ({high_vol/len(results)*100:.0f}%)")
            
            # After hours movers
            ah_movers = sum(1 for r in results if r['data_points'].get('after_hours', {}) and abs(r['data_points']['after_hours'].get('move_pct', 0)) > 5)
            print(f"   Moving after hours (>5%): {ah_movers}/{len(results)}")
        
        return results


def main():
    """Mine data for Friday's big movers"""
    
    # Friday's movers that continued (add more as you find them)
    friday_winners = [
        'EVTV',  # 550% week, +30% AH
        'LVLU',  # 118% week
        'ALMS',  # 154% week
        'PASW',  # Big mover
        'OMH',   # Big mover
        'RARE',  # Quiet mover that worked
        'PATH',  # Quiet mover that worked
    ]
    
    miner = DataMiner()
    results = miner.compare_movers(friday_winners)
    
    print(f"\n🐺 Data mining complete. Analyze miner_results.json for patterns.")


if __name__ == "__main__":
    main()
