#!/usr/bin/env python3
"""
wolf_journal.py - Wolf Pack Trade Journal

Logs trades, tracks outcomes, calculates win rates.
The memory that persists between sessions.

Usage:
    python wolf_journal.py log RR 3.45 3.00 4.50 "CES humanoid demo play"
    python wolf_journal.py close RR 4.25 "Hit resistance, took profit"
    python wolf_journal.py review
    python wolf_journal.py stats
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

JOURNAL_FILE = Path(__file__).parent / "logs" / "wolf_journal.jsonl"


# ═══════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def ensure_log_dir():
    """Create logs directory if needed"""
    JOURNAL_FILE.parent.mkdir(exist_ok=True)


def log_trade(symbol: str, entry: float, stop: float, target: float, thesis: str, shares: int = 0, capital: float = 0):
    """Log a new trade entry"""
    ensure_log_dir()
    
    trade = {
        "type": "ENTRY",
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol.upper(),
        "entry_price": entry,
        "stop_price": stop,
        "target_price": target,
        "thesis": thesis,
        "shares": shares,
        "capital_deployed": capital,
        "risk_reward": round((target - entry) / (entry - stop), 2) if entry > stop else 0,
        "risk_percent": round((entry - stop) / entry * 100, 2) if entry > 0 else 0,
        "status": "OPEN"
    }
    
    with open(JOURNAL_FILE, "a") as f:
        f.write(json.dumps(trade) + "\n")
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  🐺 TRADE LOGGED                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  Symbol:     {symbol.upper():<50} ║
║  Entry:      ${entry:<49.2f} ║
║  Stop:       ${stop:<49.2f} ║
║  Target:     ${target:<49.2f} ║
║  R/R:        {trade['risk_reward']}:1{' ' * 47} ║
║  Risk:       {trade['risk_percent']:.1f}%{' ' * 48} ║
╟──────────────────────────────────────────────────────────────────╢
║  Thesis: {thesis[:55]:<55} ║
╚══════════════════════════════════════════════════════════════════╝
""")
    return trade


def close_trade(symbol: str, exit_price: float, notes: str = ""):
    """Close an existing trade and calculate outcome"""
    ensure_log_dir()
    
    # Find the most recent open trade for this symbol
    if not JOURNAL_FILE.exists():
        print(f"❌ No journal found. Nothing to close.")
        return None
    
    trades = []
    open_trade = None
    open_trade_idx = -1
    
    with open(JOURNAL_FILE, "r") as f:
        for i, line in enumerate(f):
            trade = json.loads(line)
            trades.append(trade)
            if (trade.get("symbol") == symbol.upper() and 
                trade.get("type") == "ENTRY" and 
                trade.get("status") == "OPEN"):
                open_trade = trade
                open_trade_idx = i
    
    if not open_trade:
        print(f"❌ No open trade found for {symbol.upper()}")
        return None
    
    # Calculate outcome
    entry = open_trade["entry_price"]
    pnl_percent = ((exit_price - entry) / entry) * 100
    pnl_dollars = (exit_price - entry) * open_trade.get("shares", 0)
    
    # Determine result
    if exit_price >= open_trade["target_price"]:
        result = "TARGET_HIT"
    elif exit_price <= open_trade["stop_price"]:
        result = "STOPPED_OUT"
    elif exit_price > entry:
        result = "PROFIT_TAKEN"
    else:
        result = "LOSS_TAKEN"
    
    # Log the exit
    exit_entry = {
        "type": "EXIT",
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol.upper(),
        "entry_price": entry,
        "exit_price": exit_price,
        "pnl_percent": round(pnl_percent, 2),
        "pnl_dollars": round(pnl_dollars, 2),
        "result": result,
        "notes": notes,
        "holding_period": open_trade["timestamp"]
    }
    
    # Mark original as closed
    trades[open_trade_idx]["status"] = "CLOSED"
    
    # Rewrite journal
    with open(JOURNAL_FILE, "w") as f:
        for t in trades:
            f.write(json.dumps(t) + "\n")
        f.write(json.dumps(exit_entry) + "\n")
    
    # Display result
    emoji = "🟢" if pnl_percent > 0 else "🔴"
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  {emoji} TRADE CLOSED                                              ║
╠══════════════════════════════════════════════════════════════════╣
║  Symbol:     {symbol.upper():<50} ║
║  Entry:      ${entry:<49.2f} ║
║  Exit:       ${exit_price:<49.2f} ║
║  P&L:        {pnl_percent:+.2f}%{' ' * 47} ║
║  Result:     {result:<50} ║
╟──────────────────────────────────────────────────────────────────╢
║  Notes: {notes[:55]:<56} ║
╚══════════════════════════════════════════════════════════════════╝
""")
    return exit_entry


def review_trades():
    """Review all logged trades"""
    ensure_log_dir()
    
    if not JOURNAL_FILE.exists():
        print("📔 Journal is empty. No trades logged yet.")
        return
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║  🐺 WOLF PACK TRADE JOURNAL                                       ║
╠══════════════════════════════════════════════════════════════════╣
""")
    
    with open(JOURNAL_FILE, "r") as f:
        for line in f:
            trade = json.loads(line)
            
            if trade["type"] == "ENTRY":
                status = "🟡 OPEN" if trade["status"] == "OPEN" else "⚪ CLOSED"
                print(f"║  {trade['timestamp'][:10]} | {trade['symbol']:<6} | ENTRY @ ${trade['entry_price']:.2f} | {status:<10} ║")
            
            elif trade["type"] == "EXIT":
                emoji = "🟢" if trade["pnl_percent"] > 0 else "🔴"
                print(f"║  {trade['timestamp'][:10]} | {trade['symbol']:<6} | EXIT  @ ${trade['exit_price']:.2f} | {emoji} {trade['pnl_percent']:+.2f}% ║")
    
    print("╚══════════════════════════════════════════════════════════════════╝")


def calculate_stats():
    """Calculate win rate and other statistics"""
    ensure_log_dir()
    
    if not JOURNAL_FILE.exists():
        print("📔 Journal is empty. No stats to calculate.")
        return
    
    exits = []
    with open(JOURNAL_FILE, "r") as f:
        for line in f:
            trade = json.loads(line)
            if trade["type"] == "EXIT":
                exits.append(trade)
    
    if not exits:
        print("📊 No closed trades yet. Stats will appear after first exit.")
        return
    
    total = len(exits)
    wins = sum(1 for e in exits if e["pnl_percent"] > 0)
    losses = total - wins
    
    win_rate = (wins / total) * 100 if total > 0 else 0
    
    avg_win = 0
    avg_loss = 0
    if wins > 0:
        avg_win = sum(e["pnl_percent"] for e in exits if e["pnl_percent"] > 0) / wins
    if losses > 0:
        avg_loss = sum(e["pnl_percent"] for e in exits if e["pnl_percent"] <= 0) / losses
    
    total_pnl = sum(e["pnl_percent"] for e in exits)
    
    # Results breakdown
    target_hits = sum(1 for e in exits if e["result"] == "TARGET_HIT")
    stopped_out = sum(1 for e in exits if e["result"] == "STOPPED_OUT")
    profit_taken = sum(1 for e in exits if e["result"] == "PROFIT_TAKEN")
    loss_taken = sum(1 for e in exits if e["result"] == "LOSS_TAKEN")
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  📊 WOLF PACK STATISTICS                                          ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  OVERALL                                                         ║
║  ────────────────────────────────────────────────                ║
║  Total Trades:    {total:<45} ║
║  Win Rate:        {win_rate:.1f}%{' ' * 45} ║
║  Total P&L:       {total_pnl:+.2f}%{' ' * 44} ║
║                                                                  ║
║  AVERAGES                                                        ║
║  ────────────────────────────────────────────────                ║
║  Avg Win:         {avg_win:+.2f}%{' ' * 44} ║
║  Avg Loss:        {avg_loss:+.2f}%{' ' * 44} ║
║                                                                  ║
║  RESULTS BREAKDOWN                                               ║
║  ────────────────────────────────────────────────                ║
║  🎯 Target Hit:    {target_hits:<45} ║
║  🛑 Stopped Out:   {stopped_out:<45} ║
║  💰 Profit Taken:  {profit_taken:<45} ║
║  📉 Loss Taken:    {loss_taken:<45} ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")


def add_lesson(lesson: str):
    """Add a lesson learned to the journal"""
    ensure_log_dir()
    
    entry = {
        "type": "LESSON",
        "timestamp": datetime.now().isoformat(),
        "lesson": lesson
    }
    
    with open(JOURNAL_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  📝 LESSON LOGGED                                                 ║
╠══════════════════════════════════════════════════════════════════╣
║  {lesson[:62]:<62} ║
╚══════════════════════════════════════════════════════════════════╝
""")


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="🐺 Wolf Pack Trade Journal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python wolf_journal.py log RR 3.45 3.00 4.50 "CES humanoid demo play"
  python wolf_journal.py close RR 4.25 "Hit resistance, took profit"
  python wolf_journal.py review
  python wolf_journal.py stats
  python wolf_journal.py lesson "Don't chase after 10% gap up"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Log command
    log_parser = subparsers.add_parser("log", help="Log a new trade entry")
    log_parser.add_argument("symbol", help="Stock symbol")
    log_parser.add_argument("entry", type=float, help="Entry price")
    log_parser.add_argument("stop", type=float, help="Stop loss price")
    log_parser.add_argument("target", type=float, help="Target price")
    log_parser.add_argument("thesis", help="Trade thesis")
    log_parser.add_argument("--shares", type=int, default=0, help="Number of shares")
    log_parser.add_argument("--capital", type=float, default=0, help="Capital deployed")
    
    # Close command
    close_parser = subparsers.add_parser("close", help="Close an existing trade")
    close_parser.add_argument("symbol", help="Stock symbol")
    close_parser.add_argument("exit_price", type=float, help="Exit price")
    close_parser.add_argument("notes", nargs="?", default="", help="Exit notes")
    
    # Review command
    subparsers.add_parser("review", help="Review all trades")
    
    # Stats command
    subparsers.add_parser("stats", help="Calculate statistics")
    
    # Lesson command
    lesson_parser = subparsers.add_parser("lesson", help="Log a lesson learned")
    lesson_parser.add_argument("text", help="The lesson learned")
    
    args = parser.parse_args()
    
    if args.command == "log":
        log_trade(args.symbol, args.entry, args.stop, args.target, args.thesis, args.shares, args.capital)
    elif args.command == "close":
        close_trade(args.symbol, args.exit_price, args.notes)
    elif args.command == "review":
        review_trades()
    elif args.command == "stats":
        calculate_stats()
    elif args.command == "lesson":
        add_lesson(args.text)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
