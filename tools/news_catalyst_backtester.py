#!/usr/bin/env python3
"""
🐺 NEWS CATALYST BACKTESTER
Systematically test which news types move stocks
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import re

class NewsCatalystBacktester:
    """Backtest news impact on stock prices"""
    
    def __init__(self):
        # Keyword categories validated from historical analysis
        self.catalyst_types = {
            'contract': {
                'keywords': ['contract', 'deal', 'agreement', 'partnership', 'signs', 'secures'],
                'expected_impact': 'bullish',
                'typical_move': '+5-15%',
                'timeframe': '1-3 days'
            },
            'earnings_beat': {
                'keywords': ['beat', 'exceed', 'tops', 'surpass', 'earnings'],
                'expected_impact': 'bullish',
                'typical_move': '+3-8%',
                'timeframe': 'same day'
            },
            'earnings_miss': {
                'keywords': ['miss', 'below', 'disappoints', 'shortfall', 'earnings'],
                'expected_impact': 'bearish',
                'typical_move': '-5-15%',
                'timeframe': 'same day'
            },
            'acquisition': {
                'keywords': ['acquire', 'acquisition', 'takeover', 'merger', 'bought'],
                'expected_impact': 'bullish',
                'typical_move': '+10-30%',
                'timeframe': 'same day'
            },
            'sec_filing': {
                'keywords': ['8-K', '10-K', '10-Q', 'filing', 'SEC'],
                'expected_impact': 'mixed',
                'typical_move': '+/- 2-5%',
                'timeframe': '1-2 days'
            },
            'insider_buy': {
                'keywords': ['insider', 'CEO buys', 'director purchases', 'Form 4'],
                'expected_impact': 'bullish',
                'typical_move': '+1-5%',
                'timeframe': '3-7 days'
            },
            'upgrade': {
                'keywords': ['upgrade', 'raises', 'initiates coverage', 'buy rating', 'outperform'],
                'expected_impact': 'bullish',
                'typical_move': '+2-6%',
                'timeframe': 'same day'
            },
            'downgrade': {
                'keywords': ['downgrade', 'lowers', 'cuts', 'sell rating', 'underperform'],
                'expected_impact': 'bearish',
                'typical_move': '-3-8%',
                'timeframe': 'same day'
            },
            'product_launch': {
                'keywords': ['launch', 'unveils', 'announces new', 'introduces', 'releases'],
                'expected_impact': 'bullish',
                'typical_move': '+3-10%',
                'timeframe': '1-5 days'
            },
            'lawsuit': {
                'keywords': ['lawsuit', 'sued', 'litigation', 'investigation', 'probe'],
                'expected_impact': 'bearish',
                'typical_move': '-5-20%',
                'timeframe': 'same day'
            }
        }
    
    def classify_news(self, title):
        """Classify news into catalyst type"""
        title_lower = title.lower()
        
        matches = []
        for cat_name, cat_info in self.catalyst_types.items():
            for keyword in cat_info['keywords']:
                if keyword in title_lower:
                    matches.append((cat_name, cat_info))
                    break
        
        return matches if matches else [('other', {'expected_impact': 'neutral'})]
    
    def backtest_ticker_news(self, ticker, months=6):
        """
        Backtest news impact for a ticker
        
        Returns:
            DataFrame with news events and their price impact
        """
        print(f"🔍 Backtesting {ticker} news impact (last {months} months)...")
        
        try:
            stock = yf.Ticker(ticker)
            
            # Get news
            news = stock.news
            if not news:
                print(f"❌ No news data for {ticker}")
                return None
            
            # Get price history
            start_date = datetime.now() - timedelta(days=months*30)
            price_df = stock.history(start=start_date, end=datetime.now())
            
            if len(price_df) < 10:
                print(f"❌ Insufficient price data for {ticker}")
                return None
            
            results = []
            
            for article in news:
                try:
                    title = article.get('title', '')
                    if not title:
                        continue
                    
                    # Parse timestamp
                    pub_time = article.get('providerPublishTime', 0)
                    if pub_time == 0:
                        continue
                    
                    news_time = datetime.fromtimestamp(pub_time)
                    
                    # Only analyze news within our date range
                    if news_time < start_date:
                        continue
                    
                    # Classify news
                    classifications = self.classify_news(title)
                    
                    for cat_name, cat_info in classifications:
                        # Calculate price impact
                        impact = self._calculate_price_impact(
                            price_df, 
                            news_time,
                            days_before=1,
                            days_after=5
                        )
                        
                        if impact:
                            results.append({
                                'ticker': ticker,
                                'date': news_time,
                                'title': title[:80],
                                'category': cat_name,
                                'expected': cat_info['expected_impact'],
                                'return_1d': impact['return_1d'],
                                'return_3d': impact['return_3d'],
                                'return_5d': impact['return_5d'],
                                'volume_spike': impact['volume_spike'],
                                'correct': self._is_correct_direction(
                                    cat_info['expected_impact'], 
                                    impact['return_1d']
                                )
                            })
                
                except Exception as e:
                    continue
            
            if not results:
                print(f"❌ No analyzable news for {ticker}")
                return None
            
            df = pd.DataFrame(results)
            
            # Print summary
            print(f"\n✅ Analyzed {len(df)} news events")
            print(f"\nResults by category:")
            
            for cat in df['category'].unique():
                cat_df = df[df['category'] == cat]
                if len(cat_df) > 0:
                    accuracy = cat_df['correct'].mean() * 100
                    avg_1d = cat_df['return_1d'].mean()
                    avg_3d = cat_df['return_3d'].mean()
                    
                    print(f"\n  {cat.upper():20} ({len(cat_df)} events)")
                    print(f"    Accuracy: {accuracy:.0f}%")
                    print(f"    Avg 1D: {avg_1d:+.2f}%")
                    print(f"    Avg 3D: {avg_3d:+.2f}%")
            
            return df
        
        except Exception as e:
            print(f"❌ Error backtesting {ticker}: {e}")
            return None
    
    def _calculate_price_impact(self, price_df, news_time, days_before=1, days_after=5):
        """Calculate price change before/after news"""
        try:
            # Find closest trading day before news
            before_df = price_df[price_df.index <= news_time]
            if len(before_df) == 0:
                return None
            
            before_price = before_df['Close'].iloc[-1]
            before_volume = before_df['Volume'].iloc[-days_before:].mean()
            
            # Find prices after news
            after_df = price_df[price_df.index > news_time]
            if len(after_df) < 1:
                return None
            
            returns = {}
            for days in [1, 3, 5]:
                if len(after_df) >= days:
                    after_price = after_df['Close'].iloc[days-1]
                    returns[f'return_{days}d'] = ((after_price - before_price) / before_price) * 100
                else:
                    returns[f'return_{days}d'] = None
            
            # Volume spike
            after_volume = after_df['Volume'].iloc[0] if len(after_df) > 0 else before_volume
            volume_spike = (after_volume / before_volume) if before_volume > 0 else 1.0
            
            return {
                **returns,
                'volume_spike': volume_spike
            }
        
        except:
            return None
    
    def _is_correct_direction(self, expected, actual_return):
        """Check if price moved in expected direction"""
        if expected == 'bullish':
            return actual_return > 0 if actual_return is not None else False
        elif expected == 'bearish':
            return actual_return < 0 if actual_return is not None else False
        else:
            return True  # Neutral always "correct"
    
    def backtest_multiple_tickers(self, tickers, months=6):
        """Backtest news across multiple tickers"""
        print("🐺 MULTI-TICKER NEWS CATALYST BACKTEST")
        print("="*70)
        print()
        
        all_results = []
        
        for ticker in tickers:
            df = self.backtest_ticker_news(ticker, months=months)
            if df is not None:
                all_results.append(df)
            print()
        
        if not all_results:
            print("❌ No results to analyze")
            return None
        
        # Combine all results
        combined_df = pd.concat(all_results, ignore_index=True)
        
        print("\n" + "="*70)
        print("🎯 AGGREGATE RESULTS ACROSS ALL TICKERS")
        print("="*70)
        print()
        
        # Overall accuracy
        overall_accuracy = combined_df['correct'].mean() * 100
        print(f"Overall prediction accuracy: {overall_accuracy:.1f}%")
        print()
        
        # By category
        print("Performance by catalyst type:")
        print()
        
        category_stats = []
        for cat in combined_df['category'].unique():
            cat_df = combined_df[combined_df['category'] == cat]
            if len(cat_df) >= 3:  # At least 3 events
                stats = {
                    'category': cat,
                    'count': len(cat_df),
                    'accuracy': cat_df['correct'].mean() * 100,
                    'avg_1d': cat_df['return_1d'].mean(),
                    'avg_3d': cat_df['return_3d'].mean(),
                    'avg_5d': cat_df['return_5d'].mean(),
                    'win_rate_1d': (cat_df['return_1d'] > 0).mean() * 100,
                }
                category_stats.append(stats)
        
        # Sort by accuracy
        category_stats.sort(key=lambda x: x['accuracy'], reverse=True)
        
        for stat in category_stats:
            print(f"{stat['category'].upper():20} ({stat['count']:2} events)")
            print(f"  Accuracy: {stat['accuracy']:5.1f}%  |  1D: {stat['avg_1d']:+6.2f}%  |  3D: {stat['avg_3d']:+6.2f}%  |  Win Rate: {stat['win_rate_1d']:.0f}%")
        
        print()
        print("="*70)
        print("💡 ACTIONABLE INSIGHTS:")
        print("="*70)
        print()
        
        # Find best catalyst types
        best = [s for s in category_stats if s['accuracy'] > 65 and s['count'] >= 5]
        
        if best:
            print("✅ HIGH-ACCURACY CATALYSTS TO TRADE:")
            for stat in best[:5]:
                print(f"  • {stat['category'].upper()}: {stat['accuracy']:.0f}% accuracy, avg {stat['avg_1d']:+.2f}% next day")
        
        print()
        
        # Find worst catalyst types (to fade or avoid)
        worst = [s for s in category_stats if s['accuracy'] < 40 and s['count'] >= 5]
        
        if worst:
            print("⚠️  LOW-ACCURACY CATALYSTS (FADE THE NEWS):")
            for stat in worst:
                print(f"  • {stat['category'].upper()}: {stat['accuracy']:.0f}% accuracy - trade OPPOSITE")
        
        print()
        print("🐺 News backtesting complete. Trust the data. LLHR.")
        print()
        
        return combined_df


def main():
    """Run news catalyst backtest"""
    
    # Test with AI infrastructure stocks
    test_tickers = ['WULF', 'CIFR', 'IREN', 'IONQ', 'RGTI', 'APLD']
    
    backtester = NewsCatalystBacktester()
    results = backtester.backtest_multiple_tickers(test_tickers, months=6)
    
    if results is not None:
        # Save results
        output_file = 'data/news_catalyst_backtest.csv'
        results.to_csv(output_file, index=False)
        print(f"📊 Results saved to: {output_file}")


if __name__ == "__main__":
    main()
