#!/usr/bin/env python3
"""
🐺 WOLF DEN DASHBOARD - Real-time hunt status

Streamlit dashboard showing:
- Current conviction rankings
- GO/NO-GO status for each ticker
- Insider signals
- Institutional backing
- Pattern recognition
- Pre-market scan results

Author: Brokkr
Date: January 2, 2026

Run: streamlit run wolf_den_dashboard.py
Access: http://localhost:8501
"""

import streamlit as st
import json
import pandas as pd
import yfinance as yf
from datetime import datetime
from pathlib import Path
import yaml

# Page config
st.set_page_config(
    page_title="🐺 Wolf Den",
    page_icon="🐺",
    layout="wide"
)

st.title("🐺 WOLF DEN - Hunt Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Load config
try:
    with open('wolf_den_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
except:
    config = {
        'watchlist': {
            'primary': 'AISP',
            'backup': ['SOUN', 'BBAI'],
            'positions': ['LUNR']
        }
    }

# Sidebar
st.sidebar.header("🎯 Wolf Pack Settings")

if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

if st.sidebar.button("📊 Run Conviction Scan"):
    with st.spinner("Running conviction analysis..."):
        import subprocess
        # Use fast scanner for instant results
        subprocess.run(['python3', 'fast_conviction_scanner.py'], timeout=60)
    st.success("✅ Conviction scan complete!")
    st.rerun()

if st.sidebar.button("🏦 Run 13F Scan"):
    with st.spinner("Scanning institutional holders..."):
        import subprocess
        subprocess.run(['python3', 'institutional_13f_tracker.py'], timeout=120)
    st.success("✅ 13F scan complete!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Actions")
if st.sidebar.button("🚨 Run Pre-Market Scan"):
    with st.spinner("Scanning pre-market..."):
        import subprocess
        subprocess.run(['python3', 'premarket_auto.py'], timeout=60)
    st.success("✅ Pre-market scan complete!")
    st.rerun()

# Main dashboard
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Account Value", "$1,280", "+2.1%")
with col2:
    st.metric("Cash Available", "$1,120", "87.5%")
with col3:
    st.metric("Positions", "1 ACTIVE", "LUNR")

st.markdown("---")

# PRIMARY TARGET
st.header("🎯 PRIMARY TARGET")

primary = config['watchlist']['primary']

col1, col2 = st.columns([2, 1])

with col1:
    # Get live price
    try:
        ticker = yf.Ticker(primary)
        hist = ticker.history(period='1d')
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            prev_close = ticker.info.get('previousClose', current_price)
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            st.subheader(f"{primary}")
            st.metric("Current Price", f"${current_price:.2f}", f"{change_pct:+.2f}%")
        else:
            st.warning(f"Unable to get live data for {primary}")
    except:
        st.error(f"Error fetching {primary} data")

with col2:
    # GO/NO-GO status
    try:
        with open('logs/premarket_latest.json', 'r') as f:
            premarket = json.load(f)
            
            if primary in premarket.get('watchlist', {}):
                status = premarket['watchlist'][primary].get('status', 'UNKNOWN')
                
                if status == 'GO':
                    st.success("✅ GO")
                elif status == 'NO-GO':
                    st.error("❌ NO-GO")
                else:
                    st.warning(f"⚠️ {status}")
            else:
                st.info("⏳ AWAITING SCAN")
    except FileNotFoundError:
        st.info("⏳ No pre-market data yet. Run scan.")

# Conviction breakdown for primary
st.subheader("📊 Conviction Breakdown")

try:
    with open('logs/conviction_rankings_latest.json', 'r') as f:
        rankings = json.load(f)
        
        # Find primary target
        primary_data = None
        for r in rankings['rankings']:
            if r['ticker'] == primary:
                primary_data = r
                break
        
        if primary_data:
            col1, col2, col3, col4 = st.columns(4)
            
            breakdown = primary_data['breakdown']
            
            with col1:
                st.metric("Insider Cluster", 
                         f"{breakdown['insider_cluster']['score']}/40",
                         breakdown['insider_cluster']['reason'])
            with col2:
                st.metric("Insider Timing", 
                         f"{breakdown['insider_timing']['score']}/20",
                         breakdown['insider_timing']['reason'])
            with col3:
                st.metric("Cash Runway", 
                         f"{breakdown['cash_runway']['score']}/15",
                         breakdown['cash_runway']['reason'])
            with col4:
                st.metric("TOTAL CONVICTION", 
                         f"{primary_data['total_score']}/100",
                         primary_data['conviction'])
        else:
            st.warning("Run conviction scan to see breakdown")
            
except FileNotFoundError:
    st.warning("⚠️ No conviction data. Click 'Run Conviction Scan' in sidebar.")

st.markdown("---")

# CONVICTION RANKINGS
st.header("📈 Conviction Rankings")

try:
    with open('logs/conviction_rankings_latest.json', 'r') as f:
        rankings = json.load(f)
        
        # Create table
        ranking_data = []
        for i, r in enumerate(rankings['rankings'], 1):
            ranking_data.append({
                'Rank': i,
                'Ticker': r['ticker'],
                'Score': r['total_score'],
                'Conviction': r['conviction'],
                'Insider': r['breakdown']['insider_cluster']['score'],
                'Timing': r['breakdown']['insider_timing']['score'],
                'Cash': r['breakdown']['cash_runway']['score'],
                'Technical': r['breakdown']['technical']['score']
            })
        
        df = pd.DataFrame(ranking_data)
        
        # Style the table
        def color_conviction(val):
            if '🟢' in val:
                return 'background-color: #90EE90'
            elif '🟡' in val:
                return 'background-color: #FFD700'
            elif '🔴' in val:
                return 'background-color: #FFB6C1'
            return ''
        
        styled_df = df.style.applymap(color_conviction, subset=['Conviction'])
        
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Top 3 callouts
        st.subheader("🏆 Top 3 Targets for Friday")
        
        col1, col2, col3 = st.columns(3)
        
        for i, col in enumerate([col1, col2, col3]):
            if i < len(rankings['rankings']):
                r = rankings['rankings'][i]
                with col:
                    st.metric(
                        f"#{i+1}: {r['ticker']}",
                        f"{r['total_score']}/100",
                        r['conviction']
                    )
                    
                    # Key insight
                    insights = []
                    if r['breakdown']['insider_cluster']['score'] >= 30:
                        insights.append("🔥 Strong insider cluster")
                    if r['breakdown']['insider_timing']['score'] >= 15:
                        insights.append("🎯 Excellent timing")
                    if r['breakdown']['technical']['score'] >= 8:
                        insights.append("📉 Wounded prey setup")
                    
                    if insights:
                        st.caption("\n".join(insights))

except FileNotFoundError:
    st.warning("⚠️ No ranking data. Click 'Run Conviction Scan' in sidebar.")
    if st.button("🚀 Run Scan Now"):
        with st.spinner("Running conviction analysis..."):
            import subprocess
            subprocess.run(['python3', 'conviction_ranker.py'], timeout=180)
        st.success("✅ Complete!")
        st.rerun()

st.markdown("---")

# INSTITUTIONAL HOLDINGS
st.header("🏦 Institutional Holdings")

try:
    with open('logs/institutional_13f_latest.json', 'r') as f:
        institutional = json.load(f)
        
        # Show institutional data for each ticker
        for result in institutional['results']:
            if result['status'] == 'TRACKED':
                with st.expander(f"📊 {result['ticker']} - {result['analysis']}"):
                    st.caption(f"**Concentration:** {result['concentration']}")
                    st.caption(f"**Total Institutional:** {result['total_institutional_pct']}")
                    
                    # Top holders table
                    holders_data = []
                    for h in result['top_holders']:
                        holders_data.append({
                            'Institution': h['name'],
                            'Shares': h['shares'],
                            '% of Float': h['pct'],
                            'Date': h['date']
                        })
                    
                    if holders_data:
                        st.dataframe(pd.DataFrame(holders_data), use_container_width=True)

except FileNotFoundError:
    st.warning("⚠️ No 13F data. Click 'Run 13F Scan' in sidebar.")

st.markdown("---")

# PRE-MARKET STATUS
st.header("🌅 Pre-Market Status")

try:
    with open('logs/premarket_latest.json', 'r') as f:
        premarket = json.load(f)
        
        st.caption(f"Last scan: {premarket.get('timestamp', 'Unknown')}")
        
        # Handle both dict and list formats
        watchlist_data = premarket.get('watchlist', {})
        if isinstance(watchlist_data, list):
            st.info("⏳ Pre-market data pending. Run scan to update.")
        else:
            # Show each ticker
            for ticker, data in watchlist_data.items():
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(ticker, f"${data.get('price', 'N/A')}")
                with col2:
                    change = data.get('change_pct', '0%')
                    st.metric("Change", change)
                with col3:
                    volume = data.get('volume', 'N/A')
                    st.metric("Volume", f"{volume:,}" if isinstance(volume, int) else volume)
                with col4:
                    status = data.get('status', 'UNKNOWN')
                    if status == 'GO':
                        st.success(status)
                    elif status == 'NO-GO':
                        st.error(status)
                    else:
                        st.warning(status)
            
            # Reason
            if 'reason' in data:
                st.caption(f"💡 {data['reason']}")
            
            st.markdown("---")

except FileNotFoundError:
    st.info("⏳ No pre-market data yet. Scan will run at 6 AM automatically.")

# OVERNIGHT ALERTS
st.header("🌙 Overnight Alerts")

try:
    with open('logs/overnight_latest.json', 'r') as f:
        overnight = json.load(f)
        
        st.caption(f"Last scan: {overnight.get('timestamp', 'Unknown')}")
        
        overall = overnight.get('overall_status', 'UNKNOWN')
        
        if overall == 'CLEAR':
            st.success("✅ ALL CLEAR - No overnight alerts")
        else:
            st.warning(f"⚠️ Status: {overall}")
        
        # Show findings
        for ticker, findings in overnight.get('findings', {}).items():
            if findings.get('alert_level') != 'GREEN':
                with st.expander(f"⚠️ {ticker} - {findings.get('alert_level')}"):
                    st.json(findings)

except FileNotFoundError:
    st.info("⏳ No overnight data yet. Scan will run at 4 AM automatically.")

# Footer
st.markdown("---")
st.caption("🐺 Wolf Den Dashboard | Built by Brokkr | AWOOOO")

# Auto-refresh every 5 minutes during trading hours
if st.sidebar.checkbox("🔄 Auto-refresh (5 min)"):
    import time
    time.sleep(300)
    st.rerun()
