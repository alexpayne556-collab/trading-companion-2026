#!/usr/bin/env python3
"""
🐺 CATCH TRACKER - Learning from Every Hunt 🐺

THE PROBLEM: We see a runner, sometimes we catch it, sometimes we miss.
But we're not LEARNING from the patterns of when we catch vs miss.

THE SOLUTION: Track every trade attempt and build patterns:
1. Log when we enter, exit, win, lose
2. Track what SIGNAL triggered the trade
3. Find which entry signals have best hit rate
4. Know exactly when repeat runners are most catchable

Usage:
    python catch_tracker.py log SIDU bought 3.50 50     # Log entry
    python catch_tracker.py sold SIDU 4.00             # Log exit
    python catch_tracker.py missed SIDU "saw late"     # Log missed opportunity
    python catch_tracker.py stats                      # Show catch stats
    python catch_tracker.py patterns                   # Show winning patterns

Author: Brokkr (learning from every hunt)
Date: January 3, 2026
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import sys


class CatchTracker:
    """
    Track trades and missed opportunities to learn patterns
    """
    
    CATCH_FILE = Path('logs/catch_history.jsonl')
    PATTERNS_FILE = Path('logs/catch_patterns.json')
    
    # Known repeat runners
    REPEAT_RUNNERS = ['SIDU', 'RCAT', 'LUNR', 'ASTS', 'RDW', 'CLSK', 
                      'IONQ', 'RGTI', 'QBTS', 'QUBT', 'SMR', 'OKLO',
                      'RKLB', 'BKSY', 'AISP', 'ARQQ', 'OPTT']
    
    def __init__(self):
        self.CATCH_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.load_data()
    
    def load_data(self):
        """Load catch history"""
        self.trades = []
        
        if self.CATCH_FILE.exists():
            with open(self.CATCH_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        self.trades.append(json.loads(line))
    
    def log_entry(self, ticker: str, price: float, shares: int, signal: str = None):
        """Log a trade entry"""
        entry = {
            'type': 'entry',
            'ticker': ticker.upper(),
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M'),
            'price': price,
            'shares': shares,
            'signal': signal or 'manual',
            'day_of_week': datetime.now().strftime('%A'),
            'status': 'open'
        }
        
        self._append_log(entry)
        
        print(f"\n✅ ENTRY LOGGED: {ticker}")
        print(f"   Price: ${price:.2f} x {shares} shares")
        print(f"   Signal: {signal or 'manual'}")
        print(f"   Time: {entry['time']} on {entry['day_of_week']}")
        
        # Check if it's a repeat runner
        if ticker.upper() in self.REPEAT_RUNNERS:
            print(f"\n   🐺 This is a REPEAT RUNNER - track this one closely!")
    
    def log_exit(self, ticker: str, price: float, reason: str = None):
        """Log a trade exit"""
        # Find the open position
        open_trade = None
        for trade in reversed(self.trades):
            if (trade.get('ticker') == ticker.upper() and 
                trade.get('type') == 'entry' and 
                trade.get('status') == 'open'):
                open_trade = trade
                break
        
        if not open_trade:
            print(f"⚠️ No open position found for {ticker}")
            return
        
        # Calculate results
        entry_price = open_trade['price']
        shares = open_trade['shares']
        gain_pct = ((price - entry_price) / entry_price) * 100
        profit = (price - entry_price) * shares
        
        exit_record = {
            'type': 'exit',
            'ticker': ticker.upper(),
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M'),
            'exit_price': price,
            'entry_price': entry_price,
            'shares': shares,
            'gain_pct': round(gain_pct, 2),
            'profit': round(profit, 2),
            'signal': open_trade.get('signal'),
            'reason': reason or 'manual',
            'hold_time': self._calc_hold_time(open_trade['timestamp']),
            'won': profit > 0
        }
        
        self._append_log(exit_record)
        
        # Update entry status
        open_trade['status'] = 'closed'
        self._save_all()
        
        emoji = "🟢" if profit > 0 else "🔴"
        print(f"\n{emoji} EXIT LOGGED: {ticker}")
        print(f"   Entry: ${entry_price:.2f} → Exit: ${price:.2f}")
        print(f"   Gain: {gain_pct:+.1f}% (${profit:+.2f})")
        print(f"   Original Signal: {open_trade.get('signal', 'manual')}")
        print(f"   Hold Time: {exit_record['hold_time']}")
        
        if profit > 0:
            print(f"\n   🐺 SUCCESSFUL CATCH!")
        else:
            print(f"\n   ❌ Loss recorded. Learning opportunity.")
    
    def log_missed(self, ticker: str, reason: str, price_seen: float = None, 
                   price_went_to: float = None):
        """Log a missed opportunity"""
        missed = {
            'type': 'missed',
            'ticker': ticker.upper(),
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M'),
            'day_of_week': datetime.now().strftime('%A'),
            'reason': reason,
            'price_seen': price_seen,
            'price_went_to': price_went_to
        }
        
        if price_seen and price_went_to:
            missed['missed_gain'] = round(((price_went_to - price_seen) / price_seen) * 100, 2)
        
        self._append_log(missed)
        
        print(f"\n😤 MISSED LOGGED: {ticker}")
        print(f"   Reason: {reason}")
        
        if price_seen and price_went_to:
            missed_pct = missed['missed_gain']
            print(f"   Saw at: ${price_seen:.2f}")
            print(f"   Went to: ${price_went_to:.2f} (+{missed_pct:.1f}%)")
        
        print(f"\n   📝 This data will help catch it next time!")
    
    def _calc_hold_time(self, entry_timestamp: str) -> str:
        """Calculate how long position was held"""
        entry = datetime.fromisoformat(entry_timestamp)
        exit_time = datetime.now()
        delta = exit_time - entry
        
        if delta.days > 0:
            return f"{delta.days} days"
        elif delta.seconds >= 3600:
            return f"{delta.seconds // 3600} hours"
        else:
            return f"{delta.seconds // 60} minutes"
    
    def _append_log(self, record: dict):
        """Append record to log file"""
        with open(self.CATCH_FILE, 'a') as f:
            f.write(json.dumps(record) + '\n')
        self.trades.append(record)
    
    def _save_all(self):
        """Save all trades (for updating status)"""
        with open(self.CATCH_FILE, 'w') as f:
            for trade in self.trades:
                f.write(json.dumps(trade) + '\n')
    
    def show_stats(self):
        """Show catch statistics"""
        if not self.trades:
            print("No trades logged yet!")
            return
        
        entries = [t for t in self.trades if t['type'] == 'entry']
        exits = [t for t in self.trades if t['type'] == 'exit']
        missed = [t for t in self.trades if t['type'] == 'missed']
        
        wins = [t for t in exits if t.get('won')]
        losses = [t for t in exits if not t.get('won')]
        
        print("\n" + "🐺" * 30)
        print("   C A T C H   S T A T I S T I C S")
        print("🐺" * 30)
        
        print(f"\n📊 OVERALL STATS:")
        print(f"   Total Trades: {len(exits)}")
        print(f"   Wins: {len(wins)} | Losses: {len(losses)}")
        
        if exits:
            win_rate = (len(wins) / len(exits)) * 100
            total_profit = sum(t.get('profit', 0) for t in exits)
            avg_gain = sum(t.get('gain_pct', 0) for t in wins) / len(wins) if wins else 0
            avg_loss = sum(t.get('gain_pct', 0) for t in losses) / len(losses) if losses else 0
            
            print(f"   Win Rate: {win_rate:.1f}%")
            print(f"   Total P/L: ${total_profit:+.2f}")
            print(f"   Avg Win: +{avg_gain:.1f}% | Avg Loss: {avg_loss:.1f}%")
        
        print(f"\n😤 MISSED OPPORTUNITIES: {len(missed)}")
        if missed:
            missed_with_gains = [m for m in missed if m.get('missed_gain')]
            if missed_with_gains:
                avg_missed = sum(m['missed_gain'] for m in missed_with_gains) / len(missed_with_gains)
                print(f"   Avg Missed Gain: +{avg_missed:.1f}%")
            
            # Common reasons
            reasons = {}
            for m in missed:
                r = m.get('reason', 'unknown')
                reasons[r] = reasons.get(r, 0) + 1
            
            print(f"\n   📝 Reasons for missing:")
            for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
                print(f"      • {reason}: {count}x")
        
        # Stats by ticker
        print(f"\n📈 BY TICKER:")
        ticker_stats = {}
        for exit in exits:
            t = exit['ticker']
            if t not in ticker_stats:
                ticker_stats[t] = {'trades': 0, 'wins': 0, 'total_profit': 0}
            ticker_stats[t]['trades'] += 1
            ticker_stats[t]['total_profit'] += exit.get('profit', 0)
            if exit.get('won'):
                ticker_stats[t]['wins'] += 1
        
        for ticker, stats in sorted(ticker_stats.items(), key=lambda x: -x[1]['total_profit']):
            wr = (stats['wins'] / stats['trades']) * 100 if stats['trades'] > 0 else 0
            print(f"   {ticker}: {stats['trades']} trades, {wr:.0f}% win rate, ${stats['total_profit']:+.2f}")
    
    def show_patterns(self):
        """Analyze winning patterns"""
        exits = [t for t in self.trades if t['type'] == 'exit']
        
        if len(exits) < 3:
            print("Need at least 3 completed trades to analyze patterns!")
            return
        
        print("\n" + "🐺" * 30)
        print("   W I N N I N G   P A T T E R N S")
        print("🐺" * 30)
        
        wins = [t for t in exits if t.get('won')]
        
        # Pattern 1: Which signals work?
        print(f"\n🎯 SIGNAL PERFORMANCE:")
        signal_stats = {}
        for exit in exits:
            sig = exit.get('signal', 'manual')
            if sig not in signal_stats:
                signal_stats[sig] = {'total': 0, 'wins': 0, 'profit': 0}
            signal_stats[sig]['total'] += 1
            signal_stats[sig]['profit'] += exit.get('profit', 0)
            if exit.get('won'):
                signal_stats[sig]['wins'] += 1
        
        for sig, stats in sorted(signal_stats.items(), key=lambda x: -x[1]['profit']):
            wr = (stats['wins'] / stats['total']) * 100 if stats['total'] > 0 else 0
            print(f"   {sig}: {wr:.0f}% win rate ({stats['total']} trades, ${stats['profit']:+.2f})")
        
        # Pattern 2: Best day of week
        print(f"\n📅 BEST ENTRY DAYS:")
        day_stats = {}
        entries = [t for t in self.trades if t['type'] == 'entry']
        
        for entry in entries:
            day = entry.get('day_of_week', 'Unknown')
            if day not in day_stats:
                day_stats[day] = 0
            day_stats[day] += 1
        
        for day, count in sorted(day_stats.items(), key=lambda x: -x[1]):
            print(f"   {day}: {count} entries")
        
        # Pattern 3: Optimal hold time
        print(f"\n⏱️ HOLD TIME ANALYSIS:")
        quick_trades = [t for t in wins if 'minute' in t.get('hold_time', '')]
        day_trades = [t for t in wins if 'hour' in t.get('hold_time', '') or 'day' in t.get('hold_time', '')]
        
        if quick_trades:
            avg_quick_gain = sum(t['gain_pct'] for t in quick_trades) / len(quick_trades)
            print(f"   Quick (minutes): {len(quick_trades)} trades, avg +{avg_quick_gain:.1f}%")
        
        if day_trades:
            avg_day_gain = sum(t['gain_pct'] for t in day_trades) / len(day_trades)
            print(f"   Longer holds: {len(day_trades)} trades, avg +{avg_day_gain:.1f}%")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if signal_stats:
            best_signal = max(signal_stats.items(), key=lambda x: x[1]['profit'])
            print(f"   🎯 Best performing signal: {best_signal[0]}")
        
        if wins:
            best_ticker = max(set(t['ticker'] for t in wins), 
                            key=lambda x: sum(1 for t in wins if t['ticker'] == x))
            print(f"   🏆 Most wins with: {best_ticker}")
    
    def open_positions(self):
        """Show current open positions"""
        open_trades = [t for t in self.trades 
                      if t['type'] == 'entry' and t.get('status') == 'open']
        
        if not open_trades:
            print("\nNo open positions logged.")
            return
        
        print(f"\n📊 OPEN POSITIONS:")
        for trade in open_trades:
            print(f"   {trade['ticker']}: ${trade['price']:.2f} x {trade['shares']} shares")
            print(f"      Signal: {trade.get('signal', 'manual')}")
            print(f"      Entry: {trade['date']} at {trade['time']}")


def main():
    tracker = CatchTracker()
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python catch_tracker.py log TICKER PRICE SHARES [SIGNAL]  # Log entry")
        print("  python catch_tracker.py sold TICKER PRICE [REASON]        # Log exit")
        print("  python catch_tracker.py missed TICKER REASON [SAW] [WENT] # Log missed")
        print("  python catch_tracker.py stats                              # Show stats")
        print("  python catch_tracker.py patterns                           # Winning patterns")
        print("  python catch_tracker.py open                               # Open positions")
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'log':
        if len(sys.argv) < 5:
            print("Usage: python catch_tracker.py log TICKER PRICE SHARES [SIGNAL]")
            return
        ticker = sys.argv[2]
        price = float(sys.argv[3])
        shares = int(sys.argv[4])
        signal = sys.argv[5] if len(sys.argv) > 5 else None
        tracker.log_entry(ticker, price, shares, signal)
    
    elif cmd == 'sold':
        if len(sys.argv) < 4:
            print("Usage: python catch_tracker.py sold TICKER PRICE [REASON]")
            return
        ticker = sys.argv[2]
        price = float(sys.argv[3])
        reason = sys.argv[4] if len(sys.argv) > 4 else None
        tracker.log_exit(ticker, price, reason)
    
    elif cmd == 'missed':
        if len(sys.argv) < 4:
            print("Usage: python catch_tracker.py missed TICKER REASON [PRICE_SAW] [PRICE_WENT]")
            return
        ticker = sys.argv[2]
        reason = sys.argv[3]
        price_seen = float(sys.argv[4]) if len(sys.argv) > 4 else None
        price_went = float(sys.argv[5]) if len(sys.argv) > 5 else None
        tracker.log_missed(ticker, reason, price_seen, price_went)
    
    elif cmd == 'stats':
        tracker.show_stats()
    
    elif cmd == 'patterns':
        tracker.show_patterns()
    
    elif cmd == 'open':
        tracker.open_positions()
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == '__main__':
    main()
