#!/usr/bin/env python3
"""
🐺 HUNT #5: SEC FILING CORRELATION
Do big moves correlate with 8-K filings?
Can we detect accumulation BEFORE news?
"""

import requests
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

print("=" * 70)
print("🐺 HUNT #5: SEC FILING DETECTION")
print("Do big moves correlate with filings?")
print("=" * 70)

def get_sec_filings(cik, filing_types=['8-K', '10-K', '10-Q']):
    """Get recent SEC filings for a company"""
    url = f"https://data.sec.gov/submissions/CIK{cik:010d}.json"
    headers = {'User-Agent': 'WolfPack Trading research@wolfpack.com'}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        filings = []
        recent = data.get('filings', {}).get('recent', {})
        
        if recent:
            forms = recent.get('form', [])
            dates = recent.get('filingDate', [])
            
            for form, date in zip(forms, dates):
                if any(ft in form for ft in filing_types):
                    filings.append({
                        'form': form,
                        'date': date
                    })
        
        return filings[:50]  # Last 50 filings
    except Exception as e:
        print(f"  Error: {e}")
        return []

# CIKs for our tickers
ciks = {
    'IONQ': 1820302,
    'RGTI': 1838359,
    'QBTS': 1907685,
    'LUNR': 1865107,
    'ASTS': 1780312,
    'RCAT': 1830210,
    'SIDU': 1819035,
}

# For each ticker, check if big moves happen near 8-K filings
results = []

for ticker, cik in ciks.items():
    print(f"\n{ticker} (CIK: {cik})...")
    
    # Get filings
    filings = get_sec_filings(cik)
    print(f"  Found {len(filings)} filings")
    
    if len(filings) == 0:
        continue
    
    # Get price data
    df = yf.download(ticker, start='2024-01-01', progress=False)
    if len(df) < 30:
        continue
    
    if isinstance(df['Close'], pd.DataFrame):
        close = df['Close'].iloc[:, 0]
    else:
        close = df['Close']
    
    # For each filing, check return in following 10 days
    filing_returns = []
    
    for filing in filings:
        try:
            filing_date = pd.Timestamp(filing['date'])
            
            # Find the trading day on or after filing
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
            
            filing_returns.append({
                'ticker': ticker,
                'form': filing['form'],
                'date': filing_date.strftime('%Y-%m-%d'),
                'return': ret
            })
        except Exception as e:
            continue
    
    if len(filing_returns) >= 3:
        rets = np.array([f['return'] for f in filing_returns])
        print(f"  8-K/10-K/10-Q days: {len(rets)} signals")
        print(f"  Win Rate: {(rets > 0).mean() * 100:.1f}%")
        print(f"  Avg Return: {rets.mean():+.2f}%")
        
        results.extend(filing_returns)

# Aggregate analysis
print(f"\n{'=' * 70}")
print("AGGREGATE: ALL FILING-DAY TRADES")
print("=" * 70)

if len(results) >= 10:
    all_rets = np.array([r['return'] for r in results])
    
    print(f"Total signals: {len(all_rets)}")
    print(f"Win Rate: {(all_rets > 0).mean() * 100:.1f}%")
    print(f"Avg Return: {all_rets.mean():+.2f}%")
    print(f"Hit 10%+: {(all_rets >= 10).mean() * 100:.1f}%")
    
    # By filing type
    print(f"\nBy Filing Type:")
    for form_type in ['8-K', '10-K', '10-Q']:
        form_results = [r for r in results if form_type in r['form']]
        if len(form_results) >= 5:
            rets = np.array([r['return'] for r in form_results])
            print(f"  {form_type}: {len(rets)} signals, {(rets > 0).mean()*100:.0f}% WR, {rets.mean():+.1f}%")

# Best filing trades
print(f"\n{'=' * 70}")
print("TOP 10 FILING-DAY TRADES:")
print("=" * 70)

sorted_results = sorted(results, key=lambda x: x['return'], reverse=True)
for r in sorted_results[:10]:
    print(f"{r['date']} {r['ticker']:5} {r['form']:<10} → {r['return']:+.1f}%")
