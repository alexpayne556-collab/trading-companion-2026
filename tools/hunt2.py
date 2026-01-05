import yfinance as yf
import numpy as np
import pandas as pd

print("HUNTING IONQ/RGTI CORRELATION")
print("=" * 60)

# Download
ionq_df = yf.download('IONQ', start='2024-01-01', progress=False)
rgti_df = yf.download('RGTI', start='2024-01-01', progress=False)

print(f"IONQ days: {len(ionq_df)}")
print(f"RGTI days: {len(rgti_df)}")

# Extract close as lists - handle multi-index
if isinstance(ionq_df['Close'], pd.DataFrame):
    ionq_close = ionq_df['Close'].iloc[:, 0].values
    rgti_close = rgti_df['Close'].iloc[:, 0].values
else:
    ionq_close = ionq_df['Close'].values
    rgti_close = rgti_df['Close'].values

dates = ionq_df.index.tolist()

# Calculate correlation on returns
ionq_rets = [(ionq_close[i] - ionq_close[i-1])/ionq_close[i-1] for i in range(1, len(ionq_close))]
rgti_rets = [(rgti_close[i] - rgti_close[i-1])/rgti_close[i-1] for i in range(1, len(rgti_close))]

min_len = min(len(ionq_rets), len(rgti_rets))
ionq_rets = ionq_rets[:min_len]
rgti_rets = rgti_rets[:min_len]

corr = np.corrcoef(ionq_rets, rgti_rets)[0,1]
print(f"\nBase correlation: {corr:.3f}")

# Find IONQ 5%+ moves
big_moves = []
for i in range(1, min_len-1):
    ionq_pct = ionq_rets[i] * 100
    if abs(ionq_pct) >= 5:
        rgti_same = rgti_rets[i] * 100
        rgti_next = rgti_rets[i+1] * 100
        big_moves.append({
            'date': dates[i+1].strftime('%Y-%m-%d'),
            'ionq': ionq_pct,
            'rgti_same': rgti_same,
            'rgti_next': rgti_next
        })

print(f"\nIONQ 5%+ move days: {len(big_moves)}")

if big_moves:
    same_day = [m['rgti_same'] for m in big_moves]
    next_day = [m['rgti_next'] for m in big_moves]
    
    print(f"\nRGTI same day avg: {np.mean(same_day):.2f}%")
    print(f"RGTI next day avg: {np.mean(next_day):.2f}%")
    print(f"RGTI next day WR: {(np.array(next_day) > 0).mean()*100:.1f}%")
    
    print(f"\nFirst 10:")
    for m in big_moves[:10]:
        print(f"{m['date']}: IONQ {m['ionq']:+.1f}% | RGTI same {m['rgti_same']:+.1f}% next {m['rgti_next']:+.1f}%")

print("=" * 60)
