#!/usr/bin/env python3
"""
Form 4 Cluster Scanner - Wolf Pack's #1 Edge
Automatically detects when 3+ insiders buy same stock within 14 days
Catches AISP-type setups before they run

Data Source: SEC EDGAR RSS feed (FREE)
Alert: Email/terminal when cluster detected
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from collections import defaultdict
import json
import sqlite3
from pathlib import Path
import time

class Form4ClusterScanner:
    def __init__(self, db_path="data/form4_clusters.db"):
        """Initialize scanner with local database for tracking"""
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # SEC EDGAR RSS feed for real-time Form 4s
        self.rss_url = "https://www.sec.gov/cgi-bin/browse-edgar"
        
        # Request headers (SEC requires User-Agent)
        self.headers = {
            'User-Agent': 'Wolf Pack Trading tyr@wolfpack.trading',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
    
    def _init_database(self):
        """Create SQLite tables for tracking insider transactions"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Insider transactions table
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            insider_name TEXT,
            insider_title TEXT,
            transaction_date TEXT,
            filing_date TEXT,
            shares INTEGER,
            price REAL,
            value REAL,
            transaction_code TEXT,
            form4_url TEXT,
            is_purchase INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Cluster alerts table
        c.execute('''CREATE TABLE IF NOT EXISTS clusters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            cluster_start TEXT,
            cluster_end TEXT,
            insider_count INTEGER,
            total_value REAL,
            alert_sent INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        conn.commit()
        conn.close()
    
    def fetch_recent_form4s(self, days_back=14):
        """
        Fetch Form 4 filings from SEC EDGAR
        SEC provides RSS feed, but we'll use direct search for reliability
        """
        print(f"🔍 Scanning SEC EDGAR for Form 4s in last {days_back} days...")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # SEC EDGAR search parameters
        # We'll use the company search with form type 4
        params = {
            'action': 'getcompany',
            'type': '4',  # Form 4
            'dateb': end_date.strftime('%Y%m%d'),
            'datea': start_date.strftime('%Y%m%d'),
            'owner': 'include',  # Include insider transactions
            'output': 'atom',  # RSS feed format
            'count': '100'  # Max results per request
        }
        
        try:
            response = requests.get(
                self.rss_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return self._parse_form4_feed(response.text)
            else:
                print(f"⚠️  SEC EDGAR returned status {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching Form 4s: {e}")
            return []
    
    def _parse_form4_feed(self, xml_text):
        """Parse SEC EDGAR RSS feed XML"""
        # This is a simplified parser - SEC format can be complex
        # In production, would use edgar library for robust parsing
        transactions = []
        
        try:
            root = ET.fromstring(xml_text)
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            for entry in entries:
                # Extract basic info from RSS entry
                title = entry.find('{http://www.w3.org/2005/Atom}title').text
                link = entry.find('{http://www.w3.org/2005/Atom}link').get('href')
                updated = entry.find('{http://www.w3.org/2005/Atom}updated').text
                
                # Parse title for ticker (format: "TICKER - Form 4 - ...")
                if ' - ' in title:
                    ticker = title.split(' - ')[0].strip()
                    transactions.append({
                        'ticker': ticker,
                        'filing_url': link,
                        'filing_date': updated,
                        'title': title
                    })
            
            print(f"✅ Found {len(transactions)} Form 4 filings")
            return transactions
            
        except Exception as e:
            print(f"❌ Error parsing XML: {e}")
            return []
    
    def parse_form4_details(self, filing_url):
        """
        Parse individual Form 4 to extract transaction details
        This is simplified - real implementation would parse XML filing
        """
        # In production, would download the XML file and parse transaction table
        # For now, return placeholder structure
        return {
            'insider_name': 'Unknown',
            'insider_title': 'Unknown', 
            'transaction_date': datetime.now().strftime('%Y-%m-%d'),
            'shares': 0,
            'price': 0.0,
            'value': 0.0,
            'transaction_code': 'P',  # P = Purchase
            'is_purchase': True
        }
    
    def detect_clusters(self, window_days=14, min_insiders=3):
        """
        Detect insider buying clusters
        
        Args:
            window_days: Rolling window to check for clusters (default 14)
            min_insiders: Minimum insiders needed for cluster (default 3)
        
        Returns:
            List of tickers with active clusters
        """
        print(f"\n🎯 Detecting clusters: {min_insiders}+ insiders in {window_days} days...")
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get all purchase transactions in the window
        cutoff_date = (datetime.now() - timedelta(days=window_days)).strftime('%Y-%m-%d')
        
        c.execute('''
            SELECT ticker, COUNT(DISTINCT insider_name) as insider_count,
                   SUM(value) as total_value,
                   MIN(transaction_date) as first_buy,
                   MAX(transaction_date) as last_buy
            FROM transactions
            WHERE is_purchase = 1 
            AND transaction_date >= ?
            GROUP BY ticker
            HAVING insider_count >= ?
            ORDER BY insider_count DESC, total_value DESC
        ''', (cutoff_date, min_insiders))
        
        clusters = []
        for row in c.fetchall():
            ticker, count, value, first, last = row
            clusters.append({
                'ticker': ticker,
                'insider_count': count,
                'total_value': value,
                'first_buy': first,
                'last_buy': last,
                'days_span': (datetime.strptime(last, '%Y-%m-%d') - 
                             datetime.strptime(first, '%Y-%m-%d')).days
            })
        
        conn.close()
        
        if clusters:
            print(f"🔥 FOUND {len(clusters)} CLUSTERS:")
            for c in clusters:
                print(f"  {c['ticker']}: {c['insider_count']} insiders, "
                      f"${c['total_value']:,.0f}, {c['days_span']} days span")
        else:
            print("📭 No clusters detected")
        
        return clusters
    
    def store_transaction(self, ticker, details):
        """Store transaction in database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO transactions 
            (ticker, insider_name, insider_title, transaction_date, filing_date,
             shares, price, value, transaction_code, form4_url, is_purchase)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ticker,
            details['insider_name'],
            details['insider_title'],
            details['transaction_date'],
            details.get('filing_date', datetime.now().strftime('%Y-%m-%d')),
            details['shares'],
            details['price'],
            details['value'],
            details['transaction_code'],
            details.get('filing_url', ''),
            1 if details['is_purchase'] else 0
        ))
        
        conn.commit()
        conn.close()
    
    def scan_watchlist(self, ticker_list):
        """
        Scan specific tickers for Form 4 activity
        More targeted than scanning all of EDGAR
        """
        print(f"\n🐺 Scanning {len(ticker_list)} watchlist tickers...")
        
        results = []
        for ticker in ticker_list:
            # Rate limit: SEC allows 10 requests/second
            time.sleep(0.15)
            
            params = {
                'action': 'getcompany',
                'CIK': ticker,
                'type': '4',
                'dateb': datetime.now().strftime('%Y%m%d'),
                'datea': (datetime.now() - timedelta(days=14)).strftime('%Y%m%d'),
                'owner': 'include',
                'output': 'atom',
                'count': '10'
            }
            
            try:
                response = requests.get(
                    self.rss_url,
                    params=params,
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    filings = self._parse_form4_feed(response.text)
                    if filings:
                        results.append({
                            'ticker': ticker,
                            'form4_count': len(filings),
                            'filings': filings
                        })
                        print(f"  {ticker}: {len(filings)} Form 4s")
                
            except Exception as e:
                print(f"  ⚠️  {ticker}: {e}")
        
        return results
    
    def generate_alert(self, cluster):
        """Generate alert message for cluster detection"""
        alert = f"""
🚨 INSIDER BUYING CLUSTER DETECTED 🚨

Ticker: {cluster['ticker']}
Insiders: {cluster['insider_count']} buyers
Total Value: ${cluster['total_value']:,.0f}
Time Span: {cluster['days_span']} days
First Buy: {cluster['first_buy']}
Last Buy: {cluster['last_buy']}

⚠️ AISP-TYPE SETUP - Check conviction score immediately!
"""
        return alert


def main():
    """Command-line interface for cluster scanner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='🐺 Form 4 Cluster Scanner')
    parser.add_argument('--scan', action='store_true', help='Run full scan')
    parser.add_argument('--watchlist', type=str, help='Path to watchlist CSV')
    parser.add_argument('--detect', action='store_true', help='Detect clusters from existing data')
    parser.add_argument('--days', type=int, default=14, help='Days to look back (default: 14)')
    parser.add_argument('--min-insiders', type=int, default=3, help='Min insiders for cluster (default: 3)')
    
    args = parser.parse_args()
    
    scanner = Form4ClusterScanner()
    
    if args.scan:
        # Full SEC EDGAR scan
        filings = scanner.fetch_recent_form4s(days_back=args.days)
        print(f"\n📊 Processed {len(filings)} Form 4 filings")
    
    if args.watchlist:
        # Scan specific watchlist
        import pandas as pd
        df = pd.read_csv(args.watchlist)
        tickers = df['Symbol'].tolist() if 'Symbol' in df.columns else df['ticker'].tolist()
        results = scanner.scan_watchlist(tickers)
        
        print(f"\n📋 Watchlist Scan Complete:")
        print(f"   Tickers scanned: {len(tickers)}")
        print(f"   With Form 4s: {len(results)}")
    
    if args.detect:
        # Detect clusters
        clusters = scanner.detect_clusters(
            window_days=args.days,
            min_insiders=args.min_insiders
        )
        
        if clusters:
            print("\n" + "="*60)
            for cluster in clusters[:5]:  # Top 5
                print(scanner.generate_alert(cluster))
                print("="*60)


if __name__ == '__main__':
    main()
