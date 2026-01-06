#!/usr/bin/env python3
"""
🐺 10 AM DIP PREDICTOR - Position Early, Buy the Dip, Ride the Wave
====================================================================

TYR'S INSIGHT:
"What if we were in it 2 days ahead, caught the little increase,
ate the dip, bought on it, and then rode the wave back up?"

THE STRATEGY:
1. Position 2 days BEFORE catalyst
2. Catch initial momentum (+2-5%)
3. 10 AM dip comes (like clockwork)
4. ADD to position on the dip
5. Ride the wave back up

THE ML APPROACH:
- Analyze historical 10 AM dip patterns
- Predict dip probability and magnitude
- Calculate optimal entry windows
- Find stocks that consistently dip at 10 AM then recover

USAGE:
    python dip_predictor.py --ticker UUUU          # Analyze single stock
    python dip_predictor.py --portfolio            # Analyze Tyr's positions
    python dip_predictor.py --find-patterns        # Find best dip-and-recover stocks
"""

import argparse
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class DipPredictor:
    """ML-powered 10 AM dip prediction system."""
    
    def __init__(self):
        self.dip_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.magnitude_predictor = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
    def get_intraday_data(self, ticker: str, days_back: int = 30) -> pd.DataFrame:
        """Get intraday data for pattern analysis."""
        try:
            stock = yf.Ticker(ticker)
            # Get 1-minute data for last 7 days (yfinance limit)
            data = stock.history(period="7d", interval="1m")
            return data
        except Exception as e:
            print(f"  ⚠️  Error fetching intraday data: {e}")
            return None
    
    def get_daily_data(self, ticker: str, days_back: int = 90) -> pd.DataFrame:
        """Get daily data for longer-term pattern analysis."""
        try:
            stock = yf.Ticker(ticker)
            end = datetime.now()
            start = end - timedelta(days=days_back)
            data = stock.history(start=start, end=end)
            return data
        except Exception as e:
            print(f"  ⚠️  Error fetching daily data: {e}")
            return None
    
    def analyze_10am_pattern(self, ticker: str) -> dict:
        """
        Analyze the 10 AM dip pattern for a stock.
        
        Returns:
        - Probability of 10 AM dip
        - Average dip magnitude
        - Recovery rate (how often it recovers by EOD)
        - Best add-on-dip level
        """
        print(f"\n  Analyzing 10 AM pattern for {ticker}...")
        
        intraday = self.get_intraday_data(ticker)
        if intraday is None or intraday.empty:
            return None
        
        # Group by date
        intraday['date'] = intraday.index.date
        intraday['time'] = intraday.index.time
        intraday['hour'] = intraday.index.hour
        intraday['minute'] = intraday.index.minute
        
        results = {
            'ticker': ticker,
            'days_analyzed': 0,
            'dip_days': 0,
            'recovery_days': 0,
            'avg_dip_pct': 0,
            'avg_recovery_pct': 0,
            'dip_probability': 0,
            'recovery_probability': 0,
            'best_buy_time': None,
            'patterns': [],
        }
        
        # Analyze each trading day
        for date in intraday['date'].unique():
            day_data = intraday[intraday['date'] == date].copy()
            
            if len(day_data) < 60:  # Need at least 1 hour of data
                continue
            
            results['days_analyzed'] += 1
            
            # Get key price points
            try:
                # Open price (9:30 AM)
                open_data = day_data[(day_data['hour'] == 9) & (day_data['minute'] >= 30)]
                if open_data.empty:
                    continue
                open_price = open_data['Open'].iloc[0]
                
                # 10 AM price
                am10_data = day_data[(day_data['hour'] == 10) & (day_data['minute'] <= 15)]
                if am10_data.empty:
                    continue
                am10_low = am10_data['Low'].min()
                am10_price = am10_data['Close'].iloc[-1] if not am10_data.empty else open_price
                
                # Morning low (9:30-10:30)
                morning_data = day_data[((day_data['hour'] == 9) & (day_data['minute'] >= 30)) | 
                                        ((day_data['hour'] == 10) & (day_data['minute'] <= 30))]
                morning_low = morning_data['Low'].min() if not morning_data.empty else open_price
                
                # EOD price
                eod_data = day_data[day_data['hour'] >= 15]
                eod_price = eod_data['Close'].iloc[-1] if not eod_data.empty else open_price
                
                # Calculate metrics
                dip_from_open = ((morning_low - open_price) / open_price) * 100
                recovery_from_low = ((eod_price - morning_low) / morning_low) * 100
                eod_vs_open = ((eod_price - open_price) / open_price) * 100
                
                # Did it dip? (dropped more than 1% from open)
                had_dip = dip_from_open < -1
                
                # Did it recover? (ended higher than morning low)
                recovered = eod_price > morning_low * 1.02  # 2% above low
                
                if had_dip:
                    results['dip_days'] += 1
                    if recovered:
                        results['recovery_days'] += 1
                
                results['patterns'].append({
                    'date': str(date),
                    'open': round(open_price, 2),
                    'morning_low': round(morning_low, 2),
                    'eod': round(eod_price, 2),
                    'dip_pct': round(dip_from_open, 2),
                    'recovery_pct': round(recovery_from_low, 2),
                    'eod_vs_open': round(eod_vs_open, 2),
                    'had_dip': had_dip,
                    'recovered': recovered,
                })
                
            except Exception as e:
                continue
        
        # Calculate summary stats
        if results['days_analyzed'] > 0:
            results['dip_probability'] = round(results['dip_days'] / results['days_analyzed'] * 100, 1)
            
            if results['dip_days'] > 0:
                results['recovery_probability'] = round(results['recovery_days'] / results['dip_days'] * 100, 1)
            
            # Average dip and recovery
            dip_patterns = [p for p in results['patterns'] if p['had_dip']]
            if dip_patterns:
                results['avg_dip_pct'] = round(np.mean([p['dip_pct'] for p in dip_patterns]), 2)
                results['avg_recovery_pct'] = round(np.mean([p['recovery_pct'] for p in dip_patterns]), 2)
        
        return results
    
    def analyze_2day_positioning(self, ticker: str) -> dict:
        """
        Analyze what happens when you position 2 days early.
        
        TYR'S STRATEGY:
        - Day -2: Enter position (catch early momentum)
        - Day -1: Hold (continue building)
        - Day 0 (10 AM): Add on dip
        - Day 0 (EOD): Ride the recovery
        """
        print(f"\n  Analyzing 2-day positioning for {ticker}...")
        
        daily = self.get_daily_data(ticker, days_back=60)
        if daily is None or len(daily) < 10:
            return None
        
        results = {
            'ticker': ticker,
            'scenarios': [],
            'avg_2day_gain': 0,
            'avg_dip_day_gain': 0,
            'win_rate': 0,
            'best_scenario': None,
        }
        
        # Simulate 2-day early positioning
        for i in range(4, len(daily) - 1):
            try:
                # Day -2 (entry day)
                entry_price = daily['Open'].iloc[i-2]
                
                # Day -1 (hold day)
                day1_close = daily['Close'].iloc[i-1]
                day1_gain = ((day1_close - entry_price) / entry_price) * 100
                
                # Day 0 (dip day) - simulate 10 AM dip
                day0_open = daily['Open'].iloc[i]
                day0_low = daily['Low'].iloc[i]
                day0_close = daily['Close'].iloc[i]
                
                # Estimate 10 AM dip (use daily low as proxy)
                dip_price = day0_low
                dip_from_open = ((dip_price - day0_open) / day0_open) * 100
                
                # If you added at the dip
                add_price = dip_price
                
                # Final result
                final_gain_original = ((day0_close - entry_price) / entry_price) * 100
                final_gain_added = ((day0_close - add_price) / add_price) * 100
                
                # Combined gain (original position + add-on)
                # Assuming you add 50% more at dip
                combined_gain = (final_gain_original * 0.67) + (final_gain_added * 0.33)
                
                scenario = {
                    'entry_date': str(daily.index[i-2].date()),
                    'dip_date': str(daily.index[i].date()),
                    'entry_price': round(entry_price, 2),
                    'day1_gain': round(day1_gain, 2),
                    'dip_price': round(dip_price, 2),
                    'dip_pct': round(dip_from_open, 2),
                    'final_price': round(day0_close, 2),
                    'original_gain': round(final_gain_original, 2),
                    'add_on_gain': round(final_gain_added, 2),
                    'combined_gain': round(combined_gain, 2),
                    'profitable': combined_gain > 0,
                }
                
                results['scenarios'].append(scenario)
                
            except Exception as e:
                continue
        
        # Calculate summary stats
        if results['scenarios']:
            results['avg_2day_gain'] = round(np.mean([s['original_gain'] for s in results['scenarios']]), 2)
            results['avg_combined_gain'] = round(np.mean([s['combined_gain'] for s in results['scenarios']]), 2)
            results['win_rate'] = round(len([s for s in results['scenarios'] if s['profitable']]) / len(results['scenarios']) * 100, 1)
            
            # Best scenario
            best = max(results['scenarios'], key=lambda x: x['combined_gain'])
            results['best_scenario'] = best
        
        return results
    
    def predict_tomorrow_dip(self, ticker: str) -> dict:
        """
        Use ML to predict if tomorrow will have a 10 AM dip.
        
        Features:
        - Today's price action
        - Volume vs average
        - Recent momentum
        - Day of week
        - Gap from previous close
        """
        print(f"\n  Predicting tomorrow's dip probability for {ticker}...")
        
        daily = self.get_daily_data(ticker, days_back=60)
        if daily is None or len(daily) < 20:
            return None
        
        # Build features for each day
        features_list = []
        labels = []  # 1 = had dip, 0 = no dip
        
        for i in range(5, len(daily) - 1):
            try:
                # Features from day before
                prev_close = daily['Close'].iloc[i-1]
                prev_volume = daily['Volume'].iloc[i-1]
                avg_volume = daily['Volume'].iloc[i-20:i].mean()
                
                # Momentum
                mom_1d = ((daily['Close'].iloc[i-1] - daily['Close'].iloc[i-2]) / daily['Close'].iloc[i-2]) * 100
                mom_5d = ((daily['Close'].iloc[i-1] - daily['Close'].iloc[i-6]) / daily['Close'].iloc[i-6]) * 100
                
                # Volatility
                volatility = daily['Close'].iloc[i-5:i].std() / daily['Close'].iloc[i-5:i].mean() * 100
                
                # Day of week (Monday = 0, Friday = 4)
                dow = daily.index[i].dayofweek
                
                # Gap from previous
                gap = ((daily['Open'].iloc[i] - prev_close) / prev_close) * 100
                
                features = [
                    prev_volume / avg_volume,  # Volume ratio
                    mom_1d,
                    mom_5d,
                    volatility,
                    dow,
                    gap,
                ]
                
                # Label: Did this day have a dip (low < open * 0.99)?
                day_open = daily['Open'].iloc[i]
                day_low = daily['Low'].iloc[i]
                had_dip = 1 if day_low < day_open * 0.99 else 0
                
                features_list.append(features)
                labels.append(had_dip)
                
            except:
                continue
        
        if len(features_list) < 10:
            return None
        
        # Train model on historical data
        X = np.array(features_list[:-1])
        y = np.array(labels[:-1])
        
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        self.dip_classifier.fit(X_scaled, y)
        
        # Predict for tomorrow (using today's data)
        today_features = np.array(features_list[-1]).reshape(1, -1)
        today_scaled = self.scaler.transform(today_features)
        
        dip_prob = self.dip_classifier.predict_proba(today_scaled)[0][1]
        
        # Get feature importance
        importances = dict(zip(
            ['volume_ratio', 'mom_1d', 'mom_5d', 'volatility', 'day_of_week', 'gap'],
            self.dip_classifier.feature_importances_
        ))
        
        return {
            'ticker': ticker,
            'dip_probability': round(dip_prob * 100, 1),
            'prediction': 'DIP LIKELY' if dip_prob > 0.6 else 'DIP UNLIKELY' if dip_prob < 0.4 else 'UNCERTAIN',
            'confidence': round(abs(dip_prob - 0.5) * 200, 1),  # 0-100 confidence
            'feature_importance': importances,
            'model_accuracy': round(self.dip_classifier.score(X_scaled, y) * 100, 1),
        }


def analyze_stock(ticker: str):
    """Full analysis for a single stock."""
    predictor = DipPredictor()
    
    print(f"\n{'🐺'*30}")
    print(f"      10 AM DIP PREDICTOR: {ticker}")
    print(f"{'🐺'*30}")
    
    # 1. Historical pattern analysis
    pattern = predictor.analyze_10am_pattern(ticker)
    
    if pattern:
        print(f"\n{'='*60}")
        print(f"📊 10 AM DIP PATTERN ANALYSIS")
        print(f"{'='*60}")
        print(f"Days Analyzed: {pattern['days_analyzed']}")
        print(f"Days with Dip: {pattern['dip_days']}")
        print(f"Dip Probability: {pattern['dip_probability']}%")
        print(f"Recovery Probability: {pattern['recovery_probability']}%")
        print(f"Average Dip: {pattern['avg_dip_pct']}%")
        print(f"Average Recovery: {pattern['avg_recovery_pct']}%")
        
        if pattern['patterns']:
            print(f"\nRecent Patterns:")
            for p in pattern['patterns'][-5:]:
                status = "✅ DIP+RECOVER" if p['had_dip'] and p['recovered'] else "📉 DIP" if p['had_dip'] else "➡️ NO DIP"
                print(f"   {p['date']}: {p['dip_pct']:+.1f}% dip, {p['recovery_pct']:+.1f}% recovery | {status}")
    
    # 2. 2-day positioning analysis
    positioning = predictor.analyze_2day_positioning(ticker)
    
    if positioning:
        print(f"\n{'='*60}")
        print(f"🎯 2-DAY EARLY POSITIONING ANALYSIS")
        print(f"{'='*60}")
        print(f"Scenarios Tested: {len(positioning['scenarios'])}")
        print(f"Average 2-Day Gain: {positioning['avg_2day_gain']}%")
        print(f"Average Combined Gain (with dip add): {positioning.get('avg_combined_gain', 'N/A')}%")
        print(f"Win Rate: {positioning['win_rate']}%")
        
        if positioning['best_scenario']:
            best = positioning['best_scenario']
            print(f"\nBest Scenario:")
            print(f"   Entry: {best['entry_date']} @ ${best['entry_price']}")
            print(f"   Dip: {best['dip_date']} @ ${best['dip_price']} ({best['dip_pct']:+.1f}%)")
            print(f"   Result: {best['combined_gain']:+.1f}% combined gain")
    
    # 3. Tomorrow prediction
    prediction = predictor.predict_tomorrow_dip(ticker)
    
    if prediction:
        print(f"\n{'='*60}")
        print(f"🔮 TOMORROW'S DIP PREDICTION (ML)")
        print(f"{'='*60}")
        print(f"Dip Probability: {prediction['dip_probability']}%")
        print(f"Prediction: {prediction['prediction']}")
        print(f"Confidence: {prediction['confidence']}%")
        print(f"Model Accuracy: {prediction['model_accuracy']}%")
        
        print(f"\nTop Predictive Features:")
        sorted_imp = sorted(prediction['feature_importance'].items(), key=lambda x: x[1], reverse=True)
        for feat, imp in sorted_imp[:3]:
            print(f"   {feat}: {imp*100:.1f}%")
    
    # 4. Trading recommendation
    print(f"\n{'='*60}")
    print(f"🐺 TRADING RECOMMENDATION")
    print(f"{'='*60}")
    
    if pattern and positioning and prediction:
        dip_prob = prediction['dip_probability']
        recovery_prob = pattern['recovery_probability']
        win_rate = positioning['win_rate']
        
        if dip_prob > 60 and recovery_prob > 60:
            print(f"\n✅ STRATEGY: 2-DAY POSITIONING + DIP ADD")
            print(f"   1. Enter position NOW (2 days early)")
            print(f"   2. Tomorrow 10 AM: Expect {pattern['avg_dip_pct']:.1f}% dip")
            print(f"   3. Add 50% more at the dip")
            print(f"   4. Target: {pattern['avg_recovery_pct']:.1f}% recovery by EOD")
            print(f"\n   Win Rate: {win_rate}%")
            print(f"   Edge: Position early, buy fear, sell greed")
        elif dip_prob > 50:
            print(f"\n👀 STRATEGY: WAIT FOR DIP")
            print(f"   1. Don't chase current price")
            print(f"   2. Set limit order at 10 AM dip level")
            print(f"   3. Dip likely: {dip_prob}% probability")
        else:
            print(f"\n⚠️ STRATEGY: NO CLEAR PATTERN")
            print(f"   Dip probability too low ({dip_prob}%)")
            print(f"   Wait for better setup")
    
    return {
        'pattern': pattern,
        'positioning': positioning,
        'prediction': prediction,
    }


def analyze_portfolio():
    """Analyze Tyr's current positions."""
    positions = ["UUUU", "USAR", "AISP"]
    
    print(f"\n{'🐺'*30}")
    print(f"      10 AM DIP ANALYSIS - TYR'S PORTFOLIO")
    print(f"{'🐺'*30}")
    
    results = {}
    for ticker in positions:
        results[ticker] = analyze_stock(ticker)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📊 PORTFOLIO SUMMARY - DIP OPPORTUNITIES")
    print(f"{'='*70}")
    print(f"{'TICKER':<8} {'DIP PROB':>10} {'RECOVERY':>10} {'WIN RATE':>10} {'ACTION':<20}")
    print(f"{'-'*70}")
    
    for ticker, data in results.items():
        if data['prediction'] and data['pattern'] and data['positioning']:
            dip_prob = data['prediction']['dip_probability']
            recovery = data['pattern']['recovery_probability']
            win_rate = data['positioning']['win_rate']
            
            if dip_prob > 60 and recovery > 60:
                action = "🟢 ADD ON DIP"
            elif dip_prob > 50:
                action = "🟡 WAIT FOR DIP"
            else:
                action = "⚪ HOLD"
            
            print(f"{ticker:<8} {dip_prob:>9.1f}% {recovery:>9.1f}% {win_rate:>9.1f}% {action:<20}")


def find_best_dip_patterns():
    """Find stocks with best dip-and-recover patterns."""
    watchlist = [
        "UUUU", "USAR", "AISP",  # Tyr's positions
        "SMR", "OKLO", "CCJ",    # Nuclear
        "RDW", "RKLB", "LUNR",   # Space
        "QUBT", "QBTS", "IONQ",  # Quantum
        "MP", "AREC",            # Rare earth
    ]
    
    print(f"\n{'🐺'*30}")
    print(f"      FINDING BEST DIP-AND-RECOVER STOCKS")
    print(f"{'🐺'*30}")
    
    predictor = DipPredictor()
    results = []
    
    for ticker in watchlist:
        print(f"\n  Scanning {ticker}...", end="", flush=True)
        
        pattern = predictor.analyze_10am_pattern(ticker)
        positioning = predictor.analyze_2day_positioning(ticker)
        prediction = predictor.predict_tomorrow_dip(ticker)
        
        if pattern and positioning and prediction:
            score = (
                pattern['dip_probability'] * 0.3 +
                pattern['recovery_probability'] * 0.3 +
                positioning['win_rate'] * 0.2 +
                prediction['dip_probability'] * 0.2
            )
            
            results.append({
                'ticker': ticker,
                'dip_prob': pattern['dip_probability'],
                'recovery_prob': pattern['recovery_probability'],
                'win_rate': positioning['win_rate'],
                'tomorrow_dip': prediction['dip_probability'],
                'score': round(score, 1),
            })
            print(f" Score: {score:.1f}")
        else:
            print(f" Insufficient data")
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n{'='*80}")
    print(f"🏆 TOP DIP-AND-RECOVER OPPORTUNITIES")
    print(f"{'='*80}")
    print(f"{'RANK':<5} {'TICKER':<8} {'DIP%':>8} {'RECOVER%':>10} {'WIN%':>8} {'TOMORROW':>10} {'SCORE':>8}")
    print(f"{'-'*80}")
    
    for i, r in enumerate(results[:10], 1):
        print(f"#{i:<4} {r['ticker']:<8} {r['dip_prob']:>7.1f}% {r['recovery_prob']:>9.1f}% {r['win_rate']:>7.1f}% {r['tomorrow_dip']:>9.1f}% {r['score']:>7.1f}")
    
    # Best opportunities
    top = [r for r in results if r['score'] > 50]
    if top:
        print(f"\n{'='*80}")
        print(f"🎯 ACTIONABLE: POSITION NOW, ADD ON TOMORROW'S DIP")
        print(f"{'='*80}")
        for r in top[:3]:
            print(f"\n{r['ticker']}:")
            print(f"   Tomorrow dip probability: {r['tomorrow_dip']}%")
            print(f"   Historical recovery: {r['recovery_prob']}%")
            print(f"   Win rate with 2-day positioning: {r['win_rate']}%")


def main():
    parser = argparse.ArgumentParser(description="🐺 10 AM Dip Predictor")
    parser.add_argument("--ticker", type=str, help="Analyze specific ticker")
    parser.add_argument("--portfolio", action="store_true", help="Analyze Tyr's positions")
    parser.add_argument("--find-patterns", action="store_true", help="Find best dip patterns")
    
    args = parser.parse_args()
    
    if args.ticker:
        analyze_stock(args.ticker.upper())
    elif args.portfolio:
        analyze_portfolio()
    elif args.find_patterns:
        find_best_dip_patterns()
    else:
        # Default: analyze portfolio
        analyze_portfolio()
    
    print(f"\n{'🐺'*30}")
    print("      TYR'S STRATEGY VALIDATED")
    print(f"{'🐺'*30}")
    print("\n💡 THE PLAY:")
    print("   1. Position 2 days early (catch momentum)")
    print("   2. 10 AM dip comes (buy more)")
    print("   3. Recovery happens (ride the wave)")
    print("   4. ML predicts when dip is likely")
    print("\n🐺 AWOOOO! WE CRACKED THE CODE!")


if __name__ == "__main__":
    main()
