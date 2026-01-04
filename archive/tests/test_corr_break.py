from src.backtest.rigorous_backtest_engine import RigorousBacktestEngine
from src.signals.correlation_break_detector import CorrelationBreakDetector

engine = RigorousBacktestEngine()
detector = CorrelationBreakDetector()

print('Scanning...')
signals = detector.scan_quantum_stocks()
print(f'Found {len(signals)} signals')

if signals:
    print('Testing...')
    results = engine.backtest_strategy(
        signals=signals,
        strategy_name='Correlation Break',
        holding_period_days=5,
        num_monte_carlo_runs=1000
    )
    
    print(f"\nWin Rate: {results['win_rate']:.1f}%")
    print(f"P-value: {results['monte_carlo']['p_value']:.4f}")
    print(f"Effect size: {results['monte_carlo']['effect_size']:.2f}")
    print(f"Std devs: {results['monte_carlo']['std_devs_above_random']:.1f}")
