#!/usr/bin/env python3
"""
🐺 REPEAT RUNNER DATASET BUILDER 🐺

THE GOAL: Build a labeled dataset of WHAT HAPPENS BEFORE big moves.

For every 10%+ move we find, we collect:
- 5 days of price/volume BEFORE the move
- Technical indicators (RSI, MACD, Bollinger)
- Volume patterns
- Price patterns (consolidation, dip, etc.)
- Market context (SPY, VIX)
- Time features (day of week, time of month)
- Sector context (is the sector hot?)

Then we can train a model: Given these features, will this stock run 10%+ soon?

Usage:
    python runner_dataset_builder.py build           # Build full dataset
    python runner_dataset_builder.py analyze         # Quick analysis of patterns
    python runner_dataset_builder.py export          # Export to CSV for Colab

Author: Brokkr (preparing the training data)
Date: January 3, 2026
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import sys
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class RunnerDatasetBuilder:
    """
    Build a machine learning dataset from repeat runner history
    """
    
    # Stocks to analyze - proven repeat runners
    REPEAT_RUNNERS = [
        'SIDU', 'RCAT', 'LUNR', 'ASTS', 'RDW', 'CLSK',
        'IONQ', 'RGTI', 'QBTS', 'QUBT', 'SMR', 'OKLO',
        'RKLB', 'BKSY', 'AISP', 'ARQQ', 'OPTT', 'ACHR',
        'JOBY', 'LILM', 'RIVN', 'LCID', 'NIO', 'MARA',
        'RIOT', 'BTBT', 'BITF', 'HUT', 'CIFR'
    ]
    
    # Sector ETFs for context
    SECTOR_ETFS = {
        'market': 'SPY',
        'volatility': '^VIX',
        'tech': 'QQQ',
        'small_cap': 'IWM',
        'crypto': 'BITO'
    }
    
    # Minimum gain to be considered a "big move"
    MIN_GAIN_PCT = 10.0
    
    # Days of features to collect before each move
    LOOKBACK_DAYS = 10
    
    def __init__(self):
        self.data_dir = Path('data/ml')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.dataset = []
        
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD and signal line"""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd, signal
    
    def _calculate_bollinger(self, prices: pd.Series, period: int = 20) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        return upper, sma, lower
    
    def _get_price_position(self, price: float, high: float, low: float) -> float:
        """Where is price in its range? 0 = at low, 1 = at high"""
        if high == low:
            return 0.5
        return (price - low) / (high - low)
    
    def find_big_moves(self, ticker: str, period: str = '6mo') -> List[Dict]:
        """
        Find all 10%+ moves for a ticker
        Returns list of dates and gains
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if len(hist) < 20:
                return []
            
            moves = []
            
            for i in range(1, len(hist)):
                prev_close = hist['Close'].iloc[i-1]
                high = hist['High'].iloc[i]
                close = hist['Close'].iloc[i]
                
                # Check for 10%+ intraday move
                intraday_gain = ((high - prev_close) / prev_close) * 100
                close_gain = ((close - prev_close) / prev_close) * 100
                
                if intraday_gain >= self.MIN_GAIN_PCT:
                    moves.append({
                        'date': hist.index[i],
                        'prev_close': prev_close,
                        'high': high,
                        'close': close,
                        'intraday_gain': intraday_gain,
                        'close_gain': close_gain,
                        'volume': hist['Volume'].iloc[i],
                        'index': i
                    })
            
            return moves
            
        except Exception as e:
            print(f"   Error finding moves for {ticker}: {e}")
            return []
    
    def extract_features(self, ticker: str, move_date: datetime, hist: pd.DataFrame) -> Dict:
        """
        Extract ML features from the days BEFORE a big move
        """
        try:
            # Find the index of the move date
            move_idx = hist.index.get_loc(move_date)
            
            # Need enough history
            if move_idx < self.LOOKBACK_DAYS + 20:  # Extra for indicators
                return None
            
            # Get lookback period
            lookback_start = move_idx - self.LOOKBACK_DAYS
            lookback_data = hist.iloc[lookback_start:move_idx]
            
            # Current day data (day before the move)
            day_before = hist.iloc[move_idx - 1]
            
            features = {}
            
            # ============ PRICE FEATURES ============
            features['price'] = day_before['Close']
            features['price_change_1d'] = ((day_before['Close'] - hist.iloc[move_idx-2]['Close']) / 
                                           hist.iloc[move_idx-2]['Close']) * 100
            features['price_change_5d'] = ((day_before['Close'] - hist.iloc[move_idx-6]['Close']) / 
                                           hist.iloc[move_idx-6]['Close']) * 100
            features['price_change_10d'] = ((day_before['Close'] - hist.iloc[move_idx-11]['Close']) / 
                                            hist.iloc[move_idx-11]['Close']) * 100
            
            # Distance from highs/lows
            high_10d = lookback_data['High'].max()
            low_10d = lookback_data['Low'].min()
            features['dist_from_10d_high'] = ((day_before['Close'] - high_10d) / high_10d) * 100
            features['dist_from_10d_low'] = ((day_before['Close'] - low_10d) / low_10d) * 100
            features['price_position_10d'] = self._get_price_position(day_before['Close'], high_10d, low_10d)
            
            # ============ VOLUME FEATURES ============
            avg_volume_10d = lookback_data['Volume'].mean()
            avg_volume_5d = lookback_data['Volume'].tail(5).mean()
            features['volume_ratio_1d'] = day_before['Volume'] / avg_volume_10d if avg_volume_10d > 0 else 1
            features['volume_ratio_5d'] = avg_volume_5d / avg_volume_10d if avg_volume_10d > 0 else 1
            features['volume_trend'] = (lookback_data['Volume'].tail(3).mean() / 
                                       lookback_data['Volume'].head(3).mean()) if lookback_data['Volume'].head(3).mean() > 0 else 1
            
            # Volume spike detection (any day in lookback with 2x+ volume)
            features['had_volume_spike'] = int(any(lookback_data['Volume'] > avg_volume_10d * 2))
            
            # ============ TECHNICAL INDICATORS ============
            # Need more history for indicators
            indicator_data = hist.iloc[move_idx-30:move_idx]
            
            # RSI
            rsi = self._calculate_rsi(indicator_data['Close'])
            features['rsi'] = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            features['rsi_oversold'] = int(features['rsi'] < 30)
            features['rsi_overbought'] = int(features['rsi'] > 70)
            
            # MACD
            macd, signal = self._calculate_macd(indicator_data['Close'])
            features['macd'] = macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0
            features['macd_signal'] = signal.iloc[-1] if not pd.isna(signal.iloc[-1]) else 0
            features['macd_histogram'] = features['macd'] - features['macd_signal']
            features['macd_bullish_cross'] = int(macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2])
            
            # Bollinger Bands
            upper, middle, lower = self._calculate_bollinger(indicator_data['Close'])
            features['bb_position'] = ((day_before['Close'] - lower.iloc[-1]) / 
                                       (upper.iloc[-1] - lower.iloc[-1])) if (upper.iloc[-1] - lower.iloc[-1]) > 0 else 0.5
            features['below_lower_bb'] = int(day_before['Close'] < lower.iloc[-1])
            features['above_upper_bb'] = int(day_before['Close'] > upper.iloc[-1])
            
            # ============ PATTERN FEATURES ============
            # Consolidation (low volatility before move)
            features['volatility_10d'] = lookback_data['Close'].pct_change().std() * 100
            features['consolidation'] = int(features['volatility_10d'] < 3)  # Less than 3% daily moves
            
            # Gap detection (did it gap recently?)
            gaps = []
            for i in range(1, len(lookback_data)):
                gap = ((lookback_data['Open'].iloc[i] - lookback_data['Close'].iloc[i-1]) / 
                       lookback_data['Close'].iloc[i-1]) * 100
                gaps.append(gap)
            features['max_gap_10d'] = max(gaps) if gaps else 0
            features['had_gap_up'] = int(any(g > 3 for g in gaps))
            features['had_gap_down'] = int(any(g < -3 for g in gaps))
            
            # Red days before (wounded wolf setup)
            red_days = sum(1 for i in range(len(lookback_data)) 
                          if lookback_data['Close'].iloc[i] < lookback_data['Open'].iloc[i])
            features['red_days_10d'] = red_days
            features['consecutive_red'] = 0
            for i in range(len(lookback_data)-1, -1, -1):
                if lookback_data['Close'].iloc[i] < lookback_data['Open'].iloc[i]:
                    features['consecutive_red'] += 1
                else:
                    break
            
            # ============ TIME FEATURES ============
            features['day_of_week'] = move_date.dayofweek  # 0=Monday
            features['is_monday'] = int(move_date.dayofweek == 0)
            features['is_friday'] = int(move_date.dayofweek == 4)
            features['day_of_month'] = move_date.day
            features['is_month_start'] = int(move_date.day <= 5)
            features['is_month_end'] = int(move_date.day >= 25)
            
            return features
            
        except Exception as e:
            print(f"   Error extracting features: {e}")
            return None
    
    def add_market_context(self, features: Dict, move_date: datetime) -> Dict:
        """Add market-wide context features"""
        try:
            # Get SPY data
            spy = yf.Ticker('SPY')
            spy_hist = spy.history(start=move_date - timedelta(days=15), 
                                   end=move_date + timedelta(days=1))
            
            if len(spy_hist) >= 2:
                spy_change = ((spy_hist['Close'].iloc[-1] - spy_hist['Close'].iloc[-2]) / 
                             spy_hist['Close'].iloc[-2]) * 100
                features['spy_change_1d'] = spy_change
                features['spy_trend_5d'] = ((spy_hist['Close'].iloc[-1] - spy_hist['Close'].iloc[-6]) / 
                                           spy_hist['Close'].iloc[-6]) * 100 if len(spy_hist) >= 6 else 0
                features['market_green'] = int(spy_change > 0)
            
            # Get VIX data
            try:
                vix = yf.Ticker('^VIX')
                vix_hist = vix.history(start=move_date - timedelta(days=5), 
                                       end=move_date + timedelta(days=1))
                if len(vix_hist) >= 1:
                    features['vix'] = vix_hist['Close'].iloc[-1]
                    features['vix_high'] = int(features['vix'] > 25)
                    features['vix_low'] = int(features['vix'] < 15)
            except:
                features['vix'] = 20
                features['vix_high'] = 0
                features['vix_low'] = 0
                
        except Exception as e:
            features['spy_change_1d'] = 0
            features['spy_trend_5d'] = 0
            features['market_green'] = 1
            
        return features
    
    def build_dataset(self, period: str = '6mo'):
        """
        Build the full dataset from all repeat runners
        """
        print("\n" + "🐺" * 30)
        print("   B U I L D I N G   M L   D A T A S E T")
        print("🐺" * 30)
        
        all_samples = []
        
        for ticker in self.REPEAT_RUNNERS:
            print(f"\n📊 Processing {ticker}...")
            
            try:
                # Get full history
                stock = yf.Ticker(ticker)
                hist = stock.history(period=period)
                
                if len(hist) < 30:
                    print(f"   Insufficient data for {ticker}")
                    continue
                
                # Find all big moves
                moves = self.find_big_moves(ticker, period)
                print(f"   Found {len(moves)} big moves (10%+)")
                
                for move in moves:
                    # Extract features
                    features = self.extract_features(ticker, move['date'], hist)
                    
                    if features is None:
                        continue
                    
                    # Add market context
                    features = self.add_market_context(features, move['date'])
                    
                    # Add labels
                    features['ticker'] = ticker
                    features['move_date'] = str(move['date'].date())
                    features['actual_gain'] = move['intraday_gain']
                    features['label'] = 1  # This IS a big move
                    
                    all_samples.append(features)
                
                # Also add NON-MOVE days (negative samples)
                # These help the model learn what DOESN'T precede a big move
                move_dates = set(m['date'].date() for m in moves)
                
                non_move_count = 0
                for i in range(30, len(hist) - 1):  # Skip first 30 for indicator warmup
                    date = hist.index[i]
                    
                    # Skip if this was a big move day
                    if date.date() in move_dates:
                        continue
                    
                    # Check if next day was NOT a big move
                    next_close = hist['Close'].iloc[i + 1]
                    next_high = hist['High'].iloc[i + 1]
                    curr_close = hist['Close'].iloc[i]
                    
                    next_gain = ((next_high - curr_close) / curr_close) * 100
                    
                    if next_gain < self.MIN_GAIN_PCT:
                        # This is a "normal" day - no big move followed
                        features = self.extract_features(ticker, hist.index[i+1], hist)
                        
                        if features is None:
                            continue
                        
                        features = self.add_market_context(features, hist.index[i+1])
                        features['ticker'] = ticker
                        features['move_date'] = str(date.date())
                        features['actual_gain'] = next_gain
                        features['label'] = 0  # NOT a big move
                        
                        all_samples.append(features)
                        non_move_count += 1
                        
                        # Limit negative samples per ticker
                        if non_move_count >= len(moves) * 3:
                            break
                
                print(f"   Added {non_move_count} non-move samples")
                
            except Exception as e:
                print(f"   Error processing {ticker}: {e}")
                continue
        
        # Convert to DataFrame
        self.dataset = pd.DataFrame(all_samples)
        
        print(f"\n{'='*60}")
        print(f"   DATASET COMPLETE")
        print(f"   Total samples: {len(self.dataset)}")
        print(f"   Positive (big moves): {len(self.dataset[self.dataset['label']==1])}")
        print(f"   Negative (normal): {len(self.dataset[self.dataset['label']==0])}")
        print(f"{'='*60}")
        
        return self.dataset
    
    def analyze_patterns(self):
        """
        Quick analysis: What features are most predictive?
        """
        if len(self.dataset) == 0:
            print("Build dataset first!")
            return
        
        print("\n" + "🐺" * 30)
        print("   P A T T E R N   A N A L Y S I S")
        print("🐺" * 30)
        
        # Separate positive and negative samples
        pos = self.dataset[self.dataset['label'] == 1]
        neg = self.dataset[self.dataset['label'] == 0]
        
        # Compare means
        print("\n📊 FEATURE COMPARISON (Big Move vs Normal Day):")
        print(f"{'Feature':<30} {'Before Move':<15} {'Normal Day':<15} {'Diff':<10}")
        print("-" * 70)
        
        # Numeric features to compare
        compare_features = [
            'rsi', 'price_change_5d', 'dist_from_10d_high', 'volume_ratio_1d',
            'volatility_10d', 'consecutive_red', 'bb_position', 'macd_histogram',
            'price_position_10d', 'had_volume_spike', 'below_lower_bb'
        ]
        
        significant_patterns = []
        
        for feature in compare_features:
            if feature not in self.dataset.columns:
                continue
                
            pos_mean = pos[feature].mean()
            neg_mean = neg[feature].mean()
            diff = pos_mean - neg_mean
            diff_pct = (diff / neg_mean * 100) if neg_mean != 0 else 0
            
            print(f"{feature:<30} {pos_mean:<15.2f} {neg_mean:<15.2f} {diff_pct:+.1f}%")
            
            if abs(diff_pct) > 20:  # Significant difference
                significant_patterns.append({
                    'feature': feature,
                    'before_move': pos_mean,
                    'normal': neg_mean,
                    'diff_pct': diff_pct
                })
        
        # Most predictive patterns
        print("\n🎯 MOST PREDICTIVE PATTERNS:")
        for p in sorted(significant_patterns, key=lambda x: abs(x['diff_pct']), reverse=True)[:10]:
            direction = "higher" if p['diff_pct'] > 0 else "lower"
            print(f"   • {p['feature']}: {abs(p['diff_pct']):.0f}% {direction} before big moves")
        
        # Day of week analysis
        print("\n📅 DAY OF WEEK ANALYSIS:")
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        for day in range(5):
            count = len(pos[pos['day_of_week'] == day])
            pct = count / len(pos) * 100 if len(pos) > 0 else 0
            print(f"   {day_names[day]}: {count} moves ({pct:.1f}%)")
        
        return significant_patterns
    
    def export_for_training(self, filename: str = 'runner_dataset.csv'):
        """Export dataset to CSV for use in Colab"""
        if len(self.dataset) == 0:
            print("Build dataset first!")
            return
        
        filepath = self.data_dir / filename
        self.dataset.to_csv(filepath, index=False)
        
        print(f"\n✅ Dataset exported to: {filepath}")
        print(f"   Samples: {len(self.dataset)}")
        print(f"   Features: {len(self.dataset.columns)}")
        print("\n   Upload to Google Colab and train!")
        
        return filepath
    
    def save_dataset(self, filename: str = 'runner_dataset.json'):
        """Save dataset as JSON"""
        if len(self.dataset) == 0:
            print("Build dataset first!")
            return
        
        filepath = self.data_dir / filename
        self.dataset.to_json(filepath, orient='records', indent=2)
        
        print(f"\n✅ Dataset saved to: {filepath}")
        return filepath


def main():
    builder = RunnerDatasetBuilder()
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python runner_dataset_builder.py build    # Build full dataset")
        print("  python runner_dataset_builder.py analyze  # Analyze patterns")
        print("  python runner_dataset_builder.py export   # Export to CSV")
        print("  python runner_dataset_builder.py all      # Build + Analyze + Export")
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'build':
        builder.build_dataset()
        builder.save_dataset()
    
    elif cmd == 'analyze':
        # Load existing dataset
        dataset_path = builder.data_dir / 'runner_dataset.json'
        if dataset_path.exists():
            builder.dataset = pd.read_json(dataset_path)
            builder.analyze_patterns()
        else:
            print("No dataset found. Run 'build' first.")
    
    elif cmd == 'export':
        dataset_path = builder.data_dir / 'runner_dataset.json'
        if dataset_path.exists():
            builder.dataset = pd.read_json(dataset_path)
            builder.export_for_training()
        else:
            print("No dataset found. Run 'build' first.")
    
    elif cmd == 'all':
        builder.build_dataset()
        builder.analyze_patterns()
        builder.export_for_training()
        builder.save_dataset()
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == '__main__':
    main()
