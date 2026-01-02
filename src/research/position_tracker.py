#!/usr/bin/env python3
"""
🐺 POSITION TRACKER - Manual Position Management

Since we can't connect to Robinhood/Fidelity APIs, this tracks positions manually
Calculates P&L, stop loss proximity, and generates alerts

Author: Brokkr (Brother Mode)
Date: January 2, 2026
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import yfinance as yf


class PositionTracker:
    """
    Manual position tracking with real-time P&L
    Since broker APIs aren't available, we manage positions in JSON
    """
    
    def __init__(self):
        self.data_dir = Path('data/positions')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.positions_file = self.data_dir / 'active_positions.json'
        self.history_file = self.data_dir / 'position_history.json'
        
        self.positions = self._load_positions()
    
    def _load_positions(self) -> List[Dict]:
        """Load active positions from file"""
        if self.positions_file.exists():
            with open(self.positions_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_positions(self):
        """Save positions to file"""
        with open(self.positions_file, 'w') as f:
            json.dump(self.positions, f, indent=2)
    
    def add_position(self, 
                    ticker: str, 
                    shares: int, 
                    entry_price: float,
                    stop_loss: float = 0,
                    target1: float = 0,
                    target2: float = 0,
                    thesis: str = "",
                    broker: str = "Robinhood"):
        """Add new position"""
        
        position = {
            'ticker': ticker,
            'shares': shares,
            'entry_price': entry_price,
            'entry_date': datetime.now().isoformat(),
            'stop_loss': stop_loss,
            'target1': target1,
            'target2': target2,
            'thesis': thesis,
            'broker': broker,
            'status': 'OPEN'
        }
        
        self.positions.append(position)
        self._save_positions()
        
        print(f"✅ Added position: {ticker} ({shares} shares @ ${entry_price:.2f})")
    
    def close_position(self, ticker: str, exit_price: float, reason: str = ""):
        """Close position and move to history"""
        
        for i, pos in enumerate(self.positions):
            if pos['ticker'] == ticker and pos['status'] == 'OPEN':
                # Calculate final P&L
                pnl = (exit_price - pos['entry_price']) * pos['shares']
                pnl_pct = ((exit_price - pos['entry_price']) / pos['entry_price']) * 100
                
                # Update position
                pos['exit_price'] = exit_price
                pos['exit_date'] = datetime.now().isoformat()
                pos['pnl'] = pnl
                pos['pnl_pct'] = pnl_pct
                pos['exit_reason'] = reason
                pos['status'] = 'CLOSED'
                
                # Move to history
                self._append_to_history(pos)
                
                # Remove from active
                self.positions.pop(i)
                self._save_positions()
                
                print(f"✅ Closed position: {ticker}")
                print(f"   P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)")
                
                return pos
        
        print(f"⚠️ Position not found: {ticker}")
        return None
    
    def _append_to_history(self, position: Dict):
        """Append closed position to history"""
        history = []
        
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                history = json.load(f)
        
        history.append(position)
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_current_status(self) -> List[Dict]:
        """Get current status of all positions with live prices"""
        
        status = []
        
        for pos in self.positions:
            if pos['status'] != 'OPEN':
                continue
            
            ticker = pos['ticker']
            
            try:
                # Get current price
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Try different price fields
                current_price = (
                    info.get('currentPrice') or 
                    info.get('regularMarketPrice') or 
                    info.get('previousClose', 0)
                )
                
                # Calculate P&L
                pnl_per_share = current_price - pos['entry_price']
                pnl_total = pnl_per_share * pos['shares']
                pnl_pct = (pnl_per_share / pos['entry_price']) * 100
                
                # Calculate stop/target distances
                stop_distance_pct = 0
                if pos.get('stop_loss', 0) > 0:
                    stop_distance_pct = ((current_price - pos['stop_loss']) / current_price) * 100
                
                target1_distance_pct = 0
                if pos.get('target1', 0) > 0:
                    target1_distance_pct = ((pos['target1'] - current_price) / current_price) * 100
                
                status_dict = {
                    **pos,
                    'current_price': current_price,
                    'pnl_per_share': pnl_per_share,
                    'pnl_total': pnl_total,
                    'pnl_pct': pnl_pct,
                    'stop_distance_pct': stop_distance_pct,
                    'target1_distance_pct': target1_distance_pct,
                    'position_value': current_price * pos['shares'],
                    'timestamp': datetime.now().isoformat()
                }
                
                status.append(status_dict)
                
            except Exception as e:
                print(f"⚠️ Error getting price for {ticker}: {e}")
                continue
        
        return status
    
    def print_positions(self):
        """Print current positions"""
        status = self.get_current_status()
        
        if not status:
            print("📊 No active positions")
            return
        
        print("\n" + "=" * 70)
        print("📊 ACTIVE POSITIONS")
        print("=" * 70)
        
        total_value = 0
        total_pnl = 0
        
        for pos in status:
            emoji = '💚' if pos['pnl_pct'] > 0 else '❤️'
            
            print(f"\n{emoji} {pos['ticker']} ({pos['broker']})")
            print(f"   {pos['shares']} shares @ ${pos['entry_price']:.2f} → ${pos['current_price']:.2f}")
            print(f"   P&L: ${pos['pnl_total']:+.2f} ({pos['pnl_pct']:+.2f}%)")
            print(f"   Position Value: ${pos['position_value']:.2f}")
            
            if pos.get('stop_loss', 0) > 0:
                stop_emoji = '🚨' if pos['stop_distance_pct'] < 5 else '🛡️'
                print(f"   {stop_emoji} Stop: ${pos['stop_loss']:.2f} ({pos['stop_distance_pct']:.1f}% away)")
            
            if pos.get('target1', 0) > 0:
                target_emoji = '🎯' if pos['target1_distance_pct'] < 10 else '📍'
                print(f"   {target_emoji} Target 1: ${pos['target1']:.2f} ({pos['target1_distance_pct']:+.1f}%)")
            
            if pos.get('thesis'):
                print(f"   💡 Thesis: {pos['thesis']}")
            
            total_value += pos['position_value']
            total_pnl += pos['pnl_total']
        
        print(f"\n{'='*70}")
        print(f"💰 Total Position Value: ${total_value:.2f}")
        print(f"💵 Total P&L: ${total_pnl:+.2f}")
        print(f"{'='*70}\n")
    
    def get_alerts(self) -> List[Dict]:
        """Check for position alerts (stop loss near, targets hit)"""
        status = self.get_current_status()
        alerts = []
        
        for pos in status:
            alert_conditions = []
            
            # Stop loss proximity
            if pos.get('stop_loss', 0) > 0:
                if pos['stop_distance_pct'] < 2:
                    alert_conditions.append('🚨 STOP LOSS CRITICAL (<2%)')
                elif pos['stop_distance_pct'] < 5:
                    alert_conditions.append('⚠️ STOP LOSS NEAR (<5%)')
            
            # Target hit
            if pos.get('target1', 0) > 0:
                if pos['current_price'] >= pos['target1']:
                    alert_conditions.append('🎯 TARGET 1 HIT')
            
            if pos.get('target2', 0) > 0:
                if pos['current_price'] >= pos['target2']:
                    alert_conditions.append('🎯 TARGET 2 HIT')
            
            # Large moves
            if pos['pnl_pct'] < -10:
                alert_conditions.append('⚠️ DOWN >10%')
            
            if pos['pnl_pct'] > 20:
                alert_conditions.append('✅ UP >20%')
            
            if alert_conditions:
                alerts.append({
                    **pos,
                    'alert_conditions': alert_conditions
                })
        
        return alerts


def main():
    """CLI interface"""
    import sys
    
    tracker = PositionTracker()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'add':
            # Add position
            if len(sys.argv) < 5:
                print("Usage: python position_tracker.py add TICKER SHARES ENTRY_PRICE [STOP] [TARGET1] [TARGET2] [THESIS]")
                return
            
            ticker = sys.argv[2].upper()
            shares = int(sys.argv[3])
            entry_price = float(sys.argv[4])
            stop_loss = float(sys.argv[5]) if len(sys.argv) > 5 else 0
            target1 = float(sys.argv[6]) if len(sys.argv) > 6 else 0
            target2 = float(sys.argv[7]) if len(sys.argv) > 7 else 0
            thesis = sys.argv[8] if len(sys.argv) > 8 else ""
            
            tracker.add_position(ticker, shares, entry_price, stop_loss, target1, target2, thesis)
        
        elif command == 'close':
            # Close position
            if len(sys.argv) < 4:
                print("Usage: python position_tracker.py close TICKER EXIT_PRICE [REASON]")
                return
            
            ticker = sys.argv[2].upper()
            exit_price = float(sys.argv[3])
            reason = sys.argv[4] if len(sys.argv) > 4 else ""
            
            tracker.close_position(ticker, exit_price, reason)
        
        elif command == 'status':
            # Show status
            tracker.print_positions()
        
        elif command == 'alerts':
            # Check alerts
            alerts = tracker.get_alerts()
            
            if alerts:
                print("\n🚨 POSITION ALERTS:")
                for alert in alerts:
                    print(f"\n{alert['ticker']}:")
                    for condition in alert['alert_conditions']:
                        print(f"  {condition}")
            else:
                print("\n✅ No alerts")
    
    else:
        # Default: show status
        tracker.print_positions()


if __name__ == '__main__':
    main()
