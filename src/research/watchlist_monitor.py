#!/usr/bin/env python3
"""
Watchlist Monitor - Real-Time Price & Volume Alerts
Watches 59-ticker master list for breakouts and unusual activity

Alerts:
- Price moves >5% intraday
- Volume >2x average
- Crosses above/below key levels
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from pathlib import Path

class WatchlistMonitor:
    def __init__(self, watchlist_path="ATP_WOLF_PACK_MASTER.csv"):
        """Initialize monitor with watchlist"""
        self.watchlist_path = watchlist_path
        self.tickers = self._load_watchlist()
        self.baseline = {}  # Store baseline prices and volumes
        self.alerts = []
        
        print(f"🐺 Watchlist Monitor initialized with {len(self.tickers)} tickers")
    
    def _load_watchlist(self):
        """Load tickers from CSV"""
        try:
            df = pd.read_csv(self.watchlist_path)
            # Try both column name formats
            if 'Symbol' in df.columns:
                tickers = df['Symbol'].tolist()
            elif 'ticker' in df.columns:
                tickers = df['ticker'].tolist()
            else:
                tickers = df.iloc[:, 0].tolist()  # First column
            
            # Clean tickers
            tickers = [str(t).strip().upper() for t in tickers if pd.notna(t)]
            return tickers
        except Exception as e:
            print(f"❌ Error loading watchlist: {e}")
            return []
    
    def set_baseline(self):
        """
        Set baseline prices and volumes for comparison
        Called at market open or when starting monitor
        """
        print("\n📊 Setting baseline prices and volumes...")
        
        for ticker in self.tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period='5d')
                
                if hist.empty:
                    continue
                
                # Current price
                current_price = info.get('currentPrice', hist['Close'].iloc[-1])
                
                # Average volume (last 5 days)
                avg_volume = hist['Volume'].mean()
                
                # Today's open
                today_open = info.get('open', hist['Open'].iloc[-1])
                
                self.baseline[ticker] = {
                    'price': current_price,
                    'open': today_open,
                    'avg_volume': avg_volume,
                    'timestamp': datetime.now().isoformat()
                }
                
                print(f"  {ticker}: ${current_price:.2f}, Avg Vol: {avg_volume:,.0f}")
                
            except Exception as e:
                print(f"  ⚠️  {ticker}: {e}")
        
        print(f"✅ Baseline set for {len(self.baseline)} tickers")
    
    def check_alerts(self, price_threshold=5.0, volume_threshold=2.0):
        """
        Check all tickers for alert conditions
        
        Args:
            price_threshold: % move to trigger alert (default 5%)
            volume_threshold: Volume multiplier to trigger (default 2x)
        
        Returns:
            List of alerts
        """
        print(f"\n🔍 Checking {len(self.tickers)} tickers for alerts...")
        
        new_alerts = []
        
        for ticker in self.tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period='1d', interval='1m')
                
                if hist.empty:
                    continue
                
                # Current data
                current_price = info.get('currentPrice', hist['Close'].iloc[-1])
                current_volume = info.get('volume', hist['Volume'].sum())
                
                # Get baseline
                baseline = self.baseline.get(ticker, {})
                if not baseline:
                    continue
                
                baseline_price = baseline['price']
                baseline_open = baseline['open']
                avg_volume = baseline['avg_volume']
                
                # Calculate changes
                price_change_pct = ((current_price - baseline_open) / baseline_open) * 100
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
                
                # Check alert conditions
                alerts_triggered = []
                
                # Price move alert
                if abs(price_change_pct) >= price_threshold:
                    direction = "🚀 UP" if price_change_pct > 0 else "📉 DOWN"
                    alerts_triggered.append({
                        'type': 'PRICE_MOVE',
                        'message': f"{ticker} {direction} {abs(price_change_pct):.1f}%",
                        'ticker': ticker,
                        'current_price': current_price,
                        'change_pct': price_change_pct
                    })
                
                # Volume spike alert
                if volume_ratio >= volume_threshold:
                    alerts_triggered.append({
                        'type': 'VOLUME_SPIKE',
                        'message': f"{ticker} 📊 Volume {volume_ratio:.1f}x average",
                        'ticker': ticker,
                        'current_volume': current_volume,
                        'volume_ratio': volume_ratio
                    })
                
                # Combo alert (price + volume = strongest signal)
                if alerts_triggered and len(alerts_triggered) > 1:
                    combo_alert = {
                        'type': 'COMBO',
                        'message': f"🔥 {ticker} COMBO: {price_change_pct:+.1f}% + {volume_ratio:.1f}x volume",
                        'ticker': ticker,
                        'current_price': current_price,
                        'change_pct': price_change_pct,
                        'volume_ratio': volume_ratio,
                        'timestamp': datetime.now().isoformat()
                    }
                    new_alerts.append(combo_alert)
                    print(f"  🔥 {combo_alert['message']}")
                else:
                    for alert in alerts_triggered:
                        alert['timestamp'] = datetime.now().isoformat()
                        new_alerts.append(alert)
                        print(f"  ⚠️  {alert['message']}")
                
            except Exception as e:
                print(f"  ⚠️  {ticker}: {e}")
        
        self.alerts.extend(new_alerts)
        
        if not new_alerts:
            print("📭 No alerts triggered")
        else:
            print(f"\n✅ {len(new_alerts)} alerts triggered")
        
        return new_alerts
    
    def get_live_snapshot(self):
        """Get current snapshot of all tickers"""
        print("\n📸 Taking live snapshot of watchlist...")
        
        snapshot = []
        
        for ticker in self.tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                current_price = info.get('currentPrice', 0)
                volume = info.get('volume', 0)
                change_pct = info.get('regularMarketChangePercent', 0)
                
                snapshot.append({
                    'ticker': ticker,
                    'price': current_price,
                    'change_pct': change_pct,
                    'volume': volume,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"  ⚠️  {ticker}: {e}")
        
        return snapshot
    
    def continuous_monitor(self, interval_seconds=300, price_threshold=5.0, volume_threshold=2.0):
        """
        Run continuous monitoring loop
        
        Args:
            interval_seconds: Check interval (default 300 = 5 minutes)
            price_threshold: % move to alert (default 5%)
            volume_threshold: Volume multiplier to alert (default 2x)
        """
        print(f"\n🐺 Starting continuous monitor (checking every {interval_seconds}s)...")
        print(f"   Price alert: {price_threshold}%")
        print(f"   Volume alert: {volume_threshold}x average")
        print("   Press Ctrl+C to stop\n")
        
        # Set initial baseline
        self.set_baseline()
        
        try:
            while True:
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Checking alerts...")
                
                alerts = self.check_alerts(
                    price_threshold=price_threshold,
                    volume_threshold=volume_threshold
                )
                
                # Save alerts to file
                if alerts:
                    self._save_alerts(alerts)
                
                # Wait for next check
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitor stopped by user")
            print(f"📊 Total alerts generated: {len(self.alerts)}")
    
    def _save_alerts(self, alerts):
        """Save alerts to JSON file"""
        alert_file = Path("logs/watchlist_alerts.jsonl")
        alert_file.parent.mkdir(exist_ok=True)
        
        with open(alert_file, 'a') as f:
            for alert in alerts:
                f.write(json.dumps(alert) + '\n')
    
    def get_top_movers(self, limit=10):
        """Get top movers from current snapshot"""
        snapshot = self.get_live_snapshot()
        
        # Sort by absolute % change
        sorted_snapshot = sorted(
            snapshot,
            key=lambda x: abs(x['change_pct']),
            reverse=True
        )
        
        print(f"\n🏆 TOP {limit} MOVERS:")
        for i, ticker_data in enumerate(sorted_snapshot[:limit], 1):
            direction = "🚀" if ticker_data['change_pct'] > 0 else "📉"
            print(f"  {i}. {ticker_data['ticker']}: {direction} {ticker_data['change_pct']:+.2f}% "
                  f"(${ticker_data['price']:.2f})")
        
        return sorted_snapshot[:limit]


def main():
    """Command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='🐺 Watchlist Monitor')
    parser.add_argument('--watchlist', type=str, default='ATP_WOLF_PACK_MASTER.csv',
                       help='Path to watchlist CSV')
    parser.add_argument('--snapshot', action='store_true',
                       help='Take single snapshot')
    parser.add_argument('--monitor', action='store_true',
                       help='Start continuous monitoring')
    parser.add_argument('--interval', type=int, default=300,
                       help='Check interval in seconds (default: 300)')
    parser.add_argument('--price-alert', type=float, default=5.0,
                       help='Price move % to alert (default: 5.0)')
    parser.add_argument('--volume-alert', type=float, default=2.0,
                       help='Volume multiplier to alert (default: 2.0)')
    parser.add_argument('--top-movers', action='store_true',
                       help='Show top movers')
    
    args = parser.parse_args()
    
    monitor = WatchlistMonitor(watchlist_path=args.watchlist)
    
    if args.snapshot:
        snapshot = monitor.get_live_snapshot()
        print(f"\n✅ Snapshot captured: {len(snapshot)} tickers")
    
    if args.top_movers:
        monitor.get_top_movers()
    
    if args.monitor:
        monitor.continuous_monitor(
            interval_seconds=args.interval,
            price_threshold=args.price_alert,
            volume_threshold=args.volume_alert
        )


if __name__ == '__main__':
    main()
