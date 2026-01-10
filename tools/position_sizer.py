#!/usr/bin/env python3
"""
🐺 POSITION SIZER - Right-Size Your Bets
=========================================

FENRIR'S RULES:
- Max 20% of portfolio per position
- Max 3-4 positions at a time
- Keep 30-50% cash for opportunities
- Stop loss: -10% to -12%

THE MATH:
With $1,327 and PDT restrictions (3 day trades/5 days):
- Swing trade focus (hold overnight)
- Position size matters MORE when you can't cut losses quickly

USAGE:
    python position_sizer.py --ticker USAR --conviction high
    python position_sizer.py --portfolio          # Show current allocation
    python position_sizer.py --what-if UUUU 100   # What if UUUU hits $100?
"""

import argparse
import yfinance as yf
from datetime import datetime


# Tyr's current portfolio
PORTFOLIO = {
    "cash_rh": 363,
    "cash_fidelity": 500,
    "positions": {
        "AISP": {"shares": 89, "entry": 3.27, "account": "RH"},
        "UUUU": {"shares": 5, "entry": 18.50, "account": "RH"},
        "USAR": {"shares": 5, "entry": 14.15, "account": "RH"},
    }
}


def get_current_price(ticker: str) -> float:
    """Get current price for a ticker."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if not hist.empty:
            return hist['Close'].iloc[-1]
    except:
        pass
    return None


def calculate_portfolio_value():
    """Calculate total portfolio value and allocation."""
    positions_value = 0
    position_details = []
    
    for ticker, pos in PORTFOLIO["positions"].items():
        current_price = get_current_price(ticker)
        if current_price:
            value = pos["shares"] * current_price
            gain_pct = ((current_price - pos["entry"]) / pos["entry"]) * 100
            positions_value += value
            position_details.append({
                "ticker": ticker,
                "shares": pos["shares"],
                "entry": pos["entry"],
                "current": round(current_price, 2),
                "value": round(value, 2),
                "gain_pct": round(gain_pct, 2),
                "account": pos["account"],
            })
    
    total_cash = PORTFOLIO["cash_rh"] + PORTFOLIO["cash_fidelity"]
    total_value = positions_value + total_cash
    
    return {
        "total_value": round(total_value, 2),
        "positions_value": round(positions_value, 2),
        "cash": total_cash,
        "cash_rh": PORTFOLIO["cash_rh"],
        "cash_fidelity": PORTFOLIO["cash_fidelity"],
        "positions": position_details,
        "cash_pct": round((total_cash / total_value) * 100, 1),
        "invested_pct": round((positions_value / total_value) * 100, 1),
    }


def show_portfolio():
    """Display current portfolio allocation."""
    portfolio = calculate_portfolio_value()
    
    print("\n" + "="*60)
    print("🐺 TYR'S PORTFOLIO - CURRENT ALLOCATION")
    print("="*60)
    print(f"\nTotal Portfolio: ${portfolio['total_value']:,.2f}")
    print(f"├── Invested: ${portfolio['positions_value']:,.2f} ({portfolio['invested_pct']}%)")
    print(f"└── Cash: ${portfolio['cash']:,.2f} ({portfolio['cash_pct']}%)")
    print(f"    ├── Robinhood: ${portfolio['cash_rh']:,.2f}")
    print(f"    └── Fidelity: ${portfolio['cash_fidelity']:,.2f}")
    
    print("\n" + "-"*60)
    print(f"{'TICKER':<8} {'SHARES':>6} {'ENTRY':>8} {'CURRENT':>8} {'VALUE':>10} {'P/L':>8}")
    print("-"*60)
    
    total_pnl = 0
    for pos in portfolio["positions"]:
        pnl = pos["value"] - (pos["shares"] * pos["entry"])
        total_pnl += pnl
        pnl_str = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"
        print(f"{pos['ticker']:<8} {pos['shares']:>6} ${pos['entry']:>7.2f} ${pos['current']:>7.2f} ${pos['value']:>9.2f} {pnl_str:>8}")
    
    print("-"*60)
    pnl_str = f"+${total_pnl:.2f}" if total_pnl >= 0 else f"-${abs(total_pnl):.2f}"
    print(f"{'TOTAL':<8} {'':>6} {'':>8} {'':>8} ${portfolio['positions_value']:>9.2f} {pnl_str:>8}")
    
    # Allocation analysis
    print("\n" + "="*60)
    print("📊 ALLOCATION ANALYSIS")
    print("="*60)
    
    for pos in portfolio["positions"]:
        allocation = (pos["value"] / portfolio["total_value"]) * 100
        status = "✅" if allocation <= 20 else "⚠️ OVER 20%"
        print(f"{pos['ticker']}: {allocation:.1f}% of portfolio {status}")
    
    print(f"Cash: {portfolio['cash_pct']:.1f}% of portfolio", end=" ")
    if portfolio['cash_pct'] >= 30:
        print("✅ (30-50% target)")
    else:
        print("⚠️ (below 30% target)")
    
    # Risk analysis
    print("\n" + "="*60)
    print("⚠️ RISK ANALYSIS (10% STOP LOSS)")
    print("="*60)
    
    max_loss = 0
    for pos in portfolio["positions"]:
        stop_loss_value = pos["value"] * 0.10
        max_loss += stop_loss_value
        print(f"{pos['ticker']}: Max loss ${stop_loss_value:.2f} (if stopped out at -10%)")
    
    print(f"\nTotal max loss if ALL stopped: ${max_loss:.2f} ({(max_loss/portfolio['total_value'])*100:.1f}% of portfolio)")
    
    return portfolio


def calculate_position_size(ticker: str, conviction: str, account: str = "rh"):
    """Calculate recommended position size for a new trade."""
    portfolio = calculate_portfolio_value()
    price = get_current_price(ticker)
    
    if not price:
        print(f"❌ Could not get price for {ticker}")
        return
    
    print("\n" + "="*60)
    print(f"🎯 POSITION SIZER: {ticker}")
    print("="*60)
    print(f"\nCurrent Price: ${price:.2f}")
    print(f"Conviction: {conviction.upper()}")
    
    # Conviction-based allocation
    conviction_map = {
        "high": {"pct": 15, "description": "High conviction - clear catalyst, strong thesis"},
        "medium": {"pct": 10, "description": "Medium conviction - good setup, some unknowns"},
        "low": {"pct": 5, "description": "Low conviction - speculative, small position"},
    }
    
    if conviction.lower() not in conviction_map:
        conviction = "medium"
    
    conv = conviction_map[conviction.lower()]
    
    # Available cash
    if account.lower() == "fidelity":
        available = PORTFOLIO["cash_fidelity"]
        print(f"Account: Fidelity (${available} available)")
    else:
        available = PORTFOLIO["cash_rh"]
        print(f"Account: Robinhood (${available} available)")
    
    # Calculate position
    target_allocation = portfolio["total_value"] * (conv["pct"] / 100)
    recommended = min(target_allocation, available * 0.8)  # Keep 20% buffer
    
    shares = int(recommended / price)
    actual_cost = shares * price
    allocation_pct = (actual_cost / portfolio["total_value"]) * 100
    
    print(f"\n{conv['description']}")
    print(f"\n{'─'*60}")
    print("📊 RECOMMENDED POSITION:")
    print(f"{'─'*60}")
    print(f"Shares: {shares}")
    print(f"Cost: ${actual_cost:.2f}")
    print(f"Allocation: {allocation_pct:.1f}% of portfolio")
    
    # Stop loss calculation
    stop_loss_pct = 10
    stop_price = price * (1 - stop_loss_pct/100)
    max_loss = actual_cost * (stop_loss_pct/100)
    
    print(f"\n⚠️ RISK MANAGEMENT:")
    print(f"Stop Loss Price: ${stop_price:.2f} (-{stop_loss_pct}%)")
    print(f"Max Loss: ${max_loss:.2f}")
    
    # Profit targets
    print(f"\n🎯 PROFIT TARGETS:")
    targets = [(15, 0.25), (25, 0.25), (50, 0.50)]
    for target_pct, sell_pct in targets:
        target_price = price * (1 + target_pct/100)
        sell_shares = int(shares * sell_pct)
        profit = sell_shares * (target_price - price)
        print(f"+{target_pct}% (${target_price:.2f}): Sell {sell_shares} shares = ${profit:.2f} profit")
    
    # After purchase allocation
    print(f"\n📈 PORTFOLIO AFTER PURCHASE:")
    new_invested = portfolio["positions_value"] + actual_cost
    new_cash = portfolio["cash"] - actual_cost
    new_invested_pct = (new_invested / portfolio["total_value"]) * 100
    new_cash_pct = (new_cash / portfolio["total_value"]) * 100
    
    print(f"Invested: {new_invested_pct:.1f}% (was {portfolio['invested_pct']}%)")
    print(f"Cash: {new_cash_pct:.1f}% (was {portfolio['cash_pct']}%)")
    
    if new_cash_pct < 30:
        print("⚠️ WARNING: Cash below 30% target. Consider smaller position.")


def what_if_analysis(ticker: str, target_price: float):
    """Run what-if analysis for a price target."""
    portfolio = calculate_portfolio_value()
    
    # Find if we own this ticker
    position = None
    for pos in portfolio["positions"]:
        if pos["ticker"].upper() == ticker.upper():
            position = pos
            break
    
    if not position:
        print(f"❌ {ticker} not in current positions")
        return
    
    print("\n" + "="*60)
    print(f"🔮 WHAT-IF: {ticker} hits ${target_price}")
    print("="*60)
    
    current_value = position["value"]
    new_value = position["shares"] * target_price
    gain = new_value - current_value
    gain_from_entry = new_value - (position["shares"] * position["entry"])
    gain_pct_from_entry = ((target_price - position["entry"]) / position["entry"]) * 100
    
    print(f"\nCurrent: ${position['current']:.2f}")
    print(f"Target: ${target_price:.2f}")
    print(f"Shares: {position['shares']}")
    
    print(f"\n📈 AT TARGET:")
    print(f"Position Value: ${new_value:.2f} (currently ${current_value:.2f})")
    print(f"Gain from entry: ${gain_from_entry:.2f} (+{gain_pct_from_entry:.1f}%)")
    
    # New portfolio value
    new_portfolio = portfolio["total_value"] - current_value + new_value
    print(f"\nPortfolio Value: ${new_portfolio:,.2f} (currently ${portfolio['total_value']:,.2f})")
    
    # What if we added more NOW?
    current_price = get_current_price(ticker)
    if current_price:
        print(f"\n🤔 WHAT IF YOU ADD MORE NOW?")
        additional_shares = [5, 10, 20, 50]
        for add in additional_shares:
            cost = add * current_price
            if cost <= portfolio["cash"]:
                future_value = (position["shares"] + add) * target_price
                total_gain = future_value - (current_value + cost)
                print(f"Add {add} shares (${cost:.2f}): Gain at target = ${total_gain:.2f}")


def main():
    parser = argparse.ArgumentParser(description="🐺 Position Sizer - Right-size your bets")
    parser.add_argument("--portfolio", action="store_true", help="Show current portfolio")
    parser.add_argument("--ticker", type=str, help="Ticker to size position for")
    parser.add_argument("--conviction", type=str, default="medium", help="high/medium/low")
    parser.add_argument("--account", type=str, default="rh", help="rh or fidelity")
    parser.add_argument("--what-if", nargs=2, metavar=("TICKER", "PRICE"), help="What-if analysis")
    
    args = parser.parse_args()
    
    if args.what_if:
        ticker, price = args.what_if
        what_if_analysis(ticker, float(price))
    elif args.portfolio:
        show_portfolio()
    elif args.ticker:
        calculate_position_size(args.ticker, args.conviction, args.account)
    else:
        show_portfolio()
        print("\n" + "─"*60)
        print("Usage: python position_sizer.py --ticker SYMBOL --conviction high/medium/low")
        print("       python position_sizer.py --what-if UUUU 100")
    
    print("\n🐺 AWOOOO!")


if __name__ == "__main__":
    main()
