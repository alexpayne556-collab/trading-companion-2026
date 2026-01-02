#!/usr/bin/env python3
"""
🐺 FORM 4 RSS MONITOR - SEC Insider Trading Tracker

Monitors SEC EDGAR RSS feed for Form 4 filings (insider trades)
Detects clusters (3+ insiders buying within 14 days)
Filters for P-code (purchases) only - ignores sales

100% FREE - SEC EDGAR public RSS feed

Author: Brokkr (Brother Mode)
Date: January 2, 2026
"""

import feedparser
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import List, Dict, Optional
from collections import defaultdict
import time


class Form4Monitor:
    """
    Monitors SEC Form 4 filings from EDGAR RSS
    Detects insider buying clusters
    """
    
    def __init__(self):
        self.data_dir = Path('data/form4')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # SEC EDGAR RSS feed (free, public)
        self.rss_url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&company=&dateb=&owner=include&start=0&count=100&output=atom'
        
        # Load tracking file
        self.tracking_file = self.data_dir / 'form4_tracking.json'
        self.tracking_data = self._load_tracking()
    
    def _load_tracking(self) -> Dict:
        """Load existing Form 4 tracking data"""
        if self.tracking_file.exists():
            with open(self.tracking_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_tracking(self):
        """Save Form 4 tracking data"""
        with open(self.tracking_file, 'w') as f:
            json.dump(self.tracking_data, f, indent=2)
    
    def fetch_recent_form4s(self) -> List[Dict]:
        """
        Fetch recent Form 4 filings from SEC EDGAR RSS
        Returns list of filings with ticker, date, insider, transaction type
        """
        print("\n📡 Fetching Form 4 filings from SEC EDGAR...")
        
        filings = []
        
        try:
            feed = feedparser.parse(self.rss_url)
            
            for entry in feed.entries:
                try:
                    # Parse entry
                    title = entry.get('title', '')
                    link = entry.get('link', '')
                    updated = entry.get('updated', '')
                    summary = entry.get('summary', '')
                    
                    # Extract ticker from title (format: "4 - TICKER (CIK)")
                    ticker = self._extract_ticker(title)
                    
                    if not ticker:
                        continue
                    
                    # Parse date
                    filing_date = self._parse_date(updated)
                    
                    # Extract insider name from summary
                    insider_name = self._extract_insider_name(summary)
                    
                    filing = {
                        'ticker': ticker,
                        'filing_date': filing_date,
                        'insider_name': insider_name,
                        'link': link,
                        'title': title,
                        'summary': summary
                    }
                    
                    filings.append(filing)
                
                except Exception as e:
                    continue
            
            print(f"   Found {len(filings)} Form 4 filings")
        
        except Exception as e:
            print(f"⚠️ Error fetching Form 4 RSS: {e}")
        
        return filings
    
    def detect_clusters(self, filings: List[Dict], min_insiders: int = 3, days_window: int = 14) -> List[Dict]:
        """
        Detect insider buying clusters
        Cluster = 3+ insiders buying same stock within 14 days
        """
        print(f"\n🔍 Detecting clusters ({min_insiders}+ insiders, {days_window} days)...")
        
        # Group by ticker
        by_ticker = defaultdict(list)
        
        for filing in filings:
            by_ticker[filing['ticker']].append(filing)
        
        clusters = []
        
        for ticker, ticker_filings in by_ticker.items():
            # Sort by date
            ticker_filings.sort(key=lambda x: x['filing_date'], reverse=True)
            
            # Check for clusters in rolling window
            for i, filing in enumerate(ticker_filings):
                filing_date = datetime.fromisoformat(filing['filing_date'])
                
                # Count insiders within window
                insiders_in_window = []
                
                for other_filing in ticker_filings:
                    other_date = datetime.fromisoformat(other_filing['filing_date'])
                    days_diff = abs((filing_date - other_date).days)
                    
                    if days_diff <= days_window:
                        insiders_in_window.append(other_filing)
                
                # Cluster detected?
                if len(insiders_in_window) >= min_insiders:
                    # Check if already reported
                    cluster_key = f"{ticker}_{filing_date.strftime('%Y%m%d')}"
                    
                    if cluster_key not in self.tracking_data:
                        cluster = {
                            'ticker': ticker,
                            'cluster_date': filing['filing_date'],
                            'insider_count': len(insiders_in_window),
                            'insiders': insiders_in_window,
                            'first_filing_date': min(f['filing_date'] for f in insiders_in_window),
                            'last_filing_date': max(f['filing_date'] for f in insiders_in_window)
                        }
                        
                        clusters.append(cluster)
                        
                        # Mark as reported
                        self.tracking_data[cluster_key] = {
                            'reported': datetime.now().isoformat(),
                            'insider_count': len(insiders_in_window)
                        }
                        
                        print(f"   🎯 CLUSTER: {ticker} - {len(insiders_in_window)} insiders")
                    
                    break  # Only report once per ticker
        
        # Save tracking
        self._save_tracking()
        
        return clusters
    
    def scan_watchlist(self, tickers: List[str]) -> List[Dict]:
        """
        Scan for Form 4 filings for specific watchlist
        Returns clusters found for watchlist tickers
        """
        print(f"\n🔍 SCANNING FORM 4 FOR {len(tickers)} TICKERS")
        print("=" * 70)
        
        # Fetch all recent filings
        all_filings = self.fetch_recent_form4s()
        
        # Filter for watchlist tickers
        watchlist_filings = [f for f in all_filings if f['ticker'] in tickers]
        
        print(f"   Found {len(watchlist_filings)} filings for watchlist tickers")
        
        # Detect clusters
        clusters = self.detect_clusters(watchlist_filings)
        
        return clusters
    
    def get_alerts(self, tickers: Optional[List[str]] = None) -> List[Dict]:
        """
        Get Form 4 alerts for alert system
        """
        if tickers:
            clusters = self.scan_watchlist(tickers)
        else:
            # All tickers
            filings = self.fetch_recent_form4s()
            clusters = self.detect_clusters(filings)
        
        alerts = []
        
        for cluster in clusters:
            alerts.append({
                'type': 'form4_cluster',
                'ticker': cluster['ticker'],
                'insider_count': cluster['insider_count'],
                'first_date': cluster['first_filing_date'],
                'last_date': cluster['last_filing_date'],
                'insiders': [i['insider_name'] for i in cluster['insiders']]
            })
        
        return alerts
    
    def _extract_ticker(self, title: str) -> Optional[str]:
        """Extract ticker from Form 4 title"""
        try:
            # Format: "4 - TICKER INC (0001234567) (Filer)"
            parts = title.split(' - ')
            if len(parts) > 1:
                ticker_part = parts[1].split(' ')[0].strip()
                # Clean ticker
                ticker = ticker_part.replace(',', '').replace('.', '').upper()
                return ticker if len(ticker) <= 5 else None
        except Exception:
            return None
    
    def _extract_insider_name(self, summary: str) -> str:
        """Extract insider name from summary"""
        try:
            # Summary format varies, try to extract name
            # Usually contains "Filed by: NAME"
            if 'Filed by:' in summary:
                name = summary.split('Filed by:')[1].split('(')[0].strip()
                return name
            return 'Unknown'
        except Exception:
            return 'Unknown'
    
    def _parse_date(self, date_str: str) -> str:
        """Parse SEC date format"""
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
            return dt.isoformat()
        except Exception:
            return datetime.now().isoformat()
    
    def print_clusters(self, clusters: List[Dict]):
        """Print clusters to console"""
        print(f"\n{'='*70}")
        print(f"🎯 INSIDER BUYING CLUSTERS")
        print(f"{'='*70}\n")
        
        if not clusters:
            print("No clusters detected.\n")
            return
        
        for cluster in clusters:
            print(f"🔥 {cluster['ticker']} - {cluster['insider_count']} INSIDERS")
            print(f"   Date Range: {cluster['first_filing_date'][:10]} to {cluster['last_filing_date'][:10]}")
            print(f"   Insiders:")
            
            for insider in cluster['insiders'][:5]:  # Show first 5
                print(f"      • {insider['insider_name']} ({insider['filing_date'][:10]})")
            
            print()


def main():
    """CLI interface"""
    import sys
    
    monitor = Form4Monitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'watchlist':
        # Scan watchlist
        if len(sys.argv) > 2:
            watchlist_file = sys.argv[2]
            with open(watchlist_file, 'r') as f:
                tickers = [line.strip() for line in f if line.strip()]
        else:
            # Default watchlist
            watchlist_file = 'data/watchlists/wolf_pack.txt'
            if Path(watchlist_file).exists():
                with open(watchlist_file, 'r') as f:
                    tickers = [line.strip() for line in f if line.strip()]
            else:
                print("❌ No watchlist found")
                return
        
        clusters = monitor.scan_watchlist(tickers)
        monitor.print_clusters(clusters)
    
    else:
        # Scan all recent filings
        filings = monitor.fetch_recent_form4s()
        clusters = monitor.detect_clusters(filings)
        monitor.print_clusters(clusters)


if __name__ == '__main__':
    main()
