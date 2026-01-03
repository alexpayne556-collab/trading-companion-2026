#!/usr/bin/env python3
"""
🐺 HUNT #5b: SIDU FILING ANOMALY
SIDU: 100% WR, +39.74% on filings - WHY?
"""

import requests
import yfinance as yf
import numpy as np
import pandas as pd

print("=" * 70)
print("🐺 SIDU FILING ANOMALY")
print("100% WR, +39.74% avg - investigating...")
print("=" * 70)

def get_sec_filings(cik):
    url = f"https://data.sec.gov/submissions/CIK{cik:010d}.json"
    headers = {'User-Agent': 'WolfPack Trading research@wolfpack.com'}
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    filings = []
    recent = data.get('filings', {}).get('recent', {})
    
    if recent:
        forms = recent.get('form', [])
        dates = recent.get('filingDate', [])
        descriptions = recent.get('primaryDocument', [])
        
        for form, date, desc in zip(forms, dates, descriptions):
            filings.append({
                'form': form,
                'date': date,
                'desc': desc
            })
    
    return filings[:100]

# Get SIDU filings
cik = 1819035
filings = get_sec_filings(cik)
print(f"SIDU filings: {len(filings)}")

# Get SIDU price data
df = yf.download('SIDU', start='2024-01-01', progress=False)
if isinstance(df['Close'], pd.DataFrame):
    close = df['Close'].iloc[:, 0]
else:
    close = df['Close']

# Check each filing
print(f"\n{'Date':<12} {'Form':<10} {'10d Return':<12} {'Description'}")
print("-" * 80)

filing_trades = []

for filing in filings:
    if '8-K' in filing['form'] or '10-K' in filing['form'] or '10-Q' in filing['form']:
        try:
            filing_date = pd.Timestamp(filing['date'])
            
            # Find trading day
            future_dates = close.index[close.index >= filing_date]
            if len(future_dates) == 0:
                continue
            
            entry_date = future_dates[0]
            entry_idx = close.index.get_loc(entry_date)
            
            if entry_idx + 10 >= len(close):
                continue
            
            entry = close.iloc[entry_idx]
            exit_10d = close.iloc[entry_idx + 10]
            ret = ((exit_10d - entry) / entry) * 100
            
            print(f"{filing['date']:<12} {filing['form']:<10} {ret:+.1f}%")
            
            filing_trades.append({
                'date': filing['date'],
                'form': filing['form'],
                'return': ret
            })
        except:
            pass

print(f"\n{'=' * 70}")
print(f"Total SIDU filing trades: {len(filing_trades)}")

if filing_trades:
    rets = np.array([f['return'] for f in filing_trades])
    print(f"Win Rate: {(rets > 0).mean() * 100:.1f}%")
    print(f"Avg Return: {rets.mean():+.2f}%")

# Check if this is just because SIDU went up a lot overall
print(f"\n{'=' * 70}")
print("CONTROL: RANDOM SIDU DAYS")
print("=" * 70)

# Random 45 days
random_rets = []
for i in range(25, len(close)-10):
    entry = close.iloc[i]
    exit_10d = close.iloc[i+10]
    ret = ((exit_10d - entry) / entry) * 100
    random_rets.append(ret)

random_rets = np.array(random_rets)
print(f"All SIDU 10-day trades: {len(random_rets)}")
print(f"Win Rate: {(random_rets > 0).mean() * 100:.1f}%")
print(f"Avg Return: {random_rets.mean():+.2f}%")

# So is the filing signal BETTER than random?
if len(filing_trades) >= 5:
    filing_rets = np.array([f['return'] for f in filing_trades])
    
    mc_results = []
    for _ in range(1000):
        sample = np.random.choice(random_rets, size=len(filing_rets))
        mc_results.append(sample.mean())
    
    mc_results = np.array(mc_results)
    p_value = (mc_results >= filing_rets.mean()).mean()
    
    print(f"\nMonte Carlo P-value: {p_value:.4f}")
    if p_value < 0.05:
        print("✅ SIDU filings ARE predictive!")
    else:
        print("❌ SIDU filings NOT predictive - just a hot stock")
