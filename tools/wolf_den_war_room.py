#!/usr/bin/env python3
"""
🐺 WOLF DEN WAR ROOM - Professional Trading Dashboard

Real-time charts, technical indicators, pattern recognition.
This is not a toy. This is a weapon.

Author: Brokkr
Date: January 2, 2026
"""

import streamlit as st
import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import sys

# Add src to path for research modules
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Research modules - optional, we have NEW scanners now
RESEARCH_MODULES_AVAILABLE = False  # Not needed anymore - using new scanners

# Page config
st.set_page_config(
    page_title="🐺 Wolf Den War Room",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🐺 WOLF DEN WAR ROOM")
st.caption(f"Bloomberg-Level Research Platform | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Add tabs for different sections
tab_overview, tab_conviction, tab_wounded, tab_8k, tab_chart, tab_pressure, tab_clusters, tab_monitor, tab_sectors, tab_catalysts, tab_breakouts, tab_watchlist = st.tabs([
    "📊 Overview", "🎯 HIGH CONVICTION", "🩸 Wounded Prey", "⚡ 8-K Alerts", "📈 Live Chart", "⚡ Pressure", "🔥 Clusters", "👁️ Monitor", "🔥 Sectors", "📅 Catalysts", "💣 Breakouts", "🎯 Watchlist"
])

# Load config
try:
    with open('wolf_den_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
except:
    config = {
        'watchlist': {
            'primary': 'AISP',
            'backup': ['SOUN', 'BBAI', 'SMR', 'IONQ', 'QBTS', 'PLUG', 'HIMS', 'KVUE'],
            'positions': ['LUNR']
        },
        'entry_zones': {
            'AISP': {'low': 2.70, 'high': 2.90, 'stop': 2.30},
            'SOUN': {'low': 9.50, 'high': 10.50, 'stop': 9.00},
            'LUNR': {'low': 16.00, 'high': 16.85, 'stop': 16.00}
        }
    }

# Sidebar
st.sidebar.header("🎯 Command Center")

# Load watchlist for all modules
@st.cache_data(ttl=300)
def load_full_watchlist():
    try:
        import csv
        watchlist_file = Path('atp_watchlists/ATP_WOLF_PACK_MASTER.csv')
        with open(watchlist_file) as f:
            reader = csv.DictReader(f)
            return [row['Symbol'] for row in reader]
    except:
        return []

full_watchlist = load_full_watchlist()

# Ticker selection
all_tickers = [config['watchlist']['primary']] + config['watchlist']['backup'] + config['watchlist']['positions']
if full_watchlist:
    all_tickers = list(set(all_tickers + full_watchlist))  # Merge and dedupe
selected_ticker = st.sidebar.selectbox("Select Target", sorted(all_tickers), index=0)

# Timeframe
timeframe = st.sidebar.selectbox("Timeframe", ["1d", "5d", "1mo", "3mo", "6mo", "1y"], index=2)

# Technical indicators
show_sma = st.sidebar.checkbox("Show 20/50 SMA", value=True)
show_volume = st.sidebar.checkbox("Show Volume", value=True)
show_entry_zone = st.sidebar.checkbox("Show Entry Zone", value=True)

# Quick actions
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Quick Scans")

if st.sidebar.button("🔄 Refresh All Data"):
    st.rerun()

if st.sidebar.button("📊 Run Conviction Scan"):
    with st.spinner("Running conviction analysis..."):
        import subprocess
        subprocess.run(['python3', 'fast_conviction_scanner.py'], timeout=120)
    st.success("✅ Complete!")
    st.rerun()

if st.sidebar.button("🚨 Pre-Market Scan"):
    with st.spinner("Scanning pre-market..."):
        import subprocess
        subprocess.run(['python3', 'premarket_auto.py'], timeout=60)
    st.success("✅ Complete!")
    st.rerun()

if st.sidebar.button("🔥 Cluster Buy Scan"):
    with st.spinner("Scanning for insider buying clusters..."):
        import subprocess
        subprocess.run(['python3', 'cluster_buy_scanner.py'], timeout=90)
    st.success("✅ Complete!")
    st.rerun()

if st.sidebar.button("🩸 Wounded Prey Scan"):
    with st.spinner("Scanning for tax loss bounces..."):
        import subprocess
        subprocess.run(['python3', 'wounded_prey_scanner.py'], timeout=90)
    st.success("✅ Complete!")
    st.rerun()

if st.sidebar.button("⚡ 8-K Contract Scan"):
    with st.spinner("Scanning SEC EDGAR for 8-K contracts..."):
        import subprocess
        subprocess.run(['python3', 'sec_8k_contract_scanner.py', '--hours', '24'], timeout=120)
    st.success("✅ Complete!")
    st.rerun()

if st.sidebar.button("🏛️ Congress Tracker Scan"):
    with st.spinner("Tracking congressional trades..."):
        import subprocess
        subprocess.run(['python3', 'congress_tracker.py'], timeout=90)
    st.success("✅ Complete!")
    st.rerun()

# Research module status
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔬 Wolf Pack Scanners")
st.sidebar.success("✅ All NEW scanners loaded")
st.sidebar.caption("• Cross-Signal Validator")
st.sidebar.caption("• Wounded Prey Hunter")
st.sidebar.caption("• 8-K Contract Scanner")
st.sidebar.caption("• Cluster Buy Scanner")
st.sidebar.caption("• Congress Tracker")

# ═══════════════════════════════════════════════════════════════════════════
# HELP & INSTRUCTIONS SECTION
# ═══════════════════════════════════════════════════════════════════════════
st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 Quick Help")

with st.sidebar.expander("🎯 How To Use This Dashboard"):
    st.markdown("""
    **📊 Overview Tab**
    - Account status and conviction scores
    - Quick market snapshot
    
    **📈 Live Chart Tab**
    - Select ticker from dropdown above
    - Technical analysis with support/resistance
    - Pattern detection (bull flags, triangles)
    
    **⚡ Pressure Tab** ⭐ NEW
    - **Gamma squeeze** potential scores
    - **Monday win rates** after big Fridays
    - **Short interest** for squeeze setups
    - Higher score = more pressure built
    
    **🔥 Clusters Tab**
    - Insider buying clusters from SEC filings
    - Multiple insiders buying = conviction
    
    **👁️ Monitor Tab**
    - Real-time watchlist tracking
    - Price alerts and volume spikes
    
    **🔥 Sectors Tab**
    - Sector rotation analysis
    - Hot/cold sector rankings
    
    **📅 Catalysts Tab**
    - Earnings dates, conferences
    - CES, analyst days, etc.
    
    **💣 Breakouts Tab**
    - Failed breakouts for reversal plays
    - Stocks that ran up and crashed
    
    **🎯 Watchlist Tab**
    - Conviction rankings
    - Sorted by composite score
    """)

with st.sidebar.expander("🐺 Monday Jan 6 Battle Plan"):
    st.markdown("""
    **CES 2026 PLAYS:**
    
    🥇 **RR (Richtech Robotics)**
    - 26% short, 0.8 days to cover
    - Humanoid robot demo at CES
    - Entry: $3.35-3.50 | Stop: $3.00
    - Target: $4.50-5.00
    
    🥈 **QBTS (D-Wave)**
    - CES Foundry sponsor
    - 80% Monday win rate
    - Masterclass Jan 7, 1PM
    - Entry: Market open | Target: $40
    
    🥉 **QUBT (Quantum Computing)**
    - CES demos Jan 7-8
    - 22.7% short interest
    - HIGH RISK - tight stops!
    
    ⚠️ **AVOID:** IONQ, RGTI (no CES presence)
    """)

with st.sidebar.expander("⚡ Pressure Score Explained"):
    st.markdown("""
    **What creates PRESSURE?**
    
    | Factor | Points |
    |--------|--------|
    | Monday Win Rate | 30 |
    | Gamma Score | 25 |
    | Short Interest | 15 |
    | Accumulation | 15 |
    | Volume Surge | 15 |
    
    **Score Levels:**
    - 🔥 70+ = EXTREME pressure
    - ⚡ 55+ = HIGH pressure
    - ✅ 40+ = MODERATE
    - ⚪ <40 = LOW
    
    **The Edge:**
    MMs MUST hedge when calls go ITM.
    Shorts MUST cover on spikes.
    We find WHERE pressure builds.
    Catalyst is just the spark.
    """)

#==========================================================================
# TAB 1: OVERVIEW
#==========================================================================
with tab_overview:
    st.header("📊 Market Overview")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Account", "$1,280", "+2.1%")
    with col2:
        st.metric("Cash", "$1,120", "87.5%")
    with col3:
        st.metric("Positions", "1 Active", "LUNR")
    with col4:
        # Load conviction
        try:
            with open('logs/conviction_rankings_latest.json', 'r') as f:
                rankings = json.load(f)
                for r in rankings['rankings']:
                    if r['ticker'] == selected_ticker:
                        st.metric("Conviction", f"{r['total_score']}/100", r['conviction'])
                        break
        except:
            st.metric("Conviction", "N/A", "Run scan")

    st.markdown("---")

#==========================================================================
# TAB: PRESSURE SCANNER - Options Gamma + Monday Probability
#==========================================================================
with tab_pressure:
    st.header("⚡ Pressure Point Scanner")
    st.caption("Find where the explosion will happen - Gamma Squeeze + Monday Probability + Short Interest")
    
    # Import pressure scanner
    try:
        from wolf_pressure import get_pressure_for_dashboard, PRESSURE_UNIVERSE
        from wolf_gamma import GammaScanner
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🎯 Pressure Rankings")
            
            with st.spinner("Scanning pressure points..."):
                pressure_data = get_pressure_for_dashboard()
                
                if pressure_data:
                    # Create dataframe
                    df_data = []
                    for p in pressure_data:
                        df_data.append({
                            'Ticker': p['ticker'],
                            'Price': f"${p['price']:.2f}",
                            'Friday': f"{p['friday_change']:+.1f}%",
                            'Mon Rate': f"{p['monday_rate']}%",
                            'Gamma': f"{p['gamma_score']:.0f}",
                            'Short': f"{p['short_pct']:.1f}%",
                            'Score': p['pressure_score'],
                            'Level': p['pressure_level']
                        })
                    
                    df = pd.DataFrame(df_data)
                    
                    # Style the dataframe
                    def color_score(val):
                        if val >= 70:
                            return 'background-color: rgba(0,255,0,0.3)'
                        elif val >= 55:
                            return 'background-color: rgba(255,255,0,0.3)'
                        return ''
                    
                    st.dataframe(df, use_container_width=True, height=400)
                    
                    # Show top plays
                    st.subheader("🔥 HIGH PRESSURE PLAYS")
                    
                    high_pressure = [p for p in pressure_data if p['pressure_score'] >= 55]
                    
                    if high_pressure:
                        for p in high_pressure[:5]:
                            with st.expander(f"{p['pressure_level']} {p['ticker']} - Score: {p['pressure_score']:.0f}/100"):
                                c1, c2, c3 = st.columns(3)
                                
                                with c1:
                                    st.metric("Price", f"${p['price']:.2f}", f"{p['friday_change']:+.1f}% Fri")
                                    st.metric("Monday Win Rate", f"{p['monday_rate']}%")
                                    
                                with c2:
                                    st.metric("Gamma Score", f"{p['gamma_score']:.0f}/100")
                                    if p['trigger_strike'] > 0:
                                        st.metric("Trigger Strike", f"${p['trigger_strike']:.2f}", f"{p['distance_to_trigger']:+.1f}%")
                                    
                                with c3:
                                    st.metric("Short Interest", f"{p['short_pct']:.1f}%")
                                    if p['call_oi'] > 0:
                                        st.metric("Call OI at Strike", f"{p['call_oi']:,}")
                                
                                st.caption(f"Shares to hedge if strike triggered: {p['call_oi'] * 100:,}")
                    else:
                        st.info("No high pressure plays detected right now")
                        
        with col2:
            st.subheader("📊 Score Components")
            st.markdown("""
            **How Pressure Score Works:**
            
            | Component | Weight |
            |-----------|--------|
            | Monday Win Rate | 30 pts |
            | Gamma Score | 25 pts |
            | Short Interest | 15 pts |
            | Accumulation | 15 pts |
            | Volume Surge | 15 pts |
            
            ---
            
            **🔥 EXTREME (70+)**: Multiple forces converging
            
            **⚡ HIGH (55+)**: Strong squeeze potential
            
            **✅ MODERATE (40+)**: Worth watching
            
            ---
            
            **The Edge:**
            - MMs MUST hedge when calls go ITM
            - Shorts MUST cover on spike
            - We find WHERE pressure builds
            - Catalyst is just the spark
            """)
            
            # Jensen Huang reminder
            st.warning("""
            ⚡ **CES CATALYST**
            
            Jensen Huang speaks:
            **Sunday 4PM ET**
            
            Keywords to watch:
            - "quantum" → QBTS, QUBT
            - "robot" → RCAT
            - "space" → RDW
            """)
            
    except ImportError as e:
        st.error(f"Pressure scanner not available: {e}")
        st.info("Run: python wolf_pressure.py scan")

#==========================================================================
# TAB: HIGH CONVICTION - Cross-Signal Validator
#==========================================================================
with tab_conviction:
    st.header("🎯 HIGH CONVICTION SETUPS")
    st.caption("70+ Score = Multiple signals aligned = Ready to hunt")
    
    try:
        import sys
        import subprocess
        from pathlib import Path
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("🔥 HIGH CONVICTION PLAYS (70+)")
            
            if st.button("🔄 Run Cross-Signal Scan", key="conviction_scan"):
                with st.spinner("Scanning 55 tickers across 4 signals..."):
                    result = subprocess.run(
                        ['python3', 'cross_signal_validator.py', '--min-signals', '3'],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    st.success("✅ Scan complete!")
            
            # Try to load latest results
            try:
                results_file = Path('logs/conviction_results.json')
                if results_file.exists():
                    with open(results_file) as f:
                        data = json.load(f)
                        
                    # Filter for 70+ scores
                    high_conviction = [t for t in data.get('tickers', []) if t['total_score'] >= 70]
                    
                    if high_conviction:
                        for ticker in high_conviction:
                            with st.expander(f"🎯 {ticker['symbol']} - Score: {ticker['total_score']}/100"):
                                c1, c2, c3, c4 = st.columns(4)
                                
                                with c1:
                                    st.metric("Wounded Prey", f"{ticker.get('wounded_score', 0)}/30")
                                with c2:
                                    st.metric("Insider Buying", f"{ticker.get('insider_score', 0)}/30")
                                with c3:
                                    st.metric("8-K Contracts", f"{ticker.get('sec_score', 0)}/25")
                                with c4:
                                    st.metric("Thesis Align", f"{ticker.get('thesis_score', 0)}/15")
                                
                                st.markdown(f"**Why it's hot:** {ticker.get('reasoning', 'Multiple signals converging')}")
                    else:
                        st.info("No 70+ plays right now. Run scan or lower threshold.")
                        
                        # Show 50-69 as backup
                        strong = [t for t in data.get('tickers', []) if 50 <= t['total_score'] < 70]
                        if strong:
                            st.subheader("💪 STRONG SETUPS (50-69)")
                            for ticker in strong[:5]:
                                st.markdown(f"**{ticker['symbol']}** - {ticker['total_score']}/100")
                else:
                    st.warning("No results yet - click 'Run Cross-Signal Scan' above")
                    
            except Exception as e:
                st.error(f"Error loading results: {e}")
                st.info("Run the scanner first: python3 cross_signal_validator.py")
        
        with col2:
            st.subheader("📊 Scoring System")
            st.markdown("""
            **Signal Breakdown:**
            
            🩸 **Wounded Prey** (30 pts)
            - Down 30%+, recovering
            - Tax loss bounce (Jan 2-10)
            
            👔 **Insider Buying** (30 pts)
            - Form 4 purchases
            - Clusters (3+ insiders)
            
            ⚡ **SEC 8-K** (25 pts)
            - Material contracts filed
            - 15-min edge before news
            
            🎯 **Thesis Alignment** (15 pts)
            - AI Fuel Chain priority
            - Space/Nuclear sectors
            
            ---
            
            **🔥 HIGH (70+)**: Hunt NOW
            
            **💪 STRONG (50-69)**: Watch close
            
            **✅ MODERATE (30-49)**: Build list
            """)
    
    except Exception as e:
        st.error(f"High Conviction scanner not available: {e}")

#==========================================================================
# TAB: WOUNDED PREY - Tax Loss Bounce Hunter
#==========================================================================
with tab_wounded:
    st.header("🩸 WOUNDED PREY - Tax Loss Bounce Hunter")
    st.caption("January bounce plays: Down 30%+, recovering now (Jan 2-10 entry window)")
    
    try:
        import subprocess
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("🎯 WOUNDED PREY RANKINGS")
            
            if st.button("🔄 Run Wounded Prey Scan", key="wounded_scan"):
                with st.spinner("Scanning 55 tickers for bounce potential..."):
                    result = subprocess.run(
                        ['python3', 'wounded_prey_scanner.py'],
                        capture_output=True,
                        text=True,
                        timeout=90
                    )
                    st.success("✅ Scan complete!")
            
            # Try to load latest results
            try:
                results_file = Path('logs/wounded_prey_results.json')
                if results_file.exists():
                    with open(results_file) as f:
                        data = json.load(f)
                    
                    wounded = data.get('wounded_prey', [])
                    
                    if wounded:
                        # Filter for high scores
                        high_score = [w for w in wounded if w.get('bounce_score', 0) >= 60]
                        
                        st.subheader(f"🔥 HIGH SCORE BOUNCES (60+) - {len(high_score)} found")
                        
                        for prey in high_score:
                            with st.expander(f"🩸 {prey['ticker']} - Bounce Score: {prey.get('bounce_score', 0)}/100"):
                                c1, c2, c3 = st.columns(3)
                                
                                with c1:
                                    st.metric("Current Price", f"${prey.get('price', 0):.2f}")
                                    st.metric("52w High", f"${prey.get('high_52w', 0):.2f}")
                                    st.metric("% from High", f"{prey.get('pct_from_high', 0):.1f}%")
                                
                                with c2:
                                    st.metric("5-Day Change", f"{prey.get('change_5d', 0):+.1f}%")
                                    st.metric("Volume Ratio", f"{prey.get('volume_ratio', 0):.1f}x")
                                    st.metric("Insider Buys", prey.get('insider_count', 0))
                                
                                with c3:
                                    st.metric("Tax Loss Score", f"{prey.get('tax_loss_score', 0)}/40")
                                    st.metric("Recovery Score", f"{prey.get('recovery_score', 0)}/30")
                                    st.metric("Insider Score", f"{prey.get('insider_score', 0)}/30")
                                
                                # Entry/exit
                                st.markdown("---")
                                st.markdown(f"**📌 Entry Zone:** ${prey.get('entry_low', 0):.2f} - ${prey.get('entry_high', 0):.2f}")
                                st.markdown(f"**🎯 Target:** ${prey.get('target', 0):.2f} (+{prey.get('target_pct', 0):.1f}%)")
                                st.markdown(f"**🛡️ Stop:** ${prey.get('stop', 0):.2f} (-8%)")
                    else:
                        st.info("No wounded prey detected. Market might be too strong.")
                else:
                    st.warning("No results yet - click 'Run Wounded Prey Scan' above")
                    
            except Exception as e:
                st.error(f"Error loading results: {e}")
        
        with col2:
            st.subheader("🗓️ Timing")
            st.markdown("""
            **Tax Loss Timeline:**
            
            📅 **Dec 15-31**: Tax loss selling
            ✅ **DONE**
            
            ⏰ **Wash Sale**: 30 days
            📆 **Ends**: Jan 24-31
            
            🎯 **ENTRY WINDOW**: Jan 2-10
            ⭐ **RIGHT NOW!**
            
            📈 **Expected**: 15-30% bounce
            🗓️ **By**: End of January
            
            ---
            
            **What We Look For:**
            
            ✅ Down 30%+ from highs
            ✅ Price $2-50
            ✅ Volume picking up
            ✅ Has revenue
            ✅ Insider buying
            
            🎯 Enter early Jan
            🛡️ -8% stop
            💰 Exit by month end
            """)
    
    except Exception as e:
        st.error(f"Wounded prey scanner not available: {e}")

#==========================================================================
# TAB: 8-K ALERTS - SEC Contract Filings (15-min edge)
#==========================================================================
with tab_8k:
    st.header("⚡ 8-K CONTRACT ALERTS - The 15-Minute Edge")
    st.caption("Material contracts filed with SEC - Catch before market wakes up")
    
    try:
        import subprocess
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("🚨 RECENT 8-K FILINGS (Last 24h)")
            
            hours = st.slider("Hours to scan back", 4, 48, 24, key="8k_hours")
            
            if st.button("🔄 Scan 8-K Filings", key="8k_scan"):
                with st.spinner(f"Scanning SEC EDGAR for contracts (last {hours}h)..."):
                    result = subprocess.run(
                        ['python3', 'sec_8k_contract_scanner.py', '--hours', str(hours)],
                        capture_output=True,
                        text=True,
                        timeout=180
                    )
                    st.success("✅ Scan complete!")
            
            # Try to load latest results
            try:
                results_file = Path('logs/8k_contract_results.json')
                if results_file.exists():
                    with open(results_file) as f:
                        data = json.load(f)
                    
                    filings = data.get('filings', [])
                    
                    if filings:
                        # Filter for high value (score 30+)
                        high_value = [f for f in filings if f.get('score', 0) >= 30]
                        
                        st.subheader(f"🔥 HIGH-VALUE CONTRACTS (30+) - {len(high_value)} found")
                        
                        for filing in high_value:
                            with st.expander(f"⚡ {filing['ticker']} - Score: {filing.get('score', 0)}/100 | Filed: {filing.get('filed_at', 'Unknown')}"):
                                c1, c2 = st.columns(2)
                                
                                with c1:
                                    st.markdown(f"**Contract Type:** {filing.get('contract_type', 'Material Agreement')}")
                                    st.markdown(f"**Filed:** {filing.get('filed_at', 'Unknown')}")
                                    st.markdown(f"**Time Since:** {filing.get('hours_ago', 0):.1f} hours")
                                
                                with c2:
                                    st.metric("Value Score", f"{filing.get('score', 0)}/100")
                                    if 'price' in filing:
                                        st.metric("Current Price", f"${filing['price']:.2f}")
                                        st.metric("5d Change", f"{filing.get('change_5d', 0):+.1f}%")
                                
                                # Contract details
                                if 'description' in filing:
                                    st.markdown("**Description:**")
                                    st.markdown(filing['description'])
                                
                                # SEC link
                                if 'sec_url' in filing:
                                    st.markdown(f"[📄 View SEC Filing]({filing['sec_url']})")
                        
                        # Show all recent
                        st.subheader(f"📋 ALL RECENT FILINGS - {len(filings)} total")
                        df_data = []
                        for f in filings:
                            df_data.append({
                                'Ticker': f['ticker'],
                                'Type': f.get('contract_type', 'Material'),
                                'Score': f.get('score', 0),
                                'Filed': f.get('filed_at', ''),
                                'Hours Ago': f"{f.get('hours_ago', 0):.1f}h"
                            })
                        
                        if df_data:
                            df = pd.DataFrame(df_data)
                            st.dataframe(df, use_container_width=True)
                    else:
                        st.info(f"No 8-K contract filings in last {hours} hours")
                else:
                    st.warning("No results yet - click 'Scan 8-K Filings' above")
                    
            except Exception as e:
                st.error(f"Error loading results: {e}")
        
        with col2:
            st.subheader("⚡ The Edge")
            st.markdown("""
            **Why 8-K Contracts Matter:**
            
            ⏰ **15-Min Window**
            - Filed → SEC website
            - Before news picks up
            - Before algos react
            
            💰 **Material = Important**
            - Must disclose big deals
            - Revenue impact
            - Partnership value
            
            🎯 **What We Catch:**
            - Gov contracts
            - Partnership agreements
            - Major customer deals
            - Supply agreements
            
            ---
            
            **Scoring (0-100):**
            
            🔥 **40+**: Major contract
            - Check immediately
            - Possible entry
            
            ⚡ **30-39**: Solid deal
            - Worth reviewing
            - Add to watchlist
            
            ✅ **20-29**: Standard
            - Material but small
            - Monitor only
            
            ---
            
            **The Play:**
            1. Alert fires
            2. Read filing (2 min)
            3. Check price/volume
            4. Enter if clean
            5. Exit on news pump
            """)
    
    except Exception as e:
        st.error(f"8-K scanner not available: {e}")

#==========================================================================
# TAB 2: LIVE CHART - WOLF LEVEL ANALYSIS
#==========================================================================
with tab_chart:
    st.header(f"📊 {selected_ticker} - Professional Technical Analysis")

@st.cache_data(ttl=60)
def load_price_data(ticker, period):
    """Load price data with caching."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    info = stock.info
    return hist, info

def detect_support_resistance(hist, num_levels=3):
    """Detect key support and resistance levels"""
    prices = hist['Close'].values
    levels = []
    
    # Find local maxima and minima
    for i in range(2, len(prices) - 2):
        if prices[i] > prices[i-1] and prices[i] > prices[i-2] and \
           prices[i] > prices[i+1] and prices[i] > prices[i+2]:
            levels.append(('resistance', prices[i]))
        elif prices[i] < prices[i-1] and prices[i] < prices[i-2] and \
             prices[i] < prices[i+1] and prices[i] < prices[i+2]:
            levels.append(('support', prices[i]))
    
    # Cluster similar levels
    if levels:
        levels.sort(key=lambda x: x[1])
        clustered = []
        current_level = levels[0][1]
        current_type = levels[0][0]
        count = 1
        
        for i in range(1, len(levels)):
            if abs(levels[i][1] - current_level) / current_level < 0.02:  # 2% threshold
                current_level = (current_level * count + levels[i][1]) / (count + 1)
                count += 1
            else:
                if count >= 2:  # Only keep levels tested multiple times
                    clustered.append((current_type, current_level, count))
                current_level = levels[i][1]
                current_type = levels[i][0]
                count = 1
        
        # Sort by strength (number of tests)
        clustered.sort(key=lambda x: x[2], reverse=True)
        return clustered[:num_levels]
    
    return []

def detect_patterns(hist):
    """Detect chart patterns automatically"""
    patterns = []
    close = hist['Close'].values
    high = hist['High'].values
    low = hist['Low'].values
    
    # Bull Flag/Pennant
    if len(close) >= 20:
        first_half = close[:len(close)//2]
        second_half = close[len(close)//2:]
        
        first_trend = (first_half[-1] - first_half[0]) / first_half[0]
        second_range = (max(second_half) - min(second_half)) / min(second_half)
        
        if first_trend > 0.10 and second_range < 0.05:
            patterns.append({
                'name': '🚀 BULL FLAG',
                'signal': 'BULLISH',
                'description': f'Strong rally (+{first_trend*100:.1f}%) followed by tight consolidation. Breakout imminent.',
                'confidence': 'HIGH'
            })
    
    # Descending Triangle (Bearish)
    if len(close) >= 15:
        recent_lows = [low[i] for i in range(len(low)-15, len(low)) if low[i] == min(low[max(0,i-2):i+3])]
        if len(recent_lows) >= 3:
            low_range = (max(recent_lows) - min(recent_lows)) / min(recent_lows)
            if low_range < 0.03:  # Flat bottom
                patterns.append({
                    'name': '⚠️ DESCENDING TRIANGLE',
                    'signal': 'BEARISH',
                    'description': 'Lower highs with flat support. Watch for breakdown or reversal.',
                    'confidence': 'MEDIUM'
                })
    
    # Higher Lows (Uptrend)
    if len(close) >= 10:
        recent_lows_idx = []
        for i in range(len(low)-10, len(low)):
            if i > 2 and i < len(low)-2:
                if low[i] <= min(low[i-2:i]) and low[i] <= min(low[i+1:min(i+3, len(low))]):
                    recent_lows_idx.append(i)
        
        if len(recent_lows_idx) >= 3:
            lows = [low[i] for i in recent_lows_idx[-3:]]
            if lows[1] > lows[0] and lows[2] > lows[1]:
                patterns.append({
                    'name': '💪 HIGHER LOWS',
                    'signal': 'BULLISH',
                    'description': 'Strong uptrend established. Each dip is getting bought.',
                    'confidence': 'HIGH'
                })
    
    # Breakout above resistance
    if len(close) >= 20:
        recent_high = max(high[-20:-5])
        current = close[-1]
        if current > recent_high * 1.02:
            patterns.append({
                'name': '🔥 BREAKOUT',
                'signal': 'BULLISH',
                'description': f'Broke above resistance at ${recent_high:.2f}. Momentum building.',
                'confidence': 'HIGH'
            })
    
    # Breakdown below support
    if len(close) >= 20:
        recent_low = min(low[-20:-5])
        current = close[-1]
        if current < recent_low * 0.98:
            patterns.append({
                'name': '📉 BREAKDOWN',
                'signal': 'BEARISH',
                'description': f'Broke below support at ${recent_low:.2f}. Caution advised.',
                'confidence': 'HIGH'
            })
    
    return patterns

def calculate_rsi(prices, period=14):
    """Calculate RSI"""
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.convolve(gains, np.ones(period), 'valid') / period
    avg_loss = np.convolve(losses, np.ones(period), 'valid') / period
    
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

try:
    hist, info = load_price_data(selected_ticker, timeframe)
    
    if not hist.empty:
        # PATTERN DETECTION - Show first
        patterns = detect_patterns(hist)
        if patterns:
            st.subheader("🎯 DETECTED PATTERNS")
            cols = st.columns(len(patterns))
            for i, pattern in enumerate(patterns):
                with cols[i]:
                    if pattern['signal'] == 'BULLISH':
                        st.success(f"**{pattern['name']}**\n\n{pattern['description']}\n\n*Confidence: {pattern['confidence']}*")
                    else:
                        st.error(f"**{pattern['name']}**\n\n{pattern['description']}\n\n*Confidence: {pattern['confidence']}*")
        
        # Calculate technical indicators
        sma_20 = hist['Close'].rolling(window=20).mean()
        sma_50 = hist['Close'].rolling(window=50).mean()
        ema_9 = hist['Close'].ewm(span=9).mean()
        ema_21 = hist['Close'].ewm(span=21).mean()
        
        # Bollinger Bands
        bb_middle = hist['Close'].rolling(window=20).mean()
        bb_std = hist['Close'].rolling(window=20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        
        # RSI
        rsi = calculate_rsi(hist['Close'].values)
        
        # MACD
        ema_12 = hist['Close'].ewm(span=12).mean()
        ema_26 = hist['Close'].ewm(span=26).mean()
        macd = ema_12 - ema_26
        signal_line = macd.ewm(span=9).mean()
        
        # Support/Resistance
        sr_levels = detect_support_resistance(hist)
        
        # Create sophisticated subplots
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            row_heights=[0.5, 0.15, 0.15, 0.2],
            subplot_titles=(f'{selected_ticker} Price Action', 'RSI', 'MACD', 'Volume')
        )
        
        # Main candlestick chart
        candlestick = go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name='Price',
            increasing_line_color='#00ff00',
            decreasing_line_color='#ff0000',
            increasing_fillcolor='#00ff00',
            decreasing_fillcolor='#ff0000'
        )
        fig.add_trace(candlestick, row=1, col=1)
        
        # Bollinger Bands
        fig.add_trace(go.Scatter(x=hist.index, y=bb_upper, name='BB Upper',
                                line=dict(color='rgba(250,250,250,0.3)', width=1, dash='dash')), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=bb_lower, name='BB Lower',
                                line=dict(color='rgba(250,250,250,0.3)', width=1, dash='dash'),
                                fill='tonexty', fillcolor='rgba(250,250,250,0.05)'), row=1, col=1)
        
        # SMAs
        if show_sma:
            fig.add_trace(go.Scatter(x=hist.index, y=sma_20, name='SMA 20',
                                    line=dict(color='#FFA500', width=2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=sma_50, name='SMA 50',
                                    line=dict(color='#00BFFF', width=2)), row=1, col=1)
        
        # EMAs
        fig.add_trace(go.Scatter(x=hist.index, y=ema_9, name='EMA 9',
                                line=dict(color='#FF1493', width=1, dash='dot')), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=ema_21, name='EMA 21',
                                line=dict(color='#9370DB', width=1, dash='dot')), row=1, col=1)
        
        # Support/Resistance levels
        annotations = []
        shapes = []
        for sr_type, level, strength in sr_levels:
            color = '#00ff00' if sr_type == 'support' else '#ff0000'
            fig.add_hline(y=level, line_dash="dash", line_color=color, opacity=0.5, row=1, col=1)
            annotations.append(
                dict(x=hist.index[-1], y=level,
                     text=f"{sr_type.upper()} ${level:.2f} (x{strength})",
                     showarrow=False, xanchor='left', 
                     font=dict(color=color, size=10),
                     bgcolor='rgba(0,0,0,0.7)')
            )
        
        # Entry zone overlay
        if show_entry_zone and selected_ticker in config.get('entry_zones', {}):
            zone = config['entry_zones'][selected_ticker]
            
            shapes.extend([
                dict(type="rect",
                     xref="x", yref="y",
                     x0=hist.index[0], x1=hist.index[-1],
                     y0=zone['low'], y1=zone['high'],
                     fillcolor="green", opacity=0.15,
                     line=dict(width=2, color='green')),
                dict(type="line",
                     xref="x", yref="y",
                     x0=hist.index[0], x1=hist.index[-1],
                     y0=zone['stop'], y1=zone['stop'],
                     line=dict(color="red", width=3, dash="dash"))
            ])
            
            annotations.extend([
                dict(x=hist.index[-1], y=zone['high'],
                     text=f"🎯 ENTRY HIGH: ${zone['high']:.2f}",
                     showarrow=False, xanchor='left', 
                     font=dict(color='white', size=12, family='Arial Black'),
                     bgcolor='green', opacity=0.9),
                dict(x=hist.index[-1], y=zone['low'],
                     text=f"🎯 ENTRY LOW: ${zone['low']:.2f}",
                     showarrow=False, xanchor='left',
                     font=dict(color='white', size=12, family='Arial Black'),
                     bgcolor='green', opacity=0.9),
                dict(x=hist.index[-1], y=zone['stop'],
                     text=f"🛑 STOP LOSS: ${zone['stop']:.2f}",
                     showarrow=False, xanchor='left',
                     font=dict(color='white', size=12, family='Arial Black'),
                     bgcolor='red', opacity=0.9)
            ])
        
        # RSI
        rsi_trace = go.Scatter(
            x=hist.index[14:],  # RSI starts after period
            y=rsi,
            name='RSI',
            line=dict(color='#FFD700', width=2),
            fill='tozeroy',
            fillcolor='rgba(255,215,0,0.1)'
        )
        fig.add_trace(rsi_trace, row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
        fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1, row=2, col=1)
        fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1, row=2, col=1)
        
        # MACD
        fig.add_trace(go.Scatter(x=hist.index, y=macd, name='MACD',
                                line=dict(color='#00CED1', width=2)), row=3, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=signal_line, name='Signal',
                                line=dict(color='#FF6347', width=2)), row=3, col=1)
        
        histogram = macd - signal_line
        colors_macd = ['green' if histogram.iloc[i] > 0 else 'red' for i in range(len(histogram))]
        fig.add_trace(go.Bar(x=hist.index, y=histogram, name='Histogram',
                            marker_color=colors_macd, opacity=0.5), row=3, col=1)
        
        # Volume with color
        colors_vol = ['#00ff00' if hist['Close'].iloc[i] >= hist['Open'].iloc[i] else '#ff0000'
                     for i in range(len(hist))]
        fig.add_trace(go.Bar(
            x=hist.index,
            y=hist['Volume'],
            name='Volume',
            marker_color=colors_vol,
            showlegend=False
        ), row=4, col=1)
        
        # Add average volume line
        avg_volume = hist['Volume'].mean()
        fig.add_hline(y=avg_volume, line_dash="dash", line_color="yellow", 
                     opacity=0.5, row=4, col=1,
                     annotation_text="Avg Vol", annotation_position="right")
        
        # Update layout
        fig.update_layout(
            height=1000,
            xaxis_rangeslider_visible=False,
            template='plotly_dark',
            hovermode='x unified',
            margin=dict(l=0, r=100, t=30, b=0),
            shapes=shapes,
            annotations=annotations,
            font=dict(family='Arial', size=11),
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117'
        )
        
        fig.update_yaxes(title_text="Price ($)", row=1, col=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(title_text="RSI", row=2, col=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(title_text="MACD", row=3, col=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(title_text="Volume", row=4, col=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # INTELLIGENT ANALYSIS
        st.markdown("---")
        st.subheader("🧠 WOLF PACK ANALYSIS")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📊 Technical Signals")
            
            # Price vs SMAs
            current_price = hist['Close'].iloc[-1]
            sma20_val = sma_20.iloc[-1]
            sma50_val = sma_50.iloc[-1]
            
            if current_price > sma20_val and current_price > sma50_val:
                st.success("✅ **ABOVE both SMAs** - Bullish structure")
            elif current_price > sma20_val:
                st.warning("⚠️ **Above SMA20, below SMA50** - Mixed")
            else:
                st.error("🔴 **BELOW both SMAs** - Bearish structure")
            
            # RSI analysis
            current_rsi = rsi[-1] if len(rsi) > 0 else 50
            if current_rsi > 70:
                st.error(f"🔥 **RSI: {current_rsi:.1f}** - OVERBOUGHT")
            elif current_rsi < 30:
                st.success(f"💎 **RSI: {current_rsi:.1f}** - OVERSOLD (Buy Zone)")
            else:
                st.info(f"📊 **RSI: {current_rsi:.1f}** - Neutral")
            
            # MACD
            macd_val = macd.iloc[-1]
            signal_val = signal_line.iloc[-1]
            if macd_val > signal_val:
                st.success("📈 **MACD BULLISH** - Above signal")
            else:
                st.error("📉 **MACD BEARISH** - Below signal")
        
        with col2:
            st.markdown("### 🎯 Key Levels")
            
            if sr_levels:
                for sr_type, level, strength in sr_levels[:2]:  # Top 2
                    distance = ((current_price - level) / level) * 100
                    if sr_type == 'support':
                        st.success(f"**Support: ${level:.2f}** ({abs(distance):.1f}% {'below' if distance < 0 else 'above'})\nTested {strength}x")
                    else:
                        st.error(f"**Resistance: ${level:.2f}** ({abs(distance):.1f}% {'above' if distance > 0 else 'below'})\nTested {strength}x")
            else:
                st.info("No major S/R levels detected")
            
            # Bollinger Bands position
            bb_upper_val = bb_upper.iloc[-1]
            bb_lower_val = bb_lower.iloc[-1]
            bb_position = (current_price - bb_lower_val) / (bb_upper_val - bb_lower_val) * 100
            
            if bb_position > 80:
                st.warning(f"⚠️ **BB Position: {bb_position:.0f}%** - Near upper band")
            elif bb_position < 20:
                st.success(f"💪 **BB Position: {bb_position:.0f}%** - Near lower band (bounce zone)")
            else:
                st.info(f"📊 **BB Position: {bb_position:.0f}%** - Mid-range")
        
        with col3:
            st.markdown("### 🚨 Action Items")
            
            # Generate specific trading signals
            signals = []
            
            # RSI oversold + above support
            if current_rsi < 35 and sr_levels:
                support_close = any(sr_type == 'support' and abs(current_price - level)/level < 0.03 
                                   for sr_type, level, _ in sr_levels)
                if support_close:
                    signals.append("💎 **STRONG BUY**: RSI oversold AT support level")
            
            # Bullish crossover
            if len(macd) > 1 and macd.iloc[-2] < signal_line.iloc[-2] and macd.iloc[-1] > signal_line.iloc[-1]:
                signals.append("🚀 **BUY SIGNAL**: MACD bullish crossover")
            
            # Bearish crossover
            if len(macd) > 1 and macd.iloc[-2] > signal_line.iloc[-2] and macd.iloc[-1] < signal_line.iloc[-1]:
                signals.append("🛑 **SELL SIGNAL**: MACD bearish crossover")
            
            # Volume spike
            avg_vol = hist['Volume'].mean()
            current_vol = hist['Volume'].iloc[-1]
            if current_vol > avg_vol * 2:
                signals.append(f"📊 **VOLUME SURGE**: {current_vol/avg_vol:.1f}x average - Institutions moving")
            
            # Price near entry zone
            if selected_ticker in config.get('entry_zones', {}):
                zone = config['entry_zones'][selected_ticker]
                if zone['low'] <= current_price <= zone['high']:
                    signals.append(f"🎯 **IN ENTRY ZONE**: ${zone['low']:.2f}-${zone['high']:.2f}")
                elif current_price < zone['low'] * 1.05:
                    signals.append(f"⏳ **APPROACHING ENTRY**: Watch ${zone['low']:.2f}")
            
            # Pattern-based signals
            if patterns:
                for pattern in patterns:
                    if pattern['confidence'] == 'HIGH':
                        if pattern['signal'] == 'BULLISH':
                            signals.append(f"🚀 **{pattern['name']}**: Setup confirmed")
                        else:
                            signals.append(f"⚠️ **{pattern['name']}**: Risk elevated")
            
            if signals:
                for signal in signals:
                    st.markdown(f"- {signal}")
            else:
                st.info("📋 No immediate action items. Continue monitoring.")
        
        # Current stats row
        st.markdown("---")
        current_price = hist['Close'].iloc[-1]
        prev_close = info.get('previousClose', hist['Close'].iloc[-2])
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Current", f"${current_price:.2f}", f"{change_pct:+.2f}%")
        with col2:
            st.metric("High", f"${hist['High'].iloc[-1]:.2f}")
        with col3:
            st.metric("Low", f"${hist['Low'].iloc[-1]:.2f}")
        with col4:
            st.metric("Volume", f"{hist['Volume'].iloc[-1]:,.0f}")
        with col5:
            avg_vol = hist['Volume'].mean()
            vol_ratio = hist['Volume'].iloc[-1] / avg_vol
            st.metric("Vol Ratio", f"{vol_ratio:.2f}x", 
                     "HIGH" if vol_ratio > 2 else "NORMAL" if vol_ratio > 0.5 else "LOW")
        
        # 52-week range
        st.markdown("---")
        st.subheader("📈 52-Week Range")
        
        high_52w = info.get('fiftyTwoWeekHigh', hist['High'].max())
        low_52w = info.get('fiftyTwoWeekLow', hist['Low'].min())
        range_position = (current_price - low_52w) / (high_52w - low_52w) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("52W High", f"${high_52w:.2f}")
        with col2:
            st.metric("52W Low", f"${low_52w:.2f}")
        with col3:
            st.metric("Position", f"{range_position:.1f}%",
                     "🟢 WOUNDED PREY" if range_position < 20 else 
                     "🟡 GOOD" if range_position < 40 else
                     "🔴 HIGH" if range_position > 80 else "NEUTRAL")
        with col4:
            distance_from_low = ((current_price - low_52w) / low_52w) * 100
            st.metric("From Low", f"+{distance_from_low:.1f}%")
        
    else:
        st.error(f"Unable to load data for {selected_ticker}")
        
except Exception as e:
    st.error(f"Error loading chart: {e}")

    st.markdown("---")

    # Conviction analysis for selected ticker
    st.header("🎯 Conviction Analysis")

try:
    with open('logs/conviction_rankings_latest.json', 'r') as f:
        rankings = json.load(f)
        
        # Find current ticker
        current_data = None
        for r in rankings['rankings']:
            if r['ticker'] == selected_ticker:
                current_data = r
                break
        
        if current_data:
            # Show conviction bar
            score = current_data['total_score']
            
            # Create progress bar visualization
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Conviction Score"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen" if score >= 65 else "orange" if score >= 50 else "red"},
                    'steps': [
                        {'range': [0, 35], 'color': "rgba(255,0,0,0.3)"},
                        {'range': [35, 50], 'color': "rgba(255,165,0,0.3)"},
                        {'range': [50, 65], 'color': "rgba(255,255,0,0.3)"},
                        {'range': [65, 100], 'color': "rgba(0,255,0,0.3)"}
                    ],
                    'threshold': {
                        'line': {'color': "white", 'width': 4},
                        'thickness': 0.75,
                        'value': score
                    }
                }
            ))
            
            fig.update_layout(height=250, template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
            
            # Breakdown
            col1, col2, col3 = st.columns(3)
            
            breakdown = current_data['breakdown']
            
            with col1:
                st.markdown("#### 🔥 Insider Signals")
                st.metric("Cluster", f"{breakdown['insider_cluster']['score']}/40",
                         breakdown['insider_cluster']['reason'])
                st.metric("Timing", f"{breakdown['insider_timing']['score']}/20",
                         breakdown['insider_timing']['reason'])
            
            with col2:
                st.markdown("#### 💰 Fundamentals")
                st.metric("Cash Runway", f"{breakdown['cash_runway']['score']}/15",
                         breakdown['cash_runway']['reason'])
                st.metric("Institutional", f"{breakdown['institutional']['score']}/10",
                         breakdown['institutional']['reason'])
            
            with col3:
                st.markdown("#### 📊 Technical")
                st.metric("Setup", f"{breakdown['technical']['score']}/10",
                         breakdown['technical']['reason'])
                st.metric("Momentum", f"{breakdown['sector']['score']}/5",
                         breakdown['sector']['reason'])
            
            # Notes
            if current_data.get('notes'):
                st.info(f"💡 **Thesis**: {current_data['notes']}")
                
except FileNotFoundError:
    st.warning("⚠️ No conviction data. Click 'Run Conviction Scan' in sidebar.")

#==========================================================================
# TAB 3: FORM 4 CLUSTER SCANNER (TIER 1)
#==========================================================================
with tab_clusters:
    st.header("🔥 Form 4 Cluster Scanner")
    st.caption("Our #1 Edge - Detects when 3+ insiders buy same stock within 14 days")
    
    if RESEARCH_MODULES_AVAILABLE:
        scanner = Form4ClusterScanner()
        
        col1, col2 = st.columns(2)
        with col1:
            lookback_days = st.slider("Lookback Days", 7, 30, 14)
        with col2:
            min_insiders = st.slider("Min Insiders", 2, 5, 3)
        
        if st.button("🔍 Scan for Clusters", type="primary"):
            with st.spinner(f"Scanning SEC EDGAR for clusters ({min_insiders}+ insiders in {lookback_days} days)..."):
                clusters = scanner.detect_clusters(
                    window_days=lookback_days,
                    min_insiders=min_insiders
                )
                
                if clusters:
                    st.success(f"🎯 Found {len(clusters)} clusters!")
                    
                    for i, cluster in enumerate(clusters, 1):
                        alert = scanner.generate_alert(cluster)
                        with st.expander(f"#{i} {cluster['ticker']} - {cluster['insider_count']} insiders, ${cluster['total_value']:,.0f}"):
                            st.code(alert)
                            
                            # Cross-reference with watchlist
                            if cluster['ticker'] in (full_watchlist or all_tickers):
                                st.success("✅ IN WATCHLIST - Check conviction score!")
                            else:
                                st.warning("⚠️ Not in watchlist - Manual review needed")
                            
                            # Quick stats
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Insiders", cluster['insider_count'])
                            col2.metric("Total Value", f"${cluster['total_value']:,.0f}")
                            col3.metric("Days Span", cluster['days_span'])
                else:
                    st.info("📭 No clusters detected in database. Run a full SEC scan first.")
        
        st.markdown("---")
        st.subheader("📊 About Form 4 Clusters")
        st.markdown("""
        **Why This Works:**
        - When MULTIPLE insiders buy within a short window, it signals shared conviction
        - Insiders have access to material non-public info before it becomes public
        - AISP had 3 insiders buy $1.1M in 10 days before the run
        
        **How to Use:**
        1. Scan daily for new clusters
        2. Cross-reference with wounded prey criteria
        3. Check conviction score (should be 75+)
        4. Monitor entry zone for positioning
        
        **Data Source:** SEC EDGAR Form 4 filings (real-time, free)
        """)
    else:
        st.error("⚠️ Research modules not available")

#==========================================================================
# TAB 4: WATCHLIST MONITOR (TIER 1)
#==========================================================================
with tab_monitor:
    st.header("👁️ Watchlist Monitor")
    st.caption("Real-time alerts when any ticker moves >5% or volume >2x average")
    
    if RESEARCH_MODULES_AVAILABLE:
        monitor = WatchlistMonitor(watchlist_path="atp_watchlists/ATP_WOLF_PACK_MASTER.csv")
        
        col1, col2 = st.columns(2)
        with col1:
            price_threshold = st.slider("Price Move Alert %", 3.0, 10.0, 5.0)
        with col2:
            volume_threshold = st.slider("Volume Alert (x avg)", 1.5, 3.0, 2.0)
        
        if st.button("📸 Take Snapshot", type="primary"):
            with st.spinner(f"Scanning {len(monitor.tickers)} tickers..."):
                snapshot = monitor.get_live_snapshot()
                
                st.success(f"✅ Snapshot captured: {len(snapshot)} tickers")
                
                # Top movers
                st.subheader("🏆 Top Movers")
                
                sorted_snapshot = sorted(snapshot, key=lambda x: abs(x['change_pct']), reverse=True)[:10]
                
                for i, ticker_data in enumerate(sorted_snapshot, 1):
                    direction = "🚀" if ticker_data['change_pct'] > 0 else "📉"
                    color = "green" if ticker_data['change_pct'] > 0 else "red"
                    
                    with st.expander(f"{i}. {ticker_data['ticker']} {direction} {ticker_data['change_pct']:+.2f}%"):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Price", f"${ticker_data['price']:.2f}")
                        col2.metric("Change", f"{ticker_data['change_pct']:+.2f}%")
                        col3.metric("Volume", f"{ticker_data['volume']:,.0f}")
                        
                        # Check if meets alert criteria
                        if abs(ticker_data['change_pct']) >= price_threshold:
                            st.warning(f"⚠️ PRICE ALERT: {abs(ticker_data['change_pct']):.1f}% move!")
        
        if st.button("🔔 Set Baseline (Start Monitoring)"):
            with st.spinner("Setting baseline prices and volumes..."):
                monitor.set_baseline()
                st.success(f"✅ Baseline set for {len(monitor.baseline)} tickers. Ready to monitor!")
        
        st.markdown("---")
        st.subheader("🚨 Recent Alerts")
        
        # Load recent alerts from log
        alert_file = Path("logs/watchlist_alerts.jsonl")
        if alert_file.exists():
            alerts = []
            with open(alert_file) as f:
                for line in f:
                    alerts.append(json.loads(line))
            
            # Show last 10
            recent = alerts[-10:]
            
            for alert in reversed(recent):
                alert_type = alert['type']
                if alert_type == 'COMBO':
                    st.error(f"🔥 {alert['message']} ({alert['timestamp']})")
                elif alert_type == 'PRICE_MOVE':
                    st.warning(f"⚠️ {alert['message']} ({alert['timestamp']})")
                elif alert_type == 'VOLUME_SPIKE':
                    st.info(f"📊 {alert['message']} ({alert['timestamp']})")
        else:
            st.info("No alerts yet. Set baseline to start monitoring.")
        
        st.markdown("---")
        st.subheader("📖 About Watchlist Monitor")
        st.markdown("""
        **Why This Works:**
        - Catches breakouts in real-time before they run
        - Volume spikes signal institutional buying
        - Price + volume combo = strongest conviction
        
        **How to Use:**
        1. Set baseline at market open (9:30 AM EST)
        2. Monitor runs continuously in background
        3. Get alerted on Slack/email when criteria hit
        4. Cross-check with conviction score before entry
        
        **Alert Types:**
        - 🚀 PRICE MOVE: >5% intraday move
        - 📊 VOLUME SPIKE: >2x average volume
        - 🔥 COMBO: Both price AND volume (highest priority)
        """)
    else:
        st.error("⚠️ Research modules not available")

#==========================================================================
# TAB 5: INSIDER CLUSTERS - Using our cluster_buy_scanner.py
#==========================================================================
with tab_sectors:
    st.header("🔥 Insider Cluster Analysis")
    st.caption("Multiple insiders buying = conviction signal")
    
    try:
        import subprocess
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("🔄 Run Cluster Scan", key="sectors_cluster_scan"):
                with st.spinner("Scanning for insider buying clusters..."):
                    result = subprocess.run(
                        ['python3', 'cluster_buy_scanner.py'],
                        capture_output=True,
                        text=True,
                        timeout=90
                    )
                    st.success("✅ Scan complete!")
            
            # Load results
            try:
                results_file = Path('logs/cluster_results.json')
                if results_file.exists():
                    with open(results_file) as f:
                        data = json.load(f)
                    
                    clusters = data.get('clusters', [])
                    
                    if clusters:
                        tier1 = [c for c in clusters if c.get('tier') == 'TIER 1']
                        tier2 = [c for c in clusters if c.get('tier') == 'TIER 2']
                        
                        if tier1:
                            st.subheader(f"🔥 TIER 1 CLUSTERS ({len(tier1)}) - 5+ insiders")
                            for cluster in tier1:
                                with st.expander(f"🔥 {cluster['ticker']} - {cluster['insider_count']} insiders"):
                                    c1, c2, c3 = st.columns(3)
                                    with c1:
                                        st.metric("Insiders", cluster['insider_count'])
                                        st.metric("Total Shares", f"{cluster.get('total_shares', 0):,}")
                                    with c2:
                                        st.metric("Total Value", f"${cluster.get('total_value', 0):,.0f}")
                                        st.metric("Latest Buy", cluster.get('latest_date', 'Unknown'))
                                    with c3:
                                        st.metric("Avg Price", f"${cluster.get('avg_price', 0):.2f}")
                                        st.metric("Current Price", f"${cluster.get('current_price', 0):.2f}")
                        
                        if tier2:
                            st.subheader(f"⚡ TIER 2 CLUSTERS ({len(tier2)}) - 3-4 insiders")
                            for cluster in tier2[:5]:
                                st.markdown(f"**{cluster['ticker']}** - {cluster['insider_count']} insiders | ${cluster.get('total_value', 0):,.0f}")
                    else:
                        st.info("No clusters detected. Run scan.")
                else:
                    st.warning("No results yet - click 'Run Cluster Scan' above")
            except Exception as e:
                st.error(f"Error loading results: {e}")
        
        with col2:
            st.subheader("📊 About")
            st.markdown("""
            **Cluster = Conviction**
            
            When multiple insiders buy:
            - They see the same opportunity
            - Reduces individual risk
            - Higher conviction signal
            
            **Tiers:**
            - 🔥 TIER 1: 5+ insiders
            - ⚡ TIER 2: 3-4 insiders
            
            **Data from:**
            - SEC Form 4 filings
            - Last 90 days
            - Open market purchases only
            """)
    
    except Exception as e:
        st.error(f"Cluster scanner error: {e}")
        st.info("Run: python3 cluster_buy_scanner.py")

#==========================================================================
# TAB 4: CONGRESS TRACKER - Follow the money
#==========================================================================
with tab_catalysts:
    st.header("🏛️ Congress Tracker")
    st.caption("Follow congressional trades - they have inside info")
    
    try:
        import subprocess
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("🔄 Run Congress Scan", key="congress_scan"):
                with st.spinner("Tracking congressional trades..."):
                    result = subprocess.run(
                        ['python3', 'congress_tracker.py'],
                        capture_output=True,
                        text=True,
                        timeout=90
                    )
                    st.success("✅ Scan complete!")
            
            # Load results
            try:
                results_file = Path('logs/congress_trades.json')
                if results_file.exists():
                    with open(results_file) as f:
                        data = json.load(f)
                    
                    trades = data.get('trades', [])
                    
                    if trades:
                        st.subheader(f"📋 Recent Congressional Trades ({len(trades)})")
                        
                        for trade in trades[:20]:
                            with st.expander(f"{trade.get('ticker', 'N/A')} - {trade.get('politician', 'Unknown')} | {trade.get('transaction_type', 'N/A')}"):
                                c1, c2, c3 = st.columns(3)
                                with c1:
                                    st.markdown(f"**Politician:** {trade.get('politician', 'Unknown')}")
                                    st.markdown(f"**Party:** {trade.get('party', 'Unknown')}")
                                with c2:
                                    st.markdown(f"**Type:** {trade.get('transaction_type', 'Unknown')}")
                                    st.markdown(f"**Amount:** ${trade.get('amount_min', 0):,} - ${trade.get('amount_max', 0):,}")
                                with c3:
                                    st.markdown(f"**Filed:** {trade.get('filed_date', 'Unknown')}")
                                    st.markdown(f"**Trade Date:** {trade.get('transaction_date', 'Unknown')}")
                    else:
                        st.info("No recent trades. Run scan.")
                else:
                    st.warning("No results yet - click 'Run Congress Scan' above")
            except Exception as e:
                st.error(f"Error loading results: {e}")
        
        with col2:
            st.subheader("📊 The Edge")
            st.markdown("""
            **Why Track Congress?**
            
            ✅ Access to insider info
            ✅ Policy knowledge
            ✅ Committee insights
            ✅ Legal for them!
            
            **What to Watch:**
            - Clusters (multiple buying same stock)
            - Unusual timing
            - Committee members
            - Large positions
            
            **Data from:**
            - Congressional disclosure filings
            - 45-day reporting window
            """)
    
    except Exception as e:
        st.error(f"Congress tracker error: {e}")
        st.info("Run: python3 congress_tracker.py")

#==========================================================================
# TAB 5: PATTERN HUNTER - Repeat gainers
#==========================================================================
with tab_breakouts:
    st.header("💣 Pattern Hunter - Repeat Gainers")
    st.caption("Find stocks with predictable cycles - space/nuclear/AI sectors")
    
    try:
        import subprocess
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("🔄 Run Pattern Analysis", key="pattern_scan"):
                with st.spinner("Analyzing repeat mover patterns..."):
                    result = subprocess.run(
                        ['python3', 'pattern_hunter.py'],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    st.success("✅ Analysis complete!")
            
            st.subheader("🔥 KNOWN REPEAT RUNNERS")
            
            # Space sector
            with st.expander("🚀 SPACE SECTOR - Launch window cycles"):
                st.markdown("""
                **LUNR, RKLB, RDW**
                - **Catalyst:** Launch windows every 4-8 weeks
                - **Pattern:** +15-40% on successful launch news
                - **Pullback:** 20-30% after initial spike
                - **Re-entry:** On pullback or next launch window
                
                **What triggers it:**
                - NASA contracts
                - Successful launches
                - New mission announcements
                - Earnings with guidance
                """)
            
            # Nuclear sector
            with st.expander("☢️ NUCLEAR SECTOR - Policy cycles"):
                st.markdown("""
                **UUUU, SMR, LEU, OKLO**
                - **Catalyst:** DOE policy, uranium prices, SMR approvals
                - **Pattern:** Sector moves together
                - **Edge:** UUUU has 21 insider cluster (highest conviction)
                - **Timing:** Policy announcements, White House clean energy push
                
                **What triggers it:**
                - DOE funding announcements
                - Uranium price spikes
                - SMR construction permits
                - Climate policy news
                """)
            
            # AI Infrastructure
            with st.expander("🤖 AI INFRASTRUCTURE - Earnings cycles"):
                st.markdown("""
                **VRT, ANET, SMCI**
                - **Catalyst:** Earnings beats, hyperscaler announcements
                - **Pattern:** Pumps 1-2 weeks AFTER main AI sector
                - **Why:** Infrastructure needed for AI buildout
                - **Timing:** Following NVDA/MSFT earnings
                
                **What triggers it:**
                - Data center expansion news
                - Hyperscaler capex guidance
                - Infrastructure shortage headlines
                - Cooling/power solution announcements
                """)
            
            # Quantum
            with st.expander("⚛️ QUANTUM - Event driven"):
                st.markdown("""
                **IONQ, RGTI, QBTS, QUBT**
                - **Catalyst:** Tech demos, partnerships, breakthroughs
                - **Pattern:** +30-100% on major news, VERY volatile
                - **Risk:** HIGH - tight stops required
                - **Timing:** CES, AWS re:Invent, research papers
                
                **What triggers it:**
                - Error correction breakthroughs
                - Commercial partnerships
                - Government contracts
                - Conference demonstrations
                """)
        
        with col2:
            st.subheader("📊 The Play")
            st.markdown("""
            **How to Use:**
            
            1. **Know the sectors**
               - Space, Nuclear, AI Infra, Quantum
            
            2. **Watch for catalysts**
               - Launch windows
               - Policy news
               - Earnings
               - Conferences
            
            3. **Enter early**
               - Before news hits
               - On pullbacks
               - With insider buying
            
            4. **Exit strategy**
               - Take profit on spike
               - Hold core position
               - Re-enter on pullback
            
            **Risk Management:**
            - -8% stops always
            - Size smaller on vol
            - Never chase after +20%
            """)
    
    except Exception as e:
        st.error(f"Pattern hunter error: {e}")
        st.info("Run: python3 pattern_hunter.py")

#==========================================================================
# TAB 6: WATCHLIST RANKINGS
#==========================================================================
with tab_watchlist:
    st.header("🎯 Watchlist Rankings")

try:
    with open('logs/conviction_rankings_latest.json', 'r') as f:
        rankings = json.load(f)
        
        # Create comparison table
        ranking_data = []
        for i, r in enumerate(rankings['rankings'][:10], 1):
            ranking_data.append({
                'Rank': i,
                'Ticker': r['ticker'],
                'Score': r['total_score'],
                'Conviction': r['conviction'],
                'Insider': r['breakdown']['insider_cluster']['score'],
                'Technical': r['breakdown']['technical']['score'],
                'Notes': r.get('notes', '')[:50] + '...' if len(r.get('notes', '')) > 50 else r.get('notes', '')
            })
        
        df = pd.DataFrame(ranking_data)
        
        # Highlight selected ticker
        def highlight_selected(row):
            if row['Ticker'] == selected_ticker:
                return ['background-color: rgba(0,255,0,0.2)'] * len(row)
            return [''] * len(row)
        
        styled_df = df.style.apply(highlight_selected, axis=1)
        
        st.dataframe(styled_df, use_container_width=True, height=400)
        
except FileNotFoundError:
    st.warning("⚠️ No ranking data. Run conviction scan.")

# Footer
st.markdown("---")
st.caption("🐺 Wolf Den War Room | Real-time analysis | AWOOOO")

# Auto-refresh option
if st.sidebar.checkbox("🔄 Auto-refresh (1 min)", value=False):
    import time
    time.sleep(60)
    st.rerun()
