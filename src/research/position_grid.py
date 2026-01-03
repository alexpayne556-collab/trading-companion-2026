#!/usr/bin/env python3
"""
🐺 POSITION GRID MANAGER 🐺

Fenrir's POSITION GRID concept:
Instead of going all-in on one stock, maintain small positions across
all Tier 1 runners. When one runs, trim. When one is wounded, add.
Constant rotation.

Example with $1,000:
- SIDU: $200
- LUNR: $200
- RCAT: $200
- ASTS: $200
- RDW:  $200

When SIDU runs 20%, that's $40 profit. Scale out, add to wounded ones.
More consistent returns - you catch PART of every move.

Author: Brokkr (following Fenrir's doctrine)
Date: January 3, 2026
"""

import yfinance as yf
from datetime import datetime
from pathlib import Path
import json


class PositionGrid:
    """
    Manage a grid of positions across Tier 1 runners
    """
    
    # Default grid allocation (equal weight)
    DEFAULT_GRID = {
        'SIDU': 0.167,  # 16.7% each
        'LUNR': 0.167,
        'RCAT': 0.167,
        'ASTS': 0.167,
        'RDW':  0.167,
        'CLSK': 0.167,
    }
    
    # Rebalance thresholds
    TRIM_THRESHOLD = 0.25   # If position grows to 25%+ of portfolio, trim
    ADD_THRESHOLD = 0.10    # If position shrinks to 10%- of portfolio, add
    
    def __init__(self, portfolio_file: str = None):
        self.data_dir = Path('logs/portfolio')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.portfolio_file = portfolio_file or self.data_dir / 'position_grid.json'
        self.positions = self._load_positions()
    
    def _load_positions(self) -> dict:
        """Load existing positions or return empty"""
        if Path(self.portfolio_file).exists():
            with open(self.portfolio_file, 'r') as f:
                return json.load(f)
        return {'cash': 0, 'positions': {}, 'target_allocations': self.DEFAULT_GRID.copy()}
    
    def _save_positions(self):
        """Save positions to file"""
        with open(self.portfolio_file, 'w') as f:
            json.dump(self.positions, f, indent=2)
    
    def initialize_grid(self, total_capital: float, custom_grid: dict = None):
        """
        Initialize a new position grid with capital
        
        Args:
            total_capital: Total $ to allocate
            custom_grid: Optional custom allocation dict
        """
        grid = custom_grid or self.DEFAULT_GRID
        
        # Normalize allocations to sum to 1
        total_alloc = sum(grid.values())
        grid = {k: v/total_alloc for k, v in grid.items()}
        
        print(f"\n🐺 INITIALIZING POSITION GRID")
        print(f"   Total Capital: ${total_capital:,.2f}")
        print(f"   Grid Positions: {len(grid)}")
        print(f"\n   TARGET ALLOCATIONS:")
        
        positions = {}
        
        for ticker, allocation in grid.items():
            target_value = total_capital * allocation
            
            # Get current price
            try:
                stock = yf.Ticker(ticker)
                price = stock.history(period='1d')['Close'].iloc[-1]
                shares = int(target_value / price)  # Round down to whole shares
                actual_value = shares * price
                
                positions[ticker] = {
                    'shares': shares,
                    'avg_cost': round(price, 2),
                    'target_allocation': round(allocation, 3),
                    'current_price': round(price, 2),
                    'current_value': round(actual_value, 2),
                }
                
                print(f"   {ticker:6}: ${target_value:>8,.2f} ({allocation*100:.1f}%) → {shares} shares @ ${price:.2f}")
                
            except Exception as e:
                print(f"   {ticker:6}: ERROR - {e}")
                continue
        
        # Calculate remaining cash
        invested = sum(p['current_value'] for p in positions.values())
        cash = total_capital - invested
        
        self.positions = {
            'cash': round(cash, 2),
            'initial_capital': total_capital,
            'positions': positions,
            'target_allocations': grid,
            'created': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        self._save_positions()
        
        print(f"\n   INVESTED: ${invested:,.2f}")
        print(f"   CASH:     ${cash:,.2f}")
        print(f"   💾 Saved to: {self.portfolio_file}")
        
        return self.positions
    
    def update_prices(self):
        """Update current prices and calculate P&L"""
        if not self.positions.get('positions'):
            print("No positions to update. Run initialize_grid() first.")
            return
        
        print(f"\n🐺 POSITION GRID STATUS")
        print(f"   Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("\n" + "=" * 75)
        
        total_value = self.positions['cash']
        total_cost = 0
        
        rows = []
        
        for ticker, pos in self.positions['positions'].items():
            try:
                stock = yf.Ticker(ticker)
                current_price = stock.history(period='1d')['Close'].iloc[-1]
                
                # Update position
                pos['current_price'] = round(current_price, 2)
                pos['current_value'] = round(pos['shares'] * current_price, 2)
                pos['cost_basis'] = round(pos['shares'] * pos['avg_cost'], 2)
                pos['unrealized_pnl'] = round(pos['current_value'] - pos['cost_basis'], 2)
                pos['pnl_pct'] = round((pos['unrealized_pnl'] / pos['cost_basis']) * 100, 1) if pos['cost_basis'] > 0 else 0
                
                total_value += pos['current_value']
                total_cost += pos['cost_basis']
                
                rows.append(pos | {'ticker': ticker})
                
            except Exception as e:
                continue
        
        # Calculate current allocations
        for row in rows:
            row['current_allocation'] = round((row['current_value'] / total_value) * 100, 1)
            row['target_allocation_pct'] = round(self.positions['target_allocations'].get(row['ticker'], 0) * 100, 1)
            row['allocation_diff'] = round(row['current_allocation'] - row['target_allocation_pct'], 1)
        
        # Sort by P&L
        rows.sort(key=lambda x: x['pnl_pct'], reverse=True)
        
        # Print table
        print(f"{'TICKER':<8} {'SHARES':>8} {'AVG COST':>10} {'CURRENT':>10} {'VALUE':>10} {'P&L':>12} {'ALLOC':>12}")
        print("-" * 75)
        
        for row in rows:
            pnl_str = f"{row['unrealized_pnl']:+,.2f} ({row['pnl_pct']:+.1f}%)"
            alloc_str = f"{row['current_allocation']:.1f}% ({row['allocation_diff']:+.1f})"
            
            print(f"{row['ticker']:<8} {row['shares']:>8} ${row['avg_cost']:>8.2f} ${row['current_price']:>8.2f} ${row['current_value']:>8.2f} {pnl_str:>12} {alloc_str:>12}")
        
        print("-" * 75)
        
        total_pnl = total_value - self.positions['initial_capital']
        total_pnl_pct = (total_pnl / self.positions['initial_capital']) * 100
        
        print(f"{'CASH':<8} {'':<8} {'':<10} {'':<10} ${self.positions['cash']:>8.2f}")
        print(f"{'TOTAL':<8} {'':<8} {'':<10} {'':<10} ${total_value:>8.2f} {total_pnl:>+8.2f} ({total_pnl_pct:+.1f}%)")
        
        # Save updated positions
        self.positions['last_updated'] = datetime.now().isoformat()
        self.positions['total_value'] = round(total_value, 2)
        self.positions['total_pnl'] = round(total_pnl, 2)
        self.positions['total_pnl_pct'] = round(total_pnl_pct, 2)
        self._save_positions()
        
        return rows
    
    def check_rebalance_signals(self):
        """
        Check which positions need rebalancing
        
        TRIM: Position >25% of portfolio (take profits)
        ADD:  Position <10% of portfolio (buy weakness)
        """
        rows = self.update_prices()
        
        if not rows:
            return
        
        print("\n" + "=" * 75)
        print("🔄 REBALANCE SIGNALS")
        print("=" * 75)
        
        trim_signals = []
        add_signals = []
        
        for row in rows:
            current_alloc = row['current_allocation'] / 100
            target_alloc = row['target_allocation_pct'] / 100
            
            if current_alloc >= self.TRIM_THRESHOLD:
                excess_alloc = current_alloc - target_alloc
                trim_value = excess_alloc * self.positions['total_value']
                trim_signals.append({
                    'ticker': row['ticker'],
                    'action': 'TRIM',
                    'current_alloc': row['current_allocation'],
                    'target_alloc': row['target_allocation_pct'],
                    'suggested_sell': round(trim_value, 2),
                    'reason': 'Position overweight - take profits'
                })
            
            elif current_alloc <= self.ADD_THRESHOLD:
                deficit_alloc = target_alloc - current_alloc
                add_value = deficit_alloc * self.positions['total_value']
                add_signals.append({
                    'ticker': row['ticker'],
                    'action': 'ADD',
                    'current_alloc': row['current_allocation'],
                    'target_alloc': row['target_allocation_pct'],
                    'suggested_buy': round(add_value, 2),
                    'reason': 'Position underweight - buy weakness'
                })
        
        if trim_signals:
            print("\n🟢 TRIM SIGNALS (Take Profits):")
            for sig in trim_signals:
                print(f"   {sig['ticker']}: {sig['current_alloc']:.1f}% → {sig['target_alloc']:.1f}%")
                print(f"      Sell ~${sig['suggested_sell']:.2f} | {sig['reason']}")
        
        if add_signals:
            print("\n🔴 ADD SIGNALS (Buy Weakness):")
            for sig in add_signals:
                print(f"   {sig['ticker']}: {sig['current_alloc']:.1f}% → {sig['target_alloc']:.1f}%")
                print(f"      Buy ~${sig['suggested_buy']:.2f} | {sig['reason']}")
        
        if not trim_signals and not add_signals:
            print("\n   ✅ Portfolio is balanced - no action needed")
        
        return {'trim': trim_signals, 'add': add_signals}
    
    def simulate_grid(self, total_capital: float):
        """
        Simulate what a grid would look like with given capital
        (doesn't actually create positions)
        """
        print(f"\n🐺 GRID SIMULATION - ${total_capital:,.2f}")
        print("=" * 60)
        
        grid = self.DEFAULT_GRID
        
        print(f"\n{'TICKER':<8} {'ALLOC':>8} {'TARGET $':>10} {'PRICE':>10} {'SHARES':>8}")
        print("-" * 60)
        
        total_invested = 0
        
        for ticker, allocation in grid.items():
            target_value = total_capital * allocation
            
            try:
                stock = yf.Ticker(ticker)
                price = stock.history(period='1d')['Close'].iloc[-1]
                shares = int(target_value / price)
                actual_value = shares * price
                total_invested += actual_value
                
                print(f"{ticker:<8} {allocation*100:>6.1f}% ${target_value:>8,.0f} ${price:>8.2f} {shares:>8}")
                
            except Exception as e:
                print(f"{ticker:<8} {allocation*100:>6.1f}% ${target_value:>8,.0f} {'ERROR':>10}")
        
        print("-" * 60)
        print(f"{'TOTAL':<8} {'100.0':>6}% ${total_capital:>8,.0f}")
        print(f"{'INVESTED':<8} {'':<8} ${total_invested:>8,.0f}")
        print(f"{'CASH':<8} {'':<8} ${total_capital - total_invested:>8,.0f}")


def main():
    import sys
    
    grid = PositionGrid()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'init' and len(sys.argv) > 2:
            capital = float(sys.argv[2])
            grid.initialize_grid(capital)
        
        elif command == 'status':
            grid.update_prices()
        
        elif command == 'rebalance':
            grid.check_rebalance_signals()
        
        elif command == 'simulate' and len(sys.argv) > 2:
            capital = float(sys.argv[2])
            grid.simulate_grid(capital)
        
        else:
            print("Usage:")
            print("  python position_grid.py init <capital>     - Initialize grid with capital")
            print("  python position_grid.py status             - Show current positions")
            print("  python position_grid.py rebalance          - Check rebalance signals")
            print("  python position_grid.py simulate <capital> - Simulate grid allocation")
    else:
        # Default: show status or simulate
        if grid.positions.get('positions'):
            grid.check_rebalance_signals()
        else:
            print("No grid initialized. Run simulation with your capital:")
            grid.simulate_grid(1000)  # Default $1000 simulation


if __name__ == '__main__':
    main()
