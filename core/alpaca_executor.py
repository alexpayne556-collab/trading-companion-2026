#!/usr/bin/env python3
"""
🐺 ALPACA EXECUTOR - Turn Scanner Output Into Actual Trades
The missing piece: EXECUTION

SETUP:
1. Create Alpaca account (free): https://alpaca.markets
2. Get API keys (paper trading = safe testing)
3. pip install alpaca-trade-api
4. Set env vars: ALPACA_API_KEY, ALPACA_SECRET_KEY

This bridges the gap between "SOUN is a buy" and actually owning SOUN.
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

try:
    import alpaca_trade_api as tradeapi
except ImportError:
    print("❌ Need: pip install alpaca-trade-api")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# ALPACA CONNECTION
# ═══════════════════════════════════════════════════════════════════════════════

class AlpacaExecutor:
    """Execute trades via Alpaca API"""
    
    def __init__(self, paper=True):
        """
        Args:
            paper: True for paper trading (safe), False for live (real money)
        """
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')
        
        if not api_key or not secret_key:
            raise ValueError("Set ALPACA_API_KEY and ALPACA_SECRET_KEY env vars")
        
        base_url = 'https://paper-api.alpaca.markets' if paper else 'https://api.alpaca.markets'
        
        self.api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
        self.paper = paper
        
        # Verify connection
        try:
            account = self.api.get_account()
            print(f"✅ Connected to Alpaca ({'PAPER' if paper else 'LIVE'})")
            print(f"   Buying Power: ${float(account.buying_power):,.2f}")
            print(f"   Portfolio Value: ${float(account.portfolio_value):,.2f}")
        except Exception as e:
            raise ConnectionError(f"Alpaca connection failed: {e}")
    
    
    def get_account(self) -> Dict:
        """Get account info"""
        account = self.api.get_account()
        return {
            'buying_power': float(account.buying_power),
            'cash': float(account.cash),
            'portfolio_value': float(account.portfolio_value),
            'equity': float(account.equity),
            'paper': self.paper
        }
    
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        positions = self.api.list_positions()
        
        result = []
        for p in positions:
            result.append({
                'symbol': p.symbol,
                'qty': int(p.qty),
                'side': p.side,
                'market_value': float(p.market_value),
                'cost_basis': float(p.cost_basis),
                'unrealized_pl': float(p.unrealized_pl),
                'unrealized_plpc': float(p.unrealized_plpc) * 100,  # as percentage
                'current_price': float(p.current_price),
                'avg_entry_price': float(p.avg_entry_price)
            })
        
        return result
    
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            quote = self.api.get_latest_trade(symbol)
            return float(quote.price)
        except:
            # Fallback to last bar
            bars = self.api.get_bars(symbol, '1Min', limit=1)
            if bars:
                return float(bars[0].c)
        return 0.0
    
    
    def buy(self, symbol: str, qty: int, stop_loss_pct: float = 0.05) -> Dict:
        """
        Buy stock with automatic stop loss
        
        Args:
            symbol: Stock ticker
            qty: Number of shares
            stop_loss_pct: Stop loss percentage (0.05 = 5%)
        
        Returns:
            Order details dict
        """
        try:
            # Place market buy order
            buy_order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side='buy',
                type='market',
                time_in_force='day'
            )
            
            print(f"✅ BUY ORDER: {symbol} x{qty} @ market")
            
            # Wait a moment for fill (market orders fill fast)
            import time
            time.sleep(2)
            
            # Get fill price
            filled_order = self.api.get_order(buy_order.id)
            fill_price = float(filled_order.filled_avg_price) if filled_order.filled_avg_price else 0
            
            # Set stop loss
            if fill_price > 0 and stop_loss_pct > 0:
                stop_price = round(fill_price * (1 - stop_loss_pct), 2)
                
                stop_order = self.api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side='sell',
                    type='stop',
                    stop_price=stop_price,
                    time_in_force='gtc'  # Good til canceled
                )
                
                print(f"   Stop Loss: ${stop_price:.2f} (-{stop_loss_pct*100:.0f}%)")
                
                return {
                    'symbol': symbol,
                    'action': 'buy',
                    'qty': qty,
                    'fill_price': fill_price,
                    'stop_price': stop_price,
                    'buy_order_id': buy_order.id,
                    'stop_order_id': stop_order.id
                }
            
            return {
                'symbol': symbol,
                'action': 'buy',
                'qty': qty,
                'fill_price': fill_price,
                'buy_order_id': buy_order.id
            }
            
        except Exception as e:
            print(f"❌ BUY FAILED: {symbol} - {e}")
            return {'error': str(e)}
    
    
    def sell(self, symbol: str, qty: Optional[int] = None) -> Dict:
        """
        Sell stock (market order)
        
        Args:
            symbol: Stock ticker
            qty: Number of shares (None = sell all)
        """
        try:
            # If qty not specified, sell entire position
            if qty is None:
                position = self.api.get_position(symbol)
                qty = int(position.qty)
            
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side='sell',
                type='market',
                time_in_force='day'
            )
            
            print(f"✅ SELL ORDER: {symbol} x{qty} @ market")
            
            # Cancel any stop loss orders for this symbol
            self._cancel_stop_losses(symbol)
            
            return {
                'symbol': symbol,
                'action': 'sell',
                'qty': qty,
                'order_id': order.id
            }
            
        except Exception as e:
            print(f"❌ SELL FAILED: {symbol} - {e}")
            return {'error': str(e)}
    
    
    def _cancel_stop_losses(self, symbol: str):
        """Cancel all stop loss orders for a symbol"""
        try:
            orders = self.api.list_orders(status='open')
            for order in orders:
                if order.symbol == symbol and order.type == 'stop':
                    self.api.cancel_order(order.id)
                    print(f"   Canceled stop loss for {symbol}")
        except:
            pass
    
    
    def execute_scanner_output(self, scanner_results: List[Dict], max_positions: int = 4):
        """
        Execute trades from scanner output
        
        Args:
            scanner_results: List of dicts with {symbol, shares, entry_price}
            max_positions: Max number of positions to open
        
        Example scanner_results:
            [
                {'symbol': 'SOUN', 'shares': 8, 'entry_price': 11.75},
                {'symbol': 'BBAI', 'shares': 16, 'entry_price': 6.20},
            ]
        """
        print(f"\n🐺 EXECUTING SCANNER OUTPUT ({len(scanner_results)} candidates)")
        print("="*60)
        
        # Check current positions
        current_positions = {p['symbol'] for p in self.get_positions()}
        
        executed = 0
        for result in scanner_results:
            if executed >= max_positions:
                print(f"\n⚠️  Reached max {max_positions} positions")
                break
            
            symbol = result['symbol']
            shares = result['shares']
            
            # Skip if already own
            if symbol in current_positions:
                print(f"\n⏭️  {symbol}: Already own")
                continue
            
            # Execute
            print(f"\n{executed+1}. {symbol} - {shares} shares")
            trade_result = self.buy(symbol, shares, stop_loss_pct=0.05)
            
            if 'error' not in trade_result:
                executed += 1
        
        print(f"\n✅ Executed {executed}/{len(scanner_results)} trades")
        return executed


# ═══════════════════════════════════════════════════════════════════════════════
# PORTFOLIO TRACKER
# ═══════════════════════════════════════════════════════════════════════════════

def show_portfolio(executor: AlpacaExecutor):
    """Display current portfolio"""
    print("\n" + "="*70)
    print("📊 CURRENT PORTFOLIO")
    print("="*70)
    
    account = executor.get_account()
    positions = executor.get_positions()
    
    print(f"\n💰 ACCOUNT:")
    print(f"   Portfolio Value: ${account['portfolio_value']:,.2f}")
    print(f"   Buying Power: ${account['buying_power']:,.2f}")
    print(f"   Cash: ${account['cash']:,.2f}")
    
    if positions:
        print(f"\n📈 POSITIONS ({len(positions)}):")
        
        total_pl = sum(p['unrealized_pl'] for p in positions)
        
        for p in positions:
            pl_color = "🟢" if p['unrealized_pl'] > 0 else "🔴"
            print(f"\n  {pl_color} {p['symbol']}")
            print(f"     Qty: {p['qty']} @ ${p['avg_entry_price']:.2f}")
            print(f"     Current: ${p['current_price']:.2f}")
            print(f"     P&L: ${p['unrealized_pl']:+.2f} ({p['unrealized_plpc']:+.1f}%)")
        
        print(f"\n💵 TOTAL P&L: ${total_pl:+,.2f}")
    else:
        print("\n📭 No positions")
    
    print("\n" + "="*70)


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='🐺 Alpaca Trade Executor')
    parser.add_argument('command', choices=['status', 'portfolio', 'buy', 'sell', 'positions'],
                       help='Command to execute')
    parser.add_argument('--symbol', help='Stock symbol')
    parser.add_argument('--qty', type=int, help='Quantity')
    parser.add_argument('--live', action='store_true', help='Use live trading (default: paper)')
    
    args = parser.parse_args()
    
    # Connect
    try:
        executor = AlpacaExecutor(paper=not args.live)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nSetup:")
        print("  1. export ALPACA_API_KEY='your_key'")
        print("  2. export ALPACA_SECRET_KEY='your_secret'")
        print("  3. pip install alpaca-trade-api")
        sys.exit(1)
    
    # Execute command
    if args.command == 'status':
        account = executor.get_account()
        print(f"\n💰 Buying Power: ${account['buying_power']:,.2f}")
        print(f"📊 Portfolio Value: ${account['portfolio_value']:,.2f}")
        print(f"💵 Cash: ${account['cash']:,.2f}")
    
    elif args.command in ['portfolio', 'positions']:
        show_portfolio(executor)
    
    elif args.command == 'buy':
        if not args.symbol or not args.qty:
            print("❌ Need: --symbol TICKER --qty NUMBER")
            sys.exit(1)
        
        result = executor.buy(args.symbol, args.qty)
        if 'error' not in result:
            print(f"\n✅ Trade executed")
        else:
            print(f"\n❌ Trade failed: {result['error']}")
    
    elif args.command == 'sell':
        if not args.symbol:
            print("❌ Need: --symbol TICKER [--qty NUMBER]")
            sys.exit(1)
        
        result = executor.sell(args.symbol, args.qty)
        if 'error' not in result:
            print(f"\n✅ Trade executed")
        else:
            print(f"\n❌ Trade failed: {result['error']}")
