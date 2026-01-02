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

# Import research modules
try:
    from research.sector_rotation import SectorRotationTracker
    from research.catalyst_tracker import CatalystTracker
    from research.failed_breakout_detector import FailedBreakoutDetector
    from research.form4_cluster_scanner import Form4ClusterScanner
    from research.watchlist_monitor import WatchlistMonitor
    RESEARCH_MODULES_AVAILABLE = True
except Exception as e:
    RESEARCH_MODULES_AVAILABLE = False
    print(f"Research modules not available: {e}")

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
tab_overview, tab_chart, tab_clusters, tab_monitor, tab_sectors, tab_catalysts, tab_breakouts, tab_watchlist = st.tabs([
    "📊 Overview", "📈 Live Chart", "🔥 Clusters", "👁️ Monitor", "🔥 Sectors", "📅 Catalysts", "💣 Breakouts", "🎯 Watchlist"
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

if st.sidebar.button("🔥 Sector Rotation Scan"):
    if RESEARCH_MODULES_AVAILABLE:
        with st.spinner("Analyzing sectors..."):
            import subprocess
            subprocess.run(['python3', 'src/research/sector_rotation.py'], timeout=60)
        st.success("✅ Complete!")
        st.rerun()
    else:
        st.error("Research modules not available")

if st.sidebar.button("💣 Failed Breakout Scan"):
    if RESEARCH_MODULES_AVAILABLE:
        with st.spinner("Scanning breakouts..."):
            import subprocess
            subprocess.run(['python3', 'src/research/failed_breakout_detector.py'], timeout=120)
        st.success("✅ Complete!")
        st.rerun()

if st.sidebar.button("🔥 Form 4 Cluster Scan"):
    if RESEARCH_MODULES_AVAILABLE:
        with st.spinner("Scanning SEC EDGAR for insider clusters..."):
            import subprocess
            subprocess.run(['python3', 'src/research/form4_cluster_scanner.py', '--detect'], timeout=60)
        st.success("✅ Complete!")
        st.rerun()
    else:
        st.error("Research modules not available")

if st.sidebar.button("👁️ Watchlist Snapshot"):
    if RESEARCH_MODULES_AVAILABLE:
        with st.spinner("Taking watchlist snapshot..."):
            import subprocess
            subprocess.run(['python3', 'src/research/watchlist_monitor.py', '--snapshot', '--top-movers'], timeout=60)
        st.success("✅ Complete!")
        st.rerun()
    else:
        st.error("Research modules not available")

# Research module status
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔬 Research Modules")
if RESEARCH_MODULES_AVAILABLE:
    st.sidebar.success("✅ All modules loaded")
else:
    st.sidebar.error("⚠️ Modules not available")

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
# TAB 2: LIVE CHART
#==========================================================================
with tab_chart:
    st.header(f"📊 {selected_ticker} - Real-Time Analysis")

@st.cache_data(ttl=60)
def load_price_data(ticker, period):
    """Load price data with caching."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    info = stock.info
    return hist, info

try:
    hist, info = load_price_data(selected_ticker, timeframe)
    
    if not hist.empty:
        # Create subplots
        if show_volume:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3],
                subplot_titles=(f'{selected_ticker} Price', 'Volume')
            )
        else:
            fig = go.Figure()
        
        # Candlestick chart
        candlestick = go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name='Price',
            increasing_line_color='#00ff00',
            decreasing_line_color='#ff0000'
        )
        
        if show_volume:
            fig.add_trace(candlestick, row=1, col=1)
        else:
            fig.add_trace(candlestick)
        
        # Add SMAs
        if show_sma:
            sma_20 = hist['Close'].rolling(window=20).mean()
            sma_50 = hist['Close'].rolling(window=50).mean()
            
            if show_volume:
                fig.add_trace(go.Scatter(x=hist.index, y=sma_20, name='SMA 20', 
                                        line=dict(color='orange', width=1)), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=sma_50, name='SMA 50',
                                        line=dict(color='blue', width=1)), row=1, col=1)
            else:
                fig.add_trace(go.Scatter(x=hist.index, y=sma_20, name='SMA 20',
                                        line=dict(color='orange', width=1)))
                fig.add_trace(go.Scatter(x=hist.index, y=sma_50, name='SMA 50',
                                        line=dict(color='blue', width=1)))
        
        # Add entry zone
        if show_entry_zone and selected_ticker in config.get('entry_zones', {}):
            zone = config['entry_zones'][selected_ticker]
            
            shapes = [
                # Entry zone box
                dict(type="rect",
                     xref="x", yref="y",
                     x0=hist.index[0], x1=hist.index[-1],
                     y0=zone['low'], y1=zone['high'],
                     fillcolor="green", opacity=0.1,
                     line=dict(width=0)),
                # Stop loss line
                dict(type="line",
                     xref="x", yref="y",
                     x0=hist.index[0], x1=hist.index[-1],
                     y0=zone['stop'], y1=zone['stop'],
                     line=dict(color="red", width=2, dash="dash"))
            ]
            
            # Shapes always go in layout, not xaxis
            fig.update_layout(shapes=shapes)
            
            # Add annotations
            annotations = [
                dict(x=hist.index[-1], y=zone['high'],
                     text=f"Entry High: ${zone['high']:.2f}",
                     showarrow=False, xanchor='left', bgcolor='green', opacity=0.8),
                dict(x=hist.index[-1], y=zone['low'],
                     text=f"Entry Low: ${zone['low']:.2f}",
                     showarrow=False, xanchor='left', bgcolor='green', opacity=0.8),
                dict(x=hist.index[-1], y=zone['stop'],
                     text=f"STOP: ${zone['stop']:.2f}",
                     showarrow=False, xanchor='left', bgcolor='red', opacity=0.8)
            ]
            
            if show_volume:
                fig.update_layout(annotations=annotations)
            else:
                fig.update_layout(annotations=annotations)
        
        # Add volume bars
        if show_volume:
            colors = ['red' if hist['Close'].iloc[i] < hist['Open'].iloc[i] else 'green' 
                     for i in range(len(hist))]
            
            fig.add_trace(go.Bar(
                x=hist.index,
                y=hist['Volume'],
                name='Volume',
                marker_color=colors,
                showlegend=False
            ), row=2, col=1)
        
        # Update layout
        fig.update_layout(
            height=700 if show_volume else 500,
            xaxis_rangeslider_visible=False,
            template='plotly_dark',
            hovermode='x unified',
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        if show_volume:
            fig.update_yaxes(title_text="Price", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Current stats
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
        monitor = WatchlistMonitor(watchlist_path="ATP_WOLF_PACK_MASTER.csv")
        
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
# TAB 5: SECTOR ROTATION
#==========================================================================
with tab_sectors:
    st.header("🔥 Sector Rotation Analysis")
    
    if RESEARCH_MODULES_AVAILABLE:
        tracker = SectorRotationTracker()
        
        with st.spinner("Analyzing sector momentum..."):
            df = tracker.get_sector_performance([5, 10, 20])
            
            if not df.empty:
                ranked = tracker.rank_sectors(df)
                
                # Top 5 hot sectors
                st.subheader("🚀 HOTTEST SECTORS")
                for idx, row in ranked.head(5).iterrows():
                    with st.expander(f"{'🔥' if row['5d'] > 5 else '🟢'} {row['sector']} ({row['etf']}) - {row['5d']:+.1f}%"):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("5-Day", f"{row['5d']:+.2f}%")
                        col2.metric("10-Day", f"{row['10d']:+.2f}%")
                        col3.metric("20-Day", f"{row['20d']:+.2f}%")
                        
                        if row.get('accelerating'):
                            st.success("🚀 ACCELERATING - Getting stronger!")
                
                # Generate alerts
                st.markdown("---")
                st.subheader("⚡ Sector Alerts")
                
                alerts = tracker.generate_sector_alerts(ranked, threshold=3.0)
                
                if alerts:
                    for alert in alerts:
                        if alert['alert_type'] == 'HOT_SECTOR':
                            st.success(f"🟢 {alert['sector']} ({alert['etf']}) +{alert['performance_5d']:.1f}%")
                            st.write(f"**Watchlist tickers:** {', '.join(alert['watchlist_tickers'])}")
                            st.write(f"**Priority:** {alert['priority']}")
                            st.markdown("---")
                else:
                    st.info("No major sector movements detected")
                    
                # Full table
                st.markdown("---")
                st.subheader("📊 All Sectors")
                st.dataframe(ranked[['sector', 'etf', '5d', '10d', '20d', 'momentum_score']], use_container_width=True)
    else:
        st.error("⚠️ Research modules not available. Check installation.")

#==========================================================================
# TAB 4: CATALYST CALENDAR
#==========================================================================
with tab_catalysts:
    st.header("📅 Upcoming Catalysts")
    
    if RESEARCH_MODULES_AVAILABLE:
        tracker = CatalystTracker()
        
        # Add manual catalyst interface
        with st.sidebar:
            st.markdown("---")
            st.subheader("➕ Add Catalyst")
            cat_ticker = st.text_input("Ticker", "LUNR")
            cat_event = st.text_input("Event", "IM-3 Moon Mission")
            cat_date = st.date_input("Date")
            cat_type = st.selectbox("Type", ["EARNINGS", "PRODUCT_LAUNCH", "FDA", "CONTRACT", "TECH_DEMO"])
            cat_impact = st.selectbox("Impact", ["LOW", "MEDIUM", "HIGH", "EXTREME"])
            
            if st.button("Add Catalyst"):
                tracker.add_manual_catalysts(cat_ticker, cat_event, cat_date.strftime('%Y-%m-%d'), cat_type, cat_impact)
                st.success(f"✅ Added {cat_ticker}!")
                st.rerun()
        
        with st.spinner("Loading catalyst calendar..."):
            catalysts = tracker.get_all_catalysts(full_watchlist if full_watchlist else all_tickers, days_ahead=30)
            ranked = tracker.rank_catalysts(catalysts)
            
            if ranked:
                st.subheader(f"🎯 {len(ranked)} Catalysts in Next 30 Days")
                
                for cat in ranked:
                    ticker = cat.get('ticker', 'MARKET')
                    days = cat['days_until']
                    
                    # Urgency color
                    if days <= 3:
                        urgency = "🔴 IMMINENT"
                    elif days <= 7:
                        urgency = "🟠 THIS WEEK"
                    elif days <= 14:
                        urgency = "🟡 NEXT 2 WEEKS"
                    else:
                        urgency = "🟢 LATER"
                        
                    with st.expander(f"{urgency} | {ticker} - {cat.get('event', 'Earnings')} (Score: {cat['score']})"):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Days Until", days)
                        col2.metric("Impact", cat['impact'])
                        col3.metric("Type", cat['catalyst_type'])
                        
                        st.write(f"**Date:** {cat['date']}")
                        
                        if cat.get('last_surprise_pct'):
                            surprise = cat['last_surprise_pct']
                            if surprise > 0:
                                st.success(f"Last earnings: +{surprise:.1f}% surprise")
                            else:
                                st.error(f"Last earnings: {surprise:.1f}% miss")
            else:
                st.info("⚠️ No catalysts in next 30 days. Add manual catalysts in sidebar.")
    else:
        st.error("⚠️ Research modules not available")

#==========================================================================
# TAB 5: FAILED BREAKOUTS
#==========================================================================
with tab_breakouts:
    st.header("💣 Failed Breakout Detector")
    st.caption("Stocks that hyped, failed, and are resetting - potential reversal plays")
    
    if RESEARCH_MODULES_AVAILABLE:
        detector = FailedBreakoutDetector()
        
        with st.spinner(f"Scanning {len(full_watchlist if full_watchlist else all_tickers)} tickers..."):
            results = detector.scan_watchlist(full_watchlist if full_watchlist else all_tickers)
            
            if results:
                # Score each
                for result in results:
                    result['score'] = detector.score_reversal_potential(result)
                    
                results.sort(key=lambda x: x['score'], reverse=True)
                
                st.subheader(f"🎯 Found {len(results)} Failed Breakouts")
                
                for i, fb in enumerate(results, 1):
                    with st.expander(f"#{i} {fb['ticker']} - Reversal Score: {fb['score']}/100"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Peak", f"${fb['high']:.2f}", f"+{fb['run_pct']:.1f}%")
                            st.metric("Bottom", f"${fb['low_after']:.2f}", f"-{fb['retracement_pct']:.1f}%")
                            st.metric("Current", f"${fb['current']:.2f}", f"+{fb['current_from_low_pct']:.1f}% off low")
                            
                        with col2:
                            st.write(f"**High Date:** {fb['high_date']}")
                            st.write(f"**Low Date:** {fb['low_date']}")
                            st.write(f"**Days Since Peak:** {fb['days_since_high']}")
                            st.write(f"**Pattern:** {fb['pattern']}")
                            
                        st.info("💡 Check for insider buying to increase conviction")
            else:
                st.info("✅ No failed breakouts detected in watchlist")
    else:
        st.error("⚠️ Research modules not available")

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
