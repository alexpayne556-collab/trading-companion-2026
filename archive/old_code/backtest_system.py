#!/usr/bin/env python3
"""
🐺 WOLF PACK BACKTEST SYSTEM v1.0 - Standalone Script
Run locally with your Shadow PC GPU or any machine

This script analyzes historical SEC filings to find THE EDGE:
- What happens to price AFTER contract announcements?
- What's the average return after insider buying clusters?
- Which keywords predict the biggest moves?

Usage:
    python backtest_system.py                              # Run full defense backtest
    python backtest_system.py --ticker SIDU --days 180    # Single ticker analysis
    python backtest_system.py --sector space              # Backtest space sector
    python backtest_system.py --quick                     # Quick test (fewer tickers)

AWOOOO 🐺
"""

import argparse
import pandas as pd
import numpy as np
import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Try to import visualization libraries
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
except ImportError:
    PLOTTING_AVAILABLE = False
    print("⚠️  matplotlib/seaborn not installed. Charts will be skipped.")
    print("   Install with: pip install matplotlib seaborn")

# Try to import yfinance
try:
    import yfinance as yf
except ImportError:
    print("❌ yfinance not installed!")
    print("Run: pip install yfinance")
    exit(1)

# ============================================================
# CONFIGURATION
# ============================================================

# SEC EDGAR Configuration
SEC_BASE_URL = "https://data.sec.gov"
SEC_HEADERS = {
    "User-Agent": "WolfPackScanner contact@wolfpack.trading",
    "Accept-Encoding": "gzip, deflate"
}

# Keywords that indicate contract wins
CONTRACT_KEYWORDS = [
    "contract awarded", "contract award", "government contract",
    "defense contract", "department of defense", "dod contract",
    "idiq", "task order", "prime contract", "subcontract",
    "army", "navy", "air force", "space force", "missile defense",
    "awarded a contract", "received a contract", "contract value",
    "multi-year contract", "indefinite delivery", "ceiling value",
    "nasa", "faa", "homeland security"
]

# Sectors
SECTOR_TICKERS = {
    'defense': ['LMT', 'NOC', 'RTX', 'GD', 'LHX', 'KTOS', 'PLTR', 'BBAI'],
    'space': ['RKLB', 'LUNR', 'ASTS', 'SPCE', 'MNTS'],
    'ai_infra': ['MU', 'VRT', 'NVDA', 'AMD', 'AVGO', 'MRVL'],
    'nuclear': ['CCJ', 'LEU', 'OKLO', 'SMR', 'VST', 'CEG'],
    'small_cap_defense': ['SIDU', 'BBAI', 'KTOS', 'MRCY']
}

# ============================================================
# SEC FILING FETCHER
# ============================================================

def get_company_cik(ticker: str) -> Optional[str]:
    """Get CIK number for a ticker from SEC."""
    try:
        url = f"{SEC_BASE_URL}/files/company_tickers.json"
        response = requests.get(url, headers=SEC_HEADERS, timeout=10)
        data = response.json()
        
        for entry in data.values():
            if entry.get('ticker', '').upper() == ticker.upper():
                return str(entry['cik_str']).zfill(10)
    except:
        pass
    
    return None


def get_8k_filings(cik: str, start_date: str, end_date: str) -> List[Dict]:
    """Get all 8-K filings for a company in date range."""
    filings = []
    
    try:
        url = f"{SEC_BASE_URL}/submissions/CIK{cik}.json"
        response = requests.get(url, headers=SEC_HEADERS, timeout=15)
        data = response.json()
        
        recent = data.get('filings', {}).get('recent', {})
        forms = recent.get('form', [])
        dates = recent.get('filingDate', [])
        accessions = recent.get('accessionNumber', [])
        
        for i, form in enumerate(forms):
            if form == '8-K':
                filing_date = dates[i]
                
                if filing_date >= start_date and filing_date <= end_date:
                    filings.append({
                        'date': filing_date,
                        'type': '8-K',
                        'accession': accessions[i],
                        'cik': cik
                    })
        
        time.sleep(0.15)
        
    except Exception as e:
        pass
    
    return filings


def get_filing_text(cik: str, accession: str) -> str:
    """Get the text content of an 8-K filing."""
    try:
        acc_formatted = accession.replace('-', '')
        url = f"{SEC_BASE_URL}/Archives/edgar/data/{int(cik)}/{acc_formatted}/{accession}.txt"
        
        response = requests.get(url, headers=SEC_HEADERS, timeout=15)
        time.sleep(0.15)
        
        return response.text.lower()
    except:
        return ""


def contains_contract_keywords(text: str) -> Tuple[bool, List[str]]:
    """Check if filing text contains contract-related keywords."""
    found = []
    text_lower = text.lower()
    
    for keyword in CONTRACT_KEYWORDS:
        if keyword in text_lower:
            found.append(keyword)
    
    return len(found) > 0, found


# ============================================================
# PRICE DATA FETCHER
# ============================================================

def get_price_reaction(ticker: str, event_date: str, days_before: int = 5, days_after: int = 20) -> Optional[Dict]:
    """Get price reaction around an event date."""
    try:
        event_dt = datetime.strptime(event_date, '%Y-%m-%d')
        start_dt = event_dt - timedelta(days=days_before + 10)
        end_dt = event_dt + timedelta(days=days_after + 10)
        
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_dt.strftime('%Y-%m-%d'), 
                            end=end_dt.strftime('%Y-%m-%d'))
        
        if hist.empty or len(hist) < 10:
            return None
        
        hist.index = hist.index.tz_localize(None)
        event_idx = None
        
        for i in range(5):
            check_date = event_dt + timedelta(days=i)
            matches = hist.index[hist.index.date == check_date.date()]
            if len(matches) > 0:
                event_idx = hist.index.get_loc(matches[0])
                break
        
        if event_idx is None:
            return None
        
        event_close = hist.iloc[event_idx]['Close']
        pre_idx = max(0, event_idx - 1)
        pre_close = hist.iloc[pre_idx]['Close']
        
        returns = {}
        intervals = [1, 2, 3, 5, 10, 20]
        for days in intervals:
            future_idx = min(len(hist) - 1, event_idx + days)
            if future_idx > event_idx:
                future_close = hist.iloc[future_idx]['Close']
                returns[f'return_{days}d'] = ((future_close - event_close) / event_close) * 100
            else:
                returns[f'return_{days}d'] = None
        
        event_open = hist.iloc[event_idx]['Open']
        overnight_gap = ((event_open - pre_close) / pre_close) * 100
        
        return {
            'ticker': ticker,
            'event_date': event_date,
            'pre_close': round(pre_close, 2),
            'event_close': round(event_close, 2),
            'overnight_gap': round(overnight_gap, 2),
            **{k: round(v, 2) if v else None for k, v in returns.items()}
        }
        
    except Exception as e:
        return None


# ============================================================
# BACKTEST FUNCTION
# ============================================================

def backtest_contract_announcements(
    tickers: List[str],
    start_date: str = "2023-01-01",
    end_date: str = "2025-12-31",
    min_keywords: int = 2,
    verbose: bool = True
) -> pd.DataFrame:
    """Backtest: What happens after 8-K filings with contract keywords?"""
    results = []
    
    if verbose:
        print(f"\n🐺 WOLF PACK BACKTEST: CONTRACT ANNOUNCEMENTS")
        print(f"=" * 50)
        print(f"Analyzing {len(tickers)} tickers from {start_date} to {end_date}")
        print(f"Looking for filings with {min_keywords}+ contract keywords")
        print(f"=" * 50)
    
    for i, ticker in enumerate(tickers):
        if verbose:
            print(f"  Processing {ticker}... ({i+1}/{len(tickers)})", end='\r')
        
        try:
            cik = get_company_cik(ticker)
            if not cik:
                continue
            
            filings = get_8k_filings(cik, start_date, end_date)
            
            for filing in filings:
                text = get_filing_text(cik, filing['accession'])
                
                if not text:
                    continue
                
                has_contract, keywords = contains_contract_keywords(text)
                
                if has_contract and len(keywords) >= min_keywords:
                    reaction = get_price_reaction(ticker, filing['date'])
                    
                    if reaction:
                        results.append({
                            'ticker': ticker,
                            'filing_date': filing['date'],
                            'keywords_found': len(keywords),
                            'keywords': ', '.join(keywords[:5]),
                            **{k: v for k, v in reaction.items() if k not in ['ticker', 'event_date']}
                        })
                
                time.sleep(0.1)
                
        except Exception as e:
            if verbose:
                print(f"  ❌ Error processing {ticker}: {e}")
            continue
    
    if verbose:
        print(" " * 60, end='\r')
    
    df = pd.DataFrame(results)
    
    if verbose:
        if len(df) > 0:
            print(f"\n✅ Found {len(df)} contract announcement events!")
        else:
            print(f"\n⚠️  No contract announcements found.")
    
    return df


# ============================================================
# ANALYSIS FUNCTIONS
# ============================================================

def analyze_results(df: pd.DataFrame):
    """Analyze backtest results and show statistics."""
    if df.empty:
        print("No data to analyze.")
        return
    
    print(f"\n🐺 BACKTEST RESULTS ANALYSIS")
    print(f"=" * 50)
    print(f"Total Events: {len(df)}")
    print(f"Unique Tickers: {df['ticker'].nunique()}")
    print(f"Date Range: {df['filing_date'].min()} to {df['filing_date'].max()}")
    
    print(f"\n📊 RETURN STATISTICS:")
    print("-" * 50)
    
    return_cols = [c for c in df.columns if c.startswith('return_')]
    
    for col in return_cols:
        valid_data = df[col].dropna()
        if len(valid_data) > 0:
            days = col.split('_')[1]
            avg = valid_data.mean()
            median = valid_data.median()
            win_rate = (valid_data > 0).sum() / len(valid_data) * 100
            
            print(f"  {days:>5} | Avg: {avg:+6.2f}% | Median: {median:+6.2f}% | Win Rate: {win_rate:.1f}%")
    
    print(f"\n📈 OVERNIGHT GAP STATS:")
    print("-" * 50)
    gaps = df['overnight_gap'].dropna()
    if len(gaps) > 0:
        print(f"  Average Gap: {gaps.mean():+.2f}%")
        print(f"  Median Gap:  {gaps.median():+.2f}%")
        print(f"  Gap Up Rate: {(gaps > 0).sum() / len(gaps) * 100:.1f}%")
    
    print(f"\n🏆 TOP 10 BEST REACTIONS (5-day return):")
    print("-" * 50)
    if 'return_5d' in df.columns:
        top10 = df.nlargest(10, 'return_5d')[['ticker', 'filing_date', 'return_5d', 'keywords']]
        for _, row in top10.iterrows():
            print(f"  {row['ticker']:6} | {row['filing_date']} | {row['return_5d']:+6.2f}% | {str(row['keywords'])[:30]}...")
    
    print(f"\n📋 BY TICKER (Avg 5-day return):")
    print("-" * 50)
    if 'return_5d' in df.columns:
        by_ticker = df.groupby('ticker')['return_5d'].agg(['mean', 'count']).sort_values('mean', ascending=False)
        for ticker, row in by_ticker.head(10).iterrows():
            print(f"  {ticker:6} | Avg: {row['mean']:+6.2f}% | Events: {int(row['count'])}")


def print_edge_summary(df: pd.DataFrame):
    """Print the actionable edge we found."""
    if df.empty:
        return
    
    print(f"\n")
    print(f"🐺" * 25)
    print(f"\n        THE WOLF PACK EDGE - SUMMARY\n")
    print(f"🐺" * 25)
    
    if 'return_5d' in df.columns:
        valid_returns = df['return_5d'].dropna()
        if len(valid_returns) > 0:
            avg_5d = valid_returns.mean()
            win_rate = (valid_returns > 0).sum() / len(valid_returns) * 100
            
            print(f"""
WHAT WE FOUND:
--------------
After a company announces a government/defense contract (8-K filing):

  📈 Average 5-day return: {avg_5d:+.2f}%
  🎯 Win rate: {win_rate:.1f}%
  📊 Sample size: {len(valid_returns)} events

THE EDGE:
---------
If we had bought every stock the day a contract 8-K was filed
and sold 5 days later:

  ✅ We would have been RIGHT {win_rate:.0f}% of the time
  ✅ Average gain per trade: {avg_5d:.2f}%
  ✅ Expected value is {'POSITIVE ✅' if avg_5d > 0 else 'NEGATIVE ⚠️'}

HOW TO USE THIS:
----------------
1. Run the scanner daily to catch new 8-K filings
2. When contract keywords detected → ALERT
3. Enter position same day or next morning
4. Hold for 3-5 days
5. Take profits at target

REMEMBER:
---------
- This is a STATISTICAL edge, not a guarantee
- Use proper position sizing (5-10% of account)
- Set stop losses (Wolf Pack 2% risk rule)
- The edge works OVER TIME, not every trade

AWOOOO 🐺
            """)


def plot_results(df: pd.DataFrame, output_file: str = 'backtest_results.png'):
    """Visualize backtest results."""
    if not PLOTTING_AVAILABLE:
        print("⚠️  Plotting skipped (matplotlib not installed)")
        return
    
    if df.empty:
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Overnight gaps
    ax1 = axes[0, 0]
    df['overnight_gap'].hist(bins=30, ax=ax1, color='steelblue', edgecolor='black')
    ax1.axvline(x=0, color='red', linestyle='--')
    ax1.axvline(x=df['overnight_gap'].mean(), color='green', linestyle='--')
    ax1.set_title('🐺 Distribution of Overnight Gaps')
    ax1.set_xlabel('Gap %')
    
    # 2. 5-day returns
    ax2 = axes[0, 1]
    if 'return_5d' in df.columns:
        df['return_5d'].dropna().hist(bins=30, ax=ax2, color='green', edgecolor='black')
        ax2.axvline(x=0, color='red', linestyle='--')
        ax2.axvline(x=df['return_5d'].mean(), color='blue', linestyle='--')
        ax2.set_title('🐺 Distribution of 5-Day Returns')
        ax2.set_xlabel('Return %')
    
    # 3. Returns by keywords
    ax3 = axes[1, 0]
    if 'keywords_found' in df.columns and 'return_5d' in df.columns:
        by_keywords = df.groupby('keywords_found')['return_5d'].mean()
        by_keywords.plot(kind='bar', ax=ax3, color='purple', edgecolor='black')
        ax3.set_title('🐺 Avg 5-Day Return by # Keywords')
        ax3.set_xlabel('Keywords Found')
        ax3.set_ylabel('Avg Return %')
        ax3.set_xticklabels(ax3.get_xticklabels(), rotation=0)
    
    # 4. Cumulative returns
    ax4 = axes[1, 1]
    if 'return_5d' in df.columns:
        df_sorted = df.sort_values('filing_date')
        df_sorted['cumulative'] = df_sorted['return_5d'].fillna(0).cumsum()
        ax4.plot(range(len(df_sorted)), df_sorted['cumulative'], color='green', linewidth=2)
        ax4.fill_between(range(len(df_sorted)), df_sorted['cumulative'], alpha=0.3)
        ax4.set_title('🐺 Cumulative Returns')
        ax4.set_xlabel('Event Number')
        ax4.set_ylabel('Cumulative %')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n📊 Charts saved to {output_file}")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='🐺 Wolf Pack Backtest System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--ticker', type=str, help='Analyze single ticker')
    parser.add_argument('--days', type=int, default=365, help='Days to look back')
    parser.add_argument('--sector', type=str, choices=list(SECTOR_TICKERS.keys()), 
                        help='Backtest specific sector')
    parser.add_argument('--quick', action='store_true', help='Quick test (3 tickers)')
    parser.add_argument('--output', type=str, default='backtest_results.csv', 
                        help='Output CSV file')
    
    args = parser.parse_args()
    
    print("🐺 WOLF PACK BACKTEST SYSTEM v1.0")
    print("="* 50)
    
    # Determine tickers to analyze
    if args.ticker:
        tickers = [args.ticker.upper()]
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=args.days)).strftime('%Y-%m-%d')
        print(f"Single ticker mode: {args.ticker}")
    elif args.quick:
        tickers = ['SIDU', 'PLTR', 'RKLB']
        start_date = "2024-06-01"
        end_date = "2025-12-31"
        print("Quick test mode: 3 tickers")
    elif args.sector:
        tickers = list(set(SECTOR_TICKERS[args.sector]))
        start_date = "2024-01-01"
        end_date = "2025-12-31"
        print(f"Sector mode: {args.sector} ({len(tickers)} tickers)")
    else:
        # Default: defense + small cap defense
        defense = SECTOR_TICKERS['defense'] + SECTOR_TICKERS['small_cap_defense']
        tickers = list(set(defense))
        start_date = "2024-01-01"
        end_date = "2025-12-31"
        print(f"Default mode: Defense sector ({len(tickers)} tickers)")
    
    print(f"Period: {start_date} to {end_date}")
    print("=" * 50)
    print("\n⏱️  This may take 5-15 minutes depending on SEC API speed...\n")
    
    # Run backtest
    results = backtest_contract_announcements(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        min_keywords=1 if args.ticker else 2,
        verbose=True
    )
    
    # Analyze and visualize
    if not results.empty:
        analyze_results(results)
        print_edge_summary(results)
        plot_results(results)
        
        # Save results
        results.to_csv(args.output, index=False)
        print(f"\n💾 Results saved to {args.output}")
    else:
        print("\n⚠️  No results found.")
    
    print("\n🐺 AWOOOO - Hunt complete!")


if __name__ == "__main__":
    main()
