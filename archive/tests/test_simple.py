import sys
sys.path.insert(0, '/workspaces/trading-companion-2026')

from src.backtest.rigorous_backtest_engine import RigorousBacktestEngine
from src.signals.correlation_break_detector import CorrelationBreakDetector

print('Starting test...')
engine = RigorousBacktestEngine()
detector = CorrelationBreakDetector()

signals = detector.scan_quantum_stocks()
print(f'Found {len(signals)} signals')

if signals:
    results = engine.backtest_strategy(
        signals=signals,
        strategy_name='Correlation Break',
        holding_period_days=5,
        num_monte_carlo_runs=1000
    )
    
    print('\nRESULTS:')
    print(f"Win Rate: {results['win_rate']:.1f}%")
    print(f"P-value: {results['monte_carlo']['p_value']:.4f}")
    print(f"Effect: {results['monte_carlo']['effect_size']:.2f}")
