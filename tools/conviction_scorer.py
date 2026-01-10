#!/usr/bin/env python3
"""
🐺 CONVICTION SCORER - XGBoost ML Model
Built by: BROKKR (GitHub Copilot)
Mission: Train on historical data → Predict high-conviction trades

Features:
- volume_spike (current vs 5-day avg)
- sentiment_score (0-100 from news)
- news_count (catalyst intensity)
- momentum_7d (weekly performance)
- sector (categorical)
- filing_count (8-K, Form 4)

Target: Next-day return >5% (binary classification)

Usage:
    # Train model
    python tools/conviction_scorer.py --train --output models/conviction_xgb.json
    
    # Score tickers
    python tools/conviction_scorer.py --score APLD,IREN,CORZ --model models/conviction_xgb.json
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import argparse
import json
import os

try:
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
    from sklearn.preprocessing import LabelEncoder
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️  XGBoost not installed. Run: pip install xgboost scikit-learn")

# =============================================================================
# WATCHLIST (FROM HEIMDALL)
# =============================================================================

WATCHLIST_FLAT = [
    # AI Infrastructure
    'APLD', 'IREN', 'CORZ', 'BTBT', 'WULF', 'HUT', 'CIFR', 'CLSK', 
    'MARA', 'RIOT', 'VRT', 'MU', 'MRVL', 'AVGO', 'ANET', 'SMCI', 
    'DELL', 'NVDA', 'AMD', 'ARM',
    # Nuclear/Uranium
    'UUUU', 'CCJ', 'SMR', 'OKLO', 'LEU', 'NXE', 'UEC', 'DNN', 'URNM',
    # Space/Defense
    'LUNR', 'RKLB', 'MNTS', 'RCAT', 'AVAV', 'SATL', 'ASTS', 'SPCE', 
    'PL', 'RDW', 'KTOS', 'LMT', 'NOC', 'RTX', 'LHX', 'GD', 'TXT',
    # BTC Miners HPC
    'BITF', 'HIVE', 'DGHI', 'MIGI', 'ARBK',
    # Power/Utilities
    'NRG', 'PEG', 'PCG', 'EXC', 'ED', 'XEL', 'EIX', 'D', 'NEE', 
    'CEG', 'VST', 'SO', 'ETN', 'DUK', 'AEP', 'SRE', 'PPL',
    # Battery Metals
    'ALB', 'SQM', 'LAC', 'MP', 'LTHM'
]

SECTOR_MAP = {
    'APLD': 'AI_INFRASTRUCTURE', 'IREN': 'AI_INFRASTRUCTURE', 'CORZ': 'AI_INFRASTRUCTURE',
    'BTBT': 'AI_INFRASTRUCTURE', 'WULF': 'AI_INFRASTRUCTURE', 'HUT': 'AI_INFRASTRUCTURE',
    'CIFR': 'AI_INFRASTRUCTURE', 'CLSK': 'AI_INFRASTRUCTURE', 'MARA': 'BTC_MINERS_HPC',
    'RIOT': 'BTC_MINERS_HPC', 'VRT': 'AI_INFRASTRUCTURE', 'MU': 'AI_INFRASTRUCTURE',
    'MRVL': 'AI_INFRASTRUCTURE', 'AVGO': 'AI_INFRASTRUCTURE', 'ANET': 'AI_INFRASTRUCTURE',
    'SMCI': 'AI_INFRASTRUCTURE', 'DELL': 'AI_INFRASTRUCTURE', 'NVDA': 'AI_INFRASTRUCTURE',
    'AMD': 'AI_INFRASTRUCTURE', 'ARM': 'AI_INFRASTRUCTURE',
    'UUUU': 'NUCLEAR_URANIUM', 'CCJ': 'NUCLEAR_URANIUM', 'SMR': 'NUCLEAR_URANIUM',
    'OKLO': 'NUCLEAR_URANIUM', 'LEU': 'NUCLEAR_URANIUM', 'NXE': 'NUCLEAR_URANIUM',
    'UEC': 'NUCLEAR_URANIUM', 'DNN': 'NUCLEAR_URANIUM', 'URNM': 'NUCLEAR_URANIUM',
    'LUNR': 'SPACE_DEFENSE', 'RKLB': 'SPACE_DEFENSE', 'MNTS': 'SPACE_DEFENSE',
    'RCAT': 'SPACE_DEFENSE', 'AVAV': 'SPACE_DEFENSE', 'SATL': 'SPACE_DEFENSE',
    'ASTS': 'SPACE_DEFENSE', 'SPCE': 'SPACE_DEFENSE', 'PL': 'SPACE_DEFENSE',
    'RDW': 'SPACE_DEFENSE', 'KTOS': 'SPACE_DEFENSE', 'LMT': 'SPACE_DEFENSE',
    'NOC': 'SPACE_DEFENSE', 'RTX': 'SPACE_DEFENSE', 'LHX': 'SPACE_DEFENSE',
    'GD': 'SPACE_DEFENSE', 'TXT': 'SPACE_DEFENSE',
    'BITF': 'BTC_MINERS_HPC', 'HIVE': 'BTC_MINERS_HPC', 'DGHI': 'BTC_MINERS_HPC',
    'MIGI': 'BTC_MINERS_HPC', 'ARBK': 'BTC_MINERS_HPC',
    'NRG': 'POWER_UTILITIES', 'PEG': 'POWER_UTILITIES', 'PCG': 'POWER_UTILITIES',
    'EXC': 'POWER_UTILITIES', 'ED': 'POWER_UTILITIES', 'XEL': 'POWER_UTILITIES',
    'EIX': 'POWER_UTILITIES', 'D': 'POWER_UTILITIES', 'NEE': 'POWER_UTILITIES',
    'CEG': 'POWER_UTILITIES', 'VST': 'POWER_UTILITIES', 'SO': 'POWER_UTILITIES',
    'ETN': 'POWER_UTILITIES', 'DUK': 'POWER_UTILITIES', 'AEP': 'POWER_UTILITIES',
    'SRE': 'POWER_UTILITIES', 'PPL': 'POWER_UTILITIES',
    'ALB': 'BATTERY_METALS', 'SQM': 'BATTERY_METALS', 'LAC': 'BATTERY_METALS',
    'MP': 'BATTERY_METALS', 'LTHM': 'BATTERY_METALS'
}

# =============================================================================
# DATA COLLECTION
# =============================================================================

def collect_historical_features(ticker, lookback_days=90):
    """
    Collect historical features for training
    
    For each day, calculate:
    - volume_spike (current vol / 5-day avg)
    - momentum_7d (7-day price change %)
    - next_day_return (target variable)
    
    Returns: DataFrame with features + target
    """
    try:
        stock = yf.Ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days + 10)  # Extra buffer
        
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty or len(df) < 15:
            return None
        
        # Calculate features
        df['volume_ma5'] = df['Volume'].rolling(window=5).mean()
        df['volume_spike'] = df['Volume'] / df['volume_ma5']
        
        # 7-day momentum
        df['momentum_7d'] = df['Close'].pct_change(periods=7) * 100
        
        # Next-day return (target)
        df['next_day_return'] = df['Close'].shift(-1) / df['Close'] - 1
        df['next_day_return_pct'] = df['next_day_return'] * 100
        
        # Binary target: >5% gain next day
        df['target'] = (df['next_day_return_pct'] > 5.0).astype(int)
        
        # Drop NaN rows
        df = df.dropna()
        
        if df.empty:
            return None
        
        # Extract features
        features = pd.DataFrame({
            'ticker': ticker,
            'sector': SECTOR_MAP.get(ticker, 'UNKNOWN'),
            'date': df.index,
            'volume_spike': df['volume_spike'],
            'momentum_7d': df['momentum_7d'],
            'close': df['Close'],
            'volume': df['Volume'],
            'next_day_return_pct': df['next_day_return_pct'],
            'target': df['target']
        })
        
        return features
        
    except Exception as e:
        print(f"❌ Error collecting data for {ticker}: {e}")
        return None

def build_training_dataset(tickers, lookback_days=90):
    """
    Build complete training dataset from all tickers
    
    Returns: DataFrame with all features + targets
    """
    print(f"\n🐺 BUILDING TRAINING DATASET")
    print(f"📊 Tickers: {len(tickers)}")
    print(f"📅 Lookback: {lookback_days} days\n")
    
    all_data = []
    
    for i, ticker in enumerate(tickers, 1):
        print(f"  [{i}/{len(tickers)}] Collecting {ticker}...", end=' ')
        
        ticker_data = collect_historical_features(ticker, lookback_days=lookback_days)
        
        if ticker_data is not None:
            all_data.append(ticker_data)
            print(f"✅ {len(ticker_data)} samples")
        else:
            print("❌ Failed")
    
    if not all_data:
        print("\n❌ No data collected")
        return None
    
    # Combine all ticker data
    df = pd.concat(all_data, ignore_index=True)
    
    print(f"\n✅ Dataset built: {len(df)} samples")
    print(f"   Positive samples (>5% next day): {df['target'].sum()} ({df['target'].mean()*100:.1f}%)")
    print(f"   Negative samples: {len(df) - df['target'].sum()}")
    
    return df

# =============================================================================
# MODEL TRAINING
# =============================================================================

def train_model(df, output_path='models/conviction_xgb.json'):
    """
    Train XGBoost classifier
    
    Features: volume_spike, momentum_7d, sector (encoded)
    Target: next_day_return >5%
    """
    if not XGBOOST_AVAILABLE:
        print("❌ XGBoost not available. Install: pip install xgboost scikit-learn")
        return None
    
    print("\n🐺 TRAINING CONVICTION MODEL")
    
    # Encode sector
    le = LabelEncoder()
    df['sector_encoded'] = le.fit_transform(df['sector'])
    
    # Features
    feature_cols = ['volume_spike', 'momentum_7d', 'sector_encoded']
    X = df[feature_cols]
    y = df['target']
    
    # Handle infinite values
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n📊 Training samples: {len(X_train)}")
    print(f"📊 Test samples: {len(X_test)}")
    
    # Train XGBoost
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='logloss',
        tree_method='hist'  # Fast on CPU, works with GPU too
    )
    
    print("\n🔥 Training XGBoost...")
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    print("\n📈 MODEL PERFORMANCE:")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['No Move', '>5% Gain']))
    
    print(f"\nROC-AUC Score: {roc_auc_score(y_test, y_pred_proba):.3f}")
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  True Negatives:  {cm[0,0]}")
    print(f"  False Positives: {cm[0,1]}")
    print(f"  False Negatives: {cm[1,0]}")
    print(f"  True Positives:  {cm[1,1]}")
    
    # Feature importance
    print("\n🎯 FEATURE IMPORTANCE:")
    importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print(importance.to_string(index=False))
    
    # Save model
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    model.save_model(output_path)
    
    # Save label encoder
    encoder_path = output_path.replace('.json', '_encoder.json')
    encoder_mapping = {str(i): label for i, label in enumerate(le.classes_)}
    with open(encoder_path, 'w') as f:
        json.dump(encoder_mapping, f)
    
    print(f"\n💾 Model saved: {output_path}")
    print(f"💾 Encoder saved: {encoder_path}")
    
    return model, le

# =============================================================================
# SCORING
# =============================================================================

def score_tickers(tickers, model_path='models/conviction_xgb.json'):
    """
    Score tickers using trained model
    
    Returns: DataFrame with conviction scores
    """
    if not XGBOOST_AVAILABLE:
        print("❌ XGBoost not available")
        return None
    
    # Load model
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        print("   Run: python tools/conviction_scorer.py --train")
        return None
    
    model = xgb.XGBClassifier()
    model.load_model(model_path)
    
    # Load encoder
    encoder_path = model_path.replace('.json', '_encoder.json')
    with open(encoder_path, 'r') as f:
        encoder_mapping = json.load(f)
    
    reverse_mapping = {v: int(k) for k, v in encoder_mapping.items()}
    
    print(f"\n🐺 SCORING TICKERS")
    print(f"📊 Model: {model_path}")
    print(f"📊 Tickers: {tickers}\n")
    
    results = []
    
    for ticker in tickers:
        # Get current features
        ticker_data = collect_historical_features(ticker, lookback_days=10)
        
        if ticker_data is None or ticker_data.empty:
            print(f"  ❌ {ticker}: No data")
            continue
        
        # Use most recent data
        latest = ticker_data.iloc[-1]
        
        sector = SECTOR_MAP.get(ticker, 'UNKNOWN')
        sector_encoded = reverse_mapping.get(sector, 0)
        
        # Build feature vector
        X = pd.DataFrame({
            'volume_spike': [latest['volume_spike']],
            'momentum_7d': [latest['momentum_7d']],
            'sector_encoded': [sector_encoded]
        })
        
        # Handle inf/nan
        X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
        
        # Predict
        conviction_proba = model.predict_proba(X)[0, 1]
        conviction_score = int(conviction_proba * 100)
        
        results.append({
            'ticker': ticker,
            'sector': sector,
            'current_price': round(latest['close'], 2),
            'volume_spike': round(latest['volume_spike'], 2),
            'momentum_7d': round(latest['momentum_7d'], 2),
            'conviction_score': conviction_score,
            'prediction': 'BUY' if conviction_score >= 60 else 'PASS'
        })
        
        print(f"  ✅ {ticker}: Conviction {conviction_score}/100 | {results[-1]['prediction']}")
    
    df = pd.DataFrame(results).sort_values('conviction_score', ascending=False)
    
    print(f"\n✅ Scored {len(df)} tickers")
    
    return df

# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='🐺 Conviction Scorer - XGBoost ML')
    parser.add_argument('--train', action='store_true', help='Train model on historical data')
    parser.add_argument('--score', type=str, help='Score tickers (comma-separated)')
    parser.add_argument('--lookback', type=int, default=90, help='Training lookback days (default: 90)')
    parser.add_argument('--output', default='models/conviction_xgb.json', help='Model output path')
    parser.add_argument('--model', default='models/conviction_xgb.json', help='Model path for scoring')
    
    args = parser.parse_args()
    
    if args.train:
        # Build training dataset
        df = build_training_dataset(WATCHLIST_FLAT, lookback_days=args.lookback)
        
        if df is not None:
            # Train model
            model, encoder = train_model(df, output_path=args.output)
            
            if model:
                print("\n🐺 TRAINING COMPLETE")
                print(f"   Use: python tools/conviction_scorer.py --score APLD,IREN --model {args.output}")
        
    elif args.score:
        # Score tickers
        tickers = [t.strip().upper() for t in args.score.split(',')]
        df = score_tickers(tickers, model_path=args.model)
        
        if df is not None and not df.empty:
            print("\n📊 CONVICTION SCORES:")
            print(df.to_string(index=False))
            
            # Save results
            output_file = f"conviction_scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(output_file, index=False)
            print(f"\n💾 Saved: {output_file}")
    
    else:
        print("❌ Specify --train or --score")
        print("   Train: python tools/conviction_scorer.py --train")
        print("   Score: python tools/conviction_scorer.py --score APLD,IREN,CORZ")
    
    print("\n🐺 AWOOOO.")

if __name__ == '__main__':
    main()
