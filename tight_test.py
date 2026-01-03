import yfinance as yf
import numpy as np
import pandas as pd

print("TESTING TIGHTER CRITERIA")
print("=" * 60)

ionq_df = yf.download('IONQ', start='2024-01-01', progress=False)
rgti_df = yf.download('RGTI', start='2024-01-01', progress=False)

if isinstance(ionq_df['Close'], pd.DataFrame):
    ionq_close = ionq_df['Close'].iloc[:, 0].values
    rgti_close = rgti_df['Close'].iloc[:, 0].values
else:
    ionq_close = ionq_df['Close'].values
    rgti_close = rgti_df['Close'].values

dates = ionq_df.index.tolist()

# TIGHTER: IONQ 8%+, RGTI <2%
signals = []

for i in range(1, len(ionq_close)-5):
    ionq_move = ((ionq_close[i] - ionq_close[i-1]) / ionq_close[i-1]) * 100
    rgti_move = ((rgti_close[i] - rgti_close[i-1]) / rgti_close[i-1]) * 100
    
    if ionq_move >= 8 and rgti_move < 2:
        entry = rgti_close[i]
        exit_5d = rgti_close[min(i+5, len(rgti_close)-1)]
        ret_5d = ((exit_5d - entry) / entry) * 100
        
        signals.append({
            'date': dates[i].strftime('%Y-%m-%d'),
            'ionq': ionq_move,
            'rgti_lag': rgti_move,
            'ret_5d': ret_5d
        })

print(f"Signals (IONQ +8%, RGTI <2%): {len(signals)}")

if len(signals) >= 10:
    rets = [s['ret_5d'] for s in signals]
    
    print(f"\n5-day avg: {np.mean(rets):.2f}%")
    print(f"5-day WR: {(np.array(rets) > 0).mean()*100:.1f}%")
    
    # Monte Carlo
    all_random = []
    for i in range(len(rgti_close)-5):
        ret = ((rgti_close[i+5] - rgti_close[i]) / rgti_close[i]) * 100
        all_random.append(ret)
    
    mc_results = []
    for _ in range(1000):
        sample = np.random.choice(all_random, size=len(rets))
        mc_results.append(np.mean(sample))
    
    mc_mean = np.mean(mc_results)
    mc_std = np.std(mc_results)
    
    p_val = (np.array(mc_results) >= np.mean(rets)).mean()
    std_devs = (np.mean(rets) - mc_mean) / mc_std if mc_std > 0 else 0
    
    print(f"\nRandom baseline: {mc_mean:.2f}%")
    print(f"P-value: {p_val:.4f}")
    print(f"Std devs: {std_devs:.2f}")
    
    print(f"\nAll signals:")
    for s in signals:
        print(f"{s['date']}: IONQ +{s['ionq']:.1f}% RGTI {s['rgti_lag']:+.1f}% → {s['ret_5d']:+.1f}%")
    
    print("\n" + "=" * 60)
    if p_val < 0.05 and std_devs > 2:
        print("✅ REAL EDGE")
    elif p_val < 0.10:
        print("⚠️  MARGINAL")
    else:
        print("❌ NO EDGE")
else:
    print("Not enough signals for statistical test")

print("=" * 60)
