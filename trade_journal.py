#!/usr/bin/env python3
"""
🐺 TRADE JOURNAL - LEARN FROM EVERY HUNT
========================================

The wolf doesn't just hunt. The wolf LEARNS.

Every trade logged. Every thesis tracked. Every outcome analyzed.
Over time, you'll know:
- Which signals work best for YOU
- What mistakes you keep making
- When your edge is strongest
- How to improve

THE LEARNING LOOP:
1. PLAN - What's the thesis? Who's trapped?
2. EXECUTE - Enter with rules, not emotion
3. REVIEW - Did the thesis play out?
4. IMPROVE - What would you do differently?

Track:
- Entry thesis and trapped player
- Signal source (which scanner)
- Entry/exit prices and dates
- Outcome (win/loss/scratch)
- Lessons learned
- What you'd do differently

Built by Brokkr & Fenrir
AWOOOO 🐺
"""

import json
import csv
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid

# ============================================================================
# DATA STRUCTURES
# ============================================================================

class TradeStatus(Enum):
    OPEN = "open"
    CLOSED_WIN = "closed_win"
    CLOSED_LOSS = "closed_loss"
    CLOSED_SCRATCH = "closed_scratch"  # Break-even

class SignalSource(Enum):
    PRESSURE_SHORT_SQUEEZE = "Short Squeeze"
    PRESSURE_PANIC_RECOVERY = "Panic Recovery"
    PRESSURE_CAPITULATION = "Capitulation"
    PRESSURE_LAGGARD = "Laggard Catch-up"
    TACTICAL_LEADER_LAG = "Leader-Lag"
    TACTICAL_MOMENTUM = "Day 2 Momentum"
    TACTICAL_DIVERGENCE = "Divergence"
    SMART_MONEY = "Insider Buying"
    CONVICTION = "High Conviction"
    MANUAL = "Manual/Other"

@dataclass
class Trade:
    """A single trade with full context"""
    id: str
    ticker: str
    
    # Entry
    entry_date: str
    entry_price: float
    shares: int
    position_size_pct: float  # % of portfolio
    
    # Thesis
    signal_source: str
    trapped_player: str
    thesis: str
    
    # Targets
    target_price: float
    stop_price: float
    
    # Status
    status: str = "open"
    
    # Exit (filled when closed)
    exit_date: Optional[str] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None
    
    # Outcome (calculated when closed)
    pnl_dollars: Optional[float] = None
    pnl_percent: Optional[float] = None
    
    # Learning
    thesis_correct: Optional[bool] = None  # Did the thesis play out?
    followed_rules: Optional[bool] = None  # Did you follow entry/exit rules?
    lessons: Optional[str] = None
    would_do_differently: Optional[str] = None
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: str = ""

# ============================================================================
# JOURNAL MANAGER
# ============================================================================

class TradeJournal:
    """Manage the trade journal"""
    
    def __init__(self, filepath: str = 'data/trade_journal.json'):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(exist_ok=True)
        self.trades: List[Trade] = []
        self.load()
    
    def load(self):
        """Load journal from file"""
        if self.filepath.exists():
            try:
                with open(self.filepath, 'r') as f:
                    data = json.load(f)
                    self.trades = [Trade(**t) for t in data.get('trades', [])]
            except:
                self.trades = []
    
    def save(self):
        """Save journal to file"""
        data = {
            'updated': datetime.now().isoformat(),
            'total_trades': len(self.trades),
            'trades': [asdict(t) for t in self.trades]
        }
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_trade(self, trade: Trade) -> str:
        """Add a new trade to the journal"""
        self.trades.append(trade)
        self.save()
        return trade.id
    
    def get_trade(self, trade_id: str) -> Optional[Trade]:
        """Get a trade by ID"""
        for t in self.trades:
            if t.id == trade_id:
                return t
        return None
    
    def get_open_trades(self) -> List[Trade]:
        """Get all open trades"""
        return [t for t in self.trades if t.status == 'open']
    
    def get_closed_trades(self) -> List[Trade]:
        """Get all closed trades"""
        return [t for t in self.trades if t.status != 'open']
    
    def close_trade(self, trade_id: str, exit_price: float, exit_reason: str,
                    thesis_correct: bool, followed_rules: bool, 
                    lessons: str = "", would_do_differently: str = ""):
        """Close a trade and record learnings"""
        
        trade = self.get_trade(trade_id)
        if not trade:
            print(f"Trade {trade_id} not found")
            return
        
        # Calculate P&L
        pnl_dollars = (exit_price - trade.entry_price) * trade.shares
        pnl_percent = ((exit_price - trade.entry_price) / trade.entry_price) * 100
        
        # Determine status
        if pnl_percent > 0.5:
            status = 'closed_win'
        elif pnl_percent < -0.5:
            status = 'closed_loss'
        else:
            status = 'closed_scratch'
        
        # Update trade
        trade.status = status
        trade.exit_date = datetime.now().strftime('%Y-%m-%d')
        trade.exit_price = exit_price
        trade.exit_reason = exit_reason
        trade.pnl_dollars = round(pnl_dollars, 2)
        trade.pnl_percent = round(pnl_percent, 2)
        trade.thesis_correct = thesis_correct
        trade.followed_rules = followed_rules
        trade.lessons = lessons
        trade.would_do_differently = would_do_differently
        trade.updated_at = datetime.now().isoformat()
        
        self.save()
        return trade
    
    def get_stats(self) -> Dict:
        """Calculate journal statistics"""
        
        closed = self.get_closed_trades()
        
        if not closed:
            return {
                'total_trades': len(self.trades),
                'open_trades': len(self.get_open_trades()),
                'closed_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'total_pnl': 0
            }
        
        wins = [t for t in closed if t.status == 'closed_win']
        losses = [t for t in closed if t.status == 'closed_loss']
        
        total_pnl = sum(t.pnl_dollars or 0 for t in closed)
        
        avg_win = sum(t.pnl_percent or 0 for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t.pnl_percent or 0 for t in losses) / len(losses) if losses else 0
        
        gross_profit = sum(t.pnl_dollars or 0 for t in wins)
        gross_loss = abs(sum(t.pnl_dollars or 0 for t in losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Signal source breakdown
        signal_stats = {}
        for t in closed:
            source = t.signal_source
            if source not in signal_stats:
                signal_stats[source] = {'wins': 0, 'losses': 0, 'total_pnl': 0}
            
            if t.status == 'closed_win':
                signal_stats[source]['wins'] += 1
            else:
                signal_stats[source]['losses'] += 1
            signal_stats[source]['total_pnl'] += t.pnl_dollars or 0
        
        # Thesis accuracy
        thesis_correct = len([t for t in closed if t.thesis_correct])
        thesis_total = len([t for t in closed if t.thesis_correct is not None])
        thesis_accuracy = (thesis_correct / thesis_total * 100) if thesis_total > 0 else 0
        
        # Rule following
        followed_rules = len([t for t in closed if t.followed_rules])
        rules_total = len([t for t in closed if t.followed_rules is not None])
        rule_adherence = (followed_rules / rules_total * 100) if rules_total > 0 else 0
        
        return {
            'total_trades': len(self.trades),
            'open_trades': len(self.get_open_trades()),
            'closed_trades': len(closed),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': round(len(wins) / len(closed) * 100, 1) if closed else 0,
            'avg_win_pct': round(avg_win, 2),
            'avg_loss_pct': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'total_pnl': round(total_pnl, 2),
            'thesis_accuracy': round(thesis_accuracy, 1),
            'rule_adherence': round(rule_adherence, 1),
            'signal_stats': signal_stats
        }

# ============================================================================
# CLI INTERFACE
# ============================================================================

def create_trade_interactive(journal: TradeJournal):
    """Interactive trade creation"""
    
    print("\n" + "="*60)
    print("🐺 NEW TRADE ENTRY")
    print("="*60)
    
    ticker = input("\nTicker: ").upper().strip()
    entry_price = float(input("Entry Price: $"))
    shares = int(input("Shares: "))
    position_pct = float(input("Position Size (% of portfolio): "))
    
    print("\nSignal Sources:")
    for i, source in enumerate(SignalSource, 1):
        print(f"  {i}. {source.value}")
    signal_idx = int(input("Select signal source (number): ")) - 1
    signal_source = list(SignalSource)[signal_idx].value
    
    trapped_player = input("Who's trapped? (shorts/retail/institutions/none): ")
    thesis = input("Thesis (one sentence): ")
    
    target_price = float(input("Target Price: $"))
    stop_price = float(input("Stop Price: $"))
    
    notes = input("Additional notes (optional): ")
    
    trade = Trade(
        id=str(uuid.uuid4())[:8],
        ticker=ticker,
        entry_date=datetime.now().strftime('%Y-%m-%d'),
        entry_price=entry_price,
        shares=shares,
        position_size_pct=position_pct,
        signal_source=signal_source,
        trapped_player=trapped_player,
        thesis=thesis,
        target_price=target_price,
        stop_price=stop_price,
        notes=notes
    )
    
    trade_id = journal.add_trade(trade)
    
    print(f"\n✅ Trade logged: {trade_id}")
    print(f"   {ticker} | {shares} shares @ ${entry_price}")
    print(f"   Target: ${target_price} | Stop: ${stop_price}")
    
    return trade

def close_trade_interactive(journal: TradeJournal):
    """Interactive trade closing"""
    
    open_trades = journal.get_open_trades()
    
    if not open_trades:
        print("\n❌ No open trades to close")
        return
    
    print("\n" + "="*60)
    print("🐺 CLOSE TRADE")
    print("="*60)
    
    print("\nOpen trades:")
    for t in open_trades:
        print(f"  {t.id}: {t.ticker} | {t.shares} @ ${t.entry_price} | {t.entry_date}")
    
    trade_id = input("\nTrade ID to close: ").strip()
    
    trade = journal.get_trade(trade_id)
    if not trade:
        print(f"❌ Trade {trade_id} not found")
        return
    
    exit_price = float(input(f"Exit Price (entry was ${trade.entry_price}): $"))
    exit_reason = input("Exit reason: ")
    
    thesis_correct = input("Did the thesis play out? (y/n): ").lower() == 'y'
    followed_rules = input("Did you follow your rules? (y/n): ").lower() == 'y'
    
    lessons = input("What did you learn? ")
    would_do = input("What would you do differently? ")
    
    closed = journal.close_trade(
        trade_id, exit_price, exit_reason,
        thesis_correct, followed_rules, lessons, would_do
    )
    
    print(f"\n✅ Trade closed")
    print(f"   P&L: ${closed.pnl_dollars:+.2f} ({closed.pnl_percent:+.2f}%)")
    print(f"   Status: {closed.status}")

def show_stats(journal: TradeJournal):
    """Display journal statistics"""
    
    stats = journal.get_stats()
    
    print("\n" + "="*60)
    print("🐺 TRADING STATISTICS")
    print("="*60)
    
    print(f"\n📊 OVERVIEW")
    print(f"   Total Trades: {stats['total_trades']}")
    print(f"   Open: {stats['open_trades']} | Closed: {stats['closed_trades']}")
    
    if stats['closed_trades'] > 0:
        print(f"\n📈 PERFORMANCE")
        print(f"   Win Rate: {stats['win_rate']}%")
        print(f"   Wins: {stats['wins']} | Losses: {stats['losses']}")
        print(f"   Avg Win: +{stats['avg_win_pct']}%")
        print(f"   Avg Loss: {stats['avg_loss_pct']}%")
        print(f"   Profit Factor: {stats['profit_factor']}")
        print(f"   Total P&L: ${stats['total_pnl']:+,.2f}")
        
        print(f"\n🎯 DISCIPLINE")
        print(f"   Thesis Accuracy: {stats['thesis_accuracy']}%")
        print(f"   Rule Adherence: {stats['rule_adherence']}%")
        
        if stats['signal_stats']:
            print(f"\n📡 BY SIGNAL SOURCE")
            for source, data in sorted(stats['signal_stats'].items(), 
                                       key=lambda x: x[1]['total_pnl'], reverse=True):
                total = data['wins'] + data['losses']
                wr = (data['wins'] / total * 100) if total > 0 else 0
                print(f"   {source}:")
                print(f"      {data['wins']}W / {data['losses']}L ({wr:.0f}%) | ${data['total_pnl']:+,.2f}")

def show_open_trades(journal: TradeJournal):
    """Display open trades"""
    
    open_trades = journal.get_open_trades()
    
    print("\n" + "="*60)
    print("🐺 OPEN POSITIONS")
    print("="*60)
    
    if not open_trades:
        print("\n   No open trades")
        return
    
    for t in open_trades:
        days_held = (datetime.now() - datetime.fromisoformat(t.created_at)).days
        
        print(f"\n   {t.id}: {t.ticker}")
        print(f"   Entry: {t.shares} @ ${t.entry_price} on {t.entry_date}")
        print(f"   Target: ${t.target_price} | Stop: ${t.stop_price}")
        print(f"   Signal: {t.signal_source}")
        print(f"   Thesis: {t.thesis[:60]}...")
        print(f"   Days held: {days_held}")

def export_journal(journal: TradeJournal):
    """Export journal to CSV"""
    
    Path('exports').mkdir(exist_ok=True)
    
    trades = [asdict(t) for t in journal.trades]
    df = pd.DataFrame(trades)
    
    filepath = 'exports/trade_journal.csv'
    df.to_csv(filepath, index=False)
    
    print(f"\n✅ Journal exported: {filepath}")

def generate_report(journal: TradeJournal):
    """Generate markdown report"""
    
    stats = journal.get_stats()
    
    lines = [
        "# 🐺 TRADE JOURNAL REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
        "## 📊 Performance Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Trades | {stats['total_trades']} |",
        f"| Win Rate | {stats['win_rate']}% |",
        f"| Profit Factor | {stats['profit_factor']} |",
        f"| Total P&L | ${stats['total_pnl']:+,.2f} |",
        f"| Thesis Accuracy | {stats['thesis_accuracy']}% |",
        f"| Rule Adherence | {stats['rule_adherence']}% |",
        "",
        "---",
        "",
        "## 📡 Performance by Signal Source",
        "",
        "| Signal | Trades | Win Rate | P&L |",
        "|--------|--------|----------|-----|"
    ]
    
    for source, data in stats.get('signal_stats', {}).items():
        total = data['wins'] + data['losses']
        wr = (data['wins'] / total * 100) if total > 0 else 0
        lines.append(f"| {source} | {total} | {wr:.0f}% | ${data['total_pnl']:+,.2f} |")
    
    lines.extend([
        "",
        "---",
        "",
        "## 📝 Recent Trades",
        ""
    ])
    
    closed = sorted(journal.get_closed_trades(), 
                   key=lambda x: x.exit_date or '', reverse=True)[:10]
    
    for t in closed:
        emoji = "✅" if t.status == 'closed_win' else "❌"
        lines.extend([
            f"### {emoji} {t.ticker} - {t.exit_date}",
            f"**P&L:** ${t.pnl_dollars:+.2f} ({t.pnl_percent:+.2f}%)  ",
            f"**Signal:** {t.signal_source}  ",
            f"**Thesis:** {t.thesis}  ",
            f"**Lesson:** {t.lessons or 'None recorded'}  ",
            ""
        ])
    
    lines.extend([
        "---",
        "",
        "## 🎯 Key Learnings",
        ""
    ])
    
    # Extract common lessons
    lessons = [t.lessons for t in journal.get_closed_trades() if t.lessons]
    if lessons:
        for i, lesson in enumerate(lessons[-5:], 1):
            lines.append(f"{i}. {lesson}")
    else:
        lines.append("- No lessons recorded yet")
    
    lines.extend([
        "",
        "---",
        "",
        "**AWOOOO! 🐺**"
    ])
    
    Path('exports').mkdir(exist_ok=True)
    
    filepath = 'exports/journal_report.md'
    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"\n✅ Report generated: {filepath}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main CLI entry point"""
    
    journal = TradeJournal()
    
    print("\n" + "="*60)
    print("🐺 WOLF PACK TRADE JOURNAL")
    print("="*60)
    print("\nThe wolf learns from every hunt.\n")
    
    while True:
        print("\nCommands:")
        print("  1. new      - Log new trade")
        print("  2. close    - Close existing trade")
        print("  3. open     - Show open positions")
        print("  4. stats    - Show statistics")
        print("  5. report   - Generate report")
        print("  6. export   - Export to CSV")
        print("  7. quit     - Exit")
        
        cmd = input("\nCommand: ").strip().lower()
        
        if cmd in ['1', 'new']:
            create_trade_interactive(journal)
        elif cmd in ['2', 'close']:
            close_trade_interactive(journal)
        elif cmd in ['3', 'open']:
            show_open_trades(journal)
        elif cmd in ['4', 'stats']:
            show_stats(journal)
        elif cmd in ['5', 'report']:
            generate_report(journal)
        elif cmd in ['6', 'export']:
            export_journal(journal)
        elif cmd in ['7', 'quit', 'q', 'exit']:
            print("\n🐺 Happy hunting! AWOOOO!\n")
            break
        else:
            print("Unknown command")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        journal = TradeJournal()
        cmd = sys.argv[1]
        
        if cmd == 'stats':
            show_stats(journal)
        elif cmd == 'open':
            show_open_trades(journal)
        elif cmd == 'report':
            generate_report(journal)
        elif cmd == 'export':
            export_journal(journal)
        else:
            main()
    else:
        main()
