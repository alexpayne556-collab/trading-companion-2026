#!/usr/bin/env python3
"""
🐺 ML PREDICTOR - Machine Learning for Pattern Prediction

Uses XGBoost to predict stock moves based on validated patterns.
Trains on historical data, predicts on new signals.

Author: Brokkr (Brother Mode)
Date: January 2, 2026
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import yfinance as yf
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  scikit-learn not available. Install with: pip install scikit-learn")


class MLPredictor:
    """
    Machine Learning predictor for stock movements
    Features: Technical + Catalyst + Insider signals
    """
    
    def __init__(self):
        self.models_dir = Path('data/models')
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.scaler = None
        self.feature_names = []
        self.feature_importance = {}
    
    def build_feature_dataset(self, tickers: List[str], lookback_years: int = 3) -> pd.DataFrame:
        """
        Build ML dataset with features:
        - Technical: Distance from 52w low, RSI, volume ratio
        - Fundamental: Market cap, sector
        - Catalyst: Days to earnings, insider activity
        - Target: Did stock move >10% in next 30 days?
        """
        print(f"\n🔨 Building ML dataset for {len(tickers)} tickers...")
        
        all_features = []
        
        for ticker in tickers:
            try:
                print(f"   Processing {ticker}...", end='')
                
                stock = yf.Ticker(ticker)
                hist = stock.history(period=f'{lookback_years}y')
                info = stock.info
                
                if hist.empty or len(hist) < 100:
                    print(" ❌ Insufficient data")
                    continue
                
                # Calculate technical indicators
                hist['returns'] = hist['Close'].pct_change()
                hist['volume_ma20'] = hist['Volume'].rolling(20).mean()
                hist['volume_ratio'] = hist['Volume'] / hist['volume_ma20']
                hist['rsi'] = self._calculate_rsi(hist['Close'], 14)
                hist['high_52w'] = hist['High'].rolling(252).max()
                hist['low_52w'] = hist['Low'].rolling(252).min()
                hist['pct_from_low'] = (hist['Close'] - hist['low_52w']) / hist['low_52w'] * 100
                hist['pct_from_high'] = (hist['Close'] - hist['high_52w']) / hist['high_52w'] * 100
                
                # For each day, create feature vector
                for i in range(100, len(hist) - 30):  # Need history + forward window
                    date = hist.index[i]
                    
                    # Features at time t
                    features = {
                        'ticker': ticker,
                        'date': date,
                        
                        # Technical features
                        'pct_from_52w_low': hist['pct_from_low'].iloc[i],
                        'pct_from_52w_high': hist['pct_from_high'].iloc[i],
                        'rsi_14': hist['rsi'].iloc[i],
                        'volume_ratio': hist['volume_ratio'].iloc[i],
                        'returns_5d': hist['returns'].iloc[i-5:i].sum() * 100,
                        'returns_20d': hist['returns'].iloc[i-20:i].sum() * 100,
                        'volatility_20d': hist['returns'].iloc[i-20:i].std() * 100,
                        
                        # Fundamental features
                        'market_cap': info.get('marketCap', 0) / 1e9,  # Billions
                        'short_percent': info.get('shortPercentOfFloat', 0) * 100,
                        
                        # Target: Did stock gain >10% in next 30 days?
                        'target': 1 if hist['Close'].iloc[i:i+30].max() / hist['Close'].iloc[i] > 1.10 else 0
                    }
                    
                    all_features.append(features)
                
                print(f" ✅ {len(all_features)} samples")
                
            except Exception as e:
                print(f" ❌ Error: {e}")
                continue
        
        df = pd.DataFrame(all_features)
        print(f"\n📊 Total dataset: {len(df)} samples")
        print(f"   Positive class: {df['target'].sum()} ({df['target'].mean()*100:.1f}%)")
        
        return df
    
    def train_model(self, df: pd.DataFrame) -> Dict:
        """
        Train Random Forest classifier
        Returns metrics and feature importance
        """
        if not SKLEARN_AVAILABLE:
            print("❌ scikit-learn required for ML training")
            return {}
        
        print(f"\n🎓 Training ML Model...")
        print("=" * 70)
        
        # Prepare features and target
        feature_cols = [
            'pct_from_52w_low', 'pct_from_52w_high', 'rsi_14', 
            'volume_ratio', 'returns_5d', 'returns_20d', 
            'volatility_20d', 'market_cap', 'short_percent'
        ]
        
        X = df[feature_cols].fillna(0)
        y = df['target']
        
        self.feature_names = feature_cols
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"   Training set: {len(X_train)} samples")
        print(f"   Test set: {len(X_test)} samples")
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        print(f"\n   Training Random Forest...")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=20,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        print(f"   Train Accuracy: {train_score:.3f}")
        print(f"   Test Accuracy: {test_score:.3f}")
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
        print(f"   CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
        
        # Feature importance
        importance = dict(zip(feature_cols, self.model.feature_importances_))
        self.feature_importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        
        print(f"\n📊 Feature Importance:")
        for feature, score in self.feature_importance.items():
            print(f"   {feature:25s} {score:.3f}")
        
        # Predictions on test set
        y_pred = self.model.predict(X_test_scaled)
        
        print(f"\n📈 Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['No Move', 'Move >10%']))
        
        print(f"\n🎯 Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(f"   True Negatives:  {cm[0][0]}")
        print(f"   False Positives: {cm[0][1]}")
        print(f"   False Negatives: {cm[1][0]}")
        print(f"   True Positives:  {cm[1][1]}")
        
        # Save model
        self._save_model()
        
        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': self.feature_importance,
            'confusion_matrix': cm.tolist()
        }
    
    def predict(self, ticker: str) -> Optional[Dict]:
        """
        Predict probability of >10% move in next 30 days
        """
        if self.model is None or self.scaler is None:
            print("❌ Model not trained. Run train_model() first.")
            return None
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1y')
            info = stock.info
            
            if hist.empty or len(hist) < 100:
                return None
            
            # Calculate same features as training
            hist['returns'] = hist['Close'].pct_change()
            hist['volume_ma20'] = hist['Volume'].rolling(20).mean()
            hist['volume_ratio'] = hist['Volume'] / hist['volume_ma20']
            hist['rsi'] = self._calculate_rsi(hist['Close'], 14)
            hist['high_52w'] = hist['High'].rolling(252).max()
            hist['low_52w'] = hist['Low'].rolling(252).min()
            hist['pct_from_low'] = (hist['Close'] - hist['low_52w']) / hist['low_52w'] * 100
            hist['pct_from_high'] = (hist['Close'] - hist['high_52w']) / hist['high_52w'] * 100
            
            # Current features
            latest = hist.iloc[-1]
            
            features = {
                'pct_from_52w_low': latest['pct_from_low'],
                'pct_from_52w_high': latest['pct_from_high'],
                'rsi_14': latest['rsi'],
                'volume_ratio': latest['volume_ratio'],
                'returns_5d': hist['returns'].iloc[-5:].sum() * 100,
                'returns_20d': hist['returns'].iloc[-20:].sum() * 100,
                'volatility_20d': hist['returns'].iloc[-20:].std() * 100,
                'market_cap': info.get('marketCap', 0) / 1e9,
                'short_percent': info.get('shortPercentOfFloat', 0) * 100
            }
            
            # Create feature vector
            X = pd.DataFrame([features])[self.feature_names]
            X_scaled = self.scaler.transform(X)
            
            # Predict
            proba = self.model.predict_proba(X_scaled)[0]
            prediction = self.model.predict(X_scaled)[0]
            
            return {
                'ticker': ticker,
                'prediction': 'MOVE >10%' if prediction == 1 else 'NO MOVE',
                'probability': proba[1],
                'confidence': max(proba),
                'features': features,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error predicting {ticker}: {e}")
            return None
    
    def scan_watchlist(self, tickers: List[str], min_probability: float = 0.6) -> List[Dict]:
        """
        Scan watchlist for high-probability setups
        """
        print(f"\n🔍 Scanning {len(tickers)} tickers with ML model...")
        
        predictions = []
        
        for ticker in tickers:
            pred = self.predict(ticker)
            
            if pred and pred['probability'] >= min_probability:
                predictions.append(pred)
                print(f"   ✅ {ticker}: {pred['probability']:.1%} probability")
        
        # Sort by probability
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        
        return predictions
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _save_model(self):
        """Save trained model"""
        if not SKLEARN_AVAILABLE:
            return
        
        import pickle
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_file = self.models_dir / f'ml_predictor_{timestamp}.pkl'
        
        data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance,
            'timestamp': timestamp
        }
        
        with open(model_file, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"\n💾 Model saved: {model_file}")
    
    def load_model(self, model_file: Path):
        """Load trained model"""
        if not SKLEARN_AVAILABLE:
            return
        
        import pickle
        
        with open(model_file, 'rb') as f:
            data = pickle.load(f)
        
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        self.feature_importance = data['feature_importance']
        
        print(f"✅ Model loaded from {model_file}")


def main():
    """CLI interface"""
    import sys
    
    predictor = MLPredictor()
    
    # Load watchlist
    watchlist_file = Path('atp_watchlists/ATP_WOLF_PACK_MASTER.csv')
    
    if watchlist_file.exists():
        import csv
        with open(watchlist_file) as f:
            reader = csv.DictReader(f)
            tickers = [row['Symbol'] for row in reader]
    else:
        tickers = ['LUNR', 'IONQ', 'SMR', 'RKLB', 'GOGO', 'SOUN', 'BBAI', 'QBTS']
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'train':
            # Build dataset and train
            df = predictor.build_feature_dataset(tickers, lookback_years=2)
            
            if not df.empty:
                metrics = predictor.train_model(df)
                
                print(f"\n{'='*70}")
                print("🎓 TRAINING COMPLETE")
                print(f"{'='*70}")
        
        elif command == 'predict':
            # Predict single ticker
            if len(sys.argv) < 3:
                print("Usage: python ml_predictor.py predict TICKER")
                return
            
            ticker = sys.argv[2].upper()
            
            # Load latest model
            models = sorted(predictor.models_dir.glob('ml_predictor_*.pkl'))
            if not models:
                print("❌ No trained model found. Run 'train' first.")
                return
            
            predictor.load_model(models[-1])
            pred = predictor.predict(ticker)
            
            if pred:
                print(f"\n{'='*70}")
                print(f"🎯 ML PREDICTION: {ticker}")
                print(f"{'='*70}")
                print(f"Prediction: {pred['prediction']}")
                print(f"Probability: {pred['probability']:.1%}")
                print(f"Confidence: {pred['confidence']:.1%}")
                print(f"\nFeatures:")
                for k, v in pred['features'].items():
                    print(f"  {k:25s} {v:.2f}")
        
        elif command == 'scan':
            # Scan watchlist
            models = sorted(predictor.models_dir.glob('ml_predictor_*.pkl'))
            if not models:
                print("❌ No trained model found. Run 'train' first.")
                return
            
            predictor.load_model(models[-1])
            predictions = predictor.scan_watchlist(tickers, min_probability=0.6)
            
            print(f"\n{'='*70}")
            print(f"🎯 HIGH PROBABILITY SETUPS (≥60%)")
            print(f"{'='*70}")
            
            for pred in predictions:
                print(f"\n{pred['ticker']}")
                print(f"  Probability: {pred['probability']:.1%}")
                print(f"  Distance from 52w low: {pred['features']['pct_from_52w_low']:.1f}%")
                print(f"  RSI: {pred['features']['rsi_14']:.1f}")
                print(f"  Volume Ratio: {pred['features']['volume_ratio']:.2f}x")
    
    else:
        print("Usage:")
        print("  python ml_predictor.py train          # Train model on watchlist")
        print("  python ml_predictor.py predict TICKER # Predict single ticker")
        print("  python ml_predictor.py scan           # Scan watchlist for setups")


if __name__ == '__main__':
    main()
