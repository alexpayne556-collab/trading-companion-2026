#!/usr/bin/env python3
"""
🐺 WOLF PACK STRATEGY BACKTESTER
Validate strategies BEFORE risking real capital

"We don't gamble. We ENGINEER success."

This uses yfinance for free historical data.
For production, connect to Alpaca API for more data.

AWOOOO 🐺
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# =============================================================
# CONFIGURATION
# =============================================================

INITIAL_CAPITAL = 1280  # Wolf Pack starting capital
RISK_PER_TRADE = 0.05   # 5% max risk per trade
STOP_LOSS_PCT = 0.10    # 10% stop loss
MAX_POSITION_PCT = 0.25 # Max 25% in single position

# =============================================================
# STRATEGY: WOUNDED PREY (Tax Loss Bounce)
# =============================================================

def wounded_prey_strategy(ticker, start_date, end_date, 
                          december_drop_threshold=-10,
                          january_hold_days=20):
    """
    Wounded Prey Strategy:
    - Buy stocks that dropped >10% in December
    - Hold for 20 trading days in January
    - Exit at end of hold period or stop loss
    
    Returns backtest results.
    """
    try:
        # Get data with buffer for December analysis
        buffer_start = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=60)).strftime('%Y-%m-%d')
        stock = yf.Ticker(ticker)
        df = stock.history(start=buffer_start, end=end_date)
        
        if df.empty or len(df) < 40:
            return None
            
        df = df.reset_index()
        df['Date'] = pd.to_datetime(df['Date'])
        df['Month'] = df['Date'].dt.month
        df['Year'] = df['Date'].dt.year
        
        trades = []
        
        # Get unique years in data
        years = df['Year'].unique()
        
        for year in years:
            # December of previous year
            dec_data = df[(df['Year'] == year - 1) & (df['Month'] == 12)]
            jan_data = df[(df['Year'] == year) & (df['Month'] == 1)]
            
            if len(dec_data) < 5 or len(jan_data) < 5:
                continue
            
            # Calculate December return
            dec_start = dec_data['Close'].iloc[0]
            dec_end = dec_data['Close'].iloc[-1]
            dec_return = ((dec_end - dec_start) / dec_start) * 100
            
            # Check if wounded (down in December)
            if dec_return <= december_drop_threshold:
                # Entry: First trading day of January
                entry_date = jan_data['Date'].iloc[0]
                entry_price = jan_data['Open'].iloc[0]
                stop_price = entry_price * (1 - STOP_LOSS_PCT)
                
                # Simulate holding period
                exit_price = None
                exit_date = None
                exit_reason = None
                
                hold_data = jan_data.head(january_hold_days)
                
                for i, row in hold_data.iterrows():
                    # Check stop loss
                    if row['Low'] <= stop_price:
                        exit_price = stop_price
                        exit_date = row['Date']
                        exit_reason = 'STOP_LOSS'
                        break
                
                # If not stopped out, exit at end of period
                if exit_price is None and len(hold_data) > 0:
                    exit_price = hold_data['Close'].iloc[-1]
                    exit_date = hold_data['Date'].iloc[-1]
                    exit_reason = 'HOLD_COMPLETE'
                
                if exit_price is not None:
                    pnl_pct = ((exit_price - entry_price) / entry_price) * 100
                    
                    trades.append({
                        'ticker': ticker,
                        'year': year,
                        'dec_return': round(dec_return, 2),
                        'entry_date': entry_date,
                        'entry_price': round(entry_price, 2),
                        'exit_date': exit_date,
                        'exit_price': round(exit_price, 2),
                        'pnl_pct': round(pnl_pct, 2),
                        'exit_reason': exit_reason
                    })
        
        return trades
        
    except Exception as e:
        print(f"Error backtesting {ticker}: {e}")
        return None


# =============================================================
# STRATEGY: MOMENTUM PULLBACK
# =============================================================

def momentum_pullback_strategy(ticker, start_date, end_date,
                               momentum_threshold=15,
                               pullback_threshold=-5,
                               hold_days=10):
    """
    Momentum Pullback Strategy:
    - Find stocks up >15% over 20 days (momentum)
    - Wait for 5%+ pullback
    - Buy on pullback
    - Hold for 10 days or stop loss
    
    Returns backtest results.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty or len(df) < 30:
            return None
            
        df = df.reset_index()
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Calculate rolling momentum (20-day return)
        df['Momentum_20d'] = df['Close'].pct_change(periods=20) * 100
        
        # Calculate 5-day return (for pullback detection)
        df['Return_5d'] = df['Close'].pct_change(periods=5) * 100
        
        trades = []
        
        i = 25  # Start after we have enough data
        while i < len(df) - hold_days:
            row = df.iloc[i]
            
            # Check for momentum + pullback setup
            if row['Momentum_20d'] >= momentum_threshold and row['Return_5d'] <= pullback_threshold:
                entry_date = row['Date']
                entry_price = row['Close']
                stop_price = entry_price * (1 - STOP_LOSS_PCT)
                
                # Simulate hold period
                exit_price = None
                exit_date = None
                exit_reason = None
                
                for j in range(i + 1, min(i + hold_days + 1, len(df))):
                    future_row = df.iloc[j]
                    
                    # Check stop loss
                    if future_row['Low'] <= stop_price:
                        exit_price = stop_price
                        exit_date = future_row['Date']
                        exit_reason = 'STOP_LOSS'
                        break
                
                # If not stopped, exit at end of period
                if exit_price is None and i + hold_days < len(df):
                    exit_row = df.iloc[i + hold_days]
                    exit_price = exit_row['Close']
                    exit_date = exit_row['Date']
                    exit_reason = 'HOLD_COMPLETE'
                
                if exit_price is not None:
                    pnl_pct = ((exit_price - entry_price) / entry_price) * 100
                    
                    trades.append({
                        'ticker': ticker,
                        'entry_date': entry_date,
                        'entry_price': round(entry_price, 2),
                        'momentum_20d': round(row['Momentum_20d'], 2),
                        'pullback_5d': round(row['Return_5d'], 2),
                        'exit_date': exit_date,
                        'exit_price': round(exit_price, 2),
                        'pnl_pct': round(pnl_pct, 2),
                        'exit_reason': exit_reason
                    })
                    
                    # Skip ahead to avoid overlapping trades
                    i += hold_days
                    continue
            
            i += 1
        
        return trades
        
    except Exception as e:
        print(f"Error backtesting {ticker}: {e}")
        return None


# =============================================================
# ANALYSIS FUNCTIONS
# =============================================================

def analyze_backtest_results(trades, strategy_name):
    """Analyze backtest results and print statistics."""
    
    if not trades or len(trades) == 0:
        print(f"\n❌ {strategy_name}: No trades found")
        return None
    
    df = pd.DataFrame(trades)
    
    # Calculate statistics
    total_trades = len(df)
    winning_trades = len(df[df['pnl_pct'] > 0])
    losing_trades = len(df[df['pnl_pct'] <= 0])
    win_rate = (winning_trades / total_trades) * 100
    
    avg_win = df[df['pnl_pct'] > 0]['pnl_pct'].mean() if winning_trades > 0 else 0
    avg_loss = df[df['pnl_pct'] <= 0]['pnl_pct'].mean() if losing_trades > 0 else 0
    
    avg_return = df['pnl_pct'].mean()
    total_return = df['pnl_pct'].sum()
    max_win = df['pnl_pct'].max()
    max_loss = df['pnl_pct'].min()
    
    # Profit factor
    gross_profit = df[df['pnl_pct'] > 0]['pnl_pct'].sum()
    gross_loss = abs(df[df['pnl_pct'] <= 0]['pnl_pct'].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    # Stop loss vs hold complete
    stop_outs = len(df[df['exit_reason'] == 'STOP_LOSS'])
    holds_complete = len(df[df['exit_reason'] == 'HOLD_COMPLETE'])
    
    # Expected value per trade
    expected_value = (win_rate/100 * avg_win) + ((100-win_rate)/100 * avg_loss)
    
    print(f"\n{'='*60}")
    print(f"📊 {strategy_name} BACKTEST RESULTS")
    print(f"{'='*60}")
    print(f"Total Trades:     {total_trades}")
    print(f"Winning Trades:   {winning_trades} ({win_rate:.1f}%)")
    print(f"Losing Trades:    {losing_trades} ({100-win_rate:.1f}%)")
    print(f"")
    print(f"Average Win:      +{avg_win:.2f}%")
    print(f"Average Loss:     {avg_loss:.2f}%")
    print(f"Average Return:   {avg_return:.2f}%")
    print(f"")
    print(f"Max Win:          +{max_win:.2f}%")
    print(f"Max Loss:         {max_loss:.2f}%")
    print(f"Total Return:     {total_return:.2f}%")
    print(f"")
    print(f"Profit Factor:    {profit_factor:.2f}")
    print(f"Expected Value:   {expected_value:.2f}% per trade")
    print(f"")
    print(f"Stop Losses Hit:  {stop_outs}")
    print(f"Holds Completed:  {holds_complete}")
    print(f"{'='*60}")
    
    # Verdict
    if expected_value > 0 and profit_factor > 1.5:
        print(f"✅ VERDICT: Strategy has POSITIVE expected value")
        print(f"   This is a VALID edge worth trading.")
    elif expected_value > 0:
        print(f"⚠️  VERDICT: Strategy is MARGINALLY positive")
        print(f"   Needs more testing or refinement.")
    else:
        print(f"❌ VERDICT: Strategy has NEGATIVE expected value")
        print(f"   DO NOT TRADE THIS AS-IS.")
    
    return {
        'strategy': strategy_name,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
        'expected_value': expected_value,
        'trades': df
    }


def simulate_portfolio(results, initial_capital=1280):
    """Simulate portfolio growth using backtest results."""
    
    if results is None or 'trades' not in results:
        return None
    
    df = results['trades'].copy()
    df = df.sort_values('entry_date')
    
    capital = initial_capital
    capital_history = [capital]
    
    for _, trade in df.iterrows():
        # Position size (25% of capital max)
        position_size = min(capital * MAX_POSITION_PCT, capital * 0.9)
        
        # Calculate P/L
        pnl_dollars = position_size * (trade['pnl_pct'] / 100)
        capital += pnl_dollars
        capital_history.append(capital)
    
    # Calculate portfolio stats
    total_return = ((capital - initial_capital) / initial_capital) * 100
    max_capital = max(capital_history)
    min_capital = min(capital_history)
    max_drawdown = ((max_capital - min(capital_history[capital_history.index(max_capital):])) / max_capital) * 100 if max_capital > 0 else 0
    
    print(f"\n💰 PORTFOLIO SIMULATION")
    print(f"Starting Capital: ${initial_capital:,.2f}")
    print(f"Ending Capital:   ${capital:,.2f}")
    print(f"Total Return:     {total_return:.2f}%")
    print(f"Max Drawdown:     {max_drawdown:.2f}%")
    
    return capital


# =============================================================
# MAIN BACKTESTER
# =============================================================

def run_full_backtest():
    """Run complete backtest of Wolf Pack strategies."""
    
    print("\n" + "="*60)
    print("🐺 WOLF PACK STRATEGY BACKTESTER 🐺")
    print("Validating strategies with HISTORICAL DATA")
    print("="*60)
    
    # Watchlist to test
    watchlist = [
        # Our target stocks
        'BBAI', 'SOUN', 'SMR', 'RKLB', 'IONQ', 'RGTI',
        # Broader market to test strategy
        'AMD', 'NVDA', 'PLTR', 'SOFI', 'PATH', 'AI',
        # Energy
        'AR', 'EQT', 'CCJ',
    ]
    
    # Date range (last 3 years)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')
    
    print(f"\nBacktest Period: {start_date} to {end_date}")
    print(f"Tickers: {len(watchlist)}")
    
    # ===========================================
    # TEST 1: WOUNDED PREY STRATEGY
    # ===========================================
    
    print("\n" + "-"*60)
    print("STRATEGY 1: WOUNDED PREY (Tax Loss Bounce)")
    print("-"*60)
    
    all_wounded_trades = []
    
    for ticker in watchlist:
        print(f"  Testing {ticker}...", end=" ")
        trades = wounded_prey_strategy(ticker, start_date, end_date)
        if trades:
            all_wounded_trades.extend(trades)
            print(f"{len(trades)} trades found")
        else:
            print("No trades")
    
    wounded_results = analyze_backtest_results(all_wounded_trades, "WOUNDED PREY")
    if wounded_results:
        simulate_portfolio(wounded_results)
    
    # ===========================================
    # TEST 2: MOMENTUM PULLBACK STRATEGY
    # ===========================================
    
    print("\n" + "-"*60)
    print("STRATEGY 2: MOMENTUM PULLBACK")
    print("-"*60)
    
    all_momentum_trades = []
    
    for ticker in watchlist:
        print(f"  Testing {ticker}...", end=" ")
        trades = momentum_pullback_strategy(ticker, start_date, end_date)
        if trades:
            all_momentum_trades.extend(trades)
            print(f"{len(trades)} trades found")
        else:
            print("No trades")
    
    momentum_results = analyze_backtest_results(all_momentum_trades, "MOMENTUM PULLBACK")
    if momentum_results:
        simulate_portfolio(momentum_results)
    
    # ===========================================
    # SUMMARY
    # ===========================================
    
    print("\n" + "="*60)
    print("🐺 BACKTEST SUMMARY")
    print("="*60)
    
    if wounded_results:
        print(f"\nWOUNDED PREY:")
        print(f"   Win Rate: {wounded_results['win_rate']:.1f}%")
        print(f"   Profit Factor: {wounded_results['profit_factor']:.2f}")
        print(f"   Expected Value: {wounded_results['expected_value']:.2f}% per trade")
    
    if momentum_results:
        print(f"\nMOMENTUM PULLBACK:")
        print(f"   Win Rate: {momentum_results['win_rate']:.1f}%")
        print(f"   Profit Factor: {momentum_results['profit_factor']:.2f}")
        print(f"   Expected Value: {momentum_results['expected_value']:.2f}% per trade")
    
    print("\n" + "="*60)
    print("⚠️  IMPORTANT: These are HISTORICAL results.")
    print("   Past performance does NOT guarantee future results.")
    print("   But strategies with NO edge historically have NO edge.")
    print("   Use this to FILTER bad strategies before risking capital.")
    print("="*60)
    
    print("\n🐺 AWOOOO! Backtest complete.")
    print("   Now you KNOW, not just HOPE.\n")
    
    return {
        'wounded_prey': wounded_results,
        'momentum_pullback': momentum_results
    }


# =============================================================
# RUN IT
# =============================================================

if __name__ == "__main__":
    results = run_full_backtest()
