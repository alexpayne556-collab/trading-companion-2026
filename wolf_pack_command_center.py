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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 PRESSURE MAP",
    "💰 SMART MONEY",
    "🔫 TACTICAL",
    "📊 CONVICTION",
    "🔧 SETTINGS"
])

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
# TAB 5: SETTINGS
# ============================================================================

with tab5:
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
