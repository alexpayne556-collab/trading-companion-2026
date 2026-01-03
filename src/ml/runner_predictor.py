#!/usr/bin/env python3
"""
🐺 REPEAT RUNNER PREDICTOR - ML MODEL 🐺

This script trains a model to predict when a stock is about to make a 10%+ move.

Features used:
- Technical indicators (RSI, MACD, Bollinger)
- Volume patterns
- Price patterns (consolidation, dips, gaps)
- Market context (SPY, VIX)
- Time features

Can run locally (CPU) or on Google Colab (GPU).

Usage:
    python runner_predictor.py train           # Train model
    python runner_predictor.py predict SIDU    # Predict for a stock
    python runner_predictor.py scan            # Predict all watchlist

Author: Brokkr (the learning wolf)
Date: January 3, 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import sys
import pickle
import warnings
warnings.filterwarnings('ignore')

# ML imports
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ scikit-learn not installed. Run: pip install scikit-learn")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

# For live predictions
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


class RunnerPredictor:
    """
    Train and use ML models to predict big moves
    """
    
    DATA_DIR = Path('data/ml')
    MODEL_DIR = Path('models')
    
    # Features to use for training (must match dataset builder)
    FEATURE_COLS = [
        'price_change_1d', 'price_change_5d', 'price_change_10d',
        'dist_from_10d_high', 'dist_from_10d_low', 'price_position_10d',
        'volume_ratio_1d', 'volume_ratio_5d', 'volume_trend', 'had_volume_spike',
        'rsi', 'rsi_oversold', 'rsi_overbought',
        'macd', 'macd_signal', 'macd_histogram', 'macd_bullish_cross',
        'bb_position', 'below_lower_bb', 'above_upper_bb',
        'volatility_10d', 'consolidation',
        'max_gap_10d', 'had_gap_up', 'had_gap_down',
        'red_days_10d', 'consecutive_red',
        'day_of_week', 'is_monday', 'is_friday',
        'spy_change_1d', 'spy_trend_5d', 'market_green',
        'vix', 'vix_high', 'vix_low'
    ]
    
    def __init__(self):
        self.MODEL_DIR.mkdir(parents=True, exist_ok=True)
        self.model = None
        self.scaler = None
        self.feature_importance = {}
    
    def load_dataset(self) -> pd.DataFrame:
        """Load the training dataset"""
        dataset_path = self.DATA_DIR / 'runner_dataset.json'
        
        if not dataset_path.exists():
            print("❌ No dataset found!")
            print("   Run: python src/ml/runner_dataset_builder.py build")
            return None
        
        df = pd.read_json(dataset_path)
        print(f"✅ Loaded dataset: {len(df)} samples")
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """Prepare features for training"""
        # Get available feature columns
        available_features = [col for col in self.FEATURE_COLS if col in df.columns]
        
        print(f"   Using {len(available_features)} features")
        
        X = df[available_features].fillna(0)
        y = df['label']
        
        return X, y, available_features
    
    def train(self, model_type: str = 'xgboost'):
        """
        Train the prediction model
        """
        if not SKLEARN_AVAILABLE:
            print("❌ scikit-learn required. Run: pip install scikit-learn")
            return
        
        print("\n" + "🐺" * 30)
        print("   T R A I N I N G   M O D E L")
        print("🐺" * 30)
        
        # Load data
        df = self.load_dataset()
        if df is None:
            return
        
        # Prepare features
        X, y, feature_names = self.prepare_features(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"\n📊 Data split:")
        print(f"   Training: {len(X_train)} samples")
        print(f"   Testing: {len(X_test)} samples")
        print(f"   Positive rate: {y_train.mean():.1%}")
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Choose model
        if model_type == 'xgboost' and XGBOOST_AVAILABLE:
            print("\n🚀 Training XGBoost model...")
            self.model = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss'
            )
        elif model_type == 'gradient_boosting':
            print("\n🚀 Training Gradient Boosting model...")
            self.model = GradientBoostingClassifier(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        else:
            print("\n🚀 Training Random Forest model...")
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        
        # Train
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        y_prob = self.model.predict_proba(X_test_scaled)[:, 1]
        
        print("\n📈 MODEL PERFORMANCE:")
        print(classification_report(y_test, y_pred, target_names=['Normal', 'Big Move']))
        
        # ROC-AUC
        auc = roc_auc_score(y_test, y_prob)
        print(f"   ROC-AUC Score: {auc:.3f}")
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            self.feature_importance = dict(zip(feature_names, importance))
            
            print("\n🎯 TOP PREDICTIVE FEATURES:")
            sorted_features = sorted(self.feature_importance.items(), 
                                    key=lambda x: x[1], reverse=True)
            for feat, imp in sorted_features[:15]:
                bar = "█" * int(imp * 100)
                print(f"   {feat:<25} {bar} ({imp:.3f})")
        
        # Save model
        self._save_model(feature_names)
        
        # Cross-validation
        print("\n🔄 Cross-validation (5-fold):")
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5, scoring='roc_auc')
        print(f"   AUC scores: {cv_scores}")
        print(f"   Mean AUC: {cv_scores.mean():.3f} (+/- {cv_scores.std()*2:.3f})")
        
        return self.model
    
    def _save_model(self, feature_names: list):
        """Save trained model and scaler"""
        model_path = self.MODEL_DIR / 'runner_model.pkl'
        scaler_path = self.MODEL_DIR / 'runner_scaler.pkl'
        features_path = self.MODEL_DIR / 'runner_features.json'
        importance_path = self.MODEL_DIR / 'feature_importance.json'
        
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        with open(features_path, 'w') as f:
            json.dump(feature_names, f)
        
        with open(importance_path, 'w') as f:
            json.dump(self.feature_importance, f, indent=2)
        
        print(f"\n✅ Model saved to {self.MODEL_DIR}")
    
    def load_model(self) -> bool:
        """Load trained model"""
        model_path = self.MODEL_DIR / 'runner_model.pkl'
        scaler_path = self.MODEL_DIR / 'runner_scaler.pkl'
        
        if not model_path.exists():
            print("❌ No trained model found!")
            print("   Run: python src/ml/runner_predictor.py train")
            return False
        
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
        
        return True
    
    def predict_stock(self, ticker: str) -> dict:
        """
        Predict probability of a big move for a specific stock
        """
        if not YFINANCE_AVAILABLE:
            print("❌ yfinance required for live predictions")
            return None
        
        if self.model is None:
            if not self.load_model():
                return None
        
        # Import the dataset builder for feature extraction
        from runner_dataset_builder import RunnerDatasetBuilder
        
        builder = RunnerDatasetBuilder()
        
        try:
            # Get stock history
            stock = yf.Ticker(ticker)
            hist = stock.history(period='3mo')
            
            if len(hist) < 35:
                print(f"❌ Insufficient data for {ticker}")
                return None
            
            # Extract features for TODAY (predicting tomorrow)
            # Use the last row as the "day before potential move"
            features = builder.extract_features(ticker, hist.index[-1], hist)
            
            if features is None:
                print(f"❌ Could not extract features for {ticker}")
                return None
            
            features = builder.add_market_context(features, hist.index[-1])
            
            # Get feature vector
            feature_path = self.MODEL_DIR / 'runner_features.json'
            with open(feature_path, 'r') as f:
                feature_names = json.load(f)
            
            X = np.array([[features.get(f, 0) for f in feature_names]])
            X_scaled = self.scaler.transform(X)
            
            # Predict
            prob = self.model.predict_proba(X_scaled)[0][1]
            prediction = self.model.predict(X_scaled)[0]
            
            result = {
                'ticker': ticker,
                'probability': prob,
                'prediction': 'BIG MOVE LIKELY' if prediction == 1 else 'Normal',
                'confidence': prob if prediction == 1 else 1 - prob,
                'key_features': {}
            }
            
            # Add key feature values
            importance_path = self.MODEL_DIR / 'feature_importance.json'
            if importance_path.exists():
                with open(importance_path, 'r') as f:
                    importance = json.load(f)
                
                top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]
                for feat, _ in top_features:
                    if feat in features:
                        result['key_features'][feat] = features[feat]
            
            return result
            
        except Exception as e:
            print(f"❌ Error predicting {ticker}: {e}")
            return None
    
    def scan_watchlist(self, tickers: list = None):
        """
        Scan all watchlist stocks and rank by move probability
        """
        if tickers is None:
            tickers = [
                'SIDU', 'RCAT', 'LUNR', 'ASTS', 'RDW', 'CLSK',
                'IONQ', 'RGTI', 'QBTS', 'QUBT', 'SMR', 'OKLO',
                'RKLB', 'BKSY', 'AISP', 'ARQQ', 'OPTT'
            ]
        
        print("\n" + "🐺" * 30)
        print("   S C A N N I N G   W A T C H L I S T")
        print("🐺" * 30)
        
        results = []
        
        for ticker in tickers:
            print(f"\n   Analyzing {ticker}...", end=" ")
            result = self.predict_stock(ticker)
            
            if result:
                results.append(result)
                emoji = "🚀" if result['probability'] > 0.5 else "📊"
                print(f"{emoji} {result['probability']:.1%}")
            else:
                print("❌")
        
        # Sort by probability
        results.sort(key=lambda x: x['probability'], reverse=True)
        
        # Display results
        print("\n" + "=" * 70)
        print(f"   {'TICKER':<10} {'PROBABILITY':<15} {'PREDICTION':<20} {'CONFIDENCE'}")
        print("=" * 70)
        
        for r in results:
            emoji = "🚀" if r['probability'] > 0.5 else "  "
            print(f"{emoji} {r['ticker']:<10} {r['probability']:<15.1%} {r['prediction']:<20} {r['confidence']:.1%}")
        
        # Top picks
        hot_picks = [r for r in results if r['probability'] > 0.5]
        
        if hot_picks:
            print("\n🔥 HOT PICKS (>50% probability of 10%+ move):")
            for r in hot_picks:
                print(f"\n   {r['ticker']}: {r['probability']:.1%} probability")
                print(f"   Key signals:")
                for feat, val in r['key_features'].items():
                    print(f"      • {feat}: {val:.2f}")
        else:
            print("\n📊 No high-probability setups detected today.")
        
        return results


def main():
    predictor = RunnerPredictor()
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python runner_predictor.py train           # Train model")
        print("  python runner_predictor.py predict SIDU    # Predict for stock")
        print("  python runner_predictor.py scan            # Scan watchlist")
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'train':
        model_type = sys.argv[2] if len(sys.argv) > 2 else 'random_forest'
        predictor.train(model_type)
    
    elif cmd == 'predict':
        if len(sys.argv) < 3:
            print("Usage: python runner_predictor.py predict TICKER")
            return
        ticker = sys.argv[2].upper()
        result = predictor.predict_stock(ticker)
        
        if result:
            print(f"\n{'='*50}")
            print(f"   {result['ticker']} PREDICTION")
            print(f"{'='*50}")
            print(f"   Probability of 10%+ move: {result['probability']:.1%}")
            print(f"   Prediction: {result['prediction']}")
            print(f"   Confidence: {result['confidence']:.1%}")
            print(f"\n   Key features:")
            for feat, val in result['key_features'].items():
                print(f"      • {feat}: {val:.2f}")
    
    elif cmd == 'scan':
        predictor.scan_watchlist()
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == '__main__':
    main()
