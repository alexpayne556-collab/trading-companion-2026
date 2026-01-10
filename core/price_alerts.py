#!/usr/bin/env python3
"""
🐺 PRICE ALERT MONITOR - Never Miss a Move
Background monitoring with desktop notifications

SETUP:
  pip install plyer yfinance

WHAT IT DOES:
  - Monitors your watchlist tickers in background
  - Desktop popup when price targets hit
  - Desktop popup when RSI crosses thresholds
  - Desktop popup when volume spikes
  - Runs continuously, check every 60 seconds
"""

import time
import sys
from datetime import datetime
from typing import Dict, List, Optional

try:
    from plyer import notification
    import yfinance as yf
except ImportError:
    print("❌ Need: pip install plyer yfinance")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# ALERT CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

WATCHLIST = {
    # Your positions
    'APLD': {'target_price': 50.0, 'stop_price': 35.0},
    'KTOS': {'target_price': 120.0, 'stop_price': 100.0},
    'TLRY': {'target_price': 12.0, 'stop_price': 8.0},
    'NTLA': {'target_price': 12.0, 'stop_price': 9.0},
    
    # Monday AI targets
    'CIFR': {'target_price': 20.0, 'stop_price': 14.0},
    'IREN': {'target_price': 55.0, 'stop_price': 40.0},
    'RCAT': {'target_price': 15.0, 'stop_price': 10.0},
    
    # Other watchlist
    'SOUN': {'target_price': 15.0, 'stop_price': 10.0},
    'BBAI': {'target_price': 8.0, 'stop_price': 5.0},
    'SMR': {'target_price': 25.0, 'stop_price': 18.0},
    'OUST': {'target_price': 35.0, 'stop_price': 24.0},
}

# Alert thresholds
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 75
VOLUME_SPIKE_RATIO = 3.0  # 3x average volume


# ═══════════════════════════════════════════════════════════════════════════════
# NOTIFICATION SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

def send_alert(title: str, message: str, urgent: bool = False):
    """Send desktop notification"""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Wolf Pack",
            timeout=20 if urgent else 10
        )
        print(f"🔔 {title}: {message}")
    except Exception as e:
        print(f"⚠️  Alert failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# MONITORING ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class PriceMonitor:
    """Monitor prices and send alerts"""
    
    def __init__(self, watchlist: Dict[str, Dict]):
        self.watchlist = watchlist
        self.alerted = set()  # Track what we've alerted on
        self.last_prices = {}
    
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI from price series"""
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    
    def check_ticker(self, ticker: str, config: Dict):
        """Check a ticker for alert conditions"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get recent data (30 days for RSI calculation)
            hist = stock.history(period='1mo')
            if len(hist) < 15:
                return
            
            current_price = hist['Close'].iloc[-1]
            volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].mean()
            
            # Calculate RSI
            rsi = self.calculate_rsi(hist['Close'].tolist())
            
            # Track price change
            if ticker in self.last_prices:
                prev_price = self.last_prices[ticker]
                change_pct = ((current_price - prev_price) / prev_price) * 100
            else:
                change_pct = 0
            
            self.last_prices[ticker] = current_price
            
            # Check alerts
            alert_key = None
            
            # Target price hit
            if 'target_price' in config and current_price >= config['target_price']:
                alert_key = f"{ticker}_target"
                if alert_key not in self.alerted:
                    send_alert(
                        f"🎯 {ticker} HIT TARGET",
                        f"${current_price:.2f} >= ${config['target_price']:.2f}",
                        urgent=True
                    )
                    self.alerted.add(alert_key)
            
            # Stop price hit
            elif 'stop_price' in config and current_price <= config['stop_price']:
                alert_key = f"{ticker}_stop"
                if alert_key not in self.alerted:
                    send_alert(
                        f"🛑 {ticker} HIT STOP",
                        f"${current_price:.2f} <= ${config['stop_price']:.2f}",
                        urgent=True
                    )
                    self.alerted.add(alert_key)
            
            # RSI oversold
            if rsi < RSI_OVERSOLD:
                alert_key = f"{ticker}_oversold_{rsi:.0f}"
                if alert_key not in self.alerted:
                    send_alert(
                        f"📉 {ticker} OVERSOLD",
                        f"RSI {rsi:.0f} < {RSI_OVERSOLD} @ ${current_price:.2f}"
                    )
                    self.alerted.add(alert_key)
            
            # RSI overbought
            if rsi > RSI_OVERBOUGHT:
                alert_key = f"{ticker}_overbought_{rsi:.0f}"
                if alert_key not in self.alerted:
                    send_alert(
                        f"📈 {ticker} OVERBOUGHT",
                        f"RSI {rsi:.0f} > {RSI_OVERBOUGHT} @ ${current_price:.2f}"
                    )
                    self.alerted.add(alert_key)
            
            # Volume spike
            vol_ratio = volume / avg_volume if avg_volume > 0 else 1
            if vol_ratio >= VOLUME_SPIKE_RATIO:
                alert_key = f"{ticker}_volume_{vol_ratio:.1f}"
                if alert_key not in self.alerted:
                    send_alert(
                        f"⚡ {ticker} VOLUME SPIKE",
                        f"{vol_ratio:.1f}x avg @ ${current_price:.2f} ({change_pct:+.1f}%)"
                    )
                    self.alerted.add(alert_key)
            
        except Exception as e:
            print(f"⚠️  {ticker} check failed: {e}")
    
    
    def run_once(self):
        """Run one check cycle"""
        print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Checking {len(self.watchlist)} tickers...")
        
        for ticker, config in self.watchlist.items():
            self.check_ticker(ticker, config)
        
        print("   ✓ Check complete")
    
    
    def run_continuous(self, interval_seconds: int = 60):
        """Run monitoring loop"""
        print("="*70)
        print("🐺 PRICE ALERT MONITOR")
        print("="*70)
        print(f"\nMonitoring {len(self.watchlist)} tickers every {interval_seconds}s")
        print("Press Ctrl+C to stop\n")
        
        send_alert("🐺 Monitor Started", f"Watching {len(self.watchlist)} tickers")
        
        try:
            while True:
                self.run_once()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped")
            send_alert("🐺 Monitor Stopped", "Alert monitoring ended")


# ═══════════════════════════════════════════════════════════════════════════════
# QUICK ALERTS - One-time checks
# ═══════════════════════════════════════════════════════════════════════════════

def quick_check(ticker: str):
    """Quick check of a single ticker"""
    print(f"\n🔍 Checking {ticker}...")
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='5d')
        
        if len(hist) == 0:
            print(f"❌ No data for {ticker}")
            return
        
        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
        change = ((current - prev) / prev) * 100
        
        # RSI
        monitor = PriceMonitor({})
        rsi = monitor.calculate_rsi(hist['Close'].tolist())
        
        # Volume
        vol = hist['Volume'].iloc[-1]
        avg_vol = hist['Volume'].mean()
        vol_ratio = vol / avg_vol if avg_vol > 0 else 1
        
        print(f"\n  {ticker} @ ${current:.2f} ({change:+.1f}% today)")
        print(f"  RSI: {rsi:.0f}")
        print(f"  Volume: {vol_ratio:.1f}x average")
        
        # Assessment
        if rsi < 30:
            print("  ⚠️  OVERSOLD - Potential bounce")
        elif rsi > 75:
            print("  ⚠️  OVERBOUGHT - Take profits or wait")
        else:
            print("  ✅ RSI neutral")
        
        if vol_ratio > 3:
            print("  ⚡ VOLUME SPIKE - Something happening")
        
    except Exception as e:
        print(f"❌ Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='🐺 Price Alert Monitor')
    parser.add_argument('command', choices=['monitor', 'check', 'once'],
                       help='monitor=continuous, check=single ticker, once=one cycle')
    parser.add_argument('--ticker', help='Ticker for quick check')
    parser.add_argument('--interval', type=int, default=60,
                       help='Check interval in seconds (default: 60)')
    
    args = parser.parse_args()
    
    if args.command == 'monitor':
        monitor = PriceMonitor(WATCHLIST)
        monitor.run_continuous(interval_seconds=args.interval)
    
    elif args.command == 'check':
        if not args.ticker:
            print("❌ Need: --ticker SYMBOL")
            sys.exit(1)
        quick_check(args.ticker.upper())
    
    elif args.command == 'once':
        monitor = PriceMonitor(WATCHLIST)
        monitor.run_once()
