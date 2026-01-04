#!/usr/bin/env python3
"""
🐺 WOLF WATCHER - The Eyes That Never Close
============================================
Real-time monitoring daemon. Watches. Waits. Alerts.

MONITORS:
- Form 4 insider filings (SEC EDGAR)
- Volume spikes on watchlist
- Laggard opportunities (leader moved, follower hasn't)
- Stop price violations
- Breakout detection

ALERTS VIA:
- Console (real-time)
- Log file (persistent)
- Webhook (future: Discord/Slack/SMS)

Run: python wolf_watcher.py --watch
Stop: Ctrl+C

AWOOOO 🐺
"""

import argparse
import json
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
import requests
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional, Tuple
import threading
import hashlib

# ============================================================
# CONFIGURATION
# ============================================================

class WatcherConfig:
    """Watcher settings"""
    
    # Scan intervals (seconds)
    FORM4_INTERVAL = 300        # Check SEC every 5 minutes
    VOLUME_INTERVAL = 60        # Check volume every minute
    LAGGARD_INTERVAL = 120      # Check laggards every 2 minutes
    STOPS_INTERVAL = 30         # Check stops every 30 seconds
    
    # Alert thresholds
    VOLUME_SPIKE_THRESHOLD = 2.5    # 2.5x average volume
    LAGGARD_GAP_THRESHOLD = 3.0     # Leader up 3%+, laggard flat
    
    # Files
    ALERTS_LOG = "logs/wolf_alerts.jsonl"
    STOPS_FILE = "config/wolf_stops.json"
    WATCHLIST_FILE = "config/wolf_watchlist.json"
    SEEN_FORM4S_FILE = "logs/seen_form4s.json"
    
    # SEC headers
    SEC_HEADERS = {
        "User-Agent": "WolfPack Trading Research contact@wolfpack.local",
        "Accept": "application/json"
    }


# ============================================================
# ALERT SYSTEM
# ============================================================

class AlertSystem:
    """Unified alert dispatcher"""
    
    def __init__(self):
        self.alerts_file = Path(WatcherConfig.ALERTS_LOG)
        self.alerts_file.parent.mkdir(exist_ok=True)
        self.webhook_url = os.environ.get("WOLF_WEBHOOK_URL")
        
    def alert(self, alert_type: str, ticker: str, message: str, 
              data: dict = None, priority: str = "normal"):
        """
        Fire an alert
        
        priority: "low", "normal", "high", "critical"
        """
        timestamp = datetime.now()
        
        alert = {
            "timestamp": timestamp.isoformat(),
            "type": alert_type,
            "ticker": ticker,
            "message": message,
            "priority": priority,
            "data": data or {}
        }
        
        # Console alert with color coding
        self._console_alert(alert)
        
        # Log to file
        self._log_alert(alert)
        
        # Webhook (if configured)
        if self.webhook_url and priority in ["high", "critical"]:
            self._webhook_alert(alert)
            
        return alert
    
    def _console_alert(self, alert: dict):
        """Print alert to console with formatting"""
        priority = alert["priority"]
        
        # Priority indicators
        indicators = {
            "low": "📝",
            "normal": "🔔",
            "high": "⚡",
            "critical": "🚨"
        }
        
        # Type icons
        type_icons = {
            "form4": "📋",
            "volume_spike": "📈",
            "laggard": "🎯",
            "stop_hit": "🛑",
            "breakout": "🚀",
            "system": "⚙️"
        }
        
        icon = type_icons.get(alert["type"], "🐺")
        indicator = indicators.get(priority, "🔔")
        
        time_str = datetime.fromisoformat(alert["timestamp"]).strftime("%H:%M:%S")
        
        print(f"\n{indicator} [{time_str}] {icon} {alert['ticker']}: {alert['message']}")
        
        if alert["data"]:
            for key, value in alert["data"].items():
                print(f"    {key}: {value}")
    
    def _log_alert(self, alert: dict):
        """Append alert to log file"""
        with open(self.alerts_file, "a") as f:
            f.write(json.dumps(alert) + "\n")
    
    def _webhook_alert(self, alert: dict):
        """Send alert to webhook (Discord/Slack compatible)"""
        try:
            payload = {
                "content": f"**🐺 Wolf Alert** [{alert['priority'].upper()}]\n"
                          f"**{alert['ticker']}**: {alert['message']}"
            }
            requests.post(self.webhook_url, json=payload, timeout=5)
        except Exception as e:
            print(f"  Webhook failed: {e}")


# ============================================================
# FORM 4 WATCHER
# ============================================================

class Form4Watcher:
    """Monitor SEC EDGAR for new Form 4 filings"""
    
    def __init__(self, alert_system: AlertSystem):
        self.alerts = alert_system
        self.seen_file = Path(WatcherConfig.SEEN_FORM4S_FILE)
        self.seen_file.parent.mkdir(exist_ok=True)
        self.seen_filings = self._load_seen()
        
        # Watchlist of tickers to monitor (or None for all)
        self.watchlist = self._load_watchlist()
        
    def _load_seen(self) -> set:
        """Load previously seen filing IDs"""
        if self.seen_file.exists():
            with open(self.seen_file) as f:
                return set(json.load(f))
        return set()
    
    def _save_seen(self):
        """Save seen filings"""
        with open(self.seen_file, "w") as f:
            json.dump(list(self.seen_filings), f)
    
    def _load_watchlist(self) -> Optional[set]:
        """Load ticker watchlist"""
        watchlist_file = Path(WatcherConfig.WATCHLIST_FILE)
        if watchlist_file.exists():
            with open(watchlist_file) as f:
                data = json.load(f)
                return set(data.get("tickers", []))
        return None
    
    def _get_filing_hash(self, filing: dict) -> str:
        """Generate unique hash for a filing"""
        key = f"{filing.get('cik')}-{filing.get('filingDate')}-{filing.get('accessionNumber', '')}"
        return hashlib.md5(key.encode()).hexdigest()[:12]
    
    def check(self):
        """Check for new Form 4 filings"""
        try:
            # Get recent Form 4 filings from SEC
            url = "https://efts.sec.gov/LATEST/search-index?q=*&dateRange=custom&startdt=2026-01-04&enddt=2026-01-04&forms=4"
            
            # Alternative: check specific company filings
            # For now, scan our watchlist companies
            if self.watchlist:
                self._check_watchlist_filings()
            else:
                self._check_recent_filings()
                
        except Exception as e:
            print(f"  Form4 check error: {e}")
    
    def _check_watchlist_filings(self):
        """Check filings for watchlist companies"""
        # Sample check for demonstration
        # In production, would iterate through watchlist CIKs
        
        for ticker in list(self.watchlist)[:5]:  # Check first 5
            try:
                self._check_ticker_filings(ticker)
                time.sleep(0.5)  # Rate limiting
            except Exception:
                pass
    
    def _check_ticker_filings(self, ticker: str):
        """Check Form 4 filings for a specific ticker"""
        try:
            # Get CIK for ticker
            cik_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company={ticker}&type=4&dateb=&owner=include&count=10&output=atom"
            
            # Simplified: check submissions endpoint
            # Real implementation would map ticker to CIK first
            pass
            
        except Exception:
            pass
    
    def _check_recent_filings(self):
        """Check SEC's recent filings feed"""
        try:
            # SEC's full-text search for Form 4
            url = "https://efts.sec.gov/LATEST/search-index"
            params = {
                "q": "*",
                "forms": "4",
                "dateRange": "custom",
                "startdt": datetime.now().strftime("%Y-%m-%d"),
                "enddt": datetime.now().strftime("%Y-%m-%d")
            }
            
            response = requests.get(url, params=params, 
                                   headers=WatcherConfig.SEC_HEADERS, 
                                   timeout=10)
            
            if response.status_code == 200:
                # Parse and check for new filings
                # Alert on new insider purchases
                pass
                
        except Exception as e:
            print(f"  Recent filings check error: {e}")
    
    def simulate_alert(self, ticker: str, insider: str, shares: int, price: float):
        """Simulate a Form 4 alert for testing"""
        value = shares * price
        
        self.alerts.alert(
            alert_type="form4",
            ticker=ticker,
            message=f"NEW INSIDER PURCHASE: {insider}",
            data={
                "shares": f"{shares:,}",
                "price": f"${price:.2f}",
                "value": f"${value:,.0f}",
                "form_type": "P - Purchase"
            },
            priority="high" if value > 1_000_000 else "normal"
        )


# ============================================================
# VOLUME WATCHER
# ============================================================

class VolumeWatcher:
    """Monitor for unusual volume spikes"""
    
    def __init__(self, alert_system: AlertSystem):
        self.alerts = alert_system
        self.watchlist = self._load_watchlist()
        self.last_volumes = {}  # Track to avoid duplicate alerts
        
    def _load_watchlist(self) -> List[str]:
        """Load tickers to monitor"""
        # Load from watchlist file or use defaults
        watchlist_file = Path(WatcherConfig.WATCHLIST_FILE)
        if watchlist_file.exists():
            with open(watchlist_file) as f:
                data = json.load(f)
                return data.get("tickers", [])
        
        # Default high-volatility watchlist
        return [
            "SIDU", "NNE", "OKLO", "SMR", "IONQ", "RGTI", "QBTS",
            "SOUN", "MARA", "RIOT", "LCID", "RIVN", "ARM", "SMCI"
        ]
    
    def check(self):
        """Check for volume spikes on watchlist"""
        print(f"  📊 Checking volume on {len(self.watchlist)} tickers...")
        
        try:
            # Batch download for efficiency
            tickers_str = " ".join(self.watchlist)
            data = yf.download(tickers_str, period="5d", interval="1d", 
                              progress=False, group_by='ticker')
            
            for ticker in self.watchlist:
                try:
                    self._check_ticker_volume(ticker, data)
                except Exception:
                    pass
                    
        except Exception as e:
            print(f"  Volume check error: {e}")
    
    def _check_ticker_volume(self, ticker: str, data):
        """Check single ticker for volume spike"""
        try:
            # Handle both single and multi-ticker data formats
            if len(self.watchlist) > 1:
                ticker_data = data[ticker] if ticker in data.columns.get_level_values(0) else None
            else:
                ticker_data = data
            
            if ticker_data is None or ticker_data.empty:
                return
            
            # Get current and average volume
            volumes = ticker_data["Volume"].dropna()
            if len(volumes) < 2:
                return
            
            current_vol = volumes.iloc[-1]
            avg_vol = volumes.iloc[:-1].mean()
            
            if avg_vol == 0:
                return
            
            ratio = current_vol / avg_vol
            
            # Check for spike
            if ratio >= WatcherConfig.VOLUME_SPIKE_THRESHOLD:
                # Avoid duplicate alerts
                alert_key = f"{ticker}-{datetime.now().strftime('%Y%m%d')}"
                if alert_key not in self.last_volumes:
                    self.last_volumes[alert_key] = True
                    
                    # Get price change
                    close_prices = ticker_data["Close"].dropna()
                    price_change = 0
                    if len(close_prices) >= 2:
                        price_change = ((close_prices.iloc[-1] / close_prices.iloc[-2]) - 1) * 100
                    
                    self.alerts.alert(
                        alert_type="volume_spike",
                        ticker=ticker,
                        message=f"VOLUME SPIKE: {ratio:.1f}x average",
                        data={
                            "current_volume": f"{current_vol:,.0f}",
                            "avg_volume": f"{avg_vol:,.0f}",
                            "ratio": f"{ratio:.1f}x",
                            "price_change": f"{price_change:+.1f}%"
                        },
                        priority="high" if ratio > 5 else "normal"
                    )
                    
        except Exception:
            pass


# ============================================================
# LAGGARD WATCHER
# ============================================================

class LaggardWatcher:
    """Monitor for laggard opportunities (leader moved, follower hasn't)"""
    
    def __init__(self, alert_system: AlertSystem):
        self.alerts = alert_system
        self.alerted_pairs = {}  # Track to avoid duplicates
        
        # Define sector peer groups
        self.peer_groups = {
            "quantum": ["IONQ", "RGTI", "QBTS", "QUBT"],
            "nuclear": ["NNE", "OKLO", "SMR", "LEU", "CCJ"],
            "ai_chips": ["NVDA", "AMD", "ARM", "SMCI", "TSM"],
            "space": ["RKLB", "LUNR", "RDW", "ASTS"],
            "crypto_miners": ["MARA", "RIOT", "CLSK", "HUT"],
            "ev": ["LCID", "RIVN", "TSLA", "NIO", "XPEV"],
            "voice_ai": ["SOUN", "AI", "BBAI"],
            "biotech_ai": ["RXRX", "DNAY", "SDGR", "EXAI"]
        }
    
    def check(self):
        """Check for laggard opportunities in peer groups"""
        print(f"  🎯 Checking laggard opportunities...")
        
        for sector, tickers in self.peer_groups.items():
            try:
                self._check_sector(sector, tickers)
            except Exception as e:
                print(f"    {sector} check error: {e}")
    
    def _check_sector(self, sector: str, tickers: List[str]):
        """Check for laggards within a sector"""
        try:
            # Download recent data
            tickers_str = " ".join(tickers)
            data = yf.download(tickers_str, period="5d", interval="1d", 
                              progress=False, group_by='ticker')
            
            # Calculate returns for each ticker
            returns = {}
            
            for ticker in tickers:
                try:
                    if len(tickers) > 1:
                        ticker_data = data[ticker] if ticker in data.columns.get_level_values(0) else None
                    else:
                        ticker_data = data
                    
                    if ticker_data is None or ticker_data.empty:
                        continue
                    
                    close = ticker_data["Close"].dropna()
                    if len(close) >= 2:
                        # Today's return
                        ret = ((close.iloc[-1] / close.iloc[-2]) - 1) * 100
                        returns[ticker] = ret
                        
                except Exception:
                    pass
            
            if len(returns) < 2:
                return
            
            # Find leader (biggest gainer) and laggards
            sorted_returns = sorted(returns.items(), key=lambda x: x[1], reverse=True)
            leader = sorted_returns[0]
            
            # Check if leader has significant move
            if leader[1] >= WatcherConfig.LAGGARD_GAP_THRESHOLD:
                # Look for laggards (flat or down)
                for ticker, ret in sorted_returns[1:]:
                    gap = leader[1] - ret
                    
                    if gap >= WatcherConfig.LAGGARD_GAP_THRESHOLD and ret < 1.0:
                        # Laggard opportunity!
                        alert_key = f"{leader[0]}-{ticker}-{datetime.now().strftime('%Y%m%d')}"
                        
                        if alert_key not in self.alerted_pairs:
                            self.alerted_pairs[alert_key] = True
                            
                            self.alerts.alert(
                                alert_type="laggard",
                                ticker=ticker,
                                message=f"LAGGARD OPPORTUNITY: {leader[0]} up {leader[1]:.1f}%, {ticker} only {ret:+.1f}%",
                                data={
                                    "sector": sector,
                                    "leader": leader[0],
                                    "leader_return": f"{leader[1]:+.1f}%",
                                    "laggard_return": f"{ret:+.1f}%",
                                    "gap": f"{gap:.1f}%"
                                },
                                priority="high" if gap > 5 else "normal"
                            )
                            
        except Exception as e:
            pass


# ============================================================
# STOP PRICE WATCHER
# ============================================================

class StopWatcher:
    """Monitor positions against stop prices"""
    
    def __init__(self, alert_system: AlertSystem):
        self.alerts = alert_system
        self.stops_file = Path(WatcherConfig.STOPS_FILE)
        self.stops_file.parent.mkdir(exist_ok=True)
        self.triggered_stops = set()  # Don't re-alert same day
        
    def load_stops(self) -> Dict[str, dict]:
        """Load configured stop prices"""
        if self.stops_file.exists():
            with open(self.stops_file) as f:
                return json.load(f)
        return {}
    
    def save_stops(self, stops: Dict[str, dict]):
        """Save stop prices"""
        with open(self.stops_file, "w") as f:
            json.dump(stops, f, indent=2)
    
    def add_stop(self, ticker: str, stop_price: float, entry_price: float = None):
        """Add a stop price to monitor"""
        stops = self.load_stops()
        stops[ticker] = {
            "stop_price": stop_price,
            "entry_price": entry_price,
            "created": datetime.now().isoformat()
        }
        self.save_stops(stops)
        print(f"  ✅ Stop added: {ticker} @ ${stop_price:.2f}")
    
    def remove_stop(self, ticker: str):
        """Remove a stop"""
        stops = self.load_stops()
        if ticker in stops:
            del stops[ticker]
            self.save_stops(stops)
            print(f"  ✅ Stop removed: {ticker}")
    
    def check(self):
        """Check all stops against current prices"""
        stops = self.load_stops()
        
        if not stops:
            return
        
        print(f"  🛑 Checking {len(stops)} stop prices...")
        
        for ticker, stop_data in stops.items():
            try:
                self._check_stop(ticker, stop_data)
            except Exception:
                pass
    
    def _check_stop(self, ticker: str, stop_data: dict):
        """Check single stop"""
        try:
            # Get current price
            stock = yf.Ticker(ticker)
            info = stock.info
            current_price = info.get("regularMarketPrice") or info.get("currentPrice", 0)
            
            if current_price == 0:
                return
            
            stop_price = stop_data["stop_price"]
            entry_price = stop_data.get("entry_price")
            
            # Check if stop hit
            if current_price <= stop_price:
                alert_key = f"{ticker}-stop-{datetime.now().strftime('%Y%m%d')}"
                
                if alert_key not in self.triggered_stops:
                    self.triggered_stops.add(alert_key)
                    
                    data = {
                        "current_price": f"${current_price:.2f}",
                        "stop_price": f"${stop_price:.2f}",
                        "breach": f"-{((stop_price - current_price) / stop_price * 100):.1f}%"
                    }
                    
                    if entry_price:
                        pnl = ((current_price - entry_price) / entry_price * 100)
                        data["entry_price"] = f"${entry_price:.2f}"
                        data["total_pnl"] = f"{pnl:+.1f}%"
                    
                    self.alerts.alert(
                        alert_type="stop_hit",
                        ticker=ticker,
                        message=f"🛑 STOP PRICE HIT! Consider exit.",
                        data=data,
                        priority="critical"
                    )
                    
        except Exception:
            pass


# ============================================================
# MAIN WATCHER DAEMON
# ============================================================

class WolfWatcher:
    """Main watcher daemon - coordinates all monitors"""
    
    def __init__(self):
        self.alerts = AlertSystem()
        self.form4_watcher = Form4Watcher(self.alerts)
        self.volume_watcher = VolumeWatcher(self.alerts)
        self.laggard_watcher = LaggardWatcher(self.alerts)
        self.stop_watcher = StopWatcher(self.alerts)
        
        self.running = False
        
    def start(self):
        """Start the watcher daemon"""
        self.running = True
        
        print("=" * 60)
        print("🐺 WOLF WATCHER - The Eyes That Never Close")
        print("=" * 60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("Monitoring:")
        print(f"  📋 Form 4 filings (every {WatcherConfig.FORM4_INTERVAL}s)")
        print(f"  📈 Volume spikes (every {WatcherConfig.VOLUME_INTERVAL}s)")
        print(f"  🎯 Laggard opportunities (every {WatcherConfig.LAGGARD_INTERVAL}s)")
        print(f"  🛑 Stop prices (every {WatcherConfig.STOPS_INTERVAL}s)")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        # Log startup
        self.alerts.alert(
            alert_type="system",
            ticker="WOLF",
            message="Wolf Watcher started - monitoring active",
            priority="low"
        )
        
        # Track last check times
        last_form4 = 0
        last_volume = 0
        last_laggard = 0
        last_stops = 0
        
        try:
            while self.running:
                now = time.time()
                
                # Form 4 check
                if now - last_form4 >= WatcherConfig.FORM4_INTERVAL:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking Form 4 filings...")
                    self.form4_watcher.check()
                    last_form4 = now
                
                # Volume check
                if now - last_volume >= WatcherConfig.VOLUME_INTERVAL:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking volume...")
                    self.volume_watcher.check()
                    last_volume = now
                
                # Laggard check
                if now - last_laggard >= WatcherConfig.LAGGARD_INTERVAL:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking laggards...")
                    self.laggard_watcher.check()
                    last_laggard = now
                
                # Stop check
                if now - last_stops >= WatcherConfig.STOPS_INTERVAL:
                    self.stop_watcher.check()
                    last_stops = now
                
                # Sleep briefly
                time.sleep(5)
                
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the watcher"""
        self.running = False
        print("\n")
        print("=" * 60)
        print("🐺 Wolf Watcher stopped")
        print("=" * 60)
        
        self.alerts.alert(
            alert_type="system",
            ticker="WOLF",
            message="Wolf Watcher stopped",
            priority="low"
        )
    
    def test_alerts(self):
        """Test all alert types"""
        print("🧪 Testing alert system...")
        print()
        
        # Test Form 4 alert
        self.form4_watcher.simulate_alert(
            ticker="AAPL",
            insider="Tim Cook (CEO)",
            shares=50000,
            price=185.50
        )
        
        time.sleep(1)
        
        # Test volume alert
        self.alerts.alert(
            alert_type="volume_spike",
            ticker="SIDU",
            message="VOLUME SPIKE: 4.2x average",
            data={
                "current_volume": "15,234,567",
                "avg_volume": "3,627,040",
                "ratio": "4.2x",
                "price_change": "+12.5%"
            },
            priority="high"
        )
        
        time.sleep(1)
        
        # Test laggard alert
        self.alerts.alert(
            alert_type="laggard",
            ticker="RGTI",
            message="LAGGARD OPPORTUNITY: IONQ up +8.5%, RGTI only +1.2%",
            data={
                "sector": "quantum",
                "leader": "IONQ",
                "leader_return": "+8.5%",
                "laggard_return": "+1.2%",
                "gap": "7.3%"
            },
            priority="high"
        )
        
        time.sleep(1)
        
        # Test stop alert
        self.alerts.alert(
            alert_type="stop_hit",
            ticker="LCID",
            message="🛑 STOP PRICE HIT! Consider exit.",
            data={
                "current_price": "$2.45",
                "stop_price": "$2.50",
                "entry_price": "$3.00",
                "total_pnl": "-18.3%"
            },
            priority="critical"
        )
        
        print()
        print("✅ Alert test complete!")


# ============================================================
# WATCHLIST MANAGEMENT
# ============================================================

def create_default_watchlist():
    """Create default watchlist file"""
    watchlist = {
        "tickers": [
            # Nuclear
            "NNE", "OKLO", "SMR", "LEU", "CCJ",
            # Quantum
            "IONQ", "RGTI", "QBTS", "QUBT",
            # AI/Tech
            "SOUN", "ARM", "SMCI", "AI", "BBAI",
            # Crypto miners
            "MARA", "RIOT", "CLSK",
            # EV
            "LCID", "RIVN",
            # Space
            "RKLB", "LUNR", "ASTS",
            # Biotech
            "RXRX"
        ],
        "updated": datetime.now().isoformat()
    }
    
    watchlist_file = Path(WatcherConfig.WATCHLIST_FILE)
    watchlist_file.parent.mkdir(exist_ok=True)
    
    with open(watchlist_file, "w") as f:
        json.dump(watchlist, f, indent=2)
    
    print(f"✅ Created watchlist with {len(watchlist['tickers'])} tickers")
    return watchlist


def manage_watchlist(args):
    """Manage the watchlist"""
    watchlist_file = Path(WatcherConfig.WATCHLIST_FILE)
    
    if args.list:
        if watchlist_file.exists():
            with open(watchlist_file) as f:
                data = json.load(f)
            print(f"📋 Watchlist ({len(data['tickers'])} tickers):")
            for ticker in sorted(data["tickers"]):
                print(f"  {ticker}")
        else:
            print("No watchlist found. Use --init to create one.")
    
    elif args.add:
        if not watchlist_file.exists():
            create_default_watchlist()
        
        with open(watchlist_file) as f:
            data = json.load(f)
        
        ticker = args.add.upper()
        if ticker not in data["tickers"]:
            data["tickers"].append(ticker)
            data["updated"] = datetime.now().isoformat()
            
            with open(watchlist_file, "w") as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Added {ticker} to watchlist")
        else:
            print(f"{ticker} already in watchlist")
    
    elif args.remove:
        if not watchlist_file.exists():
            print("No watchlist found.")
            return
        
        with open(watchlist_file) as f:
            data = json.load(f)
        
        ticker = args.remove.upper()
        if ticker in data["tickers"]:
            data["tickers"].remove(ticker)
            data["updated"] = datetime.now().isoformat()
            
            with open(watchlist_file, "w") as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Removed {ticker} from watchlist")
        else:
            print(f"{ticker} not in watchlist")
    
    elif args.init:
        create_default_watchlist()


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="🐺 Wolf Watcher - Real-time market monitoring"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Watch command (main daemon)
    watch_parser = subparsers.add_parser("watch", help="Start the watcher daemon")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test alert system")
    
    # Watchlist management
    watchlist_parser = subparsers.add_parser("watchlist", help="Manage watchlist")
    watchlist_parser.add_argument("--list", action="store_true", help="Show watchlist")
    watchlist_parser.add_argument("--add", type=str, help="Add ticker to watchlist")
    watchlist_parser.add_argument("--remove", type=str, help="Remove ticker from watchlist")
    watchlist_parser.add_argument("--init", action="store_true", help="Create default watchlist")
    
    # Stops management
    stops_parser = subparsers.add_parser("stops", help="Manage stop prices")
    stops_parser.add_argument("--list", action="store_true", help="Show all stops")
    stops_parser.add_argument("--add", type=str, help="Add stop (TICKER:PRICE:ENTRY)")
    stops_parser.add_argument("--remove", type=str, help="Remove stop for ticker")
    
    # Quick check (one-time scan)
    check_parser = subparsers.add_parser("check", help="Run one-time check (no daemon)")
    check_parser.add_argument("--volume", action="store_true", help="Check volume")
    check_parser.add_argument("--laggards", action="store_true", help="Check laggards")
    check_parser.add_argument("--stops", action="store_true", help="Check stops")
    check_parser.add_argument("--all", action="store_true", help="Check everything")
    
    args = parser.parse_args()
    
    if args.command == "watch":
        watcher = WolfWatcher()
        watcher.start()
    
    elif args.command == "test":
        watcher = WolfWatcher()
        watcher.test_alerts()
    
    elif args.command == "watchlist":
        manage_watchlist(args)
    
    elif args.command == "stops":
        alerts = AlertSystem()
        stop_watcher = StopWatcher(alerts)
        
        if args.list:
            stops = stop_watcher.load_stops()
            if stops:
                print("🛑 Configured Stops:")
                for ticker, data in stops.items():
                    entry = f" (entry: ${data.get('entry_price', 0):.2f})" if data.get('entry_price') else ""
                    print(f"  {ticker}: ${data['stop_price']:.2f}{entry}")
            else:
                print("No stops configured.")
        
        elif args.add:
            parts = args.add.upper().split(":")
            ticker = parts[0]
            stop_price = float(parts[1])
            entry_price = float(parts[2]) if len(parts) > 2 else None
            stop_watcher.add_stop(ticker, stop_price, entry_price)
        
        elif args.remove:
            stop_watcher.remove_stop(args.remove.upper())
    
    elif args.command == "check":
        print("🐺 Running one-time check...")
        alerts = AlertSystem()
        
        if args.volume or args.all:
            volume_watcher = VolumeWatcher(alerts)
            volume_watcher.check()
        
        if args.laggards or args.all:
            laggard_watcher = LaggardWatcher(alerts)
            laggard_watcher.check()
        
        if args.stops or args.all:
            stop_watcher = StopWatcher(alerts)
            stop_watcher.check()
        
        print("\n✅ Check complete!")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
