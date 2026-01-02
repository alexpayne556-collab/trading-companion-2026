#!/usr/bin/env python3
"""
🐺 PRE-MARKET & AFTER-HOURS SCANNER

Scans for gaps and unusual movements outside regular trading hours
Critical for catching opportunities before market open

Author: Brokkr (Brother Mode)
Date: January 2, 2026
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, time
from pathlib import Path
import json
from typing import Dict, List, Optional
import csv


class PreMarketAfterHoursScanner:
    """
    Scanner for pre-market (4-9:30 AM) and after-hours (4-8 PM) movements
    Detects gaps, unusual volume, and opportunities
    """
    
    def __init__(self):
        self.alerts_dir = Path('logs/premarket_alerts')
        self.alerts_dir.mkdir(parents=True, exist_ok=True)
    
    def is_premarket(self) -> bool:
        """Check if currently in pre-market hours (4-9:30 AM EST)"""
        now = datetime.now().time()
        return time(4, 0) <= now < time(9, 30)
    
    def is_afterhours(self) -> bool:
        """Check if currently in after-hours (4-8 PM EST)"""
        now = datetime.now().time()
        return time(16, 0) <= now < time(20, 0)
    
    def scan_premarket_gaps(self, tickers: List[str], min_gap_pct: float = 3.0) -> List[Dict]:
        """
        Scan for pre-market gaps
        
        Args:
            tickers: List of ticker symbols
            min_gap_pct: Minimum gap % to alert (default 3%)
        
        Returns:
            List of gap alerts
        """
        print(f"\n🌅 PRE-MARKET GAP SCANNER")
        print(f"   Time: {datetime.now().strftime('%I:%M %p EST')}")
        print(f"   Scanning {len(tickers)} tickers for gaps ≥{min_gap_pct}%")
        print("=" * 70)
        
        gaps = []
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Get pre-market and previous close
                premarket_price = info.get('preMarketPrice')
                previous_close = info.get('previousClose')
                premarket_volume = info.get('preMarketVolume', 0)
                
                if premarket_price and previous_close:
                    gap_pct = ((premarket_price - previous_close) / previous_close) * 100
                    
                    if abs(gap_pct) >= min_gap_pct:
                        gaps.append({
                            'ticker': ticker,
                            'previous_close': previous_close,
                            'premarket_price': premarket_price,
                            'gap_pct': gap_pct,
                            'premarket_volume': premarket_volume,
                            'direction': 'GAP UP' if gap_pct > 0 else 'GAP DOWN',
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        direction_emoji = '🚀' if gap_pct > 0 else '💀'
                        print(f"   {direction_emoji} {ticker}: {gap_pct:+.2f}% | ${previous_close:.2f} → ${premarket_price:.2f} | Vol: {premarket_volume:,}")
                
            except Exception as e:
                # Silent fail - API issues common pre-market
                continue
        
        # Sort by absolute gap percentage
        gaps.sort(key=lambda x: abs(x['gap_pct']), reverse=True)
        
        if not gaps:
            print(f"   ℹ️  No gaps ≥{min_gap_pct}% detected")
        
        return gaps
    
    def scan_afterhours_moves(self, tickers: List[str], min_move_pct: float = 2.0) -> List[Dict]:
        """
        Scan for after-hours price movements
        
        Args:
            tickers: List of ticker symbols
            min_move_pct: Minimum move % to alert (default 2%)
        
        Returns:
            List of after-hours movement alerts
        """
        print(f"\n🌙 AFTER-HOURS MOVEMENT SCANNER")
        print(f"   Time: {datetime.now().strftime('%I:%M %p EST')}")
        print(f"   Scanning {len(tickers)} tickers for moves ≥{min_move_pct}%")
        print("=" * 70)
        
        moves = []
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Get after-hours and regular close
                ah_price = info.get('postMarketPrice')
                regular_close = info.get('regularMarketPrice')
                ah_volume = info.get('postMarketVolume', 0)
                
                if ah_price and regular_close:
                    move_pct = ((ah_price - regular_close) / regular_close) * 100
                    
                    if abs(move_pct) >= min_move_pct:
                        moves.append({
                            'ticker': ticker,
                            'regular_close': regular_close,
                            'afterhours_price': ah_price,
                            'move_pct': move_pct,
                            'afterhours_volume': ah_volume,
                            'direction': 'UP' if move_pct > 0 else 'DOWN',
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        direction_emoji = '📈' if move_pct > 0 else '📉'
                        print(f"   {direction_emoji} {ticker}: {move_pct:+.2f}% | ${regular_close:.2f} → ${ah_price:.2f} | Vol: {ah_volume:,}")
                
            except Exception as e:
                continue
        
        # Sort by absolute move percentage
        moves.sort(key=lambda x: abs(x['move_pct']), reverse=True)
        
        if not moves:
            print(f"   ℹ️  No moves ≥{min_move_pct}% detected")
        
        return moves
    
    def check_positions_extended_hours(self, positions: List[Dict]) -> List[Dict]:
        """
        Check positions for extended hours movements
        Critical for risk management
        
        Args:
            positions: List of dicts with 'ticker', 'shares', 'entry_price', 'stop_loss'
        
        Returns:
            List of position alerts
        """
        print(f"\n🎯 POSITION RISK CHECK - EXTENDED HOURS")
        print("=" * 70)
        
        alerts = []
        
        for position in positions:
            ticker = position['ticker']
            shares = position.get('shares', 0)
            entry_price = position.get('entry_price', 0)
            stop_loss = position.get('stop_loss', 0)
            
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Determine current price based on time
                if self.is_premarket():
                    current_price = info.get('preMarketPrice') or info.get('previousClose', 0)
                    session = 'PRE-MARKET'
                elif self.is_afterhours():
                    current_price = info.get('postMarketPrice') or info.get('regularMarketPrice', 0)
                    session = 'AFTER-HOURS'
                else:
                    current_price = info.get('regularMarketPrice', 0)
                    session = 'REGULAR'
                
                if current_price > 0:
                    # Calculate P&L
                    pnl_per_share = current_price - entry_price
                    pnl_total = pnl_per_share * shares
                    pnl_pct = (pnl_per_share / entry_price) * 100
                    
                    # Check stop loss proximity
                    if stop_loss > 0:
                        distance_to_stop_pct = ((current_price - stop_loss) / current_price) * 100
                    else:
                        distance_to_stop_pct = 999
                    
                    alert = {
                        'ticker': ticker,
                        'session': session,
                        'shares': shares,
                        'entry_price': entry_price,
                        'current_price': current_price,
                        'stop_loss': stop_loss,
                        'pnl_per_share': pnl_per_share,
                        'pnl_total': pnl_total,
                        'pnl_pct': pnl_pct,
                        'distance_to_stop_pct': distance_to_stop_pct,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Generate alert conditions
                    alert_conditions = []
                    
                    if distance_to_stop_pct < 5:
                        alert_conditions.append('🚨 STOP LOSS NEAR')
                    
                    if pnl_pct < -10:
                        alert_conditions.append('⚠️ DOWN >10%')
                    
                    if pnl_pct > 20:
                        alert_conditions.append('🎯 UP >20%')
                    
                    alert['alert_conditions'] = alert_conditions
                    
                    alerts.append(alert)
                    
                    # Print position status
                    pnl_emoji = '💚' if pnl_pct > 0 else '❤️'
                    print(f"   {pnl_emoji} {ticker} ({session})")
                    print(f"      {shares} shares @ ${entry_price:.2f} → ${current_price:.2f}")
                    print(f"      P&L: ${pnl_total:+.2f} ({pnl_pct:+.2f}%)")
                    if stop_loss > 0:
                        print(f"      Stop: ${stop_loss:.2f} ({distance_to_stop_pct:.1f}% away)")
                    if alert_conditions:
                        print(f"      ALERTS: {', '.join(alert_conditions)}")
                    print()
            
            except Exception as e:
                print(f"   ⚠️ {ticker}: Error checking position - {e}")
                continue
        
        return alerts
    
    def save_alerts(self, data: List[Dict], alert_type: str):
        """Save alerts to log file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.alerts_dir / f'{alert_type}_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'alert_type': alert_type,
                'alerts': data
            }, f, indent=2)
        
        print(f"\n💾 Alerts saved: {filename}")
    
    def run_morning_scan(self, watchlist_file: str):
        """
        Morning routine: Check pre-market gaps on watchlist
        Run this at 6 AM daily via cron job
        """
        print("\n" + "=" * 70)
        print("🐺 WOLF PACK MORNING PRE-MARKET SCAN")
        print(f"   {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}")
        print("=" * 70)
        
        # Load watchlist
        tickers = self._load_watchlist(watchlist_file)
        
        # Scan for gaps
        gaps = self.scan_premarket_gaps(tickers, min_gap_pct=3.0)
        
        if gaps:
            self.save_alerts(gaps, 'premarket_gaps')
            
            print(f"\n🎯 TOP GAPPERS:")
            for gap in gaps[:10]:
                direction_emoji = '🚀' if gap['gap_pct'] > 0 else '💀'
                print(f"   {direction_emoji} {gap['ticker']:6s} {gap['gap_pct']:+6.2f}%")
        
        print(f"\n{'='*70}\n")
        
        return gaps
    
    def run_evening_scan(self, watchlist_file: str, positions: List[Dict] = None):
        """
        Evening routine: Check after-hours moves and position risk
        Run this at 4:30 PM daily via cron job
        """
        print("\n" + "=" * 70)
        print("🐺 WOLF PACK EVENING AFTER-HOURS SCAN")
        print(f"   {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}")
        print("=" * 70)
        
        # Load watchlist
        tickers = self._load_watchlist(watchlist_file)
        
        # Scan for after-hours moves
        moves = self.scan_afterhours_moves(tickers, min_move_pct=2.0)
        
        if moves:
            self.save_alerts(moves, 'afterhours_moves')
            
            print(f"\n🎯 TOP MOVERS:")
            for move in moves[:10]:
                direction_emoji = '📈' if move['move_pct'] > 0 else '📉'
                print(f"   {direction_emoji} {move['ticker']:6s} {move['move_pct']:+6.2f}%")
        
        # Check positions if provided
        if positions:
            position_alerts = self.check_positions_extended_hours(positions)
            
            # Save critical alerts
            critical = [a for a in position_alerts if a.get('alert_conditions')]
            if critical:
                self.save_alerts(critical, 'position_alerts')
        
        print(f"\n{'='*70}\n")
        
        return moves, position_alerts if positions else []
    
    def _load_watchlist(self, watchlist_file: str) -> List[str]:
        """Load tickers from CSV watchlist"""
        tickers = []
        
        with open(watchlist_file, 'r') as f:
            reader = csv.DictReader(f)
            tickers = [row['Symbol'] for row in reader]
        
        return tickers


def main():
    """CLI interface"""
    import sys
    
    scanner = PreMarketAfterHoursScanner()
    
    # Default watchlist
    watchlist_file = 'atp_watchlists/ATP_WOLF_PACK_MASTER.csv'
    
    # Example positions (update with actual)
    positions = [
        {
            'ticker': 'AISP',
            'shares': 69,
            'entry_price': 3.05,
            'stop_loss': 2.30
        }
    ]
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'premarket':
            scanner.run_morning_scan(watchlist_file)
        
        elif command == 'afterhours':
            scanner.run_evening_scan(watchlist_file, positions)
        
        elif command == 'positions':
            scanner.check_positions_extended_hours(positions)
        
        else:
            print("Usage:")
            print("  python premarket_afterhours_scanner.py premarket   # Morning gaps")
            print("  python premarket_afterhours_scanner.py afterhours  # Evening moves")
            print("  python premarket_afterhours_scanner.py positions   # Position check")
    
    else:
        # Auto-detect based on time
        if scanner.is_premarket():
            scanner.run_morning_scan(watchlist_file)
        elif scanner.is_afterhours():
            scanner.run_evening_scan(watchlist_file, positions)
        else:
            print("Not currently in pre-market or after-hours.")
            print("Run manually with: premarket | afterhours | positions")


if __name__ == '__main__':
    main()
