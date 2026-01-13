# Code Integration Plan - Research to Implementation
## Bridging Research Insights with Our Existing Code

**Date:** January 13, 2026  
**Purpose:** Specific code changes needed based on research findings

---

## 🎯 PHASE 1: Enhanced Metrics (Day 3 Priority)

### File: `tools/daily_tracker.py`

**Add to class `PerformanceAnalyzer`:**

```python
def calculate_advanced_metrics(self, pattern_type=None, days=30):
    """
    Calculate all professional metrics
    
    Returns:
        dict with profit_factor, sharpe_ratio, max_drawdown, 
        recovery_factor, expectancy
    """
    
    # Get completed trades
    conn = sqlite3.connect(self.db)
    query = '''
        SELECT pct_return, hold_duration_days
        FROM predictions
        WHERE status = 'completed'
    '''
    params = []
    
    if pattern_type:
        query += ' AND pattern_type = ?'
        params.append(pattern_type)
    
    if days:
        cutoff = datetime.now() - timedelta(days=days)
        query += ' AND exit_timestamp > ?'
        params.append(cutoff)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if df.empty:
        return None
    
    returns = df['pct_return']
    
    # 1. Profit Factor = Total Wins / abs(Total Losses)
    wins = returns[returns > 0]
    losses = returns[returns < 0]
    total_wins = wins.sum()
    total_losses = abs(losses.sum())
    profit_factor = total_wins / total_losses if total_losses > 0 else 0
    
    # 2. Sharpe Ratio = (Mean Return / Std Dev) * sqrt(252)
    sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
    
    # 3. Sortino Ratio = (Mean / Downside Std) * sqrt(252)
    downside_returns = returns[returns < 0]
    downside_std = downside_returns.std()
    sortino_ratio = (returns.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0
    
    # 4. Max Drawdown
    cumulative = (1 + returns / 100).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max * 100
    max_drawdown = drawdown.min()
    
    # 5. Recovery Factor = Total Profit / abs(Max Drawdown)
    total_profit = returns.sum()
    recovery_factor = total_profit / abs(max_drawdown) if max_drawdown != 0 else 0
    
    # 6. Expectancy Per Trade = (Avg Win × Win Rate) - (Avg Loss × Loss Rate)
    win_rate = len(wins) / len(returns)
    loss_rate = len(losses) / len(returns)
    avg_win = wins.mean() if len(wins) > 0 else 0
    avg_loss = losses.mean() if len(losses) > 0 else 0
    expectancy = (avg_win * win_rate) + (avg_loss * loss_rate)
    
    # 7. Consecutive wins/losses
    consecutive_losses = self._max_consecutive(returns < 0)
    consecutive_wins = self._max_consecutive(returns > 0)
    
    return {
        'profit_factor': profit_factor,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'max_drawdown': max_drawdown,
        'recovery_factor': recovery_factor,
        'expectancy': expectancy,
        'consecutive_wins': consecutive_wins,
        'consecutive_losses': consecutive_losses,
        'total_trades': len(returns),
        'avg_win': avg_win,
        'avg_loss': avg_loss,
    }

@staticmethod
def _max_consecutive(series):
    """Calculate max consecutive True values"""
    if len(series) == 0:
        return 0
    consecutive = (series != series.shift()).cumsum()
    return series.groupby(consecutive).sum().max()


def print_performance_report(self, pattern_type=None):
    """
    Professional performance report with all metrics
    """
    
    basic_stats = self.get_performance_stats(pattern_type)
    advanced_metrics = self.calculate_advanced_metrics(pattern_type)
    
    if not basic_stats or not advanced_metrics:
        print("Not enough data for performance report")
        return
    
    print("\n" + "="*60)
    print(f"PERFORMANCE REPORT - {pattern_type or 'ALL PATTERNS'}")
    print("="*60)
    
    print("\nBASIC STATISTICS:")
    print(f"  Total Trades: {basic_stats['total_trades']}")
    print(f"  Win Rate: {basic_stats['win_rate']:.1f}%")
    print(f"  Wins: {basic_stats['winning_trades']} | Losses: {basic_stats['losing_trades']}")
    print(f"  Avg Win: {basic_stats['avg_win']:.2f}% | Avg Loss: {basic_stats['avg_loss']:.2f}%")
    print(f"  Avg Hold Days: {basic_stats['avg_hold_days']:.1f}")
    
    print("\nADVANCED METRICS:")
    print(f"  Profit Factor: {advanced_metrics['profit_factor']:.2f}")
    
    # Color-code Sharpe ratio
    sharpe = advanced_metrics['sharpe_ratio']
    sharpe_rating = "EXCELLENT" if sharpe > 2.0 else "GOOD" if sharpe > 1.0 else "POOR"
    print(f"  Sharpe Ratio: {sharpe:.2f} ({sharpe_rating})")
    
    # Color-code drawdown
    dd = advanced_metrics['max_drawdown']
    dd_rating = "EXCELLENT" if dd > -10 else "GOOD" if dd > -20 else "WARNING"
    print(f"  Max Drawdown: {dd:.1f}% ({dd_rating})")
    
    print(f"  Recovery Factor: {advanced_metrics['recovery_factor']:.2f}")
    print(f"  Expectancy/Trade: {advanced_metrics['expectancy']:.2f}%")
    
    print("\nRISK METRICS:")
    print(f"  Sortino Ratio: {advanced_metrics['sortino_ratio']:.2f}")
    print(f"  Max Consecutive Losses: {advanced_metrics['consecutive_losses']}")
    print(f"  Max Consecutive Wins: {advanced_metrics['consecutive_wins']}")
    
    print("\nBEST/WORST:")
    print(f"  Best Trade: {basic_stats['best_trade']:.2f}%")
    print(f"  Worst Trade: {basic_stats['worst_trade']:.2f}%")
    
    print("\n" + "="*60)
    print()
```

**Usage:**
```bash
python daily_tracker.py report
# Or in code:
analyzer = PerformanceAnalyzer()
analyzer.print_performance_report()
analyzer.print_performance_report('compression_oversold')
```

---

## 🎯 PHASE 2: False Positive Filters (Day 4 Priority)

### File: `tools/spring_detector.py`

**Add new class:**

```python
class SignalValidator:
    """Apply multiple filters to reduce false positives"""
    
    def __init__(self):
        self.filters_passed = {}
    
    def validate_signal(self, ticker, signal_data, stock_data):
        """
        Apply all filters - signal must pass ALL to be valid
        
        Args:
            ticker: Stock symbol
            signal_data: Dict with score, confidence, num_signals, etc.
            stock_data: DataFrame with OHLCV
        
        Returns:
            (bool, dict) - (is_valid, filter_results)
        """
        
        filters = {
            'confidence': self._check_confidence(signal_data),
            'multi_signal': self._check_multi_signal(signal_data),
            'volume': self._check_volume(stock_data),
            'market_regime': self._check_market_regime(),
            'support_resistance': self._check_support_resistance(stock_data, signal_data.get('price')),
        }
        
        all_passed = all(filters.values())
        
        if not all_passed:
            print(f"\n❌ {ticker} FILTERED OUT:")
            for filter_name, passed in filters.items():
                status = "✓" if passed else "✗"
                print(f"    {status} {filter_name}")
        
        return all_passed, filters
    
    @staticmethod
    def _check_confidence(signal_data, min_confidence=0.70):
        """Filter 1: Confidence threshold"""
        confidence = signal_data.get('confidence', 0.5)
        return confidence >= min_confidence
    
    @staticmethod
    def _check_multi_signal(signal_data, min_signals=2):
        """Filter 2: Multi-signal confirmation"""
        num_signals = signal_data.get('num_signals', 1)
        return num_signals >= min_signals
    
    @staticmethod
    def _check_volume(stock_data, min_ratio=2.0):
        """Filter 3: Volume confirmation"""
        try:
            current_vol = stock_data['Volume'].iloc[-1]
            avg_vol = stock_data['Volume'].tail(20).mean()
            ratio = current_vol / avg_vol
            return ratio >= min_ratio
        except:
            return False
    
    @staticmethod
    def _check_market_regime(crash_threshold=-0.02):
        """Filter 4: Market regime (skip during crashes)"""
        try:
            spy_data = yf.download('^GSPC', period='5d', progress=False)
            spy_return = spy_data['Close'].pct_change().iloc[-1]
            
            # If SPY down >2%, skip ALL signals
            if spy_return < crash_threshold:
                print(f"⚠️  MARKET CRASH MODE: SPY {spy_return:.2%} - SKIPPING ALL SIGNALS")
                return False
            return True
        except:
            return True  # If can't check, allow signal
    
    @staticmethod
    def _check_support_resistance(stock_data, current_price, max_distance=0.02):
        """Filter 5: Near support/resistance"""
        try:
            support = stock_data['Low'].tail(20).min()
            resistance = stock_data['High'].tail(20).max()
            
            distance_to_support = abs(current_price - support) / support
            distance_to_resistance = abs(current_price - resistance) / resistance
            
            # Valid if within 2% of support OR resistance
            near_level = (distance_to_support < max_distance or 
                         distance_to_resistance < max_distance)
            
            return near_level
        except:
            return True  # If can't check, allow signal
    
    @staticmethod
    def check_sector_momentum(ticker, sector_map=None):
        """Filter 6: Sector momentum (optional - requires sector mapping)"""
        # TODO: Implement sector mapping and momentum check
        # For now, return True (allow all)
        return True
```

**Integrate into existing scan functions:**

```python
def scan_with_filters(self):
    """
    Scan for loaded springs WITH false positive filtering
    """
    
    print("\n" + "="*60)
    print("🔍 SCANNING FOR LOADED SPRINGS (WITH FILTERS)")
    print("="*60)
    
    # Get raw signals
    raw_signals = self.scan_universe()
    
    # Apply filters
    validator = SignalValidator()
    filtered_signals = []
    
    for signal in raw_signals:
        ticker = signal['ticker']
        
        # Fetch stock data for filtering
        try:
            stock_data = yf.download(ticker, period='60d', progress=False)
            is_valid, filter_results = validator.validate_signal(
                ticker, signal, stock_data
            )
            
            if is_valid:
                signal['filters_passed'] = filter_results
                filtered_signals.append(signal)
                print(f"✓ {ticker}: Score {signal['score']:.1f} - ALL FILTERS PASSED")
            
        except Exception as e:
            print(f"❌ {ticker}: Error during validation - {e}")
    
    print(f"\n📊 RESULTS: {len(filtered_signals)}/{len(raw_signals)} signals passed filters")
    print(f"   False positive reduction: {(1 - len(filtered_signals)/len(raw_signals))*100:.1f}%")
    
    return filtered_signals
```

**Usage:**
```bash
python spring_detector.py scan_filtered
```

---

## 🎯 PHASE 3: Adaptive Scoring (Day 5 Priority)

### File: `tools/automated_spring_scanner.py`

**Add new class:**

```python
class AdaptiveScorer:
    """Learn optimal pattern weights from historical performance"""
    
    def __init__(self, db_path='intelligence.db'):
        self.db = db_path
        self.default_weights = {
            'float': 0.25,
            'news_velocity': 0.20,
            'keywords': 0.15,
            'compression': 0.20,
            'nav_discount': 0.10,
            'volume': 0.10,
        }
        self.learned_weights = None
    
    def learn_optimal_weights(self, lookback_days=90, min_trades=20):
        """
        Learn pattern component weights from outcomes
        
        Algorithm:
        1. Query pattern outcomes from last 90 days
        2. For each component (float, compression, etc.), calculate:
           - Win rate when component is strong
           - Average return when component is strong
           - Quality score = win_rate × avg_return
        3. Normalize quality scores to weights
        """
        
        conn = sqlite3.connect(self.db)
        
        # Get completed scans with outcomes
        cutoff = datetime.now() - timedelta(days=lookback_days)
        query = '''
            SELECT 
                signals,
                next_day_move,
                was_correct
            FROM spring_scans
            WHERE scan_date > ?
            AND was_correct IS NOT NULL
        '''
        
        df = pd.read_sql_query(query, conn, params=(cutoff,))
        conn.close()
        
        if len(df) < min_trades:
            print(f"⚠️  Not enough data: {len(df)} trades (need {min_trades})")
            return self.default_weights
        
        # Parse signals (stored as JSON string)
        import json
        component_stats = {}
        
        for _, row in df.iterrows():
            signals = json.loads(row['signals'])
            move = row['next_day_move']
            correct = row['was_correct']
            
            # For each component that fired
            for component in signals:
                if component not in component_stats:
                    component_stats[component] = {
                        'trades': 0,
                        'wins': 0,
                        'total_return': 0
                    }
                
                component_stats[component]['trades'] += 1
                if correct:
                    component_stats[component]['wins'] += 1
                component_stats[component]['total_return'] += move
        
        # Calculate quality scores
        quality_scores = {}
        for component, stats in component_stats.items():
            if stats['trades'] < 5:  # Need minimum sample
                continue
            
            win_rate = stats['wins'] / stats['trades']
            avg_return = stats['total_return'] / stats['trades']
            
            # Quality = win_rate × avg_return
            # Higher quality = more predictive
            quality = win_rate * avg_return
            quality_scores[component] = quality
        
        if not quality_scores:
            print("⚠️  Not enough component data")
            return self.default_weights
        
        # Normalize to weights
        total_quality = sum(quality_scores.values())
        new_weights = {}
        
        for component, quality in quality_scores.items():
            new_weights[component] = quality / total_quality
        
        # Print comparison
        print("\n" + "="*60)
        print("📊 LEARNED OPTIMAL WEIGHTS")
        print("="*60)
        
        for component in new_weights:
            old_w = self.default_weights.get(component, 0)
            new_w = new_weights[component]
            change = ((new_w - old_w) / old_w * 100) if old_w > 0 else 0
            
            print(f"{component:20s}: {old_w:.2%} → {new_w:.2%} ({change:+.0f}%)")
        
        print("="*60)
        
        self.learned_weights = new_weights
        return new_weights
    
    def score_with_learned_weights(self, ticker_data):
        """
        Score ticker using learned weights instead of defaults
        """
        
        weights = self.learned_weights or self.default_weights
        
        score = 0
        for component, value in ticker_data.items():
            weight = weights.get(component, 0)
            score += weight * value * 100  # Scale to 0-100
        
        return min(score, 100)
```

**Integrate into scanner:**

```python
def scan_with_adaptive_scoring(self):
    """
    Daily scan using learned optimal weights
    """
    
    # Load learned weights
    scorer = AdaptiveScorer(self.db)
    weights = scorer.learn_optimal_weights()
    
    # Run scan with new weights
    results = []
    for ticker in self.universe:
        try:
            data = self.get_ticker_data(ticker)
            score = scorer.score_with_learned_weights(data)
            
            if score > 50:  # Threshold
                results.append({
                    'ticker': ticker,
                    'score': score,
                    'adaptive': True
                })
        except:
            pass
    
    return sorted(results, key=lambda x: x['score'], reverse=True)
```

---

## 🎯 PHASE 4: orchestrator.py (Day 1-2 Priority)

### New File: `tools/orchestrator.py`

```python
#!/usr/bin/env python3
"""
Orchestrator - The Brain
Connects all scanners into cohesive daily workflow
"""

import sys
import schedule
import time
from datetime import datetime
import subprocess

# Import our scanners
from spring_detector import SpringDetector
from pattern_discovery import PatternDiscovery
from market_discovery import MarketDiscovery
from catalyst_detector import CatalystDetector
from daily_tracker import DailyTracker, PredictionTracker

class TradingOrchestrator:
    """
    Master controller for all trading system components
    
    Daily Workflow:
    - 7:00 AM: Morning scan (springs + patterns)
    - 9:31 AM: Market open (movers + legs + catalysts)
    - 4:00 PM: End of day logging
    - 5:00 PM: Validation + learning
    """
    
    def __init__(self):
        self.spring_detector = SpringDetector()
        self.pattern_discovery = PatternDiscovery()
        self.tracker = DailyTracker()
        self.prediction_tracker = PredictionTracker()
    
    def morning_scan(self):
        """
        7:00 AM - Find loaded springs before market open
        """
        print("\n" + "="*60)
        print(f"🌅 MORNING SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        # 1. Run spring detector
        print("\n🔍 Scanning for loaded springs...")
        springs = self.spring_detector.scan_with_filters()
        
        # 2. Run pattern discovery
        print("\n📰 Scanning news for patterns...")
        patterns = self.pattern_discovery.scan_news_patterns()
        
        # 3. Aggregate and rank
        print("\n📊 Aggregating signals...")
        watchlist = self._aggregate_signals(springs, patterns)
        
        # 4. Save predictions
        print("\n💾 Saving predictions to database...")
        for signal in watchlist[:20]:  # Top 20
            pred_id = self.prediction_tracker.log_prediction(
                ticker=signal['ticker'],
                pattern_type=signal['pattern_type'],
                score=signal['score'],
                confidence=signal['confidence'],
                entry_price=signal['price']
            )
            print(f"   Logged: {signal['ticker']} (ID: {pred_id})")
        
        # 5. Export watchlist
        self._export_watchlist(watchlist[:20], 'morning')
        
        print(f"\n✅ Morning scan complete: {len(watchlist)} signals")
        print("="*60)
        
        return watchlist
    
    def market_open_scan(self):
        """
        9:31 AM - What's moving NOW
        """
        print("\n" + "="*60)
        print(f"🔔 MARKET OPEN SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        # Run market discovery
        print("\n🔍 Discovering market movers...")
        subprocess.run(['python', 'market_discovery.py'])
        
        # Check legs
        print("\n🦵 Checking legs on movers...")
        subprocess.run(['python', 'legs_classifier.py'])
        
        # Check catalysts
        print("\n📰 Checking catalysts...")
        subprocess.run(['python', 'catalyst_detector.py', 'scan_recent'])
        
        print("\n✅ Market open scan complete")
        print("="*60)
    
    def end_of_day(self):
        """
        4:00 PM - Log today's moves
        """
        print("\n" + "="*60)
        print(f"🌆 END OF DAY - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        # Run daily tracker
        self.tracker.end_of_day()
        
        print("\n✅ EOD logging complete")
        print("="*60)
    
    def evening_analysis(self):
        """
        5:00 PM - Validate predictions + learn from outcomes
        """
        print("\n" + "="*60)
        print(f"🌙 EVENING ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        # 1. Auto-validate old predictions
        print("\n✓ Validating predictions from 5 days ago...")
        results = self.prediction_tracker.auto_validate_predictions()
        print(f"   Validated: {len(results)} predictions")
        
        # 2. Calculate pattern stats
        print("\n📊 Calculating pattern statistics...")
        subprocess.run(['python', 'automated_spring_scanner.py', 'analyze'])
        
        # 3. Learn optimal weights
        print("\n🧠 Learning optimal scoring weights...")
        from automated_spring_scanner import AdaptiveScorer
        scorer = AdaptiveScorer()
        new_weights = scorer.learn_optimal_weights()
        
        # 4. Generate tomorrow's watchlist
        print("\n🔮 Generating tomorrow's watchlist...")
        springs = self.spring_detector.scan_daily()
        self._export_watchlist(springs[:20], 'tomorrow')
        
        # 5. Print performance report
        print("\n📈 PERFORMANCE REPORT:")
        from daily_tracker import PerformanceAnalyzer
        analyzer = PerformanceAnalyzer()
        analyzer.print_performance_report()
        
        print("\n✅ Evening analysis complete")
        print("="*60)
    
    def _aggregate_signals(self, springs, patterns):
        """Combine signals from multiple sources"""
        
        combined = {}
        
        # Add springs
        for spring in springs:
            ticker = spring['ticker']
            combined[ticker] = {
                'ticker': ticker,
                'score': spring['score'],
                'confidence': spring.get('confidence', 0.7),
                'pattern_type': 'spring',
                'signals': [spring],
                'price': spring.get('price', 0)
            }
        
        # Add patterns (boost if already in springs)
        for pattern in patterns:
            ticker = pattern['ticker']
            if ticker in combined:
                # Already flagged by spring - boost confidence
                combined[ticker]['score'] = (combined[ticker]['score'] + pattern['score']) / 2
                combined[ticker]['confidence'] += 0.1
                combined[ticker]['signals'].append(pattern)
            else:
                combined[ticker] = {
                    'ticker': ticker,
                    'score': pattern['score'],
                    'confidence': pattern.get('confidence', 0.6),
                    'pattern_type': 'pattern',
                    'signals': [pattern],
                    'price': pattern.get('price', 0)
                }
        
        # Sort by score
        watchlist = sorted(combined.values(), key=lambda x: x['score'], reverse=True)
        return watchlist
    
    def _export_watchlist(self, watchlist, label=''):
        """Export to CSV for Fidelity ATP"""
        
        import csv
        filename = f"watchlist_{label}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Symbol', 'Score', 'Confidence', 'Pattern'])
            
            for item in watchlist:
                writer.writerow([
                    item['ticker'],
                    f"{item['score']:.1f}",
                    f"{item['confidence']:.2f}",
                    item['pattern_type']
                ])
        
        print(f"\n📁 Watchlist exported: {filename}")
    
    def schedule_daily_workflow(self):
        """Set up daily schedule"""
        
        # Morning scan
        schedule.every().day.at("07:00").do(self.morning_scan)
        
        # Market open
        schedule.every().day.at("09:31").do(self.market_open_scan)
        
        # End of day
        schedule.every().day.at("16:00").do(self.end_of_day)
        
        # Evening analysis
        schedule.every().day.at("17:00").do(self.evening_analysis)
        
        print("📅 Daily workflow scheduled:")
        print("   7:00 AM - Morning scan")
        print("   9:31 AM - Market open")
        print("   4:00 PM - End of day")
        print("   5:00 PM - Evening analysis")
    
    def run(self):
        """Main loop"""
        
        self.schedule_daily_workflow()
        
        print("\n🐺 ORCHESTRATOR ONLINE")
        print("Press Ctrl+C to stop\n")
        
        while True:
            schedule.run_pending()
            time.sleep(60)


# ===== COMMAND LINE =====
if __name__ == '__main__':
    orchestrator = TradingOrchestrator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'morning':
            orchestrator.morning_scan()
        elif command == 'open':
            orchestrator.market_open_scan()
        elif command == 'eod':
            orchestrator.end_of_day()
        elif command == 'evening':
            orchestrator.evening_analysis()
        elif command == 'run':
            orchestrator.run()
        else:
            print("Usage: python orchestrator.py [morning|open|eod|evening|run]")
    else:
        orchestrator.run()
```

**Usage:**
```bash
# Run specific workflow
python orchestrator.py morning
python orchestrator.py open
python orchestrator.py eod
python orchestrator.py evening

# Run continuous (scheduled)
python orchestrator.py run
```

---

## 📋 IMPLEMENTATION SEQUENCE

### Tomorrow (Jan 13 - CPI Day):
1. **Manual CPI workflow** (test all pieces)
2. **Document CPI patterns** in cpi_playbook.md
3. **Start orchestrator.py skeleton**

### Day 2 (Jan 14):
1. **Complete orchestrator.py** core functions
2. **Test morning → open → eod → evening workflow**

### Day 3 (Jan 15):
1. **Add enhanced metrics** to daily_tracker.py
2. **Test performance report** with historical data

### Day 4 (Jan 16):
1. **Add false positive filters** to spring_detector.py
2. **Test filter effectiveness** (should reduce signals by 30-50%)

### Day 5 (Jan 17):
1. **Add adaptive scoring** to automated_spring_scanner.py
2. **Test weight learning** with historical data

---

## 🐺 BROKKR NOTES

**Research validated ALL our core decisions:**
- Architecture matches industry standard
- SQLite appropriate for our scale
- Python schedule module correct choice
- Pattern-based approach is right

**Research identified exact gaps:**
- Advanced metrics (profit factor, Sharpe, drawdown)
- False positive filters (7 techniques)
- Adaptive scoring (learn from outcomes)
- orchestrator.py to tie it together

**Tomorrow CPI = First real test of complete workflow**

AWOOOO - LLHR

---

*Integration plan created: January 13, 2026, 5:55 AM ET*
