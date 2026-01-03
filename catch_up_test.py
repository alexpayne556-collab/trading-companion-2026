import yfinance as yf
import numpy as np
import pandas as pd

print("TESTING: WHEN IONQ RUNS, DOES LAGGING RGTI CATCH UP?")
print("=" * 60)

# Download
ionq_df = yf.download('IONQ', start='2024-01-01', progress=False)
rgti_df = yf.download('RGTI', start='2024-01-01', progress=False)

# Extract close
if isinstance(ionq_df['Close'], pd.DataFrame):
    ionq_close = ionq_df['Close'].iloc[:, 0].values
    rgti_close = rgti_df['Close'].iloc[:, 0].values
else:
    ionq_close = ionq_df['Close'].values
    rgti_close = rgti_df['Close'].values

dates = ionq_df.index.tolist()

# Find: IONQ moves 5%+, but RGTI lags (moves <3%)
signals = []

for i in range(1, len(ionq_close)-5):
    ionq_move = ((ionq_close[i] - ionq_close[i-1]) / ionq_close[i-1]) * 100
    rgti_move = ((rgti_close[i] - rgti_close[i-1]) / rgti_close[i-1]) * 100
    
    # IONQ runs, RGTI lags
    if ionq_move >= 5 and rgti_move < 3:
        # Check next 5 days
        entry = rgti_close[i]
        exit_1d = rgti_close[i+1]
        exit_5d = rgti_close[min(i+5, len(rgti_close)-1)]
        
        ret_1d = ((exit_1d - entry) / entry) * 100
        ret_5d = ((exit_5d - entry) / entry) * 100
        
        signals.append({
            'date': dates[i].strftime('%Y-%m-%d'),
            'ionq_move': ionq_move,
            'rgti_lag': rgti_move,
            'rgti_1d': ret_1d,
            'rgti_5d': ret_5d
        })

print(f"\nSignals (IONQ +5%, RGTI <3%): {len(signals)}")

if signals:
    rets_1d = [s['rgti_1d'] for s in signals]
    rets_5d = [s['rgti_5d'] for s in signals]
    
    print(f"\nRGTI 1-day avg: {np.mean(rets_1d):.2f}%")
    print(f"RGTI 1-day WR: {(np.array(rets_1d) > 0).mean()*100:.1f}%")
    
    print(f"\nRGTI 5-day avg: {np.mean(rets_5d):.2f}%")
    print(f"RGTI 5-day WR: {(np.array(rets_5d) > 0).mean()*100:.1f}%")
    
    # Compare to random 5-day RGTI
    all_random = []
    for i in range(len(rgti_close)-5):
        ret = ((rgti_close[i+5] - rgti_close[i]) / rgti_close[i]) * 100
        all_random.append(ret)
    
    print(f"\nRandom 5-day RGTI avg: {np.mean(all_random):.2f}%")
    print(f"Random 5-day RGTI WR: {(np.array(all_random) > 0).mean()*100:.1f}%")
    
    # Monte Carlo
    mc_results = []
    for _ in range(1000):
        sample = np.random.choice(all_random, size=len(rets_5d))
        mc_results.append(np.mean(sample))
    
    mc_mean = np.mean(mc_results)
    mc_std = np.std(mc_results)
    
    p_value = (np.array(mc_results) >= np.mean(rets_5d)).mean()
    std_devs = (np.mean(rets_5d) - mc_mean) / mc_std if mc_std > 0 else 0
    
    print(f"\nMONTE CARLO:")
    print(f"  P-value: {p_value:.4f}")
    print(f"  Std devs above random: {std_devs:.2f}")
    
    print(f"\nFirst 10 signals:")
    for s in signals[:10]:
        print(f"{s['date']}: IONQ +{s['ionq_move']:.1f}% RGTI {s['rgti_lag']:+.1f}% | Next: 1d {s['rgti_1d']:+.1f}% 5d {s['rgti_5d']:+.1f}%")
    
    print("\n" + "=" * 60)
    if p_value < 0.05 and std_devs > 2:
        print("VERDICT: REAL EDGE")
    elif p_value < 0.10:
        print("VERDICT: MARGINAL EDGE")
    else:
        print("VERDICT: NO EDGE (random)")
    print("=" * 60)
