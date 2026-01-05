#!/usr/bin/env python3
"""
🐺 WOLF DEN - The Proving Ground
=================================
Paper trading that PROVES the system works.

Not just "pretend trades" - a LABORATORY where every signal lives or dies.

THREE WOLVES, EVERY TRADE:
- BROKKR: generates the signal (data)
- FENRIR: interprets the signal (strategy)  
- TYR: makes the decision (judgment)

TRACKS:
- Every signal taken → outcome
- Every signal SKIPPED → what would have happened
- Win rates by signal source
- Running P&L

After 30 days: PROOF. Real numbers. Real track record.

AWOOOO 🐺
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import yfinance as yf
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

class DenConfig:
    """Paper trading settings"""
    
    POSITIONS_FILE = "logs/den_positions.json"
    TRADES_FILE = "logs/den_trades.jsonl"
    SKIPPED_FILE = "logs/den_skipped.jsonl"
    STATS_FILE = "logs/den_stats.json"
    
    STARTING_CAPITAL = 10000.00  # Easy math
    MAX_POSITION_PCT = 0.20       # Max 20% per position


# ============================================================
# PAPER PORTFOLIO
# ============================================================

class WolfDen:
    """Paper trading portfolio manager"""
    
    def __init__(self):
        self.positions_file = Path(DenConfig.POSITIONS_FILE)
        self.trades_file = Path(DenConfig.TRADES_FILE)
        self.skipped_file = Path(DenConfig.SKIPPED_FILE)
        self.stats_file = Path(DenConfig.STATS_FILE)
        
        # Ensure directories exist
        self.positions_file.parent.mkdir(exist_ok=True)
        
        # Load or initialize portfolio
        self.portfolio = self._load_portfolio()
    
    def _load_portfolio(self) -> dict:
        """Load portfolio state"""
        if self.positions_file.exists():
            with open(self.positions_file) as f:
                return json.load(f)
        
        # Initialize new portfolio
        return {
            "cash": DenConfig.STARTING_CAPITAL,
            "positions": {},
            "created": datetime.now().isoformat(),
            "starting_capital": DenConfig.STARTING_CAPITAL
        }
    
    def _save_portfolio(self):
        """Save portfolio state"""
        with open(self.positions_file, "w") as f:
            json.dump(self.portfolio, f, indent=2)
    
    def _log_trade(self, trade: dict):
        """Log trade to history"""
        with open(self.trades_file, "a") as f:
            f.write(json.dumps(trade) + "\n")
    
    def _log_skip(self, skip: dict):
        """Log skipped signal"""
        with open(self.skipped_file, "a") as f:
            f.write(json.dumps(skip) + "\n")
    
    # ========================================
    # TRADING
    # ========================================
    
    def buy(self, ticker: str, signal_type: str, reason: str, 
            stop_pct: float = 0.10, target_pct: float = 0.20,
            size_pct: float = 0.10) -> dict:
        """
        Open a paper position.
        
        Args:
            ticker: Stock symbol
            signal_type: What triggered this (insider_buy, gamma, etc.)
            reason: Fenrir's interpretation
            stop_pct: Stop loss percentage (default 10%)
            target_pct: Take profit percentage (default 20%)
            size_pct: Position size as % of portfolio (default 10%)
        """
        ticker = ticker.upper()
        
        # Check if already have position
        if ticker in self.portfolio["positions"]:
            return {"error": f"Already have position in {ticker}"}
        
        # Get current price
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if hist.empty:
                return {"error": f"Could not get price for {ticker}"}
            
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)
            
            current_price = hist["Close"].iloc[-1]
        except Exception as e:
            return {"error": f"Price fetch failed: {e}"}
        
        # Calculate position size
        portfolio_value = self._get_portfolio_value()
        max_position = portfolio_value * min(size_pct, DenConfig.MAX_POSITION_PCT)
        
        if max_position > self.portfolio["cash"]:
            max_position = self.portfolio["cash"]
        
        shares = int(max_position / current_price)
        
        if shares == 0:
            return {"error": "Insufficient capital for even 1 share"}
        
        cost = shares * current_price
        
        # Calculate stops and targets
        stop_price = current_price * (1 - stop_pct)
        target_price = current_price * (1 + target_pct)
        
        # Create position
        position = {
            "ticker": ticker,
            "shares": shares,
            "entry_price": current_price,
            "entry_date": datetime.now().isoformat(),
            "cost_basis": cost,
            "signal_type": signal_type,
            "reason": reason,
            "stop_price": stop_price,
            "target_price": target_price,
            "status": "open"
        }
        
        # Update portfolio
        self.portfolio["cash"] -= cost
        self.portfolio["positions"][ticker] = position
        self._save_portfolio()
        
        # Log trade
        trade = {
            "action": "BUY",
            "ticker": ticker,
            "shares": shares,
            "price": current_price,
            "cost": cost,
            "signal_type": signal_type,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        self._log_trade(trade)
        
        print(f"✅ BOUGHT {ticker}")
        print(f"   Shares: {shares} @ ${current_price:.2f}")
        print(f"   Cost: ${cost:.2f}")
        print(f"   Stop: ${stop_price:.2f} ({stop_pct*100:.0f}%)")
        print(f"   Target: ${target_price:.2f} ({target_pct*100:.0f}%)")
        print(f"   Signal: {signal_type}")
        
        return position
    
    def sell(self, ticker: str, reason: str = "manual") -> dict:
        """Close a paper position"""
        ticker = ticker.upper()
        
        if ticker not in self.portfolio["positions"]:
            return {"error": f"No position in {ticker}"}
        
        position = self.portfolio["positions"][ticker]
        
        # Get current price
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)
            current_price = hist["Close"].iloc[-1]
        except Exception as e:
            return {"error": f"Price fetch failed: {e}"}
        
        # Calculate P&L
        proceeds = position["shares"] * current_price
        pnl = proceeds - position["cost_basis"]
        pnl_pct = (current_price / position["entry_price"] - 1) * 100
        
        # Calculate hold time
        entry_date = datetime.fromisoformat(position["entry_date"])
        hold_days = (datetime.now() - entry_date).days
        
        # Update portfolio
        self.portfolio["cash"] += proceeds
        del self.portfolio["positions"][ticker]
        self._save_portfolio()
        
        # Log trade
        trade = {
            "action": "SELL",
            "ticker": ticker,
            "shares": position["shares"],
            "entry_price": position["entry_price"],
            "exit_price": current_price,
            "proceeds": proceeds,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "hold_days": hold_days,
            "signal_type": position["signal_type"],
            "exit_reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        self._log_trade(trade)
        
        result_icon = "🟢" if pnl > 0 else "🔴"
        print(f"{result_icon} SOLD {ticker}")
        print(f"   Shares: {position['shares']} @ ${current_price:.2f}")
        print(f"   P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%)")
        print(f"   Hold: {hold_days} days")
        print(f"   Reason: {reason}")
        
        return trade
    
    def skip(self, ticker: str, signal_type: str, reason: str):
        """Record a skipped signal (to track what would have happened)"""
        ticker = ticker.upper()
        
        # Get current price for later comparison
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)
            current_price = hist["Close"].iloc[-1]
        except:
            current_price = 0
        
        skip = {
            "ticker": ticker,
            "signal_type": signal_type,
            "reason": reason,
            "price_at_skip": current_price,
            "timestamp": datetime.now().isoformat()
        }
        
        self._log_skip(skip)
        
        print(f"📝 SKIPPED {ticker}")
        print(f"   Signal: {signal_type}")
        print(f"   Reason: {reason}")
        print(f"   Price: ${current_price:.2f}")
    
    # ========================================
    # MONITORING
    # ========================================
    
    def check_stops_and_targets(self) -> List[dict]:
        """Check all positions against stops and targets"""
        alerts = []
        
        for ticker, position in self.portfolio["positions"].items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1d")
                if isinstance(hist.columns, pd.MultiIndex):
                    hist.columns = hist.columns.get_level_values(0)
                current_price = hist["Close"].iloc[-1]
                
                # Check stop
                if current_price <= position["stop_price"]:
                    alerts.append({
                        "ticker": ticker,
                        "alert": "STOP HIT",
                        "price": current_price,
                        "stop": position["stop_price"]
                    })
                
                # Check target
                if current_price >= position["target_price"]:
                    alerts.append({
                        "ticker": ticker,
                        "alert": "TARGET HIT",
                        "price": current_price,
                        "target": position["target_price"]
                    })
                    
            except Exception:
                pass
        
        return alerts
    
    def update_skipped(self) -> List[dict]:
        """Update what happened to skipped signals"""
        if not self.skipped_file.exists():
            return []
        
        updates = []
        
        with open(self.skipped_file) as f:
            skips = [json.loads(line) for line in f if line.strip()]
        
        for skip in skips[-20:]:  # Last 20 skips
            if "outcome" in skip:
                continue  # Already updated
            
            try:
                stock = yf.Ticker(skip["ticker"])
                hist = stock.history(period="1d")
                if isinstance(hist.columns, pd.MultiIndex):
                    hist.columns = hist.columns.get_level_values(0)
                current_price = hist["Close"].iloc[-1]
                
                skip_price = skip.get("price_at_skip", 0)
                if skip_price > 0:
                    change = (current_price / skip_price - 1) * 100
                    
                    updates.append({
                        "ticker": skip["ticker"],
                        "signal": skip["signal_type"],
                        "skip_price": skip_price,
                        "current_price": current_price,
                        "change": change,
                        "would_have_been": f"${change*0.1:.2f}" if change > 0 else f"${change*0.1:.2f}"
                    })
            except:
                pass
        
        return updates
    
    # ========================================
    # PORTFOLIO VIEW
    # ========================================
    
    def _get_portfolio_value(self) -> float:
        """Calculate total portfolio value"""
        total = self.portfolio["cash"]
        
        for ticker, position in self.portfolio["positions"].items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1d")
                if isinstance(hist.columns, pd.MultiIndex):
                    hist.columns = hist.columns.get_level_values(0)
                current_price = hist["Close"].iloc[-1]
                total += position["shares"] * current_price
            except:
                total += position["cost_basis"]
        
        return total
    
    def status(self) -> dict:
        """Get portfolio status"""
        portfolio_value = self._get_portfolio_value()
        starting = self.portfolio["starting_capital"]
        total_return = (portfolio_value / starting - 1) * 100
        
        positions_detail = []
        
        for ticker, position in self.portfolio["positions"].items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1d")
                if isinstance(hist.columns, pd.MultiIndex):
                    hist.columns = hist.columns.get_level_values(0)
                current_price = hist["Close"].iloc[-1]
                
                pnl = (current_price - position["entry_price"]) / position["entry_price"] * 100
                value = position["shares"] * current_price
                
                positions_detail.append({
                    "ticker": ticker,
                    "shares": position["shares"],
                    "entry": position["entry_price"],
                    "current": current_price,
                    "pnl_pct": pnl,
                    "value": value,
                    "signal": position["signal_type"],
                    "stop": position["stop_price"],
                    "target": position["target_price"]
                })
            except:
                pass
        
        # Get trade stats
        stats = self._calculate_stats()
        
        return {
            "portfolio_value": portfolio_value,
            "cash": self.portfolio["cash"],
            "starting_capital": starting,
            "total_return_pct": total_return,
            "positions": positions_detail,
            "stats": stats
        }
    
    def _calculate_stats(self) -> dict:
        """Calculate trading statistics"""
        if not self.trades_file.exists():
            return {}
        
        with open(self.trades_file) as f:
            trades = [json.loads(line) for line in f if line.strip()]
        
        # Filter to completed trades (sells)
        sells = [t for t in trades if t.get("action") == "SELL"]
        
        if not sells:
            return {"trades": 0}
        
        wins = [t for t in sells if t.get("pnl", 0) > 0]
        losses = [t for t in sells if t.get("pnl", 0) <= 0]
        
        win_rate = len(wins) / len(sells) * 100 if sells else 0
        avg_win = sum(t["pnl_pct"] for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t["pnl_pct"] for t in losses) / len(losses) if losses else 0
        
        # By signal type
        by_signal = {}
        for t in sells:
            sig = t.get("signal_type", "unknown")
            if sig not in by_signal:
                by_signal[sig] = {"wins": 0, "losses": 0, "pnl": 0}
            
            if t.get("pnl", 0) > 0:
                by_signal[sig]["wins"] += 1
            else:
                by_signal[sig]["losses"] += 1
            by_signal[sig]["pnl"] += t.get("pnl", 0)
        
        return {
            "total_trades": len(sells),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": win_rate,
            "avg_win_pct": avg_win,
            "avg_loss_pct": avg_loss,
            "by_signal": by_signal
        }
    
    def display_status(self):
        """Display portfolio status"""
        status = self.status()
        
        print("=" * 70)
        print("🐺 WOLF DEN - Paper Trading Status")
        print("=" * 70)
        print()
        
        return_icon = "🟢" if status["total_return_pct"] > 0 else "🔴"
        print(f"💰 Portfolio Value: ${status['portfolio_value']:,.2f}")
        print(f"💵 Cash: ${status['cash']:,.2f}")
        print(f"{return_icon} Total Return: {status['total_return_pct']:+.2f}%")
        print()
        
        if status["positions"]:
            print("📊 OPEN POSITIONS:")
            print("-" * 70)
            print(f"{'Ticker':<8} {'Shares':>8} {'Entry':>10} {'Current':>10} {'P&L':>8} {'Signal':<15}")
            print("-" * 70)
            
            for pos in status["positions"]:
                pnl_icon = "🟢" if pos["pnl_pct"] > 0 else "🔴"
                print(f"{pos['ticker']:<8} {pos['shares']:>8} ${pos['entry']:>8.2f} ${pos['current']:>8.2f} "
                      f"{pnl_icon}{pos['pnl_pct']:>+6.1f}% {pos['signal']:<15}")
        else:
            print("📊 No open positions")
        
        print()
        
        stats = status.get("stats", {})
        if stats.get("total_trades", 0) > 0:
            print("📈 TRADING STATS:")
            print("-" * 40)
            print(f"  Total Trades: {stats['total_trades']}")
            print(f"  Win Rate: {stats['win_rate']:.1f}%")
            print(f"  Avg Win: {stats['avg_win_pct']:+.1f}%")
            print(f"  Avg Loss: {stats['avg_loss_pct']:+.1f}%")
            
            if stats.get("by_signal"):
                print()
                print("  By Signal Type:")
                for sig, data in stats["by_signal"].items():
                    total = data["wins"] + data["losses"]
                    wr = data["wins"] / total * 100 if total > 0 else 0
                    print(f"    {sig}: {data['wins']}/{total} ({wr:.0f}%) | ${data['pnl']:+.2f}")
        
        print()
        print("=" * 70)
        
        # Check alerts
        alerts = self.check_stops_and_targets()
        if alerts:
            print()
            print("🚨 ALERTS:")
            for alert in alerts:
                print(f"  {alert['ticker']}: {alert['alert']}!")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="🐺 Wolf Den - Paper trading proving ground"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show portfolio status")
    
    # Buy command
    buy_parser = subparsers.add_parser("buy", help="Open paper position")
    buy_parser.add_argument("ticker", type=str, help="Ticker symbol")
    buy_parser.add_argument("--signal", type=str, required=True, help="Signal type")
    buy_parser.add_argument("--reason", type=str, default="", help="Fenrir's interpretation")
    buy_parser.add_argument("--stop", type=float, default=0.10, help="Stop loss %")
    buy_parser.add_argument("--target", type=float, default=0.20, help="Target %")
    buy_parser.add_argument("--size", type=float, default=0.10, help="Position size %")
    
    # Sell command
    sell_parser = subparsers.add_parser("sell", help="Close paper position")
    sell_parser.add_argument("ticker", type=str, help="Ticker symbol")
    sell_parser.add_argument("--reason", type=str, default="manual", help="Exit reason")
    
    # Skip command
    skip_parser = subparsers.add_parser("skip", help="Record skipped signal")
    skip_parser.add_argument("ticker", type=str, help="Ticker symbol")
    skip_parser.add_argument("--signal", type=str, required=True, help="Signal type")
    skip_parser.add_argument("--reason", type=str, required=True, help="Why skipped")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check stops/targets")
    
    # Skipped command
    skipped_parser = subparsers.add_parser("skipped", help="Review skipped signals")
    
    # Reset command
    reset_parser = subparsers.add_parser("reset", help="Reset paper account")
    reset_parser.add_argument("--confirm", action="store_true", help="Confirm reset")
    
    args = parser.parse_args()
    
    den = WolfDen()
    
    if args.command == "status":
        den.display_status()
    
    elif args.command == "buy":
        den.buy(
            args.ticker,
            args.signal,
            args.reason,
            stop_pct=args.stop,
            target_pct=args.target,
            size_pct=args.size
        )
    
    elif args.command == "sell":
        den.sell(args.ticker, args.reason)
    
    elif args.command == "skip":
        den.skip(args.ticker, args.signal, args.reason)
    
    elif args.command == "check":
        alerts = den.check_stops_and_targets()
        if alerts:
            print("🚨 ALERTS:")
            for alert in alerts:
                print(f"  {alert['ticker']}: {alert['alert']} @ ${alert['price']:.2f}")
        else:
            print("✅ No stops or targets hit")
    
    elif args.command == "skipped":
        updates = den.update_skipped()
        if updates:
            print("📋 SKIPPED SIGNALS UPDATE:")
            print("-" * 50)
            for u in updates:
                icon = "😤" if u["change"] > 5 else "✓" if u["change"] < -5 else "➖"
                print(f"  {icon} {u['ticker']}: {u['change']:+.1f}% (was {u['signal']})")
        else:
            print("No skipped signals to review")
    
    elif args.command == "reset":
        if args.confirm:
            for f in [den.positions_file, den.trades_file, den.skipped_file]:
                if f.exists():
                    f.unlink()
            print("🔄 Paper account reset to $10,000")
        else:
            print("Add --confirm to reset account")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
