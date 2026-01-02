"""
🐺 SECTOR ROTATION TRACKER - ETF Heatmap & Alerts

Tracks 16 sector ETFs for rotation detection
Generates heatmaps (daily, weekly, monthly)
Alerts on >3% weekly moves

100% FREE - Uses yfinance

Author: Brokkr (Brother Mode)
Date: January 2, 2026
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

class SectorRotationTracker:
    """
    Tracks sector ETF performance
    Detects rotation (hot/cold sectors)
    """
    
    # 16 Sector ETFs
    SECTOR_ETFS = {
        'XLK': 'Technology',
        'XLV': 'Healthcare',
        'XLF': 'Financials',
        'XLE': 'Energy',
        'XLY': 'Consumer Discretionary',
        'XLP': 'Consumer Staples',
        'XLI': 'Industrials',
        'XLB': 'Materials',
        'XLRE': 'Real Estate',
        'XLU': 'Utilities',
        'XLC': 'Communication',
        'IYT': 'Transportation',
        'XBI': 'Biotech',
        'SMH': 'Semiconductors',
        'XHB': 'Homebuilders',
        'KRE': 'Regional Banks'
    }
    
    def __init__(self):
        self.data_dir = Path('data/sectors')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.charts_dir = Path('logs/sector_charts')
        self.charts_dir.mkdir(parents=True, exist_ok=True)
    
    def get_sector_performance(self, period: str = '1mo') -> dict:
        """
        Get performance data for all sector ETFs
        
        Args:
            period: '1d', '5d', '1mo', '3mo'
        
        Returns:
            Dict with ticker: {name, change_pct, price, etc}
        """
        print(f"\n📊 Fetching sector performance ({period})...")
        
        sector_data = {}
        
        for ticker, name in self.SECTOR_ETFS.items():
            try:
                etf = yf.Ticker(ticker)
                hist = etf.history(period=period)
                
                if len(hist) < 2:
                    continue
                
                # Calculate performance
                start_price = hist['Close'].iloc[0]
                end_price = hist['Close'].iloc[-1]
                change_pct = ((end_price - start_price) / start_price) * 100
                
                # Get current price
                current_price = hist['Close'].iloc[-1]
                
                # Volume analysis
                avg_volume = hist['Volume'].mean()
                recent_volume = hist['Volume'].iloc[-1]
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
                
                sector_data[ticker] = {
                    'name': name,
                    'change_pct': round(change_pct, 2),
                    'current_price': round(current_price, 2),
                    'start_price': round(start_price, 2),
                    'end_price': round(end_price, 2),
                    'volume_ratio': round(volume_ratio, 2),
                    'period': period
                }
                
                print(f"   {ticker}: {change_pct:+.2f}%")
            
            except Exception as e:
                print(f"⚠️ Error fetching {ticker}: {e}")
        
        return sector_data
    
    def get_multi_period_performance(self) -> dict:
        """
        Get performance across multiple time periods
        Returns nested dict: {ticker: {name, '1d', '5d', '1mo', '3mo'}}
        """
        print("\n📊 SECTOR ROTATION ANALYSIS")
        print("=" * 70)
        
        # Get all periods
        periods = {
            '1d': '1 Day',
            '5d': '5 Days',
            '1mo': '1 Month',
            '3mo': '3 Months'
        }
        
        combined_data = {}
        
        for period_key, period_name in periods.items():
            print(f"\n{period_name}:")
            sector_perf = self.get_sector_performance(period_key)
            
            for ticker, data in sector_perf.items():
                if ticker not in combined_data:
                    combined_data[ticker] = {
                        'name': data['name'],
                        'current_price': data['current_price']
                    }
                
                combined_data[ticker][period_key] = data['change_pct']
        
        return combined_data
    
    def generate_heatmap(self, sector_data: dict, period: str = '1mo', save: bool = True):
        """
        Generate visual heatmap of sector performance
        """
        print(f"\n🎨 Generating heatmap for {period}...")
        
        if not sector_data:
            print("❌ No data to plot")
            return
        
        # Prepare data
        tickers = []
        names = []
        values = []
        
        for ticker, data in sorted(sector_data.items(), key=lambda x: x[1].get(period, 0), reverse=True):
            if period in data:
                tickers.append(ticker)
                names.append(data['name'])
                values.append(data[period])
        
        if not values:
            print("❌ No values to plot")
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create color map (red to green)
        colors = ['#d62728', '#ff7f0e', '#ffff00', '#90ee90', '#2ca02c']
        n_bins = 100
        cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)
        
        # Normalize values
        vmin, vmax = min(values), max(values)
        norm = plt.Normalize(vmin=vmin, vmax=vmax)
        
        # Calculate grid dimensions (4 columns)
        n_sectors = len(values)
        n_cols = 4
        n_rows = (n_sectors + n_cols - 1) // n_cols
        
        # Plot heatmap tiles
        for i, (ticker, name, value) in enumerate(zip(tickers, names, values)):
            row = i // n_cols
            col = i % n_cols
            
            # Position
            x = col * 0.25
            y = 1 - (row + 1) * (1 / n_rows)
            width = 0.24
            height = 0.95 / n_rows
            
            # Color
            color = cmap(norm(value))
            
            # Draw rectangle
            rect = mpatches.Rectangle((x, y), width, height, 
                                      facecolor=color, edgecolor='black', linewidth=1)
            ax.add_patch(rect)
            
            # Add text
            text_color = 'white' if value < 0 else 'black'
            ax.text(x + width/2, y + height * 0.7, ticker, 
                   ha='center', va='center', fontsize=14, fontweight='bold', color=text_color)
            ax.text(x + width/2, y + height * 0.4, name, 
                   ha='center', va='center', fontsize=8, color=text_color, wrap=True)
            ax.text(x + width/2, y + height * 0.15, f'{value:+.1f}%', 
                   ha='center', va='center', fontsize=12, fontweight='bold', color=text_color)
        
        # Configure axes
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Title
        period_labels = {'1d': '1 Day', '5d': '5 Days', '1mo': '1 Month', '3mo': '3 Months'}
        title = f'🐺 SECTOR ROTATION - {period_labels.get(period, period)}'
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Add timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        plt.figtext(0.99, 0.01, f'Generated: {timestamp}', ha='right', fontsize=8, style='italic')
        
        plt.tight_layout()
        
        if save:
            filename = self.charts_dir / f'sector_heatmap_{period}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"💾 Saved: {filename}")
        
        plt.close()
    
    def detect_rotation_signals(self, sector_data: dict, threshold: float = 3.0) -> dict:
        """
        Detect rotation signals
        
        Args:
            threshold: Minimum % change to flag (default 3%)
        
        Returns:
            Dict with 'hot' and 'cold' lists
        """
        print(f"\n🔍 Detecting rotation (threshold: {threshold}%)...")
        
        hot_sectors = []
        cold_sectors = []
        
        # Use 5-day performance for rotation detection
        for ticker, data in sector_data.items():
            if '5d' in data:
                change = data['5d']
                
                if change >= threshold:
                    hot_sectors.append({
                        'ticker': ticker,
                        'name': data['name'],
                        'change_pct': change
                    })
                elif change <= -threshold:
                    cold_sectors.append({
                        'ticker': ticker,
                        'name': data['name'],
                        'change_pct': change
                    })
        
        # Sort
        hot_sectors.sort(key=lambda x: x['change_pct'], reverse=True)
        cold_sectors.sort(key=lambda x: x['change_pct'])
        
        return {
            'hot': hot_sectors,
            'cold': cold_sectors
        }
    
    def get_alerts(self) -> list:
        """
        Get sector rotation alerts for alert system
        """
        # Get multi-period data
        sector_data = self.get_multi_period_performance()
        
        # Detect rotation
        signals = self.detect_rotation_signals(sector_data, threshold=3.0)
        
        alerts = []
        
        # Hot sectors
        for sector in signals['hot']:
            alerts.append({
                'type': 'sector_rotation',
                'direction': 'HOT',
                'ticker': sector['ticker'],
                'name': sector['name'],
                'change_pct': sector['change_pct']
            })
        
        # Cold sectors
        for sector in signals['cold']:
            alerts.append({
                'type': 'sector_rotation',
                'direction': 'COLD',
                'ticker': sector['ticker'],
                'name': sector['name'],
                'change_pct': sector['change_pct']
            })
        
        return alerts
    
    def print_rotation_report(self):
        """Print full rotation report"""
        # Get data
        sector_data = self.get_multi_period_performance()
        
        # Detect rotation
        signals = self.detect_rotation_signals(sector_data)
        
        print(f"\n{'='*70}")
        print(f"🔥 HOT SECTORS (5-day)")
        print(f"{'='*70}")
        
        for sector in signals['hot']:
            print(f"   {sector['ticker']} {sector['name']}: {sector['change_pct']:+.2f}%")
        
        print(f"\n{'='*70}")
        print(f"🧊 COLD SECTORS (5-day)")
        print(f"{'='*70}")
        
        for sector in signals['cold']:
            print(f"   {sector['ticker']} {sector['name']}: {sector['change_pct']:+.2f}%")
        
        print()
        
        # Generate heatmaps
        self.generate_heatmap(sector_data, period='1d')
        self.generate_heatmap(sector_data, period='5d')
        self.generate_heatmap(sector_data, period='1mo')




# CLI Usage
if __name__ == "__main__":
    import sys
    
    tracker = SectorRotationTracker()
    
    if len(sys.argv) > 1:
        period = sys.argv[1]
        sector_data = tracker.get_multi_period_performance()
        tracker.generate_heatmap(sector_data, period=period)
    else:
        # Full report
        tracker.print_rotation_report()
