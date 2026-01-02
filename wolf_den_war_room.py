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

# Page config
st.set_page_config(
    page_title="🐺 Wolf Den War Room",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🐺 WOLF DEN WAR ROOM")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

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

# Ticker selection
all_tickers = [config['watchlist']['primary']] + config['watchlist']['backup'] + config['watchlist']['positions']
selected_ticker = st.sidebar.selectbox("Select Target", all_tickers, index=0)

# Timeframe
timeframe = st.sidebar.selectbox("Timeframe", ["1d", "5d", "1mo", "3mo", "6mo", "1y"], index=2)

# Technical indicators
show_sma = st.sidebar.checkbox("Show 20/50 SMA", value=True)
show_volume = st.sidebar.checkbox("Show Volume", value=True)
show_entry_zone = st.sidebar.checkbox("Show Entry Zone", value=True)

# Quick actions
st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Scans")

if st.sidebar.button("🔄 Refresh All Data"):
    st.rerun()

if st.sidebar.button("📊 Run Conviction Scan"):
    with st.spinner("Running conviction analysis..."):
        import subprocess
        subprocess.run(['python3', 'fast_conviction_scanner.py'], timeout=60)
    st.success("✅ Complete!")
    st.rerun()

if st.sidebar.button("🚨 Pre-Market Scan"):
    with st.spinner("Scanning pre-market..."):
        import subprocess
        subprocess.run(['python3', 'premarket_auto.py'], timeout=60)
    st.success("✅ Complete!")
    st.rerun()

# Main dashboard
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

# Price chart with technical indicators
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

# Conviction analysis
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

st.markdown("---")

# Watchlist comparison
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
