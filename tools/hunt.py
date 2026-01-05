import yfinance as yf
import pandas as pd
import numpy as np

print("HUNTING...")
print("=" * 60)

# Get data
ionq_data = yf.download('IONQ', start='2024-01-01', progress=False)
rgti_data = yf.download('RGTI', start='2024-01-01', progress=False)

ionq = ionq_data['Close']
rgti = rgti_data['Close']

# Base correlation
ionq_ret = ionq.pct_change().dropna()
rgti_ret = rgti.pct_change().dropna()

# Align indices
common_idx = ionq_ret.index.intersection(rgti_ret.index)
ionq_ret = ionq_ret.loc[common_idx]
rgti_ret = rgti_ret.loc[common_idx]

# Convert to numpy for correlation
base_corr = np.corrcoef(ionq_ret.values, rgti_ret.values)[0, 1]

print(f"\nBase correlation IONQ/RGTI: {base_corr:.3f}")

# Find days IONQ moved 5%+
big_ionq_days = []
for i in range(1, len(ionq)-1):
    ionq_move = ((ionq.iloc[i] - ionq.iloc[i-1]) / ionq.iloc[i-1]) * 100
    
    # Check if it's actually a scalar
    if isinstance(ionq_move, (int, float)) and abs(ionq_move) >= 5:
        # Check what RGTI did next day
        rgti_today = ((rgti.iloc[i] - rgti.iloc[i-1]) / rgti.iloc[i-1]) * 100
        rgti_next = ((rgti.iloc[i+1] - rgti.iloc[i]) / rgti.iloc[i]) * 100
        
        big_ionq_days.append({
            'date': ionq.index[i],
            'ionq_move': ionq_move,
            'rgti_same_day': rgti_today,
            'rgti_next_day': rgti_next
        })

print(f"\nDays with IONQ 5%+ move: {len(big_ionq_days)}")

if big_ionq_days:
    # Stats
    same_day_moves = [d['rgti_same_day'] for d in big_ionq_days]
    next_day_moves = [d['rgti_next_day'] for d in big_ionq_days]
    
    print(f"\nRGTI same day avg: {np.mean(same_day_moves):.2f}%")
    print(f"RGTI next day avg: {np.mean(next_day_moves):.2f}%")
    print(f"RGTI next day win rate: {(np.array(next_day_moves) > 0).mean() * 100:.1f}%")
    
    # Show first 10
    print(f"\nFirst 10 occurrences:")
    for d in big_ionq_days[:10]:
        print(f"{d['date'].strftime('%Y-%m-%d')}: IONQ {d['ionq_move']:+.1f}% | RGTI same {d['rgti_same_day']:+.1f}% | RGTI next {d['rgti_next_day']:+.1f}%")

print("\n" + "=" * 60)
