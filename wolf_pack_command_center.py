#!/usr/bin/env python3
"""
🐺 WOLF PACK COMMAND CENTER - UNIFIED HUNTING DASHBOARD
========================================================

One dashboard to rule them all. Every hunting tool integrated.

TABS:
1. 🎯 PRESSURE MAP - Who's trapped, who's forced to act
2. 💰 SMART MONEY - Insider buying across the market
3. 🔫 TACTICAL - Live opportunity scanner
4. 📊 CONVICTION - Our ranked targets
5. 🔧 SETTINGS - Universe management

THE PHILOSOPHY:
We don't predict price. We predict WHO WILL BE FORCED TO BUY.

Built by Brokkr & Fenrir for the Wolf Pack
AWOOOO 🐺
"""

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import json
import subprocess
import sys
from pathlib import Path

# Page config
st.set_page_config(
    page_title="🐺 Wolf Pack Command Center",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark wolf theme
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .pressure-high {
        background-color: #ff4444;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .pressure-medium {
        background-color: #ffaa00;
        color: black;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .stMetric label {
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🐺 WOLF PACK COMMAND CENTER")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | AWOOOO!")

# ============================================================================
# SIDEBAR - GLOBAL CONTROLS
# ============================================================================

with st.sidebar:
    st.header("🎮 Hunt Controls")
    
    st.markdown("---")
    
    # Quick scan buttons
    st.subheader("⚡ Quick Scans")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎯 Pressure", help="Scan for trapped players"):
            with st.spinner("Hunting..."):
                result = subprocess.run(
                    ['python', 'hunt/pressure_framework.py'],
                    capture_output=True, text=True, timeout=300,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.success("Done!")
                st.rerun()
    
    with col2:
        if st.button("💰 Insiders", help="Scan SEC for insider buying"):
            with st.spinner("Hunting..."):
                result = subprocess.run(
                    ['python', 'hunt/smart_money_hunter.py', '--filings', '500'],
                    capture_output=True, text=True, timeout=300,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.success("Done!")
                st.rerun()
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("🔫 Tactical", help="Find tactical opportunities"):
            with st.spinner("Hunting..."):
                result = subprocess.run(
                    ['python', 'hunt/tactical_scanners.py'],
                    capture_output=True, text=True, timeout=300,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.success("Done!")
                st.rerun()
    
    with col4:
        if st.button("📋 Form 4", help="Check our universe"):
            with st.spinner("Scanning..."):
                result = subprocess.run(
                    ['python', 'hunt/form4_scanner.py'],
                    capture_output=True, text=True, timeout=120,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.success("Done!")
                st.rerun()
    
    col5, col6 = st.columns(2)
    
    with col5:
        if st.button("📡 Radar", help="Check regime and invisible signals"):
            with st.spinner("Scanning..."):
                result = subprocess.run(
                    ['python', 'wolf_radar.py', 'regime'],
                    capture_output=True, text=True, timeout=60,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.success("Done!")
                st.rerun()
    
    with col6:
        if st.button("🎰 Gamma", help="Scan for gamma squeeze setups"):
            with st.spinner("Scanning..."):
                result = subprocess.run(
                    ['python', 'wolf_gamma.py', 'scan', '--tickers', 
                     'GME,AMC,MARA,RIOT,SMCI,ARM,RGTI,QBTS'],
                    capture_output=True, text=True, timeout=120,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.success("Done!")
                st.rerun()
    
    st.markdown("---")
    
    # Run ALL scans
    if st.button("🚀 RUN ALL SCANS", type="primary", use_container_width=True):
        progress = st.progress(0)
        status = st.empty()
        
        status.text("🎯 Running Pressure Framework...")
        subprocess.run(['python', 'hunt/pressure_framework.py'],
                      capture_output=True, timeout=300,
                      cwd='/workspaces/trading-companion-2026')
        progress.progress(25)
        
        status.text("💰 Hunting Smart Money...")
        subprocess.run(['python', 'hunt/smart_money_hunter.py', '--filings', '500'],
                      capture_output=True, timeout=300,
                      cwd='/workspaces/trading-companion-2026')
        progress.progress(50)
        
        status.text("🔫 Running Tactical Scanners...")
        subprocess.run(['python', 'hunt/tactical_scanners.py'],
                      capture_output=True, timeout=300,
                      cwd='/workspaces/trading-companion-2026')
        progress.progress(75)
        
        status.text("📋 Checking Form 4...")
        subprocess.run(['python', 'hunt/form4_scanner.py'],
                      capture_output=True, timeout=120,
                      cwd='/workspaces/trading-companion-2026')
        progress.progress(100)
        
        status.text("✅ All scans complete!")
        st.success("AWOOOO! 🐺")
        st.rerun()
    
    st.markdown("---")
    
    # THE HUNT button - most important
    if st.button("🐺 HUNT TODAY", type="primary", use_container_width=True, help="Find best setups NOW"):
        with st.spinner("Hunting..."):
            result = subprocess.run(
                ['python', 'wolf_hunt.py', 'today', '--risk', '500'],
                capture_output=True, text=True, timeout=300,
                cwd='/workspaces/trading-companion-2026'
            )
            st.code(result.stdout or result.stderr, language="text")
    
    st.markdown("---")
    
    # Market status
    st.subheader("📈 Market Status")
    try:
        spy = yf.Ticker("SPY")
        hist = spy.history(period='1d')
        if not hist.empty:
            spy_price = hist['Close'].iloc[-1]
            spy_prev = spy.info.get('previousClose', spy_price)
            spy_change = ((spy_price - spy_prev) / spy_prev) * 100
            st.metric("SPY", f"${spy_price:.2f}", f"{spy_change:+.2f}%")
    except:
        st.warning("Market data unavailable")
    
    st.markdown("---")
    st.caption("🐺 Wolf Pack Trading System")
    st.caption("© 2026 | AWOOOO!")

# ============================================================================
# MAIN CONTENT - TABS
# ============================================================================

tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13 = st.tabs([
    "🐺 HUNT",
    "🎯 PRESSURE MAP",
    "💰 SMART MONEY",
    "🔫 TACTICAL",
    "📊 CONVICTION",
    "📤 EXPORT",
    "📓 JOURNAL",
    "👁️ WATCHER",
    "🧠 LEARNER",
    "🔗 CORRELATOR",
    "📡 RADAR",
    "🎰 GAMMA",
    "🏠 DEN",
    "🔧 SETTINGS"
])

# ============================================================================
# TAB 0: THE HUNT - Main Decision Engine
# ============================================================================

with tab0:
    st.header("🐺 THE HUNT - Should I Trade This?")
    st.caption("One command. Everything checked. Clear verdict.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        hunt_ticker = st.text_input("Enter ticker to hunt:", "", key="hunt_main_ticker", 
                                    placeholder="GME, IONQ, MARA...")
        
        col_a, col_b = st.columns(2)
        with col_a:
            hunt_risk = st.number_input("Risk amount ($):", min_value=100, max_value=10000, 
                                        value=500, step=100, key="hunt_risk")
        with col_b:
            st.write("")  # Spacer
            st.write("")
            if st.button("🐺 HUNT THIS TICKER", type="primary", key="hunt_single"):
                if hunt_ticker:
                    with st.spinner(f"Hunting {hunt_ticker.upper()}..."):
                        result = subprocess.run(
                            ['python', 'wolf_hunt.py', hunt_ticker.upper(), '--risk', str(hunt_risk)],
                            capture_output=True, text=True, timeout=120,
                            cwd='/workspaces/trading-companion-2026'
                        )
                        st.code(result.stdout or result.stderr, language="text")
    
    with col2:
        st.subheader("⚡ Quick Hunt")
        
        if st.button("🎯 What to Hunt TODAY?", use_container_width=True, key="hunt_today"):
            with st.spinner("Finding best setups..."):
                result = subprocess.run(
                    ['python', 'wolf_hunt.py', 'today', '--risk', str(hunt_risk)],
                    capture_output=True, text=True, timeout=300,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.code(result.stdout or result.stderr, language="text")
        
        if st.button("🌐 Scan ALL Universe", use_container_width=True, key="hunt_scan"):
            with st.spinner("Scanning all tickers..."):
                result = subprocess.run(
                    ['python', 'wolf_hunt.py', 'scan', '--risk', str(hunt_risk)],
                    capture_output=True, text=True, timeout=600,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.code(result.stdout or result.stderr, language="text")
    
    st.markdown("---")
    
    st.subheader("📖 The Verdict System")
    
    st.markdown("""
    | Verdict | Meaning | Action |
    |---------|---------|--------|
    | 🟢 **HUNT** | Multiple signals aligned, clear setup | Put money down |
    | 🟡 **STALK** | Interesting but incomplete | Watch for better entry |
    | 🔴 **PASS** | Not enough edge | Skip, no trade |
    
    **7 Signals Checked:**
    1. **Gamma Squeeze** - Options chain pressure
    2. **Momentum** - Price trend strength
    3. **Volume** - Confirmation and accumulation
    4. **Short Squeeze** - Shorts getting trapped
    5. **Technical Setup** - Clean levels, breakouts
    6. **Market Regime** - Risk-on/off environment
    7. **Sector Momentum** - Peers moving together
    
    **The Three Wolves:**
    - 🔧 **Brokkr** validates signals
    - 🐺 **Fenrir** checks R:R  
    - 👑 **Tyr** makes the call
    """)

# ============================================================================
# TAB 1: PRESSURE MAP
# ============================================================================

with tab1:
    st.header("🎯 PRESSURE MAP - Who's Trapped?")
    st.caption("The question isn't 'what does the chart say'. It's 'who will be FORCED to buy?'")
    
    # Try to load pressure data from log file
    pressure_log = Path('/workspaces/trading-companion-2026/logs/pressure_scan_latest.json')
    
    # Also try to parse from stdout if log doesn't exist
    if not pressure_log.exists():
        st.info("⏳ No pressure scan data yet. Click '🎯 Pressure' in sidebar to scan.")
        
        # Show the framework explanation
        st.markdown("""
        ### 🐺 THE PRESSURE FRAMEWORK
        
        Every stock has **PLAYERS**. Each player has **CONSTRAINTS**.
        
        | Player | Constraint |
        |--------|------------|
        | **SHORTS** | Pay borrow rate DAILY. Must cover eventually. |
        | **MARKET MAKERS** | Must stay delta neutral. Mechanical hedging. |
        | **RETAIL** | Emotional. Small accounts. FOMO and panic. |
        | **INSTITUTIONS** | Need to fill large orders quietly. |
        | **INSIDERS** | Know the truth. Can't hide (Form 4). |
        
        **We detect:**
        - 🔴 SHORT SQUEEZE - Shorts bleeding, forced to cover
        - 🟠 LAGGARD CATCH-UP - Sector ripped, this stock didn't
        - 🟡 PANIC RECOVERY - Retail panic sold, institutions buying cheap
        - 🟣 CAPITULATION - Sellers exhausted, bottom forming
        """)
    else:
        try:
            with open(pressure_log, 'r') as f:
                pressure_data = json.load(f)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            signals = pressure_data.get('signals', [])
            
            short_squeeze = len([s for s in signals if s.get('type') == 'short_squeeze'])
            panic_recovery = len([s for s in signals if s.get('type') == 'panic_recovery'])
            capitulation = len([s for s in signals if s.get('type') == 'capitulation'])
            laggard = len([s for s in signals if s.get('type') == 'laggard_catchup'])
            
            with col1:
                st.metric("🔴 Short Squeeze", short_squeeze, "shorts bleeding")
            with col2:
                st.metric("🟡 Panic Recovery", panic_recovery, "retail sold")
            with col3:
                st.metric("🟣 Capitulation", capitulation, "sellers exhausted")
            with col4:
                st.metric("🟠 Laggard", laggard, "must catch up")
            
            st.markdown("---")
            
            # Top signals table
            st.subheader("🔥 Top Pressure Signals")
            
            if signals:
                df = pd.DataFrame(signals[:20])  # Top 20
                
                # Format for display
                display_cols = ['ticker', 'type', 'score', 'thesis', 'trapped_player']
                available_cols = [c for c in display_cols if c in df.columns]
                
                if available_cols:
                    st.dataframe(
                        df[available_cols].style.background_gradient(subset=['score'] if 'score' in available_cols else [], cmap='RdYlGn'),
                        use_container_width=True,
                        height=400
                    )
            else:
                st.warning("No pressure signals detected")
                
        except Exception as e:
            st.error(f"Error loading pressure data: {e}")
            st.info("Run a pressure scan to generate data")

# ============================================================================
# TAB 2: SMART MONEY
# ============================================================================

with tab2:
    st.header("💰 SMART MONEY - Insider Buying")
    st.caption("Form 4 Transaction Code P = Open Market Purchases. The only signal that matters.")
    
    smart_money_log = Path('/workspaces/trading-companion-2026/logs/smart_money_latest.json')
    
    if not smart_money_log.exists():
        st.info("⏳ No smart money scan data yet. Click '💰 Insiders' in sidebar to scan.")
        
        st.markdown("""
        ### 🐺 WHY INSIDER BUYING MATTERS
        
        - **Insiders can sell for many reasons** (diversification, taxes, etc.)
        - **Insiders only BUY for ONE reason** - they think the stock is going UP
        - **They have perfect information** - they know what's coming
        - **Form 4 is public** - they can't hide it (filed within 2 days)
        
        **What we look for:**
        - 💰 Transaction Code "P" = Open market purchase
        - 🎯 Cluster buying = Multiple insiders buying together
        - 📈 Size matters = $100K+ is meaningful
        - ⏰ Timing = Recent is better
        """)
    else:
        try:
            with open(smart_money_log, 'r') as f:
                smart_data = json.load(f)
            
            purchases = smart_data.get('purchases', [])
            
            # Summary
            col1, col2, col3 = st.columns(3)
            
            total_value = sum([p.get('value', 0) for p in purchases])
            unique_tickers = len(set([p.get('ticker', '') for p in purchases]))
            
            with col1:
                st.metric("💰 Total Value", f"${total_value:,.0f}")
            with col2:
                st.metric("📊 Unique Tickers", unique_tickers)
            with col3:
                st.metric("📝 Total Purchases", len(purchases))
            
            st.markdown("---")
            
            # Purchases table
            st.subheader("🔥 Recent Insider Purchases")
            
            if purchases:
                df = pd.DataFrame(purchases[:30])  # Top 30
                
                # Sort by value
                if 'value' in df.columns:
                    df = df.sort_values('value', ascending=False)
                
                st.dataframe(df, use_container_width=True, height=500)
            else:
                st.info("No purchases found in this scan")
                
        except Exception as e:
            st.error(f"Error loading smart money data: {e}")

# ============================================================================
# TAB 3: TACTICAL
# ============================================================================

with tab3:
    st.header("🔫 TACTICAL SCANNERS - Live Opportunities")
    st.caption("Not random patterns. SPECIFIC SITUATIONS that cause 10-20% moves.")
    
    tactical_log = Path('/workspaces/trading-companion-2026/logs/tactical_scan_latest.json')
    
    if not tactical_log.exists():
        st.info("⏳ No tactical scan data yet. Click '🔫 Tactical' in sidebar to scan.")
        
        st.markdown("""
        ### 🐺 THE 5 TACTICAL HUNTS
        
        | Hunt | What It Finds |
        |------|---------------|
        | **Leader-Follower Lag** | When IONQ moves, RGTI follows. Buy the lag. |
        | **Divergence Sniff** | Sector down, one stock flat = accumulation |
        | **Squeeze Stalker** | High short + low float + rising vol = powder keg |
        | **Second Day Momentum** | Day 1 surprise, Day 2 predictable continuation |
        | **Wounded Prey Recovery** | Volume spike after capitulation = bottom |
        
        **Why these work:**
        - Information asymmetry - insiders accumulating before news
        - Forced buying - shorts covering, gamma squeeze
        - Supply exhaustion - float absorbed, catalyst = moon
        - Herd stampede - narrative catches fire, FOMO
        """)
    else:
        try:
            with open(tactical_log, 'r') as f:
                tactical_data = json.load(f)
            
            # Show each scanner's results
            for scanner_name, results in tactical_data.items():
                with st.expander(f"🔫 {scanner_name.replace('_', ' ').title()}", expanded=True):
                    if results:
                        df = pd.DataFrame(results)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No signals from this scanner")
                        
        except Exception as e:
            st.error(f"Error loading tactical data: {e}")

# ============================================================================
# TAB 4: CONVICTION
# ============================================================================

with tab4:
    st.header("📊 CONVICTION RANKINGS")
    st.caption("Our ranked targets based on all signals combined")
    
    # Load conviction data
    conviction_log = Path('/workspaces/trading-companion-2026/logs/conviction_rankings_latest.json')
    
    if conviction_log.exists():
        try:
            with open(conviction_log, 'r') as f:
                rankings = json.load(f)
            
            ranking_list = rankings.get('rankings', [])
            
            if ranking_list:
                # Top 3 cards
                st.subheader("🏆 Top 3 Targets")
                
                cols = st.columns(3)
                for i, col in enumerate(cols):
                    if i < len(ranking_list):
                        r = ranking_list[i]
                        with col:
                            st.metric(
                                f"#{i+1} {r.get('ticker', 'N/A')}",
                                f"{r.get('total_score', 0)}/100",
                                r.get('conviction', '')
                            )
                
                st.markdown("---")
                
                # Full table
                st.subheader("📋 Full Rankings")
                df = pd.DataFrame(ranking_list)
                st.dataframe(df, use_container_width=True, height=400)
            else:
                st.info("No rankings available")
                
        except Exception as e:
            st.error(f"Error loading conviction data: {e}")
    else:
        st.info("⏳ No conviction data. Run conviction scanner.")
        
        if st.button("🚀 Run Conviction Scanner"):
            with st.spinner("Analyzing..."):
                subprocess.run(['python', 'fast_conviction_scanner.py'],
                              capture_output=True, timeout=120,
                              cwd='/workspaces/trading-companion-2026')
            st.success("Done!")
            st.rerun()

# ============================================================================
# TAB 5: EXPORT
# ============================================================================

with tab5:
    st.header("📤 EXPORT - ATP/Robinhood Watchlists")
    st.caption("One button. Top targets. Ready to import into your broker.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_targets = st.slider("Number of targets", 5, 30, 20)
    
    with col2:
        if st.button("🚀 GENERATE WATCHLIST", type="primary", use_container_width=True):
            with st.spinner("Aggregating signals and generating exports..."):
                result = subprocess.run(
                    ['python', 'wolf_export.py', '--targets', str(num_targets)],
                    capture_output=True, text=True, timeout=180,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.success("Watchlists generated!")
                st.rerun()
    
    st.markdown("---")
    
    # Check for export files
    export_path = Path('/workspaces/trading-companion-2026/exports')
    
    if export_path.exists():
        files = list(export_path.glob('wolf_*'))
        
        if files:
            st.subheader("📁 Available Exports")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**For Fidelity ATP:**")
                atp_file = export_path / 'wolf_atp_watchlist.csv'
                if atp_file.exists():
                    with open(atp_file, 'r') as f:
                        st.download_button(
                            "⬇️ Download ATP CSV",
                            f.read(),
                            file_name="wolf_atp_watchlist.csv",
                            mime="text/csv"
                        )
                
                st.markdown("**For TradingView:**")
                tv_file = export_path / 'wolf_tradingview.txt'
                if tv_file.exists():
                    with open(tv_file, 'r') as f:
                        st.download_button(
                            "⬇️ Download TradingView",
                            f.read(),
                            file_name="wolf_tradingview.txt",
                            mime="text/plain"
                        )
            
            with col2:
                st.markdown("**For Robinhood:**")
                rh_file = export_path / 'wolf_robinhood.csv'
                if rh_file.exists():
                    with open(rh_file, 'r') as f:
                        st.download_button(
                            "⬇️ Download Robinhood CSV",
                            f.read(),
                            file_name="wolf_robinhood.csv",
                            mime="text/csv"
                        )
                
                st.markdown("**Full Report:**")
                report_file = export_path / 'wolf_targets_report.md'
                if report_file.exists():
                    with open(report_file, 'r') as f:
                        st.download_button(
                            "⬇️ Download Full Report",
                            f.read(),
                            file_name="wolf_targets_report.md",
                            mime="text/markdown"
                        )
            
            st.markdown("---")
            
            # Show preview
            st.subheader("👀 Preview")
            json_file = export_path / 'wolf_targets.json'
            if json_file.exists():
                with open(json_file, 'r') as f:
                    targets = json.load(f)
                    if 'targets' in targets:
                        df = pd.DataFrame(targets['targets'][:10])
                        if not df.empty:
                            display_cols = ['rank', 'ticker', 'confidence', 'signal_source', 'sector', 'current_price', 'trapped_player']
                            available = [c for c in display_cols if c in df.columns]
                            st.dataframe(df[available], use_container_width=True)
        else:
            st.info("No exports yet. Click 'Generate Watchlist' to create them.")
    else:
        st.info("No exports yet. Click 'Generate Watchlist' to create them.")
    
    st.markdown("---")
    
    # Morning briefing
    st.subheader("📋 Morning Briefing")
    
    if st.button("📝 Generate Morning Briefing"):
        with st.spinner("Generating briefing..."):
            result = subprocess.run(
                ['python', 'morning_briefing.py'],
                capture_output=True, text=True, timeout=120,
                cwd='/workspaces/trading-companion-2026'
            )
            st.success("Briefing generated!")
            st.rerun()
    
    briefing_file = export_path / 'morning_briefing_latest.md' if export_path.exists() else None
    if briefing_file and briefing_file.exists():
        with open(briefing_file, 'r') as f:
            briefing_content = f.read()
            st.download_button(
                "⬇️ Download Morning Briefing",
                briefing_content,
                file_name=f"morning_briefing_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
            
            with st.expander("📖 View Briefing"):
                st.markdown(briefing_content[:3000] + "..." if len(briefing_content) > 3000 else briefing_content)

# ============================================================================
# TAB 6: JOURNAL
# ============================================================================

with tab6:
    st.header("📓 TRADE JOURNAL")
    st.caption("Track every trade. Learn from every hunt.")
    
    # Load journal stats
    journal_file = Path('/workspaces/trading-companion-2026/data/trade_journal.json')
    
    if journal_file.exists():
        try:
            with open(journal_file, 'r') as f:
                journal_data = json.load(f)
            
            trades = journal_data.get('trades', [])
            
            # Stats
            closed = [t for t in trades if t.get('status', '') != 'open']
            wins = [t for t in closed if t.get('status') == 'closed_win']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Trades", len(trades))
            with col2:
                st.metric("Open", len([t for t in trades if t.get('status') == 'open']))
            with col3:
                win_rate = (len(wins) / len(closed) * 100) if closed else 0
                st.metric("Win Rate", f"{win_rate:.1f}%")
            with col4:
                total_pnl = sum(t.get('pnl_dollars', 0) or 0 for t in closed)
                st.metric("Total P&L", f"${total_pnl:+,.2f}")
            
            st.markdown("---")
            
            # Open positions
            st.subheader("📈 Open Positions")
            open_trades = [t for t in trades if t.get('status') == 'open']
            if open_trades:
                df = pd.DataFrame(open_trades)
                display_cols = ['ticker', 'entry_price', 'shares', 'signal_source', 'entry_date', 'thesis']
                available = [c for c in display_cols if c in df.columns]
                st.dataframe(df[available], use_container_width=True)
            else:
                st.info("No open positions")
            
            st.markdown("---")
            
            # Recent trades
            st.subheader("📊 Recent Closed Trades")
            if closed:
                df = pd.DataFrame(closed[-10:])
                display_cols = ['ticker', 'pnl_percent', 'pnl_dollars', 'signal_source', 'thesis_correct', 'lessons']
                available = [c for c in display_cols if c in df.columns]
                st.dataframe(df[available], use_container_width=True)
            else:
                st.info("No closed trades yet")
                
        except Exception as e:
            st.error(f"Error loading journal: {e}")
    else:
        st.info("📓 No trades logged yet.")
        st.markdown("""
        **To log trades, use the CLI:**
        ```bash
        python trade_journal.py
        ```
        
        **Or quick commands:**
        ```bash
        python trade_journal.py stats    # View statistics
        python trade_journal.py open     # View open positions
        python trade_journal.py report   # Generate report
        ```
        """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Generate Journal Report"):
            subprocess.run(['python', 'trade_journal.py', 'report'],
                          capture_output=True, timeout=30,
                          cwd='/workspaces/trading-companion-2026')
            st.success("Report generated!")
    
    with col2:
        if st.button("🔄 Run Backtest"):
            with st.spinner("Running backtest (this takes a few minutes)..."):
                result = subprocess.run(['python', 'backtest_pressure.py'],
                              capture_output=True, text=True, timeout=600,
                              cwd='/workspaces/trading-companion-2026')
            st.success("Backtest complete! Check exports/backtest_results.csv")

# ============================================================================
# TAB 7: WATCHER - Real-time Monitoring
# ============================================================================

with tab7:
    st.header("👁️ Wolf Watcher - Real-Time Monitoring")
    
    st.markdown("""
    The eyes that never close. Monitor Form 4 filings, volume spikes, 
    laggard opportunities, and stop prices in real-time.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎮 Watcher Controls")
        
        if st.button("🧪 Test Alerts", use_container_width=True):
            with st.spinner("Testing..."):
                result = subprocess.run(
                    ['python', 'wolf_watcher.py', 'test'],
                    capture_output=True, text=True, timeout=30,
                    cwd='/workspaces/trading-companion-2026'
                )
                if result.returncode == 0:
                    st.success("Alert test complete!")
                    st.code(result.stdout[-2000:])
                else:
                    st.error(f"Error: {result.stderr}")
        
        if st.button("📊 Quick Volume Check", use_container_width=True):
            with st.spinner("Checking volume..."):
                result = subprocess.run(
                    ['python', 'wolf_watcher.py', 'check', '--volume'],
                    capture_output=True, text=True, timeout=120,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.code(result.stdout[-2000:] if result.stdout else "No output")
        
        if st.button("🎯 Quick Laggard Check", use_container_width=True):
            with st.spinner("Checking laggards..."):
                result = subprocess.run(
                    ['python', 'wolf_watcher.py', 'check', '--laggards'],
                    capture_output=True, text=True, timeout=120,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.code(result.stdout[-2000:] if result.stdout else "No output")
    
    with col2:
        st.subheader("🛑 Stop Management")
        
        # Add stop form
        with st.form("add_stop"):
            stop_ticker = st.text_input("Ticker")
            stop_price = st.number_input("Stop Price", min_value=0.0, step=0.01)
            entry_price = st.number_input("Entry Price (optional)", min_value=0.0, step=0.01)
            
            if st.form_submit_button("Add Stop"):
                if stop_ticker and stop_price > 0:
                    cmd = ['python', 'wolf_watcher.py', 'stops', '--add', 
                           f"{stop_ticker}:{stop_price}:{entry_price}" if entry_price > 0 
                           else f"{stop_ticker}:{stop_price}"]
                    result = subprocess.run(cmd, capture_output=True, text=True,
                                          cwd='/workspaces/trading-companion-2026')
                    st.success(f"Stop added: {stop_ticker} @ ${stop_price}")
        
        # List stops
        if st.button("📋 List Stops"):
            result = subprocess.run(
                ['python', 'wolf_watcher.py', 'stops', '--list'],
                capture_output=True, text=True,
                cwd='/workspaces/trading-companion-2026'
            )
            st.code(result.stdout if result.stdout else "No stops configured")
    
    st.markdown("---")
    
    st.subheader("📜 Recent Alerts")
    alerts_file = Path("logs/wolf_alerts.jsonl")
    if alerts_file.exists():
        alerts = []
        with open(alerts_file) as f:
            for line in f:
                try:
                    alerts.append(json.loads(line))
                except:
                    pass
        
        if alerts:
            recent = alerts[-20:][::-1]  # Last 20, newest first
            for alert in recent:
                icon = {"form4": "📋", "volume_spike": "📈", "laggard": "🎯", 
                        "stop_hit": "🛑", "system": "⚙️"}.get(alert.get("type"), "🔔")
                priority = alert.get("priority", "normal")
                color = "🔴" if priority == "critical" else "🟡" if priority == "high" else "⚪"
                
                time_str = datetime.fromisoformat(alert["timestamp"]).strftime("%H:%M:%S")
                st.markdown(f"{color} **{time_str}** {icon} **{alert['ticker']}**: {alert['message']}")
        else:
            st.info("No alerts yet. Run the watcher to generate alerts.")
    else:
        st.info("No alerts file found. Run `python wolf_watcher.py watch` to start monitoring.")
    
    st.markdown("---")
    st.code("""
# Start real-time watcher (runs continuously)
python wolf_watcher.py watch

# One-time checks
python wolf_watcher.py check --all
python wolf_watcher.py check --volume
python wolf_watcher.py check --laggards

# Manage watchlist
python wolf_watcher.py watchlist --init
python wolf_watcher.py watchlist --add TICKER
python wolf_watcher.py watchlist --list
    """, language="bash")

# ============================================================================
# TAB 8: LEARNER - Personal Trading Intelligence
# ============================================================================

with tab8:
    st.header("🧠 Wolf Learner - Your Personal Trading Intelligence")
    
    st.markdown("""
    The system that learns YOU. Analyzes your trade history, identifies your strengths
    and weaknesses, and weights signals based on YOUR track record.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Build Your Profile")
        
        if st.button("🧠 Analyze My Trading", type="primary", use_container_width=True):
            with st.spinner("Analyzing your trades..."):
                result = subprocess.run(
                    ['python', 'wolf_learner.py', 'profile'],
                    capture_output=True, text=True, timeout=60,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.code(result.stdout[-3000:] if result.stdout else "No trades found. Log some trades first!")
    
    with col2:
        st.subheader("⚖️ Signal Weights")
        
        signal_type = st.selectbox("Signal Type", [
            "insider_buy", "short_squeeze", "capitulation", "momentum",
            "laggard", "volume_spike", "pocket_pivot", "wolf_signal", "manual"
        ])
        
        if st.button("Get Weight", use_container_width=True):
            result = subprocess.run(
                ['python', 'wolf_learner.py', 'weight', signal_type],
                capture_output=True, text=True,
                cwd='/workspaces/trading-companion-2026'
            )
            st.code(result.stdout if result.stdout else "No data")
        
        if st.button("Position Size Suggestion", use_container_width=True):
            result = subprocess.run(
                ['python', 'wolf_learner.py', 'size', signal_type],
                capture_output=True, text=True,
                cwd='/workspaces/trading-companion-2026'
            )
            st.code(result.stdout if result.stdout else "No data")
    
    st.markdown("---")
    
    st.subheader("📝 Record Skipped Signal")
    
    with st.form("skip_signal"):
        skip_col1, skip_col2, skip_col3 = st.columns(3)
        
        with skip_col1:
            skip_ticker = st.text_input("Ticker Skipped")
        with skip_col2:
            skip_signal = st.selectbox("Signal Type", [
                "insider_buy", "short_squeeze", "capitulation", "momentum",
                "laggard", "volume_spike"
            ], key="skip_signal_type")
        with skip_col3:
            skip_reason = st.text_input("Reason (optional)")
        
        if st.form_submit_button("Record Skip"):
            if skip_ticker:
                cmd = ['python', 'wolf_learner.py', 'skip', skip_ticker.upper(), skip_signal]
                if skip_reason:
                    cmd.extend(['--reason', skip_reason])
                result = subprocess.run(cmd, capture_output=True, text=True,
                                       cwd='/workspaces/trading-companion-2026')
                st.success(f"Recorded skip: {skip_ticker.upper()}")
    
    st.markdown("---")
    
    # Load and display profile if exists
    profile_file = Path("logs/wolf_profile.json")
    if profile_file.exists():
        with open(profile_file) as f:
            profile = json.load(f)
        
        if "overall" in profile:
            st.subheader("📈 Your Profile Summary")
            
            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
            
            with metrics_col1:
                st.metric("Total Trades", profile["total_trades"])
            with metrics_col2:
                st.metric("Win Rate", f"{profile['overall']['win_rate']:.1f}%")
            with metrics_col3:
                st.metric("Expectancy", f"{profile['overall']['expectancy']:.2f}")
            with metrics_col4:
                st.metric("Profit Factor", f"{profile['overall']['profit_factor']:.2f}")
            
            if profile.get("strengths"):
                st.subheader("💪 Your Strengths")
                for s in profile["strengths"][:3]:
                    st.success(f"✅ {s['type'].upper()}: {s['name']} ({s['win_rate']:.0f}% win rate)")
            
            if profile.get("weaknesses"):
                st.subheader("⚠️ Your Weaknesses")
                for w in profile["weaknesses"][:3]:
                    st.warning(f"❌ {w['type'].upper()}: {w['name']} ({w['win_rate']:.0f}% win rate)")

# ============================================================================
# TAB 9: CORRELATOR - Portfolio Risk Intelligence
# ============================================================================

with tab9:
    st.header("🔗 Wolf Correlator - Portfolio Risk Intelligence")
    
    st.markdown("""
    Real portfolio thinking. Track sector exposure, correlations, and get warned
    before you accidentally concentrate risk.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Portfolio Analysis")
        
        if st.button("🔍 Analyze Portfolio", type="primary", use_container_width=True):
            with st.spinner("Analyzing..."):
                result = subprocess.run(
                    ['python', 'wolf_correlator.py', 'portfolio', '--analyze'],
                    capture_output=True, text=True, timeout=120,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.code(result.stdout[-3000:] if result.stdout else "No positions. Add some first!")
        
        if st.button("📥 Load Demo Portfolio", use_container_width=True):
            result = subprocess.run(
                ['python', 'wolf_correlator.py', 'demo'],
                capture_output=True, text=True, timeout=120,
                cwd='/workspaces/trading-companion-2026'
            )
            st.success("Demo portfolio loaded!")
            st.code(result.stdout[-3000:])
        
        if st.button("💡 Get Diversification Ideas", use_container_width=True):
            result = subprocess.run(
                ['python', 'wolf_correlator.py', 'suggest'],
                capture_output=True, text=True,
                cwd='/workspaces/trading-companion-2026'
            )
            st.code(result.stdout if result.stdout else "Add positions first")
    
    with col2:
        st.subheader("🎯 Check New Position")
        
        check_ticker = st.text_input("Ticker to Check", key="corr_check_ticker")
        
        if st.button("Check Correlations", use_container_width=True):
            if check_ticker:
                result = subprocess.run(
                    ['python', 'wolf_correlator.py', 'check', check_ticker.upper()],
                    capture_output=True, text=True, timeout=60,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.code(result.stdout if result.stdout else "Error checking")
        
        st.markdown("---")
        
        st.subheader("➕ Add Position")
        
        with st.form("add_position"):
            pos_ticker = st.text_input("Ticker")
            pos_shares = st.number_input("Shares", min_value=0.0, step=1.0)
            pos_price = st.number_input("Entry Price", min_value=0.0, step=0.01)
            
            if st.form_submit_button("Add Position"):
                if pos_ticker and pos_shares > 0 and pos_price > 0:
                    result = subprocess.run(
                        ['python', 'wolf_correlator.py', 'portfolio', '--add',
                         f"{pos_ticker.upper()}:{pos_shares}:{pos_price}"],
                        capture_output=True, text=True,
                        cwd='/workspaces/trading-companion-2026'
                    )
                    st.success(f"Added: {pos_ticker.upper()}")
    
    st.markdown("---")
    
    st.subheader("🔗 Check Correlation Between Tickers")
    
    corr_col1, corr_col2 = st.columns(2)
    with corr_col1:
        ticker1 = st.text_input("Ticker 1", key="corr_t1")
    with corr_col2:
        ticker2 = st.text_input("Ticker 2", key="corr_t2")
    
    if st.button("Calculate Correlation"):
        if ticker1 and ticker2:
            result = subprocess.run(
                ['python', 'wolf_correlator.py', 'correlation', 
                 ticker1.upper(), ticker2.upper()],
                capture_output=True, text=True, timeout=30,
                cwd='/workspaces/trading-companion-2026'
            )
            st.code(result.stdout if result.stdout else "Error")
    
    st.markdown("---")
    st.info("""
    💡 **Correlation Guide:**
    - 🔴 **> 0.85**: Essentially same position - avoid doubling up
    - 🟡 **0.70-0.85**: High correlation - consider as partial position
    - 🟢 **0.50-0.70**: Moderate - some diversification benefit
    - ⚪ **< 0.50**: Low correlation - good diversification
    """)

# ============================================================================
# TAB 10: RADAR - The Invisible
# ============================================================================

with tab10:
    st.header("📡 RADAR - The Invisible")
    st.caption("Second-order effects. What nobody else sees. What comes BEFORE.")
    
    # Regime status at top
    st.subheader("🌡️ Market Regime")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🔍 Check Regime", key="radar_regime"):
            with st.spinner("Reading market regime..."):
                result = subprocess.run(
                    ['python', 'wolf_radar.py', 'regime'],
                    capture_output=True, text=True, timeout=60,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.code(result.stdout or result.stderr, language="text")
    
    with col2:
        if st.button("📅 Calendar", key="radar_calendar"):
            with st.spinner("Loading mechanical calendar..."):
                result = subprocess.run(
                    ['python', 'wolf_radar.py', 'calendar'],
                    capture_output=True, text=True, timeout=60,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.code(result.stdout or result.stderr, language="text")
    
    with col3:
        if st.button("🔬 Full Scan", key="radar_full"):
            with st.spinner("Running full radar scan..."):
                result = subprocess.run(
                    ['python', 'wolf_radar.py', 'scan'],
                    capture_output=True, text=True, timeout=120,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.code(result.stdout or result.stderr, language="text")
    
    st.markdown("---")
    
    st.subheader("📡 Radar Detectors")
    
    st.markdown("""
    | Detector | What It Sees | Edge |
    |----------|--------------|------|
    | **Pre-Filing** | Insider signature BEFORE Form 4 | Trade before the crowd knows |
    | **Regime** | Risk-on/off/rotation/chop | Know WHEN to be aggressive |
    | **Absence** | Dogs that didn't bark | Quiet accumulation signals |
    | **Calendar** | Forced mechanical flows | Trade predictable moves |
    | **Stealth** | Hidden accumulation patterns | Spot smart money quietly entering |
    | **Reflexivity** | Self-reinforcing spirals | Catch momentum before obvious |
    """)
    
    st.markdown("---")
    
    # Single ticker radar
    st.subheader("🎯 Single Ticker Radar")
    
    radar_ticker = st.text_input("Enter ticker:", "IONQ", key="radar_ticker")
    
    if st.button("🔍 Deep Scan Ticker", key="radar_single"):
        with st.spinner(f"Running radar on {radar_ticker}..."):
            result = subprocess.run(
                ['python', 'wolf_radar.py', 'single', radar_ticker.upper()],
                capture_output=True, text=True, timeout=60,
                cwd='/workspaces/trading-companion-2026'
            )
            st.code(result.stdout or result.stderr, language="text")

# ============================================================================
# TAB 11: GAMMA - Squeeze Predictor
# ============================================================================

with tab11:
    st.header("🎰 GAMMA MAP - Squeeze Predictor")
    st.caption("Options chain analysis. Market makers HAVE to hedge. We can SEE this building.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Quick Gamma Scan")
        
        # Default high-gamma tickers
        gamma_tickers = st.text_area(
            "Tickers to scan (comma separated):",
            "GME, AMC, MARA, RIOT, SMCI, ARM, RGTI, QBTS, IONQ",
            key="gamma_tickers"
        )
        
        if st.button("🎰 Scan for Gamma", key="gamma_scan"):
            tickers = gamma_tickers.replace(" ", "")
            with st.spinner("Analyzing options chains..."):
                result = subprocess.run(
                    ['python', 'wolf_gamma.py', 'scan', '--tickers', tickers],
                    capture_output=True, text=True, timeout=120,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.code(result.stdout or result.stderr, language="text")
    
    with col2:
        st.subheader("🗺️ Deep Gamma Map")
        
        gamma_single = st.text_input("Ticker for deep dive:", "GME", key="gamma_single")
        
        if st.button("🔬 Deep Gamma Analysis", key="gamma_deep"):
            with st.spinner(f"Mapping gamma for {gamma_single}..."):
                result = subprocess.run(
                    ['python', 'wolf_gamma.py', 'map', gamma_single.upper()],
                    capture_output=True, text=True, timeout=60,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.code(result.stdout or result.stderr, language="text")
    
    st.markdown("---")
    
    st.subheader("📖 Gamma Squeeze Mechanics")
    
    st.markdown("""
    **HOW IT WORKS:**
    
    1. **Calls get bought** → MMs sell calls to provide liquidity
    2. **MMs must hedge** → They buy shares to stay delta neutral
    3. **Price rises** → Calls go more ITM, delta increases
    4. **More hedging needed** → MMs buy MORE shares
    5. **Feedback loop** → Price rockets 🚀
    
    **WHAT WE MEASURE:**
    
    | Metric | Meaning | Squeeze Signal |
    |--------|---------|----------------|
    | **Call/Put OI Ratio** | Bullish positioning | > 2:1 = bullish, > 5:1 = extreme |
    | **Gamma Wall** | High-OI strike price | Magnet for price |
    | **Near-Term Expiry** | This week's options | Max gamma effect |
    | **OTM Call Fuel** | Cheap calls above price | Rocket fuel if triggered |
    | **Volume Ratio** | Today's call vs put volume | Momentum indicator |
    """)

# ============================================================================
# TAB 12: DEN - Paper Trading
# ============================================================================

with tab12:
    st.header("🏠 WOLF DEN - Paper Trading Proving Ground")
    st.caption("Prove the edge before you risk real capital. Track every decision.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Show current status
        if st.button("📊 Refresh Status", key="den_refresh"):
            pass  # Just triggers rerun
        
        result = subprocess.run(
            ['python', 'wolf_den.py', 'status'],
            capture_output=True, text=True, timeout=30,
            cwd='/workspaces/trading-companion-2026'
        )
        st.code(result.stdout or result.stderr, language="text")
    
    with col2:
        st.subheader("⚡ Quick Actions")
        
        # Check stops
        if st.button("🛑 Check Stops/Targets", key="den_check"):
            result = subprocess.run(
                ['python', 'wolf_den.py', 'check'],
                capture_output=True, text=True, timeout=30,
                cwd='/workspaces/trading-companion-2026'
            )
            st.code(result.stdout or result.stderr, language="text")
        
        # Stats
        if st.button("📈 Show Stats", key="den_stats"):
            result = subprocess.run(
                ['python', 'wolf_den.py', 'stats'],
                capture_output=True, text=True, timeout=30,
                cwd='/workspaces/trading-companion-2026'
            )
            st.code(result.stdout or result.stderr, language="text")
    
    st.markdown("---")
    
    st.subheader("🎯 New Paper Trade")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        trade_ticker = st.text_input("Ticker:", "", key="den_ticker")
        trade_signal = st.selectbox("Signal Type:", 
            ["pressure", "gamma", "insider", "tactical", "conviction", "manual"],
            key="den_signal")
    
    with col2:
        trade_reason = st.text_input("Reason:", "", key="den_reason")
        trade_stop = st.slider("Stop Loss %:", 3, 15, 8, key="den_stop")
    
    with col3:
        trade_target = st.slider("Target %:", 5, 30, 15, key="den_target")
    
    col4, col5 = st.columns(2)
    
    with col4:
        if st.button("🟢 BUY", type="primary", key="den_buy"):
            if trade_ticker:
                stop = trade_stop / 100
                target = trade_target / 100
                result = subprocess.run(
                    ['python', 'wolf_den.py', 'buy', trade_ticker.upper(),
                     '--signal', trade_signal,
                     '--reason', trade_reason or 'Manual entry',
                     '--stop', str(stop),
                     '--target', str(target)],
                    capture_output=True, text=True, timeout=30,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.code(result.stdout or result.stderr, language="text")
    
    with col5:
        if st.button("🔴 SELL", key="den_sell"):
            if trade_ticker:
                result = subprocess.run(
                    ['python', 'wolf_den.py', 'sell', trade_ticker.upper(),
                     '--reason', trade_reason or 'Manual exit'],
                    capture_output=True, text=True, timeout=30,
                    cwd='/workspaces/trading-companion-2026'
                )
                st.code(result.stdout or result.stderr, language="text")
    
    st.markdown("---")
    
    st.subheader("📖 The Three Wolves")
    
    st.markdown("""
    | Wolf | Role | Decision |
    |------|------|----------|
    | 🔧 **Brokkr** | Builder | "The signal is valid" |
    | 🐺 **Fenrir** | Analyst | "The setup is clean" |
    | 👑 **Tyr** | Trader | "I'm taking this trade" |
    
    **Paper trading proves:**
    - Which signals actually work
    - What position sizes make sense
    - How your timing holds up
    - Where your edge really is
    """)

# ============================================================================
# TAB 13: SETTINGS
# ============================================================================

with tab13:
    st.header("🔧 Settings & Universe")
    
    st.subheader("🌐 Trading Universe")
    
    # Load universe from pressure_framework
    universe = {
        'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ', 'LAES'],
        'SPACE': ['LUNR', 'RKLB', 'RDW', 'BKSY', 'MNTS', 'ASTS', 'SPIR', 'PL', 
                  'GSAT', 'SIDU', 'SATL', 'IRDM', 'VSAT'],
        'EVTOL': ['JOBY', 'ACHR', 'LILM', 'EVTL'],
        'NUCLEAR': ['LEU', 'CCJ', 'UUUU', 'UEC', 'SMR', 'OKLO', 'DNN', 'NXE', 
                    'LTBR', 'CEG', 'TLN', 'VST', 'NNE'],
        'AI_INFRA': ['SMCI', 'DELL', 'HPE', 'ANET', 'VRT', 'PWR', 'SOUN', 'AI'],
        'SEMICONDUCTORS': ['NVDA', 'AMD', 'ARM', 'TSM', 'ASML', 'MU', 'MRVL', 'AVGO'],
        'CRYPTO': ['MARA', 'RIOT', 'CLSK', 'COIN', 'CIFR', 'HUT', 'BITF'],
        'BIOTECH': ['CRSP', 'EDIT', 'NTLA', 'BEAM', 'RXRX'],
        'FINTECH': ['SOFI', 'AFRM', 'UPST', 'NU'],
        'EV_CLEAN': ['TSLA', 'RIVN', 'LCID', 'PLUG', 'FCEL', 'BE']
    }
    
    for sector, tickers in universe.items():
        with st.expander(f"📁 {sector} ({len(tickers)} tickers)"):
            st.write(", ".join(tickers))
    
    st.markdown("---")
    
    st.subheader("📋 Quick Commands")
    
    st.code("""
# Run all scanners
python hunt/pressure_framework.py          # Who's trapped?
python hunt/smart_money_hunter.py --filings 1000  # Insider buying
python hunt/tactical_scanners.py           # Tactical situations
python hunt/form4_scanner.py               # Form 4 in our universe

# Start dashboard
streamlit run wolf_pack_command_center.py
    """, language="bash")
    
    st.markdown("---")
    
    st.subheader("📖 The Philosophy")
    st.markdown("""
    > **"The question isn't 'what does the chart say'. The question is 'who will be FORCED to buy?'"**
    
    - **Short Squeeze** = shorts FORCED to buy
    - **Gamma Squeeze** = market makers FORCED to buy
    - **Sector Sympathy** = institutions rotating, FORCED to chase
    - **Panic Recovery** = retail sold, institutions buying their shares cheap
    
    **TIMING TRUTH:**
    - 9:30-10:00 AM = The trap. Retail FOMO in, gets smoked
    - 10:00-11:00 AM = Real direction emerges
    - 11:00-3:00 PM = Chop, no edge
    - 3:00-4:00 PM = Power hour. Institutions positioning
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    🐺 Wolf Pack Command Center | Built by Brokkr & Fenrir | AWOOOO! 
    <br>
    <small>Remember: We don't predict price. We predict WHO WILL BE FORCED TO BUY.</small>
</div>
""", unsafe_allow_html=True)
