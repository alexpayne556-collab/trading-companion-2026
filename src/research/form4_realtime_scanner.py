#!/usr/bin/env python3
"""
Form 4 Real-Time Scanner - Uses OpenInsider for clean data
Scans for insider buying clusters across watchlist
Generates alerts for Monday morning

Data Source: OpenInsider.com (aggregates SEC Form 4s)
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json
import sqlite3

class RealtimeForm4Scanner:
    def __init__(self, db_path="data/insider_transactions.db"):
        """Initialize with database for tracking"""
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # OpenInsider URLs for different transaction types
        self.urls = {
            'cluster': 'http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1',
            'purchases': 'http://openinsider.com/latest-purchases-25k'
        }
    
    def _init_database(self):
        """Create tables for tracking insider transactions"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS insider_buys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            insider_name TEXT,
            insider_title TEXT,
            transaction_date TEXT,
            shares INTEGER,
            price REAL,
            value REAL,
            filing_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticker, insider_name, transaction_date, shares)
        )''')
        
        conn.commit()
        conn.close()
    
    def fetch_recent_buys(self, min_value=25000):
        """
        Fetch recent insider purchases from OpenInsider
        Returns clean, parsed data ready to use
        """
        print(f"🔍 Fetching insider buys (>${min_value:,})...")
        
        try:
            # OpenInsider has a CSV download endpoint
            url = "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=14&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&vl=25&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=5000&page=1"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"⚠️  OpenInsider returned {response.status_code}")
                return pd.DataFrame()
            
            # Parse HTML table
            tables = pd.read_html(response.text)
            
            if not tables:
                print("⚠️  No tables found")
                return pd.DataFrame()
            
            df = tables[0]  # Main table
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Filter for purchases only (exclude sales)
            if 'Trade Type' in df.columns:
                df = df[df['Trade Type'].str.contains('P-Purchase', na=False)]
            
            print(f"✅ Found {len(df)} insider purchases")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return pd.DataFrame()
    
    def store_transactions(self, df):
        """Store transactions in database"""
        if df.empty:
            return 0
        
        conn = sqlite3.connect(self.db_path)
        stored = 0
        
        for _, row in df.iterrows():
            try:
                # Map columns (OpenInsider format)
                ticker = row.get('Ticker', row.get('Symbol', ''))
                insider_name = row.get('Insider Name', 'Unknown')
                title = row.get('Title', 'Unknown')
                trans_date = row.get('Trade Date', '')
                filing_date = row.get('Filing Date', '')
                shares = int(row.get('Qty', 0))
                price = float(row.get('Price', 0))
                value = float(row.get('Value', 0))
                
                if not ticker or value < 1000:  # Skip invalid/tiny transactions
                    continue
                
                c = conn.cursor()
                c.execute('''INSERT OR IGNORE INTO insider_buys 
                    (ticker, insider_name, insider_title, transaction_date, 
                     shares, price, value, filing_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (ticker, insider_name, title, trans_date, shares, price, value, filing_date))
                
                if c.rowcount > 0:
                    stored += 1
                    
            except Exception as e:
                continue
        
        conn.commit()
        conn.close()
        
        print(f"✅ Stored {stored} new transactions")
        return stored
    
    def detect_clusters(self, days=14, min_insiders=3, min_total_value=100000):
        """
        Detect tickers where multiple insiders bought recently
        """
        print(f"\n🎯 Detecting clusters: {min_insiders}+ insiders, ${min_total_value:,}+ total...")
        
        conn = sqlite3.connect(self.db_path)
        
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        query = '''
            SELECT 
                ticker,
                COUNT(DISTINCT insider_name) as insider_count,
                SUM(value) as total_value,
                MIN(transaction_date) as first_buy,
                MAX(transaction_date) as last_buy,
                GROUP_CONCAT(insider_name, ' | ') as insiders
            FROM insider_buys
            WHERE transaction_date >= ?
            GROUP BY ticker
            HAVING insider_count >= ? AND total_value >= ?
            ORDER BY insider_count DESC, total_value DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(cutoff, min_insiders, min_total_value))
        conn.close()
        
        if df.empty:
            print("📭 No clusters detected")
            return []
        
        clusters = df.to_dict('records')
        
        print(f"🔥 FOUND {len(clusters)} CLUSTERS:")
        for c in clusters:
            print(f"  {c['ticker']}: {c['insider_count']} insiders, ${c['total_value']:,.0f}")
        
        return clusters
    
    def filter_by_watchlist(self, clusters, watchlist_path):
        """Filter clusters to only watchlist tickers"""
        try:
            df = pd.read_csv(watchlist_path)
            watchlist = df['Symbol'].str.upper().tolist() if 'Symbol' in df.columns else df['ticker'].str.upper().tolist()
            
            filtered = [c for c in clusters if c['ticker'].upper() in watchlist]
            
            print(f"\n🎯 {len(filtered)} clusters in watchlist (filtered from {len(clusters)})")
            return filtered
            
        except Exception as e:
            print(f"⚠️  Watchlist filter failed: {e}")
            return clusters
    
    def generate_alerts(self, clusters, output_file="logs/insider_cluster_alerts.txt"):
        """Generate alert file with cluster details"""
        Path(output_file).parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(f"🐺 INSIDER BUYING CLUSTERS - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write("="*70 + "\n\n")
            
            if not clusters:
                f.write("📭 No clusters detected with current criteria.\n")
                return
            
            for i, cluster in enumerate(clusters, 1):
                alert = f"""
🚨 CLUSTER #{i}: {cluster['ticker']}

Insiders Buying: {cluster['insider_count']} different insiders
Total Value: ${cluster['total_value']:,.0f}
First Buy: {cluster['first_buy']}
Last Buy: {cluster['last_buy']}

Insiders:
{cluster['insiders']}

⚠️ AISP-TYPE SETUP - Run conviction scan and check entry zone!

"""
                print(alert)
                f.write(alert)
                f.write("="*70 + "\n")
        
        print(f"\n✅ Alert file: {output_file}")
        
        # Also save JSON
        json_file = output_file.replace('.txt', '.json')
        with open(json_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'clusters': clusters,
                'count': len(clusters)
            }, f, indent=2)
        
        print(f"✅ JSON file: {json_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='🐺 Realtime Form 4 Scanner')
    parser.add_argument('--scan', action='store_true', help='Scan OpenInsider for latest buys')
    parser.add_argument('--detect', action='store_true', help='Detect clusters from database')
    parser.add_argument('--days', type=int, default=14, help='Lookback days (default: 14)')
    parser.add_argument('--min-insiders', type=int, default=3, help='Min insiders (default: 3)')
    parser.add_argument('--min-value', type=int, default=100000, help='Min total value (default: 100k)')
    parser.add_argument('--watchlist', type=str, help='Filter to watchlist CSV')
    
    args = parser.parse_args()
    
    scanner = RealtimeForm4Scanner()
    
    if args.scan:
        print("\n🔥 SCANNING OPENINSIDER FOR RECENT INSIDER BUYS")
        print("="*70)
        
        df = scanner.fetch_recent_buys()
        if not df.empty:
            scanner.store_transactions(df)
    
    if args.detect or args.scan:
        print("\n🎯 DETECTING CLUSTERS")
        print("="*70)
        
        clusters = scanner.detect_clusters(
            days=args.days,
            min_insiders=args.min_insiders,
            min_total_value=args.min_value
        )
        
        if args.watchlist and clusters:
            clusters = scanner.filter_by_watchlist(clusters, args.watchlist)
        
        scanner.generate_alerts(clusters)


if __name__ == '__main__':
    main()
