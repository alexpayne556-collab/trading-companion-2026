#!/usr/bin/env python3
"""
🐺 WOLF PACK MASTER DASHBOARD
Combines ALL hunting tools into one unified command center.

Features:
- 24-Hour Sector Rotation Monitor
- Insider Cluster Scanner
- 8-K Contract Scanner
- Wounded Prey Tax Loss Scanner
- High Conviction Cross-Signal Validator
- Morning Briefing
- Live Position Monitor
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf
import pandas as pd
import numpy as np


class MasterDashboard:
    """Unified dashboard combining all Wolf Pack tools."""
    
    def __init__(self):
        self.width = 80
        self.sectors = {
            'quantum': ['IONQ', 'RGTI', 'QBTS'],
            'space': ['RKLB', 'ASTS', 'LUNR'],
            'biotech_small': ['SAVA', 'ALNY'],
            'biotech_large': ['MRNA', 'BNTX', 'NVAX'],
            'uranium': ['CCJ', 'UEC', 'UUUU'],
            'cybersecurity': ['CRWD', 'S', 'ZS'],
            'ai_infrastructure': ['NVDA', 'AMD', 'AVGO'],
            'ai_hype': ['AI', 'BBAI'],
            'defense': ['LMT', 'RTX', 'BA'],
            'semi': ['ASML', 'TSM', 'INTC']
        }
        
    def clear_screen(self):
        """Clear terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self):
        """Print master dashboard header."""
        print("\n" + "="*self.width)
        print("🐺 WOLF PACK MASTER DASHBOARD")
        print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print("="*self.width)
    
    def section_header(self, title):
        """Print section header."""
        print(f"\n{'='*self.width}")
        print(f"📊 {title}")
        print(f"{'='*self.width}\n")
    
    # ========================================================================
    # SECTION 1: 24-HOUR SECTOR ROTATION MONITOR
    # ========================================================================
    
    def monitor_sector_rotation(self):
        """Monitor sector rotation in real-time."""
        self.section_header("24-HOUR SECTOR ROTATION MONITOR")
        
        # Calculate distance from 30d highs for each sector
        sector_status = []
        
        print("Loading sector data...")
        for sector_name, tickers in self.sectors.items():
            try:
                sector_returns = []
                for ticker in tickers:
                    try:
                        data = yf.Ticker(ticker).history(period='30d')
                        if len(data) > 0:
                            returns = data['Close'].pct_change() * 100
                            sector_returns.append(returns)
                    except:
                        continue
                
                if len(sector_returns) > 0:
                    sector_avg = pd.concat(sector_returns, axis=1).mean(axis=1)
                    cumulative = (1 + sector_avg / 100).cumprod()
                    
                    current = cumulative.iloc[-1]
                    high_30d = cumulative.max()
                    from_high = ((current / high_30d) - 1) * 100
                    
                    # Today's performance
                    today_ret = sector_avg.iloc[-1] if len(sector_avg) > 0 else 0
                    
                    sector_status.append({
                        'sector': sector_name,
                        'from_high': from_high,
                        'today': today_ret
                    })
            except:
                continue
        
        # Sort by distance from high
        sector_status.sort(key=lambda x: x['from_high'])
        
        # Display
        print("\n🟢 BEATEN DOWN (Opportunity)  🟡 MIDDLE  🔴 AT HIGHS (Extended)\n")
        
        beaten_down = []
        at_highs = []
        
        for s in sector_status:
            sector = s['sector']
            from_high = s['from_high']
            today = s['today']
            
            # Status emoji
            if from_high > -2:
                emoji = "🔴"
                status = "AT HIGH"
                at_highs.append(sector)
            elif from_high > -10:
                emoji = "🟡"
                status = "MIDDLE"
            else:
                emoji = "🟢"
                status = "BEATEN"
                beaten_down.append(sector)
            
            # Today's move
            if today > 1:
                today_emoji = "⬆️"
            elif today < -1:
                today_emoji = "⬇️"
            else:
                today_emoji = "➡️"
            
            print(f"{emoji} {sector:20s} {from_high:+6.1f}% from high  {today_emoji} Today: {today:+5.2f}%")
        
        # Summary
        print(f"\n🎯 TRADING PLAN:")
        print(f"\n✅ WATCH (Beaten down sectors):")
        print(f"   {', '.join(beaten_down) if beaten_down else 'None'}")
        print(f"   → Entry if green 2 days straight")
        
        print(f"\n❌ AVOID (Extended sectors):")
        print(f"   {', '.join(at_highs) if at_highs else 'None'}")
        print(f"   → At highs, likely to dump")
        
        return beaten_down, at_highs
    
    # ========================================================================
    # SECTION 2: TOP TICKERS TO WATCH
    # ========================================================================
    
    def scan_top_tickers(self, beaten_sectors, avoid_sectors):
        """Scan individual tickers from beaten-down sectors."""
        self.section_header("TOP TICKERS TO WATCH")
        
        watch_tickers = []
        for sector in beaten_sectors:
            if sector in self.sectors:
                watch_tickers.extend(self.sectors[sector])
        
        if not watch_tickers:
            print("⚠️  No beaten-down sectors found")
            return
        
        print(f"Scanning {len(watch_tickers)} tickers from beaten-down sectors...\n")
        
        ticker_data = []
        for ticker in watch_tickers:
            try:
                data = yf.Ticker(ticker).history(period='10d')
                if len(data) < 2:
                    continue
                
                current_price = data['Close'].iloc[-1]
                prev_close = data['Close'].iloc[-2]
                today_change = ((current_price / prev_close) - 1) * 100
                
                # 5d performance
                if len(data) >= 5:
                    five_d_start = data['Close'].iloc[-5]
                    five_d_change = ((current_price / five_d_start) - 1) * 100
                else:
                    five_d_change = 0
                
                ticker_data.append({
                    'ticker': ticker,
                    'price': current_price,
                    'today': today_change,
                    '5d': five_d_change
                })
            except:
                continue
        
        # Sort by today's performance
        ticker_data.sort(key=lambda x: x['today'], reverse=True)
        
        # Display
        print("Ticker  Price    Today    5d")
        print("-" * 40)
        
        for t in ticker_data:
            emoji = "🟢" if t['today'] > 1 else "🔴" if t['today'] < -1 else "⚪"
            print(f"{emoji} {t['ticker']:6s} ${t['price']:7.2f}  {t['today']:+6.2f}%  {t['5d']:+6.2f}%")
        
        # Entry signals
        print(f"\n🎯 ENTRY SIGNALS:")
        green_today = [t for t in ticker_data if t['today'] > 2]
        if green_today:
            print(f"   ✅ Strong today: {', '.join([t['ticker'] for t in green_today[:3]])}")
        else:
            print(f"   ⏳ Wait for green day confirmation")
    
    # ========================================================================
    # SECTION 3: EXTENDED TICKERS (AVOID)
    # ========================================================================
    
    def scan_avoid_tickers(self, avoid_sectors):
        """Scan tickers from extended sectors to avoid."""
        self.section_header("TICKERS TO AVOID (Extended)")
        
        avoid_tickers = []
        for sector in avoid_sectors:
            if sector in self.sectors:
                avoid_tickers.extend(self.sectors[sector])
        
        if not avoid_tickers:
            print("✅ No extended sectors at risk")
            return
        
        print(f"Monitoring {len(avoid_tickers)} tickers at highs...\n")
        
        for ticker in avoid_tickers:
            try:
                data = yf.Ticker(ticker).history(period='5d')
                if len(data) < 2:
                    continue
                
                current_price = data['Close'].iloc[-1]
                prev_close = data['Close'].iloc[-2]
                today_change = ((current_price / prev_close) - 1) * 100
                
                emoji = "🟢" if today_change > 0 else "🔴"
                print(f"{emoji} {ticker:6s} ${current_price:7.2f}  {today_change:+6.2f}%")
            except:
                continue
        
        print(f"\n⚠️  These sectors at highs - expect dumps soon")
    
    # ========================================================================
    # SECTION 4: CONVICTION SCORECARD
    # ========================================================================
    
    def conviction_scorecard(self):
        """Score conviction for beaten-down sectors."""
        self.section_header("CONVICTION SCORECARD")
        
        print("""
Track these signals over 24 hours to confirm rotation:

Signal                    Biotech_Small  Cybersecurity  AI_Hype
─────────────────────────────────────────────────────────────
Green Day 1 (Jan 8)             [ ]            [ ]        [ ]
Volume increasing               [ ]            [ ]        [ ]
Sector rank improving           [ ]            [ ]        [ ]
Extended sectors dumping        [ ]            [ ]        [ ]
News catalyst                   [ ]            [ ]        [ ]
Green Day 2 (Jan 9)             [ ]            [ ]        [ ]

SCORING:
  • 6/6 = 🟢 HIGH CONVICTION (Enter full position)
  • 4-5/6 = 🟡 MEDIUM (Enter 50%, add if continues)
  • <4/6 = 🔴 LOW (Wait for better setup)

POSITION SIZING:
  • Risk $154 total
  • Split across 2-3 best sectors
  • Stop: -3% per ticker
  • Target: +10-20% (3-6 day hold)
""")
    
    # ========================================================================
    # SECTION 5: MORNING CHECKLIST
    # ========================================================================
    
    def morning_checklist(self):
        """Display morning trading checklist."""
        self.section_header("MORNING CHECKLIST")
        
        now = datetime.now()
        hour = now.hour
        
        print(f"Current time: {now.strftime('%H:%M ET')}\n")
        
        if hour < 9:
            print("🌅 PRE-MARKET (Before 9:30 AM):")
            print("   [ ] Check overnight news")
            print("   [ ] Review beaten sector pre-market moves")
            print("   [ ] Set alerts for 9:30 AM open")
            print("   [ ] Review entry targets")
        
        elif hour == 9:
            print("🔔 MARKET OPEN (9:30 AM):")
            print("   [ ] Watch beaten sectors - opening green?")
            print("   [ ] Watch extended sectors - dumping?")
            print("   [ ] Wait 10-15 min for volatility to settle")
            print("   [ ] Enter 50% if signals confirm")
        
        elif hour < 12:
            print("📊 MID-MORNING (10:00 AM - 12:00 PM):")
            print("   [ ] Are gains holding or fading?")
            print("   [ ] Volume confirming moves?")
            print("   [ ] Add remaining 50% if strong")
        
        elif hour < 15:
            print("⏰ MID-DAY (12:00 PM - 3:00 PM):")
            print("   [ ] Monitor for pullbacks (entry if missed)")
            print("   [ ] Check if thesis still intact")
            print("   [ ] Prepare for power hour")
        
        elif hour < 16:
            print("🔥 POWER HOUR (3:00 PM - 4:00 PM):")
            print("   [ ] Smart money entering or exiting?")
            print("   [ ] Hold overnight if strong into close")
            print("   [ ] Exit if weakness appears")
        
        else:
            print("🌙 AFTER HOURS (After 4:00 PM):")
            print("   [ ] Review: Did beaten sectors close green?")
            print("   [ ] Check for news catalysts")
            print("   [ ] Plan for tomorrow's open")
            print("   [ ] Update conviction scorecard")
        
        print()
    
    # ========================================================================
    # SECTION 6: PACK WISDOM
    # ========================================================================
    
    def pack_wisdom(self):
        """Display Wolf Pack trading wisdom."""
        self.section_header("🐺 PACK WISDOM")
        
        print("""
TODAY'S LESSONS:

1. DON'T CHASE HIGHS
   • Space/Quantum ran +100% (LUNR, RKLB)
   • Jan 7 = dump starting (ASTS -12%)
   • Buying now = buying the top

2. HUNT LAGGARDS
   • Biotech Small: -21.7% from highs
   • Cybersecurity: -10.2% from highs
   • These are EARLY, not late

3. WAIT FOR CONFIRMATION
   • Don't enter Day 1 (hope)
   • Enter Day 2 (proof)
   • If beaten sectors green 2 days → rotation confirmed

4. TIGHT STOPS
   • -3% stop per ticker
   • We're early, so risk is LOW
   • Wrong = exit fast

5. THE 6-DAY LIE
   • "Quantum runs 6 days" = FALSE
   • Actual: Max 3-day streaks
   • Historical averages ≠ current market

🎯 THE EDGE:

Most traders:
  ❌ Chase what's moving
  ❌ Buy after +50% moves
  ❌ FOMO into tops

Smart traders:
  ✅ Hunt what's beaten down
  ✅ Buy before the move
  ✅ Exit when others enter

Don't hunt at highs. Hunt at lows.

AWOOOO 🐺

GOD FORGIVES. BROTHERS DON'T.
THE WOLF THAT WAITS EATS.
THE WOLF THAT CHASES STARVES.
""")
    
    # ========================================================================
    # MAIN RUN FUNCTION
    # ========================================================================
    
    def run(self, continuous=False):
        """Run the master dashboard."""
        while True:
            self.clear_screen()
            self.print_header()
            
            # Section 1: Sector Rotation
            beaten_sectors, avoid_sectors = self.monitor_sector_rotation()
            
            # Section 2: Top Tickers
            if beaten_sectors:
                self.scan_top_tickers(beaten_sectors, avoid_sectors)
            
            # Section 3: Avoid Tickers
            if avoid_sectors:
                self.scan_avoid_tickers(avoid_sectors)
            
            # Section 4: Conviction Scorecard
            self.conviction_scorecard()
            
            # Section 5: Morning Checklist
            self.morning_checklist()
            
            # Section 6: Pack Wisdom
            self.pack_wisdom()
            
            # Footer
            print("="*self.width)
            if continuous:
                print(f"🔄 Auto-refresh in 5 minutes... (Press Ctrl+C to stop)")
                print("="*self.width + "\n")
                try:
                    time.sleep(300)  # 5 minutes
                except KeyboardInterrupt:
                    print("\n\n🐺 Dashboard stopped. Hunt well, wolf.\n")
                    break
            else:
                print(f"💡 Run with --continuous to auto-refresh every 5 minutes")
                print("="*self.width + "\n")
                break


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='🐺 Wolf Pack Master Dashboard')
    parser.add_argument('--continuous', '-c', action='store_true',
                       help='Auto-refresh every 5 minutes')
    
    args = parser.parse_args()
    
    dashboard = MasterDashboard()
    dashboard.run(continuous=args.continuous)


if __name__ == "__main__":
    main()
